"""EXPLORATORY attribution round 4, mechanisms (sim/ATTRIBUTION-PLAN-R4.md). Not part of sim/PREREG.md.

Rebuilds r3's S and DR panels from r3's plan hash (r3's alarm counts and M2x3 shares are reproduced and
asserted) plus a fresh replication set, and rescores them under counterfactual composites. drift_sim.py,
attribution.py, attribution_r2.py and attribution_r3.py are imported unchanged.

    python3 sim/attribution_r4.py --plan-sha <sha256 of sim/ATTRIBUTION-PLAN-R4.md>
    python3 sim/attribution_r4.py --check
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import attribution as a1
import attribution_r3 as a3
import drift_sim as ds
from attribution import DAY, LAST_ALARM

HERE = Path(__file__).parent
PLAN_PATH = HERE / "ATTRIBUTION-PLAN-R4.md"
R3_SHA = "4c378002ff32220ae7c13539aa3b1ff01af77b1dbd16aaeaa1b33f613fa2cf4b"
CELLS = a3.CELLS
VARIANTS = ["frozen", "matched_mean", "matched", "recentred", "matched_recentred", "share_rule"]
J45 = [ds.IDX_MSGLEN, ds.IDX_NEGSELF]
SHARE_CUT = 0.5


def panels(sha, cell, n):
    """r3's S and DR panels for `sha` (a3.build without the families r4 does not use), with change days."""
    s, dr = a3.gen(sha, "S", cell, n), a3.gen(sha, "DR", cell, n)
    cday = np.random.default_rng(a3.seed(sha, "cday", "S")).integers(50, 101, n).astype(float)
    return {"S": (s, cday), "DR": (dr, dr["t0"])}


def agent_gap(p):
    """Agent-text mean minus human mean, indicators 4 and 5, as the generator sets them: indicator 4's agent
    mean is MU_M4 SDs above H4's mean over used baseline days; indicator 5's is MU_M5."""
    hb = p["H"][:, :ds.BASELINE_DAYS][p["used"][:, :ds.BASELINE_DAYS]]
    return ds.MU_M4_DEFAULT * hb[:, ds.IDX_MSGLEN].std(ddof=1), ds.MU_M5 - hb[:, ds.IDX_NEGSELF].mean()


def variant(p, v):
    """The panel as scored under `v`. frozen: A-fixed as run (baseline of 4 and 5 fit on the unfiltered X,
    scored on X_filtered). matched: baseline fit on the scored X_filtered (matched_mean: its mean only, see
    `composite`). recentred: agent text moved to the human population mean in X and X_filtered. share_rule:
    matched, with 4 and 5 missing on days where pi' > 0.5."""
    X, Xf = p["X"].copy(), p["X_filtered"].copy()
    if "recentred" in v:
        for j, g in zip(J45, agent_gap(p)):
            X[:, :, j] -= p["pi_t"] * g
            Xf[:, :, j] -= p["pi_prime"] * g
    if v == "share_rule":
        Xf[:, :, J45] = np.where((p["pi_prime"] > SHARE_CUT)[..., None], np.nan, Xf[:, :, J45])
    if v in ("matched_mean", "matched", "matched_recentred", "share_rule"):
        X[:, :, J45] = Xf[:, :, J45]
    return dict(p, X=X, X_filtered=Xf)


def composite(p, v):
    """A-fixed composite of `p` scored under variant `v`; matched_mean keeps the frozen SD of 4 and 5 (fit on X)."""
    q = variant(p, v)
    base = ds.fit_baseline(q["X"], q["used"], q["L_obs"])
    if v == "matched_mean":
        base["sd"][:, J45] = ds.fit_baseline(p["X"], p["used"], p["L_obs"])["sd"][:, J45]
    return ds.compute_composite(q, ds.DEFAULT_FEATURES, baseline=base)


WIN = (DAY >= ds.BASELINE_DAYS) & (DAY <= LAST_ALARM)


def scored(C, h):
    return ds.run_cusum(C, h)[0] & WIN


def s_rate(sc, trk):
    """Scored alarms per tracked person-month, days 28-134."""
    a, t = sc.sum(1), trk.sum(1)
    return lambda idx: a[idx].sum() / (t[idx].sum() / 30)


def c_stats(C, trk):
    """Over tracked days 28-134: mean of C; pooled within-person SD; lag-1 within-person autocorrelation
    (products of person-centred C on consecutive tracked days over the sum of squares)."""
    k = trk.sum(1)
    s1 = np.where(trk, C, 0.0).sum(1)
    dev = np.where(trk, C - (s1 / np.maximum(k, 1))[:, None], 0.0)
    ss, xy = (dev ** 2).sum(1), (dev[:, 1:] * dev[:, :-1]).sum(1)
    return dict(mean=lambda i: s1[i].sum() / k[i].sum(),
                sd=lambda i: np.sqrt(ss[i].sum() / (k[i].sum() - (k[i] > 0).sum())),
                ac1=lambda i: xy[i].sum() / ss[i].sum())


def margins(p, alarms):
    """Per person, over scored alarms in `alarms`: count, M2x3-confirmed count, confirmable count (>= 2
    responded baseline probes and >= 1 responded probe on t+1, t+3, t+5), and over confirmable alarms the
    sums of mean true D on the responded probe days (level) and on the responded baseline probes (base)."""
    n = alarms.shape[0]
    out = {k: np.zeros(n) for k in ("all", "conf", "able", "level", "base", "margin")}
    bd = ds.PROBE_BASELINE_DAYS
    for i, t in zip(*np.nonzero(alarms)):
        out["all"][i] += 1
        out["conf"][i] += a1.confirmed(p, i, t, (1, 3, 5))
        rb = p["responded"][i, bd]
        days = [t + o for o in (1, 3, 5) if p["responded"][i, t + o]]
        if rb.sum() >= 2 and days:
            level, base = p["D"][i, days].mean(), p["D"][i, bd][rb].mean()
            out["able"][i] += 1
            out["level"][i] += level
            out["base"][i] += base
            out["margin"][i] += level - base
    return out


def run_set(sha, n, h, rng, reproduce=None):
    """Every M-A, M-B and M-C quantity for one panel set. `reproduce`: r3's JSON, to assert its numbers."""
    sc, res = {}, {}
    for cell in CELLS:
        for fam, (p, cd) in panels(sha, cell, n).items():
            for v in VARIANTS:
                C, reason = composite(p, v)
                sc[cell, fam, v] = dict(p=p, cd=cd, C=C, reason=reason, trk=(reason == 0) & WIN,
                                        scored=scored(C, h))
    all_i = np.arange(n)
    target = s_rate(sc["default", "S", "frozen"]["scored"], sc["default", "S", "frozen"]["trk"])(all_i)
    for (cell, fam, v), f in sc.items():
        if fam != "S":
            continue
        S, DR = f, sc[cell, "DR", v]
        h_star = ds.bisect(lambda x: s_rate(scored(S["C"], x), S["trk"])(all_i), 0.5, 20.0, target, n_iter=30)
        hit = s_rate(scored(S["C"], h_star), S["trk"])(all_i)
        assert 0.5 < h_star < 20 and abs(hit / target - 1) < 0.05, (cell, v, h_star, hit, target)
        DR["sens"] = ds._sensitivity(DR["scored"], DR["cd"]).astype(float)
        DR["sens_m"] = ds._sensitivity(scored(DR["C"], h_star), DR["cd"]).astype(float)
        cs = c_stats(S["C"], S["trk"])
        g = dict(h_star=h_star, n_S_alarms=int(S["scored"].sum()), n_DR_alarms=int(DR["scored"].sum()),
                 S_rate=a1.boot(s_rate(S["scored"], S["trk"]), rng, n),
                 DR_sens21=a1.boot(lambda i, d=DR["sens"]: d[i].mean(), rng, n),
                 DR_sens21_rate_matched=a1.boot(lambda i, d=DR["sens_m"]: d[i].mean(), rng, n),
                 S_pi_prime_gap=a1.boot(a3.pi_gap(S, "pi_prime"), rng, n),
                 S_pi_t_gap=a1.boot(a3.pi_gap(S, "pi_t"), rng, n),
                 **{f"S_C_{k}": a1.boot(fn, rng, n) for k, fn in cs.items()})
        if v == "share_rule":  # A4 diagnostics: usable baseline days of indicator 5 per person
            k = (~np.isnan(variant(S["p"], v)["X_filtered"][:, :ds.BASELINE_DAYS, ds.IDX_NEGSELF])).sum(1)
            g["baseline_days_ind5_share"] = {str(c): float((np.minimum(k, 4) == c).mean()) for c in range(5)}
            g["S_alarm_share_from_under_4_days"] = float(S["scored"][k < 4].sum() / S["scored"].sum())
        res[f"{cell}/{v}"] = g
    if reproduce:
        for cell in CELLS:
            for fam in ("S", "DR"):
                f = sc[cell, fam, "frozen"]
                post = (DAY >= np.maximum(f["cd"], ds.BASELINE_DAYS)[:, None]) & (DAY <= LAST_ALARM)
                got, want = int((f["scored"] & post).sum()), reproduce["cells"][cell][fam]["n_scored_alarms_post"]
                assert got == want, f"r3 not reproduced: {cell} {fam} {got} != {want}"

    def paired(fn_x, fn_y, op):
        return lambda i: op(fn_x(i), fn_y(i))
    con = {}
    for cell in CELLS[1:]:
        for v in VARIANTS:
            x, y = sc[cell, "S", v], sc["default", "S", v]
            dx, dy = sc[cell, "DR", v], sc["default", "DR", v]
            cx, cy = c_stats(x["C"], x["trk"]), c_stats(y["C"], y["trk"])
            con[f"{cell}_over_default/{v}"] = dict(
                S_rate_ratio=a1.boot(paired(s_rate(x["scored"], x["trk"]), s_rate(y["scored"], y["trk"]), np.divide), rng, n),
                DR_sens21_ratio=a1.boot(a1.ratio(dx["sens"], dy["sens"]), rng, n),
                DR_sens21_rate_matched_ratio=a1.boot(a1.ratio(dx["sens_m"], dy["sens_m"]), rng, n),
                S_C_mean_diff=a1.boot(paired(cx["mean"], cy["mean"], np.subtract), rng, n),
                S_C_sd_ratio=a1.boot(paired(cx["sd"], cy["sd"], np.divide), rng, n))

    # A2: share of the log S-rate gap (cell over default) that the matched baseline closes.
    def closure(cell, v):
        rr = {w: paired(s_rate(sc[cell, "S", w]["scored"], sc[cell, "S", w]["trk"]),
                        s_rate(sc["default", "S", w]["scored"], sc["default", "S", w]["trk"]), np.divide)
              for w in ("frozen", v)}
        return lambda i: 1 - np.log(rr[v](i)) / np.log(rr["frozen"](i))
    for v in ("matched_mean", "matched"):
        con[f"A2_closure_bernoulli_mix/{v}"] = a1.boot(closure("bernoulli_mix", v), rng, n)
    # A4: under bernoulli_mix, rate-matched DR sensitivity with the share rule over without (matched).
    a, b = sc["bernoulli_mix", "DR", "share_rule"]["sens_m"], sc["bernoulli_mix", "DR", "matched"]["sens_m"]
    con["A4_share_rule_over_matched_bernoulli_mix"] = a1.boot(a1.ratio(a, b), rng, n)
    # B1: default S, share of the alarm-day pi' gap left when the agent text is recentred.
    for base, rec in (("frozen", "recentred"), ("matched", "matched_recentred")):
        gx, gy = (a3.pi_gap(sc["default", "S", v], "pi_prime") for v in (rec, base))
        con[f"B1_gap_left_after_recentring_default/{base}"] = a1.boot(paired(gx, gy, np.divide), rng, n)

    # M-C, frozen scoring: confirmation margin on the r3 C1 rows (DR post-onset alarms; S every scored alarm).
    mc = {}
    for cell in CELLS:
        for fam in ("S", "DR"):
            f = sc[cell, fam, "frozen"]
            win = f["scored"] & ((DAY >= f["cd"][:, None]) if fam == "DR" else True)
            mc[cell, fam] = margins(f["p"], win)
    for cell in CELLS[1:]:
        for fam in ("S", "DR"):
            x, y = mc[cell, fam], mc["default", fam]
            g = {}
            for name, num, den in (("M2x3_share", "conf", "all"), ("confirmable_share", "able", "all"),
                                   ("level", "level", "able"), ("base", "base", "able"), ("margin", "margin", "able")):
                g[name + "_diff"] = a1.boot(paired(a1.ratio(x[num], x[den]), a1.ratio(y[num], y[den]), np.subtract),
                                            rng, n)
            con[f"MC_{fam}_{cell}_minus_default"] = g
            if reproduce:
                key = "share_post_M2x3" if fam == "DR" else "share_all_M2x3"
                r3c = reproduce["cells"]
                assert abs(x["conf"].sum() / x["all"].sum() - r3c[cell][fam][key]["point"]) < 1e-12, (cell, fam)
                want = r3c[cell][fam][key]["point"] - r3c["default"][fam][key]["point"]
                assert abs(g["M2x3_share_diff"]["point"] - want) < 1e-12, f"r3 M2x3 not reproduced: {cell} {fam}"
    return dict(by_cell_variant=res, contrasts=con, S_rate_target=target)


def run(plan_sha, n=ds.N_PERSONS):
    h = json.loads((HERE / "tuning.json").read_text())["h"]["A-fixed"]["h"]
    r3 = json.loads((HERE / "attribution_r3.json").read_text())
    rng = np.random.default_rng(a3.seed(f"r4:{plan_sha}", "boot"))
    return dict(label="EXPLORATORY (sim/ATTRIBUTION-PLAN-R4.md); not sim/PREREG.md; synthetic only",
                plan_sha256=plan_sha, h_A_fixed=h,
                r3_panels=run_set(R3_SHA, n, h, rng, reproduce=r3),
                replication=run_set(f"r4:{plan_sha}", n, h, rng))


def check():
    n = 200
    p = {c: a3.gen("check-r4", "S", c, n) for c in ("default", "bernoulli_mix")}
    b = p["bernoulli_mix"]
    assert np.nanmax(np.abs(b["X"][:, :, J45] - b["X_filtered"][:, :, J45])) < 1e-9, "bernoulli: X != X_filtered"
    d = p["default"]
    C0, _ = composite(d, "frozen")
    C1, _, _, _ = a1.score_panel(d, 3.334)
    assert np.array_equal(C0, C1, equal_nan=True), "frozen variant differs from attribution.score_panel"
    q = variant(d, "recentred")
    hb = d["H"][:, :ds.BASELINE_DAYS][d["used"][:, :ds.BASELINE_DAYS]].mean(0)
    big = d["pi_t"] > 0.5
    for j in J45:  # recovered agent text M = (X - (1 - pi) H) / pi now has the human mean
        M = (q["X"][:, :, j] - (1 - d["pi_t"]) * d["H"][:, :, j]) / d["pi_t"]
        assert abs(np.nanmean(M[big]) - hb[j]) < 0.03, (j, np.nanmean(M[big]), hb[j])
    s = variant(d, "share_rule")
    miss = np.isnan(s["X_filtered"][:, :, ds.IDX_NEGSELF]) & d["used"]
    assert np.array_equal(miss, (d["pi_prime"] > SHARE_CUT) & d["used"])
    assert np.array_equal(s["X"][:, :, J45], s["X_filtered"][:, :, J45], equal_nan=True)
    print("check OK: bernoulli X equals X_filtered on 4 and 5; frozen variant equals attribution.score_panel; "
          "recentred agent text has the human mean; share rule masks exactly pi' > 0.5 and the baseline matches")


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
            sys.exit(f"--plan-sha does not match sha256(sim/ATTRIBUTION-PLAN-R4.md) = {on_disk}")
        out = run(a.plan_sha)
        (HERE / "attribution_r4.json").write_text(json.dumps(out, indent=2) + "\n")
        print(json.dumps(out["r3_panels"]["contrasts"], indent=1)[:6000])
