"""Replication of the observer-step claims (STEP-003, UNLOG-003, BREAK-003) on fresh synthetic populations
(DESIGN STAGE, EXPLORATORY). SYNTHETIC ONLY: D is one invented, non-diagnostic wellbeing/functioning state; no
real data is read. Scores no prediction. Imports break_003.py's dependencies unchanged; the runtime patches are
n3.SEED (the population) and s3.apply_log (rule variants), both per worker process.

    python3 sim/rep_003.py      # -> sim/rep_003.json

Claims, seeds, calibration checks and expectations: sim/REP-003.md.
"""

import hashlib
import json
from itertools import product
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import absorb_003 as a3
import decide_003 as d3
import drift_sim as ds
import load_003 as l3
import net_003 as n3
import obs_003 as o3
import step_003 as st3
import study003 as s3
import unlog_003 as u3

HERE = Path(__file__).parent
N, HZ, DETS, SHIFTS, DARMS, RHOS = s3.N, a3.HZ, st3.DETS, st3.SHIFTS, st3.DARMS, l3.RHOS
APPLY_LOG = s3.apply_log
RULES = {"L1": APPLY_LOG, "L1_step": o3.step_rule(False), "L1_did": o3.step_rule(True)}
WS = (1, 2, 4)
r4 = lambda x: round(float(x), 4)
R = 200
SEEDS = [int(hashlib.sha256(f"rep003:{r}".encode()).hexdigest()[:8], 16) for r in range(R)]
assert len(set(SEEDS)) == R and not {s3.DESIGN_SEED, ds.TUNING_SEED, d3.CHECK_SEED} & set(SEEDS)


def population(seed):
    """{cell: {key: (est, se, lo, hi)}} for one population, its own resample matrix, in-window persons."""
    n3.SEED = seed
    f, c = n3.drps_pair()
    alarms = d3.alarms_fn(json.loads((HERE / "tuning_003.json").read_text()))
    brng = np.random.default_rng([seed, 99]).integers(0, N, (s3.NBOOT, N))
    t0 = f["t0"]
    w = (~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)) * 1.0
    den, denb = w.sum(), w[brng].sum(1)
    assert denb.min() > 0
    sh = lambda x: ((x * w).sum() / den, (x * w)[brng].sum(1) / denb)  # (point, bootstrap) share
    summ = lambda e, b: (r4(e), r4(b.std(ddof=1)), r4(np.percentile(b, 2.5)), r4(np.percentile(b, 97.5)))

    def ind(p, rules):
        out = {}
        for det, name in product(DETS, rules):
            s3.apply_log = RULES[name]
            a = alarms(p, 28, det, "L1")[0]
            for hz in HZ:
                out[(det, name, hz)] = ds._sensitivity(a, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)
        return out

    out = {"n_inwin": int(den)}
    try:
        Ic = ind(c, RULES)
        Icq = {arm: ind(u3.unlogged(c, *SHIFTS[arm]), RULES) for arm in DARMS}
        for arm, det, hz in product(DARMS, DETS, HZ):
            k = lambda n: (det, n, hz)
            x = (Icq[arm][k("L1_did")] - Ic[k("L1_did")]) - (Icq[arm][k("L1_step")] - Ic[k("L1_step")])
            out[f"{arm}_{det}_h{hz}"] = {"did_minus_step_added": summ(*sh(x))}
        for rho in RHOS:
            fr = l3.scaled(f, c, rho)
            If = ind(fr, ("L1", "L1_step"))
            for arm in DARMS:
                Ifq = ind(u3.unlogged(fr, *SHIFTS[arm]), ("L1", "L1_step"))
                for det, hz in product(DETS, HZ):
                    k = lambda n: (det, n, hz)
                    # share(L1_step) - share(L1), break_003's float order (it decides p*'s ties at u0 = 0)
                    T0, F0, Ts, Fs = ([a - b for a, b in zip(sh(I[k("L1_step")]), sh(I[k("L1")]))]
                                      for I in (If, Ic, Ifq, Icq[arm]))
                    e = {"T0": summ(*T0), "F0": summ(*F0), "Ts": summ(*Ts), "Fs": summ(*Fs)}
                    for wt in WS:
                        u0 = [a - wt * b for a, b in zip(T0, F0)]  # (point, bootstrap) U at p 0
                        u1 = [a - wt * b for a, b in zip(Ts, Fs)]  # U at p 1
                        e[f"U_w{wt}_p0.0"], e[f"U_w{wt}_p1.0"] = summ(*u0), summ(*u1)
                        # BREAK-003's p*: 0 if behind at p 0, 1 if never behind on [0, 1], else the crossing
                        ps = [np.where(a <= 0, 0.0, np.where(b >= 0, 1.0, a / np.where(a - b == 0, 1, a - b)))
                              for a, b in zip(u0, u1)]
                        e[f"pstar_w{wt}"] = summ(*ps)
                    out[f"rho{rho}_{arm}_{det}_h{hz}"] = e
    finally:
        s3.apply_log = APPLY_LOG
    return out


def check_design(d):
    """The design population reproduces break_003.json and unlog_003.json (vectorized float order: 1e-4)."""
    brk, unl = (json.loads((HERE / x).read_text()) for x in ("break_003.json", "unlog_003.json"))
    assert d["n_inwin"] == brk["n_inwin"] == unl["n_inwin"]
    near = lambda a, b: all(abs(x - b[y]) <= 1e-4 + 1e-9 for x, y in zip(a, ("est", "se", "lo", "hi")))
    n = 0
    for rho, arm, det, hz in product(RHOS, DARMS, DETS, HZ):
        ref, mine = brk[f"rho{rho}"][f"{arm}_{det}_h{hz}"], d[f"rho{rho}_{arm}_{det}_h{hz}"]
        for key, v in mine.items():
            assert near(v, ref[key]), (rho, arm, det, hz, key, v, ref[key])
            n += 1
    for arm, det, hz in product(("conc0.5", "post0.5"), DETS, HZ):
        assert near(d[f"{arm}_{det}_h{hz}"]["did_minus_step_added"], unl[arm][det][f"L1_did_minus_L1_step_added_h{hz}"])
        n += 1
    return n


def claims(p):
    """The fixed claims (REP-003.md) for one population, k 0.5, 63 d, in-window. est = [0], lo = [2], hi = [3]."""
    g = lambda rho, arm, key: p[f"rho{rho}_{arm}_A-k0.5_h63"][key]
    mono = lambda arm, key: all(g(a, arm, key)[0] < g(b, arm, key)[0] for a, b in zip(RHOS, RHOS[1:]))
    nondec = lambda arm, key: all(g(a, arm, key)[0] <= g(b, arm, key)[0] for a, b in zip(RHOS, RHOS[1:]))
    return {
        "C1_dep_increases_in_rho": mono("conc0.5", "U_w1_p0.0"),
        "C2_dep_lo_gt0_rho1_rho2": all(g(r, "conc0.5", "U_w1_p0.0")[2] > 0 for r in (1.0, 2.0)),
        "C3_did_minus_step_added_lo_gt0": p["conc0.5_A-k0.5_h63"]["did_minus_step_added"][2] > 0,
        "C4a_U11_ge0_rho_ge0.5": all(g(r, "conc0.5", "U_w1_p1.0")[0] >= 0 for r in (0.5, 1.0, 2.0)),
        "C4b_U11_lo_gt0_rho1_rho2": all(g(r, "conc0.5", "U_w1_p1.0")[2] > 0 for r in (1.0, 2.0)),
        "C4c_U11_lt0_rho0": g(0.0, "conc0.5", "U_w1_p1.0")[0] < 0,
        "C5_U21_lt0_every_rho": all(g(r, "conc0.5", "U_w2_p1.0")[0] < 0 for r in RHOS),
        "C6_pstar2_pstar4_nondecreasing": nondec("conc0.5", "pstar_w2") and nondec("conc0.5", "pstar_w4"),
        "C7a_neg_U11_lt0_rho0_rho0.5": all(g(r, "conc-0.5", "U_w1_p1.0")[0] < 0 for r in (0.0, 0.5)),
        "C7b_neg_U21_U41_gt0_every_rho": all(g(r, "conc-0.5", f"U_w{x}_p1.0")[0] > 0 for r in RHOS for x in (2, 4)),
        "C8_post_U_ge0_every_rho_w": all(g(r, "post0.5", f"U_w{x}_p1.0")[0] >= 0 for r in RHOS for x in WS),
    }


def stats(a, dv):
    """Across populations: a is R x (est, se, lo, hi), dv the design point."""
    est, m, se = a[:, 0], a[:, 0].mean(), a[:, 1].mean()
    sd = est.std(ddof=1)
    return dict(design=dv, mean=r4(m), mcse=r4(sd / np.sqrt(R)), sd=r4(sd), mean_se=r4(se),
                sd_over_se=r4(sd / se) if se > 0 else None, coverage=r4(((a[:, 2] <= m) & (m <= a[:, 3])).mean()),
                est_gt0=r4((est > 0).mean()), lo_gt0=r4((a[:, 2] > 0).mean()), hi_lt0=r4((a[:, 3] < 0).mean()),
                q05=r4(np.percentile(est, 5)), q50=r4(np.percentile(est, 50)), q95=r4(np.percentile(est, 95)),
                design_pct=r4(((est < dv).sum() + 0.5 * (est == dv).sum()) / R))


def main():
    with Pool(10) as pool:
        design, *reps = pool.map(population, [s3.DESIGN_SEED] + SEEDS)
    n_checked = check_design(design)
    summary = {cell: {key: stats(np.array([p[cell][key] for p in reps]), dv[0]) for key, dv in keys.items()}
               for cell, keys in design.items() if cell != "n_inwin"}
    cl = [claims(p) for p in reps]
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", R=R, seeds=SEEDS,
               design_seed=s3.DESIGN_SEED, design_values_checked=n_checked,
               n_inwin=dict(design=design["n_inwin"], mean=r4(np.mean([p["n_inwin"] for p in reps])),
                            min=min(p["n_inwin"] for p in reps), max=max(p["n_inwin"] for p in reps)),
               claims={k: dict(design=claims(design)[k], share=r4(np.mean([c[k] for c in cl]))) for k in cl[0]},
               summary=summary,
               sha256={x: s3.sha256(HERE / x) for x in ("rep_003.py", "break_003.py", "step_003.py", "unlog_003.py",
                                                        "load_003.py", "obs_003.py", "absorb_003.py", "study003.py",
                                                        "decide_003.py", "net_003.py", "attribution.py",
                                                        "drift_sim.py", "tuning_003.json", "break_003.json",
                                                        "unlog_003.json")})
    (HERE / "rep_003.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
