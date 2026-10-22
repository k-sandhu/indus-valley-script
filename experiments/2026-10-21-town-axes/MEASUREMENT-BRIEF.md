# Measurement brief: axis bearings of planned Harappan towns

Brief of 21 October 2026, given verbatim to four measuring agents. We are compiling a table of the directions in which the walls and streets of Harappan towns were laid out. Each town is measured four times: twice from georeferenced satellite imagery and twice from published plans, by agents who do not see each other's numbers. You are one of these agents. Your role, your output directory and your method are named at the end of your assignment message.

## What to measure

The towns are listed in [towns-v1.json](towns-v1.json). The eleven under `required` come first; then take as many of the `optional` towns as you can, and add any other Harappan town with straight architecture that you come across, under a new slug. The coordinates in that file are unverified guesses. Locate each site yourself from published coordinates and the imagery, and report the coordinates you used.

A measurable structure is a straight line built in the Harappan period: the face of a fortification or platform, the edge of a street or lane, a drain, or a long house wall. Measure lines at least 20 m long where possible, and prefer the longest continuous lines. Exclude modern features, among them roads, field boundaries, canals, fences, paths for visitors, protective roofs, museum buildings, excavation trench edges and spoil heaps. Where a site has several parts (a citadel and a lower town, separate mounds or enclosures), measure each part and say which part each line belongs to. If a source or your own reading assigns a line to a building phase, record it.

For every line, report its bearing: the azimuth of the line clockwise from north in degrees, in the range 0 to 180. Also report its deviation, which is the bearing folded to the nearest cardinal direction, in the range −45 to +45, positive when the line is turned clockwise. A line with bearing 7° and a line with bearing 97° both have deviation +7°; a line with bearing 176° has deviation −4°. Give each line a one-sigma error in degrees that you can justify from the way you measured it, and its length in metres.

Group the lines into systems. A system is a set of lines in one part of the town that share a direction within a few degrees, together with the lines at right angles to them. For each system give the length-weighted mean deviation, its standard error, the standard deviation of the individual lines, the total measured length and the number of lines. Say which system you consider the town's main layout and why, and report every other system you find, including parts of a town that are oriented differently. A town with no measurable line is reported with the reason.

Measure the lines yourself. If a publication states an orientation value, record it under `published_values` with its citation and page, and do not let it replace or adjust your own measurement.

## Imagery measurers (roles img-A and img-B)

Use the Esri World Imagery tile service, `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`, at the highest zoom that gives real detail (usually 18 or 19). The tiles are in Web Mercator (EPSG:3857), north is up, and the projection preserves angles, so a bearing computed from global pixel coordinates (x east, y down) as `atan2(dx, -dy)` is a bearing from true north. Mosaic the tiles you need, record the zoom, the tile range and the SHA-256 of every mosaic you measure, and note any acquisition date the service reports for the imagery (the `World_Imagery/MapServer/identify` or the imagery metadata layer may give it; record `null` if not). Sentinel-2 images through the Earth Search catalogue (`https://earth-search.aws.element84.com/v1`) are an open alternative at 10 m for large sites, and may be used as a second witness.

Imagery files are third-party material. Save them only under `data/raw/2026-10-21-town-axes/<your role>/`, which Git ignores, and never copy them into the experiment directory. Record the attribution "Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community" in your source record.

- **img-A, manual method.** Identify each line on the mosaic and record its two endpoints in global pixel coordinates at the stated zoom. You may refine a line by fitting it to several points picked along the same edge. Derive the error from the endpoint uncertainty you estimate in pixels and the line's length.
- **img-B, automatic method.** Draw a polygon around the exposed Harappan architecture of each part of the town, excluding modern features, and compute the dominant orientation inside it from image gradients: a magnitude-weighted histogram of gradient direction (or a structure tensor) folded modulo 90°, with the peak located to a fraction of a bin. Estimate the error by resampling subareas of the polygon. Check every peak by eye against the image, report secondary peaks, and list a few individual lines measured from endpoints as a check on the automatic value. Record the polygons as longitude–latitude vertices.

## Plan measurers (roles plan-A and plan-B)

Find, for each town, the published plans that show the Harappan architecture with a north arrow: the excavation report's site plan and plans of excavated areas, and later survey plans. Many reports are held locally. Search `data/MANIFEST.json`, `research/literature/sources/` and `data/raw/2026-10-06-evidence-census/sites-deep/` (Marshall 1931, Mackay 1938 and 1943, Vats 1940, the Dholavira preliminary report, *Excavations at Kalibangan: The Harappans* Part II, Rao 1963 on Rangpur, the Shikarpur 2008–09 report, Jansen and Urban 1987, issues of *Indian Archaeology – A Review*, *Puratattva* and others), and search the web for others, for example on harappa.com, archive.org and the authors' pages. Save downloaded files under `data/raw/2026-10-21-town-axes/<your role>/` with their URL, retrieval time and SHA-256. Do not copy plans into the experiment directory.

For each plan, record the full citation, the figure or plate number and printed page, the file path and SHA-256, the PDF page index you rendered, the scale bar, the survey year if stated, and the exact label of the north arrow. Classify the arrow as `true`, `magnetic`, `grid` or `unspecified`, using only what the plan or its report states. Measure the direction of the arrow on the rendered page and the direction of each line, and report each line's bearing and deviation relative to the plan's north. Do not correct for magnetic declination. Include in the error the uncertainty of the arrow as drawn and of the page rendering (a skewed scan rotates everything; measure the page's own frame or grid lines to check). Where a town has several plans, measure each one and keep them separate.

## Output

Write one JSON file per town to `experiments/2026-10-21-town-axes/<your role directory>/towns/<slug>.json`, with these fields:

```json
{
  "town": "slug", "role": "img-A", "measured_utc": "...",
  "location": {"lat": 0.0, "lon": 0.0, "basis": "how you located the site"},
  "sources": [{"id": "src1", "kind": "imagery|plan", "citation_or_service": "...", "locator": "figure, plate, page or tile range", "file": "local path", "sha256": "...", "north_reference": "true|magnetic|grid|unspecified", "north_label_text": "...", "survey_year": null, "imagery_date": null}],
  "structures": [{"id": "S1", "source": "src1", "part": "lower town", "kind": "street edge", "description": "...", "endpoints": "pixel or lon-lat coordinates", "length_m": 0.0, "bearing_deg": 0.0, "deviation_deg": 0.0, "sigma_deg": 0.0, "phase": null, "confidence": "high|medium|low"}],
  "systems": [{"id": "sys1", "source": "src1", "part": "...", "structures": ["S1"], "deviation_deg": 0.0, "se_deg": 0.0, "sd_deg": 0.0, "total_length_m": 0.0, "n_lines": 1}],
  "main_system": "sys1", "main_system_reason": "...",
  "published_values": [],
  "measurable": true, "notes": "..."
}
```

Also write `METHOD.md` in your role directory, describing in connected prose what you did, the tools and code you used, the problems you met and how you resolved them, and `sources.json` listing every source with its acquisition record. Put your scripts in a `code/` subdirectory of your role directory. Run Python from the repository root with the system Python 3.13 (NumPy, SciPy, Pillow, OpenCV, Requests and PyMuPDF are installed). Web search and fetch tools may be deferred; load them with ToolSearch if you need them.

## Independence

Read only this brief, `towns-v1.json`, your own role directory and the sources you measure. Do not open any other file or directory under `experiments/2026-10-21-town-axes/`, the file `knowledge/directions/parpola-forward-2026-10-20.md`, or any directory `experiments/2026-10-20-*`. Do not write anywhere except your role directory and your `data/raw/` subdirectory. Do not commit, stash or switch branches. When you finish, reply with the list of towns you wrote, the towns you could not measure and why, and the paths of your files. Do not put any bearing or deviation value in your reply.

## Writing

Write `METHOD.md` and the `notes` fields for a reader who has not seen this brief: maximise comprehension, explain each step directly in connected prose, keep the shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the explanation. Use "we" for the project's actions.
