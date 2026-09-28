# sim/RESULTS.md

P1 to P3 are pipeline construction checks, not findings.

## P1: FAIL

```json
{
  "SP": {
    "ratio_naive_over_fixed": 1.233859748293466,
    "ci95": [
      1.1276584103683367,
      1.3517850753295177
    ],
    "threshold": [
      2.0,
      null
    ],
    "ablation_ratio": 1.0470921168423462,
    "note": "confirmed by A-fixed-minus-iii",
    "PASS": false
  },
  "VA": {
    "ratio_naive_over_fixed": 1.0341899214360575,
    "ci95": [
      0.9209307148399453,
      1.15883108030883
    ],
    "threshold": [
      0.5,
      2.0
    ],
    "ablation_ratio": null,
    "note": "no matching component",
    "PASS": true
  },
  "DE": {
    "ratio_naive_over_fixed": 1.004429066194671,
    "ci95": [
      0.887533571129622,
      1.139816362449963
    ],
    "threshold": [
      0.5,
      2.0
    ],
    "ablation_ratio": null,
    "note": "no matching component",
    "PASS": true
  },
  "BI": {
    "ratio_naive_over_fixed": 0.8000799444481193,
    "ci95": [
      0.7229368449474585,
      0.8744633449041094
    ],
    "threshold": [
      0.5,
      2.0
    ],
    "ablation_ratio": null,
    "note": "no matching component",
    "PASS": true
  }
}
```

## P1b: PASS

```json
{
  "de_over_s_fa_ratio": 0.9714021414484006,
  "threshold": 1.5,
  "PASS": true
}
```

## P2: FAIL

```json
{
  "sens_A_naive": 0.108,
  "sens_A_fixed": 0.2,
  "sens_A_fixed_minus_i": 0.147,
  "gap": 0.09200000000000001,
  "gap_explained_by_i": 0.05300000000000002,
  "PASS": false
}
```

## P3: FAIL

```json
{
  "av_logged_removeiv_ratio": 1.8471966317973942,
  "av2_over_s_ratio": 1.7479819209528602,
  "PASS": false
}
```

## P4: FAIL

```json
{
  "all_days": {
    "slope": 0.9301928367161915,
    "corr": 0.47138868260701944
  },
  "triggered": {
    "slope": 0.8906220949024769,
    "corr": 0.4814866248370666,
    "corr_deflation": -0.010097942230047174,
    "slope_attenuation_rel": 0.04254036394583404
  },
  "mixed": {
    "slope": 0.9280214659356326,
    "corr": 0.4962639091294609
  },
  "mixed_ipw": {
    "slope": 0.8868653621310675,
    "corr": 0.48857329329401994,
    "slope_diff": 0.04332747458512398,
    "corr_diff": 0.0171846106870005
  },
  "current_check_isolated_mechanism": {
    "false": [
      1.2737564917154398,
      1.2242044480001057,
      0.03890228943885461
    ],
    "true": [
      1.4149939319773537,
      1.3293979637034035,
      0.060492109781938024
    ]
  },
  "PASS": false
}
```

## P5: FAIL

```json
{
  "rel_bias_by_m1_and_schedule": {
    "default": {
      "fixed": 0.004942028629761267,
      "random": 0.023677329622998212,
      "triggered": 0.04254036394583404,
      "mixed": 0.01319006284611282
    },
    "m1_05": {
      "fixed": 0.018057630894768167,
      "random": 0.01062142237034599,
      "triggered": 0.04240162438812968,
      "mixed": 0.004961337827033925
    },
    "m1_15": {
      "fixed": 0.01742474290025356,
      "random": 0.03958965252803192,
      "triggered": 0.00601782939345587,
      "mixed": 0.03670003203313786
    }
  },
  "m1_05_random_under_5pct": true,
  "m1_15_added_bias_ge_10pct_every_schedule": false,
  "response_propensity_ipw_m1_15_random": {
    "bias_raw": 0.02958874506549214,
    "bias_ipw": 0.020720683769336223,
    "frac_removed": 0.29971062566280615,
    "removes_less_than_half": true
  },
  "PASS": false
}
```

## P6: PASS

```json
{
  "default": {
    "ind4_att_formula_mean": 0.25485700816798423,
    "ind4_att_mc_mean": 0.27830736789910127,
    "ind4_within_0.03": true,
    "ind4_filtered_att_formula_mean": 0.8210435092878201,
    "ind4_filtered_att_mc_mean": 0.8335720952492927,
    "ind4_filtered_within_0.03": true,
    "ind5_att_formula_mean": 0.26001901934114613,
    "ind5_att_mc_mean": 0.27089153069096356,
    "ind5_within_0.03": true,
    "ind5_filtered_att_formula_mean": 0.7869904051509504,
    "ind5_filtered_att_mc_mean": 0.7891483887618816,
    "ind5_filtered_within_0.03": true
  },
  "bernoulli_mix": {
    "ind4_att_formula_mean": 0.20851051520449712,
    "ind4_att_mc_mean": 0.18961843496637457,
    "ind4_within_0.03": true,
    "ind4_filtered_att_formula_mean": 0.20851051521739492,
    "ind4_filtered_att_mc_mean": 0.18961843497926542,
    "ind4_filtered_within_0.03": true,
    "ind5_att_formula_mean": 0.187050969508098,
    "ind5_att_mc_mean": 0.184220469377905,
    "ind5_within_0.03": true,
    "ind5_filtered_att_formula_mean": 0.18705096951981914,
    "ind5_filtered_att_mc_mean": 0.18422046938972614,
    "ind5_filtered_within_0.03": true
  },
  "pi_rises_with_D": {
    "ind4_att_formula_mean": 0.27644532168194397,
    "ind4_att_mc_mean": 0.42699088899224463,
    "ind4_within_0.03": false,
    "ind4_filtered_att_formula_mean": 0.9082655700612007,
    "ind4_filtered_att_mc_mean": 1.0307026594259943,
    "ind4_filtered_within_0.03": false,
    "ind5_att_formula_mean": 0.285023898056776,
    "ind5_att_mc_mean": -0.08201930690182851,
    "ind5_within_0.03": false,
    "ind5_filtered_att_formula_mean": 0.8998372643524487,
    "ind5_filtered_att_mc_mean": 0.32712434004204055,
    "ind5_filtered_within_0.03": false
  },
  "pi_rises_signed_departure": {
    "higher_by_ge_0_05": true
  },
  "PASS": true
}
```

## P7: FAIL

```json
{
  "sens_DR": 0.197,
  "sens_DV": 0.087,
  "gap_points": 11.000000000000002,
  "PASS": false
}
```

## P8: PASS

```json
{
  "sens_A_fixed": 0.197,
  "sens_probe_only": 0.024,
  "sens_gap_points": 17.3,
  "rmst42_A_fixed": 33.454,
  "rmst42_probe_only": 40.573,
  "rmst_gap_days": 7.119,
  "PASS": true
}
```

## P9: FAIL

```json
{
  "sens_BD_days29_49": 0.272,
  "sens_DR": 0.197,
  "PASS": false
}
```

## P10: PASS

```json
{
  "fa_CS": 0.25879408215259464,
  "fa_S": 0.1510476423869092,
  "ratio": 1.7133275174841356,
  "PASS": true
}
```
