# sim/SENS-BASELINE-PLAN.md: matched-baseline sensitivity analysis of the frozen P1 to P10 (EXPLORATORY)

Status: EXPLORATORY, post-freeze, synthetic. It is not part of `sim/PREREG.md` and is not a re-scoring. The
frozen verdicts in `sim/results.json` (run 2, commit `6c17e0c`) stand as the confirmatory record. This plan
is hashed and committed before the evaluation run. Whether its result enters the paper record, and how the
next paper version discloses spec 001 section 18.1, are Abhay's decisions (spec 001 18.3 point 3); this
analysis only supplies the numbers.

## 1. Question

Spec 001 section 18.1: A-fixed fits the per-person mean and SD of indicators 4 and 5 on the unfiltered `X`,
and component (ii) scores them on `X_filtered`. PREREG's wording for (ii) does not say which series the
baseline uses. Do the frozen P1 to P10 verdicts depend on that choice?

## 2. Variants

All three run the frozen `score()` (`drift_sim.py` at `2272fec`, unchanged since `9fea182`) on the frozen
evaluation seeds (`eval_seed`, PREREG sha256 `60db6dd1...8f17`), with `B = 2000` and the frozen decision rule.

| variant | baseline of 4 and 5 under (ii) | `h` and schedules |
|---|---|---|
| M0 | as run (unfiltered `X`) | frozen `sim/tuning.json` |
| M1 (primary) | matched: fit on `X_filtered` | re-tuned by the frozen procedure (`tune_h` for every architecture, `tune_schedules`) on the tuning seed 20260927 under the matched baseline |
| M2 | matched | frozen |

- **Mechanism.** One wrapper around `compute_composite` (`sens_baseline.matched_cc`). When the authorship
  filter is on and a per-person baseline is passed, it replaces that baseline's mean and SD for indicators 4
  and 5 with ones fit by `fit_baseline` on `X_filtered`, on the same days. Nothing else changes.
- **Reach.** The wrapper sits at the single function every A-fixed composite goes through. It therefore also
  reaches the targeted-help feedback composite inside `generate_panel`, so in the targeted cells (P2) the
  generated help, and with it `X`, differs under M1 and M2. That is intended: the matched system would
  generate its own help.
- **Unaffected by construction.** Architectures with the filter off (`pop`, `A-naive`, `A-fixed-minus-ii`)
  and `probe-only` are unchanged. Their `h` must come out identical under M1's re-tune.
- **M1 is the primary variant.** It is what the preregistered procedure would have produced had the baseline
  matched: the frozen tuning procedure sets the operating point. M2 shows what the mismatch did to the
  operating point alone.
- **Outputs.** `score()`'s own writes go to a temporary directory; `sim/results.json`, `sim/RESULTS.md` and
  `sim/tuning.json` are never written. Output: `sim/sens_baseline.json`.

## 3. Construction checks (E0); any failure stops the reading

- E0a. Re-running the frozen tuning procedure with the as-run composite reproduces every `h` in
  `sim/tuning.json` and the schedule values `p_trig`, `p_trig2`, `c_star`. Both maximum absolute
  differences are reported. Above `1e-6` the M1 re-tune is not comparable, and this is reported instead of M1.
- E0b. M0 against the committed `sim/results.json`. Predicted outcome: not byte-identical.
  `sim/POSTFREEZE-DEVIATIONS.md` section 8 records that `score` at any commit after `33f9912` changes 9
  P6 `se`/`lo`/`hi` fields by at most 5.6e-17, through a change in floating-point operation order. The
  current `drift_sim.py` (unchanged since `9fea182`) is such a commit. The criterion is that M0 differs from
  the committed predictions only in P6 fields, each by at most `1e-15`. Every differing path and its
  absolute difference is stored (`E0b_M0_minus_committed`). M1 and M2 are compared against M0.
- E0c. M1's re-tuned `h` for `pop`, `A-naive`, `A-fixed-minus-ii` and `probe-only` equal E0a's, and M1's
  schedules were tuned with M1's own A-fixed `h` (`h_fixed_used`).
- E0d. P6 is identical in M0, M1 and M2. P6 uses constant-help panels and single indicators, never the
  composite. This is true by construction and is a check, not a prediction.
- `--check` (run before hashing) asserts that `matched_cc` equals attribution r4's `matched` rescoring,
  is identical when the filter is off and for `pop`, and leaves the caller's baseline untouched. It also
  asserts that it differs for A-fixed under default mixing.

## 4. Predictions (stated before the run)

The primary verdict set has 14 booleans: `P1.{SP,VA,DE,BI}.PASS` (the committed P1 has no top-level `PASS`)
and `P1b, P2, ..., P10 .PASS`. The script emits changes in this set as `E4_primary_changes_M1/M2`, and
every other boolean change as `component_changes_M1/M2`.

- **E2.** M1's re-tuned A-fixed `h` is below the frozen 3.334: the matched baseline removes the level
  offset (S mean +0.141 to +0.028 on r3's panels) and the inflated scale of z4 and z5.
- **E3.** Under M2, A-fixed's S false alarms per tracked person-month (P10's `fa_S`) fall below the as-run
  0.151, for the same reason.
- **E4 (primary).** Under M1, none of the 14 primary verdicts changes. Basis: on r3's panels the
  rate-matched DR sensitivity moved from 0.181 to 0.162 (spec 001 18.3), and the frozen margins are wide
  except in these places:
  - P10: ratio 1.713, interval [1.479, 1.993] against 1.5, fails narrowly. It could flip to PASS.
  - P1 SP: 1.232 [1.128, 1.352] against at least 2x, so a flip needs a large move. P1 VA/DE/BI pass
    inside 0.5x to 2x, with the closest bound at BI's 0.723.
  - P8: gap 17.8 [15.2, 20.4] points against 10. A flip needs a drop of more than 5.2 points.
  - A component, not a primary verdict: `P5.m1_05_random_under_5pct` is -0.0078 [-0.0566, 0.0388]
    against ±0.05, and misses by 0.007, so it could flip. P5's top-level verdict is pinned by
    `added_bias` (lower bounds 0.053 to 0.070 against 0.10).
  - P2 is scored in `targeted_theta1_05`. Under M1 and M2 there the generated help, and with it the data,
    changes as well as the composite (section 2). A P2 change is read as the matched system's whole effect,
    not the composite's alone.
- **E5.** P8 holds under M1 (a narrower reading of E4, named because P8 is one of the two frozen PASSes).

## 5. Reading rule

- Every boolean in each prediction is compared against M0, including the G2/G3/P4 ambiguity alternatives.
  A change in a primary verdict under M1 means the frozen conclusion depends on the baseline choice. No
  change means the verdict is robust to it in this analysis. In neither case is any verdict re-scored.
- Changes under M2 alone are read as an operating-point effect (frozen `h` off its target), not as a
  dependence of the conclusion.
- Shifts in the primary statistics are reported as M0 and M1 points with their intervals.
  - A paired M1-minus-M0 interval is feasible. `mc_stat` uses `seed=0` with the same person counts, and
    outside `targeted_theta1_05` the panels are identical, so the bootstrap draws are shared.
  - It is not planned, because it would mean re-implementing `score()`'s statistics outside the frozen
    code. Reading differences against the separate intervals is conservative.
- Single evaluation seed set. No replication set is planned: the question is about the frozen run itself.

## 6. Limits

- This is one alternative to one choice. The other unstated choices that `drift_sim.py` flags as `CHOICE:`
  are not varied.
- The matched baseline is the reading taken in spec 001 18.3 point 1. It is not the only possible fix: a
  pooled or minimum-day baseline (18.3 point 2) is not run.
- Nothing here changes paper v4, `sim/PREREG.md`, `sim/POSTFREEZE-DEVIATIONS.md` or any frozen result.
