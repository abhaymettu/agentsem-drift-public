"""L1_step vs L1, and the sensitivity-for-specificity trade with D and an unlogged unmapped shift in the same
persons (DESIGN STAGE, EXPLORATORY). SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning
state; no real data is read. Scores no prediction. Imports obs_003.py, load_003.py, unlog_003.py and their
imports unchanged; the runtime patch is s3.apply_log (rule variants), restored.

    python3 sim/step_003.py      # -> sim/step_003.json

Parts, contrasts and expectations: sim/STEP-003.md.
"""

import json
from pathlib import Path

import numpy as np

import absorb_003 as a3
import decide_003 as d3
import drift_sim as ds
import load_003 as l3
import net_003 as n3
import obs_003 as o3
import study003 as s3
import unlog_003 as u3

HERE = Path(__file__).parent
SEED, N = s3.DESIGN_SEED, s3.N
APPLY_LOG, HZ, DETS = s3.apply_log, a3.HZ, ("A-k0.5", "A-kstar")
RULES = {"L1": APPLY_LOG, "L2": APPLY_LOG, "oracle": APPLY_LOG,
         "L1_step": o3.step_rule(False), "L1_did": o3.step_rule(True)}
BASE = {k: k[:2] if k.startswith("L") else k for k in RULES}
SHIFTS = {**u3.ARMS, "conc-0.5": (-0.5, 0)}  # unlogged unmapped shift (s, start day - c)
DARMS = ("conc0.5", "conc-0.5", "post0.5")  # part C: the shift in both the D arm and the no-D-change arm
PAIRS = (("L1_step", "L1"), ("L1_did", "L1_step"))


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    load = json.loads((HERE / "load_003.json").read_text())
    unlog = json.loads((HERE / "unlog_003.json").read_text())
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
                a = alarms(p, 28, det, BASE[name])[0]
                for hz in HZ:
                    out[(det, name, hz)] = ds._sensitivity(a, t0, window=hz,
                                                           exclude_pre_onset_alarms=False).astype(float)
        return out

    sub = lambda A, B: {k: A[k] - B[k] for k in A}
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED, rhos=l3.RHOS,
               shifts=SHIFTS, n_inwin=int(inwin.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("step_003.py", "unlog_003.py", "load_003.py", "obs_003.py",
                                                        "absorb_003.py", "study003.py", "decide_003.py",
                                                        "net_003.py", "attribution.py", "drift_sim.py",
                                                        "tuning_003.json", "load_003.json", "unlog_003.json")})
    try:
        Ic, If = ind(c), ind(f)
        # Part A: L1_step - L1 in D-dependent share across LOAD-003's rho sweep.
        for rho in l3.RHOS:
            net = sub(ind(l3.scaled(f, c, rho)), Ic)
            r = {}
            for det in DETS:
                for hz in HZ:
                    for name in ("L1", "L1_step", "L1_did"):
                        assert pt(net[(det, name, hz)]) == load[f"rho{rho}"][det][f"{name}_h{hz}"]["net"]
                    r[f"{det}_L1_step_minus_L1_h{hz}"] = diff(net[(det, "L1_step", hz)], net[(det, "L1", hz)])
            out[f"A_rho{rho}"] = r
        # Part B: L1_step - L1 in added false-alarm share, unlogged shift, no D change.
        Icq = {}
        for arm, (s, lag) in SHIFTS.items():
            Icq[arm] = ind(u3.unlogged(c, s, lag))
            add = sub(Icq[arm], Ic)
            r = {}
            for det in DETS:
                for hz in HZ:
                    for name in RULES:
                        r[f"{det}_{name}_added_h{hz}"] = pt(add[(det, name, hz)])
                        if arm in unlog:
                            assert r[f"{det}_{name}_added_h{hz}"] == unlog[arm][det][f"{name}_h{hz}"]["added"]
                    r[f"{det}_L1_step_minus_L1_added_h{hz}"] = diff(add[(det, "L1_step", hz)], add[(det, "L1", hz)])
            out[f"B_{arm}"] = r
        # Part C: the same shift in the D arm and the no-D-change arm. dd = D-dependent share under the shift
        # (paired, same shift in both arms); dd_change = dd minus the no-shift D-dependent share (load rho 1);
        # trade = (dd_a - dd_b) - (added_a - added_b), sensitivity gain minus false-alarm cost weighted 1:1.
        dd0 = sub(If, Ic)
        for arm in DARMS:
            s, lag = SHIFTS[arm]
            dd, add = sub(ind(u3.unlogged(f, s, lag)), Icq[arm]), sub(Icq[arm], Ic)
            r = {}
            for det in DETS:
                for hz in HZ:
                    for name in RULES:
                        k = (det, name, hz)
                        r[f"{det}_{name}_h{hz}"] = dict(dd=pt(dd[k]), dd_change=pt(dd[k] - dd0[k]))
                    for a, b in PAIRS:
                        ka, kb = (det, a, hz), (det, b, hz)
                        r[f"{det}_{a}_minus_{b}_h{hz}"] = dict(
                            dd=diff(dd[ka], dd[kb]), added=diff(add[ka], add[kb]),
                            trade=diff(dd[ka] - add[ka], dd[kb] - add[kb]))
            out[f"C_{arm}"] = r
    finally:
        s3.apply_log = APPLY_LOG
    (HERE / "step_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
