# Spec 001: the drift layer. Passive within-person change detection with sparse probes in a general-purpose agent

Status: v3, FREEZE WITH EDITS applied (E1 to E14 from the v2 diff check, verbatim). Frozen as sim/PREREG.md once the pilot supplies pi_bar, kappa_a and mu_M4 for indicator 4. Earlier: DRAFT v2. The Opus design review (opus-design-review.md in the lane dir) said DO NOT FREEZE with 15 required edits; R1 to R15 are applied here. Freeze follows a diff check.
Base: `/tmp/selfreport-build-brief.md` (auditor brief, 2026-09-27), copied to
`~/lanes/bridge-jobs/agentsem-overnight-20260927/selfreport-build-brief.md`. This spec extends it and does
not restate it.

## 0. Framing (his words, 2026-09-27 20:01 CDT, relayed)

Self-report administration is not the point. The agent should assess a person naturally and
unofficially from their normal use, plus occasional nudges and specific questions, so it knows how to
intervene: notice wellbeing and functioning drift early, or at least not make it worse.

**Framing ruling (his words, 2026-09-27 21:02 CDT, relayed): no clinical diagnosis claims anywhere in the drift work;
diagnosis has its own regulations. Frame it as helping people: a drift signal with a referral and
intervention orientation.** Until the separate regulatory-boundary note (general wellness vs clinical
claims) lands, every artifact uses conservative non-diagnostic language. No condition names are used as
targets, no screening or severity claims are made, and outputs are support suggestions, never assessments.

Read as a research object: **the loop** (observe, quantify uncertainty, ask rarely, act reversibly),
evaluated as measurement. The target is *within-person change from the person's own baseline*. It is
not a diagnosis, not a screening result, and not a between-person score of any condition.

## 1. What this adds to the agentSEM program (and what it does not redo)

| already in the program | where | used here as |
|---|---|---|
| helpful-agent trap: help moves the indicator | Study 1a (`agentsem-trap-world`) | a scenario channel; unhelped-day scoring is the fix, cited not re-derived |
| ask-versus-infer budget rules (fixed / random / passive-informed) | Study 2 S1 (`agentsem-study2-integration` 41d6774): item-level RMSE, "no rule difference resolved at 300-1000 person-weeks" | context. The schedules here differ: they are timed by a CUSUM trigger and judged on calibration and detection, not on RMSE |
| task friction under micro-randomized help; unhelped-day scoring holds under state-dependent help (`theta1`) | Study 5 sim (`agentsem-study5-feasibility` 3dfe3c2) | the friction indicators' DGP shape; the `theta1 = 0.5` cell is carried here |
| contamination attenuation `Att` (E5/E7; Props 1 to 3 at `c = 0`) | ghost-respondents day-1 derivations | the authorship-contamination formula for indicators 4 and 5 (P6) |

New here, with the known results each applies:

- **N1. General-purpose-agent indicators across contexts.** Coding, writing and personal use in one
  stream. Indicator non-invariance at agent/model version changes, logged and unlogged.
- **N2. Probe-schedule calibration.** A trigger on a statistic of past composites biases the slope,
  because past composites predict current state beyond today's composite. A band trigger also restricts
  range and so deflates the correlation. A random floor plus IPW on the logged propensity recovers the
  population value; without IPW it does not. This applies Pearson (1903), Lawley (1944) and Thorndike
  Cases II and III, and it is structurally verification bias (Begg & Greenes 1983, Biometrics 39:207-215)
  moved to a dynamic trigger. It is a known result in a new setting, not a discovery (paper-citations.md, 2026-09-27). Triggered/event-contingent EMA prior art
  must be read before the paper calls N2 new (prior-art gap c is search-only so far).
- **N3. Authorship contamination of the user's own trace.** A share of "user" text is machine-authored:
  pasted agent drafts, hook and system injections, autonomous-lane prompts. Autonomous sessions also
  contaminate timing indicators at the session level. This is measured on real metadata (the pilot), and
  the simulation takes `pi`, `kappa` and `delta` for indicator 4 from it.
- **N4. Negative-control casebook**, including families the fixed architecture was not designed for.

## 2. Deliverables

D1. `sim/drift_sim.py`: case generator and architectures, numpy only. `--check` self-test.
D2. `sim/PREREG.md`: this spec's sections 3 to 6 verbatim plus the tuned values, committed and hashed
    before scoring. Evaluation seeds are derived from that hash. Results go to `sim/results.json` and
    `sim/RESULTS.md`.
D3. `pilot/trace_audit.py`: metadata-only audit of Abhay's own Claude Code transcripts, plus
    `pilot/INVENTORY.md` (section 7). Aggregates only; per-message table in gitignored `data/`.
D4. `demo/`: offline, non-sending static HTML that replays fictional cases (section 9, stage 1).
D5. `paper/DRAFT.md`: methods paper, every number traced to an artifact. **Binding framing guards:**
    (1) one latent, non-diagnostic wellbeing/functioning state `D`; nothing in it maps to any clinical
    condition, and no condition name appears as a target or result; (2) every `lam`, `psi`, `eta`, `kappa`, `gam` is invented, and all
    sensitivities are conditional on them; (3) help moves indicators only, never `D`, so nothing here
    bears on whether intervening helps or harms; (4) the probe is valid by construction (`Y = D + e`);
    (5) the false-alarm target of 1 per 6 person-months is high for a deployed product, and a sensitivity
    vs false-alarm curve is reported alongside it; (6) architecture B is not compared; (7) the pilot is
    n = 1 and descriptive.
D6. Receipts and the decision slate in the lane dir.

## 3. Generator (D1)

Per person: 140 days; days 1 to 28 are the baseline window. **1000 persons per family per cell.** Every architecture and schedule runs on the same simulated persons, and differences use a paired person bootstrap.
Persons are the replicates; the Monte Carlo SE is the SD across persons over sqrt(200), or a
2000-draw person bootstrap for ratios. The MC SE is reported beside every number.

- Latent state `D_t` (standardized, within-person): AR(1), `phi_D = 0.7`, marginal SD 1. Drift families
  add a ramp from onset `t0 ~ U[50, 100]` to `+delta_D = 1.0` over `ramp ~ U[7, 21]` days, then hold.
  Family BD puts the onset at `t0 ~ U[10, 25]`, inside the baseline.
- Workload `L_t`: AR(1) with `phi_L = 0.8`, marginal SD 1; SP adds a +1.5 SD block of 10 to 14 days.
  **Observed workload** `L_obs = L + N(0, 0.25)` (variance 0.25).
- Context `ctx` per day in {code, write, personal}, multinomial with base shares (0.5, 0.3, 0.2). The
  personal share's logit rises by `eta = 0.1` per SD of `D`. Family CS switches base shares to
  (0.1, 0.2, 0.7) from a random day in [50, 100], with no state change.
- Usage: a day is used with probability `expit(a0 - kappa * D_t - 4 * vacation_t - 2 * diseng_t)`, with
  `a0 = logit(0.8)`. Default `kappa = 0`; cell `kappa = 0.3`. DE lowers usage (`diseng_t = 1` from a
  random day in [50, 100]) with no state change.
- Indicators on used days, j = 1..6: 1 late-activity share, 2 session fragmentation, 3 deferral/abandon
  rate, 4 message length (log chars of user-role text), 5 negative self-reference rate, 6 reply latency.
  Human-generated value: `H_jt = lam_j D_t + gam_j L_t + beta_j[ctx_t] - A_t psi_j (1 + theta1 D_t) + e_jt`,
  `e ~ N(0, 1)`. `lam_j ~ U[0.25, 0.5]` is drawn per person and indicator. `gam = (0.3, 0.3, 0.3, 0, 0, 0.3)`.
  `beta_j[ctx]` takes the values (0, 0.3, 0.6) for code/write/personal on indicators 1, 4 and 5, and 0
  elsewhere. `psi = 0.5` on indicators 2 and 3 only. Default `theta1 = 0`; cell `theta1 = 0.5`.
- **Authorship mixing (indicators 4, 5), stated mechanism: daily averaging.** The observed value is
  `X_jt = (1 - pi_t) H_jt + pi_t M_jt`, with agent-text value `M_jt ~ N(mu_Mj, kappa_a)` independent of
  `D`, so `c = 0`. `pi_t ~ Beta(10 pi_bar, 10 (1 - pi_bar))`, so Var(pi) = pi_bar (1 - pi_bar) / 11, `pi_bar`, taken from the pilot's human-typed vs other share
  for indicator 4 (default 0.2 until the pilot lands, then replaced before the freeze), `kappa_a` (default 0.5) and `mu_M4` (default +1.0; agent drafts are longer) are replaced by the
  pilot's indicator-4 estimates before the freeze, as `pi_bar` is. Indicator 5's `kappa_a = 0.5` and `mu_M5 = -1.0` (agent text has near-zero negative
  self-reference). Cells: Bernoulli mixing (`pi_t in {0, 1}`); `pi_t` rising with `D` (logit slope 0.5;
  delegation when the state is elevated).
- Agent help: `A_t ~ Bernoulli(p_t)`, `p_t` logged and clipped to [0.1, 0.9]. Default constant 0.3;
  cell targeted, `p_t = clip(expit(logit(0.3) + C_{t-1}), 0.1, 0.9)` (A-fixed's composite).
- Version change (AV): on a random day in [50, 100], indicators 2 and 6 shift in mean by +0.5 and in
  loading by x0.7. Logged for 50 percent of AV persons. Family AV2: the same change (+0.5 in mean, loading x0.7) on indicators 1 and 4, never logged.
- Broken integration (BI): indicators 1 and 6 are missing for 10 to 20 days from a random day in [50, 100].
- Probe answer `Y_t = D_t + e_Y`, reliability 0.7. Response probability `expit(logit(0.8) - m1 * D_t)`.
  Default `m1 = 0`; cells `m1 = 0.5` and `m1 = 1.5`. Probe reactivity is 0; the effect is not simulated.

**Families.** S stable; DR drift; VA vacation (7 to 14 days, from a random day in [50, 100]); SP sprint;
BI broken integration; AV version change; DE disengagement; DV drift with a vacation whose start is drawn from U[t0 - 5, t0 + 5]; CS context shift; BD drift inside the baseline; AV2 unlogged change on other indicators.

**Cells.** One default cell plus one-at-a-time variations: `kappa = 0.3`; `m1 = 0.5`; `m1 = 1.5`;
targeted help; targeted help with `theta1 = 0.5`; Bernoulli mixing; `pi_t` rising with `D`.

**Not used for tuning; mechanism known at design time:** AV, DV. **Not designed for:** CS, BD, AV2.
Evaluation seeds for every family are derived from the sha256 of the committed PREREG. Tuning uses the
separate seed 20260927.

## 4. Architectures and schedules

Missing-data handling (all architectures): the composite is the mean of the within-person z-scores of
the available indicators (baseline mean and SD per person); the composite is not re-standardized, and `k` is in its units. On a day with no usage, or no usable
indicator, the CUSUM statistic `S` is held.

- `pop`: z-scores against the population mean and SD taken from the S tuning run; the same CUSUM.
- `A-naive`: personal baseline over days 1 to 28, all six indicators on every used day, all user-role
  text counted in 4 and 5, no workload term, no reset, no abstention.
- `A-fixed`: A-naive plus:
  - (i) indicators 2 and 3 are used only on unhelped days;
  - (ii) indicators 4 and 5 are computed from text an authorship filter labels human, with the filter at
    se 0.9 / sp 0.95 for agent text;
  - (iii) indicators 1, 2, 3 and 6 are residualized on `L_obs` with a per-person slope fit in the
    baseline;
  - (iv) at a logged version change, `S` is reset and indicators 2 and 6 are re-baselined over the next
    14 days, during which `S` is held;
  - (v) the layer abstains (holds `S`) on days where the 14-day usage count is below 40 percent of the
    baseline rate.
  Context is treated as nuisance-with-signal and is not adjusted in either architecture; CS measures
  what that choice costs.
- **Ablations:** A-fixed minus each of (i) to (v), one at a time.
- `B` (LLM evidence reader): **not run.** No local model is installed (`ollama list` was empty on
  2026-09-27). It is specified in the paper as future work, not simulated with a stand-in.
- CUSUM: one-sided, `S_t = max(0, S_{t-1} + C_t - k)`, with `k = 0.5`. After an alarm, `S` resets to 0
  and a 14-day refractory period follows. `h` is tuned per architecture on S (tuning seed) to 1 false
  alarm per 6 tracked person-months.
- **Probe schedules** (on top of A-fixed). Every schedule except `none` has a fixed baseline block of
  4 probes (days 7, 14, 21, 28), counted in the budget.
  - `none`;
  - `fixed`: every 10 days after the baseline;
  - `random`: daily p = 0.1;
  - `triggered`: p_trig on days when `S` is in [h/2, h);
  - `mixed`: floor 0.04 plus p_trig' in the band;
  - control `current`: probe when `C_t > c*` (a `--check` item, not a prediction).
  The budget target is 3.0 probes per person-month after the baseline. p_trig, p_trig' and c* are
  tuned on a 50/50 S+DR mix (tuning seed), and the realized budget is reported per family. Every
  probe's propensity is logged. IPW is identified only for `random` and `mixed`; for `triggered` and
  `fixed` it is reported as "not identified" (positivity fails).
- **Confirmation rule:** an alarm is confirmed if a probe inside the next 7 days reads above the
  person's baseline-block probe mean by at least 0.5.
- **Probe-only comparator:** a CUSUM on the probe answers alone (z-scored on the baseline block),
  `random` schedule at the matched budget, with `h` tuned the same way.

**Tunables:** `k` 0.5, fixed a priori; `h`, tuned on S; the band [h/2, h), a priori; the 40 percent
abstention cut, a priori; the 0.5 confirmation margin, a priori; the 28-day baseline, a priori; the
14-day refractory and re-baseline, a priori; p_trig, p_trig' and c*, tuned on S+DR.

## 5. Metrics

- **Sensitivity** within 21 days of onset (DR, DV, BD). An alarm before onset counts as a false alarm.
  Abstention across the window with no alarm counts as a miss.
- **Median days to detect**, among detected.
- **False alarms** per tracked person-month and per total person-month, in every family (pre-onset
  days only in drift families).
- **Abstention share** of person-days, with its reasons; for DR, reported at `kappa = 0.3` against
  `kappa = 0`.
- **Probes** per person-month, by family.
- **Confirmation rule:** PPV of confirmed alarms, confirmed false alarms per person-month, days to
  confirmation.
- **Calibration** on probe days: person-centred (on the analysed days) slope of `Y` on `C` and their
  correlation, against the all-days values; unweighted and, where identified, IPW.
- **Sensitivity vs false-alarm curve**, by sweeping `h` on S and DR (default cell).
- **Spread** of person-level false-alarm rates (IQR), not only the mean.

## 6. Predictions (frozen with D2)

Each prediction holds if its 95% Monte Carlo interval lies beyond the stated threshold in the default
cell, unless another cell is named. A 'within X' prediction holds if its 95% MC interval lies inside ±X. It is reported per cell elsewhere. "Holds across the grid" is
claimed only if it holds in every cell. A failed prediction is reported as failed, and nothing is
re-tuned after scoring.

**Pipeline construction checks** (brief item 2; not findings, labelled as such in the paper):

- **P1.** False alarms per tracked person-month, A-naive against A-fixed, by family, with the
  component responsible named: SP at least 2x (iii, workload); VA and DE within 0.5x to 2x (holding `S`
  means neither architecture accumulates evidence on unused days); BI within 0.5x to 2x (no component
  targets indicator missingness). SP is confirmed by the ablation removing (iii). VA, DE and BI have no matching component; they test missing-data handling only.
- **P1b.** A-fixed's DE false alarms per total person-month are no more than 1.5x its S rate (DE changes usage only).
- **P2.** In the targeted-help cell with `theta1 = 0.5`, DR sensitivity for A-naive is lower than for
  A-fixed by at least 10 points, and removing (i) accounts for at least half of the gap. In the
  constant-help default cell, P2 is not tested.
- **P3.** On AV logged persons, removing (iv) raises false alarms by at least 2x. On AV2 (unlogged,
  other indicators), A-fixed's false alarms are at least 2x its S rate. The cost of the reset (the
  sensitivity loss for onsets inside the 14-day re-baseline window) is reported, with no threshold.

**Predictions:**

- **P4.** With `m1 = 0`, triggered-only probes deflate the person-centred composite-to-probe
  correlation relative to its all-days value by at least 0.05, and attenuate the slope by at least 10%
  relative. The reason is that the trigger depends on past composites, which predict current `D` beyond
  `C_t`. The `current` control, run with a common `lam` and population z-scaling, leaves the slope within 5% relative (a `--check` item); in the default cell its value is reported without a threshold. Under `mixed`,
  IPW with the logged propensity recovers both within 0.03 of the all-days values.
- **P5.** Slope bias is stated as relative bias. At `m1 = 0.5` it is under 5% under `random`: the
  default MNAR cell is benign. At `m1 = 1.5` the slope bias added over the same schedule at `m1 = 0` is at least 10% relative under every schedule. A
  response-propensity IPW estimated from observables (`C_t`, lagged composites, day of week) removes
  less than half of it, because response depends on `D_t` beyond what the composite carries.
- **P6.** Under daily averaging with `pi_t` independent of `D`, the within-person validity (the
  person-centred correlation with `D`) of indicators 4 and 5 is attenuated by
  `Att = (1 - E pi) / sqrt(E[(1-pi)^2] + E[pi^2] kappa_r + Var(pi) delta_r^2)`, within 0.03. Here
  `kappa_r` and `delta_r` are the agent-text variance ratio and mean gap in units of the human
  indicator's SD. `V_H` is the person's within-person variance of `H_j`, and Att is evaluated per person and averaged. P6 is scored on the unfiltered indicator; A-fixed's filtered indicator is scored with `pi` replaced by `pi' = 0.1 pi / (0.1 pi + 0.95 (1 - pi))`. In the Bernoulli cell, the same formula reduces to ghost E7 at `c = 0`, again within
  0.03. In the `pi_t`-rising-with-`D` cell, indicator 4's validity is higher than the independent-`pi`
  formula by at least 0.05 (`mu_M4` exceeds the mean of `H_4`): a spurious state coupling through the mean.
- **P7.** A-fixed's DV sensitivity is at least 15 points below its DR sensitivity.
- **P8.** At matched false alarms and budget, A-fixed (whose CUSUM uses no probe answers) has DR sensitivity within 21 days at least 10 points above probe-only, and a restricted mean time to detection, censored at 42 days, at least 3 days shorter. This compares passive-only with probe-only detection. Fusion of probes with passive data is not tested, and the paper says so.
- **P9.** BD sensitivity is an alarm within the first 21 tracked days (days 29 to 49). A-fixed's BD sensitivity
  is at most half its DR sensitivity within 21 days of onset.
- **P10.** On CS, A-fixed's false alarms are at least 1.5x its S rate: not adjusting for context
  makes a context-mix change a false-alarm source.

## 7. Corpus pilot (D3), metadata only

Input: `~/.claude/projects/**/*.jsonl`, read-only. Kept per entry: timestamp, session id, project slug,
`type`/role, `isSidechain`, `isMeta`, the native provenance fields (`promptSource`, `turnOrigin`,
`entrypoint`, and similar, with coverage reported by month), `version`, `message.model`, content length
in chars, and an authorship class. **Never read:** `origin.body`, `toolUseResult`.

Classes, native fields first and markers as fallback: `human-typed`, `tool-result`, `injected`,
`lane-prompt` (hash match against `~/.instinct/lanes/prompts/`, in memory), `sidechain`,
`pasted-agent` (an exact span of 200 or more chars matching an earlier assistant message in the
session; a boolean only; pastes from other sessions or other apps are missed, named as a limitation), and `third-party` (structural markers only, an estimate). Sessions are also
classed as autonomous, mixed or interactive.

**Reported:** contamination quantities only. That means class shares; for indicators 1, 2 and 4, `pi`,
`kappa` and `delta` and the naive-minus-filtered gap; the share of each naive indicator that comes from
autonomous sessions; data density; missingness; version and model change frequency; the rights and
provenance inventory; and change points in the naive and filtered usage series on a train/test time
split, each attributed to independently dated agent-infrastructure events. **Not reported:** filtered
indicator levels over time (a self-state proxy). Indicator 5 cannot be computed from metadata and is
not. Dictated text is indistinguishable from typed text; this is named as a limitation.

## 8. Out of scope tonight

Any real person's state; any outbound nudge; architecture B; human-subjects protocol text beyond what
the paper's proposed-study section needs; push or publication.

## 9. Staged gates (revised auditor brief, 2026-09-27 20:12, supersedes where it differs)

Source: `selfreport-build-brief-v2.md` in the lane dir.

- **Stage 1: fictional (tonight).** Simulation plus an offline demo that replays **fictional** cases.
  The demo is non-sending: it proposes one reversible support action per change point and executes
  nothing. It shows evidence, uncertainty, abstentions, false alarms and time-to-detection, and has a
  visible privacy control and kill switch (a replay stop and a data-off toggle).
- **Stage 2: own-corpus pilot, gated.** (a) A rights/provenance inventory of every surface he controls
  (agent chats, vault, calendar, tasks, git, dictation, messaging relays): what exists, the date range, who
  authored it, and whether third-party content is present. Metadata only. (b) A timestamped data
  dictionary and provenance ledger. (c) Missingness and agent-policy-change analysis *before* anything is
  called personal. (d) A train/test time split. (e) Descriptive change points in the usage indicators,
  each checked against **independently dated** events (agent-infrastructure changes dated by git commits
  and dated backups, travel dated by calendar). No accuracy, sensitivity or validity claims are made
  without independent labels, and **no labels are manufactured by a model**.
- **Gate to stage 3 (a real-trace replay demo):** independent dated anchors exist for at least some
  change points, third-party content can be excluded, and he has consented in `DECISIONS.md` to replay
  his own traces. Until then the demo stays fictional.
- **Abstention analysis** is a first-class metric in the simulation and in any replay: the share of
  person-days on which the layer declines to assess, the reasons, and false alarms among assessed days
  versus all days.

## 10. Direction correction (his, 2026-09-27 21:28 CDT; supersedes sections 2 D4 and 9 where they differ)

Source: `~/.claude/CONTEXT.md`, "2026-09-27 9:28pm - agentSEM direction". agentSEM measures a person's
state naturally, from their normal agent conversations: no questionnaires, and no psych bot. **The
contribution is measurement validity.** He builds no system and no product; the agent is the object of
study. No clinical diagnosis claims. Theory, simulation and his own corpus only, with nothing faked.

Consequences:
- **D4 (demo) is cancelled.** A replay of a drift layer is a system prototype. Section 9's stage 1 demo
  and stage 3 replay are withdrawn, and any visual becomes a figure in the paper.
- **The simulation stays and is read as validity evidence.** Architectures A-naive, A-fixed and pop are
  alternative scoring rules whose validity is under test, not products. Probe schedules are
  criterion-sampling designs for a future validation study, not an agent administering items. P4 and P5
  concern bias in validity estimates caused by how the criterion is sampled.
- **The corpus audit stays.** It uses his own corpus and measures how much of the trace is his (a
  construct-irrelevant-variance threat), never his state.
- **The paper (D5) is the endpoint.** It is a measurement-validity paper: an argument-based validity
  chain from trace to indicator to within-person score to change claim, the threats to each link, the
  pre-registered simulation (every failure reported), and the one-person corpus audit.

## 11. Amendment A1 (2026-10-03): observation process and elapsed time

Source: the 2026-09-30 literature read on continuous-time and informative-observation models. The
on-disk read, `~/experiments/lit-wip-review-20260930/agentsem-literature-read.md` with register
`sources.md`, is checkpoint revised-wip-2, reviewed REVISE (`VERDICT.md` there). Its fixes, including the
S12 correction used in 11.4, are in the dashboard version and the vault summaries
(`01-Projects/Agent-Delivered-Self-Report/readings/2026-09-30-rast-ct-informative-observation.md`,
`evidence/2026-09-30-findings-to-retain-ct-informative-observation.md`), which the vault note records as
passing follow-up review. S-numbers refer to the register.

**Status.** Post-freeze. Sections 3 to 6, `sim/PREREG.md`, its hash-derived seeds, the results and paper
v4 are unchanged (v4 stays untouched, his call 2026-09-28). This section governs how the frozen results
are described from now on and what the next agentSEM simulation must contain. No grid, threshold,
estimator or run is frozen here; every new family, field or comparator below is a candidate for that
study's own spec and review.

### 11.1 The observation mechanisms already in this spec, classified

"At random" means conditionally independent of the currently unobserved state given recorded
pre-decision history (S3, S9). Adaptive is not the same as nonignorable.

| mechanism | depends on | class | consequence |
|---|---|---|---|
| `triggered`, `mixed` probe timing | `S`, a function of observed composites, evaluated on used days only | at random given recorded history, including same-day usage | for `triggered` the obstacle is positivity, not ignorability: zero propensity outside the band, so IPW is not identified (section 4); `mixed` keeps a floor and is identified |
| day usage, default and VA, DE | not `D` | independent of the state | missing days are ignorable for `D`; VA and DE test missing-data handling only (P1, P1b) |
| day usage, `kappa = 0.3` | current `D_t` | not at random given history | holding `S` on unused days is not a correction for it |
| probe response, `m1` | current `D_t` | not at random given history | P5's claim that observable-based IPW removes under half the bias belongs here; in real data `m1` is not estimable and enters only as a sensitivity range (S10, S28) |
| broken integration, BI | nothing about the person | recording outage | a gap in the record, not an event-free interval |

The paper's verification-bias framing of P4 is consistent with this table. This fixes the
vocabulary for prior-art gap (c) but does not close it: event-contingent EMA prior art is still
search-only, with the leads named in `VERDICT.md` (Revol 2025 on episode-contingent ESM;
Ma/Mermelstein/Hedeker 2022; McNeish 2025 on response nonignorability) unread here.

### 11.2 Elapsed time

The generator is a daily AR(1) with `phi_D = 0.7`. Under it, the stationary part of `D` carries over a
gap of `h` days as `0.7^h`: 0.082 at `h = 7` and 0.0068 at `h = 14` (arithmetic, not a finding). A
sustained mean shift, such as the held DR ramp, does not decay. The CUSUM has no lag model: a held `S`
keeps evidence from a transient excursion at full weight across a gap, where a filter would shrink it by
about `0.7^h` and widen its uncertainty. The frozen design sees this only through VA, DE and DV (P1,
P1b, P7). The next study adds an elapsed-time comparator whose predicted state and uncertainty depend on
the gap (a state-space filter with gap-dependent transition, or a continuous-time model, S1-S2), with
equal spacing kept as a reference check. Continuous time is a baseline, not a contribution: it removes a
timing misspecification and says nothing about why an observation occurred.

### 11.3 An empty interval depends on the opportunity

Four kinds of empty interval are different data (S4, S13): no use during a known observable window; no
answer to a sent probe; no probe because the schedule did not ask; and unknown activity because
recording failed. A no-event interval is informative only over a known window (the survival term of a
point-process likelihood, read appendix A). The frozen architectures do not separate an outage from
ordinary missingness: BI blanks indicators 1 and 6 on used days, the composite averages the indicators
that remain, and no component targets indicator missingness (P1). The next study's own data contract
adds indicator-level availability `U_jt`, separate from usage. An unavailable indicator is not stood in
for by the others, and a day without enough available indicators is reported as abstention with reason
"unknown availability", never as no change (read appendix D).

### 11.4 Engagement in both directions

Only the `kappa = 0.3` cell links state to usage, and only in one direction: a worse state means less
use. In one cohort with electronic self-ratings (S12, prior literature), low-mood
episodes went with the most complete data, remission with less engagement, and moves from euthymia into
worse states with more missing ratings; level and change carried different associations. That is one
cohort and one modality, not a rule for agents, but it is enough to require both signs. The next grid
includes `kappa < 0` and a change-dependent usage term (usage depending on `D_t - D_{t-7}` as well as
`D_t`).

### 11.5 Person change versus observer change

The contribution the read leaves open (its sections 7, 8 and H) is a controlled validity comparison:
whether a within-person score separates change in the person from change in how the agent observes,
helps or records. AV and AV2 (indicator mapping), BI (recording), DE (usage) and the targeted-help cells
cover parts of this. A pure policy shift with `D` unchanged is missing. Candidate family **PS**, two
variants for the next spec (hypotheses, not frozen predictions):
- **Observation-policy shift.** The agent changes how often it prompts or checks in, which changes usage
  and session structure (indicators 1, 2 and 6) without changing `D`. This is the read's central example:
  a detector that uses conversation frequency can learn the agent's behavior and fail when the policy
  changes (read section 5). It belongs in the first, help-off comparison.
- **Help-policy shift** (help extension only, 11.6). Dropping the help propensity from 0.3 to 0.1 on a
  random day in [50, 100] moves the composite by about 0.03 (indicators 2 and 3 rise 0.088 of their
  baseline SD; arithmetic), far under `k = 0.5`. The variant needs a larger help effect, sized in that
  spec and not tuned for alarms.

A mid-follow-up probe-schedule change is the probe-side twin and matters for the probe-only comparator.

Rules for that comparison:
- **Comparators.** An established joint timing-and-mark model (S6-S7), the elapsed-time filter of 11.2,
  a gap/count predictor, a policy-aware candidate, and an estimator matched to whichever target is named
  (read sections 1 and 8, H).
- **One information budget.** Comparators read the same observed contract, with expected event counts
  matched where a contrast needs it. A model that sees `D`, unlogged availability or future records is
  labelled oracle.
- **Online scoring is filtering** on history available at `t`, never smoothing with later records.
- **Metrics.** Target bias and interval coverage, unchanged-person false alarms, detection delay,
  long-gap uncertainty and policy-shift performance, scored at calendar-time checkpoints with empty
  intervals included (read section 8).
- **No method has to win.** Acceptable findings include: an established event/mark model suffices
  under a logged policy; one logged field (intended probe time, `U_jt`, help propensity) is necessary;
  or the target cannot be distinguished in a named regime and abstention is the right output.

### 11.6 Target and construct

Path A (residual scale, close to Rast's IVD model, S20, S27) and path B (a specified latent dynamic
quantity: a change in mean, transition rate or innovation variance; read appendix G) are the read's two
candidates. This spec's mean-change target (the DR ramp) is the case the read calls an alternative first
target (its section 8). Nothing here chooses A or B for the Rast-shaped study, and no CUSUM alarm here
is reported as a variance or volatility result. For a future variance target, DR is the
mean-change-with-variance-fixed control, because a misspecified location distorts scale estimates even
with noninformative observation (S19). Innovation, measurement-error, observed within-person,
between-person scale and time-varying residual-scale variance stay distinct (read appendix C).

Outside simulation (real traces, the corpus audit), a change recovered from the indicators is a change of
engagement regime until an independent anchor ties it to the construct: inferred states in marked event
models can separate utilization regimes rather than severity (S7). This holds for all six indicators. In simulation the indicators load on `D` by
construction (`lam_j`), so the rule does not apply there. Section 10's validity chain carries it as a
named threat at the indicator-to-score link.

Beyond D5 guard 3, the next study's first comparison runs help-off (read section 9). Action-to-state
feedback is a question for a separate consented randomized study (read section 9, S25); INITIATIVE does
not estimate it.

### 11.7 Novelty boundary

Not claimable as new:

| idea | prior art |
|---|---|
| modelling uneven intervals | S1-S2 |
| state-dependent observation, with its weighting, shared-parameter and sensitivity fixes | S3-S5, S9-S10, S28-S29 |
| separate visiting, recording and outcome processes | S11 |
| latent state from event timing plus content | S6-S7 |
| observation-aware prediction and its transport problem | S8 |
| choosing observations and actions together | S17 |
| latent-variance tracking under informative timing | S26 |
| variance targets in longitudinal data | S19, S21, S33 |
| agentic sensing for wellbeing | S15-S16 |
| adaptive language assessment | S30-S32 |
| the recursive observe-estimate-observe loop | S22 |

Claimable only if demonstrated: a specified comparison, identification argument or record design that
separates person change from observer change in ordinary agent use. The read's S34-S36 (residual-scale
models tied to missingness, volatility under informative observation, a mood-volatility/MNAR preprint)
appear in the dashboard version of its register but not in the on-disk ledger, so they are unverified
here.

## 12. Amendment A2 (2026-10-03): timing versus state

Source: `~/code/agentsem/design-input-time-registration-20261001.md` (sha256 `318f1924...522be`) and
its incorporation brief `design-brief-agentsem-20261001.md` (sha256 `ffa49b3b...f9639a`). Both are WIP
from 2026-10-01; the umbrella folder is not a git repo, so the hashes pin the versions read. Base commit:
`fe355aa`. The input reads a machine transcript of an EEG talk on registration, in which trials,
conditions and subjects each get their own timing transformation. The talk motivates separating timing
from amplitude but validates no method for behavioral event streams. Its pure-noise check is a
speculative recommendation, not a reported result.

**Status.** As in section 11: post-freeze. Nothing here is frozen, and every arm, family and field is a
candidate for the next study's own spec and review.

### 12.1 Timing is already inside this spec's target

Indicator 1 (late-activity share) responds to phase, to the spread of activity and to added activity
mass. Indicators 2 (fragmentation) and 6 (reply latency) are timing quantities. In the generator all
three load on `D` (`lam_j`). If `D` acts on indicator 1 partly through phase, aligning activity times
before scoring removes that part of the channel, so this spec has no "align before detection" rule.

That argument can be tested only in a generator that emits within-day event times. The frozen generator
draws indicator 1 as a daily value and cannot express phase separately from amplitude. The next
generator computes indicators from event times by the pilot's own rule and declares whether simulated
behavior follows the wall clock or the sun.

Outside simulation a timing change has causes other than the person's state: timezone and travel,
daylight-saving transitions, term or work schedules, the agent's own scheduler, and autonomous lanes. The
pilot attributes 0.7497 of late-window entries to autonomous sessions (`pilot/RESULTS.md`). Under 11.6, a
timing change in real traces is a change of timing regime until an independent anchor ties it to the
construct.

### 12.2 The clock is part of the indicator definition

The pilot computes late share on a fixed America/Chicago wall clock. "Late" is local hour in [0, 5),
the day boundary is local midnight, and fragmentation bins by local hour (`pilot/trace_audit.py` lines
50-51, 470-473, 586, 591). Three consequences:

- **Timezone.** The transcripts carry no timezone field; a sample check this lane found only
  `timestamp`. The fixed-zone rule is therefore an unsourced known-warp assumption, and travel would move
  indicator 1 with no change relative to the local clock. The next data contract records the device
  timezone or a dated travel record. A day with neither is an abstention with reason "unknown clock",
  parallel to 11.3's unknown availability.
- **Daylight saving.** Chicago transitions at 02:00, inside the late window. On spring-forward night the
  window is 4 hours and the day 23. On fall-back night the window is 6 hours, the day is 25, and the
  repeated hour falls into one fragmentation bin. Transition dates are flagged as exposure-altered, not
  only as known-warp dates. Separately, a routine anchored to light or sleep moves an hour against the
  clock on those dates.
- **Day boundary.** The [0, 5) window credits late activity to the calendar date after the evening it
  continues. A delay that pushes activity past midnight moves entries between dates. That changes each
  date's count, its used/unused status and its late share at once. A fixed boundary at the person's
  baseline activity trough, set from the baseline window only, is a candidate alternative.

The pilot's numbers stay as computed. Later text that describes indicator 1 names its clock and
boundary.

A known warp (timezone, daylight saving) comes from an independent record and corrects the clock. An
estimated warp is a model with its own uncertainty. The two are never reported as the same kind of
adjustment.

### 12.3 Candidate comparison

All arms read the same observed contract (11.5, one information budget).

| arm | what it does | status |
|---|---|---|
| R0 raw | indicators on a declared, sourced local clock and a declared fixed day boundary | baseline, always kept |
| R1 phase summary | one daily phase summary of user-initiated events, kept as its own series with uncertainty. Example: the circular mean of event times, or the onset of the most-active block in the rest-activity tradition (Van Someren et al. 1999, Chronobiology International 16:505-518). It enters detection only as a sensitivity arm, labelled as removing the phase channel, because residualizing on phase erases it as R2 does | first comparator |
| R2 restricted registration | a bounded day-level shift against a template fit on the baseline window and frozen, with the warp of 12.4 between days. No per-session or per-event warp | most complex arm admitted |
| oracle | the generator's true shift | an upper bound for reference, never a baseline |

**Why R2 is restricted.** Phase and amplitude are not separately identified unless the warp class and
the template are constrained:
- Marron, Ramsay, Sangalli and Srivastava 2015, Statistical Science 30:468-484, doi 10.1214/15-STS524;
- Kneip and Ramsay 2008, JASA 103:1155-1165, doi 10.1198/016214508000000517.

Days are bins, not stimulus-locked trials, and a sparse day can hold a handful of events, so a flexible
per-day warp would be fit to noise. The input's event/day/person hierarchy is therefore reduced to a
person-level template and a day-level shift. Registration of sparse, fragmented curves exists (Matuk,
Bharath, Chkrebtii and Kurtek 2022, JASA 117:1964-1980, doi 10.1080/01621459.2021.1893179) and is not
needed for a first comparison.

The citation details were located by search in this lane and checked by the review subagent. Abstracts
only were read.

### 12.4 Identification and the information boundary

- **Abstain when there is no phase.** Before any template is fit, flatness is tested by a prespecified
  test on the baseline event clock-angles (for example Rayleigh), at an alpha fixed on the tuning seed. A
  flat person gets the abstention reason "phase not estimable", not a shift of zero. A day with fewer
  than `n_min` user-initiated events abstains with the reason "too few events". Aligning noise to a
  template reproduces the template, so a fitted template is not evidence of a shared shape.
- **Past-only boundary.** Events are assigned to day `d` by the fixed boundary of R0. `ŝ_d` is
  estimated only from events in that window after it closes, and the aligned late window is computed
  inside it. No boundary depends on `ŝ_d` or on any later day.
- **Fixed inputs.** The template is fit on days 1 to 28 and frozen. A whole-series retrospective
  re-alignment is labelled offline (11.5: filtering, not smoothing). The template, the shift bound,
  `n_min` and alpha use the tuning seed only.
- **Which events.** Phase is estimated from user-initiated events only. Replies to agent-initiated
  prompts and autonomous-lane traffic are excluded, because the agent's scheduler set their timing
  (11.5, PS). A probe schedule that follows the estimated phase makes observation times depend on the
  estimate. That stays at random given recorded history (11.1) only if the estimate is logged with the
  propensity.
- **Event models in transformed time.** If an intensity model is fit in warped time `u = w(t)`, then
  `lambda_u(u) = lambda_t(w^-1(u)) * (w^-1)'(u)`. Observation windows, `U_jt` and outages map through
  `w` and its derivative. An outage stays an outage and is never interpolated.
- **The warp must be continuous.** A piecewise-constant day shift is not a valid warp: adjacent days
  overlap or leave a gap of `s_{d+1} - s_d`. R2's warp is continuous and monotone, interpolating
  linearly between day anchors, so within day `d`, `w'(t) = 1 - (s_{d+1} - s_d)/24h`, with
  `|s_{d+1} - s_d| < 24h`. Exposure is carried through this derivative. Only a constant shift has
  `w' = 1`. For past-only scoring, day `d` is scored with the last anchor carried forward.
- **What registration cannot do.** It does not change any class in 11.1, does not make observation
  ignorable, and does not supply opportunities during an outage (11.3). The continuous-time and
  observation-process baselines (11.2, 11.5) stay in the comparison.

### 12.5 The timing shift as its own quantity

Raw timestamps, the estimated daily shift and its uncertainty are kept together. An aligned series never
replaces them. The summaries are fixed before scoring:
- the shift from baseline in hours (delay or advance);
- its day-to-day variability;
- the weekday-weekend difference. This is analogous to social jetlag (Wittmann, Dinich, Merrow and
  Roenneberg 2006, Chronobiology International 23:497-509), which is defined on sleep midpoints these
  data do not contain.

Whether a shift predicts an independently anchored outcome beyond raw timing, exposure and context is a
question for an anchored validation study. In simulation the link is built in. A predictive association
is not a state claim.

### 12.6 Null and failure suite

The full pipeline runs in every family: flatness test, template fit, shift estimation and detector. A
detector given oracle alignment never stands in for it. Daylight-saving transition dates fall inside
every family's follow-up.

| control | family |
|---|---|
| pure noise, no shared shape | S with a flat within-day template |
| autocorrelated or heteroskedastic timing noise, no effect | S with AR(1) day-level jitter |
| phase only, estimated | new **PH**: a sustained template shift of fixed size with `D` unchanged, unlogged (a schedule shift) |
| phase only, known | PH with a logged timezone change. This tests R0's clock correction, not registration |
| amplitude only | DR with the template held fixed |
| joint | DR in which `D` also delays the template |
| policy only | PS (11.5), with the agent's prompts at fixed clock times |
| missing responses, outages | the `m1` cells; BI |
| sparse events, changing context | a low-volume cell; CS |
| drift inside the baseline | BD, whose template is fit on contaminated baseline days |

What counts as a false alarm depends on the target, so results are read per target:

| target | PH | joint | R2 |
|---|---|---|---|
| the person's mean change (this spec's DR) | null: alarms are false | positive | admitted |
| a timing regime | positive | positive | excluded: it removes the target |

Metrics are section 5's, plus:
- phase-estimate bias and interval coverage against the generator;
- the share of persons and days abstaining for each reason;
- indicator 1's within-person validity per arm;
- the composite sensitivity on DR and joint per arm, with `h` retuned per arm on S to the same
  false-alarm target;
- false alarms on PH, by arm;
- on flat persons, the non-abstention rate (at most alpha) and the peak amplitude of the aligned mean.

Some absorption of `D`'s late-activity mass by the shift estimate is expected. R2's criterion on DR is
therefore non-inferiority to R0 within a margin fixed in the preregistration, not equality. Failed fits
and abstentions stay in denominators (section 5). Target, tuning, the shift bound, the PH size, `n_min`,
alpha, thresholds and stopping rules are fixed in that study's preregistration before scoring.

### 12.7 Decisions and change log

**Adopted as candidates:** arms R0 to R2 and the oracle, clock provenance and transition-date flags, a
fixed trough-anchored day boundary, family PH, an event-time generator.

**Rejected:**
- a universal align-before-detection rule (12.1);
- flexible hierarchical event/day/person warps for the first comparison, since the data have no repeated
  stimulus-locked curves and days can be sparse;
- a piecewise-constant day shift, which is not a warp (12.4);
- any day boundary that depends on the current shift estimate, which would leak future events;
- porting the EEG method without checking its repeated-curve and phase-amplitude assumptions;
- reporting the talk's pure-noise check as done;
- reading a schedule shift as a change in the person (11.6, `CLAIMS-ENVELOPE.md`).

**Open for that spec:** midnight or trough boundary; the shift bound, PH size, `n_min`, flatness alpha
and non-inferiority margin; which phase summary; whether timing is part of the target (12.6 table).

**Unchanged:** sections 3 to 6, `sim/PREREG.md`, paper v4, the pilot's computed numbers.

**Change log.** An Opus methods review of the first draft (this lane, 2026-10-03) returned REVISE with
nine blocking items. The eight that concern this spec were all accepted:
- the warp is continuous with its derivative, replacing "only labels move";
- the boundary is past-only;
- daylight saving changes exposure;
- a target-by-family table was added;
- the DR criterion is per-indicator non-inferiority with per-arm `h`;
- a flatness test and `n_min` were added;
- R1 is a series and a sensitivity arm only;
- this log and the hashes were added.

Its non-blocking items were also accepted:
- indicator 1 is no longer called a pure phase quantity;
- the generator declares its clock;
- the open parameters are listed;
- BD contamination is noted;
- the Matuk citation is completed.

The review confirmed the intensity formula, the pilot grounding, all five citations, the tuning/scoring
separation and that no frozen material changed.

## 13. Note (2026-10-03): prior-art gap (c) read

Source: the three leads named in section 11.1, read in full text by lane `agentsem-lit-gap-c-oct03`. Ma
et al. was read from the PMC author manuscript, with equations described from the prose. Revol et al. and
McNeish were read from accepted-manuscript preprints on PsyArXiv. All three DOIs were checked on
Crossref. **Status:** as in sections 11 and 12. These are notes for the next paper version and the next
study's spec.

| source | what it does |
|---|---|
| Ma, Mermelstein & Hedeker (2022), *Stat Med* 41(10):1780-1796, doi:10.1002/sim.9328 | Shared-parameter location-scale model for event-contingent EMA. A daily count of missed self-initiated reports, detected through random prompts converted to event reports, depends on a person random effect that is linked to the location effects and to the random scale (IVD) effect. Observation depends only on time-invariant person effects and covariates. The authors say it is valid under random-coefficient-dependent MNAR and may be biased under outcome-dependent MNAR (Little). |
| Revol, Ariens, Lafit, Adolf & Ceulemans (2025), *Psychol Methods*, online, doi:10.1037/met0000758 | Episode-contingent ESM: sampling starts when the observed process is far from its mean, with follow-ups. The OLS AR slope is not materially biased; precision trades predictor variance against effective pairs. Under this design the lag-1 autocorrelation no longer equals the AR coefficient, so they advise fitting the regression (sec. 6.3). A continuous-time fit (ctsem) on these data was biased upward at high instrument precision (sec. 6.4.1, supplement C, which was not read). The paper frames this as time spacing, not missingness. |
| McNeish (2025), *Psychol Methods*, online, doi:10.1037/met0000742 | DK-DSEM: a probit missingness model on the current latent within-person component, its lag and time. Identification rests on normality and exclusion restrictions that cannot be tested, so MNAR models are offered as sensitivity analyses (comparing specifications, local sensitivity). The simulated mechanism is one-signed (high values go missing). Residual scale is not a cause of missingness. |

### 13.1 What changes

1. **N2 gets its ESM instance.** Revol et al. is the ESM case of selection on the predictor and matches
   N2 and the draft's unbiased-slope statement; their tail trigger widens the predictor range where this
   spec's band narrows it. The next paper version
   cites Revol et al. beside Lathia et al. (2013) in the criterion-sampling paragraph.
2. **Gap (c) narrows but does not close.** None of the three covers a trigger on a statistic other than
   the predictor, or a random floor with logged propensities and weighting in an ESM schedule. Those
   stay attributed to verification bias (Begg & Greenes 1983) and micro-randomized-trial weighting
   (Boruvka et al. 2018). The remaining search is for ESM schedules that mix triggered and random
   prompts and weight by the logged probability.
3. **11.1 vocabulary.** `m1` is outcome-dependent MNAR: response depends on the current `D_t`. A
   shared-parameter model of Ma et al.'s form, which ties observation to time-invariant person effects,
   would not cover it. McNeish's DK-DSEM models the `m1` form directly and identifies it only through
   untestable assumptions, which supports treating `m1` as a sensitivity range. The next spec names
   both forms of sensitivity analysis: a grid on `m1` (as in P5) and a comparison of specifications (as
   in McNeish). P5's "observable-based IPW removes under half the bias" is covered by none of the three
   and stays a simulation result of this study.
4. **11.2 elapsed time.** A continuous-time comparator is not automatically unbiased on triggered data
   (Revol et al., ctsem). The next study checks its elapsed-time comparator under `triggered` and
   `mixed` against the oracle before treating it as the baseline.
5. **11.7 novelty table.** Add Ma et al. 2022 as a new row, "residual scale (IVD) linked to the
   observation process". Path A therefore cannot claim that link; its claim is limited to
   agent-mediated observation and observer change. Add McNeish 2025 to the state-dependent observation
   row. Add Revol et al. 2025 as a new row, "event-contingent sampling and dynamic estimates".
6. **11.4.** McNeish simulates one sign only (`kappa` is free in the model but not varied). The
   `kappa < 0` and change-dependent cells extend a known model; they are not new.

### 13.2 What does not change

- N2 stays "a known result in a new setting, not a discovery". No reading contradicts it or makes it new.
- 11.1's `triggered` classification and section 4's IPW statement hold: Revol et al.'s unsampled middle
  range leaves a correctly specified linear slope unbiased, so positivity binds only for weighting and
  for misspecified or nonparametric targets.

### 13.3 Open

- Not yet read: Lin, Mermelstein & Hedeker (2018, the closest Path A lead) and Li et al. (2014, Path
  B), both from the same `VERDICT.md` list; Revol et al.'s supplement C; the typeset versions.
- S34-S36 are still unverified. `sources.md` on disk stops at S33. Neither page tarball in
  `~/experiments` nor the vault note defines S34-S36; the vault note cites them by tag only. The
  dashboard read returned 404 to a logged-out request on 2026-10-03. Ma et al. fits the "residual-scale
  models tied to missingness" description, but that match is not evidence of what S34 is.

## 14. Note (2026-10-03): person change versus observer change, first exploratory run

Source: `sim/ATTRIBUTION-PLAN.md` (r1) and `sim/ATTRIBUTION.md`. **Status:** exploratory, as section 11. Sections
3 to 6, `sim/PREREG.md`, the frozen results and paper v4 are unchanged. The run puts numbers on the 11.5
candidate family PS, frozen generator, A-fixed, 1000 persons per family:

1. An unlogged, indicator-only observation-policy shift (PS-sub, +0.5 on indicators 1, 2, 6) raises
   post-change alarms 3.5-fold over the same persons without it.
2. A per-person indicator-pattern test over the 14 days before an alarm has no power here: it keeps
   0.87 to 0.93 of alarms in every family, person change or not. A loading-proportional observer change
   cannot be separated from person change by indicators at all, as the invariance argument predicts.
3. Three confirmation probes after the alarm read 0.76 of DR alarms as person change, against 0.46 to
   0.56 elsewhere, at 0.46 probes per person-month. Part of what they confirm is real momentary
   elevation: alarms in S fire at a mean `D_t` of 1.35.

For the next study's spec: the policy log is the separator these numbers support (11.5's "one logged
field is necessary" outcome); confirmation probes need spacing past the state's memory, or the target
must name momentary elevation; usage-changing PS, `m1 > 0` and targeted help remain to run.

## 15. Decision (2026-10-03): the next study's target is a sustained mean shift in D

**Provenance.** Section 14 and `~/audit/agentsem-next-2026-10-03.md` left this as Abhay's call. He delegated
it on 2026-10-03 (15:20 CDT, his words: "You make the decisions or make the decisions with Opus"), with
the conservative option preferred wherever his data is touched. One Opus methods review returned REVISE
with four blocking items; all four were accepted and are in the text below.

**Decision.** The next study's target is a *sustained shift in the mean level of `D`*. Momentary elevation
is not a target. A family counts as positive only if its generator adds a deterministic mean component to
`D` of at least `delta_D`, held for at least 14 days after any ramp ends. 14 days matches the refractory
period and the re-baseline window (section 4). AR(1) excursions of `D` never count, whatever their duration: at the
robustness cell `phi_D = 0.9` (`drift_sim.py:2656`) an excursion takes about 29 days to decay to 0.05, so a
duration-based definition would admit it. `delta_D` is set in the next spec.

**Scope of the decision.**
- PH (12.6) stays null, as in the mean-change row of the 12.6 table. Whether timing is part of the target
  (12.7) is still open.
- Path A against path B (11.6) is still open. Sustained changes in transition rate or innovation variance
  are not this target.
- S stays a null family, so `h` keeps its anchor (tuned on S to a false-alarm rate, section 4). S alarms on
  transient high `D_t` stay false alarms.

**Consequences for the next spec.**
1. Confirmation probes must be spaced past the state's memory. The spacing is a function of `phi_D`
   and must hold across the `phi_D` grid. Lags at which `phi_D^L` falls below 0.05: 3 days at 0.3, 9 days
   at 0.7 (`0.7^9 = 0.040`) and 29 days at 0.9. The cost is *days to confirmation* (section 5), not days to
   detect.
2. The frozen 7-day confirmation rule sits inside the state's memory (`0.7^7 = 0.082`), and any probe in
   the window confirms, which favours early probes. Frozen confirmation PPV is read with that caveat.
3. The policy log is the primary separator of person change from observer change (section 14). This asks nothing of the person. Probes are a secondary separator.
4. In simulation only, false alarms are also broken down by alarm-day `D_t`, as a descriptive diagnostic.
   No `D_t` or alarm-day state estimate is computed from real traces (constitution I).

**Rationale.**
- The decision matches the frozen design. Section 5 counts S alarms, and pre-onset alarms in drift families, as false; DR is a ramp
  that holds, and the target is "within-person change from the person's own baseline" (section 0).
- Privacy. A momentary target would make the layer a day-level state detector. That is closer to state
  monitoring, which the framing ruling does not bar outright but which sits nearer to screening. Probe
  count is set by the budget (section 4), not by the target, so the gain is a narrower inference, not
  fewer asks.
- Constitution I and VII already bar real-data state estimates and real probes in this repo. This target
  governs simulation scoring and any future consented study.

**Reversibility.**
- Until the next study's preregistration is frozen, this can be reversed with a dated note here.
- After the freeze, a momentary-elevation rescoring can be added as tagged exploratory work (constitution
  III), and simulations rerun cheaply. Only a confirmatory momentary claim needs a new study version.

**Unchanged:** sections 3 to 6, `sim/PREREG.md`, the frozen results, paper v4, section 14's numbers.
