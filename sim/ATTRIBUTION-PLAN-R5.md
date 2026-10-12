# sim/ATTRIBUTION-PLAN-R5.md -- EXPLORATORY r5, not frozen

Round 5 of the person-versus-observer attribution runs. r1 (`sim/ATTRIBUTION-PLAN.md`, sha256 `dbc0024a...`,
results `sim/ATTRIBUTION.md`) defined three attribution rules: M1 (no probe), M2 (one probe) and M2x3
(three probes). It scored them on spec 001's default cell. Spec 003 then froze and ran five cells:
- `kappa` -0.3 and +0.3;
- change-dependent usage 0.3;
- probe-response `m1` 0.5 and 1.5.

The frozen run is `sim/PREREG-003.md` section 5 (sha256 `06ee4757...`), with results in `sim/results_003.json`
`cells`. It reports four metrics per cell: S false alarms per month, DR-1.0 21-day sensitivity, the
spaced-confirmed share and the unconfirmable share. No round has computed r1's person-attributed shares
for these cells. This round fills that gap (lane `agentsem-attrib-r5-1011`; owner call 2026-10-11 21:18,
relayed by main).

**This run is EXPLORATORY r5. It was never planned before. It is not a PREREG-003 amendment and not part
of `sim/PREREG.md`. It changes no H1-H5 or P1-P10 verdict, no frozen code path, no number in paper v4, and
nothing in r1 to r4.** Its outputs (`sim/attribution_r5.json`, `sim/ATTRIBUTION-R5.md`) repeat this label.
No result here may be folded into a confirmatory claim. All numbers are synthetic.

This text applies an Opus methods review made before hashing: REVISE, one blocking finding (D6) and nine
minor ones, all applied. It also applies one ponytail finding: E2's ratio is computed from point estimates.
Before this file was hashed, only `--check` ran. It uses throwaway seeds and the n 60 `run_study`
comparison, and the reviewer ran its own throwaway-seed probes. No panel on this round's seeds was scored.

Seeds derive from this file's sha256 with the tag `attribution-r5`. The script asserts they differ from:
- the PREREG-003 evaluation seed (192815961, in `results_003.json`);
- the tuning seed (20260927);
- the design seeds (20261003 and 20261004).

Frozen state carried as documented, not touched: `drift_sim.py --check` cell (c), drift=True, fails at a
relative difference of 0.0605 against the 5% tolerance. This is pre-freeze deviation 1, recorded by the
owner's decision of 2026-10-11 20:39.

## (a) Panels

The five cells are built exactly as `study003.run_study` builds them:
```
study003.panels(base, 0.7, ("S", "DR-1.0"), cell=ci, n=4000, **kw)
```
The cell index `ci` and keyword `kw` are:

| ci | cell | kw |
|---|---|---|
| 1 | `kappa-0.3` | `kappa=-0.3` |
| 2 | `kappa+0.3` | `kappa=0.3` |
| 3 | `change_dep_0.3` | `kappa_c=0.3` |
| 4 | `m1_0.5` | `m1=0.5` |
| 5 | `m1_1.5` | `m1=1.5` |

The common settings are:
- phi 0.7;
- help off;
- onset U[70, 120];
- detection days [0, 210), with probe answers generated through day 296;
- N 4000, PREREG-003's evaluation N.

Within a cell, S and DR-1.0 share the main random stream, so they are the same persons and paired.
Across cells the persons are independent, as in the frozen run.

**Reference cell (added, not one of the five).** `ci = 0`, no `kw`: spec 003's default at phi 0.7 on this
round's seed. It exists only so cell effects have a comparison. It is labelled `reference` everywhere.

`base` is `sha256("attribution-r5:<plan sha>:eval")`, truncated as r1 does.

## (b) Detector

The detector is the frozen cells' own: `study003.detector_C(p, 28, "A")`, then `study003.cusum` with
`k = 0.5`. `h = 1.898499` comes from `tuning_003.json` cell 0.7, B 28, A-k0.5 (section 5's "cells reuse
phi 0.7's h"). The detector uses the matched filtered baseline and starts the CUSUM on day 28. Alarms come
from the unchanged frozen code. The script asserts the following, and it imports `drift_sim.py`,
`attribution.py` and `study003.py` unchanged:
- the sha256 values of `study003.py`, `tuning_003.json`, `drift_sim.py` and `attribution.py` are the ones
  PREREG-003 lists;
- `PREREG-003.md` itself has sha256 `06ee4757...`;
- `results_003.json` records that prereg sha and the same four file hashes.

`--check` recomputes `run_study`'s five cell metrics S false alarms per month and DR-1.0 21-day
sensitivity at n 60 with this script's code and asserts they are equal to 4 decimals. It also asserts that
S and DR-1.0 in a cell share persons: `L`, `Y - D`, and pre-onset `used` and `responded` are equal.

## (c) Rules (r1 section d, unchanged except where marked)

Each rule is applied to every alarm on day `t` in [28, 210). An alarm is "scored" if it falls in that range.

- **M0.** Every alarm is read as person change.
- **M1.** r1's 14-day concentration statistic `Q`: `attribution.q_stat` with window `t-13..t`, at least 3
  usable days per indicator, and `J' >= 3`. The alarm is read as person change when `Q < q*` or when `Q`
  is not assessable.
  - Per-indicator z: `study003.zscores(p, 28)` with days of `reason > 0` blanked, which is `study003.q_at`'s
    masking. These are the z-scores the cell composite averages; `--check` asserts that they average
    exactly to it.
- **M2.** One probe on `t + 1` (`attribution.confirmed`, offset 1). It reads as person change when the
  answer exceeds the mean of the answered baseline probes on days 6, 13, 20 and 27 by at least 0.5. No
  answer, or fewer than 2 answered baseline probes, reads as not confirmed.
- **M2x3.** Probes on `t + 1`, `t + 3` and `t + 5`. The mean of the answered ones is compared with the
  same baseline and the same margin. No answer reads as not confirmed.
- **M3.** M1 and M2x3. Reported because r1 reports it.

**q\*.** r1's rule on this detector: the 90th percentile of `Q` over every DR-1.0 alarm on days
`[t0, t0 + 21)`, with `t0 >= 28` by construction. It is computed on a separate tuning panel: reference cell,
1000 persons (r1's tuning N), base tag `tune`. One `q*` serves every cell (the r1/r2 precedent).

## (d) Metrics (person bootstrap, 2000 draws, `attribution.boot`)

Per cell, for each rule M1, M2, M2x3 and M3:

1. **S share.** Person-attributed over scored alarms on days [41, 210) (primary, D6), and over [28, 210)
   (secondary). Also reported: the S M0 rate per tracked person-month on days [28, 210), which is the cell's
   `S_fa_per_month` definition.
2. **DR-1.0 shares.** Over `[t0, t0 + 21)` and over `[t0, 210)`.
3. **DR-1.0 21-day sensitivity** under each rule, and its ratio to M0. As in r1, this uses
   `drift_sim._sensitivity` with `exclude_pre_onset_alarms=True`: a pre-onset person-attributed alarm makes
   the person undetected under that rule.
4. **Separation.** DR `[t0, 210)` share minus S share (primary S window, and the [28, 210) S window).
   This is paired: one resample index for both families.
5. **Diagnostics.**
   - The share of all scored alarms where `Q` is not assessable, per family.
   - The share answered on `t + 1`, for S on [41, 210) and for DR on `[t0, t0 + 21)`.
   - Momentary-state selection (r1's metric 4): mean `D_t`, `D_{t+1}` and mean `D` over `t+1, t+3, t+5`
     on scored alarms (S [41, 210), DR `[t0, 210)`), against mean `D` on tracked days in the same window.
     The bases of E3 and E4 rest on r1's values from a different detector, and this shows whether they
     carry over.
6. **Cell minus reference.** For the primary S share and DR `[t0, t0 + 21)` share under M1, M2 and M2x3,
   and for the primary M2x3 separation. The two panels are resampled independently.

Sanity reading, not a check that can fail the run: this round's M0 S rate and M0 DR sensitivity are set
beside `results_003.json`'s values, with z = (r5 - frozen) / combined SE.
- Each of the five cells is compared with its frozen cell.
- The reference cell is compared with `detection.phi0.7_B28_A-k0.5` (S rate and DR-1.0 `sens21`).

These are the same definitions on different seeds, so |z| above about 3 would mean the cell construction
differs.

## (e) Deviations from r1, stated before running

| # | r1 | here | reason |
|---|---|---|---|
| D1 | frozen A-fixed, `h = 3.334`, baseline on unfiltered `X`, help on, T 140 | spec 003's A-fixed k = 0.5, `h = 1.898499`, matched baseline, help off, T 210 | the brief asks for the spec 003 cells; their alarms come from this detector |
| D2 | scored alarms on days 28-134 | days 28-209 | r1's cutoff existed because T = 140 left no room for `t + 5`; here probes run to day 296 |
| D3 | S share over `[max(c_i, 28), 134]` (paired PS change day) | every scored S alarm | the cells have no PS family, so S has no change day |
| D4 | q* on a default-cell DR panel | q* on this round's reference-cell DR-1.0 panel, every in-window alarm | same rule on the cells' detector. `tuning_003.json`'s `q_star` (3.921) used first detections only and is reported beside it, not used |
| D5 | families S, PS-sub, PS-prop, DR, AV2, CS | S and DR-1.0 | the frozen cells contain only these two; no observer-change family is added |
| D6 | no scored window reached day 28 (S from `c_i >= 50`, DR from `t0 >= 50`) | primary S window starts on day 41; [28, 210) is secondary | an alarm on days 28-40 has a Q window holding baseline-fit days 15-27 (in-sample z), and the day-27 baseline probe correlates with `D_{t+1}` (Opus pre-hash review). DR's `t0 >= 70` is unaffected |
| D7 | DR onset U{50..100}, ramp U{7..21} | onset U[70, 120], same ramp | spec 003's cell generator |
| D8 | N 1000 per family | N 4000 (tuning panel 1000) | PREREG-003's evaluation N |
| D9 | alarms possible before day 28, and their refractory period could block days 28-41 | C held and no alarm before day 28 | spec 003's CUSUM starts at its baseline |
| D10 | r1 metrics (e)1 rates per person-month for M1-M3, and (e)5 probe cost | not computed | the brief asks for shares; the S M0 rate is kept as the cell's own metric |

## (f) Expectations, stated before running (exploratory; scored mechanically on point estimates, never confirmatory)

S shares here mean the primary [41, 210) window.

| | expectation | basis |
|---|---|---|
| K | (calibration) reference DR `[t0, t0+21)` M1 share within 0.05 of 0.9 | q* is DR's 90th percentile, though on another panel |
| E1 | in every cell, \|cell minus reference\| < 0.05 for the M1 S share and the M1 DR `[t0, t0+21)` share | the cells change usage or probe response, not the indicator model |
| E2 | DR `[t0, t0+21)` shares fall with `m1`: reference > m1_0.5 > m1_1.5 under both M2 and M2x3 (point estimates); m1_1.5 over reference is at most 0.5 for M2 and at most 0.8 for M2x3 | the answer probability at `D` near 1.3 to 1.5 is `expit(logit 0.8 - m1 D)`: about 0.30 to 0.37 at m1 1.5 against 0.8, and answered days select lower `D` |
| E3 | the S M2 share at m1_1.5 is at least 0.10 below reference | S alarm days carry `D_{t+1}` near 1 (r1: 0.98), so answers fall to about 0.47 |
| E4 | the M2x3 separation (DR minus S) is smaller at m1_1.5 than at reference (point estimate) | DR's probe days carry higher `D` than S's, so DR loses more answers |
| E5 | in the three usage cells (`kappa` +-0.3, change-dependent 0.3), \|cell minus reference\| < 0.05 for the M2 and M2x3 DR `[t0, t0+21)` shares (point estimates) | `responded` does not depend on use in the generator. With about 1100 DR window alarms per cell, 0.05 is about 2.4 SE of a cell-minus-reference difference, so a true null fails one of the six comparisons roughly 6-9% of the time; a miss near 0.05 is read against its interval |

## (g) What this does not do

- It does not edit `drift_sim.py`, `study003.py`, `attribution.py`, `PREREG-003.md`, `tuning_003.json`,
  `results_003.json` or paper v4.
- It adds no generator mechanism and no observer-change family to the cells.
- It reads no real data.
- It does not use a PREREG or PREREG-003 seed.
- It makes no claim about the frozen cells' confirmatory metrics.
- M1 ignores variance changes, as in r1.
- Commits are local. Pushing is the owner's call (constitution VII).
