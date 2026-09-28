# Is it the person or the agent? Validity threats to inferring within-person change from everyday agent conversations

Working paper, draft 1 (2026-09-27). Working title.

Author: Abhay Mettu. **Affiliation, corresponding address and acknowledgements: PLACEHOLDER, owner
decision, not filled in.**

Where the numbers come from. Section 3's design values and tuned constants are read from
`sim/PREREG.md` (frozen at commit `3c11e4f`, sha256
`60db6dd195942387e5572a640224c4cb13836f29c37c1b611b14c70598678f17`) and `sim/tuning.json`. Section 4's
numbers are read from `pilot/RESULTS.md`, `pilot/results.json`, `pilot/INVENTORY.md` and
`pilot/indicator4_params.json`, all from the corpus snapshot reproduced by
`python3 pilot/trace_audit.py --until 2026-09-28T01:32:31Z`. Simulation results are not in this draft;
they are marked [SIM RESULTS] and [PENDING RUN 2]. Every simulation number is synthetic. Prior agentSEM
work is cited by repository and commit. Unresolved items are listed at the end.

---

## 0. Abstract

General-purpose agents take in much of the ordinary language people produce while they work, and it is
tempting to treat a change in a trace-derived score as a change in the person. I argue that this
inference has not been validated and set out what validating it would take. I lay it out as an
argument-based validity chain with four links: trace to indicator (whose behaviour is this?),
indicators to a within-person score (is the score invariant across contexts, agent versions and agent
help?), score to change claim (against what baseline, with what missing days?), and change claim to
criterion evidence (how was the criterion sampled?). For each link I name the threat and the evidence
that would support the inference. I then report the design of a pre-registered simulation in which
three candidate scoring rules and five criterion-sampling designs are scored on eleven families of
synthetic persons, with ten predictions frozen before scoring. [SIM RESULTS]. Last, I audit the first
link on my own agent transcripts, using metadata only. Of 73,955 user-role entries, 0.93 percent (1.44
percent of characters) were typed by me; the rest were tool results, subagent traffic, injected text
and lane prompts. 84 percent of sessions had no typed entry, and those sessions supplied 75 percent of
the late-night entries and of the fragmentation units in the naive series. Over 21 days, naive and
authorship-filtered versions of the same indicator correlated at 0.90 (late activity), 0.28 (message
length) and 0.12 (session fragmentation). The audit is n = 1, descriptive, and capped by 45-day
transcript retention. The contribution is the chain, the design requirements it implies for a
consented validation study, and evidence that in one real corpus the first link fails badly enough for
a naive score to mostly reflect the agent and its automation.

---

## 1. Introduction

A person who uses a general-purpose agent for a working day leaves a long trace: what they asked for,
when, how long their messages were, how often they switched sessions, and what they left unfinished.
The same stream carries coding, writing and personal use. The volume is large and the collection is
passive, so it is natural to ask whether the trace could tell the agent something about the person's
wellbeing or functioning, and in particular whether it could notice when that state moves away from the
person's own usual range.

The existing work that comes closest does one of three things. The first uses dialogue that is already
about mental health. Tieleman et al. (2026) fine-tune a language model to estimate a questionnaire-scale
severity score from AI mental-health dialogue (final N = 3,953, held-out N = 842, r = .80). <!-- cite: -->
The second elicits answers: ALBA (Varadarajan et al., 2024) and MAQuA (Varadarajan et al., 2026) choose
open-ended or item-level questions adaptively and score them against a full questionnaire, and Yun et
al. (2024) use a language model to vary the wording of a questionnaire an agent administers daily. The
third classifies conversations or people cross-sectionally. Anthropic (2025) classified 131,484 of 4.5
million sampled conversations as affective (2.9 percent of use) with an aggregate, privacy-preserving
clustering tool, and stated that it had no longitudinal data. Eichstaedt et al. (2018) predicted a
chart-recorded condition from pre-index social-media language between persons (N = 683, AUC = 0.72). <!-- cite: -->
The OpenAI and MIT Media Lab study (arXiv 2504.03888) varied features of a voice
product and measured self-reported loneliness, socialization and emotional dependence over four weeks.

None of these asks whether a within-person change in a score computed from ordinary, non-clinical agent
use is a change in the person. The passive-sensing literature gives a reason to ask before building
anything: in GLOBEM, a multi-year, multi-site phone-sensing dataset of more than 700 user-years, existing
models did not generalize across cohorts or years (Xu et al., 2023). Early-warning work on dense
experience sampling shows that within-person dynamics can carry information before a transition
(Helmich et al., 2023), but it rests on intensive self-report, not on a trace the person did not
produce for measurement. In the prior-art searches recorded for this project I found no study that
validates within-person change inferred from general-purpose assistant logs against a repeated,
independent criterion (`prior-art-passive.md`, gap a). That is a statement about those searches, not
proof of absence.

The question this paper takes up is a validity question in the sense of Messick (1995) and Kane (2013):
what would have to be true, and what evidence would show it, for the claim "this person's score has
moved away from their baseline" to be read as "this person has changed"? Agent traces make the question
harder than it is for a phone sensor, for a reason that has nothing to do with language models' skill.
The agent writes much of what ends up in the "user" stream, the agent's help changes what the person
does next, and the agent's software changes under the person every few days. A score can move because
any of those moved.

The contribution has three parts: a validity chain with the threats to each link (section 2); a
pre-registered simulation of those threats, in which the probe schedules are designs for sampling a
criterion in a future validation study (section 3; design reported, results pending); and a
metadata-only audit of the first link on my own agent transcripts, which reports contamination and
estimates no state (section 4). Section 5 turns these into requirements for a consented validation
study, section 6 states the scope, and section 7 is the single translational paragraph.

The paper builds no system, proposes no product, and makes no claim about any clinical condition. The
agent is the object of study, as a measurement context.

---

## 2. The validity argument

### 2.1 Frame

I use the argument-based approach (Kane, 2013): state the interpretation as a chain of inferences, each
resting on assumptions, and collect evidence for the assumptions that are least plausible. Validity is
a property of an interpretation of scores, not of an instrument (Messick, 1995; AERA, APA and NCME,
2014). Messick's two named threats organize most of what follows: construct-irrelevant variance (the
score moves for reasons other than the construct) and construct underrepresentation (the score misses
part of the construct). Borsboom et al. (2004) add a condition that turns out to be decisive here: a
score is valid for an attribute only if variation in the attribute causes variation in the score. A
message the agent wrote cannot be caused by the person's state, however well it correlates with it.

The interpretation under test is:

> A rise in person i's trace-derived score above that person's own baseline, sustained over days,
> indicates a change in person i's wellbeing or functioning state.

It has four links. The chain is only as strong as its weakest link, and the links fail in order: if
the trace is not the person's behaviour, nothing downstream can repair it.

### 2.2 Link 1: trace to indicator (authorship)

**Inference.** An indicator computed from the "user" side of the transcript, such as message length,
late-night activity, or session fragmentation, summarizes the person's behaviour.

**Threat.** Much of an agent transcript's user-role stream is not typed by the user: tool results,
harness and hook injections, automated-lane prompts, subagent traffic, and agent drafts pasted back.
Sessions can also run with no person present, which contaminates timing indicators: an automated job
at 3 a.m. adds late-night activity that no one performed. This is construct-irrelevant variance in Messick's
sense, and under Borsboom et al.'s condition it is not variance the person's state can cause.

The contamination has a known form. For an indicator computed by daily averaging over entries, with a
day's machine share `pi_t` and machine text independent of the state, the observed within-person
validity is attenuated by

    Att = (1 - E pi) / sqrt(E[(1 - pi)^2] + E[pi^2] kappa_r + Var(pi) delta_r^2),

where `kappa_r` and `delta_r` are the machine-text variance ratio and mean gap in units of the human
indicator's SD (spec P6). At Bernoulli mixing this reduces to the zero-coupling case of the
contamination formula derived for covert AI authorship in survey responses (Mettu, ghost-respondents
working paper, E5 and E7 at `c = 0`), where contamination at zero coupling always attenuates and never
flips sign. Two departures matter in agent traces. If the machine share rises with the state (a person
delegates more when things are hard), the machine text's mean gap couples to the state and can create
validity that belongs to the delegation, not to the behaviour (P6's third clause). And filtering is
imperfect: a filter that catches 90 percent of machine text and keeps 95 percent of human text leaves a
residual share `pi' = 0.1 pi / (0.1 pi + 0.95 (1 - pi))`, which is small only when `pi` is small.

**Evidence that would support the inference.** A recorded source for each entry, with coverage
reported; a measured machine share per indicator; naive against filtered comparisons; and a class for
person-absent sessions.

**Where addressed.** Section 4 measures all of this on one corpus. Section 3 carries the measured
indicator-4 values into the simulation and tests the attenuation formula (P6).

### 2.3 Link 2: indicator to within-person score (invariance and level)

**Inference.** The composite of an individual's indicators, standardized against that individual's
baseline, means the same thing on every day it is computed.

**Threats.** Three sources of non-invariance are specific to agents.

- *Context.* One stream mixes coding, writing and personal use; an indicator's mean can differ by
  context, and the mix can shift with or without a state change. The prior-art searches for this
  project found no empirical study of this invariance for chat-derived indicators
  (`prior-art-passive.md`, gap b).
- *Agent and model version.* A version change can move an indicator's mean and its loading. A logged
  change can be re-baselined; an unlogged one looks like drift.
- *Help.* The agent's help changes the person's next behaviour. In agentSEM Study 1a
  (`~/code/agentsem-trap-world`, commit `21ec751`, `MORNING-HANDOFF.md`), an adaptive agent's help
  left a shadow in the logs that raised internal consistency and fit while validity fell (in closed
  form; the grid showed only a small fall); personalized help, not uniform help, created the trap. A
  world with no person signal passed internal consistency, fit and convergent checks there and failed
  only on test-retest stability. Reliability evidence cannot stand in for validity evidence here, as
  also seen when language-model questionnaire responses reached high internal consistency while
  failing structural fit and invariance against human baselines (Shen and Han, 2026).

There is also the level question. Associations across persons do not license claims about change
within a person, and models that do not separate the two conflate stable differences with
within-person processes (Curran and Bauer, 2011; Hamaker et al., 2015; Bolger and Laurenceau, 2013).
A score that separates people well can carry no information about a given person's change.

**Evidence that would support the inference.** Indicator loadings and means that are equal, within a
stated margin, across contexts, across logged versions, and on helped and unhelped days; help that is
randomized and logged, so that its effect can be separated from the person's state (Klasnja et al.,
2015); logged version identifiers; within-person designs.

**Where addressed.** Section 3's generator plants context effects, version changes (logged and
unlogged) and help effects, including help whose size grows with the state. The candidate scoring rule
A-fixed scores friction indicators on unhelped days only, following agentSEM Study 5
(`~/code/agentsem-study5-feasibility`, commit `3dfe3c2`, `FALSIFICATION-PLAN.md`), where an estimator
using unhelped days held its null under state-dependent help and the help-adjusted estimator did not.
Section 4 counts version and model changes in the real corpus.

### 2.4 Link 3: score to change claim (baseline and missingness)

**Inference.** A sustained rise of the score above the person's baseline, as judged by a sequential
statistic, reflects change in the person rather than a change in how, how much, or whether the person
used the agent.

**Threats.**

- *Baseline.* The baseline is a window of the person's own history. If the state is already changing
  inside that window, the reference is wrong, and later change is measured against a moving target.
- *Non-state change.* A workload spike, a vacation, disengagement from the tool, a broken integration
  that drops indicators, a shift in the mix of work: each can move the score with no change in state.
- *Missingness.* Days without use are not missing at random if use depends on the state. In Rubin's
  (1976) terms, usage missingness that depends on the unobserved state is missing not at random, and no
  analysis of the observed days alone can remove the bias it causes. An abstention rule (declining to
  compute a score when recent usage is thin) trades coverage for protection against this, and the
  trade has to be reported, not hidden.

**Evidence that would support the inference.** A reported false-flag rate on persons with no state
change, broken down by the kind of non-state change; the sensitivity of the change statistic to
planted change, and the time to flag; the abstention share with its reasons; evidence about the usage
mechanism, not an assumption.

**Where addressed.** Section 3: families SP (workload sprint), VA (vacation), DE (disengagement), BI
(broken integration), CS (context shift), BD (drift inside the baseline) and DV (drift overlapping a
vacation), with a usage-depends-on-state cell (`kappa = 0.3`) and abstention reported as a metric.
The change statistic is a one-sided CUSUM (Page, 1954). Section 4 reports usage missingness in the
real corpus and the base rate of candidate infrastructure events near change points.

### 2.5 Link 4: change claim to criterion evidence (criterion sampling)

**Inference.** The relation between the trace score and an independent criterion, estimated from the
occasions on which the criterion was collected, estimates the relation on all occasions.

**Threat.** The criterion is collected on a subset of days. If which days get one depends on the trace
score, the estimated validity is biased. This is an old result. Selection on a variable related to the predictor
changes the observed correlation (Pearson, 1903; Lawley, 1944), and the direct and indirect cases of
range restriction and their corrections are standard in personnel selection (Thorndike, 1949, Cases II
and III [unverified: case labels confirmed only in secondary sources]; Sackett and Yang, 2000). The
structure closest to the one here is verification bias: when a positive index test raises the chance
that the reference standard is applied, accuracy estimates are biased, and weighting each verified case
by the inverse of its verification probability corrects them (Begg and Greenes, 1983). Outcome-dependent
two-phase designs use the same family of corrections (Tao et al., 2021; Zhou et al., 2002 [unverified]).
In experience sampling, trigger design has been shown to change which contexts are sampled (Lathia et
al., 2013), though without an attenuation result or a correction.

What this setting adds is a dynamic trigger. A schedule that asks for the criterion when a CUSUM on
past scores is high selects on a statistic of past scores, which predict the current state beyond the
current score, so the slope is biased and the correlation range-restricted. A random floor with every
occasion's selection probability logged makes inverse-probability weighting possible; a trigger-only
or fixed schedule does not, because some days have zero probability. This is a known result in a new
setting, not a discovery (`paper-citations.md`, verdict). The event-contingent and adaptive sampling
literature has been searched but not read in full (see Open items), and until it is, the paper does
not call the dynamic-trigger case new.

A second threat is criterion non-response: if the person answers less often when their state is worse,
answered occasions are missing not at random (Rubin, 1976), and a propensity model built from
observables cannot fully correct it.

**Evidence that would support the inference.** A random floor with logged propensities; weighted and
unweighted estimates side by side; response rates by trace-score level; a stated non-response model.

**Where addressed.** Section 3, predictions P4 and P5. Section 5, requirement R5.

### 2.6 Summary table

| link | inference | main threat | evidence that would support it | where in this paper |
|---|---|---|---|---|
| 1. trace to indicator | the indicator is the person's behaviour | machine-authored entries and person-absent sessions (construct-irrelevant variance) | entry-level provenance; measured machine share; naive vs filtered comparison | section 4 (measured); section 3, P6 |
| 2. indicator to within-person score | the score means the same thing every day | context, agent/model version and help non-invariance; between/within conflation | invariance across contexts, versions and help; logged randomized help; within-person design | section 3 (families CS, AV, AV2; help cells; P2, P3, P10); section 4 (version counts) |
| 3. score to change claim | a sustained rise is a change in the person | baseline contamination; non-state change; usage missing not at random | false-flag rates by non-state family; sensitivity and time to flag; abstention share and reasons | section 3 (P1, P1b, P7, P9; `kappa` cell); section 4 (missingness, change-point base rate) |
| 4. change claim to criterion | criterion-occasion validity equals all-occasion validity | score-dependent criterion sampling; criterion non-response missing not at random | random floor with logged propensities; weighted vs unweighted estimates; response by score level | section 3 (P4, P5); section 5 (R5) |

---

## 3. Pre-registered simulation

### 3.1 Status and reading

The design below is `sim/PREREG.md`, frozen at commit `3c11e4f` of `agentsem-drift` with sha256
`60db6dd195942387e5572a640224c4cb13836f29c37c1b611b14c70598678f17`. The PREREG carries spec sections 3
to 6 verbatim plus the tuned values, and every evaluation seed is derived from that hash. The freeze is
a committed, hashed file in a local repository; it is not an external registration.

Two readings of the simulation are ruled out in advance. The scoring rules are candidate scoring rules
whose validity is under test. They are not products and nothing here is deployed. The probe schedules
are designs for sampling a criterion in a future validation study; they are not an agent administering
questions to anyone. Everything in this section is synthetic. The simulation tests the logic of the
validity argument and where each scoring rule fails; it says nothing about predictive validity in real
people.

### 3.2 Generator

Each synthetic person has 140 days, with days 1 to 28 as baseline, and there are 1,000 persons per
family per cell. All rules and schedules run on the same persons, so differences are paired and
resampled with a person bootstrap. The full specification is in the PREREG; the parts that carry the
threats are these.

- **State.** One latent, non-clinical wellbeing and functioning state `D_t`, standardized within
  person, AR(1) with `phi_D = 0.7`. Drift families add a ramp of `+1.0` SD from an onset in days 50 to
  100, over 7 to 21 days.
- **Nuisance processes.** Workload (AR(1), observed with noise); a daily context of code, write or
  personal, whose personal share rises slightly with `D`; and usage with probability
  `expit(logit(0.8) - kappa D_t)` minus vacation and disengagement terms, where `kappa = 0.3` in one cell makes unused days depend on the
  state.
- **Indicators.** Six, on used days: late-activity share, session fragmentation, deferral rate, message
  length, negative self-reference rate, reply latency. Each is `H_jt = lam_j D_t + gam_j L_t +
  beta_j[ctx_t] - A_t psi_j (1 + theta1 D_t) + e_jt`, with per-person loadings `lam_j ~ U[0.25, 0.5]`,
  workload loadings on the timing and friction indicators, context offsets on indicators 1, 4 and 5,
  and a help effect on indicators 2 and 3 that can grow with the state (`theta1 = 0.5` in one cell).
- **Authorship mixing** on indicators 4 and 5, by daily averaging: `X_jt = (1 - pi_t) H_jt + pi_t M_jt`,
  with machine text independent of `D`. Indicator 4's parameters come from section 4
  (`pilot/indicator4_params.json`, main thread): `pi_bar = 0.845`, `kappa_a = 0.547`, `mu_M4 = 0.274`
  within-person SDs. Two cells vary the mechanism: Bernoulli mixing, and a machine share that rises
  with `D`.
- **Help** is Bernoulli with a logged probability, constant 0.3 by default and targeted on the previous
  day's composite in two cells.
- **Version change.** Indicators 2 and 6 shift by +0.5 in mean with loading x0.7, logged for half of
  family AV; family AV2 applies the same change to indicators 1 and 4, never logged.
- **Criterion.** `Y_t = D_t + e_Y`, reliability 0.7, valid by construction. Response probability falls
  with `D` at rate `m1` (0 by default; 0.5 and 1.5 in two cells).

**Families.** S (stable), DR (drift), VA (vacation), SP (workload sprint), BI (broken integration), AV
(version change), DE (disengagement), DV (drift overlapping a vacation), CS (context shift, no state
change), BD (drift inside the baseline), AV2 (unlogged version change). AV and DV were not used for
tuning. CS, BD and AV2 are families the fixed rule was not designed for.

**Cells.** A default cell plus one-at-a-time variations: `kappa = 0.3`; `m1 = 0.5`; `m1 = 1.5`;
targeted help; targeted help with `theta1 = 0.5`; Bernoulli mixing; machine share rising with `D`.

### 3.3 Candidate scoring rules

Every rule averages within-person z-scores of the available indicators into a daily composite and runs
a one-sided CUSUM, `S_t = max(0, S_{t-1} + C_t - k)`, `k = 0.5`, with a reset and a 14-day refractory
period after a flag and `S` held on days with no usable indicator. The threshold `h` is tuned per rule
on family S (tuning seed 20260927) to one false flag per six tracked person-months.

- `pop`: population rather than personal z-scores.
- `A-naive`: personal baseline, all indicators on every used day, all user-role text in indicators 4
  and 5, no workload term, no reset, no abstention.
- `A-fixed`: `A-naive` plus (i) indicators 2 and 3 on unhelped days only; (ii) indicators 4 and 5 from
  text an authorship filter labels human (sensitivity 0.9, specificity 0.95 for machine text); (iii)
  timing and friction indicators residualized on observed workload; (iv) reset and a 14-day
  re-baseline at a logged version change; (v) abstention when 14-day usage falls below 40 percent of
  the baseline rate. Ablations remove each component in turn.
- `probe-only`: a CUSUM on criterion answers alone, random schedule, matched budget.

Context is not adjusted by any rule; family CS measures that cost. A language-model evidence reader is
specified as future work and not run, so it is not compared. Tuned thresholds (`sim/tuning.json`):
`h` = 1.125 (`pop`), 1.739 (`A-naive`), 3.334 (`A-fixed`), 6.539 (`probe-only`).

### 3.4 Criterion-sampling designs

Each design except `none` includes a fixed baseline block of four criterion occasions (days 7, 14, 21
and 28). The budget target is 3.0 occasions per person-month after the baseline.

- `none`;
- `fixed`: every 10 days;
- `random`: each day with probability 0.1;
- `triggered`: with probability `p_trig` on days when `S` lies in [h/2, h);
- `mixed`: a random floor of 0.04 per day plus `p_trig'` in the same band;
- `current` (a construction check, not a prediction): on days when the current composite exceeds `c*`.

Every occasion's selection probability is logged. Inverse-probability weighting is identified only
for `random` and `mixed`; for `triggered` and `fixed` it is reported as not identified, because some
days have zero probability. A flag counts as confirmed if a criterion occasion within the next 7 days
reads at least 0.5 above the person's baseline-block mean.

Tuned values: `p_trig = 1.0`, `p_trig' = 0.795`, `c* = 0.956`. The `triggered` design cannot reach the
budget even at `p_trig = 1.0` (realized 2.265 per person-month on the tuning mix); `mixed` and `current`
reach 3.0.

### 3.5 Metrics

Sensitivity within 21 days of onset and median days to flag; false flags per tracked and per total
person-month in every family, with the spread across persons; abstention share with reasons; realized
criterion occasions per person-month; for the confirmation rule, positive predictive value; on
criterion occasions, the person-centred slope and correlation of criterion on composite against the
all-days values, unweighted and weighted where identified; and a sensitivity against false-flag curve
from sweeping `h`. Monte Carlo standard errors are reported beside every number.

### 3.6 Predictions

A prediction holds if its 95 percent Monte Carlo interval lies beyond the stated threshold in the
default cell unless another cell is named. A failed prediction is reported as failed, and nothing is
re-tuned after scoring.

P1 to P3 are pipeline construction checks: they test whether each component of `A-fixed` does what it
was built to do, and they are not findings. **P1**: `A-naive` has at least 2x `A-fixed`'s false flags on
SP, confirmed by the ablation without (iii), and 0.5x to 2x on VA, DE and BI. **P1b**: `A-fixed`'s DE
false flags per total person-month are at most 1.5x its S rate. **P2**: under targeted, state-dependent
help, `A-naive`'s DR sensitivity is at least 10 points below `A-fixed`'s, and removing (i) accounts for
at least half of the gap. **P3**: removing (iv) at least doubles false flags on logged AV persons, and
`A-fixed`'s false flags on AV2 are at least 2x its S rate.

The predictions proper:

- **P4 (criterion sampling).** With `m1 = 0`, the trigger-only design deflates the person-centred
  correlation of criterion on composite by at least 0.05 and attenuates the slope by at least 10
  percent relative to all days. Under `mixed`, weighting by the logged propensity recovers both within
  0.03.
- **P5 (criterion non-response).** At `m1 = 0.5`, slope bias under `random` is under 5 percent. At `m1 =
  1.5`, the added slope bias is at least 10 percent under every design, and a response-propensity weight
  estimated from observables removes less than half of it.
- **P6 (authorship).** With machine share independent of `D`, indicators 4 and 5 match the attenuation
  formula of section 2.2 within 0.03, unfiltered and (with the residual share) filtered; the Bernoulli
  cell matches ghost-respondents E7 at `c = 0`; and when the machine share rises with `D`, indicator 4's
  validity exceeds the formula by at least 0.05.
- **P7.** `A-fixed`'s DV sensitivity is at least 15 points below its DR sensitivity.
- **P8.** At matched false flags and budget, `A-fixed`, which uses no criterion answers, has DR
  sensitivity at least 10 points above `probe-only` and a restricted mean time to flag (censored at 42
  days) at least 3 days shorter. Combining passive and criterion data is not tested.
- **P9.** On BD, `A-fixed`'s sensitivity in days 29 to 49 is at most half its DR sensitivity.
- **P10.** On CS, `A-fixed`'s false flags are at least 1.5x its S rate, because context is not adjusted.

At `pi_bar = 0.845`, the filter's residual share is `pi' = 0.365` (PREREG), so the filtered indicator 4
is diluted, not cleaned. The PREREG also records that the fixed mixing distribution implies a day-level
SD of 0.109 against 0.174 in the pilot; this is carried forward uncorrected.

### 3.7 Deviations recorded before the freeze

The PREREG lists five, all before any evaluation-seed run: (1) a construction check on the `current`
design fails for drift persons (slope moves 6.0 percent against a 5 percent bound) and is reported as
failed; (2) `triggered` cannot meet the budget, and P4 does not depend on budget matching; (3) the
scoring function was called once on a non-evaluation seed for timing, with outputs reported deleted
unread; (4) conventions the spec left open, including that P4 to P6 are scored on family S; (5)
`probe-only`'s `h` was re-tuned so that tuning and scoring use the same schedule (12.206 to 6.539).

### Results [PENDING RUN 2]

[SIM RESULTS: P1 to P10 with Monte Carlo intervals, per family and cell; ablations; sensitivity against
false-flag curve; abstention shares; criterion-sampling calibration table. To be filled from
`sim/results.json` after run 2, with any post-freeze change to scoring code listed as a deviation with
before and after values.]

---

## 4. A one-person corpus audit of the first link

### 4.1 Methods

**Data.** My own Claude Code transcripts under `~/.claude/projects/**/*.jsonl`, read only, in the
snapshot fixed by `pilot/trace_audit.py --until 2026-09-28T01:32:31Z`. The scan opened 2,280 of 2,281
files and parsed 75,145 user-role and 125,875 assistant-role entries with no parse errors; the 73,955
user-role entries on or before the snapshot time are the denominator below.

**Metadata only.** Per entry: timestamp, session, project, role, sidechain and meta flags, native
provenance fields, harness version, model id, content length, and an authorship class. Tool-result
payloads are never read. Assistant text is used only in memory for the paste check and then discarded.

**Authorship classes**, in priority order: `sidechain` (subagent traffic); `tool-result`; `injected`
(native provenance where present, otherwise structural markers of harness and hook text); `human+paste`
or `injected` for entries with a paste marker, depending on whether typed text remains outside it;
`lane-prompt` (a session's first entry matching a stored automated-lane prompt); and `human-typed`
for the rest. `promptSource` is present on 4.5 percent of user entries and `turnOrigin` on 2.1
percent, so the classifier rests mostly on markers.

**Other signals.** A paste-marker flag; whether a typed entry shares a 200-character span with one of
the session's last five assistant turns; whether a tool's name matches a messaging, calendar or email
keyword. Sessions are `autonomous` (no typed entry), `mixed` or `interactive`.

**Indicators.** Late-activity share (entries between 00:00 and 05:00 local), session fragmentation
(distinct sessions per active hour) and message length (mean log characters), each in a naive version
(all user-role entries) and a filtered version (`human-typed` only). The audit reports how far the two
disagree and never the level of a filtered series, which is the nearest thing in the pipeline to a
behavioural signal about the person. Indicator 5 needs text content and was not computed.

**Change points.** Days with a typed entry were split chronologically at 70 percent (cutoff
2026-09-21). Change points were found on training days by penalized binary segmentation and checked
against independently dated infrastructure events: harness versions, model ids, dated configuration
backups, dated policy sections and hook modification times. Only dates and matches are kept.

### 4.2 Results

**Who wrote the "user" stream.**

| class | share of entries | share of characters |
|---|---:|---:|
| tool-result | 0.655 | 0.550 |
| sidechain | 0.262 | 0.341 |
| injected | 0.071 | 0.091 |
| lane-prompt | 0.003 | 0.004 |
| human-typed | 0.0093 | 0.0144 |
| human+paste | 0.000 | 0.000 |

Of 73,955 user-role entries, 688 were classed as typed by me. On the main thread (sidechain excluded),
the machine share of text-bearing entries is 0.888 by entry and 0.845 as a day mean, with a day-level
SD of 0.174 over 24 days; with sidechain traffic, the day-mean share is 0.929. Machine text is 0.274
within-person SDs longer than typed text on average, with a variance ratio of 0.547. These are the
values the simulation's indicator 4 takes.

**Person-absent sessions.** Of 1,544 main sessions, 1,303 (0.844) had no typed entry, 20 were mixed and
221 interactive. The autonomous sessions supplied 0.570 of all naive user-role entries, 0.750 of the
entries between 00:00 and 05:00, and 0.746 of the session-by-hour units behind the fragmentation
indicator. Three quarters of the naive timing signal comes from sessions in which no person typed.

**Naive against filtered.** Over the 21 days with both series:

| indicator | correlation, naive vs filtered | mean absolute difference |
|---|---:|---:|
| late-activity share | 0.90 | 0.081 |
| session fragmentation | 0.12 | 2.62 sessions per active hour |
| message length (mean log chars) | 0.28 | 1.21 |

The correlations were 0.94, 0.15 and 0.38 on the 15 paired training days and 0.90, -0.30 and 0.78 on
the 6 paired test days; 6 days are too few to read the difference as a change. On 3 of 24 active days
the naive series had data and the filtered series had none. The naive fragmentation series is nearly
unrelated to the filtered one; it largely counts how many automated sessions were running. Late
activity agreed best over this window, although three quarters of its naive entries came from
autonomous sessions, so the agreement is a property of this window and not a guarantee.

**Pastes, agent drafts, third parties.** 0.30 percent of user-role entries carried a paste marker, and
none was classed `human+paste`: under the classifier's rules, such an entry is classed as injected
when no typed text remains outside the paste, or takes an earlier class. None of the 688 typed entries
shared a 200-character span with one of the session's last five assistant turns, a bounded check that
misses pastes from older turns, other sessions and other applications. 0.77 percent of tool results
came from a tool whose name matched a messaging, calendar or email keyword, a structural estimate of
third-party content and not a count of other people.

**Infrastructure churn and change points.** The snapshot has 7 harness versions and 10 model ids, and
27 dated infrastructure-event candidates in all. The training period yielded 8 change points across
the six series, and all 8 fell within 3 days of a candidate event. The base rate makes that
uninformative: every calendar day in the observed range (share 1.00) has a candidate within 3 days. The
match attributes no change point to any event, and an unmatched change point would not indicate a
change in the person either. What the base rate shows is the design problem: in this corpus, every
change in a trace-derived series has a plausible infrastructure explanation nearby.

**Data density.** 24 days had user-role activity and 21 had a typed entry, one in August and the rest
in September 2026.

### 4.3 Limitations of the audit

- **n = 1, descriptive.** One person's corpus, and that person also wrote the audit, the lanes behind
  most of the machine text, and the harness configuration. The shares describe this corpus, not any
  population, and they reflect how much automation this user runs.
- **Dictation.** Dictated text is indistinguishable from typed text at the metadata level, and both
  land in `human-typed`. It is the person's text, so the machine share is unaffected, but message length
  and latency mean different things for the two input modes, and the typed share cannot be split.
- **Other unseen channels.** Messages relayed from a phone or another client look like desktop typing.
  An automated lane whose prompt was never stored is classed as typed, so the typed share is an upper
  bound on that account. The marker `hook success` is short and could misclassify a real message; no
  such case was checked.
- **Retention.** The harness setting `cleanupPeriodDays` is 45 in `~/.claude/settings.json`, so
  transcripts older than 45 days are deleted on a rolling basis. Only 24 active days existed at the
  snapshot. Any longitudinal analysis of this corpus, including anything that looks like within-person
  change, is capped by that setting (decision slate D12, open).
- **Scope of indicators.** Three of six indicators were computed. Indicator 5 needs content analysis,
  which this audit does not do. Machine-share parameters were estimated for indicator 4 only.
- **No labels.** No state was estimated and no label was made or inferred. The audit bears on link 1
  only.

---

## 5. What a validation study would need

These requirements follow from sections 2 to 4. They describe a future study with consenting
participants. Nothing here has been built, and none of it describes a product.

**R1. Entry-level authorship provenance.** Every entry needs a recorded source: typed, dictated, pasted,
injected by the harness, returned by a tool, sent by an automated process, or produced by a subagent.
Markers are a weak substitute; the native fields covered under 5 percent of entries in section 4.
Person-absent sessions need their own class, timing indicators should use person-present sessions only,
and provenance coverage should be reported by period.

**R2. Logged, randomized help.** Help delivered with a known, logged probability, so that its effect
can be separated from the state (Klasnja et al., 2015; Nahum-Shani et al., 2018). The agentSEM results
in section 2.3 point to a constant rather than targeted help probability and to scoring friction
indicators on unhelped days, with a carryover check on next-day indicators.

**R3. Logged agent and model versions.** Every entry carries the harness version and model id, and
every change is dated; the pilot saw 7 versions and 10 model ids in about a month. The handling of a
logged change is pre-specified, and unlogged changes are expected (family AV2).

**R4. A stated baseline and abstention policy.** The baseline window, change inside it, days without
use and the rule for declining to score are fixed before data and reported with their coverage cost.

**R5. A random criterion floor with logged propensities.** Every day has a known, non-zero probability
of a criterion occasion, and every occasion's probability is logged. A score-based trigger may be
added, but validity estimates are then weighted by the logged propensity and also reported unweighted.
The criterion is an independent, validated self-report or clinician rating in a consented study.
Criterion non-response is modelled, and its dependence on the trace score reported.

**R6. Retention sized to the question.** A within-person change study needs months of history per
person, including a clean baseline; 45-day retention does not allow it. What is retained (metadata or
text), and for how long, is a consent question as well as a design question.

**R7. Within-person designs.** Enough occasions per person to estimate within-person relations, and an
analysis that separates within-person from between-person variation (Curran and Bauer, 2011; Hamaker et
al., 2015). Accuracy across persons is not evidence for links 2 or 3.

**R8. Consent and scope.** Participants consent to the specific data surfaces, the retention period and
the criterion schedule. Other people's content in a participant's stream (pasted messages, results from
messaging or email tools) is excluded or separately cleared; section 4's estimate is structural only,
and a content-level pass could find more or less. It has been proposed that inferences about mental
state be governed the same way whatever their source, text included (Horiuchi, 2026, read at abstract
level only). The study's outputs are research data; any feedback to participants falls under section 7.

---

## 6. Limitations and scope

These limits bind the whole paper.

1. **One latent state, not a condition.** The simulated state `D` is a single, non-clinical wellbeing
   and functioning variable. Nothing in the simulation maps to any clinical condition, and no condition
   is a target or a result anywhere in this work.
2. **Invented parameters.** Every loading, help effect, context effect, usage dependence and workload
   loading (`lam`, `psi`, `eta`, `kappa`, `gam`) in the generator is invented. Only indicator 4's mixing
   parameters come from data, and from one person. Every sensitivity, false-flag rate and bias the
   simulation reports is conditional on these values.
3. **Help moves indicators only.** In the generator, help changes indicators and never changes `D`.
   Nothing in this paper bears on whether an agent's intervening helps or harms anyone.
4. **The criterion is valid by construction.** `Y = D + e`. Real criteria have their own validity
   questions, and the simulation does not model them.
5. **The false-flag target is high.** One false flag per six tracked person-months is a tuning target
   for comparing rules, and it is high for any setting in which a flag would reach a person. The
   sensitivity against false-flag curve is reported alongside it so that other operating points can be
   read off.
6. **One rule is not compared.** A language-model evidence reader is described as future work and not
   run, and no conclusion about it is drawn.
7. **The corpus audit is n = 1 and descriptive.** It measures authorship contamination in one person's
   transcripts over 24 active days and estimates nothing about that person.

Two further limits follow from the design. The simulation compares passive-only and criterion-only
rules (P8) and does not test combining them. And agentSEM Study 2 S1
(`~/code/agentsem-study2-integration`, commit `41d6774`) found no resolved difference between fixed,
random and passive-informed budget rules for when to ask rather than infer, at 300 to 1,000
person-weeks, on item-level error; the schedules here are timed by a CUSUM and judged on calibration and
detection, so that null is context, not a result this paper extends.

---

## 7. Translational note

**Translational paragraph (the only one in this paper).** If a future consented study established the
chain in section 2, the method could inform research on wellness-oriented tools that track trends and
baselines over time, looking for within-person change from a person's own baseline in behavioural
patterns. Such a tool may help people notice changes worth discussing with a professional. When the
patterns it tracks move outside their usual range, it could let the person know that talking with a
healthcare professional might be helpful,
without naming any condition, labeling the change as abnormal, or recommending any treatment. Signals of this kind are screening-level; any individual-level
concern warrants professional evaluation. **This is a measurement method, not a diagnostic instrument.
Score changes are screening-level signals. No clinical inference about any individual should be drawn
without professional assessment.** The current regulatory line between general wellness software and a
regulated device is drawn by intended use as stated in claims (FDA, 2026), and nothing in this paper
states an intended use.

---

## References

Status tags: [VERIFIED] means a primary page was opened and matched, per the lane's citation files;
[VERIFIED, summary] means verified through a search or fetch summary rather than a full read;
[unverified] means the listed reason in the source file applies. Sources: `paper-citations.md`,
`prior-art-passive.md` and `lit-verify.md` in `~/lanes/bridge-jobs/agentsem-overnight-20260927/`.

- AERA, APA and NCME (2014). *Standards for Educational and Psychological Testing.* American Educational Research Association. [VERIFIED]
- Anthropic (2025, June 27). How people use Claude for support, advice, and companionship. anthropic.com/research. [VERIFIED]
- Begg, C. B., and Greenes, R. A. (1983). Assessment of diagnostic tests when disease verification is subject to selection bias. *Biometrics*, 39(1), 207-215. [VERIFIED] <!-- cite: -->
- Bolger, N., and Laurenceau, J.-P. (2013). *Intensive Longitudinal Methods: An Introduction to Diary and Experience Sampling Research.* Guilford Press. [VERIFIED]
- Borsboom, D., Mellenbergh, G. J., and van Heerden, J. (2004). The concept of validity. *Psychological Review*, 111(4), 1061-1071. [VERIFIED]
- Curran, P. J., and Bauer, D. J. (2011). The disaggregation of within-person and between-person effects in longitudinal models of change. *Annual Review of Psychology*, 62, 583-619. [VERIFIED]
- Eichstaedt et al. (2018). Facebook language predicts depression in medical records. *PNAS*. doi:10.1073/pnas.1802331115. [VERIFIED, summary] <!-- cite: -->
- FDA/CDRH (2026, January 6). *General Wellness: Policy for Low Risk Devices.* Guidance for Industry and FDA Staff. fda.gov/media/90652/download. [VERIFIED]
- Hamaker, E. L., Kuiper, R. M., and Grasman, R. P. P. P. (2015). A critique of the cross-lagged panel model. *Psychological Methods*, 20(1), 102-116. [VERIFIED]
- Helmich, Smit, Bringmann, Schreuder, Oldehinkel, Wichers, and Snippe (2023). Detecting impending symptom transitions using early-warning signals in individuals receiving treatment for depression. journals.sagepub.com, doi:10.1177/21677026221137006. [VERIFIED, summary] <!-- cite: -->
- Horiuchi, S. (2026). Governing mental-state inference: Source-neutral regulatory triggers and tiered obligations. arXiv:2608.00936. [VERIFIED, abstract only]
- Kane, M. T. (2013). Validating the interpretations and uses of test scores. *Journal of Educational Measurement*, 50(1), 1-73. [VERIFIED]
- Klasnja, P., Hekler, E. B., Shiffman, S., Boruvka, A., Almirall, D., Tewari, A., and Murphy, S. A. (2015). Microrandomized trials: An experimental design for developing just-in-time adaptive interventions. *Health Psychology*, 34(Suppl), 1220-1228. [VERIFIED]
- Lathia, N., Rachuri, K. K., Mascolo, C., and Rentfrow, P. J. (2013). Contextual dissonance: Design bias in sensor-based experience sampling methods. *UbiComp '13.* [VERIFIED]
- Lawley, D. N. (1944). A note on Karl Pearson's selection formulae. *Proceedings of the Royal Society of Edinburgh, Section A*, 62(1), 28-30. [VERIFIED; volume year 1944]
- Messick, S. (1995). Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning. *American Psychologist*, 50(9), 741-749. [VERIFIED]
- Mettu, A. (2026). Ghost respondents: A boundary map for covert AI authorship in open-ended survey data. Working paper, draft 2, `~/code/ghost-respondents/paper/GHOST-RESPONDENTS-DRAFT.md`, section 2.2 (E5, E7). [own work, unpublished]
- Mettu, A. agentSEM Study 1a, helpful-agent trap. `~/code/agentsem-trap-world`, commit `21ec751`, `MORNING-HANDOFF.md`. [own work, unpublished]
- Mettu, A. agentSEM Study 2 S1, budget-rule power comparison (synthetic). `~/code/agentsem-study2-integration`, commit `41d6774`. [own work, unpublished]
- Mettu, A. agentSEM Study 5, D3 falsification simulation. `~/code/agentsem-study5-feasibility`, commit `3dfe3c2`, `FALSIFICATION-PLAN.md`. [own work, unpublished]
- Nahum-Shani, I., Smith, S. N., Spring, B. J., Collins, L. M., Witkiewitz, K., Tewari, A., and Murphy, S. A. (2018). Just-in-time adaptive interventions (JITAIs) in mobile health: Key components and design principles for ongoing health behavior support. *Annals of Behavioral Medicine*, 52(6), 446-462. [VERIFIED]
- OpenAI and MIT Media Lab (2025). Investigating affective use and emotional well-being on ChatGPT. arXiv:2504.03888. [VERIFIED, summary]
- Page, E. S. (1954). Continuous inspection schemes. *Biometrika*, 41(1-2), 100-115. [VERIFIED]
- Pearson, K. (1903). Mathematical contributions to the theory of evolution. XI. On the influence of natural selection on the variability and correlation of organs. *Philosophical Transactions of the Royal Society of London, Series A*, 200, 1-66. [VERIFIED]
- Rubin, D. B. (1976). Inference and missing data. *Biometrika*, 63(3), 581-592. [VERIFIED]
- Sackett, P. R., and Yang, H. (2000). Correction for range restriction: An expanded typology. *Journal of Applied Psychology*, 85(1), 112-118. [VERIFIED]
- Shen and Han (2026). The reliability illusion in synthetic patients. *Proceedings of CLPsych 2026.* aclanthology.org/2026.clpsych-1.7. [VERIFIED]
- Tao, R., Mercaldo, N. D., Haneuse, S., Maronge, J. M., Rathouz, P. J., Heagerty, P. J., and Schildcrout, J. S. (2021). Two-wave two-phase outcome-dependent sampling designs, with applications to longitudinal binary data. *Statistics in Medicine*, 40(8), 1863-1876. [VERIFIED]
- Thorndike, R. L. (1949). *Personnel Selection: Test and Measurement Techniques.* Wiley. [VERIFIED for existence, author, publisher and year; Case II and Case III labels unverified against the 1949 text]
- Tieleman, O., Zhu, Z., Su, T., Bell, S. J., Hull, T. D., and Stamatis, C. A. (2026). Fine-tuning LLMs for passive depression severity estimation from AI mental health dialogue. arXiv:2606.17973. [VERIFIED] <!-- cite: -->
- Varadarajan, V., Sikström, S., Kjell, O., and Schwartz, H. A. (2024). ALBA: Adaptive language-based assessments for mental health. *NAACL 2024.* aclanthology.org/2024.naacl-long.136. [VERIFIED]
- Varadarajan, V., Xu, H., Boehme, R. A., Mirstrom, M. M., Sikström, S., and Schwartz, H. A. (2026). MAQuA: Multi-outcome adaptive question-asking for mental health using item response theory. *EACL 2026.* aclanthology.org/2026.eacl-long.313. [VERIFIED]
- Xu et al. (2023). GLOBEM: multi-year, multi-site passive-sensing and wellbeing dataset and cross-dataset generalization benchmark. arXiv:2211.02733; *IMWUT / UbiComp 2023.* doi:10.1145/3569485. [VERIFIED, summary]
- Yun, H. S., Arjmand, M., Sherlock, P., Paasche-Orlow, M. K., Griffith, J. W., and Bickmore, T. (2024). Keeping users engaged during repeated administration of the same questionnaire: Using large language models to reliably diversify questions. *ACM IVA 2024.* arXiv:2311.12707. [VERIFIED]
- Zhou, H., Weaver, M. A., Qin, J., Longnecker, M. P., and Wang, M. C. (2002). A semiparametric empirical likelihood method for biased sampling schemes with auxiliary covariates. *Biometrics.* [unverified: found via search snippets only; volume and pages not confirmed]

---

## Open items for the author

1. **Affiliation, address, acknowledgements** are placeholders.
2. **Simulation results.** Section 3 has no results; the abstract has [SIM RESULTS]. Score run 1 at the
   freeze is preserved but was flagged by an audit before reporting (receipts, 21:22), and run 2 is
   pending. Any code fix between the freeze and run 2 must be listed in section 3.7 as a post-freeze
   deviation with before and after values.
3. **Monte Carlo SE denominator.** The PREREG says 1,000 persons per family per cell but gives the MC SE
   as the SD across persons over sqrt(200). The draft does not repeat the formula. Decide which is
   intended and state it.
4. **Triggered and event-contingent sampling prior art.** Spec N2 requires reading this literature
   before the paper calls the dynamic-trigger case new. Only searches exist. Unread items include
   arXiv 2609.06269 (adaptive EMA with a hybrid language model, search-only), the per-decision
   inverse-probability-weighting literature for micro-randomized trials (no single confirmed citation),
   and a PMC paper recasting Case III as collider bias (PMC11187666, authors and venue unconfirmed).
   None of these is cited in the body.
5. **Thorndike Case II and III labels** are confirmed only in secondary sources; the body carries an
   [unverified] tag. A primary check, or citing Sackett and Yang (2000) alone for the labels, would
   remove it.
6. **Zhou et al. (2002)** is tagged [unverified]; confirm or drop.
7. **Horiuchi (2026)** was read at abstract level only; whether it addresses general-purpose assistants
   is unconfirmed.
8. **Pilot parameters for indicators 1 and 2.** Spec section 7 asks for `pi`, `kappa` and `delta` for
   indicators 1, 2 and 4; `pilot/indicator4_params.json` has indicator 4 only. Section 4 reports the
   autonomous-session shares for the timing indicators instead.
9. **Pasted-draft window.** Spec section 7 describes the paste check as matching an earlier assistant
    message in the session; the implementation checks the last five assistant turns. Section 4 reports
    what was implemented; the spec text should be reconciled.
10. **Retention (slate D12).** Whether to raise `cleanupPeriodDays` above 45 is open. It caps any
    longitudinal own-corpus work and every day of delay loses the oldest day.
11. **Dictation share.** The share of typed-class entries that were dictated is unknown from metadata.
    If it matters for the length and latency indicators, a source-level record is needed (R1).
12. **External registration.** The freeze is a hashed commit in a local repository, not an external
    registry, and run 1 was already scored at it, so an external registration now would post-date
    scoring. Decide whether "pre-registered" should read "frozen and hashed before scoring".
13. **Figures.** Spec section 10 says visuals become paper figures. None exist yet. Candidates: the
    class-share bar, the autonomous-session share of each naive indicator, the change-point base-rate
    plot, and the sensitivity against false-flag curve after run 2.
14. **Venue and length.** Target venue not chosen. The body is about 6,950 words by whitespace count
    (tables and formulas included), excluding references; results from run 2 will add to it.
