"""EXPLORATORY change-attribution run (sim/ATTRIBUTION-PLAN.md). Not part of sim/PREREG.md.

Imports drift_sim.py unchanged. PS families are post-hoc arithmetic on the S panel, so S, PS-sub and
PS-prop share persons, change days and draws (a paired design).

    python3 sim/attribution.py --plan-sha <sha256 of sim/ATTRIBUTION-PLAN.md>
    python3 sim/attribution.py --check     # z-decomposition, lam recording and shift self-test
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import drift_sim as ds

HERE = Path(__file__).parent
PLAN_PATH = HERE / "ATTRIBUTION-PLAN.md"
J = ds.N_IND
T = ds.T_DAYS
WINDOW = 14
MIN_DAYS = 3
MIN_IND = 3
Q_PCTL = 90
LAST_ALARM = 134  # alarms after this day cannot get M2x3's three probes (plan section c)
B = 2000
RULES = ["M0", "M1", "M2", "M2x3", "M3"]
DAY = np.arange(T)[None, :]


def seed(plan_sha, *parts):
    on_disk = hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()
    if on_disk != plan_sha:
        sys.exit(f"--plan-sha does not match sha256(sim/ATTRIBUTION-PLAN.md) = {on_disk}")
    tag = ":".join(["attribution", plan_sha, *map(str, parts)]).encode()
    return int(hashlib.sha256(tag).hexdigest()[:16], 16) % (2**32 - 1)


class LamRecorder:
    """Forwards to a real Generator; keeps what generate_panel's single `uniform` call (lam) returns."""

    def __init__(self, rng):
        self._rng, self.lam = rng, None

    def uniform(self, *a, **k):
        out = self._rng.uniform(*a, **k)
        assert self.lam is None, "generate_panel made a second uniform call"
        self.lam = out
        return out

    def __getattr__(self, name):
        return getattr(self._rng, name)


def ps_profiles(lam, cday, ramp):
    """tau (n, T, J) for PS-sub (step, +0.5 on 1, 2, 6) and PS-prop (lam_i x 1.0, DR's ramp)."""
    after = (DAY >= cday[:, None]).astype(float)
    sub = np.zeros((len(cday), T, J))
    for j in (ds.IDX_LATE, ds.IDX_FRAG, ds.IDX_LATENCY):
        sub[:, :, j] = 0.5 * after
    frac = np.clip((DAY - cday[:, None]) / ramp[:, None], 0, 1)
    prop = frac[:, :, None] * lam[:, None, :]
    return {"PS-sub": sub, "PS-prop": prop}


def shift(panel, tau):
    """Add intercept shifts tau (n, T, J). Indicators 4, 5 carry them in the human share only."""
    p = dict(panel)
    X, Xf, H = p["X"] + tau, p["X_filtered"] + tau, p["H"] + tau
    for j in (ds.IDX_MSGLEN, ds.IDX_NEGSELF):
        X[:, :, j] = p["X"][:, :, j] + (1 - p["pi_t"]) * tau[:, :, j]
        Xf[:, :, j] = p["X_filtered"][:, :, j] + (1 - p["pi_prime"]) * tau[:, :, j]
    p.update(X=X, X_filtered=Xf, H=H)
    return p


def score_panel(panel, h):
    """A-fixed composite, alarms and the per-indicator z-scores the composite averages."""
    base = ds.fit_baseline(panel["X"], panel["used"], panel["L_obs"])
    C, reason = ds.compute_composite(panel, ds.DEFAULT_FEATURES, baseline=base)
    alarm, _, _ = ds.run_cusum(C, h)
    z = np.full(panel["X"].shape, np.nan)
    for j in range(J):
        p = dict(panel)
        off = np.arange(J) != j
        p["X"] = panel["X"].copy()
        p["X_filtered"] = panel["X_filtered"].copy()
        p["X"][:, :, off] = np.nan
        p["X_filtered"][:, :, off] = np.nan
        z[:, :, j], _ = ds.compute_composite(p, ds.DEFAULT_FEATURES, baseline=base)
    return C, reason, alarm, z


def q_stat(z, i, t):
    w = z[i, max(0, t - WINDOW + 1):t + 1, :]
    n = (~np.isnan(w)).sum(0)
    keep = n >= MIN_DAYS
    if keep.sum() < MIN_IND:
        return np.nan
    d = np.nanmean(w[:, keep], 0)
    nk = n[keep]
    dbar = (nk * d).sum() / nk.sum()
    return (nk * (d - dbar) ** 2).sum() / (keep.sum() - 1)


def confirmed(panel, i, t, offsets):
    Yb = panel["Y"][i, ds.PROBE_BASELINE_DAYS]
    rb = panel["responded"][i, ds.PROBE_BASELINE_DAYS]
    ans = [panel["Y"][i, t + o] for o in offsets if panel["responded"][i, t + o]]
    if rb.sum() < 2 or not ans:
        return False
    return bool(np.mean(ans) - Yb[rb].mean() >= ds.CONFIRM_MARGIN)


def attribute(panel, alarm, z, q_star):
    """Per-rule (n, T) booleans: scored alarm read as person change."""
    scored = alarm & (DAY >= ds.BASELINE_DAYS) & (DAY <= LAST_ALARM)
    out = {r: np.zeros_like(alarm) for r in RULES}
    Q = np.full(alarm.shape, np.nan)
    for i, t in zip(*np.nonzero(scored)):
        q = Q[i, t] = q_stat(z, i, t)
        m1 = np.isnan(q) or q < q_star
        m23 = confirmed(panel, i, t, (1, 3, 5))
        out["M0"][i, t] = True
        out["M1"][i, t] = m1
        out["M2"][i, t] = confirmed(panel, i, t, (1,))
        out["M2x3"][i, t] = m23
        out["M3"][i, t] = m1 and m23
    return out, Q, scored


def boot(fn, rng, *ns):
    """Point + person bootstrap; one index array per independently resampled panel."""
    pt = fn(*map(np.arange, ns))
    bs = np.array([fn(*(rng.integers(0, k, k) for k in ns)) for _ in range(B)])
    return dict(point=float(pt), se=float(np.nanstd(bs, ddof=1)),
                lo=float(np.nanpercentile(bs, 2.5)), hi=float(np.nanpercentile(bs, 97.5)))


def ratio(num, den):
    return lambda idx: num[idx].sum() / max(den[idx].sum(), 1e-9)


def run(plan_sha):
    h = json.loads((HERE / "tuning.json").read_text())["h"]["A-fixed"]["h"]
    cell = ds.cell_params("default")
    n = ds.N_PERSONS
    rng_b = np.random.default_rng(seed(plan_sha, "boot"))

    # q*: 90th percentile of Q over DR alarms in [t0, t0 + 21), tuning panel.
    tp = ds.generate_panel(np.random.default_rng(seed(plan_sha, "tune", "DR")), "DR", cell)
    _, _, al, z = score_panel(tp, h)
    win = (DAY >= tp["t0"][:, None]) & (DAY < tp["t0"][:, None] + 21) & (DAY >= ds.BASELINE_DAYS)
    qs = np.array([q_stat(z, i, t) for i, t in zip(*np.nonzero(al & win))])
    qs = qs[~np.isnan(qs)]
    q_star = float(np.percentile(qs, Q_PCTL))

    rec = LamRecorder(np.random.default_rng(seed(plan_sha, "eval", "S")))
    s = ds.generate_panel(rec, "S", cell)
    rc = np.random.default_rng(seed(plan_sha, "cday", "S"))
    cday = rc.integers(50, 101, n).astype(float)
    ramp = rc.integers(7, 22, n).astype(float)
    panels = {"S": (s, cday)}
    for fam, tau in ps_profiles(rec.lam, cday, ramp).items():
        panels[fam] = (shift(s, tau), cday)
    for fam in ("DR", "AV2", "CS"):
        sd = seed(plan_sha, "eval", fam)
        p = ds.generate_panel(np.random.default_rng(sd), fam, cell)
        cd = {"DR": p["t0"], "AV2": p["av_day"],
              "CS": ds.sample_events(np.random.default_rng(sd), "CS", n)["cs_day"]}[fam]
        panels[fam] = (p, cd)

    res = dict(label="EXPLORATORY (sim/ATTRIBUTION-PLAN.md); not sim/PREREG.md; synthetic only",
               plan_sha256=plan_sha, h_A_fixed=h, q_star=q_star, n_tune_alarms=int(len(qs)),
               families={})
    per = {}
    for fam, (p, cd) in panels.items():
        C, reason, alarm, z = score_panel(p, h)
        attr, Q, scored = attribute(p, alarm, z, q_star)
        post = (DAY >= np.maximum(cd, ds.BASELINE_DAYS)[:, None]) & (DAY <= LAST_ALARM)
        tracked = ((reason == 0) & post).sum(1)
        tracked_all = ((reason == 0) & (DAY >= ds.BASELINE_DAYS) & (DAY <= LAST_ALARM)).sum(1)
        a_post = {r: (attr[r] & post).sum(1) for r in RULES}
        per[fam] = dict(a_post=a_post, tracked=tracked)
        f = dict(n_scored_alarms_post=int(a_post["M0"].sum()))
        for r in RULES:
            f[f"rate_post_{r}"] = boot(lambda idx, r=r: a_post[r][idx].sum() / (tracked[idx].sum() / 30), rng_b, n)
            f[f"share_post_{r}"] = boot(ratio(a_post[r], a_post["M0"]), rng_b, n)
        months = tracked_all.sum() / 30
        f["probes_per_pm"] = {"M2": float(scored.sum() / months), "M2x3": float(3 * scored.sum() / months),
                              "M3": float(3 * scored.sum() / months), "baseline_block": 4}
        ii, tt = np.nonzero(scored & post)
        D = p["D"]
        f["selection"] = dict(
            mean_D_alarm_day=float(D[ii, tt].mean()), mean_D_t_plus_1=float(D[ii, tt + 1].mean()),
            mean_D_probe_days=float(((D[ii, tt + 1] + D[ii, tt + 3] + D[ii, tt + 5]) / 3).mean()),
            mean_D_tracked=float(D[(reason == 0) & post].mean()))
        f["share_Q_not_assessable"] = float(np.isnan(Q[ii, tt]).mean())
        if fam == "DR":
            w21 = (DAY >= cd[:, None]) & (DAY < cd[:, None] + 21)
            a21 = {r: (attr[r] & w21).sum(1) for r in RULES}
            det0 = ds._sensitivity(attr["M0"], cd).astype(float)
            for r in RULES:
                f[f"share_window21_{r}"] = boot(ratio(a21[r], a21["M0"]), rng_b, n)
                det = ds._sensitivity(attr[r], cd).astype(float)
                f[f"sens21_{r}"] = boot(lambda idx, d=det: d[idx].mean(), rng_b, n)
                f[f"sens21_ratio_{r}"] = boot(lambda idx, d=det: d[idx].mean() / det0[idx].mean(), rng_b, n)
        res["families"][fam] = f

    ps, sp, dr, pp = per["PS-sub"], per["S"], per["DR"], per["PS-prop"]
    res["A1_ratio_PSsub_over_S_M0"] = boot(
        lambda idx: (ps["a_post"]["M0"][idx].sum() / ps["tracked"][idx].sum())
        / (sp["a_post"]["M0"][idx].sum() / sp["tracked"][idx].sum()), rng_b, n)
    for r in RULES[1:]:
        res[f"A2_PSsub_rate_{r}_over_M0"] = boot(ratio(ps["a_post"][r], ps["a_post"]["M0"]), rng_b, n)
    # A6: (DR share - PS-prop share) under M2x3 minus the same under M1; DR, PS-prop independent.
    def gap(r):
        return lambda i, k: (dr["a_post"][r][i].sum() / dr["a_post"]["M0"][i].sum()
                             - pp["a_post"][r][k].sum() / pp["a_post"]["M0"][k].sum())
    g23, g1 = gap("M2x3"), gap("M1")
    res["A6_gap_M1"] = boot(g1, rng_b, n, n)
    res["A6_gap_M2x3"] = boot(g23, rng_b, n, n)
    res["A6_gap_M2x3_minus_M1"] = boot(lambda i, k: g23(i, k) - g1(i, k), rng_b, n, n)
    res["K1_share_M1_DR_minus_PSprop"] = res["A6_gap_M1"]
    return res


def check():
    cell = ds.cell_params("default")
    rec = LamRecorder(np.random.default_rng(1))
    p = ds.generate_panel(rec, "S", cell, n=200)
    p_ref = ds.generate_panel(np.random.default_rng(1), "S", cell, n=200)
    assert np.array_equal(p["X"], p_ref["X"], equal_nan=True), "wrapper changed the draws"
    assert rec.lam.shape == (200, J) and rec.lam.min() >= 0.25 and rec.lam.max() <= 0.5
    h = json.loads((HERE / "tuning.json").read_text())["h"]["A-fixed"]["h"]
    C, reason, _, z = score_panel(p, h)
    ok = reason == 0
    err = np.nanmax(np.abs(np.nanmean(z, -1)[ok] - C[ok]))
    assert err < 1e-9, f"per-indicator z do not average to C: {err}"
    cday, ramp = np.full(200, 60.0), np.full(200, 10.0)
    tau = ps_profiles(rec.lam, cday, ramp)
    q = shift(p, tau["PS-prop"])
    d1 = q["X"][:, 75, ds.IDX_FRAG] - p["X"][:, 75, ds.IDX_FRAG]
    d4 = q["X"][:, 75, ds.IDX_MSGLEN] - p["X"][:, 75, ds.IDX_MSGLEN]
    m = ~np.isnan(d1)
    assert np.allclose(d1[m], rec.lam[m, ds.IDX_FRAG])
    assert np.allclose(d4[m], ((1 - p["pi_t"][:, 75]) * rec.lam[:, ds.IDX_MSGLEN])[m])
    d_mid = q["X"][:, 65, ds.IDX_FRAG] - p["X"][:, 65, ds.IDX_FRAG]
    m65 = ~np.isnan(d_mid)
    assert np.allclose(d_mid[m65], 0.5 * rec.lam[m65, ds.IDX_FRAG])  # halfway up a 10-day ramp
    assert np.array_equal(np.isnan(q["X"]), np.isnan(p["X"]))
    assert np.allclose(q["X"][:, :61], p["X"][:, :61], equal_nan=True)
    qs = shift(p, tau["PS-sub"])
    assert np.allclose(np.nan_to_num(qs["X"][:, 70, ds.IDX_MSGLEN] - p["X"][:, 70, ds.IDX_MSGLEN]), 0)
    print(f"check OK: draws unchanged by recorder; z decomposition max err {err:.2e}; "
          "PS-prop ramp and authorship scaling exact; PS-sub leaves 3, 4, 5 alone; pre-change days untouched")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-sha")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    else:
        out = run(a.plan_sha)
        (HERE / "attribution.json").write_text(json.dumps(out, indent=2) + "\n")
        print(json.dumps({k: v for k, v in out.items() if k != "families"}, indent=1))
