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
