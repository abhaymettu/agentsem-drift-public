# sim/POST-EVALUATION-003.md -- post-evaluation amendment to PREREG-003 (2026-10-07)

**SYNTHETIC ONLY.** Every number below comes from simulated persons carrying one invented, non-diagnostic state D.
No real person's data enters any run cited here, and nothing here is a clinical or diagnostic finding.

Post-evaluation amendment, dated 2026-10-07; frozen files untouched, see (g) and (h).

## (a) Status and timeline

Times are CDT on 2026-10-07, from file mtimes and git commit times
(`/Users/abhay/lanes/anchor-research/evidence/prereg003-review-20261007/TIMELINE.md`).

| time | event |
|---|---|
| 10:18 | Blocking design review of the PREREG-003 draft started (Opus review lane). |
| 10:44 | `REVIEW.md` written; 10:45 `READY.md`: verdict CHANGES-REQUIRED, "not ready to freeze". |
| 10:49 to 11:16 | Fixes lane: `fixes.patch` (11:12) and `RESULT.md` (11:16), preparation only, not adopted, H3 OWNER-PENDING. |
| 11:05 | Owner to the anchor-research lane: "Make all the decisions for me. Whatever would be ideal for the paper." |
| 12:24 | Owner: "commit them yourself". 12:24 to 12:27: commits `6dcead9`, `8d8508a`, `5fec5a4`, then `57208bc` (PREREG-003 frozen, N 4000). |
| 12:27:52 to 12:29:09 | `score` run; results committed in `52286ad` at 12:33. |
| 13:27 | Coordinator takeover: preserve the frozen artefacts and prepare this dated amendment. |

- The anchor-research lane did not read
  `REVIEW.md`, `READY.md`, `fixes.patch` or `RESULT.md` before freezing: they lived under
  `~/lanes/opus-reviews/`, were launched by the coordinator, and no lane prompt, `STATE.md` entry or ask-queue
  answer pointed to them.
- **What the review asked for and what was frozen differ.** The review's blocking items (REVIEW.md section 4)
  were not applied: H3 was frozen on the point rule, the plug-in projections were not relabelled, and the
  scorer guardrails were not added (the frozen `score` still accepts `--n`, does not compare the files with
  HEAD, does not refuse to overwrite `results_003.json`, and has no seed-collision assert). The review
  recommended keeping N 2000; the frozen file sets N 4000. RESULTS-003.md (Deviations) records that `score` ran
  once and that `results_003.json` stores `n` 4000; the frozen scorer could not itself enforce either.

## (b) Frozen verdict preserved

Under the frozen rule (PREREG-003 section 2), **H3 FAILS.** L1 on PS-sub has a point estimate of 1.5756, which is
not below 1.5 (interval [1.4205, 1.7489]). The other five clauses hold under the frozen rule. H2a holds, so the
registered tally stands at one of two. The four construction checks hold (RESULTS-003.md, Verdicts).

Nothing is rescored. No threshold moves, 1.5 included, and nothing is re-tuned. `results_003.json`
(`verdicts.H3.holds` false) remains the record of the evaluation, and the frozen verdict is reported first
wherever H3 is reported.

## (c) Post-evaluation three-way interval reading (post hoc)

**Label: post-evaluation amendment, adopted after the evaluation.** The rule is REVIEW.md section 2.2's
recommendation, written before the freeze (10:44) and not applied to the frozen file; it is adopted here as a
reading, after the results were seen. It does not replace the frozen verdict of section (b).

Rule (REVIEW.md section 2.2), applied to the stored 4-decimal values:
- L1 and L2 clauses hold if the 95% upper bound is below 1.5 and fail if the lower bound is at or above 1.5.
- L0 clauses hold if the lower bound is above 1.5 and fail if the upper bound is at or below 1.5.
- Any other clause is inconclusive. H3 holds if all six hold, fails if any fails, and is inconclusive otherwise.

| clause | est | lo | hi | frozen rule | frozen verdict | interval reading (post hoc) |
|---|---|---|---|---|---|---|
| L1 PS-sub | 1.5756 | 1.4205 | 1.7489 | point below 1.5 | fails | **INCONCLUSIVE** (interval crosses 1.5) |
| L1 PS-use | 1.4599 | 1.3211 | 1.6276 | point below 1.5 | holds | **INCONCLUSIVE** (interval crosses 1.5) |
| L2 PS-sub | 1.2110 | 1.1195 | 1.3090 | point below 1.5 | holds | HOLDS (upper bound below 1.5) |
| L2 PS-use | 1.1935 | 1.1035 | 1.2859 | point below 1.5 | holds | HOLDS |
| L0 PS-sub | 3.1239 | 2.9606 | 3.3025 | interval above 1.5 | holds | HOLDS (lower bound above 1.5) |
| L0 PS-use | 3.1286 | 2.9611 | 3.3126 | interval above 1.5 | holds | HOLDS |
| **H3, all six** | | | | all six hold | **FAILS** | **INCONCLUSIVE** (no clause fails; two are inconclusive) |

- Neither L1 point is read as a pass or a fail.
- **Why the review objected to the point rule (its blocking item).** Across 500 fresh synthetic populations at
  N 2000, the generator puts logged PS-sub L1/S at about 1.585 (MCSE 0.005), above 1.5, and PS-use at about 1.496
  (0.005). The design draw (1.421) sat at the 16th percentile at N 1000, so a point-rule pass would have been
  sampling noise (rates in (d)) on a clause the generator does not meet (REVIEW.md sections 2.1 and 2.2). The evaluation estimate, 1.5756, is close to the generator's value.
- **This outcome was the review's expected one.** At N 4000, the evaluation N, the review's Monte Carlo has
  PS-sub's L1 clause holding / failing / inconclusive on the interval in 0.002 / 0.206 / 0.792 of populations,
  and PS-use's in 0.034 / 0.034 / 0.932 (REVIEW.md section 2.2 table; design-stage, see section (d)).
- The unregistered L1_step arm (PREREG-003 section 4) is not part of this reading and is not scored: PS-sub
  0.9344 [0.8570, 1.0218], PS-use 0.9273 [0.8494, 1.0141].

## (d) Status of the review's Monte Carlo

The review's simulation numbers are **synthetic and design-stage**: 500 fresh synthetic populations at each of
N 1000, 2000 and 4000, seeds `sha256("opusreview003:r")[:8]` for r 0 to 499, scored with the same statistics and
bootstrap as the scorer (REVIEW.md section 1). They describe the generator's operating characteristics. They are
not confirmatory power, not a finding, and not evidence about the evaluation draw beyond context. They were not
read by the freezing lane and so are not in PREREG-003 section 7's disclosure; they are disclosed here.

REVIEW.md section 3.2, "Joint power (generator, 500 populations per N)", with its labels. "Drafted" is the rule
that was frozen (L1/L2 on the point, L0 on the interval); "interval" is H3 holding on all six intervals.

| set | rules | N 1000 | N 2000 | N 4000 |
|---|---|---|---|---|
| H3, all six | drafted | 0.298 | 0.224 | 0.148 |
| H3, all six | interval | 0.008 | 0.004 | 0.002 |
| registered tally, H2a + H3 | drafted | 0.296 | 0.224 | 0.148 |
| construction checks, H1a + H1b + H4 + H5 | drafted | 0.936 | 0.998 | 1.000 |
| everything | drafted / interval | 0.276 / 0.006 | 0.224 / 0.004 | 0.148 / 0.002 |

The
bootstrap was calibrated in the review's runs (mean SE over between-population SD 0.97 to 1.06 at N 1000 and
2000; percentile coverage 92% to 96%; REVIEW.md section 2.2 item 6).

## (e) Budget reading amendment (post hoc)

**From this amendment on, post hoc, the 3.0 probes-per-tracked-person-month target is read on the 95% upper
bound.** PREREG-003 section 5 did not say how the target is read (REVIEW.md section 2.4 asked for a reading rule),
and this choice is made after the results. The claim's scope is unchanged: it is made only at `phi_D` 0.7.

- **At `phi_D` 0.7, `wait` meets 3.0 on the upper bound for every family**: DR-1.5 2.4009 [2.3763, 2.4249],
  DR-1.0 1.9521 [1.9254, 1.9781], S 1.2585 [1.2391, 1.2772]. Under `all`, DR-1.5 does not (3.3179 [3.2711,
  3.3628]). The cost to DR-1.5 is in persons confirmed in window, 0.3207 under `all` and 0.2883 under `wait`
  (no paired interval stored).
- **At `phi_D` 0.9** (outside the claim's scope), `wait` meets 3.0 for every family (DR-1.5 1.5265 [1.5131,
  1.5400]), and on this draw so does `all` (DR-1.5 2.9260 [2.8752, 2.9802]).
- **At `phi_D` 0.3** (outside the claim's scope), `wait` equals `all` in every family, and DR-1.5 does not meet
  3.0 under either (3.6990 [3.6541, 3.7401]); DR-1.0 (2.6492 [2.6063, 2.6911]) and S (1.3552 [1.3302, 1.3805])
  do. Only `stop` brings DR-1.5 under 3.0 there (1.7982 [1.7750, 1.8177]).
- On this evaluation draw the point and upper-bound readings agree in every cell of the budget table, so the
  amendment changes no budget statement in RESULTS-003.md. All numbers are from `results_003.json`, block
  `budget`, `probes_per_tracked_month` and `persons_confirmed_in_window`.

## (f) Definition and wording corrections

Salvaged from the fixes lane's preparation patch (`fixes.patch`), which was written before the freeze against
the draft and is **not applied**. Only definition and wording corrections are taken; each was checked against the
frozen `study003.py`. The patch's N 2000 text, OWNER-PENDING markers, scorer guardrails, seed list and disclosure
additions are not taken. **Each item below is a definition or wording correction only; no number changes.**

1. **H3 statistic** (clarifies PREREG-003 section 2, H3 item, and section 6, H3 row). For each rule and family, the logged persons' alarms over `[max(c, B), T)` per 30 of
   their tracked days in that window, pooled over persons (total alarms over total tracked days), divided by the
   same persons' pooled rate on the S panel over the same window. A tracked day is one with `reason == 0`: the
   detector neither abstains nor holds. Days inside the CUSUM's 14-day refractory period count as tracked (as in
   frozen `drift_sim`), so the frozen phrase "non-refractory tracked days" is wrong. L1 sets `reason` 4 on its hold
   days `(c, c + 14]` (days with `used` set), so those are not tracked.
2. **H1b persons** (clarifies PREREG-003 section 3, H1b, and section 6, H1b row). DR-1.0 persons with an alarm in `[t0, t0 + 21)` and none before `t0`
   (`exclude_pre_onset_alarms=True`, the scorer's default). Each person's first in-window alarm, which is then the
   person's first post-baseline alarm, is confirmed; the statistic is the spaced confirmed share over the
   next-day confirmed share, each among confirmable alarms.
3. **H4 persons** (clarifies PREREG-003 section 3, H4, and section 6, H4 row). Logged DR+PS persons with `t0` in `[c, c + 13]`, so that D's shift, first nonzero on day `t0 + 1`,
   begins inside the hold `(c, c + 14]`; in practice these are the logged persons with `t0 >= c` (247 on the
   design seed, REVIEW.md section 3.7). The statistic is 21-day sensitivity with
   `exclude_pre_onset_alarms=False`. "Onsets inside `(c, c + W]`" in the frozen text means this.
4. **H5 wording and M1 statistic** (clarifies PREREG-003 section 3, H5, and section 6, H5 row). The claim is limited to M1: "M1, the indicator-pattern rule, does not separate
   unlogged PS-prop from DR-1.0 by more than 0.10." Statistic: among persons with an alarm in `[x0, x0 + 42)`
   (A-fixed `k = 0.5`, rule L0; `x0` is the onset `t0` for DR-1.0 and the change day `c` for PS-prop), the share
   whose first such alarm M1 calls person, that is, unless `Q >= q*`; all DR-1.0 persons minus unlogged PS-prop
   persons. **L0+label:** without a log entry it labels every alarm person, and neither arm has an entry, so the
   difference is 0 for any data; it is true by definition and unscored, and because it reads the policy log it is
   not an "indicator-only rule".
5. **Exact `wait` semantics** (clarifies PREREG-003 section 5, first paragraph). After a probed alarm on day `a`, the next alarm can be probed from day `a + 3L + 1` (`L` = 3, 9,
   29 at `phi_D` 0.3, 0.7, 0.9), whether or not any of its probes was answered; an alarm on day `a + 3L` is not
   probed. At most one confirmation is in flight per person. It is not "confirm once per person episode": on a
   sustained shift `wait` probes again every `3L + 1` days (28 at `phi_D` 0.7) while alarms continue. Every budget
   number was produced by this time-based rule.
6. **Why H1 and H2 are scored under `all`** (clarifies PREREG-003 section 1, "Probe rule for scoring", and
   section 5, fourth reasons bullet). H1a, H2a and H2b score S's first
   post-baseline alarm; H1b scores DR-1.0's first in-window detection among persons with no pre-onset alarm, which
   is that person's first post-baseline alarm. Every rule probes a person's first post-baseline alarm, so the
   four statistics are identical under `all`, `wait` and `stop` by construction. The frozen reason (the
   0.154 -> 0.134 fall) concerns all DR-1.0 persons, a different population from H1b's. The frozen scorer carries
   no assertion of this; the evidence is the review's fixture (REVIEW.md section 2.5).
7. **Plug-in projections are conditional on the design draw** (clarifies PREREG-003 section 1, evaluation N
   bullet; section 2, H3 bullets; section 3, H1b and H5 M1). Every
   "projected interval-level probability" and every "projected to hold with probability" figure in the frozen
   text is a plug-in projection from DECIDE-003 part (a): it takes the design draw's estimate as the true value,
   so it is conditional on the design draw being the truth, not a probability of passing under the generator.
   Three frozen sentences read differently on that label:
   - Section 1, "the registered prediction gets a more decisive test either way": under the frozen point rule
     the PS-sub pass rate under the generator falls as N rises (0.298, 0.224, 0.148 at N 1000, 2000, 4000), and a
     decisive interval verdict that PS-sub's L1 clause fails would take about 30,000 persons for an 80%
     chance (REVIEW.md section 2.1). Raising N was not a remedy for H3.
   - Section 2, the L1 clause "may fail about as often as it holds": the two existing draws pooled give 1.542,
     above 1.5, and under the generator the clause fails on the point rule about three times in four at N 2000 (REVIEW.md
     sections 2.2 and 3.6). "The joint probability over all H3 clauses was not computed" is superseded by
     REVIEW.md section 3.2 (section (d) above).
   - Section 3, H1b's 0.85 "misses at every N": that reason rests on the design draw (9th percentile); the
     generator puts H1b at 0.876 (REVIEW.md section 3.1). The registered 0.70 is not changed.
8. **Verdict comparisons are on 4-decimal values** (clarifies PREREG-003 section 6). `verdicts` compares the point estimate and interval ends as `boot` stores them, rounded to 4
   decimals, with the thresholds.
9. **Probe-rule column of the scoring map** (clarifies PREREG-003 section 6). H3, H4 and H5 use no probes, so their probe-rule entry `all` means "not applicable".

## (g) What this amendment does not do

- No rerun of any kind, no N 2000 run, no new seed, and no new simulation. Every number above is already in
- No retroactive freeze: this file is not a pre-registration and does not claim to have been written before the
  `results_003.json` and `RESULTS-003.md` are byte-identical to their commits (section (h)). The 1.5 threshold
- Nothing in (b) to (f) changes a frozen verdict or threshold.

## (h) Hashes

Computed with `shasum -a 256` on 2026-10-07 when this file was written. Each frozen file equals its blob at the
commit listed.

| file | commit | sha256 |
|---|---|---|
| `sim/PREREG-003.md` | `57208bc` | `06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79` |
| `sim/study003.py` | `6dcead9` | `037f31ec7534c8c4afd5364dd9b55f504c5f8f7479d7e2750f0b0ec8b00c031e` |
| `sim/decide_003.py` | `6dcead9` | `9fd3a0bc7e4b9afa34e6753f92a9b50277d99ac6cbe530f39c021f106b98f715` |
| `sim/tuning_003.json` | `d641d4c` | `c7002d79ffb9cf99eabcbd0888fa375ae2c2528fd968237d6ce40fd4384bd51d` |
| `sim/results_003.json` | `52286ad` | `922cd808aa05602750d3e2908b9354f8ec91ddb2736b8381faa8fd56c0e8000c` |
| `sim/RESULTS-003.md` | `52286ad` | `b4d47fd20378df124c9a28bbd4685ab524e9ae73a4595494e9bd6fcef5d26b9d` |
| `~/lanes/opus-reviews/prereg003-20261007/REVIEW.md` | outside the repo | `35adb9077bbc4fdc2e117c3f8861cdb23619f30a4f1fc8911f47a37c010accd4` |
| `~/lanes/opus-reviews/prereg003-20261007/READY.md` | outside the repo | `457f8ddac87efea206b873782662694d04c57c64de17ea113de1a47d8227de96` |
| `~/lanes/opus-reviews/prereg003-fixes-20261007/fixes.patch` | outside the repo | `e8e5ca68205125dc520714e47ee173d27b739ad46c0a4a1ee52d9093a678cd45` |
| `~/lanes/opus-reviews/prereg003-fixes-20261007/RESULT.md` | outside the repo | `7d07a150d7ae0fca13c03c1ddb7f07d31162ddc30d8ff38776ab1c21f50c6231` |
| `~/lanes/anchor-research/evidence/prereg003-review-20261007/TIMELINE.md` | outside the repo | `859057abd24863e9fc5660d02b7da05dad8f0738c1f73d71f9d3b16a3f0722fe` |

The REVIEW.md, fixes.patch and results hashes match the prefixes cited in TIMELINE.md, READY.md, RESULT.md and
RESULTS-003.md (35adb907..., e8e5ca68..., 922cd808...).
