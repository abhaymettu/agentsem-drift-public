# sim/ATTRIBUTION-R4.md -- EXPLORATORY results, not frozen, synthetic only

Plan: `sim/ATTRIBUTION-PLAN-R4.md` r1, sha256 `ea64e1cf5a207ec9254e018a5bf8dbacc8be772180004648d82d5635d41a23e2`,
committed at `a9ab42d` before any evaluation panel was scored. Code: `sim/attribution_r4.py` at that commit
(`--check` passes). Raw output: `sim/attribution_r4.json`. A second run from the committed hash gave a
byte-identical JSON (`cmp`; sha256 `66d34cd498c98926bb9cbf8a3df87525ca3869ac27d28ebfd7acdf8ebed71445`).

Not part of `sim/PREREG.md`. No P1-P10 verdict, no paper v4 number and nothing in r1 to r3 or spec 003
changes. `drift_sim.py`, `attribution.py`, `attribution_r2.py` and `attribution_r3.py` are unchanged since
`9fea182`, `ccbcf51`, `21b28d5` and `ddf508e`. `drift_sim.py --check` passes except item (c), the
documented pre-freeze deviation 1.

Panels: r3's own and a fresh replication set, written *rep.* below. On r3's own panels, the asserts that
r3's post-change alarm counts, M2x3 shares and their differences reproduce exactly all passed. Each set
has 1000 simulated persons per family and cell, S and DR, constant help and frozen `h = 3.334`. The person
bootstrap uses 2000 draws, and brackets are 95 percent intervals. Rate-matched intervals are conditional
on `h*`, since the bisection is not bootstrapped.

The S rate counts every tracked day 28 to 134. On that window the frozen `bernoulli_mix` over default S
rate ratio is 0.179 [0.136, 0.225] (rep. 0.223), against r3's post-change 0.170.

## Predictions

| | prediction | r3's panels | holds | rep. | holds |
|---|---|---|---|---|---|
| A1 | frozen: S composite mean, default minus `bernoulli_mix`, at least 0.05 | 0.111 [0.107, 0.115] | yes | 0.107 | yes |
| A1 | matched: same difference within ±0.03 | -0.003 [-0.008, +0.002] | yes | -0.006 | yes |
| A1 | frozen: composite SD ratio, `bernoulli_mix` over default, below 1 | 0.870 [0.866, 0.875] | yes | 0.871 | yes |
| A2 | share of the log S-rate gap closed by the matched baseline at least 0.5 (point; both intervals span 0.5) | 0.518 [0.440, 0.598] | yes | 0.550 [0.467, 0.645] | yes |
| A3 | rate-matched DR sensitivity ratio, `bernoulli_mix` over default, matched, between 0.5 and 1.0 | 0.963 [0.828, 1.113] | yes | 0.862 [0.742, 0.981] | yes |
| A4 | `bernoulli_mix`, rate-matched DR sensitivity, `share_rule` over matched, at least 1.0 | 0.846 [0.721, 0.986] | no | 0.949 [0.808, 1.106] | no |
| B1 | default S, frozen: share of the alarm-day `pi'` gap left after recentring at least 0.5 (direction only) | 0.743 [0.272, 1.243] | yes | 0.669 [0.158, 1.276] | yes |
| B2 | default S, matched: alarm-day `pi'` gap interval below 0 (construction check) | -0.068 [-0.097, -0.039] | yes | -0.020 [-0.054, +0.012] | no |
| C1 | DR `bernoulli_mix`: margin difference has the share difference's sign (read only if the margin interval excludes 0) | margin +0.184 [+0.077, +0.288], share +0.091 | yes | +0.286 [+0.174, +0.403], share +0.055 | yes |
| C1 | S `pi_rises_with_D`: same | margin -0.158 [-0.242, -0.074], share -0.054 | yes | -0.100 [-0.186, -0.012], share -0.013 | yes |
| C1 | DR `pi_rises_with_D`: same | margin +0.004 [-0.043, +0.054], share +0.024 [+0.001, +0.049] | unresolved | +0.008 [-0.045, +0.059], share +0.006 [-0.018, +0.030] | unresolved |
| (report only) | S `bernoulli_mix` | margin +0.186 [-0.039, +0.392], share +0.021 | | -0.177 [-0.406, +0.038], share -0.075 | |

## What the numbers say

### M-A: why `bernoulli_mix` alarms less at the frozen `h`

1. **About half of r3's lower alarm rate is the baseline mismatch going away.**
   - Under default Beta mixing, A-fixed standardizes the filtered indicators 4 and 5 against a baseline fit
     on unfiltered text. The S composite mean is +0.141 as run and +0.028 with a matched baseline (rep. the
     same), an offset of 0.114 against the plan's hand figure of about 0.12. Under `bernoulli_mix` the two
     series coincide and there is no offset.
   - Of A2's closure, the level offset accounts for 0.29 (rep. 0.34) and the scale inflation for the other
     0.23 (rep. 0.21).
   - Under the matched baseline, `bernoulli_mix`'s composite SD is 0.925 of default's, and its lag-1
     autocorrelation is 0.128 against 0.188 (rep. 0.137, 0.198). What drives the remaining half was not
     tested.
2. **At a matched false-flag rate, all-or-nothing days cost little detection.**
   - DR's rate-matched 21-day sensitivity under `bernoulli_mix` is 0.86 [0.74, 1.00] of default's with the
     frozen baseline (rep. 0.78). For the matched baseline, see A3.
   - Against 0.26 at the frozen `h`, most of r3's gap is the operating point, which `h` sets, not lost
     power. Tuning `h` under the mixing regime (17.3 proposal 3, first option) recovers it in this oracle
     form.
3. **The oracle minimum-human-text rule.** A4 came in below 1 on both sets, so the plan's pre-stated
   reading applies:
   - `h*` rises from 1.69 to 4.03 (rep. 1.78 to 4.04).
   - Indicator 5's baseline rests on 0 to 3 usable days for 55 percent of persons (2.4 percent with 0,
     8.8 with 1, 19.3 with 2, 24.5 with 3). Those persons give 63 percent of S alarms (rep. 64).
   - The composite's SD on S is 3.97, against 0.52 without the rule.
   - So A4 is read as the cost of a small baseline for this oracle rule, not as evidence about dropping
     agent-day noise.

   Not predicted:
   - Under `pi_rises_with_D` the same rule raises rate-matched DR sensitivity from 0.150 to 0.186 (rep.
     0.139 to 0.165; no paired interval was planned). The rule drops indicators 4 and 5 on high-share
     days, which in that cell are high-`D` days on which filtered indicator 5 moves toward the agent mean
     (not tested).
   - In the default cell the rule leaves rate-matched sensitivity about where it was: 0.163 against
     0.162 (rep. 0.155 against 0.159).

### M-B: the human-text false-alarm route

4. B1 holds on both sets. The point estimates point toward the human-weight channel (`1 - pi'`) that the
   plan predicted, rather than the lower agent mean r3 guessed at; the intervals do not separate the
   channels.
   - B2 holds on r3's panels. On the replication the frozen gap is -0.054 and the matched gap -0.020, so
     whether the mismatch amplifies the route is not settled by two panel sets.
   - Under `bernoulli_mix` (no prediction; 73 and 90 S alarms) the gap is -0.148 (rep. -0.234), and
     recentring leaves -0.073 (rep. -0.186).

### M-C: r3's sign question under `pi_rises_with_D`

5. **The DR `pi_rises_with_D` row is unresolved.**
   - Over confirmable DR alarms, the mean true `D` on answered probe days falls by 0.047 [0.002, 0.092]
     against default. The mean true `D` on the answered baseline probes falls by 0.051 [0.032, 0.072]. So
     the margin that M2x3 thresholds barely moves, and its interval cannot exclude shifts of about 0.05.
   - The confirmable share moves by +0.004.
   - r3's level metric and the margin-based share are on different scales. On the margin scale the
     point estimate is near 0 on both sets, and the share difference is +0.024 on r3's panels and +0.006
     on the replication.
6. **The other two C1 rows agree in sign with the margin on both sets (table).**
   - In both DR rows the baseline term falls: -0.10 and -0.05 (rep. -0.15, -0.04). Under the mixing cells,
     DR alarms come more from persons whose baseline probe days had lower `D`. Why is not tested.

## For the next study's spec, and for him (INFERENCE, not run)

- **The frozen implementation standardizes against a different mixture than it scores** (plan (a)). It is
  an implementation property of A-fixed that PREREG's wording does not settle.
  - Every A-fixed composite quantity carries it: the frozen run, paper v4, r1 to r3, the (ii) ablation,
    and the generated help in the targeted cells.
  - The frozen `h` was tuned with it, so the frozen false-flag rate is on target.
  - On these panels, default's rate-matched DR sensitivity is 0.181 as run and 0.162 with a matched
    baseline (rep. 0.175, 0.159). No interval was planned for this comparison, and these are not the
    PREREG seeds. It is not an estimate for the frozen run or paper v4 (plan (f)).
  - Whether the frozen run gets a matched-baseline sensitivity rerun, and how the next paper version
    discloses this, is his call.
  - Any new study should fit the baseline on the series it scores. Spec 003's generator and scorer,
    `sim/study003.py`, do not exist yet.
- **Calibrate in units the regime does not change.** The composite is not re-standardized, so `k` and `h`
  mean different things whenever the indicators' scale or offset shifts with the authorship regime.
  - Tuning `h` under the estimated regime works in oracle form (point 2).
  - A rule that drops agent-heavy days needs a baseline rule to go with it (point 3), such as a minimum
    day count or a pooled baseline.

## Review trail

| step | reviewer | outcome |
|---|---|---|
| plan + script | Opus methods review | REVISE, 5 blocking, all applied before hashing; 10 non-blocking applied |
| plan + script | ponytail | 7 cuts, all applied |
| write-up | Opus accuracy review | REVISE, 10 blocking (two copied numbers, a lint statement, six readings past the plan, a missing report-only row), all applied; 9 non-blocking applied |
| write-up | ponytail | 12 cuts, all applied |

`scripts/claims_lint.sh` passes on this file. On the hashed plan it flags one word in the revision log, the
term used there for the baseline-day counts. It is not clinical, and it is left unchanged so the plan keeps
its hash.
