# Decision evidence for PREREG-003

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This is evidence for
the proposals in `sim/DESIGN-003.md` section 4, which are his to decide. It decides nothing.

Code: `sim/decide_003.py` -> `sim/decide_003.json`. Design seed 20261003 (the design run's persons and
resample matrix); the sqrt(N) check uses 20261004. Neither is the tuning seed or a PREREG-003 evaluation seed.

## Plan (committed before the run)

**(a) Evaluation N.** Per drafted or proposed threshold: the chance that an evaluation run of 1000, 2000 or
4000 persons puts the point estimate, and the 95% interval, on the side the prediction needs. The calculation
takes the design estimate as the true value and lets the SE scale as 1/sqrt(N). One empirical check: H3's
logged PS-sub L1/S ratio at N 1000 and 2000 on a fresh seed, where the SE ratio should be near 1.41.

**(b) Probe budget** (spaced lag, 28 days, 4 probes, each `phi`). Three rules:
- `all`: every alarm is probed, the design rule. It must reproduce `design_003.json`.
- `wait`: no new probes until the last probed alarm's third probe is answered.
- `stop`: `wait`, plus no probes after a person's first confirmed alarm.

The first alarm is probed under every rule, so H1 and H2 do not change. Reported: probes per tracked month,
the share of alarms probed, confirmed false alarms (S), confirmed PPV, and the share of persons with a
confirmed alarm inside `[t0, t0 + 21)` (DR).

Expected:
- DR-1.5 at `phi_D` 0.7 drops under 3.0 probes per tracked month under `wait`.
- The cost is a lower in-window confirmed share. A pending pre-onset false alarm can block probes on the
  true alarm. Under `stop`, a confirmed pre-onset false alarm blocks them for good.

**(c) The PS-prop mechanism** (`phi_D` 0.7, A-fixed `k = 0.5`). DESIGN-003 section 3 item 4 offered a
reason, untested there: the re-baseline over `(c, c + 14]` sees only part of a ramped shift.

Two tests:
- **Dose-response.** Logged PS-prop L1 and L2 ratios to S by ramp tertile (7 to 11, 12 to 16, 17 to 21
  days).
- **Longer windows.** Re-baseline windows of 21 and 28 days. Window 14 must reproduce the design.

Also reported under each window: PS-sub's ratios, and DR+PS's logged 21-day sensitivity, which is the
hold's cost on true change.

Expected, if the reason is right:
- The ratio rises with ramp length.
- A 28-day window brings the 17-to-21 tertile toward PS-sub's ratios.
- DR+PS's L1 sensitivity falls as the window grows.

If the ratio does not rise with ramp length, the reason is wrong. That gets reported, not explained away.

## Results (DESIGN STAGE, synthetic; they inform his decisions and score nothing)

Provenance: code `decide_003.py` at commit `b070795` plus no later edit, output `decide_003.json` sha256
`ccb784b011d1faffbd11730823ed990d30f277a3c842ad7fbf83ec3d2506c7c7`. A second run reproduced it byte for byte
(`cmp`). The reproduction asserts passed: under the `all` rule the budget equals `design_003.json` for S, DR-1.0
and DR-1.5 at `phi_D` 0.7. With window 14, the PS-prop L1 ratio, the PS-sub L2 ratio and DR+PS's L1 logged
sensitivity equal the design run's. Intervals are 95% paired person-bootstrap intervals over the design run's
resample matrix, written "est [lo, hi]".

### (a) Evaluation N

The chance that an evaluation run lands on the side the prediction needs, with the design estimate taken as
true:

| item | design est (SE at 1000) | point, N 1000 / 2000 / 4000 | 95% interval, N 1000 / 2000 / 4000 |
|---|---|---|---|
| H1a, at most -0.15 | -0.236 (0.033) | 0.996 / 1.0 / 1.0 | 0.744 / 0.959 / 0.999 |
| H1b, at least 0.85 | 0.810 (0.050) | 0.213 / 0.130 / 0.055 | 0.003 / 0.001 / 0.0 |
| H1b proposed, at least 0.70 | same | 0.987 / 0.999 / 1.0 | 0.601 / 0.879 / 0.993 |
| H2a, at least 0.10 | 0.201 (0.024) | 1.0 at every N | 0.99 / 1.0 / 1.0 |
| H2b, at least 0.05 | -0.003 (0.033) | 0.054 / 0.012 / 0.001 | 0.0 at every N |
| H3, PS-sub L1/S under 1.5 | 1.421 (0.135) | 0.722 / 0.797 / 0.880 | 0.085 / 0.129 / 0.216 |
| H3, PS-use L1/S under 1.5 | 1.376 (0.128) | 0.834 / 0.915 / 0.974 | 0.161 / 0.279 / 0.493 |
| H3, L2 (both families) and L0 | see `decide_003.json` | 1.0 | at least 0.995 |
| H4, above 0 | 0.154 (0.028) | 1.0 | 1.0 |
| H5 M1, under 0.10 | 0.020 (0.017) | 1.0 | 0.998 / 1.0 / 1.0 |

The empirical check is consistent with the SE scaling: on seed 20261004, logged PS-sub L1/S is 1.656 [1.366,
2.023] at N 1000 and 1.629 [1.421, 1.864] at N 2000, an SE ratio of 1.459 against 1.414 expected. The design
seed gave 1.421: within sampling error (difference 0.235, combined SE about 0.21), but on the other side of 1.5.

What this means for the decisions:
- N does not rescue H3's L1 clause at 1.5. Even at 4000 persons the PS-sub interval clears 1.5 about a fifth of
  the time (PS-use about half), so the decision is about the rule or the window (part c), not about N.
- H1b at 0.85 and H2b are projected to miss at every N (interval-level probability at most 0.003).
- At N 2000, every other drafted or proposed item reaches an interval-level probability of about 0.88 or more.

### (b) Probe budget (spaced lag, 28 days, 4 probes)

Probes per tracked person-month, including the baseline block. The second figure is the share of DR persons
with a confirmed alarm inside `[t0, t0 + 21)`:

| `phi_D` (lag) | family | `all` | `wait` | `stop` |
|---|---|---|---|---|
| 0.3 (3) | DR-1.5 | 3.68; 0.386 | 3.68; 0.386 | 1.74; 0.326 |
| 0.7 (9) | S | 1.32 | 1.24 | 1.17 |
| 0.7 (9) | DR-1.0 | 2.39; 0.154 | 1.93; 0.134 | 1.52; 0.109 |
| 0.7 (9) | DR-1.5 | 3.24; 0.281 | 2.35; 0.252 | 1.61; 0.215 |
| 0.9 (29) | DR-1.0 | 2.25; 0.185 | 1.38; 0.089 | 1.28; 0.088 |
| 0.9 (29) | DR-1.5 | 2.93; 0.280 | 1.52; 0.165 | 1.38; 0.164 |

- At `phi_D` 0.3, `wait` equals `all` exactly. A wait of 3 x 3 + 1 = 10 days is shorter than the 14-day
  refractory, so `wait` never blocks an alarm there. That explanation is arithmetic, not a separate test.
- DR-1.5 under `all` also overruns 3.0 at `phi_D` 0.3, so the overrun is not specific to the default cell.
- `wait` brings DR-1.5 under 3.0 at `phi_D` 0.7 (2.35 [2.29, 2.39]) at about 0.03 of in-window confirmed share.
- At `phi_D` 0.9, consistent with the 88-day wait, `wait` roughly halves DR-1.0's in-window confirmed share and
  cuts DR-1.5's by about 40%; DR-1.0's confirmed PPV falls from 0.467 to 0.385.
- `wait` also lowers S's confirmed false alarms per tracked month: 0.061 to 0.052 at `phi_D` 0.7, and 0.100
  to 0.046 at 0.9.
- `stop` lowers the in-window confirmed share more than `wait` at `phi_D` 0.3 and 0.7.

Budget decision (DESIGN-003 section 4 item 5): no single rule is free; the bullets above give the costs.

### (c) The PS-prop mechanism

Logged persons' post-change alarm rate over S's, paired. N per ramp tertile: 187, 179 and 143 logged persons.

| window | rule | all | ramp 7-11 | ramp 12-16 | ramp 17-21 | PS-sub |
|---|---|---|---|---|---|---|
| 14 | L1 | 2.604 [2.217, 3.067] | 1.979 [1.509, 2.572] | 2.977 [2.201, 4.202] | 3.075 [2.332, 4.064] | 1.421 [1.175, 1.706] |
| 14 | L2 | 2.304 | 1.754 | 2.644 | 2.705 | 1.171 [1.034, 1.307] |
| 21 | L1 | 1.656 [1.360, 1.971] | 1.265 | 1.971 | 1.871 | 1.025 [0.831, 1.230] |
| 21 | L2 | 1.365 | 1.051 | 1.621 | 1.534 | 1.051 [0.929, 1.176] |
| 28 | L1 | 1.275 [1.044, 1.550] | 1.020 | 1.536 | 1.359 | 0.836 [0.658, 1.027] |
| 28 | L2 | 0.973 [0.797, 1.188] | 0.788 | 1.172 | 1.023 | 1.014 [0.904, 1.134] |

DR+PS, 21-day sensitivity among logged persons:

| window | L0 | L1 | L2 | oracle |
|---|---|---|---|---|
| 14 | 0.502 | 0.081 [0.059, 0.105] | 0.284 [0.246, 0.323] | 0.258 |
| 21 | 0.502 | 0.020 [0.010, 0.033] | 0.315 [0.275, 0.356] | 0.258 |
| 28 | 0.502 | 0.020 [0.010, 0.033] | 0.319 [0.279, 0.359] | 0.258 |

Against the expectations:
1. **The ratio rises with ramp length: partly.** The shortest tertile is lowest under every window and rule.
   The two longer tertiles are close at window 14, and the middle one is higher at 21 and 28, with wide,
   overlapping intervals. No tertile contrast was computed (the tertiles are disjoint persons). So the
   dose-response is supported only as "shortest ramps do least harm".
2. **A longer window brings PS-prop toward PS-sub: yes, in point estimate.** At 28 days, L2 reaches parity
   with S. The window also moves PS-sub's L1 ratio.
3. **L1 loses true change as the window grows: yes** (table above). That 21 and 28 days give the same figure
   fits detections that all fall on or before the change day, which no hold touches (the hold is `(c, c + W]`).
   That was not checked separately.
4. **Not expected:** L2's DR+PS sensitivity rises slightly with the window and sits above the oracle rule's,
   in point estimate only. No paired difference was computed. At window 14 the intervals overlap (0.284
   [0.246, 0.323] against 0.258 [0.221, 0.296]). A cause was not tested.

What this means for the H3 decision: the 14-day re-baseline window is inherited from the frozen code
(`drift_sim.py` `REBASELINE_WINDOW = 14`, rule (iv)). A 21-day window would put PS-sub's L1/S clearly under 1.5
on the design seed (1.025 [0.831, 1.230]). PS-use was not run under 21. It would also cut logged PS-prop's L2
excess over S from 1.30 to 0.37. The known price is L1's sensitivity to true change beginning near a logged
change. Not recomputed under a longer window: H4, PS-use's H3 ratios, and `policy_log`'s in-window mask, which
depends on the window. Changing the window is a spec 003 change, his to make, and would need the tuning and
the design run redone under it before any freeze.
