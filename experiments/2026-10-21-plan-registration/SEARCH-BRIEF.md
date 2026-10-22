# Brief for the search agent: plans of Rakhigarhi and Shikarpur

You work for the plan-registration package of the Indus research repository at `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (run every command from that root, with Python 3.13). Your agent label is S. Your task has three stages for each of two towns, Rakhigarhi (Hisar district, Haryana, about 29.29 N, 76.11 E) and Shikarpur (Kachchh, Gujarat, about 23.24 N, 70.68 E): find a published plan, measure the directions of its Harappan walls relative to the plan's own north arrow, and then register the plan to satellite imagery. Read [REGISTRATION-BRIEF.md](REGISTRATION-BRIEF.md) first. Its rules on what not to open, on tools, on control points and on the control file apply to you; write your control files to `experiments/2026-10-21-plan-registration/control-S/` and use `--reg S` with the tools.

## Stage 1: finding a plan

A usable plan shows Harappan structures (walls, a fortification, a street grid or drains) with straight runs long enough to measure, has a north arrow, and preferably a scale bar. For registration it should also show, or be linkable to a plan that shows, features visible today: mound outlines or contours, roads, a village, canals, survey pillars. An earlier search found only these, all unusable for wall directions: for Rakhigarhi, A. Nath's report *Excavations at Rakhigarhi 1997-98 to 1999-2000* (ASI; Internet Archive item `excavationsatrakhigarhi19972000amarendranath_457_Z`), whose figures are sections, and Nath's site plans in *Puratattva* 28 (1998) and 31 (2001), which show mounds only and are marked not to scale; for Shikarpur, K. K. Bhan and P. Ajithprasad's excavation reports of 2007-08 and 2008-09 on harappa.com (a contour map; the one structural plan replaced by an image placeholder in the open copy) and C. Gadekar and P. Ajithprasad's paper on the Shikarpur lithic assemblage in the *Journal of Lithic Studies* (Figure 2, a site plan). Copies the earlier search downloaded are in `data/raw/2026-10-21-town-axes/plan-B/downloads/` (`nath_rakhigarhi_1997-2000.pdf`, `puratattva28.pdf`, `puratattva31.pdf`, `shikarpur_2007-08_harappacom.pdf`, `shikarpur_lithic_studies_764.pdf`); look at them again, since a figure judged unusable for wall directions may still serve as an auxiliary plan.

Then search further: the Deccan College excavations at Rakhigarhi from 2013 (V. Shinde and colleagues; reports, theses and journal papers on RGR-1, RGR-2, RGR-4 and RGR-7 with trench and structure plans), *Indian Archaeology - A Review* entries for Rakhigarhi (1997-2001) and Shikarpur, the Shikarpur fortification papers of the M. S. University of Baroda team, and any open thesis. Use web search, the Internet Archive's search interfaces and open repositories. Save every download under `data/raw/2026-10-21-plan-registration/S/downloads/` and record for each the URL, final URL, UTC retrieval time, HTTP status, byte size and SHA-256 in `experiments/2026-10-21-plan-registration/measure-S/sources.json`, together with the sources you examined and rejected and why. Do not log in anywhere, do not accept terms on anyone's behalf, and download only openly available files.

## Stage 2: measuring the plan

For each usable plan, render the page with `cptools.py render` and measure on that render, in its pixel frame. Read crops through `cptools.py grid`.

- **Arrow.** Pick the tail and tip of the north arrow's shaft (or the midline of a compass rose from centre to the N tip). Its page azimuth is atan2(dx, −dy) in degrees, clockwise from page-up, with x to the right and y downward. Its error is the picking term atan(√2 e / L) for the shaft length L in pixels and an endpoint error e of at least one pixel, combined in quadrature with a drafting term of 0.5° for a ruled arrow, 0.75° to 1° for a small or decorative rose and 1.5° for a short freehand arrow. Record whether the arrow is labelled true, magnetic or grid north, or not labelled (`unspecified`).
- **Scale bar.** Pick its end ticks and give the length in metres.
- **Lines.** For each straight wall face, street edge, drain or fortification face, pick the two ends of the longest continuous straight stretch, avoiding corners. You may refine a pick by fitting a total-least-squares line to the dark pixels within a few pixels of it. A line's page azimuth is computed as for the arrow; its bearing is its page azimuth minus the arrow's, modulo 180°; its deviation is the bearing folded to the nearest cardinal direction, in (−45°, +45°], positive clockwise. Its error combines in quadrature the picking term over the line's length, the arrow term, and a rendering term of 0.1° to 0.7° by kind of reproduction (0.1° for a native digital drawing, up to 0.7° for a creased fold-out photographed at low resolution) or, where the plan has a printed frame or grid, half the difference between its parallel lines.
- **Systems.** Group the lines of one part of the town that share a direction within a few degrees, together with lines square to them, into a system. Its deviation is the length-weighted mean of its lines' deviations, its standard deviation the weighted scatter, and its standard error the root sum square of the scatter divided by the square root of the effective number of lines and of the arrow and rendering terms. Declare one main system per town, the system of largest total length in the town's principal walled or gridded part, with a reason.

Write the measurements, before you start any registration, to `experiments/2026-10-21-plan-registration/measure-S/towns/<town>.json` in this form (field names matter, because the coordinator's code reads them):

```json
{
 "town": "rakhigarhi",
 "measured_utc": "2026-10-21T20:00:00Z",
 "sources": [
  {"id": "<short source id>", "citation_or_service": "...", "locator": "Fig. 3, printed page 12 (PDF page index 20)",
   "file": "data/raw/2026-10-21-plan-registration/S/downloads/<file>.pdf", "sha256": "...",
   "north_reference": "unspecified", "north_label_text": "N", "survey_year": null,
   "pdf_page_index": 20, "render": "data/raw/2026-10-21-plan-registration/S/renders/<file>.png", "render_sha256": "...",
   "scale_bar_measurement": {"p1_px": [x, y], "p2_px": [x, y], "length_m": 20.0, "m_per_px": 0.1},
   "north_arrow_measurement": {"tail_px": [x, y], "tip_px": [x, y], "page_azimuth_deg": 0.0, "shaft_length_px": 60.0,
                               "pick_sigma_deg": 0.9, "drafting_sigma_deg": 1.0, "method": "hand pick", "description": "..."},
   "rendering_check": {"distortion_sigma_deg": 0.3, "note": "..."}}
 ],
 "structures": [
  {"id": "s1", "source": "<source id>", "part": "<named part, e.g. RGR-2 fortification>", "kind": "wall",
   "description": "...", "endpoints_px": [[x1, y1], [x2, y2]], "length_m": 30.0,
   "bearing_deg": 0.0, "deviation_deg": 0.0, "sigma_deg": 1.0}
 ],
 "systems": [
  {"id": "sys1", "source": "<source id>", "part": "<same part name>", "structures": ["s1"], "deviation_deg": 0.0,
   "se_deg": 1.0, "sd_deg": 0.5, "total_length_m": 30.0, "n_lines": 1, "description": "..."}
 ],
 "main_system": "sys1",
 "main_system_reason": "...",
 "notes": "..."
}
```

Keep any measuring code you write in `experiments/2026-10-21-plan-registration/measure-S/code/`. A town for which no usable plan exists gets a town file with empty `sources`, `structures` and `systems`, `main_system: null`, and the examined sources in `notes`.

## Stage 3: registering the plan

Register each measured plan under the rules of the registration brief, with the plan id `<town>:<source id>`. Your plans are not in `plans-v1.json`, so list each one in its control file's `aux_plans` with its `render` and `scale_bar` as well (this lets the checking tool find it), and use the same id in the link.

End with a short report in connected prose: the sources examined, the plans found, the systems measured with their part names (the numbers are in your files), whether each plan was registered and with what rotation error and scale ratio, and the files you wrote. Write it to maximise the reader's comprehension: explain directly in connected prose, keep shared assumptions together, and do not interrupt the account with repeated warnings or corrective comparisons.
