"""DR+PS sensitivity net of a paired no-change counterfactual (DESIGN STAGE, EXPLORATORY). SYNTHETIC ONLY: D
is one invented, non-diagnostic wellbeing/functioning state; no real data is read. Scores no prediction.
Imports study003.py, decide_003.py and drift_sim.py unchanged; the runtime patches are a counterfactual family
'DR0+PS' (DR+PS with delta_D = 0) and ds.REBASELINE_WINDOW, all restored.

    python3 sim/net_003.py      # -> sim/net_003.json

The counterfactual uses DR+PS's seeds and events, so each person keeps their noise, change day, log and
observer change and loses only the D step (and D's pull on context). Per rule, detector, window W in (14, 21)
and horizon in (21, 42, 63) days from onset: raw sensitivity (the design's), chance (the same rule on the
counterfactual), net = raw - chance per person, and the share of raw detections the counterfactual also has.
Populations: logged DR+PS persons, and those with onset in [c, c + 13] (the design's H4 population).
"""

import json
from pathlib import Path

import numpy as np

import decide_003 as d3
import drift_sim as ds
import study003 as s3

HERE = Path(__file__).parent
SEED, PHI, N = s3.DESIGN_SEED, 0.7, s3.N
RULES = ("L0", "L1", "L2", "oracle")
PAIRS = (("L2", "oracle"), ("L2", "L1"), ("L1", "oracle"), ("L0", "oracle"))


def drps_pair():
    """(DR+PS as the design generates it, the same persons with delta_D = 0)."""
    s3.FAMILY["DR0+PS"] = ("DR", 0.0)
    s3.STEP_SHIFT.add("DR0+PS")
    s3.USE_SHIFT.add("DR0+PS")
    try:
        out = []
        for fam in ("DR+PS", "DR0+PS"):
            rng, side = s3.seeds(SEED, PHI, 0)
            p = s3.gen(rng, s3.events(side, "DR+PS", N), fam, n=N, phi=PHI)
            p["phi"] = PHI
            out.append(p)
    finally:
        del s3.FAMILY["DR0+PS"]
        s3.STEP_SHIFT.discard("DR0+PS")
        s3.USE_SHIFT.discard("DR0+PS")
    f, c = out
    ref = s3.panels(SEED, PHI, ("DR+PS",))["DR+PS"]
    assert np.array_equal(f["X"], ref["X"], equal_nan=True), "DR+PS differs from the design's panel"
    step = np.clip((np.arange(s3.T_GEN)[None, :] - f["t0"][:, None]) / f["ramp"][:, None], 0, 1)
    assert np.allclose(f["D"] - c["D"], step), "the counterfactual differs by more than the D step"
    assert np.array_equal(f["used"], c["used"]) and np.array_equal(f["log_day"], c["log_day"], equal_nan=True)
    return f, c


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    design = json.loads((HERE / "design_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, f, c = d3.alarms_fn(tun), *drps_pair()
    t0 = f["t0"]
    logged = ~np.isnan(f["log_day"])
    inwin = logged & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    pops = {"inwin": inwin, "logged": logged}
    day = np.arange(s3.T)[None, :]
    share = lambda x, w: s3.ratio(x * w, w * 1.0)
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED,
               n_inwin=int(inwin.sum()), n_logged=int(logged.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("net_003.py", "study003.py", "decide_003.py",
                                                        "drift_sim.py", "tuning_003.json", "design_003.json")})
    w0 = ds.REBASELINE_WINDOW
    try:
        for W in (14, 21):
            ds.REBASELINE_WINDOW = W
            for det in ("A-k0.5", "A-kstar", "oracle-D"):
                r, det_s = {}, {}
                for rule in (("L0",) if det == "oracle-D" else RULES):
                    af, ac = alarms(f, 28, det, rule)[0], alarms(c, 28, det, rule)[0]
                    for hz in (21, 42, 63):
                        sf, sc = (ds._sensitivity(a, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
                                  for a in (af, ac))
                        det_s[(rule, hz)] = (sf, sc)
                        for g, w in pops.items():
                            r[f"{rule}_{g}_h{hz}"] = dict(
                                raw=s3.boot(share(sf, w), N, brng),
                                chance=s3.boot(share(sc, w), N, brng),
                                net=s3.boot(share(sf - sc, w), N, brng),
                                also_without_change=s3.boot(s3.ratio(sf * sc * w, sf * w), N, brng))
                    if det == "A-k0.5" and rule in ("L0", "L2"):
                        # composite SD on the counterfactual, in-window persons: hold days (c, c + W] vs [28, c)
                        C = s3.detector_C(c, 28, "A", rule)[0]
                        cd = c["cday"][:, None]
                        hold = inwin[:, None] & (day > cd) & (day <= cd + W)
                        pre = inwin[:, None] & (day >= 28) & (day < cd)
                        r[f"{rule}_cf_composite_sd_hold_vs_pre"] = [round(float(np.nanstd(C[m])), 4) for m in (hold, pre)]
                if det != "oracle-D":
                    for a, b in PAIRS:
                        for g, w in pops.items():
                            (fa, ca), (fb, cb) = det_s[(a, 21)], det_s[(b, 21)]
                            for kind, xa, xb in (("raw", fa, fb), ("net", fa - ca, fb - cb)):
                                r[f"{a}_minus_{b}_{g}_h21_{kind}"] = s3.boot(
                                    lambda idx, xa=xa, xb=xb, w=w: share(xa, w)(idx) - share(xb, w)(idx), N, brng)
                out[f"W{W}_{det}"] = r
    finally:
        ds.REBASELINE_WINDOW = w0
    dr = design["policy_log"]["A-k0.5"]["dr"]
    for rule in RULES:  # reproduction: raw in-window sensitivity at 21 days equals the design's
        assert out["W14_A-k0.5"][f"{rule}_inwin_h21"]["raw"] == dr[f"DR+PS_{rule}_sens21_onset_in_rebaseline_window"], rule
    assert out["W14_A-k0.5"]["L2_minus_L1_inwin_h21_raw"] == dr["H4_L2_minus_L1_onset_in_window"]
    (HERE / "net_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
