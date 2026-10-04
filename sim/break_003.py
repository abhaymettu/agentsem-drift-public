"""When re-centring the unmapped indicators pays: L1_step - L1 in U = TPR - w * FPR when a share p of logged
changes carries a concurrent unlogged unmapped shift, across rho (DESIGN STAGE, EXPLORATORY). SYNTHETIC ONLY: D is
one invented, non-diagnostic wellbeing/functioning state; no real data is read. Scores no prediction. Imports
step_003.py, obs_003.py, load_003.py, unlog_003.py and their imports unchanged; the runtime patch is s3.apply_log
(rule variants), restored.

    python3 sim/break_003.py      # -> sim/break_003.json

Quantities, break-even and expectations: sim/BREAK-003.md.
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
SEED, N = s3.DESIGN_SEED, s3.N
APPLY_LOG, HZ, DETS, SHIFTS, DARMS = s3.apply_log, a3.HZ, st3.DETS, st3.SHIFTS, st3.DARMS
RULES = {"L1": APPLY_LOG, "L1_step": o3.step_rule(False)}
WS = (1, 2, 4)  # false-alarm weight w in U = TPR - w * FPR (CHOICE)
PS = (0.0, 0.5, 1.0)  # share p of persons with the concurrent shift (U is linear in p)


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    step = json.loads((HERE / "step_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, (f, c) = d3.alarms_fn(tun), n3.drps_pair()
    t0 = f["t0"]
    inwin = ~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    share = lambda x: s3.ratio(x * inwin, inwin * 1.0)
    bt = lambda fn: s3.boot(fn, N, brng)
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

    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED, rhos=l3.RHOS,
               shifts={a: SHIFTS[a] for a in DARMS}, ws=WS, ps=PS, n_inwin=int(inwin.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("break_003.py", "step_003.py", "unlog_003.py",
                                                        "load_003.py", "obs_003.py", "absorb_003.py", "study003.py",
                                                        "decide_003.py", "net_003.py", "attribution.py",
                                                        "drift_sim.py", "tuning_003.json", "step_003.json")})
    try:
        Ic = ind(c)
        Icq = {arm: ind(u3.unlogged(c, *SHIFTS[arm])) for arm in DARMS}
        for rho in l3.RHOS:
            fr = l3.scaled(f, c, rho)
            If, r = ind(fr), {}
            for arm in DARMS:
                Ifq = ind(u3.unlogged(fr, *SHIFTS[arm]))
                for det, hz in product(DETS, HZ):
                    k = lambda n: (det, n, hz)
                    D = lambda I: lambda idx: share(I[k("L1_step")])(idx) - share(I[k("L1")])(idx)
                    # L1_step - L1 in TPR and FPR, without (0) and with (s) the shift
                    T0, F0, Ts, Fs = D(If), D(Ic), D(Ifq), D(Icq[arm])
                    U = lambda w, p: lambda idx: (1 - p) * (T0(idx) - w * F0(idx)) + p * (Ts(idx) - w * Fs(idx))

                    def pstar(w):
                        """Share p up to which L1_step's U is at least L1's (0 if behind at p = 0; 1 if never
                        behind on [0, 1])."""
                        def fn(idx):
                            u0, u1 = U(w, 0)(idx), U(w, 1)(idx)
                            return 0.0 if u0 <= 0 else 1.0 if u1 >= 0 else u0 / (u0 - u1)
                        return fn

                    r[f"{arm}_{det}_h{hz}"] = dict(
                        T0=bt(T0), F0=bt(F0), Ts=bt(Ts), Fs=bt(Fs),
                        **{f"U_w{w}_p{p}": bt(U(w, p)) for w in WS for p in PS},
                        **{f"pstar_w{w}": bt(pstar(w)) for w in WS})
                    # reproduce STEP-003: part A (no shift, every rho), part B added and part C dd (rho 1)
                    dl = lambda I, J: diff(I[k("L1_step")] - J[k("L1_step")], I[k("L1")] - J[k("L1")])
                    assert dl(If, Ic) == step[f"A_rho{rho}"][f"{det}_L1_step_minus_L1_h{hz}"], (rho, arm, det, hz)
                    if rho == 1.0:
                        sc = step[f"C_{arm}"][f"{det}_L1_step_minus_L1_h{hz}"]
                        assert dl(Ifq, Icq[arm]) == sc["dd"], (arm, det, hz)
                        assert dl(Icq[arm], Ic) == sc["added"], (arm, det, hz)
                        # STEP-003's 1:1 trade is U at w 2, p 1, plus the no-change FPR difference
                        e = r[f"{arm}_{det}_h{hz}"]
                        assert abs(e["U_w2_p1.0"]["est"] + e["F0"]["est"] - sc["trade"]["est"]) < 3e-4
            out[f"rho{rho}"] = r
    finally:
        s3.apply_log = APPLY_LOG
    (HERE / "break_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
