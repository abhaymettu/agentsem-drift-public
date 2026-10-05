# Observer-step chain: which numbers to cite

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. This is a reading guide over committed results.** It maps each headline number from NET-003 through
BREAK-003 to its replication status in REP-003 (200 fresh populations, `rep_003.json`, sha256 4f046f45...), so a
paper table quotes the right column. Which rule the paper adopts (L1 or L1_step) and the false-alarm weight w
are his CHOICE items and are not set here.

Setting for every row unless stated: DR+PS pair, `phi_D` 0.7, W 14, k 0.5, 63 d, in-window persons, `conc0.5`
shift, rho = how much of D's realized effect reaches the unmapped indicators (LOAD-003). "Design" is the single
population (seed 20261003, 247 in-window persons) all of NET-003 to BREAK-003 ran on. "Generator" is the mean over
the 200 REP-003 populations (MCSE 0.002 to 0.004 for U, 0.007 to 0.014 for p*(2) and p*(4)).

## 1. Replicated: quote the generator column

| Quantity | Source | rho 0 | rho 0.5 | rho 1 | rho 2 |
|---|---|---|---|---|---|
| U(1, 0), D-dependent L1_step - L1 | STEP-003 A, design | 0.049 | 0.093 | 0.150 | 0.243 |
| | generator | 0.004 | 0.053 | 0.111 | 0.219 |
| U(1, 1), Youden, shift in every person | BREAK-003, design | -0.028 | 0.049 | 0.117 | 0.158 |
| | generator | 0.041 | 0.093 | 0.128 | 0.142 |
| U(2, 1) | BREAK-003, design | -0.215 | -0.138 | -0.069 | -0.028 |
| | generator | -0.148 | -0.096 | -0.061 | -0.047 |
| p*(2), break-even share | BREAK-003, design | 0.40 | 0.58 | 0.78 | 0.92 |
| | generator plug-in | 0.33 | 0.56 | 0.75 | 0.86 |
| p*(4) | BREAK-003, design | 0.36 | 0.42 | 0.49 | 0.57 |
| | generator plug-in | 0.29 | 0.35 | 0.42 | 0.50 |

Also replicated: L1_did - L1_step added false alarms, `conc0.5` (UNLOG-003): design 0.198, generator 0.225
(0.002); lower end above 0 in every population.

Where design and generator differ, the design values are one draw's sampling error, not a bias in the method (F0 at the 15.5th
percentile; REP-003.md finding 1).

Consequences for text and tables:
- In the generator, U(1, 1) is positive in 91% of
  populations, so L1_step >= L1 under Youden weighting at every rho when the shift is in every person.
- p*(1) at rho 0 is not stable (per-population values are 0 or 1 by the sign of a near-zero contrast; mean 0.54,
  SD 0.49). Do not tabulate it. For p*(2) and p*(4), design minus plug-in is at most 0.07.
- Claims C4b, C5, C6, C8 replicate in only 0.75 to 0.90 of populations (REP-003.md claim table); cite them with
  the share.
- At w = 2 the generator favours L1 at p = 1 at every rho; the population interval excludes 0 in only 16% (rho 1)
  and 9% (rho 2) of populations.

## 2. Still single-draw: cite with the population stated, or rerun on the 200 populations first

| Result | Source | Design value (k 0.5, 63 d unless stated) |
|---|---|---|
| L0 interaction of D change with observer change | FACT-003 | 0.154 [0.079, 0.224] (W 14, 21 d) |
| L1 gain from removing the D ramp from its re-baseline | ABSORB-003 | 0.190 to 0.348, +0.158 [0.117, 0.206] |
| L1_did - L1, D-dependent | OBS-003, LOAD-003 | 0.194 [0.105, 0.272] at rho 1; 0.012 / 0.105 / 0.194 / 0.316 at rho 0 / 0.5 / 1 / 2 |
| Added alarm share by rule, `conc0.5` | UNLOG-003 | L1 0.004, L1_step 0.283, L1_did 0.482, L2 0.397, oracle 0.300 |
| L1_step - L1_bsd, step 3 of the chain (re-centring unmapped) | HYB-003 | 0.040 [-0.013, 0.094] at rho 0 to 0.202 [0.138, 0.267] at rho 2; no-change step 3 -0.069 [-0.120, -0.025] |
| L1_step - L1 added false alarms by shift arm | STEP-003 B | `conc0.5` 0.279, `post0.5` 0.065 (covers 0), `conc-0.5` -0.138 (generator values derivable from `rep_003.json` as Fs - F0, not computed here) |

The L1_did - L1 values are L1_step - L1 values plus L1_did - L1_step, so the rho-0 reading carries the same F0
and T0 draw as section 1. The F0 draw offsets part A by 0.024 w at every rho, so treat every rho in the OBS/LOAD row as design-draw-sensitive, most at rho 0.
HYB-003's chain steps sum to L1_step - L1 (asserted there); REP-003 replicated the sum, not the steps.

REP-003 checked interval calibration for L1_step - L1 only (median coverage 0.945 over all cells; at 42 and 63 d, 1 of 272 distinct quantities below 0.90); the intervals in
the table above were not checked.

## 3. Draft results paragraph (for his edit)

Across 200 simulated populations of 1000 persons (227 to 309 in-window persons each), L1_step, which leaves the
unmapped indicators on their pre-change baseline at a logged observer change, exceeded L1, which re-centres them,
in D-dependent true-positive minus false-positive rate by a mean of 0.004 (MCSE 0.002) at rho 0, rising to 0.219
at rho 2 (k 0.5, 63 d; rho scales D's realized effect on the unmapped indicators, 1 as generated; the two rules
also differ in mapped-indicator treatment and hold SD, which HYB-003 decomposes). When an unlogged shift on
the unmapped indicators coincides with the logged change in every person, L1_step's advantage under equal
weighting is 0.041 at rho 0 and 0.093 to 0.142 at rho 0.5 to 2; at twice the weight on false alarms, L1 is ahead
at every rho (-0.148 to -0.047). The plug-in break-even share of logged changes with a concurrent unlogged shift,
at that weight, is 0.33 at rho 0 and 0.86 at rho 2.

## 4. For him to decide

- Whether the paper tables cite section 1's generator column and drop the design-draw rho-0 readings.
- Whether committed STEP-003.md, BREAK-003.md and HYB-003.md get a pointer to REP-003 for those readings.
- Whether the section 2 results are rerun on the 200 populations (proposal at ~/code/agentsem/RUNLOG.md
  line 130: about 7 min wall at load ~100 for the observer-step numbers; may not cover the FACT, ABSORB and LOAD scripts).
