"""Does L1_did's gain survive when D moves mapped and unmapped indicators unequally? (DESIGN STAGE, EXPLORATORY)
SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no real data is read. Scores no
prediction. Imports obs_003.py and its imports unchanged; the runtime patch is s3.apply_log (rule variants), restored.

    python3 sim/load_003.py      # -> sim/load_003.json

Variants, contrasts and expectations: sim/LOAD-003.md.
"""

import json
from pathlib import Path

import numpy as np

import absorb_003 as a3
import decide_003 as d3
import drift_sim as ds
import net_003 as n3
import obs_003 as o3
import study003 as s3

HERE = Path(__file__).parent
SEED, N, J = s3.DESIGN_SEED, s3.N, s3.J
APPLY_LOG, HZ = s3.apply_log, a3.HZ
UNM = [j for j in range(J) if j not in s3.PS_MAP]  # indicators 3, 4, 5 (0-based 2, 3, 4)
RHOS = (0.0, 0.5, 1.0, 2.0)


def scaled(f, c, rho):
    """DR+PS with D's effect on the unmapped indicators scaled by rho: c + rho * (f - c) on those indicators of
    every series the detector reads. f and c share every draw but the D step, so f - c is D's whole effect there
    (loading and context). rho = 1 returns f itself, so it reproduces obs_003.json bit for bit."""
    if rho == 1.0:
        return f
    v = dict(f)
    for k in ("X", "X_filtered", "X0", "Xf0"):
        a = f[k].copy()
        a[..., UNM] = c[k][..., UNM] + rho * (f[k][..., UNM] - c[k][..., UNM])
        v[k] = a
    return v


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    obs = json.loads((HERE / "obs_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, (f, c) = d3.alarms_fn(tun), n3.drps_pair()
    t0 = f["t0"]
    inwin = ~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    share = lambda x: s3.ratio(x * inwin, inwin * 1.0)
    XrC = s3.zscores(c, 28)[3]
    rules = {"L1": APPLY_LOG, "L2": APPLY_LOG, "oracle": APPLY_LOG,
             "L1_bothCF": a3.l1_variant(mean_src=XrC, sd_src=XrC),
             "L1_step": o3.step_rule(False), "L1_did": o3.step_rule(True)}
    base = {k: k[:2] if k.startswith("L") else k for k in rules}
    pairs = (("L1_did", "L1"), ("L1_did", "L1_step"), ("oracle", "L1_did"), ("L1_did", "L2"),
             ("L1_did", "L1_bothCF"))
    assert ds.REBASELINE_WINDOW == 14
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED, rhos=RHOS,
               n_inwin=int(inwin.sum()), unmapped=UNM,
               sha256={x: s3.sha256(HERE / x) for x in ("load_003.py", "obs_003.py", "absorb_003.py", "study003.py",
                                                        "decide_003.py", "net_003.py", "drift_sim.py",
                                                        "tuning_003.json", "obs_003.json")})
    bsd = a3.baseline(f)["sd"][:, list(s3.PS_MAP)]
    try:
        ch = {}  # no-D-change arm alarms: rho does not touch it
        for det in ("A-k0.5", "A-kstar"):
            for name, fn in rules.items():
                s3.apply_log = fn
                ch[(det, name)] = alarms(c, 28, det, base[name])[0]
        for rho in RHOS:
            v = scaled(f, c, rho)
            z, usable = s3.zscores(v, 28)[:2]
            r = {"step_error_inwin": {}}
            for did in (False, True):
                e = (o3.step_est(v, z, usable, list(s3.PS_MAP), did) - 0.5 / bsd)[inwin]
                r["step_error_inwin"]["did" if did else "raw"] = dict(mean=round(float(e.mean()), 4),
                                                                      sd=round(float(e.std()), 4))
            for det in ("A-k0.5", "A-kstar"):
                S, rd = {}, {}
                for name, fn in rules.items():
                    s3.apply_log = fn
                    af = alarms(v, 28, det, base[name])[0]
                    for hz in HZ:
                        sf, sc = (ds._sensitivity(a, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
                                  for a in (af, ch[(det, name)]))
                        S[(name, hz)] = sf - sc
                        rd[f"{name}_h{hz}"] = dict(raw=s3.boot(share(sf), N, brng), chance=s3.boot(share(sc), N, brng),
                                                   net=s3.boot(share(sf - sc), N, brng))
                        if rho == 1.0:  # reproduction of obs_003.json
                            ref = obs[f"W14_{det}"][f"{name}_inwin_h{hz}"]
                            assert all(rd[f"{name}_h{hz}"][k] == ref[k] for k in ("raw", "chance", "net")), (det, name, hz)
                for hz in HZ:
                    for a, b in pairs:
                        rd[f"{a}_minus_{b}_h{hz}"] = s3.boot(
                            lambda idx, xa=S[(a, hz)], xb=S[(b, hz)]: share(xa)(idx) - share(xb)(idx), N, brng)
                    if rho == 1.0:
                        assert rd[f"L1_did_minus_L1_h{hz}"] == obs[f"W14_{det}"][f"L1_did_minus_L1_inwin_h{hz}"]
                r[det] = rd
            if rho == 1.0:
                ref = obs["W14_step_error_inwin"]
                assert r["step_error_inwin"] == {"raw": ref["DR+PS_raw"], "did": ref["DR+PS_did"]}
            out[f"rho{rho}"] = r
    finally:
        s3.apply_log = APPLY_LOG
    (HERE / "load_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
