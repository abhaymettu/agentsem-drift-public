"""REP2-003: generator means for the still single-draw observer-step results (OBSERVER-STEP-DIGEST.md section 2)
on REP-003's 200 populations (DESIGN STAGE, EXPLORATORY). SYNTHETIC ONLY: D is one invented, non-diagnostic
wellbeing/functioning state; no real data is read. Scores no prediction. Every imported file is unchanged; the
runtime patches are n3.SEED and f3.SEED (the population) and s3.apply_log (rule variants), per worker process.

    python3 sim/rep2_003.py [--workers N]          # -> sim/rep2_003.json
    python3 sim/rep2_003.py --smoke [--workers N]  # design seed + 2 populations -> /tmp/rep2_003_smoke.json

Quantities, populations, expectations: sim/REP2-003.md. Points only (no bootstrap), k 0.5, in-window persons.
"""

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import absorb_003 as a3
import decide_003 as d3
import drift_sim as ds
import fact_003 as f3
import hyb_003 as h3
import load_003 as l3
import net_003 as n3
import obs_003 as o3
import rep_003 as rp
import study003 as s3
import unlog_003 as u3

HERE = Path(__file__).parent
N, RHOS, DET, APPLY_LOG, r4 = s3.N, l3.RHOS, "A-k0.5", s3.apply_log, rp.r4
ALARMS = d3.alarms_fn(json.loads((HERE / "tuning_003.json").read_text()))
U5 = ("L1", "L1_step", "L1_did", "L2", "oracle")  # UNLOG-003's rules


def population(seed):
    """{quantity: point} for one population. Each block reproduces the named source lines with its float order."""
    n3.SEED = f3.SEED = seed
    assert ds.REBASELINE_WINDOW == 14
    f, c = n3.drps_pair()
    t0 = f["t0"]
    w = (~np.isnan(f["log_day"]) & (t0 >= f["cday"]) & (t0 <= f["cday"] + 13)) * 1.0
    pt = lambda x: s3.ratio(x * w, w)(np.arange(N))  # s3.boot's point (est) on in-window persons
    XrC = s3.zscores(c, 28)[3]
    rules = {"L0": (APPLY_LOG, "L0"), "L1": (APPLY_LOG, "L1"), "L2": (APPLY_LOG, "L2"),
             "oracle": (APPLY_LOG, "oracle"), "L1_step": (o3.step_rule(False), "L1"),
             "L1_did": (o3.step_rule(True), "L1"), "L1_bsd": (h3.RULES["L1_bsd"], "L1"),
             "L1_bothCF": (a3.l1_variant(mean_src=XrC, sd_src=XrC), "L1")}

    def sens(p, name, hz=63):
        s3.apply_log, base = rules[name]
        a = ALARMS(p, 28, DET, base)[0]
        return ds._sensitivity(a, t0, window=hz, exclude_pre_onset_alarms=False).astype(float)

    q = {"n_inwin": int(w.sum())}
    try:
        Sc = {k: sens(c, k) for k in ("L1", "L1_step", "L1_did", "L1_bsd", "L1_bothCF", "L2", "oracle")}
        # FACT-003: fact_003.py main() lines 81-88, W 14, rule L0, 21 d: interaction F - C - O + N.
        P = f3.arms()
        assert np.array_equal(P["F"]["t0"], t0) and np.array_equal(P["F"]["X"], f["X"], equal_nan=True)
        s = {a: sens(P[a], "L0", 21) for a in "FCON"}
        q["fact_L0_interaction_h21"] = pt(s["F"] - s["C"] - s["O"] + s["N"])
        # ABSORB-003: absorb_003.py main() lines 105-121, W 14: net = share(sf - sc); difference of shares.
        Sf = {k: sens(f, k) for k in ("L1", "L1_bothCF")}
        dd = {k: Sf[k] - Sc[k] for k in Sf}
        q["absorb_L1_dd"], q["absorb_L1_bothCF_dd"] = pt(dd["L1"]), pt(dd["L1_bothCF"])
        q["absorb_L1_bothCF_minus_L1_dd"] = pt(dd["L1_bothCF"]) - pt(dd["L1"])
        # OBS-003 / LOAD-003: load_003.py main() lines 66-96 (c alarms reused across rho; rho 1 is f, OBS-003's
        # obs_003.py lines 97-114). HYB-003 part A: hyb_003.py main() lines 115-118 and pairs() lines 80-86.
        # rep_003's U(1, 0) (L1_step - L1) is kept for the cross-check against rep_003.json.
        for rho in RHOS:
            v = l3.scaled(f, c, rho)
            dd = {k: sens(v, k) - Sc[k] for k in ("L1", "L1_step", "L1_did", "L1_bsd")}
            q[f"load_L1_did_minus_L1_dd_rho{rho}"] = pt(dd["L1_did"]) - pt(dd["L1"])
            q[f"hyb_step3_dd_rho{rho}"] = pt(dd["L1_step"]) - pt(dd["L1_bsd"])
            q[f"xcheck_L1_step_minus_L1_dd_rho{rho}"] = pt(dd["L1_step"]) - pt(dd["L1"])
        # HYB-003 part 0: hyb_003.py main() line 112, pairs() on the no-change shares.
        q["hyb_step3_nochange"] = pt(Sc["L1_step"]) - pt(Sc["L1_bsd"])
        # UNLOG-003: unlog_003.py main() lines 78-107, `conc0.5`: added = share(shifted - no-shift).
        cq = u3.unlogged(c, *u3.ARMS["conc0.5"])
        for k in U5:
            q[f"unlog_conc0.5_added_{k}"] = pt(sens(cq, k) - Sc[k])
    finally:
        s3.apply_log = APPLY_LOG
    return {k: v if k == "n_inwin" else r4(v) for k, v in q.items()}


def timed(seed):
    t = time.time()
    return population(seed), time.time() - t


def check_design(d):
    """The design seed reproduces each source JSON's point (est) to 1e-4; returns the number of values checked."""
    j = {x: json.loads((HERE / f"{x}_003.json").read_text()) for x in ("fact", "absorb", "load", "obs", "unlog", "hyb")}
    ab, un = j["absorb"][f"W14_{DET}"], j["unlog"]["conc0.5"][DET]
    ref = {"fact_L0_interaction_h21": j["fact"][f"W14_{DET}"]["L0_interaction"]["est"],
           "absorb_L1_dd": ab["L1_h63"]["net"]["est"], "absorb_L1_bothCF_dd": ab["L1_bothCF_h63"]["net"]["est"],
           "absorb_L1_bothCF_minus_L1_dd": ab["L1_bothCF_minus_L1_net_h63"]["est"],
           "hyb_step3_nochange": j["hyb"]["0_nochange"][f"{DET}_L1_step_minus_L1_bsd_h63"]["share"]["est"],
           **{f"unlog_conc0.5_added_{k}": un[f"{k}_h63"]["added"]["est"] for k in U5}}
    for rho in RHOS:
        ref[f"load_L1_did_minus_L1_dd_rho{rho}"] = j["load"][f"rho{rho}"][DET]["L1_did_minus_L1_h63"]["est"]
        ref[f"hyb_step3_dd_rho{rho}"] = j["hyb"][f"A_rho{rho}"][f"{DET}_L1_step_minus_L1_bsd_h63"]["dd"]["est"]
    assert ref["load_L1_did_minus_L1_dd_rho1.0"] == j["obs"][f"W14_{DET}"]["L1_did_minus_L1_inwin_h63"]["est"]
    assert d["n_inwin"] == j["fact"]["n_inwin"] == j["hyb"]["n_inwin"]
    for k, v in ref.items():
        assert abs(d[k] - v) <= 1e-4 + 1e-9, (k, d[k], v)
    return len(ref)


def summary(v, dv):
    """Across populations: v the per-population points, dv the design point."""
    v = np.array(v)
    m, sd = v.mean(), v.std(ddof=1)
    return dict(design=dv, mean=r4(m), sd=r4(sd), mcse=r4(sd / np.sqrt(len(v))),
                design_side=None if dv == 0 else r4((np.sign(v) == np.sign(dv)).mean()),
                design_pct=r4(((v < dv).sum() + 0.5 * (v == dv).sum()) / len(v)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    seeds = rp.SEEDS[:2] if a.smoke else rp.SEEDS
    t = time.time()
    with Pool(a.workers) as pool:
        (design, td), *res = pool.map(timed, [s3.DESIGN_SEED] + seeds)
    wall = time.time() - t
    reps = [p for p, _ in res]
    n_checked = check_design(design)
    keys = [k for k in design if k != "n_inwin"]
    per_pop = {k: [p[k] for p in reps] for k in ["n_inwin"] + keys}
    out = dict(label="DESIGN STAGE, EXPLORATORY, SYNTHETIC: scores no prediction", R=len(seeds), seeds=seeds,
               design_seed=s3.DESIGN_SEED, design=design, design_values_checked=n_checked,
               summary={k: summary(per_pop[k], design[k]) for k in keys}, per_population=per_pop)
    rep = HERE / "rep_003.json"
    if not a.smoke and rep.exists():  # same quantities, same populations: means must match rep_003.json
        rs = json.loads(rep.read_text())["summary"]
        x = {f"rho{rho}": (out["summary"][f"xcheck_L1_step_minus_L1_dd_rho{rho}"]["mean"],
                           rs[f"rho{rho}_conc0.5_{DET}_h63"]["U_w1_p0.0"]["mean"]) for rho in RHOS}
        x["did_minus_step_added"] = (r4(np.mean(per_pop["unlog_conc0.5_added_L1_did"])
                                        - np.mean(per_pop["unlog_conc0.5_added_L1_step"])),
                                     rs[f"conc0.5_{DET}_h63"]["did_minus_step_added"]["mean"])
        assert all(abs(m - r) <= 1e-3 for m, r in x.values()), x
        out["rep_003_crosscheck"] = x
    out["sha256"] = {x: s3.sha256(HERE / x) for x in (
        "REP2-003.md", "rep2_003.py", "rep_003.py", "fact_003.py", "absorb_003.py", "obs_003.py", "load_003.py",
        "unlog_003.py", "hyb_003.py", "study003.py", "decide_003.py", "net_003.py", "attribution.py",
        "drift_sim.py", "tuning_003.json", "fact_003.json", "absorb_003.json", "obs_003.json", "load_003.json",
        "unlog_003.json", "hyb_003.json")}
    dest = Path("/tmp/rep2_003_smoke.json") if a.smoke else HERE / "rep2_003.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    secs = [td] + [s for _, s in res]
    print(f"design values checked: {n_checked}, all within 1e-4; wrote {dest}")
    print(f"wall {wall:.1f} s with {a.workers} workers; per population {min(secs):.1f} to {max(secs):.1f} s "
          f"(mean {np.mean(secs):.1f}); full run ~ {201 * np.mean(secs) / 8 / 60:.1f} min at 8 workers")


if __name__ == "__main__":
    main()
