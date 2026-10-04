# sim/SENS-BASELINE.md: matched-baseline sensitivity analysis, results (EXPLORATORY)

EXPLORATORY, post-freeze and synthetic. This is not part of `sim/PREREG.md` and is not a re-scoring:
the frozen verdicts in `sim/results.json` stand. Plan: `sim/SENS-BASELINE-PLAN.md`, sha256
`e9768ee5f8d9273b0c6f4c63de7ef478fdacebe73f4e0e5c888025d70013488c`, committed in `3fa1a03` before the run.
Output: `sim/sens_baseline.json`, sha256 `7c18568e4b3e0a6d01ee90682ac40b62c5cf84a84de9dfd7c92374396934ab81`.
A second run from the same hash gave a byte-identical file (`cmp`).
The run used the frozen evaluation seeds (PREREG `60db6dd1...8f17`), `drift_sim.py` unchanged since `9fea182`,
and took 60 s.

Variants: M0 as run; M1 matched baseline for indicators 4 and 5 under (ii), with every `h` and schedule
re-tuned by the frozen procedure (primary); M2 matched baseline with the frozen `h` and schedules.

## 1. Construction checks (E0): all pass

| check | result |
|---|---|
| `--check` (before hashing) | passes |
| E0a: frozen tuning re-run reproduces `sim/tuning.json` | max abs difference 0.0 for every `h` and for `p_trig`, `p_trig2`, `c_star` |
| E0b: M0 against the committed predictions | not byte-identical, as predicted: exactly 9 P6 `se`/`lo`/`hi` fields differ, the largest by 5.6e-17 (criterion: P6 only, each at most 1e-15) |
| E0c: unfiltered architectures' `h` unchanged under M1; M1 schedules tuned with M1's A-fixed `h` | both true |
| E0d: P6 identical in M0, M1, M2 | true for M1 and M2 |
| all 14 primary verdict keys present | true |

## 2. Predictions

| prediction (stated before the run) | result | holds |
|---|---|---|
| E2: M1's re-tuned A-fixed `h` below 3.334 | 2.317 | yes |
| E3: under M2, A-fixed's S false alarms per tracked person-month below 0.151 | 0.072 | yes |
| E4 (primary): under M1, none of the 14 primary verdicts changes | 0 changes; no component boolean changes either | yes |
| E5: P8 holds under M1 | gap 15.7 [13.3, 18.2] points (threshold 10); RMST gap 6.78 [6.01, 7.55] days (threshold 3) | yes |

Under M1, the re-tuned `h` is 1.978 for minus-i, 2.507 for minus-iii, and 2.317 for minus-iv and minus-v.

**Not predicted.** Under M2, 5 of the 14 primary verdicts change, and their G2 (pooled) and G3 alternatives
change with them:
- P1 VA, DE and BI go from PASS to FAIL;
- P1 SP goes from FAIL to PASS;
- P8 goes from PASS to FAIL.

By the reading rule, these are an operating-point effect, not a dependence of the conclusion. With the frozen
`h`, A-fixed's S false-alarm rate is 0.072 per tracked person-month, against 0.151 as run. Any reuse of the
frozen `h` outside the frozen code path would need re-tuning.

## 3. Primary statistics, M0 against M1 (M2 for reference)

Each cell gives the point estimate with its 95% MC interval. Read the differences against the separate
intervals; no paired interval is computed (plan section 5). Thresholds are from PREREG section 6.

| statistic | threshold | M0 (as run) | M1 (matched, re-tuned) | M2 (matched, frozen `h`) |
|---|---|---|---|---|
| P1 SP naive/fixed FA ratio | at least 2 | 1.232 [1.128, 1.352] | 1.324 [1.217, 1.449] | 2.727 [2.382, 3.159] |
| P1 VA ratio | 0.5 to 2 | 1.033 [0.921, 1.159] | 1.018 [0.906, 1.133] | 2.243 [1.943, 2.621] |
| P1 DE ratio | 0.5 to 2 | 1.000 [0.888, 1.140] | 1.026 [0.898, 1.179] | 2.330 [1.959, 2.864] |
| P1 BI ratio | 0.5 to 2 | 0.800 [0.723, 0.874] | 0.868 [0.778, 0.968] | 1.874 [1.633, 2.165] |
| P1b DE/S FA ratio | at most 1.5 | 0.604 [0.500, 0.733] | 0.594 [0.488, 0.723] | 0.551 [0.409, 0.733] |
| P2 A-fixed minus A-naive DR sensitivity (targeted help) | at least 0.10, half from (i) | 0.092 [0.067, 0.119] | 0.057 [0.035, 0.081] | -0.004 [-0.025, 0.017] |
| P3 AV2/S FA ratio | at least 2 | 1.748 [1.503, 2.034] | 1.523 [1.288, 1.793] | 1.704 [1.351, 2.172] |
| P4 triggered correlation deflation | at least 0.05 | 0.104 [0.076, 0.133] | 0.120 [0.087, 0.154] | 0.088 [0.052, 0.124] |
| P4 triggered slope attenuation | at least 0.10 | 0.248 [0.185, 0.313] | 0.267 [0.191, 0.341] | 0.226 [0.144, 0.305] |
| P4 mixed IPW slope minus all-days | within 0.03 | -0.055 [-0.124, 0.018] | -0.034 [-0.111, 0.045] | -0.054 [-0.136, 0.031] |
| P4 mixed IPW correlation minus all-days | within 0.03 | -0.014 [-0.048, 0.020] | 0.001 [-0.034, 0.035] | -0.005 [-0.041, 0.030] |
| P5 `m1_05` random relative bias | under 0.05 | -0.008 [-0.057, 0.039] | -0.008 [-0.057, 0.039] | -0.008 [-0.057, 0.039] |
| P5 added bias at `m1_15`, fixed / random / triggered / mixed | at least 0.10 each | lower bounds 0.069 / 0.070 / 0.061 / 0.053 | lower bounds 0.071 / 0.070 / 0.088 / 0.114 | not shown |
| P7 DR minus DV, points | at least 15 | 11.0 [8.0, 14.1] | 9.6 [6.6, 12.4] | 7.1 [4.7, 9.4] |
| P8 A-fixed minus probe-only, points | at least 10 | 17.8 [15.2, 20.4] | 15.7 [13.3, 18.2] | 9.5 [7.5, 11.6] |
| P9 BD sensitivity minus half DR | at most 0 | 0.174 [0.144, 0.203] | 0.142 [0.114, 0.172] | 0.071 [0.048, 0.095] |
| P10 CS/S FA ratio | at least 1.5 | 1.713 [1.479, 1.993] | 1.475 [1.258, 1.740] | 1.570 [1.242, 2.001] |
| A-fixed DR 21-day sensitivity (P7/P8/P9) | none | 0.197 | 0.176 | 0.114 |

The P5 `m1_05` component, which the plan named as a possible flip, still misses by 0.007 under M1.

## 4. Reading

1. **The frozen P1 to P10 verdicts are robust to the baseline choice in spec 001 section 18.1, in this
   analysis.** Under the preregistered tuning procedure with a matched baseline, all 14 primary verdicts and
   every component boolean are unchanged. This is one seed set and one alternative to one unstated choice.
2. **Not predicted: the point estimates of detection are lower under M1, but the drop is not established.**
   - DR sensitivity is 0.176 under M1, against 0.197 as run.
   - P7's gap is 9.6 against 11.0, P8's 15.7 against 17.8, and P9's margin 0.142 against 0.174, so P9
     moves toward its threshold and still fails.
   - The separate intervals overlap, and no paired interval was computed.
   - The as-run baseline therefore did not lower the frozen run's detection at its tuned rate, by point
     estimate. Which feature of the mismatch is responsible is not tested.
3. **Not predicted: P10 moved away from the possible flip that E4 named.** E4 expected P10 might flip to
   PASS. Instead the point estimate fell below 1.5 (1.475), and P10 is a FAIL in both.
4. **Not predicted: P2's gap is 0.057 under M1, against 0.092 as run.** This includes the generated help
   changing (plan section 4). P2 fails in both.
5. **Not predicted: M1's schedules.**
   - Re-tuned under the matched baseline, the mixed schedule reaches its cap, `p_trig2 = 1.0`, at a
     realized budget of 2.76 probes per person-month against the 3.0 target.
   - The triggered schedule was already short of target as run, at 2.26, and realizes 1.62 under M1.
   - M1's P4 and P5 rows for these schedules are therefore at a lower budget than M0's. No P4 or P5
     verdict changed.

## 5. What this does not settle

- Whether this analysis enters the paper record, and how paper v4's successor discloses section 18.1. That
  is Abhay's call (spec 001 18.3 point 3).
- A pooled or minimum-day baseline (18.3 point 2) was not run.
- Whether the lower detection point estimates under M1 are real, and if so, why. A paired interval
  would need `score()`'s statistics re-implemented outside the frozen code.
