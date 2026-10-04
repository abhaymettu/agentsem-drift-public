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
