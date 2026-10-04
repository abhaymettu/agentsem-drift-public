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

## Results (DESIGN STAGE, synthetic; they inform PREREG-003's wording and score nothing)

Provenance: code `fact_003.py` at commit `08a38c6`, output `fact_003.json` sha256
`209642a0e1e7b9fd5feaa28385fe84cb260f3c5cb340187ea8160e02ed8ba0f5`. A second run reproduced it byte for byte
(`cmp`). Every assert in the plan passed, including the reproduction of `net_003.json`. Intervals are 95% paired
person-bootstrap intervals over the design run's resample matrix, "est [lo, hi]". In-window n = 247.

### Rates per arm and contrasts (A-fixed `k = 0.5`, W = 14, 21 days from onset)

| rule | F | C | O | N | D effect with observer change (F - C) | D effect without it (O - N) | interaction | C - N |
|---|---|---|---|---|---|---|---|---|
| L0 | 0.526 | 0.251 | 0.215 | 0.093 | 0.275 [0.217, 0.329] | 0.121 [0.085, 0.163] | 0.154 [0.079, 0.224] | 0.158 [0.114, 0.208] |
| L1 | 0.113 | 0.057 | 0.105 | 0.053 | 0.057 [0.031, 0.087] | 0.053 [0.026, 0.083] | 0.004 [-0.012, 0.023] | 0.004 [-0.013, 0.021] |
| L2 | 0.267 | 0.134 | 0.267 | 0.121 | 0.134 [0.096, 0.178] | 0.146 [0.106, 0.191] | -0.012 [-0.041, 0.017] | 0.012 [-0.008, 0.033] |
| oracle | 0.227 | 0.101 | 0.215 | 0.093 | 0.126 [0.087, 0.167] | 0.121 [0.085, 0.163] | 0.004 [-0.016, 0.024] | 0.008 [0.000, 0.020] |

L0 and the oracle rule do not depend on W, so their rows are the same at W = 21. The in-window set is fixed at
`[c, c + 13]` at both windows, so the W = 21 rows below are not H4 as study003 scores it at W = 21 (`c + W - 1`).

Paired gaps between rules' no-change rates (C, N) and interactions:

| gap | detector, W | in C | in N | interaction |
|---|---|---|---|---|
| L2 - oracle | k 0.5, 14 | 0.032 [-0.009, 0.074] | 0.028 [-0.015, 0.069] | -0.016 [-0.048, 0.016] |
| L2 - oracle | k 0.5, 21 | 0.049 [0.004, 0.089] | 0.049 [0.009, 0.089] | 0.012 [-0.023, 0.047] |
| L2 - oracle | k*, 14 | -0.004 [-0.035, 0.024] | -0.012 [-0.045, 0.016] | -0.004 [-0.037, 0.028] |
| L2 - L1 (H4's rules) | k 0.5, 14 | 0.077 [0.034, 0.120] | 0.069 [0.025, 0.113] | -0.016 [-0.050, 0.016] |
| L2 - L1 (H4's rules) | k 0.5, 21 | 0.146 [0.104, 0.194] | 0.142 [0.100, 0.191] | 0.016 [-0.011, 0.046] |
| L2 - L1 (H4's rules) | k*, 14 | 0.081 [0.046, 0.118] | 0.061 [0.029, 0.094] | 0.008 [-0.024, 0.041] |

### Against the expectations

1. **L0's interaction is positive and excludes 0: yes.** 0.154 [0.079, 0.224] at k 0.5 and 0.093
   [0.018, 0.163] at k*. In O and N, L0 and the oracle rule score the same panel the same way, so NET-003's
   L0 - oracle D-dependent gap equals L0's interaction minus the oracle rule's (0.154 - 0.004 = 0.150 at k 0.5;
   0.093 - 0.020 = 0.073 at k*). That gap is the observer shift and the `D` change acting together, which
   NET-003 credited to `D`, not better `D` detection by L0.
2. **The oracle rule's interaction covers 0: yes at k 0.5** (0.004 [-0.016, 0.024]). At k* it is 0.020
   [0.000, 0.042]: 6 persons positive, 1 negative.
3. **In N, L0 equals the oracle rule: yes** (0.093 at k 0.5, 0.085 at k*). **L2's N rate is above L0's:
   partly:** the interval excludes 0 only at k 0.5, W = 21 (gap table, in N; L2 - oracle equals L2 - L0 there).
4. **C - N is at least 0.10 for L0: yes** (0.158 at k 0.5, 0.194 at k*). **It covers 0 for the oracle rule
   and L2: for L2 yes,** except a lower end of 0.000 at k*, W 21. For the oracle rule, C - N is 2 of 247
   persons at k 0.5 and 1 at k*, all positive; the 0.000 lower end is the bootstrap's floor, not evidence of
   no effect.
5. **L1's C - N covers 0: yes** (0.004 [-0.013, 0.021], k 0.5, W 14).
6. **L2 - oracle in C excludes 0 at k 0.5, W 14: no** (0.032 [-0.009, 0.074]); it does at W = 21 (gap table).
   The gap is about the same in N, where nothing changes and the log is false. No paired interval was
   computed for the difference between L2's and the oracle rule's C - N.

### What this changes for PREREG-003 (proposals, not decisions)

1. **NET-003's proposal holds, with one addition.** Scoring DR+PS rule comparisons as D-dependent removes the
   observer change's direct alarms (C - N, 0.158 for L0) but keeps its interaction with `D` (0.154 for L0).
   For a comparison that involves L0, report the interaction beside the D-dependent value. For L2 the
   interaction intervals cover 0; for the oracle rule the interaction is at most 0.020; L1's is 0 [0, 0] at
   W = 21 because L1 detects no in-window person in O or N there.
2. **H4's raw gap shows no detectable dependence on the observer change, and almost half of it is not about
   `D`.** The H4 interaction covers 0 at every detector and window, but its bounds reach 0.050, so an
   interaction of that size against the D-dependent 0.077 is not ruled out. Of H4's raw 0.154 (k 0.5, W 14),
   0.069 [0.025, 0.113] is present in N, where neither `D` nor the observer changes: a gap in no-change rates,
   mostly L1 alarming less than L0 (0.053 against 0.093) rather than L2 alarming more (L2 - L0 in N, 0.028
   [-0.015, 0.069]). No interval was computed for L0 - L1, or for the observer change's own part of the
   L2 - L1 gap (0.008).
3. **Spec 003 has no family with a false exogenous log entry, so the design does not measure one.** Here
   falseness changes little: L1's `D` effect is 0.053 with a false log (O - N) and 0.057 with a true one
   (F - C), against 0.121 for L0 and the oracle rule; L2's excess over the oracle rule at W = 21 is 0.049 in
   both N and C. These costs come with acting on an entry near onset, true or false. Whether to add a
   false-log family is his call.
