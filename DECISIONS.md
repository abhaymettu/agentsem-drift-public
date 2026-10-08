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

### Referee, 2026-10-07 (lane agentsem-h3referee-oct07; fresh-context Opus reviewer, read-only on the evidence)

**Verdict: AMEND.** Option B stays the only registered rule for future H3 work, with its rule text plus one added
disclosure sentence (item 1) and one added pre-run quantity (item 4). Four statements in the Reasoning, "Why B
stands" and "Reverse by" are wrong and are superseded by items 2, 3, 5 and 6. The entry above is left as written;
where an item below names one of its sentences, the item governs.

**Claim checked.** Future registrations read H3 on REVIEW.md 2.2's three-way interval rule as the only registered
rule; 003 is not rescored and its frozen FAIL is reported first.

**Checks that passed** (run by this referee). Every number cited above matches its source: REVIEW.md 2.1, 2.2 and
3.2 (0.298 / 0.224 / 0.148; 0.002; 0.066 / 0.098 / 0.206; 1.585 and 1.496; 30,656; coverage 92% to 96%),
DECIDE-003 (a) (0.880) and (c) ([1.175, 1.706]), POST-EVALUATION-003 (b) and (c), and sim/results_003.json (the
six H3 clauses, L1_step 0.9344 [0.857, 1.0218] and 0.9273 [0.8494, 1.0141], n 4000). The six frozen sha256 values
equal POST-EVALUATION-003 (h), and `python3 sim/study003.py --check` prints "check OK". The rule does not pass by
construction (it holds in 0.002 of N 4000 populations under the generator) and rescores nothing, so it does not
conflict with the frozen FAIL. C and D stay rejected for the reasons given. DECISIONS-20261005 keeps W=14 and
contains no "1.5"; the 13:42 anchor-research entry in ~/code/agentsem/RUNLOG.md carries the open call;
paper/AUTHOR-NOTES.md section 9 rule 2 uses the interval reading, labelled post hoc.

**Amendments.**
1. *The choice is post hoc; the rule says so.* "B is the only option written before any result" is wrong. A was
   also written before the evaluation (DESIGN-003 section 4 item 3, frozen as PREREG-003 section 2), and C was
   written beside B in REVIEW.md 2.2 at 10:44. All three predate the 12:27 freeze; the choice among them was made
   on 2026-10-07 after the 003 results. B's advantage over C is that it keeps the registered all-six claim
   (REVIEW.md 2.2), not its date. Append to the rule text: "This rule was adopted for future work on 2026-10-07,
   after the 003 evaluation. Under 003's frozen rule H3 FAILS; under this rule 003 reads inconclusive."
2. *What B was urged against.* "It was urged when the plug-in projection gave the point rule a 0.880 pass rate at
   N 4000 ... so it argued against the result expected at the time" and "was pressed when it was expected to cost
   a pass" misstate the record. The reviewer who urged B had the generator Monte Carlo, in which the point rule
   holds 0.224 at N 2000 (REVIEW.md 2.1, 3.6), and expected B to return inconclusive about 0.90 (REVIEW.md 2.2).
   The 0.880 is the lane's plug-in, at the N 4000 the lane chose after 11:05; the review recommended N 2000.
   Read instead: B was written before the evaluation draw existed, by a reviewer who expected it to return
   inconclusive, not to hold.
3. *What A does.* "A fails it only through noise" is backwards. Under the generator (PS-sub L1/S about 1.585) A
   returns FAIL in 0.852 of N 4000 populations (1 minus 0.148, REVIEW.md 3.2), the correct verdict; A *passes*
   only through noise. B's cost, stated: at N 4000 it returns FAIL in at least 0.206 (PS-sub's L1 fail rate,
   REVIEW.md 2.2 table) and inconclusive in most of the rest. B is chosen because both of its decisive verdicts
   are error-controlled, not because it is more decisive; at practical N it is less decisive than A.
4. *Coverage, made checkable.* The 92% floor is H3's ratios at N 4000, where the bootstrap SE runs about 6% under
   the between-population SD (REVIEW.md 2.2 item 6), so reversal trigger 3 already sits at its edge. The rule's
   pre-run statement adds the generator coverage of the six H3 intervals at the registered N, from the same Monte
   Carlo that gives the hold, fail and inconclusive probabilities. Without it trigger 3 has no measurement.
5. *Reversal mechanics.* "Mechanically, `git revert` of this file's commit removes the entry; nothing else depends
   on it" does not work. Tested in a scratch clone: at f71bcd4, `git revert --no-commit f71bcd4` stages
   `D DECISIONS.md`, deleting the whole decision log; once any later entry exists (this sub-entry included) it
   stops with `CONFLICT (modify/delete)` and exit 1. Reverse only by a new dated entry, as the first sentence of
   "Reverse by" says.
6. *L1 versus L1_step.* The entry calls this question open, citing sim/HYB-003.md (committed 2026-10-04).
   PREREG-003 section 4, frozen later under the owner delegation, says "L1_step is the rule carried into the
   paper", and sim/OBSERVER-STEP-DIGEST.md reads it so. What remains open is whether H3's claim is about L1_step.
   Trigger 1 means an owner statement to that effect, not the existing PREREG-003 sentence, and its citation ban
   also covers the design-stage L1_step values seen before the freeze, 0.977 [0.844, 1.108] and 0.960 [0.836,
   1.095] (PREREG-003 section 7).
7. *Grant wording.* The quoted grant ("a research or design call that waited on him ...") is the conductor's
   lane-prompt summary of his 2026-10-07 multiple-choice answers
   (~/.instinct/lanes/prompts/agentsem-h3rule-oct07-20261007-190016.txt), not his words.

Not changed by this sub-entry: the frozen files and verdict, 1.5, W 14, the paper. Audit:
~/audit/agentsem-h3referee-2026-10-07.md

## 2026-10-07 | L1 versus L1_step, and the paper's H3 paragraph

**Decided by** an Opus reviewer (model opus, effort xhigh) under the owner's 2026-10-07 overnight grant (the
conductor's summary of his multiple-choice answers, not his words; referee amendment 7). Both calls were open in
RUNLOG.md (19:31 entry: "L1 vs L1_step question and the paper H3 wording stay his"). No simulation was run.

### Decision 1: L1 versus L1_step

**Decision.** Two senses, answered separately.
- (i) The rule the method carries: no new choice. PREREG-003 section 4 ("L1_step is the rule carried into the
  paper; L1_did is dropped") records the owner-delegated pick "L1_step over L1_did" (~/.instinct/DECISIONS-20261005.md
  line 24), which chose between the two observer-step variants, not L1_step over L1. The same section keeps L1
  against L1_step a reported trade-off with no single `w`. That answers sim/HYB-003.md's "the choice is the project
  owner's" (lines 175 to 180): it stays a trade-off, because both deciding quantities (how often unlogged changes
  coincide with logged ones; how strongly D loads on the unmapped indicators early) are "not estimable here".
  STEP-003 agrees ("L1_step over L1 does not hold unconditionally").
- (ii) Future H3: the L1 clause stays on L1 under the three-way interval rule above; L1_step stays an unregistered
  comparison. "Reverse by" trigger 1 of the H3-rule entry has not fired and this entry does not fire it.

**Options considered.**
- 1A. Status quo as above. **Chosen.**
- 1B. Move H3's L1 clause to L1_step. Rejected: it switches the clause's target after L1 failed (1.5756) and
  L1_step passed (option D of the H3-rule entry). It is also not a risky test: all four known L1_step intervals sit
  at or below 1.108 against 1.5 (design 0.977 [0.844, 1.108], 0.960 [0.836, 1.095], PREREG-003 section 7;
  evaluation 0.9344 [0.8570, 1.0218], 0.9273 [0.8494, 1.0141], results_003.json `verdicts.H3.L1_step`), and H3's
  logged families lack the one condition in which L1_step loses to L1, an unlogged shift on the unmapped indicators
  coinciding with the logged change (STEP-003 finding 3; OBSERVER-STEP-DIGEST section 1). No generator Monte Carlo
  of L1_step's H3 ratio exists, so its pre-run probabilities could not be stated without new simulation.
- 1C. Register both. Rejected: as extra conjunction clauses they are near-certain and cannot move H3 (PS-sub's L1
  clause governs it, REVIEW.md 2.2 item 5); as a separate tallied hypothesis it adds a known pass (REVIEW.md 3.5:
  L1_step "should stay out of" the tally).
- 1D. Declare it an empirical question. Not a substitute: it is what sense (i) already is, and it gives no rule for
  sense (ii).

**Strongest case against.** The paper carries L1_step, so the carried rule never faces a registered test, and H3
stays on a rule believed to fail for PS-sub (generator about 1.585). **Why 1A stands:** the paper does not
recommend L1_step over L1; L1 is the rule H3 was registered and sized on; an L1_step clause in these families tests
the one condition already known to favour it; rule B can fail L1 on evidence through N (about 30,656 persons for an
80% decisive fail); and 1A stays reversible in either direction, while a registered 1B could not be withdrawn.

**Reverse by** a new dated entry below (never `git revert`; referee amendment 5) when:
1. The owner states that H3's claim is about L1_step. Then L1_step enters under rule B, registered before new data
   with its own hold, fail and inconclusive probabilities and coverage from a new generator Monte Carlo; 0.934,
   0.927, 0.977 and 0.960 are not cited as support; the registration discloses that the switch followed L1's 003 fail.
2. A future design includes unlogged shifts coinciding with logged changes. Then a separate L1_step hypothesis,
   outside H3's conjunction, may be registered with its own probabilities.
3. The paper comes to recommend L1_step over L1. Then that rule is registered prospectively as a separate,
   labelled hypothesis, its place in the tally stated before data.
4. Consented data estimate the coincidence rate or D's early loading and put one rule ahead at a stated `w`.
   Then sense (i) is revisited.
5. The owner overrules this entry for any reason.

### Decision 2: the paper's H3 paragraph (paper/DRAFT.md section 3.7)

**Decision.** Two edits applied; the "[author wording]" marker stays for the owner.
- "It recommended reading every clause" now reads "The review recommended ...": the nearest antecedent was
  sim/POST-EVALUATION-003.md, which recommends nothing.
- One sentence added (about 50 words) stating the future-work rule from the H3-rule entry, its post hoc adoption
  date (referee amendment 1) and that it is stricter for a pass: at N 4000 the review's Monte Carlo had H3 holding
  on the interval in 0.002 of populations, against 0.148 on the frozen rule (POST-EVALUATION-003 (d) table,
  "H3, all six | interval"). "The same six clauses" carries Decision 1 (L1, not L1_step).
- paper/AUTHOR-NOTES.md item 10 records the status and what remains for him.
- Checked and kept: every number in the paragraph matches results_003.json and POST-EVALUATION-003 (c), (d) after
  4-to-3-decimal rounding; "the frozen FAIL is the generator's usual outcome, not bad luck" is consistent with
  referee amendment 3 (the frozen rule fails correctly in 0.852 of N 4000 populations).

**Options considered.** 2A (accept as is, remove marker): rejected, keeps the wrong antecedent and omits the forward
rule. 2B with marker removal: rejected, an agent would be signing off his authorship of submitted prose (AUTHOR-NOTES
item 10 and section 10; ~/lanes/anchor-research/STATE.md "The paper's wording of the H3 result is his"), which the
grant (no publishing or outward messages) does not cover. Pure 2C (leave everything): rejected, leaves a known error
and an unstated rule the grant can fix. **Chosen:** 2B's edits, 2C for the marker.

**Strongest case against.** The body is about 5,373 words against the 5,000-word guide, and a forward commitment in a
results paragraph can read as defensive. **Why it stands:** the sentence is under 1% of the body, and the 0.002
against 0.148 contrast is the most direct evidence that the post hoc rule makes a pass harder, not easier. He can cut
it when he removes the marker; the open item is now a read, not a decision.

**Reverse by** a new dated entry below plus a paper edit (never `git revert`): if he cuts or rewrites the sentence,
record it; if the H3 future rule is reversed, change the sentence in the same commit.

**Not changed:** frozen files and the frozen H3 FAIL, 1.5, W 14, the "[author wording]" marker, paper/SUPPLEMENT.md.

## 2026-10-07 | The AI-use statement and the H3 paragraph's humanizer read

**Decided by** an Opus reviewer (model opus, effort xhigh, read-only) under the owner's 2026-10-07 overnight grant
(the conductor's summary of his multiple-choice answers, not his words). Open in RUNLOG.md since the 19:42 entry:
"owner reads the H3 paragraph (humanizer) and removes the marker; AI-use statement names both DECISIONS.md calls".
The marker itself was already decided (entry above, Decision 2: it stays for him) and was not reopened.

### Decision 1: the AI-use statement (paper/DRAFT.md declarations block)

**Decision.** B: a bracketed "[owner to confirm ...]" candidate in the Use of AI tools paragraph, after "working
under the author's direction". It covers the spec 003 pre-freeze review, the freezing lane's lane decisions (among
them H3's point rule) and freeze under the delegation quoted in PREREG-003 section 8, and both 2026-10-07 calls
above, and says neither changed a frozen file, threshold or verdict. AUTHOR-NOTES items 13 and 15 note it.

**New evidence the earlier entries did not weigh.** sim/PREREG-003.md line 7 says decisions marked "(lane
decision)" were made by the lane; line 43 marks H3's decision rule as one; section 8 (line 161) quotes the owner's
delegation verbatim. "Under the author's direction" understates this, and the candidate minimal line ("Claude
assisted with code development and manuscript preparation") alone would contradict PREREG-003.

**Deposit check.** DECISIONS.md is not on `main` (`git cat-file -e main:DECISIONS.md` fails), no remote branch
contains aebb6f4, the Data statement does not list it, and it carries `~/` and `/Users/` paths. The sentence
therefore names the file without claiming it is deposited; the deposit stays his.

**Options considered.**
- A. The same sentence unbracketed. Rejected: the declarations assert nothing beyond what the coordinator supplied
  (AUTHOR-NOTES item 15), and the 2026-10-07 delegation is a summary of his answers, not his words.
- B. Bracketed candidate. **Chosen.**
- C. Add nothing. Rejected: leaves a known understatement in the statement a transparency-minded reader checks.

**Strongest case against.** It tells reviewers an agent chose a rule knowing it passed on the design draw (section
3.6), and it adds about 105 words to a body already over the 5,000-word guide. **Why it stands:** a methods reader
who finds the lane decisions in the repository without a disclosure is the worse outcome for his application, and
the bracket forces his read before submission.

**Reverse by** deleting the bracketed sentence from paper/DRAFT.md and adding a dated entry here (never `git
revert`). If he keeps it but does not deposit DECISIONS.md, replace "in the decision log `DECISIONS.md`" with "in
the author's records".

### Decision 2: humanizer read of the H3 paragraph

**Decision.** (a): no agent rewrite. Paper paragraph and marker unchanged.

**Options considered.**
- (a) Nothing beyond the entry above. **Chosen.**
- (b) A humanized candidate in AUTHOR-NOTES. Rejected: still agent prose, doubles his read without settling
  authorship, and adds a second text to audit.
- (c) Humanizer edits applied to the paper, marker kept. Rejected: rewrites a paragraph whose numbers and hedges
  were just audited and pre-empts the read the marker exists for.

**Reasoning.** The paragraph's main AI tells are its "X, not Y" contrasts ("not bad luck", "a comparison, not a
rescue", "neither confirmatory power nor evidence"), each an audited hedge a humanizer would flatten. No academic
voice sample exists for humanizer (only voice-dna.md for job prose and the PhD outreach drafts). The new sentence
is already plain, with no em dashes.

**Strongest case against.** The OPEN item and the global rule put prose under his name through humanizer.
**Answer:** run humanizer when he reads the paragraph, on the whole paper before submission, holding fixed 1.576
[1.421, 1.749], 1.309, 1.286, 0.792, 0.148 and 0.002 and keeping the post hoc and "not a rescue" hedges.
Submission is his step.

**Reverse by:** if he wants a candidate before his read, write one into AUTHOR-NOTES item 10 with the paper
unchanged and the marker kept. Nothing to undo.

## 2026-10-07 | The owner-only items: H3 marker, AI-use bracket, DECISIONS.md deposit

**Decided by** an Opus reviewer (model opus, effort xhigh, read-only) under the owner's 2026-10-07 overnight grant
(the conductor's summary of his multiple-choice answers, not his words). Open in RUNLOG.md since the 20:00 entry,
which labelled it "his only"; a lane was dispatched on it anyway. Third Opus ruling on these items today.

### Part 1: H3 paragraph marker and humanizer read

**Decision.** 1a: stays his; paper unchanged. Removing "[author wording]" (paper/DRAFT.md:381) signs off prose
under his name, which the entry "L1 versus L1_step, and the paper's H3 paragraph" (Decision 2) already reserved
for him; there is still no academic voice sample for humanizer. **Rejected:** 1b, agent humanizes and removes the
marker. **Case against:** the grant routes owner calls to a reviewer, so deferring looks like refusing it. **Why it
stands:** the paragraph is likely writing-sample material for Dec 1, and his own read is what lets him defend it.
**Reverse by:** on his message, add a dated entry here, run humanizer holding the numbers listed in the AI-use
entry's Decision 2, then remove the marker.

### Part 2: the AI-use bracket

**Decision.** 2a: stays bracketed. Nothing has changed since the entry "The AI-use statement and the H3
paragraph's humanizer read", and the delegation it describes is a conductor summary, not his words. **Rejected:**
2b unbracket (asserts in his name); 2c cut to the minimal line (contradicts PREREG-003 section 8). **Case
against:** a bracketed draft is not submittable. **Why it stands:** submission is his step; the bracket costs one
read. **Reverse by:** as in that entry's Decision 1.

### Part 3: whether DECISIONS.md is deposited

**Decision.** 3c: preparation only, the deposit decision stays his (outward-facing). paper/AUTHOR-NOTES.md
section 5 gains item 4: DECISIONS.md is on `eval/authorship-filter`, not `main`, so a `main` deposit leaves it
out; its `~/` and `/Users/` pointers are no reason to withhold it; and the bracket wording follows from his answer.

**New evidence.** Home-directory pointers are not peculiar to DECISIONS.md: `sim/PREREG.md:4` carries one on
`origin/main`; `sim/PREREG-003.md:8` and `sim/POST-EVALUATION-003.md` lines 11, 25 and 201-205 carry them on this
branch (checked with `git grep`; PREREG-003 is not on `main`). The Data statement lists POST-EVALUATION-003 for the
supplement (paper/DRAFT.md:205-207).

**Rejected.** 3a no change (section 5 item 1 would include or drop the file by branch choice, with no one
deciding); 3b agent decides "not deposited" (outward-facing, his); 3d scrub the paths now (rewrites append-only
entries for no gain, since frozen files carry the same kind).

**Case against:** item 4 repeats the bracket and the AI-use entry's "Reverse by". **Why it stands:** section 5 is
the checklist he works from at deposit time.

**Reverse by** deleting AUTHOR-NOTES section 5 item 4 and adding a dated entry here (never `git revert`).

**Dispatch.** These items are owner-only; reopen only on his own message.


## 2026-10-07 19:54 CDT | Delegated owner read of the H3 paragraph

Abhay's original phone message at 19:52:18 CDT, phonemsg-REDACTED,
explicitly delegated this read: "You read it for me and make the decision". It replied to the
H3 owner-read flag. Instinct read the paragraph at 8309e19, both earlier research decisions and
the referee amendments, and accepted the paragraph as written.

Decision: remove only the "[author wording]" marker from paper/DRAFT.md section 3.7. Keep the
antecedent fix and future-rule sentence, including the 0.002 versus 0.148 distinction. No humanizer
rewrite: the contrasts are audited hedges and flattening them would lose those hedges.
AUTHOR-NOTES item 10 records the completed read. Marker removal is delegated owner sign-off on
this prose, not a claim that Abhay personally performed the read or a submission/deposit approval.

This supersedes the owner-read hold in the immediately preceding provisional lane entry. Its
AI-use bracket and deposit items remain held. No AI-use text, frozen science or numbers changed.
Reverse only by a new dated decision and explicit prose edit, never by reverting the whole log.
