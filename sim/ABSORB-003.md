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

## Results (DESIGN STAGE, synthetic; they inform wording and score nothing)

Provenance: code `absorb_003.py` at commit `7023a4b`, output `absorb_003.json` sha256
`38e7c2dad64b518b9342dbd2e3dd27be1bc8ee044b930ee7824929e5f1166841`. A second run reproduced it byte for byte
(`cmp`). Every assert passed: L1, L0 and the oracle rule reproduce `net_003.json` at both W, both detectors and
all three horizons. Intervals are 95% paired person-bootstrap intervals over the design run's resample matrix,
"est [lo, hi]". In-window persons, n = 247. "D-dependent" is NET-003's measure (raw minus the no-change rate
per person), so the caveats there apply: it credits D with any interaction and scores a person who alarms in
both arms as 0.

### The table (A-fixed `k = 0.5`, W = 14, D-dependent sensitivity)

| variant | 21 days | 42 days | 63 days | no-change rate, 63 days |
|---|---|---|---|---|
| L1 | 0.057 | 0.186 | 0.190 [0.147, 0.241] | 0.304 |
| L1_sdCF | 0.057 | 0.194 | 0.198 | 0.304 |
| L1_meanCF | 0.101 | 0.324 | 0.340 | 0.304 |
| L1_bothCF | 0.109 | 0.332 | 0.348 [0.293, 0.407] | 0.304 |
| L1_sdB | 0.065 | 0.182 | 0.194 | 0.279 |
| oracle rule | 0.126 | 0.332 | 0.441 [0.382, 0.504] | 0.211 |

Paired differences, D-dependent:

| difference | k 0.5, W 14, 63 d | k*, W 14, 63 d | k 0.5, W 21, 63 d |
|---|---|---|---|
| L1_bothCF - L1 (absorption, all) | 0.158 [0.117, 0.206] | 0.182 [0.136, 0.231] | 0.227 [0.175, 0.285] |
| L1_meanCF - L1 (mean channel) | 0.150 [0.110, 0.198] | 0.182 [0.137, 0.233] | 0.207 [0.157, 0.264] |
| L1_sdCF - L1 (SD channel) | 0.008 [0.000, 0.021] | 0.000 [0.000, 0.000] | -0.004 [-0.025, 0.016] |
| L1_sdB - L1 | 0.004 [-0.051, 0.058] | 0.016 [-0.036, 0.063] | 0.036 [-0.012, 0.083] |
| oracle - L1_bothCF (left over) | 0.093 [0.012, 0.174] | 0.061 [-0.026, 0.149] | 0.061 [-0.027, 0.146] |
| oracle - L1 | 0.251 [0.172, 0.322] | 0.243 [0.159, 0.318] | 0.287 [0.214, 0.356] |

Mechanism (point values, in-window persons, all six indicators): the absorbed share (the mean `D` step over
the used hold days) averages 0.40 at W = 14 and 0.58 at W = 21. The hold mean is 0.134 baseline SD higher with
the ramp than without it at W = 14 (0.192 at W = 21). The hold SD with the ramp is a median 1.008 times the
hold SD without it (1.011 at W = 21), and the no-ramp hold SD is a median 0.987 times the baseline SD.

### Against the expectations

1. **Reproduction: yes.**
2. **Removing the ramp from the re-baseline lifts L1 by at least half the gap to the oracle rule: yes.** 0.158
   of the 0.251 gap (63%) at 63 days, interval excluding 0, at k 0.5, W 14; also at k* and W = 21 (table).
3. **The mean channel is larger than the SD channel: yes,** and the SD channel is about nil (table; mechanism
   paragraph). NET-003's "absorbs part of the ramp" is an absorption of the ramp into the new mean.
4. **Dose: yes, borderline.** L1's 63-day D-dependent sensitivity by absorbed-share tertile (low to high) is
   0.229, 0.232 and 0.110; top minus bottom -0.119 [-0.233, -0.003] (k*: -0.156 [-0.278, -0.043]; W = 21:
   -0.120 [-0.224, -0.013]). L1_bothCF: 0.265, 0.427, 0.354; top minus bottom 0.089 [-0.052, 0.238], covering 0.
   The oracle rule is flat (-0.019 [-0.167, 0.135]). L1's own values are flat over the bottom two tertiles and
   drop in the top one (absorbed share above 0.45 at W = 14), but its cost against L1_bothCF, which shares L1's
   hold and reset, rises across all three: 0.036, 0.195 and 0.244 (point values, no interval; k*: 0.12, 0.12,
   0.30; W = 21: 0.10, 0.23, 0.35). The cost is not confined to the top tertile, and the tertiles do not locate
   a threshold.
5. **L1_sdB - L1 positive and smaller than the mean channel: smaller, yes; positive only as a point estimate,
   not detectable** (0.004 [-0.051, 0.058]). L1_sdB lowers L1's no-change rate (0.304 to 0.279) and its raw
   rate together.
6. **Absorption costs more at W = 21: yes as a point estimate, not tested** (0.227 against 0.158 at 63 days,
   k 0.5; no interval on the difference).
7. **The left-over gap shrinks from 21 to 63 days: no.** At k 0.5, W 14, oracle - L1_bothCF is 0.016
   [-0.039, 0.069], 0.000 [-0.081, 0.081] and 0.093 [0.012, 0.174] at 21, 42 and 63 days: L1_bothCF matches the
   oracle rule to 42 days and falls behind after. As point estimates it shrinks at k* (0.105 to 0.061) and at
   W = 21, k 0.5 (0.122 to 0.061); no interval on either change. At 63 days (k 0.5, W 14) L1_bothCF's raw rate
   equals the oracle rule's (0.652 and 0.652), so the whole 0.093 is the no-change-rate gap (0.304 against
   0.211). A candidate, not tested: the 14-day re-baseline mean is noisier than the 28-day baseline, which would
   raise L1_bothCF's no-change rate (the both-arms caveat above).

### What this changes (proposals, not decisions)

1. **The paper and PREREG-003 can name L1's DR+PS cost at 42 to 63 days.** On these persons, most of L1's
   shortfall against the oracle rule at 63 days (item 2) is the re-baseline absorbing the part of the `D` ramp
   that happens during the hold: 0.158 with mean and SD together, 0.150 for the mean alone. This is the cost of
   absorption given L1's hold and reset; the attribution depends on that order. At k 0.5, W 14, what is left
   once the ramp is removed from the re-baseline (oracle - L1_bothCF) is 0.016 [-0.039, 0.069] at 21 days and
   0.000 [-0.081, 0.081] at 42; at k* it is 0.105 [0.058, 0.151] and 0.065 [-0.020, 0.147], and at W = 21,
   k 0.5, 0.122 [0.081, 0.165] at 21 days. That remainder bundles the hold, the S reset and the noise of a
   14-day re-estimate; this run does not separate them.
2. **Keeping the baseline SD does not fix it** (L1_sdB). Every variant that does fix it here uses the no-change
   arm, which exists only in simulation. An implementable candidate is not tested here: estimate only the
   observer step, on the indicators the log maps, so the ramp on the other indicators is not absorbed. L2 is
   near this: it re-baselines indicators 1, 2 and 6 only, and its 63-day D-dependent value in NET-003 is 0.344.
   But L2 still re-baselines 1, 2 and 6 over the hold, where D also loads, and keeps S running; its 0.344 being
   near L1_bothCF's 0.348 is not evidence that the two work the same way.
3. **Whether H4 (L2 - L1) carries this mechanism is not tested.** H4 is scored at 21 days. There, removing the
   ramp from L1's re-baseline raises L1 by 0.053 [0.027, 0.081] (k 0.5, W 14; H4 D-dependent 0.077 [0.032,
   0.123]), 0.028 [0.011, 0.052] at k* (H4 0.109), and 0.004 [0.000, 0.013] at W = 21 (H4 0.162), so at W = 21
   H4 is almost entirely something other than absorption. This run does not split H4.
