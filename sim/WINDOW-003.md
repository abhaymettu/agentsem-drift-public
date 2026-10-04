# The re-baseline window: 14 against 21 and 28 days

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This is evidence for
DECIDE-003's H3 decision, which is his to make. It decides nothing and changes no spec.

Code: `sim/window_003.py` -> `sim/window_003.json`. Tuning seed and design seed 20261003, with the design run's
resample matrix. The window is patched at runtime (`ds.REBASELINE_WINDOW`). `study003.py` and spec 003 are
unchanged.

## Why

DECIDE-003 gave three options for H3. One is to move the re-baseline window from 14 to 21 days, which, it said,
would need the tuning and the design run redone. It left three things unmeasured under 21: PS-use's H3 ratios,
H4, and `policy_log`'s in-window mask.

In `study003.py` the window is read in two places only: the L1/L2 hold in `apply_log`, and H4's in-window mask.
L0 returns before reading it, and the tuning runs on L0 alone. If that reading is right, a new window leaves the
tuning and everything outside `policy_log` unchanged. This run tests that rather than assuming it.

## Plan (committed before the run)

For W = 21 and 28:
1. Rerun the tuning; compare with `tuning_003.json`.
2. Rerun the whole design run; compare every leaf with `design_003.json` (W = 14) and list what changed.
3. DECIDE-003 part (a)'s evaluation-N sizing on the new `policy_log`.
4. H4 on the design's population (logged DR+PS, onset in `[c, c + 13]`) as well as on W's own population,
   which spec 003 s8 defines by the window. W = 14 must reproduce the design's H4.

Expected:
- The tuning is identical, and no leaf outside `policy_log` changes.
- Inside `policy_log`, only leaves from rules L1 and L2 change, plus H4 and its counts. L0, the oracle rule,
  L0+label, H5 and AV's L0 arm do not.
- Logged PS-use's L1/S falls below 1.5 at W = 21, as PS-sub's did (1.025 in DECIDE-003).
- H4 grows with W on both populations: L1 loses more of the true change, and L2 holds.

What does not follow from any of this: L0+label's `W = 14` is justified in spec 003 s8 as matching the
re-baseline window. A window change breaks that match, and the label window would be his to restate.

## Results (DESIGN STAGE, synthetic; they inform his decision and score nothing)

Provenance: code `window_003.py` at commit `f4cf416` plus no later edit, output `window_003.json` sha256
`b29a95b5c11129068eb2b5d5ff737c8bcb70ed35ea9f980d5eded8834a8ce0b4`; a second run reproduced it byte for byte
(`cmp`). The W = 14 assert passed: H4 on the design's population reproduces `design_003.json` (0.1538).
Intervals are 95% paired person-bootstrap intervals over the design run's resample matrix, "est [lo, hi]".

### Against the expectations

1. **The tuning is identical: yes.** `run_tune()` under W = 21 and W = 28 equals `tuning_003.json` (`c`, `k*`,
   every `h`, `q*`). A window change needs no retuning.
2. **Nothing outside `policy_log` changes: yes.** 8476 leaves were compared (all of `design_003.json` except
   its 5 label and provenance leaves). 734 change at W = 21 and 735 at W = 28. All are in `policy_log`, and each
   belongs to an L1 or L2 arm, to H4 or to `L2_minus_L1`. L0, the oracle rule, L0+label, H5, PS-endo and AV's L0
   arm are unchanged. The two changed sets are not nested: three confirmation-share leaves (two SEs, one
   estimate) equal their W = 14 value at one window but not the other.
3. **PS-use's L1/S falls below 1.5 at W = 21: yes** (0.985, table).
4. **H4 grows with W: yes. "On both populations": the premise was wrong.** The DR+PS generator sets the change
   day at `t0 + U[-5, 5]` (`study003.py` `events`). Every logged onset therefore falls at most 5 days after the
   change, and any window of 6 days or more holds the same 247 persons. H4's population does not move with W
   in this design, and the two H4 versions are the same number.

### H3 and H4, A-fixed `k = 0.5`, `phi_D` 0.7 (PS rows: logged persons; DR+PS rows: as labelled)

| quantity | W = 14 (design) | W = 21 | W = 28 |
|---|---|---|---|
| PS-sub L1/S | 1.421 [1.175, 1.706] | 1.025 [0.831, 1.230] | 0.836 [0.658, 1.027] |
| PS-sub L2/S | 1.171 [1.034, 1.307] | 1.051 [0.929, 1.176] | 1.014 [0.904, 1.134] |
| PS-use L1/S | 1.376 [1.135, 1.647] | 0.985 [0.804, 1.204] | 0.861 [0.689, 1.052] |
| PS-use L2/S | 1.101 [0.970, 1.233] | 1.053 [0.931, 1.174] | 1.038 [0.929, 1.158] |
| PS-prop L1/S | 2.604 [2.217, 3.067] | 1.656 [1.360, 1.971] | 1.275 [1.044, 1.550] |
| PS-prop L2/S | 2.304 [1.963, 2.711] | 1.365 [1.129, 1.618] | 0.973 [0.797, 1.188] |
| H4: DR+PS L2 minus L1, onset in window (247) | 0.154 [0.100, 0.209] | 0.308 [0.256, 0.366] | 0.316 [0.262, 0.373] |
| DR+PS L1 sensitivity, onset in window | 0.113 [0.078, 0.154] | 0.004 [0.000, 0.013] | 0.004 [0.000, 0.013] |
| DR+PS L2 sensitivity, onset in window | 0.267 [0.217, 0.322] | 0.312 [0.260, 0.370] | 0.320 [0.264, 0.379] |
| DR+PS L0 / oracle rule, onset in window | 0.526 / 0.227 | same | same |
| DR+PS L1 sensitivity, all persons | 0.315 [0.289, 0.346] | 0.285 [0.260, 0.316] | 0.285 [0.260, 0.316] |
| AV logged, L1 FA per tracked month | 0.203 [0.178, 0.231] | 0.161 [0.140, 0.186] | 0.146 [0.126, 0.168] |

Under A-fixed `k*` the pattern is the same. PS-sub L1/S is 1.217, 0.835 and 0.671; PS-use L1/S is 1.177,
0.848 and 0.706; DR+PS L1 sensitivity in window is 0.024, 0.000 and 0.000; H4 is 0.190, 0.251 and 0.263.

**Evaluation-N sizing at W = 21** (DECIDE-003 part a, design estimate taken as true): every H3 clause, H4 and H5
are projected to clear their threshold at interval level with probability at least 0.997 at N 1000. At
W = 14, H3's L1 clause was at most 0.49 at N 4000.

### What this means for the H3 decision (his)

- **Moving to 21 is cheaper than DECIDE-003 said.** It needs no retuning, and only the L1/L2 part of
  `policy_log` changes. Still needed if he picks it:
  - a study-003-local window constant in place of the two `ds.REBASELINE_WINDOW` reads (`apply_log` and
    `policy_log`'s in-window mask), leaving frozen `drift_sim.py` (whose rule (iv) reads the same constant)
    at 14;
  - `design_003.json` and DECIDE-003's sizing regenerated from committed code, since this run used a runtime
    patch;
  - the hard-coded "(c, c + 14]" in `apply_log`'s docstring and `policy_log`'s comment, spec 003 s8's L1 and L2
    rows ("over 14 days", "for 14 days"), and `DESIGN-003.md`'s H3/H4 figures.
- **H3 at 21 would pass almost by design, so it tests less.** The window is being chosen after H3's L1 clause
  sat on 1.5 at 14 on design data. DECIDE-003's second seed put PS-sub L1/S 0.235 higher at 14. The same
  shift at 21 would give about 1.26, still under 1.5.
- **The cost of the longer window falls on L1.** Within the 21-day scoring window, L1's in-window sensitivity
  is 0.004 (0.113 at 14). At W of 21 or more that window lies almost entirely inside L1's hold, so this follows
  nearly by construction, and it is why 21 and 28 give the same figure. Detection later than 21 days was not
  measured. The design places onsets only 0 to 5 days after the change. By the same mechanism, L1 is blind to
  any change that begins inside `(c, c + W]`.
- **L2's in-window sensitivity rises** from 0.267 to 0.312, against L0's 0.526 and the oracle rule's 0.227 (point
  estimates; no paired difference computed). H4, a construction check, reduces to L2's in-window sensitivity,
  because L1's is about 0.
- **28 days adds little for H3 over 21.** It matters for PS-prop, which H3 does not cover. PS-prop's L1/S at 21
  is above 1.5 in point estimate only. It reaches parity with S only under L2 at 28 (0.973 [0.797, 1.188]).
- **Not settled by this run:**
  - L0+label's `W = 14` is justified in spec 003 s8 as matching both the refractory period and the re-baseline
    window. A window change breaks the second match.
  - Whether the generator's `U[-5, 5]` onset offset (check 4) is the right design.
