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
