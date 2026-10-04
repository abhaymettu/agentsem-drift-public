"""2x2 counterfactual for DR+PS: D change x observer change (DESIGN STAGE, EXPLORATORY). SYNTHETIC ONLY: D is
one invented, non-diagnostic wellbeing/functioning state; no real data is read. Scores no prediction.
Imports study003.py, decide_003.py and drift_sim.py unchanged; the runtime patches add three families and set
ds.REBASELINE_WINDOW, all restored.

    python3 sim/fact_003.py      # -> sim/fact_003.json

Arms, contrasts and expectations: sim/FACT-003.md.
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
ARMS = {"F": ("DR+PS", 1.0, True), "C": ("DR0+PS", 0.0, True), "O": ("DR+noPS", 1.0, False), "N": ("DR0+noPS", 0.0, False)}


def arms():
    """The four arms, generated from DR+PS's main and side seeds."""
    new = [(name, d, obs) for name, d, obs in ARMS.values() if name != "DR+PS"]
    for name, d, obs in new:
        s3.FAMILY[name] = ("DR", d)
        if obs:
            s3.STEP_SHIFT.add(name)
            s3.USE_SHIFT.add(name)
    try:
        out = {}
        for a, (name, _, _) in ARMS.items():
            rng, side = s3.seeds(SEED, PHI, 0)
            out[a] = s3.gen(rng, s3.events(side, "DR+PS", N), name, n=N, phi=PHI)
            out[a]["phi"] = PHI
    finally:
        for name, _, _ in new:
            del s3.FAMILY[name]
            s3.STEP_SHIFT.discard(name)
            s3.USE_SHIFT.discard(name)
    F, C, O, Nn = (out[a] for a in "FCON")
    ref = s3.panels(SEED, PHI, ("DR+PS",))["DR+PS"]
    assert np.array_equal(F["X"], ref["X"], equal_nan=True), "F differs from the design's DR+PS panel"
    step = np.clip((np.arange(s3.T_GEN)[None, :] - F["t0"][:, None]) / F["ramp"][:, None], 0, 1)
    for a, b in ((F, C), (O, Nn)):
        assert np.allclose(a["D"] - b["D"], step), "a D pair differs by more than the D step"
        assert np.array_equal(a["used"], b["used"]), "a D pair differs in usage"
    for a, b in ((F, O), (C, Nn)):
        assert np.array_equal(a["D"], b["D"]), "an observer pair differs in D"
    for x in (C, O, Nn):
        assert np.array_equal(x["log_day"], F["log_day"], equal_nan=True), "arms differ in the log"
    for x in (O, Nn):  # no observer change: the oracle rule's panel is the observed one
        assert np.array_equal(x["X0"], x["X"], equal_nan=True)
    return out


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    net = json.loads((HERE / "net_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, P = d3.alarms_fn(tun), arms()
    t0 = P["F"]["t0"]
    inwin = ~np.isnan(P["F"]["log_day"]) & (t0 >= P["F"]["cday"]) & (t0 <= P["F"]["cday"] + 13)
    ix = lambda s: s["F"] - s["C"] - s["O"] + s["N"]
    share = lambda x: s3.ratio(x * inwin, inwin * 1.0)
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED,
               n_inwin=int(inwin.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("fact_003.py", "study003.py", "decide_003.py",
                                                        "drift_sim.py", "tuning_003.json", "net_003.json")})
    w0 = ds.REBASELINE_WINDOW
    try:
        for W in (14, 21):
            ds.REBASELINE_WINDOW = W
            for det in ("A-k0.5", "A-kstar"):
                r, S = {}, {}
                for rule in RULES:
                    S[rule] = s = {a: ds._sensitivity(alarms(P[a], 28, det, rule)[0], t0, window=21,
                                            exclude_pre_onset_alarms=False).astype(float) for a in "FCON"}
                    for a in "FCON":
                        r[f"{rule}_{a}"] = s3.boot(share(s[a]), N, brng)
                    for key, x in (("D_with_obs", s["F"] - s["C"]), ("D_without_obs", s["O"] - s["N"]),
                                   ("interaction", ix(s)),
                                   ("obs_part_of_no_change", s["C"] - s["N"])):
                        r[f"{rule}_{key}"] = s3.boot(share(x), N, brng)
                    n3 = net[f"W{W}_{det}"][f"{rule}_inwin_h21"]  # reproduction of net_003.json
                    assert (r[f"{rule}_F"], r[f"{rule}_C"], r[f"{rule}_D_with_obs"]) == (n3["raw"], n3["chance"], n3["net"]), (W, det, rule)
                for a, b in (("L2", "oracle"), ("L2", "L1"), ("L2", "L0")):
                    for arm in "CN":
                        r[f"{a}_minus_{b}_{arm}"] = s3.boot(share(S[a][arm] - S[b][arm]), N, brng)
                    r[f"{a}_minus_{b}_interaction"] = s3.boot(share(ix(S[a]) - ix(S[b])), N, brng)
                out[f"W{W}_{det}"] = r
    finally:
        ds.REBASELINE_WINDOW = w0
    (HERE / "fact_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
