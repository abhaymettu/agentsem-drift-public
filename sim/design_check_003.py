"""DESIGN-STAGE check for spec 003 (not a result; no prediction is scored). Imports drift_sim.py
unchanged and patches its DELTA_D global per run. Seed 20261003 is a design seed: it is not the
tuning seed (20260927) and not a PREREG-derived evaluation seed. Output: sim/design_check_003.json.
Detection runs on days < T; D is generated for 3 * 29 more days and read only by confirmation probes, so
no confirmation is censored (Opus review r0, item 1). The h values mix sources: 0.7 is the frozen PREREG
h, 0.3 and 0.9 are robustness retunes. The cell is spec 001's default (constant help 0.3).

    python3 sim/design_check_003.py
"""

import json
from pathlib import Path

import numpy as np

import drift_sim as ds

SEED, N, T = 20261003, 1000, 210
T_GEN = T + 3 * 29  # confirmation-only tail
H = {0.3: 2.3535, 0.7: 3.334, 0.9: 4.8422}  # A-fixed h: robustness.json phi cells; frozen PREREG at 0.7
LAG = {0.3: 3, 0.7: 9, 0.9: 29}  # smallest L with phi^L < 0.05 (spec 001 s15)
VAR_E = 1 / 0.7 - 1  # probe error variance at reliability 0.7, Var(D) = 1
BASE_DAYS = np.array(ds.PROBE_BASELINE_DAYS)
M = 3  # confirmation probes per alarm
DELTAS = (0.5, 1.0, 1.5)
MARGIN = 0.5  # delta_min / 2


def confirm_share(rng, D, alarm_days, lag, margin):
    """Share of alarms confirmed: mean of M probes at a + lag*k (k = 1..M) minus the reference >= margin.
    Reference: the baseline-block probe mean; and (oracle, simulation only) the same block with the true
    baseline D replaced by the generator mean 0, probe noise kept, so the gap is baseline D error only."""
    out, oracle = [], []
    for i, a in alarm_days:
        days = a + lag * np.arange(1, M + 1)
        y = D[i, days] + rng.normal(0, np.sqrt(VAR_E), M)
        e_b = rng.normal(0, np.sqrt(VAR_E), len(BASE_DAYS))
        out.append(y.mean() - (D[i, BASE_DAYS] + e_b).mean() >= margin)
        oracle.append(y.mean() - e_b.mean() >= margin)
    return (float(np.mean(out)), float(np.mean(oracle))) if out else (None, None)


def run(delta, phi, family):
    ds.DELTA_D = delta
    rng = np.random.default_rng([SEED, int(delta * 100), int(phi * 10), family == "DR"])
    p = ds.generate_panel(rng, family, ds.cell_params("default"), n=N, T=T_GEN, phi_D=phi)
    base = ds.fit_baseline(p["X"], p["used"], p["L_obs"])
    C, _ = ds.compute_composite(p, ds.DEFAULT_FEATURES, baseline=base)
    alarm, _, _ = ds.run_cusum(C, H[phi])
    alarm[:, T:] = False  # detection ends at T
    day = np.arange(T_GEN)[None, :]
    r = {}
    if family == "DR":
        t0, hold = p["t0"], p["t0"] + p["ramp"]
        pre = (day >= ds.BASELINE_DAYS) & (day < t0[:, None])
        post = (day >= hold[:, None]) & (day < T)
        r["composite_shift"] = float(np.nanmean(
            np.nanmean(np.where(post, C, np.nan), 1) - np.nanmean(np.where(pre, C, np.nan), 1)))
        r["sens_21d"] = float(ds._sensitivity(alarm, t0, window=21).mean())
        clean = ~(alarm & (day < t0[:, None])).any(1)  # same persons as sens_21d's primary rule
        sel = alarm & (day >= t0[:, None]) & (day < t0[:, None] + 21) & clean[:, None]
    else:
        sel = alarm & (day >= ds.BASELINE_DAYS)
        who, bm = sel.any(1), p["D"][:, :ds.BASELINE_DAYS].mean(1)  # true D over the baseline window
        r["sd_baseline_mean_D"] = float(bm.std())
        r["baseline_mean_D_alarmed"], r["baseline_mean_D_not"] = float(bm[who].mean()), float(bm[~who].mean())
        pseudo_t0 = rng.integers(50, 101, N).astype(float)  # chance level, DR's onset law on S
        r["chance_sens_21d"] = float(ds._sensitivity(alarm, pseudo_t0, window=21).mean())
    first = [(i, int(np.argmax(sel[i]))) for i in np.where(sel.any(1))[0]]
    r["n_alarms"] = len(first)
    r["D_alarm_day"] = float(np.mean([p["D"][i, a] for i, a in first])) if first else None
    for name, lag in (("next_day", 1), ("spaced", LAG[phi])):
        r[f"confirm_{name}"], r[f"oracle_ref_{name}"] = confirm_share(rng, p["D"], first, lag, MARGIN)
    return r


def main():
    out = {"seed": SEED, "n": N, "T": T, "T_gen": T_GEN, "h": H, "lag": LAG, "m": M, "margin": MARGIN, "cells": {}}
    for phi in (0.3, 0.7, 0.9):
        out["cells"][f"S_phi{phi}"] = run(0.0, phi, "S")
        for delta in DELTAS:
            out["cells"][f"DR_d{delta}_phi{phi}"] = run(delta, phi, "DR")
    Path(__file__).with_name("design_check_003.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
