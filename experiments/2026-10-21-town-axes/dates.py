"""Layout dates under the frozen date rule (PROTOCOL.md, Layout date; AMENDMENT-1.md, Layout date).

The tier choice for each town was made by the coordinating agent from the dating records in dating-v1/towns/
before any bearing was read; it is written out below with its reason. The IntCal20 sensitivity date is computed
here from the layout-phase radiocarbon determinations in those records.

python dates.py --intcal data/raw/2026-10-21-town-axes/coordinator/intcal20.14c --out dates-v1/dates.json
"""
from pathlib import Path
import argparse
import json

import numpy as np

from common import BASE, finite, provenance, write_new


def ce(bce):
    """Astronomical year for a year BCE (2500 BCE = -2499)."""
    return None if bce is None else 1 - bce


# town: (part in the dating record, tier, start BCE, sigma years, source and reason, phase keys for the IntCal20 check)
SELECTION = {
    "mohenjo-daro": ("lower town (DK-G, HR and VS areas): street grid", 3, 2800, 200,
                     "No radiocarbon from the layout phase. Tier 3: Mackay 1938 dates the lowest attainable levels of the grid to c. 2800 BC by cross-dating (range 2800-2500). Jansen 1987 models a foundation about 2400 BC and Kenoyer 1998 dates urban Mohenjo-daro from about 2600 BC; neither is the excavator's dated layout phase, so they are recorded as disagreements.", []),
    "harappa": ("Mound F: perimeter wall and Great Hall ('granary')", 2, 2450, 150,
                "Both imagery measurers' main systems lie on Mound F. Tier 2: HARP's Period 3B begins 'ca. 2450 BC' in calibrated radiocarbon years (Kenoyer and Meadow 2010: xlv); the start is given without a range, so sigma is 150 years. Meadow and Kenoyer 2005 give 'c. 2450/2400'.", ["3B"]),
    "lothal": ("dock", 3, 2350, 200,
               "Tier 3: Phase IIa starts c. 2350 BC by Rao's cross-dating and count of building phases back from uncalibrated radiocarbon (Rao 1979; restated by Frenez and Tosi 2005). Possehl and Raval 1989 calibrate the Lothal A dates to a Harappan settlement of Gujarat c. 2500-2300 BC, which dates Phase I as a whole rather than the dock.", ["Phase IIA", "Phase IIa"]),
    "dholavira": ("castle (eastern, higher subdivision of the citadel)", 3, 3000, 200,
                  "Both imagery measurers' main systems are the castle. The dating record gives its layout phase as Stage I (first fortification), c. 3000-2900 BCE by stratigraphy and ceramic cross-dating (Bisht 2015: 104); tier 3. The castle was remodelled with monumental gates in Stage III (c. 2800-2500 BCE). Sengupta et al. 2020 dated carbonates from all stages, but only the abstract was available.", []),
    "sutkagen-dor": ("citadel (walled enclosure between two natural ridges)", None, None, None,
                     "No source dates the enclosure; the published spans (Dales 1977, 1992; Pakistan heritage database) are general Harappan-period ranges. No date: the town does not enter scoring.", []),
    "kalibangan": ("lower town (KLB-2, eastern mound: walled lower city with street grid)", 2, 2600, 150,
                   "Plan main systems are the KLB-2 street grid. Tier 2: the excavation team's latest statement, Part II (2020) p. 1423, gives Period II as 'circa 2600 to circa 1900 B.C.' from calibrated radiocarbon (also Lal 2003 p. 27, 'commencing around 2600 BC').", ["Period II", "Harappa"]),
    "surkotada": ("citadel (western, higher enclosure)", 2, 2400, 50,
                  "Tier 2: Possehl and Raval 1989 (p. 10) calibrate the Surkotada and Lothal dates and place the Harappan settlement of Kutch c. 2500-2300 BC; the start is stated as a range, so D is its midpoint and sigma a quarter of its width. Joshi's own figures (2055-1970 BC) are uncalibrated.", ["IA"]),
    "banawali": ("lower town (outer walled town to the east and north of the citadel, with radial streets)", None, None, None,
                 "The excavator's final scheme (IAR 1986-87, 1987-88) assigns the citadel and lower town to Period IC, for which no date or radiocarbon exists; his earlier attribution to Period II (from c. 2300 BC) is superseded. No date under the rule.", []),
    "chanhu-daro": ("Mound II: fired-brick town of Mackay's Harappa II occupation", 3, 3000, 200,
                    "No radiocarbon from the Harappa II town. Tier 3: Mackay's own date for the Harappa culture levels, 3000-2600 BC by cross-dating (letter of 1936 quoted in Mackay 1943 p. 253). The French mission dates a mud-brick planned town below these levels to 2600/2500-2300 BCE, which places Harappa II later still; that town is a different part.", []),
    "farmana": ("settlement area (Locality 1 of the main mound)", 2, 2600, 150,
                "Tier 2: Shinde 2023 dates Periods IIA and IIB together to 2600-2400 BCE 'on the basis of a few AMS dates'; the 2011 report puts the town plan in Period IIA.", ["Harappan"]),
    "gola-dhoro": ("whole town: the fortified enclosure", None, None, None,
                   "No calendar start is published for Phase II, in which the wall was built; the regional synthesis of Abhayan et al. 2025 brackets BSR I and II together in c. 2600-2200 BCE. No date under the rule.", []),
    "kanmer": ("whole town: the fortified main mound", 2, 2500, 150,
               "Tier 2: the excavators' AMS dates bracket the urban phase, beginning with KMR IIa, 'between 2500 and 2000 BC' (Kharakwal et al. 2011 p. 368).", ["IIa", "IIA"]),
    "rangpur": ("excavated area of the Harappan settlement", 3, 2000, 200,
                "No radiocarbon from Rangpur. Tier 3: Rao 1963 dates the first Harappan structural phase of II A to c. 2000 BC by cross-dating with Lothal; later syntheses move II A earlier on ceramic grounds without dates from the site.", []),
    "rojdi": ("circumvallation and gateway (whole settlement)", 2, 2000, 150,
              "The plan main system, a Subphase 2b building on the Main Mound, does not match a dated part, so Amendment 1 takes the earliest walled part: the circumvallation, Rojdi C, 2000-1700 BC on calibrated radiocarbon (Possehl and Raval 1989 pp. 11-13, 171).", ["Rojdi C"]),
}


def load_intcal(path):
    rows = []
    for line in Path(path).read_text(encoding="latin-1").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = [float(x) for x in line.replace(",", " ").split()[:3]]
        rows.append(parts)
    a = np.array(sorted(rows))
    grid = np.arange(0, 12001)
    return grid, np.interp(grid, a[:, 0], a[:, 1]), np.interp(grid, a[:, 0], a[:, 2])


def calibrate_median(age, sigma, curve):
    grid, mu, sd = curve
    s2 = sigma ** 2 + sd ** 2
    p = np.exp(-0.5 * (age - mu) ** 2 / s2) / np.sqrt(s2)
    c = np.cumsum(p) / p.sum()
    cal_bp = float(grid[np.searchsorted(c, 0.5)])
    lo, hi = float(grid[np.searchsorted(c, 0.025)]), float(grid[np.searchsorted(c, 0.975)])
    return cal_bp, lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intcal", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    curve = load_intcal(a.intcal)
    towns, inputs = [], [Path(a.intcal)]
    for f in sorted((BASE / "dating-v1" / "towns").glob("*.json")):
        inputs.append(f)
        rec = json.loads(f.read_text(encoding="utf-8"))
        slug = rec["town"]
        out = {"town": slug, "parts": []}
        for p in rec.get("parts", []):
            r = p.get("excavator_range_bce") or [None, None]
            out["parts"].append({"part": p.get("part"), "layout_phase": p.get("layout_phase"), "excavator_range_bce": r,
                                 "D_year": ce(r[0]) if r and r[0] else None, "sigma_D": 200 if r and r[0] else None})
        fo = (rec.get("first_occupation") or {}).get("range_bce") or [None]
        out["D_first_occupation_year"] = ce(fo[0]) if fo and fo[0] else None
        sel = SELECTION.get(slug)
        if sel:
            part, tier, start, sig, reason, keys = sel
            out.update(date_part=part, date_tier=tier, D_year=ce(start), sigma_D=sig, date_source=reason)
            match = next((p for p in rec.get("parts", []) if (p.get("part") or "").startswith(part[:25])), None)
            dets = []
            if match and keys:
                for d in match.get("radiocarbon") or []:
                    ph = str(d.get("phase") or "")
                    if any(k in ph for k in keys) and d.get("age_bp_5568") and d.get("sigma_5568"):
                        dets.append(d)
            if dets:
                oldest = max(dets, key=lambda d: d["age_bp_5568"])
                med, lo, hi = calibrate_median(oldest["age_bp_5568"], oldest["sigma_5568"], curve)
                out.update(D_14C_year=finite(1950 - med, 0), sigma_D_14C=finite((hi - lo) / 3.92, 0),
                           D_14C_basis={"lab_no": oldest.get("lab_no"), "age_bp_5568": oldest["age_bp_5568"], "sigma": oldest["sigma_5568"],
                                        "phase": oldest.get("phase"), "cal_bp_median": med, "cal_bp_95": [lo, hi], "n_layout_determinations": len(dets)})
            else:
                out.update(D_14C_year=None, D_14C_basis="no layout-phase determination with a 5568-year age in the dating record")
        towns.append(out)
    result = {"schema_version": "1.0", "task": "town-axes-dates", "synthetic": False,
              "rule": "PROTOCOL.md Layout date tiers: 1 Bayesian start boundary (none published for any town), 2 calibrated start from site radiocarbon, 3 excavator's cross-dated start; AMENDMENT-1.md for plan-based towns",
              "years": "D_year is an astronomical year: 2500 BCE = -2499",
              "intcal": "IntCal20 (Reimer et al. 2020, Radiocarbon 62: 725-757); D_14C_year is the median calendar age of the oldest layout-phase determination",
              "towns": towns, "provenance": provenance(inputs, [BASE / "dates.py", BASE / "common.py"])}
    print(write_new(a.out, result))


if __name__ == "__main__":
    main()
