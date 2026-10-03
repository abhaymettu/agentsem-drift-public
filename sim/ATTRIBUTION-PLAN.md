# sim/ATTRIBUTION-PLAN.md -- EXPLORATORY, not frozen

Spec 001 section 11.5 names the one contribution left open: a specified comparison that separates
change in the person from change in how the agent observes. This plan runs the smallest version of it
on the frozen generator. It asks: after an A-fixed alarm, can a scoring rule tell a change in `D` from
a change in the indicators' measurement, and what does each kind of evidence cost?

**This run is EXPLORATORY. It is not part of `sim/PREREG.md` and changes no P1-P10 verdict, no frozen
code path, and no number in paper v4.** Its outputs (`sim/attribution.json`, `sim/ATTRIBUTION.md`)
repeat this label. Seeds come from this file's sha256, with the tag `attribution`, so they cannot
collide with PREREG or robustness seeds. Results are candidate evidence for the next study's spec
(section 11.5's PS family); nothing here is frozen for it.

Revision r1 applies an Opus methods review (REVISE, 6 blocking items, all applied) before any
evaluation panel was scored. Only a 100-person smoke run with throwaway seeds, outputs suppressed, ran
before this plan was hashed.

## (a) The identification point (known result, new setting)

In the generator, indicator `j` on a used day is `lam_ij D_t + (other terms) + e_jt`. A change of the
person's state by `c` moves indicator means by `lam_ij c`. A change in measurement moves them by
intercept shifts `tau_ij` with `D` unchanged; neither changes residual variances here. From indicators
alone the two are distinguishable only when `tau_i` is not proportional to `lam_i`: a factor-mean change
and intercept changes proportional to the loadings give the same indicator means. This is the
measurement-invariance result (Meredith 1993, Psychometrika 58:525-543; partial invariance, Byrne,
Shavelson & Muthen 1989, Psychol Bull 105:456-466; longitudinal form, Widaman, Ferrer & Conger 2010,
Child Dev Perspect 4:10-18) applied to one person's change. Separating a proportional observer change
needs evidence outside the trace: a probe answer (`Y_t = D_t + e_Y`) or a log of the change (A-fixed's
(iv)). In this generator one channel breaks exact equivalence: `D` also moves context shares through
`ETA_CTX = 0.1`, which shifts `beta_ctx` on indicators 1, 4 and 5 by about 0.008 per unit of `D`, about
2 percent of the loading term.

## (b) Families (1000 persons each, frozen default cell)

| family | source | change from day `c_i` | `D` changes |
|---|---|---|---|
| S | frozen generator | none | no |
| PS-sub | the S panel, post-hoc | step intercept +0.5 on indicators 1, 2, 6 (late share, fragmentation, reply latency), unlogged, indicator-only | no |
| PS-prop | the S panel, post-hoc | intercept `lam_ij x 1.0` on all six, ramped over `r_i ~ U{7..21}` days, unlogged | no |
| DR | frozen generator | `D` ramp to +1.0 from `t0`, over `U{7..21}` days | yes |
| AV2 | frozen generator | +0.5 mean and loading x0.7 on indicators 1, 4, unlogged | no |
| CS | frozen generator | context shares to (0.1, 0.2, 0.7) | no |

`c_i ~ U{50..100}` is drawn once per person for the S panel, and S, PS-sub and PS-prop use the same
persons, the same `c_i` and the same draws, so contrasts among them are paired. For DR, AV2 and CS,
`c_i` is the family's own change day (`t0`, `av_day`, and `cs_day` reproduced by re-running
`sample_events` on the same seed, which `generate_panel` calls first). Those three panels are
independent of the S panel and of each other.

PS-sub is spec 11.5's observation-policy shift: an agent that checks in more often fragments sessions,
moves activity times and lengthens reply latency, with the person unchanged. It is indicator-only:
usage does not change (the post-hoc construction cannot add used days; usage change is the DE family).
The +0.5 size matches AV and AV2. PS-prop is the identification boundary of (a): each person's own
`lam_i` (recorded by wrapping the rng passed to the unchanged `generate_panel` and keeping the return
of its single `uniform` call) times DR's shift, with DR's ramp shape.

Post-hoc construction: on day `t`, add `tau_ij(t)` to `X` and `X_filtered` for indicators 1, 2, 3 and
6. For indicators 4 and 5 (authorship-mixed), the shift sits in the human part: add
`(1 - pi_t) tau_ij(t)` to `X` and `(1 - pi'_t) tau_ij(t)` to `X_filtered`. `H` gets `tau_ij(t)`
(nothing on the A-fixed path reads `H`). The baseline (days 1-28) is untouched because `c_i >= 50`.

## (c) Scoring and the alarm set

A-fixed, frozen features, frozen `h = 3.334` from `sim/tuning.json`, frozen CUSUM. Per-indicator
z-scores come from calling the frozen `compute_composite` once per indicator with every other
indicator blanked in both `X` and `X_filtered`, using the baseline fit on the unblanked `X`; the
`--check` self-test asserts they average exactly to the composite.

**Scored alarms** are A-fixed alarms on days 28 to 134. Alarms on days 135-139 cannot get M2x3's three
probes, so they are left out of every rule's metrics, and tracked days are counted over the same range.
DR's 21-day sensitivity window ends by day 121, so it is unaffected.

## (d) Attribution rules (applied to every scored alarm on day `t`)

- **M0 none.** Every alarm is read as person change (the frozen behaviour).
- **M1 calibrated concentration test, no probe.** Window: days `t-13..t`. For each indicator with at
  least 3 usable days there, `d_j` = mean z, `n_j` = count. With `J'` such indicators (needs
  `J' >= 3`), `Q = sum_j n_j (d_j - dbar)^2 / (J' - 1)`, `dbar` the `n_j`-weighted mean. The alarm is
  read as person change when `Q < q*`, and also when `J' < 3` (not assessable). `Q` is not chi-square
  distributed (z-scores are autocorrelated and share `D`; a person change is not flat in z-units because
  `lam_ij / sd_ij` varies and indicators 4, 5 are attenuated by `1 - pi'`), so it is used only as an
  ordinal statistic with an empirical cutoff: `q*` is the 90th percentile of `Q` over DR alarms on days
  `[t0, t0 + 21)` in a separate tuning panel (DR, 1000 persons, seed tag `tune`, disjoint from the
  evaluation DR tag `eval`).
- **M2 one probe.** One probe on day `t + 1`, answered per the panel's `responded`. Read as person
  change when the answer exceeds the mean of the answered baseline-block probes (0-indexed days 6, 13,
  20, 27, `PROBE_BASELINE_DAYS`) by at least 0.5 (the frozen confirmation margin). No answer, or fewer
  than 2 answered baseline probes, reads as not confirmed. Deviation from the frozen rule: the frozen
  code sets the baseline mean to 0 when fewer than 2 baseline probes are answered, and confirms on any
  probe in the next 7 days.
- **M2x3 three probes.** Probes on days `t+1`, `t+3`, `t+5`; the mean of the answered ones against the
  same baseline mean and margin. No answer reads as not confirmed.
- **M3 = M1 and M2x3.**

Probe cost: per-alarm probes per tracked person-month (1 for M2, 3 for M2x3 and M3), with the 4-probe
baseline block reported separately.

## (e) Metrics (person bootstrap, 2000 draws; paired only within S, PS-sub, PS-prop)

1. **Post-change person-attributed alarms per tracked person-month**, scored alarms on days
   `[max(c_i, 28), 134]`, for S, PS-sub, PS-prop, AV2, CS.
2. **Attributed share**: person-attributed over all scored alarms in that window, per family and rule.
   DR's share is reported over `[t0, t0 + 21)` and over `[t0, 134]`.
3. **DR retained sensitivity**: share of DR persons with a person-attributed alarm in `[t0, t0 + 21)`,
   pre-onset person-attributed alarms excluded as in the frozen `_sensitivity`; per rule and as a ratio
   to M0.
4. **Momentary-state selection** on scored post-change alarms in S, PS-sub and PS-prop: mean `D_t` on
   the alarm day, `D_{t+1}`, and the mean of `D` over `t+1, t+3, t+5` (the days the probes read), against
   mean `D` on tracked days.
5. Probe cost as in (d).

## (f) Predictions, stated before running

- **A1.** Under M0, PS-sub's post-change alarm rate exceeds S's by a ratio above 1.5 (AV2's frozen ratio
  was 1.75).
- **A2.** M1 cuts PS-sub's person-attributed post-change rate to at most half of M0's.
- **A4.** M2 separates weakly: DR retention under M2 below 0.65 of M0, and PS-sub's M2 attributed share
  above 0.25. Decomposition: the answer rate of 0.8 alone caps retention near 0.8; the remainder comes
  from `D_{t+1}` and probe error (`e_Y` SD 0.65) against a margin of 0.5 on a shift of 1.0.
- **A5.** Mean `D_t` on S and PS-sub scored alarm days is above 0.3.
- **A6 (discrimination).** (DR share minus PS-prop share) under M2x3 exceeds the same difference under
  M1 by at least 0.15, with a bootstrap 95 percent interval above 0. Shares use DR over `[t0, 134]` and
  PS-prop over `[c_i, 134]`; the two panels are resampled independently.

**Calibration and known-answer checks, not predictions.** DR retention under M1 is near 0.9 by
construction of `q*`. M1's PS-prop share should be within 0.10 of DR's `[t0, 134]` share, by (a);
a larger gap would mean the eta channel, the ramp or the attenuation of indicators 4 and 5 matter more
than (a) says.

## (g) What this does not do

No new generator mechanism enters the frozen code; PS families are post-hoc arithmetic on the S panel
in a separate script (`sim/attribution.py`) that imports `drift_sim.py` unchanged. No PREREG seed is
used. No real data is read. M1 ignores variance changes (AV2's loading x0.7 changes variance). The
`kappa`, `m1`, targeted-help and mixing cells are not run; `m1 > 0` would weaken M2 further and is
left for the next spec.
