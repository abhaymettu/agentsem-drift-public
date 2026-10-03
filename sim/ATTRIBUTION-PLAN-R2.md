# sim/ATTRIBUTION-PLAN-R2.md -- EXPLORATORY, not frozen

Round 2 of the person-versus-observer attribution run (`sim/ATTRIBUTION-PLAN.md` r1, plan sha256
`dbc0024a...`, results `sim/ATTRIBUTION.md`). r1 ran spec 001's default cell only. This round runs
the one remaining cell that the next study does not take over: **targeted help**.

**This run is EXPLORATORY. It is not part of `sim/PREREG.md` or of spec 003, and it changes no P1-P10
verdict, no frozen code path, no number in paper v4 and nothing in `sim/ATTRIBUTION*` r1.** Its
outputs (`sim/attribution_r2.json`, `sim/ATTRIBUTION-R2.md`) repeat this label. Seeds come from this
file's sha256 with the tag `attribution-r2`, so they cannot collide with PREREG, robustness, r1 or
design-check seeds.

## (a) Which cells, and why only one

r1 left these unrun: `m1 > 0`, `kappa`, targeted help, the two mixing cells (`bernoulli_mix`,
`pi_rises_with_D`), and logged PS. This round's brief names four of them (`m1 > 0`, `kappa`, targeted
help, logged PS); the mixing cells are outside it and stay open. They act on indicators 4 and 5 through
the authorship filter (ii), and spec 003 does not take them.

Spec 003 r2 (DRAFT, commit `ca8baf7`) puts three of the brief's four into the next study's design:

- `kappa` in {-0.3, 0.3} and `m1` in {0.5, 1.5} at `phi_D = 0.7` (spec 003 section 5, grid);
- logged PS. r1's version is the frozen reset (iv) mapped to indicators 1, 2 and 6: `S` is reset, the
  mapped indicators are held 14 days and re-baselined. That lies between spec 003's L1 (every indicator
  re-baselined) and L2 (mapped indicators only, `S` running). H3 tests logged PS-sub under both L1 and
  L2.

Running them here would show their direction before `PREREG-003` freezes its thresholds, so they are
skipped. Spec 003 is a DRAFT; if it later drops the grid or L2, those cells have no study and return
to this list. Spec 003 defers targeted help ("Targeted help is deferred", section 5). That cell is run
here. Usage-changing PS needs a generator extension and stays out (spec 003's PS-use).

## (b) Mechanism, from the frozen code

In the `targeted` cell, from day 28 the agent helps on day `t` with probability
`clip(expit(logit(0.3) + C_{t-1}), 0.1, 0.9)`, where `C` is A-fixed's own composite without (iv). A
held day (`C` NaN) keeps the last value, which starts at 0.
During the baseline, days 0-27, help is constant at 0.3, as in the default cell. Help lowers indicators
2 and 3 (fragmentation, deferral) by `psi = 0.5`, times `(1 + theta1 D_t)`; `theta1 = 0.5` in
`targeted_theta1_05` and 0 otherwise. Help moves neither `D` nor the probe answer `Y`.

A-fixed's unhelped filter (i) drops indicators 2 and 3 on every helped day. Help's effect on the
indicator values therefore never reaches the post-baseline composite. Targeted help changes A-fixed in
two ways:
- **Which days lose indicators 2 and 3.** Help is now concentrated on days after a high composite, so
  during an alarm's run-up the composite averages fewer indicators.
- **The baseline fit** (days 0-27, help constant at 0.3). Under `theta1 = 0.5`, helped baseline days
  carry the extra `-0.25 D` on indicators 2 and 3. Help draws then follow from the changed composite.

**Pairing across cells.** The constant-help branch draws `n x T` uniforms. The targeted branch draws
`n x 28`, then `n` per day for 112 days, the same count; `theta1` draws nothing. Every draw after the
help branch is therefore identical across cells for one seed: the probe noise, `responded`, the probe
answers `Y`. So is every draw before it: `D`, events, usage, loadings, context, mixing. Help itself is
not paired between `default` and the targeted cells: the two branches read the uniforms in a different
order, even on days 0-27. `targeted` and `targeted_theta1_05` share their uniforms, and their help
differs only through the composite. `X` and `H` differ with help. In a 300-person trial panel (seed 5,
S) the post-baseline help rate was 0.300 against 0.340. `--check` (DR, 200 persons, seed 1) and `run()`
(every family, both targeted cells against `default`) assert that `D`, `Y`, `responded`, `used`,
`L_obs` and `pi_t` are bit-identical.

## (c) Families, cells, scoring and rules

- **Cells:** `default` (the paired reference, new seeds; r1's numbers are not reused), `targeted`, and
  `targeted_theta1_05`.
- **Families:** S, PS-sub, PS-prop, DR, AV2 and CS, built as in r1 section (b), 1000 persons each.
  - DR, AV2 and CS are generated in each cell, with help feedback live.
  - PS-sub and PS-prop are post-hoc shifts of that cell's S panel, as in r1. Under targeted help this
    has a known gap: help was drawn from the unshifted composite, so the extra help the shift would
    have triggered is missing. That extra help would drop indicators 2 and 3 more often. On helped and
    unhelped days PS-sub's mean composite shift is the same (1.5/6 = 1.0/4), so the missing help acts
    only through composite variance and the baseline fit, and its sign on B3 is unknown. The gap is
    sized, not corrected: on post-change tracked days, the mean of the targeting probability that the
    shifted composite implies, minus the one the unshifted composite implies. Days where either
    `C_{t-1}` is NaN are left out (the generator would hold the last value). This uses A-fixed's
    composite as scored, which equals the feedback composite when no version change is logged, as in S
    (`--check` asserts it).
- **Scoring:** A-fixed with the frozen features, `h = 3.334` from `sim/tuning.json`, the frozen CUSUM,
  and per-indicator z-scores as in r1 section (c). The scored-alarm window (days 28-134), the
  post-change window `[max(c_i, 28), 134]` and DR's windows are as in r1.
- **Rules:** M0, M1, M2, M2x3 and M3, as in r1 section (d).
  - `q*` is tuned once, as in r1, on a default-cell DR tuning panel (tag `tune`). It is applied
    unchanged in every cell, as the frozen `h` is.
  - DR retention under M1 is reported per cell. It is near 0.9 by construction only in the default
    cell (r1: 0.916).
- **Metrics,** per cell: r1's post-change rate and share per rule, DR's 21-day sensitivity and its
  ratio to M0, the momentary-state selection table, the M1 not-assessable share, and r1's A6 gaps
  (M1, M2x3, and their difference). S's shares are also reported over every scored alarm, days 28-134.
  DR's share over `[t0, t0 + 21)` and the probe cost are not repeated. Plus:
  1. **Paired cell contrasts** per family and rule, by person bootstrap with one index array for both
     cells: `targeted - default` and `targeted_theta1_05 - targeted`, for post-change shares and for
     the M0 post-change rate as a ratio.
  2. **Help concentration.** Help rate on scored alarm days and on tracked post-baseline days (days
     28-134), in S, per cell, and the paired difference of that gap, `targeted - default`.
  3. **The PS feedback gap** described above.

## (d) Predictions, stated before running

Bounds were sized on a design seed (tag `design-sizing`, not derived from this plan, 1000 persons),
reading bootstrap SEs only: S's whole-window M2x3 difference 0.020, DR's 0.010, B5's
difference-in-differences 0.030, the largest `theta1` share difference 0.013.

- **B1 (probes are not moved by help).** The paired difference `targeted - default` in the M2x3 share
  is within 0.05 of 0, and its 95 percent interval lies inside +/-0.10: for S over every scored alarm
  (days 28-134; S has no change), and for DR over `[t0, 134]`.
- **B2 (the profile test stays powerless; near-certain).** Under `targeted`, M1's post-change share is
  at least 0.80 in every family. Targeted help leaves indicators 2 and 3 fewer usable days before an
  alarm, which shrinks `Q`.
- **B3 (an observer shift still alarms).** Under `targeted`, the PS-sub over S M0 post-change rate
  ratio is above 1.5, with a 95 percent interval above 1.5. Second clause, close to true by
  construction (PS-sub inherits S's help, and its per-day shift does not depend on help): the ratio to
  the default cell's PS-sub over S ratio is between 0.8 and 1.25 (point estimate).
- **B4 (construction check, `theta1`).** Between `targeted_theta1_05` and `targeted`:
  - every paired post-change share difference (6 families x M1, M2, M2x3, M3) is within 0.04 of 0
    (about 3 SE, since 24 conditions are checked);
  - every family's M0 post-change rate ratio is within 0.95 to 1.05.
- **B5 (mechanism check, help concentration).** In S, (help rate on scored alarm days minus help rate
  on tracked days 28-134) under `targeted`, minus the same under `default`, is at least 0.05, with a
  paired 95 percent interval above 0. The default-cell gap is reported without a bound: constant help
  is tied to alarms through composite variance (a helped day averages 4 indicators) and through the
  baseline fit, which includes helped days.

Every other metric in (c) is reported without a prediction; default-cell r2 is set next to r1 as a
replication on new seeds.

## (e) What this does not do

- No new generator mechanism.
  - `sim/attribution_r2.py` imports `drift_sim.py` unchanged.
  - It reuses r1's functions from `sim/attribution.py` unchanged.
  - `drift_sim.py --check` passes except item (c), the documented pre-freeze deviation 1 in
    `sim/PREREG.md`. The file is unchanged since `9fea182`.
- No PREREG seed is used, and no real data is read.
- No A-fixed ablation. Removing filter (i) under targeted help is P2's question, settled in the frozen
  run.

The momentary-versus-sustained target is decided (sustained mean shift, spec 001 section 15). S alarms
are counted as false here, as in r1.

## Revisions

- **r0 to r1, before hashing.** Opus methods review REVISE (3 blocking, all applied) and a ponytail
  review (8 cuts, all applied); B4's bound widened from 0.03 to 0.04 after the sizing. Only two smoke
  runs (100 and 60 persons, outputs suppressed) and the design-seed sizing (SEs only) ran before this plan was hashed.
