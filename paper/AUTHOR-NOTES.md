# Author notes for paper/DRAFT.md (v4.3)

Kept out of the manuscript on purpose: provenance, local paths, verification status of references, the
referee-response map, and open items. v0 `a497ae3`, v1 `d0db495`, v2 `3fb50cd`, v3 `e1f2c72` (voice pass `201f649`); v4 `4c46cb3`; v4.1 adds section 3.11 (matched-baseline sensitivity); v4.2 (uncommitted, 2026-10-07) adds sections 3.12
(spec 003 methods) and 3.13 (spec 003 results, Table 3) and a "3.13, H3" pointer in the section 2.7 table.
v4.3 (uncommitted, 2026-10-07) trims the body to the venue's suggested length and moves detail, verbatim, to
`paper/SUPPLEMENT.md`; section 10 below records what moved, what was cut, the counts and the renumbering.
Section, table and figure numbers elsewhere in these notes are v4.2's unless marked; section 10 maps them.

## 1. Provenance

| what | where |
|---|---|
| frozen pre-scoring document | `sim/PREREG.md`, commit `3c11e4f` (2026-09-27 21:21:40 CDT), sha256 `60db6dd195942387e5572a640224c4cb13836f29c37c1b611b14c70598678f17`; unchanged since the freeze (`git diff 3c11e4f HEAD sim/PREREG.md` is empty) |
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
| matched-baseline sensitivity (section 3.11) | plan `sim/SENS-BASELINE-PLAN.md`, sha256 `e9768ee5f8d9273b0c6f4c63de7ef478fdacebe73f4e0e5c888025d70013488c`, committed in `3fa1a03` (2026-10-03); results `sim/sens_baseline.json`, sha256 `7c18568e4b3e0a6d01ee90682ac40b62c5cf84a84de9dfd7c92374396934ab81`, `sim/SENS-BASELINE.md`, commit `24ddeb6`; byte-identical rerun. The level offset (+0.14 against +0.03) and scale factor (about 1.2) are from `~/audit/agentsem-next4-2026-10-03.md` section 1, attribution round-3 panels |
| spec 003 pre-registration | `sim/PREREG-003.md`, frozen at commit `57208bc` (2026-10-07 12:27:07 CDT), sha256 `06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79` |
| spec 003 evaluation | `sim/results_003.json`, sha256 `922cd808aa05602750d3e2908b9354f8ec91ddb2736b8381faa8fd56c0e8000c`, with `sim/RESULTS-003.md`, commit `52286ad` (2026-10-07 12:33:54 CDT); `n` 4000, seed 192815961 derived from the frozen file's sha256 |
| spec 003 post-evaluation amendment | `sim/POST-EVALUATION-003.md`, dated 2026-10-07, written after the evaluation, committed in `626ce6c`, section (g) repaired in `533aa14`, sha256 `7ad60923a2ef11d28324d6f6ddd46cae670efe5ae1f9d445968126027c7bbfda`; post hoc readings only, frozen verdicts unchanged (section 9) |
| spec 003 design text (section 3.12) | `specs/003-sustained-shift/spec.md` (r5) sections 3, 4, 7 and 8: shifts 1.0 and 1.5, ramp U[7, 21], probe days `a + L` to `a + 3L`, margin 0.5, oracle reference, families, L0, L1, L2; `sim/PREREG-003.md` sections 1, 2, 5 and 7: help-off, `T` 210, 28-day baseline, 4 baseline probes, `W` 14, N 4000, 1000 resamples, the `wait`/`all`/`stop` rules, and the choices disclosed as made after the design run |
| spec 003 pre-freeze review (sections 3.12, 3.13) | `~/lanes/opus-reviews/prereg003-20261007/REVIEW.md`, sha256 `35adb9077bbc4fdc2e117c3f8861cdb23619f30a4f1fc8911f47a37c010accd4`, outside the repo; timeline `~/lanes/anchor-research/evidence/prereg003-review-20261007/TIMELINE.md`, sha256 `859057ab...`. The paper cites both only through `sim/POST-EVALUATION-003.md` sections (a), (c), (d) and (h) |
| observer-step paragraph (section 3.13) | design stage, exploratory, not frozen: `sim/OBSERVER-STEP-DIGEST.md` sections 1 to 3; `sim/rep2_003.json` (REP2-003, 200 populations) and `sim/rep_003.json` (REP-003, same 200 seeds) |
| spec 003 candidate text | `~/lanes/anchor-research/drafts/paper-spec003-results-draft.md` (176 lines), inserted in v4.2 as section 3.13; its opening method sentences moved into 3.12, its "Table 2" renumbered Table 3 (2.7 already has a Table 2), its definitions block turned into Table 3's notes, and L1_did and the HYB-003 step glossed in the observer-step paragraph |
| ORCID (declarations block) | 0009-0001-2434-353X, the candidate from the Courier release source; public record checked 2026-10-07 14:44 CDT by the coordinator via `pub.orcid.org/v3.0/0009-0001-2434-353X/person`: given name Abhay, family name Mettu, name visibility public. Shown in the draft as "[ORCID 0009-0001-2434-353X, public record checked 2026-10-07; author to confirm use]" |
| corpus no-read claims (Disclosures, Ethics; section 4.1) | `pilot/trace_audit.py` cannot prove that no other person's content was read. `extract_text_and_chars` walks tool_result content inside `message.content` in memory to count characters (only the separate `toolUseResult` field is never read), and user-role text, which can hold pasted third-party material (0.30 percent of entries carry a paste marker), is read in memory to classify authorship. The Disclosures therefore keep "[owner to confirm: no other person's content was read]" and say tool-result content was walked only to count characters. Section 4.1's "Tool-result payloads are never read" was not changed and conflicts with the code (open item 16) |
| figures | `paper/figures.py` renders `paper/fig1` to `fig4` (.svg) from `sim/results.json`, `sim/metrics.json` and `pilot/results.json`. Since v4.3 file numbers no longer match figure numbers: `fig2` is Supplement Figure S1, `fig3` is main-text Figure 2 and `fig4` is main-text Figure 3 (file names unchanged; the SVGs carry no figure numbers). v4 edited text labels only (fig1 subtitle and footnote, fourth stage renamed "Use"; fig3 title and description); after re-running `figures.py`, every numeric token in all four SVGs is identical to `HEAD` (`201f649`) |
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
- Section 3.12: `n` 4000, `nboot` 1000, `T` 210, `onset` [70, 121) (U[70, 120]), `lags` {0.3: 3, 0.7: 9,
  0.9: 29}, `seed` 192815961, `prereg_sha256`: `sim/results_003.json` top level. Shifts 1.0 and 1.5, margin 0.5
  (`margin`), four baseline probes, PS-sub's indicators 1, 2 and 6, DR+PS within 5 days of onset, 14-day
  re-baseline: spec 003 sections 3, 4, 7 and 8 and PREREG-003 section 1. Freeze `57208bc` at 12:27 CDT:
  POST-EVALUATION-003 (a) and (h). Design values 1.421 and [1.175, 1.706], 1.629, 0.70 and 0.715, N 2000 to
  4000: PREREG-003 sections 1, 2, 3 and 7. Review at 10:44, not read by the freezing lane, blocking items not
  applied: POST-EVALUATION-003 (a). 1.629 (check seed 20261004, PS-sub L1/S at N 2000): PREREG-003 section 2.
  W 21 evaluated and not taken: PREREG-003 sections 1 and 7. Budget target 3.0 probes per tracked
  person-month: PREREG-003 section 5. Scored once, attested by the run log, not enforced by the scorer:
  RESULTS-003 "Deviations" and POST-EVALUATION-003 (a). Nine definition corrections, "non-refractory"
  retired: POST-EVALUATION-003 (f), items 1 to 9.
- Section 3.13, "Reported, not scored" (added after the 2026-10-07 science review, item B2): H2b 0.0475
  [0.0153, 0.0801], `verdicts.H2b`; its dropped 0.05 threshold, spec 003 section 11; H6 -0.0230 [-0.0335,
  -0.0118] and -0.0518 [-0.0643, -0.0395], `verdicts.H6.{DR-1.0,DR-1.5}` (RESULTS-003 "Reported, not
  scored"); L2 minus L1_step 0.2080 [0.1827, 0.2318], `verdicts.H4.L1_step`. The frozen-rule H3 pass rate
  0.148 at N 4000, and 0.002 for H3 holding on the interval at N 4000 (section 3.7 future-rule sentence): POST-EVALUATION-003 (d), REVIEW.md section 3.2 ("H3, all six, drafted").
- Section 3.13, Table 3 and the H2a, construction-check and H3 paragraphs: `sim/results_003.json`, block
  `verdicts` (printed in `sim/RESULTS-003.md`, "Verdicts"): `verdicts.H1a`, `H1b`, `H2a`, `H4`
  (`est`, `lo`, `hi`, `threshold`); `verdicts.H3.clauses.{L1_PS-sub, L1_PS-use, L2_PS-sub, L2_PS-use,
  L0_PS-sub, L0_PS-use}`, threshold 1.5, `verdicts.H3.holds` false; `verdicts.H5.clauses.M1` and
  `verdicts.H5.L0label` (0.0000); `verdicts.H3.L1_step.{PS-sub, PS-use}` (0.9344 [0.8570, 1.0218], 0.9273
  [0.8494, 1.0141]). Prose rounds the 4-decimal values to 3. H2a's design value 0.201: PREREG-003 section 2.
  Table 3's definitions and notes: POST-EVALUATION-003 (f) items 1 to 6 and 8; "at least two probes answered":
  spec 003 section 7.
- Section 3.13, post hoc H3 reading: interval verdicts and upper bounds 1.309 and 1.286, POST-EVALUATION-003
  (c); 1.585, the 16th percentile, 500 populations per N and 0.792, POST-EVALUATION-003 (c) and (d), from
  REVIEW.md sections 2.1 and 2.2 (synthetic, design-stage).
- Section 3.13, probe budget: `sim/results_003.json`, block `budget`; 2.401 [2.376, 2.425] and 3.318 [3.271,
  3.363], `budget.phi0.7_DR-1.5.{wait,all}.probes_per_tracked_month`; upper bounds 1.978 and 1.277,
  `budget.phi0.7_{DR-1.0,S}.wait.probes_per_tracked_month.hi`; 0.321 and 0.288,
  `budget.phi0.7_DR-1.5.{all,wait}.persons_confirmed_in_window`; 0.066 and 0.053,
  `budget.phi0.7_S.{all,wait}.confirmed_fa_per_tracked_month`; 0.260 and 0.160,
  `budget.phi0.9_DR-1.5.{all,wait}.persons_confirmed_in_window`; 3.699 [3.654, 3.740] and 1.798 [1.775,
  1.818], `budget.phi0.3_DR-1.5.{all,stop}.probes_per_tracked_month`. The difference 0.032 (0.0324, no
  paired interval): RESULTS-003 "Probe budget". Upper-bound reading and point/upper agreement:
  POST-EVALUATION-003 (e); `wait` semantics and 28 days at 0.7: (f) item 5.
- Section 3.13, observer-step paragraph: 200 populations and 227 to 309 in-window persons,
  `rep2_003.json` `R` and `per_population.n_inwin` (min 227, max 309); 0.004 (MCSE 0.002) and 0.219,
  `rep2_003.json` `summary.xcheck_L1_step_minus_L1_dd_rho{0.0,2.0}` (0.0041, mcse 0.0018; 0.2186); 0.041 and
  0.093 to 0.142, `rep_003.json` `summary.rho{0.0,0.5,1.0,2.0}_conc0.5_A-k0.5_h63.U_w1_p1.0.mean` (0.0411,
  0.0932, 0.1424 at rho 2); -0.148 to -0.047, same keys with `U_w2_p1.0` (-0.1479, -0.0466); 0.108 and
  0.154, `rep2_003.json` `summary.fact_L0_interaction_h21.{mean,design}`; -0.001, 0.071, 0.150, 0.273,
  `summary.load_L1_did_minus_L1_dd_rho{0.0,0.5,1.0,2.0}.mean`; 0.005 and 0.208,
  `summary.hyb_step3_dd_rho{0.0,2.0}.mean`. "About zero" at rho 0: digest section 2 (`design_side` 0.465 and
  0.51). Not carried over from the candidate draft: p*(2) and p*(4), and the ABSORB and UNLOG generator
  means.
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
- Sections 3.12 and 3.13: the review's Monte Carlo figures (about 1.585, the 16th percentile, 500 populations
  per N, 0.792, 0.148), which the H3 paragraph now attributes to REVIEW.md (sha256 `35adb907...`), exist only in REVIEW.md, outside the repo, and reach the paper through POST-EVALUATION-003 (c)
  and (d); the times 10:44 and 12:27 are the file and history times listed in its section (a).
- Section 3.12's design values (1.421, [1.175, 1.706], 1.629, 0.715) are design-stage numbers quoted in the
  frozen PREREG-003, from `sim/DESIGN-003.md`, `sim/DECIDE-003.md` and the check seed 20261004 run.

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
| Lamp and MacKinnon (2024) | verified from PMC full text; Crossref gives 59(3), 647-648, matching the draft (citations ledger 2026-10-07), so the page question is closed; the referee says it is a two-page abstract, so it is cited only alongside Sackett and Yang |
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

S34 to S36: `grep -c -E '\bS3[4-6]\b' paper/DRAFT.md` returned 0 on 2026-10-07, so the paper carries no S34,
S35 or S36 tag and no opaque tag claim; nothing was replaced. (Spec 003 section 13 still lists "the S34 to S36
sources" as open; they do not reach the paper.)

Metadata updated 2026-10-07 from `~/lanes/anchor-research/evidence/citations-20261007/ledger.md` (Crossref):
GLOBEM (Xu et al.) year 2022, not 2023, in the entry and the in-text citation (the venue string "IMWUT /
UbiComp 2023" was left as it was); Yun et al. now carry the IVA 2024 title ("...repeated interviews by a
virtual agent..."); Shen and Han gain the subtitle; Eichstaedt et al. 115(44), 11203-11208; Helmich et al.
*Clinical Psychological Science* 11(6), 994-1010 (the journal name was added with the volume). Nothing else in
the references changed.

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

The `<!-- cite: -->` comments stay in DRAFT.md, which is the lint source: `scripts/claims_lint.sh`
exempts those lines. The submission file is produced by this export, which strips them:

    sed 's/ *<!-- cite: -->//' paper/DRAFT.md > paper/SUBMISSION.md

SUBMISSION.md is a build product and is not committed.

## 5. Outward-facing actions (author only)

1. Deposit the repository, the frozen document (`sim/PREREG.md`), both scoring runs and the
   reporting-only metrics with a DOI (OSF or Zenodo), which also gives the external timestamp a local
   commit cannot.
2. Make Mettu (2026a, 2026b) retrievable (deposit or preprint).
3. Confirm or replace the bracketed ethics sentence, now in the Disclosures block before section 3.
4. Decide whether `DECISIONS.md` is deposited (on `eval/authorship-filter`, not `main`);
   if not, change the AI-use bracket's log reference to "the author's records".

### Round 3 (coordinator, v3)

| item | status |
|---|---|
| robustness grid (item 14 / N5) | done: 3.10 "Exploratory robustness (not frozen)", plan hashed before the run, POSTFREEZE item 9 disclosed; S3, S5, S6 hold in every cell; S1 holds for `triggered` everywhere, fails for `current` in lam_low only; S2 direction holds on points in all 11 cells, indicator 4's interval crosses zero in three cells (precision); S4 surfaced probe-only below chance at `m1 = 1.5`, reported as unplanned |
| figures | done: four figures referenced at first use, with method-language captions |
| ergodicity citations (item 10) | done |

### Round 4 (v3 review, v4)

| item | status |
|---|---|
| M1 (3.10 against its plan) | done: 3.10 opening paragraph and S2 bullet; 3.9 grid sentence |
| M2 (S4) | done: 3.10 S4 bullet. The referee's 43 percent figure is not used. |
| M3 (abstract, Thorndike) | done: abstract says the attenuation cannot be attributed to the trigger's history; 3.9 splits the sentence (Case II/III fits the correlation deflation, not the slope attenuation) |
| M4 | done: grid default uses re-tuned `h` 3.209 (robustness.json `cells.default.tuned_h.A-fixed.h`) against 3.334 (`sim/tuning.json`) and different seeds; triggered ratio 0.829 [0.770, 0.890]; not comparable with Table 1 |
| M5 (figures) | done: text labels only; see provenance row; caption clause names the two estimators (-0.08 mean per-person attenuation ratio, `P6.pi_rises_with_D.ind5_att_mc_mean`; -0.011 person-averaged within-person correlation, metrics item n) |
| item 17 | done in the draft: header "Manuscript draft v4"; export stated above. DOI and ethics confirmation remain author actions |
| ethics placeholder | done: "no other person's content was read (third-party traffic was counted only by tool name)", still bracketed |
| suggested | 4.2 table now two decimals throughout (1.00, 0.11, -0.02, 0.24, matching Figure 4). The fig2 y-axis ticks were not changed (label-only edits were allowed; ticks are computed) |

Deferred: only the optional N1 check (`triggered` on the previous day's statistic in the homogeneous
isolate), which needs a new run.

## 6. Open items for the author

1. Affiliation, corresponding address, acknowledgements, and a conflicts statement.
2. AI-use statement: add what the author personally checked, if the venue asks for it.
3. Optional, not required by the referees and not done: the IPW checks from round-1 suggestion 3, the
   G3-reading curve, and a check of the P9 candidate explanation.
4. P1b's lower bound is exactly 0.500; check whether it is a bootstrap quantile or a floor.
5. Begg and Greenes (1983) full text; the unverified list is in section 4.
6. Venue word limit (Advances in Methods and Practices in Psychological Science) against the body.
   Addressed in v4.3 under the owner's 17:02 CDT decision ("Trim it to be ideal"): body 5,373 words against
   the General Article guide of 3,000 to 5,000 (section 10); the excess is caveats kept beside their claims. The guide is not a hard limit.
7. Retention: whether to raise `cleanupPeriodDays` above 45.
8. The spec's pasted-draft check says "earlier assistant message"; the code checks the last five turns.
9. Whether section 3.11 stays in the submitted version (spec 001 section 18.3 point 3), and whether the word
   limit (item 6) absorbs its roughly 260 words. v4.3: it stays as the second paragraph of section 3.5 (about
   100 words, mismatch caveat and verdict kept); the full v4.2 text is Supplement S9. Inserted 2026-10-07 under the owner's delegation of the
   pending paper decisions.
10. H3 paragraph read and accepted 2026-10-07 under the owner's delegation; "[author wording]"
   marker removed. See DECISIONS.md, 19:54 entry. AI-use wording and deposit remain separate.
11. Word limit (items 6 and 9). Superseded by the v4.3 trim: by the section 10 script, the body (title
   through the declarations block, excluding the abstract, Appendix A and references) is 5,373 words after the
   science review fixes (4,991 before them), down from 10,305 for v4.2 by the same script; spec 003 is now
   sections 3.6 (279 words) and 3.7 (464), against
   464 and 1,538 in v4.2. The observer-step paragraph and Table 3 with its caption moved to Supplement S11.
   The earlier figures (11,424 after the AMPPS restructure, 11,084 before; v4 8,410, v4.1 8,690) came from a
   different count that also included the abstract and table punctuation, so they are not comparable.
12. The abstract, section 3.1 and the Data and code availability statement now carry the science review's
   minimal sentences for spec 003 (item B3). Confirm the wording, and whether `REVIEW.md` (outside the repository,
   cited by hash in 3.13, v4.3 section 3.7) should be deposited with the supplement.
13. Section 3.12 (v4.3: section 3.6) calls the reviewer "a separate AI agent" and the freezer "the freezing lane (the agent session
   that froze the file)"; confirm this description against the AI-use statement, which does not yet mention
   the spec 003 freeze or review. Status 2026-10-07: candidate added in DRAFT, see DECISIONS.md.
14. The manuscript header still reads "Manuscript draft v4, 2026-09-28"; it was not bumped for v4.1 or v4.2.
15. Declarations are DRAFT until the author confirms. The "Author contributions and conflicts" block is marked
   "[DRAFT declarations, pending the author's confirmation]": sole author, independent researcher, no external
   funding, no competing interests, the ORCID line, and the candidate AI line "Claude assisted with code
   development and manuscript preparation." beside placeholders for the model and version, purpose, what was
   checked and limits, which the venue asks for. None of these was asserted beyond what the coordinator supplied.
   AMPPS layout (submission guidelines as fetched by the coordinator, 2026-10-07): disclosures (preregistration
   distinction, data and materials links and why anything is unavailable, simulation reporting, ethics) sit in a
   "Disclosures" block before section 3; author contributions and conflicts sit after the body, before Appendix
   A. The former "Statements" section is gone; its AI-use paragraph moved into the declarations block and its
   ethics and data paragraphs into Disclosures, every bracketed placeholder kept. New placeholders: the corpus
   audit's preregistration status, the persistent link, and "[owner to confirm: no other person's content was
   read]". Items 1 and 2 above are partly answered by this block once confirmed. The candidate minimal line alone
   would contradict `sim/PREREG-003.md` section 8, where the freezing lane made the registered decision rules.
16. (reworded 2026-10-07 16:22 under the owner's 16:19 grant: 4.1 now says payloads are walked in memory only to count characters and are not stored or classified; the Disclosures state the parse does not establish whose words each payload contains.) Section 4.1 said "Tool-result payloads are never read", but `pilot/trace_audit.py` walks tool_result content in
   memory to count characters (provenance row "corpus no-read claims"). Reword 4.1 or confirm the intended
   meaning; not changed here.

## 9. Rationale for post-evaluation material (2026-10-07)

Numbered to match open item 9 of section 6, which it answers for section 3.11; it also sets the terms for any
spec 003 material. Everything named here is synthetic.

**Why section 3.11 stays.** It discloses an as-run choice found after scoring (the baseline series for
indicators 4 and 5) and reports a sensitivity analysis that was planned and hashed before it ran. Its claims stay
inside what that analysis supports, and the section says so in its own text:
- one seed set: the frozen evaluation seeds, re-scored;
- one alternative: the baseline fit on the filtered series (re-tuned, and with the frozen thresholds kept);
- no paired interval: the detection drop is reported as not established;
- frozen verdicts unchanged: none of the 14 primary verdicts in Table 1 changes, and the as-run baseline is
  called a disclosed choice, not a fix.
Dropping it would remove the disclosure of a known mismatch. The word-limit question (item 6) stays open.

**When a spec 003 subsection enters the paper.** Only if all of the following hold:
1. The frozen H3 verdict comes first: H3 FAILS under the frozen point rule, because PS-sub's L1 ratio,
   1.5756 [1.4205, 1.7489], is not below 1.5; the registered tally is one of two (H2a holds).
2. The interval reading comes second and is labelled post hoc: both L1 clauses are inconclusive (each interval
   crosses 1.5), L2 and L0 hold on both families, and the conjunction is inconclusive. Neither L1 point is
   called a pass.
3. The pre-freeze review is disclosed: it was complete at 10:44 CDT, before the 12:27 freeze, and the freezing
   lane did not read it. Its blocking objection to the point rule is stated.
4. The review's Monte Carlo is labelled synthetic and design-stage (500 populations per N), not confirmatory
   power and not evidence about the evaluation draw.
The candidate text is `~/lanes/anchor-research/drafts/paper-spec003-results-draft.md`, inserted in v4.2 as
section 3.13, with the methods in section 3.12 (provenance rows in section 1).

Full amendment: `sim/POST-EVALUATION-003.md` (provenance row in section 1).

## 10. v4.3 trim to the venue length (2026-10-07)

Owner decision, phone, 17:02 CDT, after seeing the length against AMPPS: "Trim it to be ideal". AMPPS General
Articles are guided at 3,000 to 5,000 words (`~/lanes/anchor-research/evidence/citations-20261007/ampps-requirements.md`).
No simulation was run and no frozen file was touched.

**Count method.** One script (`/tmp/count_paper.py`, kept for this session only): words are whitespace tokens
containing a letter or digit, after removing HTML comments, `---` rules and table separator rows; tables and
figure captions count. Body is the title through the declarations block, excluding the abstract, Appendix A
and references.

| part | v4.2 | v4.3 |
|---|---:|---:|
| body | 10,305 | 5,373 |
| abstract | 363 | 350 |
| references | 960 | 960 |
| Appendix A | 175 | 0 (Supplement S1) |
| total | 11,803 | 6,683 |
| supplement (new file, whole file) | | 6,940 |

Per section, v4.2 then v4.3: introduction 458 / 282; section 2 1,567 / 1,300 (2.1 238 / 184, 2.2 255 / 217,
2.3 183 / 167, 2.4 272 / 230, 2.5 294 / 223, 2.6 107 / 106, 2.7 214 / 169); Disclosures 408 / 368; section 3
5,975 / 2,213; section 4 999 / 595 (4.1 345 / 172, 4.2 520 / 325, 4.3 125 / 89); section 5 263 / 197;
section 6 305 / 88; section 7 157 / 157; declarations 141 / 141. Section 3 in v4.2: 3.1 143, 3.2 346, 3.3 233,
3.4 126, 3.5 128, 3.6 228, 3.7 584, 3.8 533, 3.9 927, 3.10 439, 3.11 279, 3.12 464, 3.13 1,538. In v4.3: 3.1 53,
3.2 298, 3.3 207, 3.4 717, 3.5 188, 3.6 279, 3.7 464.

**Renumbering.** Section 3 is now: 3.1 Status (v4.2 3.1); 3.2 Design (v4.2 3.2 to 3.4); 3.3 Decision rule and
scoring runs (3.5, 3.6); 3.4 Results (3.7 to 3.9); 3.5 Exploratory analyses (3.10, 3.11); 3.6 Spec 003 design
(3.12); 3.7 Spec 003 results (3.13). The section 2.7 table is now Table 1 (its "earlier link" column, the
referee-response mapping, was dropped and the backing column now names R1 to R9). v4.2 Table 1 is Table S1 and
Table 3 is Table S2. v4.2 Figure 2 is Figure S1; Figures 3 and 4 are now Figures 2 and 3. Appendix A is
Supplement S1.

**Moved to `paper/SUPPLEMENT.md` ("Supplementary material, private draft, 2026-10-07").** Each block is the
v4.2 text verbatim, with only cross-references updated to v4.3 numbering; the main text points to each one.
- S1: Appendix A (the attenuation derivation) and the residual-share sentence of 2.2.
- S2: 3.2 generator in full (equations, parameter values, families, cells).
- S3: 3.3 rules with ablations and tuned thresholds, 3.4 schedule parameters, 3.5 decision-rule detail.
- S4: 3.6 scoring runs and post-freeze fixes, including run 1's P8 numbers and the re-tune.
- S5: 3.7 with Table S1 (all eleven predictions, caption, precision glossary, notes).
- S6: 3.8 reporting-only metrics in full, with Figure S1.
- S7: 3.9 in full (P4 detail including the previous-day reading and weighted numbers, P5 totals, P6 entry versus
  day-level paragraph, P9 candidate explanation, mechanisms paragraph).
- S8: 3.10 robustness grid with its S1 to S6 expectation bullets (a note says these labels are not supplement
  sections).
- S9: 3.11 matched-baseline sensitivity in full.
- S10: 3.12 spec 003 design and freeze in full (probe spacing, probe rules, families, commit `57208bc`, every
  post-design choice).
- S11: from 3.13, Table S2 with its caption and notes, the reported-not-scored paragraph, the L1_step numbers,
  the probe-budget paragraph and the observer-step paragraph.
- S12: 4.1 in full, and from 4.2 the main-thread count paragraph, person-absent detail, time-split
  correlations, pastes and third parties, change-point detail and data density; 4.3's four bullets.
- S13: section 6's seven-item list and the combining paragraph.

**Cut from the main text, by kind.** Repeated statements (persons per cell, seeds and "local commit, not an
external registration" given in both Disclosures and section 3; the product disclaimer given three times);
glosses that restated Table S1, Table S2 or Figure 3 (audit); the introduction's roadmap paragraph and
"It is natural to ask" opener; definitions given twice (the filter's sensitivity and specificity, the residual
share, family lists); the referee-response scaffolding (Table 1's "earlier link" column); bullet lists that a
sentence carries (section 6, section 4.3); and literature detail that a citation string carries (2.5's
range-restriction sentence, the Anthropic counts, GLOBEM's user-years).

**Kept as required.** The frozen H3 FAIL first and the post hoc INCONCLUSIVE second with no point pass; the
"[author wording]" marker; the sentence that a pass on the point is weaker than a pass on the interval; the
review timing (complete at 10:44, before the freeze, not read by the freezing lane), the post-evaluation
amendment and `REVIEW.md` with its hash; the design-draw versus generator caveat; the A-fixed baseline
mismatch; the corpus parsing limitation in Ethics; n = 1 non-generalization; every bracketed placeholder and
the DRAFT declarations label; no S34 to S36 tags. The abstract dropped the generator-mechanism clause and the
weighted-recovery sentence (with its "1,000 persons"); every number it keeps is unchanged, and it now
labels the sensitivity figures as reporting-only and the sign change as a hypothetical cell.

**Not changed, noted.** `scripts/claims_lint.sh` fails on the Shen and Han reference title (two questionnaire names)
both before and after this edit; SUPPLEMENT.md passes. Bolger and Laurenceau (2013) was already uncited in v4.2.

**Science review applied (same day).** `~/lanes/anchor-research/reports/paper-v43-trim-science-review-20261007.md`,
verdict REVISE. B1: 3.3 now states the P8 re-tune (probe-only `h` 6.539 to 22.949, tuning seed only) and the
frozen sqrt(200) standard-error leftover. B2: 3.4 and 3.5 state that three of the six robustness expectations
failed their interval rule in named cells. B3: 3.4 restores the previous-day reading, 16.1 percent [10.0, 22.1],
with its equal weight, so S4's pointer holds. B4: 3.4 and the abstract label 0.197, 0.053, "3.7 times" and the
false-flag rates as frozen reporting-only metrics computed after scoring with no threshold, and give the high
tuning target. B5: the two S12 paragraphs that began mid-sentence (line ranges started one line late) now carry
their v4.2 openings. Non-blocking: re-attached the entry versus day-level mixing caveat (3.2, 4.2), "a property
of this window" (4.2), "keeping the frozen thresholds changes five verdicts" (3.5), "classed as typed" (4.2);
3.6's oracle reworded as H2a's comparator; "training period" defined in 4.2; Table 1 cites Table S1 for P1 to
P3, P10 and the use row's P2; 2.3 regains the varying indicator count and the link from per-person loadings
to section 3's pooled statistics; 2.4 regains "it also weakens generalization"; 2.5 regains the previous-day
history sentence and the full non-response qualifier; 2.6 regains "as in two of the simulation's cells";
Figures 1 and 3 are now called out. Not applied: N6's E1 to E6 relabelling (it would change the plan's labels)
and N8's orphan reference.

