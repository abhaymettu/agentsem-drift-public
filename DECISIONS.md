# DECISIONS

Dated research and design decisions for this repo, newest last. Every number cited is synthetic.

## 2026-10-07 | H3's decision rule for future work

**Decided by** an Opus reviewer (model opus, effort xhigh) under the owner's 2026-10-07 overnight grant: "a
research or design call that waited on him is decided by an Opus reviewer and recorded in DECISIONS.md". The
call had been open in ~/code/agentsem/RUNLOG.md since the 13:42 anchor-research entry ("any owner answer on H3's
rule for future work").

**Decision.** Any future registration that tests H3 (a replication, a spec 004, a "future work" plan) reads it on
the three-way interval rule of REVIEW.md section 2.2, the same rule POST-EVALUATION-003 (c) applies post hoc. It
is the only registered rule. No L2-only conjunction is registered or tallied beside it.

Rule text for a future registration:
> H3 is scored on spec 003 section 8's L1, L2 and L0 (not L1_step), on logged PS-sub and PS-use persons, at W 14
> and threshold 1.5. Each clause is read on its 95% paired person-bootstrap interval, on 4-decimal values. L1 and
> L2 clauses hold if the upper bound is below 1.5 and fail if the lower bound is at or above 1.5. L0 clauses hold
> if the lower bound is above 1.5 and fail if the upper bound is at or below 1.5. Any other clause is
> inconclusive. H3 holds if all six hold, fails if any fails, and is inconclusive otherwise. The scorer output is
> three-valued. Before the run, the registration states the hold, fail and inconclusive probabilities for each
> clause and for H3 at the registered N under the generator. Every clause is reported with its estimate, interval
> and verdict. L1_step is reported as an unregistered comparison.

**Options considered.**
- A. Keep the frozen point rule (L1, L2 point below 1.5; L0 lower bound above 1.5). Rejected: chosen on the
  design draw (16th percentile); no error control, since under the generator (PS-sub L1/S about 1.585) it passes
  0.298 / 0.224 / 0.148 of the time at N 1000 / 2000 / 4000, so smaller samples pass more often; the only item
  read on a point estimate (REVIEW.md 2.2 items 1 to 4).
- B. Three-way interval rule. **Chosen.**
- C. Restate H3 on L2 and L0 only, L1 reported as an estimate. Rejected: it drops the clause that failed, after it
  failed, which is the selective-reporting pattern a methods reader looks for. REVIEW.md 2.2 offered it as an
  owner alternative that "must be disclosed as such".
- D. Put L1_step in the L1 clause. Rejected: L1_step was an unregistered, unscored arm (PREREG-003 section 4);
  choosing it after seeing 0.9344 [0.8570, 1.0218] and 0.9273 [0.8494, 1.0141] is the most selective option.
- Not on the table (settled): moving 1.5 (REVIEW.md 2.2: "not acceptable"; POST-EVALUATION-003 (g)), W 21
  (~/.instinct/DECISIONS-20261005.md, W 14 kept).

**Reasoning.**
- Least selective: B is the only option written before any result (REVIEW.md, 10:44, before the 12:27 freeze).
  It was urged when the plug-in projection gave the point rule a 0.880 pass rate at N 4000 (DECIDE-003 (a)), so
  it argued against the result expected at the time. C and D were each picked knowing which clause failed or which
  arm passed.
- Error control: each clause is a one-sided 2.5% test, and "holds" is an intersection-union test. At N 4000 the
  generator passes PS-sub's L1 clause 0.148 under A and 0.002 under B (REVIEW.md 2.1, 2.2).
- One standard: H1a, H1b, H2a, H4, H5 and L0 are already read on their intervals; the bootstrap is calibrated
  (percentile coverage 92% to 96%, REVIEW.md 2.2 item 6).
- Testable through N, not through the rule: under B, PS-sub's L1 fail rate rises with N (0.066 / 0.098 / 0.206 at
  N 1000 / 2000 / 4000, REVIEW.md 2.2 table); about 30,656 persons give an 80% decisive fail (REVIEW.md 2.1).
  PS-use sits at about 1.496 under the generator, where "inconclusive" is the correct answer at any practical N.
- Consistent with what is already written: POST-EVALUATION-003 (c) and the paper's results subsection
  (paper/AUTHOR-NOTES.md section 9, rule 2) use this reading.

**Strongest case against (the reviewer's own).** The sequence reads: the frozen rule fails H3, a post hoc rule
turns the failure into "inconclusive", and the post hoc rule then becomes the future standard. And with a 0.002
hold rate, the author would be registering a claim believed false for PS-sub under a rule that mostly returns
"inconclusive", which looks like ritual; restating H3 (C) would be more candid. **Why B stands:** B predates the
results and was pressed when it was expected to cost a pass; it is stricter than A on "holds"; the 003 FAIL stays
first wherever H3 is reported. A claim believed false should be tested by a rule that can fail it on evidence, and
A fails it only through noise. C removes the failed clause after the fact. Low information at a given N is fixed
by choosing N, not by changing the claim.

**What this does NOT change.**
- Frozen files and hashes: sim/PREREG-003.md (57208bc), sim/study003.py, sim/decide_003.py, sim/tuning_003.json,
  sim/results_003.json, sim/RESULTS-003.md; `python3 sim/study003.py --check` passes and the six sha256 values equal
  POST-EVALUATION-003 (h).
- The frozen verdict: H3 FAILS on L1 PS-sub 1.5756 [1.4205, 1.7489]; the registered tally stays one of two.
  Nothing is rescored.
- The 1.5 threshold, W 14, H1b 0.70, L1_step over L1_did, sim/POST-EVALUATION-003.md, spec 003.
- Paper wording: paper/DRAFT.md and paper/SUPPLEMENT.md are the author's and are untouched. No simulation was run.

**Reverse by** adding a new dated entry below this one (do not edit this entry) when any of these holds:
1. The owner decides the open L1 versus L1_step question (sim/HYB-003.md, last paragraph of the results) for
   L1_step. Then L1_step enters the L1 clause under this same rule, registered before new data with its own
   probabilities; the 003 values (0.934, 0.927) may not be cited as support.
2. The owner states that H3's claim is about L2 only. Then option C applies, disclosed as a restatement made after
   the 003 results.
3. Interval coverage for the H3 ratios falls clearly below 92% at the registered N. Then the interval method
   changes, not the threshold.
4. The owner overrules this entry for any reason; his word replaces it.
Mechanically, `git revert` of this file's commit removes the entry; nothing else depends on it.

**Corrections to the lane's options brief (found by the reviewer, checked against the files).** The brief
(audit artifact, below) misattributed four sources. The settled 1.5 threshold and "N is not the lever" come from
POST-EVALUATION-003 (g) and REVIEW.md 2.1, not DECISIONS-20261005 (grep for "1.5" there returns 0). "N is not
the lever" holds for the point rule only. The phrase "the interval rule fails on the design seed by
construction" comes from ~/lanes/anchor-research/asks/prereg003-decisions.md item 2, not a RUNLOG, and it is
wrong: the design interval [1.175, 1.706] crosses 1.5, so the clause was inconclusive through sampling. The open
L1 versus L1_step question is recorded in sim/HYB-003.md, not the RUNLOG.

Audit: ~/audit/agentsem-h3rule-2026-10-07.md
