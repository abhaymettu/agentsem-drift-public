# Supplementary material, private draft, 2026-10-07

Supplement to "Is it the person or the agent? Validity threats to inferring within-person change from agent
conversation traces". Each block below was moved here from the body of draft v4.2 when the body was trimmed to
the venue's suggested length. Wording, numbers and labels are unchanged, except that cross-references now point
to the trimmed draft's section numbers. Tables S1 and S2 are Tables 1 and 3 of v4.2, and Figure S1 is Figure 2 of v4.2
(v4.2's Figures 3 and 4 are now main-text Figures 2 and 3). Section
numbers in the headings below give each block's v4.2 location. References are those of the main text.

## S1. The attenuation formula (v4.2 Appendix A and section 2.2)

A filter that catches 90 percent of machine text and keeps 95 percent of human text leaves a residual share `pi' = 0.1 pi / (0.1 pi + 0.95 (1 - pi))`.

Let an indicator's daily value be `X = (1 - pi) H + pi M`, where `H` is the human value, `M` the machine
value, and the day's machine share `pi` is independent of `H` and `M`, with `M` independent of `D` and of
`H`. Write `mu_H`, `V_H` and `mu_M`, `V_M` for their means and variances within person. Then
`Cov(X, D) = E(1 - pi) Cov(H, D)`, and

    Var(X) = E[(1 - pi)^2] V_H + E[pi^2] V_M + Var(pi) (mu_H - mu_M)^2,

because `Var((1 - pi) H) = E[(1 - pi)^2] V_H + Var(pi) mu_H^2`, `Var(pi M) = E[pi^2] V_M + Var(pi) mu_M^2`,
and `Cov((1 - pi) H, pi M) = -Var(pi) mu_H mu_M`. Dividing `Cor(X, D)` by `Cor(H, D)` and writing
`kappa = V_M / V_H` and `delta = (mu_M - mu_H) / sqrt(V_H)` gives

    Att = (1 - E pi) / sqrt(E[(1 - pi)^2] + E[pi^2] kappa + Var(pi) delta^2).

The formula needs `pi` independent of `D`. When `pi` depends on `D`, `Cov(X, D)` gains a term from the
mean gap, `Cov(pi, D) (mu_M - mu_H)`, whose sign is the sign of the gap times the sign of the coupling;
this is the rising-share distortion in section 3.4.

## S2. Generator (v4.2 section 3.2)

Each synthetic person has 140 days (days 1 to 28 are baseline), with 1,000 persons per family per
cell; all rules run on the same persons. The state
`D_t` is AR(1) with `phi_D = 0.7` and marginal SD 1; drift families add a ramp of +1.0 SD from an onset in
days 50 to 100, over 7 to 21 days. Workload and a daily context (code, write, personal) vary alongside
it; a day is used with probability `expit(logit(0.8) - kappa D_t)`, less on vacation or disengagement. Six indicators are observed on used days (late-activity share, session fragmentation, deferral
rate, message length, negative self-reference, reply latency), each `H_jt = lam_j D_t + gam_j L_t +
beta_j[ctx_t] - A_t psi_j (1 + theta1 D_t) + e_jt`, with per-person loadings `lam_j ~ U[0.25, 0.5]`.

Indicators 4 and 5 are mixed with machine text by daily averaging, `X_jt = (1 - pi_t) H_jt + pi_t M_jt`,
with `M` independent of `D`. For indicator 4 the generator takes `pi_bar = 0.845`, `kappa = 0.547` and
`delta = 0.274` from the corpus audit; the share is a day mean, but `kappa` and `delta` were computed over
entries and used as day-level parameters (Supplement S7 gives the consequence). Help is logged, with probability
0.3 by default; a version change shifts indicators 2 and 6 by +0.5 and scales their loading by 0.7. The criterion `Y_t = D_t + e_Y` has
reliability 0.7, and the probability of answering falls with `D` at rate `m1`.

**Families.** S (stable), DR (drift), VA (vacation), SP (workload sprint), BI (broken integration), AV
(version change, logged for half), DE (disengagement), DV (drift overlapping a vacation), CS (context
shift), BD (drift beginning inside the baseline) and AV2 (unlogged version change on indicators 1 and
4); the fixed rule was not designed for CS, BD or AV2.

**Cells.** A default cell plus one-at-a-time variations: `kappa = 0.3`; `m1 = 0.5`; `m1 = 1.5`;
help targeted on the previous day's composite; targeted help whose effect grows with the state
(`theta1 = 0.5`); Bernoulli mixing; and a machine share that rises with `D` (logit slope 0.5). The
rising-share cell is hypothetical: it models delegation of drafts, which the audit did not measure.

## S3. Candidate scoring rules, criterion-sampling designs and decision rule (v4.2 sections 3.3 to 3.5)

### Candidate scoring rules

Every rule averages within-person z-scores of the available indicators into a daily composite `C_t` and
runs a one-sided CUSUM, `S_t = max(0, S_{t-1} + C_t - k)` with `k = 0.5` (Page, 1954), with a reset and a
14-day refractory period after a flag and `S` held on days with no usable indicator. The threshold `h` is
tuned per rule on family S, on a separate tuning seed, to one false flag per six tracked person-months.

- `pop`: population rather than personal z-scores.
- `A-naive`: personal baseline, all indicators on every used day, all user-role text in indicators 4
  and 5, no workload term, no reset, no abstention.
- `A-fixed`: `A-naive` plus (i) indicators 2 and 3 on unhelped days only, following an earlier result in
  this program that unhelped-day scoring holds under state-dependent help (Mettu, 2026b, Study 5); (ii)
  indicators 4 and 5 from text an authorship filter labels human (sensitivity 0.9, specificity 0.95);
  (iii) timing and friction indicators residualized on observed workload; (iv) reset and a 14-day
  re-baseline at a logged version change; (v) abstention when 14-day usage falls below 40 percent of the
  baseline rate. Ablations remove each component in turn.
- `probe-only`: a CUSUM on criterion answers alone, z-scored on a four-probe baseline block, random
  schedule, matched budget.

No rule adjusts for context. Tuned thresholds (`sim/tuning.json`):
`h` = 1.125 (`pop`), 1.739 (`A-naive`), 3.334 (`A-fixed`) and 22.949 (`probe-only`, after the
post-freeze re-tune in Supplement S4).

### Criterion-sampling designs

Each design except `none` has a fixed baseline block of four criterion occasions (days 7, 14, 21 and 28)
and a budget target of 3.0 occasions per person-month after the baseline: `none`; `fixed`, every 10
days; `random`, each day with probability 0.1; `triggered`, with probability 1.0 on days when `S` lies in
[h/2, h); `mixed`, a random floor of 0.04 per day plus probability 0.795 in the same band; and `current`,
a construction check that probes when `C_t` exceeds 0.956. The triggered design reaches only 2.265 per
person-month. Selection probabilities are logged; weighting is identified only for `random` and `mixed`. A flag counts as confirmed if a criterion occasion within
the next 7 days reads at least 0.5 above the person's baseline-block mean.

### Decision rule

A prediction holds only if its 95 percent Monte Carlo interval lies beyond its frozen threshold (or, for
a "within X" clause, inside plus or minus X), in the default cell unless another is named. Intervals come
from a 2,000-draw person bootstrap, paired within a panel and independent across panels. A failed
prediction is reported as failed, and nothing is re-tuned after scoring. The frozen text's
standard-error formula divides by the square root of 200, a leftover from an earlier design; the
literal reading would change neither verdict that holds. Table S1 gives the eleven predictions and their
thresholds. P1, P1b, P2 and P3 are construction checks, which test whether each component of `A-fixed` does what it was built to do; they
are not findings.

## S4. Scoring runs and post-freeze fixes (v4.2 section 3.6)

Run 1 was scored first, at the freeze. A separate audit of the scoring code against the frozen text, run
by an AI agent within the same project, found that run 1 decided every prediction on point estimates
rather than on the interval rule and departed from the frozen text in four places: P1b's denominator
(tracked instead of total person-months); P4's probe window, all-days reference and weighted
correlation; P5's reference slope, which was conditioned on response; and P8's criterion-only rule,
z-scored on about 22 baseline-window answers its schedule never administers instead of the four-probe
block. Run 1 is kept, superseded; run 2, committed 43 minutes after the freeze, applies only those fixes. The P8 fix changes the criterion-only threshold, so the frozen tuning procedure
was re-run on the corrected code and the tuning seed, moving its `h` from 6.539 to 22.949; no
evaluation-seed number was used. Run 1's P8 was 17.3 points [14.7, 19.8] and 7.12 days [6.34, 7.91];
run 2's is in Table S1. Every verdict the fixes changed went from PASS to FAIL (P6 and P10). Where the
frozen text allows two readings, the verdict uses the as-run reading, fixed before scoring, and the
alternative is reported beside it; for trigger timing the alternative is the more natural one for a real
study and gets equal weight in section 3.4 and Supplement S7.

## S5. Table S1, predictions of the first simulation (v4.2 section 3.7)

Only P1b and P8 hold. The other nine fail, including three of the four construction checks.

**Table S1. Predictions, score run 2.** Point [95% Monte Carlo interval], 1,000 persons per family per
cell; "cc", construction check. Alternatives: G2, pooled false-flag rate; G3, a pre-onset flag does not
cancel a later detection; P4, previous day's statistic; P6, validity scale. Precision: "clear miss",
interval wholly on the wrong side; "undecided", interval straddles the threshold; "not decidable", a
"within X" interval wider than 2X; "opposite", interval wholly beyond the predicted direction.

| | statistic | threshold | run 2 | verdict | precision | alternative reading |
|---|---|---|---|---|---|---|
| P1 (cc) | SP false flags, A-naive / A-fixed | >= 2 | 1.23 [1.13, 1.35] | FAIL | clear miss | G2: 1.23 [1.13, 1.35] |
| | VA / DE / BI, same ratio | in [0.5, 2] | 1.03 [0.92, 1.16] / 1.00 [0.89, 1.14] / 0.80 [0.72, 0.87] | holds | holds | G2: 1.03 / 0.99 / 0.80 |
| P1b (cc) | DE / S false flags per total person-month | <= 1.5 | 0.60 [0.50, 0.73] | PASS | holds | none |
| P2 (cc) | DR sensitivity, A-fixed minus A-naive, targeted state-dependent help (points) | >= 10 | 9.2 [6.7, 11.9] | FAIL | undecided | G3: 12.4 [9.6, 15.2] |
| | margin by which removing (i) exceeds half the gap | >= 0 | 0.007 [-0.009, 0.022] | fails | undecided | G3: 0.023 [0.007, 0.039] |
| P3 (cc) | logged AV false flags, without (iv) / with | >= 2 | 1.85 [1.66, 2.06] | FAIL | undecided | G2: 1.85 [1.67, 2.07] |
| | AV2 / S false flags, A-fixed | >= 2 | 1.75 [1.50, 2.03] | fails | undecided | G2: 1.76 [1.51, 2.04] |
| P4 | triggered: correlation deflation | >= 0.05 | 0.104 [0.076, 0.133] | holds | holds | 0.049 [0.021, 0.077] |
| | triggered: relative slope attenuation | >= 10% | 24.8% [18.5, 31.3] | holds | holds | 16.1% [10.0, 22.1] |
| | mixed, weighted slope minus all-days | within 0.03 | -0.055 [-0.124, 0.018] | FAIL | not decidable | 0.067 [0.001, 0.132] |
| | mixed, weighted correlation minus all-days | within 0.03 | -0.014 [-0.048, 0.020] | fails | not decidable | 0.016 [-0.015, 0.046] |
| P5 | relative slope bias, `m1 = 0.5`, random | within 5% | -0.8% [-5.7, 3.9] | FAIL | undecided | none |
| | added bias at `m1 = 1.5` over `m1 = 0`: fixed / random / triggered / mixed | >= 10% each | 13.1% [6.9, 18.2] / 13.5% [7.0, 17.5] / 15.5% [6.1, 24.6] / 12.2% [5.3, 18.8] | fails | undecided | none |
| | share of bias removed by response-propensity weighting | < 0.5 | -0.107 [-0.231, -0.011] | holds | holds | lags 1 to 3: -0.103; added bias only: -0.114 |
| P6 | indicator 4, simulated minus formula attenuation, unfiltered / filtered | within 0.03 | 0.023 [0.002, 0.046] / 0.013 [-0.002, 0.029] | FAIL / holds | undecided / holds | |
| | indicator 5, same, unfiltered / filtered | within 0.03 | 0.011 [-0.027, 0.054] / 0.002 [-0.021, 0.024] | fails / holds | not decidable / holds | |
| | Bernoulli cell, indicator 4 / indicator 5 | within 0.03 | -0.019 [-0.046, 0.006] / -0.003 [-0.025, 0.018] | fails / holds | undecided / holds | |
| | rising share, indicator 4, simulated minus formula | >= 0.05 | 0.151 [0.119, 0.192] | holds | holds | validity scale: 0.043 [0.037, 0.049] |
| P7 | DR minus DV sensitivity, A-fixed (points) | >= 15 | 11.0 [8.0, 14.1] | FAIL | clear miss | G3: 14.7 [11.3, 18.1] |
| P8 | DR sensitivity, A-fixed minus probe-only (points) | >= 10 | 17.8 [15.2, 20.4] | PASS | holds | G3: 23.7 [20.9, 26.5] |
| | restricted mean time to flag, probe-only minus A-fixed (days) | >= 3 | 7.73 [6.94, 8.49] | holds | holds | G3: 9.98 [9.11, 10.77] |
| P9 | BD sensitivity minus half of DR sensitivity | <= 0 | 0.174 [0.144, 0.203] | FAIL | opposite | G3: 0.142 [0.112, 0.173] |
| P10 | CS / S false flags, A-fixed | >= 1.5 | 1.71 [1.48, 1.99] | FAIL | undecided | none |

A prediction fails if any part fails; every alternative reading gives the same verdict. P1's SP
ablation ratio is 1.047, so the workload component did not account for the SP difference. P5's "under 5 percent" is scored as the interval lying inside plus or
minus 5 percent. In the Bernoulli cell the filtered and unfiltered indicator 4 coincide because the
residual share `pi'` equals `pi` when `pi` is 0 or 1.

## S6. Frozen metrics not used by any prediction (v4.2 section 3.8)

The frozen design also lists metrics that no prediction scores. They were computed from the run 2 panels
after scoring, as reporting only, with no thresholds.

**Sensitivity against false flags** (Figure S1). A-fixed's sensitivity peaks at 0.240 [0.214, 0.268] at `h` =
2.128 (0.343 false flags per tracked person-month) and falls on both sides: to 0.057 at `h` = 0.667
(1.167 false flags) and 0.020 at `h` = 10.002 (0.011). A-naive peaks at 0.198 [0.175, 0.224]. The fall at
loose thresholds is expected from the as-run sensitivity rule, under which a flag before onset makes the
person a miss even when a later flag falls inside the window; under the alternative reading (G3) that
reason disappears, but the curve was not computed under it.

![Figure S1](fig2_sensitivity_vs_false_flags.svg)

*Figure S1.* Sensitivity within 21 days of onset (family DR) against false flags per tracked
person-month (family S) as the threshold is swept, for A-fixed and A-naive, with 95 percent bands;
points mark each rule's chance baseline at its realized false-flag rate.

**Chance baselines.** For each rule, random flags at the rule's own realized false-flag rate on S, placed
on DR's tracked days and scored with the same pre-onset exclusion and tracked-day definition as the
observed sensitivity, give a chance sensitivity. A-fixed's 0.197 is 3.7 times its chance level of 0.053
[0.039, 0.067]; A-naive's 0.154 is 2.4 times 0.063; `pop`'s 0.180 is 2.3 times 0.077; the ablations are
1.8 to 3.1 times theirs. Probe-only's 0.019 [0.011, 0.028] is against a chance level of 0.015 [0.008,
0.023].

**Realized false flags.** On family S of the evaluation seed, per tracked person-month: A-fixed 0.151
[0.132, 0.169], A-naive 0.155, `pop` 0.162 and probe-only 0.179 [0.115, 0.250], against a tuning target of
0.167. The interquartile range of person-level rates is 0.323 for A-fixed and 0 for probe-only: at least
three quarters of persons had no false flag under probe-only. Its rate per total person-month, 0.014, is
about 8 percent of its tracked rate, so it is tracked on few days.

**Person-level validity.** Because pooled coefficients can hide persons whose scores carry little
information (section 2.3; Fisher, Medaglia and Jeronimus, 2018), the distribution is reported. Across
persons, the within-person correlation of A-fixed's composite with
the state on tracked days averaged 0.565 [0.560, 0.571] on S (5th to 95th percentile 0.410 to 0.695) and
0.596 on DR, and no person's was at or below zero. For the raw message-length and negative
self-reference indicators it was at or below zero for 18.8 to 21.5 percent of persons across S and DR;
after filtering, for 0.4 to 0.8 percent.

**Usage depending on the state.** At `kappa = 0.3`, A-fixed's DR sensitivity was 0.168 [0.145, 0.190]
against 0.197 at `kappa = 0`, and abstention rose from 0.199 to 0.232, almost all from unused days.

**Other metrics.** `pop` reached a DR sensitivity of 0.180 [0.157, 0.204]. The confirmation rule's
positive predictive value on DR was 0.195 to 0.226 across schedules, and the median time to flag was 14
days [13, 15]. Under `triggered` the realized budget was 1.50 per person-month on S and 3.23 on DR. The
frozen reset cost cannot be computed: no frozen family has both a drift onset and a version change.

## S7. Full text of the discussion of the first simulation's results (v4.2 section 3.9)

Some results follow from the generator's structure: selection attenuation when the criterion schedule
depends on the score; weighting on observables not removing state-dependent non-response; and
the sign of state-coupled contamination, which follows from `X = H + pi (M - H)`. They are expected
whenever `phi_D > 0`, the trigger depends on the score, the loadings are non-zero, and the coupling and
mean gap are non-zero; on an exploratory grid (Supplement S8) the direction held on point estimates
everywhere, but three expectations failed their interval rule in named cells. The magnitudes (0.197,
17.8 points, 24.8 percent) are set by invented values.

**Which mechanisms appeared.** Selection attenuation, state-coupled authorship distortion and the
non-state false-flag sources appeared; the workload component (SP ablation ratio 1.047) and component
(i) did not do their jobs, and P9 went the opposite way.

**Criterion sampling (P4)** (Figure 2, left). The triggered slope was 0.700 [0.640, 0.759] against an all-days slope of
0.930, an attenuation of 24.8 percent [18.5, 31.3], with the correlation deflated by 0.104 [0.076,
0.133]. The `current` control, probing whenever today's composite exceeds a fixed cut, gave a slope of 0.694 [0.588, 0.802], an attenuation of 25.4 percent [14.1, 36.7], and a
correlation deflation of 0.281 [0.254, 0.309]. Selecting on the current score alone produces the same
slope attenuation, so the 24.8 percent should not be attributed to the trigger's history. Direct
selection on the predictor leaves the slope unbiased in a homogeneous linear-Gaussian model (the frozen
check with a common loading and population scaling moved it by about 6 percent); here it plausibly
combines with per-person loadings, scaling and person-centring on the selected days. With the previous day's
statistic in the trigger, the attenuation was 16.1 percent [10.0, 22.1]; that reading is closer to
selection on history, but the estimator effect seen in `current` has not been separated from it.
Weighted recovery could not be shown under either reading (-0.055 [-0.124, 0.018] with today's
statistic; an overshoot of 0.067 [0.001, 0.132] with the previous day's); an interval about 0.14 wide
cannot fit a band 0.06 wide. The correlation deflation is the classical range-restriction result (Thorndike, 1949;
Sackett and Yang, 2000), structurally the verification bias of Begg and Greenes (1983), shown here in
the agent-probing setting. The slope attenuation is not that result: direct selection leaves the slope
unbiased in a homogeneous model, so it plausibly reflects the estimator, as above. The history-conditional weighting from
micro-randomized trials (Boruvka et al., 2018) applies, but at N = 1,000 its interval is too wide to show
recovery.

**Criterion non-response (P5).** At `m1 = 1.5`, the total relative slope bias was -15.3 percent [-20.0,
-10.7] (fixed), -14.3 percent [-18.8, -9.8] (random), -40.3 percent [-47.8, -33.1] (triggered) and -18.3
percent [-23.6, -13.1] (mixed). The triggered total includes the 24.8 percent selection attenuation that
the same schedule shows at `m1 = 0`; the added bias is in Table S1. A response-propensity weight fitted on
the current composite, a lagged composite and day of week did not remove it, in a generator where
response depends on the state by construction.

**Authorship (P6).** The contamination formula tracks the simulated attenuation in expectation (largest
point difference 0.023), but three of the six comparisons in Table S1 fall outside plus or minus 0.03 on
the interval. The hypothetical rising-share cell gives the largest distortion the simulation found (Figure 2,
right). Message length's attenuation factor exceeded the formula by 0.151 [0.119, 0.192]: validity
supplied by delegation rather than by behaviour. For negative self-reference, whose machine-text mean
sits below the human mean, the within-person validity was -0.011 [-0.016, -0.005] against 0.340 [0.334,
0.346] for the unmixed indicator, so its sign changed; filtering restored the sign but not the size
(0.138 [0.131, 0.146]). This is not a frozen prediction, since P6's rising-share clause names indicator 4
only, and it follows from an invented machine-text mean (-1.0 SD) and an invented coupling slope (0.5).

Indicator 4 ran at the audit's entry-level variance ratio and mean gap. Analytically, the formula gives
an attenuation of 0.235 at those values (0.802 after filtering) and 0.527 at the corpus's day-level
values (0.929 after filtering), which match the generator's daily averaging; the frozen simulation thus
used the values that imply more attenuation, and it was not re-run.

**Drift inside the baseline (P9).** BD was flagged more often in days 29 to 49 (0.272) than DR within 21
days of onset (0.197), the opposite of the prediction. One unchecked candidate: a BD onset in days 10 to
25 with a 7 to 21 day ramp can still be rising after day 28, against a baseline that absorbed only part
of it; the pre-onset rule also applies only to the DR side.

**P8.** P8's pass is a win over a criterion-only comparator indistinguishable from chance (0.019
[0.011, 0.028] against 0.015 [0.008, 0.023]), whose false-flag matching held per tracked person-month
(0.179 against 0.151) but not per total person-month (0.014 against 0.121): a property of the frozen
four-probe scaling, not evidence that passive scoring beats asking.

## S8. Exploratory robustness, not frozen (v4.2 section 3.10)

In this block, S1 to S6 name the robustness plan's six expectations, not sections of this supplement.

An exploratory grid varied one parameter at a time around the frozen default, in 11 cells of 1,000
persons: the loading range ([0.10, 0.25] and [0.50, 0.80]), `phi_D` (0.3 and 0.9), the help effect (0.25
and 1.0), day-level indicator-4 contamination, the rising-share slope (0.25 and 1.0), and `m1 = 1.5`. The
plan, its six expectations and its success rule (a 95 percent interval excluding the null in every
cell) were committed and hashed before the run (supplementary repository, `sim/ROBUSTNESS-PLAN.md`);
two cells were computed once before that commit, for a refactor check. `h` was re-tuned per cell and the
schedule parameters were not. The grid changes no verdict in Table S1.

Under the plan's pre-stated rule, three of the six expectations held in every cell (S3, S5, S6), and
three failed the pre-stated rule in named cells (S1, S2, S4; bullets below). The grid's default cell uses a re-tuned A-fixed threshold
(`h` = 3.209, against 3.334 in the frozen tuning) and different seeds, so its magnitudes (for example a
triggered slope ratio of 0.829 [0.770, 0.890]) are not comparable with Table S1.

- Held: passive rules beat their own chance baselines, state-dependent non-response added bias that
  propensity weighting did not remove (tested at `m1 = 1.5` only: added bias 0.162 [0.091, 0.207]), and
  the context shift raised false flags (CS over S ratio 1.43 to 1.93), in every cell tested.
- S1 failed in one cell. The triggered schedule's probed-day slope was below the all-days slope in
  every cell (ratio 0.550 to 0.893); the `current` control's interval crossed 1 in the low-loading cell
  (0.885 [0.622, 1.176]).
- S2 failed in three cells. Its direction held in all 11 cells on point estimates (positive for
  indicator 4, negative for indicator 5), but indicator 4's interval crossed zero in the low-loading,
  high-persistence and strong-coupling cells, where its standard error was 5 to 16 times the default's.
  Read as precision rather than a sign reversal, this still means the grid says little about indicator 4
  in those cells. The indicator-5 value in the low-loading cell, -2.707 [-6.264, -0.707], is not
  interpretable: the simulated attenuation ratio divides by the unmixed indicator's within-person
  validity, which is small at weak loadings.
- S4 failed in one cell. It expected probe-only to be indistinguishable from chance; at `m1 = 1.5`
  probe-only fell just below its chance baseline (-0.010 [-0.019, -0.001]), a single marginal exclusion
  in 1 of 11 cells, which chance alone can produce. The below-chance direction was not anticipated, and
  attributing it to non-response concentrating when the state is elevated is a post hoc conjecture. In
  the other ten cells, an interval containing zero is not evidence of equivalence.

## S9. Exploratory sensitivity: the baseline series for indicators 4 and 5, not frozen (v4.2 section 3.11)

A-fixed's component (ii) scores indicators 4 and 5 from the authorship-filtered text, but the per-person
baseline mean and standard deviation that those two indicators are standardized against were fit on the
unfiltered text, in the frozen code and in every run above. The frozen text did not say which series the
baseline uses, and the mismatch was found after scoring, while reading the code (supplementary repository,
spec section 18.1). On the attribution round's panels, not the frozen seeds, it offsets the composite's level
(an S mean of about +0.14 as run against +0.03 with a matched baseline) and inflates the scale of the two
z-scores by about 1.2; because `h` was tuned with both, the frozen false-flag rate is unaffected. A post-freeze
sensitivity analysis, planned and hashed before it ran (`sim/SENS-BASELINE-PLAN.md`), re-scored the frozen
evaluation seeds with the baseline fit on the filtered series and every threshold and schedule re-tuned by the
frozen procedure. None of the 14 primary verdicts in Table S1, and no component boolean, changed. Detection
point estimates were lower (A-fixed's 21-day DR sensitivity 0.176 against 0.197; P8's gap 15.7 [13.3, 18.2]
against 17.8 [15.2, 20.4] points), with overlapping separate intervals and no paired interval computed, so the
drop is not established. With the frozen thresholds kept instead of re-tuned, five verdicts change and
A-fixed's false-flag rate falls to 0.072 per tracked person-month against 0.151 as run, which the plan's
reading rule classes as an operating-point effect. The frozen verdicts stand; the as-run baseline is a
disclosed choice, not a fix, and the matched baseline is the one a future scorer should use.

## S10. Spec 003 design and freeze (v4.2 section 3.12)

Spec 003 keeps the generator of section 3.2 and Supplement S2 and A-fixed (`k = 0.5`), with help off, a 210-day record and a 28-day
baseline. In families DR-1.0 and DR-1.5, `D` ramps to a mean 1.0 or 1.5 SD higher from an onset drawn uniformly on
days 70 to 120, and stays there. An alarm (a flag, section 3.2) on day `a` is confirmed if probes on `a + L`, `a +
2L` and `a + 3L` (`L` = 3, 9 and 29 at `phi_D` 0.3, 0.7 and 0.9) average at least 0.5 above four baseline probes;
the comparators are next-day probes and, in simulation only, an oracle reference free of baseline error in `D`.
The probe rule `wait` probes a later alarm only after the last probed alarm's third probe day; `all` probes every
alarm, and `stop` none after a first confirmation; the budget target is 3.0 probes per tracked person-month. In
the PS families the agent's own behaviour changes on a day in the same window, logged for half of persons with the
indicators it can touch: PS-sub raises indicators 1, 2 and 6, PS-use also adds check-ins, PS-prop shifts in
proportion to each person's loadings, and DR+PS adds PS-use's change to DR-1.0 near onset. Rule L0 ignores the
log; L1 resets `S`, holds it and re-baselines every indicator over 14 days; L2 re-baselines only the logged
indicators; M1 attributes an alarm from the indicator pattern alone.

Two registered predictions (H2a, H3) and four construction checks (H1a, H1b, H4, H5) were frozen in
`sim/PREREG-003.md` (supplementary repository) at commit `57208bc`, 12:27 CDT on 2026-10-07, sha256
`06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79`, a local commit, and scored once (attested by
the run log; the frozen scorer did not enforce it) at N = 4,000 persons per cell, with 1,000 bootstrap resamples
and a seed (192815961) derived from the frozen file's hash. Choices made after the design run are disclosed there:
H3's point rule for L1 and L2, chosen knowing it passed on the design draw (1.421) where the interval rule did not
([1.175, 1.706]), while the only other draw gave 1.629, above 1.5; H1b's 0.70, just under the design lower bound
(0.715); H2b's demotion to exploratory; a 21-day re-baseline window, evaluated and not taken; the budget rule; and
N, raised from 2,000.

A blocking design review by a separate AI agent was complete at 10:44 CDT, before the freeze, but the freezing
lane (the agent session that froze the file) had not read it, and its blocking items, among them an objection to
H3's point rule, were not applied. A dated amendment written after the evaluation (`sim/POST-EVALUATION-003.md`)
discloses the review and adds post hoc readings and nine definition corrections, one of which retires the frozen
phrase "non-refractory tracked days"; it changes no frozen verdict, threshold or number.

## S11. Spec 003 results detail (v4.2 section 3.13)

**Table S2. Predictions, spec 003 evaluation run.** Point [95% person-bootstrap interval], 4,000 persons per cell;
"cc", construction check. S, stationary `D` with no observer change; DR-1.0, a ramp in `D`; PS-sub, PS-use and
PS-prop, stationary `D` with an observer change logged for half of each family's persons (PS-use also raises the
agent's check-ins; PS-prop's change is proportional to each person's loadings). H3 uses the logged persons of
PS-sub and PS-use, H5 the unlogged persons of PS-prop. H3's rate, for each rule and family, is the logged persons'
alarms per 30 tracked days from the later of the change day and the end of the 28-day baseline to day 210, pooled
over persons (total alarms over total tracked days), divided by the same persons' pooled rate on the S panel over
the same window. A tracked day is one on which the detector neither abstains nor holds: days in the 14-day
refractory period count as tracked (the frozen text's "non-refractory" misdescribes the scorer that produced the
verdicts), and L1's 14 hold days after the change do not. Verdicts compare the stored 4-decimal values with the
thresholds. A prediction fails if any clause fails.

| | statistic | threshold | est [95% interval] | verdict |
|---|---|---|---|---|
| H1a (cc) | S, `phi_D` 0.7: confirmed share, spaced minus next-day | interval at or below -0.15 | -0.2643 [-0.2956, -0.2345] | PASS |
| H1b (cc) | DR-1.0, `phi_D` 0.7: spaced over next-day confirmed share, first in-window alarm (persons in the Notes) | interval at or above 0.70 | 0.8871 [0.8398, 0.9403] | PASS |
| H2a | S, `phi_D` 0.9: spaced confirmed share minus oracle-reference share | interval at or above 0.10 | 0.2019 [0.1748, 0.2267] | PASS |
| H3 | logged-person alarm rate over S, all six clauses | all six hold | | FAIL |
| | L1, PS-sub | point below 1.5 | 1.5756 [1.4205, 1.7489] | fails |
| | L1, PS-use | point below 1.5 | 1.4599 [1.3211, 1.6276] | holds |
| | L2, PS-sub | point below 1.5 | 1.2110 [1.1195, 1.3090] | holds |
| | L2, PS-use | point below 1.5 | 1.1935 [1.1035, 1.2859] | holds |
| | L0, PS-sub | interval above 1.5 | 3.1239 [2.9606, 3.3025] | holds |
| | L0, PS-use | interval above 1.5 | 3.1286 [2.9611, 3.3126] | holds |
| H4 (cc) | logged DR+PS, `phi_D` 0.7: 21-day sensitivity, L2 minus L1 (persons in the Notes) | interval above 0.0 | 0.2035 [0.1768, 0.2306] | PASS |
| H5 (cc) | persons alarmed under L0 within 42 days of onset (DR-1.0) or of the change (unlogged PS-prop): share whose first such alarm M1 attributes to the person, DR-1.0 minus PS-prop | interval inside (-0.10, 0.10) | -0.0014 [-0.0153, 0.0123] | PASS |

*Notes.* The definitions follow the amendment's wording corrections (`sim/POST-EVALUATION-003.md`, section (f)),
which change no number. H1b: among DR-1.0 persons with an alarm in `[t0, t0 + 21)` and none before the onset `t0`,
the first in-window alarm is confirmed, and the statistic is the spaced confirmed share over the next-day
confirmed share, each among confirmable alarms (at least two probes answered). H4: logged DR+PS persons with `t0`
in `[c, c + 13]`, where `c` is the change day, so that the shift begins inside L1's hold; 21-day sensitivity, with
pre-onset alarms not excluded. H5: among persons with an alarm under L0 in `[x0, x0 + 42)`, where `x0` is the
onset for DR-1.0 and the change day for PS-prop, the share whose first such alarm M1 attributes to the person.
H5's second clause, L0+label, is 0.0000 for any data: the rule labels an alarm *person* unless a logged change
falls in the 14 days before it, and neither arm has a log entry, so the clause is true by definition and not
scored. Because it reads the policy log it is not an indicator-only rule, and H5's claim is limited to M1. H1 and
H2 are scored under the probe rule `all`; each scores a person's first post-baseline alarm, which every rule
probes, so the statistics are the same under `all`, `wait` and `stop`. H3, H4 and H5 use no probes. Nothing was
re-tuned after scoring.

**Reported, not scored** (PREREG-003 section 4). H2b, the reduction in the H2a gap from a 28-day to a 56-day
baseline, was 0.0475 [0.0153, 0.0801], under the 0.05 threshold it was demoted from. H6, matched `k` minus `k =
0.5` in 21-day sensitivity at `phi_D` 0.7, was -0.0230 [-0.0335, -0.0118] for DR-1.0 and -0.0518 [-0.0643,
-0.0395] for DR-1.5. On H4's persons, L2 minus the unregistered L1_step was 0.2080 [0.1827, 0.2318].

**Unregistered comparison arm for H3.** The unregistered L1_step arm,
which leaves the unmapped indicators on their pre-change baseline, gave 0.934 [0.857, 1.022] on PS-sub and 0.927
[0.849, 1.014] on PS-use. It was not sized or registered for H3 and is reported as a comparison, not a rescue:
under the frozen rule H3 stands as failed.

**Probe budget.** Under the `wait` rule (section 3.6 and Supplement S10), DR-1.5 used 2.401 [2.376, 2.425] probes
per tracked person-month at `phi_D` 0.7; the design rule `all` used 3.318 [3.271, 3.363]. The target is read on
the 95 percent upper bound, a reading rule adopted post hoc in the amendment because the frozen text gave none; on
this draw the point and upper-bound readings agree in every cell of the budget table. On that reading `wait` met
3.0 for every family at `phi_D` 0.7 (upper bounds 2.425 for DR-1.5, 1.978 for DR-1.0, 1.277 for S). The cost is in
the in-window share: persons confirmed in window fell from 0.321 under `all` to 0.288 under `wait`, a difference
of 0.032 for which the run stores no paired interval. `wait` also lowered S's confirmed false alarms per tracked
month at `phi_D` 0.7 (0.066 to 0.053). The 3.0 target is claimed only at `phi_D` 0.7: at 0.9 `wait` cut DR-1.5's
in-window share from 0.260 to 0.160, and at 0.3 it equalled `all`, under which DR-1.5 did not meet 3.0 (3.699
[3.654, 3.740]); only `stop` did (1.798 [1.775, 1.818]). Only `all`, `wait` and `stop` were compared, so `wait` is
the best of three, not shown optimal.

**Observer-step rules (exploratory, not frozen).** These are design-stage generator means, synthetic, and score no
prediction. Across 200 simulated populations of 1,000 persons (227 to 309 in-window persons each), L1_step
exceeded L1, which re-centres the unmapped indicators, in D-dependent true-positive minus false-positive rate by
about zero at rho 0 (0.004, MCSE 0.002), rising to 0.219 at rho 2 (k 0.5, 63 d; rho scales D's realized effect on
the unmapped indicators, 1 as generated). With an unlogged shift on the unmapped indicators concurrent with the
logged change in every person, L1_step's advantage under equal weighting was 0.041 at rho 0 and 0.093 to 0.142 at
rho 0.5 to 2; at twice the weight on false alarms, L1 was ahead at every rho (-0.148 to -0.047). On the same
populations, the L0 interaction of the D change with the observer change at 21 days was 0.108 (single draw 0.154).
L1_did, a within-person difference-in-differences variant dropped before the freeze, exceeded L1 by about zero at
rho 0 (-0.001) and by 0.071, 0.150 and 0.273 at rho 0.5, 1 and 2; and the step of a decomposition from L1 to
L1_step that only stops re-centring the unmapped indicators was about zero at rho 0 (0.005) and 0.208 at rho 2.

## S12. Corpus audit detail (v4.2 sections 4.1 to 4.3)

### Methods, in full (v4.2 section 4.1)

**Data and scope.** The corpus is my own transcripts from one coding-agent command-line tool, read only.
I am a heavy user of automation (section 4.2), so the corpus is not a sample of everyday agent
conversations, and the contamination below tracks this user's automation. Every
aggregate below is computed on the 73,955 user-role entries timestamped on or before a snapshot cutoff
(2026-09-28T01:32:31Z), which the audit script reproduces from any later state of the corpus. Raw scan
counts are not reported: they depend on when the scan runs, because the transcript store keeps growing,
including from the sessions that produced this analysis.

**What is kept.** Per-entry metadata (timestamp, session, role, flags, provenance fields, harness
version, model id, length) and an authorship class. Tool-result payloads are walked in memory only to count characters and are not stored or classified; other text is
used only in memory, to classify and check for pastes.

**Authorship classes**, in priority order: `sidechain` (subagent traffic); `tool-result`; `injected`
(native provenance where present, otherwise structural markers of harness and hook text); `human+paste`
or `injected` for entries with a paste marker, depending on whether typed text remains outside it;
`lane-prompt` (a session's first entry matching a stored automated prompt); and `human-typed` for the
rest. Native provenance fields cover under 5 percent of user entries, so the classifier rests mostly on
markers. Sessions are `autonomous` (no typed entry), `mixed` or `interactive`.

**Indicators.** Late-activity share (entries between 00:00 and 05:00 local), session fragmentation
(distinct sessions per active hour) and message length (mean log characters), each in three versions:
naive (all user-role entries), middle (dropping the structurally tagged tool results and subagent
traffic) and typed (`human-typed` only). Only the
disagreement between versions is reported, never the level of a typed series, which is the nearest
thing here to a behavioural signal about the person.

**Change points.** Days with a typed entry were split chronologically at 70 percent (cutoff
2026-09-21). Change points were found on training days by penalized binary segmentation and checked
against independently dated infrastructure events (versions, model ids, configuration backups, policy
dates, hook changes).

### Result paragraphs shortened or moved (v4.2 section 4.2)

Of 73,955 user-role entries, 688 were classed as typed. On the main thread, excluding tool results and
subagent traffic, there were 6,154 text-bearing entries: 688 typed and 5,466 machine-authored, and the
5,466 are exactly the injected (5,249) and automated-prompt (217) entries. The machine text here is harness
injection and automated prompts, not delegated drafts. Its share is 0.888 by entry and 0.845 as a day
mean (SD 0.174 over 24 days); its entry-level gap and variance ratio are 0.274 and 0.547, and its
day-level share, gap and ratio (21 days) are 0.823, 0.196 and 0.098.

**Person-absent sessions.** Of 1,544 main sessions, 1,303 (0.844) had no typed entry, 20 were mixed and
221 interactive. The autonomous sessions supplied 0.570 of all naive user-role entries, 0.750 of the
entries between 00:00 and 05:00, and 0.746 of the session-by-hour units behind the fragmentation
indicator.

Fragmentation contamination comes from injected and automated-prompt traffic: dropping tool results and
subagent traffic leaves the series almost unchanged, and the middle series is nearly unrelated to the
typed one. Message length is broken twice, by tool-result and subagent traffic and again by injection.
Late activity agreed best even though three quarters of its naive entries came from autonomous
sessions, so that agreement is a property of this window. Split by time (15 training and 6 test days), the naive
against typed correlations were 0.94, 0.15 and 0.38, then 0.90, -0.30 and 0.78; 6 days are too few to
read as a change.

**Pastes, agent drafts, third parties.** 0.30 percent of user-role entries carried a paste marker, and
none was classed `human+paste`. No typed entry shared a 200-character span with the session's last five assistant turns, a check that
misses older and cross-session pastes. 0.77
percent of tool results came from a tool whose name matched a messaging, calendar or email keyword, a
structural estimate of third-party content, not a count of other people.

**Change points.** The snapshot has 7 harness versions, 10 model ids and 27 dated
infrastructure-event candidates. The training period yielded 8 change points across the six naive
and filtered series, and all 8 fell within 3 days of a candidate event. That is uninformative,
because every calendar day in the range has a candidate within 3 days: in this corpus every change in a
trace-derived series has a plausible infrastructure explanation nearby.

**Data density.** 24 days had user-role activity and 21 had a typed entry.

### Limitations of the audit, in full (v4.2 section 4.3)

- **n = 1, descriptive.** One person's corpus from one tool, and that person also wrote the audit, the
  automated processes behind most of the machine text, and the harness configuration. It is an
  existence proof and a measurement protocol, not an estimate for any population.
- **Unseen channels.** Dictated text and messages relayed from a phone look like desktop typing. An
  automated process whose prompt was never stored is classed as typed, so the typed share is an upper
  bound on that account.
- **Retention.** The tool deleted transcripts after 45 days, leaving 24 active days; any longitudinal
  analysis of this corpus is capped by that setting.
- **Scope of measurement.** Three of six indicators were computed, and no state or label was estimated.

## S13. Limitations and scope, full list (v4.2 section 6)

1. **One latent state, not a condition.** The simulated state `D` is a single, non-clinical wellbeing
   and functioning variable. Nothing in the simulation maps to any clinical condition, and no condition
   is a target or a result anywhere in this work.
2. **Invented parameters.** Every loading, help effect, context effect, usage dependence and workload
   loading (`lam`, `psi`, `eta`, `kappa`, `gam`) in the generator is invented, as are the machine-text
   parameters for indicator 5 and the coupling in the rising-share cell. Only indicator 4's mixing
   parameters come from data, from one person, and at the entry rather than the day level. Every
   sensitivity, false-flag rate and bias is conditional on these values.
3. **Help moves indicators only.** In the generator, help changes indicators and never changes `D`.
   Nothing in this paper bears on whether an agent's intervening helps or harms anyone.
4. **The criterion is valid by construction.** `Y = D + e`. Real criteria have their own validity
   questions, and the simulation does not model them.
5. **The false-flag target is high.** One false flag per six tracked person-months is a tuning target
   for comparing rules, high for any setting in which a flag would reach a person; Supplement S6 shows
   other operating points.
6. **One rule is not compared.** A language-model evidence reader was specified as future work and not
   run, because no local model was available, and no conclusion about it is drawn.
7. **The corpus audit is n = 1 and descriptive.** It measures authorship contamination in one person's
   transcripts over 24 active days and estimates nothing about that person.

Combining passive and criterion data was not tested. An earlier simulation in this program found no
resolved difference between ask-versus-infer budget rules at 300 to 1,000 person-weeks (Mettu, 2026b,
Study 2); the schedules here are judged on calibration and detection instead.
