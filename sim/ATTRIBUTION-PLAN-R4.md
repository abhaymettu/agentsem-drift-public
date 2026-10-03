# sim/ATTRIBUTION-PLAN-R4.md -- EXPLORATORY, not frozen

Round 4 of the attribution runs. r3 (`sim/ATTRIBUTION-PLAN-R3.md`, sha256 `4c378002...`, results
`sim/ATTRIBUTION-R3.md`, `b088165`) left three results without a tested mechanism (spec 001 section 17.5).
This round tests a mechanism for each:

- **M-A.** Under `bernoulli_mix` the frozen `h` gives M0 alarm rates of 0.17 to 0.33 times default in every
  family and 0.26 of DR's 21-day sensitivity.
- **M-B.** In the default cell, S alarm days have a filtered authorship share `pi'` 0.068 below tracked days.
- **M-C.** Under `pi_rises_with_D`, DR's alarm-selection shift (-0.042) and its M2x3 share change
  (+0.024) have opposite signs.

**This run is EXPLORATORY. It is not part of `sim/PREREG.md` or of spec 003, and it changes no P1-P10
verdict, no frozen code path, no number in paper v4 and nothing in r1 to r3.** Its outputs
(`sim/attribution_r4.json`, `sim/ATTRIBUTION-R4.md`) repeat this label. All numbers are synthetic.

## (a) A code fact found while preparing this round (before any r4 number)

`attribution.score_panel`, and the frozen scoring code it copies, fit A-fixed's per-person baseline
mean and SD on the **unfiltered** `X`:
- in `drift_sim.py`, `_run_arch` and six more literal `fit_baseline(panel["X"], ...)` sites (`check_b`,
  `check_e`, `check_f`, `tune_h`, `tune_schedules`, `metrics`), plus `generate_panel` line 686;
- elsewhere, `attribution_r2.py` line 198 and `design_check_003.py` line 47. `compute_composite` then scores indicators 4 and 5 from **`X_filtered`** (feature
(ii)). So A-fixed's z-scores for 4 and 5 are `(X_filtered - mean(X)) / sd(X)`: the scored series and the
baseline it is standardized against are different text mixtures. PREREG's wording for (ii) ("indicators 4
and 5 are computed from text an authorship filter labels human") does not say which series the baseline
uses. `sim/POSTFREEZE-DEVIATIONS.md` and spec 001 do not mention it (searched for `fit_baseline` and
"baseline" with "filter").

What it implies, by hand, before running anything:
- Under the default Beta mixing, `X` is mostly agent text (`E pi = 0.845`) and `X_filtered` mostly human
  (`E pi' ~ 0.37`). Indicator 5's agent text has mean -1, below the human mean (about +0.2 from context),
  so `X_filtered` sits about 0.58 raw units above `mean(X)`, against `sd(X)` of about 0.65: indicator 5's
  z-score carries an offset of about +0.9. Indicator 4's agent text sits above the human mean, giving an
  offset of about -0.2. Averaged over five to six usable indicators, the composite carries an offset of
  about **+0.12** on every day, and the z-scores of 4 and 5 have SD about 1.2 rather than 1.
- `k = 0.5` is in the composite's units (the composite is not re-standardized), and `h = 3.334` was tuned
  under the default cell, so the frozen operating point absorbs this offset.
- Under `bernoulli_mix`, `pi` is 0 or 1, so `pi' = pi` (to 1e-11) and `X_filtered` equals `X`: the offset
  vanishes. **This is a candidate for M-A that r3 did not consider.**
- Not affected: every single-indicator validity in the frozen run and in r3. These are computed on raw
  `X`, `X_filtered` or `H` and never use the baseline.
- Affected: every quantity computed on the A-fixed composite, meaning every A-fixed alarm, rate and
  sensitivity. Also affected:
  - the A-fixed-minus-(ii) ablation, which removes this mismatch along with the filter;
  - the targeted-help cells' *generated* help, whose feedback composite (`generate_panel` line 686) carries
    the same mismatch.

This round measures the mechanism and does not change the frozen code. Whether the frozen run gets a
sensitivity rerun with a matched baseline is his call (results section "For him").

## (b) Panels

1. **r3's panels, primary.** S and DR rebuilt with `attribution_r3.gen` from r3's plan hash, in all three
   cells (`default`, `bernoulli_mix`, `pi_rises_with_D`). The script asserts exact reproduction of:
   - r3's post-change M0 alarm counts (S and DR, every cell);
   - r3's M2x3 shares and their differences (S every scored alarm, DR post-onset).

   The S rate here is over every tracked day 28 to 134. r3's 0.17 was the post-`cday` rate, so the frozen
   ratio is restated in this window.
2. **Replication.** The same quantities on fresh seeds (`attribution_r3.gen` keyed by `r4:<this plan's
   sha256>`, a seed string no earlier round used).

1000 persons per family and cell, constant help, frozen `h = 3.334`, person bootstrap with 2000 draws.

## (c) Scoring variants

Each is a post hoc change to the panel before A-fixed scoring; nothing in the generator changes.

| variant | what changes |
|---|---|
| `frozen` | none (A-fixed as run; the baseline of 4 and 5 is fit on `X`) |
| `matched_mean` | the baseline *mean* of 4 and 5 is fit on `X_filtered`; their SD stays as run (fit on `X`). Removes the level offset only. |
| `matched` | the baseline mean and SD of 4 and 5 are fit on `X_filtered`, the series that is scored. Removes the level offset and the scale inflation. |
| `recentred` | agent text is moved to the human population mean in both `X` and `X_filtered` (`X -= pi g`, `X_filtered -= pi' g`). `g` is the agent mean minus the human mean, per indicator: for indicator 4 it is exactly the generator's gap; for indicator 5 the agent mean is the generator's -1, and the human reference is r4's choice (the pooled mean of `H5` over used baseline days). Per-person offsets remain. |
| `matched_recentred` | both |
| `share_rule` | `matched`, plus indicators 4 and 5 marked missing on days where `pi' > 0.5` (most kept text is agent). This is proposal 3 of spec 001 section 17.3. It is an oracle version: `pi'` is a deterministic function of `pi` here, while a deployed rule would estimate it from the filter's flag counts. The cut-off 0.5 is fixed here, and no other cut-off is run. |

**Rate-matched sensitivity.** For each cell and variant, `h*` is found by bisection on the S panel so that
S's scored M0 rate (days 28 to 134 per tracked person-month) equals the default cell's frozen rate at the
frozen `h` on the same panel set. DR's 21-day M0 sensitivity (frozen primary, pre-onset alarms exclude
detection) is then read at `h*`. This is proposal 3's other option (tune `h` under the regime) in oracle
form. Its interval is conditional on `h*`, because the bisection is not bootstrapped.

## (d) Metrics

Per panel set, cell and variant:
- the S M0 rate;
- DR's 21-day sensitivity at the frozen `h` and at `h*`;
- on S tracked days 28 to 134, the composite's mean, its pooled within-person SD and its lag-1
  within-person autocorrelation over consecutive tracked days;
- under `share_rule`, the distribution of usable baseline days for indicator 5 per person (0, 1, 2, 3, 4
  or more), and the share of S alarms from persons with fewer than 4;
- the M-B gap: mean `pi'` (and `pi_t`) on S scored alarm days minus on tracked days.

Paired contrasts, cell over or minus default, per variant: S rate ratio, DR sensitivity ratios, composite
mean difference and SD ratio. Plus these:
- **A2 closure.** `1 - log(rate ratio, variant) / log(rate ratio, frozen)` for S under `bernoulli_mix`,
  for `matched_mean` and `matched`: the share of the log rate gap closed by removing the level offset
  alone, and by removing level and scale.
- **A4.** Under `bernoulli_mix`, rate-matched DR sensitivity with `share_rule` over `matched`.
- **B1.** Default S: the M-B gap after recentring over the gap before, with the frozen baseline and with the
  matched one.
- **M-C.** Frozen scoring, the four r3 C1 rows (DR post-onset alarms, S every scored alarm, each under
  `bernoulli_mix` and `pi_rises_with_D`). M2x3 confirms an alarm when the mean of `Y` on the responded
  probe days `t+1, t+3, t+5` is at least 0.5 above the mean on the responded baseline probes. So its share moves
  through:
  1. the share of alarms that are confirmable (at least 2 responded baseline probes and at least 1
     responded probe);
  2. the noise-free margin over confirmable alarms: mean true `D` on the responded probe days (*level*)
     minus mean true `D` on the responded baseline probes (*base*).

  r3's selection metric was the level alone, over all three probe days, whether answered or not. Reported:
  paired differences in the M2x3 share, the confirmable share, level, base and margin.

## (e) Predictions, stated before running (r3's panels)

Bounds were sized on a design seed (string `design-sizing-r4`, not derived from this plan), reading
bootstrap SEs only: A2 closure 0.038 (`matched`; `matched_mean` was added after sizing and is not sized); rate-matched DR sensitivity ratio under `matched` 0.063; A4 0.070;
B1 0.21 (frozen) and 0.18 (matched); default S gap under `matched` 0.013; M-C margin differences 0.028 to
0.092 and M2x3 differences 0.013 to 0.052.

- **A1 (construction check of (a)).**
  - Under `frozen`, the S composite mean is higher in default than in `bernoulli_mix` by at least 0.05.
  - Under `matched`, the difference is within ±0.03.
  - Under `frozen`, the composite SD ratio `bernoulli_mix` over default is below 1.
- **A2 (main).** The matched baseline closes at least half of the log S-rate gap: A2 closure under
  `matched` at least 0.5 (point estimate).
  - Reading, fixed now: if it holds, r3's lower alarm rate under `bernoulli_mix` is read mainly as the
    frozen baseline mismatch disappearing under all-or-nothing days, not as a property of Bernoulli mixing
    as such.
  - `matched_mean`'s closure, reported beside it without a bound, splits that share into **level** (the
    offset) and **scale** (the SD inflation): level is `matched_mean`'s closure, and scale is the
    difference.
  - If A2 fails, what is left after level and scale is read as **signal**: the composite's dependence on
    `D` and its persistence under that regime.
- **A3.** The rate-matched DR sensitivity ratio, `bernoulli_mix` over default, is between 0.5 and 1.0
  under `matched` (point estimate).
  - Reading: most of r3's 0.26 is operating point. What remains below 1 is lost signal, since indicators 4
    and 5 carry `D` on only about 15% of days.
  - A ratio above 1.0 would mean that, at a matched false-flag rate, all-or-nothing days cost no
    detection. This would be read as the frozen default's mismatch costing sensitivity, and checked
    against default's own `matched` over `frozen` rate-matched sensitivity.
- **A4.** Under `bernoulli_mix`, `share_rule` does not lower rate-matched DR sensitivity: the ratio is at
  least 1.0 (point estimate).
  - Reason: on the agent days it drops two pure-noise z-scores from a mean of six.
  - Risk stated now: the baseline of 4 and 5 then rests on about 3 human days per person, and the frozen
    fallback (mean 0, SD 1) applies below 2. With 2 or 3 days the SD rests on 1 or 2 degrees of freedom
    (floor 1e-6), so some z-scores are very large.
  - Reading, fixed now: if A4 is below 1 and `h*` under `share_rule` is above `h*` under `matched`, A4 is
    read as the cost of a small baseline for this oracle rule, not as evidence about dropping agent-day
    noise. The baseline-day distribution and the share of S alarms from persons with fewer than 4 days
    are reported for that reading.
- **B1.** Default S, frozen baseline: at least half of the alarm-day `pi'` gap is left after recentring
  (point estimate; weak, SE about 0.2).
  - Reasoning: removing the mean gap removes only the channel r3 guessed at (agent text has a lower
    indicator 5).
  - The channel predicted to carry more is the human weight `1 - pi'`. Alarms fire on high-`D` days, and on
    those days a lower `pi'` lets more of the human deviation into 4 and 5 (by hand, about four times the
    mean channel).
- **B2 (construction check, as A1).** Default S, matched baseline, no recentring: the gap's 95 percent
  interval is below 0. Both channels reach `z4` and `z5` under any per-person affine baseline; `matched`
  only rescales them by about 1/1.2, so this checks that the route does not depend on the mismatch.
- **C1.** Three rows: DR under both cells, and S under `pi_rises_with_D`. In each, the paired margin
  difference has the same sign as the paired M2x3 share difference (point estimates).
  - A row is read only when its margin difference's 95 percent interval excludes 0; otherwise the row is
    *unresolved*. C1 is judged row by row.
  - S under `bernoulli_mix` is reported only (r3's difference +0.021, SE about 0.06).
  - The DR `pi_rises_with_D` row is the one r3 could not resolve. The level difference here is over
    *responded* probe days, unlike r3's metric:
    - if it is at least 0, r3's sign mismatch is read as an effect of counting only answered probes;
    - if it is negative while the margin agrees in sign with the share, the baseline term accounts for it;
    - if the margin disagrees, the confirmable share or the threshold's shape does, and both are reported.

**Replication.** The same predictions are evaluated on the replication set and reported beside the
primary ones. A prediction that holds on r3's panels but not on the replication is reported as such.

**Multiplicity.** About seven predictions on two panel sets are judged on point estimates without
error-rate control. Each is read on its own. B1 (SE about 0.2 against a 0.5 bound) cannot discriminate
sharply and is read as direction only.

Every other quantity is reported without a prediction: `pi_rises_with_D` under every variant,
`share_rule` in default, `recentred` rate ratios, and the M-B gap under `bernoulli_mix` (r3 had 39 S alarms
there).

## (f) What this does not do

- `drift_sim.py`, `attribution.py`, `attribution_r2.py` and `attribution_r3.py` are unchanged (since
  `9fea182`, `ccbcf51`, `21b28d5`, `ddf508e`). No PREREG seed is used and no real data is read.
- No frozen number is recomputed. The effect of (a) on P1 to P10 and on paper v4's A-fixed numbers is not
  estimated here.
- `share_rule` and rate matching are oracle checks of spec 001 section 17.3's proposal 3, not a design
  decision for spec 003.
- `kappa`, `m1 > 0`, logged PS and usage-changing PS stay with spec 003.

## Revisions

- r0 to r1, before hashing. Opus methods review REVISE: 5 blocking, all applied.
  - Level and scale separated (`matched_mean`), and the readings reworded.
  - C1 rows read only when their interval excludes 0; S `bernoulli_mix` made report-only; the
    answered-probes reading added.
  - B2 labelled a construction check.
  - A4 given a failure reading and baseline-day diagnostics.
  - The `h*` bisection asserted to reach its target.

  Non-blocking 1 to 10 applied: the call-site list and the targeted-help generation, the "not affected"
  reason, the S window, the recentring reference, an own-share assert, wording, A3's reading above 1, and
  multiplicity. Ponytail: 7 cuts, all applied.
- Before hashing, only these ran: `--check`; the design-seed sizing (SEs only, quoted in (e)); one
  200-person smoke run on the seed string `smoke-r4` (key names only).
