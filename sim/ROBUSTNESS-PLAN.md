# sim/ROBUSTNESS-PLAN.md -- EXPLORATORY, not frozen

This plan answers referee round-1 item 14 / round-2 N5 (`~/lanes/bridge-jobs/agentsem-overnight-20260927/paper-referee-review.md`):
separate the paper's structural findings (results that follow qualitatively from the generator's
structure) from the magnitudes, which are set by invented parameter values. It defines a one-at-a-time
grid around the frozen default and a success rule for "holds across the grid."

**This grid is EXPLORATORY. It is not part of `sim/PREREG.md` and does not change any P1-P10 verdict.**
Every output the `robust` subcommand writes (`sim/robustness.json`, `sim/ROBUSTNESS.md`) repeats that
label. Nothing here touches `sim/PREREG.md`, `sim/results.json`, `sim/metrics.json` or `specs/`.

## (a) The one-at-a-time grid

Each cell changes exactly one parameter from the frozen default (`sim/PREREG.md` section 3/4); every
other parameter stays at its frozen value. `N = 1000` persons per cell, family S (plus DR and CS where
a check needs them), matching the frozen design's own person count.

| dimension | values (default marked) | generator support |
|---|---|---|
| `lam` range (per-person, per-indicator loading) | `[0.10, 0.25]`, `[0.25, 0.50]` (default), `[0.50, 0.80]` | `generate_panel(..., lam_range=...)` -- already a parameter |
| `phi_D` (AR(1) persistence of the latent state) | 0.3, 0.7 (default), 0.9 | `generate_panel(..., phi_D=...)` -- new keyword, default `PHI_D` |
| `psi` (help's effect size on indicators 2, 3) | 0.25, 0.5 (default), 1.0 | `generate_panel(..., psi=...)` -- new keyword, default `PSI` |
| indicator-4 contamination | entry-level pilot (default: `pi_bar=0.845`, `kappa_a4=0.547`, `mu_m4=0.274`), day-level pilot (`pi_bar=0.8229027541216615`, `kappa_a4=0.09840995564479449`, `mu_m4=0.19624929309002312`, from `pilot/indicator4_params.json`'s `day_level_main_thread`) | `generate_panel(..., pi_bar=, kappa_a4=, mu_m4=)` -- already parameters |
| rising-share logit slope (the `pi_rises_with_D` cell's coupling strength) | 0.25, 0.5 (default), 1.0 | `generate_panel(..., rising_slope=...)` -- new keyword, default `0.5` |
| `m1` (response-MNAR strength) | 0 (default), 1.5 | `cell_params("m1_15")` -- already the frozen `m1_15` cell |

One-at-a-time against a single shared default collapses to **11 distinct cells** (the "all defaults"
cell is shared across dimensions, not repeated per dimension):

`default`, `lam_low` (`[0.10,0.25]`), `lam_high` (`[0.50,0.80]`), `phi_D_low` (0.3), `phi_D_high` (0.9),
`psi_low` (0.25), `psi_high` (1.0), `ind4_daylevel` (day-level pilot), `rising_slope_025` (0.25),
`rising_slope_10` (1.0), `m1_15` (1.5). **All 11 are runnable.**

**Three of these six dimensions had no generator parameter at all** -- `phi_D`, `psi` and the
rising-share logit slope were module-level constants (`PHI_D`, `PSI`, and the literal `0.5` inside the
`cell["pi_rises"]` branch) referenced directly inside `generate_panel`'s body. Rather than hack around
that, `generate_panel` gained three new keyword arguments -- `phi_D=PHI_D`, `psi=PSI`,
`rising_slope=0.5` -- each defaulting to exactly the constant it replaces, threaded to the same three
call sites (`D = ar1_panel(rng, n, T, phi_D)`; `build_H_X`'s `psi[None, None, :]` term, both the
vectorized and the single-day targeted-help-loop copies; `pi_t = expit(logit(pi_bar) + rising_slope *
D)`). `psi` is passed as the full 6-length array (`PSI`'s shape), with `_psi_scaled(val)` building the
grid's scalar-valued cells by setting indicators 2 and 3 (`IDX_FRAG`, `IDX_DEFER` -- PSI's only nonzero
slots in the frozen spec) to `val` and leaving the rest at 0, matching the frozen array's shape exactly.
(`cell_params`'s existing `theta1` remains a different tunable -- it scales PSI's *interaction* with
`D`, not its base magnitude.)

**Proof this changes no frozen output:** every existing call site (`--check`, `tune`, `score`, `metrics`,
and every call inside `generate_panel` itself for cells that don't pass these new kwargs) omits them and
gets the exact default value, so it is bit-identical to before. Proved directly, in a scratch copy (not
this repo -- `sim/results.json`/`sim/metrics.json` here were never touched):
- `python3 sim/drift_sim.py --check` -> 8 of 9 (same `(c)` deviation as before, unchanged).
- `score --prereg-sha 60db6dd1...8f17` and `metrics --prereg-sha 60db6dd1...8f17`, then `cmp` against
  the committed `sim/results.json`/`sim/metrics.json`: `metrics.json` is byte-identical. `results.json`
  differs from the committed file at a handful of `se`/`lo`/`hi` fields in P6, in the last one or two
  significant digits (e.g. `0.011275979460566962` vs `...963`) -- but an unmodified copy of this
  repo's own `HEAD` code, run the same way in the same environment, reproduces that *exact same*
  discrepancy at the *exact same* fields, and the modified code's `results.json` is byte-for-byte
  identical to the unmodified control's `results.json`. That isolates the discrepancy to pre-existing,
  environment-level floating-point noise (almost certainly a numpy/BLAS version difference between this
  machine and whatever produced the committed file) that predates and is unrelated to this change; the
  generator edit itself contributes zero additional difference.

## (b) Structural outcomes and their expectations

Each S-item is a direction/sign claim tied to the generator's structure (AR(1) persistence,
history-dependent selection, the algebraic sign of `X = H + pi(M - H)`, MNAR response), not a magnitude
threshold. Every expectation below is stated before any cell is run.

- **S1 -- selection attenuation (referee item 14, mechanism 1; N1).** *Expectation:* on family S,
  A-fixed, the `triggered` and `current` schedules probe preferentially on days the composite is
  already elevated, so the person-centred slope of `Y` on `C` restricted to those probed days is
  attenuated toward zero relative to the all-days slope, in every cell, regardless of `lam` range,
  `phi_D`, `psi`, indicator-4 contamination or the rising-share slope. **Tested as the ratio of the
  probed-day slope to the all-days slope being < 1**, not a signed difference: a signed difference's
  sign depends on the (arbitrary) sign of the all-days slope itself, so it is not a reliable attenuation
  test if a cell ever pushed that slope negative, while the ratio test is attenuation-direction-invariant
  (`b_obs / b_all < 1` means `b_obs` sits closer to zero than `b_all`, with the same relative
  orientation, whichever sign `b_all` happens to have). This is the qualitative claim behind P4 and N1's
  `current`-vs-`triggered` comparison; the grid does not resolve N1's separate estimator-vs-history
  question, only whether the direction of the attenuation itself is robust.
- **S2 -- sign of state-coupled contamination (referee item 14, mechanism 3).** *Expectation:* in the
  `pi_rises_with_D` mixing cell, `X_jt = (1-pi_t) H_jt + pi_t M_jt` with `pi_t` rising in `D` means the
  indicator whose agent-text mean `mu_M` sits *above* the human mean (indicator 4, `mu_M4 > mean(H4)`)
  gets a positive spurious coupling with `D` on top of its attenuation -- its simulated attenuation
  ratio exceeds the independent-`pi` closed form. Indicator 5's `mu_M5 = -1.0` sits *below* its own
  mean, so the same mechanism pushes the other way: its ratio falls short of the formula. This sign
  pattern is algebraic (it follows from the mixing identity and the sign of `mu_M - mean(H)`, not from
  any specific `lam`/contamination/rising-slope magnitude), so it is expected in every cell tested,
  including now the `rising_slope_025`/`rising_slope_10` cells themselves (crossing the
  `pi_rises_with_D` mix mode with each runnable cell's own `lam`/contamination/`rising_slope` value; it
  does not depend on `m1`, so its panel always uses `m1 = 0`).
- **S3 -- passive rules beat their own chance baseline (metrics.json item (h)).** *Expectation:* every
  passive (non-probe) architecture -- `pop`, `A-naive`, `A-fixed`, and the five `A-fixed-minus-*`
  ablations -- accumulates real CUSUM evidence from indicators that carry a genuine, if attenuated,
  `lam`-scaled signal, so each one's DR sensitivity within 21 days exceeds an independent random-flagging
  rule run at that architecture's own realized false-flag rate. This should survive weaker signal
  (`lam_low`) as long as `lam > 0`.
- **S4 -- probe-only is indistinguishable from chance (referee round 2, N3).** *Expectation:* probe-only
  has no passive signal at all -- it is a CUSUM on sparse, matched-budget probe answers alone -- so its
  observed DR sensitivity is not detectably different from its own chance baseline; this is the reverse
  of S3's claim and is expected to survive because it follows from probe-only's construction (no
  indicator data enters it), not from any parameter value.
- **S5 -- response-MNAR increases the absolute relative slope bias, and observable-IPW does not fully
  remove it (referee item 14, mechanism 2).** *Expectation:* raising `m1` from 0 to 1.5 makes response
  depend on `D_t` directly; a response-propensity model fit only on observables available to the layer
  (`C_t`, one lag, day of week) cannot recover the part of that dependence that runs through `D_t` net of
  `C_t`. Concretely: (i) `m1 = 1.5` **increases the absolute value of the relative slope bias**
  (`|(b_obs - b_all) / b_all|`, random schedule) over its value at `m1 = 0` -- the frozen `sim/
  results.json` (`P5.rel_bias_by_m1_and_schedule`) shows the *signed* relative bias at `m1 = 1.5` is
  itself **negative** (roughly -20 to -48 percent across schedules), so the claim is that `|bias|` grows,
  never that the bias is positive; and (ii) the IPW-corrected bias does not fall to zero -- the 95%
  interval on the fraction of bias removed does not reach 1.0 (full removal). This is inherently a
  statement about the `m1` axis, so it is only a non-degenerate test in the `m1_15` cell (see (c)); the
  other ten runnable cells have `m1 = 0` by construction and would compare `m1=0` against itself.
- **S6 -- A-fixed's false flags on CS exceed S (frozen P10's direction).** *Expectation:* context is
  untreated as nuisance in A-fixed, so a context-mix change with no state change (family CS) is a
  false-flag source: the pooled false-flag ratio (CS over S) exceeds 1 in every cell, independent of
  `lam`, indicator-4 contamination, or `m1`.

## (c) Success rule

A structural finding **"holds across the grid"** only if its 95% Monte Carlo interval (2000-draw person
bootstrap, `mc_stat`, exactly as `score()`/`metrics()` use) **excludes the null in every one of the 11
cells**:

- S1: interval of the **ratio** (probed-day slope / all-days slope) entirely `<= 1`, for both `triggered`
  and `current`, in every cell. (Not a signed difference -- see (b)'s S1 note on why a ratio test is the
  direction-invariant one.)
- S2: interval of (simulated attenuation minus closed-form attenuation) entirely `>= 0` for indicator 4
  and entirely `<= 0` for indicator 5, in every cell.
- S3: interval of (observed minus chance sensitivity) entirely `>= 0`, for every one of the 8 passive
  architectures, in every cell.
- S6: interval of the CS-over-S false-flag ratio entirely `>= 1`, in every cell.
- S5: **only evaluated in the cell where `m1 != 0`** (`m1_15`); interval of the added `|relative bias|`
  (`m1=1.5` minus `m1=0`, both `|(b_obs-b_all)/b_all|`) entirely `>= 0`, **and** the IPW fraction-removed
  interval's upper bound `< 1.0`, must both hold. The other 10 cells (`m1 = 0`) are reported as
  `"not_applicable"`, not as a pass or a fail.
- **S4 is a "within" claim, not a "beyond" claim, and its null is reversed from S1/S2/S3/S5/S6**: it
  holds in a cell if the 95% interval of (observed minus chance sensitivity) for probe-only **contains
  zero** -- i.e. it fails to exclude the null of "no difference from chance." This is the one item where
  "holds" means the null survives, matching the referee's own "indistinguishable from chance" language
  (round 2, N3); the direction is stated explicitly here so it is not read as a copy-paste of the other
  five items' rule.

Where a finding fails in one or more cells, those cells are listed by name (`sim/ROBUSTNESS.md`'s
per-finding summary), exactly as `sim/PREREG.md` section 6 already requires for "holds across the grid."

**Schedule-tuning scope note:** only `h` is re-tuned per cell (see (e)). The probe-schedule tuning
parameters (`p_trig`, `p_trig2`, `c_star`) are reused from the frozen `sim/tuning.json` unchanged in
every cell. This is a scope limitation, stated here rather than hidden: a cell whose composite
distribution shifts enough to change the operating point of the `triggered`/`mixed`/`current` schedules
is not perfectly re-calibrated to the same realized budget. S1's `triggered`/`current` checks are read
with that caveat.

## (d) Seeds

Seeds are derived from `sha256(sim/ROBUSTNESS-PLAN.md)` (this file, hashed exactly as `eval_seed()`
hashes `sim/PREREG.md`), with the literal tag `"robust"` folded into every hash input:
`sha256("robust:" + plan_sha256 + ":" + ":".join(str(p) for p in parts))`, truncated to 64 bits exactly
like `eval_seed`. This is disjoint from the evaluation seeds (`eval_seed()`'s tag is
`f"{prereg_sha}:{family}:{cell}"`, hashed from a different file's sha256 with no `"robust"` literal) and
from the fixed tuning seed `20260927` (a bare integer constant, not derived from any file hash). The
`robust` subcommand's `robust_seed(plan_sha, *parts)` **refuses to run** (raises before generating
anything) unless `sha256(sim/ROBUSTNESS-PLAN.md) == --plan-sha`, exactly mirroring `eval_seed()`'s refusal
when `--prereg-sha` does not match `sim/PREREG.md`.

## (e) The `h` tuning policy

`h` is re-tuned per cell, per architecture (all 9 of `ARCHS_FOR_H`, including `probe-only`), on a
`robust_seed`-derived tuning draw, to the same false-flag target used everywhere else in this repo (1
false alarm per 6 tracked person-months). **Why:** S3 and S4 compare each architecture's *observed*
sensitivity against its *own* chance baseline computed at its *own* realized false-flag rate on S --
that comparison is only informative if every architecture is actually operating at (approximately) the
matched false-flag rate in that cell. A cell that changes `lam` range, `phi_D`, `psi` or indicator-4
contamination shifts the composite's distribution, so the frozen default's `h` values would not hold
every architecture to the same false-flag rate in a different cell; re-tuning `h` per cell keeps the
false-flag rate the constant across cells that S3/S4's chance-baseline comparison needs. (`m1` and the
rising-share slope do not move the composite at all -- `m1` only touches `Y`/response, and
`rising_slope` only applies inside the `pi_rises_with_D` mix mode that S1/S3/S4/S5/S6's own panels never
use -- so re-tuning under the `m1_15`/`rising_slope_*` cells reproduces the default's `h` up to
independent tuning-seed noise, by construction, not because it was skipped.) `p_trig`, `p_trig2` and
`c_star` are not re-tuned (see (c)'s schedule-tuning scope note) -- only `h`, per this brief's explicit
instruction.
