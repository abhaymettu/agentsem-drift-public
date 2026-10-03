# sim/ATTRIBUTION.md -- EXPLORATORY results, not frozen, synthetic only

Plan: `sim/ATTRIBUTION-PLAN.md` r1, sha256 `dbc0024ac14d7eb877415006c46fde3544ba9530f8e46fc7f2e6580057f3d22d`,
committed at `ccbcf51` before any evaluation panel was scored. Code: `sim/attribution.py` at that
commit (`--check` passes). Raw output: `sim/attribution.json`. Not part of `sim/PREREG.md`; no P1-P10
verdict and no paper v4 number changes. 1000 simulated persons per family, frozen default cell, A-fixed
at the frozen `h = 3.334`. Person bootstrap, 2000 draws; `±` is the bootstrap SE. Runtime 3.3 s.

`q* = 6.59`, from 245 tuning-panel DR alarms in `[t0, t0 + 21)`.

## Results by family

Scored alarms on days `[max(c_i, 28), 134]`. Rate is person-attributed alarms per tracked person-month.
Share is person-attributed alarms over all scored alarms.

| family | `D` changes | alarms | rate M0 | share M1 | share M2 | share M2x3 | share M3 |
|---|---|---|---|---|---|---|---|
| S | no | 256 | 0.159 ± 0.011 | 0.875 ± 0.021 | 0.527 ± 0.033 | 0.562 ± 0.033 | 0.484 ± 0.032 |
| PS-sub | no | 895 | 0.555 ± 0.020 | 0.880 ± 0.012 | 0.461 ± 0.017 | 0.511 ± 0.018 | 0.446 ± 0.018 |
| PS-prop | no | 1216 | 0.755 ± 0.022 | 0.874 ± 0.011 | 0.434 ± 0.015 | 0.456 ± 0.016 | 0.390 ± 0.016 |
| AV2 | no | 627 | 0.398 ± 0.018 | 0.925 ± 0.011 | 0.469 ± 0.020 | 0.509 ± 0.021 | 0.474 ± 0.021 |
| CS | no | 551 | 0.341 ± 0.016 | 0.871 ± 0.015 | 0.508 ± 0.022 | 0.517 ± 0.022 | 0.450 ± 0.022 |
| DR, `[t0, 134]` | yes | 1104 | 0.692 ± 0.022 | 0.896 ± 0.010 | 0.625 ± 0.015 | 0.756 ± 0.014 | 0.674 ± 0.016 |
| DR, `[t0, t0+21)` | yes | | | 0.893 ± 0.020 | 0.611 ± 0.032 | 0.766 ± 0.027 | 0.672 ± 0.030 |

The share of alarms where M1 was not assessable (`J' < 3`) was 0 in every family.

**DR 21-day sensitivity** (ratio to M0): M0 0.166 ± 0.012; M1 0.152 (0.916 ± 0.026); M2 0.122
(0.735 ± 0.044); M2x3 0.153 (0.922 ± 0.042); M3 0.138 (0.831 ± 0.046).

**Probe cost** per tracked person-month in S: M2 0.15, M2x3 and M3 0.46, plus the 4-probe baseline
block. The frozen budget target is 3.0.

**Momentary-state selection** (scored post-change alarms; mean `D` on tracked days is 0.02 in S, PS-sub
and PS-prop):

| family | `D_t` on alarm day | `D_{t+1}` | mean `D` over `t+1, t+3, t+5` |
|---|---|---|---|
| S | 1.35 | 0.98 | 0.53 |
| PS-sub | 0.92 | 0.66 | 0.40 |
| PS-prop | 0.80 | 0.56 | 0.31 |
| AV2 | 0.80 | 0.56 | 0.33 |
| CS | 1.12 | 0.77 | 0.41 |
| DR | 1.77 | 1.51 | 1.28 |

## Predictions

| | prediction | estimate | holds |
|---|---|---|---|
| A1 | PS-sub / S alarm rate under M0 above 1.5 | 3.50 ± 0.18 (95% 3.19 to 3.88) | yes |
| A2 | M1 cuts PS-sub's rate to at most 0.5 of M0 | 0.880 ± 0.012 (0.856 to 0.904) | no |
| A4 | M2 DR retention below 0.65 of M0, and PS-sub M2 share above 0.25 | retention 0.735 ± 0.044; share 0.461 ± 0.017 | share yes, retention no |
| A5 | mean `D_t` on S and PS-sub alarm days above 0.3 | 1.35 and 0.92 | yes |
| A6 | (DR minus PS-prop share) under M2x3 exceeds that under M1 by 0.15, CI above 0 | 0.279 ± 0.027 (0.229 to 0.332) | yes |

Known-answer check: M1's DR share minus its PS-prop share is 0.022 ± 0.015 (-0.008 to 0.050), within
the 0.10 that section (a) of the plan implies.

## Reading

1. **An unlogged change in how the agent observes is a large false-alarm source.** A +0.5 intercept
   shift on three timing and session indicators, with the person unchanged, raised A-fixed's
   post-change alarm rate 3.5-fold over the same persons without the shift (A1). AV2, which shifts two
   indicators and also lowers their loadings, gives 0.398 against S's 0.159 over the same window
   (about 2.5-fold, independent panels); its frozen ratio of 1.75 is over all tracked months.

2. **A per-person profile test has no power at this scale.** M1 kept 0.87 to 0.93 of alarms in every
   family, person change or not, and PS-prop is invisible to it by construction. A post-hoc check
   (separate seed, not in the plan) shows why. PS-sub's shift alone gives a noise-free `Q` of 0.63. On
   random tracked days in S, `Q` has a median of 2.53 and a 90th percentile of 5.76; `q*` is 6.59. `Q`
   sits far above its independent-days value of about 1 because the z-scores are autocorrelated and
   share `D` and workload. A 14-day window gives about 8 to 11 usable days per indicator, which is too
   few to see a 0.45-SD shift confined to half the indicators. Indicator-pattern evidence for observer
   change is a between-person tool (DIF and partial invariance across many people), not a
   within-one-person alarm-time tool, unless the window is several times longer.

   The check, from `sim/` (seed 7, S panel, 2000 random person-days on days 41-133):
   `base sd` per indicator 1.11, 1.10, 1.09, 0.65, 0.64, 1.08; usable days per 14-day window 11.2, 7.8,
   7.8, 11.2, 11.2, 11.2; noise-free `Q` = `sum n_j (d_j - dbar)^2 / 5` with `d_j = 0.5 / sd_j` on
   indicators 1, 2, 6 and 0 elsewhere. It used `score_panel` and `q_stat` from `attribution.py`.

3. **Probes separate, but only partly, and the alarm selects the state they read** (see tables). In
   the shared-person S/PS-sub pair, the rate PS-sub adds over S falls from 0.396 per person-month under
   M0 to 0.195 under M2x3 and 0.171 under M3 (differences of the table's point rates). The rest
   survives because alarms fire on days of high momentary state even with no sustained change, and a
   probe the next day reads that excursion. With `phi_D = 0.7`, probes at `t+1..t+5` still sit inside
   its memory (0.7^5 = 0.17). The frozen design scores those S alarms as false; they are true momentary
   elevations against a sustained-change target, and a confirmation probe cannot tell the two apart
   unless it is spaced beyond the state's memory. This is N2's verification-bias structure again, at
   the confirmation step: the alarm selects which days the criterion is sampled on.

4. **Costs.** M3 over M2x3 lowers non-state rates by 0.012 to 0.050 per person-month for 0.09 of
   sensitivity; M1 is not worth its cost here.

## Candidates for the next study's spec (not tested here)

- Confirmation probes spaced past the state's memory (`h` with `phi_D^h` small, e.g. 7 to 14 days)
  when the target is sustained change, or a target that names momentary elevation explicitly so that
  S's alarms stop counting as false.
- The policy log as the primary separator, which is section 11.5's "one logged field is necessary"
  outcome. In the frozen run, removing reset (iv) raised logged-AV false alarms 1.85-fold (P3). This
  run shows that neither indicator patterns nor a few probes replace the log.
- `m1 > 0`, `kappa`, targeted help and usage-changing PS variants were not run.
