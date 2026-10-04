"""EXPLORATORY post-freeze sensitivity analysis (sim/SENS-BASELINE-PLAN.md). Not part of sim/PREREG.md.

Spec 001 section 18.1: A-fixed fits the baseline of indicators 4 and 5 on the unfiltered X and scores them
on X_filtered. This reruns the frozen score() on the frozen evaluation seeds under three variants:
  M0  as run (must reproduce sim/results.json byte for byte);
  M1  matched baseline, every h and schedule re-tuned by the frozen procedure on the tuning seed;
  M2  matched baseline, frozen h and schedules.
drift_sim.py is imported unchanged. The variant is one wrapper around compute_composite. score()'s own
writes go to a temporary directory, so sim/results.json, sim/RESULTS.md and sim/tuning.json are never
written.

    python3 sim/sens_baseline.py --check
    python3 sim/sens_baseline.py --plan-sha <sha256 of sim/SENS-BASELINE-PLAN.md>
"""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

import drift_sim as ds

HERE = Path(__file__).parent
PLAN_PATH = HERE / "SENS-BASELINE-PLAN.md"
PREREG_SHA = "60db6dd195942387e5572a640224c4cb13836f29c37c1b611b14c70598678f17"
J45 = [ds.IDX_MSGLEN, ds.IDX_NEGSELF]
FROZEN_CC = ds.compute_composite
UNFILTERED_ARCHS = ["pop", "A-naive", "A-fixed-minus-ii", "probe-only"]


def matched_cc(panel, features, baseline=None, pop_ref=None):
    """compute_composite with indicators 4 and 5 standardized on the series they are scored on."""
    if features["authorship_filter"] and baseline is not None:
        fb = ds.fit_baseline(panel["X_filtered"], panel["used"], panel["L_obs"])
        baseline = dict(baseline, mean=baseline["mean"].copy(), sd=baseline["sd"].copy())
        baseline["mean"][:, J45] = fb["mean"][:, J45]
        baseline["sd"][:, J45] = fb["sd"][:, J45]
    return FROZEN_CC(panel, features, baseline, pop_ref)


def retune(cc, pi_bar, kappa_a4, mu_m4):
    """The frozen tuning procedure (run_tune without its write) under composite `cc`."""
    ds.compute_composite = cc
    try:
        kw = dict(pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)
        H = {a: ds.tune_h(a, **kw) for a in ds.ARCHS_FOR_H}
        return H, ds.tune_schedules(**kw)
    finally:
        ds.compute_composite = FROZEN_CC


def score_variant(cc, H, P, frozen):
    """score() on the frozen evaluation seeds with composite `cc` and tuning (H, P). Returns its
    predictions and the bytes it would have written to sim/results.json."""
    load, here = ds._load_frozen, ds.HERE
    ds.compute_composite, ds._load_frozen = cc, (lambda action: (H, P, *frozen[2:]))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ds.HERE = Path(tmp)
            res = ds.score(PREREG_SHA)
            return res["predictions"], (Path(tmp) / "results.json").read_bytes()
    finally:
        ds.compute_composite, ds._load_frozen, ds.HERE = FROZEN_CC, load, here


PRIMARY = ["P1.SP.PASS", "P1.VA.PASS", "P1.DE.PASS", "P1.BI.PASS"] + [
    f"{p}.PASS" for p in ("P1b", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10")]


def leaves(d, path=""):
    """Every non-container value in a JSON-like tree, flattened to path -> value."""
    items = d.items() if isinstance(d, dict) else enumerate(d) if isinstance(d, list) else None
    if items is None:
        return {path[:-1]: d}
    out = {}
    for k, v in items:
        out.update(leaves(v, f"{path}{k}."))
    return out


def leaf_diffs(a, b):
    """Paths where two prediction trees differ: |a - b| for numbers, [a, b] otherwise (NaN equals NaN)."""
    la, lb = leaves(json.loads(json.dumps(a, default=float))), leaves(json.loads(json.dumps(b, default=float)))
    out = {}
    for k in sorted(set(la) | set(lb)):
        x, y = la.get(k), lb.get(k)
        num = all(isinstance(z, (int, float)) and not isinstance(z, bool) for z in (x, y))
        if num and not (x == y or (np.isnan(x) and np.isnan(y))):
            out[k] = abs(x - y)
        elif not num and x != y:
            out[k] = [x, y]
    return out


def verdict_changes(base, other):
    """Booleans that differ, as path -> [base, other]."""
    return {k: v for k, v in leaf_diffs(base, other).items()
            if isinstance(v, list) and any(isinstance(z, bool) for z in v)}


def run(save):
    frozen = ds._load_frozen("score")
    H0, P0, pi_bar, kappa_a4, mu_m4 = frozen
    sched = ("p_trig", "p_trig2", "c_star")
    out = dict(label="EXPLORATORY post-freeze sensitivity (sim/SENS-BASELINE-PLAN.md); not sim/PREREG.md; "
                     "not a re-scoring; synthetic only", prereg_sha256=PREREG_SHA)

    # E0: the harness reproduces the frozen tuning and the frozen scoring.
    Hr, Pr = retune(FROZEN_CC, pi_bar, kappa_a4, mu_m4)
    out["E0a_retune_h_maxabs"] = max(abs(Hr[a]["h"] - H0[a]["h"]) for a in ds.ARCHS_FOR_H)
    out["E0a_retune_schedules_maxabs"] = max(abs(Pr[k] - P0[k]) for k in sched)
    m0, m0_bytes = score_variant(FROZEN_CC, H0, P0, frozen)
    out["E0b_M0_results_byte_identical"] = m0_bytes == (HERE / "results.json").read_bytes()
    out["E0b_M0_minus_committed"] = leaf_diffs(m0, json.loads((HERE / "results.json").read_text())["predictions"])
    out["predictions"] = dict(M0=m0)
    save(out)

    H1, P1 = retune(matched_cc, pi_bar, kappa_a4, mu_m4)
    out["E0c_unfiltered_archs_h_unchanged"] = all(H1[a]["h"] == Hr[a]["h"] for a in UNFILTERED_ARCHS)
    out["E0c_M1_schedules_use_M1_h"] = P1["h_fixed_used"] == H1["A-fixed"]["h"]
    out["tuning"] = dict(M0=dict(h={a: H0[a]["h"] for a in H0}, schedules=P0),
                         M1=dict(h={a: H1[a]["h"] for a in H1}, schedules=P1))
    out["predictions"]["M1"], _ = score_variant(matched_cc, H1, P1, frozen)
    save(out)
    out["predictions"]["M2"], _ = score_variant(matched_cc, H0, P0, frozen)
    for m in ("M1", "M2"):
        ch = verdict_changes(m0, out["predictions"][m])
        out[f"E4_primary_changes_{m}"] = {k: v for k, v in ch.items() if k in PRIMARY}
        out[f"component_changes_{m}"] = {k: v for k, v in ch.items() if k not in PRIMARY}
        out[f"E0d_P6_identical_{m}"] = not leaf_diffs(m0["P6"], out["predictions"][m]["P6"])
    out["E4_primary_keys_present"] = all(k in leaves(json.loads(json.dumps(m0, default=float))) for k in PRIMARY)
    save(out)
    return out


def check():
    p = ds.generate_panel(np.random.default_rng(7), "S", ds.cell_params("default"), n=200)
    base = ds.fit_baseline(p["X"], p["used"], p["L_obs"])
    # matched_cc equals rescoring with X's 4 and 5 replaced by X_filtered's (attribution r4's `matched`).
    q = dict(p, X=p["X"].copy())
    q["X"][:, :, J45] = p["X_filtered"][:, :, J45]
    Cq, rq = FROZEN_CC(q, ds.DEFAULT_FEATURES, baseline=ds.fit_baseline(q["X"], q["used"], q["L_obs"]))
    Cm, rm = matched_cc(p, ds.DEFAULT_FEATURES, baseline=base)
    assert np.array_equal(Cq, Cm, equal_nan=True) and np.array_equal(rq, rm), "matched_cc != r4 matched"
    # unchanged where the filter is off or the baseline is the population one; caller's baseline untouched
    before = {k: base[k].copy() for k in ("mean", "sd")}
    for f in (ds.NAIVE_FEATURES, ds.ablation_features("ii")):
        assert np.array_equal(matched_cc(p, f, baseline=base)[0], FROZEN_CC(p, f, baseline=base)[0], equal_nan=True)
    pop = ds.pop_reference(p)
    assert np.array_equal(matched_cc(p, ds.NAIVE_FEATURES, pop_ref=pop)[0],
                          FROZEN_CC(p, ds.NAIVE_FEATURES, pop_ref=pop)[0], equal_nan=True)
    assert all(np.array_equal(before[k], base[k]) for k in before), "matched_cc mutated the caller's baseline"
    # it differs where it should: A-fixed on the default (continuous) mixing
    assert not np.array_equal(Cm, FROZEN_CC(p, ds.DEFAULT_FEATURES, baseline=base)[0], equal_nan=True)
    print("check OK: matched_cc equals r4's matched rescoring; identical with the filter off and for pop; "
          "caller's baseline untouched; differs for A-fixed under default mixing")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-sha")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
    else:
        on_disk = hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()
        if on_disk != a.plan_sha:
            sys.exit(f"--plan-sha does not match sha256(sim/SENS-BASELINE-PLAN.md) = {on_disk}")
        def save(o):
            (HERE / "sens_baseline.json").write_text(json.dumps(dict(plan_sha256=a.plan_sha, **o), indent=2,
                                                                default=float) + "\n")
        out = run(save)
        print(json.dumps({k: out[k] for k in out if k[:2] in ("E0", "E4") or k.startswith("component")}, indent=1))
