"""L1_did's false-alarm route: an unlogged shift on the unmapped indicators, with no D change (DESIGN STAGE,
EXPLORATORY). SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no real data is
read. Scores no prediction. Imports obs_003.py and its imports unchanged; the runtime patch is s3.apply_log (rule
variants), restored.

    python3 sim/unlog_003.py      # -> sim/unlog_003.json

Arms, contrasts and expectations: sim/UNLOG-003.md.
"""

import json
from pathlib import Path

import numpy as np

import absorb_003 as a3
import attribution as at
import decide_003 as d3
import drift_sim as ds
import load_003 as l3
import net_003 as n3
import obs_003 as o3
import study003 as s3

HERE = Path(__file__).parent
SEED, N = s3.DESIGN_SEED, s3.N
APPLY_LOG, HZ, UNM = s3.apply_log, a3.HZ, l3.UNM
ARMS = {"conc0.25": (0.25, 0), "conc0.5": (0.5, 0), "post0.5": (0.5, 15)}  # (raw shift s, start day - c)


def unlogged(c, s, lag):
    """c plus an unlogged intercept shift s on the unmapped indicators from day cday + lag (human share only on
    indicators 4, 5, as the generator's observer shift). Applied to X0/Xf0 too: the oracle rule knows the
    logged change only."""
    day = np.arange(s3.T_GEN)[None, :]
    after = day >= np.where(np.isnan(c["cday"]), np.inf, c["cday"])[:, None] + lag
    tau = np.zeros(c["X"].shape)
    tau[..., UNM] = s * after[..., None]
    q, q0 = at.shift(c, tau), at.shift(dict(c, X=c["X0"], X_filtered=c["Xf0"]), tau)
    q.update(X0=q0["X"], Xf0=q0["X_filtered"])
    return q


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    obs = json.loads((HERE / "obs_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, (f, c) = d3.alarms_fn(tun), n3.drps_pair()
    t0 = f["t0"]
    inwin = ~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    share = lambda x: s3.ratio(x * inwin, inwin * 1.0)
    rules = {"L1": APPLY_LOG, "L2": APPLY_LOG, "oracle": APPLY_LOG,
             "L1_step": o3.step_rule(False), "L1_did": o3.step_rule(True)}
    base = {k: k[:2] if k.startswith("L") else k for k in rules}
    pairs = (("L1_did", "L1_step"), ("L1_did", "L2"), ("L1_did", "oracle"), ("L1_did", "L1"))
    assert ds.REBASELINE_WINDOW == 14
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED, arms=ARMS,
               n_inwin=int(inwin.sum()), unmapped=UNM,
               sha256={x: s3.sha256(HERE / x) for x in ("unlog_003.py", "load_003.py", "obs_003.py",
                                                        "absorb_003.py", "study003.py", "decide_003.py",
                                                        "net_003.py", "attribution.py", "drift_sim.py",
                                                        "tuning_003.json", "obs_003.json")})
    bsd = a3.baseline(c)["sd"][:, list(s3.PS_MAP)]

    def step_err(p):
        z, usable = s3.zscores(p, 28)[:2]
        r = {}
        for did in (False, True):
            e = (o3.step_est(p, z, usable, list(s3.PS_MAP), did) - 0.5 / bsd)[inwin]
            r["did" if did else "raw"] = dict(mean=round(float(e.mean()), 4), sd=round(float(e.std()), 4))
        return r

    ref_err = obs["W14_step_error_inwin"]
    err0 = step_err(c)
    assert err0 == {"raw": ref_err["noDchange_raw"], "did": ref_err["noDchange_did"]}
    z0, u0 = s3.zscores(c, 28)[:2]
    try:
        S0 = {}  # the no-shift arm's per-person alarm-in-horizon (obs_003's no-change arm)
        for det in ("A-k0.5", "A-kstar"):
            for name, fn in rules.items():
                s3.apply_log = fn
                a0 = alarms(c, 28, det, base[name])[0]
                for hz in HZ:
                    s0 = ds._sensitivity(a0, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
                    S0[(det, name, hz)] = s0
                    assert s3.boot(share(s0), N, brng) == obs[f"W14_{det}"][f"{name}_inwin_h{hz}"]["chance"]
        for arm, (s, lag) in ARMS.items():
            q = unlogged(c, s, lag)
            # Unmapped indicators' mean hold z shift, in baseline z: what the DiD reference reads from the shift.
            z1 = s3.zscores(q, 28)[0]
            h = a3.windows(c)[0][..., None] & u0
            dz = np.where(h, z1 - z0, np.nan)[..., UNM]
            r = {"step_error_inwin": step_err(q),
                 "unmapped_hold_z_shift_inwin": round(float(np.nanmean(np.nanmean(dz, axis=(1, 2))[inwin])), 4)}
            if lag > ds.REBASELINE_WINDOW:  # outside the hold, the step estimates cannot see the shift
                assert r["step_error_inwin"] == err0
            for det in ("A-k0.5", "A-kstar"):
                S, rd = {}, {}
                for name, fn in rules.items():
                    s3.apply_log = fn
                    a1 = alarms(q, 28, det, base[name])[0]
                    for hz in HZ:
                        s1 = ds._sensitivity(a1, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
                        s0 = S0[(det, name, hz)]
                        S[(name, hz)] = s1 - s0
                        rd[f"{name}_h{hz}"] = dict(shifted=s3.boot(share(s1), N, brng),
                                                   added=s3.boot(share(s1 - s0), N, brng))
                for hz in HZ:
                    for a, b in pairs:
                        rd[f"{a}_minus_{b}_added_h{hz}"] = s3.boot(
                            lambda idx, xa=S[(a, hz)], xb=S[(b, hz)]: share(xa)(idx) - share(xb)(idx), N, brng)
                r[det] = rd
            out[arm] = r
    finally:
        s3.apply_log = APPLY_LOG
    (HERE / "unlog_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
