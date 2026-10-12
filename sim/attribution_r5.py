"""EXPLORATORY attribution round 5 (sim/ATTRIBUTION-PLAN-R5.md): r1's M1, M2, M2x3 on spec 003's five frozen
cells. Not part of sim/PREREG.md or sim/PREREG-003.md; changes no verdict. Imports drift_sim.py,
attribution.py and study003.py unchanged; the cells' alarms come from study003's own detector.

    python3 sim/attribution_r5.py --plan-sha <sha256 of sim/ATTRIBUTION-PLAN-R5.md>
    python3 sim/attribution_r5.py --check     # about a minute: includes a run_study comparison at n 60
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import attribution as a1
import drift_sim as ds
import study003 as s3

HERE = Path(__file__).parent
PLAN_PATH = HERE / "ATTRIBUTION-PLAN-R5.md"
PREREG_003_SHA = "06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79"
PHI, BL = 0.7, 28
S_FIRST = BL + a1.WINDOW - 1  # 41: first day whose Q window holds no baseline-fit day (D6)
# ci 1-5 as in study003.run_study; ci 0 is this round's reference cell (plan section a)
CELLS = [("reference", {}), ("kappa-0.3", dict(kappa=-0.3)), ("kappa+0.3", dict(kappa=0.3)),
         ("change_dep_0.3", dict(kappa_c=0.3)), ("m1_0.5", dict(m1=0.5)), ("m1_1.5", dict(m1=1.5))]
RULES = a1.RULES
DAY = np.arange(s3.T)[None, :]
TAKEN_SEEDS = {192815961, ds.TUNING_SEED, s3.DESIGN_SEED, 20261004}


def seed(plan_sha, tag):
    on_disk = s3.sha256(PLAN_PATH)
    if on_disk != plan_sha:
        sys.exit(f"--plan-sha does not match sha256(sim/ATTRIBUTION-PLAN-R5.md) = {on_disk}")
    v = int(hashlib.sha256(f"attribution-r5:{plan_sha}:{tag}".encode()).hexdigest()[:16], 16) % (2**32 - 1)
    assert v not in TAKEN_SEEDS, tag
    return v


def frozen():
    """Assert the frozen files are the ones PREREG-003 lists; return (h, tuning_003 q*, results_003)."""
    assert s3.sha256(HERE / "PREREG-003.md") == PREREG_003_SHA, "PREREG-003.md changed"
    prereg = (HERE / "PREREG-003.md").read_text()
    for f in ("study003.py", "tuning_003.json", "drift_sim.py", "attribution.py"):
        assert s3.sha256(HERE / f) in prereg, f"{f} differs from the sha256 PREREG-003 lists"
    res003 = json.loads((HERE / "results_003.json").read_text())
    assert res003["prereg_sha256"] == PREREG_003_SHA and res003["sha256"] == s3.provenance()
    tun = json.loads((HERE / "tuning_003.json").read_text())
    return tun["cells"][str(PHI)]["h"][str(BL)]["A-k0.5"], tun["q_star"], res003


def score(p, h):
    """The cell detector's alarms, reason, and the per-indicator z its composite averages (reason > 0 blanked)."""
    C, reason, _ = s3.detector_C(p, BL, "A")
    alarm = s3.cusum(C, h, ds.K_CUSUM)
    z, _, _, _ = s3.zscores(p, BL)
    return alarm, reason, np.where((reason > 0)[..., None], np.nan, z), C


def attribute(p, alarm, z, q_star):
    """attribution.attribute with every alarm scored: probes for t + 5 exist up to day 214 < T_GEN (D2)."""
    out = {r: np.zeros_like(alarm) for r in RULES}
    Q = np.full(alarm.shape, np.nan)
    for i, t in zip(*np.nonzero(alarm)):
        q = Q[i, t] = a1.q_stat(z, i, t)
        m1 = np.isnan(q) or q < q_star
        m23 = a1.confirmed(p, i, t, (1, 3, 5))
        out["M0"][i, t] = True
        out["M1"][i, t] = m1
        out["M2"][i, t] = a1.confirmed(p, i, t, (1,))
        out["M2x3"][i, t] = m23
        out["M3"][i, t] = m1 and m23
    return out, Q


def q_star_r1(plan_sha, h):
    """r1's q*: 90th percentile of Q over every DR-1.0 alarm in [t0, t0 + 21), reference-cell tuning panel."""
    p = s3.panels(seed(plan_sha, "tune"), PHI, ("DR-1.0",), cell=0, n=ds.N_PERSONS)["DR-1.0"]
    alarm, _, z, _ = score(p, h)
    t0 = p["t0"][:, None]
    qs = np.array([a1.q_stat(z, i, t) for i, t in zip(*np.nonzero(alarm & (DAY >= t0) & (DAY < t0 + 21)))])
    qs = qs[~np.isnan(qs)]
    return float(np.percentile(qs, a1.Q_PCTL)), int(len(qs))


def counts(p, h, q_star):
    """Per-person counts by rule in each window, plus diagnostics. S windows: s41 (primary), all (from 28)."""
    alarm, reason, z, _ = score(p, h)
    attr, Q = attribute(p, alarm, z, q_star)
    dr = not np.all(np.isnan(p["t0"]))
    if dr:
        t0 = p["t0"][:, None]
        wins = dict(w21=(DAY >= t0) & (DAY < t0 + 21), post=DAY >= t0)
    else:
        wins = dict(s41=DAY >= S_FIRST, all=DAY >= BL)
    c = {w: {r: (attr[r] & m).sum(1) for r in RULES} for w, m in wins.items()}
    ans1 = p["responded"][:, 1:s3.T + 1]  # answered on t + 1
    m = alarm & wins["w21" if dr else "s41"]
    diag = dict(answered_t1=((ans1 & m).sum(1), m.sum(1)), q_na=((np.isnan(Q) & alarm).sum(1), alarm.sum(1)))
    sel_w = wins["post" if dr else "s41"]
    ii, tt = np.nonzero(alarm & sel_w)
    D = p["D"]
    selection = dict(mean_D_alarm_day=float(D[ii, tt].mean()), mean_D_t_plus_1=float(D[ii, tt + 1].mean()),
                     mean_D_probe_days=float(((D[ii, tt + 1] + D[ii, tt + 3] + D[ii, tt + 5]) / 3).mean()),
                     mean_D_tracked=float(D[:, :s3.T][(reason == 0) & sel_w].mean()))
    tracked = (reason[:, BL:] == 0).sum(1) / 30.0
    sens = {r: ds._sensitivity(attr[r], p["t0"]).astype(float) for r in RULES} if dr else None
    return dict(c=c, diag=diag, selection=selection, tracked=tracked, sens=sens, n_alarms=int(alarm.sum()),
                n_alarms_window={w: int(v["M0"].sum()) for w, v in c.items()})


def stat_fns(S, D):
    """Named statistics of one cell as functions of one paired resample index."""
    f = {"S_rate_M0_per_tracked_month": s3.ratio(S["c"]["all"]["M0"], S["tracked"]),
         "DR_sens21_M0": s3.ratio(D["sens"]["M0"], np.ones_like(D["sens"]["M0"]))}
    for r in RULES[1:]:
        f[f"S_share_{r}"] = s3.ratio(S["c"]["s41"][r], S["c"]["s41"]["M0"])
        f[f"S_share_from28_{r}"] = s3.ratio(S["c"]["all"][r], S["c"]["all"]["M0"])
        f[f"DR_share_w21_{r}"] = s3.ratio(D["c"]["w21"][r], D["c"]["w21"]["M0"])
        f[f"DR_share_post_{r}"] = s3.ratio(D["c"]["post"][r], D["c"]["post"]["M0"])
        f[f"DR_sens21_{r}"] = s3.ratio(D["sens"][r], np.ones_like(D["sens"][r]))
        f[f"DR_sens21_ratio_{r}"] = s3.ratio(D["sens"][r], D["sens"]["M0"])
        f[f"separation_{r}"] = (lambda idx, r=r: f[f"DR_share_post_{r}"](idx) - f[f"S_share_{r}"](idx))
        f[f"separation_from28_{r}"] = (lambda idx, r=r: f[f"DR_share_post_{r}"](idx) - f[f"S_share_from28_{r}"](idx))
    for fam, X in (("S", S), ("DR", D)):
        f[f"{fam}_answered_t1"] = s3.ratio(*X["diag"]["answered_t1"])
        f[f"{fam}_Q_not_assessable"] = s3.ratio(*X["diag"]["q_na"])
    return f


CONTRASTS = ["S_share_M1", "S_share_M2", "S_share_M2x3", "DR_share_w21_M1", "DR_share_w21_M2",
             "DR_share_w21_M2x3", "separation_M2x3"]


def sanity(g, ref):
    """(r5 - frozen) / combined SE for the two quantities results_003 also reports (plan section d)."""
    pairs = (("S_rate_M0_per_tracked_month", ref["S_fa_per_month"]), ("DR_sens21_M0", ref["DR-1.0_sens21"]))
    return {k: dict(r5=g[k]["point"], results_003=v["est"],
                    z=(g[k]["point"] - v["est"]) / np.hypot(g[k]["se"], v["se"])) for k, v in pairs}


def run(plan_sha):
    h, q_star_003, res003 = frozen()
    q_star, n_q = q_star_r1(plan_sha, h)
    base = seed(plan_sha, "eval")
    rng = np.random.default_rng(seed(plan_sha, "boot"))
    n = s3.N_SCORE
    det = res003["detection"]["phi0.7_B28_A-k0.5"]
    frozen_ref = dict(res003["cells"], reference={"S_fa_per_month": det["S_fa_per_month"],
                                                  "DR-1.0_sens21": det["DR-1.0"]["sens21"]})
    res = dict(label="EXPLORATORY r5 (sim/ATTRIBUTION-PLAN-R5.md); not PREREG-003, not sim/PREREG.md; synthetic only",
               plan_sha256=plan_sha, prereg_003_sha256=PREREG_003_SHA, sha256=s3.provenance(), h=h,
               q_star=q_star, n_q_alarms=n_q, q_star_tuning_003_not_used=q_star_003, n=n, nboot=a1.B, cells={})
    fns = {}
    for ci, (name, kw) in enumerate(CELLS):
        P = s3.panels(base, PHI, ("S", "DR-1.0"), cell=ci, n=n, **kw)
        S, D = counts(P["S"], h, q_star), counts(P["DR-1.0"], h, q_star)
        fns[name] = stat_fns(S, D)
        g = dict(n_alarms_S=S["n_alarms"], n_alarms_S_window=S["n_alarms_window"], n_alarms_DR=D["n_alarms"],
                 n_alarms_DR_window=D["n_alarms_window"], selection_S=S["selection"], selection_DR=D["selection"])
        g.update({k: a1.boot(fn, rng, n) for k, fn in fns[name].items()})
        g["sanity_vs_results_003"] = sanity(g, frozen_ref[name])
        res["cells"][name] = g
    ref = fns["reference"]
    for name, _ in CELLS[1:]:
        f = fns[name]
        res["cells"][name]["minus_reference"] = {
            k: a1.boot(lambda i, j, k=k: f[k](i) - ref[k](j), rng, n, n) for k in CONTRASTS}
    res["expectations"] = expectations(res["cells"])
    return res


def expectations(c):
    """Plan section f, scored on point estimates."""
    pt = lambda cell, k: c[cell][k]["point"]
    d = lambda cell, k: c[cell]["minus_reference"][k]["point"]
    use, m = ("kappa-0.3", "kappa+0.3", "change_dep_0.3"), ("m1_0.5", "m1_1.5")
    k = pt("reference", "DR_share_w21_M1")
    e = {"K": dict(est=k, holds=abs(k - 0.9) < 0.05)}
    v1 = {f"{x}:{key}": d(x, key) for x in use + m for key in ("S_share_M1", "DR_share_w21_M1")}
    e["E1"] = dict(est=v1, holds=all(abs(v) < 0.05 for v in v1.values()))
    v2 = {r: [pt(x, f"DR_share_w21_{r}") for x in ("reference",) + m] for r in ("M2", "M2x3")}
    o2 = {r: v[2] / v[0] for r, v in v2.items()}
    e["E2"] = dict(est=dict(shares_ref_m05_m15=v2, m15_over_ref=o2),
                   holds=all(a > b > cc for a, b, cc in v2.values()) and o2["M2"] <= 0.5 and o2["M2x3"] <= 0.8)
    e["E3"] = dict(est=d("m1_1.5", "S_share_M2"), holds=d("m1_1.5", "S_share_M2") <= -0.10)
    e["E4"] = dict(est=dict(m1_15=pt("m1_1.5", "separation_M2x3"), reference=pt("reference", "separation_M2x3")),
                   holds=pt("m1_1.5", "separation_M2x3") < pt("reference", "separation_M2x3"))
    v5 = {f"{x}:{key}": d(x, key) for x in use for key in ("DR_share_w21_M2", "DR_share_w21_M2x3")}
    e["E5"] = dict(est=v5, holds=all(abs(v) < 0.05 for v in v5.values()))
    return e


def check():
    assert list(s3.probe_days(BL, 4)) == ds.PROBE_BASELINE_DAYS and ds.CONFIRM_MARGIN == s3.MARGIN
    h, _, _ = frozen()
    n = 300
    for kw in (dict(kappa_c=0.3), dict(m1=1.5)):
        P = s3.panels(7, PHI, ("S", "DR-1.0"), cell=3, n=n, **kw)
        pS, pD = P["S"], P["DR-1.0"]
        pre = np.arange(s3.T_GEN)[None, :] <= pD["t0"][:, None]  # D's ramp starts on t0 + 1
        assert np.array_equal(pS["L"], pD["L"]) and np.allclose(pS["Y"] - pS["D"], pD["Y"] - pD["D"])
        assert np.array_equal(pS["used"][pre], pD["used"][pre]) and np.array_equal(pS["responded"][pre], pD["responded"][pre])
        for p in P.values():
            alarm, reason, z, C = score(p, h)
            _, usable, _, _ = s3.zscores(p, BL)
            ok = (reason == 0)
            assert np.array_equal(~np.isnan(z), usable & ok[..., None]), "Q reads z the composite does not"
            err = np.nanmax(np.abs(np.nanmean(z[:, BL:], -1)[ok[:, BL:]] - C[:, BL:][ok[:, BL:]]))
            assert err < 1e-12, f"z do not average to the cell composite: {err}"
            assert not alarm[:, :BL].any() and alarm.any()
            assert p["Y"].shape[1] >= s3.T + 5
    # The frozen run_study's cell metrics, recomputed by this script's code on the same seed.
    tun = json.loads((HERE / "tuning_003.json").read_text())
    rs = s3.run_study(31337, tun, n=60)["cells"]
    for ci, (name, kw) in enumerate(CELLS[1:], start=1):
        P = s3.panels(31337, PHI, ("S", "DR-1.0"), cell=ci, n=60, **kw)
        f = stat_fns(counts(P["S"], h, 6.0), counts(P["DR-1.0"], h, 6.0))
        idx = np.arange(60)
        assert round(f["S_rate_M0_per_tracked_month"](idx), 4) == rs[name]["S_fa_per_month"]["est"], name
        assert round(f["DR_sens21_M0"](idx), 4) == rs[name]["DR-1.0_sens21"]["est"], name
    # Known answers for the rules on a hand panel: three alarms, one per outcome.
    T_ = s3.T_GEN
    hp = dict(Y=np.zeros((3, T_)), responded=np.ones((3, T_), dtype=bool))
    hp["Y"][:, [41, 43, 45]] = 0.6           # mean 0.6 against baseline 0: confirmed by M2 and M2x3
    hp["Y"][1, 41] = 0.4                     # M2 fails, M2x3 mean 0.53 holds
    hp["responded"][2, 41:46] = False        # no answer: neither confirms
    zh = np.zeros((3, s3.T, s3.J))
    zh[1, 27:41, 0] = 3.0                    # one indicator off: Q = (14 * 2.5^2 + 5 * 14 * 0.5^2) / 5 = 21
    alarm = np.zeros((3, s3.T), dtype=bool)
    alarm[:, 40] = True
    attr, Q = attribute(hp, alarm, zh, q_star=6.0)
    assert np.allclose(Q[:, 40], [0.0, 21.0, 0.0]), Q[:, 40]
    assert [attr[r][:, 40].tolist() for r in RULES] == [
        [True, True, True], [True, False, True], [True, False, False], [True, True, False], [True, False, False]]
    print("check OK: frozen hashes; probe block and margin match r1; S and DR-1.0 paired; Q reads exactly the z "
          "the cell composite averages; run_study's five cell M0 metrics reproduced at n 60; M0-M3 and Q known answers")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-sha")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    else:
        out = run(a.plan_sha)
        (HERE / "attribution_r5.json").write_text(json.dumps(out, indent=2) + "\n")
        print(json.dumps({k: v for k, v in out.items() if k != "cells"}, indent=1))
