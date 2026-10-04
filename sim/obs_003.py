"""An implementable fix for L1's ramp absorption: re-estimate only the observer step (DESIGN STAGE, EXPLORATORY)
SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no real data is read. Scores no
prediction. Imports study003.py, decide_003.py, net_003.py, absorb_003.py and drift_sim.py unchanged; the runtime
patches are s3.apply_log (rule variants) and ds.REBASELINE_WINDOW, both restored.

    python3 sim/obs_003.py      # -> sim/obs_003.json

Rules, contrasts and expectations: sim/OBS-003.md.
"""

import json
from pathlib import Path

import numpy as np

import absorb_003 as a3
import decide_003 as d3
import drift_sim as ds
import net_003 as n3
import study003 as s3

HERE = Path(__file__).parent
SEED, N, T, J = s3.DESIGN_SEED, s3.N, s3.T, s3.J
APPLY_LOG, HZ = s3.apply_log, a3.HZ
OMIT6 = s3.PS_MAP[:2]  # a log map that misses indicator 6, which the observer change does shift


def step_est(p, z, usable, lm, did):
    """Observer step on the mapped indicators `lm`, in baseline z: their hold-mean z, minus (if `did`) the mean
    hold z of the unmapped indicators, which reads the person's concurrent change where the logged change does
    not act (0 when no unmapped indicator has 2 hold days)."""
    h = a3.windows(p)[0][..., None] & usable  # hold-mean z per indicator, needs >= 2 usable hold days
    cnt = h.sum(1)
    ok = cnt >= 2
    m = np.where(ok, np.where(h, z, 0.0).sum(1) / np.maximum(cnt, 1), 0.0)
    um = [j for j in range(J) if j not in lm]
    ref = np.where(ok[:, um], m[:, um], 0.0).sum(1) / np.maximum(ok[:, um].sum(1), 1)
    return m[:, lm] - ref[:, None] * did


def step_rule(did):
    """L1 or L2 (by `rule`) with the post-hold re-baseline replaced by the baseline z minus an estimated observer
    step on the mapped indicators; unmapped indicators keep the baseline z. Baseline mean and SD are kept. The
    hold, reason 4 and L1's S reset are the rule's."""
    def apply_log(p, z, usable, reason, Xr, rule, log_day=None, log_map=None):
        z1, u1, reason, reset = APPLY_LOG(p, z, usable, reason, Xr, rule, log_day, log_map)
        lm = list(p["log_map"] if log_map is None else log_map)
        zs = z.copy()
        zs[..., lm] -= step_est(p, z, usable, lm, did)[:, None, :]
        return np.where(a3.windows(p)[1][..., None] & u1, zs, z1), u1, reason, reset
    return apply_log


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    net = json.loads((HERE / "net_003.json").read_text())
    absorb = json.loads((HERE / "absorb_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, (f, c) = d3.alarms_fn(tun), n3.drps_pair()
    assert f["log_exo"] and tuple(f["log_map"]) == s3.PS_MAP
    t0 = f["t0"]
    logged = ~np.isnan(f["log_day"])
    inwin = logged & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    pops = {"inwin": inwin, "logged": logged}
    share = lambda x, w: s3.ratio(x * w, w * 1.0)
    XrC = s3.zscores(c, 28)[3]
    # name: (rule passed to the scorer, apply_log, log kwargs)
    rules = {"L0": ("L0", APPLY_LOG, {}), "L1": ("L1", APPLY_LOG, {}), "L2": ("L2", APPLY_LOG, {}),
             "oracle": ("oracle", APPLY_LOG, {}),
             "L1_bothCF": ("L1", a3.l1_variant(mean_src=XrC, sd_src=XrC), {}),
             "L1_step": ("L1", step_rule(False), {}), "L1_did": ("L1", step_rule(True), {}),
             "L2_did": ("L2", step_rule(True), {}),
             "L2_om6": ("L2", APPLY_LOG, dict(log_map=OMIT6)),
             "L1_did_om6": ("L1", step_rule(True), dict(log_map=OMIT6))}
    pairs = (("L1_did", "L1"), ("L2_did", "L2"), ("L1_did_om6", "L1"))
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED,
               n_inwin=int(inwin.sum()), n_logged=int(logged.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("obs_003.py", "absorb_003.py", "study003.py",
                                                        "decide_003.py", "net_003.py", "drift_sim.py",
                                                        "tuning_003.json", "net_003.json", "absorb_003.json")})
    w0 = ds.REBASELINE_WINDOW
    try:
        for W in (14, 21):
            ds.REBASELINE_WINDOW = W
            # Step-estimate error on the mapped indicators, in baseline z (true step: 0.5 / baseline SD).
            bsd = a3.baseline(f)["sd"][:, list(s3.PS_MAP)]
            err = {}
            for arm, p in (("DR+PS", f), ("noDchange", c)):
                z, usable = s3.zscores(p, 28)[:2]
                for did in (False, True):
                    e = (step_est(p, z, usable, list(s3.PS_MAP), did) - 0.5 / bsd)[inwin]
                    err[f"{arm}_{'did' if did else 'raw'}"] = dict(mean=round(float(e.mean()), 4),
                                                                   sd=round(float(e.std()), 4))
            out[f"W{W}_step_error_inwin"] = err
            for det in ("A-k0.5", "A-kstar"):
                r, S = {}, {}
                for name, (rule, fn, kw) in rules.items():
                    s3.apply_log = fn
                    af, ac = (alarms(p, 28, det, rule, **kw)[0] for p in (f, c))
                    for hz in HZ:
                        sf, sc = (ds._sensitivity(a, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
                                  for a in (af, ac))
                        S[(name, hz)] = sf, sc
                        for g, w in pops.items():
                            r[f"{name}_{g}_h{hz}"] = dict(raw=s3.boot(share(sf, w), N, brng),
                                                          chance=s3.boot(share(sc, w), N, brng),
                                                          net=s3.boot(share(sf - sc, w), N, brng))
                for hz in HZ:
                    for a, b in pairs:
                        (fa, ca), (fb, cb) = S[(a, hz)], S[(b, hz)]
                        for g, w in pops.items():
                            r[f"{a}_minus_{b}_{g}_h{hz}"] = s3.boot(
                                lambda idx, xa=fa - ca, xb=fb - cb, w=w: share(xa, w)(idx) - share(xb, w)(idx),
                                N, brng)
                    for name in ("L0", "L1", "L2", "oracle"):  # reproduction of net_003.json
                        for g in pops:
                            ref, got = net[f"W{W}_{det}"][f"{name}_{g}_h{hz}"], r[f"{name}_{g}_h{hz}"]
                            assert all(got[k] == ref[k] for k in ("raw", "chance", "net")), (W, det, name, g, hz)
                    assert r[f"L1_bothCF_inwin_h{hz}"]["net"] == absorb[f"W{W}_{det}"][f"L1_bothCF_h{hz}"]["net"]
                out[f"W{W}_{det}"] = r
    finally:
        ds.REBASELINE_WINDOW = w0
        s3.apply_log = APPLY_LOG
    (HERE / "obs_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
