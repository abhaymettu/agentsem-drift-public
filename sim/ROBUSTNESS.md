# sim/ROBUSTNESS.md

EXPLORATORY, not frozen -- this grid is not part of sim/PREREG.md and changes no P1-P10 verdict. See sim/ROBUSTNESS-PLAN.md for the grid, the expectations stated before running, and the success rule.

## Summary: does each structural finding hold across the grid?

| finding | holds across grid | failing cells |
|---|---|---|
| S1 | False | lam_low |
| S2 | False | lam_low, phi_D_high, rising_slope_10 |
| S3 | True | none |
| S4 | False | m1_15 |
| S5 | True | none |
| S6 | True | none |

Per-cell values with intervals: `sim/robustness.json`, key `cells.<name>`.
