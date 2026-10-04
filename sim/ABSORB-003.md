# Why L1 plateaus on DR+PS: a test of ramp absorption by the re-baseline

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs how
PREREG-003 and the paper describe rule L1's cost on DR+PS. It decides nothing and changes no spec.

Code: `sim/absorb_003.py` -> `sim/absorb_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, the
design run's resample matrix, NET-003's paired arms (DR+PS, and the same persons with `delta_D = 0`).
`study003.py`, `decide_003.py`, `net_003.py`, `drift_sim.py` and spec 003 are unchanged.

## Why

NET-003 (expectation 6): for DR+PS persons with onset in `[c, c + 13]`, A-fixed `k = 0.5`, W = 14, L1's
D-dependent sensitivity is 0.057, 0.186 and 0.190 at 21, 42 and 63 days from onset; the oracle rule's is 0.126,
0.332 and 0.441. L1 gains to 42 days and is then flat. The reason given in NET-003's plan was not tested: L1
re-estimates every indicator's mean and SD over the hold `(c, c + W]`, and for these persons the `D` ramp
(onset `t0` in `[c, c + 13]`, ramp 7 to 21 days) is partly under way during the hold. The new mean then
contains part of the shift L1 is meant to detect, and the new SD contains the ramp's trend.

## Plan (committed before the run)

L1 variants that differ from L1 only in the series the post-hold mean and SD are estimated on. The hold days,
reason 4, the S reset on `c + 1` and the post-hold scoring of the panel's own series are L1's:

| variant | post-hold mean from | post-hold SD from | uses |
|---|---|---|---|
| L1 | own hold days | own hold days | the rule (reproduces NET-003) |
| L1_meanCF | no-D-change arm, same hold days | own | oracle information |
| L1_sdCF | own | no-D-change arm | oracle information |
| L1_bothCF | no-D-change arm | no-D-change arm | oracle information |
| L1_sdB | own | the detector's 28-day baseline SD | implementable |

The no-D-change arm is the same person with the same noise, usage, log and observer change, so L1_bothCF is L1
with the `D` ramp removed from the re-baseline only. On the no-D-change arm itself the CF variants equal L1.

For W in (14, 21), detectors A-fixed `k = 0.5` and `k*`, in-window persons (n = 247), horizons 21, 42 and 63 days:
1. Each variant's raw sensitivity, no-change rate and D-dependent sensitivity (NET-003's measures), with L0 and
   the oracle rule recomputed beside them.
2. Paired D-dependent differences: L1_bothCF - L1 (whole absorption), L1_meanCF - L1 (mean channel),
   L1_sdCF - L1 (SD channel), L1_sdB - L1, oracle - L1_bothCF (what is left: the hold and the reset), oracle - L1.
3. Dose: each person's absorbed share, the mean of the `D` step `clip((d - t0) / ramp, 0, 1)` over their used
   hold days. D-dependent sensitivity at 63 days by tertile of that share, per variant, and top minus bottom
   tertile.
4. Mechanism point values (in-window persons, all six indicators): the hold-mean difference between arms in
   baseline SD units, the median ratio of hold SDs between arms, and the median hold SD over baseline SD on the
   no-D-change arm.

Asserts: L1, L0 and the oracle rule reproduce `net_003.json` (raw, no-change rate, D-dependent) at every W,
detector and horizon; the two arms share the baseline; the log is exogenous.

Expected (k 0.5, W 14 unless stated):
1. The reproduction asserts pass.
2. L1_bothCF lifts L1's D-dependent sensitivity at 63 days from 0.190 by at least half the gap to the oracle
   rule, to 0.315 or more, and the paired interval excludes 0.
3. The mean channel is larger than the SD channel at 63 days.
4. L1's D-dependent sensitivity at 63 days is lowest in the top absorbed-share tertile, and its top-minus-bottom
   interval lies below 0. L1_bothCF's top-minus-bottom interval covers 0.
5. L1_sdB - L1 at 63 days is positive and smaller than L1_meanCF - L1.
6. L1_bothCF - L1 at 63 days is larger at W 21 than at W 14.
7. oracle - L1_bothCF is larger at 21 days than at 63 days (the hold blinds L1 early, then L1 catches up).
