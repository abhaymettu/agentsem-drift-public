# L1_did's false-alarm route: an unlogged shift on the unmapped indicators

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs whether
PREREG-003 and the paper can specify L1_did (OBS-003) and what it costs. It decides nothing and changes no spec.

Code: `sim/unlog_003.py` -> `sim/unlog_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, W 14, the
design run's resample matrix, NET-003's no-D-change arm (DR+PS persons with `delta_D = 0`: same noise, change
day, log and logged observer step). `obs_003.py` and everything it imports are unchanged.

## Why

LOAD-003 finding 4: L1_did adds the unmapped indicators' mean hold shift to the mapped indicators. When that
shift is D, it raises D-dependent sensitivity. When it is something else, L1_did carries it onto the mapped
indicators too. LOAD-003 could not test this: rho scaled only D's effect, so every no-change rate was fixed by
construction. A rule proposed for the paper needs its specificity cost tested alongside its sensitivity gain.
The case most likely in real data is a second, unlogged observer change (a tool or pipeline update) that moves
message-content indicators at about the time of a logged change on timing indicators.

## Plan (committed before the run)

Arms, all on the no-D-change arm c: an unlogged intercept shift `s` (raw units) on the unmapped indicators 3, 4,
5 from day `c + lag`, applied as the generator applies observer shifts (indicators 4 and 5 carry it in the human
share only). It is applied to the oracle rule's unshifted series too: the oracle rule knows the logged change
only. The logged change and its log are untouched.
- `conc0.25`, `conc0.5`: s 0.25 and 0.5 from the change day (lag 0), so the DiD reference reads it during the hold.
  0.5 is the size of the logged observer step.
- `post0.5`: s 0.5 from day c + 15, after the hold, so no step estimate can see it.

Rules: L1, L1_step, L1_did, L2, the oracle rule. Detectors A-fixed `k = 0.5` (primary) and `k*`; horizons 21,
42 and 63 days from t0 (the onset the no-D-change arm keeps from DR+PS); in-window persons (n = 247).
1. Per rule and arm: the alarm share with the shift and the added share (shifted minus no-shift, per person).
2. Paired differences in added share with intervals: L1_did - L1_step (what the DiD reference transfers),
   L1_did - L2, L1_did - the oracle rule, L1_did - L1.
3. The unmapped indicators' mean hold z shift (baseline z), and the raw and DiD step-estimate errors per arm.

Asserts: the no-shift arm reproduces `obs_003.json`'s no-change rates (5 rules, both detectors, 3 horizons) and
its no-D-change step errors; in `post0.5` both step errors equal the no-shift arm's.

Expected (k 0.5, in-window, 63 days unless stated):
1. The asserts pass.
2. In both `conc` arms the raw step error equals the no-shift arm's (-0.021), and the DiD step error's mean is
   the no-shift arm's (0.013) minus the unmapped hold z shift, to within 0.005.
3. In `conc0.5`, L1_did - L1_step in added share is positive and its interval excludes 0; in `conc0.25` it is
   positive (point).
4. In both `conc` arms, L1's added share is within 0.02 of 0 at both detectors and all horizons (its re-baseline
   absorbs a shift that starts with the hold).
5. In `conc0.5`, L1_did - L2 in added share is positive and its interval excludes 0.
6. In `post0.5`, the L1_did - L1_step interval covers 0 at both detectors and all horizons.

Reading (not an expectation): set L1_did's added share in `conc0.5` against its D-dependent sensitivity gain
over L1 in OBS-003 (0.194 [0.105, 0.272], same cell). A gain smaller than or near the added share means L1_did
buys sensitivity with specificity whenever such shifts are common.
