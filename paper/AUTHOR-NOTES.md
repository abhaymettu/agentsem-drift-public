# Author notes for paper/DRAFT.md (v3)

Kept out of the manuscript on purpose: provenance, local paths, verification status of references, the
referee-response map, and open items. v0 `a497ae3`, v1 `d0db495`, v2 `3fb50cd`; v3 is uncommitted.

## 1. Provenance

| what | where |
|---|---|
| frozen pre-scoring document | `sim/PREREG.md`, commit `3c11e4f` (2026-09-27 21:21:40 CDT), sha256 `60db6dd195942387e5572a640224c4cb13836f29c37c1b611b14c70598678f17`; unchanged since the freeze (`git diff 3c11e4f HEAD -- sim/PREREG.md` empty) |
| run 1 (superseded) | `sim/superseded-run1/results.json`, `RESULTS.md` |
| run 2 code | commit `5bc2310` (22:04:20 CDT); fixes listed in `sim/POSTFREEZE-DEVIATIONS.md` items 1 to 6 |
| run 2 results | `sim/results.json`, `sim/RESULTS.md`, commit `6c17e0c` (22:05:55 CDT) |
| reporting-only metrics | `sim/metrics.json`, `sim/METRICS.md` (POSTFREEZE item 7; commit `33f9912`, items a to q) |
| tuned values | `sim/tuning.json` (`h.probe-only` 22.949 after re-tune; run 1 value under `h.probe_only_h_run1`) |
| scoring-code audit | `~/lanes/bridge-jobs/agentsem-overnight-20260927/score-fidelity-audit.md` (run by an Opus agent in the same lane) |
| referee review | `~/lanes/bridge-jobs/agentsem-overnight-20260927/paper-referee-review.md` |
| spec, including section 10 (21:28 CDT reframing) | `specs/001-drift-layer/spec.md`; section 10 was committed in `5bc2310`, not in the freeze |
| corpus audit | `pilot/trace_audit.py`, `pilot/results.json`, `pilot/RESULTS.md`, `pilot/INVENTORY.md`, `pilot/indicator4_params.json`; snapshot `--until 2026-09-28T01:32:31Z` |
| retention setting | `~/.claude/settings.json`, `cleanupPeriodDays: 45` |
| program studies cited as Mettu (2026b) | Study 1a `~/code/agentsem-trap-world` commit `21ec751` (`MORNING-HANDOFF.md`); Study 2 S1 `~/code/agentsem-study2-integration` commit `41d6774`; Study 5 `~/code/agentsem-study5-feasibility` commit `3dfe3c2` (`FALSIFICATION-PLAN.md`) |
| Mettu (2026a) | `~/code/ghost-respondents/paper/GHOST-RESPONDENTS-DRAFT.md`, section 2.2 (E5, E7) |
| exploratory robustness grid | plan `sim/ROBUSTNESS-PLAN.md`, sha256 `e1dbc8b74be6b3067e9433b76a1d1b24b01b705994b6a248771ad65f11836606`, committed in `3fb50cd` (2026-09-27 23:43:25 CDT); results `sim/robustness.json`, `sim/ROBUSTNESS.md`; two cells (`default`, `m1_15`) computed before the commit for a refactor check, disclosed as `sim/POSTFREEZE-DEVIATIONS.md` item 9 |
| figures | `paper/figures.py` renders `paper/fig1` to `fig4` (.svg) from `sim/results.json`, `sim/metrics.json` and `pilot/results.json`. File numbers match figure numbers in the draft (renamed 2026-09-27) |
| citation verification files | `~/lanes/bridge-jobs/agentsem-overnight-20260927/paper-citations.md`, `prior-art-passive.md`, `lit-verify.md` |

### Where each number comes from

- Table 1 and section 3.9: `sim/results.json` (`predictions`). P5 totals at `m1 = 1.5`:
  `P5.rel_bias_by_m1_and_schedule.m1_15`. Trigger-timing alternative: `P4.trigger_timing_ambiguous_P4`.
- Section 3.8 and the indicator-5 validity, chance baselines and analytic attenuation in 3.9:
  `sim/metrics.json` (`a` curve; `b` abstention; `c` budgets; `d` PPV; `e` IQR; `f` median days; `h`
  chance baselines; `i` realized false flags; `j` reset cost; `k` current; `l` pop; `m` kappa cell; `n`
  indicator-5 validity; `o` analytic attenuation; `p` person-level validity; `q` current beside
  triggered, used for the P4 paragraph in 3.9).
- Section 3.10: `sim/robustness.json` (`cells.<cell>.S1`, `S2`, `S3_S4.by_architecture`, `S5`, `S6`;
  `summary`). S2 indicator-4 SE in the failing cells: 0.0817 (lam_low), 0.0555 (phi_D_high), 0.1794
  (rising_slope_10) against 0.0115 in the default, ratios 7.1, 4.8 and 15.6 ("5 to 16 times").
- Figure captions: Figure 3's -0.08 and 0.29 are `P6.pi_rises_with_D.ind5_att_mc_mean` and
  `ind5_att_formula_mean`; Figure 4's 73,955 is `pilot/results.json` aggregates.
- Section 3.3 thresholds, 3.4 schedule values: `sim/tuning.json`; `pi' = 0.365` and the SD 0.109 vs 0.174
  note: `sim/PREREG.md`.
- Section 4: only post-cutoff aggregates from `pilot/results.json` (`aggregates`: 73,955 user-role entries,
  the class counts, sessions, naive-vs-filtered statistics, `indicators_middle_series_contamination`,
  change points) and
  `pilot/indicator4_params.json` (main thread and `day_level_main_thread`). These are identical in the
  committed run and the working-tree re-run, and `trace_audit.py --until 2026-09-28T01:32:31Z` reproduces
  them from any later corpus state.
- Raw scan counts, kept here as provenance only (they depend on when the scan runs, because the live
  transcript store keeps growing, including from the analysis sessions themselves):

  | run | files found / opened | user-role entries parsed | assistant-role parsed | dropped by cutoff | promptSource / turnOrigin coverage |
  |---|---|---:|---:|---:|---|
  | committed (`HEAD`) | 2,281 / 2,280 | 75,145 | 125,875 | 1,190 | 3,397 (4.5%) / 1,609 (2.1%) |
  | working-tree re-run | 2,311 / 2,310 | 76,192 | 127,670 | 2,237 | 3,425 (4.5%) / 1,637 (2.1%) |

  Both runs: 0 parse errors, 0 unparseable timestamps, 326 lane-prompt files loaded.

### Numbers that do not come from sim/*.json or pilot/*.json

- Run 1's P8 intervals, 17.3 [14.7, 19.8] and 7.12 [6.34, 7.91]: the points are in
  `sim/superseded-run1/results.json` (17.3; 7.119), the intervals only in `score-fidelity-audit.md` (G1
  table).
- Commit timestamps (git log), the 21:28 time of spec section 10 (spec text), and the 45-day retention
  (`~/.claude/settings.json`).
- The "about 22 baseline-window answers" in section 3.6: `sim/POSTFREEZE-DEVIATIONS.md` item 6.

### Discrepancies noticed

- The coordinator's brief said every passive rule is 2 to 3.7 times its chance baseline. In
  `sim/metrics.json` the ablation without (ii) is 1.8 times (0.144 against 0.081). The draft says "the
  ablations are 1.8 to 3.1 times theirs".
- P5 share of bias removed: `sim/results.json` lower bound -0.23146 (reported -0.231);
  `POSTFREEZE-DEVIATIONS.md` item 4 says -23.2 percent.
- In `sim/metrics.json`, the person-level IQR interval for A-fixed-minus-ii is [0.075, 0.326], far wider
  than the others; not used in the draft.

## 2. Reference verification status

From the three citation files. The manuscript carries no status tags.

| reference | status |
|---|---|
| AERA, APA and NCME (2014); Messick (1995); Kane (2013); Borsboom et al. (2004) | verified |
| Curran and Bauer (2011); Hamaker et al. (2015); Bolger and Laurenceau (2013) | verified |
| Pearson (1903); Lawley (1944, volume year; 1943 may be the reading year) | verified |
| Thorndike (1949) | book verified; Case II and III labels confirmed only in secondary sources, so the draft attributes the labels to Sackett and Yang (2000) |
| Sackett and Yang (2000); Page (1954); Rubin (1976); Klasnja et al. (2015); Nahum-Shani et al. (2018) | verified |
| Begg and Greenes (1983) | abstract and secondary summaries only; JSTOR full text not read <!-- cite: --> |
| Lamp and MacKinnon (2024) | verified from PMC full text; page span 647-648 not reconciled with the publisher; the referee says it is a two-page abstract, so it is cited only alongside Sackett and Yang |
| Boruvka et al. (2018) | verified (arXiv full text; JASA details via PubMed) |
| Lathia et al. (2013) | verified, pages 183-192 |
| Zhou et al. (2002) | verified at the abstract page, with the corrected title |
| Tao et al. (2021) | verified |
| ALBA, MAQuA, Yun et al. (2024), Anthropic (2025), Shen and Han (2026) | verified |
| Tieleman et al. (2026), arXiv 2606.17973 | verified (never "Slingshot" or "Ash") |
| Eichstaedt et al. (2018); GLOBEM (Xu et al., 2023); OpenAI and MIT Media Lab (2025); Helmich et al. (2023) | verified through search or fetch summaries, not full reads |
| Horiuchi (2026) | abstract only |
| FDA (2026) General Wellness guidance | verified |
| Mettu (2026a, 2026b) | own unpublished work; not retrievable until deposited |

Added in v3, all verified in `paper-citations.md` ("Ergodicity and person-level generalization (round
2)"): Molenaar (2004); Fisher, Medaglia and Jeronimus (2018); Adolf and Fried (2019), a PNAS letter;
Hamaker (2025, Annual Review of Clinical Psychology); Hamaker's chapter in Mehl and Conner's handbook,
cited as 2012 (the year used in most citations and in APA PsycNet), while Guilford's page lists the book
as 2011 hardcover and 2013 paperback. Its pages (43 to 61) come only from a secondary source, so the
reference gives none.

Not cited because unverified: Mohr, Zhang and Schueller (2017) on personal sensing; the
intensive-longitudinal invariance literature; Qian et al. (2021) (partly verified only).

## 3. Referee responses

Required revisions:

| item | status | note |
|---|---|---|
| 1 non-response attribution | addressed | abstract and 3.9 report the added bias (12 to 16 percent) and the four totals with intervals; triggered total said to include the 24.8 percent selection |
| 2 trigger timing | addressed | 2.5 says the as-run trigger uses S_t; abstract, Table 1 and 3.9 give both readings and the +0.067 overshoot; 3.6 justifies keeping S_t as primary (fixed before scoring, switching after would be post hoc) and gives S_{t-1} equal weight |
| 3 pilot parameters | addressed, option (b) plus the analytic values | "These are the values..." deleted; entry-level use stated; day-level analytic attenuation reported (0.235 vs 0.527); machine text identified as injection plus automated prompts; rising-share cell labelled hypothetical. No re-run |
| 4 chance baselines and P8 | addressed | chance baselines, realized false flags and person-level IQR reported; P8 described as a win over a nearly blind comparator. The referee's Poisson figure (0.11) is not used |
| 5 missing frozen metrics | addressed | all reported in 3.8 except the reset cost, which is not computable from the frozen panels (stated) |
| 6 precision column | addressed | Table 1 "precision" column; abstract states the frozen design could not show weighted recovery |
| 7 overreach | addressed | list of what appeared and what did not; "not fixable" reworded; indicator-5 validity with interval, labelled non-frozen and dependent on invented values |
| 8 run disclosure | addressed | audit described as run by an AI agent in the same project; AI-use statement; run 1 P8 beside run 2; timestamps; section 10 reframing disclosed |
| 9 Kane structure | addressed | section 2 recast as scoring, generalization, extrapolation, backing and use, with a mapping column to the earlier links |
| 10 missing inferences | done | person-level validity distribution in 3.8 (metrics item p); ergodicity and person-level citations added in v3 (2.3, 3.8) |
| 11 Borsboom sentence | addressed | rewritten in 2.2 as the referee proposed |
| 12 construct and direction | addressed | 2.1 |
| 13 one primary link per threat | addressed | context and usage missingness placed under extrapolation, with a cross-reference to generalization |
| 14 structure vs magnitude | done | v3 adds the exploratory one-at-a-time grid (3.10), committed and hashed before the run; conditions updated in 3.9 |
| 15 corpus scope | addressed | title changed from "everyday agent conversations" to "agent conversation traces"; abstract and 4.1 scope the corpus to one heavy-automation user's coding-agent transcripts; "existence proof and measurement protocol" wording used |
| 16 middle series | done in v2 | naive, middle and typed correlations in 4.2 (contamination quantities only) |
| 17 journal form | partly | ethics placeholder added in v2; cite comments kept for claims_lint and stripped at export (section 4); DOI deposit and external timestamp are author actions (section 5) |
| 18 duplicate screening sentence | addressed | |

Suggested revisions addressed: 1, 4, 5 (conjunctive chain), 6, 7 (Sackett and Yang for case labels), and
the Bernoulli explanation from 9. The rest are open items below.

### Round 2 (v1 review)

| item | status in v2 |
|---|---|
| N1 current vs triggered | done: `current` (slope 0.694 [0.588, 0.802], attenuation 25.4 [14.1, 36.7], correlation deflation 0.281) beside triggered in the abstract and 3.9; history attribution for 24.8 percent withdrawn; 2.5 rewritten; 16.1 percent caveated; novelty now "a known selection result shown in the agent-probing setting". The homogeneous-isolate run of `triggered` (optional) not done |
| item 4 matching premise | done: per tracked 0.179 vs 0.151, per total 0.014 vs 0.121 |
| N2 | done: 0.138 |
| N3 | done: "indistinguishable from chance" |
| N4 | done: "is expected from" |
| N5 / item 14 | done: stated conditions replace "any parameter values" |
| N6 | done: grid qualifier restored |
| N7 | done: chance rule's pre-onset exclusion and tracked-day definition stated |
| 10(c) | done (metrics item p) |
| 16 | done (middle series) |
| 17 | partly (ethics placeholder; export command; outward actions listed) |
| ponytail cuts | done: P8 one sentence; duplicate G3 P8 mention, P5 repeat and P4 novelty duplicates removed; scan-count mechanism and deferred restatements removed here |
| length | body 8,000 words, excluding Appendix A and references (8,207 with the appendix) |

## 4. Submission export

The `<!-- cite: -->` comments stay in DRAFT.md because `scripts/claims_lint.sh` exempts those lines.
Strip them for submission with:

    sed 's/ *<!-- cite: -->//' paper/DRAFT.md > paper/SUBMISSION.md

## 5. Outward-facing actions (author only)

1. Deposit the repository, the frozen document (`sim/PREREG.md`), both scoring runs and the
   reporting-only metrics with a DOI (OSF or Zenodo), which also gives the external timestamp a local
   commit cannot.
2. Make Mettu (2026a, 2026b) retrievable (deposit or preprint).
3. Confirm or replace the bracketed ethics sentence in Statements.

### Round 3 (coordinator, v3)

| item | status |
|---|---|
| robustness grid (item 14 / N5) | done: 3.10 "Exploratory robustness (not frozen)", plan hashed before the run, POSTFREEZE item 9 disclosed; S3, S5, S6 hold in every cell; S1 holds for `triggered` everywhere, fails for `current` in lam_low only; S2 direction holds on points in all 11 cells, indicator 4's interval crosses zero in three cells (precision); S4 surfaced probe-only below chance at `m1 = 1.5`, reported as unplanned |
| figures | done: four figures referenced at first use, with method-language captions |
| ergodicity citations (item 10) | done |

Deferred: only the optional N1 check (`triggered` on the previous day's statistic in the homogeneous
isolate), which needs a new run.

## 6. Open items for the author

1. Affiliation, corresponding address, acknowledgements, and a conflicts statement.
2. AI-use statement: add what the author personally checked, if the venue asks for it.
3. Optional, not required by the referees and not done: the IPW checks from round-1 suggestion 3, the
   G3-reading curve, and a check of the P9 candidate explanation.
4. P1b's lower bound is exactly 0.500; check whether it is a bootstrap quantile or a floor.
5. Begg and Greenes (1983) full text; the unverified list is in section 4.
6. Venue word limit (Advances in Methods and Practices in Psychological Science) against the body
   (about 8,320 words excluding Appendix A and references).
8. Retention: whether to raise `cleanupPeriodDays` above 45.
9. The spec's pasted-draft check says "earlier assistant message"; the code checks the last five turns.
