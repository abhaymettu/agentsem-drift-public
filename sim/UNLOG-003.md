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

## Results (run after the plan commit `aeff91d`)

`unlog_003.json` sha256 d430735040ef287e80e9eb10900e285860debe4effe67528340a670fc3bd9b09; the rerun was
byte-identical (`cmp`), also by the Opus reviewer. Every assert passed.

No D change in any arm; added share as the plan defines it (paired). No-shift no-change rates (63 d, k 0.5):
L1 0.304, L1_step 0.211, L1_did 0.211, L2 0.316, oracle 0.211. Unmapped indicators' mean hold z shift: 0.207
(`conc0.25`), 0.413 (`conc0.5`), 0 (`post0.5`).

Table 1. Added alarm share, k 0.5, in-window persons (n = 247), 63 days [95% interval]:

| arm | L1 | L1_step | L1_did | L2 | oracle |
|---|---|---|---|---|---|
| conc0.25 | 0.000 [-0.012, 0.012] | 0.146 [0.104, 0.191] | 0.243 [0.191, 0.298] | 0.178 [0.132, 0.230] | 0.146 [0.100, 0.189] |
| conc0.5 | 0.004 [-0.012, 0.022] | 0.283 [0.228, 0.343] | 0.482 [0.418, 0.540] | 0.397 [0.340, 0.458] | 0.300 [0.243, 0.354] |
| post0.5 | 0.219 [0.173, 0.272] | 0.283 [0.228, 0.343] | 0.251 [0.196, 0.305] | 0.263 [0.211, 0.318] | 0.263 [0.210, 0.316] |

Table 2. Paired differences in added share, same cell:

| arm | L1_did - L1_step | L1_did - L2 | L1_did - oracle | L1_did - L1 |
|---|---|---|---|---|
| conc0.25 | 0.097 [0.037, 0.156] | 0.065 [0.004, 0.128] | 0.097 [0.034, 0.161] | 0.243 [0.192, 0.297] |
| conc0.5 | 0.198 [0.131, 0.265] | 0.085 [0.013, 0.151] | 0.182 [0.106, 0.254] | 0.478 [0.411, 0.541] |
| post0.5 | -0.032 [-0.097, 0.031] | -0.012 [-0.083, 0.049] | -0.012 [-0.074, 0.046] | 0.032 [-0.045, 0.101] |

Findings:
1. **The DiD reference carries an unlogged unmapped shift onto the mapped indicators, and that raises false
   alarms.** The DiD step error falls by the unmapped hold z shift (0.013 to -0.194 and -0.401), as `step_est`
   implies; the evidence is the alarms. L1_did - L1_step in added share is positive in both `conc` arms (table
   2); at `k*`, 63 d: 0.231 [0.162, 0.299] (`conc0.5`) and 0.089 [0.028, 0.151] (`conc0.25`).
2. **L1_did's extra cost is the transfer: L1_step pays the same whether the shift starts at c or after the
   hold.** L1_step holds all indicators over the hold, estimates the step from the mapped indicators only, and
   keeps the unmapped indicators on their baseline z after it, so the two arms differ in what it scores only on
   day c. Its whole alarm series differs between `conc0.5` and `post0.5` for 2 of 247 in-window persons (1 at
   `k*`), and its 63-day alarm indicator for none. L1_did's series differs for 192 (206 at `k*`) and its
   63-day indicator for 57 (66). L1's series also differs (156; 154 at `k*`), because it re-baselines on the
   hold data the two arms do not share.
3. **By 42 days every rule except L1 pays for an unlogged shift; L1 pays for none that starts with the logged
   change.** L1 re-baselines all indicators over the hold, so it absorbs a concurrent shift, the same mechanism
   that made it absorb the D ramp (ABSORB-003). The oracle rule knows the logged change only. At `k*` 21 d,
   L1_step pays 0.000 [0.000, 0.000] (`conc0.25`) and 0.004 (`conc0.5`).
4. **Given a concurrent 0.5 unmapped shift in every person, L1_did's extra false-alarm cost over L1_step exceeds
   its extra sensitivity (points; at 0.25 the intervals overlap).** The planned reading, against L1: L1_did's
   added share in `conc0.5` is 0.482 [0.418, 0.540], against its D-dependent gain over L1 of 0.194 [0.105,
   0.272] (OBS-003, same cell), so the gain is smaller than the added share. The L1_step comparison is added
   because L1 absorbs the concurrent shift (L1_did - L1 0.478 [0.411, 0.541]). In LOAD-003 (rho 1, same cell),
   L1_did - L1_step in D-dependent sensitivity is 0.045 [-0.024, 0.114]; here its extra added share is 0.198
   (`conc0.5`) and 0.097 (`conc0.25`). These come from different arms and are not a paired contrast. How much
   this matters depends on how often such shifts happen, which no run here can estimate.
5. **At 21 days L1_did - L2 is negative in both `conc` arms and both detectors** (`conc0.5`: k 0.5 -0.146
   [-0.208, -0.081], `k*` -0.275 [-0.336, -0.212]), consistent with L1_did's full hold and S reset (L2 holds
   only the mapped indicators). By 63 days at k 0.5 it is positive (table 2).

Expectations, scored clause by clause:
1. Yes.
2. Yes (finding 1, by construction); raw -0.021 in both `conc` arms; DiD within 0.001 of the stated value.
3. Yes (table 2).
4. Yes: points -0.004 to 0.004. In `conc0.5` two interval upper bounds pass 0.02 (k 0.5 63 d 0.022, `k*` 42 d
   0.025); the clause names no interval.
5. Yes (table 2).
6. Yes in all six cells; `k*` 21 d [0.000, 0.021] touches 0.

What this means for the paper, if it specifies an observer-step re-baseline: L1_step (raw hold shift on the
mapped indicators, no DiD) gets most of L1_did's D-dependent sensitivity (0.340 vs 0.385, rho 1, points;
L1_did - L1_step 0.045 [-0.024, 0.114]) without the transfer, and L1_did has the false-alarm route shown here.
The choice of rule is the project owner's (Abhay's).
