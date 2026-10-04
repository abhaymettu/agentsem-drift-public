# L1_step vs L1, and the trade with D and an unlogged shift in the same persons

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs which
observer-step rule, if any, PREREG-003 and the paper specify. It decides nothing and changes no spec.

Code: `sim/step_003.py` -> `sim/step_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, W 14, the
design run's resample matrix, NET-003's DR+PS pair (the D arm and the same persons with `delta_D = 0`).
`obs_003.py`, `load_003.py`, `unlog_003.py` and everything they import are unchanged.

## Why

UNLOG-003 proposed L1_step as the paper's observer-step rule, but no run has an interval for L1_step - L1, the
contrast the paper would report if it picks L1_step (UNLOG-003 proposal 3). UNLOG-003 finding 4 also set L1_did's
extra false-alarm cost against its extra sensitivity from different arms (LOAD-003 vs UNLOG-003), which is not a
paired contrast. And L1 absorbs a concurrent unlogged shift (UNLOG-003 finding 3), so L1_step's gain over L1 may
reverse when such shifts occur; no run has both sides for the same persons. An unmapped shift of the opposite
sign, a masking route for L1_did, is also untested.

## Plan (committed before the run)

Rules: L1, L1_step, L1_did, L2, the oracle rule. Detectors A-fixed `k = 0.5` (primary) and `k*`; horizons 21, 42
and 63 days from t0; in-window persons (n = 247). Unlogged shift: UNLOG-003's `unlogged()` (intercept shift `s`
on unmapped indicators 3, 4, 5 from day `c + lag`, also on the oracle rule's unshifted series).

- **Part A.** LOAD-003's rho sweep (rho 0, 0.5, 1, 2): L1_step - L1 in D-dependent share (D arm minus no-D-change
  arm, per person), with intervals.
- **Part B.** UNLOG-003's arms (`conc0.25`, `conc0.5`, `post0.5`) plus `conc-0.5` (s -0.5 from the change day),
  no D change: each rule's added false-alarm share, and L1_step - L1 in it, with intervals.
- **Part C.** The same shift applied to both the D arm and the no-D-change arm, for `conc0.5`, `conc-0.5` and
  `post0.5`. Per rule: `dd`, the D-dependent share under the shift (D arm with shift minus no-D-change arm with
  shift, per person), and `dd_change`, `dd` minus the no-shift D-dependent share. For L1_step - L1 and L1_did -
  L1_step: the difference in `dd`, in added share, and `trade` = difference in `dd` minus difference in added
  share. `trade` weights one D-dependent alarm against one added false alarm, 1:1 (CHOICE; the paper's weighting
  is the owner's). It assumes every person carries the shift; it is not a prevalence-weighted rate.

Asserts: part A reproduces `load_003.json`'s D-dependent shares for L1, L1_step, L1_did at every rho (both
detectors, 3 horizons); part B reproduces `unlog_003.json`'s added shares for all 5 rules in its 3 arms.

Expected (k 0.5, in-window, 63 days unless stated):
1. The asserts pass.
2. Part A: L1_step - L1 is positive at every rho (points), its interval excludes 0 at rho 1 and 2 and covers 0
   at rho 0.
3. Part B: L1_step - L1 in added share excludes 0 in `conc0.25` and `conc0.5` at 42 and 63 days; it is negative
   in `conc-0.5` and positive in `post0.5` (points).
4. Part C `conc-0.5`: every rule except L1 has a negative added share (points; the CUSUM is one-sided upward);
   L1's is within 0.02 of 0; L1_did - L1_step in added share is negative (point).
5. Part C `conc-0.5`: L1_did - L1_step in `dd` is below its no-shift value, 0.045 (point): the DiD reference
   masks D when the unmapped shift is negative.
6. Part C `conc0.5`: `trade` for L1_did - L1_step is negative and its interval excludes 0 (the paired version
   of UNLOG-003 finding 4).
7. Part C: `trade` for L1_step - L1 is negative in `conc0.5` and positive in `post0.5` (points).
8. Part C: L1's `dd_change` is within 0.03 of 0 in `conc0.5` and `conc-0.5` (L1 absorbs a concurrent shift).

Reading (not an expectation): if expectation 7 holds, neither L1 nor L1_step dominates; which one the paper
should prefer depends on how often an unlogged change coincides with a logged one, which no simulation here can
estimate.

## Results (run after the plan commit `c51e738`)

`step_003.json` sha256 aa24b73ce8f363ee3935d1bd450b28f06faba4866bc50610e59d47851fcc0ef9; the rerun was
byte-identical (`cmp`). Every assert passed. Run time 33.5 s to about 2 minutes (machine load).

Table 1 (part A). L1_step - L1 in D-dependent share, in-window persons (n = 247) [95% interval]:

| rho | k 0.5, 21 d | k 0.5, 42 d | k 0.5, 63 d | k*, 63 d |
|---|---|---|---|---|
| 0 | -0.004 [-0.025, 0.017] | 0.008 [-0.037, 0.052] | 0.049 [-0.008, 0.107] | 0.020 [-0.038, 0.072] |
| 0.5 | -0.004 [-0.033, 0.025] | 0.012 [-0.042, 0.066] | 0.093 [0.028, 0.160] | 0.093 [0.027, 0.158] |
| 1 | 0.012 [-0.024, 0.049] | 0.044 [-0.021, 0.105] | 0.150 [0.081, 0.217] | 0.138 [0.067, 0.211] |
| 2 | 0.077 [0.031, 0.123] | 0.202 [0.138, 0.270] | 0.243 [0.169, 0.315] | 0.223 [0.153, 0.295] |

Table 2 (part B). L1_step - L1 in added false-alarm share, no D change:

| arm | k 0.5, 21 d | k 0.5, 42 d | k 0.5, 63 d | k*, 63 d |
|---|---|---|---|---|
| conc0.25 | 0.032 [0.012, 0.056] | 0.101 [0.065, 0.139] | 0.146 [0.104, 0.193] | 0.158 [0.108, 0.204] |
| conc0.5 | 0.053 [0.028, 0.083] | 0.182 [0.133, 0.232] | 0.279 [0.221, 0.343] | 0.287 [0.231, 0.343] |
| post0.5 | -0.016 [-0.054, 0.021] | -0.036 [-0.102, 0.024] | 0.065 [-0.008, 0.135] | 0.028 [-0.037, 0.096] |
| conc-0.5 | 0.000 [-0.020, 0.020] | -0.069 [-0.109, -0.030] | -0.138 [-0.187, -0.089] | -0.109 [-0.162, -0.057] |

Table 3 (part C). The shift in both arms, k 0.5, 63 d. Per rule `dd`; row `none` is the no-shift
value (LOAD-003, rho 1). Contrasts as `dd` / added / `trade`:

| arm | L1 | L1_step | L1_did | L1_step - L1 | L1_did - L1_step |
|---|---|---|---|---|---|
| none | 0.190 | 0.340 | 0.385 | 0.150 / 0 / 0.150 | 0.045 / 0 / 0.045 |
| conc0.5 | 0.178 | 0.295 | 0.247 | 0.117 / 0.279 / **-0.162 [-0.275, -0.053]** | -0.049 / 0.198 / **-0.247 [-0.363, -0.120]** |
| conc-0.5 | 0.206 | 0.223 | 0.117 | 0.016 / -0.138 / **0.154 [0.041, 0.256]** | **-0.105 [-0.158, -0.055]** / -0.028 / -0.077 [-0.165, 0.008] |
| post0.5 | 0.194 | 0.295 | 0.340 | 0.101 / 0.065 / 0.036 [-0.085, 0.153] | 0.044 / -0.032 / 0.077 [-0.042, 0.191] |

Findings:
1. **L1_step's gain over L1 is a late gain and grows with D's effect on the unmapped indicators (rho).** At 63
   days it excludes 0 from rho 0.5 up (table 1); at rho 0 it covers 0 (0.049 [-0.008, 0.107]). At 21 days it
   covers 0 for rho up to 1, and at `k*`, rho 1, it is negative, -0.016 [-0.032, -0.004]. A likely reason, not
   isolated here: L1_step keeps the unmapped indicators on their baseline z after the hold, so D's ramp on them
   counts in full, while L1 re-baselines it away.
2. **L1 absorbs a concurrent unlogged shift of either sign; L1_step does not** (table 2; expectations 4, 8).
3. **With a concurrent +0.5 shift in every person, L1 beats L1_step on the 1:1 trade at 63 days** (-0.162
   [-0.275, -0.053]); at `k*` it is -0.126 [-0.244, 0.000]. **With the shift after the hold, L1_step beats L1 at
   42 days** (0.206 [0.102, 0.320]; `k*` 0.142 [0.041, 0.250]). The other two cells cover 0: `post0.5` at 63 d
   (0.036) and `conc0.5` at 42 d (-0.012 [-0.118, 0.092]). So neither rule dominates: at both 42 and 63 days the
   point sign flips between `conc0.5` and `post0.5`, though at each horizon only one side excludes 0; the sign
   depends on whether unlogged changes coincide with logged ones.
4. **L1_did is never ahead of L1_step on the trade with an interval that excludes 0, in any arm, detector or
   horizon** (18 cells). With a concurrent +0.5 shift, at 63 days it has more false alarms (0.198) and a lower
   `dd` point (-0.049 [-0.115, 0.020]; at `k*` -0.134 [-0.205, -0.060], excluding 0). Its `dd` falls with the
   shift (`dd_change` -0.138 [-0.228, -0.033]). A likely reason, not isolated here: persons already alarmed by
   the shift alone leave less for D to add. At 21 days the shift raises its `dd` (`dd_change` 0.170 [0.094,
   0.243]), so the sign depends on horizon. This makes UNLOG-003 finding 4 a paired contrast, and in `conc0.5`
   the trade excludes 0 at 42 and 63 days at both detectors.
5. **A negative concurrent shift masks D under L1_did.** Its `dd` falls from 0.385 to 0.117 (`dd_change` -0.267
   [-0.347, -0.181]), and L1_did - L1_step in `dd` is -0.105 [-0.158, -0.055]. L1_step's `dd` also falls
   (-0.117 [-0.203, -0.036]): the shift lowers the unmapped indicators' z in every post-hold score. L1_step's
   positive `trade` over L1 in this arm (0.154) comes from the shift suppressing L1_step's alarms, not from better
   detection: its `dd` is not detectably higher than L1's (0.016 [-0.058, 0.084]); the trade is 0.016 - (-0.138).
   The 1:1 trade rewards suppression; read it with the `dd` column.

Expectations, scored clause by clause:
1. Yes.
2. Yes (table 1, k 0.5 63 d column); it also excludes 0 at rho 0.5, which the plan did not state.
3. Yes: excludes 0 in `conc0.25` and `conc0.5` at 42 and 63 days; -0.138 in `conc-0.5`; 0.065 in `post0.5`.
4. Yes: L1_step -0.154, L1_did -0.182, L2 -0.243, oracle -0.138 (each interval excludes 0); L1 -0.016
   [-0.042, 0.008]; L1_did - L1_step -0.028.
5. Yes: -0.105.
6. Yes: -0.247 [-0.363, -0.120].
7. Yes: -0.162 (`conc0.5`), 0.036 (`post0.5`, interval covers 0).
8. Yes: -0.012 and 0.016.

What this means for the paper, if it specifies an observer-step re-baseline: L1_did is never ahead of L1_step on
the trade with an interval excluding 0, and is behind in `conc0.5` at 42 and 63 days. L1_step over L1 does not
hold unconditionally: L1_step is ahead at 63 days when unlogged unmapped changes are absent (rho >= 0.5) and at
42 days when they start after the hold, and behind at 63 days (k 0.5) when they coincide with a logged change;
the other horizon and detector cells cover 0. A rule that re-baselines the unmapped indicators over the hold (as
L1 does) and subtracts the raw step on the mapped ones (as L1_step does) is untested; it should absorb a
concurrent unmapped shift, and, if finding 1's likely reason holds, also D's ramp on the unmapped indicators. The
choice is the project owner's (Abhay's).
