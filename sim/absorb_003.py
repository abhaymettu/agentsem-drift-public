"""Why L1 plateaus on DR+PS: does the re-baseline over the hold absorb the D ramp? (DESIGN STAGE, EXPLORATORY)
SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no real data is read. Scores no
prediction. Imports study003.py, decide_003.py, net_003.py and drift_sim.py unchanged; the runtime patches are
s3.apply_log (L1 variants) and ds.REBASELINE_WINDOW, both restored.

    python3 sim/absorb_003.py      # -> sim/absorb_003.json

Variants, contrasts and expectations: sim/ABSORB-003.md.
"""

import json
from pathlib import Path

import numpy as np

import decide_003 as d3
import drift_sim as ds
import net_003 as n3
import study003 as s3

HERE = Path(__file__).parent
SEED, N, T = s3.DESIGN_SEED, s3.N, s3.T
APPLY_LOG = s3.apply_log
HZ = (21, 42, 63)


def windows(p):
    c, day = p["log_day"][:, None], np.arange(T)[None, :]
    return (day > c) & (day <= c + ds.REBASELINE_WINDOW), day > c + ds.REBASELINE_WINDOW


def hold_stats(p, src):
    """apply_log's re-baseline mean and SD per person and indicator, computed on `src` over p's hold days
    (per indicator, as apply_log, so the floating-point order is the same)."""
    hold = windows(p)[0] & p["used"][:, :T]
    m, sd = np.zeros((len(hold), s3.J)), np.ones((len(hold), s3.J))
    for j in range(s3.J):
        vals = np.where(hold, src[:, :, j], np.nan)
        cnt = (~np.isnan(vals)).sum(1)
        m[:, j] = np.where(cnt >= 2, np.nanmean(vals, 1), 0.0)
        sdj = np.nanstd(vals, 1, ddof=1)
        sd[:, j] = np.where((cnt >= 2) & (sdj > 1e-6), sdj, 1.0)
    return m, sd


def baseline(p):
    """The detector's own 28-day baseline fit (zscores' fit on the observed panel)."""
    X = p["X"][:, :T].copy()
    X[..., s3.J45] = p["X_filtered"][:, :T][..., s3.J45]
    return ds.fit_baseline(X, p["used"][:, :T], p["L_obs"][:, :T], 0, 28)


def l1_variant(mean_src=None, sd_src=None, sd_fixed=None):
    """L1, with the post-hold mean (and SD) estimated on another series over the same hold days, or a fixed SD.
    None = the panel's own series, i.e. L1 itself. Hold, reason 4 and the S reset are L1's."""
    def apply_log(p, z, usable, reason, Xr, rule, log_day=None, log_map=None):
        z, usable, reason, reset = APPLY_LOG(p, z, usable, reason, Xr, rule, log_day, log_map)
        m = hold_stats(p, Xr if mean_src is None else mean_src)[0]
        sd = sd_fixed if sd_fixed is not None else hold_stats(p, Xr if sd_src is None else sd_src)[1]
        znew = ds.safe_div(Xr - m[:, None], sd[:, None])
        return np.where(windows(p)[1][..., None] & usable, znew, z), usable, reason, reset
    return apply_log


def main():
    tun = json.loads((HERE / "tuning_003.json").read_text())
    net = json.loads((HERE / "net_003.json").read_text())
    brng = np.random.default_rng([SEED, 99]).integers(0, N, (s3.NBOOT, N))  # the design run's matrix
    alarms, (f, c) = d3.alarms_fn(tun), n3.drps_pair()
    bf, bc = baseline(f), baseline(c)
    assert f["log_exo"] and all(np.array_equal(bf[x], bc[x], equal_nan=True) for x in bf), "log not exogenous, or baselines differ"
    bsd = bf["sd"]
    t0, day = f["t0"], np.arange(T)[None, :]
    inwin = ~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)
    share = lambda x, w=inwin: s3.ratio(x * w, w * 1.0)
    diff = lambda x, y, wx=inwin, wy=inwin: lambda idx: share(x, wx)(idx) - share(y, wy)(idx)
    XrF, XrC = s3.zscores(f, 28)[3], s3.zscores(c, 28)[3]  # XrC: the re-baseline without the D ramp
    variants = {"L1": {}, "L1_meanCF": dict(mean_src=XrC), "L1_sdCF": dict(sd_src=XrC),
                "L1_bothCF": dict(mean_src=XrC, sd_src=XrC), "L1_sdB": dict(sd_fixed=bsd)}
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", seed=SEED,
               n_inwin=int(inwin.sum()),
               sha256={x: s3.sha256(HERE / x) for x in ("absorb_003.py", "study003.py", "decide_003.py",
                                                        "net_003.py", "drift_sim.py", "tuning_003.json",
                                                        "net_003.json")})
    w0 = ds.REBASELINE_WINDOW
    try:
        for W in (14, 21):
            ds.REBASELINE_WINDOW = W
            hold = windows(f)[0] & f["used"][:, :T]
            step = np.clip((day - t0[:, None]) / f["ramp"][:, None], 0, 1)
            absorbed = np.where(hold, step, 0).sum(1) / np.maximum(hold.sum(1), 1)  # D-step share in the hold mean
            cuts = np.quantile(absorbed[inwin], [1 / 3, 2 / 3])
            terc = [inwin & (absorbed <= cuts[0]), inwin & (absorbed > cuts[0]) & (absorbed <= cuts[1]),
                    inwin & (absorbed > cuts[1])]
            (mF, sF), (mC, sC) = hold_stats(f, XrF), hold_stats(c, XrC)
            out[f"W{W}_mechanism"] = dict(  # point values, in-window persons, all six indicators
                absorbed_share_mean=round(float(absorbed[inwin].mean()), 4),
                absorbed_share_tertile_cuts=[round(float(x), 4) for x in cuts],
                tertile_n=[int(x.sum()) for x in terc],
                hold_mean_shift_in_baseline_sd=round(float(np.mean(((mF - mC) / bsd)[inwin])), 4),
                hold_sd_ratio_F_over_CF_median=round(float(np.median((sF / sC)[inwin])), 4),
                hold_sd_over_baseline_sd_median_CF=round(float(np.median((sC / bsd)[inwin])), 4))
            for det in ("A-k0.5", "A-kstar"):
                r, S = {}, {}
                for name, kw in [*variants.items(), ("L0", None), ("oracle", None)]:
                    rule = "L1" if kw is not None else name
                    s3.apply_log = l1_variant(**kw) if kw is not None else APPLY_LOG
                    af, ac = (alarms(p, 28, det, rule)[0] for p in (f, c))
                    for hz in HZ:
                        sf, sc = (ds._sensitivity(a, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
                                  for a in (af, ac))
                        S[(name, hz)] = sf - sc
                        r[f"{name}_h{hz}"] = dict(raw=s3.boot(share(sf), N, brng), chance=s3.boot(share(sc), N, brng),
                                                  net=s3.boot(share(sf - sc), N, brng))
                    r[f"{name}_net_h63_by_absorbed_tertile"] = [s3.boot(share(S[(name, 63)], w), N, brng) for w in terc]
                    r[f"{name}_net_h63_top_minus_bottom_tertile"] = s3.boot(
                        diff(S[(name, 63)], S[(name, 63)], terc[2], terc[0]), N, brng)
                for hz in HZ:
                    for a, b in (("L1_bothCF", "L1"), ("L1_meanCF", "L1"), ("L1_sdCF", "L1"), ("L1_sdB", "L1"),
                                 ("oracle", "L1_bothCF"), ("oracle", "L1")):
                        r[f"{a}_minus_{b}_net_h{hz}"] = s3.boot(diff(S[(a, hz)], S[(b, hz)]), N, brng)
                    for name in ("L1", "L0", "oracle"):  # reproduction of net_003.json
                        ref = net[f"W{W}_{det}"][f"{name}_inwin_h{hz}"]
                        assert (r[f"{name}_h{hz}"]["raw"], r[f"{name}_h{hz}"]["chance"], r[f"{name}_h{hz}"]["net"]) == \
                            (ref["raw"], ref["chance"], ref["net"]), (W, det, name, hz)
                out[f"W{W}_{det}"] = r
    finally:
        ds.REBASELINE_WINDOW = w0
        s3.apply_log = APPLY_LOG
    (HERE / "absorb_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
