# When re-centring the unmapped indicators pays: break-even false-alarm weight and concurrent-shift share

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs how the
paper states the observer-step choice (re-centre the unmapped indicators at a logged change, L1, or not,
L1_step). It decides nothing and changes no spec.

Code: `sim/break_003.py` -> `sim/break_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, W 14, the
design run's resample matrix, NET-003's DR+PS pair, in-window persons (n = 247). `step_003.py`, `obs_003.py`,
`load_003.py`, `unlog_003.py` and everything they import are unchanged.

## Why

HYB-003 reduced L1 vs L1_step to one question (re-centre the unmapped indicators or not) and said the answer
depends on two quantities simulation cannot supply: how often an unlogged change coincides with a logged one
(p), and how strongly D loads on the unmapped indicators early (rho). A third quantity was fixed silently: the
weight on false alarms.

STEP-003 and HYB-003 scored the trade-off as `trade` = `dd` - added, called 1:1. With the shift in both arms,
`dd` = A(f+s) - A(c+s) and added = A(c+s) - A(c), where A is the in-window alarm share. So
`trade` = A(f+s) - 2 A(c+s) + A(c): the false alarms under the shift are counted twice (once inside `dd`, once
as added), and the no-change false-alarm rate A(c) enters with a plus sign. In the usual form U = TPR - w FPR
(w = cost of a false alarm in units of a detection, which also carries the ratio of no-change to D-change
persons), STEP-003's `trade` for L1_step - L1 equals U at w = 2 with the shift in every person, plus the
no-change FPR difference. From `step_003.json` and `obs_003.json` points (k 0.5, 63 d, rho 1, `conc0.5`), before
this run:
- `trade` -0.162 = U(w 2, p 1) -0.069 + no-change FPR difference -0.093;
- at w = 1 (Youden), U(p 1) = `dd` = +0.117: L1_step is ahead even when every logged change has the concurrent
  shift;
- L1 is ahead at p = 1 only for w above 1.63 (= TPR difference 0.304 / FPR difference 0.186).

So the trade-off STEP-003 and HYB-003 reported holds only for false-alarm weights above about 1.6 at rho 1,
63 d. This phase maps where L1 overtakes L1_step across w, p and rho, with intervals, instead of at one point.

## Plan (committed before the run)

Rules L1 and L1_step (as in STEP-003). For each rho in LOAD-003's sweep (0, 0.5, 1, 2), each shift arm of
STEP-003 part C (`conc0.5`, `conc-0.5`, `post0.5`; the shift is in the D arm and the no-D-change arm), detectors
A-fixed `k = 0.5` (primary) and `k*`, horizons 21, 42 and 63 d, the paired differences L1_step - L1 in:
- T0 = TPR without the shift, A(f_rho); F0 = FPR without the shift, A(c);
- Ts = TPR with the shift, A(f_rho + s); Fs = FPR with the shift, A(c + s).

A share p of persons carries the shift (the expected share for a random p-subset, so exact as a weighted mean):
U(w, p) = (1 - p)(T0 - w F0) + p(Ts - w Fs), for w in {1, 2, 4} (a CHOICE grid, not a recommendation) and
p in {0, 0.5, 1}. Break-even p*(w): the share up to which L1_step's U is at least L1's. U is linear in p, so
p* = U(w,0) / (U(w,0) - U(w,1)) when U(w,0) > 0 > U(w,1); p* = 1 when U(w,0) > 0 and U(w,1) >= 0 (no
break-even on [0, 1]); p* = 0 when U(w,0) <= 0. Intervals: the same person bootstrap, p* computed in each
resample (clipped as above, so interval ends at 0 or 1 mean "at the boundary").

Asserts: for every rho, T0 - F0 reproduces `step_003.json` part A exactly; at rho 1, Ts - Fs reproduces part C
`dd`, Fs - F0 reproduces part C added, and U(2, 1) + F0 equals part C `trade` (points, 3e-4).

Expected (k 0.5, 63 d, in-window, `conc0.5` unless stated; rho 1 points are derivable beforehand, as above, so
the expectations are about the other rhos and the intervals):
1. The asserts pass.
2. At w = 1, U(1, 1) is positive (point) at every rho, with an interval excluding 0 at rho 1 and 2. So
   p*(1) = 1 at every rho: under Youden weighting, no share of concurrent unlogged shifts makes L1 better.
3. p*(2) and p*(4) are non-decreasing in rho (points). p*(2) < 1 at rho 0 and 0.5; p*(4) < 1 at every rho.
4. `post0.5`: p*(w) = 1 for every w at rho 0.5, 1 and 2 (points): L1 does not absorb a shift that starts after
   the hold, so it has nothing to gain there.
5. Precision: the p*(2) interval at rho 1 is wider than 0.3. That is, at n = 247 the break-even share is poorly
   determined even in simulation.

Reading (not an expectation): if 2 and 3 hold, the paper can state the observer-step choice as a condition on
w and p rather than a trade-off, and Study 1 needs only rough estimates of p and rho to place itself.

## Results (run after the plan commit `de324fe`)

`break_003.json` sha256 81e41b0e7dcb5ebb481c6dfd5b5a5f37bae0953b060830cddd1c002ba74cd238; the rerun was
byte-identical (`cmp`). Every assert passed: part A for every rho, part C added (equal to part B's; the code
comment says part B) and part C `dd` at rho 1, and the trade identity (`trade` = U(2, 1) + F0) in all 18 rho-1
cells. Run time about 3 minutes. Values are L1_step - L1, rounded to 3 dp from the 4-dp JSON, so sums can differ
by 0.001.

Table 1. k 0.5, 63 d, `conc0.5`. U(w, 1) is every logged change carrying the concurrent +0.5 shift.

| rho | U(1, 0) = T0 - F0 | U(1, 1) | U(2, 1) | p*(1) | p*(2) | p*(4) |
|---|---|---|---|---|---|---|
| 0 | 0.049 | -0.028 [-0.087, 0.027] | -0.215 [-0.315, -0.123] | 0.63 [0, 1] | 0.40 [0.16, 0.60] | 0.36 [0.17, 0.53] |
| 0.5 | 0.093 | 0.049 [-0.013, 0.114] | -0.138 [-0.244, -0.041] | 1 [0.83, 1] | 0.58 [0.32, 0.84] | 0.42 [0.22, 0.61] |
| 1 | 0.150 | 0.117 [0.044, 0.189] | -0.069 [-0.188, 0.042] | 1 [1, 1] | 0.78 [0.51, 1] | 0.49 [0.29, 0.69] |
| 2 | 0.243 | 0.158 [0.080, 0.240] | -0.028 [-0.155, 0.092] | 1 [1, 1] | 0.92 [0.66, 1] | 0.57 [0.37, 0.77] |

Components (rho 1): T0 0.057 [0.004, 0.112], F0 -0.093 [-0.146, -0.038], Ts 0.304 [0.243, 0.365],
Fs 0.186 [0.133, 0.243]. F0 does not depend on rho or the arm.

Table 2. k 0.5, 63 d, other arms, p*(1) / p*(2) / p*(4) points.

| rho | `conc-0.5` | `post0.5` |
|---|---|---|
| 0 | 0.35 / 1 / 1 | 1 / 1 / 1 |
| 0.5 | 0.64 / 1 / 1 | 1 / 1 / 1 |
| 1 | 1 / 1 / 1 | 1 / 1 / 1 |
| 2 | 1 / 1 / 1 | 1 / 1 / 1 |

`k*`, 63 d, `conc0.5`: p*(2) 0.36, 0.60, 0.83, 0.84 and p*(4) 0.31, 0.39, 0.45, 0.50 at rho 0, 0.5, 1, 2;
p*(1) = 1 at every rho (rho 0 interval [0, 1]).

**A limit of the planned p*.** p* is defined from p = 0 upward, so it is 0 whenever U(w, 0) <= 0, including when
L1_step is behind at p = 0 but ahead at p = 1 (the crossing runs the other way). That happens (U(w, 0) <= 0 < U(w, 1)) in 24 of the 216
(rho, arm, detector, horizon, w) combinations, all at 21 or 42 d and 20 of them at `k*`; every |U| involved is at
most 0.085 (27 with the tie convention U(w, 0) < 0 <= U(w, 1)). In those, p* = 0 understates L1_step. In every k 0.5 63 d cell U(w, 0) > 0, so
Tables 1 and 2 are unaffected. Intervals of [0, 1] mean U(w, 0) straddles 0 across resamples, not that p* is
anywhere in [0, 1]; 72 of the 216 have one, 68 of them at 21 or 42 d.

Horizons: at 21 d, L1 and L1_step barely differ without the shift for rho up to 1 (k 0.5 U(1, 0) -0.004 to 0.012;
`k*` -0.016 to -0.012 at every rho). At rho 2, k 0.5, the difference is 0.077 [0.031, 0.123]. So the choice matters
mainly at 42 and 63 d, except at high rho.

Expectations (k 0.5, 63 d, `conc0.5`):
1. **Met.** All asserts pass.
2. **Failed** (rho 0; the other clauses met). U(1, 1) is -0.028 [-0.087, 0.027] at rho 0, so p*(1) = 0.63
   there, not 1. At rho 0.5, 1 and 2 it is positive (0.049, 0.117, 0.158) with intervals excluding 0 at 1 and 2,
   and p*(1) = 1.
3. **Met.** p*(2) rises 0.40, 0.58, 0.78, 0.92 and p*(4) 0.36, 0.42, 0.49, 0.57; both are < 1 at every rho.
4. **Met.** `post0.5`: p*(w) = 1 for every w at every rho, rho 0 included.
5. **Met.** The p*(2) interval at rho 1 is [0.51, 1], width 0.49.

Reading:
1. **STEP-003's and HYB-003's "1:1 trade" is not 1:1 in TPR:FPR terms.** It equals U at w = 2 with the shift in
   every person, plus the no-change FPR difference F0. The F0 term credits whichever rule has the higher no-change
   false-alarm rate. At rho 1 (k 0.5, 63 d, `conc0.5`) it is -0.093 of the -0.162, and without it the result covers
   0 (U(2, 1) -0.069 [-0.188, 0.042]). Under Youden weighting (w = 1; k 0.5, 63 d), L1_step is at least as good as
   L1 at every share p of concurrent +0.5 shifts from rho 0.5 up (points; the interval on U(1, 1) excludes 0 from
   rho 1). At `k*`, 63 d this holds from rho 0. STEP-003 finding 3 ("neither rule dominates", at rho 1) holds at
   w = 2 and 4 in point sign. At rho 1 and w = 1, L1_step is ahead at every p in all three arms (k 0.5, 63 d). The
   identity applies to HYB-003's step-3 trade too, but this run does not evaluate that contrast at other w.
2. **Where L1 wins (k 0.5, 63 d, `conc0.5`), it needs both a heavy false-alarm weight and a common coincidence.** At
   w = 2, L1 is ahead only when more than 40% (rho 0) to 92% (rho 2) of logged changes carry the shift; at w = 4,
   more than 36% to 57%. Even at p = 1, L1's lead at w = 2 is not detectably different from 0 at rho 1 and 2
   (U(2, 1) intervals cover 0). The p*(2) intervals are 0.34 to 0.52 wide. At 42 d (k 0.5), L1 is never ahead at w = 2 for rho >= 1.
3. **The shift's sign matters (k 0.5, 63 d).** At w = 1, L1 is ahead at high p in two cases: a concurrent -0.5 shift
   (p* 0.35 at rho 0, 0.64 at rho 0.5) and a +0.5 shift at rho 0 (p* 0.63). At w = 2 and 4, under `conc-0.5`,
   L1_step is ahead at every p. This comes from fewer false alarms, not better detection: L1_step's FPR is lower
   than L1's under the shift (Fs -0.231 [-0.285, -0.178]), and its TPR is lower too (Ts -0.215 [-0.274, -0.154] at
   rho 1), as in STEP-003 finding 5. A shift that starts after the hold never favours L1 at 63 d (both detectors).
4. **For Study 1 and the paper,** the decision then needs three inputs, not two: rho, p (with the sign of typical
   coinciding changes) and w. w is a value judgement. The paper can state the rule as: re-centre when coincident unlogged changes are common
   enough to pass the break-even p*(w), which falls as w rises and rises with rho (Table 1). At w = 1 that happens
   only near rho 0. These synthetic break-evens hold at k 0.5, 63 d.

Reviews: ponytail (plan, code), no cuts; Opus accuracy check REVISE, 6 blocking (all in the reading) and 7
non-blocking items, all applied, numbers and algebra confirmed; ponytail (text) 5 of 8 cuts applied.
