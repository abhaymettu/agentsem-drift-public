#!/usr/bin/env python3
"""Render the paper's figures as plain SVG text.

Constitution: numpy + stdlib only, one render script. This is that script.
No number in these figures is typed in by hand -- every value plotted is read
from the three committed JSON files below. Text labels (axis titles, stage
names, threat names) are the only literals, and they are copied from the
paper's own section 2 table and section 4 prose, not invented here.

Inputs (read-only, committed):
  sim/results.json
  sim/metrics.json
  pilot/results.json

Outputs:
  paper/fig1_validity_chain.svg
  paper/fig2_sensitivity_vs_false_flags.svg
  paper/fig3_selection_and_authorship.svg
  paper/fig4_contamination.svg

Palette, marks and accessibility rules follow the dataviz skill's reference
palette (references/palette.md): the 8-hue categorical order validated for
adjacent-pair CVD safety, status colors reserved, text in ink tokens only,
legends + direct labels for every multi-series chart, and a <title>/<desc>
pair in every SVG. These are static print figures for a manuscript, so only
the light-surface palette is used (no dark-mode toggle, no hover layer).
"""
import html
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(*parts):
    with open(os.path.join(ROOT, *parts)) as f:
        return json.load(f)


# --------------------------------------------------------------------------
# Palette (dataviz skill, references/palette.md -- light surface, unchanged)
# --------------------------------------------------------------------------

CAT = [
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"
BORDER = "rgba(11,11,11,0.10)"

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


# --------------------------------------------------------------------------
# Small SVG-building helpers (stdlib only)
# --------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s), quote=False)


def svg_open(width, height, title, desc):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family=\'{FONT}\' role="img" '
        f'aria-labelledby="svgtitle svgdesc">\n'
        f'<title id="svgtitle">{esc(title)}</title>\n'
        f'<desc id="svgdesc">{esc(desc)}</desc>\n'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{SURFACE}"/>\n'
    )


SVG_CLOSE = "</svg>\n"


def text(x, y, s, size=13, fill=INK_SECONDARY, anchor="start", weight="normal",
          italic=False):
    style = f'font-style:italic;' if italic else ""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" style="{style}">'
        f'{esc(s)}</text>\n'
    )


def tspan_block(x, y, lines, size=13, fill=INK_SECONDARY, anchor="start",
                 weight="normal", line_height=None):
    lh = line_height or (size * 1.35)
    out = [f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
           f'text-anchor="{anchor}" font-weight="{weight}">']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        out.append(f'<tspan x="{x:.2f}" dy="{dy:.2f}">{esc(ln)}</tspan>')
    out.append("</text>\n")
    return "".join(out)


def line(x1, y1, x2, y2, stroke=INK_MUTED, width=2, dash=None, cap="round"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="{cap}"{d}/>\n')


def circle(cx, cy, r, fill, ring=SURFACE, ring_w=2):
    return (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" '
            f'stroke="{ring}" stroke-width="{ring_w}"/>\n')


def diamond(cx, cy, r, fill, ring=SURFACE, ring_w=2):
    pts = f"{cx:.2f},{cy-r:.2f} {cx+r:.2f},{cy:.2f} {cx:.2f},{cy+r:.2f} {cx-r:.2f},{cy:.2f}"
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{ring}" '
            f'stroke-width="{ring_w}"/>\n')


def rect(x, y, w, h, fill, rx=4, stroke=None, stroke_w=1.5):
    s = f' stroke="{stroke}" stroke-width="{stroke_w}"' if stroke else ""
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'rx="{rx}" fill="{fill}"{s}/>\n')


def path(d, stroke=None, width=2, fill="none", cap="round", join="round"):
    f = f' fill="{fill}"'
    s = f' stroke="{stroke}" stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="{join}"' if stroke else ""
    return f'<path d="{d}"{f}{s}/>\n'


def arrow(x1, y, x2, stroke=INK_MUTED, width=2):
    out = line(x1, y, x2 - 8, y, stroke=stroke, width=width)
    out += path(f"M {x2-10:.2f} {y-5:.2f} L {x2:.2f} {y:.2f} L {x2-10:.2f} {y+5:.2f}",
                stroke=stroke, width=width, fill="none")
    return out


class Scale:
    """Linear scale from a data domain to a pixel range."""

    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v):
        if self.d1 == self.d0:
            return self.r0
        return self.r0 + (v - self.d0) * (self.r1 - self.r0) / (self.d1 - self.d0)


def nice_ticks(lo, hi, n=5):
    """Small stdlib replacement for a d3-style 'nice' tick generator."""
    if hi <= lo:
        hi = lo + 1.0
    raw_step = (hi - lo) / max(n, 1)
    # pick from {1,2,2.5,5,10} * magnitude
    exp = math.floor(math.log10(raw_step)) if raw_step > 0 else 0
    base = 10 ** exp
    for m in (1, 2, 2.5, 5, 10):
        step = m * base
        if step >= raw_step:
            break
    start = math.floor(lo / step) * step
    ticks = []
    v = start
    while v <= hi + step * 1e-9:
        ticks.append(round(v, 10))
        v += step
    return ticks


def fmt_num(v):
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s


def legend_row(x, y, items, size=12, swatch=10, gap=18, item_gap=110):
    """items: list of (label, color, shape) shape in {'line','square','diamond'}."""
    out = ""
    cx = x
    for label, color, shape in items:
        if shape == "line":
            out += line(cx, y - 4, cx + 18, y - 4, stroke=color, width=3)
            lx = cx + 18 + 6
        elif shape == "diamond":
            out += diamond(cx + 6, y - 4, 6, color)
            lx = cx + 18
        else:
            out += rect(cx, y - 10, 14, 10, color, rx=2)
            lx = cx + 14 + 6
        out += text(lx, y, label, size=size, fill=INK_SECONDARY)
        cx += item_gap
    return out


# --------------------------------------------------------------------------
# Figure 1: the validity chain
# --------------------------------------------------------------------------

def fig1_validity_chain(out_path):
    """Static diagram of Table 2 (DRAFT.md section 2.7): the four inferences
    in the chain and the threats each one carries. Labels are copied from the
    paper; there are no plotted numbers in this figure."""

    W, H = 1200, 620
    title = "The validity chain and its threats"
    desc = ("Diagram of the inference chain from a trace-derived score to its use: "
            "scoring, generalization, extrapolation, use. "
            "Each stage lists the threats mapped to it in the paper's Table 2.")

    stages = [
        ("Scoring", "does the score summarize\nthe person's behaviour?",
         ["Authorship contamination"]),
        ("Generalization", "is the baseline and the\ncomposite dependable?",
         ["Person heterogeneity"]),
        ("Extrapolation", "does a score change reflect\na state change?",
         ["Help-dependent indicators",
          "Version/context non-invariance",
          "Usage MNAR",
          "Criterion sampling and non-response"]),
        ("Use", "does acting on the score\nchange what it measures?",
         ["Consequences"]),
    ]

    n = len(stages)
    margin_x, top = 56, 150
    gap = 46
    box_w = (W - 2 * margin_x - (n - 1) * gap) / n
    header_h = 78
    row_h = 30
    max_threats = max(len(s[2]) for s in stages)
    box_h = header_h + 18 + max_threats * row_h + 20

    out = svg_open(W, H, title, desc)
    out += text(W / 2, 40, title, size=22, fill=INK_PRIMARY, anchor="middle", weight="600")
    out += text(W / 2, 66, "Table 2, section 2.7: each inference, then the threats its backing must answer",
                size=13, fill=INK_MUTED, anchor="middle", italic=True)

    y0 = top
    for i, (name, sub, threats) in enumerate(stages):
        x0 = margin_x + i * (box_w + gap)
        color = CAT[i % len(CAT)]

        out += rect(x0, y0, box_w, box_h, fill="#ffffff", rx=10, stroke=BORDER, stroke_w=1.5)
        out += rect(x0, y0, box_w, 6, fill=color, rx=3)

        out += tspan_block(x0 + 16, y0 + 32, [name], size=16.5, fill=INK_PRIMARY, weight="600")
        out += tspan_block(x0 + 16, y0 + 52, sub.split("\n"), size=11.5, fill=INK_MUTED,
                            line_height=14)

        ly = y0 + header_h + 16
        out += line(x0 + 16, ly - 10, x0 + box_w - 16, ly - 10, stroke=GRID, width=1)
        for t in threats:
            out += circle(x0 + 22, ly - 4, 4, fill=color, ring=SURFACE, ring_w=1)
            # wrap long threat labels at ~26 chars
            words = t.split(" ")
            lines_, cur = [], ""
            for w in words:
                trial = (cur + " " + w).strip()
                if len(trial) > 27 and cur:
                    lines_.append(cur)
                    cur = w
                else:
                    cur = trial
            if cur:
                lines_.append(cur)
            out += tspan_block(x0 + 34, ly, lines_, size=12.5, fill=INK_SECONDARY,
                                line_height=15)
            ly += row_h if len(lines_) == 1 else row_h + 14

        if i < n - 1:
            ay = y0 + box_h / 2
            out += arrow(x0 + box_w + 4, ay, x0 + box_w + gap - 4, stroke=INK_MUTED, width=2)

    out += text(margin_x, top + box_h + 44,
                "Backing for extrapolation (section 2.5: criterion sampling, criterion non-response) is folded "
                "into extrapolation above.",
                size=11.5, fill=INK_MUTED, italic=True)
    out += SVG_CLOSE

    with open(out_path, "w") as f:
        f.write(out)


# --------------------------------------------------------------------------
# Figure 2: sensitivity vs. false flags
# --------------------------------------------------------------------------

def fig2_sensitivity_vs_false_flags(out_path):
    metrics = load("sim", "metrics.json")["metrics"]
    curve = metrics["a_sensitivity_vs_false_flag_curve"]["curve"]
    chance = metrics["h_chance_baseline_sensitivity_vs_observed"]["by_architecture"]

    series_names = ["A-fixed", "A-naive"]
    colors = {"A-fixed": CAT[0], "A-naive": CAT[1]}

    all_x = []
    all_y = []
    for name in series_names:
        for pt in curve[name]:
            all_x.append(pt["fa_per_tracked_person_month"]["hi"])
            all_x.append(pt["fa_per_tracked_person_month"]["lo"])
            all_y.append(pt["sensitivity_within_21d"]["hi"])
            all_y.append(pt["sensitivity_within_21d"]["lo"])
    for name in series_names:
        all_x.append(chance[name]["realized_fa_per_tracked_person_month_on_S"])
        all_y.append(chance[name]["chance_sensitivity_within_21d"]["point"])

    x_lo, x_hi = 0.0, max(all_x) * 1.04
    y_lo, y_hi = 0.0, max(all_y) * 1.08

    W, H = 1200, 740
    ml, mr, mt, mb = 84, 200, 116, 90
    pw, ph = W - ml - mr, H - mt - mb

    title = "Detecting a planted drift: sensitivity vs. false flags"
    desc = ("Sensitivity within 21 days of a planted drift's onset against false "
            "flags per tracked person-month, swept over the detection threshold, for "
            "the fixed-baseline and naive architectures. Shaded bands are bootstrap "
            "intervals on sensitivity. Diamonds mark each architecture's chance "
            "baseline at its own realized false-flag rate.")

    out = svg_open(W, H, title, desc)
    out += text(W / 2, 36, title, size=20, fill=INK_PRIMARY, anchor="middle", weight="600")
    out += text(W / 2, 58, "Threshold swept from strict to loose; shaded bands are bootstrap intervals on sensitivity",
                size=12.5, fill=INK_MUTED, anchor="middle", italic=True)

    sx = Scale(x_lo, x_hi, ml, ml + pw)
    sy = Scale(y_lo, y_hi, mt + ph, mt)

    xt = nice_ticks(x_lo, x_hi, 6)
    yt = nice_ticks(y_lo, y_hi, 5)
    for t in yt:
        if t < y_lo - 1e-9 or t > y_hi + 1e-9:
            continue
        yy = sy(t)
        out += line(ml, yy, ml + pw, yy, stroke=GRID, width=1)
        out += text(ml - 12, yy + 4, fmt_num(t), size=12, fill=INK_MUTED, anchor="end")
    for t in xt:
        if t < x_lo - 1e-9 or t > x_hi + 1e-9:
            continue
        xx = sx(t)
        out += line(xx, mt, xx, mt + ph, stroke=GRID, width=1)
        out += text(xx, mt + ph + 22, fmt_num(t), size=12, fill=INK_MUTED, anchor="middle")

    out += line(ml, mt + ph, ml + pw, mt + ph, stroke=BASELINE, width=1.5)
    out += line(ml, mt, ml, mt + ph, stroke=BASELINE, width=1.5)
    out += text(ml + pw / 2, mt + ph + 56, "false flags per tracked person-month",
                size=14, fill=INK_SECONDARY, anchor="middle")
    out += (f'<text x="{ml-56:.2f}" y="{mt+ph/2:.2f}" font-size="14" fill="{INK_SECONDARY}" '
            f'text-anchor="middle" transform="rotate(-90 {ml-56:.2f} {mt+ph/2:.2f})">'
            f'sensitivity within 21 days of onset</text>\n')

    for name in series_names:
        color = colors[name]
        pts = curve[name]
        band_top = " ".join(f"{sx(p['fa_per_tracked_person_month']['point']):.2f},{sy(p['sensitivity_within_21d']['hi']):.2f}" for p in pts)
        band_bot = " ".join(f"{sx(p['fa_per_tracked_person_month']['point']):.2f},{sy(p['sensitivity_within_21d']['lo']):.2f}" for p in reversed(pts))
        out += f'<polygon points="{band_top} {band_bot}" fill="{color}" fill-opacity="0.12" stroke="none"/>\n'

        d = "M " + " L ".join(
            f"{sx(p['fa_per_tracked_person_month']['point']):.2f} {sy(p['sensitivity_within_21d']['point']):.2f}"
            for p in pts
        )
        out += path(d, stroke=color, width=2.5)
        for p in pts:
            out += circle(sx(p['fa_per_tracked_person_month']['point']),
                           sy(p['sensitivity_within_21d']['point']), 3.6, fill=color, ring=SURFACE, ring_w=1.2)

        last = pts[-1]
        first = pts[0]
        lx = sx(first['fa_per_tracked_person_month']['point'])
        ly_ = sy(first['sensitivity_within_21d']['point'])
        label_dx = 14 if name == "A-fixed" else 14
        out += text(lx + label_dx, ly_ - 10, name, size=13.5, fill=color, anchor="start", weight="600")

        cb = chance[name]
        cx_ = sx(cb["realized_fa_per_tracked_person_month_on_S"])
        cy_ = sy(cb["chance_sensitivity_within_21d"]["point"])
        out += diamond(cx_, cy_, 7, fill="#ffffff", ring=color, ring_w=2.5)

    # Direct label for the chance markers, placed beside them in the plot
    # area (not in the header, where it would collide with the title block).
    cb_fixed = chance["A-fixed"]
    cb_naive = chance["A-naive"]
    cx_lo = min(sx(cb_fixed["realized_fa_per_tracked_person_month_on_S"]),
                sx(cb_naive["realized_fa_per_tracked_person_month_on_S"]))
    cy_avg = (sy(cb_fixed["chance_sensitivity_within_21d"]["point"]) +
              sy(cb_naive["chance_sensitivity_within_21d"]["point"])) / 2
    out += text(cx_lo + 18, cy_avg + 4,
                "chance baseline: random flags at each", size=11.5, fill=INK_MUTED, italic=True)
    out += text(cx_lo + 18, cy_avg + 20,
                "architecture's own false-flag rate", size=11.5, fill=INK_MUTED, italic=True)

    leg_items = [(n, colors[n], "line") for n in series_names]
    out += legend_row(ml, 92, leg_items, item_gap=130)

    out += SVG_CLOSE
    with open(out_path, "w") as f:
        f.write(out)


# --------------------------------------------------------------------------
# Figure 4: contamination
# --------------------------------------------------------------------------

def fig4_contamination(out_path):
    pilot = load("pilot", "results.json")
    agg = pilot["aggregates"]
    by_class = agg["by_class"]

    total_entries = sum(v["entries"] for v in by_class.values())
    total_chars = sum(v["chars"] for v in by_class.values())

    class_order = ["tool-result", "sidechain", "injected", "lane-prompt", "human-typed"]
    class_labels = {
        "tool-result": "tool result",
        "sidechain": "subagent (sidechain)",
        "injected": "harness/hook injected",
        "lane-prompt": "automated prompt",
        "human-typed": "human-typed",
    }
    class_colors = {name: CAT[i] for i, name in enumerate(class_order)}

    shares = []
    for name in class_order:
        v = by_class.get(name, {"entries": 0, "chars": 0})
        shares.append((name, v["entries"] / total_entries, v["chars"] / total_chars))

    naive_mid = agg["indicators_middle_series_contamination"]["naive_vs_middle"]
    mid_typed = agg["indicators_middle_series_contamination"]["middle_vs_filtered"]
    naive_typed = agg["indicators_naive_vs_filtered_overall"]["report"]

    indicators = [
        ("late_share", "late-activity share"),
        ("fragmentation", "session fragmentation"),
        ("mean_log_len", "message length\n(mean log chars)"),
    ]
    comparisons = [
        ("naive vs typed", naive_typed, "correlation_naive_vs_filtered", CAT[0]),
        ("naive vs middle", naive_mid, "correlation", CAT[1]),
        ("middle vs typed", mid_typed, "correlation", CAT[2]),
    ]

    W, H = 1200, 830
    title = "Who wrote the \"user\" stream: contamination quantities"
    desc = ("Left: share of user-role entries and characters by authorship class, "
            "one person's agent-usage corpus. Right: day-level correlation between "
            "the naive, middle, and human-typed-only versions of three indicators; "
            "no indicator level or time series is shown, only agreement between "
            "authorship filters.")

    out = svg_open(W, H, title, desc)
    out += text(W / 2, 38, title, size=20, fill=INK_PRIMARY, anchor="middle", weight="600")
    out += text(W / 2, 60, "Section 4 corpus audit: authorship classes and cross-filter agreement, not levels over time",
                size=12.5, fill=INK_MUTED, anchor="middle", italic=True)

    # ---- Panel A: shares by authorship class (grouped horizontal bars) ----
    pa_x0, pa_y0 = 60, 160
    pa_w, pa_h = 520, 560
    out += text(pa_x0, pa_y0 - 22, "Share of the user-role stream, by authorship class",
                size=14.5, fill=INK_PRIMARY, weight="600")

    row_h = pa_h / len(class_order)
    bar_h = 15
    max_share = max(max(e, c) for _, e, c in shares) * 1.15
    label_w = 168
    plot_x0 = pa_x0 + label_w
    plot_w = pa_w - label_w - 10
    sxA = Scale(0, max_share, plot_x0, plot_x0 + plot_w)

    xt = nice_ticks(0, max_share, 4)
    for t in xt:
        if t > max_share:
            continue
        xx = sxA(t)
        out += line(xx, pa_y0, xx, pa_y0 + pa_h, stroke=GRID, width=1)
        out += text(xx, pa_y0 + pa_h + 20, f"{t*100:.0f}%", size=11.5, fill=INK_MUTED, anchor="middle")
    out += line(plot_x0, pa_y0 + pa_h, plot_x0 + plot_w, pa_y0 + pa_h, stroke=BASELINE, width=1.5)

    for i, (name, e_share, c_share) in enumerate(shares):
        ry = pa_y0 + i * row_h
        color = class_colors[name]
        out += text(pa_x0, ry + row_h / 2 + 4, class_labels[name], size=12.5, fill=INK_SECONDARY, anchor="start")

        y_e = ry + row_h / 2 - bar_h - 2
        y_c = ry + row_h / 2 + 2
        w_e = sxA(e_share) - plot_x0
        w_c = sxA(c_share) - plot_x0
        out += rect(plot_x0, y_e, max(w_e, 1), bar_h, fill=color, rx=3)
        out += rect(plot_x0, y_c, max(w_c, 1), bar_h, fill=color, rx=3)
        out += (f'<rect x="{plot_x0:.2f}" y="{y_c:.2f}" width="{max(w_c,1):.2f}" height="{bar_h}" rx="3" '
                f'fill="{color}" fill-opacity="0.55"/>\n')
        out += text(plot_x0 + max(w_e, 1) + 8, y_e + bar_h - 3, f"{e_share*100:.1f}%", size=10.5, fill=INK_MUTED)
        out += text(plot_x0 + max(w_c, 1) + 8, y_c + bar_h - 3, f"{c_share*100:.1f}%", size=10.5, fill=INK_MUTED)

    leg_y = pa_y0 + pa_h + 50
    out += rect(plot_x0, leg_y - 10, 14, 10, INK_MUTED, rx=2)
    out += text(plot_x0 + 20, leg_y, "share of entries", size=12, fill=INK_SECONDARY)
    out += (f'<rect x="{plot_x0+150:.2f}" y="{leg_y-10:.2f}" width="14" height="10" rx="2" '
            f'fill="{INK_MUTED}" fill-opacity="0.55"/>\n')
    out += text(plot_x0 + 170, leg_y, "share of characters", size=12, fill=INK_SECONDARY)

    # ---- Panel B: naive/middle/typed correlations by indicator ----
    pb_x0 = pa_x0 + pa_w + 70
    pb_w = W - pb_x0 - 60
    pb_y0 = 160
    pb_h = 470
    out += text(pb_x0, pb_y0 - 22, "Agreement between authorship filters, by indicator",
                size=14.5, fill=INK_PRIMARY, weight="600")

    all_vals = []
    for _, comp, key, _ in comparisons:
        for ind_key, _ in indicators:
            all_vals.append(comp[ind_key][key])
    y_lo = min(0, min(all_vals)) - 0.05
    y_hi = max(1.0, max(all_vals)) + 0.05
    syB = Scale(y_lo, y_hi, pb_y0 + pb_h, pb_y0)

    yt = nice_ticks(y_lo, y_hi, 5)
    for t in yt:
        if t < y_lo or t > y_hi:
            continue
        yy = syB(t)
        out += line(pb_x0, yy, pb_x0 + pb_w, yy, stroke=GRID, width=1)
        out += text(pb_x0 - 10, yy + 4, fmt_num(t), size=11.5, fill=INK_MUTED, anchor="end")
    zero_y = syB(0)
    out += line(pb_x0, zero_y, pb_x0 + pb_w, zero_y, stroke=BASELINE, width=1.5)

    group_w = pb_w / len(indicators)
    bar_w = 22
    inner_gap = 8
    n_comp = len(comparisons)
    group_content_w = n_comp * bar_w + (n_comp - 1) * inner_gap

    for gi, (ind_key, ind_label) in enumerate(indicators):
        gx0 = pb_x0 + gi * group_w + (group_w - group_content_w) / 2
        for ci, (clabel, comp, key, color) in enumerate(comparisons):
            v = comp[ind_key][key]
            bx = gx0 + ci * (bar_w + inner_gap)
            y_top = syB(max(v, 0))
            y_bot = syB(min(v, 0))
            h = max(abs(y_bot - y_top), 1)
            out += rect(bx, y_top, bar_w, h, fill=color, rx=3)
            vy = y_top - 6 if v >= 0 else y_bot + 16
            out += text(bx + bar_w / 2, vy, f"{v:.2f}", size=10, fill=INK_MUTED, anchor="middle")
        lines_ = ind_label.split("\n")
        out += tspan_block(gx0 + group_content_w / 2, pb_y0 + pb_h + 22, lines_,
                            size=12, fill=INK_SECONDARY, anchor="middle", line_height=14)

    leg_items = [(c[0], c[3], "square") for c in comparisons]
    out += legend_row(pb_x0, pb_y0 - 60, leg_items, item_gap=140)

    out += SVG_CLOSE
    with open(out_path, "w") as f:
        f.write(out)


# --------------------------------------------------------------------------
# Figure 3: selection and authorship
# --------------------------------------------------------------------------

def fig3_selection_and_authorship(out_path):
    results = load("sim", "results.json")
    metrics = load("sim", "metrics.json")["metrics"]

    p4 = results["predictions"]["P4"]
    q = metrics["q_current_vs_triggered_P4"]

    schedules = [
        ("all-days", p4["all_days"], CAT[0]),
        ("triggered", p4["triggered"], CAT[1]),
        ("current", q["current"], CAT[2]),
        ("mixed-IPW", p4["mixed_ipw"], CAT[3]),
    ]

    p6 = results["predictions"]["P6"]["pi_rises_with_D"]
    groups = [
        ("indicator 4", "raw", p6["ind4_att_formula_mean"], p6["ind4_att_mc_mean"]),
        ("indicator 4", "filtered", p6["ind4_filtered_att_formula_mean"], p6["ind4_filtered_att_mc_mean"]),
        ("indicator 5", "raw", p6["ind5_att_formula_mean"], p6["ind5_att_mc_mean"]),
        ("indicator 5", "filtered", p6["ind5_filtered_att_formula_mean"], p6["ind5_filtered_att_mc_mean"]),
    ]

    W, H = 1200, 640
    title = "Criterion sampling, and validity under rising agent share"
    desc = ("Left: the person-centred slope and correlation of the criterion on "
            "the composite on all days and on the days sampled by three criterion "
            "schedules (the CUSUM-triggered schedule, the current-score control, "
            "and the mixed schedule with inverse-probability weighting), "
            "with bootstrap intervals. Right: the predicted (formula) versus "
            "realized (simulated) attenuation ratio for indicators 4 and 5 when "
            "the agent-authored share rises with the state, raw and after "
            "authorship filtering.")

    out = svg_open(W, H, title, desc)
    out += text(W / 2, 36, title, size=19, fill=INK_PRIMARY, anchor="middle", weight="600")

    # ---- Left panel: slope & corr by schedule, horizontal dot-whisker ----
    lx0, ly0 = 60, 120
    lw, lh = 560, 440
    out += text(lx0, ly0 - 26, "Validity slope and correlation, by criterion schedule",
                size=14, fill=INK_PRIMARY, weight="600")

    all_vals = []
    for _, s, _ in schedules:
        for k in ("slope", "corr"):
            all_vals += [s[k]["lo"], s[k]["hi"]]
    x_lo, x_hi = 0, max(all_vals) * 1.08
    label_w = 100
    plot_x0 = lx0 + label_w
    plot_w = lw - label_w
    sxL = Scale(x_lo, x_hi, plot_x0, plot_x0 + plot_w)

    xt = nice_ticks(x_lo, x_hi, 5)
    for t in xt:
        if t > x_hi:
            continue
        xx = sxL(t)
        out += line(xx, ly0, xx, ly0 + lh, stroke=GRID, width=1)
        out += text(xx, ly0 + lh + 22, fmt_num(t), size=11.5, fill=INK_MUTED, anchor="middle")
    out += line(plot_x0, ly0 + lh, plot_x0 + plot_w, ly0 + lh, stroke=BASELINE, width=1.5)

    row_h = lh / len(schedules)
    measure_colors = {"slope": CAT[0], "corr": CAT[1]}
    for i, (name, s, _) in enumerate(schedules):
        ry = ly0 + i * row_h + row_h / 2
        out += text(lx0, ry + 4, name, size=12.5, fill=INK_SECONDARY, anchor="start")
        for j, k in enumerate(("slope", "corr")):
            v = s[k]
            dy = ry - 8 + j * 16
            color = measure_colors[k]
            x_pt = sxL(v["point"])
            out += line(sxL(v["lo"]), dy, sxL(v["hi"]), dy, stroke=color, width=2)
            out += line(sxL(v["lo"]), dy - 4, sxL(v["lo"]), dy + 4, stroke=color, width=2)
            out += line(sxL(v["hi"]), dy - 4, sxL(v["hi"]), dy + 4, stroke=color, width=2)
            out += circle(x_pt, dy, 5, fill=color, ring=SURFACE, ring_w=1.5)
            if i == 0:
                out += text(x_pt, dy - 10, k, size=10.5, fill=color, anchor="middle", weight="600")

    leg_items = [("slope", CAT[0], "line"), ("correlation", CAT[1], "line")]
    out += legend_row(plot_x0, ly0 - 44, leg_items, item_gap=110)

    # ---- Right panel: P6 attenuation, predicted vs realized ----
    rx0 = lx0 + lw + 70
    rw = W - rx0 - 60
    ry0 = 120
    rh = 400
    out += text(rx0, ry0 - 26, "Attenuation ratio when agent share rises with the state",
                size=14, fill=INK_PRIMARY, weight="600")

    vals = []
    for _, _, f, m in groups:
        vals += [f, m]
    y_lo = min(0, min(vals)) - 0.1
    y_hi = max(vals) + 0.15
    syR = Scale(y_lo, y_hi, ry0 + rh, ry0)

    yt = nice_ticks(y_lo, y_hi, 5)
    for t in yt:
        if t < y_lo or t > y_hi:
            continue
        yy = syR(t)
        out += line(rx0, yy, rx0 + rw, yy, stroke=GRID, width=1)
        out += text(rx0 - 10, yy + 4, fmt_num(t), size=11.5, fill=INK_MUTED, anchor="end")
    zero_y = syR(0)
    out += line(rx0, zero_y, rx0 + rw, zero_y, stroke=BASELINE, width=1.5)

    group_w = rw / len(groups)
    bar_w, inner_gap = 26, 10
    pair_w = 2 * bar_w + inner_gap
    formula_color, sim_color = CAT[4], CAT[5]
    for gi, (ind, kind, f_val, m_val) in enumerate(groups):
        gx0 = rx0 + gi * group_w + (group_w - pair_w) / 2
        for ci, (v, color) in enumerate(((f_val, formula_color), (m_val, sim_color))):
            bx = gx0 + ci * (bar_w + inner_gap)
            y_top = syR(max(v, 0))
            y_bot = syR(min(v, 0))
            h = max(abs(y_bot - y_top), 1)
            out += rect(bx, y_top, bar_w, h, fill=color, rx=3)
            vy = y_top - 6 if v >= 0 else y_bot + 16
            out += text(bx + bar_w / 2, vy, f"{v:.2f}", size=10, fill=INK_MUTED, anchor="middle")
        out += tspan_block(gx0 + pair_w / 2, ry0 + rh + 22, [ind, kind],
                            size=11.5, fill=INK_SECONDARY, anchor="middle", line_height=14)

    leg_items = [("predicted (formula)", formula_color, "square"),
                 ("realized (simulated)", sim_color, "square")]
    out += legend_row(rx0, ry0 - 44, leg_items, item_gap=170)

    out += text(rx0, ry0 + rh + 60,
                "Indicator 5, raw, crosses zero: its validity changes sign under rising agent share.",
                size=11.5, fill=INK_MUTED, italic=True)

    out += SVG_CLOSE
    with open(out_path, "w") as f:
        f.write(out)


def main():
    figs = [
        (fig1_validity_chain, "fig1_validity_chain.svg"),
        (fig2_sensitivity_vs_false_flags, "fig2_sensitivity_vs_false_flags.svg"),
        (fig3_selection_and_authorship, "fig3_selection_and_authorship.svg"),
        (fig4_contamination, "fig4_contamination.svg"),
    ]
    for fn, name in figs:
        out = os.path.join(HERE, name)
        fn(out)
        print("wrote", out)


if __name__ == "__main__":
    main()
