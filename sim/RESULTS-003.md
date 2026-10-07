# sim/RESULTS-003.md -- evaluation run scored against PREREG-003

**SYNTHETIC ONLY.** Every number below comes from simulated persons carrying one invented, non-diagnostic state.
No real person's data enters this run, and nothing here is a clinical or diagnostic finding.

- Scores `sim/PREREG-003.md` as frozen at commit `57208bc` (sha256 `06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79`).
- Evaluation seed, not chosen by hand: `int(sha256("<prereg sha256>:study003").hexdigest()[:16], 16) mod (2^32 - 1)`
  = **192815961** (PREREG-003 section 1; recomputed from the sha256 above when this note was written).
- Nothing was re-tuned after scoring. `tuning_003.json` and `study003.py` carry the sha256 listed in PREREG-003 section 1.
- Run facts from `sim/results_003.json`: label `EVALUATION (PREREG-003)`, `n` 4000 persons per cell, `nboot` 1000,
  `T` 210, onsets drawn on the integers [70, 121) (U[70, 120]), lags 3 / 9 / 29 days at `phi_D` 0.3 / 0.7 / 0.9.
  Written 2026-10-07 12:29 CDT, about 2 minutes after the freeze commit (12:27:07 CDT).
- Intervals are 95% person-bootstrap percentile intervals. Numbers are given at the 4 decimals stored in the JSON.

## Verdicts

Scored items (PREREG-003 sections 2 and 3), as printed by `python3 sim/study003.py verdicts sim/results_003.json`.
H2a and H3 are the registered predictions; H1a, H1b, H4 and H5 are construction checks.

| item | est | lo | hi | threshold | rule | holds |
|---|---|---|---|---|---|---|
| H1a (check) | -0.2643 | -0.2956 | -0.2345 | -0.15 | 95% interval at or below -0.15 | yes |
| H1b (check) | 0.8871 | 0.8398 | 0.9403 | 0.70 | 95% interval at or above 0.70 | yes |
| H2a (registered) | 0.2019 | 0.1748 | 0.2267 | 0.10 | 95% interval at or above 0.10 | yes |
| **H3 (registered), all six clauses** | | | | | all six clauses hold | **no** |
| H3 L1 PS-sub | 1.5756 | 1.4205 | 1.7489 | 1.5 | point estimate below 1.5 | **no** |
| H3 L1 PS-use | 1.4599 | 1.3211 | 1.6276 | 1.5 | point estimate below 1.5 | yes |
| H3 L2 PS-sub | 1.2110 | 1.1195 | 1.3090 | 1.5 | point estimate below 1.5 | yes |
| H3 L2 PS-use | 1.1935 | 1.1035 | 1.2859 | 1.5 | point estimate below 1.5 | yes |
| H3 L0 PS-sub | 3.1239 | 2.9606 | 3.3025 | 1.5 | 95% interval above 1.5 | yes |
| H3 L0 PS-use | 3.1286 | 2.9611 | 3.3126 | 1.5 | 95% interval above 1.5 | yes |
| H4 (check), L2 - L1 | 0.2035 | 0.1768 | 0.2306 | 0.0 | 95% interval above 0 | yes |
| H5 (check), M1 clause | -0.0014 | -0.0153 | 0.0123 | 0.10 | 95% interval inside (-0.10, 0.10) | yes |
| H5, L0+label clause | 0.0000 | 0.0000 | 0.0000 | | true by construction, not scored | not scored |

Reported, not scored (PREREG-003 sections 3 and 4).

| item | est | lo | hi |
|---|---|---|---|
| H2b, gap 28 d minus gap 56 d (`phi_D` 0.9) | 0.0475 | 0.0153 | 0.0801 |
| H6 DR-1.0, matched `k` minus `k = 0.5`, 21-day sensitivity (`phi_D` 0.7) | -0.0230 | -0.0335 | -0.0118 |
| H6 DR-1.5, same | -0.0518 | -0.0643 | -0.0395 |
| H3 L1 PS-sub (registered) | 1.5756 | 1.4205 | 1.7489 |
| H3 L1_step PS-sub (unregistered arm) | 0.9344 | 0.8570 | 1.0218 |
| H3 L1 PS-use (registered) | 1.4599 | 1.3211 | 1.6276 |
| H3 L1_step PS-use (unregistered arm) | 0.9273 | 0.8494 | 1.0141 |
| H4 L2 - L1 (registered) | 0.2035 | 0.1768 | 0.2306 |
| H4 L2 - L1_step (unregistered arm) | 0.2080 | 0.1827 | 0.2318 |

## Probe budget (PREREG-003 section 5)

Estimate [95% interval]. The last two columns: for S, confirmed false alarms per tracked month and no in-window
column; for DR-1.0 and DR-1.5, confirmed PPV and the share of persons confirmed in window.

| `phi_D` | family | rule | probes per tracked person-month | probed share of alarms | confirmed FA per tracked month (S) / confirmed PPV (DR) | persons confirmed in window (DR) |
|---|---|---|---|---|---|---|
| 0.3 | S | `all` | 1.3552 [1.3302, 1.3805] | 1.0000 [1.0000, 1.0000] | 0.0550 [0.0508, 0.0593] | n/a |
| 0.3 | S | `wait` | 1.3552 [1.3302, 1.3805] | 1.0000 [1.0000, 1.0000] | 0.0550 [0.0508, 0.0593] | n/a |
| 0.3 | S | `stop` | 1.2430 [1.2236, 1.2603] | 0.7888 [0.7670, 0.8102] | 0.0369 [0.0344, 0.0392] | n/a |
| 0.3 | DR-1.0 | `all` | 2.6492 [2.6063, 2.6911] | 1.0000 [1.0000, 1.0000] | 0.6798 [0.6524, 0.7077] | 0.1983 [0.1867, 0.2107] |
| 0.3 | DR-1.0 | `wait` | 2.6492 [2.6063, 2.6911] | 1.0000 [1.0000, 1.0000] | 0.6798 [0.6524, 0.7077] | 0.1983 [0.1867, 0.2107] |
| 0.3 | DR-1.0 | `stop` | 1.7263 [1.7021, 1.7489] | 0.4944 [0.4828, 0.5073] | 0.6691 [0.6394, 0.7007] | 0.1628 [0.1512, 0.1745] |
| 0.3 | DR-1.5 | `all` | 3.6990 [3.6541, 3.7401] | 1.0000 [1.0000, 1.0000] | 0.7995 [0.7816, 0.8184] | 0.3705 [0.3560, 0.3858] |
| 0.3 | DR-1.5 | `wait` | 3.6990 [3.6541, 3.7401] | 1.0000 [1.0000, 1.0000] | 0.7995 [0.7816, 0.8184] | 0.3705 [0.3560, 0.3858] |
| 0.3 | DR-1.5 | `stop` | 1.7982 [1.7750, 1.8177] | 0.3388 [0.3308, 0.3465] | 0.7954 [0.7764, 0.8158] | 0.3177 [0.3035, 0.3327] |
| 0.7 | S | `all` | 1.3506 [1.3242, 1.3772] | 1.0000 [1.0000, 1.0000] | 0.0661 [0.0610, 0.0712] | n/a |
| 0.7 | S | `wait` | 1.2585 [1.2391, 1.2772] | 0.8249 [0.8132, 0.8367] | 0.0533 [0.0493, 0.0572] | n/a |
| 0.7 | S | `stop` | 1.1704 [1.1557, 1.1850] | 0.6575 [0.6366, 0.6781] | 0.0377 [0.0353, 0.0401] | n/a |
| 0.7 | DR-1.0 | `all` | 2.4424 [2.3976, 2.4862] | 1.0000 [1.0000, 1.0000] | 0.5696 [0.5456, 0.5956] | 0.1787 [0.1678, 0.1905] |
| 0.7 | DR-1.0 | `wait` | 1.9521 [1.9254, 1.9781] | 0.6970 [0.6906, 0.7031] | 0.5684 [0.5426, 0.5960] | 0.1547 [0.1440, 0.1650] |
| 0.7 | DR-1.0 | `stop` | 1.5200 [1.5039, 1.5359] | 0.4299 [0.4204, 0.4401] | 0.5412 [0.5119, 0.5725] | 0.1265 [0.1170, 0.1368] |
| 0.7 | DR-1.5 | `all` | 3.3179 [3.2711, 3.3628] | 1.0000 [1.0000, 1.0000] | 0.6973 [0.6794, 0.7174] | 0.3207 [0.3065, 0.3352] |
| 0.7 | DR-1.5 | `wait` | 2.4009 [2.3763, 2.4249] | 0.6323 [0.6283, 0.6361] | 0.7030 [0.6834, 0.7242] | 0.2883 [0.2747, 0.3018] |
| 0.7 | DR-1.5 | `stop` | 1.6137 [1.6001, 1.6280] | 0.3165 [0.3107, 0.3228] | 0.6903 [0.6690, 0.7141] | 0.2480 [0.2350, 0.2613] |
| 0.9 | S | `all` | 1.4019 [1.3704, 1.4345] | 1.0000 [1.0000, 1.0000] | 0.0957 [0.0877, 0.1033] | n/a |
| 0.9 | S | `wait` | 1.1300 [1.1173, 1.1431] | 0.5293 [0.5143, 0.5457] | 0.0469 [0.0436, 0.0502] | n/a |
| 0.9 | S | `stop` | 1.0915 [1.0804, 1.1026] | 0.4627 [0.4462, 0.4802] | 0.0383 [0.0358, 0.0408] | n/a |
| 0.9 | DR-1.0 | `all` | 2.2687 [2.2201, 2.3174] | 1.0000 [1.0000, 1.0000] | 0.4632 [0.4386, 0.4873] | 0.1673 [0.1555, 0.1797] |
| 0.9 | DR-1.0 | `wait` | 1.3868 [1.3723, 1.4017] | 0.3895 [0.3825, 0.3970] | 0.4074 [0.3743, 0.4384] | 0.0930 [0.0838, 0.1015] |
| 0.9 | DR-1.0 | `stop` | 1.2869 [1.2760, 1.2981] | 0.3204 [0.3127, 0.3288] | 0.4002 [0.3669, 0.4311] | 0.0902 [0.0810, 0.0990] |
| 0.9 | DR-1.5 | `all` | 2.9260 [2.8752, 2.9802] | 1.0000 [1.0000, 1.0000] | 0.5489 [0.5279, 0.5690] | 0.2602 [0.2462, 0.2740] |
| 0.9 | DR-1.5 | `wait` | 1.5265 [1.5131, 1.5400] | 0.3341 [0.3291, 0.3389] | 0.5165 [0.4909, 0.5418] | 0.1603 [0.1485, 0.1710] |
| 0.9 | DR-1.5 | `stop` | 1.3773 [1.3684, 1.3867] | 0.2632 [0.2575, 0.2684] | 0.5122 [0.4859, 0.5376] | 0.1575 [0.1457, 0.1683] |

At `phi_D` 0.7, `wait` meets the 3.0 target for DR-1.5, the only family whose `all` arm exceeds it (3.3179 [3.2711, 3.3628]),
on the point estimate (2.4009) and on the whole interval (upper bound 2.4249), and costs DR-1.5 0.0324 of persons
confirmed in window against `all` (0.3207 to 0.2883; the JSON stores no paired interval for this difference).

## Reading

1. Of the two registered predictions, H2a holds (0.2019 [0.1748, 0.2267], interval above 0.10) and H3 fails.
2. H3 fails on one of its six clauses: L1 on PS-sub has a point estimate of 1.5756 against the rule "below 1.5",
   0.0756 above the threshold, interval [1.4205, 1.7489]. The other five clauses hold: L1 PS-use 1.4599 (0.0401
   below 1.5), L2 PS-sub 1.2110 and PS-use 1.1935, L0 lower bounds 2.9606 and 2.9611 above 1.5.
3. The frozen text flagged this clause before the run. Section 1 projected the L1 clause to hold with probability
   0.880 (PS-sub) at N 4000 if the design-seed value were the truth. Section 2 recorded that the check seed 20261004
   gave PS-sub L1/S 1.629 [1.421, 1.864], above 1.5, and that the L1 clause "may fail about as often as it holds".
   The evaluation estimate, 1.5756, lies between the design seed's 1.421 and the check seed's 1.629.
4. Under section 2, H3 is reported as failed and nothing is re-tuned. The L1_step ratios (0.9344 PS-sub, 0.9273
   PS-use) belong to the unregistered arm of section 4 and do not enter the H3 verdict.
5. All four construction checks hold: H1a -0.2643 [-0.2956, -0.2345], H1b 0.8871 [0.8398, 0.9403], H4 0.2035
   [0.1768, 0.2306], H5 M1 -0.0014 [-0.0153, 0.0123]. H5's L0+label clause is 0.0000 by construction.
6. Among the unscored items, H2b is 0.0475 [0.0153, 0.0801] (design -0.003 [-0.069, 0.057]), and H6 is negative
   for both DR-1.0 (-0.0230 [-0.0335, -0.0118]) and DR-1.5 (-0.0518 [-0.0643, -0.0395]); section 4 predicted no
   direction for H6.

## Deviations

None from the frozen text found. The `score` subcommand ran once, writing `sim/results_003.json`. The run log
(`/tmp/score003.log`, created 12:27:52 CDT, last line `exit 0 at 12:29:09`) puts it at under 2 minutes, shorter
than the plan expected; PREREG-003 itself states no expected duration. The file's `n` field reads 4000, the
section 1 evaluation N (`N_SCORE`), so the short run was not a smaller run. Section 6 says the exact scoring
commands were to be written at freeze; the frozen text names the command form only in section 1
(`study003.py score --prereg-sha <sha>`).

## Files

- `sim/results_003.json`, sha256 `922cd808aa05602750d3e2908b9354f8ec91ddb2736b8381faa8fd56c0e8000c` (untracked when this note was written).
- `sim/PREREG-003.md`, sha256 `06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79` (frozen at `57208bc`).
- Provenance block of `results_003.json` (`label`, `prereg_sha256`, `seed`, `n`, and the `sha256` map written by `provenance()`):

```
label           EVALUATION (PREREG-003)
prereg_sha256   06ee47576d02bc440560115b07aad029e8c7574480b684b4c7779d796c99bb79
seed            192815961
n               4000
study003.py     037f31ec7534c8c4afd5364dd9b55f504c5f8f7479d7e2750f0b0ec8b00c031e
drift_sim.py    206a549651f351dfa47e0d72468f1c787d6df9d83d2df5a8516fb74b9837db87
attribution.py  06060e3c3fefd97a30d6bd6fc65235ff4ab544a4a2d97275559f3a12deb78655
tuning_003.json c7002d79ffb9cf99eabcbd0888fa375ae2c2528fd968237d6ce40fd4384bd51d
```
