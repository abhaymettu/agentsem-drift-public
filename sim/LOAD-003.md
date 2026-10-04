# L1_did when D moves mapped and unmapped indicators unequally

**Status: DESIGN STAGE, EXPLORATORY. Every number is synthetic. No prediction is scored.** This informs whether
PREREG-003 and the paper can specify L1_did (OBS-003) and which assumption it must state. It decides nothing and
changes no spec.

Code: `sim/load_003.py` -> `sim/load_003.json`. Design seed 20261003, `phi_D` 0.7, 28-day baseline, W 14, the
design run's resample matrix, NET-003's paired arms (DR+PS, and the same persons with `delta_D = 0`).
`obs_003.py` and everything it imports are unchanged.

## Why

OBS-003: L1_did (keep the baseline mean and SD; after the hold subtract from mapped indicators 1, 2, 6 their
hold-mean z minus the unmapped indicators' mean hold z) lifts L1's 63-day in-window D-dependent sensitivity
0.190 -> 0.385 (k 0.5, W 14). Its DiD reference works only if D moves the unmapped indicators about as much, in
baseline z, as the mapped ones. In the generator it does on average (loadings U[0.25, 0.5] on every indicator).
Real indicators need not: D could show more in timing (mapped) than in message content (unmapped), or the
reverse. A reviewer will ask what the rule costs when that assumption fails. OBS-003 also cut three interval
contrasts before its run (oracle - L1_did, L1_did - L2, L1_did - L1_bothCF); this plan states them before the run.

## Plan (committed before the run)

Effect ratio rho: in the DR+PS arm, D's realized effect on the unmapped indicators 3, 4, 5 is scaled by rho, as
`c + rho * (f - c)` on each series the detector reads (X, X_filtered, and the oracle's unshifted X0, Xf0), where f
is DR+PS and c the same persons without the D change. f and c share every draw but the D step, so `f - c` is
D's whole effect on that indicator: its loading, and on indicators 4 and 5 also its context channel through the
authorship mix. rho scales that realized effect, not the loading itself. Mapped indicators keep f. rho in {0, 0.5, 1, 2}; rho = 1 is f itself.
rho = 0: D does not show on the unmapped indicators, so the reference reads only noise and L1_did should behave as
L1_step. rho = 2: the reference over-reads D and L1_did subtracts part of the person's change from the mapped
indicators. The no-D-change arm does not depend on rho, so every rule's no-change rate is the same at every rho.
rho also changes the total D signal, so rules are compared within a rho, not across.

Rules (OBS-003's): L1, L1_step, L1_did, L2, the oracle rule, L1_bothCF (ramp-free L1, oracle information).
Detectors A-fixed `k = 0.5` (primary) and `k*`; horizons 21, 42, 63 days; in-window persons (n = 247).
1. Each rule's raw sensitivity, no-change rate and D-dependent sensitivity.
2. Paired D-dependent differences with intervals: L1_did - L1, L1_did - L1_step (what the DiD reference adds),
   oracle - L1_did, L1_did - L2, L1_did - L1_bothCF.
3. Step-estimate error on the mapped indicators (estimate minus the true step 0.5 / baseline SD), raw and DiD.

Asserts: at rho = 1 every rule's measures, L1_did - L1 and the DiD step error reproduce `obs_003.json` (W 14).

Expected (k 0.5, in-window, 63 days unless stated):
1. The asserts pass.
2. The raw step error is the same at every rho (asserted at rho = 1 against `obs_003.json`); the DiD step error's mean falls linearly in rho, to within 0.005
   of `raw - rho * (raw - DiD at rho 1)`.
3. L1_did - L1_step falls as rho rises (points), its interval covers 0 at rho = 0, it is positive at rho = 0.5
   (point) and negative at rho = 2 (point).
4. L1_did - L1 is positive and its interval excludes 0 at every rho.
5. At rho = 1, the intervals of oracle - L1_did, L1_did - L2 and L1_did - L1_bothCF all cover 0.

## Results

(after the run)
