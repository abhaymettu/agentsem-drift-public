"""Re-baseline window 21 and 28 days against the design's 14 (DESIGN STAGE, EXPLORATORY): the evidence behind
DECIDE-003's H3 option 'move to 21'. SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning
state; no real data is read. Scores no prediction. Imports study003.py, decide_003.py and drift_sim.py
unchanged; the runtime patches are ds.REBASELINE_WINDOW and, for the tuning rerun, s3.HERE (so tuning_003.json
is not overwritten), both restored.

    python3 sim/window_003.py      # -> sim/window_003.json

Per window W in (21, 28), on the tuning and design seeds:
(1) the tuning rerun, compared with tuning_003.json;
(2) the whole design run, every leaf compared with design_003.json (which is W = 14), listing what changed;
(3) DECIDE-003 part (a)'s evaluation-N sizing on W's policy_log;
(4) H4 on the design's population (logged DR+PS persons with onset in [c, c + 13]), since policy_log's own H4
    population follows W. W = 14 is also run for (4) and must reproduce design_003.json's H4.
"""

import json
import tempfile
from pathlib import Path

import numpy as np

import decide_003 as d3
import drift_sim as ds
import study003 as s3

HERE = Path(__file__).parent
SEED = s3.DESIGN_SEED


def leaves(d, path=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from leaves(v, path + (k,))
    else:
        yield "/".join(path), d


def h4_design_population(tun, brng):
    alarms, p = d3.alarms_fn(tun), s3.panels(SEED, 0.7, ("DR+PS",))["DR+PS"]
    p["phi"] = 0.7
    w = ~np.isnan(p["log_day"]) & (p["t0"] >= p["cday"]) & (p["t0"] <= p["cday"] + 13)
    s1, s2 = (ds._sensitivity(alarms(p, 28, "A-k0.5", r)[0], p["t0"], window=21, exclude_pre_onset_alarms=False)
              .astype(float) for r in ("L1", "L2"))
    return s3.boot(lambda idx: s3.ratio(s2 * w, w * 1.0)(idx) - s3.ratio(s1 * w, w * 1.0)(idx), s3.N, brng)


def main():
    design = json.loads((HERE / "design_003.json").read_text())
    tun = json.loads((HERE / "tuning_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, s3.N, (s3.NBOOT, s3.N))  # the design run's matrix
    old, w0, h0 = dict(leaves(design)), ds.REBASELINE_WINDOW, s3.HERE
    assert w0 == 14
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED,
               sha256={f: s3.sha256(HERE / f) for f in ("window_003.py", "decide_003.py", "study003.py",
                                                        "tuning_003.json", "design_003.json", "drift_sim.py")},
               H4_design_population={"W14": h4_design_population(tun, brng)})
    assert out["H4_design_population"]["W14"] == design["policy_log"]["A-k0.5"]["dr"]["H4_L2_minus_L1_onset_in_window"]
    try:
        for W in (21, 28):
            ds.REBASELINE_WINDOW = W
            with tempfile.TemporaryDirectory() as tmp:
                s3.HERE = Path(tmp)
                tuning_equal = s3.run_tune() == tun
            s3.HERE = h0
            run = s3.run_study(SEED, tun)
            new = dict(leaves(run))
            changed = sorted(k for k in new if new[k] != old[k])
            out[f"W{W}"] = dict(tuning_equal=tuning_equal, n_leaves=len(new), changed=changed,
                                sizing=d3.sizing({**design, "policy_log": run["policy_log"]}),
                                policy_log=run["policy_log"])
            out["H4_design_population"][f"W{W}"] = h4_design_population(tun, brng)
    finally:
        ds.REBASELINE_WINDOW, s3.HERE = w0, h0
    (HERE / "window_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
