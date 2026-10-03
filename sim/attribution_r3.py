"""EXPLORATORY attribution round 3, the mixing cells (sim/ATTRIBUTION-PLAN-R3.md). Not part of sim/PREREG.md.

Imports drift_sim.py, r1's attribution.py and r2's attribution_r2.py unchanged. The authorship-share draw
(`beta` in `default`, `random` in `bernoulli_mix`, none in `pi_rises_with_D`) is routed to a side stream,
so every other draw is identical across the three cells for one seed and cell contrasts are paired.

    python3 sim/attribution_r3.py --plan-sha <sha256 of sim/ATTRIBUTION-PLAN-R3.md>
    python3 sim/attribution_r3.py --check
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import attribution as a1
import attribution_r2 as a2
import drift_sim as ds
from attribution import DAY, LAST_ALARM

HERE = Path(__file__).parent
PLAN_PATH = HERE / "ATTRIBUTION-PLAN-R3.md"
CELLS = ["default", "bernoulli_mix", "pi_rises_with_D"]
PAIRED = ["D", "Y", "responded", "used", "L_obs", "A", "H"]


def seed(plan_sha, *parts):
    tag = ":".join(["attribution-r3", plan_sha, *map(str, parts)]).encode()
    return int(hashlib.sha256(tag).hexdigest()[:16], 16) % (2**32 - 1)


class PiRouter:
    """Forwards to `rng`, except the draw right after the 3-D `standard_normal` (the indicator errors `e`):
    if it is the authorship share (`beta` or `random`), it comes from `side`. Records how many were routed."""

    def __init__(self, rng, side):
        self._rng, self._side, self._armed, self.routed = rng, side, False, 0

    def __getattr__(self, name):
        f = getattr(self._rng, name)

        def call(*a, **k):
            armed, self._armed = self._armed, False
            if armed and name in ("beta", "random"):
                self.routed += 1
                return getattr(self._side, name)(*a, **k)
            out = f(*a, **k)
            if name == "standard_normal" and np.ndim(out) == 3:
                self._armed = True
            return out
        return call


def gen(plan_sha, fam, cell, n, rec=None):
    rng = rec or np.random.default_rng(seed(plan_sha, "eval", fam))
    r = PiRouter(rng, np.random.default_rng(seed(plan_sha, "pi", fam)))
    p = ds.generate_panel(r, fam, ds.cell_params(cell), n=n)
    assert r.routed == (cell != "pi_rises_with_D"), f"{fam} {cell}: routed {r.routed}"
    return p


def build(plan_sha, cell, n):
    """{family: (panel, change day)}, as r2's build. Seeds do not depend on the cell."""
    rec = a1.LamRecorder(np.random.default_rng(seed(plan_sha, "eval", "S")))
    s = gen(plan_sha, "S", cell, n, rec)
    rc = np.random.default_rng(seed(plan_sha, "cday", "S"))
    cday = rc.integers(50, 101, n).astype(float)
    ramp = rc.integers(7, 22, n).astype(float)
    panels = {"S": (s, cday)}
    for fam, tau in a1.ps_profiles(rec.lam, cday, ramp).items():
        panels[fam] = (a1.shift(s, tau), cday)
    for fam in ("DR", "AV2", "CS"):
        p = gen(plan_sha, fam, cell, n)
        cd = {"DR": p["t0"], "AV2": p["av_day"],
              "CS": ds.sample_events(np.random.default_rng(seed(plan_sha, "eval", fam)), "CS", n)["cs_day"]}[fam]
        panels[fam] = (p, cd)
    return panels, rec.lam


def mean_gap(pi, x, y):
    """Bootstrappable mean of `pi` over mask x minus over mask y, pooled across persons."""
    a, na, b, nb = (pi * x).sum(1), x.sum(1), (pi * y).sum(1), y.sum(1)
    return lambda idx: a[idx].sum() / na[idx].sum() - b[idx].sum() / nb[idx].sum()


def pi_gap(f, key):
    """Mean authorship share (`pi_t` or `pi_prime`) on scored alarm days minus on tracked days 28-134."""
    trk = (f["reason"] == 0) & (DAY >= ds.BASELINE_DAYS) & (DAY <= LAST_ALARM)
    return mean_gap(f["p"][key], f["scored"], trk)


def dr_pi_shift(f, key):
    """DR: mean share on tracked days in [t0 + ramp, 134] minus on tracked days 28 to t0 - 1."""
    p, trk = f["p"], f["reason"] == 0
    pre = trk & (DAY >= ds.BASELINE_DAYS) & (DAY < p["t0"][:, None])
    post = trk & (DAY >= (p["t0"] + p["ramp"])[:, None]) & (DAY <= LAST_ALARM)
    return mean_gap(p[key], post, pre)


def pre_onset_rate(f):
    """DR: scored alarms on days [28, t0) per tracked person-month in that window."""
    pre = (DAY >= ds.BASELINE_DAYS) & (DAY < f["cd"][:, None])
    a, t = (f["scored"] & pre).sum(1), ((f["reason"] == 0) & pre).sum(1)
    return lambda idx: a[idx].sum() / (t[idx].sum() / 30)


def probe_D(f, n):
    """Mean true D over probe days t+1, t+3, t+5 of scored post-change alarms (the alarm-selection channel)."""
    ii, tt = np.nonzero(f["scored"] & f["post"])
    D = f["p"]["D"]
    v, k = np.bincount(ii, (D[ii, tt + 1] + D[ii, tt + 3] + D[ii, tt + 5]) / 3, n), np.bincount(ii, minlength=n)
    return lambda idx: v[idx].sum() / k[idx].sum()


def run(plan_sha, n=ds.N_PERSONS):
    h = json.loads((HERE / "tuning.json").read_text())["h"]["A-fixed"]["h"]
    rng = np.random.default_rng(seed(plan_sha, "boot"))

    # q*: as r1 and r2, 90th percentile of Q over DR alarms in [t0, t0 + 21), default-cell tuning panel.
    tp = ds.generate_panel(np.random.default_rng(seed(plan_sha, "tune", "DR")), "DR",
                           ds.cell_params("default"), n=n)
    _, _, al, z = a1.score_panel(tp, h)
    win = (DAY >= tp["t0"][:, None]) & (DAY < tp["t0"][:, None] + 21) & (DAY >= ds.BASELINE_DAYS)
    qs = np.array([a1.q_stat(z, i, t) for i, t in zip(*np.nonzero(al & win))])
    qs = qs[~np.isnan(qs)]
    q_star = float(np.percentile(qs, a1.Q_PCTL))

    sc, lams = {}, []
    for cell in CELLS:
        panels, lam = build(plan_sha, cell, n)
        lams.append(lam)
        sc[cell] = a2.score_cell(panels, h, q_star)
    assert all(np.array_equal(lams[0], m) for m in lams), "loadings differ across cells"
    for fam in a2.FAMILIES:
        for c in CELLS[1:]:
            for k in PAIRED:
                a, b = sc["default"][fam]["p"][k], sc[c][fam]["p"][k]
                assert np.array_equal(a, b, equal_nan=True), f"{fam} {k} not paired, {c}"

    res = dict(label="EXPLORATORY (sim/ATTRIBUTION-PLAN-R3.md); not sim/PREREG.md; synthetic only",
               plan_sha256=plan_sha, h_A_fixed=h, q_star=q_star, n_tune_alarms=int(len(qs)),
               cells={c: a2.summarize(sc[c], rng, n) for c in CELLS},
               contrasts={f"{c}_minus_default": a2.contrast(sc[c], sc["default"], rng, n) for c in CELLS[1:]})
    for c in CELLS:
        s, ps = sc[c]["S"], sc[c]["PS-sub"]
        res[f"C3_PSsub_over_S_M0_{c}"] = a1.boot(lambda i, f=ps, s=s: a2.rate(f)(i) / a2.rate(s)(i), rng, n)
        for key in ("pi_t", "pi_prime"):
            res[f"C5_S_{key}_alarm_minus_tracked_{c}"] = a1.boot(pi_gap(s, key), rng, n)
            res[f"C5_DR_{key}_post_minus_pre_{c}"] = a1.boot(dr_pi_shift(sc[c]["DR"], key), rng, n)
        # Validity of the filtered indicators 4 and 5 on S: pooled within-person correlation with D, used days.
        p = s["p"]
        for j in (ds.IDX_MSGLEN, ds.IDX_NEGSELF):
            x = p["X_filtered"][:, :, j]
            res[f"validity_S_filtered_ind{j + 1}_{c}"] = float(ds.person_slope_corr(~np.isnan(x), p["D"], x)[1])
    x = sc["default"]["S"]["p"]["H"][:, :, ds.IDX_NEGSELF]
    res["validity_S_unmixed_H_ind5"] = float(ds.person_slope_corr(~np.isnan(x) & sc["default"]["S"]["p"]["used"],
                                                                  sc["default"]["S"]["p"]["D"], x)[1])
    for c in CELLS[1:]:
        fx, fy = sc[c]["DR"], sc["default"]["DR"]
        for excl, tag in ((True, ""), (False, "_keep_pre_onset")):
            dx, dy = (ds._sensitivity(f["attr"]["M0"], f["cd"], exclude_pre_onset_alarms=excl).astype(float)
                      for f in (fx, fy))
            res[f"C6_DR_sens21_M0_ratio_{c}_over_default{tag}"] = a1.boot(
                lambda idx: dx[idx].mean() / dy[idx].mean(), rng, n)
        rx, ry = pre_onset_rate(fx), pre_onset_rate(fy)
        res[f"C6_DR_pre_onset_M0_rate_ratio_{c}_over_default"] = a1.boot(lambda idx: rx(idx) / ry(idx), rng, n)
        for fam in ("S", "DR"):
            sx, sy = probe_D(sc[c][fam], n), probe_D(sc["default"][fam], n)
            res[f"C1_{fam}_probe_day_D_diff_{c}_minus_default"] = a1.boot(lambda idx: sx(idx) - sy(idx), rng, n)
    return res


def check():
    a2.check()
    n = 200
    p = {c: gen("check", "DR", c, n) for c in CELLS}
    for c in CELLS[1:]:
        for k in PAIRED:
            assert np.array_equal(p["default"][k], p[c][k], equal_nan=True), f"{c}: {k} not paired"
        assert not np.array_equal(p["default"]["pi_t"], p[c]["pi_t"])
    assert set(np.unique(p["bernoulli_mix"]["pi_t"])) == {0.0, 1.0}
    assert abs(p["bernoulli_mix"]["pi_t"].mean() - ds.PI_BAR_DEFAULT) < 0.005
    assert np.allclose(p["pi_rises_with_D"]["pi_t"],
                       ds.expit(ds.logit(ds.PI_BAR_DEFAULT) + 0.5 * p["pi_rises_with_D"]["D"]))
    # The side-stream Beta has the frozen mean (pi_bar) and the Beta(10 pi_bar, 10 (1 - pi_bar)) SD.
    pi = p["default"]["pi_t"]
    sd = np.sqrt(ds.PI_BAR_DEFAULT * (1 - ds.PI_BAR_DEFAULT) / 11)
    assert abs(pi.mean() - ds.PI_BAR_DEFAULT) < 0.005 and abs(pi.std() - sd) < 0.005, (pi.mean(), pi.std())
    print(f"check OK: {', '.join(PAIRED)} identical across {', '.join(CELLS)} for one seed; pi_t differs; "
          "bernoulli pi in {0, 1} with mean pi_bar; pi_rises pi = expit(logit(pi_bar) + 0.5 D); side-stream Beta moments match")


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
            sys.exit(f"--plan-sha does not match sha256(sim/ATTRIBUTION-PLAN-R3.md) = {on_disk}")
        out = run(a.plan_sha)
        (HERE / "attribution_r3.json").write_text(json.dumps(out, indent=2) + "\n")
        print(json.dumps({k: v for k, v in out.items() if k not in ("cells", "contrasts")}, indent=1))
