"""Which part of L1's re-baseline does what: a one-change-at-a-time chain from L1 to L1_step (DESIGN STAGE,
EXPLORATORY). SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no real data is read.
Scores no prediction. Imports step_003.py, obs_003.py, load_003.py, unlog_003.py and their imports unchanged; the
runtime patch is s3.apply_log (rule variants), restored.

    python3 sim/hyb_003.py      # -> sim/hyb_003.json

Chain, contrasts and expectations: sim/HYB-003.md.
"""

import json
from itertools import product
from pathlib import Path

import numpy as np

import absorb_003 as a3
import decide_003 as d3
import drift_sim as ds
import load_003 as l3
import net_003 as n3
import obs_003 as o3
import step_003 as st3
import study003 as s3
import unlog_003 as u3

HERE = Path(__file__).parent
SEED, N, J = s3.DESIGN_SEED, s3.N, s3.J
APPLY_LOG, HZ, DETS, SHIFTS, DARMS = s3.apply_log, a3.HZ, st3.DETS, st3.SHIFTS, st3.DARMS


def raw_step_on(sel):
    """L1, except that after the hold the indicators `sel(log map)` take the baseline z minus their raw hold-mean
    step (o3.step_est, no DiD), keeping the baseline mean and SD; the rest keep L1's re-baseline (hold mean and
    hold SD). The hold, reason 4 and the S reset are L1's."""
    def apply_log(p, z, usable, reason, Xr, rule, log_day=None, log_map=None):
        z1, u1, reason, reset = APPLY_LOG(p, z, usable, reason, Xr, rule, log_day, log_map)
        js = list(sel(p["log_map"] if log_map is None else log_map))
        zs = z1.copy()
        zs[..., js] = np.where(a3.windows(p)[1][..., None] & u1[..., js],
                               z[..., js] - o3.step_est(p, z, usable, js, False)[:, None, :], z1[..., js])
        return zs, u1, reason, reset
    return apply_log


# The chain: each rule changes one thing from the one before it.
RULES = {"L1": APPLY_LOG,
         "L1_hyb": raw_step_on(lambda lm: lm),          # mapped: hold SD -> baseline SD
         "L1_bsd": raw_step_on(lambda lm: range(J)),    # unmapped: hold SD -> baseline SD (re-centred, as L1)
         "L1_step": o3.step_rule(False)}                # unmapped: not re-centred
PAIRS = (("L1_hyb", "L1"), ("L1_bsd", "L1_hyb"), ("L1_step", "L1_bsd"), ("L1_bsd", "L1"))


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    obs = json.loads((HERE / "obs_003.json").read_text())
    load = json.loads((HERE / "load_003.json").read_text())
    step = json.loads((HERE / "step_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, (f, c) = d3.alarms_fn(tun), n3.drps_pair()
    t0 = f["t0"]
    inwin = ~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    share = lambda x: s3.ratio(x * inwin, inwin * 1.0)
    pt = lambda x: s3.boot(share(x), N, brng)
    diff = lambda xa, xb: s3.boot(lambda idx: share(xa)(idx) - share(xb)(idx), N, brng)
    assert ds.REBASELINE_WINDOW == 14

    def ind(p):
        """Per person, alarm in [t0, t0 + hz) for every (detector, rule, horizon)."""
        out = {}
        for det in DETS:
            for name, fn in RULES.items():
                s3.apply_log = fn
                a = alarms(p, 28, det, "L1")[0]
                for hz in HZ:
                    out[(det, name, hz)] = ds._sensitivity(a, t0, window=hz,
                                                           exclude_pre_onset_alarms=False).astype(float)
        return out

    def pairs(x, keys):
        """Paired contrasts over PAIRS for each statistic in x (name -> per-person array per (det, rule, hz))."""
        r = {}
        for det in DETS:
            for hz in HZ:
                for a, b in PAIRS:
                    r[f"{det}_{a}_minus_{b}_h{hz}"] = {s: diff(x[s][(det, a, hz)], x[s][(det, b, hz)]) for s in keys}
                    # the chain's three steps sum to L1_step - L1 (points, paired, same denominators)
                e = [r[f"{det}_{a}_minus_{b}_h{hz}"][keys[0]]["est"] for a, b in PAIRS[:3]]
                tot = pt(x[keys[0]][(det, "L1_step", hz)] - x[keys[0]][(det, "L1", hz)])["est"]
                assert abs(sum(e) - tot) < 3e-4, (det, hz, e, tot)  # four 4-dp rounded points
        return r

    sub = lambda A, B: {k: A[k] - B[k] for k in A}
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED, rhos=l3.RHOS,
               shifts=SHIFTS, n_inwin=int(inwin.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("hyb_003.py", "step_003.py", "unlog_003.py", "load_003.py",
                                                        "obs_003.py", "absorb_003.py", "study003.py",
                                                        "decide_003.py", "net_003.py", "attribution.py",
                                                        "drift_sim.py", "tuning_003.json", "obs_003.json",
                                                        "load_003.json", "step_003.json")})
    def per_rule(x, sfx, ref):
        """Share per (detector, rule, horizon); L1 and L1_step must equal ref(det, name, hz)."""
        r = {}
        for det, hz, name in product(DETS, HZ, RULES):
            v = r[f"{det}_{name}{sfx}_h{hz}"] = pt(x[(det, name, hz)])
            assert name not in ("L1", "L1_step") or v == ref(det, name, hz), (sfx, det, name, hz)
        return r

    try:
        Ic = ind(c)
        # Part 0: no-change alarm share (no D change, no unlogged shift) per rule, and the chain in it.
        out["0_nochange"] = {**per_rule(Ic, "", lambda d, n, h: obs[f"W14_{d}"][f"{n}_inwin_h{h}"]["chance"]),
                             **pairs({"share": Ic}, ("share",))}
        # Part A: the chain in D-dependent share across LOAD-003's rho sweep.
        for rho in l3.RHOS:
            net = sub(ind(l3.scaled(f, c, rho)), Ic)
            out[f"A_rho{rho}"] = {**per_rule(net, "", lambda d, n, h: load[f"rho{rho}"][d][f"{n}_h{h}"]["net"]),
                                  **pairs({"dd": net}, ("dd",))}
        # Part B: added false-alarm share from an unlogged unmapped shift, no D change.
        Icq = {}
        for arm, (s, lag) in SHIFTS.items():
            Icq[arm] = ind(u3.unlogged(c, s, lag))
            add = sub(Icq[arm], Ic)
            out[f"B_{arm}"] = {**per_rule(add, "_added", lambda d, n, h: step[f"B_{arm}"][f"{d}_{n}_added_h{h}"]),
                               **pairs({"added": add}, ("added",))}
        # Part C: the shift in both the D arm and the no-D-change arm (as STEP-003 part C): dd, added, and
        # trade = dd - added per person (1:1, CHOICE).
        for arm in DARMS:
            s, lag = SHIFTS[arm]
            dd, add = sub(ind(u3.unlogged(f, s, lag)), Icq[arm]), sub(Icq[arm], Ic)
            out[f"C_{arm}"] = {**per_rule(dd, "_dd", lambda d, n, h: step[f"C_{arm}"][f"{d}_{n}_h{h}"]["dd"]),
                               **pairs({"dd": dd, "added": add, "trade": sub(dd, add)}, ("trade", "dd", "added"))}
    finally:
        s3.apply_log = APPLY_LOG
    (HERE / "hyb_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
