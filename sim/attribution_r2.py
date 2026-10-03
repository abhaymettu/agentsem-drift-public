"""EXPLORATORY attribution round 2, targeted help (sim/ATTRIBUTION-PLAN-R2.md). Not part of sim/PREREG.md.

Imports drift_sim.py and r1's attribution.py unchanged. One seed per family serves all three cells: the
help branch draws the same number of uniforms in every cell, so every other draw is identical and cell
contrasts are paired by person.

    python3 sim/attribution_r2.py --plan-sha <sha256 of sim/ATTRIBUTION-PLAN-R2.md>
    python3 sim/attribution_r2.py --check
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import attribution as a1
import drift_sim as ds
from attribution import DAY, LAST_ALARM, RULES

HERE = Path(__file__).parent
PLAN_PATH = HERE / "ATTRIBUTION-PLAN-R2.md"
CELLS = ["default", "targeted", "targeted_theta1_05"]
FAMILIES = ["S", "PS-sub", "PS-prop", "DR", "AV2", "CS"]
PAIRED = ["D", "Y", "responded", "used", "L_obs", "pi_t"]


def seed(plan_sha, *parts):
    tag = ":".join(["attribution-r2", plan_sha, *map(str, parts)]).encode()
    return int(hashlib.sha256(tag).hexdigest()[:16], 16) % (2**32 - 1)


def build(plan_sha, cell, n):
    """{family: (panel, change day)}. Seeds do not depend on the cell."""
    cp = ds.cell_params(cell)
    rec = a1.LamRecorder(np.random.default_rng(seed(plan_sha, "eval", "S")))
    s = ds.generate_panel(rec, "S", cp, n=n)
    rc = np.random.default_rng(seed(plan_sha, "cday", "S"))
    cday = rc.integers(50, 101, n).astype(float)
    ramp = rc.integers(7, 22, n).astype(float)
    panels = {"S": (s, cday)}
    for fam, tau in a1.ps_profiles(rec.lam, cday, ramp).items():
        panels[fam] = (a1.shift(s, tau), cday)
    for fam in ("DR", "AV2", "CS"):
        sd = seed(plan_sha, "eval", fam)
        p = ds.generate_panel(np.random.default_rng(sd), fam, cp, n=n)
        cd = {"DR": p["t0"], "AV2": p["av_day"],
              "CS": ds.sample_events(np.random.default_rng(sd), "CS", n)["cs_day"]}[fam]
        panels[fam] = (p, cd)
    return panels, rec.lam


def score_cell(panels, h, q_star):
    out = {}
    for fam, (p, cd) in panels.items():
        C, reason, alarm, z = a1.score_panel(p, h)
        attr, Q, scored = a1.attribute(p, alarm, z, q_star)
        post = (DAY >= np.maximum(cd, ds.BASELINE_DAYS)[:, None]) & (DAY <= LAST_ALARM)
        out[fam] = dict(p=p, cd=cd, C=C, reason=reason, attr=attr, Q=Q, scored=scored, post=post,
                        a_post={r: (attr[r] & post).sum(1) for r in RULES},
                        a_all={r: attr[r].sum(1) for r in RULES},  # every scored alarm, days 28-134
                        tracked=((reason == 0) & post).sum(1))
    return out


def share(f, r, key="a_post"):
    return lambda idx: f[key][r][idx].sum() / max(f[key]["M0"][idx].sum(), 1e-9)


def rate(f, r="M0"):
    """Per tracked person-month."""
    return lambda idx: f["a_post"][r][idx].sum() / (f["tracked"][idx].sum() / 30)


def help_counts(f):
    """Per person: helped scored-alarm days, scored-alarm days, helped tracked days, tracked days (28-134)."""
    A = f["p"]["A"]
    trk = (f["reason"] == 0) & (DAY >= ds.BASELINE_DAYS) & (DAY <= LAST_ALARM)
    return (A & f["scored"]).sum(1), f["scored"].sum(1), (A & trk).sum(1), trk.sum(1)


def help_gap(f):
    ha, na, ht, nt = help_counts(f)
    return lambda idx: ha[idx].sum() / na[idx].sum() - ht[idx].sum() / nt[idx].sum()


def summarize(sc, rng, n):
    res = {}
    for fam, f in sc.items():
        p, D = f["p"], f["p"]["D"]
        g = dict(n_scored_alarms_post=int(f["a_post"]["M0"].sum()))
        for r in RULES:
            g[f"rate_post_{r}"] = a1.boot(rate(f, r), rng, n)
        for r in RULES[1:]:
            g[f"share_post_{r}"] = a1.boot(share(f, r), rng, n)
        ii, tt = np.nonzero(f["scored"] & f["post"])
        g["selection"] = dict(
            mean_D_alarm_day=float(D[ii, tt].mean()), mean_D_t_plus_1=float(D[ii, tt + 1].mean()),
            mean_D_probe_days=float(((D[ii, tt + 1] + D[ii, tt + 3] + D[ii, tt + 5]) / 3).mean()),
            mean_D_tracked=float(D[(f["reason"] == 0) & f["post"]].mean()))
        g["share_Q_not_assessable"] = float(np.isnan(f["Q"][ii, tt]).mean())
        if fam == "DR":
            cd, attr = f["cd"], f["attr"]
            det0 = ds._sensitivity(attr["M0"], cd).astype(float)
            for r in RULES:
                det = ds._sensitivity(attr[r], cd).astype(float)
                g[f"sens21_{r}"] = a1.boot(lambda idx, d=det: d[idx].mean(), rng, n)
                if r != "M0":
                    g[f"sens21_ratio_{r}"] = a1.boot(lambda idx, d=det: d[idx].mean() / det0[idx].mean(), rng, n)
        if fam == "S":  # help on scored alarm days against tracked post-baseline days
            ha, na, ht, nt = help_counts(f)
            g["help_alarm_days"] = float(ha.sum() / na.sum())
            g["help_tracked_days"] = float(ht.sum() / nt.sum())
            g["help_alarm_minus_tracked"] = a1.boot(help_gap(f), rng, n)
            for r in RULES[1:]:
                g[f"share_all_{r}"] = a1.boot(share(f, r, "a_all"), rng, n)
        if fam.startswith("PS"):  # targeting probability the shift implies, minus the one drawn from
            s = sc["S"]
            Cp, Cs = f["C"][:, :-1], s["C"][:, :-1]
            m = f["post"][:, 1:] & (f["reason"][:, 1:] == 0) & ~np.isnan(Cp) & ~np.isnan(Cs)
            pt = lambda C: np.clip(ds.expit(ds.logit(0.3) + C), 0.1, 0.9)
            g["feedback_gap_p_target"] = float((pt(Cp) - pt(Cs))[m].mean())
        res[fam] = g
    dr, pp = sc["DR"], sc["PS-prop"]
    gap = {r: (lambda i, k, r=r: share(dr, r)(i) - share(pp, r)(k)) for r in ("M1", "M2x3")}
    for r, fn in gap.items():  # r1's A6 gaps; DR and PS-prop panels resampled independently
        res[f"A6_gap_{r}"] = a1.boot(fn, rng, n, n)
    res["A6_gap_M2x3_minus_M1"] = a1.boot(lambda i, k: gap["M2x3"](i, k) - gap["M1"](i, k), rng, n, n)
    return res


def contrast(x, y, rng, n):
    """Paired, x minus y, same persons: share differences and the M0 rate ratio, per family."""
    out = {}
    for fam in FAMILIES:
        fx, fy = x[fam], y[fam]
        g = {f"share_diff_{r}": a1.boot(lambda idx, r=r: share(fx, r)(idx) - share(fy, r)(idx), rng, n)
             for r in RULES[1:]}
        g["rate_ratio_M0"] = a1.boot(lambda idx: rate(fx)(idx) / rate(fy)(idx), rng, n)
        if fam == "S":  # B1 for S: every scored alarm, days 28-134 (S has no change)
            g["share_all_diff_M2x3"] = a1.boot(
                lambda idx: share(fx, "M2x3", "a_all")(idx) - share(fy, "M2x3", "a_all")(idx), rng, n)
        out[fam] = g
    return out


def run(plan_sha, n=ds.N_PERSONS):
    h = json.loads((HERE / "tuning.json").read_text())["h"]["A-fixed"]["h"]
    rng = np.random.default_rng(seed(plan_sha, "boot"))

    # q*: as r1, 90th percentile of Q over DR alarms in [t0, t0 + 21), default-cell tuning panel.
    tp = ds.generate_panel(np.random.default_rng(seed(plan_sha, "tune", "DR")), "DR",
                           ds.cell_params("default"), n=n)
    _, _, al, z = a1.score_panel(tp, h)
    win = (DAY >= tp["t0"][:, None]) & (DAY < tp["t0"][:, None] + 21) & (DAY >= ds.BASELINE_DAYS)
    qs = np.array([a1.q_stat(z, i, t) for i, t in zip(*np.nonzero(al & win))])
    qs = qs[~np.isnan(qs)]
    q_star = float(np.percentile(qs, a1.Q_PCTL))

    sc, lams = {}, []
    for cell in CELLS:
        panels, lam = build(plan_sha, cell, n)
        lams.append(lam)
        sc[cell] = score_cell(panels, h, q_star)
    assert all(np.array_equal(lams[0], m) for m in lams), "loadings differ across cells"
    for fam in FAMILIES:
        for c in CELLS[1:]:
            for k in PAIRED:
                a, b = sc["default"][fam]["p"][k], sc[c][fam]["p"][k]
                assert np.array_equal(a, b, equal_nan=True), f"{fam} {k} not paired, {c}"

    res = dict(label="EXPLORATORY (sim/ATTRIBUTION-PLAN-R2.md); not sim/PREREG.md; synthetic only",
               plan_sha256=plan_sha, h_A_fixed=h, q_star=q_star, n_tune_alarms=int(len(qs)),
               cells={c: summarize(sc[c], rng, n) for c in CELLS},
               contrasts={"targeted_minus_default": contrast(sc["targeted"], sc["default"], rng, n),
                          "theta1_05_minus_targeted": contrast(sc["targeted_theta1_05"], sc["targeted"], rng, n)})
    b3 = {c: (lambda i, f=sc[c]["PS-sub"], s=sc[c]["S"]: rate(f)(i) / rate(s)(i)) for c in ("default", "targeted")}
    for c, fn in b3.items():
        res[f"B3_PSsub_over_S_M0_{c}"] = a1.boot(fn, rng, n)
    res["B3_ratio_targeted_over_default"] = a1.boot(lambda i: b3["targeted"](i) / b3["default"](i), rng, n)
    sd, st = help_gap(sc["default"]["S"]), help_gap(sc["targeted"]["S"])
    res["B5_help_gap_targeted_minus_default"] = a1.boot(lambda idx: st(idx) - sd(idx), rng, n)
    return res


def check():
    a1.check()
    n = 200
    p = {c: ds.generate_panel(np.random.default_rng(1), "DR", ds.cell_params(c), n=n) for c in CELLS}
    for c in CELLS[1:]:
        for k in PAIRED:
            assert np.array_equal(p["default"][k], p[c][k], equal_nan=True), f"{c}: {k} not paired"
    assert not np.array_equal(p["default"]["A"], p["targeted"]["A"])
    # PS feedback gap reads the scored composite: with no version change it equals the targeting one.
    s = ds.generate_panel(np.random.default_rng(2), "S", ds.cell_params("targeted"), n=n)
    base = ds.fit_baseline(s["X"], s["used"], s["L_obs"])
    c0, _ = ds.compute_composite(s, ds.DEFAULT_FEATURES, baseline=base)
    c1, _ = ds.compute_composite(s, ds.ablation_features("iv"), baseline=base)
    assert np.array_equal(c0, c1, equal_nan=True), "(iv) changes the S composite"
    print(f"check OK: {', '.join(PAIRED)} identical across {', '.join(CELLS)} for one seed; "
          "help differs; scored composite equals the targeting composite on S")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-sha")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    else:
        on_disk = hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()
        if on_disk != a.plan_sha:
            sys.exit(f"--plan-sha does not match sha256(sim/ATTRIBUTION-PLAN-R2.md) = {on_disk}")
        out = run(a.plan_sha)
        (HERE / "attribution_r2.json").write_text(json.dumps(out, indent=2) + "\n")
        print(json.dumps({k: v for k, v in out.items() if k not in ("cells", "contrasts")}, indent=1))
