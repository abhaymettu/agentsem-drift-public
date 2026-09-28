# sim/POSTFREEZE-DEVIATIONS.md -- run 2 code changes, against the score-fidelity audit

Frozen at commit `3c11e4f` (`sim/PREREG.md` sha256 `60db6dd195942387e5572a640224c4cb13836f29c37c1b611b14c70598678f17`).
Audit: `~/lanes/bridge-jobs/agentsem-overnight-20260927/score-fidelity-audit.md`. Every change below
is a code fix in `sim/drift_sim.py` (plus one `sim/tuning.json` splice for the P8 re-tune); nothing
in `sim/PREREG.md` or `specs/` was touched, and `score()` was not run against the evaluation seed in
this repo -- only in a scratch copy, to compare against the audit's own faithful re-implementation
(`audit.py`, `p8fix.py`, `audit_out.json`). Per section 6, "nothing is re-tuned after scoring"; run 1
already produced `sim/results.json` (kept, superseded) before any of these fixes existed, so nothing
here re-tunes anything *after* a scoring run -- the one re-tune (item 6 below) reruns the frozen
tuning procedure on corrected pre-scoring code, on the tuning seed, exactly as PREREG's own
pre-freeze deviation 5 already did once for the same architecture.

## 1. G1 -- decision rule (every prediction)

- **Audit row:** G1 (cross-cutting; every P1-P10 row).
- **Frozen PREREG text (section 6):** "Each prediction holds if its 95% Monte Carlo interval lies
  beyond the stated threshold in the default cell... A 'within X' prediction holds if its 95% MC
  interval lies inside +-X." Section 3: "the Monte Carlo SE is reported beside every number" and
  "differences use a paired person bootstrap."
- **Run 1:** only P1 computed an interval at all, and P1 itself decided PASS/FAIL on the bootstrap
  *mean*, not the interval (`mean >= lo_thr`). Every other prediction (P1b-P10) decided on a bare
  point estimate. No MC SE was reported anywhere except P1's own interval.
- **Run 2:** a new `mc_stat(fn, ns, B=2000, seed=0)` computes, for every reported number, the point
  estimate (evaluated on the identity index, not the bootstrap mean), the 95% interval from a
  2000-draw person bootstrap, and an `se` (the bootstrap SD -- the section-3 "SD across persons over
  sqrt(N)" convention, with N the actual person count rather than the stale 200 the text carries
  over from spec v2; a bootstrap SD approximates this directly for these statistics, per the
  audit's own note that the two track each other). `ns` lists one person-count per independent
  panel: a single-element list resamples one index and reuses it against every same-panel quantity
  (paired, e.g. A-naive vs A-fixed on the same panel); a multi-element list draws independent
  resamples per panel (e.g. DR vs DV, different families -- G4). `_verdict(stat, kind, thr)` then
  decides PASS only if the *whole* interval clears the threshold (`ge`/`le`/`within`/`range`). This
  can only turn a run-1 PASS into a FAIL (P6, P10), never the reverse, since a point estimate that
  already failed cannot pass under a stricter interval rule.

## 2. P1b -- false-alarm denominator

- **Audit row:** P1b (BUG).
- **Frozen PREREG text (section 6):** "A-fixed's DE false alarms per **total** person-month are no
  more than 1.5x its S rate."
- **Run 1:** divided by *tracked* person-months (`_fa_month_pp`, denominator = `reason==0` days /
  30), not total person-months.
- **Run 2:** the ratio is computed from total post-baseline alarm counts over total post-baseline
  person-months, `(T_DAYS - BASELINE_DAYS) / 30` per person -- the `N * total_months` factor cancels
  in the ratio, so the statistic reduces to `sum(alarms_DE) / sum(alarms_S)` over post-baseline days.
  `fa_DE_total_person_month` and `fa_S_total_person_month` are reported alongside the ratio. Result:
  ratio 0.604 [0.500, 0.733] -- PASS, matching the audit's faithful re-implementation exactly.

## 3. P4 -- probe window, response conditioning, IPW correlation, signed attenuation

- **Audit row:** P4 (BUG: analysis window; IPW correlation unweighted).
- **Frozen PREREG text (section 5/6):** "Calibration on probe days: person-centred... slope of Y on
  C and their correlation, against the all-days values." "Under mixed, IPW with the logged
  propensity recovers both [slope and correlation] within 0.03 of the all-days values." Section 4:
  every schedule except `none` "has a fixed baseline block of 4 probes (days 7, 14, 21, 28)."
- **Run 1:** the triggered/mixed probe masks (`obs_t`, `obs_m`) included the p=1 baseline block,
  while the all-days reference (`all_mask`) was post-baseline only -- no reading of the text makes
  the two windows the same quantity. The all-days reference also conditioned on `responded`, which
  the spec's "all-days" does not. The mixed-IPW correlation (`r_m_ipw`) was `np.corrcoef` on the
  weighted-centred-but-otherwise-unweighted concatenation, not a weighted correlation. The reported
  slope attenuation was `abs(b_all - b_t) / abs(b_all)`, which cannot distinguish attenuation from
  inflation.
- **Run 2:** `obs_t`/`obs_m` are restricted to `post_mask` (post-baseline only, matching the
  all-days reference's window); `all_mask` drops `& resp4`; the mixed-IPW correlation is computed
  with a proper weighted formula (`_pcorr_weighted`: `sum(w*cc*yy) / sqrt(sum(w*cc^2)*sum(w*yy^2))`,
  added as an option on `person_slope_corr` and used directly via the new `_pstats`/`_pslope`/
  `_pcorr_weighted` vectorized per-person sufficient-statistics helpers, which also make the
  2000-draw bootstrap tractable); the slope-attenuation figure is signed
  (`(b_all - b_t) / b_all`), not `abs`. Result (post-baseline window): corr deflation 0.104
  [0.076, 0.133], slope attenuation 24.8% [18.5, 31.3] -- both clear their thresholds (triggered
  half holds); mixed-IPW slope diff -0.055 [-0.124, 0.018] and corr diff -0.014 [-0.048, 0.020] --
  neither is inside +-0.03 at the lower bound, so **P4 still FAILs, now only on the IPW half**.
  These numbers match the audit's own faithful re-implementation (`audit_out.json`,
  `P4_faithful_readingA_postbaseline`) to within rounding.
- **AMBIGUOUS (reported, not adopted):** the trigger-timing question (`in_band` on S_t, as-run/
  primary, vs S_{t-1}, the alternative) is computed and reported under
  `preds["P4"]["trigger_timing_ambiguous_P4"]`; the verdict uses the primary (S_t) reading.

## 4. P5 -- reference conditioned on response; probe window

- **Audit row:** P5 (BUG: reference conditions on response; same window defect as P4).
- **Frozen PREREG text (section 6):** "the slope bias added over the same schedule at m1=0 is at
  least 10% relative"; relative bias is against the all-days slope, not the responders' slope.
- **Run 1:** `all5 = post5 & ~np.isnan(C5) & resp5` (and `all5b` likewise) computed the "true" slope
  on responders only. At m1=1.5, response depends on D, so this reference carries the very MNAR
  selection P5 exists to measure. Probe masks also included the baseline block (same defect as P4).
- **Run 2:** `all5`/`all5b` drop `& resp5`/`& resp5b`; the per-schedule `obs` masks are restricted
  to `post5` (post-baseline only). The response-propensity IPW's own propensity fit still uses every
  administered probe (baseline block included), since that model is estimating response propensity,
  not the reference slope -- only the final bias/slope comparison is window-restricted, matching the
  audit's own faithful re-implementation. Result (both fixes): `m1=0.5:random` signed relative bias
  -0.8% [-5.7, 3.9] (interval not inside +-5% -> fails the interval rule, though the point passes);
  added bias at m1=1.5 over m1=0, every schedule, point >=10% but every lower bound <10% (fails the
  interval rule); response-propensity IPW removes -10.7% [-23.2, -1.1] of the bias ("less than half"
  holds). Net: **P5 passes on points, fails under the frozen interval rule.** These numbers match
  the audit's `audit_out.json` (`P5_faithful_ref_all_days_readingA`) to within rounding.
- **AMBIGUOUS (reported, not adopted):** "lagged composites" (one lag, as-run/primary, vs several)
  and "it" (the total m1=1.5 bias, as-run/primary, vs the bias added over m1=0) are both computed
  and reported under `preds["P5"]["lagged_composites_ambiguous"]` and `preds["P5"]["it_ambiguous"]`.

## 5. P1 -- note string reports the ablation ratio

- **Audit row:** P1 ("The `note` string 'confirmed by A-fixed-minus-iii' is static text printed
  whatever the ablation shows (cosmetic, and misleading at 1.047)").
- **Frozen PREREG text (section 6):** "SP is confirmed by the ablation removing (iii)."
- **Run 1:** `note = "confirmed by A-fixed-minus-iii"` for every SP run, regardless of what the
  ablation ratio actually was.
- **Run 2:** SP's note is built from the computed ablation ratio itself:
  `f"ablation ratio (A-naive FA-month / A-fixed-minus-iii FA-month) = {ablation_ratio:.4f}"`. The
  ablation ratio is unchanged in value (still computed the same way, on tracked-months, per-person
  rates -- no BUG was found in how it is computed, only in how it was described); VA/DE/BI keep
  "no matching component" (an accurate description, not a claim tied to a computed number).
- **Reporting-only:** the P1 note now prints the ablation ratio (1.047) instead of the fixed string
  'confirmed by A-fixed-minus-iii', which was false; no verdict depends on it.

## 6. P8 -- probe-only z-scoring, and its re-tune disclosure

- **Audit row:** P8 (BUG: probe-only z-scoring).
- **Frozen PREREG text (section 4):** "a CUSUM on the probe answers alone (z-scored on the baseline
  block)"; the baseline block is "4 probes (days 7, 14, 21, 28)." PREREG's own pre-freeze deviation 5
  already re-tuned probe-only's `h` once, for a different reason (oracle vs actual `random`-schedule
  subsample), and states the fallback convention followed here: "Baseline-fit fallbacks: mean 0, SD
  1... for fewer than 2 or 3 observations."
- **Run 1:** `probe_only_C` z-scored on all responded `Y` over days 1-28 (`Yb = Y[:, :BASELINE_DAYS]`)
  -- about 22 answers the `random` schedule never actually administers pre-baseline, not the 4-probe
  baseline block the spec names.
- **Run 2:** `probe_only_C` now indexes exactly `PROBE_BASELINE_DAYS = [6, 13, 20, 27]` (days 7, 14,
  21, 28), with the documented fallback (mean 0 / SD 1 when fewer than 2 responded baseline probes).
  Because `probe_only_C` is the single shared implementation used by both `tune_h('probe-only', ...)`
  and `score()`'s P8 (so the two cannot drift apart, per PREREG's own stated convention), this
  changes what `h` needs to be tuned to. `tune_h('probe-only')` was re-run on the tuning seed
  (20260927), family S, target 1 false alarm per 6 tracked person-months, exactly as before but on
  the corrected code: `h` moved from 6.539074181460682 (run 1) to 22.948591090463605 (run 2),
  matching the audit's faithful re-implementation (22.949) bit-for-bit. **No other tuned value was
  touched**: `sim/tuning.json`'s `h.probe-only` now holds the re-tuned value; the run-1 value is kept
  under the new key `h.probe_only_h_run1` (with a `note` field explaining the supersession); every
  other architecture's `h`, and the `schedules` block (`p_trig`, `p_trig2`, `c_star`, realized
  budgets), are byte-identical to before, since none of them call `probe_only_C`. Result: probe-only
  DR sensitivity 0.019; sensitivity gap 17.8 points [15.2, 20.4] (>=10 holds); RMST gap 7.73 days
  [6.94, 8.49] (>=3 holds) -- **P8 PASSes**, matching the audit's faithful re-implementation and
  `p8fix.py`'s own printed output to within floating-point rounding.
  - **Re-tune disclosure (section 6: "nothing is re-tuned after scoring"):** this re-tune is not a
    re-tune *after* scoring. Run 1's `sim/results.json` (kept, superseded) already reflects a full
    scoring pass under the old, buggy `probe_only_C` and the old `h`; run 1's P8 was **also a PASS**
    (sensitivity gap and RMST gap both cleared their thresholds even with the unfixed z-scoring,
    since probe-only was already far weaker than A-fixed either way). The re-tune here repeats the
    *frozen tuning procedure* -- the same `tune_h` bisection, the same tuning seed, the same target
    -- on the *corrected* probe-only code, before adopting it into a fresh `score()` run (run 2). No
    evaluation-seed number from either run 1 or run 2 was used to pick or adjust `h`; `h` is picked
    purely from the tuning-seed panel, as PREREG's own tuned-values procedure requires.

## AMBIGUOUS items -- both readings computed and reported

For every AMBIGUOUS item the audit lists, `score()` now computes the as-run (primary) reading and
the audit's "more natural" alternative reading, and reports both (the alternative's own PASS/FAIL is
reported beside the primary's; only the primary reading gates each prediction's headline `PASS`):

| Item | Where in `results.json` | Primary (as-run) | Alternative (audit's "more natural") |
|---|---|---|---|
| G2, FA estimator | `preds["P1"][fam]["fa_estimator_ambiguous_G2"]`, `preds["P3"]["fa_estimator_ambiguous_G2"]` | mean of person-level FA rates (Reading 2) | pooled: total alarms / total tracked months (Reading 1) |
| G3, pre-onset alarms | `preds["P2"/"P7"/"P8"/"P9"]["pre_onset_alarm_ambiguous_G3"]` | pre-onset alarm excludes detection (Reading 1) | pre-onset alarm routed to FA tally only; still detected later (Reading 2) |
| P4 trigger timing | `preds["P4"]["trigger_timing_ambiguous_P4"]` | `in_band` on S_t | `in_band` on S_{t-1} |
| P5 "lagged composites" | `preds["P5"]["lagged_composites_ambiguous"]` | one lag (also marked more-natural/minimal) | lags 1-3 |
| P5 "it" | `preds["P5"]["it_ambiguous"]` | "it" = total m1=1.5 raw bias | "it" = bias added over m1=0 (more-natural) |
| P6 validity vs attenuation scale | `preds["P6"]["validity_vs_attenuation_scale_ambiguous"]` | attenuation-ratio scale (also more-natural) | validity scale: r(X,D) vs Att_formula * r(H,D) |

None of these alternative readings is adopted for any prediction's headline verdict; per the table
above, three of the six items happen to have the audit's more-natural reading equal to run 2's
primary/as-run reading already (P1b's ambiguity resolved outright by item 2's fix; P5's lagged-
composites and P6's validity-scale items), and the other three (G2, G3, P4 trigger timing) are
reported as genuine alternatives per the audit's instruction, without changing any PASS/FAIL.

## Verification

`python3 sim/drift_sim.py --check` reproduces the same 9 of 10 checks, with only `(c)` failing
(PREREG's documented pre-freeze deviation 1 -- the `current`-control drift-world slope moves 6.05%
relative against a 5% bound, unchanged by any of the above). In a scratch copy of this repo (not
this working tree), `score --prereg-sha 60db6dd1...8f17` reproduces point estimates and 95%
intervals matching the audit's own faithful re-implementation (`audit_out.json`, `p8fix.py`) to
within rounding/bootstrap-seed noise, for every prediction. Final verdicts: P1b and P8 PASS; P1, P2,
P3, P4, P5, P6, P7, P9, P10 FAIL -- identical to the audit's predicted "after BUG fixes + interval
rule" table, and no run-1 FAIL becomes a PASS.

## 7. `metrics` subcommand (reporting only, added after run-2)

- reporting-only addition: `metrics` subcommand outputs the PREREG section 5 metrics that score() omitted; no verdict depends on them; run after the run-2 results commit 6c17e0c.
