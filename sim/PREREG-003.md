# sim/PREREG-003.md -- DRAFT pre-registration for spec 003

**Status: DRAFT. Not frozen, not pushed. Nothing here is a result.** It becomes a pre-registration only when he
lifts the freeze and commits it. No evaluation seed has been run. Every number cited is a synthetic design-stage
number (`sim/DESIGN-003.md`, `sim/DECIDE-003.md`, `sim/REP-003.md`) and is listed under Disclosure as seen
before the freeze. Decisions marked **(lane decision)** were made by the lane under the 2026-10-05 relay
(`/Users/abhay/.instinct/DECISIONS-20261005.md`, Update 9:27, which delegated "the probe budget rule, H5 and the
PREREG-003 slot text"; N and H3's decision rule rest on reading "slot text" broadly). **(owner-delegated)**
were made in that file's earlier section. Both kinds are his to overturn before the freeze.

## 1. Fixed setup

- Generator and scorer: `sim/study003.py` at the commit recorded at freeze. Frozen `drift_sim.py` and
  `attribution.py` unchanged.
- Defaults: help-off, onsets U[70, 120], `phi_D` 0.7, 28-day baseline, 4 baseline probes (spaced), A-fixed
  `k = 0.5`, `T = 210`.
- Re-baseline window `W = 14` days (owner-delegated). `W = 21` was evaluated and not taken: it puts PS-sub's
  L1/S at 1.025 [0.831, 1.230] on the design seed (PS-use not run under 21) and cuts DR+PS L1's 21-day
  sensitivity from 0.081 to 0.020 (DECIDE-003 part c), blinding L1 in `(c, c + W]`.
- Evaluation N: **4000 persons per cell (owner-delegated, 2026-10-07).** The lane had drafted 2000. Every
  thresholded registered item except H3's L1 clause has a projected interval-level probability of about 0.88 or
  more at N 2000 (DECIDE-003 part a). Under H3's registered point rule the L1 clause is projected to hold with
  probability 0.797 (PS-sub) and 0.915 (PS-use) at N 2000, against 0.880 and 0.974 at N 4000. The joint
  probability over all H3 clauses was not computed. N was raised to 4000 because the only cost is compute and
  the registered prediction gets a more decisive test either way.
- Evaluation bootstrap: 1000 person resamples, shared across statistics, 95% percentile intervals.
- Evaluation seed: not chosen by hand. `study003.py score --prereg-sha <sha>` derives it as
  `sha256("<sha>:study003")` of the frozen file, so it is fixed by the freeze commit, and the scorer refuses unless
  this file lists the current sha256 of `study003.py` and `tuning_003.json` (listed at freeze, not here). It
  equals none of the design (20261003, 20261004), tuning (20260927), REP-003 (`sha256("rep003:r")`) or
  OBS/LOAD/STEP/HYB/BREAK/UNLOG-003 seeds.
- **Probe rule for scoring.** H1, H2 and the budget comparison arm are scored under the design rule `all`, the
  rule they were sized under (reason in section 5).

## 2. Registered predictions (tally: H2a and H3)

A failed prediction is reported as failed and nothing is re-tuned after scoring. Intervals are 95% paired
person-bootstrap intervals.

- **H2a.** At `phi_D` 0.9, S's spaced confirmed share exceeds its oracle-reference share by at least 0.10.
  Holds if the interval lies at or above 0.10. Design 0.201 [0.155, 0.246].
- **H3 (W = 14 owner-delegated; decision rule lane decision, following DESIGN-003 section 4 item 3).** Scored
  on spec 003 section 8's L1 and L2 (not L1_step), on logged PS-sub and PS-use persons. The rate is alarms per
  30 non-refractory tracked days over `[max(c, B), T)`, for logged persons, divided by the same persons' rate
  on the S panel. **H3 holds only if all six clauses hold:** L1 and L2 on PS-sub and on PS-use each have a
  point estimate below 1.5, and L0 on PS-sub and on PS-use each have an interval lower bound above 1.5.
  Intervals for L1 and L2 are reported, not required.
  - Design values: L1 PS-sub 1.421 [1.175, 1.706], PS-use 1.376 [1.135, 1.647]; L2 1.171 and 1.101; L0 3.061
    [2.792, 3.380] and 3.050 [2.790, 3.366].
  - At N 2000 the L1 point lands above 1.5 about 20.3% (PS-sub) to 8.5% (PS-use) of the time if the design
    seed's value is the truth, and its interval clears 1.5 13% to 28% of the time.
  - The only other draw, check seed 20261004, gave PS-sub L1/S 1.629 [1.421, 1.864] at N 2000, above 1.5.
    The projections take the design seed's value as true and are optimistic if the check seed is nearer the
    truth: the L1 clause may fail about as often as it holds.
  - A pass on the point is weaker than a pass on the interval, and the paper says so.

## 3. Construction checks (labelled as checks in the paper, not findings)

- **H1a.** At `phi_D` 0.7, spaced confirmation lowers S's confirmed share by at least 0.15 against the
  next-day rule. Holds if the interval lies at or below -0.15. Design -0.236 [-0.302, -0.173].
- **H1b (owner-delegated).** Spaced confirmation keeps at least **0.70** of DR-1.0's next-day share. Holds if
  the interval lies at or above 0.70. Design 0.810 [0.715, 0.916]; the earlier 0.85 was not taken because it
  misses at every N (interval-level probability at most 0.003).
- **H4.** On DR+PS, L2 loses less sensitivity than L1 for onsets inside the re-baseline window. Holds if the
  interval of L2 - L1 lies above 0. Design +0.154 [0.100, 0.209].
- **H5 (lane decision).** For unlogged PS-prop, no indicator-only rule separates it from DR-1.0 by more than
  0.10 in person-attributed share.
  - **M1 clause: kept as a registered check.** Holds if the interval lies inside (-0.10, 0.10). Design 0.020
    [-0.013, 0.053]; projected interval-level probability 0.998 or more at N 1000 and above.
  - **L0+label clause: kept in the paper, labelled true by construction, not scored.** Neither family
    carries a label, so the difference is exactly 0.000 in the design run (DESIGN-003 section 3 item 5).
## 4. Reported estimates (not scored)

- **H2b (owner-delegated: exploratory).** The reduction in the gap from 28 to 56 baseline days, probes held at
  4 (28-day gap minus 56-day gap), with its interval. Design -0.003 [-0.069, 0.057].
- **H6.** Matched `k` against `k = 0.5` at matched false alarms. No direction predicted; estimate with interval.
- **Observer-step rule (owner-delegated).** L1_step is the rule carried into the paper; L1_did is dropped.
  L1_step is not in spec 003 and H3 and H4 were sized on L1 only, so L1_step is reported beside L1 for H3 and
  H4 as an unregistered arm. The L1 against L1_step choice is reported as a trade-off, with the false-alarm
  weight `w` over the grid 1 to 4 beside the Youden reading. **No single `w` is registered.** Numbers cited
  come from REP-003's 200-population generator means (`sim/OBSERVER-STEP-DIGEST.md`), not the design draw.

## 5. Probe budget rule (lane decision)

**Rule: `wait`.** The first alarm of a person is probed. After that, no new probes until the last probed
alarm's third probe day has passed (3 x lag + 1 days), answered or not. An operational form of DESIGN-003
section 4 item 5's "confirm once per person episode". The design rule `all` is a comparison arm in every
cell, and the budget table reports both. Only `all`, `wait` and `stop` were compared, so `wait` is the best
of three, not shown optimal.

Reasons, from DECIDE-003 part b (no new simulation):
- At `phi_D` 0.7, `wait` takes DR-1.5 from 3.24 to 2.35 [2.29, 2.39] probes per tracked person-month, under
  the frozen 3.0 target, for about 0.03 of in-window confirmed share (0.281 -> 0.252). `all` overruns 3.0.
- `wait` also lowers S's confirmed false alarms per tracked month (0.061 -> 0.052 at 0.7).
- `stop` (no probes after a first confirmed alarm) is rejected: more in-window share lost at `phi_D` 0.3 and
  0.7 (0.215 at 0.7 against `wait`'s 0.252), and a confirmed pre-onset false alarm would block the true alarm
  for good.
- The first alarm is probed under every rule, but "H1 and H2 do not change" was not tested: H1b scores the
  first in-window detection, which `wait` can block (DR-1.0's in-window share already falls 0.154 -> 0.134).
  Hence H1 and H2 are scored under `all` (section 1).

Scope and costs, reported with the budget table:
- The rule runs in every cell. The paper claims the 3.0 target only at `phi_D` 0.7, a reporting scope, not a
  property of the rule, since a deployed system does not know `phi_D`.
- At 0.9 every rule meets 3.0 on the point estimate (`all` 2.93 [2.82, 3.04]), and `wait` costs DR-1.5 0.280
  -> 0.165 of in-window share and halves DR-1.0's. The headroom is bought with sensitivity.
- At 0.3 `wait` equals `all` (a 10-day wait is shorter than the 14-day refractory) and DR-1.5 stays at 3.68;
  only `stop` meets 3.0 there (1.74).
- The budget comparison is a design-constraint report, not a pass/fail prediction.

## 6. Scoring map

Defaults of section 1 unless a row says otherwise. Statistic definitions are in `study003.py`; the exact
scoring commands are to be written at freeze (section 8).

| item | family / contrast | `phi_D` | baseline days | probes | probe rule | subset, window, statistic |
|---|---|---|---|---|---|---|
| H1a | S spaced - S next-day | 0.7 | 28 | 4 | `all` | S's confirmed share of the first post-baseline alarm |
| H1b | DR-1.0 spaced / next-day | 0.7 | 28 | 4 | `all` | persons with a first in-window detection, confirmed share |
| H2a | S spaced - oracle reference | 0.9 | 28 | 4 | `all` | S's first post-baseline alarm, confirmed share |
| H2b | gap 28 d - gap 56 d | 0.9 | 28, 56 | 4 | `all` | as H2a, per arm |
| H3 | PS-sub, PS-use logged / S; L0, L1, L2 | 0.7 | 28 | 4 | `all` | rate per 30 non-refractory days over `[max(c, B), T)`, paired |
| H4 | DR+PS, L2 - L1 | 0.7 | 28 | 4 | `all` | sensitivity, onsets inside `(c, c + W]`, 21 d |
| H5 | PS-prop unlogged vs DR-1.0; M1 | 0.7 | 28 | 4 | `all` | person-attributed share difference |
| Budget | S, DR-1.0, DR-1.5 | 0.3, 0.7, 0.9 | 28 | 4 | `all`, `wait`, `stop` | probes per tracked person-month; in-window confirmed share |

## 7. Disclosure (required before freeze)

Seen before this draft, so none counts as blind: `sim/DESIGN-003.md` (`design_003.json` sha256 `a4064d3f...`),
`sim/DECIDE-003.md` (`decide_003.json` sha256 `ccb784b0...`), `sim/REP-003.md` (`rep_003.json` sha256
`4f046f45...`), and the OBS, LOAD, UNLOG, STEP, HYB and BREAK-003 runs behind the observer-step choice. Every
number cited above was seen. Forking paths:
- H3's point rule was chosen knowing it passes on the design seed (1.421) while the interval rule fails there
  ([1.175, 1.706]), and the check seed (1.629) falls on the other side.
- H2b, a registered clause in spec 003 section 11, was demoted to exploratory after the design projected it to
  fail (interval-level probability 0.0 at every N).
- H1b's 0.70 sits just under the design lower bound 0.715.
- `W = 21` was evaluated (DECIDE-003 part c) and rejected.
- The budget rule was picked after all three rules' costs were seen on the design persons, and the selection
  criterion (meet 3.0 at `phi_D` 0.7 with the least loss of in-window share) was written after the run.
- N 2000 was chosen after the projection table.

Scorer changes made after the design run: the PPV fix of `e193a51` (only pre-onset alarms count as false).
- 2026-10-07: `run_study` takes the person count `n`; `N = 1000` stays the default, so `design` reproduces
  `design_003.json` (every committed key, recomputed); `score` runs at `N_SCORE = 4000` (section 1), `--n`
  overrides.
- 2026-10-07: `probe_rule` (`all`, `wait`, `stop`) moved unchanged from `decide_003.py` into `study003.py`;
  `run_study` writes the section 5 budget table (`budget`, every `phi_D`), equal to `decide_003.json`'s on the
  design seed.
- 2026-10-07: `verdicts(out)` applies sections 2 and 3 to a run's output from one threshold table; `score`
  writes `verdicts` into `results_003.json`, and `study003.py verdicts <file>` prints them for any results file.
- 2026-10-07: L1_step added to `policy_log` as the unregistered arm of section 4 (`obs_003.step_rule(False)`),
  reported beside L1 for H3 and H4 in `verdicts` with `scored: false`. Its design-seed values were seen when the
  design run was reproduced to test the change (not committed): H3 L1_step/S PS-sub 0.977 [0.844, 1.108], PS-use
  0.960 [0.836, 1.095]; H4 L2 - L1_step 0.174 [0.127, 0.224].
Any further scorer change before the freeze must be listed here.

## 8. Decisions and what remains before the freeze

Owner delegation, 2026-10-07 11:05 CDT, verbatim: "Make all the decisions for me. Whatever would be ideal for the
paper." Under it, the lane took every lane decision through to a choice:
- N: raised from 2000 to 4000 (section 1).
- H3: the point-estimate rule and the all-six-clauses reading stand (section 2); a pass on the point is reported
  as weaker than a pass on the interval.
- H5: the M1 clause is scored, the L0+label clause is true by construction and not scored (section 3).
- Probe budget rule `wait`, with the `phi_D` 0.7 reporting scope; H1 and H2 scored under `all` (sections 1, 5).
- The three scorer gaps found 2026-10-06 are closed and listed in section 7.
- Spec 003 section 11 wording of H3 and H5 is taken as it stands.

Remaining before `score`: the freeze commit, which lists here the sha256 of `study003.py` and `tuning_003.json`
at that commit. Spec 003 section 13's other open items (the PS-use intercept size, the S34 to S36 sources) do
not bear on the scorer and stay open. No push.
