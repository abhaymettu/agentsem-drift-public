# Spec 003 design run: what PREREG-003 is sized from

**Status: DESIGN STAGE. Every number is synthetic. No prediction is scored, and nothing here is a result.**
Spec 003 section 11 says `PREREG-003` restates every threshold "on the new defaults ... using a
non-evaluation seed and the planned SEs". This file is that sizing.

## Provenance

| item | value |
|---|---|
| code | `sim/study003.py`, commit `e193a51`, sha256 `59357a5830b38e13c3ee9b48a1aa68152f58dc527e541e1afd950ffd6f2445e4` |
| tuning | `sim/tuning_003.json` (tuning seed 20260927 only), sha256 `c7002d79ffb9cf99eabcbd0888fa375ae2c2528fd968237d6ce40fd4384bd51d` |
| design output | `sim/design_003.json`, sha256 `a4064d3ff177a0a7dac904c695e1704590be9af254e8280de18612cee95fdc13` |
| seed | 20261003, which is neither the tuning seed nor a PREREG-003 evaluation seed |
| frozen code | `drift_sim.py` and `attribution.py` unchanged; their sha256 values are recorded in the JSON |

**Checks run:**
- `study003.py --check` passes. Event sampling, the generator (14 family and cell cases), the composite and
  the CUSUM are bit-identical with `drift_sim.py` wherever the frozen code can express them.
- Help-off is exact.
- S, DR and every PS family share the same persons.
- On PS-sub, the oracle rule equals S exactly.
- `tune` and `design` each reproduce byte for byte from a second run (`cmp`).

**Bootstrap.** 1000 person resamples. Every statistic uses one shared resample matrix, so paired
differences are computed directly. Intervals are 95% percentile intervals, written "est [lo, hi]", and
rounded half up to 3 dp. Comparisons across cells (the `m1` and usage cells) use separate samples.

## 1. What the build settles in spec 003's open list (section 13)

- **`c` for matched `k`.** Estimated help-off on the tuning seed: the composite shift of DR-1.0 against the
  paired S panel, on days after the ramp ends.
  - 0.334, 0.336 and 0.342 at `phi_D` 0.3, 0.7 and 0.9.
  - So `k*` is 0.167 to 0.171. The help-on design check gave about 0.35.
- **The 8-probe spacing.**
  - `floor((k + 1) B / m) - 1`. It reproduces the frozen block at 28 days and 4 probes (6, 13, 20, 27).
  - 28 days, 8 probes: 2, 6, 9, 13, 16, 20, 23, 27.
  - 56 days, 4 probes: 13, 27, 41, 55.
  - Flagged CHOICE in the code; reversible before the freeze.
- **`h`.** A-fixed at `k = 0.5` is retuned to 1.898 at `phi_D` 0.7 with the 28-day baseline. This is not
  the frozen detector: it runs help-off, fits the baseline on the scored series (spec 001 18.3(1)), starts
  at day `B` and runs to `T = 210`. The frozen 3.334 is not reused (spec 001 19.2).

## 2. The drafted predictions and construction checks on the design seed

Default unless stated: `phi_D = 0.7`, 28-day baseline, 4 baseline probes, A-fixed `k = 0.5`, design-known
spacing. H1, H4 and H5 are construction checks (spec 003 s11).

| drafted (spec 003 s11) | design-seed estimate | the drafted form would |
|---|---|---|
| H1a: spaced lowers S's confirmed share by at least 0.15 against next-day | -0.236 [-0.302, -0.173] | hold |
| H1b: spaced keeps at least 0.85 of DR-1.0's next-day share | 0.810 [0.715, 0.916] (155 detected persons) | fail on the point estimate |
| H2a: at `phi_D` 0.9, S spaced share minus oracle-reference share at least 0.10 | 0.201 [0.155, 0.246] | hold |
| H2b: a 56-day baseline shrinks that gap by at least 0.05, probes held at 4 | -0.003 [-0.069, 0.057] (gap 0.201 at 28 days, 0.204 at 56) | fail |
| H3: logged PS-sub, L1 within 1.5x of S | 1.421 [1.175, 1.706] | hold on the point; the interval crosses 1.5 |
| H3: logged PS-sub, L2 | 1.171 [1.034, 1.307] | hold |
| H3: logged PS-use, L1 / L2 | 1.376 [1.135, 1.647] / 1.101 [0.970, 1.233] | hold on the point |
| H3: L0 does not (logged PS-sub / PS-use) | 3.061 [2.792, 3.380] / 3.050 [2.790, 3.366] | hold |
| H4: on DR+PS, L2 minus L1 sensitivity for onsets inside the re-baseline window | +0.154 [0.100, 0.209] (247 persons) | hold |
| H5: unlogged PS-prop vs DR-1.0, person share, L0+label | 0.000, exactly | hold by construction (neither family carries a label) |
| H5: same, M1 | 0.020 [-0.013, 0.053] | hold |
| H6: matched `k` minus `k = 0.5`, DR-1.0 21-day sensitivity | -0.014 [-0.034, 0.007] | estimate only |

The H3 ratios are paired: the same persons, over the same post-change window on S. Under matched `k`,
logged PS-sub gives L1 1.217 and L2 0.949.

## 3. Not predicted, and relevant to the freeze

1. **More baseline days reduce selection on the baseline, but not the probe-block gap, at any persistence
   tested.**
   - The true baseline mean `D` of alarmed against non-alarmed S persons:
     - `phi_D` 0.7: -0.231 against +0.151 at 28 days; -0.115 against +0.107 at 56.
     - `phi_D` 0.9: -0.485 against +0.282 at 28 days; -0.324 against +0.175 at 56.
   - The paired 56-against-28-day gap difference (H2b) is about 0 at all three `phi_D`.
   - At 0.7 the gap's point estimates are lower with eight probes: 0.105 (28 days, 4 probes), 0.084 (28, 8),
     0.107 (56, 4), 0.066 (56, 8). The arm intervals overlap, and no paired difference was computed.
2. **Detection at the threshold is low.** A-fixed's S false-alarm rate is about 0.17 per tracked
   person-month.
   - DR-1.0, 21-day sensitivity:
     - A-fixed: 0.155 [0.133, 0.177] at 28 days (chance level 0.044, from pseudo-onsets on S) and 0.210 at
       56 days (chance 0.057).
     - oracle-D, which reads true `D_t` every day (false-alarm rate 0.185 and 0.178; chance 0.076 and
       0.092): 0.336 and 0.399.
   - Matched `k` at `phi_D` 0.7 gives no 21-day gain (H6). At `phi_D` 0.3 with 56 days, H6 is +0.052 [0.028,
     0.077].
   - Matched `k`'s 42-day sensitivity at 0.7 is higher: 0.352 against 0.330 at 28 days, and 0.507 against
     0.430 at 56. That comparison is unpaired.
3. **The L0+label window is shorter than the effect it labels.** Under L0 an observer shift stays in the
   composite, and alarms continue past `W`.
   - With W = 14, DR-1.0's person-labelled share minus PS-sub's is 0.189 [0.158, 0.219]. This mixes logged
     and unlogged persons; unlogged persons are person-labelled by construction.
   - With W = 28, PS-sub's person share falls from 0.811 to 0.620. But DR+PS's falls from 0.878 to 0.694:
     more true changes near a logged change are labelled *observer*.
4. **A ramped observer change survives the rules.**
   - Logged PS-prop stays at 2.604 times S under L1 and 2.304 under L2, against 1.421 and 1.171 for PS-sub.
   - A likely reason, not tested here: the re-baseline is fit over `(c, c + 14]`. For ramps longer than 14
     days (ramps run 7 to 21), it sees only part of the shift.
5. **The reset costs true detections near a logged change.**
   - DR+PS, 21-day sensitivity, logged persons:
     - L0: 0.502. This is inflated by the observer change.
     - L1: 0.081.
     - L2: 0.284.
     - oracle: 0.258.
   - L1 keeps about a third of the oracle's detections.
6. **Endogenous change.** After its own change, PS-endo runs at 2.601 times S's false-alarm rate [2.399,
   2.864]. By design no rule acts on it.
7. **Probes separate person from observer change only partly.** Spaced confirmed share:
   - Of the first post-change alarm: 0.32 to 0.34 for PS-sub, PS-use and PS-prop under L0, L1 and L2;
     0.382 for PS-endo.
   - Of S's first alarm after the baseline: 0.416.
   - Of the first in-window detection: 0.689 for DR-1.0, 0.841 for DR-1.5.
   - The alarm selections differ, and the comparisons are unpaired.
8. **Budget.** Probes per tracked person-month, including the baseline block (spaced, 28 days, 4 probes):
   - S: 1.32. DR-1.0: 2.39. DR-1.5: 3.24.
   - The frozen 7-day rule, at its every-day upper bound, gives 4.49 for DR-1.0.
   - On a sustained shift the detector keeps alarming after each refractory period: 0.735 and 1.182 alarms
     per tracked post-onset month for DR-1.0 and DR-1.5. Each alarm draws three probes, so DR-1.5 exceeds
     the frozen 3.0 budget target.
9. **Response that depends on `D`.** At `m1 = 1.5`, probe response falls as `D` rises, by construction
   (`logit 0.8 - m1 D`).
   - DR-1.0's first detections are then unconfirmable 0.643 [0.560, 0.724] of the time, against 0.148 at
     the default `m1 = 0`.
   - S's unconfirmable share also rises, 0.223 against 0.111.
   - These are separate samples, with no paired difference.
10. **PPV, a scoring fix made in this lane.**
    - The frozen definition counts every alarm outside `[t0, t0 + 21)` as false. Under a sustained shift and
      `T = 210`, the first design run gave DR-1.0 a confirmed PPV of about 0.10. That output was not kept;
      the figure is from the `e193a51` commit message.
    - Spec 003 section 2 counts only pre-onset alarms as false. Under that rule the PPV is 0.571 [0.520,
      0.626] (spaced) and 0.504 (frozen 7-day rule).
    - Confirmed alarms after the 21-day window leave both the numerator and the denominator.
11. **Regression families.** Alarms per tracked person-month against S's 0.166:
    - VA 0.160, DE 0.144, SP 0.171, BI 0.164, CS 0.258.
    - The drift families: BD 0.624, DV 0.595.
    - AV, logged: 0.312 under L0, 0.203 under L1, 0.165 under L2. AV, unlogged: 0.271.

## 4. Proposals for PREREG-003 (not decisions)

1. **H1b.** Restate the threshold at 0.70, or keep 0.85 and expect it to fail. H1 stays a construction
   check either way.
2. **H2b.** Drop it as a prediction. The 56-day effect stays an estimate that answers Q2's baseline
   question (section 6).
3. **H3.** State the decision rule. The proposal: L1 and L2 hold on the point estimate below 1.5, and L0
   holds on its lower bound above 1.5. At L1's design SE of 0.136, an evaluation run of this size puts the
   L1 point above 1.5 about 28% of the time.
4. **H5.** Keep the M1 clause. Label the L0+label clause as true by construction, or drop it.
5. **Budget.** Either confirm once per person episode, with no new probes until the first confirmation
   resolves, or state that DR-1.5 runs above 3.0 per tracked month.
6. **Disclosure.** `PREREG-003` lists this file's sha256 and every number above as seen before the freeze.
   It also lists any scorer change made after this run.

## 5. Open

- **Reason 5, too few available indicators,** cannot fire in this study's families.
- **The `L1_map_omits_6` arm equals L1,** because L1 ignores the map. It is kept as a check.
- **Spec 003 section 11's sentence** "H2's second clause and H3 have no design evidence yet" is stale. It is
  for the freeze to rewrite.
- **Carried:** spec 003 section 13's remaining items, and the 003b elapsed-time filter.
