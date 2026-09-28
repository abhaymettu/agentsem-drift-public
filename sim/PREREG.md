# sim/PREREG.md -- frozen pre-registration

STATUS: frozen by the commit that adds this file. The sha256 of this file is recorded in the lane receipts
(`~/lanes/bridge-jobs/agentsem-overnight-20260927/receipts.md`) at freeze time, because a file cannot contain its own hash. This document is hashed with sha256, and
every evaluation seed used by `score()` is derived from that hash via `eval_seed()`. It is committed
before any evaluation-seed scoring runs, per constitution III (freeze before scoring).

Indicator-4 pilot values (constitution II: real, non-inferential authorship metadata, not invented).
Sourced from `pilot/indicator4_params.json` ("main_thread", 24 days), landed 2026-09-27, superseding
the spec's design-time placeholders (`PI_BAR = 0.2`, `KAPPA_A4 = 0.5`, `MU_M4 = 1.0`):

Reproduce with `python3 pilot/trace_audit.py --until 2026-09-28T01:32:31Z` (the corpus snapshot the values were taken
from; the live corpus keeps growing).

- `PI_BAR = 0.845` (day-mean non-human share of indicator-4 text)
- `KAPPA_A4 = 0.547` (agent-text variance for indicator 4)
- `MU_M4 = 0.274` (agent-text mean gap, in units of indicator 4's own
  within-person SD -- the pilot reports this SD-relative, not raw, so `generate_panel` converts it to
  the raw scale internally using indicator 4's own empirical baseline mean/SD; PSI is 0 for indicator 4
  so this conversion needs no help-mode assumption)

**Known deviation** (constitution IV: source or mark it): the pilot's realized day-level SD of `pi` is
0.174. The spec fixes the mixing distribution at `Beta(10 pi_bar, 10 (1 - pi_bar))` a priori, which at
`pi_bar = 0.845` implies SD = sqrt(pi_bar(1-pi_bar)/11) = 0.109. This
gap between the fixed-concentration Beta and the pilot's actual dispersion is carried forward, not
corrected, per the spec's a priori tunable list.

At this `pi_bar`, A-fixed's authorship filter still leaves a non-trivial residual mixture:
`pi' = 0.1 pi_bar / (0.1 pi_bar + 0.95 (1 - pi_bar))` = 0.365,
down from pi_bar itself -- indicator 4 is diluted but not zeroed out; see the P6 --check (d) rerun at
this pi_bar in the build report for the attenuation this implies and whether indicator 4 still carries
signal at this contamination level.

## Pre-freeze deviations (recorded before any evaluation-seed run)

1. **`--check (c)` fails for drift persons.** The `current` control's slope moves 6.0% relative for
   drift persons (converging to about 5.4% at n = 60,000) and 3.9% for stable persons. The bound is 5%.
   The reviewer's own toy (`opus-review-checks/p4check.py`) gives the same order of effect (5.3%). The
   5% bound was an expectation, not a property of the DGP. It is kept as written and reported as failed
   for drift, and the paper discusses it under calibration. P4's frozen thresholds are unchanged.
2. **The triggered schedule cannot meet the 3.0 probes per person-month budget.** At p_trig = 1.0 it
   reaches 2.265 on the S+DR mix (`tuning.json`, `triggered_budget_target_unreachable`). It runs at
   p_trig = 1.0, and its realized budget is reported per family. P4 compares each schedule with its own
   all-days value, so it does not depend on budget matching. P8 does not use `triggered`.
3. **One pre-freeze call of `score()` for timing.** The builder called `score()` once with a
   monkeypatched non-evaluation seed function to time the grid (about 2.4 s). It reports that it deleted
   the outputs unread beyond checking that the keys exist. No evaluation-seed outcome has been computed.
   The DGP is the same, so this is disclosed, not hidden.
4. **Builder conventions the spec left open:**
   - The targeted-help baseline (days 1 to 28) uses constant p = 0.3.
   - Targeting uses A-fixed's composite without feature (iv).
   - `mu_M4` is read in human-SD units and converted internally.
   - Baseline-fit fallbacks: mean 0, SD 1, slope 0 for fewer than 2 or 3 observations.
   - P4 to P6 are scored on family S.
5. **Probe-only's `h` was re-tuned pre-freeze, after a review fix.** `tune_h('probe-only', ...)`
   previously scored an oracle over every responded day (as if probe-only observed the full-
   resolution `Y` z-score on every day), not the `random` schedule (baseline block plus daily
   p = 0.1) the spec actually specifies for it. Fixed via one shared `probe_only_C()` helper used
   by both tuning and `score()`'s P8, so the two can no longer drift apart. Re-tuned on the same
   tuning seed 20260927, family S, target 1 false alarm per 6 tracked person-months: `h` moved
   from 12.206 (oracle) to 6.539 (actual `random`-schedule subsample; se rose from 0.0103 to
   0.0262, expected with far fewer observed days). This is allowed pre-freeze (no evaluation seed
   has been touched). No other tuned value changed: the other 8 architectures' `h` and the
   schedules block (`p_trig`, `p_trig2`, `c_star`, realized budgets) were independently
   recomputed and reproduce bit-for-bit.

## Tuned values (tuning seed 20260927, family S / 50-50 S+DR mix; see sim/tuning.json for MC SEs)

```json
{
  "seed": 20260927,
  "n_persons": 1000,
  "pi_bar": 0.845,
  "kappa_a4": 0.547,
  "mu_m4": 0.274,
  "h": {
    "pop": {
      "h": 1.1249347774999023,
      "fa_per_month": 0.1663685152057245,
      "se": 0.007380457869130357
    },
    "A-naive": {
      "h": 1.7389433940814796,
      "fa_per_month": 0.1663685152057245,
      "se": 0.009991451004787367
    },
    "A-fixed": {
      "h": 3.334059865253539,
      "fa_per_month": 0.1667207120573403,
      "se": 0.009560896416310158
    },
    "A-fixed-minus-i": {
      "h": 2.787842753091673,
      "fa_per_month": 0.16638525790833156,
      "se": 0.009613411605929675
    },
    "A-fixed-minus-ii": {
      "h": 1.6983614457965361,
      "fa_per_month": 0.1667207120573403,
      "se": 0.009549548610174402
    },
    "A-fixed-minus-iii": {
      "h": 3.730378785959738,
      "fa_per_month": 0.16638525790833156,
      "se": 0.010007641568572982
    },
    "A-fixed-minus-iv": {
      "h": 3.334059865253539,
      "fa_per_month": 0.1667207120573403,
      "se": 0.009560896416310158
    },
    "A-fixed-minus-v": {
      "h": 3.334059865253539,
      "fa_per_month": 0.16670393559928443,
      "se": 0.009559429467686582
    },
    "probe-only": {
      "h": 6.539074181460682,
      "fa_per_month": 0.16505726476532676,
      "se": 0.026168812573987826
    }
  },
  "schedules": {
    "p_trig": 1.0,
    "p_trig2": 0.7947019867547169,
    "c_star": 0.9564857684190429,
    "realized_budget": {
      "triggered": 2.2649999999999997,
      "mixed": 2.9999999999994342,
      "current": 2.9999999999999996
    },
    "h_fixed_used": 3.334059865253539,
    "triggered_budget_target_unreachable": true,
    "mixed_budget_target_unreachable": false
  },
  "wall_seconds": 3.2938458919525146
}
```

## Prediction-to-cell mapping (which families/cells/architectures/schedules each prediction scores on)

```json
{
  "P1 (construction check)": {
    "families": [
      "SP",
      "VA",
      "DE",
      "BI"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-naive",
      "A-fixed",
      "A-fixed-minus-iii"
    ]
  },
  "P1b (construction check)": {
    "families": [
      "DE",
      "S"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed"
    ]
  },
  "P2 (construction check)": {
    "families": [
      "DR"
    ],
    "cells": [
      "targeted_theta1_05"
    ],
    "architectures": [
      "A-naive",
      "A-fixed",
      "A-fixed-minus-i"
    ]
  },
  "P3 (construction check)": {
    "families": [
      "AV",
      "AV2",
      "S"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed",
      "A-fixed-minus-iv"
    ]
  },
  "P4": {
    "families": [
      "S"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed"
    ],
    "schedules": [
      "triggered",
      "mixed",
      "current"
    ],
    "note": "current uses a dedicated common-lam / population-z-scaling isolate (--check c), not the family-S/A-fixed panel; its default-cell value is reported without a threshold."
  },
  "P5": {
    "families": [
      "S"
    ],
    "cells": [
      "default",
      "m1_05",
      "m1_15"
    ],
    "architectures": [
      "A-fixed"
    ],
    "schedules": [
      "none",
      "fixed",
      "random",
      "triggered",
      "mixed"
    ]
  },
  "P6": {
    "families": [
      "S"
    ],
    "cells": [
      "default",
      "bernoulli_mix",
      "pi_rises_with_D"
    ],
    "architectures": [
      "A-fixed"
    ],
    "note": "indicator-level; scored on X (P6 raw) and X_filtered (via pi') without running the full CUSUM pipeline"
  },
  "P7": {
    "families": [
      "DR",
      "DV"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed"
    ]
  },
  "P8": {
    "families": [
      "S",
      "DR"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed",
      "probe-only"
    ],
    "schedules": [
      "none"
    ],
    "note": "probe-only uses its own tuned h and the random schedule at the standard 3.0/month budget target; A-fixed runs passive-only (schedule none)"
  },
  "P9": {
    "families": [
      "BD",
      "DR"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed"
    ]
  },
  "P10": {
    "families": [
      "CS",
      "S"
    ],
    "cells": [
      "default"
    ],
    "architectures": [
      "A-fixed"
    ]
  }
}
```

## Exact commands to score

```
python3 sim/drift_sim.py --check
SHA=$(python3 -c "import hashlib;print(hashlib.sha256(open('sim/PREREG.md','rb').read()).hexdigest())")
python3 sim/drift_sim.py score --prereg-sha $SHA
```

## Spec sections 3 to 6, verbatim (copied programmatically from specs/001-drift-layer/spec.md; no drift)

## 3. Generator (D1)

Per person: 140 days; days 1 to 28 are the baseline window. **1000 persons per family per cell.** Every architecture and schedule runs on the same simulated persons, and differences use a paired person bootstrap.
Persons are the replicates; the Monte Carlo SE is the SD across persons over sqrt(200), or a
2000-draw person bootstrap for ratios. The MC SE is reported beside every number.

- Latent state `D_t` (standardized, within-person): AR(1), `phi_D = 0.7`, marginal SD 1. Drift families
  add a ramp from onset `t0 ~ U[50, 100]` to `+delta_D = 1.0` over `ramp ~ U[7, 21]` days, then hold.
  Family BD puts the onset at `t0 ~ U[10, 25]`, inside the baseline.
- Workload `L_t`: AR(1) with `phi_L = 0.8`, marginal SD 1; SP adds a +1.5 SD block of 10 to 14 days.
  **Observed workload** `L_obs = L + N(0, 0.25)` (variance 0.25).
- Context `ctx` per day in {code, write, personal}, multinomial with base shares (0.5, 0.3, 0.2). The
  personal share's logit rises by `eta = 0.1` per SD of `D`. Family CS switches base shares to
  (0.1, 0.2, 0.7) from a random day in [50, 100], with no state change.
- Usage: a day is used with probability `expit(a0 - kappa * D_t - 4 * vacation_t - 2 * diseng_t)`, with
  `a0 = logit(0.8)`. Default `kappa = 0`; cell `kappa = 0.3`. DE lowers usage (`diseng_t = 1` from a
  random day in [50, 100]) with no state change.
- Indicators on used days, j = 1..6: 1 late-activity share, 2 session fragmentation, 3 deferral/abandon
  rate, 4 message length (log chars of user-role text), 5 negative self-reference rate, 6 reply latency.
  Human-generated value: `H_jt = lam_j D_t + gam_j L_t + beta_j[ctx_t] - A_t psi_j (1 + theta1 D_t) + e_jt`,
  `e ~ N(0, 1)`. `lam_j ~ U[0.25, 0.5]` is drawn per person and indicator. `gam = (0.3, 0.3, 0.3, 0, 0, 0.3)`.
  `beta_j[ctx]` takes the values (0, 0.3, 0.6) for code/write/personal on indicators 1, 4 and 5, and 0
  elsewhere. `psi = 0.5` on indicators 2 and 3 only. Default `theta1 = 0`; cell `theta1 = 0.5`.
- **Authorship mixing (indicators 4, 5), stated mechanism: daily averaging.** The observed value is
  `X_jt = (1 - pi_t) H_jt + pi_t M_jt`, with agent-text value `M_jt ~ N(mu_Mj, kappa_a)` independent of
  `D`, so `c = 0`. `pi_t ~ Beta(10 pi_bar, 10 (1 - pi_bar))`, so Var(pi) = pi_bar (1 - pi_bar) / 11, `pi_bar`, taken from the pilot's human-typed vs other share
  for indicator 4 (default 0.2 until the pilot lands, then replaced before the freeze), `kappa_a` (default 0.5) and `mu_M4` (default +1.0; agent drafts are longer) are replaced by the
  pilot's indicator-4 estimates before the freeze, as `pi_bar` is. Indicator 5's `kappa_a = 0.5` and `mu_M5 = -1.0` (agent text has near-zero negative
  self-reference). Cells: Bernoulli mixing (`pi_t in {0, 1}`); `pi_t` rising with `D` (logit slope 0.5;
  delegation when the state is elevated).
- Agent help: `A_t ~ Bernoulli(p_t)`, `p_t` logged and clipped to [0.1, 0.9]. Default constant 0.3;
  cell targeted, `p_t = clip(expit(logit(0.3) + C_{t-1}), 0.1, 0.9)` (A-fixed's composite).
- Version change (AV): on a random day in [50, 100], indicators 2 and 6 shift in mean by +0.5 and in
  loading by x0.7. Logged for 50 percent of AV persons. Family AV2: the same change (+0.5 in mean, loading x0.7) on indicators 1 and 4, never logged.
- Broken integration (BI): indicators 1 and 6 are missing for 10 to 20 days from a random day in [50, 100].
- Probe answer `Y_t = D_t + e_Y`, reliability 0.7. Response probability `expit(logit(0.8) - m1 * D_t)`.
  Default `m1 = 0`; cells `m1 = 0.5` and `m1 = 1.5`. Probe reactivity is 0; the effect is not simulated.

**Families.** S stable; DR drift; VA vacation (7 to 14 days, from a random day in [50, 100]); SP sprint;
BI broken integration; AV version change; DE disengagement; DV drift with a vacation whose start is drawn from U[t0 - 5, t0 + 5]; CS context shift; BD drift inside the baseline; AV2 unlogged change on other indicators.

**Cells.** One default cell plus one-at-a-time variations: `kappa = 0.3`; `m1 = 0.5`; `m1 = 1.5`;
targeted help; targeted help with `theta1 = 0.5`; Bernoulli mixing; `pi_t` rising with `D`.

**Not used for tuning; mechanism known at design time:** AV, DV. **Not designed for:** CS, BD, AV2.
Evaluation seeds for every family are derived from the sha256 of the committed PREREG. Tuning uses the
separate seed 20260927.

## 4. Architectures and schedules

Missing-data handling (all architectures): the composite is the mean of the within-person z-scores of
the available indicators (baseline mean and SD per person); the composite is not re-standardized, and `k` is in its units. On a day with no usage, or no usable
indicator, the CUSUM statistic `S` is held.

- `pop`: z-scores against the population mean and SD taken from the S tuning run; the same CUSUM.
- `A-naive`: personal baseline over days 1 to 28, all six indicators on every used day, all user-role
  text counted in 4 and 5, no workload term, no reset, no abstention.
- `A-fixed`: A-naive plus:
  - (i) indicators 2 and 3 are used only on unhelped days;
  - (ii) indicators 4 and 5 are computed from text an authorship filter labels human, with the filter at
    se 0.9 / sp 0.95 for agent text;
  - (iii) indicators 1, 2, 3 and 6 are residualized on `L_obs` with a per-person slope fit in the
    baseline;
  - (iv) at a logged version change, `S` is reset and indicators 2 and 6 are re-baselined over the next
    14 days, during which `S` is held;
  - (v) the layer abstains (holds `S`) on days where the 14-day usage count is below 40 percent of the
    baseline rate.
  Context is treated as nuisance-with-signal and is not adjusted in either architecture; CS measures
  what that choice costs.
- **Ablations:** A-fixed minus each of (i) to (v), one at a time.
- `B` (LLM evidence reader): **not run.** No local model is installed (`ollama list` was empty on
  2026-09-27). It is specified in the paper as future work, not simulated with a stand-in.
- CUSUM: one-sided, `S_t = max(0, S_{t-1} + C_t - k)`, with `k = 0.5`. After an alarm, `S` resets to 0
  and a 14-day refractory period follows. `h` is tuned per architecture on S (tuning seed) to 1 false
  alarm per 6 tracked person-months.
- **Probe schedules** (on top of A-fixed). Every schedule except `none` has a fixed baseline block of
  4 probes (days 7, 14, 21, 28), counted in the budget.
  - `none`;
  - `fixed`: every 10 days after the baseline;
  - `random`: daily p = 0.1;
  - `triggered`: p_trig on days when `S` is in [h/2, h);
  - `mixed`: floor 0.04 plus p_trig' in the band;
  - control `current`: probe when `C_t > c*` (a `--check` item, not a prediction).
  The budget target is 3.0 probes per person-month after the baseline. p_trig, p_trig' and c* are
  tuned on a 50/50 S+DR mix (tuning seed), and the realized budget is reported per family. Every
  probe's propensity is logged. IPW is identified only for `random` and `mixed`; for `triggered` and
  `fixed` it is reported as "not identified" (positivity fails).
- **Confirmation rule:** an alarm is confirmed if a probe inside the next 7 days reads above the
  person's baseline-block probe mean by at least 0.5.
- **Probe-only comparator:** a CUSUM on the probe answers alone (z-scored on the baseline block),
  `random` schedule at the matched budget, with `h` tuned the same way.

**Tunables:** `k` 0.5, fixed a priori; `h`, tuned on S; the band [h/2, h), a priori; the 40 percent
abstention cut, a priori; the 0.5 confirmation margin, a priori; the 28-day baseline, a priori; the
14-day refractory and re-baseline, a priori; p_trig, p_trig' and c*, tuned on S+DR.

## 5. Metrics

- **Sensitivity** within 21 days of onset (DR, DV, BD). An alarm before onset counts as a false alarm.
  Abstention across the window with no alarm counts as a miss.
- **Median days to detect**, among detected.
- **False alarms** per tracked person-month and per total person-month, in every family (pre-onset
  days only in drift families).
- **Abstention share** of person-days, with its reasons; for DR, reported at `kappa = 0.3` against
  `kappa = 0`.
- **Probes** per person-month, by family.
- **Confirmation rule:** PPV of confirmed alarms, confirmed false alarms per person-month, days to
  confirmation.
- **Calibration** on probe days: person-centred (on the analysed days) slope of `Y` on `C` and their
  correlation, against the all-days values; unweighted and, where identified, IPW.
- **Sensitivity vs false-alarm curve**, by sweeping `h` on S and DR (default cell).
- **Spread** of person-level false-alarm rates (IQR), not only the mean.

## 6. Predictions (frozen with D2)

Each prediction holds if its 95% Monte Carlo interval lies beyond the stated threshold in the default
cell, unless another cell is named. A 'within X' prediction holds if its 95% MC interval lies inside ±X. It is reported per cell elsewhere. "Holds across the grid" is
claimed only if it holds in every cell. A failed prediction is reported as failed, and nothing is
re-tuned after scoring.

**Pipeline construction checks** (brief item 2; not findings, labelled as such in the paper):

- **P1.** False alarms per tracked person-month, A-naive against A-fixed, by family, with the
  component responsible named: SP at least 2x (iii, workload); VA and DE within 0.5x to 2x (holding `S`
  means neither architecture accumulates evidence on unused days); BI within 0.5x to 2x (no component
  targets indicator missingness). SP is confirmed by the ablation removing (iii). VA, DE and BI have no matching component; they test missing-data handling only.
- **P1b.** A-fixed's DE false alarms per total person-month are no more than 1.5x its S rate (DE changes usage only).
- **P2.** In the targeted-help cell with `theta1 = 0.5`, DR sensitivity for A-naive is lower than for
  A-fixed by at least 10 points, and removing (i) accounts for at least half of the gap. In the
  constant-help default cell, P2 is not tested.
- **P3.** On AV logged persons, removing (iv) raises false alarms by at least 2x. On AV2 (unlogged,
  other indicators), A-fixed's false alarms are at least 2x its S rate. The cost of the reset (the
  sensitivity loss for onsets inside the 14-day re-baseline window) is reported, with no threshold.

**Predictions:**

- **P4.** With `m1 = 0`, triggered-only probes deflate the person-centred composite-to-probe
  correlation relative to its all-days value by at least 0.05, and attenuate the slope by at least 10%
  relative. The reason is that the trigger depends on past composites, which predict current `D` beyond
  `C_t`. The `current` control, run with a common `lam` and population z-scaling, leaves the slope within 5% relative (a `--check` item); in the default cell its value is reported without a threshold. Under `mixed`,
  IPW with the logged propensity recovers both within 0.03 of the all-days values.
- **P5.** Slope bias is stated as relative bias. At `m1 = 0.5` it is under 5% under `random`: the
  default MNAR cell is benign. At `m1 = 1.5` the slope bias added over the same schedule at `m1 = 0` is at least 10% relative under every schedule. A
  response-propensity IPW estimated from observables (`C_t`, lagged composites, day of week) removes
  less than half of it, because response depends on `D_t` beyond what the composite carries.
- **P6.** Under daily averaging with `pi_t` independent of `D`, the within-person validity (the
  person-centred correlation with `D`) of indicators 4 and 5 is attenuated by
  `Att = (1 - E pi) / sqrt(E[(1-pi)^2] + E[pi^2] kappa_r + Var(pi) delta_r^2)`, within 0.03. Here
  `kappa_r` and `delta_r` are the agent-text variance ratio and mean gap in units of the human
  indicator's SD. `V_H` is the person's within-person variance of `H_j`, and Att is evaluated per person and averaged. P6 is scored on the unfiltered indicator; A-fixed's filtered indicator is scored with `pi` replaced by `pi' = 0.1 pi / (0.1 pi + 0.95 (1 - pi))`. In the Bernoulli cell, the same formula reduces to ghost E7 at `c = 0`, again within
  0.03. In the `pi_t`-rising-with-`D` cell, indicator 4's validity is higher than the independent-`pi`
  formula by at least 0.05 (`mu_M4` exceeds the mean of `H_4`): a spurious state coupling through the mean.
- **P7.** A-fixed's DV sensitivity is at least 15 points below its DR sensitivity.
- **P8.** At matched false alarms and budget, A-fixed (whose CUSUM uses no probe answers) has DR sensitivity within 21 days at least 10 points above probe-only, and a restricted mean time to detection, censored at 42 days, at least 3 days shorter. This compares passive-only with probe-only detection. Fusion of probes with passive data is not tested, and the paper says so.
- **P9.** BD sensitivity is an alarm within the first 21 tracked days (days 29 to 49). A-fixed's BD sensitivity
  is at most half its DR sensitivity within 21 days of onset.
- **P10.** On CS, A-fixed's false alarms are at least 1.5x its S rate: not adjusting for context
  makes a context-mix change a false-alarm source.
