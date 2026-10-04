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
