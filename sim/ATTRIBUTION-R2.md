# sim/ATTRIBUTION-R2.md -- EXPLORATORY results, not frozen, synthetic only

Plan: `sim/ATTRIBUTION-PLAN-R2.md` r1, sha256
`5ae0419c911da13dd270c41e77582562efc7fe588ba4117416db1d7eb4e220e3`, committed at `21b28d5` before any
evaluation panel was scored. Code: `sim/attribution_r2.py` at that commit (`--check` passes); it
imports `drift_sim.py` and r1's `attribution.py` unchanged. Raw output: `sim/attribution_r2.json`. A
second run from the same hash reproduces it byte for byte (`cmp` identical; both sha256
`a79b3a31f65463a7861c9ae7f441a40045e0a6e6dc35222c1f8240964521a5b2`). Not part of `sim/PREREG.md` or spec 003; no
P1-P10 verdict, no paper v4 number and nothing in r1's `sim/ATTRIBUTION*` changes.

Setup:
- 1000 simulated persons per family, A-fixed at the frozen `h = 3.334`.
- Three cells: `default` (constant help 0.3), `targeted` (help probability rises with A-fixed's
  composite of the day before), and `targeted_theta1_05` (as `targeted`, with help's effect scaled by
  `1 + 0.5 D`).
- Each family uses one seed in all three cells. `D`, the probes and usage are therefore identical
  across cells, and the cell contrasts are paired by person.
- Person bootstrap, 2000 draws. `±` is the bootstrap SE, and brackets are 95 percent intervals.
- Runtime 83 s (shell `time`, first run).
- `q* = 6.38`, from 278 default-cell tuning DR alarms (r1: 6.59).

Skipped, with reasons in the plan's section (a):
- `kappa`, `m1 > 0` and logged PS, which spec 003 r2 takes into the next study;
- usage-changing PS, which needs a generator extension;
- the mixing cells, which are outside this brief.

## Predictions

| | prediction | estimate | holds |
|---|---|---|---|
| B1 | `targeted - default` M2x3 share within 0.05 of 0, interval inside +/-0.10: S (every scored alarm) and DR | S +0.010 ± 0.021 [-0.029, +0.052]; DR -0.016 ± 0.011 [-0.037, +0.004] | yes |
| B2 | under `targeted`, M1 share at least 0.80 in every family (near-certain) | 0.835 (CS) to 0.922 (AV2) | yes |
| B3 | under `targeted`, PS-sub over S M0 rate ratio above 1.5 with interval above 1.5; ratio to default's ratio in 0.8 to 1.25 (close to true by construction) | 3.00 ± 0.14 [2.74, 3.32]; 0.952 ± 0.034 | yes |
| B4 | `theta1_05 - targeted`: all 24 share differences within 0.04; all M0 rate ratios in 0.95 to 1.05 (construction check) | largest share difference 0.0095 (CS, M2); rate ratios 0.990 to 1.011 | yes |
| B5 | in S, (help on alarm days minus help on tracked days) under `targeted`, minus the same under `default`, at least 0.05, interval above 0 (mechanism check) | 0.204 ± 0.028 [0.148, 0.261] | yes |

## Results by cell

Post-change window `[max(c_i, 28), 134]`. The rate is M0 alarms per tracked person-month. The share is
the fraction of scored alarms read as person change.

| family | cell | alarms | rate M0 | share M1 | share M2 | share M2x3 |
|---|---|---|---|---|---|---|
| S | default | 271 | 0.171 ± 0.012 | 0.889 | 0.557 | 0.590 ± 0.032 |
| S | targeted | 290 | 0.183 ± 0.012 | 0.890 | 0.514 | 0.597 ± 0.028 |
| PS-sub | default | 855 | 0.539 ± 0.021 | 0.895 | 0.473 | 0.508 ± 0.019 |
| PS-sub | targeted | 871 | 0.549 ± 0.021 | 0.908 | 0.483 | 0.527 ± 0.020 |
| PS-prop | default | 1178 | 0.742 ± 0.023 | 0.875 | 0.442 | 0.479 ± 0.017 |
| PS-prop | targeted | 1179 | 0.743 ± 0.023 | 0.880 | 0.436 | 0.481 ± 0.016 |
| AV2 | default | 583 | 0.368 ± 0.017 | 0.940 | 0.473 | 0.532 ± 0.023 |
| AV2 | targeted | 615 | 0.388 ± 0.018 | 0.922 | 0.447 | 0.491 ± 0.022 |
| CS | default | 584 | 0.361 ± 0.017 | 0.827 | 0.486 | 0.519 ± 0.022 |
| CS | targeted | 632 | 0.391 ± 0.018 | 0.835 | 0.519 | 0.528 ± 0.022 |
| DR `[t0, 134]` | default | 1168 | 0.737 ± 0.023 | 0.891 | 0.649 | 0.779 ± 0.014 |
| DR `[t0, 134]` | targeted | 1166 | 0.736 ± 0.023 | 0.899 | 0.626 | 0.763 ± 0.014 |

Other planned metrics:
- **DR retention under M1** (21-day sensitivity ratio to M0): 0.957 default, 0.948 targeted, 0.934
  theta1 (r1 0.916). `q*` was tuned on a separate panel, so the default cell is not exactly 0.9.
- **M1 not assessable:** 0 of alarms in every family and cell.
- **S's M2x3 share over every scored alarm:** 0.570 default, 0.581 targeted.
- In the JSON only: DR sensitivity per rule, the A6 M1 and M2x3 gaps per cell, M3 shares, the
  selection table, and help concentration in the theta1 cell.

**DR 21-day sensitivity** under M0, with the ratio to M0 under M2x3:
- default: 0.186, ratio 0.871 ± 0.039;
- targeted: 0.193, ratio 0.855 ± 0.039;
- theta1: 0.196, ratio 0.878 ± 0.039.

Each cell's SE is about 0.012, and no paired interval was computed for the sensitivity difference.

**Paired `targeted / default` M0 rate ratios** (none was predicted):

| family | ratio | interval |
|---|---|---|
| S | 1.070 ± 0.037 | [1.003, 1.146] |
| CS | 1.082 ± 0.022 | [1.041, 1.125] |
| AV2 | 1.055 ± 0.024 | [1.010, 1.102] |
| PS-sub | 1.019 | [0.990, 1.051] |
| PS-prop | 1.001 | [0.978, 1.024] |
| DR | 0.998 | [0.972, 1.023] |

**Paired share differences, `targeted - default`.** Of the 24 share differences (6 families x 4
rules), two have intervals that exclude 0, both in AV2:
- M2x3: -0.041 ± 0.019 [-0.078, -0.003];
- M3: -0.050 ± 0.019 [-0.087, -0.013].

**Help concentration in S.** Help on scored alarm days against tracked days 28-134:
- default: 0.341 against 0.302 (gap 0.039 ± 0.022, interval [-0.005, 0.084], which includes 0);
- targeted: 0.587 against 0.344.

**PS feedback gap** (targeting probability the shifted composite implies, minus the one drawn, on
post-change tracked days). It is the same in all three cells, so it belongs to the shift, not to the
help regime:
- PS-sub: +0.049;
- PS-prop: +0.064.

Its effect on PS-sub's rate was not computed, and its sign is unknown.

**Default cell against r1** (new seeds, same design):

| quantity | r2 | r1 |
|---|---|---|
| PS-sub over S M0 ratio | 3.15 ± 0.15 | 3.50 ± 0.18 |
| M1 share range | 0.83 to 0.94 | 0.87 to 0.93 |
| DR M2x3 share | 0.779 | 0.756 |
| A6 difference of gaps | 0.284 ± 0.025 | 0.279 ± 0.027 |
| M1 known answer: DR minus PS-prop share | 0.016 ± 0.015 | 0.022 ± 0.015 |
| DR 21-day sensitivity under M0 | 0.186 | 0.166 |

## Reading

1. **Targeted help leaves the retested attribution results where r1 found them.**
   - **The probe rules.** Help moves neither `D` nor the probe answer, and each alarm's probe verdict
     reads only the paired `Y` and `responded`. The alarm set does change, so B1 is an empirical
     result, not something the design implies.
   - **B2, B3.** Both hold as in r1 (table above).
   - **A6.** The probes still separate DR from PS-prop by 0.26 more than M1 does, in both targeted
     cells (default 0.28).

2. **`theta1` does not move A-fixed's attribution results** (B4). A help effect that grows with the
   state reaches A-fixed through two channels:
   - the baseline fit, which includes helped days;
   - the help draws, which follow the changed composite.

   The filter removes everything else. Together the two channels change no post-change share by 0.01
   or more. Whether `theta1` matters for detectors without filter (i) is P2's question in the frozen
   run, and it is not tested here.

3. **Targeting concentrates help on alarm days, and the families with no person change alarm a little
   more.**
   - **Help.** Targeting puts help on alarm days by construction (B5). On a helped day the composite
     averages 4 indicators, not 6.
   - **Alarm rates.**
     - S, AV2 and CS rise 5 to 8 percent, with intervals above 1.
     - PS-sub, PS-prop and DR do not; the PS families' help was drawn from S's composite.
   - **Mechanism, not tested.** The rises are consistent with dropout of indicators 2 and 3 on
     high-composite days raising the composite's variance. At `theta1 = 0` the dropout pattern is the
     only systematic channel after the baseline.
   - **AV2.** Its two share differences that exclude 0 (above) are 2 of 24 correlated contrasts. About
     1.2 are expected to exclude 0 by chance, so they are not interpreted.

   If the rises are real, they are a smaller instance of r1's point that the agent's own behavior
   changes which alarms fire.

4. **The PS construction misses some help under targeting** (the feedback gap above). B3's first
   clause fails only if the missing help halves PS-sub's targeted rate (3.0 against 1.5). The largest
   targeting effect on any rate in this run is 1.08.

## Open

- **The mixing cells** (`bernoulli_mix`, `pi_rises_with_D`) are not run in any attribution round and
  are not in spec 003. `pi_rises_with_D` is the agent's authorship share rising with the state, an
  observer change tied to `D`.
- **If spec 003 changes.** `kappa`, `m1 > 0` and logged PS are left to spec 003. If its DRAFT drops
  them, they return here.
- **Usage-changing PS** needs `study003.py` (spec 003's PS-use).
- **Help in a policy log.** Whether the dropout cost of targeted help (point 3) belongs in spec 003's
  log as an endogenous entry. Spec 003 keeps help off in its default cell and defers targeted help.
