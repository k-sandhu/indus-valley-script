"""Measure the fortification of Shikarpur on Gadekar, Rajesh & Ajithprasad 2014 (JLS 1(1)), Fig. 2,
and write experiments/2026-10-21-plan-registration/measure-S/towns/shikarpur.json together with
measure-S/fits_shikarpur.json (every fitted line, including the rendering-check lines).

The picks below were read from gridded crops of the render (cptools.py grid, scale 5-10). Each line
is a list of collinear pieces chosen to skip trench boxes, labels, leader lines, the West
Entrance and Eastern Gate breaks and the mound outline where it touches the band.
Run from the repository root: python -P experiments/2026-10-21-plan-registration/measure-S/code/build_shikarpur.py
"""
import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from linefit import fit_line, load_gray  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "experiments" / "2026-10-21-plan-registration" / "measure-S"
RENDER = "data/raw/2026-10-21-plan-registration/S/renders/jls764_fig2_native.png"
DOWNLOAD = "data/raw/2026-10-21-plan-registration/S/downloads/jls764_html_fig_3262.png"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


# scale bar: black bar on rows 561-562; left end where pixel 34 is ~70 % dark, right end where
# pixel 150 is ~25 % dark (pixel-boundary frame of the grid crops); 0-50 m
SB = {"p1_px": [34.3, 562.0], "p2_px": [150.26, 562.0], "length_m": 50.0}
SB["m_per_px"] = round(SB["length_m"] / math.hypot(SB["p2_px"][0] - SB["p1_px"][0], SB["p2_px"][1] - SB["p1_px"][1]), 5)

FORT = [
    ("s1", "north face, outer", dict(pieces=[(90, 106.5, 165, 106.5), (197, 106.5, 224, 106.5), (256, 107.5, 333, 107.5), (353, 108.3, 366, 108.3)], mode="edge", white=-1, half=3, trim=0.0)),
    ("s2", "north face, inner", dict(pieces=[(113, 133.2, 165, 133.2), (182, 133.8, 200, 133.8)], mode="edge", white=1, half=2.5, trim=0.0)),
    ("s3", "south face, outer", dict(pieces=[(98, 401.5, 232, 401.5), (253, 401.5, 366, 401.5)], mode="edge", white=1, half=3, trim=0.0)),
    ("s4", "south face, inner", dict(pieces=[(113, 378.5, 198, 378.5), (254, 378.5, 320, 378.5)], mode="edge", white=-1, half=3, trim=0.0)),
    ("s5", "west face, outer", dict(pieces=[(85, 110, 85, 132), (85, 140, 85, 188), (85, 224, 85, 332)], mode="edge", white=1, half=3, trim=0.0)),
    ("s6", "west face, inner", dict(pieces=[(110, 152, 110, 188), (110, 224, 110, 368)], mode="edge", white=-1, half=3, trim=0.0)),
    ("s7", "east face, outer", dict(pieces=[(369, 110, 369, 133), (369, 141, 369, 156), (369, 175, 369, 238), (369, 270, 369, 368), (369, 377, 369, 399)], mode="edge", white=-1, half=3, trim=0.0)),
    ("s8", "east face, inner", dict(pieces=[(345, 175, 345, 238), (345, 272, 345, 368)], mode="edge", white=1, half=3, trim=0.0)),
]
NOTES = {
    "s1": "Outer (north) edge of the grey band, drawn with a dashed outline; pieces skip the trench Do14, the trench at the north-east corner and the leader lines of 'White plaster line' and 'Ext. Rampart'.",
    "s2": "Inner (south) edge of the north band, measured only from x 113 to 200: east of x ~205 the band edge runs into the Ea1 grid line drawn 2-3 px below it and cannot be separated.",
    "s3": "Outer (south) edge of the south band; pieces skip trench Fp1 and the 'Ex. Rampart' leader; the west end is clear of the mound outline.",
    "s4": "Inner (north) edge of the south band; pieces skip the trench labels Fk13/Fp1 and the 'Ia1' label; the Fa1-Ia1 grid line 6 px to the north lies outside the profile window.",
    "s5": "Outer (west) edge of the west band; pieces skip the Ea1 grid line crossing, trench Bv6 and the West Entrance break, and stop where the mound outline touches the band (y > 335).",
    "s6": "Inner (east) edge of the west band; pieces skip the 'Ea1' label, trench Bv6 and the West Entrance break.",
    "s7": "Outer (east) edge of the east band; pieces skip the grid-line crossings, the trench at the 'Ext. Rampart' and the Eastern Gate trenches.",
    "s8": "Inner (west) edge of the east band below the bastion; pieces skip the trench at y 158-172, trench Hc2 and the Eastern Gate.",
}
CHECK = {
    "grid_h136": dict(pieces=[(45, 136, 96, 136), (118, 136, 166, 136), (184, 136, 222, 136), (242, 136, 325, 136)], mode="ink", half=2.5, trim=0.0),
    "grid_h372": dict(pieces=[(112, 372, 200, 372), (254, 372, 325, 372), (347, 372, 366, 372)], mode="ink", half=2.5, trim=0.0),
    "grid_v100": dict(pieces=[(100, 150, 100, 186), (100, 224, 100, 366)], mode="ink", half=3, trim=0.0),
    "grid_v329": dict(pieces=[(329, 190, 329, 236), (329, 270, 329, 366), (329, 384, 329, 560)], mode="ink", half=3, trim=0.0),
    "frame_left": dict(pieces=[(3.5, 20, 3.5, 780)], mode="ink", half=3, trim=0.0),
    "frame_right": dict(pieces=[(596.5, 20, 596.5, 780)], mode="ink", half=3, trim=0.0),
    "frame_top": dict(pieces=[(20, 3.5, 580, 3.5)], mode="ink", half=3, trim=0.0),
    "frame_bottom": dict(pieces=[(20, 789.5, 580, 789.5)], mode="ink", half=3, trim=0.0),
}
# north symbol: a cross-hair rose (circle, dot and cross) under the letter N; the N-S stroke
# outside the circle, both arms, fitted as one line; the E-W stroke as a check
ARROW = dict(pieces=[(479.9, 131.5, 479.9, 126.0), (479.9, 100.5, 479.9, 94.5)], mode="ink", half=3, trim=0.0)
ARROW_EW = dict(pieces=[(461.5, 113.5, 467.5, 113.5), (492.5, 113.5, 498.5, 113.5)], mode="ink", half=3, trim=0.0)

DRAFT_ARROW = 1.0      # small decorative rose
RENDER_SIGMA = 0.1     # native digital drawing; grid half-differences are smaller (see rendering_check)


def az(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1]))) % 360.0


def fold(b):
    d = ((b + 45.0) % 90.0) - 45.0
    return 45.0 if d == -45.0 else d


def main():
    g = load_gray(ROOT / RENDER)
    fits = {}
    a = fit_line(g, **ARROW)
    fits["arrow_ns"] = a
    fits["arrow_ew"] = fit_line(g, **ARROW_EW)
    tail, tip = a["p1"], a["p2"]
    arrow_az = az(tail, tip)
    if arrow_az > 180:
        arrow_az -= 360
    L_arrow = math.hypot(tip[0] - tail[0], tip[1] - tail[1])
    pick_arrow = math.degrees(math.atan(math.sqrt(2) * 1.0 / L_arrow))
    sig_arrow = math.hypot(pick_arrow, DRAFT_ARROW)

    for k, s in CHECK.items():
        fits[k] = fit_line(g, **s)
    def axis(k):
        return fits[k]["page_azimuth_deg"] % 180.0
    dv = abs(((axis("grid_v100") - axis("grid_v329") + 90) % 180) - 90) / 2
    dh = abs(((axis("grid_h136") - axis("grid_h372") + 90) % 180) - 90) / 2
    dfv = abs(((axis("frame_left") - axis("frame_right") + 90) % 180) - 90) / 2
    dfh = abs(((axis("frame_top") - axis("frame_bottom") + 90) % 180) - 90) / 2

    mpp = SB["m_per_px"]
    structures = []
    for sid, name, spec in FORT:
        r = fit_line(g, **spec)
        fits[sid] = r
        L = r["length_px"]
        bearing = (az(r["p1"], r["p2"]) - arrow_az) % 180.0
        dev = fold(bearing)
        pick = math.degrees(math.atan(math.sqrt(2) * 1.0 / L))
        sig = math.sqrt(pick ** 2 + sig_arrow ** 2 + RENDER_SIGMA ** 2)
        structures.append({
            "id": sid, "source": "jls2014-fig2", "part": "Shikarpur fortification", "kind": "fortification",
            "description": f"Fortification, {name} face as drafted (edge of the grey 'Plan of fortification' band against white paper, level-207 crossing). " + NOTES[sid],
            "endpoints_px": [r["p1"], r["p2"]], "length_m": round(L * mpp, 1),
            "bearing_deg": round(bearing, 3), "deviation_deg": round(dev, 3), "sigma_deg": round(sig, 3),
            "fit": {"method": "sub-pixel edge profiles every 1 px, total least squares with 3xMAD rejection (measure-S/code/linefit.py)",
                    "rms_px": r["rms_px"], "n_points": r["n_points"], "n_rejected": r["n_rejected"], "length_px": L,
                    "pick_sigma_deg": round(pick, 3)},
        })

    w = [s["length_m"] for s in structures]
    d = [s["deviation_deg"] for s in structures]
    W = sum(w)
    mean = sum(wi * di for wi, di in zip(w, d)) / W
    sd = math.sqrt(sum(wi * (di - mean) ** 2 for wi, di in zip(w, d)) / W)
    neff = W ** 2 / sum(wi ** 2 for wi in w)
    se = math.sqrt((sd / math.sqrt(neff)) ** 2 + sig_arrow ** 2 + RENDER_SIGMA ** 2)

    town = {
        "town": "shikarpur",
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": [{
            "id": "jls2014-fig2",
            "citation_or_service": "C. Gadekar, S. V. Rajesh and P. Ajithprasad 2014, 'Shikarpur lithic assemblage: New questions regarding Rohri chert blade production', Journal of Lithic Studies 1(1), doi:10.2218/jls.v1i1.764 (CC BY 2.5 Scotland), Figure 2, 'Plan of the Harappan site at Shikarpur showing features of the fortification wall with eastern entrance gate and plan of structures, both inside and outside of the fortified area' (courtesy Department of Archaeology and Ancient History, M.S.U. Baroda); drawing title 'SHIKARPUR Plan of the Harappan mound and Fortification'.",
            "locator": "Figure 2, image file 3262 of the HTML galley 1564 (journals.ed.ac.uk/lithicstudies/article/download/764/1564/3262), retrieved through the Wayback Machine capture of 2025-09-09; the PDF galley carries an [image] placeholder in its place",
            "file": DOWNLOAD, "sha256": sha(DOWNLOAD),
            "north_reference": "unspecified", "north_label_text": "N", "survey_year": None,
            "pdf_page_index": None,
            "render": RENDER, "render_sha256": sha(RENDER),
            "render_note": "The source is a 605 x 800 px RGBA PNG, not a PDF page, so cptools.py render does not apply; the render is the same image flattened onto white with no resampling.",
            "scale_bar_measurement": SB,
            "north_arrow_measurement": {
                "tail_px": tail, "tip_px": tip, "page_azimuth_deg": round(arrow_az, 3), "shaft_length_px": round(L_arrow, 2),
                "pick_sigma_deg": round(pick_arrow, 3), "drafting_sigma_deg": DRAFT_ARROW, "method": "sub-pixel ink fit of the N-S stroke (measure-S/code/linefit.py)",
                "description": "Cross-hair rose under the letter N: a ring with a filled centre and a cross whose N-S stroke runs from y 94.5 to 131.5; the stroke is fitted on its two arms outside the ring, the tail at the south tip and the tip at the north tip. "
                               f"The E-W stroke fits at page azimuth {fits['arrow_ew']['page_azimuth_deg']:.3f} deg, square to the N-S stroke within 0.04 deg.",
                "sigma_deg": round(sig_arrow, 3)},
            "rendering_check": {
                "distortion_sigma_deg": RENDER_SIGMA,
                "note": (f"Native digital drawing rasterised by the journal. Survey-grid lines drawn on the plan: vertical Ea1 line {axis('grid_v100'):.3f} and Ia1 line {axis('grid_v329'):.3f} deg (half-difference {dv:.3f}); "
                         f"horizontal lines at y 136 {axis('grid_h136'):.3f} and y 372 {axis('grid_h372'):.3f} deg (half-difference {dh:.3f}; the y-136 line is partly merged with the band edge). "
                         f"Figure frame half-differences {dfv:.3f} (left-right) and {dfh:.3f} (top-bottom). We use 0.1 deg, the value for a native digital drawing, which exceeds all of these.")},
        }],
        "structures": structures,
        "systems": [{
            "id": "sys1", "source": "jls2014-fig2", "part": "Shikarpur fortification", "structures": [s["id"] for s in structures],
            "deviation_deg": round(mean, 3), "se_deg": round(se, 3), "sd_deg": round(sd, 3), "total_length_m": round(W, 1),
            "n_lines": len(structures), "n_eff": round(neff, 2),
            "description": "The four faces of the near-square fortification, outer and inner edges of the drafted band. North and south faces run within about 1 deg of the plan's E-W, the west and east faces within about 0.5 deg of its N-S; the band is drawn turned slightly clockwise relative to the survey-grid lines and the north symbol, which are themselves aligned with the page to within 0.02 deg."}],
        "main_system": "sys1",
        "main_system_reason": "The fortification is the only Harappan structure drawn at measurable length on the plan and encloses the principal walled part of the town; it is the system of largest total length.",
        "notes": ("The band is the excavators' 'Plan of fortification': a reconstruction joining the excavated segments of the mud-brick wall (hatched, in trenches Do14, Ek13, Bv6, Hh6, Hc2, Fp1 and others) by straight faces drawn with dashed outlines, so the faces are drafted, not traced along exposed masonry over their whole length. "
                  "Inside the fortification the plan draws trenches and labels only ('Structures Ph. I', 'Centre Square', 'Brick paved floor'), with no wall lines. Outside it, trench Ik7 ('Str. remains') holds wall lines about 20 px (9 m) long a few pixels from the trench edges; they were not measured, since their picking error alone exceeds 4 deg. "
                  "The arrow term (2.4 deg, set by the 37-px north stroke and a one-pixel endpoint floor) dominates every line's sigma. "
                  "Survey-grid lines Ea1, Fa1, Ia1 and grid pegs are drawn but no grid values or datum are given. "
                  "In the context text of IAR 1989-90 (p. 20) we read a statement about the orientation of structures in the 1989-90 trenches G and H of the Gujarat State excavation; it played no part in these measurements."),
    }
    (PKG / "towns").mkdir(parents=True, exist_ok=True)
    (PKG / "towns" / "shikarpur.json").write_text(json.dumps(town, indent=1))
    (PKG / "fits_shikarpur.json").write_text(json.dumps({"render": RENDER, "render_sha256": sha(RENDER), "fits": fits,
                                                       "arrow_page_azimuth_deg": arrow_az}, indent=1))
    for s in structures:
        print(s["id"], s["length_m"], s["bearing_deg"], s["deviation_deg"], s["sigma_deg"])
    print("system", round(mean, 3), "sd", round(sd, 3), "se", round(se, 3), "W", round(W, 1), "neff", round(neff, 2), "arrow", round(arrow_az, 4), round(sig_arrow, 3))
    print(town["sources"][0]["rendering_check"]["note"])


if __name__ == "__main__":
    main()
