# sim/ATTRIBUTION-PLAN-R3.md -- EXPLORATORY, not frozen

Round 3 of the person-versus-observer attribution run. r1 (`sim/ATTRIBUTION-PLAN.md`, sha256 `dbc0024a...`)
ran the default cell; r2 (`sim/ATTRIBUTION-PLAN-R2.md`, sha256 `5ae0419c...`) ran targeted help. This
round runs the two cells no round has run: **`bernoulli_mix` and `pi_rises_with_D`**.

**This run is EXPLORATORY. It is not part of `sim/PREREG.md` or of spec 003, and it changes no P1-P10
verdict, no frozen code path, no number in paper v4 and nothing in `sim/ATTRIBUTION*` r1 or r2.** Its
outputs (`sim/attribution_r3.json`, `sim/ATTRIBUTION-R3.md`) repeat this label. Seeds come from this
file's sha256 with the tag `attribution-r3`, so they cannot collide with PREREG, robustness, r1, r2 or
design-check seeds.

## (a) Why these cells

r2's open list names them (`sim/ATTRIBUTION-R2.md`, Open). Spec 003 r2 (DRAFT, `ca8baf7`) does not take
them, so running them previews nothing in `PREREG-003`. They act only on indicators 4 and 5 (message
length, negative self-reference), the two indicators mixed with agent-written text:

- **`bernoulli_mix`.** Each day is all human or all agent (`pi_t` is 1 with probability `pi_bar = 0.845`,
  else 0) instead of continuous Beta mixing. The authorship filter (ii) then keeps the agent day whole
  (`pi' = 1`) and the human day whole (`pi' = 0`): filtered indicators 4 and 5 carry `D` on about 15% of
  used days and agent noise on the rest. No observer change is tied to the state. This cell asks whether
  r1's conclusions survive a different noise structure on two of six indicators.
- **`pi_rises_with_D`.** The agent's share rises with the person's state: `pi_t = expit(logit(pi_bar) +
  0.5 D_t)`. This is an observer change caused by the person change. The frozen run (P6, metrics item
  (n)) found that it removes the raw validity of indicator 5 (within-person correlation with `D` -0.011
  against 0.340 unmixed) and leaves 0.138 after the filter. **Reading fixed here, before running:** under
  the decided target (sustained mean shift in `D`, spec 001 section 15), a DR alarm is a person change
  whether or not the observer also changed with it, and an S alarm is false. So a rule that reads a DR
  alarm as observer change under `pi_rises_with_D` is wrong by that target, even though the observer did
  change.

## (b) Pairing

`generate_panel` draws the authorship share right after the indicator errors `e` (a 3-D
`standard_normal`): `beta` in `default`, `random` in `bernoulli_mix`, nothing in `pi_rises_with_D`. The
three cells therefore consume the main stream differently, and every later draw (agent text `M`, help
`A`, probe noise, `responded`) would differ across cells. `sim/attribution_r3.py` passes a forwarding
wrapper (`PiRouter`, the same pattern as r1's `LamRecorder`) that serves that one draw from a side stream
(tag `pi`). `drift_sim.py` is unchanged. With the wrapper, one seed gives bit-identical `D`, `Y`,
`responded`, `used`, `L_obs`, help `A` and human-scale indicators `H` in all three cells; only `pi_t`
(hence `X`, `X_filtered`, `pi_prime`) differs. `--check` (DR, 200 persons) and `run()` (every family)
assert this, assert the wrapper routed exactly one draw in `default` and `bernoulli_mix` and none in
`pi_rises_with_D`, and check that the side-stream Beta has the frozen mean and SD.

The default cell here is not r1's or r2's default cell: its `pi_t` comes from the side stream. It is the
paired reference, on new seeds, and is set next to r1 and r2 as a replication.

## (c) Families, scoring, rules, metrics

As r2 section (c), with `bernoulli_mix` and `pi_rises_with_D` in place of the two targeted cells:

- **Families:** S, PS-sub, PS-prop (post-hoc shifts of that cell's S panel, as r1; PS-prop's shift on
  indicators 4 and 5 is scaled by that cell's `1 - pi` in `X` and `1 - pi'` in `X_filtered`, so under
  `bernoulli_mix` the filtered shift is zero on agent days), DR, AV2, CS; 1000 persons each. Help is constant
  (0.3) in all three cells.
- **Scoring:** A-fixed, frozen features, `h = 3.334` from `sim/tuning.json`, frozen CUSUM, per-indicator
  z-scores as r1. `q*` tuned once on a default-cell DR tuning panel (plain generator, tag `tune`), applied
  unchanged in every cell, as the frozen `h` is.
- **Rules:** M0, M1, M2, M2x3, M3, as r1 section (d). Windows as r1.
- **Metrics:** r2's per-cell summary (reused unchanged from `attribution_r2.py`; its two help metrics,
  `help_alarm_minus_tracked` and `feedback_gap_p_target`, are uninformative under constant help and are
  not interpreted), r2's paired contrasts per family and rule (`cell -
  default` share differences, M0 rate ratio, and S's whole-window M2x3 share difference), plus:
  1. **C3**, the PS-sub over S M0 post-change rate ratio per cell.
  2. **C5, mechanism.** In S, the mean of `pi_t`, and of `pi_prime`, on scored alarm days minus on
     tracked days 28-134. In DR, the mean on tracked days in `[t0 + ramp, 134]` minus on tracked days
     `[28, t0)`. Per cell.
  3. **C6.** DR's paired 21-day M0 sensitivity ratio, cell over default, with pre-onset alarms excluding
     detection (the frozen primary, `exclude_pre_onset_alarms=True`) and kept (`False`), plus DR's paired
     pre-onset M0 alarm rate ratio (scored alarms on days `[28, t0)` per tracked person-month).
  4. **Alarm selection.** For S and DR, the paired difference `cell - default` in mean true `D` over the
     probe days `t+1, t+3, t+5` of scored post-change alarms. `Y` and `responded` are identical across
     cells, so the M2x3 share can move only through which alarms fire and when; this metric shows that
     channel.
  5. **Validity.** Per cell, on S, the pooled within-person correlation of filtered indicators 4 and 5
     with `D` over used days, and the unmixed `H` indicator 5 as reference. (The frozen item (n) is the
     person-averaged correlation; this is the pooled one, so the two are not compared number for
     number.)

## (d) Predictions, stated before running

Bounds were sized on a design seed (tag `design-sizing`, not derived from this plan, 1000 persons),
reading bootstrap SEs only. `bernoulli_mix`: S's whole-window M2x3 difference 0.057, DR's 0.024, the
largest of 24 share differences 0.082, PS-sub over S 0.95, M1 share up to 0.042. `pi_rises_with_D`:
0.023, 0.012, 0.032, 0.21, up to 0.020. C5 in S under `pi_rises_with_D` 0.002, in DR 0.001; C6 0.040.
The large `bernoulli_mix` SEs on S quantities imply fewer S alarms in that cell; this was seen before
the bounds below were written, and the S-based bounds for that cell are dropped or loosened accordingly.

- **C1 (the mixing does not move the probes' reading through alarm selection).** The paired difference `cell - default` in the M2x3
  share is within 0.05 of 0 with a 95 percent interval inside +/-0.10: for DR over `[t0, 134]` in both
  cells, and for S over every scored alarm (days 28-134) in `pi_rises_with_D`. S under `bernoulli_mix` is
  reported without a bound (SE 0.057). The probes cannot see `pi` (true by construction: `Y` is paired),
  so C1 tests only the alarm-selection channel. A C1 miss that comes with a shift in metric 4 is read as
  alarm timing or selection, not as the probes seeing the observer change.
- **C2 (the profile test stays powerless).** M1's post-change share (point estimate) is at least 0.80 in
  every family under `pi_rises_with_D`, and at least 0.70 under `bernoulli_mix` (SE up to 0.042; r2's
  lowest share was 0.835).
- **C3 (an observer shift still alarms; close to a construction check, as r2's B3: PS-sub shifts
  indicators 1, 2 and 6, none of which involve `pi`).** The PS-sub over S M0 rate ratio is above 1.5 in both cells;
  under `pi_rises_with_D` its 95 percent interval is also above 1.5. Under `bernoulli_mix` the point
  estimate only (SE 0.95).
- **C5 (mechanism, `pi_rises_with_D`).** In S, `pi_t` on scored alarm days exceeds `pi_t` on tracked days
  by at least 0.02, interval above 0. In DR, post-ramp `pi_t` exceeds pre-onset `pi_t` by at least 0.02,
  interval above 0. Near-certain by construction; it checks that the cell does what (a) says.
- **C6 (direction only; weak, the expected effect is about one SE).** Under `pi_rises_with_D`, DR's
  paired 21-day M0 sensitivity ratio to default (frozen primary) is below 1 (point estimate). Reason: the
  filtered indicator 5 moves toward the agent mean (-1) as `D` rises, against its human loading, so its
  mean shift under DR shrinks. Indicator 4's agent text sits +0.274 human SD above the human mean and
  moves with `D` in the human direction; a rough calculation says it offsets only part of indicator 5's
  loss. A ratio below 1 is read as the composite's smaller mean shift only if the `keep_pre_onset` ratio
  is also below 1; if only the primary ratio is, the pre-onset rate ratio says whether more pre-onset
  alarms did it. No bound on the size.

Every other metric in (c) is reported without a prediction, including all of `bernoulli_mix`'s rate
ratios and C6 for `bernoulli_mix`.

## (e) What this does not do

- No new generator mechanism; `drift_sim.py` unchanged since `9fea182`, `attribution.py` since `ccbcf51`,
  `attribution_r2.py` since `21b28d5`. `drift_sim.py --check` passes except item (c), the documented
  pre-freeze deviation 1 in `sim/PREREG.md`.
- No PREREG seed is used, and no real data is read.
- No new detector or adjustment. A detector that conditions on the logged authored share (the agent
  knows what it wrote, up to filter error) is a design question for spec 003's policy log, not run here.
  **Hazard for spec 003, stated before running:** spec 001 section 15 makes the policy log the primary
  separator. Under `pi_rises_with_D` the authored share changes because `D` changed. A separator that
  labels alarms *observer* when the logged authored share moved would mislabel DR alarms, which are person
  change by the target. Spec 003 section 8 already says endogenous changes never trigger a reset or a
  label; a share that tracks the state continuously is endogenous in that sense but is not a discrete
  entry in the log's current record.
- `kappa`, `m1 > 0`, logged PS and usage-changing PS stay with spec 003 as r2 left them.

## Revisions

- r0 to r1, before hashing. Opus methods review REVISE (3 blocking: C2's bound under `bernoulli_mix`;
  C6's pre-onset confound and its indicator-4 omission; no metric to read a C1 miss), all applied, plus
  non-blocking items 1-6 (C3 and C1 labelled as construction or channel checks, the help metrics marked
  uninformative, the PS-prop wording, the policy-log hazard, a Bernoulli mean check). Item 7 (couple the
  `default` and `bernoulli_mix` shares through one uniform) is not applied: it needs a Beta inverse CDF,
  outside numpy. Ponytail review: 3 cuts, all applied.
- Only `--check`, the design-seed sizing (SEs only, quoted above) and one 60-person smoke run (tag
  `smoke-r3`, only key names printed) ran before this plan was hashed.
