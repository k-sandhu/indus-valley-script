"""Star and sun positions, refraction, extinction and horizon azimuths for the town-axes protocol.

Implements the astronomy section of PROTOCOL.md: Hipparcos positions moved with ERFA pmsafe,
long-term precession of Vondrak, Capitaine and Wallace (2011) through ERFA ltpb/ltpecl/ltpequ,
Bennett (1982) refraction, Kasten and Young (1989) air mass, and setting or rising azimuths on
an azimuth-dependent apparent horizon.
"""
from pathlib import Path
import json
import math

import erfa
import numpy as np

BASE = Path(__file__).resolve().parent
MAS = math.pi / (180 * 3600 * 1000)
SUN_SEMIDIAMETER = 0.267
LIMITING_MAG = 6.0
T_CELSIUS, P_HPA = 20.0, 1010.0
TARGETS = [
    ("alcyone", "star", "set"), ("aldebaran", "star", "set"), ("procyon", "star", "set"),
    ("sun-equinox-set", "sun", "set"), ("sun-equinox-rise", "sun", "rise"),
    ("sun-june-set", "sun", "set"), ("sun-june-rise", "sun", "rise"),
    ("sun-december-set", "sun", "set"), ("sun-december-rise", "sun", "rise"),
]
SIDE = {name: side for name, _, side in TARGETS}


def load_stars(path=BASE / "stars-v1.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {s["key"]: s for s in data["stars"]}


def jd_of_epoch(epoch):
    """Julian epoch (TT) to a two-part Julian date."""
    return 2451545.0, (epoch - 2000.0) * 365.25


def star_mean_of_date(star, epoch):
    """Right ascension and declination (degrees) on the mean equator and equinox of the epoch."""
    ra = math.radians(star["ra_deg_icrs"])
    dec = math.radians(star["dec_deg_icrs"])
    pmr = star["pmra_mas_yr"] * MAS / math.cos(dec)
    pmd = star["pmdec_mas_yr"] * MAS
    px = star["parallax_mas"] / 1000.0
    rv = star["radial_velocity_km_s"] or 0.0
    a, b = jd_of_epoch(epoch)
    ra2, dec2, *_ = erfa.pmsafe(ra, dec, pmr, pmd, px, rv, 2451545.0, 0.0, a, b)
    v = erfa.s2c(ra2, dec2)
    m = erfa.ltpb(epoch)
    w = m @ v
    r, d = erfa.c2s(w)
    return math.degrees(r) % 360.0, math.degrees(d)


def obliquity(epoch):
    """Mean obliquity (degrees) from the Vondrak long-term ecliptic and equator poles."""
    pe = erfa.ltpecl(epoch)
    pq = erfa.ltpequ(epoch)
    return math.degrees(math.acos(float(np.clip(np.dot(pe, pq), -1, 1))))


def declination(target, epoch, stars):
    if target in stars:
        return star_mean_of_date(stars[target], epoch)[1]
    eps = obliquity(epoch)
    if "equinox" in target:
        return 0.0
    if "june" in target:
        return eps
    if "december" in target:
        return -eps
    raise KeyError(target)


def refraction(h_app):
    """Bennett (1982) refraction in degrees at apparent altitude h_app (degrees), scaled to 20 C, 1010 hPa."""
    h = max(h_app, -1.5)
    r_arcmin = 1.0 / math.tan(math.radians(h + 7.31 / (h + 4.4)))
    return r_arcmin / 60.0 * (P_HPA / 1010.0) * (283.0 / (273.0 + T_CELSIUS))


def airmass(h_app):
    """Kasten and Young (1989) relative air mass at apparent altitude h_app (degrees)."""
    return 1.0 / (math.sin(math.radians(h_app)) + 0.50572 * (h_app + 6.07995) ** -1.6364)


def extinction_angle(mag, k, mlim=LIMITING_MAG):
    """Apparent altitude at which m + k (X - 1) = mlim; 0 when the star stays visible to the horizon."""
    if k <= 0:
        return -90.0
    x_needed = 1.0 + (mlim - mag) / k
    if airmass(0.0) <= x_needed:
        return 0.0
    lo, hi = 0.0, 90.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if airmass(mid) > x_needed:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def azimuth_at_altitude(dec, lat, h_true, side):
    """Azimuth from north (degrees) of declination dec at true altitude h_true; None if never reached."""
    d, p, h = (math.radians(x) for x in (dec, lat, h_true))
    c = (math.sin(d) - math.sin(p) * math.sin(h)) / (math.cos(p) * math.cos(h))
    if abs(c) > 1:
        return None
    a = math.degrees(math.acos(c))
    return 360.0 - a if side == "set" else a


def visible_altitude(target, horizon_alt, mag, k):
    """Apparent altitude of the target's centre at last or first sight, given the apparent horizon there."""
    if target.startswith("sun"):
        return horizon_alt - SUN_SEMIDIAMETER
    e = extinction_angle(mag, k) if k is not None else -90.0
    return max(horizon_alt, e)


def event_azimuth(target, epoch, lat, horizon, stars, k=0.30, flat=False):
    """Azimuth of last sight (setting) or first sight (rising), iterating over the horizon profile.

    horizon is a callable azimuth -> apparent horizon altitude in degrees; flat=True uses 0 everywhere.
    """
    side = SIDE[target]
    dec = declination(target, epoch, stars)
    mag = stars[target]["v_mag_protocol"] if target in stars else None
    hz = (lambda a: 0.0) if flat else horizon
    az = 270.0 if side == "set" else 90.0
    for _ in range(100):
        h_app = visible_altitude(target, hz(az), mag, k)
        h_true = h_app - refraction(h_app)
        new = azimuth_at_altitude(dec, lat, h_true, side)
        if new is None:
            return None
        if abs(new - az) < 1e-3:
            az = new
            break
        az = new
    return az


def nearest_cardinal(az):
    return 90.0 * round(az / 90.0) % 360.0


def predicted_deviation(target, year_ce, lat, horizon, stars, k=0.30, flat=False):
    """Predicted grid deviation (degrees, clockwise positive) for an astronomical year (2500 BCE = -2499)."""
    az = event_azimuth(target, float(year_ce), lat, horizon, stars, k=k, flat=flat)
    if az is None:
        return None
    if target.startswith("sun-june") or target.startswith("sun-december"):
        card = 270.0 if SIDE[target] == "set" else 90.0
    else:
        card = nearest_cardinal(az)
    dev = (az - card + 180.0) % 360.0 - 180.0
    return dev


def deviation_rate(target, year_ce, lat, horizon, stars, k=0.30, flat=False, step=50.0):
    """d(theta)/dD in degrees per year, from theta at D +/- step years."""
    a = predicted_deviation(target, year_ce + step, lat, horizon, stars, k, flat)
    b = predicted_deviation(target, year_ce - step, lat, horizon, stars, k, flat)
    if a is None or b is None:
        return None
    return (a - b) / (2 * step)
