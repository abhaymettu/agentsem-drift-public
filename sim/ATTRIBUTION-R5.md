# sim/ATTRIBUTION-R5.md: EXPLORATORY r5 results, not frozen, synthetic only

**Provenance.**
- Plan: `sim/ATTRIBUTION-PLAN-R5.md`, sha256 `6bcc7bbf45f7c06f34f1a0463169b9456ea778d29b4fbd7649ceead7d245f27a`. It was
  committed at `5f1da38`, together with `sim/attribution_r5.py` (sha256 `c1067c9d...`), before any panel on
  this round's seeds was scored.
- Raw output: `sim/attribution_r5.json`, sha256 `5a6ffaf5375f11068a6e81847f19f101ee0c48c61a660216762ba5e67ac01004`.
  A rerun produced output identical to the byte (`cmp`).

**Status.** This round was not in any earlier plan or preregistration. It is not a PREREG-003 amendment and not part of
`sim/PREREG.md`. No H1-H5 or P1-P10 verdict changes, and no number in paper v4 or `results_003.json`
changes. Nothing here may be folded into a confirmatory claim.

**Design.** Each cell has N 4000 persons, with S and DR-1.0 paired within a cell. The detector is spec 003's
A-fixed (k = 0.5, `h = 1.898499`, phi 0.7, 28-day baseline). Uncertainty comes from a person bootstrap of
2000 draws; `±` is the bootstrap SE, and brackets are 95% intervals. Runtime is 72 s (numpy 2.5.3,
Python 3.14.7).

`q* = 3.835`, from 253 DR-1.0 alarms in `[t0, t0 + 21)` on the reference-cell tuning panel. `tuning_003.json`'s
first-detection `q*` is 3.921; it is not used here.

## Shares by cell

Columns:
- S share: person-attributed over scored S alarms on days [41, 210). This is the primary window (D6).
- DR w21: DR-1.0 alarms in `[t0, t0 + 21)`.
- Separation: DR `[t0, 210)` share minus S share, paired.

| cell | S M1 | S M2 | S M2x3 | DR w21 M1 | DR w21 M2 | DR w21 M2x3 | separation M1 | separation M2 | separation M2x3 |
|---|---|---|---|---|---|---|---|---|---|
| reference | 0.866 ± 0.008 | 0.548 ± 0.010 | 0.613 ± 0.011 | 0.914 ± 0.008 | 0.654 ± 0.014 | 0.795 ± 0.012 | 0.013 ± 0.007 | 0.112 ± 0.010 | 0.189 ± 0.010 |
| kappa-0.3 | 0.855 ± 0.007 | 0.554 ± 0.009 | 0.593 ± 0.010 | 0.874 ± 0.010 | 0.679 ± 0.014 | 0.798 ± 0.012 | 0.005 ± 0.006 | 0.101 ± 0.009 | 0.204 ± 0.010 |
| kappa+0.3 | 0.880 ± 0.007 | 0.550 ± 0.011 | 0.601 ± 0.011 | 0.886 ± 0.010 | 0.669 ± 0.015 | 0.813 ± 0.013 | 0.006 ± 0.006 | 0.098 ± 0.011 | 0.199 ± 0.011 |
| change_dep_0.3 | 0.878 ± 0.007 | 0.560 ± 0.010 | 0.603 ± 0.011 | 0.875 ± 0.010 | 0.638 ± 0.015 | 0.788 ± 0.013 | -0.004 ± 0.007 | 0.085 ± 0.010 | 0.194 ± 0.010 |
| m1_0.5 | 0.875 ± 0.007 | 0.506 ± 0.010 | 0.598 ± 0.010 | 0.890 ± 0.010 | 0.521 ± 0.015 | 0.767 ± 0.013 | -0.000 ± 0.007 | 0.020 ± 0.010 | 0.162 ± 0.010 |
| m1_1.5 | 0.862 ± 0.007 | 0.317 ± 0.009 | 0.508 ± 0.010 | 0.904 ± 0.009 | 0.246 ± 0.013 | 0.526 ± 0.015 | 0.011 ± 0.006 | -0.071 ± 0.010 | 0.007 ± 0.011 |

Window sizes:
- Scored S alarms on [41, 210) per cell: 2932 to 3352.
- DR alarms in `[t0, t0 + 21)`: 982 to 1144.
- DR alarms in `[t0, 210)`: 8417 to 9586.

The secondary S window [28, 210) moves no S share or separation by more than 0.007
(`S_share_from28_*`, `separation_from28_*` in the JSON). M3 (M1 and M2x3) and DR's `[t0, 210)` shares are in
the JSON.

**DR-1.0 21-day sensitivity, ratio to M0.** A pre-onset person-attributed alarm makes the person undetected,
as in r1.

| cell | M0 sens21 | M1 | M2 | M2x3 |
|---|---|---|---|---|
| reference | 0.154 ± 0.006 | 0.976 ± 0.014 | 0.815 ± 0.025 | 0.937 ± 0.022 |
| kappa-0.3 | 0.157 ± 0.006 | 0.954 ± 0.016 | 0.848 ± 0.026 | 0.967 ± 0.025 |
| kappa+0.3 | 0.146 ± 0.006 | 0.926 ± 0.013 | 0.807 ± 0.025 | 0.945 ± 0.023 |
| change_dep_0.3 | 0.151 ± 0.006 | 0.927 ± 0.014 | 0.793 ± 0.027 | 0.917 ± 0.023 |
| m1_0.5 | 0.158 ± 0.006 | 0.933 ± 0.014 | 0.667 ± 0.025 | 0.887 ± 0.023 |
| m1_1.5 | 0.163 ± 0.006 | 0.963 ± 0.013 | 0.333 ± 0.021 | 0.623 ± 0.025 |

**Diagnostics.**
- **Q not assessable.** The share of scored alarms where `Q` could not be assessed was 0 in every cell and
  family.
- **Probe answered on `t + 1`.** By cell:

  | | reference | kappa-0.3 | kappa+0.3 | change_dep_0.3 | m1_0.5 | m1_1.5 |
  |---|---|---|---|---|---|---|
  | S | 0.785 | 0.804 | 0.799 | 0.811 | 0.716 | 0.487 |
  | DR w21 | 0.803 | 0.803 | 0.813 | 0.804 | 0.644 | 0.329 |

- **Momentary-state selection.** On scored S alarms, `D` is 1.23 to 1.33 on the alarm day, 0.87 to 0.95 on
  `t + 1`, and 0.50 to 0.55 over the probe days. Mean `D` on tracked days is -0.06 to 0.06.

  On DR `[t0, 210)` alarms, the same three readings are 1.79 to 1.85, 1.55 to 1.60, and 1.31 to 1.34. Mean
  `D` on tracked days is 0.86 to 0.99.

  r1's S value of `D_{t+1}` was 0.98, from a different detector. The bases of E3 and E4 carry over.

**Sanity reading against `results_003.json`.** These are the same definitions on different seeds, so the
check is |z| below about 3. Across the 12 comparisons (S M0 rate and DR M0 sens21, six cells), |z| is at
most 1.11.

## Expectations (plan section f, scored on point estimates)

| | expectation | estimate | holds |
|---|---|---|---|
| K | (calibration) reference DR w21 M1 share within 0.05 of 0.9 | 0.914 | yes |
| E1 | \|cell - reference\| < 0.05, M1 S and DR w21 shares, five cells | largest \|d\| 0.041 (kappa-0.3, DR w21) | yes |
| E2 | DR w21 shares fall with `m1`: reference > m1_0.5 > m1_1.5 under both M2 and M2x3; m1_1.5 over reference is at most 0.5 for M2 and at most 0.8 for M2x3 | M2 0.654 > 0.521 > 0.246, ratio 0.375; M2x3 0.795 > 0.767 > 0.526, ratio 0.661 | yes |
| E3 | S M2 share at m1_1.5 at least 0.10 below reference | -0.231 [-0.256, -0.206] | yes |
| E4 | the M2x3 separation (DR minus S) is smaller at m1_1.5 than at reference | 0.007 against 0.189; difference -0.182 [-0.210, -0.154] | yes |
| E5 | \|cell - reference\| < 0.05, M2 and M2x3 DR w21 shares, three usage cells | largest \|d\| 0.025 (kappa-0.3, M2) | yes |

E1 holds, but the five DR w21 M1 differences are all negative (-0.011 to -0.041). Three of their intervals
exclude 0:
- kappa-0.3: [-0.066, -0.016];
- kappa+0.3: [-0.055, -0.002];
- change_dep_0.3: [-0.068, -0.013].

The DR `[t0, 210)` M1 shares show no such pattern (0.860 to 0.886 against the reference's 0.879).

Two explanations remain, and this round cannot tell them apart:
- **A high reference.** All five differences share the reference panel, and its w21 share of 0.914 sits
  above the nominal 0.90, so a high reference would push all five the same way.
- **A small usage effect.** The two m1 cells, where the generator changes only probe response (which M1
  never reads), give -0.025 and -0.011, with intervals covering 0. The three intervals that exclude 0 are
  the usage cells, where `used` depends on `D` and so can change which days enter `Q`'s window.

## Reading (exploratory)

1. **M1 does not separate person change from no change, in any cell.** The M1 separation is -0.004 to 0.013.
   M1 reads 0.855 to 0.880 of S alarms and 0.860 to 0.886 of DR `[t0, 210)` alarms as person change. This
   matches r1, where M1's share was flat across families (0.87 to 0.93).
   - M1 never reads probe response, so the m1 cells cannot move it except by chance.
   - Usage changes move its DR w21 share by up to -0.041, inside E1's 0.05 (see the E1 note). Its
     separation stays at -0.004 to 0.006 in the usage cells.
2. **The usage cells leave the probe rules where the reference is.** Under kappa -0.3, kappa +0.3 and
   change-dependent 0.3, every M2 and M2x3 share differs from the reference by at most 0.025, and the M2x3
   separation stays at 0.19 to 0.20. This is expected by construction: in the generator, whether a probe
   is answered depends on `D` and `m1`, not on use (study003.py:224).
3. **At m1 1.5, response that falls with `D` removes the probes' separation.**
   - DR's M2x3 w21 share falls from 0.795 to 0.526.
   - M2x3's DR-minus-S separation falls from 0.189 to 0.007. The probe rule then reads true change and no
     change at about the same rate.
   - Under M2 the separation turns negative (-0.071 ± 0.010). DR `[t0, 210)` alarms carry higher `D` on
     `t + 1` than S alarms (1.58 against 0.95). At m1 1.5 the answer probability falls with `D`, so DR
     loses more answers, and no answer reads as not confirmed. The `t + 1` answered share is 0.33 for DR w21
     alarms against 0.49 for S; it was not computed for DR `[t0, 210)`.
   - M2x3 keeps 0.623 of M0's 21-day sensitivity, against 0.937 at reference.

   At m1 0.5 the M2x3 separation falls only to 0.162 [difference -0.027, interval -0.054 to 0.000]. M2
   loses most of its separation (0.020).
4. **Comparison with spec 003's frozen cells (qualitative).** The m1_1.5 drop goes the same way as
   `results_003.json`'s DR-1.0 unconfirmable share, which rises from 0.23 at m1 0.5 to 0.55 at m1 1.5.
   - **Non-response.** The frozen rule sets an alarm with fewer than 2 answered confirmation probes aside
     as unconfirmable. r1's rules read no answer as not person change, so here non-response lowers the
     share.
   - **Otherwise not comparable.** The frozen metric scores each person's first in-window detection, with
     probes on days a + 9, a + 18 and a + 27. Here every alarm is scored, with probes on t + 1, t + 3 and
     t + 5.
   - **The frozen rule absorbs only part of it.** The frozen confirmed share among confirmable DR-1.0
     alarms also falls, from 0.733 to 0.637, so setting non-response aside does not remove the whole
     effect.

None of this is confirmatory. These are synthetic panels, with one seed per cell and expectations stated
in the hashed plan before the run.

## Checks

- `python3 sim/attribution_r5.py --check` passed. It covers:
  - the frozen hashes (PREREG-003 sha, the four listed files, `results_003.json` provenance);
  - r1's probe block and margin;
  - the S and DR-1.0 pairing;
  - that `Q` reads exactly the z the cell composite averages;
  - `run_study`'s five cell M0 metrics, reproduced at n 60;
  - M0-M3 and `Q` known answers on a hand panel.
- `python3 sim/study003.py --check` returned OK.
- `python3 sim/attribution.py --check` returned OK.
- `python3 sim/drift_sim.py --check`: a, b and d-i OK. Cell (c) with drift=True returns FAIL at 0.0605, the
  documented frozen P4 state (pre-freeze deviation 1, owner decision 2026-10-11 20:39), unchanged.
- The frozen files show no diff against HEAD.
