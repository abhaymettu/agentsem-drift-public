# sim/METRICS.md

REPORTING ONLY: PREREG section 5 metrics that `score()` does
not output. No thresholds and no verdicts are computed or implied here -- every number
below is a plain report, with a 95% Monte Carlo interval from a 2000-draw person
bootstrap (`mc_stat`), exactly as score()'s predictions use. "Flag" is this file's word
for a CUSUM alarm; "tracked" person-months count only days the layer did not abstain,
"total" person-months count every post-baseline day regardless of abstention.

## a_sensitivity_vs_false_flag_curve

```json
{
  "note": "h swept on the default cell; false-flag rate measured on family S, sensitivity within 21 days of onset measured on family DR, at each swept h.",
  "curve": {
    "A-fixed": [
      {
        "h": 0.6668119730507078,
        "fa_per_tracked_person_month": {
          "point": 1.167277466498836,
          "se": 0.018277384916411336,
          "lo": 1.1315026648005087,
          "hi": 1.2030656402788067
        },
        "sensitivity_within_21d": {
          "point": 0.057,
          "se": 0.0072934428190037275,
          "lo": 0.043,
          "hi": 0.072
        }
      },
      {
        "h": 0.8091143576943441,
        "fa_per_tracked_person_month": {
          "point": 1.0125538859122454,
          "se": 0.018366938726693316,
          "lo": 0.9760354391631302,
          "hi": 1.0468774634797895
        },
        "sensitivity_within_21d": {
          "point": 0.081,
          "se": 0.008703597305311552,
          "lo": 0.064975,
          "hi": 0.099
        }
      },
      {
        "h": 0.9817850762816865,
        "fa_per_tracked_person_month": {
          "point": 0.8618404197253071,
          "se": 0.018408803177365488,
          "lo": 0.8264377205388206,
          "hi": 0.8971438432477565
        },
        "sensitivity_within_21d": {
          "point": 0.118,
          "se": 0.010272800638895085,
          "lo": 0.09897500000000001,
          "hi": 0.138
        }
      },
      {
        "h": 1.1913049457633855,
        "fa_per_tracked_person_month": {
          "point": 0.7097902487384848,
          "se": 0.01787871833791848,
          "lo": 0.6750553756987603,
          "hi": 0.7437957419420492
        },
        "sensitivity_within_21d": {
          "point": 0.157,
          "se": 0.011380688809948827,
          "lo": 0.135,
          "hi": 0.179
        }
      },
      {
        "h": 1.4455378352004142,
        "fa_per_tracked_person_month": {
          "point": 0.579795706949751,
          "se": 0.016761817757342087,
          "lo": 0.5467501264247985,
          "hi": 0.6114396054914472
        },
        "sensitivity_within_21d": {
          "point": 0.203,
          "se": 0.012844977256513932,
          "lo": 0.178,
          "hi": 0.228
        }
      },
      {
        "h": 1.7540258188527054,
        "fa_per_tracked_person_month": {
          "point": 0.4548138081605828,
          "se": 0.01543592830808323,
          "lo": 0.42401951922161735,
          "hi": 0.4848524001709321
        },
        "sensitivity_within_21d": {
          "point": 0.222,
          "se": 0.013364174809323883,
          "lo": 0.196,
          "hi": 0.248
        }
      },
      {
        "h": 2.128347317021524,
        "fa_per_tracked_person_month": {
          "point": 0.34286478117028507,
          "se": 0.014008263166812878,
          "lo": 0.3144435034968136,
          "hi": 0.3690677712587922
        },
        "sensitivity_within_21d": {
          "point": 0.24,
          "se": 0.01385263681662761,
          "lo": 0.214,
          "hi": 0.268
        }
      },
      {
        "h": 2.5825516666771,
        "fa_per_tracked_person_month": {
          "point": 0.24896126897842336,
          "se": 0.01177224272514762,
          "lo": 0.22587511992273643,
          "hi": 0.2710522276543493
        },
        "sensitivity_within_21d": {
          "point": 0.229,
          "se": 0.013555127249029006,
          "lo": 0.203,
          "hi": 0.256
        }
      },
      {
        "h": 3.1336864325275053,
        "fa_per_tracked_person_month": {
          "point": 0.17143239058514254,
          "se": 0.010213414284495853,
          "lo": 0.1512945458063005,
          "hi": 0.19131130619567205
        },
        "sensitivity_within_21d": {
          "point": 0.202,
          "se": 0.012787521421372126,
          "lo": 0.177,
          "hi": 0.229
        }
      },
      {
        "h": 3.80243724999395,
        "fa_per_tracked_person_month": {
          "point": 0.11796419858977643,
          "se": 0.008382482616664922,
          "lo": 0.10131430284263818,
          "hi": 0.13394553748331295
        },
        "sensitivity_within_21d": {
          "point": 0.154,
          "se": 0.011322968893460812,
          "lo": 0.132975,
          "hi": 0.176
        }
      },
      {
        "h": 4.613904215196121,
        "fa_per_tracked_person_month": {
          "point": 0.07518964499348356,
          "se": 0.006484824271707977,
          "lo": 0.06259927605228001,
          "hi": 0.0876560782030742
        },
        "sensitivity_within_21d": {
          "point": 0.133,
          "se": 0.010701703648508037,
          "lo": 0.112,
          "hi": 0.154
        }
      },
      {
        "h": 5.598543962043925,
        "fa_per_tracked_person_month": {
          "point": 0.04845554899580052,
          "se": 0.00506318175240339,
          "lo": 0.03874067211275103,
          "hi": 0.058397441659762156
        },
        "sensitivity_within_21d": {
          "point": 0.09,
          "se": 0.00888614206280657,
          "lo": 0.073,
          "hi": 0.108
        }
      },
      {
        "h": 6.793312785234353,
        "fa_per_tracked_person_month": {
          "point": 0.027736624597596158,
          "se": 0.003880095733379316,
          "lo": 0.02042707178420004,
          "hi": 0.03546971457497007
        },
        "sensitivity_within_21d": {
          "point": 0.052,
          "se": 0.006927255187461778,
          "lo": 0.039,
          "hi": 0.066
        }
      },
      {
        "h": 8.243053713769596,
        "fa_per_tracked_person_month": {
          "point": 0.016040457598609826,
          "se": 0.002702688151599441,
          "lo": 0.011046127037909956,
          "hi": 0.02145497258849947
        },
        "sensitivity_within_21d": {
          "point": 0.034,
          "se": 0.0056096313365377164,
          "lo": 0.023,
          "hi": 0.045
        }
      },
      {
        "h": 10.002179595760616,
        "fa_per_tracked_person_month": {
          "point": 0.010693638399073217,
          "se": 0.002156635959345626,
          "lo": 0.00667978502426986,
          "hi": 0.015051933520976222
        },
        "sensitivity_within_21d": {
          "point": 0.02,
          "se": 0.004415137905135091,
          "lo": 0.012,
          "hi": 0.029
        }
      }
    ],
    "A-naive": [
      {
        "h": 0.34778867881629594,
        "fa_per_tracked_person_month": {
          "point": 0.999509880366253,
          "se": 0.0188281444260694,
          "lo": 0.963059057021341,
          "hi": 1.0350758622192877
        },
        "sensitivity_within_21d": {
          "point": 0.038,
          "se": 0.006236020764677483,
          "lo": 0.026,
          "hi": 0.05
        }
      },
      {
        "h": 0.4220092392558354,
        "fa_per_tracked_person_month": {
          "point": 0.8925746875487335,
          "se": 0.01866508355865488,
          "lo": 0.8561121785977996,
          "hi": 0.9275935569823994
        },
        "sensitivity_within_21d": {
          "point": 0.061,
          "se": 0.00768755281179369,
          "lo": 0.046,
          "hi": 0.077
        }
      },
      {
        "h": 0.512068991502044,
        "fa_per_tracked_person_month": {
          "point": 0.7806269075678927,
          "se": 0.018216712622168764,
          "lo": 0.7444020775846241,
          "hi": 0.8156043827372151
        },
        "sensitivity_within_21d": {
          "point": 0.1,
          "se": 0.009456959397212207,
          "lo": 0.08297500000000001,
          "hi": 0.118
        }
      },
      {
        "h": 0.6213481309563404,
        "fa_per_tracked_person_month": {
          "point": 0.6476262615011028,
          "se": 0.017527762467003487,
          "lo": 0.6143707012256147,
          "hi": 0.6817998855700464
        },
        "sensitivity_within_21d": {
          "point": 0.131,
          "se": 0.01068775504041433,
          "lo": 0.111,
          "hi": 0.152
        }
      },
      {
        "h": 0.7539482105926276,
        "fa_per_tracked_person_month": {
          "point": 0.5239824448058458,
          "se": 0.01626617969012667,
          "lo": 0.49217397581527383,
          "hi": 0.5567905658453642
        },
        "sensitivity_within_21d": {
          "point": 0.168,
          "se": 0.011931467793689756,
          "lo": 0.145,
          "hi": 0.192
        }
      },
      {
        "h": 0.9148460837581034,
        "fa_per_tracked_person_month": {
          "point": 0.4140396996903335,
          "se": 0.015046124043087424,
          "lo": 0.3849659200811881,
          "hi": 0.44319925504762364
        },
        "sensitivity_within_21d": {
          "point": 0.186,
          "se": 0.01246176518579021,
          "lo": 0.162,
          "hi": 0.21
        }
      },
      {
        "h": 1.1100806994550385,
        "fa_per_tracked_person_month": {
          "point": 0.32514982066077036,
          "se": 0.013849356398000476,
          "lo": 0.29731490183362624,
          "hi": 0.35183178677487437
        },
        "sensitivity_within_21d": {
          "point": 0.19,
          "se": 0.012233898719907096,
          "lo": 0.166,
          "hi": 0.214
        }
      },
      {
        "h": 1.3469797610549945,
        "fa_per_tracked_person_month": {
          "point": 0.24260921870474747,
          "se": 0.012155074180085965,
          "lo": 0.21826700224928022,
          "hi": 0.26661232583984906
        },
        "sensitivity_within_21d": {
          "point": 0.198,
          "se": 0.012622228570147132,
          "lo": 0.174975,
          "hi": 0.224
        }
      },
      {
        "h": 1.634434755583512,
        "fa_per_tracked_person_month": {
          "point": 0.17376968832846926,
          "se": 0.010389305636579185,
          "lo": 0.1534321045935936,
          "hi": 0.1934579669388165
        },
        "sensitivity_within_21d": {
          "point": 0.164,
          "se": 0.011911528029602247,
          "lo": 0.142,
          "hi": 0.18802499999999986
        }
      },
      {
        "h": 1.9832346761966437,
        "fa_per_tracked_person_month": {
          "point": 0.1196337469646,
          "se": 0.008859155128285272,
          "lo": 0.10185757163678841,
          "hi": 0.13694211018093877
        },
        "sensitivity_within_21d": {
          "point": 0.135,
          "se": 0.010809750429689673,
          "lo": 0.115,
          "hi": 0.15602499999999986
        }
      },
      {
        "h": 2.4064709633910115,
        "fa_per_tracked_person_month": {
          "point": 0.08387729186624189,
          "se": 0.007208986340893687,
          "lo": 0.07016268000520567,
          "hi": 0.09808868826645266
        },
        "sensitivity_within_21d": {
          "point": 0.102,
          "se": 0.009450547096343688,
          "lo": 0.084,
          "hi": 0.121
        }
      },
      {
        "h": 2.9200288635281293,
        "fa_per_tracked_person_month": {
          "point": 0.05046004411076704,
          "se": 0.005738347092819583,
          "lo": 0.039484230674545144,
          "hi": 0.06183997320669573
        },
        "sensitivity_within_21d": {
          "point": 0.074,
          "se": 0.008124123071928682,
          "lo": 0.058,
          "hi": 0.09
        }
      },
      {
        "h": 3.5431836467382114,
        "fa_per_tracked_person_month": {
          "point": 0.03107804041259162,
          "se": 0.004566916498790018,
          "lo": 0.022427060136401777,
          "hi": 0.04000854722498499
        },
        "sensitivity_within_21d": {
          "point": 0.053,
          "se": 0.006923883381494829,
          "lo": 0.04,
          "hi": 0.067
        }
      },
      {
        "h": 4.299324061935645,
        "fa_per_tracked_person_month": {
          "point": 0.01904783122062067,
          "se": 0.0033655756033743496,
          "lo": 0.013010006901281821,
          "hi": 0.026066244530381064
        },
        "sensitivity_within_21d": {
          "point": 0.033,
          "se": 0.0056265375643002,
          "lo": 0.022,
          "hi": 0.045
        }
      },
      {
        "h": 5.216830182244439,
        "fa_per_tracked_person_month": {
          "point": 0.0116960367144162,
          "se": 0.002495165634751288,
          "lo": 0.007327892694152606,
          "hi": 0.016728585669052182
        },
        "sensitivity_within_21d": {
          "point": 0.024,
          "se": 0.004862385875082221,
          "lo": 0.015,
          "hi": 0.034
        }
      }
    ]
  }
}
```

## b_abstention_share_by_family

```json
{
  "note": "Reasons: unused_day (no usage), no_usable_indicator, low_usage_abstain_v (feature v), version_reset_hold_iv (feature iv). Share is of post-baseline (tracked-window) person-days.",
  "by_family": {
    "S": {
      "total_abstention_share": {
        "point": 0.19845535714285714,
        "se": 0.0011989765857190757,
        "lo": 0.19605357142857144,
        "hi": 0.2007859375
      },
      "unused_day": {
        "point": 0.19844642857142858,
        "se": 0.0011986445658809894,
        "lo": 0.19604464285714285,
        "hi": 0.2007595982142857
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 8.92857142857143e-06,
        "se": 9.191511701120724e-06,
        "lo": 0.0,
        "hi": 2.6785714285714284e-05
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "DR": {
      "total_abstention_share": {
        "point": 0.19941071428571427,
        "se": 0.001159762662366436,
        "lo": 0.19713392857142858,
        "hi": 0.20161674107142857
      },
      "unused_day": {
        "point": 0.19934821428571428,
        "se": 0.001155652023329927,
        "lo": 0.19708035714285715,
        "hi": 0.20154486607142857
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 6.25e-05,
        "se": 3.635833443072919e-05,
        "lo": 0.0,
        "hi": 0.00014285714285714287
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "VA": {
      "total_abstention_share": {
        "point": 0.2895625,
        "se": 0.0014640711362450107,
        "lo": 0.28657120535714287,
        "hi": 0.29247321428571427
      },
      "unused_day": {
        "point": 0.2667946428571429,
        "se": 0.0012365603510012784,
        "lo": 0.2643212053571429,
        "hi": 0.26917857142857143
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 0.022767857142857142,
        "se": 0.0004966312707245125,
        "lo": 0.021767857142857144,
        "hi": 0.023741294642857142
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "SP": {
      "total_abstention_share": {
        "point": 0.20033928571428572,
        "se": 0.0011995567404087927,
        "lo": 0.1979015625,
        "hi": 0.20267924107142857
      },
      "unused_day": {
        "point": 0.20033928571428572,
        "se": 0.0011995567404087927,
        "lo": 0.1979015625,
        "hi": 0.20267924107142857
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "BI": {
      "total_abstention_share": {
        "point": 0.20258928571428572,
        "se": 0.001144670188846723,
        "lo": 0.20041049107142855,
        "hi": 0.20483950892857145
      },
      "unused_day": {
        "point": 0.20257142857142857,
        "se": 0.0011435887658150835,
        "lo": 0.20038392857142856,
        "hi": 0.20481294642857142
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 1.785714285714286e-05,
        "se": 1.2620538056166554e-05,
        "lo": 0.0,
        "hi": 4.464285714285714e-05
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "AV": {
      "total_abstention_share": {
        "point": 0.25144642857142857,
        "se": 0.0019460378601366375,
        "lo": 0.24760669642857144,
        "hi": 0.25537522321428574
      },
      "unused_day": {
        "point": 0.20179464285714285,
        "se": 0.0011497124275853927,
        "lo": 0.19962477678571428,
        "hi": 0.20398214285714286
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 1.785714285714286e-05,
        "se": 1.7971918625670084e-05,
        "lo": 0.0,
        "hi": 5.357142857142857e-05
      },
      "version_reset_hold_iv": {
        "point": 0.04963392857142857,
        "se": 0.001613303756471827,
        "lo": 0.04655267857142857,
        "hi": 0.052866294642857144
      }
    },
    "DE": {
      "total_abstention_share": {
        "point": 0.5095625,
        "se": 0.003031238123693547,
        "lo": 0.5037044642857142,
        "hi": 0.515671875
      },
      "unused_day": {
        "point": 0.4600714285714286,
        "se": 0.0022999236157780533,
        "lo": 0.4556515625,
        "hi": 0.46469642857142857
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 0.049491071428571426,
        "se": 0.0010383400802122808,
        "lo": 0.0474015625,
        "hi": 0.05150915178571429
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "DV": {
      "total_abstention_share": {
        "point": 0.2947767857142857,
        "se": 0.0015480667200151149,
        "lo": 0.29169620535714286,
        "hi": 0.2976785714285714
      },
      "unused_day": {
        "point": 0.27082142857142855,
        "se": 0.0012809175370781746,
        "lo": 0.2682316964285714,
        "hi": 0.2732232142857143
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 0.023955357142857143,
        "se": 0.0005080861861119272,
        "lo": 0.022919642857142857,
        "hi": 0.024964285714285713
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "CS": {
      "total_abstention_share": {
        "point": 0.2009642857142857,
        "se": 0.001186183391285087,
        "lo": 0.19854441964285713,
        "hi": 0.20323258928571428
      },
      "unused_day": {
        "point": 0.20092857142857143,
        "se": 0.0011847261262886589,
        "lo": 0.1985263392857143,
        "hi": 0.2031879464285714
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 3.571428571428572e-05,
        "se": 2.2271168313668742e-05,
        "lo": 0.0,
        "hi": 8.928571428571429e-05
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "BD": {
      "total_abstention_share": {
        "point": 0.19961607142857143,
        "se": 0.0012274540735581218,
        "lo": 0.19712477678571427,
        "hi": 0.202
      },
      "unused_day": {
        "point": 0.1995625,
        "se": 0.0012231892931335508,
        "lo": 0.19707142857142856,
        "hi": 0.2019377232142857
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 5.357142857142857e-05,
        "se": 3.7709288928317944e-05,
        "lo": 0.0,
        "hi": 0.00013392857142857144
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "AV2": {
      "total_abstention_share": {
        "point": 0.2020267857142857,
        "se": 0.0012072355739488312,
        "lo": 0.1996875,
        "hi": 0.20443883928571427
      },
      "unused_day": {
        "point": 0.20201785714285714,
        "se": 0.001206554014422399,
        "lo": 0.19968727678571427,
        "hi": 0.20442968749999998
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 8.92857142857143e-06,
        "se": 8.633441464625129e-06,
        "lo": 0.0,
        "hi": 2.6785714285714284e-05
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    }
  },
  "DR_kappa_0_3": {
    "total_abstention_share": {
      "point": 0.23158928571428572,
      "se": 0.001315009243526787,
      "lo": 0.22904464285714285,
      "hi": 0.23426785714285714
    },
    "unused_day": {
      "point": 0.23142857142857143,
      "se": 0.001303747442744084,
      "lo": 0.22891941964285714,
      "hi": 0.23405379464285714
    },
    "no_usable_indicator": {
      "point": 0.0,
      "se": 0.0,
      "lo": 0.0,
      "hi": 0.0
    },
    "low_usage_abstain_v": {
      "point": 0.0001607142857142857,
      "se": 5.7446477115818816e-05,
      "lo": 6.25e-05,
      "hi": 0.00028571428571428574
    },
    "version_reset_hold_iv": {
      "point": 0.0,
      "se": 0.0,
      "lo": 0.0,
      "hi": 0.0
    }
  },
  "DR_kappa_0": {
    "total_abstention_share": {
      "point": 0.19941071428571427,
      "se": 0.001159762662366436,
      "lo": 0.19713392857142858,
      "hi": 0.20161674107142857
    },
    "unused_day": {
      "point": 0.19934821428571428,
      "se": 0.001155652023329927,
      "lo": 0.19708035714285715,
      "hi": 0.20154486607142857
    },
    "no_usable_indicator": {
      "point": 0.0,
      "se": 0.0,
      "lo": 0.0,
      "hi": 0.0
    },
    "low_usage_abstain_v": {
      "point": 6.25e-05,
      "se": 3.635833443072919e-05,
      "lo": 0.0,
      "hi": 0.00014285714285714287
    },
    "version_reset_hold_iv": {
      "point": 0.0,
      "se": 0.0,
      "lo": 0.0,
      "hi": 0.0
    }
  }
}
```

## c_probes_per_person_month_by_family_schedule

```json
{
  "S": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.01875,
        "se": 0.027080680474488552,
        "lo": 2.96625,
        "hi": 3.0709955357142857
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 1.4975892857142858,
        "se": 0.060117854189270896,
        "lo": 1.3789285714285713,
        "hi": 1.6130357142857141
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 2.410446428571429,
        "se": 0.04993282426232067,
        "lo": 2.313200892857143,
        "hi": 2.5063459821428564
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.2451785714285712,
        "se": 0.04759719965547322,
        "lo": 2.1535714285714285,
        "hi": 2.3389285714285712
      },
      "ipw_identified": false
    }
  },
  "DR": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.006964285714286,
        "se": 0.0269860123356228,
        "lo": 2.953660714285714,
        "hi": 3.0600066964285713
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 3.232767857142857,
        "se": 0.07360312302414622,
        "lo": 3.0881183035714286,
        "hi": 3.3817098214285712
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 3.7808035714285717,
        "se": 0.0617341614936649,
        "lo": 3.657046875,
        "hi": 3.9042991071428568
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 3.9297321428571426,
        "se": 0.06347196631037383,
        "lo": 3.8126651785714283,
        "hi": 4.057767857142857
      },
      "ipw_identified": false
    }
  },
  "VA": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.002410714285714,
        "se": 0.027428169331288176,
        "lo": 2.9480290178571424,
        "hi": 3.0562499999999995
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 1.2854464285714284,
        "se": 0.05000852359940107,
        "lo": 1.1844508928571427,
        "hi": 1.3824308035714283
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 2.2165178571428568,
        "se": 0.04348323270162892,
        "lo": 2.132142857142857,
        "hi": 2.298482142857143
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.015625,
        "se": 0.039737692041667015,
        "lo": 1.9374107142857142,
        "hi": 2.0954531249999997
      },
      "ipw_identified": false
    }
  },
  "SP": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 2.9689285714285716,
        "se": 0.025759488607175994,
        "lo": 2.9201718750000003,
        "hi": 3.020089285714285
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 1.6103571428571428,
        "se": 0.05883215302976908,
        "lo": 1.4957008928571427,
        "hi": 1.72715625
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 2.4854464285714286,
        "se": 0.05053179429040911,
        "lo": 2.387142857142857,
        "hi": 2.581908482142857
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.3823214285714283,
        "se": 0.04832892435507884,
        "lo": 2.2890870535714285,
        "hi": 2.4774241071428573
      },
      "ipw_identified": false
    }
  },
  "BI": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 2.9483035714285717,
        "se": 0.027689010001748258,
        "lo": 2.8968549107142856,
        "hi": 3.0029531249999994
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 1.7416071428571427,
        "se": 0.06204499283359553,
        "lo": 1.620254464285714,
        "hi": 1.869113839285714
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 2.5883035714285714,
        "se": 0.05291562544205183,
        "lo": 2.4843482142857143,
        "hi": 2.689024553571428
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.4851785714285715,
        "se": 0.04681066884312985,
        "lo": 2.393015625,
        "hi": 2.576256696428571
      },
      "ipw_identified": false
    }
  },
  "AV": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.0238392857142857,
        "se": 0.026508767217337817,
        "lo": 2.9732142857142856,
        "hi": 3.0760714285714283
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 1.696607142857143,
        "se": 0.06128911489100989,
        "lo": 1.5790111607142856,
        "hi": 1.8171562499999998
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 2.53125,
        "se": 0.05205598276464474,
        "lo": 2.429444196428572,
        "hi": 2.6336049107142854
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.3702678571428573,
        "se": 0.04657697966073823,
        "lo": 2.280535714285714,
        "hi": 2.463770089285714
      },
      "ipw_identified": false
    }
  },
  "DE": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 2.999732142857143,
        "se": 0.026060131105449146,
        "lo": 2.950982142857143,
        "hi": 3.0508995535714285
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 0.8630357142857142,
        "se": 0.04098370876775975,
        "lo": 0.7840111607142857,
        "hi": 0.9455424107142857
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 1.912232142857143,
        "se": 0.03692263368345243,
        "lo": 1.843125,
        "hi": 1.9885714285714284
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 1.3992857142857142,
        "se": 0.033539570846018496,
        "lo": 1.334189732142857,
        "hi": 1.4662566964285715
      },
      "ipw_identified": false
    }
  },
  "DV": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.0085714285714285,
        "se": 0.02644350780902908,
        "lo": 2.9544642857142853,
        "hi": 3.0583928571428567
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 2.7924107142857144,
        "se": 0.06595528350789429,
        "lo": 2.662767857142857,
        "hi": 2.923138392857143
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 3.457232142857143,
        "se": 0.056017377819675876,
        "lo": 3.3490111607142854,
        "hi": 3.5667924107142848
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 3.405535714285714,
        "se": 0.05733063217589408,
        "lo": 3.2930357142857143,
        "hi": 3.516160714285714
      },
      "ipw_identified": false
    }
  },
  "CS": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.0,
        "se": 0.026687291559790896,
        "lo": 2.9485714285714284,
        "hi": 3.0533169642857145
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 2.15625,
        "se": 0.06801652016092886,
        "lo": 2.018551339285714,
        "hi": 2.2899174107142857
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 2.910535714285714,
        "se": 0.056647332388156224,
        "lo": 2.7961540178571425,
        "hi": 3.0270669642857144
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.8025892857142853,
        "se": 0.05256591992855339,
        "lo": 2.69625,
        "hi": 2.9035848214285713
      },
      "ipw_identified": false
    }
  },
  "BD": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 2.974017857142857,
        "se": 0.028083883906884922,
        "lo": 2.9188125,
        "hi": 3.030287946428571
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 4.24125,
        "se": 0.08534113500932523,
        "lo": 4.077026785714286,
        "hi": 4.413488839285714
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 4.579821428571428,
        "se": 0.07062261249106327,
        "lo": 4.442136160714285,
        "hi": 4.718886160714285
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 4.668482142857142,
        "se": 0.07288510706930589,
        "lo": 4.5313325892857135,
        "hi": 4.8182142857142845
      },
      "ipw_identified": false
    }
  },
  "AV2": {
    "none": {
      "probes_per_person_month": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "ipw_identified": false
    },
    "fixed": {
      "probes_per_person_month": {
        "point": 2.9464285714285707,
        "se": 8.884005476064869e-16,
        "lo": 2.9464285714285707,
        "hi": 2.9464285714285707
      },
      "ipw_identified": false
    },
    "random": {
      "probes_per_person_month": {
        "point": 3.0128571428571425,
        "se": 0.02650203796414578,
        "lo": 2.9622254464285716,
        "hi": 3.0634821428571426
      },
      "ipw_identified": true
    },
    "triggered": {
      "probes_per_person_month": {
        "point": 2.297410714285714,
        "se": 0.06957958913880682,
        "lo": 2.1645200892857144,
        "hi": 2.433220982142857
      },
      "ipw_identified": false
    },
    "mixed": {
      "probes_per_person_month": {
        "point": 3.0225,
        "se": 0.05925194457803059,
        "lo": 2.905707589285714,
        "hi": 3.138763392857143
      },
      "ipw_identified": true
    },
    "current": {
      "probes_per_person_month": {
        "point": 2.888035714285714,
        "se": 0.0516456613394442,
        "lo": 2.7873013392857144,
        "hi": 2.9954598214285713
      },
      "ipw_identified": false
    }
  }
}
```

## d_confirmation_rule_DR

```json
{
  "note": "Ground truth per flag: true iff it falls in [onset, onset+21); confirmed iff a probe in [t+1, t+7] is observed and reads >= 0.5 above the person's baseline-block probe mean (section 4's confirmation rule). Family DR, A-fixed.",
  "random": {
    "PPV_confirmed_flags": {
      "point": 0.1948608137044968,
      "se": 0.01707049824682061,
      "lo": 0.16166054842320765,
      "hi": 0.229259061393457
    },
    "confirmed_false_flags_per_person_month": {
      "point": 0.10071428571428571,
      "se": 0.00545292678885911,
      "lo": 0.09026116071428571,
      "hi": 0.11142857142857142
    },
    "mean_days_to_confirmation": {
      "point": 3.6766595289079227,
      "se": 0.08503610722804322,
      "lo": 3.509047266052455,
      "hi": 3.846686440677966
    },
    "ipw_identified": true,
    "n_flags_total": 1514,
    "n_confirmed_total": 467,
    "n_confirmed_true": 91,
    "n_confirmed_false": 376
  },
  "mixed": {
    "PPV_confirmed_flags": {
      "point": 0.21535893155258765,
      "se": 0.014289926854894315,
      "lo": 0.18696360127177739,
      "hi": 0.2433796476648054
    },
    "confirmed_false_flags_per_person_month": {
      "point": 0.12589285714285714,
      "se": 0.0064132656029639735,
      "lo": 0.11357142857142857,
      "hi": 0.1392857142857143
    },
    "mean_days_to_confirmation": {
      "point": 4.030050083472454,
      "se": 0.07796428057950931,
      "lo": 3.8844947960487364,
      "hi": 4.187734794648517
    },
    "ipw_identified": true,
    "n_flags_total": 1514,
    "n_confirmed_total": 599,
    "n_confirmed_true": 129,
    "n_confirmed_false": 470
  },
  "triggered": {
    "PPV_confirmed_flags": {
      "point": 0.22586872586872586,
      "se": 0.01636584356981693,
      "lo": 0.1938752191918815,
      "hi": 0.2580016129032258
    },
    "confirmed_false_flags_per_person_month": {
      "point": 0.10741071428571428,
      "se": 0.006093786283241662,
      "lo": 0.09616071428571428,
      "hi": 0.12000669642857138
    },
    "mean_days_to_confirmation": {
      "point": 4.3108108108108105,
      "se": 0.07503156740966188,
      "lo": 4.168626880984952,
      "hi": 4.462565196482307
    },
    "ipw_identified": false,
    "n_flags_total": 1514,
    "n_confirmed_total": 518,
    "n_confirmed_true": 117,
    "n_confirmed_false": 401
  }
}
```

## e_person_level_false_flag_rate_iqr

```json
{
  "S": {
    "point": 0.3225806451612903,
    "se": 0.024472773619688134,
    "lo": 0.3108855720971243,
    "hi": 0.32967032967032966
  },
  "VA": {
    "point": 0.3458299919807538,
    "se": 0.08188321867976155,
    "lo": 0.0,
    "hi": 0.3614457831325301
  },
  "SP": {
    "point": 0.32967032967032966,
    "se": 0.002537267724756287,
    "lo": 0.32608695652173914,
    "hi": 0.33707865168539325
  },
  "BI": {
    "point": 0.32967032967032966,
    "se": 0.0026252588423048284,
    "lo": 0.32608695652173914,
    "hi": 0.3333333333333333
  },
  "AV": {
    "point": 0.3488372093023256,
    "se": 0.006702723633759511,
    "lo": 0.34090909090909094,
    "hi": 0.36585365853658536
  },
  "DE": {
    "point": 0.0,
    "se": 0.009097163682761747,
    "lo": 0.0,
    "hi": 0.0
  },
  "CS": {
    "point": 0.3448275862068966,
    "se": 0.0028993223506162437,
    "lo": 0.34090909090909094,
    "hi": 0.3529411764705882
  }
}
```

## f_median_days_to_detect_among_detected

```json
{
  "DR": {
    "median_days_to_detect": {
      "point": 14.0,
      "se": 0.6170213591755469,
      "lo": 13.0,
      "hi": 15.0
    },
    "n_detected": 197
  },
  "DV": {
    "median_days_to_detect": {
      "point": 17.0,
      "se": 0.6308208184203151,
      "lo": 16.0,
      "hi": 18.0
    },
    "n_detected": 87
  },
  "BD": {
    "median_days_to_detect": {
      "point": 21.0,
      "se": 0.6018654820882028,
      "lo": 20.0,
      "hi": 23.0
    },
    "n_detected": 272
  }
}
```

## g_false_flags_per_total_vs_tracked_person_month

```json
{
  "S": {
    "fa_per_tracked_person_month": {
      "point": 0.1510476423869092,
      "se": 0.00954846412484073,
      "lo": 0.13231015706024113,
      "hi": 0.16924191078070075
    },
    "fa_per_total_person_month": {
      "point": 0.12107142857142857,
      "se": 0.007644130636989431,
      "lo": 0.10607142857142857,
      "hi": 0.1355424107142857
    }
  },
  "DR": {
    "fa_per_tracked_person_month": {
      "point": 0.5058773671179712,
      "se": 0.015183074713237276,
      "lo": 0.47661409017074036,
      "hi": 0.5349892515832487
    },
    "fa_per_total_person_month": {
      "point": 0.40499999999999997,
      "se": 0.012126186584778315,
      "lo": 0.38142187499999997,
      "hi": 0.4283035714285714
    }
  },
  "VA": {
    "fa_per_tracked_person_month": {
      "point": 0.1436489084945142,
      "se": 0.008525072019668603,
      "lo": 0.12645342865247153,
      "hi": 0.16032239814245422
    },
    "fa_per_total_person_month": {
      "point": 0.10205357142857142,
      "se": 0.006058590468722906,
      "lo": 0.08973214285714286,
      "hi": 0.11410714285714285
    }
  },
  "SP": {
    "fa_per_tracked_person_month": {
      "point": 0.17786561264822134,
      "se": 0.009993623614781665,
      "lo": 0.15922521628068467,
      "hi": 0.19794167855882877
    },
    "fa_per_total_person_month": {
      "point": 0.14223214285714286,
      "se": 0.007999316812638813,
      "lo": 0.12723214285714285,
      "hi": 0.15830357142857143
    }
  },
  "BI": {
    "fa_per_tracked_person_month": {
      "point": 0.17601612361437688,
      "se": 0.009650044933671683,
      "lo": 0.1572293715410578,
      "hi": 0.19513116501986774
    },
    "fa_per_total_person_month": {
      "point": 0.14035714285714285,
      "se": 0.00769340028256145,
      "lo": 0.12535714285714286,
      "hi": 0.1556316964285714
    }
  },
  "AV": {
    "fa_per_tracked_person_month": {
      "point": 0.198955127746368,
      "se": 0.010086639315089468,
      "lo": 0.17971092077790674,
      "hi": 0.21971463367987254
    },
    "fa_per_total_person_month": {
      "point": 0.1489285714285714,
      "se": 0.00761435188371177,
      "lo": 0.1344642857142857,
      "hi": 0.16420312499999998
    }
  },
  "DE": {
    "fa_per_tracked_person_month": {
      "point": 0.14910156747801706,
      "se": 0.01081378839954335,
      "lo": 0.12801419462697516,
      "hi": 0.17114295479332298
    },
    "fa_per_total_person_month": {
      "point": 0.073125,
      "se": 0.005342278499181218,
      "lo": 0.06294642857142857,
      "hi": 0.08383928571428571
    }
  },
  "DV": {
    "fa_per_tracked_person_month": {
      "point": 0.48654807874912953,
      "se": 0.015907674652970095,
      "lo": 0.4568924028063926,
      "hi": 0.5184288437270569
    },
    "fa_per_total_person_month": {
      "point": 0.343125,
      "se": 0.011240363425767258,
      "lo": 0.32223214285714286,
      "hi": 0.36589285714285713
    }
  },
  "CS": {
    "fa_per_tracked_person_month": {
      "point": 0.25879408215259464,
      "se": 0.011626195183998524,
      "lo": 0.23620510610661105,
      "hi": 0.2814085087430186
    },
    "fa_per_total_person_month": {
      "point": 0.20678571428571427,
      "se": 0.009303289141575686,
      "lo": 0.1888392857142857,
      "hi": 0.22499999999999998
    }
  },
  "BD": {
    "fa_per_tracked_person_month": {
      "point": 0.6800307887955557,
      "se": 0.018688103057875542,
      "lo": 0.6447339592296986,
      "hi": 0.7170641170598833
    },
    "fa_per_total_person_month": {
      "point": 0.5442857142857143,
      "se": 0.015026937338703087,
      "lo": 0.515625,
      "hi": 0.5740312499999999
    }
  },
  "AV2": {
    "fa_per_tracked_person_month": {
      "point": 0.2655164311369205,
      "se": 0.011835360071365533,
      "lo": 0.24309922590868357,
      "hi": 0.2898054435131933
    },
    "fa_per_total_person_month": {
      "point": 0.21187499999999998,
      "se": 0.009466507596281508,
      "lo": 0.19339285714285714,
      "hi": 0.23142857142857143
    }
  }
}
```

## h_chance_baseline_sensitivity_vs_observed

```json
{
  "note": "Chance rule: independent random flags on DR's own tracked days (per this architecture), at the per-day rate implied by that architecture's realized false-flag rate on S; simulated once per architecture (not a Poisson closed form).",
  "by_architecture": {
    "pop": {
      "realized_fa_per_tracked_person_month_on_S": 0.16207365161405307,
      "chance_sensitivity_within_21d": {
        "point": 0.077,
        "se": 0.008437808249422774,
        "lo": 0.06,
        "hi": 0.093
      },
      "observed_sensitivity_within_21d": {
        "point": 0.18,
        "se": 0.012163396641519567,
        "lo": 0.157,
        "hi": 0.204
      }
    },
    "A-naive": {
      "realized_fa_per_tracked_person_month_on_S": 0.15505602958540335,
      "chance_sensitivity_within_21d": {
        "point": 0.063,
        "se": 0.007570457295423501,
        "lo": 0.048975000000000005,
        "hi": 0.078
      },
      "observed_sensitivity_within_21d": {
        "point": 0.154,
        "se": 0.01152396974524598,
        "lo": 0.132975,
        "hi": 0.178
      }
    },
    "A-fixed": {
      "realized_fa_per_tracked_person_month_on_S": 0.1510476423869092,
      "chance_sensitivity_within_21d": {
        "point": 0.053,
        "se": 0.007040973203458874,
        "lo": 0.039,
        "hi": 0.067
      },
      "observed_sensitivity_within_21d": {
        "point": 0.197,
        "se": 0.012532532941946353,
        "lo": 0.173,
        "hi": 0.222
      }
    },
    "A-fixed-minus-i": {
      "realized_fa_per_tracked_person_month_on_S": 0.15739699018635891,
      "chance_sensitivity_within_21d": {
        "point": 0.065,
        "se": 0.007720339229522849,
        "lo": 0.05,
        "hi": 0.08
      },
      "observed_sensitivity_within_21d": {
        "point": 0.193,
        "se": 0.012512960604570997,
        "lo": 0.169,
        "hi": 0.218
      }
    },
    "A-fixed-minus-ii": {
      "realized_fa_per_tracked_person_month_on_S": 0.1510476423869092,
      "chance_sensitivity_within_21d": {
        "point": 0.081,
        "se": 0.008786124159085702,
        "lo": 0.064,
        "hi": 0.098
      },
      "observed_sensitivity_within_21d": {
        "point": 0.144,
        "se": 0.011015527616702577,
        "lo": 0.124,
        "hi": 0.166
      }
    },
    "A-fixed-minus-iii": {
      "realized_fa_per_tracked_person_month_on_S": 0.15572610918650373,
      "chance_sensitivity_within_21d": {
        "point": 0.061,
        "se": 0.007504705144084598,
        "lo": 0.047,
        "hi": 0.07502499999999986
      },
      "observed_sensitivity_within_21d": {
        "point": 0.184,
        "se": 0.012221355101225689,
        "lo": 0.16,
        "hi": 0.208
      }
    },
    "A-fixed-minus-iv": {
      "realized_fa_per_tracked_person_month_on_S": 0.1510476423869092,
      "chance_sensitivity_within_21d": {
        "point": 0.076,
        "se": 0.008408576087894606,
        "lo": 0.06,
        "hi": 0.093
      },
      "observed_sensitivity_within_21d": {
        "point": 0.197,
        "se": 0.012532532941946353,
        "lo": 0.173,
        "hi": 0.222
      }
    },
    "A-fixed-minus-v": {
      "realized_fa_per_tracked_person_month_on_S": 0.15104595985474636,
      "chance_sensitivity_within_21d": {
        "point": 0.064,
        "se": 0.007641594858797016,
        "lo": 0.05,
        "hi": 0.079
      },
      "observed_sensitivity_within_21d": {
        "point": 0.196,
        "se": 0.012532591538677772,
        "lo": 0.172,
        "hi": 0.221
      }
    },
    "probe-only": {
      "realized_fa_per_tracked_person_month_on_S": 0.1791549295774648,
      "chance_sensitivity_within_21d": {
        "point": 0.015,
        "se": 0.003921654936212436,
        "lo": 0.008,
        "hi": 0.023
      },
      "observed_sensitivity_within_21d": {
        "point": 0.019,
        "se": 0.004218515489656075,
        "lo": 0.011,
        "hi": 0.028
      }
    }
  }
}
```

## i_realized_false_flags_on_S_by_architecture

```json
{
  "pop": {
    "fa_per_tracked_person_month": {
      "point": 0.16207365161405307,
      "se": 0.00726416988369409,
      "lo": 0.14778045796812003,
      "hi": 0.17605263686789385
    },
    "fa_per_total_person_month": {
      "point": 0.12991071428571427,
      "se": 0.005818600599259155,
      "lo": 0.11839285714285713,
      "hi": 0.14116071428571428
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3333333333333333,
      "se": 0.0019988472379523273,
      "lo": 0.32967032967032966,
      "hi": 0.3333333333333333
    }
  },
  "A-naive": {
    "fa_per_tracked_person_month": {
      "point": 0.15505602958540335,
      "se": 0.009876668858864075,
      "lo": 0.13541495026272182,
      "hi": 0.17336010822443612
    },
    "fa_per_total_person_month": {
      "point": 0.12428571428571428,
      "se": 0.007918677106140314,
      "lo": 0.10874330357142857,
      "hi": 0.13901785714285714
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.04287819050451975,
      "lo": 0.3068916999789607,
      "hi": 0.32967032967032966
    }
  },
  "A-fixed": {
    "fa_per_tracked_person_month": {
      "point": 0.1510476423869092,
      "se": 0.00954846412484073,
      "lo": 0.13231015706024113,
      "hi": 0.16924191078070075
    },
    "fa_per_total_person_month": {
      "point": 0.12107142857142857,
      "se": 0.007644130636989431,
      "lo": 0.10607142857142857,
      "hi": 0.1355424107142857
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.024472773619688134,
      "lo": 0.3108855720971243,
      "hi": 0.32967032967032966
    }
  },
  "A-fixed-minus-i": {
    "fa_per_tracked_person_month": {
      "point": 0.15739699018635891,
      "se": 0.009889605012113585,
      "lo": 0.13798793131110137,
      "hi": 0.1766917599747897
    },
    "fa_per_total_person_month": {
      "point": 0.1261607142857143,
      "se": 0.007920366852692253,
      "lo": 0.110625,
      "hi": 0.14169642857142856
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.008178001889973745,
      "lo": 0.31578947368421056,
      "hi": 0.32967032967032966
    }
  },
  "A-fixed-minus-ii": {
    "fa_per_tracked_person_month": {
      "point": 0.1510476423869092,
      "se": 0.009611688313030687,
      "lo": 0.132583919247726,
      "hi": 0.16932450142385375
    },
    "fa_per_total_person_month": {
      "point": 0.12107142857142857,
      "se": 0.007697422905623046,
      "lo": 0.10607142857142857,
      "hi": 0.1358035714285714
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.0509153424076432,
      "lo": 0.075,
      "hi": 0.32608695652173914
    }
  },
  "A-fixed-minus-iii": {
    "fa_per_tracked_person_month": {
      "point": 0.15572610918650373,
      "se": 0.009476794413907457,
      "lo": 0.13655596454150337,
      "hi": 0.1734246496417833
    },
    "fa_per_total_person_month": {
      "point": 0.12482142857142857,
      "se": 0.007585512508745775,
      "lo": 0.10955357142857143,
      "hi": 0.13901785714285714
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.0035969598533849107,
      "lo": 0.31578947368421056,
      "hi": 0.3305860805860806
    }
  },
  "A-fixed-minus-iv": {
    "fa_per_tracked_person_month": {
      "point": 0.1510476423869092,
      "se": 0.00954846412484073,
      "lo": 0.13231015706024113,
      "hi": 0.16924191078070075
    },
    "fa_per_total_person_month": {
      "point": 0.12107142857142857,
      "se": 0.007644130636989431,
      "lo": 0.10607142857142857,
      "hi": 0.1355424107142857
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.024472773619688134,
      "lo": 0.3108855720971243,
      "hi": 0.32967032967032966
    }
  },
  "A-fixed-minus-v": {
    "fa_per_tracked_person_month": {
      "point": 0.15104595985474636,
      "se": 0.009548124487614757,
      "lo": 0.13230864667236145,
      "hi": 0.16924007113124215
    },
    "fa_per_total_person_month": {
      "point": 0.12107142857142857,
      "se": 0.007644130636989431,
      "lo": 0.10607142857142857,
      "hi": 0.1355424107142857
    },
    "person_level_fa_rate_iqr": {
      "point": 0.3225806451612903,
      "se": 0.024472773619688134,
      "lo": 0.3108855720971243,
      "hi": 0.32967032967032966
    }
  },
  "probe-only": {
    "fa_per_tracked_person_month": {
      "point": 0.1791549295774648,
      "se": 0.03463976609997159,
      "lo": 0.11534455889595331,
      "hi": 0.24989797104968137
    },
    "fa_per_total_person_month": {
      "point": 0.014196428571428572,
      "se": 0.0027478103077034103,
      "lo": 0.009107142857142857,
      "hi": 0.01982142857142857
    },
    "person_level_fa_rate_iqr": {
      "point": 0.0,
      "se": 0.0,
      "lo": 0.0,
      "hi": 0.0
    }
  }
}
```

## j_p3_reset_cost

```json
{
  "computable": false,
  "reason": "not computable from the frozen panels: families are mutually exclusive scenario channels -- DR's av_day/av_logged are all-NaN/False (no version-change event is generated for the DR family) and AV's t0 is all-NaN (no drift onset is generated for the AV family), so no frozen panel has both a drift onset and a logged version change to measure the re-baseline window's sensitivity cost against."
}
```

## k_current_control_default_cell

```json
{
  "note": "Ordinary `current` schedule (probe when C_t > c*) on family S / A-fixed / default cell; reported without a threshold, per PREREG P4's own text.",
  "all_days": {
    "slope": {
      "point": 0.9304749233110137,
      "se": 0.007396286164540217,
      "lo": 0.9164760886983816,
      "hi": 0.9451462034887382
    },
    "corr": {
      "point": 0.4709082772906699,
      "se": 0.0031497176873031417,
      "lo": 0.46482534709628753,
      "hi": 0.4772074667781008
    }
  },
  "current": {
    "slope": {
      "point": 0.6937019665754508,
      "se": 0.0551821036744326,
      "lo": 0.5883364484193828,
      "hi": 0.8019046226017402
    },
    "corr": {
      "point": 0.19022645488603157,
      "se": 0.014595448636377942,
      "lo": 0.1623028997332941,
      "hi": 0.21935699014824792
    }
  },
  "ipw_identified": false
}
```

## l_pop_architecture

```json
{
  "DR_sensitivity_within_21d": {
    "point": 0.18,
    "se": 0.012163396641519567,
    "lo": 0.157,
    "hi": 0.204
  },
  "S_false_flags": {
    "fa_per_tracked_person_month": {
      "point": 0.16207365161405307,
      "se": 0.00726416988369409,
      "lo": 0.14778045796812003,
      "hi": 0.17605263686789385
    },
    "fa_per_total_person_month": {
      "point": 0.12991071428571427,
      "se": 0.005818600599259155,
      "lo": 0.11839285714285713,
      "hi": 0.14116071428571428
    }
  }
}
```

## m_kappa_0_3_vs_kappa_0_cell_DR

```json
{
  "DR_sensitivity_within_21d": {
    "kappa_0": {
      "point": 0.197,
      "se": 0.012532532941946353,
      "lo": 0.173,
      "hi": 0.222
    },
    "kappa_0_3": {
      "point": 0.168,
      "se": 0.011688778925806928,
      "lo": 0.145,
      "hi": 0.19
    }
  },
  "DR_false_flags": {
    "kappa_0": {
      "fa_per_tracked_person_month": {
        "point": 0.5058773671179712,
        "se": 0.015183074713237276,
        "lo": 0.47661409017074036,
        "hi": 0.5349892515832487
      },
      "fa_per_total_person_month": {
        "point": 0.40499999999999997,
        "se": 0.012126186584778315,
        "lo": 0.38142187499999997,
        "hi": 0.4283035714285714
      }
    },
    "kappa_0_3": {
      "fa_per_tracked_person_month": {
        "point": 0.49394622481466854,
        "se": 0.016452941206225095,
        "lo": 0.4624462936189516,
        "hi": 0.5259840018676388
      },
      "fa_per_total_person_month": {
        "point": 0.37955357142857143,
        "se": 0.012604922398039816,
        "lo": 0.3554397321428571,
        "hi": 0.4039352678571428
      }
    }
  },
  "DR_abstention_share": {
    "kappa_0": {
      "total_abstention_share": {
        "point": 0.19941071428571427,
        "se": 0.001159762662366436,
        "lo": 0.19713392857142858,
        "hi": 0.20161674107142857
      },
      "unused_day": {
        "point": 0.19934821428571428,
        "se": 0.001155652023329927,
        "lo": 0.19708035714285715,
        "hi": 0.20154486607142857
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 6.25e-05,
        "se": 3.635833443072919e-05,
        "lo": 0.0,
        "hi": 0.00014285714285714287
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    },
    "kappa_0_3": {
      "total_abstention_share": {
        "point": 0.23158928571428572,
        "se": 0.001315009243526787,
        "lo": 0.22904464285714285,
        "hi": 0.23426785714285714
      },
      "unused_day": {
        "point": 0.23142857142857143,
        "se": 0.001303747442744084,
        "lo": 0.22891941964285714,
        "hi": 0.23405379464285714
      },
      "no_usable_indicator": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      },
      "low_usage_abstain_v": {
        "point": 0.0001607142857142857,
        "se": 5.7446477115818816e-05,
        "lo": 6.25e-05,
        "hi": 0.00028571428571428574
      },
      "version_reset_hold_iv": {
        "point": 0.0,
        "se": 0.0,
        "lo": 0.0,
        "hi": 0.0
      }
    }
  }
}
```

## n_indicator5_validity_pi_rises_with_D

```json
{
  "note": "Person-averaged within-person correlation of indicator 5 (negative self-reference) with D, in the pi_rises_with_D cell, family S -- raw (X) and authorship-filtered (X_filtered, mixed with pi'); r(H5,D), the unmixed reference, is included for scale.",
  "raw_validity_corr_X5_D": {
    "point": -0.010712728545334381,
    "se": 0.0030957519136847592,
    "lo": -0.016470774081209845,
    "hi": -0.004510148150588703
  },
  "filtered_validity_corr_X5_D": {
    "point": 0.13847701088229314,
    "se": 0.0036817482100059717,
    "lo": 0.13114242632132359,
    "hi": 0.14574241014669617
  },
  "reference_unmixed_corr_H5_D": {
    "point": 0.339767520666182,
    "se": 0.0032729235675916556,
    "lo": 0.3334525556110852,
    "hi": 0.3461804366760646
  },
  "n_persons_raw": 1000,
  "n_persons_filtered": 1000
}
```

## o_analytic_attenuation_pilot_params

```json
{
  "note": "Att = (1 - E pi) / sqrt(E[(1-pi)^2] + E[pi^2] kappa + Var(pi) delta^2), pi ~ Beta(10 pi_bar, 10(1-pi_bar)); E[pi]/Var(pi) in closed form (E[pi]=pi_bar, Var(pi)=pi_bar(1-pi_bar)/11 since the Beta's a+b=10 always). Filtered substitutes pi' = 0.1 pi / (0.1 pi + 0.95 (1-pi)) throughout; pi' has no closed-form moments, so they are estimated from a 2,000,000-draw Monte Carlo integral (deterministic, seed 4) rather than simulated persons. Parameters are read from pilot/indicator4_params.json, not hard-coded.",
  "params": {
    "entry_level_main_thread": {
      "pi_bar": 0.8450399098564537,
      "kappa": 0.5472780043258888,
      "delta": 0.2744164005064454,
      "att_formula_raw": 0.23518370873879496,
      "att_formula_filtered": 0.8021988097678927
    },
    "day_level_main_thread": {
      "pi_bar": 0.8229027541216615,
      "kappa": 0.09840995564479449,
      "delta": 0.19624929309002312,
      "att_formula_raw": 0.5266783587329055,
      "att_formula_filtered": 0.9287631785034727
    }
  }
}
```
