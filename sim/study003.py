"""Spec 003 (DRAFT) generator and scorer: a sustained mean shift in D, spaced confirmation, and the policy
log as separator of person change from observer change. SYNTHETIC ONLY: D is one invented,
non-diagnostic wellbeing/functioning state; no condition is named; no real data is read.

    python3 sim/study003.py --check                    # bit-identity with drift_sim + known answers
    python3 sim/study003.py tune                       # tuning seed only -> sim/tuning_003.json
    python3 sim/study003.py design                     # design seed only -> sim/design_003.json
    python3 sim/study003.py score --prereg-sha <sha> [--n <int>]
                                                       # refuses unless sim/PREREG-003.md matches <sha> and
                                                       # lists the sha256 of study003.py and tuning_003.json;
                                                       # N_SCORE persons per cell unless --n is given
    python3 sim/study003.py verdicts <results.json>    # print the PREREG-003 verdicts of any results file

`design` sizes PREREG-003 (spec 003 section 11): it scores no prediction and its seed is neither the
tuning seed nor a PREREG-003 evaluation seed. Imports drift_sim.py and attribution.py unchanged.

Reimplemented, because a constant patch cannot express them (spec 003 section 4): event sampling (window
U[70, 120]), the usage step (PS-use's time-varying intercept, kappa < 0, change-dependent usage) and the
composite's per-indicator z-scores (L1 and L2 act per indicator). `--check` asserts each equals the frozen
code wherever the frozen code can express it. Every family draws its events from a side stream, so all
families in one (phi, cell) share the main stream: the same persons, paired across families and arms.
Interpretations of the DRAFT spec are flagged "CHOICE:".
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import attribution as at
import drift_sim as ds

HERE = Path(__file__).parent
PREREG_003 = HERE / "PREREG-003.md"
J = ds.N_IND
J45 = [ds.IDX_MSGLEN, ds.IDX_NEGSELF]
PS_MAP = (ds.IDX_LATE, ds.IDX_FRAG, ds.IDX_LATENCY)  # indicators 1, 2, 6
N, T, TAIL = 1000, 210, 87  # detection on days < T; D and probe answers run 3 x 29 more days
T_GEN = T + TAIL
ONSET = (70, 121)  # U[70, 120]
PHIS = (0.3, 0.7, 0.9)
DELTA_MIN, M_CONF = 1.0, 3
MARGIN = DELTA_MIN / 2
FA_TARGET = 1 / 6
ARMS = ((28, 4), (28, 8), (56, 4), (56, 8))  # (baseline days, baseline probes)
FIXED_LAG = 9
W_LABEL = (14, 28)
DESIGN_SEED = 20261003
NBOOT = 1000
N_SCORE = 4000  # PREREG-003 section 1 evaluation N (owner-delegated 2026-10-07); `design` keeps N

# Verdict table, from PREREG-003 sections 2 (H2a, H3) and 3 (H1a, H1b, H4, H5) only: (item, clause) -> (path in
# run_study's output, rule, threshold). An item holds only if all its clauses hold. A-fixed k = 0.5 throughout.
_CF, _PL = ("confirmation",), ("policy_log", "A-k0.5")
VERDICT_RULES = {
    ("H1a", None): (_CF + ("phi0.7_B28_m4_H1_S_spaced_minus_next_day",), "hi<=", -0.15),
    ("H1b", None): (_CF + ("phi0.7_B28_m4_H1_DR-1.0_spaced_over_next_day",), "lo>=", 0.70),
    ("H2a", None): (_CF + ("phi0.9_B28_m4_spaced", "S_gap_block_minus_oracle"), "lo>=", 0.10),
    **{("H3", f"{r}_{f}"): (_PL + (f, f"{r}_logged_ratio_to_S"), "lo>" if r == "L0" else "est<", 1.5)
       for r in ("L1", "L2", "L0") for f in ("PS-sub", "PS-use")},
    ("H4", None): (_PL + ("dr", "H4_L2_minus_L1_onset_in_window"), "lo>", 0.0),
    ("H5", "M1"): (_PL + ("H5_M1_DR_minus_unlogged_PSprop",), "inside", 0.10),
}
RULE_WORDS = {"hi<=": "95% interval lies at or below {}", "lo>=": "95% interval lies at or above {}",
              "lo>": "95% interval lies above {}", "est<": "point estimate below {}",
              "inside": "95% interval lies inside (-{0}, {0})"}
# Reported with scored: false (PREREG-003 sections 3 and 4): place in the verdicts -> path.
UNSCORED = {("H2b",): _CF + ("phi0.9_H2_gap_B28m4_minus_B56m4",),
            ("H5", "L0label"): _PL + ("H5_L0label_DR_minus_unlogged_PSprop",),  # true by construction
            ("H6", "DR-1.0"): ("detection", "phi0.7_B28_H6_DR-1.0_kstar_minus_k05"),
            ("H6", "DR-1.5"): ("detection", "phi0.7_B28_H6_DR-1.5_kstar_minus_k05"),
            ("H3", "L1_step", "PS-sub"): _PL + ("PS-sub", "L1_step_logged_ratio_to_S"),
            ("H3", "L1_step", "PS-use"): _PL + ("PS-use", "L1_step_logged_ratio_to_S"),
            ("H4", "L1_step"): _PL + ("dr", "H4_L2_minus_L1_step_onset_in_window")}

# family -> (frozen family whose mechanism it uses, delta_D)
FAMILY = {f: (f, 1.0 if f in ("DR", "DV", "BD") else 0.0) for f in ds.FAMILIES}
FAMILY.update({"DR-0.5": ("DR", 0.5), "DR-1.0": ("DR", 1.0), "DR-1.5": ("DR", 1.5), "DR+PS": ("DR", 1.0),
               "PS-sub": ("S", 0.0), "PS-use": ("S", 0.0), "PS-prop": ("S", 0.0), "PS-endo": ("S", 0.0)})
STEP_SHIFT = {"PS-sub", "PS-use", "PS-endo", "DR+PS"}  # +0.5 on indicators 1, 2, 6 from the change day
USE_SHIFT = {"PS-use", "PS-endo", "DR+PS"}  # usage intercept a0 + 0.5 (logit) from the change day


def lag_for(phi):
    """Smallest L with phi^L < 0.05 (spec 001 s15)."""
    return int(np.ceil(np.log(0.05) / np.log(phi) + 1e-12))


def probe_days(B, m):
    """m baseline probes evenly spaced inside [0, B), the last on day B - 1; (28, 4) is the frozen block.
    CHOICE (spec 003 s13 open item): (28, 8) -> 2, 6, 9, 13, 16, 20, 23, 27; (56, 4) -> 13, 27, 41, 55."""
    return np.array([(k + 1) * B // m - 1 for k in range(m)])


# ---------------------------------------------------------------------------------------------- generator
def sample_events(rng, family, n, lo=50, hi=101):
    """ds.sample_events with the event window U[lo, hi - 1] as a parameter. BD keeps U[10, 25]."""
    nan = lambda: np.full(n, np.nan)
    ev = dict(t0=nan(), ramp=nan(), vac_start=nan(), vac_len=nan(), sprint_start=nan(), sprint_len=nan(),
              bi_start=nan(), bi_len=nan(), av_day=nan(), av_logged=np.zeros(n, dtype=bool), cs_day=nan(),
              de_day=nan())
    if family in ("DR", "DV", "BD"):
        ev["t0"] = (rng.integers(10, 26, n) if family == "BD" else rng.integers(lo, hi, n)).astype(float)
        ev["ramp"] = rng.integers(7, 22, n).astype(float)
    if family in ("VA", "DV"):
        ev["vac_len"] = rng.integers(7, 15, n).astype(float)
        if family == "DV":
            a, b = ev["t0"] - 5, ev["t0"] + 5
            ev["vac_start"] = a + rng.random(n) * (b - a)
        else:
            ev["vac_start"] = rng.integers(lo, hi, n).astype(float)
    if family == "SP":
        ev["sprint_len"] = rng.integers(10, 15, n).astype(float)
        ev["sprint_start"] = rng.integers(lo, hi, n).astype(float)
    if family == "BI":
        ev["bi_len"] = rng.integers(10, 21, n).astype(float)
        ev["bi_start"] = rng.integers(lo, hi, n).astype(float)
    if family in ("AV", "AV2"):
        ev["av_day"] = rng.integers(lo, hi, n).astype(float)
        if family == "AV":
            ev["av_logged"] = rng.random(n) < 0.5
    if family == "DE":
        ev["de_day"] = rng.integers(lo, hi, n).astype(float)
    if family == "CS":
        ev["cs_day"] = rng.integers(lo, hi, n).astype(float)
    return ev


def events(rng, fam, n, window=ONSET):
    """Spec 003 events, all from the side stream `rng`. PS-sub, PS-use and PS-prop draw the same change
    days and logging (paired); DR+PS reuses DR's t0 and ramp. PS-endo's change day is set by
    `endo_panel`. Only DR's onset moves to `window`; AV, AV2, BI and the regression families keep the frozen
    U[50, 100] (spec 003 s4: "as spec 001", "unchanged"), and are scored at the 28-day baseline only."""
    base = FAMILY[fam][0]
    ev = sample_events(rng, base, n, *(window if base == "DR" else (50, 101)))
    ev.update(cday=np.full(n, np.nan), logged=np.zeros(n, dtype=bool), ps_ramp=np.full(n, np.nan))
    if fam in ("PS-sub", "PS-use", "PS-prop"):
        ev["cday"] = rng.integers(*ONSET, n).astype(float)
        ev["logged"] = rng.random(n) < 0.5
        ev["ps_ramp"] = rng.integers(7, 22, n).astype(float)  # drawn for all three; read by PS-prop
    elif fam == "DR+PS":
        ev["cday"] = ev["t0"] + rng.integers(-5, 6, n)
        ev["logged"] = rng.random(n) < 0.5
    return ev


def gen(rng, ev, fam, n=N, T=T_GEN, phi=ds.PHI_D, kappa=0.0, kappa_c=0.0, m1=0.0, help_off=True):
    """ds.generate_panel's constant-help path with the events supplied, plus spec 003's usage terms,
    help-off and observer shifts. help_off=False with frozen events on the main stream and no PS family
    reproduces ds.generate_panel bit for bit (--check). Help-off draws the help uniforms anyway and sets
    psi = 0, A = False, so help-off panels share every other draw with help-on ones."""
    base, delta = FAMILY[fam]
    day = np.arange(T)[None, :]
    D = ds.ar1_panel(rng, n, T, phi)
    if not np.all(np.isnan(ev["t0"])):
        D = D + np.clip((day - ev["t0"][:, None]) / ev["ramp"][:, None], 0, 1) * delta
    L = ds.ar1_panel(rng, n, T, ds.PHI_L)
    if base == "SP":
        L = L + 1.5 * ((day >= ev["sprint_start"][:, None]) & (day < (ev["sprint_start"] + ev["sprint_len"])[:, None]))
    L_obs = L + rng.normal(0, np.sqrt(0.25), (n, T))
    ctx = ds.sample_ctx(rng, D, base, ev["cs_day"])
    vacation = np.zeros((n, T), dtype=bool)
    if base in ("VA", "DV"):
        vacation = (day >= ev["vac_start"][:, None]) & (day < (ev["vac_start"] + ev["vac_len"])[:, None])
    diseng = day >= ev["de_day"][:, None] if base == "DE" else np.zeros((n, T), dtype=bool)

    cday = np.where(np.isnan(ev["cday"]), np.inf, ev["cday"])[:, None]
    after = day >= cday
    eta = ds.A0_USE - kappa * D - 4 * vacation - 2 * diseng
    if fam in USE_SHIFT:
        eta = eta + 0.5 * after
    if kappa_c:
        # CHOICE: change-dependent usage, worse change -> less use, D_{t-7} read as D_0 for t < 7; the
        # design run's size kappa_c = 0.3 matches |kappa| (spec 003 s4 gives none).
        eta = eta - kappa_c * (D - D[:, np.maximum(np.arange(T) - 7, 0)])
    used = rng.random((n, T)) < ds.expit(eta)

    lam = rng.uniform(0.25, 0.5, (n, J))
    e = rng.standard_normal((n, T, J))
    beta_ctx = np.zeros((n, T, J))
    for j in ds.BETA_CTX_INDICATORS:
        beta_ctx[:, :, j] = np.select([ctx == ds.CTX_CODE, ctx == ds.CTX_WRITE, ctx == ds.CTX_PERSONAL], ds.BETA_BY_CTX)
    av_day = ev["av_day"] if base in ("AV", "AV2") else np.full(n, np.nan)
    av_logged = ev["av_logged"] if base == "AV" else np.zeros(n, dtype=bool)
    av_inds = (ds.IDX_FRAG, ds.IDX_LATENCY) if base == "AV" else (ds.IDX_LATE, ds.IDX_MSGLEN)
    lam_mult = np.ones((n, T, J))
    mean_shift = np.zeros((n, T, J))
    if base in ("AV", "AV2"):
        av_after = day >= av_day[:, None]
        for j in av_inds:
            lam_mult[:, :, j] = np.where(av_after, 0.7, 1.0)
            mean_shift[:, :, j] = np.where(av_after, 0.5, 0.0)
    bi_mask = np.zeros((n, T), dtype=bool)
    if base == "BI":
        bi_mask = (day >= ev["bi_start"][:, None]) & (day < (ev["bi_start"] + ev["bi_len"])[:, None])

    H4_raw = (lam[:, None, ds.IDX_MSGLEN] * lam_mult[:, :, ds.IDX_MSGLEN] * D + ds.GAM[ds.IDX_MSGLEN] * L
              + beta_ctx[:, :, ds.IDX_MSGLEN] + e[:, :, ds.IDX_MSGLEN] + mean_shift[:, :, ds.IDX_MSGLEN])
    h4b = H4_raw[:, :ds.BASELINE_DAYS][used[:, :ds.BASELINE_DAYS]]
    mu_m = np.array([h4b.mean() + ds.MU_M4_DEFAULT * h4b.std(ddof=1), -1.0])
    kap_m = np.array([ds.KAPPA_A4_DEFAULT, ds.MIX_KAPPA_A5])
    pi_t = rng.beta(10 * ds.PI_BAR_DEFAULT, 10 * (1 - ds.PI_BAR_DEFAULT), (n, T))
    M = np.stack([rng.normal(mu_m[k], np.sqrt(kap_m[k]), (n, T)) for k in range(2)], axis=-1)
    pi_prime = 0.1 * pi_t / (0.1 * pi_t + 0.95 * (1 - pi_t) + 1e-12)

    A = rng.random((n, T)) < 0.3
    psi = ds.PSI
    if help_off:
        A, psi = np.zeros((n, T), dtype=bool), np.zeros(J)
    H = (lam[:, None, :] * lam_mult) * D[:, :, None] + ds.GAM[None, None, :] * L[:, :, None] \
        + beta_ctx - A[:, :, None] * psi[None, None, :] + e + mean_shift

    def mix(Hx, share):
        X = Hx.copy()
        for k, j in enumerate(J45):
            X[:, :, j] = ds.mix_authorship(Hx[:, :, j], share, M[:, :, k])
        return np.where(used[:, :, None], ds.apply_bi_mask(X, bi_mask), np.nan)

    X, Xf = mix(H, pi_t), mix(H, pi_prime)
    H = ds.apply_bi_mask(H, bi_mask)
    Y = D + rng.normal(0, np.sqrt(1 / 0.7 - 1), (n, T))
    resp_p = ds.expit(ds.logit(0.8) - m1 * D)
    responded = rng.random((n, T)) < resp_p

    # Observer change: intercept shifts tau, human share only for indicators 4, 5 (as attribution.shift).
    tau = np.zeros((n, T, J))
    if fam in STEP_SHIFT:
        tau[:, :, list(PS_MAP)] = 0.5 * after[..., None]
    elif fam == "PS-prop":
        frac = np.clip((day - cday) / np.nan_to_num(ev["ps_ramp"], nan=1.0)[:, None], 0, 1)
        tau = frac[..., None] * lam[:, None, :]

    # Policy log: one exogenous entry per logged person (PS-endo's is endogenous), with its indicator map.
    if base == "AV":
        log_day, log_map = np.where(av_logged, av_day, np.nan), av_inds
    else:
        log_day = np.where(ev["logged"], ev["cday"], np.nan)
        log_map = tuple(range(J)) if fam == "PS-prop" else PS_MAP  # CHOICE: PS-prop's map is every indicator
    p = dict(family=fam, D=D, L=L, L_obs=L_obs, ctx=ctx, used=used, A=A, H=H, X=X, X_filtered=Xf,
                X0=X, Xf0=Xf, pi_t=pi_t, pi_prime=pi_prime, Y=Y, resp_p=resp_p, responded=responded,
                U=~np.isnan(H), av_day=av_day, av_logged=av_logged, av_inds=av_inds, bi_mask=bi_mask,
                t0=ev["t0"], ramp=ev["ramp"], cday=ev["cday"], log_day=log_day, log_map=log_map,
                log_exo=fam != "PS-endo")
    return at.shift(p, tau) if tau.any() else p


# ---------------------------------------------------------------------------------------------- scorer
def zscores(p, B, unshifted=False):
    """Per-indicator z (n, T, J), usable mask, reason and residualized series of ds.compute_composite with
    (iv) off, on days < T. The baseline is fit on the scored series: indicators 4 and 5 read X_filtered
    and so does their baseline (spec 001 s18.3(1)). Reason 5: fewer than 3 available indicators (U_jt).
    `unshifted` scores X0 / Xf0, the panel with the observer shift subtracted (the oracle rule). CHOICE: the
    oracle rule removes the intercept shift tau only; PS-use's, PS-endo's and DR+PS's extra used days stay.
    Reason 5 is unreachable in this study's families (only BI removes indicators, 2 of 6)."""
    X = (p["X0"] if unshifted else p["X"])[:, :T].copy()
    X[..., J45] = (p["Xf0"] if unshifted else p["X_filtered"])[:, :T][..., J45]
    used, L_obs = p["used"][:, :T], p["L_obs"][:, :T]
    b = ds.fit_baseline(X, used, L_obs, 0, B)
    usable = used[..., None] & ~np.isnan(X)
    usable &= ~(p["A"][:, :T, None] & np.isin(np.arange(J), [ds.IDX_FRAG, ds.IDX_DEFER]))
    Xr = X.copy()
    for j in (ds.IDX_LATE, ds.IDX_FRAG, ds.IDX_DEFER, ds.IDX_LATENCY):
        Xr[:, :, j] = X[:, :, j] - b["slope"][:, j][:, None] * (L_obs - b["lmean"][:, None])
    z = np.where(usable, ds.safe_div(Xr - b["mean"][:, None, :], b["sd"][:, None, :]), np.nan)
    reason = np.zeros(used.shape, dtype=int)
    reason[~used] = 1
    reason[used & (usable.sum(-1) == 0)] = 2
    low = ds.rolling_sum(used.astype(float), ds.ABSTAIN_WINDOW) < \
        ds.ABSTAIN_USAGE_FRAC * b["usage_rate"][:, None] * ds.ABSTAIN_WINDOW
    reason[low & (reason == 0)] = 3
    usable &= ~low[..., None]
    few = used & (p["U"][:, :T].sum(-1) < 3)
    reason[few & (reason == 0)] = 5
    usable &= ~few[..., None]
    return z, usable, reason, Xr


def composite(z, usable, reason):
    cnt = usable.sum(-1)
    C = np.where(cnt > 0, np.where(usable, z, 0.0).sum(-1) / np.maximum(cnt, 1), np.nan)
    return np.where(reason > 0, np.nan, C)


def apply_log(p, z, usable, reason, Xr, rule, log_day=None, log_map=None):
    """Rules L1 / L2 at each person's logged exogenous change day c (spec 003 s8). Hold window (c, c + 14],
    as frozen (iv); the change day c itself is scored unheld, as in frozen (iv). L1: every indicator held and
    re-baselined over the window, S reset to 0 on c + 1 (spec 003 s8 and PREREG "S is reset"; frozen (iv)
    only holds S, so L1 is not the frozen code's (iv)).
    L2: only the mapped indicators held and re-baselined; S keeps running on the rest. Endogenous entries
    never act. Returns (z, usable, reason, reset mask or None)."""
    if rule == "L1_step":
        return l1_step(p, z, usable, reason, Xr, log_day, log_map)
    log_day = p["log_day"] if log_day is None else log_day
    log_map = p["log_map"] if log_map is None else log_map
    has = ~np.isnan(log_day) if p["log_exo"] and len(log_map) else np.zeros(len(log_day), dtype=bool)
    if rule == "L0" or not has.any():
        return z, usable, reason, None
    day = np.arange(T)[None, :]
    c = np.where(has, log_day, np.inf)[:, None]
    hold, after = (day > c) & (day <= c + ds.REBASELINE_WINDOW), day > c + ds.REBASELINE_WINDOW
    used = p["used"][:, :T]
    z, usable, reason = z.copy(), usable.copy(), reason.copy()
    for j in (range(J) if rule == "L1" else log_map):
        vals = np.where(hold & used, Xr[:, :, j], np.nan)
        cnt = (~np.isnan(vals)).sum(1)
        m = np.where(cnt >= 2, np.nanmean(vals, 1), 0.0)
        sd = np.nanstd(vals, 1, ddof=1)
        sd = np.where((cnt >= 2) & (sd > 1e-6), sd, 1.0)
        znew = ds.safe_div(Xr[:, :, j] - m[:, None], sd[:, None])
        z[:, :, j] = np.where(after & usable[:, :, j], znew, z[:, :, j])
        usable[:, :, j] &= ~hold
    reset = None
    if rule == "L1":
        reason[hold & used] = 4
        reset = day == c + 1
    return z, usable, reason, reset


def l1_step(p, z, usable, reason, Xr, log_day=None, log_map=None):
    """L1_step (unregistered arm, PREREG-003 section 4), as obs_003.step_rule(False) with rule L1: L1, but after
    the hold the mapped indicators read the baseline z minus their hold-mean baseline z (the estimated observer
    step; 0 with fewer than 2 usable hold days) and unmapped indicators keep the baseline z. As obs_003, the
    windows come from p's own log day."""
    z1, u1, reason, reset = apply_log(p, z, usable, reason, Xr, "L1", log_day, log_map)
    lm = list(p["log_map"] if log_map is None else log_map)
    day, c = np.arange(T)[None, :], p["log_day"][:, None]
    h = ((day > c) & (day <= c + ds.REBASELINE_WINDOW))[..., None] & usable
    cnt = h.sum(1)
    m = np.where(cnt >= 2, np.where(h, z, 0.0).sum(1) / np.maximum(cnt, 1), 0.0)
    zs = z.copy()
    zs[..., lm] -= m[:, None, lm]
    return np.where((day > c + ds.REBASELINE_WINDOW)[..., None] & u1, zs, z1), u1, reason, reset


def cusum(C, h, k, reset=None):
    """ds.run_cusum (refractory 14), plus S := 0 on reset days; returns the alarm array only."""
    n, Tn = C.shape
    S, refr = np.zeros(n), np.zeros(n, dtype=int)
    alarm = np.zeros((n, Tn), dtype=bool)
    for t in range(Tn):
        if reset is not None:
            S = np.where(reset[:, t], 0.0, S)
        c = C[:, t]
        held = np.isnan(c)
        S = np.where(held, S, np.maximum(0.0, S + np.where(held, 0.0, c) - k))
        newly = (refr <= 0) & ~held & (S >= h)
        alarm[:, t] = newly
        S = np.where(newly, 0.0, S)
        refr = np.where(newly, ds.REFRACTORY, np.maximum(refr - 1, 0))
    return alarm


def detector_C(p, B, det, rule="L0", **log):
    """(C, reason, reset) for detector 'A' (A-fixed composite; k is chosen by the caller) or 'oracle-D'.
    CHOICE: the CUSUM starts at day B, when the detector's own baseline exists (C held before B).
    CHOICE: 'oracle-D' reads true D_t every day against its known mean 0 and SD 1, with k = delta_min / 2:
    the upper bound of perfect measurement of D; it is unaffected by observer change and by rules. (The
    deterministic level component alone gives no false alarm on S, so h could not be tuned on it.)
    With help-off, the matched baseline and the late start, 'A-fixed k = 0.5' here is not the frozen
    A-fixed: it keeps the frozen k and composite form, with its own h."""
    if det == "oracle-D":
        C, reason, reset = p["D"][:, :T].copy(), np.zeros((p["D"].shape[0], T), dtype=int), None
    else:
        z, usable, reason, Xr = zscores(p, B, unshifted=rule == "oracle")
        z, usable, reason, reset = apply_log(p, z, usable, reason, Xr, "L0" if rule == "oracle" else rule, **log)
        C = composite(z, usable, reason)
    C[:, :B] = np.nan
    return C, reason, reset


def fa_rate(alarm, reason, B):
    return alarm[:, B:].sum() / max((reason[:, B:] == 0).sum() / 30.0, 1e-9)


def first_in(alarm, lo, hi):
    """Per person: day of the first alarm in [lo, hi) (per-person arrays), -1 if none."""
    day = np.arange(alarm.shape[1])[None, :]
    hit = alarm & (day >= lo[:, None]) & (day < hi[:, None])
    return np.where(hit.any(1), hit.argmax(1), -1)


def confirm(p, a, lag, base_days):
    """Spaced confirmation (spec 003 s7) of the alarm on day a[i] (-1 = none): probes on a + lag * (1..3).
    Returns per-person (confirmed, unconfirmed, unconfirmable, oracle-reference confirmed, days to
    confirmation). Unconfirmable: fewer than 2 answered confirmation probes or (CHOICE; attribution.py's
    M2x3 returns unconfirmed here) fewer than 2 answered baseline probes. Oracle reference: the baseline
    block with true baseline D replaced by the generator mean 0, probe noise kept.
    lag=None is the frozen 7-day rule (drift_sim.py:2196-2217): confirmed if any answered probe on
    a+1..a+7 reads at least the margin above the baseline mean (0 with fewer than 2 answered baseline
    probes), never unconfirmable. CHOICE: every one of the 7 days is probed, the rule's upper bound; the
    frozen run probed on a stochastic schedule."""
    n = len(a)
    has = a >= 0
    i = np.arange(n)[:, None]
    yb, rb = p["Y"][:, base_days], p["responded"][:, base_days]
    eb = yb - p["D"][:, base_days]
    mean = lambda v, w: ds.safe_div(np.where(w, v, 0.0).sum(1), w.sum(1))
    offs = np.arange(1, 8) if lag is None else lag * np.arange(1, M_CONF + 1)
    days = np.clip(a[:, None], 0, None) + offs[None, :]
    y, r = p["Y"][i, days], p["responded"][i, days]
    if lag is None:
        nb = rb.sum(1) >= 2
        hit = r & (y - np.where(nb, mean(yb, rb), 0.0)[:, None] >= MARGIN)
        ohit = r & (y - np.where(nb, mean(eb, rb), 0.0)[:, None] >= MARGIN)
        conf = has & hit.any(1)
        return conf, has & ~conf, np.zeros(n, dtype=bool), has & ohit.any(1), np.where(conf, hit.argmax(1) + 1, 0)
    ok = has & (r.sum(1) >= 2) & (rb.sum(1) >= 2)
    conf = ok & (mean(y, r) - mean(yb, rb) >= MARGIN)
    oconf = ok & (mean(y, r) - mean(eb, rb) >= MARGIN)
    return conf, ok & ~conf, has & ~ok, oconf, np.where(conf, M_CONF * lag, 0)


def confirm_all(p, alarm, lag, base_days, B, onset=None):
    """Every alarm in [B, T), per person: (alarms, confirmed, confirmed inside [onset, onset + 21), confirmed
    before onset). Spec 003 s2: in a positive family only pre-onset alarms are false."""
    n_c, n_t, n_f = np.zeros(len(alarm)), np.zeros(len(alarm)), np.zeros(len(alarm))
    for t in range(B, T):
        a = np.where(alarm[:, t], t, -1)
        if (a >= 0).any():
            c = confirm(p, a, lag, base_days)[0]
            n_c += c
            if onset is not None:
                n_t += c & (t >= onset) & (t < onset + 21)
                n_f += c & (t < onset)
    return alarm[:, B:].sum(1) * 1.0, n_c, n_t, n_f


def probe_rule(p, alarm, lag, bd, B, onset, rule):
    """PREREG-003 section 5's probe rules, per person: (probed alarms, confirmed, confirmed in [onset, onset + 21),
    confirmed before onset). 'all' probes every alarm (confirm_all); 'wait' probes no new alarm until the last
    probed alarm's third probe day has passed (3 x lag + 1 days); 'stop' is 'wait' with no probes after a
    person's first confirmed alarm. Ported from decide_003.py unchanged."""
    n = len(alarm)
    probed, n_c, n_t, n_f = (np.zeros(n) for _ in range(4))
    nxt, stopped = np.full(n, B), np.zeros(n, dtype=bool)
    for t in range(B, T):
        el = alarm[:, t] if rule == "all" else alarm[:, t] & (t >= nxt) & ~stopped
        if not el.any():
            continue
        c = confirm(p, np.where(el, t, -1), lag, bd)[0]
        probed += el
        n_c += c
        if onset is not None:
            n_t += c & (t >= onset) & (t < onset + 21)
            n_f += c & (t < onset)
        nxt = np.where(el, t + M_CONF * lag + 1, nxt)
        stopped |= c & (rule == "stop")
    return probed, n_c, n_t, n_f


def share(cf):
    """Confirmed share among confirmable first alarms; unconfirmable ones are reported, not counted."""
    return ratio(cf[0] * 1.0, (cf[0] | cf[1]) * 1.0)


def q_at(z, reason, f):
    """attribution.py's M1 statistic Q (14-day concentration) at day f[i]; NaN where f < 0."""
    zz = np.where((reason > 0)[..., None], np.nan, z)
    return np.array([at.q_stat(zz, i, f[i]) if f[i] >= 0 else np.nan for i in range(len(f))])


# ---------------------------------------------------------------------------------------------- statistics
def boot(fn, n, bidx):
    """Point estimate, person-bootstrap SE and 95% percentile interval over the fixed resample matrix
    `bidx` (NBOOT x n). Persons are paired across every family, arm, rule and detector, and every statistic
    uses the same resamples; paired differences are computed inside one fn. `dropped` counts resamples
    where the statistic was undefined (an empty denominator)."""
    est = fn(np.arange(n))
    bs = np.array([fn(ix) for ix in bidx])
    ok = np.isfinite(bs)
    bs = bs[ok]
    r = lambda x: None if not np.isfinite(x) else round(float(x), 4)
    out = dict(est=r(est), se=r(bs.std(ddof=1)) if len(bs) > 1 else None,
               lo=r(np.percentile(bs, 2.5)) if len(bs) else None, hi=r(np.percentile(bs, 97.5)) if len(bs) else None)
    if not ok.all():
        out["dropped"] = int((~ok).sum())
    return out


def ratio(num, den):
    return lambda idx: num[idx].sum() / den[idx].sum() if den[idx].sum() > 0 else np.nan


# ---------------------------------------------------------------------------------------------- tune
def seeds(base, phi, cell):
    tag = int(phi * 10) * 100 + cell
    return np.random.default_rng([base, tag]), np.random.default_rng([base, tag, 1])


def panels(base_seed, phi, fams, cell=0, n=None, **cellkw):
    """Generate the listed families for one (phi, cell): one main seed, one side seed, paired persons.
    n=None reads the module's N at call time."""
    n = N if n is None else n
    out = {}
    for fam in fams:
        rng, side = seeds(base_seed, phi, cell)
        out[fam] = gen(rng, events(side, fam, n), fam, n=n, phi=phi, **cellkw)
    return out


def tune_h(C, reason, B, k):
    h = ds.bisect(lambda x: fa_rate(cusum(C, x, k), reason, B), 0.1, 40.0, FA_TARGET)
    fa = fa_rate(cusum(C, h, k), reason, B)
    assert abs(fa / FA_TARGET - 1) < 0.05, (h, fa)
    return round(float(h), 6)


def run_tune():
    """Tuning seed only (spec 003 s5). Per phi: c = composite shift per unit delta_D, help-off, from DR-1.0
    against the paired S panel on days after the ramp ends (28-day baseline); k* = c / 2. Then h for
    A-fixed at k = 0.5, at k*, and oracle-D, per phi and baseline length, at 1 FA per 6 tracked
    person-months on S. q* for M1: attribution.py's rule (90th percentile of Q at DR-1.0 detections,
    phi 0.7, 28 days, k = 0.5). CHOICE: c is estimated at the 28-day baseline and reused at 56; q* uses
    first in-window detections, where attribution.py used every alarm in its window."""
    out = dict(seed=ds.TUNING_SEED, fa_target=FA_TARGET, cells={})
    for phi in PHIS:
        P = panels(ds.TUNING_SEED, phi, ("S", "DR-1.0"))
        Cs, rs, _ = detector_C(P["S"], 28, "A")
        Cd, rd, _ = detector_C(P["DR-1.0"], 28, "A")
        day = np.arange(T)[None, :]
        post = (day >= (P["DR-1.0"]["t0"] + P["DR-1.0"]["ramp"])[:, None]) & (rs == 0) & (rd == 0)
        c = float(np.nanmean(np.where(post, Cd - Cs, np.nan)))
        cell = dict(c=round(c, 6), k_star=round(c / 2, 6), h={})
        for B in (28, 56):
            CsB, rsB, _ = detector_C(P["S"], B, "A")
            Co, ro, _ = detector_C(P["S"], B, "oracle-D")
            cell["h"][str(B)] = {"A-k0.5": tune_h(CsB, rsB, B, ds.K_CUSUM),
                                 "A-kstar": tune_h(CsB, rsB, B, round(c / 2, 6)),
                                 "oracle-D": tune_h(Co, ro, B, MARGIN)}
        out["cells"][str(phi)] = cell
    p = panels(ds.TUNING_SEED, 0.7, ("DR-1.0",))["DR-1.0"]
    z, usable, reason, _ = zscores(p, 28)
    C = composite(z, usable, reason)
    C[:, :28] = np.nan
    alarm = cusum(C, out["cells"]["0.7"]["h"]["28"]["A-k0.5"], ds.K_CUSUM)
    det = first_in(alarm, p["t0"], p["t0"] + 21)
    qs = q_at(z, reason, det)[det >= 0]
    out["q_star"] = round(float(np.nanpercentile(qs, at.Q_PCTL)), 6)
    out["n_q"] = int(np.isfinite(qs).sum())
    (HERE / "tuning_003.json").write_text(json.dumps(out, indent=1))
    return out


# ---------------------------------------------------------------------------------------------- study
def endo_panel(base_seed, phi, s_panel, h_ref, cell=0, n=None, **cellkw):
    """PS-endo: PS-use's change 3 days after the person's first post-baseline alarm of the reference
    detector (A-fixed, k = 0.5, 28 days); always logged as endogenous. Persons without an alarm get none.
    An alarm on days 207-209 puts the change at T or later: logged, never observed in detection."""
    n = N if n is None else n
    C, _, _ = detector_C(s_panel, 28, "A")
    a = first_in(cusum(C, h_ref, ds.K_CUSUM), np.full(n, 28), np.full(n, T))
    rng, side = seeds(base_seed, phi, cell)
    ev = events(side, "S", n)
    ev["cday"] = np.where(a >= 0, a + 3, np.nan).astype(float)
    ev["logged"] = a >= 0
    p = gen(rng, ev, "PS-endo", n=n, phi=phi, **cellkw)
    C2, _, _ = detector_C(p, 28, "A")
    a2 = first_in(cusum(C2, h_ref, ds.K_CUSUM), np.full(n, 28), np.full(n, T))
    assert np.array_equal(a, a2), "PS-endo's change altered the alarm that triggered it"
    return p


def run_study(base_seed, tun, n=N):
    """All spec 003 quantities for one seed base. `design` passes DESIGN_SEED; `score` an evaluation seed."""
    brng = np.random.default_rng([base_seed, 99]).integers(0, n, (NBOOT, n))  # shared resample matrix
    out = dict(seed=base_seed, n=n, T=T, T_gen=T_GEN, onset=list(ONSET), margin=MARGIN, nboot=NBOOT,
               lags={str(phi): lag_for(phi) for phi in PHIS}, detection={}, confirmation={}, policy_log={},
               cells={}, regression={}, budget={})
    ones = np.ones(n)
    pseudo = np.random.default_rng([base_seed, 2]).integers(*ONSET, n).astype(float)

    def alarms(p, B, det, rule="L0", **log):
        tc = tun["cells"][str(p["phi"])]
        k = {"A-k0.5": ds.K_CUSUM, "A-kstar": tc["k_star"], "oracle-D": MARGIN}[det]
        C, reason, reset = detector_C(p, B, "oracle-D" if det == "oracle-D" else "A", rule, **log)
        return cusum(C, tc["h"][str(B)][det], k, reset), reason

    def sens(alarm, onset, w, excl=True):
        return ds._sensitivity(alarm, onset, window=w, exclude_pre_onset_alarms=excl).astype(float)

    # ---- Q1 detection, and baseline error / alarm-day D on S (spec 003 s10)
    for phi in PHIS:
        P = panels(base_seed, phi, ("S", "DR-0.5", "DR-1.0", "DR-1.5"), n=n)
        for p in P.values():
            p["phi"] = phi
        for B in (28, 56):
            for det in ("A-k0.5", "A-kstar", "oracle-D"):
                key = f"phi{phi}_B{B}_{det}"
                aS, rS = alarms(P["S"], B, det)
                trS = (rS[:, B:] == 0).sum(1) / 30.0
                r = {"S_fa_per_month": boot(ratio(aS[:, B:].sum(1), trS), n, brng),
                     "S_chance_sens21": boot(ratio(sens(aS, pseudo, 21), ones), n, brng)}
                if det == "A-k0.5":
                    bm = P["S"]["D"][:, :B].mean(1)
                    who = aS[:, B:].any(1)
                    r["S_true_baseline_D_alarmed"] = boot(ratio(bm * who, who * 1.0), n, brng)
                    r["S_true_baseline_D_not"] = boot(ratio(bm * ~who, ~who * 1.0), n, brng)
                    dS = np.where(aS[:, B:], P["S"]["D"][:, B:T], 0.0)
                    r["S_alarm_day_D"] = boot(ratio(dS.sum(1), aS[:, B:].sum(1) * 1.0), n, brng)
                for d in ("DR-0.5", "DR-1.0", "DR-1.5"):
                    pd = P[d]
                    a, rr = alarms(pd, B, det)
                    t0 = pd["t0"]
                    pre = (np.arange(T)[None, :] >= B) & (np.arange(T)[None, :] < t0[:, None])
                    r[d] = {"sens21": boot(ratio(sens(a, t0, 21), ones), n, brng),
                            "sens42": boot(ratio(sens(a, t0, 42), ones), n, brng),
                            "rmst42": boot(ratio(ds._rmst42(a, t0), ones), n, brng),
                            "pre_onset_fa_per_month": boot(ratio((a & pre).sum(1), ((rr == 0) & pre).sum(1) / 30.0), n, brng),
                            "post_onset_alarms_per_month": boot(ratio((a & ~pre & (np.arange(T)[None, :] >= B)).sum(1),
                                                                      ((rr == 0) & ~pre & (np.arange(T)[None, :] >= B)).sum(1) / 30.0), n, brng)}
                out["detection"][key] = r
            # H6: matched k minus k = 0.5, DR sensitivity at 21 days, paired persons, each at its own h
            for d in ("DR-1.0", "DR-1.5"):
                a0, _ = alarms(P[d], B, "A-k0.5")
                a1, _ = alarms(P[d], B, "A-kstar")
                s0, s1 = sens(a0, P[d]["t0"], 21), sens(a1, P[d]["t0"], 21)
                out["detection"][f"phi{phi}_B{B}_H6_{d}_kstar_minus_k05"] = boot(
                    lambda idx: s1[idx].mean() - s0[idx].mean(), n, brng)

        # ---- Q2 confirmation, A-fixed k = 0.5, rule L0, all four baseline arms; lags: design-known spaced,
        # fixed 9, next-day (a+1..a+3, as design_check_003.py; M2x3 used a+1, a+3, a+5) and the frozen 7-day rule
        gaps = {}
        for B, m in ARMS:
            bd = probe_days(B, m)
            fams = {f: P[f] for f in ("S", "DR-0.5", "DR-1.0", "DR-1.5")}
            al = {f: alarms(p, B, "A-k0.5") for f, p in fams.items()}
            first = {"S": first_in(al["S"][0], np.full(n, B), np.full(n, T))}
            for d in ("DR-0.5", "DR-1.0", "DR-1.5"):
                t0 = fams[d]["t0"]
                first[d] = np.where(sens(al[d][0], t0, 21) > 0, first_in(al[d][0], t0, t0 + 21), -1)
            res = {}
            for lagname, lag in (("spaced", lag_for(phi)), ("fixed9", FIXED_LAG), ("next_day", 1), ("frozen7", None)):
                cf = res[lagname] = {f: confirm(fams[f], first[f], lag, bd) for f in fams}
                cS, uS, xS, oS, _ = cf["S"]
                r = {"lag": lag, "S_n_first_alarms": int((first["S"] >= 0).sum()),
                     "S_confirmed_share": boot(share(cf["S"]), n, brng),
                     "S_oracle_ref_share": boot(ratio(oS * 1.0, (cS | uS) * 1.0), n, brng),
                     "S_gap_block_minus_oracle": boot(
                         lambda idx: share(cf["S"])(idx) - ratio(oS * 1.0, (cS | uS) * 1.0)(idx), n, brng),
                     "S_unconfirmable_share": boot(ratio(xS * 1.0, (first["S"] >= 0) * 1.0), n, brng)}
                for f in fams:
                    c, x, d_ = cf[f][0], cf[f][2], cf[f][4]
                    n_al, n_c, n_t, n_f = confirm_all(fams[f], al[f][0], lag, bd, B, None if f == "S" else fams[f]["t0"])
                    tr = (al[f][1][:, B:] == 0).sum(1) / 30.0
                    g = r.setdefault(f, {})
                    g["days_to_confirmation"] = boot(ratio(d_ * 1.0, c * 1.0), n, brng)
                    # confirmation probes plus the arm's baseline block (m per person), per tracked month
                    g["probes_per_tracked_month"] = boot(ratio((7 if lag is None else M_CONF) * n_al + m, tr), n, brng)
                    if f == "S":
                        g["confirmed_fa_per_tracked_month"] = boot(ratio(n_c, tr), n, brng)
                    else:
                        g.update(n_detected=int((first[f] >= 0).sum()), confirmed_share=boot(share(cf[f]), n, brng),
                                 unconfirmable_share=boot(ratio(x * 1.0, (first[f] >= 0) * 1.0), n, brng),
                                 confirmed_ppv=boot(ratio(n_t, n_t + n_f), n, brng),
                                 pre_onset_confirmed_fa_per_tracked_month=boot(ratio(n_f, tr), n, brng))
                out["confirmation"][f"phi{phi}_B{B}_m{m}_{lagname}"] = r
            sp, nd = res["spaced"], res["next_day"]
            out["confirmation"][f"phi{phi}_B{B}_m{m}_H1_S_spaced_minus_next_day"] = boot(
                lambda idx: share(sp["S"])(idx) - share(nd["S"])(idx), n, brng)
            out["confirmation"][f"phi{phi}_B{B}_m{m}_H1_DR-1.0_spaced_over_next_day"] = boot(
                lambda idx: share(sp["DR-1.0"])(idx) / share(nd["DR-1.0"])(idx), n, brng)
            gaps[(B, m)] = lambda idx, c=sp["S"]: share(c)(idx) - ratio(c[3] * 1.0, (c[0] | c[1]) * 1.0)(idx)
        out["confirmation"][f"phi{phi}_H2_gap_B28m4_minus_B56m4"] = boot(
            lambda idx: gaps[(28, 4)](idx) - gaps[(56, 4)](idx), n, brng)

        # ---- probe budget (PREREG-003 section 5): spaced lag, 28 days, 4 probes, rules all / wait / stop
        bd, lag = probe_days(28, 4), lag_for(phi)
        for fam in ("S", "DR-1.0", "DR-1.5"):
            p = P[fam]
            a, rr = alarms(p, 28, "A-k0.5")
            tr = (rr[:, 28:] == 0).sum(1) / 30.0
            r = {}
            for rule in ("all", "wait", "stop"):
                pr, n_c, n_t, n_f = probe_rule(p, a, lag, bd, 28, None if fam == "S" else p["t0"], rule)
                g = r[rule] = {"probes_per_tracked_month": boot(ratio(M_CONF * pr + 4, tr), n, brng),
                               "probed_share_of_alarms": boot(ratio(pr, a[:, 28:].sum(1) * 1.0), n, brng)}
                if fam == "S":
                    g["confirmed_fa_per_tracked_month"] = boot(ratio(n_c, tr), n, brng)
                else:
                    g["confirmed_ppv"] = boot(ratio(n_t, n_t + n_f), n, brng)
                    g["persons_confirmed_in_window"] = boot(ratio((n_t > 0) * 1.0, ones), n, brng)
            # the 'all' rule is the design rule: same persons, same numbers as the confirmation block
            want = out["confirmation"][f"phi{phi}_B28_m4_spaced"][fam]["probes_per_tracked_month"]["est"]
            assert r["all"]["probes_per_tracked_month"]["est"] == want, (phi, fam, want)
            out["budget"][f"phi{phi}_{fam}"] = r

        # ---- Q3 policy log at phi 0.7, 28 days, both A-fixed k
        if phi == 0.7:
            fams = ("PS-sub", "PS-use", "PS-prop", "DR+PS", "AV", "AV2")
            Q = panels(base_seed, phi, fams, n=n)
            Q["S"], Q["DR-1.0"] = P["S"], P["DR-1.0"]
            Q["PS-endo"] = endo_panel(base_seed, phi, P["S"], tun["cells"]["0.7"]["h"]["28"]["A-k0.5"], n=n)
            for p in Q.values():
                p["phi"] = phi
            out["policy_log"] = policy_log(Q, alarms, sens, brng, tun, n)

    # ---- cells at phi 0.7: usage (kappa -0.3, +0.3, change-dependent 0.3) and probe response m1 0.5, 1.5
    for ci, (name, kw) in enumerate((("kappa-0.3", dict(kappa=-0.3)), ("kappa+0.3", dict(kappa=0.3)),
                                     ("change_dep_0.3", dict(kappa_c=0.3)), ("m1_0.5", dict(m1=0.5)),
                                     ("m1_1.5", dict(m1=1.5))), start=1):
        P = panels(base_seed, 0.7, ("S", "DR-1.0"), cell=ci, n=n, **kw)
        for p in P.values():
            p["phi"] = 0.7
        aS, rS = alarms(P["S"], 28, "A-k0.5")
        aD, _ = alarms(P["DR-1.0"], 28, "A-k0.5")
        fS = first_in(aS, np.full(n, 28), np.full(n, T))
        t0 = P["DR-1.0"]["t0"]
        fD = np.where(sens(aD, t0, 21) > 0, first_in(aD, t0, t0 + 21), -1)
        # CHOICE: the cells reuse phi 0.7's h (frozen precedent), its lag 9 and the 28-day, 4-probe arm
        cS, uS, xS, _, _ = confirm(P["S"], fS, 9, probe_days(28, 4))
        cD, uD, xD, _, _ = confirm(P["DR-1.0"], fD, 9, probe_days(28, 4))
        out["cells"][name] = {
            "S_fa_per_month": boot(ratio(aS[:, 28:].sum(1), (rS[:, 28:] == 0).sum(1) / 30.0), n, brng),
            "DR-1.0_sens21": boot(ratio(sens(aD, t0, 21), ones), n, brng),
            "S_spaced_confirmed_share": boot(ratio(cS * 1.0, (cS | uS) * 1.0), n, brng),
            "DR-1.0_spaced_confirmed_share": boot(ratio(cD * 1.0, (cD | uD) * 1.0), n, brng),
            "S_unconfirmable_share": boot(ratio(xS * 1.0, (fS >= 0) * 1.0), n, brng),
            "DR-1.0_unconfirmable_share": boot(ratio(xD * 1.0, (fD >= 0) * 1.0), n, brng)}

    # ---- regression families (no prediction): alarm rate per tracked person-month, phi 0.7, 28 days, L0
    R = panels(base_seed, 0.7, ("VA", "DE", "SP", "CS", "BD", "DV", "BI"), cell=9, n=n)
    for fam, p in R.items():
        p["phi"] = 0.7
        a, rr = alarms(p, 28, "A-k0.5")
        out["regression"][fam] = boot(ratio(a[:, 28:].sum(1), (rr[:, 28:] == 0).sum(1) / 30.0), n, brng)
    return out


def policy_log(Q, alarms, sens, brng, tun, n):
    """Spec 003 s8 at phi 0.7, 28-day baseline. Every alarm is scored against the generator status."""
    out = {}
    day = np.arange(T)[None, :]
    S = Q["S"]
    for det in ("A-k0.5", "A-kstar"):
        r = {}
        a_S, r_S = alarms(S, 28, det)
        for fam in ("PS-sub", "PS-use", "PS-prop", "PS-endo"):
            p = Q[fam]
            cd = np.where(np.isnan(p["cday"]), np.inf, p["cday"])
            post = (day >= cd[:, None]) & (day >= 28)
            logged = ~np.isnan(p["log_day"])
            groups = {"logged": logged, "unlogged": ~logged & np.isfinite(cd), "all": np.isfinite(cd)}
            sS = (a_S & post).sum(1)
            tS = ((r_S == 0) & post).sum(1) / 30.0
            fr = {}
            arms = [("L0", {}), ("L1", {}), ("L2", {}), ("oracle", {})]
            if fam in ("PS-sub", "PS-use"):  # L1 ignores the map, so L1_map_omits_6 equals L1 (a check)
                arms += [("L1_map_omits_6", dict(log_map=PS_MAP[:2])), ("L2_map_omits_6", dict(log_map=PS_MAP[:2])),
                         ("L1_coverage_1", dict(log_day=p["cday"])), ("L2_coverage_1", dict(log_day=p["cday"])),
                         ("L1_step", {})]  # L1_step: unregistered arm, PREREG-003 section 4
            for name, kw in arms:
                a, rr = alarms(p, 28, det, name if name == "L1_step" else name.split("_")[0], **kw)
                s, t_ = (a & post).sum(1), ((rr == 0) & post).sum(1) / 30.0
                for g, w in groups.items():
                    if fam == "PS-endo" and g != "logged":
                        continue
                    num, den = s * w, t_ * w
                    fr[f"{name}_{g}_post_fa_per_month"] = boot(ratio(num, den), n, brng)
                    # paired: the same persons and post-change window on S
                    fr[f"{name}_{g}_ratio_to_S"] = boot(
                        lambda idx, num=num, den=den, w=w: ratio(num, den)(idx) / ratio(sS * w, tS * w)(idx), n, brng)
            r[fam] = fr
        # L0+label: person-labelled share of post-change / post-onset alarms, W = 14 and 28.
        # CHOICE: scoring window [x0, x0 + 42), x0 = the change day (PS) or onset (DR-1.0, DR+PS).
        lab = {}
        for fam in ("PS-sub", "PS-use", "PS-prop", "DR-1.0", "DR+PS"):
            p = Q[fam]
            x0 = p["t0"] if fam.startswith("DR") else p["cday"]
            a, _ = alarms(p, 28, det)
            win = (day >= x0[:, None]) & (day < x0[:, None] + 42) & (day >= 28)
            aw = a & win
            for W in W_LABEL:
                ld = p["log_day"] if p["log_exo"] and len(p["log_map"]) else np.full(n, np.nan)
                ldv = np.where(np.isnan(ld), -np.inf, ld)[:, None]
                obs = aw & (ldv >= day - W) & (ldv <= day)
                for g, w in (("all", np.ones(n, dtype=bool)), ("unlogged", np.isnan(ld))):
                    lab[f"{fam}_W{W}_{g}"] = ((aw & ~obs).sum(1) * w, aw.sum(1) * w)
        r["label_person_share"] = {k: boot(ratio(*v), n, brng) for k, v in lab.items()}
        for fam in ("PS-sub", "PS-use", "PS-prop", "DR+PS"):  # separation: DR-1.0's share minus the family's
            r["label_person_share"][f"sep_DR-1.0_minus_{fam}_W14"] = boot(
                lambda idx, f=fam: ratio(*lab["DR-1.0_W14_all"])(idx) - ratio(*lab[f"{f}_W14_all"])(idx), n, brng)
        # Spaced confirmation after each rule (lag 9, 28 days, 4 probes) on the first alarm from the change
        # day (PS) or onset (DR+PS). Person-confirmed under L0+label = labelled person (W = 14) and confirmed.
        pc = {}
        bd = probe_days(28, 4)
        for fam in ("PS-sub", "PS-use", "PS-prop", "PS-endo", "DR+PS"):
            p = Q[fam]
            x0 = np.maximum(p["t0"] if fam == "DR+PS" else np.nan_to_num(p["cday"], nan=T), 28)
            for rule in ("L0", "L1", "L2"):
                a, _ = alarms(p, 28, det, rule)
                f = first_in(a, x0, np.full(n, T))
                cf = confirm(p, f, 9, bd)
                pc[f"{fam}_{rule}_confirmed_share"] = boot(share(cf), n, brng)
                pc[f"{fam}_{rule}_unconfirmable_share"] = boot(ratio(cf[2] * 1.0, (f >= 0) * 1.0), n, brng)
                if rule == "L0":
                    ld = p["log_day"] if p["log_exo"] and len(p["log_map"]) else np.full(n, np.nan)
                    for W in W_LABEL:
                        person = (f >= 0) & ~((ld >= f - W) & (ld <= f))
                        pc[f"{fam}_L0label_W{W}_person_confirmed_share"] = boot(
                            ratio((person & cf[0]) * 1.0, (cf[0] | cf[1]) * 1.0), n, brng)
        r["confirmation_after_rule"] = pc
        # H5 (known answer): unlogged PS-prop vs DR-1.0, person-attributed share, L0+label and M1
        num_d, den_d = lab["DR-1.0_W14_all"]
        num_p, den_p = lab["PS-prop_W14_unlogged"]
        r["H5_L0label_DR_minus_unlogged_PSprop"] = boot(
            lambda idx: ratio(num_d, den_d)(idx) - ratio(num_p, den_p)(idx), n, brng)
        m1 = {}
        for fam in ("DR-1.0", "PS-prop"):
            p = Q[fam]
            x0 = p["t0"] if fam == "DR-1.0" else p["cday"]
            z, usable, reason, _ = zscores(p, 28)
            a, _ = alarms(p, 28, det)
            f = first_in(a, x0, x0 + 42)
            w = (f >= 0) & (np.ones(n, dtype=bool) if fam == "DR-1.0" else np.isnan(p["log_day"]))
            f = np.where(w, f, -1)
            m1[fam] = (((f >= 0) & ~(q_at(z, reason, f) >= tun["q_star"])) * 1.0, w * 1.0)  # M1: person unless Q >= q*
        r["H5_M1_DR_minus_unlogged_PSprop"] = boot(
            lambda idx: ratio(*m1["DR-1.0"])(idx) - ratio(*m1["PS-prop"])(idx), n, brng)
        # DR sensitivity under each rule (the log's cost on true change), and DR+PS
        dr, drps = {}, {}
        for rule in ("L0", "L1", "L2", "oracle", "L1_step"):
            a, _ = alarms(Q["DR-1.0"], 28, det, rule)
            dr[f"DR-1.0_{rule}_sens21_excl_false"] = boot(ratio(sens(a, Q["DR-1.0"]["t0"], 21, False), np.ones(n)), n, brng)
            p = Q["DR+PS"]
            a, _ = alarms(p, 28, det, rule)
            s = sens(a, p["t0"], 21, False)
            # D's shift starts on t0 + 1, so it begins inside the hold (c, c + 14] when c <= t0 <= c + 13
            logged = ~np.isnan(p["log_day"])
            inwin = logged & (p["t0"] >= p["cday"]) & (p["t0"] <= p["cday"] + ds.REBASELINE_WINDOW - 1)
            dr[f"DR+PS_{rule}_sens21_excl_false"] = boot(ratio(s, np.ones(n)), n, brng)
            dr[f"DR+PS_{rule}_sens21_logged"] = boot(ratio(s * logged, logged * 1.0), n, brng)
            dr[f"DR+PS_{rule}_sens21_onset_in_rebaseline_window"] = boot(ratio(s * inwin, inwin * 1.0), n, brng)
            obs_caused = (a & (day >= p["cday"][:, None]) & (day < p["t0"][:, None]) & (day >= 28)).sum(1)
            dr[f"DR+PS_{rule}_observer_caused_fa_per_100_persons"] = boot(ratio(100 * obs_caused * 1.0, np.ones(n)), n, brng)
            drps[rule] = (s, inwin, logged)
        (s1, w, lg), s2 = drps["L1"], drps["L2"][0]
        dr["H4_L2_minus_L1_onset_in_window"] = boot(lambda idx: ratio(s2 * w, w * 1.0)(idx) - ratio(s1 * w, w * 1.0)(idx), n, brng)
        dr["L2_minus_L1_logged"] = boot(lambda idx: ratio(s2 * lg, lg * 1.0)(idx) - ratio(s1 * lg, lg * 1.0)(idx), n, brng)
        s1s = drps["L1_step"][0]
        dr["H4_L2_minus_L1_step_onset_in_window"] = boot(
            lambda idx: ratio(s2 * w, w * 1.0)(idx) - ratio(s1s * w, w * 1.0)(idx), n, brng)
        dr["n_DRPS_onset_in_window"] = int(w.sum())
        r["dr"] = dr
        # AV / AV2 under the rules: overall alarm rate post-baseline
        r["av"] = {}
        for fam in ("AV", "AV2"):
            lg = Q[fam]["av_logged"]
            for rule in ("L0", "L1", "L2"):
                a, rr = alarms(Q[fam], 28, det, rule)
                al, tr = a[:, 28:].sum(1), (rr[:, 28:] == 0).sum(1) / 30.0
                r["av"][f"{fam}_{rule}_fa_per_month"] = boot(ratio(al, tr), n, brng)
                if fam == "AV":  # frozen P3's contrast: logged against unlogged
                    r["av"][f"AV_{rule}_logged_fa_per_month"] = boot(ratio(al * lg, tr * lg), n, brng)
                    r["av"][f"AV_{rule}_unlogged_fa_per_month"] = boot(ratio(al * ~lg, tr * ~lg), n, brng)
        r["L1_step_label"] = "unregistered arm, PREREG-003 section 4"
        out[det] = r
    return out


# ---------------------------------------------------------------------------------------------- verdicts
def verdicts(out):
    """VERDICT_RULES applied to a run_study output (design_003.json or results_003.json): per clause the
    statistic, the rule in words, the threshold and `holds`; an item holds only if all its clauses do. UNSCORED
    entries carry scored: false and are skipped when the file lacks them (L1_step is newer than the design run)."""
    def stat(path):
        b = out
        for k in path:
            b = b.get(k) if isinstance(b, dict) else None
        return None if b is None else {k: b[k] for k in ("est", "lo", "hi")}
    v = {}
    for (item, clause), (path, rule, thr) in VERDICT_RULES.items():
        b = stat(path)
        est, lo, hi = b["est"], b["lo"], b["hi"]
        holds = None not in (est, lo, hi) and {"hi<=": hi <= thr, "lo>=": lo >= thr, "lo>": lo > thr,
                                               "est<": est < thr, "inside": -thr < lo and hi < thr}[rule]
        c = dict(b, rule=RULE_WORDS[rule].format(thr), threshold=thr, holds=bool(holds))
        if clause is None:
            v[item] = c
        else:
            v.setdefault(item, {"clauses": {}})["clauses"][clause] = c
    for item in ("H3", "H5"):
        v[item]["holds"] = all(c["holds"] for c in v[item]["clauses"].values())
    for place, path in UNSCORED.items():
        b = stat(path)
        if b is not None:
            d = v
            for k in place[:-1]:
                d = d.setdefault(k, {})
            d[place[-1]] = dict(b, scored=False)
    for item in ("H3", "H4"):
        if "L1_step" in v[item]:
            v[item]["L1_step"]["label"] = "unregistered arm, PREREG-003 section 4"
    return v


# ---------------------------------------------------------------------------------------------- check
def check():
    rng = lambda s: np.random.default_rng(s)
    # (a) event sampler reproduces the frozen one at the frozen window
    for fam in ds.FAMILIES:
        e1, e2 = sample_events(rng(5), fam, 300), ds.sample_events(rng(5), fam, 300)
        assert all(np.array_equal(e1[k], e2[k], equal_nan=True) for k in e2), fam
    # (b) generator reproduces ds.generate_panel: frozen events on the main stream, help on
    keys = ("D", "L", "L_obs", "ctx", "used", "A", "H", "X", "X_filtered", "pi_t", "pi_prime", "Y", "resp_p",
            "responded", "av_day", "av_logged", "bi_mask", "t0", "ramp")
    cases = [(f, "default", 140, ds.PHI_D) for f in ds.FAMILIES] + \
            [("S", "kappa03", 140, ds.PHI_D), ("DR", "m1_15", 140, ds.PHI_D), ("DR", "default", T_GEN, 0.9)]
    for fam, cname, Tc, phi in cases:
        cell = ds.cell_params(cname)
        q = ds.generate_panel(rng(11), fam, cell, n=300, T=Tc, phi_D=phi)
        r = rng(11)
        p = gen(r, events(r, fam, 300, (50, 101)), fam, n=300, T=Tc, phi=phi, kappa=cell["kappa"], m1=cell["m1"], help_off=False)
        bad = [k for k in keys if not np.array_equal(p[k], q[k], equal_nan=True)]
        assert not bad and p["av_inds"] == q["av_inds"], (fam, cname, bad)
    # (c) composite and CUSUM equal the frozen code ((iv) off, baseline on the scored series)
    f_noiv = ds.ablation_features("iv")
    for help_off in (False, True):
        r = rng(12)
        p = gen(r, events(r, "AV", 300), "AV", n=300, help_off=help_off)
        for B in (28, 56):
            Xs = p["X"].copy()
            Xs[..., J45] = p["X_filtered"][..., J45]
            q = {k: (v[:, :T] if isinstance(v, np.ndarray) and v.ndim >= 2 else v) for k, v in p.items()}
            Cq, rq = ds.compute_composite(q, f_noiv, baseline=ds.fit_baseline(Xs[:, :T], q["used"], q["L_obs"], 0, B))
            z, usable, reason, _ = zscores(p, B)
            assert np.array_equal(composite(z, usable, reason), Cq, equal_nan=True) and np.array_equal(reason, rq)
        a1, _, _ = ds.run_cusum(Cq, 3.0)
        assert np.array_equal(cusum(Cq, 3.0, ds.K_CUSUM), a1)
    assert not p["A"].any() and np.allclose(
        gen(rng(3), events(rng(4), "S", 50), "S", n=50, help_off=True)["H"],
        (lambda q: q["H"] + q["A"][..., None] * ds.PSI)(gen(rng(3), events(rng(4), "S", 50), "S", n=50, help_off=False)),
        atol=1e-12)
    # (d) pairing and observer shifts
    P = panels(77, 0.7, ("S", "PS-sub", "PS-use", "PS-prop", "DR-1.0", "DR+PS"), )
    S = P["S"]
    for fam in ("PS-sub", "PS-use", "PS-prop"):
        assert np.array_equal(P[fam]["D"], S["D"]) and np.array_equal(P[fam]["cday"], P["PS-sub"]["cday"])
        pre = np.arange(T_GEN)[None, :] < P[fam]["cday"][:, None]
        assert np.array_equal(np.where(pre[..., None], P[fam]["X"], 0), np.where(pre[..., None], S["X"], 0), equal_nan=True)
    assert np.array_equal(P["PS-sub"]["used"], S["used"]) and (P["PS-use"]["used"] >= S["used"]).all()
    assert (P["PS-use"]["used"] > S["used"]).any() and np.array_equal(P["DR+PS"]["D"], P["DR-1.0"]["D"])
    zs = zscores(P["PS-sub"], 28, unshifted=True)
    z0 = zscores(S, 28)
    assert np.array_equal(composite(*zs[:3]), composite(*z0[:3]), equal_nan=True), "oracle rule != S"
    # (e) rules: no log entry -> L1 = L2 = L0; L1 holds the whole composite, L2 only the mapped indicators
    for rule in ("L1", "L2"):
        zz = apply_log(S, *z0, rule)
        assert zz[3] is None and zz[0] is z0[0]
    p = P["PS-sub"]
    zp = zscores(p, 28)
    i = int(np.where(~np.isnan(p["log_day"]) & (p["log_day"] < T - 20))[0][0])
    c = int(p["log_day"][i])
    _, u1, r1, reset = apply_log(p, *zp, "L1")
    _, u2, r2, _ = apply_log(p, *zp, "L2")
    assert reset[i, c + 1] and reset[i].sum() == 1 and not u1[i, c + 1:c + 15].any()
    assert not u2[i, c + 1:c + 15][:, list(PS_MAP)].any() and np.array_equal(u2[i, c + 1:c + 15, 2:5], zp[1][i, c + 1:c + 15, 2:5])
    # (f) constants
    assert [lag_for(x) for x in PHIS] == [3, 9, 29] and list(probe_days(28, 4)) == ds.PROBE_BASELINE_DAYS
    assert list(probe_days(28, 8)) == [2, 6, 9, 13, 16, 20, 23, 27] and list(probe_days(56, 4)) == [13, 27, 41, 55]
    # (g) probe rules on a hand-built panel: lag 3, Y = 0 except person 1 from day 28 on (so each of person 1's
    # alarms confirms: probe mean 1 against baseline mean 0), onset 45; person 2 has no alarm
    yp = np.zeros((3, T_GEN))
    yp[1, 28:] = 1.0
    hp = dict(Y=yp, D=np.zeros((3, T_GEN)), responded=np.ones((3, T_GEN), dtype=bool))
    al = np.zeros((3, T), dtype=bool)
    al[0, [30, 32, 40, 60]] = al[1, [30, 35, 50]] = True
    want = {"all": ([4, 3, 0], [0, 3, 0], [0, 1, 0], [0, 2, 0]),  # (probed, confirmed, in [45, 66), before 45)
            "wait": ([3, 2, 0], [0, 2, 0], [0, 1, 0], [0, 1, 0]),  # 30 blocks until 30 + 3 x 3 + 1 = 40
            "stop": ([3, 1, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0])}  # person 1 stops after confirming at 30
    for rule, w in want.items():
        got = probe_rule(hp, al, 3, probe_days(28, 4), 28, np.full(3, 45.0), rule)
        assert all(list(g) == list(x) for g, x in zip(got, w)), (rule, got)
    # (h) verdicts read the keys PREREG-003 cites: the draft's design values, to three decimals
    v = verdicts(json.loads((HERE / "design_003.json").read_text()))
    h3 = v["H3"]["clauses"]
    for got, w in ((v["H2a"], (0.201, 0.155, 0.246)), (h3["L1_PS-sub"], (1.421, 1.175, 1.706)),
                   (h3["L1_PS-use"], (1.376, 1.135, 1.647)), (h3["L2_PS-sub"], (1.171,)), (h3["L2_PS-use"], (1.101,)),
                   (h3["L0_PS-sub"], (3.061, 2.792, 3.380)), (h3["L0_PS-use"], (3.050, 2.790, 3.366)),
                   (v["H1a"], (-0.236, -0.302, -0.173)), (v["H1b"], (0.810, 0.715, 0.916)),
                   (v["H4"], (0.154, 0.100, 0.209)), (v["H5"]["clauses"]["M1"], (0.020, -0.013, 0.053)),
                   (v["H2b"], (-0.003, -0.069, 0.057))):
        assert all(abs(got[k] - x) <= 5e-4 + 1e-9 for k, x in zip(("est", "lo", "hi"), w)), (got, w)  # draft rounds half up
    assert all(v[k]["holds"] for k in ("H1a", "H1b", "H2a", "H3", "H4", "H5")) and v["H2b"]["scored"] is False
    # (i) run_study end to end at n = 60: budget for every phi, verdicts run, L1_step present
    tun = json.loads((HERE / "tuning_003.json").read_text())
    o = run_study(DESIGN_SEED, tun, n=60)
    assert o["n"] == 60 and sorted(o["budget"]) == sorted(f"phi{x}_{f}" for x in PHIS for f in ("S", "DR-1.0", "DR-1.5"))
    assert all(set(r) == {"all", "wait", "stop"} for r in o["budget"].values())
    vo = verdicts(o)
    assert set(vo) >= {"H1a", "H1b", "H2a", "H3", "H4", "H5", "H2b", "H6"} and "L1_step" in vo["H3"] and "L1_step" in vo["H4"]
    print("check OK: events, generator (14 cases) and composite/CUSUM bit-identical with drift_sim; help-off exact; "
          "families paired; oracle rule on PS-sub equals S; L1/L2 inert without a log, hold as specified; lags 3/9/29; "
          "probe rules all/wait/stop on a hand panel; verdicts reproduce the draft's design values; run_study at n 60")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance():
    return {f: sha256(HERE / f) for f in ("study003.py", "drift_sim.py", "attribution.py", "tuning_003.json")}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if cmd == "--check":
        check()
    elif cmd == "tune":
        print(json.dumps(run_tune(), indent=1))
    elif cmd == "design":
        tun = json.loads((HERE / "tuning_003.json").read_text())
        out = dict(label="DESIGN (spec 003 s11): sizes PREREG-003, scores no prediction; not a result",
                   sha256=provenance(), **run_study(DESIGN_SEED, tun))
        (HERE / "design_003.json").write_text(json.dumps(out, indent=1))
    elif cmd == "score":
        sha = sys.argv[sys.argv.index("--prereg-sha") + 1]
        if not PREREG_003.exists() or sha256(PREREG_003) != sha:
            raise RuntimeError("sim/PREREG-003.md is missing or does not match --prereg-sha; no evaluation seed.")
        text = PREREG_003.read_text()
        if not all(sha256(HERE / f) in text for f in ("study003.py", "tuning_003.json")):
            raise RuntimeError("PREREG-003 does not list the current sha256 of study003.py and tuning_003.json.")
        tun = json.loads((HERE / "tuning_003.json").read_text())
        seed = int(hashlib.sha256(f"{sha}:study003".encode()).hexdigest()[:16], 16) % (2**32 - 1)
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else N_SCORE
        out = dict(label="EVALUATION (PREREG-003)", prereg_sha256=sha, sha256=provenance(), **run_study(seed, tun, n))
        out["verdicts"] = verdicts(out)
        (HERE / "results_003.json").write_text(json.dumps(out, indent=1))
    elif cmd == "verdicts":
        print(json.dumps(verdicts(json.loads(Path(sys.argv[2]).read_text())), indent=1))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
