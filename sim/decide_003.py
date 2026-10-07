"""Decision evidence for PREREG-003 (DESIGN STAGE, EXPLORATORY): the numbers behind DESIGN-003.md section 4's
proposals. SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no real data is read.
Scores no prediction. Imports study003.py, drift_sim.py and attribution.py unchanged; the only runtime patch is
ds.REBASELINE_WINDOW in part (c), restored after each arm.

    python3 sim/decide_003.py      # -> sim/decide_003.json

(a) Evaluation-N sizing: per drafted or proposed threshold, the chance an evaluation run of N persons lands on
    the design estimate's side of it (point, and 95% interval), taking the design estimate as true and
    SE ~ 1/sqrt(N); plus one empirical sqrt(N) check (H3, logged PS-sub L1/S) at N 1000 and 2000 on CHECK_SEED.
(b) Probe budget, spaced lag, 28 days, 4 probes, every phi: 'all' (every alarm probed, the design rule; must
    reproduce design_003.json), 'wait' (no new probes until the last probed alarm's third probe has been
    answered), 'stop' ('wait', and no probes after a person's first confirmed alarm).
(c) PS-prop mechanism, phi 0.7, A-fixed k = 0.5: logged PS-prop L1 and L2 against S by ramp tertile, and
    re-baseline windows 14 (must reproduce the design), 21 and 28, with PS-sub's ratios and DR+PS's logged
    21-day sensitivity (the hold's cost on true change) under each window.
"""

import json
from functools import reduce
from pathlib import Path
from statistics import NormalDist

import numpy as np

import drift_sim as ds
import study003 as s3

HERE = Path(__file__).parent
SEED = s3.DESIGN_SEED
CHECK_SEED = 20261004  # neither the tuning, design nor a PREREG-003 evaluation seed
NS = (1000, 2000, 4000)
Z = NormalDist()

# item -> (path in design_003.json, threshold, direction the prediction needs: +1 above, -1 below)
ITEMS = {
    "H1a S spaced-next_day <= -0.15": (("confirmation", "phi0.7_B28_m4_H1_S_spaced_minus_next_day"), -0.15, -1),
    "H1b DR-1.0 spaced/next_day >= 0.85": (("confirmation", "phi0.7_B28_m4_H1_DR-1.0_spaced_over_next_day"), 0.85, 1),
    "H1b proposed >= 0.70": (("confirmation", "phi0.7_B28_m4_H1_DR-1.0_spaced_over_next_day"), 0.70, 1),
    "H2a gap phi0.9 >= 0.10": (("confirmation", "phi0.9_B28_m4_spaced", "S_gap_block_minus_oracle"), 0.10, 1),
    "H2b 28-56 gap shrink >= 0.05": (("confirmation", "phi0.9_H2_gap_B28m4_minus_B56m4"), 0.05, 1),
    "H3 PS-sub L1/S < 1.5": (("policy_log", "A-k0.5", "PS-sub", "L1_logged_ratio_to_S"), 1.5, -1),
    "H3 PS-sub L2/S < 1.5": (("policy_log", "A-k0.5", "PS-sub", "L2_logged_ratio_to_S"), 1.5, -1),
    "H3 PS-use L1/S < 1.5": (("policy_log", "A-k0.5", "PS-use", "L1_logged_ratio_to_S"), 1.5, -1),
    "H3 PS-use L2/S < 1.5": (("policy_log", "A-k0.5", "PS-use", "L2_logged_ratio_to_S"), 1.5, -1),
    "H3 PS-sub L0/S > 1.5": (("policy_log", "A-k0.5", "PS-sub", "L0_logged_ratio_to_S"), 1.5, 1),
    "H3 PS-use L0/S > 1.5": (("policy_log", "A-k0.5", "PS-use", "L0_logged_ratio_to_S"), 1.5, 1),
    "H4 L2-L1 in window > 0": (("policy_log", "A-k0.5", "dr", "H4_L2_minus_L1_onset_in_window"), 0.0, 1),
    "H5 M1 DR-PSprop < 0.10": (("policy_log", "A-k0.5", "H5_M1_DR_minus_unlogged_PSprop"), 0.10, -1),
}


def sizing(design):
    """P(evaluation point, and 95% interval, on the side the prediction needs), true value = design estimate."""
    out = {}
    for name, (path, thr, sgn) in ITEMS.items():
        b = reduce(dict.__getitem__, path, design)
        r = dict(est=b["est"], se1000=b["se"], threshold=thr)
        for n in NS:
            m = sgn * (b["est"] - thr) / (b["se"] * np.sqrt(1000 / n))
            r[f"N{n}_p_point"] = round(Z.cdf(m), 3)
            r[f"N{n}_p_interval"] = round(Z.cdf(m - 1.96), 3)
        out[name] = r
    return out


def ratio_to_S(s, t_, sS, tS, w, n, brng):
    """Paired: the family's post-change rate over S's, same persons w and same post-change window."""
    return s3.boot(lambda idx: s3.ratio(s * w, t_ * w)(idx) / s3.ratio(sS * w, tS * w)(idx), n, brng)


def alarms_fn(tun):
    def alarms(p, B, det, rule="L0", **log):
        tc = tun["cells"][str(p["phi"])]
        k = {"A-k0.5": ds.K_CUSUM, "A-kstar": tc["k_star"], "oracle-D": s3.MARGIN}[det]
        C, reason, reset = s3.detector_C(p, B, "oracle-D" if det == "oracle-D" else "A", rule, **log)
        return s3.cusum(C, tc["h"][str(B)][det], k, reset), reason
    return alarms


def budget(tun, design, brng):
    alarms, out = alarms_fn(tun), {}
    B, m = 28, 4
    bd = s3.probe_days(B, m)
    for phi in s3.PHIS:
        P = s3.panels(SEED, phi, ("S", "DR-1.0", "DR-1.5"))
        lag = s3.lag_for(phi)
        for fam, p in P.items():
            p["phi"] = phi
            a, rr = alarms(p, B, "A-k0.5")
            tr = (rr[:, B:] == 0).sum(1) / 30.0
            onset = None if fam == "S" else p["t0"]
            r = {}
            for rule in ("all", "wait", "stop"):
                pr, n_c, n_t, n_f = s3.probe_rule(p, a, lag, bd, B, onset, rule)
                g = r[rule] = {"probes_per_tracked_month": s3.boot(s3.ratio(s3.M_CONF * pr + m, tr), s3.N, brng),
                               "probed_share_of_alarms": s3.boot(s3.ratio(pr, a[:, B:].sum(1) * 1.0), s3.N, brng)}
                if fam == "S":
                    g["confirmed_fa_per_tracked_month"] = s3.boot(s3.ratio(n_c, tr), s3.N, brng)
                else:
                    g["confirmed_ppv"] = s3.boot(s3.ratio(n_t, n_t + n_f), s3.N, brng)
                    g["persons_confirmed_in_window"] = s3.boot(s3.ratio((n_t > 0) * 1.0, np.ones(s3.N)), s3.N, brng)
            if phi == 0.7:  # the 'all' rule is the design rule: same persons, same numbers
                want = design["confirmation"][f"phi{phi}_B{B}_m{m}_spaced"][fam]["probes_per_tracked_month"]["est"]
                assert r["all"]["probes_per_tracked_month"]["est"] == want, (fam, want)
            out[f"phi{phi}_{fam}"] = r
    return out


def mechanism(tun, design, brng):
    alarms, out = alarms_fn(tun), {}
    phi, B, day = 0.7, 28, np.arange(s3.T)[None, :]
    rng, side = s3.seeds(SEED, phi, 0)
    ev = s3.events(side, "PS-prop", s3.N)
    Q = {"PS-prop": s3.gen(rng, ev, "PS-prop", n=s3.N, phi=phi)}
    Q.update(s3.panels(SEED, phi, ("S", "PS-sub", "DR+PS")))
    for p in Q.values():
        p["phi"] = phi
    ramp = ev["ps_ramp"]
    a_S, r_S = alarms(Q["S"], B, "A-k0.5")
    groups = {"all": np.ones(s3.N, dtype=bool), "ramp7-11": ramp <= 11, "ramp12-16": (ramp >= 12) & (ramp <= 16),
              "ramp17-21": ramp >= 17}
    w0 = ds.REBASELINE_WINDOW
    try:
        for W in (14, 21, 28):
            ds.REBASELINE_WINDOW = W
            r = {}
            for fam in ("PS-prop", "PS-sub"):
                p = Q[fam]
                post = (day >= p["cday"][:, None]) & (day >= B)
                lg = ~np.isnan(p["log_day"])
                sS, tS = (a_S & post).sum(1), ((r_S == 0) & post).sum(1) / 30.0
                for rule in ("L1", "L2"):
                    a, rr = alarms(p, B, "A-k0.5", rule)
                    s, t_ = (a & post).sum(1), ((rr == 0) & post).sum(1) / 30.0
                    for g, w in (groups.items() if fam == "PS-prop" else [("all", groups["all"])]):
                        r[f"{fam}_{rule}_{g}_logged_ratio_to_S"] = ratio_to_S(s, t_, sS, tS, w & lg, s3.N, brng)
            p = Q["DR+PS"]
            lg = ~np.isnan(p["log_day"])
            for rule in ("L0", "L1", "L2", "oracle"):
                a, _ = alarms(p, B, "A-k0.5", rule)
                s = ds._sensitivity(a, p["t0"], window=21, exclude_pre_onset_alarms=False).astype(float)
                r[f"DR+PS_{rule}_sens21_logged"] = s3.boot(s3.ratio(s * lg, lg * 1.0), s3.N, brng)
            out[f"W{W}"] = r
    finally:
        ds.REBASELINE_WINDOW = w0
    pl = design["policy_log"]["A-k0.5"]
    for key, want in (("PS-prop_L1_all_logged_ratio_to_S", pl["PS-prop"]["L1_logged_ratio_to_S"]),
                      ("PS-sub_L2_all_logged_ratio_to_S", pl["PS-sub"]["L2_logged_ratio_to_S"]),
                      ("DR+PS_L1_sens21_logged", pl["dr"]["DR+PS_L1_sens21_logged"])):
        assert out["W14"][key]["est"] == want["est"], (key, want)
    out["n_logged_by_ramp"] = {g: int((w & ~np.isnan(Q["PS-prop"]["log_day"])).sum()) for g, w in groups.items()}
    return out


def sqrt_n_check(tun):
    """H3's logged PS-sub L1/S ratio and its bootstrap SE at N 1000 and 2000 on CHECK_SEED."""
    alarms, out, n0 = alarms_fn(tun), {}, s3.N
    try:
        for n in (1000, 2000):
            s3.N = n
            brng = np.random.default_rng([CHECK_SEED, 99]).integers(0, n, (s3.NBOOT, n))
            Q = s3.panels(CHECK_SEED, 0.7, ("S", "PS-sub"))
            day = np.arange(s3.T)[None, :]
            for p in Q.values():
                p["phi"] = 0.7
            p = Q["PS-sub"]
            post = (day >= p["cday"][:, None]) & (day >= 28)
            w = ~np.isnan(p["log_day"])
            a_S, r_S = alarms(Q["S"], 28, "A-k0.5")
            a, rr = alarms(p, 28, "A-k0.5", "L1")
            out[f"N{n}"] = ratio_to_S((a & post).sum(1), ((rr == 0) & post).sum(1) / 30.0, (a_S & post).sum(1),
                                      ((r_S == 0) & post).sum(1) / 30.0, w, n, brng)
    finally:
        s3.N = n0
    out["se_ratio_1000_over_2000"] = round(out["N1000"]["se"] / out["N2000"]["se"], 3)
    return out


def main():
    design = json.loads((HERE / "design_003.json").read_text())
    tun = json.loads((HERE / "tuning_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, s3.N, (s3.NBOOT, s3.N))  # the design run's matrix
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED, check_seed=CHECK_SEED,
               sha256={f: s3.sha256(HERE / f) for f in ("decide_003.py", "study003.py", "tuning_003.json",
                                                        "design_003.json", "drift_sim.py", "attribution.py")},
               sizing=sizing(design), budget=budget(tun, design, brng), mechanism=mechanism(tun, design, brng),
               sqrt_n_check=sqrt_n_check(tun))
    (HERE / "decide_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
