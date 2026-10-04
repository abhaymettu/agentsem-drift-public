# DR+PS: D change x observer change, a 2x2 counterfactual

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs
PREREG-003's H4 wording and the DR+PS rule comparisons. It decides nothing and changes no spec.

Code: `sim/fact_003.py` -> `sim/fact_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, the design
run's resample matrix. `study003.py`, `decide_003.py`, `drift_sim.py` and spec 003 are unchanged.

## Why

NET-003 compared DR+PS with one counterfactual: the same persons without the `D` step. Two things it left open:
1. Its D-dependent measure credits `D` with any interaction between the `D` change and the observer change.
   L0 - oracle stayed at 0.150 [0.075, 0.221] on that measure (k 0.5, W 14). NET-003 gave a reason it did not
   test: the observer shift brings L0's S closer to `h`, so the `D` change tips more alarms than it would alone.
2. Its no-change rate lumps chance, the observer change and L2's 3-indicator composite during the hold, and
   it computed no paired interval on any gap between two rules' no-change rates.

## Plan (committed before the run)

Four arms on DR+PS's seeds and events. Every person keeps their noise, onset, change day and log entry:

| arm | `D` step | observer change |
|---|---|---|
| F (the design's DR+PS) | yes | yes |
| C (NET-003's counterfactual) | no | yes |
| O | yes | no |
| N | no | no |

"Observer change" is everything spec 003 adds to DR+PS from the change day: +0.5 on indicators 1, 2 and 6, and
+0.5 on the usage intercept. The log entry, and each rule's handling of it, stays in all four arms. In O and N
the log is therefore a false log: it records a change that did not happen.

For W in (14, 21) and detectors A-fixed `k = 0.5` and `k*`, rules L0, L1, L2 and oracle, on in-window persons
(onset in `[c, c + 13]`, n = 247), 21-day sensitivity with `exclude_pre_onset_alarms=False` as in the design:
1. The rate in each arm.
2. Paired contrasts per rule: `D` effect with the observer change (F - C, NET-003's D-dependent), without it
   (O - N), the interaction (F - C) - (O - N), and the observer change's part of the no-change rate (C - N).
3. Paired gaps between rules in C and in N, and in the interaction: L2 - oracle, L2 - L1, L2 - L0.

Asserts: F equals the design's DR+PS panel; each `D` pair differs only by the `D` step and has the same usage;
each observer pair has the same `D`; all arms share the log; O and N's oracle panel is the observed one. F, C
and F - C reproduce `net_003.json` for every rule, detector and W.

Expected:
1. L0's interaction is positive and its interval excludes 0 at k 0.5, W 14 (NET-003's untested reason).
2. The oracle rule's interaction covers 0: it subtracts the intercept shift, and only the extra used days stay.
3. In N, L0 and the oracle rule have the same rate (same panel, same handling). L2's N rate is above L0's: the
   false log still puts L2 on its 3-indicator composite during the hold.
4. The observer change's part of the no-change rate (C - N) is at least 0.10 for L0, and covers 0 for the
   oracle rule and for L2.
5. L1's C - N covers 0: its no-change rate (0.057 at k 0.5, W 14) comes from the reset and re-baseline, not the
   observer change.
6. L2 - oracle in C (NET-003: 0.134 against 0.101) excludes 0 at k 0.5, W 14.
