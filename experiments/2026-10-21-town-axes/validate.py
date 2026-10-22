"""Validation gate of PROTOCOL.md: obliquity, Thuban's pole passage and a comparison with Wanzke's table."""
import argparse
import math

import astro
from common import BASE, finite, provenance, write_new

WANZKE_GON = {  # Wanzke 1987, printed p. 37: setting point from west to north, gon
    "procyon": {-2499: 5.4, -1499: 8.3},
    "aldebaran": {-2499: -3.0, -1499: 3.8},
    "alcyone": {-2499: 2.4, -1499: 8.0},
}
MD_LAT = 27.324  # Mohenjo-daro, towns-v1.json starting coordinate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    stars = astro.load_stars()
    eps = astro.obliquity(-2499.0)
    best = min((90.0 - astro.star_mean_of_date(stars["thuban"], float(y))[1], y) for y in range(-3600, -1999))
    thuban_year = best[1]
    rows = []
    for key, vals in WANZKE_GON.items():
        for year, gon in vals.items():
            flat = lambda az: 0.0
            geo = astro.azimuth_at_altitude(astro.declination(key, float(year), stars), MD_LAT, 0.0, "set")
            refr = astro.predicted_deviation(key, year, MD_LAT, flat, stars, k=None, flat=True)
            ext = astro.predicted_deviation(key, year, MD_LAT, flat, stars, k=0.30, flat=True)
            rows.append({
                "target": key, "year_astronomical": year, "declination_deg": finite(astro.declination(key, float(year), stars), 4),
                "wanzke_gon": gon, "wanzke_deg": finite(gon * 0.9, 3),
                "geometric_h0_deg": finite(geo - 270.0, 3),
                "refracted_flat_horizon_deg": finite(refr, 3),
                "extinction_k030_flat_horizon_deg": finite(ext, 3),
            })
    checks = {
        "obliquity_2500_bce_deg": finite(eps, 4),
        "obliquity_pass": abs(eps - 23.97) <= 0.02,
        "thuban_min_polar_distance_deg": finite(best[0], 4),
        "thuban_min_year_astronomical": thuban_year,
        "thuban_pass": -2899 <= thuban_year <= -2699,
    }
    result = {
        "schema_version": "1.0", "task": "town-axes-validation", "synthetic": False,
        "checks": checks, "gate_passed": checks["obliquity_pass"] and checks["thuban_pass"],
        "wanzke_comparison": rows,
        "extinction_angles_deg_k030": {k: finite(astro.extinction_angle(stars[k]["v_mag_protocol"], 0.30), 3) for k in ("alcyone", "aldebaran", "procyon")},
        "extinction_angles_deg_k020": {k: finite(astro.extinction_angle(stars[k]["v_mag_protocol"], 0.20), 3) for k in ("alcyone", "aldebaran", "procyon")},
        "extinction_angles_deg_k045": {k: finite(astro.extinction_angle(stars[k]["v_mag_protocol"], 0.45), 3) for k in ("alcyone", "aldebaran", "procyon")},
        "provenance": provenance([BASE / "stars-v1.json"], [BASE / "astro.py", BASE / "validate.py", BASE / "common.py"]),
    }
    print(write_new(a.out, result))


if __name__ == "__main__":
    main()
