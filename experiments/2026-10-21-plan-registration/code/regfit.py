"""Similarity registration of a published plan to Web Mercator imagery.

This module holds the frozen fit and error model of PROTOCOL.md. It is
imported by the registrars' checking tool (which never prints a rotation)
and by the coordinator's register.py (which runs once, after the control
point files are hashed).

Coordinates
  plan pixels   x to the right, y down, in the render file named for the plan.
                The fit works in (x, -y), a right-handed frame with y up.
  map           Web Mercator metres from global pixel coordinates at a zoom,
                then shifted to the control points' centroid and multiplied by
                cos(latitude of the centroid), so that map units are ground
                metres. A uniform factor does not change a rotation.
  rotation phi  counter-clockwise angle from the plan frame to the map frame.
                Page-up on the plan then has true bearing -phi, and a
                direction with page azimuth a (clockwise from page-up) has true
                bearing a - phi.
"""
import math

import numpy as np

R_EARTH = 6378137.0
CIRC = 2 * math.pi * R_EARTH

# One-sigma identification uncertainty per coordinate, in ground metres,
# for the pair of positions (plan and imagery) of a control point.
CLASS_SIGMA_M = {"A": 3.0, "B": 6.0, "C": 12.0, "P": 2.0}
PIXEL_TERM_PX = 1.5          # picking uncertainty on either image, in its pixels
SCALE_TOLERANCE = 0.15       # fitted scale must lie within 15% of the scale bar
MAX_CHI2_PER_DOF = 9.0       # above this the registration is rejected
MIN_SINGULAR_RATIO = 0.10    # control points must not lie on one line
MAX_SIGMA_PHI_DEG = 5.0      # above this a registration is reported as uninformative


def global_px_to_merc(gx, gy, z):
    n = 256.0 * 2 ** z
    return (gx / n - 0.5) * CIRC, (0.5 - gy / n) * CIRC


def merc_to_lonlat(E, N):
    lon = math.degrees(E / R_EARTH)
    lat = math.degrees(math.atan(math.sinh(N / R_EARTH)))
    return lon, lat


def lonlat_to_merc(lon, lat):
    E = math.radians(lon) * R_EARTH
    N = R_EARTH * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return E, N


def ground_m_per_px(lat, z):
    return CIRC * math.cos(math.radians(lat)) / (256.0 * 2 ** z)


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def fold45(a):
    """Fold a bearing to the nearest cardinal direction, result in (-45, +45]."""
    d = a % 90.0
    if d > 45.0:
        d -= 90.0
    if d <= -45.0:
        d += 90.0
    return d


def _solve(P, Q, w):
    """Weighted least squares for Q = [[a,-b],[b,a]] P + t.

    P, Q: (N, 2) arrays. w: (N,) weights, applied to both coordinates.
    Returns params (a, b, tx, ty), covariance (unit-weight prior), residuals.
    """
    N = len(P)
    A = np.zeros((2 * N, 4))
    y = np.zeros(2 * N)
    A[0::2, 0] = P[:, 0]
    A[0::2, 1] = -P[:, 1]
    A[0::2, 2] = 1.0
    A[1::2, 0] = P[:, 1]
    A[1::2, 1] = P[:, 0]
    A[1::2, 3] = 1.0
    y[0::2] = Q[:, 0]
    y[1::2] = Q[:, 1]
    W = np.repeat(w, 2)
    AtW = A.T * W
    cov = np.linalg.inv(AtW @ A)
    params = cov @ (AtW @ y)
    res = (y - A @ params).reshape(N, 2)
    return params, cov, res


def fit_link(P, Q, sigma, *, scale_bar=None, q_unit_to_m=1.0, reveal_rotation=False):
    """Fit one link (plan to map, or plan to plan) and apply the error model.

    P: (N, 2) plan coordinates in the right-handed frame (x, -y), pixels.
    Q: (N, 2) target coordinates (ground metres for a map link, right-handed
       pixels of the target plan for a plan link).
    sigma: (N,) one-sigma per coordinate, in target units.
    scale_bar: plan metres per pixel from the plan's scale bar, or None.
    q_unit_to_m: metres per target unit (1 for the map, the target plan's
       metres per pixel for a plan link), used for the scale check.
    """
    P = np.asarray(P, float)
    Q = np.asarray(Q, float)
    sigma = np.asarray(sigma, float)
    N = len(P)
    out = {"n_points": N}
    if N < 3:
        out.update(accepted=False, reasons=["fewer than three control points"])
        return out
    w = 1.0 / sigma ** 2
    params, cov, res = _solve(P, Q, w)
    a, b = params[0], params[1]
    s = math.hypot(a, b)
    phi = math.degrees(math.atan2(b, a))
    J = np.array([-b / s ** 2, a / s ** 2, 0.0, 0.0])
    sig_prior = math.degrees(math.sqrt(J @ cov @ J))
    chi2 = float(np.sum((res ** 2).sum(axis=1) * w))
    dof = 2 * N - 4
    chi2_dof = chi2 / dof if dof > 0 else float("nan")
    sig_scaled = sig_prior * max(1.0, math.sqrt(chi2_dof)) if dof > 0 else sig_prior
    # Leave-one-out rotations (N >= 4).
    loo = []
    if N >= 4:
        for i in range(N):
            k = np.arange(N) != i
            pk, _, _ = _solve(P[k], Q[k], w[k])
            loo.append(math.degrees(math.atan2(pk[1], pk[0])))
        mean_loo = math.degrees(math.atan2(np.mean(np.sin(np.radians(loo))), np.mean(np.cos(np.radians(loo)))))
        dev = np.array([wrap180(x - mean_loo) for x in loo])
        sig_jk = math.sqrt((N - 1) / N * float(np.sum(dev ** 2)))
    else:
        sig_jk = None
    sig_phi = max(sig_scaled, sig_jk or 0.0)
    # Mirror check: the same points fitted with the plan reflected.
    Pm = P.copy()
    Pm[:, 1] = -Pm[:, 1]
    _, _, res_m = _solve(Pm, Q, w)
    chi2_mirror = float(np.sum((res_m ** 2).sum(axis=1) * w))
    # Geometry: singular values of the centred target configuration.
    sv = np.linalg.svd(Q - Q.mean(axis=0), compute_uv=False)
    sv_ratio = float(sv[1] / sv[0]) if sv[0] > 0 else 0.0
    fitted_m_per_px = s * q_unit_to_m
    reasons = []
    if sv_ratio < MIN_SINGULAR_RATIO:
        reasons.append(f"control points nearly collinear (singular-value ratio {sv_ratio:.3f})")
    if dof > 0 and chi2_dof > MAX_CHI2_PER_DOF:
        reasons.append(f"chi2 per degree of freedom {chi2_dof:.2f} exceeds {MAX_CHI2_PER_DOF}")
    if chi2_mirror <= chi2:
        reasons.append("the mirrored plan fits as well as or better than the plan")
    scale_ratio = None
    if scale_bar:
        scale_ratio = fitted_m_per_px / scale_bar
        if abs(scale_ratio - 1.0) > SCALE_TOLERANCE:
            reasons.append(f"fitted scale {fitted_m_per_px:.4f} m/px differs from the scale bar {scale_bar:.4f} by more than 15%")
    accepted = not reasons
    norm_res = np.sqrt((res ** 2).sum(axis=1)) / sigma
    out.update(
        dof=dof,
        chi2=chi2,
        chi2_per_dof=chi2_dof,
        fitted_m_per_px=fitted_m_per_px,
        scale_bar_m_per_px=scale_bar,
        scale_ratio=scale_ratio,
        singular_value_ratio=sv_ratio,
        chi2_mirror=chi2_mirror,
        sigma_phi_prior_deg=sig_prior,
        sigma_phi_chi2_scaled_deg=sig_scaled,
        sigma_phi_jackknife_deg=sig_jk,
        sigma_phi_deg=sig_phi,
        informative=sig_phi <= MAX_SIGMA_PHI_DEG,
        residuals_target_units=res.tolist(),
        residuals_m=(res * q_unit_to_m).tolist(),
        normalised_residuals=norm_res.tolist(),
        accepted=accepted,
        reasons=reasons,
    )
    if reveal_rotation:
        out["phi_deg"] = phi
        out["loo_phi_deg"] = loo or None
        out["max_loo_change_deg"] = max(abs(wrap180(x - phi)) for x in loo) if loo else None
    return out


def link_arrays(link, plans, mosaics):
    """Turn a control-point link from a registrar's file into fit inputs.

    link["to"] is "map" or the id of another plan. Each point has plan_px
    [x, y] on the link's plan, and either mosaic + mosaic_px (map links) or
    target_px (plan links), with a class in CLASS_SIGMA_M.
    """
    src = plans[link["plan"]]
    m_src = src.get("scale_bar_m_per_px")
    pts = link["points"]
    P = np.array([[p["plan_px"][0], -p["plan_px"][1]] for p in pts], float)
    if link["to"] == "map":
        EN = []
        img_px_m = []
        for p in pts:
            mz = mosaics[p["mosaic"]]
            ox, oy = mz["origin_global_px"]
            gx = ox + p["mosaic_px"][0]
            gy = oy + p["mosaic_px"][1]
            EN.append(global_px_to_merc(gx, gy, mz["zoom"]))
            img_px_m.append(mz["ground_m_per_px"])
        EN = np.array(EN)
        c = EN.mean(axis=0)
        lat0 = merc_to_lonlat(c[0], c[1])[1]
        Q = (EN - c) * math.cos(math.radians(lat0))
        q_unit = 1.0
        px_src = m_src if m_src else 0.0
        sig = np.array([math.sqrt(CLASS_SIGMA_M[p["class"]] ** 2 + (PIXEL_TERM_PX * px_src) ** 2
                                  + (PIXEL_TERM_PX * img_px_m[i]) ** 2) for i, p in enumerate(pts)])
    else:
        tgt = plans[link["to"]]
        m_tgt = tgt.get("scale_bar_m_per_px")
        if not m_tgt:
            raise ValueError(f"plan link to {link['to']} needs a target plan with a scale bar")
        Q = np.array([[p["target_px"][0], -p["target_px"][1]] for p in pts], float)
        q_unit = m_tgt
        px_src = m_src if m_src else 0.0
        sig_m = np.array([math.sqrt(CLASS_SIGMA_M[p["class"]] ** 2 + (PIXEL_TERM_PX * px_src) ** 2
                                    + (PIXEL_TERM_PX * m_tgt) ** 2) for p in pts])
        sig = sig_m / m_tgt
    return P, Q, sig, q_unit


def fit_from_link(link, plans, mosaics, *, reveal_rotation=False, subset=None):
    pts = link["points"]
    if subset is not None:
        link = dict(link, points=[p for p in pts if subset(p)])
    if len(link["points"]) < 3:
        return {"n_points": len(link["points"]), "accepted": False, "reasons": ["fewer than three control points"]}
    P, Q, sig, q_unit = link_arrays(link, plans, mosaics)
    return fit_link(P, Q, sig, scale_bar=plans[link["plan"]].get("scale_bar_m_per_px"),
                    q_unit_to_m=q_unit, reveal_rotation=reveal_rotation)
