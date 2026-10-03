# sim/ATTRIBUTION-R3.md -- EXPLORATORY results, not frozen, synthetic only

Plan: `sim/ATTRIBUTION-PLAN-R3.md` r1, sha256 `4c378002ff32220ae7c13539aa3b1ff01af77b1dbd16aaeaa1b33f613fa2cf4b`,
committed at `ddf508e` before any evaluation panel was scored. Code: `sim/attribution_r3.py` at that
commit (`--check` passes). Raw output: `sim/attribution_r3.json`. Not part of `sim/PREREG.md`; no P1-P10
verdict, no paper v4 number and nothing in r1, r2 or spec 003 changes. 1000 simulated persons per family
and cell, A-fixed at the frozen `h = 3.334`, constant help. Person bootstrap, 2000 draws; brackets are 95
percent intervals. `q* = 6.76`, from 251 tuning-panel DR alarms. A second run from the committed hash
gave a byte-identical JSON (`cmp`; sha256 `21be844256fdd41f786d50dea7a0070647ef49f364f76a027e5cd2087c810dc2`).
`drift_sim.py` (unchanged since `9fea182`) `--check` passes except item (c), the documented pre-freeze
deviation 1 in `sim/PREREG.md`; `attribution.py` and `attribution_r2.py` are unchanged.

Cells: `default` (Beta mixing of agent text into indicators 4 and 5, the paired reference),
`bernoulli_mix` (each day all human or all agent) and `pi_rises_with_D` (the agent's share rises with
`D`). One seed per family serves all three cells; `D`, `Y`, `responded`, `used`, `L_obs`, help and the
human-scale indicators are bit-identical across cells (asserted), so cell contrasts are paired by person.

## Predictions

| | prediction | estimate | holds |
|---|---|---|---|
| C1 | M2x3 share, cell minus default, within 0.05 and interval inside +/-0.10: DR, `bernoulli_mix` | +0.091 [+0.053, +0.133] | no |
| C1 | same, DR, `pi_rises_with_D` | +0.024 [+0.001, +0.048] | yes |
| C1 | same, S over every scored alarm, `pi_rises_with_D` | -0.054 [-0.101, -0.008] | no (narrowly) |
| C2 | M1 share at least 0.80 in every family (`pi_rises_with_D`), at least 0.70 (`bernoulli_mix`) | lowest 0.839 (S); lowest 0.816 (PS-sub) | yes |
| C3 | PS-sub over S M0 rate ratio above 1.5 (interval too, `pi_rises_with_D`) | 4.05 [3.61, 4.58]; `bernoulli_mix` 6.97 [5.16, 10.24] | yes |
| C5 | `pi_rises_with_D`: S alarm-day `pi_t` minus tracked, and DR post-ramp minus pre-onset, at least 0.02, interval above 0 | S +0.060 [+0.055, +0.065]; DR +0.057 [+0.056, +0.059] | yes |
| C6 | `pi_rises_with_D`: DR 21-day M0 sensitivity ratio to default below 1 | 0.807 [0.723, 0.894] | yes |

**Reading the C1 misses by the rule stated in the plan.** Both misses come with a shift in the paired
alarm-selection metric (mean true `D` on the probe days `t+1, t+3, t+5`, cell minus default): DR under
`bernoulli_mix` +0.096 [+0.016, +0.178], S under `pi_rises_with_D` -0.254 [-0.346, -0.166]. They are
therefore read as changes in which alarms fire, not as the probes seeing the mixing. The S miss is over
every scored alarm (days 28-134); the selection metric, as the plan defines it, covers post-change alarms
only. One sign does not line up: DR under `pi_rises_with_D` has a selection shift of -0.042 [-0.083,
-0.001] and still a +0.024 M2x3 share; this is not resolved here. S under `bernoulli_mix`, reported
without a bound, is +0.021 [-0.095, +0.136].

**Reading C6 by the plan's rule.** The ratio with pre-onset alarms kept is also below 1, 0.836 [0.777,
0.898], so the loss is read as a smaller composite shift under drift, not as extra pre-onset alarms. The
pre-onset rate ratio is 0.875 [0.796, 0.956], so pre-onset alarms fell too. Under `bernoulli_mix`
(no prediction): 0.260, kept 0.207, pre-onset rate ratio 0.205.

## Paired contrasts whose intervals exclude the null

Cell minus default (shares) or cell over default (M0 rate ratio), from `contrasts/` in the JSON. All six
`bernoulli_mix` rate ratios lie between 0.168 and 0.327; they are not repeated below.

| cell | family | contrast | estimate |
|---|---|---|---|
| `bernoulli_mix` | PS-sub | M1 share | -0.072 [-0.118, -0.027] |
| | PS-prop | M2, M2x3, M3 share | +0.090, +0.096 [+0.033, +0.155], +0.073 |
| | DR | M2x3, M3 share | +0.091 [+0.053, +0.133], +0.078 [+0.027, +0.129] |
| `pi_rises_with_D` | S | M2, M2x3, M3 share (post-change) | -0.085, -0.111 [-0.181, -0.044], -0.086 |
| | PS-sub | M2x3, M3 share | -0.041 [-0.073, -0.008], -0.046 [-0.081, -0.014] |
| | PS-prop | M1, M2, M3 share; M0 rate ratio | -0.021, -0.035, -0.032; 1.080 [1.051, 1.111] |
| | DR | M1, M2x3, M3 share; M0 rate ratio | +0.044, +0.024, +0.054; 0.802 [0.776, 0.828] |
| | CS | M2 share | -0.053 [-0.100, -0.005] |

The other `pi_rises_with_D` rate ratios (S 0.917, PS-sub 1.026, AV2 1.048, CS 1.013) have intervals
that include 1. With 62 contrasts, about three would exclude the null by chance; the single
PS-prop M1 and CS M2 entries are not interpreted.

## The default cell as a replication

PS-sub over S is 3.62 [3.26, 4.05] (r1 3.50, r2's default 3.15). The A6 difference of gaps is 0.270
[0.220, 0.318] (r1 0.279, r2 0.284). M1 keeps 0.839 to 0.927 of alarms in every family (r1 0.871 to
0.925). r1's three conclusions hold on new seeds with the side-stream share.

## Results by cell

Post-change scored alarms, rate per tracked person-month, shares of scored alarms.

| cell | family | alarms | rate M0 | share M1 | share M2x3 | `D` on probe days |
|---|---|---|---|---|---|---|
| default | S | 230 | 0.144 | 0.839 | 0.604 | 0.48 |
| | PS-sub | 833 | 0.521 | 0.888 | 0.540 | 0.44 |
| | DR | 1199 | 0.751 | 0.903 | 0.775 | 1.32 |
| `bernoulli_mix` | S | 39 | 0.024 | 0.846 | 0.590 | 0.45 |
| | PS-sub | 272 | 0.170 | 0.816 | 0.570 | 0.39 |
| | DR | 321 | 0.201 | 0.903 | 0.866 | 1.42 |
| `pi_rises_with_D` | S | 211 | 0.132 | 0.839 | 0.493 | 0.23 |
| | PS-sub | 855 | 0.535 | 0.876 | 0.499 | 0.34 |
| | DR | 961 | 0.602 | 0.947 | 0.799 | 1.28 |

PS-prop, AV2 and CS are in the JSON. DR 21-day M0 sensitivity: default 0.181, `bernoulli_mix` 0.047,
`pi_rises_with_D` 0.146.

**Validity of the filtered indicators** (S panel, pooled within-person correlation with `D` over used
days; unmixed indicator 5 is 0.346):

| cell | indicator 4 | indicator 5 |
|---|---|---|
| default | 0.279 | 0.272 |
| `bernoulli_mix` | 0.071 | 0.068 |
| `pi_rises_with_D` | 0.342 | 0.141 |

Same direction as the frozen run's indicator 5 (metrics item (n), 0.138, different estimator).

## What the numbers say

1. **An observer change tied to the person's state is not misread as observer change by the probes or by
   the profile test. Its cost is detection.**
   - Under `pi_rises_with_D`, DR's probe-confirmed share is unchanged (C1), and M1's DR share rises
     rather than falls (+0.044 [+0.029, +0.059]).
   - DR's 21-day sensitivity falls (C6). Filtered indicator 5's validity halves and indicator 4's rises
     (table above). Indicator 4's rise is consistent with its agent text sitting above the human mean
     (not tested).
   - So, by the decided target, the state-tied share is a measurement-validity problem for the composite,
     not an attribution problem.
   - The share does move after a person change, by +0.057 in `pi_t` and +0.118 in `pi'` (C5, DR). This
     is the hazard the plan named: a policy-log rule that read a change in the logged authored share as
     observer change would mislabel these persons. No such rule was run.

2. **The mixing regime sets the detector's operating point.**
   - The frozen `h` was tuned under Beta mixing. Under `bernoulli_mix` it gives:
     - M0 alarm rates of 0.17 to 0.33 times default in every family (S 0.170 [0.109, 0.227]);
     - 0.26 [0.19, 0.33] of DR's 21-day sensitivity.
   - Validity falls to about 0.07 (table above) because, on an all-agent day, the generator's filter
     returns an indicator made entirely of falsely kept agent text (`pi' = 1`). Why the alarm rate
     falls was not tested.

3. **Not predicted: the day's authorship share is a false-alarm route even with the filter.**
   - In the default cell, S alarm days have a filtered share `pi'` 0.068 [0.050, 0.085] below tracked
     days (`pi_t` 0.035 below). Under `bernoulli_mix` the gap is 0.148 [0.048, 0.259].
   - Alarms fire more on days with more human text (untested guess: indicator 5's agent text has mean
     -1, below the human mean).
   - In `pi_rises_with_D`, S alarms fire at a mean `D_t` of 0.98 against 1.26 in default, and S's M2x3
     share falls (C1's narrow miss). That is consistent with this route working against the state route
     when the share rises with `D` (not tested).
   - C5 in DR without coupling: default -0.001 [-0.002, +0.001], `bernoulli_mix` -0.002 [-0.007, +0.004].

4. **Construction limits.**
   - The `default` and `bernoulli_mix` shares are paired in persons, not in the share draw itself.
     Coupling the two draws through one uniform would need a Beta inverse CDF, which numpy lacks.
   - Help is constant, so r2's help metrics in the JSON (`help_alarm_minus_tracked`,
     `feedback_gap_p_target`) are not interpreted.
   - The generator has no minimum-human-text rule for indicators 4 and 5.

## For the next study's spec (INFERENCE, not run)

- **The pilot's mixing regime lies between these two cells in day-level SD.** Its realized day-level SD
  of `pi` is 0.174 and the frozen Beta gives 0.109 (`drift_sim.py` lines 83-84, PREREG known deviation);
  a Bernoulli day with the same mean gives sqrt(0.845 x 0.155) = 0.362 (computed here). Whether the
  pilot's days are bimodal is not known. This run does not show where the frozen `h` sits for that regime. The
  next study should tune `h` under the pilot's estimated share distribution, or test a rule that marks
  indicators 4 and 5 missing on days with too little human text.
- **The authored share is known to the agent, up to filter error.** It can be logged per day as a
  covariate. If it moves with the state, as `pi_rises_with_D` builds in, logging it as an observer-change
  event would mislabel person change (point 1). Spec 003 section 8's "endogenous" means caused by the
  layer's own output, not by the person's state, so its never-label rule does not cover this case as
  written, and its record has no field for a continuous share.

## Review trail

| step | reviewer | outcome |
|---|---|---|
| plan | Opus methods review | REVISE, 3 blocking, all applied before hashing; non-blocking 6 of 7 applied |
| plan | ponytail | 3 cuts, all applied |
| write-up | Opus accuracy review | REVISE, 6 blocking, all applied; 6 non-blocking applied |
| write-up | ponytail | 8 cuts; 7 applied, 1 shortened instead (the untested human-text guess, which the next-study section uses) |
