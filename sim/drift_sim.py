"""Drift layer simulation (spec 001, v3). SYNTHETIC ONLY -- no real person's state is estimated.

Passive within-person change detection with sparse probes in a general-purpose agent. One latent `D`;
a non-diagnostic wellbeing/functioning state; it maps to no clinical condition. Every lam, psi, eta, kappa, gam is invented.

    python3 sim/drift_sim.py --check                       # known-answer self test
    python3 sim/drift_sim.py tune                          # tuning-seed-only; writes sim/tuning.json
    python3 sim/drift_sim.py score --prereg-sha <sha>       # NOT to be run pre-freeze; needs a committed PREREG
    python3 sim/drift_sim.py metrics --prereg-sha <sha>     # REPORTING ONLY: PREREG section 5 metrics
                                                             # score() omits; no thresholds, no verdicts;
                                                             # writes sim/metrics.json, sim/METRICS.md
    python3 sim/drift_sim.py robust --plan-sha <sha>        # EXPLORATORY grid, sim/ROBUSTNESS-PLAN.md;
                                                             # NOT part of PREREG/specs; no P1-P10 verdict
                                                             # changes; writes sim/robustness.json,
                                                             # sim/ROBUSTNESS.md

PRE-FREEZE STAGE: this file may be exercised via --check and tune() only. Evaluation seeds come from
eval_seed(), which raises unless sim/PREREG.md exists and its sha256 matches --prereg-sha. Tuning uses
the fixed tuning seed 20260927 and family S (or the S+DR mix), never an evaluation seed.

Ambiguities the spec leaves open, and the choice made here (see also the final report): the "C_{t-1}"
feedback signal for targeted help during generation; the exact causal bootstrapping of A-fixed's own
baseline while that baseline is still being formed; the Beta(pi) / current-control isolation; the
authorship-filter mechanics under continuous daily mixing. Each is flagged at its point of use below with
a comment starting "CHOICE:".
"""

import hashlib
import json
import re
import sys
import time
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

HERE = Path(__file__).parent
PREREG_PATH = HERE / "PREREG.md"
SPEC_PATH = HERE.parent / "specs" / "001-drift-layer" / "spec.md"

# ----------------------------------------------------------------------------------------------
# Constants (section 3-4 of the spec). N_PERSONS is 1000 per spec v3 E1 (was 200 in v2).
# ----------------------------------------------------------------------------------------------
N_PERSONS = 1000
T_DAYS = 140
BASELINE_DAYS = 28
N_IND = 6
IDX_LATE, IDX_FRAG, IDX_DEFER, IDX_MSGLEN, IDX_NEGSELF, IDX_LATENCY = range(6)

PHI_D = 0.7
PHI_L = 0.8
DELTA_D = 1.0
GAM = np.array([0.3, 0.3, 0.3, 0.0, 0.0, 0.3])
PSI = np.array([0.0, 0.5, 0.5, 0.0, 0.0, 0.0])
BETA_CTX_INDICATORS = (IDX_LATE, IDX_MSGLEN, IDX_NEGSELF)
BETA_BY_CTX = (0.0, 0.3, 0.6)  # code, write, personal
CTX_CODE, CTX_WRITE, CTX_PERSONAL = 0, 1, 2
ETA_CTX = 0.1
K_CUSUM = 0.5
REFRACTORY = 14
BAND_LO_FRAC = 0.5  # h/2
CONFIRM_WINDOW = 7
CONFIRM_MARGIN = 0.5
ABSTAIN_USAGE_FRAC = 0.4
ABSTAIN_WINDOW = 14
REBASELINE_WINDOW = 14
BUDGET_TARGET = 3.0  # probes / person-month, post-baseline
MIX_KAPPA_A5 = 0.5
MU_M5 = -1.0
FILTER_SE = 0.9  # P(filter correctly flags true-agent content) -> survival (1-se)
FILTER_SP = 0.95  # P(filter correctly keeps true-human content)
TUNING_SEED = 20260927

# Pilot-supplied placeholders for indicator 4 (constitution II: real, non-inferential authorship
# metadata, not invented). Sourced from pilot/indicator4_params.json ("main_thread", 24 days),
# 2026-09-27. `score()` reads these back from sim/tuning.json and asserts they match sim/PREREG.md.
PI_BAR_DEFAULT = 0.845     # day-mean non-human share of indicator-4 text (pi_bar_daymean)
KAPPA_A4_DEFAULT = 0.547   # agent-text variance for indicator 4 (kappa_a)
MU_M4_DEFAULT = 0.274      # agent-text mean gap, in units of indicator 4's own within-person SD
# KNOWN DEVIATION (recorded again in PREREG.md): the pilot's realized day-level SD of pi is 0.174;
# Beta(10*pi_bar, 10*(1-pi_bar)) at pi_bar=0.845 implies SD = sqrt(pi_bar*(1-pi_bar)/11) = 0.109. The
# spec fixes the Beta concentration at 10 a priori, so this gap is carried, not corrected.

FAMILIES = ["S", "DR", "VA", "SP", "BI", "AV", "DE", "DV", "CS", "BD", "AV2"]
CELL_NAMES = ["default", "kappa03", "m1_05", "m1_15", "targeted", "targeted_theta1_05",
              "bernoulli_mix", "pi_rises_with_D"]


def expit(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def logit(p):
    return np.log(p / (1 - p))


A0_USE = logit(0.8)


def safe_div(a, b, fill=0.0):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    shape = np.broadcast(a, b).shape
    a = np.broadcast_to(a, shape)
    b = np.broadcast_to(b, shape)
    out = np.full(shape, fill, dtype=float)
    ok = np.abs(b) > 1e-12
    np.divide(a, b, out=out, where=ok)
    return out


def bisect(f, lo, hi, target, n_iter=40):
    """Bisect a monotonically DECREASING f(x) to the x where f(x) == target, over n_iter
    halvings of [lo, hi]. For an INCREASING g(x), pass f = lambda x: -g(x) and target = -target
    (the sign flip preserves the same search direction; see call sites in tune_h/tune_schedules/
    check_b). Replaces five separately hand-rolled bisection loops with one implementation."""
    for _ in range(n_iter):
        mid = (lo + hi) / 2
        if f(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def person_slope_corr(mask, C, Y, weight=None):
    """Person-centered (optionally weighted) slope of Y on C, and the pooled correlation,
    restricted to `mask`. One implementation shared by check_c, check_e and score()'s P4/P5
    calibration blocks."""
    num = den = 0.0
    cs, ys = [], []
    for i in range(C.shape[0]):
        m = mask[i]
        if m.sum() < 3:
            continue
        c, y = C[i, m], Y[i, m]
        w = np.ones(m.sum()) if weight is None else weight[i, m]
        wc, wy = np.average(c, weights=w), np.average(y, weights=w)
        cc, yy = c - wc, y - wy
        num += (w * cc * yy).sum()
        den += (w * cc * cc).sum()
        cs.append(cc)
        ys.append(yy)
    b = num / den if den else np.nan
    if cs:
        cat_c, cat_y = np.concatenate(cs), np.concatenate(ys)
        r = np.corrcoef(cat_c, cat_y)[0, 1] if len(cat_c) > 1 else np.nan
    else:
        r = np.nan
    return b, r


# ----------------------------------------------------------------------------------------------
# Cells (section 3): one default cell plus 7 one-at-a-time variations = 8 cells total.
# ----------------------------------------------------------------------------------------------
def cell_params(name):
    p = dict(kappa=0.0, m1=0.0, theta1=0.0, help_mode="constant", mix_mode="beta", pi_rises=False)
    if name == "default":
        pass
    elif name == "kappa03":
        p["kappa"] = 0.3
    elif name == "m1_05":
        p["m1"] = 0.5
    elif name == "m1_15":
        p["m1"] = 1.5
    elif name == "targeted":
        p["help_mode"] = "targeted"
    elif name == "targeted_theta1_05":
        p["help_mode"] = "targeted"
        p["theta1"] = 0.5
    elif name == "bernoulli_mix":
        p["mix_mode"] = "bernoulli"
    elif name == "pi_rises_with_D":
        p["mix_mode"] = "beta"
        p["pi_rises"] = True
    else:
        raise ValueError(f"unknown cell {name!r}")
    return p


# ----------------------------------------------------------------------------------------------
# eval_seed: evaluation seeds are derived from the committed, hashed PREREG. This function is the
# ONLY sanctioned way to get a family/cell evaluation seed; it refuses to run pre-freeze.
# ----------------------------------------------------------------------------------------------
def eval_seed(prereg_sha256, family, cell):
    if not PREREG_PATH.exists():
        raise RuntimeError("sim/PREREG.md is missing; cannot derive an evaluation seed pre-freeze.")
    on_disk = hashlib.sha256(PREREG_PATH.read_bytes()).hexdigest()
    if on_disk != prereg_sha256:
        raise RuntimeError(
            f"--prereg-sha {prereg_sha256!r} does not match sim/PREREG.md's sha256 {on_disk!r}. "
            "Evaluation seeds are only derived from the committed, frozen PREREG."
        )
    tag = f"{prereg_sha256}:{family}:{cell}".encode()
    return int(hashlib.sha256(tag).hexdigest()[:16], 16) % (2**32 - 1)


# ----------------------------------------------------------------------------------------------
# Family event sampling (section 3). Each family activates only its own mechanism(s); this keeps
# the 11 families mutually exclusive scenario channels, run one at a time.
# ----------------------------------------------------------------------------------------------
def sample_events(rng, family, n):
    ev = dict(t0=np.full(n, np.nan), ramp=np.full(n, np.nan),
              vac_start=np.full(n, np.nan), vac_len=np.full(n, np.nan),
              sprint_start=np.full(n, np.nan), sprint_len=np.full(n, np.nan),
              bi_start=np.full(n, np.nan), bi_len=np.full(n, np.nan),
              av_day=np.full(n, np.nan), av_logged=np.zeros(n, dtype=bool),
              cs_day=np.full(n, np.nan), de_day=np.full(n, np.nan))
    drift = family in ("DR", "DV", "BD")
    if drift:
        if family == "BD":
            ev["t0"] = rng.integers(10, 26, n).astype(float)  # U[10,25]
        else:
            ev["t0"] = rng.integers(50, 101, n).astype(float)  # U[50,100]
        ev["ramp"] = rng.integers(7, 22, n).astype(float)  # U[7,21]
    if family in ("VA", "DV"):
        ev["vac_len"] = rng.integers(7, 15, n).astype(float)  # 7-14 days
        if family == "DV":
            lo, hi = ev["t0"] - 5, ev["t0"] + 5
            ev["vac_start"] = lo + rng.random(n) * (hi - lo)
        else:
            ev["vac_start"] = rng.integers(50, 101, n).astype(float)
    if family == "SP":
        ev["sprint_len"] = rng.integers(10, 15, n).astype(float)  # 10-14 days
        ev["sprint_start"] = rng.integers(50, 101, n).astype(float)
    if family == "BI":
        ev["bi_len"] = rng.integers(10, 21, n).astype(float)  # 10-20 days
        ev["bi_start"] = rng.integers(50, 101, n).astype(float)
    if family in ("AV", "AV2"):
        ev["av_day"] = rng.integers(50, 101, n).astype(float)
        if family == "AV":
            ev["av_logged"] = rng.random(n) < 0.5
        # AV2 never logged (all False, already the default).
    if family == "DE":
        ev["de_day"] = rng.integers(50, 101, n).astype(float)
    if family == "CS":
        ev["cs_day"] = rng.integers(50, 101, n).astype(float)
    return ev


def ar1_panel(rng, n, T, phi):
    """Stationary AR(1), marginal SD 1, shape (n, T)."""
    z = rng.standard_normal((n, T))
    x = np.empty((n, T))
    x[:, 0] = z[:, 0]
    for t in range(1, T):
        x[:, t] = phi * x[:, t - 1] + np.sqrt(1 - phi**2) * z[:, t]
    return x


def sample_ctx(rng, D, family, cs_day):
    n, T = D.shape
    day = np.arange(T)[None, :]
    if family == "CS":
        switched = day >= cs_day[:, None]
        base = np.where(switched[..., None], np.array([0.1, 0.2, 0.7]), np.array([0.5, 0.3, 0.2]))
    else:
        base = np.broadcast_to(np.array([0.5, 0.3, 0.2]), (n, T, 3)).copy()
    logit_write = np.log(base[..., 1] / base[..., 0])
    logit_personal = np.log(base[..., 2] / base[..., 0]) + ETA_CTX * D
    logits = np.stack([np.zeros((n, T)), logit_write, logit_personal], axis=-1)
    m = logits.max(-1, keepdims=True)
    p = np.exp(logits - m)
    p /= p.sum(-1, keepdims=True)
    cdf = np.cumsum(p, axis=-1)
    u = rng.random((n, T, 1))
    ctx = (u > cdf).sum(-1)  # 0=code,1=write,2=personal
    return ctx


def rolling_sum(x, window):
    """Trailing rolling sum over the last `window` days (inclusive of day t), day 0 padded with itself."""
    n, T = x.shape
    c = np.cumsum(x, axis=1)
    out = np.empty_like(c)
    out[:, :window] = c[:, :window]  # partial windows at the start use whatever is available
    out[:, window:] = c[:, window:] - c[:, :-window]
    return out


# ----------------------------------------------------------------------------------------------
# Baseline stats and the A-fixed composite. Both A-naive and A-fixed (and its ablations) share this
# machinery; `features` toggles which of (i)-(v) are active. `pop_ref` (mu, sd) switches to the
# population-level baseline used by the `pop` architecture.
# ----------------------------------------------------------------------------------------------
def fit_baseline(X, used, L_obs, day_lo=0, day_hi=BASELINE_DAYS):
    """Per-person mean/sd per indicator, per-person OLS slope on L_obs, and baseline usage rate,
    all fit on days [day_lo, day_hi) using used & available observations. Fallback mean 0 / sd 1 /
    slope 0 when too few observations (documented CHOICE: no spec-given fallback)."""
    n, T, J = X.shape
    Xb = X[:, day_lo:day_hi, :]
    ub = used[:, day_lo:day_hi]
    ok = ub[..., None] & ~np.isnan(Xb)
    cnt = ok.sum(1)
    xsum = np.where(ok, Xb, 0.0).sum(1)
    mean = safe_div(xsum, cnt)
    mean = np.where(cnt >= 2, mean, 0.0)
    var = np.where(ok, (Xb - mean[:, None, :]) ** 2, 0.0).sum(1)
    sd = np.sqrt(safe_div(var, np.maximum(cnt - 1, 1)))
    sd = np.where((cnt >= 2) & (sd > 1e-6), sd, 1.0)
    # per-person slope of each indicator on L_obs, baseline window, OLS through (indicator, L_obs)
    Lb = L_obs[:, day_lo:day_hi]
    slope = np.zeros((n, J))
    for j in range(J):
        okj = ub & ~np.isnan(Xb[:, :, j])
        cj = okj.sum(1)
        lm = safe_div(np.where(okj, Lb, 0.0).sum(1), cj)
        xm = safe_div(np.where(okj, Xb[:, :, j], 0.0).sum(1), cj)
        cov = np.where(okj, (Lb - lm[:, None]) * (Xb[:, :, j] - xm[:, None]), 0.0).sum(1)
        varl = np.where(okj, (Lb - lm[:, None]) ** 2, 0.0).sum(1)
        s = safe_div(cov, varl)
        slope[:, j] = np.where(cj >= 3, s, 0.0)
    usage_rate = used[:, day_lo:day_hi].mean(1)
    lmean = Lb.mean(1)
    return dict(mean=mean, sd=sd, slope=slope, usage_rate=usage_rate, lmean=lmean)


DEFAULT_FEATURES = dict(unhelped_filter=True, authorship_filter=True, residualize=True,
                         version_reset=True, low_usage_abstain=True)
NAIVE_FEATURES = dict(unhelped_filter=False, authorship_filter=False, residualize=False,
                       version_reset=False, low_usage_abstain=False)


def ablation_features(remove):
    f = dict(DEFAULT_FEATURES)
    key = {"i": "unhelped_filter", "ii": "authorship_filter", "iii": "residualize",
           "iv": "version_reset", "v": "low_usage_abstain"}[remove]
    f[key] = False
    return f


def compute_composite(panel, features, baseline=None, pop_ref=None):
    """The composite C_t (n, T) with NaN on held days, plus a reason code (n, T) int:
    0 assessed, 1 unused day, 2 no usable indicator, 3 low-usage abstention (v),
    4 version-change re-baseline hold (iv). Reuses X_analysis, which already carries the
    authorship-filter substitution (ii) when panel['pi_prime'] is used upstream; here (ii) just
    picks which of X / X_filtered feeds indicators 3,4."""
    X = panel["X"].copy()
    used = panel["used"]
    A = panel["A"]
    L_obs = panel["L_obs"]
    n, T, J = X.shape
    if features["authorship_filter"]:
        X[:, :, IDX_MSGLEN] = panel["X_filtered"][:, :, IDX_MSGLEN]
        X[:, :, IDX_NEGSELF] = panel["X_filtered"][:, :, IDX_NEGSELF]

    usable = used[..., None] & ~np.isnan(X)
    if features["unhelped_filter"]:
        helped = A[..., None] & np.isin(np.arange(J), [IDX_FRAG, IDX_DEFER])[None, None, :]
        usable = usable & ~helped

    if pop_ref is not None:
        mean, sd = pop_ref["mean"], pop_ref["sd"]
        mean = np.broadcast_to(mean, (n, J))
        sd = np.broadcast_to(sd, (n, J))
        slope = np.zeros((n, J))
        lmean = np.zeros(n)
        usage_rate = np.full(n, 0.8)
    else:
        mean, sd, slope, lmean, usage_rate = (baseline["mean"], baseline["sd"], baseline["slope"],
                                               baseline["lmean"], baseline["usage_rate"])

    Xr = X.copy()
    if features["residualize"]:
        for j in (IDX_LATE, IDX_FRAG, IDX_DEFER, IDX_LATENCY):
            Xr[:, :, j] = X[:, :, j] - slope[:, j][:, None] * (L_obs - lmean[:, None])

    z = safe_div(Xr - mean[:, None, :], sd[:, None, :])
    z = np.where(usable, z, np.nan)

    hold_window = None
    if features["version_reset"] and panel.get("av_day") is not None:
        z, usable, hold_window = _apply_version_reset(panel, z, usable, Xr, used)

    reason = np.zeros((n, T), dtype=int)
    reason[~used] = 1
    no_ind = usable.sum(-1) == 0
    reason[no_ind & used] = 2

    if features["low_usage_abstain"]:
        trail = rolling_sum(used.astype(float), ABSTAIN_WINDOW)
        cut = ABSTAIN_USAGE_FRAC * usage_rate[:, None] * ABSTAIN_WINDOW
        low = trail < cut
        reason[low & (reason == 0)] = 3
        usable = usable & ~low[..., None]

    if hold_window is not None:
        reason[hold_window & used] = 4  # version-change re-baseline hold (iv) takes label priority

    cnt = usable.sum(-1)
    C = np.where(cnt > 0, np.where(usable, z, 0.0).sum(-1) / np.maximum(cnt, 1), np.nan)
    C = np.where(reason > 0, np.nan, C)
    return C, reason


def _apply_version_reset(panel, z, usable, Xr, used):
    """Feature (iv): at a LOGGED version change, hold S for 14 days, then re-baseline indicators
    2 and 6 (AV) / 1 and 4 (AV2) over that 14-day window and use the new baseline afterward."""
    n, T = used.shape
    av_day = panel["av_day"]
    logged = panel["av_logged"]
    changed_inds = panel["av_inds"]
    has_event = ~np.isnan(av_day) & logged
    if not has_event.any():
        return z, usable, np.zeros((n, T), dtype=bool)
    day = np.arange(T)[None, :]
    ad = np.where(np.isnan(av_day), np.inf, av_day)[:, None]
    hold_window = has_event[:, None] & (day > ad) & (day <= ad + REBASELINE_WINDOW)
    usable = usable & ~hold_window[..., None]
    after_window = has_event[:, None] & (day > ad + REBASELINE_WINDOW)
    lo = np.clip(av_day, 0, T - 1).astype(int)
    for j in changed_inds:
        # re-baseline mean/sd for indicator j from the 14 days right after the change
        vals = np.full((n, REBASELINE_WINDOW), np.nan)
        for k in range(REBASELINE_WINDOW):
            idx = np.clip(lo + 1 + k, 0, T - 1)
            row = Xr[np.arange(n), idx, j]
            u = used[np.arange(n), idx]
            vals[:, k] = np.where(u & has_event, row, np.nan)
        cnt = (~np.isnan(vals)).sum(1)
        m = np.nanmean(vals, axis=1)
        m = np.where(cnt >= 2, m, 0.0)
        sdv = np.nanstd(vals, axis=1, ddof=1)
        sdv = np.where((cnt >= 2) & (sdv > 1e-6), sdv, 1.0)
        znew = safe_div(Xr[:, :, j] - m[:, None], sdv[:, None])
        z[:, :, j] = np.where(after_window & has_event[:, None], znew, z[:, :, j])
    return z, usable, hold_window


# ----------------------------------------------------------------------------------------------
# CUSUM. One-sided, k in the composite's own units (NOT re-standardized). Refractory: after an
# alarm, S resets to 0 and continues updating normally, but a new alarm cannot fire for 14 days
# (CHOICE: "hold" (abstention, frozen S) and "refractory" (blocked re-alarm, S still moves) are
# kept distinct -- the spec's confirmation window of 7 days sits inside the 14-day refractory,
# which only makes sense if S is still live during it).
# ----------------------------------------------------------------------------------------------
def run_cusum(C, h, k=K_CUSUM, refractory=REFRACTORY):
    n, T = C.shape
    S = np.zeros(n)
    refr = np.zeros(n, dtype=int)
    alarm_day = np.full((n, T), False)
    in_band = np.full((n, T), False)
    Strace = np.zeros((n, T))
    for t in range(T):
        c = C[:, t]
        held = np.isnan(c)
        S = np.where(held, S, np.maximum(0.0, S + np.where(held, 0.0, c) - k))
        Strace[:, t] = S
        can_alarm = (refr <= 0) & ~held
        newly = can_alarm & (S >= h)
        alarm_day[:, t] = newly
        in_band[:, t] = (~held) & (S >= h * BAND_LO_FRAC) & (S < h)
        S = np.where(newly, 0.0, S)
        refr = np.where(newly, refractory, np.maximum(refr - 1, 0))
    return alarm_day, in_band, Strace


# ----------------------------------------------------------------------------------------------
# Probe schedules. Baseline block (days 7,14,21,28) is common to every schedule except `none`.
# ----------------------------------------------------------------------------------------------
def probe_schedule(rng, schedule, C, in_band, p_trig=None, p_trig2=None, c_star=None):
    n, T = C.shape
    probed = np.zeros((n, T), dtype=bool)
    prop = np.zeros((n, T))
    identified = schedule in ("random", "mixed")
    if schedule == "none":
        return probed, prop, identified
    base_days = [6, 13, 20, 27]
    probed[:, base_days] = True
    prop[:, base_days] = 1.0
    post = np.arange(28, T)
    if schedule == "fixed":
        fdays = list(range(37, T, 10))  # every 10 days after the baseline (day 38, 48, ...)
        probed[:, fdays] = True
        prop[:, fdays] = 1.0
    elif schedule == "random":
        prop[:, post] = 0.1
        probed[:, post] = rng.random((n, len(post))) < 0.1
    elif schedule == "triggered":
        band_post = in_band[:, post]
        prop[:, post] = np.where(band_post, p_trig, 0.0)
        probed[:, post] = rng.random((n, len(post))) < prop[:, post]
    elif schedule == "mixed":
        band_post = in_band[:, post]
        prop[:, post] = np.clip(np.where(band_post, 0.04 + p_trig2, 0.04), 0, 1)
        probed[:, post] = rng.random((n, len(post))) < prop[:, post]
    elif schedule == "current":
        cpost = C[:, post]
        hit = (~np.isnan(cpost)) & (cpost > c_star)
        probed[:, post] = hit
        prop[:, post] = np.where(hit, 1.0, 0.0)  # deterministic control, not IPW-eligible
        identified = False
    else:
        raise ValueError(schedule)
    return probed, prop, identified


def expected_budget_per_month(prop, T=T_DAYS, baseline=BASELINE_DAYS):
    """Expected probes/month from the logged propensities directly (noise-free): used for bisection
    during tuning so the search target is a deterministic function of the tuned parameter, not a
    fresh stochastic draw each iteration."""
    post_months = (T - baseline) / 30.0
    return prop[:, baseline:].sum(1).mean() / post_months


# ----------------------------------------------------------------------------------------------
# Logistic regression via Newton-Raphson / IRLS (numpy only), used for the response-propensity
# IPW in P5.
# ----------------------------------------------------------------------------------------------
def logistic_irls(Xd, y, n_iter=50, ridge=1e-6, tol=1e-10):
    n, p = Xd.shape
    beta = np.zeros(p)
    for _ in range(n_iter):
        eta = Xd @ beta
        mu = expit(eta)
        w = np.clip(mu * (1 - mu), 1e-6, None)
        z = eta + (y - mu) / w
        WX = Xd * w[:, None]
        H = Xd.T @ WX + ridge * np.eye(p)
        g = Xd.T @ (w * z)
        beta_new = np.linalg.solve(H, g)
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta


def dow_features(T, offset=0):
    d = (np.arange(T) + offset) % 7
    ang = 2 * np.pi * d / 7
    return np.stack([np.ones(T), np.sin(ang), np.cos(ang)], axis=-1)  # (T, 3)


# ----------------------------------------------------------------------------------------------
# Generator.
# ----------------------------------------------------------------------------------------------
def mix_authorship(H_col, pi_arr, M_col):
    """Shared authorship-mixing formula for indicators 4, 5 (message length, negative
    self-reference): the spec's daily-averaging mechanism, X = (1 - pi) H + pi M. One
    implementation used for both the unfiltered X (mixed with pi) and the authorship-filtered
    X_filtered (mixed with pi')."""
    return (1 - pi_arr) * H_col + pi_arr * M_col


def apply_bi_mask(arr, bi_mask):
    """Broken integration (BI): indicators 1 (late-activity share) and 6 (reply latency) are
    missing for the bi_mask window. Applied identically to H, X and X_filtered -- `arr` may be
    a full (n, T, J) array or a single day's (n, J) slice; bi_mask is all-False for every family
    but BI, so this is a no-op elsewhere."""
    arr = arr.copy()
    arr[..., IDX_LATE] = np.where(bi_mask, np.nan, arr[..., IDX_LATE])
    arr[..., IDX_LATENCY] = np.where(bi_mask, np.nan, arr[..., IDX_LATENCY])
    return arr


def generate_panel(rng, family, cell, n=N_PERSONS, T=T_DAYS,
                    pi_bar=PI_BAR_DEFAULT, kappa_a4=KAPPA_A4_DEFAULT, mu_m4=MU_M4_DEFAULT,
                    lam_range=(0.25, 0.5), phi_D=PHI_D, psi=PSI, rising_slope=0.5):
    """One generated world for a family x cell combination. Returns a dict with every array the
    architectures and metrics need. `A` (help) and `X` (indicators 4,5 authorship-mixed already
    applied) are shared across every downstream architecture and schedule for this same panel --
    the shared-persons / paired-bootstrap design of spec v3.

    `phi_D`, `psi` and `rising_slope` (added for `robust`, sim/ROBUSTNESS-PLAN.md) default to the
    exact frozen constants PHI_D, PSI and 0.5 -- every existing call site that omits them is
    bit-identical to before this change. They only thread the already-frozen mechanism through
    (D's own AR(1) persistence, indicators 2/3's help-effect array, the pi_rises branch's coupling
    slope); no generator mechanics change."""
    ev = sample_events(rng, family, n)
    D = ar1_panel(rng, n, T, phi_D)
    if not np.all(np.isnan(ev["t0"])):
        day = np.arange(T)[None, :]
        ramp = np.clip((day - ev["t0"][:, None]) / ev["ramp"][:, None], 0, 1) * DELTA_D
        D = D + ramp

    L = ar1_panel(rng, n, T, PHI_L)
    if family == "SP":
        day = np.arange(T)[None, :]
        in_sprint = (day >= ev["sprint_start"][:, None]) & (day < (ev["sprint_start"] + ev["sprint_len"])[:, None])
        L = L + 1.5 * in_sprint
    L_obs = L + rng.normal(0, np.sqrt(0.25), (n, T))

    ctx = sample_ctx(rng, D, family, ev["cs_day"])

    vacation = np.zeros((n, T), dtype=bool)
    if family in ("VA", "DV"):
        day = np.arange(T)[None, :]
        vacation = (day >= ev["vac_start"][:, None]) & (day < (ev["vac_start"] + ev["vac_len"])[:, None])
    diseng = np.zeros((n, T), dtype=bool)
    if family == "DE":
        day = np.arange(T)[None, :]
        diseng = day >= ev["de_day"][:, None]

    p_use = expit(A0_USE - cell["kappa"] * D - 4 * vacation - 2 * diseng)
    used = rng.random((n, T)) < p_use

    lam = rng.uniform(*lam_range, (n, N_IND))
    e = rng.standard_normal((n, T, N_IND))
    beta_ctx = np.zeros((n, T, N_IND))
    for j in BETA_CTX_INDICATORS:
        beta_ctx[:, :, j] = np.select([ctx == CTX_CODE, ctx == CTX_WRITE, ctx == CTX_PERSONAL], BETA_BY_CTX)

    av_day = ev["av_day"] if family in ("AV", "AV2") else np.full(n, np.nan)
    av_logged = ev["av_logged"] if family == "AV" else np.zeros(n, dtype=bool)
    av_inds = (IDX_FRAG, IDX_LATENCY) if family == "AV" else (IDX_LATE, IDX_MSGLEN)
    lam_mult = np.ones((n, T, N_IND))
    mean_shift = np.zeros((n, T, N_IND))
    if family in ("AV", "AV2"):
        day = np.arange(T)[None, :]
        after = day >= av_day[:, None]
        for j in av_inds:
            lam_mult[:, :, j] = np.where(after, 0.7, 1.0)
            mean_shift[:, :, j] = np.where(after, 0.5, 0.0)

    bi_mask = np.zeros((n, T), dtype=bool)
    if family == "BI":
        day = np.arange(T)[None, :]
        bi_mask = (day >= ev["bi_start"][:, None]) & (day < (ev["bi_start"] + ev["bi_len"])[:, None])

    # authorship mixing (indicators 4,5 i.e. IDX_MSGLEN, IDX_NEGSELF)
    # CHOICE / pilot-units note: the pilot reports mu_M4 in units of indicator 4's own within-person
    # SD ("mu_M4_humanSD"), not the spec's original raw-scale placeholder convention (+1.0 was raw).
    # `mu_m4` is therefore interpreted here as human-SD units and converted to the raw scale using
    # H4's own population mean/SD -- exact, not approximate, because PSI[IDX_MSGLEN] = 0 so H4 does
    # not depend on A_t at all and can be computed before any help-mode branching.
    H4_raw = (lam[:, None, IDX_MSGLEN] * lam_mult[:, :, IDX_MSGLEN] * D + GAM[IDX_MSGLEN] * L
              + beta_ctx[:, :, IDX_MSGLEN] + e[:, :, IDX_MSGLEN] + mean_shift[:, :, IDX_MSGLEN])
    ub = used[:, :BASELINE_DAYS]
    h4b = H4_raw[:, :BASELINE_DAYS][ub]
    pop_mean_h4, pop_sd_h4 = h4b.mean(), h4b.std(ddof=1)
    mu_m4_raw = pop_mean_h4 + mu_m4 * pop_sd_h4
    mu_m = np.array([mu_m4_raw, -1.0])
    kap_m = np.array([kappa_a4, MIX_KAPPA_A5])
    if cell["mix_mode"] == "bernoulli":
        pi_t = (rng.random((n, T)) < pi_bar).astype(float)
    elif cell["pi_rises"]:
        pi_t = expit(logit(pi_bar) + rising_slope * D)
    else:
        a, b = 10 * pi_bar, 10 * (1 - pi_bar)
        pi_t = rng.beta(a, b, (n, T))
    M = np.stack([rng.normal(mu_m[k], np.sqrt(kap_m[k]), (n, T)) for k in range(2)], axis=-1)

    def build_H_X(A):
        H = (lam[:, None, :] * lam_mult) * D[:, :, None] + GAM[None, None, :] * L[:, :, None] \
            + beta_ctx - (A[:, :, None] * psi[None, None, :] * (1 + cell["theta1"] * D[:, :, None])) \
            + e + mean_shift
        X = H.copy()
        for k, j in enumerate((IDX_MSGLEN, IDX_NEGSELF)):
            X[:, :, j] = mix_authorship(H[:, :, j], pi_t, M[:, :, k])
        H = apply_bi_mask(H, bi_mask)
        X = apply_bi_mask(X, bi_mask)
        X = np.where(used[:, :, None], X, np.nan)
        return H, X

    pi_prime = 0.1 * pi_t / (0.1 * pi_t + 0.95 * (1 - pi_t) + 1e-12)

    def build_X_filtered(H, pi_prime_arr):
        Xf = H.copy()
        for k, j in enumerate((IDX_MSGLEN, IDX_NEGSELF)):
            Xf[:, :, j] = mix_authorship(H[:, :, j], pi_prime_arr, M[:, :, k])
        Xf = apply_bi_mask(Xf, bi_mask)
        Xf = np.where(used[:, :, None], Xf, np.nan)
        return Xf

    if cell["help_mode"] == "constant":
        A = rng.random((n, T)) < 0.3
        H, X = build_H_X(A)
        X_filtered = build_X_filtered(H, pi_prime)
    else:
        # CHOICE: baseline (days 0-27) always uses constant help p=0.3 -- A-fixed's own baseline
        # cannot be causally available before day 28, so targeting can only start once it is.
        A = np.zeros((n, T), dtype=bool)
        A[:, :BASELINE_DAYS] = rng.random((n, BASELINE_DAYS)) < 0.3
        Hfull, Xfull = build_H_X(A)  # A is False past day 28 here; only the baseline slice is used
        Xfull_filtered = build_X_filtered(Hfull, pi_prime)
        H = np.zeros((n, T, N_IND))
        X = np.full((n, T, N_IND), np.nan)
        X_filtered = np.full((n, T, N_IND), np.nan)
        H[:, :BASELINE_DAYS] = Hfull[:, :BASELINE_DAYS]
        X[:, :BASELINE_DAYS] = Xfull[:, :BASELINE_DAYS]
        X_filtered[:, :BASELINE_DAYS] = Xfull_filtered[:, :BASELINE_DAYS]
        base = fit_baseline(X[:, :BASELINE_DAYS], used[:, :BASELINE_DAYS], L_obs[:, :BASELINE_DAYS],
                             0, BASELINE_DAYS)
        # CHOICE: A-fixed's own composite (the C_{t-1} feedback signal for targeted help) is
        # computed via the SAME compute_composite() code path A-fixed's post-hoc scoring uses --
        # features (i)-(iii) and (v) active, (iv) omitted (PREREG deviation 4 already states this),
        # not a hand-duplicated formula. It is recomputed on the history through day t-1 each
        # iteration: O(T^2) but T <= 140, and only ever exercised by help_mode='targeted', never by
        # tuning (which always uses cell='default', help_mode='constant'). A day compute_composite
        # holds (C is NaN) HOLDS the feedback signal at its last known value, mirroring how the
        # CUSUM's own S is held on a held day -- it is not reset to 0.
        features_targeted = ablation_features("iv")
        last_c = np.zeros(n)
        for t in range(BASELINE_DAYS, T):
            tm1 = t - 1
            panel_partial = dict(X=X[:, :t, :], X_filtered=X_filtered[:, :t, :], used=used[:, :t],
                                  A=A[:, :t], L_obs=L_obs[:, :t], av_day=None)
            C_hist, _ = compute_composite(panel_partial, features_targeted, baseline=base)
            Cprev = C_hist[:, -1]
            Cprev = np.where(np.isnan(Cprev), last_c, Cprev)
            last_c = Cprev
            p_t = np.clip(expit(logit(0.3) + Cprev), 0.1, 0.9)
            A[:, t] = rng.random(n) < p_t
            # single-day slice of the same formula build_H_X uses, to avoid recomputing H for every
            # prior day inside this loop.
            Ht = ((lam * lam_mult[:, t, :]) * D[:, t][:, None] + GAM[None, :] * L[:, t][:, None]
                  + beta_ctx[:, t, :]
                  - (A[:, t][:, None] * psi[None, :] * (1 + cell["theta1"] * D[:, t][:, None]))
                  + e[:, t, :] + mean_shift[:, t, :])
            Xt = Ht.copy()
            Xt[:, IDX_MSGLEN] = mix_authorship(Ht[:, IDX_MSGLEN], pi_t[:, t], M[:, t, 0])
            Xt[:, IDX_NEGSELF] = mix_authorship(Ht[:, IDX_NEGSELF], pi_t[:, t], M[:, t, 1])
            Xft = Ht.copy()
            Xft[:, IDX_MSGLEN] = mix_authorship(Ht[:, IDX_MSGLEN], pi_prime[:, t], M[:, t, 0])
            Xft[:, IDX_NEGSELF] = mix_authorship(Ht[:, IDX_NEGSELF], pi_prime[:, t], M[:, t, 1])
            Ht = apply_bi_mask(Ht, bi_mask[:, t])
            Xt = apply_bi_mask(Xt, bi_mask[:, t])
            Xft = apply_bi_mask(Xft, bi_mask[:, t])
            Xt = np.where(used[:, t][:, None], Xt, np.nan)
            Xft = np.where(used[:, t][:, None], Xft, np.nan)
            H[:, t, :], X[:, t, :], X_filtered[:, t, :] = Ht, Xt, Xft

    Y = D + rng.normal(0, np.sqrt(1 / 0.7 - 1), (n, T))
    resp_p = expit(logit(0.8) - cell["m1"] * D)
    responded = rng.random((n, T)) < resp_p

    return dict(family=family, D=D, L=L, L_obs=L_obs, ctx=ctx, used=used, A=A, H=H, X=X,
                X_filtered=X_filtered, pi_t=pi_t, pi_prime=pi_prime, Y=Y, resp_p=resp_p,
                responded=responded, av_day=av_day, av_logged=av_logged, av_inds=av_inds,
                bi_mask=bi_mask, t0=ev["t0"], ramp=ev["ramp"], vac_start=ev["vac_start"],
                vac_len=ev["vac_len"])


# ----------------------------------------------------------------------------------------------
# --check : known-answer tests (a)-(i).
# ----------------------------------------------------------------------------------------------
def check_a(verbose):
    """(a) lam=0 -> within-person validity of every indicator ~ 0. Uses generate_panel's own
    `lam_range` argument (forced to (0, 0)) instead of a hand-built copy of the generator."""
    rng = np.random.default_rng(1)
    cell = cell_params("default")
    n = 300
    panel = generate_panel(rng, "S", cell, n=n, lam_range=(0.0, 0.0))
    H, D, used = panel["H"], panel["D"], panel["used"]
    valid = []
    for j in range(N_IND):
        hj = np.where(used, H[:, :, j], np.nan)
        r = np.array([np.corrcoef(hj[i][~np.isnan(hj[i])], D[i][~np.isnan(hj[i])])[0, 1]
                       for i in range(n) if (~np.isnan(hj[i])).sum() > 5])
        valid.append(np.nanmean(r))
    ok = all(abs(v) < 0.06 for v in valid)
    if verbose:
        print("  (a) lam=0 per-indicator within-person r(H,D):", np.round(valid, 4), "-> OK" if ok else "FAIL")
    return ok, valid


def check_b(verbose):
    """(b) no drift, S held -> CUSUM false-alarm rate under A-naive matches a direct simulation.
    `h` is bisected on the pipeline's own composite to a moderate, easy-to-verify operating point
    (not the deployed 1/6-month target, which is too high to compare at this n/T without huge MC
    noise); the same h is then applied to an i.i.d. surrogate with the pipeline's empirical
    tracked-C variance, and the two false-alarm rates are compared."""
    rng = np.random.default_rng(2)
    cell = cell_params("default")
    n = 1000
    panel = generate_panel(rng, "S", cell, n=n)
    baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
    C, reason = compute_composite(panel, NAIVE_FEATURES, baseline=baseline)

    target = 2.0  # a moderate FA/month target, just for a well-powered comparison
    h_probe = bisect(lambda mid: fa_rate_for_h(C, mid, reason), 0.1, 20.0, target, n_iter=30)
    fa_from_pipeline = fa_rate_for_h(C, h_probe, reason)

    rng2 = np.random.default_rng(2)
    Craw = rng2.standard_normal((n, T_DAYS))
    sd_pipeline = np.nanstd(C[:, BASELINE_DAYS:])
    Craw = Craw * sd_pipeline
    reason_direct = np.zeros((n, T_DAYS), dtype=int)
    fa_direct = fa_rate_for_h(Craw, h_probe, reason_direct)
    ratio = fa_from_pipeline / fa_direct if fa_direct > 0 else np.nan
    ok = 0.5 < ratio < 2.0
    if verbose:
        print(f"  (b) h={h_probe:.3f} FA/month pipeline={fa_from_pipeline:.4f} "
              f"direct-iid-matched-sd={fa_direct:.4f} ratio={ratio:.3f} -> {'OK' if ok else 'FAIL'}")
    return ok, (fa_from_pipeline, fa_direct)


def check_c(verbose, n=8000, T=140):
    """(c) `current` control (common lam, population z-scaling) leaves the slope within 5% relative.
    A direct, isolated translation of the reviewer's p4check.py mechanism. `c_star` is a single fixed
    operating point, calibrated once on the no-drift world and then applied unchanged to the drift
    world -- matching how a real deployment would calibrate a threshold once, not re-pick it per
    family."""
    rng = np.random.default_rng(3)
    lam = 0.375
    results = {}
    c_star = None
    for drift in (False, True):
        D = ar1_panel(rng, n, T, PHI_D)
        if drift:
            t0 = rng.integers(50, 101, n)
            r = rng.integers(7, 22, n)
            day = np.arange(T)[None, :]
            D = D + np.clip((day - t0[:, None]) / r[:, None], 0, 1)
        X = lam * D[:, :, None] + rng.standard_normal((n, T, 6))
        pop_mean = X[:, :BASELINE_DAYS, :].mean((0, 1))
        pop_sd = X[:, :BASELINE_DAYS, :].std((0, 1), ddof=1)
        z = (X - pop_mean) / pop_sd
        C = z.mean(-1)
        Y = D + rng.normal(0, np.sqrt(1 / 0.7 - 1), (n, T))
        if c_star is None:
            c_star = np.nanpercentile(C[:, BASELINE_DAYS:], 90)  # calibrated once, on the no-drift world
        m = np.zeros((n, T), dtype=bool)
        m[:, BASELINE_DAYS:] = True
        probed_cur = np.zeros((n, T), dtype=bool)
        probed_cur[:, BASELINE_DAYS:] = C[:, BASELINE_DAYS:] > c_star

        b_all = person_slope_corr(m, C, Y)[0]
        b_cur = person_slope_corr(probed_cur, C, Y)[0]
        rel = abs(b_cur - b_all) / abs(b_all)
        results[drift] = (b_all, b_cur, rel)
    ok = all(rel < 0.05 for _, _, rel in results.values())
    if verbose:
        for d, (a, c, r) in results.items():
            print(f"  (c) current-control drift={d}: all-days slope={a:.4f} current slope={c:.4f} "
                  f"rel diff={r:.4f} -> {'OK' if r < 0.05 else 'FAIL'}")
    return ok, results


def check_d(verbose, n=2_000_000):
    """(d) P6 formula matches simulated attenuation under averaging (fixed pi and Beta pi) and
    Bernoulli mixing, within MC error at large n. Direct translation of p56check.py's mechanism,
    extended to Beta(pi) and to the per-person V_H formulation used in P6."""
    rng = np.random.default_rng(4)
    lam = 0.4
    D = rng.standard_normal(n)
    H = lam * D + rng.standard_normal(n) * np.sqrt(1 - lam**2)
    VH = H.var()
    r_h = np.corrcoef(H, D)[0, 1]
    cases = []
    for pi_bar, kap, mu_m, mode in [(0.3, 1.0, 0.0, "fixed"), (0.3, 0.5, 1.0, "fixed"),
                                     (0.2, 0.5, 1.0, "beta"), (0.2, 0.5, 1.0, "bernoulli"),
                                     (PI_BAR_DEFAULT, KAPPA_A4_DEFAULT, MU_M4_DEFAULT * 1.0, "beta-pilot")]:
        if mode == "fixed":
            pi = np.full(n, pi_bar)
        elif mode in ("beta", "beta-pilot"):
            pi = rng.beta(10 * pi_bar, 10 * (1 - pi_bar), n)
        else:
            pi = (rng.random(n) < pi_bar).astype(float)
        M = rng.normal(mu_m, np.sqrt(kap), n)
        X = (1 - pi) * H + pi * M
        kappa_r = kap / VH
        delta_r = (mu_m - H.mean()) / np.sqrt(VH)
        Epi, Epi2, Varpi = pi.mean(), (pi**2).mean(), pi.var()
        att_formula = _att(Epi, Epi2, Varpi, kappa_r, delta_r)
        r_x = np.corrcoef(X, D)[0, 1]
        att_mc = r_x / r_h
        ok = abs(att_mc - att_formula) < 0.03
        cases.append((mode, pi_bar, round(att_mc, 4), round(att_formula, 4), ok, round(r_x, 4)))
    ok_all = all(c[4] for c in cases)
    if verbose:
        for mode, pi_bar, mc, formula, ok, r_x in cases:
            print(f"  (d) mode={mode} pi_bar={pi_bar}: MC={mc} formula={formula} -> {'OK' if ok else 'FAIL'}"
                  + (f"  [pilot pi_bar: realized r(X,D)={r_x} vs r(H,D)={round(r_h,4)} -- indicator 4 "
                     f"still carries signal, just heavily diluted]" if mode == "beta-pilot" else ""))
    return ok_all, cases


def check_e(verbose, n=400):
    """(e) IPW on the random schedule gives the all-days slope within MC error."""
    rng = np.random.default_rng(5)
    cell = cell_params("default")
    cell["m1"] = 1.5  # a schedule with real MNAR pressure so IPW has something to correct
    panel = generate_panel(rng, "S", cell, n=n)
    baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
    C, reason = compute_composite(panel, DEFAULT_FEATURES, baseline=baseline)
    alarm, in_band, S = run_cusum(C, h=6.0)
    probed, prop, identified = probe_schedule(rng, "random", C, in_band)
    Y = panel["Y"]
    responded = panel["responded"]
    obs = probed & responded & ~np.isnan(C)

    all_mask = np.arange(T_DAYS)[None, :] >= BASELINE_DAYS
    all_mask = np.broadcast_to(all_mask, (n, T_DAYS)) & ~np.isnan(C) & responded
    b_all = person_slope_corr(all_mask, C, Y)[0]
    b_raw = person_slope_corr(obs, C, Y)[0]
    ipw_w = np.where(obs, safe_div(1.0, prop, 0.0), 0.0)
    b_ipw = person_slope_corr(obs, C, Y, weight=ipw_w)[0]
    rel_raw = abs(b_raw - b_all) / abs(b_all)
    rel_ipw = abs(b_ipw - b_all) / abs(b_all)
    ok = rel_ipw < 0.10
    if verbose:
        print(f"  (e) all-days slope={b_all:.4f} raw-random={b_raw:.4f} (rel {rel_raw:.3f}) "
              f"IPW={b_ipw:.4f} (rel {rel_ipw:.3f}) -> {'OK' if ok else 'FAIL'}")
    return ok, (b_all, b_raw, b_ipw)


def check_f(verbose, n=400):
    """(f) positivity: triggered / fixed return "not identified"."""
    rng = np.random.default_rng(6)
    cell = cell_params("default")
    panel = generate_panel(rng, "S", cell, n=n)
    baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
    C, reason = compute_composite(panel, DEFAULT_FEATURES, baseline=baseline)
    alarm, in_band, S = run_cusum(C, h=6.0)
    _, _, id_trig = probe_schedule(rng, "triggered", C, in_band, p_trig=0.3)
    _, _, id_fixed = probe_schedule(rng, "fixed", C, in_band)
    _, _, id_rand = probe_schedule(rng, "random", C, in_band)
    _, _, id_mixed = probe_schedule(rng, "mixed", C, in_band, p_trig2=0.3)
    ok = (not id_trig) and (not id_fixed) and id_rand and id_mixed
    if verbose:
        print(f"  (f) identified: triggered={id_trig} fixed={id_fixed} random={id_rand} mixed={id_mixed} "
              f"-> {'OK' if ok else 'FAIL'}")
    return ok, (id_trig, id_fixed, id_rand, id_mixed)


def check_g(verbose):
    """(g) known-value assert on the pi' formula. The DGP never simulates the filter's se/sp
    confusion matrix -- it uses pi' = (1-se)*pi / ((1-se)*pi + sp*(1-pi)) directly (Bayes' rule
    for P(truly agent | filter passed as human)). So the check is a known-value assert on that
    closed form, not a Monte Carlo of a classifier mechanism the pipeline doesn't run. Cross-checked
    against the odds-ratio form of Bayes' rule (prior odds x likelihood ratio) -- an independent
    algebraic path to the same number -- and against PREREG.md's own stated value at pi_bar."""
    def pi_prime_formula(pi):
        return (1 - FILTER_SE) * pi / ((1 - FILTER_SE) * pi + FILTER_SP * (1 - pi) + 1e-12)

    def pi_prime_odds(pi):
        prior_odds = pi / (1 - pi)
        lr = (1 - FILTER_SE) / FILTER_SP
        post_odds = prior_odds * lr
        return post_odds / (1 + post_odds)

    results = []
    ok_all = True
    for pi in (0.0, 0.5, 0.845, 1.0):
        a = pi_prime_formula(pi)
        b = pi if pi in (0.0, 1.0) else pi_prime_odds(pi)  # trivial at the boundaries regardless of se/sp
        ok = abs(a - b) < 1e-6
        ok_all = ok_all and ok
        results.append((pi, a, b, ok))
    known_value_ok = abs(pi_prime_formula(PI_BAR_DEFAULT) - 0.365) < 0.001  # PREREG.md's own stated value
    ok_all = ok_all and known_value_ok
    if verbose:
        for pi, a, b, ok in results:
            print(f"  (g) pi={pi}: formula={a:.6f} odds-rule cross-check={b:.6f} -> {'OK' if ok else 'FAIL'}")
        print(f"  (g) pi_bar={PI_BAR_DEFAULT}: pi'={pi_prime_formula(PI_BAR_DEFAULT):.4f} "
              f"(PREREG.md states 0.365) -> {'OK' if known_value_ok else 'FAIL'}")
    return ok_all, results


def check_h(verbose, n=400):
    """(h) observed workload noise variance 0.25."""
    rng = np.random.default_rng(8)
    cell = cell_params("default")
    panel = generate_panel(rng, "S", cell, n=n)
    noise = panel["L_obs"] - panel["L"]
    v = noise.var(ddof=1)
    ok = abs(v - 0.25) < 0.01
    if verbose:
        print(f"  (h) Var(L_obs - L) = {v:.4f} (target 0.25) -> {'OK' if ok else 'FAIL'}")
    return ok, v


def check_i(verbose):
    """(i) asserts spec sections 3-6 appear verbatim in sim/PREREG.md."""
    spec_text = SPEC_PATH.read_text()
    lines = spec_text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "## 3. Generator (D1)")
    end = next(i for i, l in enumerate(lines) if l.strip() == "## 7. Corpus pilot (D3), metadata only")
    body = "\n".join(lines[start:end]).rstrip()
    prereg_on_disk = PREREG_PATH.read_text() if PREREG_PATH.exists() else ""
    ok = bool(prereg_on_disk) and body in prereg_on_disk
    if verbose:
        print(f"  (i) spec sections 3-6 verbatim in sim/PREREG.md ({len(body)} chars) -> "
              f"{'OK' if ok else 'FAIL'}")
    return ok, len(body)


def run_check(verbose=True):
    t0 = time.time()
    results = {}
    for name, fn in [("a", check_a), ("b", check_b), ("c", check_c), ("d", check_d),
                      ("e", check_e), ("f", check_f), ("g", check_g), ("h", check_h),
                      ("i", check_i)]:
        if verbose:
            print(f"[check {name}]")
        ok, detail = fn(verbose)
        results[name] = ok
        if verbose:
            print()
    all_ok = all(results.values())
    print("check summary:", results, "ALL OK" if all_ok else "SOME FAILED", f"({time.time()-t0:.1f}s)")
    return all_ok, results


# ----------------------------------------------------------------------------------------------
# Tuning (tuning seed 20260927 only; family S / 50-50 S+DR mix only, per the pre-freeze scope).
# ----------------------------------------------------------------------------------------------
ARCHS_FOR_H = ["pop", "A-naive", "A-fixed", "A-fixed-minus-i", "A-fixed-minus-ii",
               "A-fixed-minus-iii", "A-fixed-minus-iv", "A-fixed-minus-v", "probe-only"]


def arch_features(name):
    if name == "A-naive":
        return NAIVE_FEATURES
    if name == "A-fixed":
        return DEFAULT_FEATURES
    if name.startswith("A-fixed-minus-"):
        return ablation_features(name.rsplit("-", 1)[-1])
    return None  # pop / probe-only handled separately


def fa_rate_for_alarm(alarm, reason):
    """False alarms per tracked person-month, given an alarm array already run. Shared by
    fa_rate_for_h (which runs the CUSUM itself) and score()'s per-family FA/month checks (which
    already have `alarm` from _run_arch and don't need to re-run it)."""
    tracked = (reason[:, BASELINE_DAYS:] == 0).sum()
    return alarm[:, BASELINE_DAYS:].sum() / max(tracked / 30.0, 1e-9)


def fa_rate_for_h(C, h, reason):
    alarm, band, S = run_cusum(C, h)
    return fa_rate_for_alarm(alarm, reason)


def pop_reference(panel):
    """Population-level baseline (mean, sd) for the `pop` architecture, from this panel's own
    baseline block. One definition, shared by tune_h('pop', ...) and _run_arch('pop', ...)."""
    return dict(mean=np.nanmean(panel["X"][:, :BASELINE_DAYS, :], (0, 1)),
                sd=np.nanstd(panel["X"][:, :BASELINE_DAYS, :], (0, 1)))


# POSTFREEZE fix (score-fidelity audit): the 4-probe baseline block (section 4) is days 7, 14, 21,
# 28 -- 0-indexed [6, 13, 20, 27]. probe_only_C previously z-scored on all responded Y over days
# 1-28 (about 22 answers the `random` schedule never actually administers pre-baseline); it now
# z-scores on exactly those 4 probe answers, per PREREG deviation 4's fallback convention.
PROBE_BASELINE_DAYS = [6, 13, 20, 27]

# Schedule -> the single extra probe_schedule() kwarg it needs, and the tuning.json ("schedules",
# i.e. P) key that supplies its value. One dict shared by metrics()'s probes_block and
# confirmation_block in place of their two separately hand-written if/elif kwargs ladders
# (schedules not in this dict, e.g. 'none'/'fixed'/'random', need no extra kwarg).
SCHED_KW = {"triggered": "p_trig", "mixed": "p_trig2", "current": "c_star"}


def probe_only_C(panel, rng):
    """Probe-only comparator's composite: a CUSUM on probe answers alone, z-scored on the
    4-probe baseline block (days 7, 14, 21, 28; section 4), under the `random` schedule (spec
    section 4: daily p = 0.1 post-baseline, plus the fixed baseline block) at the matched budget
    -- not an oracle over every responded day. C (and reason) are defined only on days actually
    probed AND responded; every other day holds. One implementation, shared by
    tune_h('probe-only', ...) and score()'s P8."""
    Yb = panel["Y"][:, PROBE_BASELINE_DAYS]
    respb = panel["responded"][:, PROBE_BASELINE_DAYS]
    v = np.where(respb, Yb, np.nan)
    cnt = respb.sum(1)
    m = np.where(cnt >= 2, np.nanmean(v, 1), 0.0)
    s = np.nanstd(v, 1, ddof=1)
    s = np.where((cnt >= 2) & (s > 1e-6), s, 1.0)
    probed, _, _ = probe_schedule(rng, "random", panel["Y"], np.zeros_like(panel["Y"], dtype=bool))
    observed = probed & panel["responded"]
    C = safe_div(panel["Y"] - m[:, None], s[:, None])
    C = np.where(observed, C, np.nan)
    reason = np.where(observed, 0, 1)
    return C, reason


def tune_h(arch, n=N_PERSONS, seed=TUNING_SEED, target=1 / 6,
           pi_bar=PI_BAR_DEFAULT, kappa_a4=KAPPA_A4_DEFAULT, mu_m4=MU_M4_DEFAULT,
           lam_range=(0.25, 0.5), cell_name="default", phi_D=PHI_D, psi=PSI, rising_slope=0.5):
    """`lam_range`/`cell_name`/`phi_D`/`psi`/`rising_slope` are passthrough extensions for `robust`
    (sim/ROBUSTNESS-PLAN.md): every existing call site omits them and gets the original default-cell
    behavior bit-for-bit. Nothing about the generator itself changes."""
    rng = np.random.default_rng(seed)
    cell = cell_params(cell_name)
    if arch == "probe-only":
        panel = generate_panel(rng, "S", cell, n=n, pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4,
                                lam_range=lam_range, phi_D=phi_D, psi=psi, rising_slope=rising_slope)
        rng2 = np.random.default_rng(seed + 1)
        C, reason = probe_only_C(panel, rng2)
    else:
        panel = generate_panel(rng, "S", cell, n=n, pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4,
                                lam_range=lam_range, phi_D=phi_D, psi=psi, rising_slope=rising_slope)
        baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
        if arch == "pop":
            C, reason = compute_composite(panel, NAIVE_FEATURES, pop_ref=pop_reference(panel))
        else:
            C, reason = compute_composite(panel, arch_features(arch), baseline=baseline)

    h_star = bisect(lambda mid: fa_rate_for_h(C, mid, reason), 0.1, 30.0, target, n_iter=40)
    fa_final = fa_rate_for_h(C, h_star, reason)
    boots = []
    rng_b = np.random.default_rng(seed + 999)
    n_persons = C.shape[0]
    alarm, _, _ = run_cusum(C, h_star)
    tracked_pp = (reason[:, BASELINE_DAYS:] == 0).sum(1)
    alarms_pp = alarm[:, BASELINE_DAYS:].sum(1)
    for _ in range(500):
        idx = rng_b.integers(0, n_persons, n_persons)
        mon, al = tracked_pp[idx].sum(), alarms_pp[idx].sum()
        boots.append(al / (mon / 30.0) if mon > 0 else np.nan)
    se = np.nanstd(boots, ddof=1)
    return dict(h=float(h_star), fa_per_month=float(fa_final), se=float(se))


def tune_schedules(n=N_PERSONS, seed=TUNING_SEED, target=BUDGET_TARGET,
                    pi_bar=PI_BAR_DEFAULT, kappa_a4=KAPPA_A4_DEFAULT, mu_m4=MU_M4_DEFAULT):
    rng = np.random.default_rng(seed + 7)
    cell = cell_params("default")
    n_s = n // 2
    n_dr = n - n_s
    panel_s = generate_panel(rng, "S", cell, n=n_s, pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)
    panel_dr = generate_panel(rng, "DR", cell, n=n_dr, pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)

    def cat(a, b):
        return np.concatenate([a, b], axis=0)

    panel = {k: (cat(panel_s[k], panel_dr[k]) if isinstance(panel_s[k], np.ndarray) and panel_s[k].ndim >= 1
                 and panel_s[k].shape[:1] == (n_s,) else panel_s[k]) for k in panel_s}
    baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
    h_fixed = tune_h("A-fixed", n=n, seed=seed, pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)["h"]
    C, reason = compute_composite(panel, DEFAULT_FEATURES, baseline=baseline)
    alarm, in_band, S = run_cusum(C, h_fixed)

    def expected_for_ptrig(p):
        _, prop, _ = probe_schedule(rng, "triggered", C, in_band, p_trig=p)
        return expected_budget_per_month(prop)

    unreachable_trig = expected_for_ptrig(1.0) < target
    # expected_for_ptrig is INCREASING in p (more triggering -> more probes): negate both sides.
    p_trig_bisected = bisect(lambda mid: -expected_for_ptrig(mid), 0.0, 1.0, -target, n_iter=40)
    p_trig = 1.0 if unreachable_trig else p_trig_bisected

    def expected_for_ptrig2(p):
        _, prop, _ = probe_schedule(rng, "mixed", C, in_band, p_trig2=p)
        return expected_budget_per_month(prop)

    unreachable_mixed = expected_for_ptrig2(1.0) < target
    p_trig2_bisected = bisect(lambda mid: -expected_for_ptrig2(mid), 0.0, 1.0, -target, n_iter=40)
    p_trig2 = 1.0 if unreachable_mixed else p_trig2_bisected

    def budget_for_cstar(c):
        probed, prop, _ = probe_schedule(rng, "current", C, in_band, c_star=c)
        return expected_budget_per_month(prop)

    # budget_for_cstar is DECREASING in c* (higher c* -> fewer probes): same direction as bisect().
    c_star = bisect(budget_for_cstar, -3.0, 3.0, target, n_iter=40)

    realized = dict(triggered=expected_for_ptrig(p_trig), mixed=expected_for_ptrig2(p_trig2),
                     current=budget_for_cstar(c_star))
    return dict(p_trig=float(p_trig), p_trig2=float(p_trig2), c_star=float(c_star),
                realized_budget=realized, h_fixed_used=float(h_fixed),
                triggered_budget_target_unreachable=bool(unreachable_trig),
                mixed_budget_target_unreachable=bool(unreachable_mixed))


def run_tune(pi_bar=PI_BAR_DEFAULT, kappa_a4=KAPPA_A4_DEFAULT, mu_m4=MU_M4_DEFAULT):
    t0 = time.time()
    out = {"seed": TUNING_SEED, "n_persons": N_PERSONS,
           "pi_bar": pi_bar, "kappa_a4": kappa_a4, "mu_m4": mu_m4, "h": {}, "schedules": None}
    for arch in ARCHS_FOR_H:
        print("tuning h for", arch, "...", flush=True)
        out["h"][arch] = tune_h(arch, pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)
        print("  ", out["h"][arch], flush=True)
    print("tuning schedules on S+DR mix ...", flush=True)
    out["schedules"] = tune_schedules(pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)
    print("  ", out["schedules"], flush=True)
    out["wall_seconds"] = time.time() - t0
    (HERE / "tuning.json").write_text(json.dumps(out, indent=2))
    print(f"wrote sim/tuning.json in {out['wall_seconds']:.1f}s")
    return out


# ----------------------------------------------------------------------------------------------
# score(): implemented per the deliverable, but NOT to be run pre-freeze (D0 not run this session).
# Reuses the exact primitives exercised by --check and tune(). PASS/FAIL is against the frozen
# thresholds in section 6; P1-P3 are labelled construction checks, not findings.
#
# POSTFREEZE decision rule (score-fidelity audit, G1): a prediction holds only if its whole 95%
# Monte Carlo interval clears the threshold (section 6), not its point estimate or bootstrap mean.
# `mc_stat` replaces the old `person_bootstrap` (which decided on the bootstrap mean and had no
# notion of independent vs paired panels). The MC SE reported beside every number is the bootstrap
# SD -- the section-3 "SD across persons over sqrt(N)" convention, with N the actual person count
# (not the stale 200 the spec text carries over from v2), which a bootstrap SD approximates
# directly for these smooth per-person statistics (see PREREG.md's G1 ambiguity note).
# ----------------------------------------------------------------------------------------------
def mc_stat(fn, ns, B=2000, seed=0):
    """95%-MC-interval decision statistic from a `B`-draw person bootstrap. `ns` lists one
    person-count per independent panel `fn` draws on: pass `ns=[N]` and have `fn` reuse its single
    index array against every same-panel input for a PAIRED quantity (same persons under two
    architectures/schedules); pass `ns=[N1, N2, ...]` for quantities from independent panels
    (different families/cells), each drawing its own resample. `point` is `fn` evaluated on the
    identity index (not the bootstrap mean); `se` is the bootstrap SD; `lo`/`hi` are the 2.5/97.5
    percentiles."""
    rng = np.random.default_rng(seed)
    point = float(fn(*[np.arange(n) for n in ns]))
    draws = np.array([fn(*[rng.integers(0, n, n) for n in ns]) for _ in range(B)], dtype=float)
    lo, hi = (float(x) for x in np.nanpercentile(draws, [2.5, 97.5]))
    se = float(np.nanstd(draws, ddof=1))
    return dict(point=point, se=se, lo=lo, hi=hi)


def _verdict(stat, kind, thr):
    """PASS iff the WHOLE 95% MC interval clears the threshold (section 6's decision rule).
    kind='ge': interval entirely >= thr. kind='le': interval entirely <= thr. kind='within':
    interval entirely inside +-thr. kind='range': interval entirely inside [thr[0], thr[1]]."""
    lo, hi = stat["lo"], stat["hi"]
    if kind == "ge":
        return bool(lo >= thr)
    if kind == "le":
        return bool(hi <= thr)
    if kind == "within":
        return bool(lo >= -thr and hi <= thr)
    if kind == "range":
        return bool(lo >= thr[0] and hi <= thr[1])
    raise ValueError(kind)


def _fa_month_pp(alarm, reason):
    """Per-person FA/month, for bootstrap resampling and the IQR spread metric."""
    mon = (reason[:, BASELINE_DAYS:] == 0).sum(1)
    al = alarm[:, BASELINE_DAYS:].sum(1)
    return safe_div(al, mon / 30.0, fill=np.nan)


def _fa_pooled(alarm, reason, idx):
    """Pooled FA/tracked-person-month over the persons in `idx`: total alarms over total tracked
    months (G2's Reading 1 -- the estimand `h` is tuned to; `fa_rate_for_alarm` restricted to a
    person subset for bootstrap resampling)."""
    tracked = (reason[idx, BASELINE_DAYS:] == 0).sum()
    return alarm[idx, BASELINE_DAYS:].sum() / max(tracked / 30.0, 1e-9)


def _sensitivity(alarm, onset, window=21, exclude_pre_onset_alarms=True):
    """Per-person detected boolean. `exclude_pre_onset_alarms` (G3's ambiguity): True (default,
    as-run/primary) classifies on the first alarm -- a pre-onset alarm makes the person a
    false-alarm case, not detected. False (the audit's "more natural" alternative, Reading 2)
    routes the pre-onset alarm to the FA tally only; the person still counts as detected if a
    later alarm falls inside the window."""
    day = np.arange(alarm.shape[1])[None, :]
    in_window = (day >= onset[:, None]) & (day < onset[:, None] + window)
    detected = (alarm & in_window).any(1)
    if exclude_pre_onset_alarms:
        pre = day < onset[:, None]
        fa_pre = (alarm & pre).any(1)
        detected = detected & ~fa_pre
    return detected  # per-person boolean detected


def _rmst42(alarm, onset, cap=42, exclude_pre_onset_alarms=True):
    """Per-person restricted time to detection, censored at `cap` days from onset: days from onset
    to the first true alarm, or `cap` if none. `exclude_pre_onset_alarms`: see `_sensitivity`;
    True (as-run/primary) censors at `cap` when a pre-onset alarm preceded onset."""
    n, T = alarm.shape
    day = np.arange(T)[None, :]
    days_from_onset = day - onset[:, None]
    in_window = (days_from_onset >= 0) & (days_from_onset < cap)
    hit = alarm & in_window
    candidate = np.where(hit, days_from_onset, cap)
    first = candidate.min(1).astype(float)
    if exclude_pre_onset_alarms:
        pre = days_from_onset < 0
        fa_pre = (alarm & pre).any(1)
        first = np.where(fa_pre, float(cap), first)
    return first


def _days_to_detect(alarm, onset, day_lo, day_hi):
    """Per-person days from `onset` to the first alarm inside [day_lo, day_hi) (per-person arrays),
    NaN if never detected in that window, and NaN also when a pre-onset alarm already fired
    (mirrors `_sensitivity`/`_rmst42`'s primary G3 reading; unlike those two, this metrics-only
    helper is never called with the alternative reading, so the toggle was dropped -- pre-onset
    alarms are always masked). Generalizes `_sensitivity`/`_rmst42`'s onset-anchored window to a
    window whose bounds need not equal onset/onset+21 -- BD's metrics-section detection window is
    the first 21 TRACKED days (28:49), not 21 days from its own (pre-baseline) onset, so
    `day_lo`/`day_hi` and `onset` are passed separately. Used for the PREREG section 5 'median days
    to detect among detected' metric only (REPORTING ONLY; no threshold uses this)."""
    n, T = alarm.shape
    day = np.arange(T)[None, :]
    in_window = (day >= day_lo[:, None]) & (day < day_hi[:, None])
    hit = alarm & in_window
    any_hit = hit.any(1)
    first_day = np.where(hit, day, T).min(1).astype(float)
    dtd = first_day - onset
    dtd = np.where(any_hit, dtd, np.nan)
    pre = day < onset[:, None]
    fa_pre = (alarm & pre).any(1)
    dtd = np.where(fa_pre, np.nan, dtd)
    return dtd


def _att(Epi, Epi2, Varpi, kappa, delta):
    """Closed-form attenuation: Att = (1 - E[pi]) / sqrt(E[(1-pi)^2] + E[pi^2] kappa +
    Var(pi) delta^2), with E[(1-pi)^2] recovered from Var(pi) and E[pi] via Var(1-pi) = Var(pi)
    (an exact identity, not an approximation). Shared by check_d, attenuation_person (P6) and
    att_formula_value (metrics section o). att_formula_value_filtered keeps its own raw Monte
    Carlo E[(1-pi')^2] estimate -- pi' has no closed form, so that quantity is a genuinely
    different (empirically estimated) number, not a duplicate of this identity."""
    E1mpi2 = Varpi + (1 - Epi) ** 2
    return (1 - Epi) / np.sqrt(E1mpi2 + Epi2 * kappa + Varpi * delta ** 2)


def _run_arch(panel, arch_name, h):
    if arch_name == "pop":
        C, reason = compute_composite(panel, NAIVE_FEATURES, pop_ref=pop_reference(panel))
    else:
        baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
        C, reason = compute_composite(panel, arch_features(arch_name), baseline=baseline)
    alarm, in_band, S = run_cusum(C, h)
    return C, reason, alarm, in_band


def _prereg_stated_value(prereg_text_on_disk, name):
    # Anchored to the bullet-list line ("- `NAME = value`"), NOT the earlier prose mention of the
    # spec's design-time placeholders ("the spec's design-time placeholders (`PI_BAR = 0.2`, ...)"),
    # which uses the exact same `NAME = value` token syntax for a different, superseded number.
    m = re.search(rf"^- `{name} = ([0-9.eE+-]+)`", prereg_text_on_disk, re.MULTILINE)
    if not m:
        raise RuntimeError(f"could not find a '- `{name} = ...`' bullet line in sim/PREREG.md")
    return float(m.group(1))


# ----------------------------------------------------------------------------------------------
# Vectorized per-person sufficient statistics for a person-centred (optionally weighted) slope
# and correlation of Y on C, restricted to `mask`. Used by P4/P5's 2000-draw bootstraps: computing
# these once and then only summing over resampled person indices is what makes a 2000-draw
# bootstrap over person-centred slopes/correlations tractable (a naive per-draw call into
# `person_slope_corr`, which loops over persons in Python, would be ~2000x slower). Mirrors the
# audit's own bootstrap implementation exactly (score-fidelity audit, audit.py's `pstats`).
# ----------------------------------------------------------------------------------------------
def _pstats(mask, C, Y, w=None):
    w = np.ones_like(C) if w is None else w
    m = mask & ~np.isnan(C)
    W = np.where(m, w, 0.0)
    c = np.where(m, C, 0.0)
    y = np.where(m, Y, 0.0)
    Ws = W.sum(1)
    ok = (m.sum(1) >= 3) & (Ws > 0)
    wc = safe_div((W * c).sum(1), Ws)
    wy = safe_div((W * y).sum(1), Ws)
    cc = np.where(m, c - wc[:, None], 0.0)
    yy = np.where(m, y - wy[:, None], 0.0)
    st = dict(wxy=(W * cc * yy).sum(1), wxx=(W * cc * cc).sum(1), wyy=(W * yy * yy).sum(1),
              n=m.sum(1).astype(float), sc=cc.sum(1), sy=yy.sum(1),
              scc=(cc * cc).sum(1), syy=(yy * yy).sum(1), scy=(cc * yy).sum(1))
    return {k: np.where(ok, v, 0.0) for k, v in st.items()}


def _pslope(s, idx):
    return s["wxy"][idx].sum() / s["wxx"][idx].sum()


def rel_bias(sa, so, idx):
    """Signed relative bias of the observed-schedule slope against the all-days slope, both
    from `_pstats` sufficient statistics. Shared by P5's per-cell/per-schedule `rel_bias_fn`
    and its `added_bias_fn` (m1=1.5 vs m1=0 comparison)."""
    ba = _pslope(sa, idx)
    return (_pslope(so, idx) - ba) / ba


def _pcorr_unweighted(s, idx):
    """np.corrcoef on the concatenated (weighted-centred) values -- unweighted itself, matching
    every non-P4-IPW call site of person_slope_corr."""
    Nn = s["n"][idx].sum()
    mc = s["sc"][idx].sum() / Nn
    my = s["sy"][idx].sum() / Nn
    cov = s["scy"][idx].sum() / Nn - mc * my
    return cov / np.sqrt((s["scc"][idx].sum() / Nn - mc**2) * (s["syy"][idx].sum() / Nn - my**2))


def _pcorr_weighted(s, idx):
    """BUG fix (P4's mixed-IPW correlation): sum(w*cc*yy) / sqrt(sum(w*cc^2) * sum(w*yy^2))."""
    return s["wxy"][idx].sum() / np.sqrt(s["wxx"][idx].sum() * s["wyy"][idx].sum())


# G3 ambiguity (pre-onset alarms, section "AMBIGUOUS items" of POSTFREEZE-DEVIATIONS.md): the
# alternative reading's text is identical at every one of its 4 call sites (P2, P7, P8, P9) in
# score() below; spread with `**G3_READINGS` into each `alternative` dict there.
G3_READINGS = dict(
    reading="pre-onset alarm routed to the FA tally only; still detected if a later alarm falls in "
            "the window (Reading 2, the audit's more-natural reading)",
)


def _load_frozen(action):
    """Load and validate the tuning inputs shared by score() and metrics(): sim/PREREG.md must
    exist, and tuning.json's pi_bar/kappa_a4/mu_m4 (read from the committed tuning run, not
    passed in on the CLI) must equal the values the frozen sim/PREREG.md itself states
    (constitution III/IV). Returns (H, P, pi_bar, kappa_a4, mu_m4)."""
    if not PREREG_PATH.exists():
        raise RuntimeError(f"sim/PREREG.md missing -- cannot {action} pre-freeze.")
    prereg_text_on_disk = PREREG_PATH.read_text()
    tuning = json.loads((HERE / "tuning.json").read_text())
    H = tuning["h"]
    P = tuning["schedules"]
    pi_bar, kappa_a4, mu_m4 = tuning["pi_bar"], tuning["kappa_a4"], tuning["mu_m4"]
    for name, val in (("PI_BAR", pi_bar), ("KAPPA_A4", kappa_a4), ("MU_M4", mu_m4)):
        expected = _prereg_stated_value(prereg_text_on_disk, name)
        assert abs(val - expected) < 1e-9, (
            f"tuning.json's {name}={val} does not match sim/PREREG.md's stated {name}={expected}"
        )
    return H, P, pi_bar, kappa_a4, mu_m4


def attenuation_person(h, d, x, pi_i, kap, mu_m):
    """Per-person P6 attenuation: the closed-form Att and the direct MC ratio r(X,D)/r(H,D),
    for one indicator/mixing variant (unfiltered: pi, X; filtered: pi', X_filtered). Also
    returns rH, rX (used only by the validity-vs-attenuation-scale ambiguity below). Returns
    None if this person's within-person H variance is too small to be informative. Module-level
    (not a score()-local closure) so `robust`'s S2 check (sim/ROBUSTNESS-PLAN.md) can reuse it."""
    VH = h.var()
    if VH < 1e-9:
        return None
    rH = np.corrcoef(h, d)[0, 1]
    kappa_r = kap / VH
    delta_r = (mu_m - h.mean()) / np.sqrt(VH)
    Epi, Epi2, Varpi = pi_i.mean(), (pi_i**2).mean(), pi_i.var()
    att_formula = _att(Epi, Epi2, Varpi, kappa_r, delta_r)
    rX = np.corrcoef(x, d)[0, 1]
    att_mc = rX / rH if abs(rH) > 1e-6 else np.nan
    return att_formula, att_mc, rH, rX


def score(prereg_sha):
    H, P, pi_bar, kappa_a4, mu_m4 = _load_frozen("score")
    preds = {}

    def panel_for(family, cell_name):
        seed = eval_seed(prereg_sha, family, cell_name)
        rng = np.random.default_rng(seed)
        return generate_panel(rng, family, cell_params(cell_name), n=N_PERSONS,
                               pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)

    # ---- P1 (construction check): A-naive vs A-fixed FA/month on SP, VA, DE, BI ----
    # G1: decide on the 95% MC interval (paired: A-naive and A-fixed share the same panel/persons).
    # G2 (AMBIGUOUS, as-run primary = Reading 2, mean-of-person-rates): report both the as-run
    # ratio-of-person-rate-sums and the alternative pooled (total-alarms/total-tracked-months) ratio.
    p1 = {}
    for fam, lo_thr, hi_thr in [("SP", 2.0, None), ("VA", 0.5, 2.0), ("DE", 0.5, 2.0), ("BI", 0.5, 2.0)]:
        panel = panel_for(fam, "default")
        _, reason_n, alarm_n, _ = _run_arch(panel, "A-naive", H["A-naive"]["h"])
        _, reason_f, alarm_f, _ = _run_arch(panel, "A-fixed", H["A-fixed"]["h"])
        fa_n = _fa_month_pp(alarm_n, reason_n)
        fa_f = _fa_month_pp(alarm_f, reason_f)

        def ratio_fn(idx, fa_n=fa_n, fa_f=fa_f):
            return np.nansum(fa_n[idx]) / max(np.nansum(fa_f[idx]), 1e-9)

        def ratio_fn_pooled(idx, alarm_n=alarm_n, reason_n=reason_n, alarm_f=alarm_f, reason_f=reason_f):
            return _fa_pooled(alarm_n, reason_n, idx) / max(_fa_pooled(alarm_f, reason_f, idx), 1e-9)

        stat = mc_stat(ratio_fn, [N_PERSONS])
        kind = "ge" if hi_thr is None else "range"
        thr = lo_thr if hi_thr is None else [lo_thr, hi_thr]
        passed = _verdict(stat, kind, thr)
        stat_pooled = mc_stat(ratio_fn_pooled, [N_PERSONS])
        passed_pooled = _verdict(stat_pooled, kind, thr)
        if fam == "SP":
            _, reason_iii, alarm_iii, _ = _run_arch(panel, "A-fixed-minus-iii", H["A-fixed-minus-iii"]["h"])
            fa_iii = _fa_month_pp(alarm_iii, reason_iii)
            ablation_ratio = np.nansum(fa_n) / max(np.nansum(fa_iii), 1e-9)
            note = f"ablation ratio (A-naive FA-month / A-fixed-minus-iii FA-month) = {ablation_ratio:.4f}"
        else:
            ablation_ratio = None
            note = "no matching component"
        p1[fam] = dict(ratio_naive_over_fixed=stat, threshold=[lo_thr, hi_thr],
                        ablation_ratio=ablation_ratio, note=note, PASS=bool(passed),
                        fa_estimator_ambiguous_G2=dict(
                            as_run_primary="mean of person-level FA rates (Reading 2)",
                            alternative_pooled=dict(stat=stat_pooled, PASS=bool(passed_pooled),
                                                     reading="pooled: total alarms / total tracked months (Reading 1); "
                                                             "the audit's more-natural reading (matches the h tuning estimand)")))
    preds["P1"] = p1

    # ---- P1b: A-fixed DE FA/month <= 1.5x its S FA/month ----
    # BUG fix: denominator is TOTAL person-months (post-baseline person-days/30), not tracked
    # person-months. Ratio of totals cancels the shared N*(T-28)/30 denominator, so it reduces to
    # the ratio of total post-baseline alarm counts.
    panel_de = panel_for("DE", "default")
    panel_s = panel_for("S", "default")
    _, reason_de, alarm_de, _ = _run_arch(panel_de, "A-fixed", H["A-fixed"]["h"])
    _, reason_s, alarm_s, _ = _run_arch(panel_s, "A-fixed", H["A-fixed"]["h"])
    al_de_pp = alarm_de[:, BASELINE_DAYS:].sum(1)
    al_s_pp = alarm_s[:, BASELINE_DAYS:].sum(1)
    fa_s_pp = _fa_month_pp(alarm_s, reason_s)  # per-person tracked-month FA rate, reused by P3's av2_ratio (G2)
    total_months = (T_DAYS - BASELINE_DAYS) / 30.0
    fa_de_total_pm = float(al_de_pp.sum() / (N_PERSONS * total_months))
    fa_s_total_pm = float(al_s_pp.sum() / (N_PERSONS * total_months))

    def p1b_ratio(idx_de, idx_s):
        return al_de_pp[idx_de].sum() / max(al_s_pp[idx_s].sum(), 1e-9)

    # DE and S are different families -- independent panels (G4) -- so bootstrap them independently.
    p1b_stat = mc_stat(p1b_ratio, [N_PERSONS, N_PERSONS])
    preds["P1b"] = dict(fa_DE_total_person_month=fa_de_total_pm, fa_S_total_person_month=fa_s_total_pm,
                         de_over_s_fa_ratio=p1b_stat, threshold=1.5, PASS=bool(_verdict(p1b_stat, "le", 1.5)))

    # ---- P2 (construction check): DR, targeted_theta1_05 ----
    # G1: paired 95% MC interval (A-naive/A-fixed/A-fixed-minus-i share the same targeted panel).
    # G3 (AMBIGUOUS, as-run primary = Reading 1, pre-onset alarm excludes detection): both readings
    # of `_sensitivity` are computed and reported; the verdict uses the primary reading.
    panel_dr_t = panel_for("DR", "targeted_theta1_05")
    onset = panel_dr_t["t0"]
    _, _, alarm_naive, _ = _run_arch(panel_dr_t, "A-naive", H["A-naive"]["h"])
    _, _, alarm_fixed, _ = _run_arch(panel_dr_t, "A-fixed", H["A-fixed"]["h"])
    _, _, alarm_mi, _ = _run_arch(panel_dr_t, "A-fixed-minus-i", H["A-fixed-minus-i"]["h"])

    def _p2_stats(excl):
        sn = _sensitivity(alarm_naive, onset, exclude_pre_onset_alarms=excl).astype(float)
        sf = _sensitivity(alarm_fixed, onset, exclude_pre_onset_alarms=excl).astype(float)
        smi = _sensitivity(alarm_mi, onset, exclude_pre_onset_alarms=excl).astype(float)

        def gap_fn(idx):
            return sf[idx].mean() - sn[idx].mean()

        def half_margin_fn(idx):
            return (sf[idx].mean() - smi[idx].mean()) - 0.5 * gap_fn(idx)

        gap_stat = mc_stat(gap_fn, [N_PERSONS])
        half_stat = mc_stat(half_margin_fn, [N_PERSONS])
        passed = _verdict(gap_stat, "ge", 0.10) and _verdict(half_stat, "ge", 0.0)
        return dict(sens_A_naive=float(sn.mean()), sens_A_fixed=float(sf.mean()),
                    sens_A_fixed_minus_i=float(smi.mean()), gap=gap_stat,
                    gap_explained_by_i=half_stat, PASS=bool(passed))

    p2_primary = _p2_stats(True)
    p2_alt = _p2_stats(False)
    preds["P2"] = dict(**p2_primary,
                        pre_onset_alarm_ambiguous_G3=dict(
                            as_run_primary="pre-onset alarm excludes detection (Reading 1)",
                            alternative=dict(**p2_alt, **G3_READINGS)))

    # ---- P3 (construction check): AV logged persons, and AV2 vs S ----
    # G1: av_ratio is paired within AV-logged persons; av2_ratio compares independent panels (AV2, S).
    # G2 (AMBIGUOUS, as-run primary = Reading 2, mean-of-person-rates): both readings reported.
    panel_av = panel_for("AV", "default")
    logged = panel_av["av_logged"]
    nl = int(logged.sum())
    _, reason_iv, alarm_iv, _ = _run_arch(panel_av, "A-fixed", H["A-fixed"]["h"])
    _, reason_miv, alarm_miv, _ = _run_arch(panel_av, "A-fixed-minus-iv", H["A-fixed-minus-iv"]["h"])
    fa_iv = _fa_month_pp(alarm_iv, reason_iv)[logged]
    fa_miv = _fa_month_pp(alarm_miv, reason_miv)[logged]
    alarm_iv_l, reason_iv_l = alarm_iv[logged], reason_iv[logged]
    alarm_miv_l, reason_miv_l = alarm_miv[logged], reason_miv[logged]

    def av_ratio_fn(idx):
        return np.nansum(fa_miv[idx]) / max(np.nansum(fa_iv[idx]), 1e-9)

    def av_ratio_pooled_fn(idx):
        return _fa_pooled(alarm_miv_l, reason_miv_l, idx) / max(_fa_pooled(alarm_iv_l, reason_iv_l, idx), 1e-9)

    av_stat = mc_stat(av_ratio_fn, [nl])
    av_stat_pooled = mc_stat(av_ratio_pooled_fn, [nl])

    panel_av2 = panel_for("AV2", "default")
    _, reason_av2, alarm_av2, _ = _run_arch(panel_av2, "A-fixed", H["A-fixed"]["h"])
    fa_av2 = _fa_month_pp(alarm_av2, reason_av2)

    def av2_ratio_fn(i, j):
        return np.nansum(fa_av2[i]) / max(np.nansum(fa_s_pp[j]), 1e-9)

    def av2_ratio_pooled_fn(i, j):
        return _fa_pooled(alarm_av2, reason_av2, i) / max(_fa_pooled(alarm_s, reason_s, j), 1e-9)

    av2_stat = mc_stat(av2_ratio_fn, [N_PERSONS, N_PERSONS])
    av2_stat_pooled = mc_stat(av2_ratio_pooled_fn, [N_PERSONS, N_PERSONS])
    passed_p3 = _verdict(av_stat, "ge", 2.0) and _verdict(av2_stat, "ge", 2.0)
    passed_p3_pooled = _verdict(av_stat_pooled, "ge", 2.0) and _verdict(av2_stat_pooled, "ge", 2.0)
    preds["P3"] = dict(av_logged_removeiv_ratio=av_stat, av2_over_s_ratio=av2_stat,
                        PASS=bool(passed_p3),
                        fa_estimator_ambiguous_G2=dict(
                            as_run_primary="mean of person-level FA rates (Reading 2)",
                            alternative_pooled=dict(av_logged_removeiv_ratio=av_stat_pooled,
                                                     av2_over_s_ratio=av2_stat_pooled,
                                                     PASS=bool(passed_p3_pooled),
                                                     reading="pooled: total alarms / total tracked months (Reading 1); "
                                                             "the audit's more-natural reading")))

    # ---- P4: S, A-fixed, triggered/mixed/current calibration ----
    # BUG fixes (score-fidelity audit): (a) probe-day samples are restricted to post-baseline days,
    # to match the all-days reference, which never includes the p=1 baseline block; (b) the
    # all-days reference is not conditioned on response (the same defect as P5's -- harmless at
    # m1=0 but present in the code); (c) the mixed-IPW correlation is properly weighted, not
    # np.corrcoef on the unweighted concatenation; (d) the slope-attenuation figure is signed, not
    # abs (an inflation would otherwise misreport as an attenuation). G1: every number decided on
    # its 95% MC interval (paired -- same S panel/persons throughout).
    panel_s4 = panel_for("S", "default")
    h_fixed = H["A-fixed"]["h"]
    C4, reason4, alarm4, band4 = _run_arch(panel_s4, "A-fixed", h_fixed)
    _, _, Strace4 = run_cusum(C4, h_fixed)
    rng4 = np.random.default_rng(eval_seed(prereg_sha, "S", "default") + 1)

    Y4, resp4 = panel_s4["Y"], panel_s4["responded"]
    post_mask = np.zeros_like(reason4, dtype=bool)
    post_mask[:, BASELINE_DAYS:] = True
    all_mask = post_mask & ~np.isnan(C4)  # BUG fix: drop "& resp4"

    probed_t, prop_t, id_t = probe_schedule(rng4, "triggered", C4, band4, p_trig=P["p_trig"])
    obs_t = probed_t & resp4 & ~np.isnan(C4) & post_mask  # BUG fix: restrict to post-baseline
    probed_m, prop_m, id_m = probe_schedule(rng4, "mixed", C4, band4, p_trig2=P["p_trig2"])
    obs_m = probed_m & resp4 & ~np.isnan(C4) & post_mask  # BUG fix: restrict to post-baseline
    w_m = np.where(obs_m, safe_div(1.0, prop_m), 0.0)

    sa, st_, sm = _pstats(all_mask, C4, Y4), _pstats(obs_t, C4, Y4), _pstats(obs_m, C4, Y4)
    sw = _pstats(obs_m, C4, Y4, w=w_m)

    def _p4_block(st, sw, extra=False):
        """One P4 calibration block (corr deflation / signed slope attenuation / mixed-IPW slope
        and corr diffs, each as a 95% MC interval) for a given triggered-stats/mixed-IPW-stats
        pair. Shared by the primary (S_t band) and alternative (S_{t-1} band) readings below."""
        def point(idx, sa=sa, st=st, sw=sw):
            ba, bt, bw = _pslope(sa, idx), _pslope(st, idx), _pslope(sw, idx)
            ra, rt = _pcorr_unweighted(sa, idx), _pcorr_unweighted(st, idx)
            rw = _pcorr_weighted(sw, idx)  # BUG fix: weighted IPW correlation
            out = dict(corr_deflation=ra - rt, slope_atten_rel=(ba - bt) / ba,  # BUG fix: signed
                       ipw_slope_minus_all=bw - ba, ipw_corr_minus_all=rw - ra)
            if extra:
                out.update(b_all=ba, r_all=ra, b_trig=bt, r_trig=rt, b_mixed_ipw=bw, r_mixed_ipw=rw)
            return out

        def mc(key):
            return mc_stat(lambda idx: point(idx)[key], [N_PERSONS])

        corr_deflation = mc("corr_deflation")
        slope_atten_rel = mc("slope_atten_rel")
        ipw_slope_minus_all = mc("ipw_slope_minus_all")
        ipw_corr_minus_all = mc("ipw_corr_minus_all")
        passed = (_verdict(corr_deflation, "ge", 0.05) and _verdict(slope_atten_rel, "ge", 0.10)
                  and _verdict(ipw_slope_minus_all, "within", 0.03)
                  and _verdict(ipw_corr_minus_all, "within", 0.03))
        return dict(mc=mc, corr_deflation=corr_deflation, slope_atten_rel=slope_atten_rel,
                    ipw_slope_minus_all=ipw_slope_minus_all, ipw_corr_minus_all=ipw_corr_minus_all,
                    passed=passed)

    p4_primary = _p4_block(st_, sw, extra=True)
    corr_deflation = p4_primary["corr_deflation"]
    slope_atten_rel = p4_primary["slope_atten_rel"]
    ipw_slope_minus_all = p4_primary["ipw_slope_minus_all"]
    ipw_corr_minus_all = p4_primary["ipw_corr_minus_all"]
    b_all_s, r_all_s = p4_primary["mc"]("b_all"), p4_primary["mc"]("r_all")
    b_trig_s, r_trig_s = p4_primary["mc"]("b_trig"), p4_primary["mc"]("r_trig")
    b_mixed_ipw_s, r_mixed_ipw_s = p4_primary["mc"]("b_mixed_ipw"), p4_primary["mc"]("r_mixed_ipw")
    passed_p4 = p4_primary["passed"]
    ok_current, current_detail = check_c(False)

    # AMBIGUOUS (P4 trigger timing, reported not adopted): as-run `in_band` uses S_t (today's
    # CUSUM statistic, after folding in today's C_t). The alternative reading uses S_{t-1}
    # (yesterday's), since a probe is decided before the day's own data exist -- the audit's
    # more-natural reading. Independent probe draws (a separate rng offset); band4 (S_t) is
    # already the primary as-run reading via _run_arch above.
    Strace_prev = np.concatenate([np.zeros((N_PERSONS, 1)), Strace4[:, :-1]], axis=1)
    band4_alt = (Strace_prev >= h_fixed * BAND_LO_FRAC) & (Strace_prev < h_fixed)
    rng4_alt = np.random.default_rng(eval_seed(prereg_sha, "S", "default") + 101)
    probed_t_alt, _, _ = probe_schedule(rng4_alt, "triggered", C4, band4_alt, p_trig=P["p_trig"])
    obs_t_alt = probed_t_alt & resp4 & ~np.isnan(C4) & post_mask
    probed_m_alt, prop_m_alt, _ = probe_schedule(rng4_alt, "mixed", C4, band4_alt, p_trig2=P["p_trig2"])
    obs_m_alt = probed_m_alt & resp4 & ~np.isnan(C4) & post_mask
    w_m_alt = np.where(obs_m_alt, safe_div(1.0, prop_m_alt), 0.0)
    st_alt, sw_alt = _pstats(obs_t_alt, C4, Y4), _pstats(obs_m_alt, C4, Y4, w=w_m_alt)

    p4_alt = _p4_block(st_alt, sw_alt)
    corr_deflation_alt = p4_alt["corr_deflation"]
    slope_atten_rel_alt = p4_alt["slope_atten_rel"]
    ipw_slope_minus_all_alt = p4_alt["ipw_slope_minus_all"]
    ipw_corr_minus_all_alt = p4_alt["ipw_corr_minus_all"]
    passed_p4_alt = p4_alt["passed"]

    preds["P4"] = dict(all_days=dict(slope=b_all_s, corr=r_all_s),
                        triggered=dict(slope=b_trig_s, corr=r_trig_s, corr_deflation=corr_deflation,
                                        slope_attenuation_rel=slope_atten_rel),
                        mixed_ipw=dict(slope=b_mixed_ipw_s, corr=r_mixed_ipw_s,
                                        slope_diff=ipw_slope_minus_all, corr_diff=ipw_corr_minus_all),
                        current_check_isolated_mechanism=current_detail,
                        PASS=bool(passed_p4),
                        trigger_timing_ambiguous_P4=dict(
                            as_run_primary="in_band on S_t (today's CUSUM statistic, after folding in C_t)",
                            alternative=dict(
                                corr_deflation=corr_deflation_alt, slope_attenuation_rel=slope_atten_rel_alt,
                                mixed_ipw_slope_diff=ipw_slope_minus_all_alt, mixed_ipw_corr_diff=ipw_corr_minus_all_alt,
                                PASS=bool(passed_p4_alt),
                                reading="in_band on S_{t-1} (yesterday's CUSUM statistic, before today's C_t is "
                                        "folded in); the audit's more-natural reading, since a probe is decided "
                                        "before the day's data exist")))

    # ---- P5: S, m1 in {0, 0.5, 1.5}, A-fixed, schedules fixed/random/triggered/mixed ----
    # BUG fixes (score-fidelity audit): (a) the all-days reference is not conditioned on response
    # -- at m1>0 response depends on D, so a responders-only reference carries the very MNAR bias
    # P5 exists to measure; (b) probe-day samples are restricted to post-baseline days, matching
    # P4. G1: every number decided on its 95% MC interval; G4: comparisons ACROSS m1 cells are
    # unpaired by design (different simulated persons per cell), comparisons within one cell
    # across schedules are paired (same panel).
    sa_by_cell, so_by_cell = {}, {}
    biases = {}
    for m1_cell in ("default", "m1_05", "m1_15"):
        panel5 = panel_for("S", m1_cell)
        C5, reason5, alarm5, band5 = _run_arch(panel5, "A-fixed", H["A-fixed"]["h"])
        Y5, resp5 = panel5["Y"], panel5["responded"]
        post5 = np.zeros_like(reason5, dtype=bool)
        post5[:, BASELINE_DAYS:] = True
        all5 = post5 & ~np.isnan(C5)  # BUG fix: drop "& resp5"
        sa5 = _pstats(all5, C5, Y5)
        sa_by_cell[m1_cell] = sa5
        so_by_cell[m1_cell] = {}
        rng5 = np.random.default_rng(eval_seed(prereg_sha, "S", m1_cell) + 2)
        sched_biases = {}
        for sched, kw in [("fixed", {}), ("random", {}), ("triggered", dict(p_trig=P["p_trig"])),
                           ("mixed", dict(p_trig2=P["p_trig2"]))]:
            probed, prop, ident = probe_schedule(rng5, sched, C5, band5, **kw)
            obs = probed & resp5 & ~np.isnan(C5) & post5  # BUG fix: restrict to post-baseline
            so5 = _pstats(obs, C5, Y5)
            so_by_cell[m1_cell][sched] = so5

            def rel_bias_fn(idx, sa5=sa5, so5=so5):
                return rel_bias(sa5, so5, idx)

            sched_biases[sched] = mc_stat(rel_bias_fn, [N_PERSONS])
        biases[m1_cell] = sched_biases

    def added_bias_fn(sched):
        def f(idx15, idx0):
            b15 = rel_bias(sa_by_cell["m1_15"], so_by_cell["m1_15"][sched], idx15)
            b0 = rel_bias(sa_by_cell["default"], so_by_cell["default"][sched], idx0)
            return abs(b15) - abs(b0)
        return f

    added_bias = {s: mc_stat(added_bias_fn(s), [N_PERSONS, N_PERSONS]) for s in biases["default"]}
    added_bias_ok = all(_verdict(added_bias[s], "ge", 0.10) for s in added_bias)
    p5 = dict(rel_bias_by_m1_and_schedule=biases,
              added_abs_rel_bias_m1_15_minus_m1_0=added_bias,
              m1_05_random_under_5pct=bool(_verdict(biases["m1_05"]["random"], "within", 0.05)),
              m1_15_added_bias_ge_10pct_every_schedule=bool(added_bias_ok))

    # response-propensity IPW at m1=1.5, random schedule
    panel5b = panel_for("S", "m1_15")
    C5b, reason5b, alarm5b, band5b = _run_arch(panel5b, "A-fixed", H["A-fixed"]["h"])
    Y5b, resp5b = panel5b["Y"], panel5b["responded"]
    rng5b = np.random.default_rng(eval_seed(prereg_sha, "S", "m1_15") + 3)
    probed5b, prop5b, _ = probe_schedule(rng5b, "random", C5b, band5b)
    n5, T5 = C5b.shape
    lag = np.concatenate([np.zeros((n5, 1)), np.nan_to_num(C5b[:, :-1])], axis=1)
    dow = np.tile(dow_features(T5), (n5, 1, 1))
    feats = np.concatenate([np.nan_to_num(C5b)[..., None], lag[..., None], dow], axis=-1)
    admin = probed5b
    yresp = resp5b[admin].astype(float)
    beta_hat = logistic_irls(feats[admin], yresp)
    p_resp_hat = expit(feats @ beta_hat)
    post5b = np.zeros_like(reason5b, dtype=bool)
    post5b[:, BASELINE_DAYS:] = True
    obs5b = probed5b & resp5b & ~np.isnan(C5b) & post5b  # BUG fix: restrict to post-baseline
    w_resp = np.where(obs5b, safe_div(1.0, np.clip(p_resp_hat, 0.05, 1.0)), 0.0)
    all5b = post5b & ~np.isnan(C5b)  # BUG fix: drop "& resp5b"
    sa5b = _pstats(all5b, C5b, Y5b)
    sraw5b = _pstats(obs5b, C5b, Y5b)
    sipw5b = _pstats(obs5b, C5b, Y5b, w=w_resp)

    def bias(s, idx):
        """Absolute bias of an observed-schedule slope (`s`, `_pstats` sufficient statistics)
        against the m1=1.5 all-days slope (`sa5b`). Shared by the raw/IPW/IPW-lag-alt bias
        figures below."""
        return abs(_pslope(s, idx) - _pslope(sa5b, idx))

    def frac(s_ipw):
        """Fraction of the raw bias that `s_ipw`'s IPW removes, as a function of `idx`."""
        def f(idx):
            br = bias(sraw5b, idx)
            return 1 - bias(s_ipw, idx) / br if br > 1e-9 else np.nan
        return f

    bias_raw_stat = mc_stat(lambda idx: bias(sraw5b, idx), [N_PERSONS])
    bias_ipw_stat = mc_stat(lambda idx: bias(sipw5b, idx), [N_PERSONS])
    frac_removed_stat = mc_stat(frac(sipw5b), [N_PERSONS])
    removes_less_than_half = _verdict(frac_removed_stat, "le", 0.5)
    p5["response_propensity_ipw_m1_15_random"] = dict(
        bias_raw=bias_raw_stat, bias_ipw=bias_ipw_stat, frac_removed=frac_removed_stat,
        removes_less_than_half=bool(removes_less_than_half))
    p5["PASS"] = bool(p5["m1_05_random_under_5pct"] and p5["m1_15_added_bias_ge_10pct_every_schedule"]
                       and removes_less_than_half)

    # AMBIGUOUS ("it"): as-run/primary reads "removes less than half of it" as the total m1=1.5
    # raw bias (bias_raw_stat above). The alternative -- the audit's more-natural reading -- reads
    # "it" as the bias ADDED over m1=0 (same 'random' schedule): frac of (raw_bias@1.5 -
    # raw_bias@0) that IPW removes. Independent panels (m1=1.5 vs m1=0, G4).
    def raw_bias0_fn(idx):
        sa0, so0 = sa_by_cell["default"], so_by_cell["default"]["random"]
        return abs(_pslope(so0, idx) - _pslope(sa0, idx))

    def frac_removed_it_alt_fn(idx15, idx0):
        raw15, ipw15, raw0 = bias(sraw5b, idx15), bias(sipw5b, idx15), raw_bias0_fn(idx0)
        denom = raw15 - raw0
        return (raw15 - ipw15) / denom if abs(denom) > 1e-9 else np.nan

    frac_removed_it_alt_stat = mc_stat(frac_removed_it_alt_fn, [N_PERSONS, N_PERSONS])
    removes_less_than_half_it_alt = _verdict(frac_removed_it_alt_stat, "le", 0.5)

    # AMBIGUOUS ("lagged composites"): as-run/primary uses one lag (the minimal reading, marked
    # more-natural by the audit). Alternative: several lags (lag 1-3) as additional IPW features.
    lag2 = np.concatenate([np.zeros((n5, 2)), np.nan_to_num(C5b[:, :-2])], axis=1)
    lag3 = np.concatenate([np.zeros((n5, 3)), np.nan_to_num(C5b[:, :-3])], axis=1)
    feats_alt = np.concatenate([np.nan_to_num(C5b)[..., None], lag[..., None], lag2[..., None],
                                 lag3[..., None], dow], axis=-1)
    beta_hat_alt = logistic_irls(feats_alt[admin], yresp)
    p_resp_hat_alt = expit(feats_alt @ beta_hat_alt)
    w_resp_alt = np.where(obs5b, safe_div(1.0, np.clip(p_resp_hat_alt, 0.05, 1.0)), 0.0)
    sipw5b_alt = _pstats(obs5b, C5b, Y5b, w=w_resp_alt)

    bias_ipw_lagalt_stat = mc_stat(lambda idx: bias(sipw5b_alt, idx), [N_PERSONS])
    frac_removed_lagalt_stat = mc_stat(frac(sipw5b_alt), [N_PERSONS])
    removes_less_than_half_lagalt = _verdict(frac_removed_lagalt_stat, "le", 0.5)

    p5["lagged_composites_ambiguous"] = dict(
        as_run_primary="one lag (the minimal reading; the audit's more-natural reading)",
        alternative=dict(bias_ipw=bias_ipw_lagalt_stat, frac_removed=frac_removed_lagalt_stat,
                          removes_less_than_half=bool(removes_less_than_half_lagalt),
                          reading="lag 1-3 as additional response-propensity IPW features"))
    p5["it_ambiguous"] = dict(
        as_run_primary="'it' = the total m1=1.5 raw bias",
        alternative=dict(frac_removed=frac_removed_it_alt_stat,
                          removes_less_than_half=bool(removes_less_than_half_it_alt),
                          reading="'it' = the bias ADDED over m1=0 for the same schedule "
                                  "(the audit's more-natural reading)"))
    preds["P5"] = p5

    # ---- P6: indicator-level attenuation, families default / bernoulli_mix / pi_rises_with_D ----
    # G1: each ind_within_0.03 / higher_by_ge_0.05 check decided on a 95% MC interval, bootstrapped
    # over the (variable-length) list of persons informative for that indicator/cell -- mirrors
    # the audit's own per-person-list bootstrap exactly.
    p6 = {}
    validity_scale_lists = {}  # stashed for the pi_rises_with_D ind4 validity-vs-attenuation ambiguity
    for cell_name in ("default", "bernoulli_mix", "pi_rises_with_D"):
        panel6 = panel_for("S", cell_name)
        used6 = panel6["used"]
        D6 = panel6["D"]
        pi6, pip6 = panel6["pi_t"], panel6["pi_prime"]
        cell_res = {}
        for j, mu_m, kap in ((IDX_MSGLEN, mu_m4, kappa_a4), (IDX_NEGSELF, -1.0, MIX_KAPPA_A5)):
            H6 = panel6["H"][:, :, j]
            X6 = panel6["X"][:, :, j]
            Xf6 = panel6["X_filtered"][:, :, j]
            atts, mcs, atts_f, mcs_f = [], [], [], []
            rH_list, rX_list = [], []
            for i in range(N_PERSONS):
                ok = used6[i]
                if ok.sum() < 10:
                    continue
                h, d = H6[i, ok], D6[i, ok]
                res = attenuation_person(h, d, X6[i, ok], pi6[i, ok], kap, mu_m)
                if res is None:
                    continue
                atts.append(res[0]); mcs.append(res[1]); rH_list.append(res[2]); rX_list.append(res[3])
                # A-fixed's filtered indicator: per spec P6, pi is replaced by pi' here.
                res_f = attenuation_person(h, d, Xf6[i, ok], pip6[i, ok], kap, mu_m)
                if res_f is not None:
                    atts_f.append(res_f[0]); mcs_f.append(res_f[1])
            atts, mcs = np.array(atts), np.array(mcs)
            atts_f, mcs_f = np.array(atts_f), np.array(mcs_f)
            ind = j + 1  # PREREG's 1-based indicator numbering (IDX_MSGLEN=3 -> indicator 4, etc.)
            # 95% MC interval for nanmean(mcs) - nanmean(atts), bootstrapping over the qualifying
            # person list itself (P6 drops uninformative persons); likewise for the filtered pair.
            diff_stat = mc_stat(lambda idx: np.nanmean(mcs[idx]) - np.nanmean(atts[idx]),
                                 [len(atts)], seed=3)
            diff_f_stat = mc_stat(lambda idx: np.nanmean(mcs_f[idx]) - np.nanmean(atts_f[idx]),
                                   [len(atts_f)], seed=3)
            cell_res[f"ind{ind}_att_formula_mean"] = float(np.nanmean(atts))
            cell_res[f"ind{ind}_att_mc_mean"] = float(np.nanmean(mcs))
            cell_res[f"ind{ind}_diff_mc_minus_formula"] = diff_stat
            cell_res[f"ind{ind}_within_0.03"] = bool(_verdict(diff_stat, "within", 0.03))
            cell_res[f"ind{ind}_filtered_att_formula_mean"] = float(np.nanmean(atts_f))
            cell_res[f"ind{ind}_filtered_att_mc_mean"] = float(np.nanmean(mcs_f))
            cell_res[f"ind{ind}_filtered_diff_mc_minus_formula"] = diff_f_stat
            cell_res[f"ind{ind}_filtered_within_0.03"] = bool(_verdict(diff_f_stat, "within", 0.03))
            if cell_name == "pi_rises_with_D" and j == IDX_MSGLEN:
                validity_scale_lists["formula"] = atts
                validity_scale_lists["rH"] = np.array(rH_list)
                validity_scale_lists["rX"] = np.array(rX_list)
        p6[cell_name] = cell_res
    pr = p6["pi_rises_with_D"]
    ind4_diff_stat = pr["ind4_diff_mc_minus_formula"]
    higher_ok = _verdict(ind4_diff_stat, "ge", 0.05)
    p6["pi_rises_signed_departure"] = dict(higher_by_ge_0_05=bool(higher_ok))
    p6["PASS"] = bool(p6["default"]["ind4_within_0.03"] and p6["default"]["ind5_within_0.03"]
                      and p6["default"]["ind4_filtered_within_0.03"] and p6["default"]["ind5_filtered_within_0.03"]
                      and p6["bernoulli_mix"]["ind4_within_0.03"] and p6["bernoulli_mix"]["ind5_within_0.03"]
                      and p6["bernoulli_mix"]["ind4_filtered_within_0.03"]
                      and p6["bernoulli_mix"]["ind5_filtered_within_0.03"]
                      and p6["pi_rises_signed_departure"]["higher_by_ge_0_05"])

    # AMBIGUOUS (P6 validity vs attenuation scale, pi_rises_with_D ind4 only): as-run/primary
    # compares ATTENUATION RATIOS (Att_mc vs Att_formula, above) -- the audit's more-natural
    # reading, since P6's "within 0.03" clauses elsewhere are all on the ratio scale and "the
    # formula" itself outputs a ratio. The alternative compares VALIDITY directly: r(X,D) vs
    # Att_formula * r(H,D) -- smaller in magnitude by a factor of about r(H,D).
    formula_l, rH_l, rX_l = validity_scale_lists["formula"], validity_scale_lists["rH"], validity_scale_lists["rX"]
    validity_diff = rX_l - formula_l * rH_l
    n_v = len(validity_diff)
    validity_stat = mc_stat(lambda idx: np.nanmean(validity_diff[idx]), [n_v])
    p6["validity_vs_attenuation_scale_ambiguous"] = dict(
        as_run_primary="attenuation-ratio scale: Att_mc vs Att_formula (the audit's more-natural reading)",
        alternative=dict(diff_mc_minus_formula=validity_stat,
                          higher_by_ge_0_05=bool(_verdict(validity_stat, "ge", 0.05)),
                          reading="validity scale: r(X,D) vs Att_formula * r(H,D)"))
    preds["P6"] = p6

    # ---- P7: DV sensitivity at least 15 points below DR sensitivity, A-fixed ----
    # G1: independent panels (DR, DV; G4 -- different families, seeded separately).
    # G3 (AMBIGUOUS, as-run primary = Reading 1): both readings reported.
    panel_dr7 = panel_for("DR", "default")
    panel_dv7 = panel_for("DV", "default")
    _, _, alarm_dr7, _ = _run_arch(panel_dr7, "A-fixed", H["A-fixed"]["h"])
    _, _, alarm_dv7, _ = _run_arch(panel_dv7, "A-fixed", H["A-fixed"]["h"])

    def _p7_stats(excl):
        sdr = _sensitivity(alarm_dr7, panel_dr7["t0"], exclude_pre_onset_alarms=excl).astype(float)
        sdv = _sensitivity(alarm_dv7, panel_dv7["t0"], exclude_pre_onset_alarms=excl).astype(float)
        gap = mc_stat(lambda i, j: 100 * (sdr[i].mean() - sdv[j].mean()), [N_PERSONS, N_PERSONS])
        return sdr, sdv, gap

    sens_dr7, sens_dv7, gap_stat7 = _p7_stats(True)
    _, _, gap_stat7_alt = _p7_stats(False)
    preds["P7"] = dict(sens_DR=float(sens_dr7.mean()), sens_DV=float(sens_dv7.mean()),
                        gap_points=gap_stat7, PASS=bool(_verdict(gap_stat7, "ge", 15)),
                        pre_onset_alarm_ambiguous_G3=dict(
                            as_run_primary="pre-onset alarm excludes detection (Reading 1)",
                            alternative=dict(
                                gap_points=gap_stat7_alt, PASS=bool(_verdict(gap_stat7_alt, "ge", 15)),
                                **G3_READINGS)))

    # ---- P8: A-fixed passive-only (schedule none) vs probe-only (random, matched budget), DR ----
    # G1: paired (same DR panel/persons under both architectures). POSTFREEZE re-tune disclosure:
    # H["probe-only"]["h"] is the re-tuned value from the corrected probe_only_C (4-probe baseline
    # block); run 1's value is preserved in tuning.json under "probe_only_h_run1" (see
    # sim/POSTFREEZE-DEVIATIONS.md). G3 (AMBIGUOUS, as-run primary = Reading 1): both readings.
    panel_dr8 = panel_for("DR", "default")
    _, _, alarm_af8, _ = _run_arch(panel_dr8, "A-fixed", H["A-fixed"]["h"])
    rng_po8 = np.random.default_rng(eval_seed(prereg_sha, "DR", "default") + 10)
    Cpo8, reason_po8 = probe_only_C(panel_dr8, rng_po8)
    alarm_po8, _, _ = run_cusum(Cpo8, H["probe-only"]["h"])

    def _p8_stats(excl):
        saf = _sensitivity(alarm_af8, panel_dr8["t0"], exclude_pre_onset_alarms=excl).astype(float)
        spo = _sensitivity(alarm_po8, panel_dr8["t0"], exclude_pre_onset_alarms=excl).astype(float)
        raf = _rmst42(alarm_af8, panel_dr8["t0"], exclude_pre_onset_alarms=excl)
        rpo = _rmst42(alarm_po8, panel_dr8["t0"], exclude_pre_onset_alarms=excl)
        sens_gap = mc_stat(lambda idx: 100 * (saf[idx].mean() - spo[idx].mean()), [N_PERSONS])
        rmst_gap = mc_stat(lambda idx: rpo[idx].mean() - raf[idx].mean(), [N_PERSONS])
        passed = _verdict(sens_gap, "ge", 10) and _verdict(rmst_gap, "ge", 3)
        return saf, spo, raf, rpo, sens_gap, rmst_gap, passed

    saf8, spo8, raf8, rpo8, sens_gap8, rmst_gap8, passed8 = _p8_stats(True)
    _, _, _, _, sens_gap8_alt, rmst_gap8_alt, passed8_alt = _p8_stats(False)
    preds["P8"] = dict(sens_A_fixed=float(saf8.mean()), sens_probe_only=float(spo8.mean()),
                        sens_gap_points=sens_gap8,
                        rmst42_A_fixed=float(raf8.mean()), rmst42_probe_only=float(rpo8.mean()),
                        rmst_gap_days=rmst_gap8, PASS=bool(passed8),
                        pre_onset_alarm_ambiguous_G3=dict(
                            as_run_primary="pre-onset alarm excludes detection (Reading 1)",
                            alternative=dict(
                                sens_gap_points=sens_gap8_alt, rmst_gap_days=rmst_gap8_alt,
                                PASS=bool(passed8_alt), **G3_READINGS)))

    # ---- P9: BD alarm within tracked days 29-49; A-fixed BD sens <= 0.5 * DR sens ----
    # G1: independent panels (BD, DR; G4). G3 (AMBIGUOUS, DR side only -- BD's onset sits inside
    # the baseline, so the BD side has no pre-onset-alarm exclusion by design): both readings of
    # the DR side reported.
    panel_bd9 = panel_for("BD", "default")
    _, _, alarm_bd9, _ = _run_arch(panel_bd9, "A-fixed", H["A-fixed"]["h"])
    sens_bd9_pp = alarm_bd9[:, BASELINE_DAYS:BASELINE_DAYS + 21].any(1).astype(float)

    def _p9_margin(excl):
        sdr9 = _sensitivity(alarm_dr7, panel_dr7["t0"], exclude_pre_onset_alarms=excl).astype(float)
        stat = mc_stat(lambda i, j: sens_bd9_pp[i].mean() - 0.5 * sdr9[j].mean(), [N_PERSONS, N_PERSONS])
        return sdr9, stat

    sens_dr9, margin9 = _p9_margin(True)
    _, margin9_alt = _p9_margin(False)
    preds["P9"] = dict(sens_BD_days29_49=float(sens_bd9_pp.mean()), sens_DR=float(sens_dr9.mean()),
                        margin_BD_minus_halfDR=margin9, PASS=bool(_verdict(margin9, "le", 0.0)),
                        pre_onset_alarm_ambiguous_G3=dict(
                            as_run_primary="pre-onset alarm excludes detection (Reading 1); DR side only",
                            alternative=dict(
                                margin_BD_minus_halfDR=margin9_alt, PASS=bool(_verdict(margin9_alt, "le", 0.0)),
                                **G3_READINGS)))

    # ---- P10: CS FA/month >= 1.5x its S rate, A-fixed ----
    # G1: independent panels (CS, S; G4). Already the pooled FA/month reading -- no G2 ambiguity is
    # flagged for P10 by the audit (it is already consistent with the h-tuning estimand).
    panel_cs10 = panel_for("CS", "default")
    _, reason_cs10, alarm_cs10, _ = _run_arch(panel_cs10, "A-fixed", H["A-fixed"]["h"])

    def p10_ratio(i, j):
        return _fa_pooled(alarm_cs10, reason_cs10, i) / max(_fa_pooled(alarm_s, reason_s, j), 1e-9)

    p10_stat = mc_stat(p10_ratio, [N_PERSONS, N_PERSONS])
    preds["P10"] = dict(fa_CS=fa_rate_for_alarm(alarm_cs10, reason_cs10),
                         fa_S=fa_rate_for_alarm(alarm_s, reason_s),
                         ratio=p10_stat, PASS=bool(_verdict(p10_stat, "ge", 1.5)))

    results = {"prereg_sha256": prereg_sha, "pi_bar": pi_bar, "kappa_a4": kappa_a4, "mu_m4": mu_m4,
               "predictions": preds}
    (HERE / "results.json").write_text(json.dumps(results, indent=2, default=float))

    lines = ["# sim/RESULTS.md", "", "P1 to P3 are pipeline construction checks, not findings.", ""]
    for name in ["P1", "P1b", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]:
        p = preds.get(name, {})
        verdict = "PASS" if p.get("PASS") else "FAIL"
        lines.append(f"## {name}: {verdict}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(p, indent=2, default=float))
        lines.append("```")
        lines.append("")
    (HERE / "RESULTS.md").write_text("\n".join(lines))
    return results


# ----------------------------------------------------------------------------------------------
# metrics(): PREREG section 5 lists metrics that score()'s section-6 predictions never output
# (score() only computes the specific statistics each P1-P10 threshold needs). This subcommand is
# REPORTING ONLY: no thresholds, no PASS/FAIL, no verdicts -- it reuses the same eval_seed()
# panels, the same tuned h/schedule parameters (sim/tuning.json), and the same primitives
# (compute_composite, run_cusum, probe_schedule, mc_stat, _fa_month_pp, _fa_pooled, _sensitivity)
# that --check and score() already exercise. It writes sim/metrics.json and sim/METRICS.md and
# touches nothing score() reads or writes (sim/results.json, sim/RESULTS.md are untouched, and
# --prereg-sha is validated the same way but no PASS/FAIL depends on any number computed here).
# ----------------------------------------------------------------------------------------------
REASON_LABELS = {1: "unused_day", 2: "no_usable_indicator", 3: "low_usage_abstain_v",
                 4: "version_reset_hold_iv"}


def fa_block(alarm, reason):
    """False-flag rate summary for one (alarm, reason) pair: false flags per tracked
    person-month (`_fa_pooled`: pooled total-alarms / total-tracked-months), per total
    person-month (every post-baseline day, regardless of abstention), and the IQR (spread) of
    person-level false-flag rates (`_fa_month_pp`). One helper shared by metrics() (e), (g), (i)
    and (m), which all report some subset of this same triple per family/architecture/cell."""
    total_months = (T_DAYS - BASELINE_DAYS) / 30.0
    fa_pp = _fa_month_pp(alarm, reason)

    def tracked_fn(idx):
        return _fa_pooled(alarm, reason, idx)

    def total_fn(idx):
        return alarm[idx, BASELINE_DAYS:].sum() / (N_PERSONS * total_months)

    def iqr_fn(idx):
        sub = fa_pp[idx]
        return np.nanpercentile(sub, 75) - np.nanpercentile(sub, 25)

    return dict(fa_per_tracked_person_month=mc_stat(tracked_fn, [N_PERSONS]),
                fa_per_total_person_month=mc_stat(total_fn, [N_PERSONS]),
                person_level_fa_rate_iqr=mc_stat(iqr_fn, [N_PERSONS]))


def sens_stat(alarm, onset, window=21):
    """Person-averaged sensitivity within `window` days of onset, with its 95% MC interval:
    `_sensitivity(...).astype(float)` followed by `mc_stat` of its person-mean. One helper shared
    by metrics() (a)'s h-sweep, (h)'s chance baseline, and (m)'s kappa comparison."""
    s = _sensitivity(alarm, onset, window=window).astype(float)
    return mc_stat(lambda idx: s[idx].mean(), [N_PERSONS])


def metrics(prereg_sha):
    H, P, pi_bar, kappa_a4, mu_m4 = _load_frozen("compute metrics")
    total_months = (T_DAYS - BASELINE_DAYS) / 30.0

    panel_cache = {}

    def panel_for(family, cell_name):
        key = (family, cell_name)
        if key not in panel_cache:
            seed = eval_seed(prereg_sha, family, cell_name)
            rng = np.random.default_rng(seed)
            panel_cache[key] = generate_panel(rng, family, cell_params(cell_name), n=N_PERSONS,
                                               pi_bar=pi_bar, kappa_a4=kappa_a4, mu_m4=mu_m4)
        return panel_cache[key]

    arch_cache = {}

    def arch_run(family, cell_name, arch):
        """(C, reason, alarm, in_band) for any of ARCHS_FOR_H ('pop', 'A-naive', 'A-fixed',
        'A-fixed-minus-*') plus 'probe-only', which `_run_arch` does not itself cover (it is a
        CUSUM on probe answers alone, not an indicator composite). Cached per (family, cell,
        arch); a fresh, deterministic rng derived from eval_seed feeds probe_only_C's own
        `random`-schedule draw, mirroring score()'s P8 pattern."""
        key = (family, cell_name, arch)
        if key not in arch_cache:
            if arch == "probe-only":
                panel = panel_for(family, cell_name)
                # CHOICE: offset +10 matches score()'s own P8 probe_only_C draw exactly (same
                # family DR, same eval seed) -- so this metric's probe-only DR sensitivity
                # reproduces P8's sens_probe_only bit-for-bit rather than an independent redraw.
                rng_po = np.random.default_rng(eval_seed(prereg_sha, family, cell_name) + 10)
                C, reason = probe_only_C(panel, rng_po)
                alarm, in_band, _ = run_cusum(C, H["probe-only"]["h"])
                arch_cache[key] = (C, reason, alarm, in_band)
            else:
                arch_cache[key] = _run_arch(panel_for(family, cell_name), arch, H[arch]["h"])
        return arch_cache[key]

    def composite_for(family, cell_name, arch):
        """Composite (C, reason) without running the CUSUM -- used by the (a) h-sweep, which
        varies h against the same composite instead of re-fitting the baseline per h."""
        panel = panel_for(family, cell_name)
        baseline = fit_baseline(panel["X"], panel["used"], panel["L_obs"])
        return compute_composite(panel, arch_features(arch), baseline=baseline)

    out = {}

    # ---- (a) sensitivity-vs-false-flag curve: sweep h on S (false-flag axis) and DR (sensitivity
    # axis), for A-fixed and A-naive. CHOICE: h grid is 15 points geometrically spaced from 0.2x to
    # 3.0x each architecture's own tuned h (A-fixed and A-naive are tuned to very different h
    # scales; a shared absolute grid would put one architecture's whole curve in one corner). ----
    curve = {}
    for arch in ("A-fixed", "A-naive"):
        panel_dr = panel_for("DR", "default")
        Cs, reason_s = composite_for("S", "default", arch)
        Cdr, reason_dr = composite_for("DR", "default", arch)
        onset_dr = panel_dr["t0"]
        h_center = H[arch]["h"]
        h_grid = np.geomspace(0.2 * h_center, 3.0 * h_center, 15)
        points = []
        for h in h_grid:
            alarm_s, _, _ = run_cusum(Cs, float(h))
            alarm_dr, _, _ = run_cusum(Cdr, float(h))
            fa_stat = mc_stat(lambda idx, a=alarm_s, r=reason_s: _fa_pooled(a, r, idx), [N_PERSONS])
            points.append(dict(h=float(h), fa_per_tracked_person_month=fa_stat,
                                sensitivity_within_21d=sens_stat(alarm_dr, onset_dr)))
        curve[arch] = points
    out["a_sensitivity_vs_false_flag_curve"] = dict(
        note="h swept on the default cell; false-flag rate measured on family S, sensitivity "
             "within 21 days of onset measured on family DR, at each swept h.",
        curve=curve)

    # ---- (b) abstention share of person-days, by reason, for every family (A-fixed, default
    # cell); DR additionally at kappa=0.3 (cell kappa03) against kappa=0 (cell default). Measured
    # over post-baseline (tracked-window) person-days, matching where fa_rate_for_alarm and
    # _fa_month_pp already measure "tracked" vs "total". ----
    def abstention_block(family, cell_name):
        _, reason, _, _ = arch_run(family, cell_name, "A-fixed")
        post = reason[:, BASELINE_DAYS:]
        block = {"total_abstention_share": mc_stat(
            lambda idx: (post[idx] > 0).sum() / post[idx].size, [N_PERSONS])}
        for code, label in REASON_LABELS.items():
            block[label] = mc_stat(lambda idx, code=code: (post[idx] == code).sum() / post[idx].size,
                                    [N_PERSONS])
        return block

    abstention = {fam: abstention_block(fam, "default") for fam in FAMILIES}
    abstention_dr_kappa03 = abstention_block("DR", "kappa03")
    out["b_abstention_share_by_family"] = dict(
        note="Reasons: unused_day (no usage), no_usable_indicator, low_usage_abstain_v (feature v), "
             "version_reset_hold_iv (feature iv). Share is of post-baseline (tracked-window) "
             "person-days.",
        by_family=abstention,
        DR_kappa_0_3=abstention_dr_kappa03,
        DR_kappa_0=abstention["DR"])

    # ---- (c) probes per person-month, by family and schedule (the realized budget), A-fixed. ----
    schedules_list = ["none", "fixed", "random", "triggered", "mixed", "current"]

    def probes_block(family, cell_name):
        Caf, reason_af, alarm_af, in_band_af = arch_run(family, cell_name, "A-fixed")
        rng_p = np.random.default_rng(eval_seed(prereg_sha, family, cell_name) + 500)
        block = {}
        for sched in schedules_list:
            kwargs = {SCHED_KW[sched]: P[SCHED_KW[sched]]} if sched in SCHED_KW else {}
            probed, prop, identified = probe_schedule(rng_p, sched, Caf, in_band_af, **kwargs)
            per_person = probed[:, BASELINE_DAYS:].sum(1) / total_months
            stat = mc_stat(lambda idx, pp=per_person: pp[idx].mean(), [N_PERSONS])
            block[sched] = dict(probes_per_person_month=stat, ipw_identified=bool(identified))
        return block

    out["c_probes_per_person_month_by_family_schedule"] = {
        fam: probes_block(fam, "default") for fam in FAMILIES}

    # ---- (d) confirmation rule: PPV of confirmed flags, confirmed false flags per person-month,
    # mean days to confirmation, under random/mixed/triggered, on family DR (A-fixed). A flag's
    # ground truth is true iff it falls in [onset, onset+21) (same window as sensitivity); a flag
    # is confirmed if a probe in [t+1, t+CONFIRM_WINDOW] is observed (probed & responded) and reads
    # at least CONFIRM_MARGIN above the person's baseline-block (days 7/14/21/28) probe mean. ----
    def confirmation_block(schedule):
        panel = panel_for("DR", "default")
        onset = panel["t0"]
        Caf, reason_af, alarm_af, in_band_af = arch_run("DR", "default", "A-fixed")
        rng_c = np.random.default_rng(eval_seed(prereg_sha, "DR", "default") + 700
                                       + schedules_list.index(schedule))
        kwargs = {SCHED_KW[schedule]: P[SCHED_KW[schedule]]} if schedule in SCHED_KW else {}
        probed, prop, identified = probe_schedule(rng_c, schedule, Caf, in_band_af, **kwargs)
        responded = panel["responded"]
        Y = panel["Y"]
        observed = probed & responded

        Yb = Y[:, PROBE_BASELINE_DAYS]
        respb = responded[:, PROBE_BASELINE_DAYS]
        v = np.where(respb, Yb, np.nan)
        cnt = respb.sum(1)
        base_mean = np.where(cnt >= 2, np.nanmean(v, 1), 0.0)

        n, T = alarm_af.shape
        confirmed_true = np.zeros(n)
        confirmed_false = np.zeros(n)
        days_sum = np.zeros(n)
        n_confirmed = np.zeros(n)
        n_flags_total = 0
        for i in range(n):
            flag_days = np.nonzero(alarm_af[i])[0]
            n_flags_total += flag_days.size
            for t in flag_days:
                is_true = (t >= onset[i]) and (t < onset[i] + 21)
                lo, hi = t + 1, min(t + CONFIRM_WINDOW, T - 1) + 1
                if lo >= hi:
                    continue
                window = np.arange(lo, hi)
                hits = window[observed[i, window] & (Y[i, window] - base_mean[i] >= CONFIRM_MARGIN)]
                if hits.size:
                    first = hits.min()
                    n_confirmed[i] += 1
                    days_sum[i] += (first - t)
                    if is_true:
                        confirmed_true[i] += 1
                    else:
                        confirmed_false[i] += 1

        def ppv_fn(idx):
            tp, fp = confirmed_true[idx].sum(), confirmed_false[idx].sum()
            return tp / max(tp + fp, 1e-9)

        def cfa_pm_fn(idx):
            return confirmed_false[idx].sum() / (N_PERSONS * total_months)

        def days_fn(idx):
            return days_sum[idx].sum() / max(n_confirmed[idx].sum(), 1e-9)

        return dict(PPV_confirmed_flags=mc_stat(ppv_fn, [N_PERSONS]),
                    confirmed_false_flags_per_person_month=mc_stat(cfa_pm_fn, [N_PERSONS]),
                    mean_days_to_confirmation=mc_stat(days_fn, [N_PERSONS]),
                    ipw_identified=bool(identified),
                    n_flags_total=int(n_flags_total),
                    n_confirmed_total=int(n_confirmed.sum()),
                    n_confirmed_true=int(confirmed_true.sum()),
                    n_confirmed_false=int(confirmed_false.sum()))

    out["d_confirmation_rule_DR"] = dict(
        note="Ground truth per flag: true iff it falls in [onset, onset+21); confirmed iff a "
             "probe in [t+1, t+7] is observed and reads >= 0.5 above the person's baseline-block "
             "probe mean (section 4's confirmation rule). Family DR, A-fixed.",
        random=confirmation_block("random"),
        mixed=confirmation_block("mixed"),
        triggered=confirmation_block("triggered"))

    # ---- (e) IQR (spread) of person-level false-flag rates, A-fixed, default cell. ----
    iqr_families = ["S", "VA", "SP", "BI", "AV", "DE", "CS"]
    iqr_out = {}
    for fam in iqr_families:
        _, reason, alarm, _ = arch_run(fam, "default", "A-fixed")
        iqr_out[fam] = fa_block(alarm, reason)["person_level_fa_rate_iqr"]
    out["e_person_level_false_flag_rate_iqr"] = iqr_out

    # ---- (f) median days to flag among detected, DR/DV (21 days from onset) and BD (the first 21
    # tracked days, 28:49, per P9's own window -- BD's onset sits inside the baseline). A-fixed. ----
    def dtd_block(fam):
        panel = panel_for(fam, "default")
        _, _, alarm, _ = arch_run(fam, "default", "A-fixed")
        onset = panel["t0"]
        n = alarm.shape[0]
        if fam == "BD":
            day_lo = np.full(n, float(BASELINE_DAYS))
            day_hi = np.full(n, float(BASELINE_DAYS + 21))
        else:
            day_lo, day_hi = onset, onset + 21
        dtd = _days_to_detect(alarm, onset, day_lo, day_hi)
        stat = mc_stat(lambda idx: np.nanmedian(dtd[idx]), [N_PERSONS])
        return dict(median_days_to_detect=stat, n_detected=int(np.sum(~np.isnan(dtd))))

    out["f_median_days_to_detect_among_detected"] = {fam: dtd_block(fam) for fam in ("DR", "DV", "BD")}

    # ---- (g) false flags per TOTAL person-month beside per TRACKED person-month, every family. ----
    fa_totals = {}
    for fam in FAMILIES:
        _, reason, alarm, _ = arch_run(fam, "default", "A-fixed")
        block = fa_block(alarm, reason)
        fa_totals[fam] = dict(fa_per_tracked_person_month=block["fa_per_tracked_person_month"],
                               fa_per_total_person_month=block["fa_per_total_person_month"])
    out["g_false_flags_per_total_vs_tracked_person_month"] = fa_totals

    # ---- (h) chance baseline: for each architecture (incl. probe-only), simulate a rule that
    # flags on random TRACKED days on DR at the SAME realized false-flag rate that architecture
    # gets on S, and report its sensitivity within 21 days beside the architecture's own observed
    # DR sensitivity. CHOICE: simulated (not a Poisson-window closed form) -- one random draw per
    # architecture from a fixed rng derived from eval_seed, not resampled inside mc_stat, exactly
    # how every probe-schedule draw elsewhere in this file is handled; "tracked" uses that SAME
    # architecture's own tracked-day pattern on the DR panel (reason == 0), so the chance rule
    # only gets to flag where the real rule could have. ----
    chance = {}
    panel_dr_h = panel_for("DR", "default")
    onset_h = panel_dr_h["t0"]
    for arch_idx, arch in enumerate(ARCHS_FOR_H):
        _, reason_s_h, alarm_s_h, _ = arch_run("S", "default", arch)
        _, reason_dr_h, alarm_dr_h, _ = arch_run("DR", "default", arch)
        fa_rate_s_h = fa_rate_for_alarm(alarm_s_h, reason_s_h)
        p_day = fa_rate_s_h / 30.0
        tracked_dr_h = np.zeros_like(reason_dr_h, dtype=bool)
        tracked_dr_h[:, BASELINE_DAYS:] = (reason_dr_h[:, BASELINE_DAYS:] == 0)
        rng_chance = np.random.default_rng(eval_seed(prereg_sha, "DR", "default") + 5000 + arch_idx)
        chance_alarm = (rng_chance.random(alarm_dr_h.shape) < p_day) & tracked_dr_h
        chance[arch] = dict(
            realized_fa_per_tracked_person_month_on_S=float(fa_rate_s_h),
            chance_sensitivity_within_21d=sens_stat(chance_alarm, onset_h),
            observed_sensitivity_within_21d=sens_stat(alarm_dr_h, onset_h))
    out["h_chance_baseline_sensitivity_vs_observed"] = dict(
        note="Chance rule: independent random flags on DR's own tracked days (per this "
             "architecture), at the per-day rate implied by that architecture's realized "
             "false-flag rate on S; simulated once per architecture (not a Poisson closed form).",
        by_architecture=chance)

    # ---- (i) realized false flags per tracked and per total person-month on S, every
    # architecture (incl. probe-only and pop), with the IQR across persons. ----
    s_fa_by_arch = {}
    for arch in ARCHS_FOR_H:
        _, reason_s_i, alarm_s_i, _ = arch_run("S", "default", arch)
        s_fa_by_arch[arch] = fa_block(alarm_s_i, reason_s_i)
    out["i_realized_false_flags_on_S_by_architecture"] = s_fa_by_arch

    # ---- (j) P3's reset cost: A-fixed DR sensitivity for onsets landing inside the 14-day
    # re-baseline window after a logged version change, vs with no version change. Families are
    # mutually exclusive scenario channels (sample_events only sets av_day for AV/AV2, t0 only for
    # DR/DV/BD) -- checked programmatically below rather than assumed. ----
    dr_panel_j = panel_for("DR", "default")
    av_panel_j = panel_for("AV", "default")
    dr_has_version_change = bool(np.any(~np.isnan(dr_panel_j["av_day"]) & dr_panel_j["av_logged"]))
    av_has_drift_onset = bool(np.any(~np.isnan(av_panel_j["t0"])))
    assert not dr_has_version_change and not av_has_drift_onset, (
        "a combined drift/version-change panel unexpectedly exists -- families were assumed to be "
        "mutually exclusive scenario channels (sample_events only sets av_day for AV/AV2, t0 only "
        "for DR/DV/BD); j_p3_reset_cost's 'not computable' reason below no longer holds and this "
        "metric needs an actual computation, not just the fixed reason string."
    )
    out["j_p3_reset_cost"] = dict(
        computable=False,
        reason="not computable from the frozen panels: families are mutually exclusive "
               "scenario channels -- DR's av_day/av_logged are all-NaN/False (no version-change "
               "event is generated for the DR family) and AV's t0 is all-NaN (no drift onset is "
               "generated for the AV family), so no frozen panel has both a drift onset and a "
               "logged version change to measure the re-baseline window's sensitivity cost "
               "against.")

    # ---- (k) the `current` control's own value in the default cell (slope, corr vs all-days),
    # family S, A-fixed -- distinct from the isolated common-lam/pop-z-scaling mechanism check_c
    # exercises (score()'s own --check (c) / P4's current_check_isolated_mechanism). This is the
    # ordinary `current` schedule run on the same S/A-fixed panel used throughout, reported with
    # no threshold, per PREREG P4's own text ("in the default cell its value is reported without
    # a threshold"). ----
    panel_k = panel_for("S", "default")
    Ck, reason_k, alarm_k, band_k = arch_run("S", "default", "A-fixed")
    Yk, respk = panel_k["Y"], panel_k["responded"]
    post_mask_k = np.zeros_like(reason_k, dtype=bool)
    post_mask_k[:, BASELINE_DAYS:] = True
    all_mask_k = post_mask_k & ~np.isnan(Ck)
    rng_k = np.random.default_rng(eval_seed(prereg_sha, "S", "default") + 6000)
    probed_k, prop_k, id_k = probe_schedule(rng_k, "current", Ck, band_k, c_star=P["c_star"])
    obs_k = probed_k & respk & ~np.isnan(Ck) & post_mask_k
    sa_k = _pstats(all_mask_k, Ck, Yk)
    sc_k = _pstats(obs_k, Ck, Yk)
    out["k_current_control_default_cell"] = dict(
        note="Ordinary `current` schedule (probe when C_t > c*) on family S / A-fixed / default "
             "cell; reported without a threshold, per PREREG P4's own text.",
        all_days=dict(slope=mc_stat(lambda idx: _pslope(sa_k, idx), [N_PERSONS]),
                       corr=mc_stat(lambda idx: _pcorr_unweighted(sa_k, idx), [N_PERSONS])),
        current=dict(slope=mc_stat(lambda idx: _pslope(sc_k, idx), [N_PERSONS]),
                      corr=mc_stat(lambda idx: _pcorr_unweighted(sc_k, idx), [N_PERSONS])),
        ipw_identified=bool(id_k))

    # ---- (l) pop's DR sensitivity and S false flags -- pulled from (h)/(i) above (pop is one of
    # ARCHS_FOR_H in both), not recomputed. ----
    out["l_pop_architecture"] = dict(
        DR_sensitivity_within_21d=chance["pop"]["observed_sensitivity_within_21d"],
        S_false_flags=dict(
            fa_per_tracked_person_month=s_fa_by_arch["pop"]["fa_per_tracked_person_month"],
            fa_per_total_person_month=s_fa_by_arch["pop"]["fa_per_total_person_month"]))

    # ---- (m) kappa=0.3 cell: A-fixed DR sensitivity, abstention share, and false flags, vs
    # kappa=0 (the default cell). Abstention shares reuse the (b) block's DR entries. ----
    kappa_sens, kappa_fa = {}, {}
    for cell_m, label_m in (("default", "kappa_0"), ("kappa03", "kappa_0_3")):
        panel_m = panel_for("DR", cell_m)
        _, reason_m, alarm_m, _ = arch_run("DR", cell_m, "A-fixed")
        onset_m = panel_m["t0"]
        kappa_sens[label_m] = sens_stat(alarm_m, onset_m)
        block = fa_block(alarm_m, reason_m)
        kappa_fa[label_m] = dict(fa_per_tracked_person_month=block["fa_per_tracked_person_month"],
                                  fa_per_total_person_month=block["fa_per_total_person_month"])
    out["m_kappa_0_3_vs_kappa_0_cell_DR"] = dict(
        DR_sensitivity_within_21d=kappa_sens,
        DR_false_flags=kappa_fa,
        DR_abstention_share=dict(kappa_0=abstention["DR"], kappa_0_3=abstention_dr_kappa03))

    # ---- (n) P6 indicator-5 sign-flip check in the pi_rises_with_D cell: the simulated
    # within-person validity itself (raw r(X5,D) and filtered r(Xfiltered5,D)), person-averaged
    # with a bootstrap interval -- not the attenuation-ratio scale P6 itself reports. mu_M5 = -1.0
    # sits BELOW indicator 5's own mean, opposite in sign to indicator 4's mu_M4 case (which P6
    # already flags as a positive spurious coupling), so this checks for a sign flip rather than
    # just extra attenuation. Reuses the same per-person qualifying-list bootstrap P6 uses
    # (variable-length list, not N_PERSONS). ----
    panel_n = panel_for("S", "pi_rises_with_D")
    used_n, D_n = panel_n["used"], panel_n["D"]
    X5_n, Xf5_n, H5_n = (panel_n["X"][:, :, IDX_NEGSELF], panel_n["X_filtered"][:, :, IDX_NEGSELF],
                          panel_n["H"][:, :, IDX_NEGSELF])
    rX_list, rXf_list, rH_list = [], [], []
    for i in range(N_PERSONS):
        ok = used_n[i]
        if ok.sum() < 10:
            continue
        d = D_n[i, ok]
        if d.std() < 1e-9:
            continue
        x, xf, h = X5_n[i, ok], Xf5_n[i, ok], H5_n[i, ok]
        if x.std() > 1e-9:
            rX_list.append(np.corrcoef(x, d)[0, 1])
        if xf.std() > 1e-9:
            rXf_list.append(np.corrcoef(xf, d)[0, 1])
        if h.std() > 1e-9:
            rH_list.append(np.corrcoef(h, d)[0, 1])
    rX_arr, rXf_arr, rH_arr = np.array(rX_list), np.array(rXf_list), np.array(rH_list)
    out["n_indicator5_validity_pi_rises_with_D"] = dict(
        note="Person-averaged within-person correlation of indicator 5 (negative self-reference) "
             "with D, in the pi_rises_with_D cell, family S -- raw (X) and authorship-filtered "
             "(X_filtered, mixed with pi'); r(H5,D), the unmixed reference, is included for scale.",
        raw_validity_corr_X5_D=mc_stat(lambda idx: np.nanmean(rX_arr[idx]), [len(rX_arr)], seed=9),
        filtered_validity_corr_X5_D=mc_stat(lambda idx: np.nanmean(rXf_arr[idx]), [len(rXf_arr)], seed=9),
        reference_unmixed_corr_H5_D=mc_stat(lambda idx: np.nanmean(rH_arr[idx]), [len(rH_arr)], seed=9),
        n_persons_raw=int(len(rX_arr)), n_persons_filtered=int(len(rXf_arr)))

    # ---- (o) analytic P6 attenuation formula evaluated at the pilot's own parameter sets (read
    # from pilot/indicator4_params.json, never hard-coded), both raw and authorship-filtered
    # (pi -> pi'). Population-level formula (E[pi] etc from the Beta(10 pi_bar, 10(1-pi_bar))
    # distribution directly) -- the VH=1 idealization check_d's own "beta-pilot" case already uses
    # (reproduces its ~0.235 for the entry-level parameters), not the per-person VH-normalized
    # version P6/attenuation_person compute. ----
    def att_formula_value(pi_bar_v, kappa_v, delta_v):
        Epi = pi_bar_v
        Varpi = pi_bar_v * (1 - pi_bar_v) / 11.0  # exact: Beta(10 pi_bar, 10(1-pi_bar)), a+b=10
        Epi2 = Varpi + Epi ** 2
        return _att(Epi, Epi2, Varpi, kappa_v, delta_v)

    def att_formula_value_filtered(pi_bar_v, kappa_v, delta_v, n=2_000_000, seed=4):
        # pi' = 0.1 pi / (0.1 pi + 0.95 (1 - pi)) has no closed-form Beta moments; estimated from
        # a large, deterministic Monte Carlo draw (not an eval-seed/simulated-person quantity).
        rng_o = np.random.default_rng(seed)
        pi_o = rng_o.beta(10 * pi_bar_v, 10 * (1 - pi_bar_v), n)
        pip_o = 0.1 * pi_o / (0.1 * pi_o + 0.95 * (1 - pi_o))
        Epi, Epi2, Varpi = pip_o.mean(), (pip_o ** 2).mean(), pip_o.var()
        E1mpi2 = ((1 - pip_o) ** 2).mean()
        return (1 - Epi) / np.sqrt(E1mpi2 + Epi2 * kappa_v + Varpi * delta_v ** 2)

    pilot_params = json.loads((HERE.parent / "pilot" / "indicator4_params.json").read_text())
    mt_o, dl_o = pilot_params["main_thread"], pilot_params["day_level_main_thread"]
    o_sets = {
        "entry_level_main_thread": dict(pi_bar=mt_o["pi_bar_daymean"], kappa=mt_o["kappa_a"],
                                         delta=mt_o["mu_M4_humanSD"]),
        "day_level_main_thread": dict(pi_bar=dl_o["pi_bar_daymean"], kappa=dl_o["kappa_a_day"],
                                       delta=dl_o["mu_M4_day"]),
    }
    o_out = {}
    for label, prm in o_sets.items():
        o_out[label] = dict(
            pi_bar=prm["pi_bar"], kappa=prm["kappa"], delta=prm["delta"],
            att_formula_raw=float(att_formula_value(prm["pi_bar"], prm["kappa"], prm["delta"])),
            att_formula_filtered=float(att_formula_value_filtered(prm["pi_bar"], prm["kappa"], prm["delta"])))
    out["o_analytic_attenuation_pilot_params"] = dict(
        note="Att = (1 - E pi) / sqrt(E[(1-pi)^2] + E[pi^2] kappa + Var(pi) delta^2), pi ~ "
             "Beta(10 pi_bar, 10(1-pi_bar)); E[pi]/Var(pi) in closed form (E[pi]=pi_bar, "
             "Var(pi)=pi_bar(1-pi_bar)/11 since the Beta's a+b=10 always). Filtered substitutes "
             "pi' = 0.1 pi / (0.1 pi + 0.95 (1-pi)) throughout; pi' has no closed-form moments, so "
             "they are estimated from a 2,000,000-draw Monte Carlo integral (deterministic, seed "
             "4) rather than simulated persons. Parameters are read from "
             "pilot/indicator4_params.json, not hard-coded.",
        params=o_out)

    # ---- (p) person-level validity; see note. ----
    def _person_r_dist(vals, tracked, D):
        r_list = []
        for i in range(N_PERSONS):
            ok = tracked[i] & ~np.isnan(vals[i]) & ~np.isnan(D[i])
            if ok.sum() < 10:
                continue
            d, v = D[i, ok], vals[i, ok]
            if d.std() < 1e-9 or v.std() < 1e-9:
                continue
            r_list.append(float(np.corrcoef(v, d)[0, 1]))
        r = np.array(r_list)
        quantiles = dict(zip(("p5", "p25", "p50", "p75", "p95"),
                              (float(x) for x in np.percentile(r, [5, 25, 50, 75, 95]))))
        return dict(quantiles=quantiles,
                    share_r_le_0=float(np.mean(r <= 0)),
                    mean_r=mc_stat(lambda idx, r=r: np.nanmean(r[idx]), [r.size], seed=9),
                    n_persons=int(r.size))

    def person_validity_block(family):
        panel_p = panel_for(family, "default")
        Cp, reason_p, _, _ = arch_run(family, "default", "A-fixed")
        tracked_p = np.zeros_like(reason_p, dtype=bool)
        tracked_p[:, BASELINE_DAYS:] = reason_p[:, BASELINE_DAYS:] == 0
        Dp = panel_p["D"]
        indicators = {"indicator4": IDX_MSGLEN, "indicator5": IDX_NEGSELF}
        return dict(composite_A_fixed=_person_r_dist(Cp, tracked_p, Dp),
                    **{f"{name}_{kind}": _person_r_dist(panel_p[key][:, :, idx], tracked_p, Dp)
                       for name, idx in indicators.items()
                       for kind, key in (("raw", "X"), ("filtered", "X_filtered"))})

    out["p_person_level_validity"] = dict(
        note="Within-person correlation of the A-fixed composite (and the raw/authorship-"
             "filtered single indicators 4 and 5, IDX_MSGLEN/IDX_NEGSELF) with the true D, over "
             "tracked (post-baseline, reason==0) days; frozen default-cell panels, families S "
             "and DR. Distribution across qualifying persons (>=10 tracked days, non-degenerate "
             "D and indicator variance): quantiles 5/25/50/75/95, share of persons with r <= 0, "
             "and the person-averaged mean with a 2000-draw person bootstrap interval (mc_stat, "
             "the same variable-length-list pattern as item (n)).",
        S=person_validity_block("S"),
        DR=person_validity_block("DR"))

    # (q) triggered reuses P4's rng (eval_seed+1, drawn first); current uses unused offset +6200.
    panel_q = panel_for("S", "default")
    Cq, reason_q, _, band_q = arch_run("S", "default", "A-fixed")
    Yq, resp_q = panel_q["Y"], panel_q["responded"]
    post_mask_q = np.zeros_like(reason_q, dtype=bool)
    post_mask_q[:, BASELINE_DAYS:] = True
    all_mask_q = post_mask_q & ~np.isnan(Cq)

    rng_trig_q = np.random.default_rng(eval_seed(prereg_sha, "S", "default") + 1)
    probed_tq, _, id_tq = probe_schedule(rng_trig_q, "triggered", Cq, band_q, p_trig=P["p_trig"])
    obs_tq = probed_tq & resp_q & ~np.isnan(Cq) & post_mask_q

    rng_cur_q = np.random.default_rng(eval_seed(prereg_sha, "S", "default") + 6200)
    probed_cq, _, id_cq = probe_schedule(rng_cur_q, "current", Cq, band_q, c_star=P["c_star"])
    obs_cq = probed_cq & resp_q & ~np.isnan(Cq) & post_mask_q

    sa_q = _pstats(all_mask_q, Cq, Yq)
    st_q = _pstats(obs_tq, Cq, Yq)
    sc_q = _pstats(obs_cq, Cq, Yq)

    def _q_block(s):
        return dict(
            slope=mc_stat(lambda idx: _pslope(s, idx), [N_PERSONS]),
            corr=mc_stat(lambda idx: _pcorr_unweighted(s, idx), [N_PERSONS]),
            corr_deflation=mc_stat(lambda idx: _pcorr_unweighted(sa_q, idx) - _pcorr_unweighted(s, idx),
                                    [N_PERSONS]),
            slope_attenuation_rel=mc_stat(
                lambda idx: (_pslope(sa_q, idx) - _pslope(s, idx)) / _pslope(sa_q, idx), [N_PERSONS]))

    out["q_current_vs_triggered_P4"] = dict(
        note="`current` control (probe when C_t > c*) computed on exactly the same S/A-fixed/"
             "default panel, composite, all-days mask and person-centred sufficient statistics "
             "as P4's triggered schedule; triggered here reproduces P4's own numbers bit-for-bit "
             "(same rng offset, drawn first from a fresh rng). Reported without a threshold, per "
             "PREREG P4's own text ('in the default cell its value is reported without a "
             "threshold'). corr_deflation and slope_attenuation_rel are signed, vs all-days, "
             "exactly as P4's own fields.",
        all_days=dict(slope=mc_stat(lambda idx: _pslope(sa_q, idx), [N_PERSONS]),
                       corr=mc_stat(lambda idx: _pcorr_unweighted(sa_q, idx), [N_PERSONS])),
        triggered=_q_block(st_q),
        current=_q_block(sc_q),
        ipw_identified_triggered=bool(id_tq),
        ipw_identified_current=bool(id_cq))

    metrics_out = {"prereg_sha256": prereg_sha, "pi_bar": pi_bar, "kappa_a4": kappa_a4,
                   "mu_m4": mu_m4, "reporting_only": True, "metrics": out}
    (HERE / "metrics.json").write_text(json.dumps(metrics_out, indent=2, default=float))

    md = ["# sim/METRICS.md", "", "REPORTING ONLY: PREREG section 5 metrics that `score()` does",
          "not output. No thresholds and no verdicts are computed or implied here -- every number",
          "below is a plain report, with a 95% Monte Carlo interval from a 2000-draw person",
          "bootstrap (`mc_stat`), exactly as score()'s predictions use. \"Flag\" is this file's word",
          "for a CUSUM alarm; \"tracked\" person-months count only days the layer did not abstain,",
          "\"total\" person-months count every post-baseline day regardless of abstention.", ""]

    def section(title, body_lines):
        md.append(f"## {title}")
        md.append("")
        md.extend(body_lines)
        md.append("")

    def jb(obj):
        return ["```json", json.dumps(obj, indent=2, default=float), "```"]

    # One section per `out` entry, in insertion order (a) through (o): the heading is the key
    # itself, followed by the entry's JSON -- which already carries its own "note" field wherever
    # one applies -- instead of a 15 hand-written title/blurb pair kept in sync with `out` by hand.
    for key, value in out.items():
        section(key, jb(value))

    (HERE / "METRICS.md").write_text("\n".join(md))
    return metrics_out


# ----------------------------------------------------------------------------------------------
# robust: EXPLORATORY grid over the frozen defaults (sim/ROBUSTNESS-PLAN.md -- referee round-1 item
# 14 / round-2 N5). NOT part of sim/PREREG.md or specs/; no P1-P10 verdict is touched. Every output
# is headed "EXPLORATORY, not frozen". Reuses generate_panel, cell_params, compute_composite,
# run_cusum, probe_schedule, fit_baseline, _run_arch, probe_only_C, mc_stat, _pstats/_pslope/
# _pcorr_*, _sensitivity/sens_stat, fa_rate_for_alarm/_fa_pooled, attenuation_person/_att and
# logistic_irls exactly as --check/tune/score/metrics already do; no generator mechanics change.
# ----------------------------------------------------------------------------------------------
ROBUSTNESS_PLAN_PATH = HERE / "ROBUSTNESS-PLAN.md"


def robust_seed(plan_sha, *parts):
    """The only sanctioned way to get a robustness-grid seed (sim/ROBUSTNESS-PLAN.md section (d)):
    refuses to run unless sha256(sim/ROBUSTNESS-PLAN.md) matches `plan_sha`, mirroring eval_seed()'s
    refusal on sim/PREREG.md. The literal "robust" tag plus the plan's own sha256 make every seed
    disjoint from eval_seed()'s (hashed from a different file, no "robust" literal) and from the
    fixed tuning seed 20260927 (a bare constant, not a hash)."""
    if not ROBUSTNESS_PLAN_PATH.exists():
        raise RuntimeError("sim/ROBUSTNESS-PLAN.md is missing; cannot derive a robustness seed.")
    on_disk = hashlib.sha256(ROBUSTNESS_PLAN_PATH.read_bytes()).hexdigest()
    if on_disk != plan_sha:
        raise RuntimeError(
            f"--plan-sha {plan_sha!r} does not match sim/ROBUSTNESS-PLAN.md's sha256 {on_disk!r}. "
            "Robustness seeds are only derived from the committed, hashed plan."
        )
    tag = ":".join(["robust", plan_sha, *(str(p) for p in parts)]).encode()
    return int(hashlib.sha256(tag).hexdigest()[:16], 16) % (2**32 - 1)


def _psi_scaled(val):
    """PSI with its two nonzero entries (indicators 2 and 3, IDX_FRAG/IDX_DEFER -- the only slots
    the frozen spec gives a nonzero psi) both set to `val`; indicators 1, 4, 5, 6 stay 0, exactly
    as in the frozen PSI array. Grid cells vary this shared scalar, not the per-indicator shape."""
    out = np.zeros(N_IND)
    out[IDX_FRAG] = val
    out[IDX_DEFER] = val
    return out


def _robust_grid():
    """The one-at-a-time grid, sim/ROBUSTNESS-PLAN.md section (a). A function (not a module-level
    constant) so it re-reads pilot/indicator4_params.json fresh on every call, same as metrics()'s
    item (o) does, instead of caching a stale read across a long-running process. Every cell is
    computable: generate_panel's phi_D/psi/rising_slope keyword arguments (added for this grid, each
    defaulting to the frozen constant) make every dimension in the plan's table reachable without
    changing the generator's mechanics or any frozen output (see sim/ROBUSTNESS-PLAN.md section (a)
    for the byte-identical proof against sim/results.json and sim/metrics.json)."""
    dl = json.loads((HERE.parent / "pilot" / "indicator4_params.json").read_text())["day_level_main_thread"]
    return [
        dict(name="default", dimension="(baseline)", value="frozen default", cell_name="default",
             gen_kwargs={}),
        dict(name="lam_low", dimension="lam_range", value=[0.10, 0.25], cell_name="default",
             gen_kwargs=dict(lam_range=(0.10, 0.25))),
        dict(name="lam_high", dimension="lam_range", value=[0.50, 0.80], cell_name="default",
             gen_kwargs=dict(lam_range=(0.50, 0.80))),
        dict(name="phi_D_low", dimension="phi_D", value=0.3, cell_name="default",
             gen_kwargs=dict(phi_D=0.3)),
        dict(name="phi_D_high", dimension="phi_D", value=0.9, cell_name="default",
             gen_kwargs=dict(phi_D=0.9)),
        dict(name="psi_low", dimension="psi", value=0.25, cell_name="default",
             gen_kwargs=dict(psi=_psi_scaled(0.25))),
        dict(name="psi_high", dimension="psi", value=1.0, cell_name="default",
             gen_kwargs=dict(psi=_psi_scaled(1.0))),
        dict(name="ind4_daylevel", dimension="indicator4_contamination", value="day-level pilot",
             cell_name="default",
             gen_kwargs=dict(pi_bar=dl["pi_bar_daymean"], kappa_a4=dl["kappa_a_day"],
                              mu_m4=dl["mu_M4_day"])),
        dict(name="rising_slope_025", dimension="rising_share_logit_slope", value=0.25,
             cell_name="default", gen_kwargs=dict(rising_slope=0.25)),
        dict(name="rising_slope_10", dimension="rising_share_logit_slope", value=1.0,
             cell_name="default", gen_kwargs=dict(rising_slope=1.0)),
        dict(name="m1_15", dimension="m1", value=1.5, cell_name="m1_15", gen_kwargs={}),
    ]


def _robust_tune_all(plan_sha, cell):
    """Re-tune h for every ARCHS_FOR_H architecture at this cell's own lam_range/phi_D/psi/
    indicator-4-contamination values (sim/ROBUSTNESS-PLAN.md section (e)); m1 and rising_slope do
    not affect the composite (m1 only touches Y/response; rising_slope only applies inside the
    pi_rises_with_D mix mode, never used by tuning's own always-"default" cell), so tuning under an
    m1- or rising_slope-only cell reproduces the default's h up to independent seed noise, by design.
    `cell["gen_kwargs"]` is passed straight through: tune_h's own keyword defaults already equal the
    frozen constants, so a key this cell doesn't vary falls back to exactly what the old per-key
    `.get(..., DEFAULT)` extraction produced."""
    H_cell = {}
    for arch in ARCHS_FOR_H:
        seed = robust_seed(plan_sha, "tune", cell["name"], arch)
        H_cell[arch] = tune_h(arch, seed=seed, cell_name=cell["cell_name"], **cell["gen_kwargs"])
    return H_cell


def _robust_family_panel(plan_sha, family, cell, extra, cell_name_override=None):
    seed = robust_seed(plan_sha, family, cell["name"], extra)
    rng = np.random.default_rng(seed)
    cn = cell_name_override if cell_name_override is not None else cell["cell_name"]
    cp = cell_params(cn)
    return generate_panel(rng, family, cp, n=N_PERSONS, **cell["gen_kwargs"])


def _s1_selection_attenuation(plan_sha, cell, H_cell, P_frozen):
    """S1: triggered/current attenuate the probe-on-composite slope vs all-days. Tested as the
    RATIO of the probed-day slope to the all-days slope being < 1, not a signed difference: a
    signed difference's sign depends on the (arbitrary) sign of the all-days slope itself, while
    the ratio test is attenuation-direction-invariant (b_obs/b_all < 1 means |b_obs| < |b_all| with
    the same relative orientation, whether b_all is positive or negative)."""
    panel = _robust_family_panel(plan_sha, "S", cell, "s1")
    h = H_cell["A-fixed"]["h"]
    C, reason, alarm, band = _run_arch(panel, "A-fixed", h)
    Y, resp = panel["Y"], panel["responded"]
    post = np.zeros_like(reason, dtype=bool)
    post[:, BASELINE_DAYS:] = True
    all_mask = post & ~np.isnan(C)
    sa = _pstats(all_mask, C, Y)
    out = {}
    rng_p = np.random.default_rng(robust_seed(plan_sha, "s1_probe", cell["name"]))
    for sched, kw in (("triggered", dict(p_trig=P_frozen["p_trig"])),
                      ("current", dict(c_star=P_frozen["c_star"]))):
        probed, prop, ident = probe_schedule(rng_p, sched, C, band, **kw)
        obs = probed & resp & ~np.isnan(C) & post
        so = _pstats(obs, C, Y)
        ratio_stat = mc_stat(lambda idx, sa=sa, so=so: _pslope(so, idx) / _pslope(sa, idx),
                              [N_PERSONS])
        out[sched] = dict(slope_ratio_obs_over_all=ratio_stat,
                           holds=bool(_verdict(ratio_stat, "le", 1.0)))
    out["holds"] = bool(out["triggered"]["holds"] and out["current"]["holds"])
    return out


def _s2_state_coupled_sign(plan_sha, cell):
    """S2: in pi_rises_with_D, indicator 4's attenuation ratio is inflated vs the independent-pi
    formula, indicator 5's is deflated. Does not depend on m1, so this panel always uses m1=0.
    Passes through this cell's full gen_kwargs (lam_range, phi_D, psi, indicator-4 contamination,
    rising_slope), so e.g. the rising_slope_025/rising_slope_10 cells actually vary the coupling
    strength this check is about."""
    gk = cell["gen_kwargs"]
    kappa_a4 = gk.get("kappa_a4", KAPPA_A4_DEFAULT)
    mu_m4 = gk.get("mu_m4", MU_M4_DEFAULT)
    panel = _robust_family_panel(plan_sha, "S", cell, "s2_pi_rises",
                                  cell_name_override="pi_rises_with_D")
    used, D = panel["used"], panel["D"]
    out = {}
    for ind_label, j, mu_m, kap in (("indicator4", IDX_MSGLEN, mu_m4, kappa_a4),
                                     ("indicator5", IDX_NEGSELF, -1.0, MIX_KAPPA_A5)):
        H_, X_, pi_ = panel["H"][:, :, j], panel["X"][:, :, j], panel["pi_t"]
        atts, mcs = [], []
        for i in range(N_PERSONS):
            ok = used[i]
            if ok.sum() < 10:
                continue
            res = attenuation_person(H_[i, ok], D[i, ok], X_[i, ok], pi_[i, ok], kap, mu_m)
            if res is None:
                continue
            atts.append(res[0]); mcs.append(res[1])
        atts, mcs = np.array(atts), np.array(mcs)
        diff_stat = mc_stat(lambda idx: np.nanmean(mcs[idx]) - np.nanmean(atts[idx]),
                             [len(atts)], seed=3)
        out[ind_label] = dict(diff_mc_minus_formula=diff_stat, n_persons=int(len(atts)))
    out["indicator4"]["holds"] = bool(_verdict(out["indicator4"]["diff_mc_minus_formula"], "ge", 0.0))
    out["indicator5"]["holds"] = bool(_verdict(out["indicator5"]["diff_mc_minus_formula"], "le", 0.0))
    out["holds"] = bool(out["indicator4"]["holds"] and out["indicator5"]["holds"])
    return out


def _s3_s4_chance_baseline(plan_sha, cell, H_cell):
    """S3: every passive rule beats its own chance baseline. S4: probe-only does not (within chance).
    Chance rule and matched-false-flag-rate logic mirror metrics.json item (h) exactly."""
    panel_s = _robust_family_panel(plan_sha, "S", cell, "s3s4_S")
    panel_dr = _robust_family_panel(plan_sha, "DR", cell, "s3s4_DR")
    onset = panel_dr["t0"]
    out = {}
    for arch in ARCHS_FOR_H:
        h = H_cell[arch]["h"]
        if arch == "probe-only":
            rng_po_s = np.random.default_rng(robust_seed(plan_sha, "s3s4_po_S", cell["name"]))
            C_s, reason_s = probe_only_C(panel_s, rng_po_s)
            alarm_s, _, _ = run_cusum(C_s, h)
            rng_po_dr = np.random.default_rng(robust_seed(plan_sha, "s3s4_po_DR", cell["name"]))
            C_dr, reason_dr = probe_only_C(panel_dr, rng_po_dr)
            alarm_dr, _, _ = run_cusum(C_dr, h)
        else:
            _, reason_s, alarm_s, _ = _run_arch(panel_s, arch, h)
            _, reason_dr, alarm_dr, _ = _run_arch(panel_dr, arch, h)
        fa_rate_s = fa_rate_for_alarm(alarm_s, reason_s)
        p_day = fa_rate_s / 30.0
        tracked_dr = np.zeros_like(reason_dr, dtype=bool)
        tracked_dr[:, BASELINE_DAYS:] = (reason_dr[:, BASELINE_DAYS:] == 0)
        rng_chance = np.random.default_rng(robust_seed(plan_sha, "s3s4_chance", cell["name"], arch))
        chance_alarm = (rng_chance.random(alarm_dr.shape) < p_day) & tracked_dr
        obs_bool = _sensitivity(alarm_dr, onset).astype(float)
        chance_bool = _sensitivity(chance_alarm, onset).astype(float)
        diff_stat = mc_stat(lambda idx, o=obs_bool, c=chance_bool: o[idx].mean() - c[idx].mean(),
                             [N_PERSONS])
        out[arch] = dict(realized_fa_per_tracked_person_month_on_S=float(fa_rate_s),
                          observed_sensitivity_within_21d=sens_stat(alarm_dr, onset),
                          chance_sensitivity_within_21d=sens_stat(chance_alarm, onset),
                          diff_obs_minus_chance=diff_stat)
    s3_archs = [a for a in ARCHS_FOR_H if a != "probe-only"]
    for a in s3_archs:
        out[a]["holds_s3"] = bool(_verdict(out[a]["diff_obs_minus_chance"], "ge", 0.0))
    po_diff = out["probe-only"]["diff_obs_minus_chance"]
    out["probe-only"]["holds_s4"] = bool(po_diff["lo"] <= 0.0 <= po_diff["hi"])
    return dict(by_architecture=out,
                S3_holds=bool(all(out[a]["holds_s3"] for a in s3_archs)),
                S4_holds=bool(out["probe-only"]["holds_s4"]))


def _s5_mnar_ipw(plan_sha, cell, H_cell):
    """S5: m1=1.5 increases the ABSOLUTE VALUE of the relative slope bias over m1=0 (random
    schedule) -- the frozen results show the signed relative bias is NEGATIVE at m1=1.5, so the
    claim is about |bias| growing, not the bias's sign -- and response-propensity IPW (same
    features as P5: C_t, one lag, day of week) does not remove all of it. Only a non-degenerate test
    where this cell's own m1 != 0 (i.e. the m1_15 cell); see plan section (b)/(c)."""
    if cell["cell_name"] != "m1_15":
        return dict(applicable=False,
                    reason="this cell's m1 is 0 (frozen default); no m1 axis to compare against")
    h = H_cell["A-fixed"]["h"]
    panel0 = _robust_family_panel(plan_sha, "S", cell, "s5_m1_0", cell_name_override="default")
    panel1 = _robust_family_panel(plan_sha, "S", cell, "s5_m1_15", cell_name_override="m1_15")

    def slope_bias_random(panel, label):
        C, reason, alarm, band = _run_arch(panel, "A-fixed", h)
        Y, resp = panel["Y"], panel["responded"]
        post = np.zeros_like(reason, dtype=bool)
        post[:, BASELINE_DAYS:] = True
        all_mask = post & ~np.isnan(C)
        sa = _pstats(all_mask, C, Y)
        rng_p = np.random.default_rng(robust_seed(plan_sha, "s5_probe", cell["name"], label))
        probed, prop, ident = probe_schedule(rng_p, "random", C, band)
        obs = probed & resp & ~np.isnan(C) & post
        so = _pstats(obs, C, Y)
        return sa, so, obs, C, alarm, band, Y, resp

    sa0, so0, *_ = slope_bias_random(panel0, "m1_0")
    sa1, so1, _, C1, alarm1, band1, Y1, resp1 = slope_bias_random(panel1, "m1_15")

    def added_bias_fn(idx1, idx0):
        """|relative bias| at m1=1.5 minus |relative bias| at m1=0 (random schedule), exactly
        mirroring score()'s own P5 added_bias_fn (rel_bias() = (b_obs - b_all) / b_all). NOT the
        raw unscaled slope difference -- the frozen results show a NEGATIVE relative bias at
        m1=1.5 (P5.rel_bias_by_m1_and_schedule), so the claim is that |bias| grows, not that the
        (signed) bias itself is positive."""
        b1 = abs(rel_bias(sa1, so1, idx1))
        b0 = abs(rel_bias(sa0, so0, idx0))
        return b1 - b0

    added_bias_stat = mc_stat(added_bias_fn, [N_PERSONS, N_PERSONS])

    rng_ipw = np.random.default_rng(robust_seed(plan_sha, "s5_ipw", cell["name"]))
    probed1, prop1, _ = probe_schedule(rng_ipw, "random", C1, band1)
    n1, T1 = C1.shape
    lag = np.concatenate([np.zeros((n1, 1)), np.nan_to_num(C1[:, :-1])], axis=1)
    dow = np.tile(dow_features(T1), (n1, 1, 1))
    feats = np.concatenate([np.nan_to_num(C1)[..., None], lag[..., None], dow], axis=-1)
    admin = probed1
    yresp = resp1[admin].astype(float)
    beta_hat = logistic_irls(feats[admin], yresp)
    p_resp_hat = expit(feats @ beta_hat)
    obs1 = probed1 & resp1 & ~np.isnan(C1)
    obs1[:, :BASELINE_DAYS] = False
    w_resp = np.where(obs1, safe_div(1.0, np.clip(p_resp_hat, 0.05, 1.0)), 0.0)
    sraw1 = _pstats(obs1, C1, Y1)
    sipw1 = _pstats(obs1, C1, Y1, w=w_resp)

    def bias_fn(s, idx):
        return abs(_pslope(s, idx) - _pslope(sa1, idx))

    def frac_fn(idx):
        br = bias_fn(sraw1, idx)
        return 1 - bias_fn(sipw1, idx) / br if br > 1e-9 else np.nan

    bias_raw_stat = mc_stat(lambda idx: bias_fn(sraw1, idx), [N_PERSONS])
    bias_ipw_stat = mc_stat(lambda idx: bias_fn(sipw1, idx), [N_PERSONS])
    frac_removed_stat = mc_stat(frac_fn, [N_PERSONS])
    holds = bool(_verdict(added_bias_stat, "ge", 0.0) and frac_removed_stat["hi"] < 1.0)
    return dict(applicable=True, added_bias_m1_15_minus_m1_0=added_bias_stat,
                bias_raw=bias_raw_stat, bias_ipw=bias_ipw_stat, frac_removed=frac_removed_stat,
                holds=holds)


def _s6_cs_vs_s(plan_sha, cell, H_cell):
    """S6: A-fixed's false flags on CS exceed its rate on S (P10's direction)."""
    h = H_cell["A-fixed"]["h"]
    panel_cs = _robust_family_panel(plan_sha, "CS", cell, "s6_CS")
    panel_s = _robust_family_panel(plan_sha, "S", cell, "s6_S")
    _, reason_cs, alarm_cs, _ = _run_arch(panel_cs, "A-fixed", h)
    _, reason_s, alarm_s, _ = _run_arch(panel_s, "A-fixed", h)

    def ratio_fn(i, j):
        return _fa_pooled(alarm_cs, reason_cs, i) / max(_fa_pooled(alarm_s, reason_s, j), 1e-9)

    ratio_stat = mc_stat(ratio_fn, [N_PERSONS, N_PERSONS])
    return dict(fa_ratio_CS_over_S=ratio_stat, holds=bool(_verdict(ratio_stat, "ge", 1.0)))


def compute_robust_cell(plan_sha, cell, P_frozen):
    """One grid cell's full S1-S6 computation. Never writes a file -- `run_robust` does that."""
    H_cell = _robust_tune_all(plan_sha, cell)
    return dict(tuned_h=H_cell,
                S1=_s1_selection_attenuation(plan_sha, cell, H_cell, P_frozen),
                S2=_s2_state_coupled_sign(plan_sha, cell),
                S3_S4=_s3_s4_chance_baseline(plan_sha, cell, H_cell),
                S5=_s5_mnar_ipw(plan_sha, cell, H_cell),
                S6=_s6_cs_vs_s(plan_sha, cell, H_cell))


def run_robust(plan_sha):
    robust_seed(plan_sha, "startup_check")  # fail fast if --plan-sha doesn't match, before any work
    t0 = time.time()
    P_frozen = json.loads((HERE / "tuning.json").read_text())["schedules"]
    grid = _robust_grid()
    cells_out = {}
    for cell in grid:
        print(f"[robust] cell {cell['name']} ...", flush=True)
        cells_out[cell["name"]] = compute_robust_cell(plan_sha, cell, P_frozen)

    def grid_verdict(holds_path):
        per_cell = {name: holds_path(res) for name, res in cells_out.items()}
        bools = [v for v in per_cell.values() if isinstance(v, bool)]  # excludes S5's not_applicable
        failing = [n for n, v in per_cell.items() if v is False]
        return dict(per_cell=per_cell, holds_across_grid=bool(bools) and all(bools),
                    failing_cells=failing)

    summary = {
        "S1": grid_verdict(lambda r: r["S1"]["holds"]),
        "S2": grid_verdict(lambda r: r["S2"]["holds"]),
        "S3": grid_verdict(lambda r: r["S3_S4"]["S3_holds"]),
        "S4": grid_verdict(lambda r: r["S3_S4"]["S4_holds"]),
        "S5": grid_verdict(lambda r: (r["S5"]["holds"] if r["S5"]["applicable"] else "not_applicable")),
        "S6": grid_verdict(lambda r: r["S6"]["holds"]),
    }

    out = dict(status="EXPLORATORY, not frozen -- see sim/ROBUSTNESS-PLAN.md; no P1-P10 verdict changes",
               plan_sha256=plan_sha,
               grid=[{"name": c["name"], "dimension": c["dimension"], "value": c["value"]}
                     for c in grid],
               cells=cells_out, summary=summary)
    (HERE / "robustness.json").write_text(json.dumps(out, indent=2, default=float))

    lines = ["# sim/ROBUSTNESS.md", "",
             "EXPLORATORY, not frozen -- this grid is not part of sim/PREREG.md and changes no "
             "P1-P10 verdict. See sim/ROBUSTNESS-PLAN.md for the grid, the expectations stated "
             "before running, and the success rule.", "",
             "## Summary: does each structural finding hold across the grid?", "",
             "| finding | holds across grid | failing cells |", "|---|---|---|"]
    lines += [f"| {k} | {v['holds_across_grid']} | {', '.join(v['failing_cells']) or 'none'} |"
              for k, v in summary.items()]
    lines += ["", "Per-cell values with intervals: `sim/robustness.json`, key `cells.<name>`.", ""]
    (HERE / "ROBUSTNESS.md").write_text("\n".join(lines))
    print(f"wrote sim/robustness.json and sim/ROBUSTNESS.md in {time.time() - t0:.1f}s")
    return out


# ----------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    if "--check" in args:
        ok, _ = run_check()
        sys.exit(0 if ok else 1)
    if args and args[0] == "tune":
        run_tune()
        return
    if args and args[0] in ("score", "metrics", "robust"):
        cmd = args[0]
        flag = "--plan-sha" if cmd == "robust" else "--prereg-sha"
        sha = args[args.index(flag) + 1] if flag in args else None
        if not sha:
            print(f"{cmd} requires {flag} <sha256>", file=sys.stderr)
            sys.exit(2)
        {"score": score, "metrics": metrics, "robust": run_robust}[cmd](sha)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
