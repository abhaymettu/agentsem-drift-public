# L1_did when D moves mapped and unmapped indicators unequally

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs whether
PREREG-003 and the paper can specify L1_did (OBS-003) and which assumption it must state. It decides nothing and
changes no spec.

Code: `sim/load_003.py` -> `sim/load_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, W 14, the
design run's resample matrix, NET-003's paired arms (DR+PS, and the same persons with `delta_D = 0`).
`obs_003.py` and everything it imports are unchanged.

## Why

OBS-003: L1_did (keep the baseline mean and SD; after the hold subtract from mapped indicators 1, 2, 6 their
hold-mean z minus the unmapped indicators' mean hold z) lifts L1's 63-day in-window D-dependent sensitivity
0.190 -> 0.385 (k 0.5, W 14). Its DiD reference works only if D moves the unmapped indicators about as much, in
baseline z, as the mapped ones. In the generator it does on average (loadings U[0.25, 0.5] on every indicator).
Real indicators need not: D could show more in timing (mapped) than in message content (unmapped), or the
reverse. A reviewer will ask what the rule costs when that assumption fails. OBS-003 also cut three interval
contrasts before its run (oracle - L1_did, L1_did - L2, L1_did - L1_bothCF); this plan states them before the run.

## Plan (committed before the run)

Effect ratio rho: in the DR+PS arm, D's realized effect on the unmapped indicators 3, 4, 5 is scaled by rho, as
`c + rho * (f - c)` on each series the detector reads (X, X_filtered, and the oracle's unshifted X0, Xf0), where f
is DR+PS and c the same persons without the D change. f and c share every draw but the D step, so `f - c` is
D's whole effect on that indicator: its loading, and on indicators 4 and 5 also its context channel through the
authorship mix. rho scales that realized effect, not the loading itself. Mapped indicators keep f. rho in {0, 0.5, 1, 2}; rho = 1 is f itself.
rho = 0: D does not show on the unmapped indicators, so the reference reads only noise and L1_did should behave as
L1_step. rho = 2: the reference over-reads D and L1_did subtracts part of the person's change from the mapped
indicators. The no-D-change arm does not depend on rho, so every rule's no-change rate is the same at every rho.
rho also changes the total D signal, so rules are compared within a rho, not across.

Rules (OBS-003's): L1, L1_step, L1_did, L2, the oracle rule, L1_bothCF (ramp-free L1, oracle information).
Detectors A-fixed `k = 0.5` (primary) and `k*`; horizons 21, 42, 63 days; in-window persons (n = 247).
1. Each rule's raw sensitivity, no-change rate and D-dependent sensitivity.
2. Paired D-dependent differences with intervals: L1_did - L1, L1_did - L1_step (what the DiD reference adds),
   oracle - L1_did, L1_did - L2, L1_did - L1_bothCF.
3. Step-estimate error on the mapped indicators (estimate minus the true step 0.5 / baseline SD), raw and DiD.

Asserts: at rho = 1 every rule's measures, L1_did - L1 and the DiD step error reproduce `obs_003.json` (W 14).

Expected (k 0.5, in-window, 63 days unless stated):
1. The asserts pass.
2. The raw step error is the same at every rho (asserted at rho = 1 against `obs_003.json`); the DiD step error's mean falls linearly in rho, to within 0.005
   of `raw - rho * (raw - DiD at rho 1)`.
3. L1_did - L1_step falls as rho rises (points), its interval covers 0 at rho = 0, it is positive at rho = 0.5
   (point) and negative at rho = 2 (point).
4. L1_did - L1 is positive and its interval excludes 0 at every rho.
5. At rho = 1, the intervals of oracle - L1_did, L1_did - L2 and L1_did - L1_bothCF all cover 0.

## Results (run after the plan commit `ef2e41c`)

`load_003.json` sha256 f281b8358e68da3ee4105da1b8fe59162432d61a6a1dffa6d2836c63e95d3595; the rerun was
byte-identical (`cmp`). Every assert passed: at rho = 1 all six rules' measures (both detectors, all horizons),
L1_did - L1 and both step errors reproduce `obs_003.json`.

**The plan text above has the rho = 2 sign backwards.** A reference that over-reads D makes the step estimate too
small, so the mapped indicators keep a positive residual after the correction. The rho-dependent part of that
residual exists only in the D-change arm (the no-D-change arm's is -0.013 baseline z at every rho). It adds D
signal to the mapped indicators; it does not remove it. The plan is left as committed.

k 0.5, in-window persons (n = 247), 63 days from onset. D-dependent sensitivity = raw minus no-change rate. The
no-change rates do not depend on rho (L1 0.304, L1_step 0.211, L1_did 0.211, L2 0.316, oracle 0.211, L1_bothCF
0.304):

| rho | L1 | L1_step | L1_did | L2 | oracle | DiD step error (mean) |
|---|---|---|---|---|---|---|
| 0 | 0.117 | 0.166 | 0.130 | 0.101 | 0.215 | 0.157 |
| 0.5 | 0.154 | 0.247 | 0.259 | 0.231 | 0.296 | 0.095 |
| 1 | 0.190 | 0.340 | 0.385 | 0.344 | 0.441 | 0.033 |
| 2 | 0.275 | 0.518 | 0.591 | 0.498 | 0.595 | -0.092 |

The raw step error is 0.124 at every rho.

Paired D-dependent differences [95% interval], same cell:

| rho | L1_did - L1 | L1_did - L1_step | oracle - L1_did | L1_did - L2 | L1_did - L1_bothCF |
|---|---|---|---|---|---|
| 0 | 0.012 [-0.043, 0.066] | -0.036 [-0.094, 0.021] | 0.085 [0.030, 0.139] | 0.028 [-0.017, 0.072] | -0.040 [-0.104, 0.018] |
| 0.5 | 0.105 [0.034, 0.172] | 0.012 [-0.050, 0.079] | 0.036 [-0.027, 0.098] | 0.028 [-0.036, 0.090] | -0.004 [-0.083, 0.070] |
| 1 | 0.194 [0.105, 0.272] | 0.045 [-0.024, 0.114] | 0.057 [-0.016, 0.126] | 0.040 [-0.033, 0.106] | 0.036 [-0.053, 0.118] |
| 2 | 0.316 [0.232, 0.396] | 0.073 [0.008, 0.134] | 0.004 [-0.063, 0.068] | 0.093 [0.026, 0.160] | 0.085 [-0.004, 0.163] |

Findings:
1. **In this generator, L1_did's gain over L1 needs D to show on the unmapped indicators.** It holds at rho 0.5,
   1 and 2 (intervals exclude 0). At rho 0 it covers 0, and L1_did is no better than L1_step. At `k*`: rho 0
   -0.008 [-0.063, 0.050]; rho 0.5 0.085 [0.013, 0.155].
2. **This run cannot show a specificity cost.** rho scales only D's own effect, and the no-D-change arm's alarms
   are computed once and reused, so every no-change rate is the same at every rho by construction. Here the cost
   of rho < 1 falls on D-dependent sensitivity only. A failure of the assumption through an unmapped shift that D
   did not cause would reach the no-change arm; this run did not test that (finding 4).
3. **The DiD step error is exactly linear in rho,** 0.033 above raw at rho 0. That offset is minus the unmapped
   reference's mean hold shift with no D change (-0.033; `obs_003.json` no-D-change arm, DiD minus raw: 0.0333).
   Why the reference is nonzero there was not tested.
4. **DiD adds the unmapped indicators' mean hold shift to the mapped ones at every rho** (L1_did's post-hold
   mapped z is L1_step's plus that shift). That is why L1_did - L1_step rises with rho. Above rho 1 the added
   shift exceeds the mapped indicators' own D shift (DiD step error -0.092). In this generator that shift is D,
   so it raises D-dependent sensitivity; an unmapped shift from another cause would be carried over the same way.
5. **The three contrasts OBS-003 cut (rho 1, k 0.5, 63 d) all cover 0** (table, rho 1). Five cells outside the
   primary one exclude 0. At `k*` the oracle rule beats L1_did at every horizon: 21 d 0.130 [0.088, 0.180], 42 d
   0.089 [0.021, 0.154], 63 d 0.069 [0.004, 0.133]. At `k*` 21 d L2 beats L1_did: L1_did - L2 -0.105
   [-0.152, -0.065]. At k 0.5, 42 d, L1_did beats L2: 0.077 [0.017, 0.135]. So this run cannot say that L1_did
   matches the oracle rule or beats L2, and at `k*` it says it does not match the oracle rule.

Expectations, scored clause by clause:
1. Yes.
2. Partly. Raw error constant: yes. DiD clause: no. The error falls exactly linearly but sits 0.033 above the
   stated line at rho 0 (0.157 vs 0.124), 0.017 at rho 0.5 and 0.033 at rho 2 (-0.092 vs -0.058), outside the
   0.005 tolerance. The line assumed a zero reference without D (finding 3).
3. Two of four clauses. Falls as rho rises: no, it rises. Covers 0 at rho 0: yes. Positive at 0.5: yes. Negative
   at 2: no.
4. No. At rho 0 the point is positive (0.012) but the interval covers 0; it holds at 0.5, 1 and 2.
5. Yes in the primary cell; five cells outside it exclude 0 (finding 5).

What the paper would have to state if it specifies L1_did: the change being detected moves the unmapped
indicators, in baseline z, by a substantial fraction of what it moves the mapped ones. rho 0.5 (an unmapped hold
shift about 0.43 of the mapped one in this generator) was enough at 63 days for both detectors but not at `k*`
42 days (0.024 [-0.030, 0.086]); 0 was not; the threshold between them was not located. An unlogged change on
unmapped indicators would be carried onto the mapped ones, a false-alarm route this run did not test (finding 4).
