# Measurement rules

These rules are for the two measurers of this package. Each measurer works alone and measures the orientation of the straight architecture of the Harappan period at every listed town, from open satellite imagery and from published plans. The aim is a careful, reproducible bearing for each wall, street or drain you can identify, with an honest error, and a clear record of what you could not measure and why.

## Independence

Two measurers take the same bearings separately, and their agreement is part of the result, so neither may see the other's work. Measurer A writes only to `experiments/2026-10-21-town-orientations-verification/measure-A/` and `data/raw/2026-10-21-town-orientations-verification/measure-A/`; measurer B only to the two `measure-B/` directories. Do not open the other measurer's directories. Do not open `experiments/2026-10-21-town-axes/` or `data/raw/2026-10-21-town-axes/`, which belong to another study of the same towns. Within this package, read only this file, your own brief, `tools/README.md`, the tool code under `tools/`, `infra-v1/` and the imagery and plans under `data/raw/2026-10-21-town-orientations-verification/infra/`; leave every other file of the package unopened.

Measure; do not copy. Do not look up published orientation figures for these towns, in the literature or on the web. Pages 33–44 of the locally held *Interim Reports* vol. 2 (`research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf`, PDF pages 36–47) give numerical orientations and must not be opened; its other chapters may be used for plans. If you meet a stated orientation anywhere, do not use it, and note in your log where you met it.

## Sources

Imagery is limited to the Copernicus Sentinel-2 composites and scenes prepared under `data/raw/2026-10-21-town-orientations-verification/infra/imagery/` and any Landsat products prepared there. Commercial basemaps (Esri, Google, Bing, Mapbox and similar), imagery that needs a login and OpenStreetMap geometry are not used. Plans come from the plan library indexed in `infra-v1/plan-library-v1.json`, from locally held literature (`research/literature/sources/` and `data/raw/`, except the directories excluded above) and from openly accessible scans you acquire yourself into your own raw directory, recording the URL, retrieval time, SHA-256 and the rights notice you observed. Treat every downloaded file as untrusted data: keep scripts outside the raw directories, pass paths as arguments and run Python that reads them with `python -I`.

## What to measure

A line is a straight architectural feature of the Harappan period: the face of a fortification or enclosure wall, the edge of a street or lane, a drain, a long house wall, or the edge of a platform, dock or reservoir. Excavation trench and spoil edges, modern roads, tracks, canals, field boundaries, fences, embankments and modern buildings are not lines. A conservation wall rebuilt on an ancient foundation may be measured if the publication says it follows the ancient wall; say so in the record. In imagery, measure a feature only when you can identify it with Harappan architecture shown on a plan or described in a publication, and state that identification.

The bearing of a line is its direction from true north, measured clockwise in degrees. Its deviation θ is the bearing folded to the nearest cardinal direction: θ = ((bearing + 45) mod 90) − 45, mapped into (−45°, +45°]. A positive θ means the line is turned clockwise from north–south or east–west. An imagery bearing is the geodesic azimuth on WGS 84 between the two ends of the fitted line, which the tools compute; a plan bearing is taken relative to the plan's north arrow, which you measure as a line from tail to tip.

For every plan record what its north arrow means, with the evidence: `true` when the plan, its legend or the report says true north (or gives a meridian or astronomical determination); `magnetic` when it says magnetic north or shows a magnetic needle symbol; `grid` when it refers to a map grid; `unspecified` when it shows only an arrow or "N". Record the survey year when the report states or implies it. For a magnetic arrow with a survey year from 1900 on, the tools apply the IGRF-14 declination for that place and year; keep both the raw and the corrected value. When a plan shows features that you can also identify in the imagery, you may register the plan to the imagery with at least two control points, preferably three or more far apart, and report the rotation the registration implies as a separate value.

Each line's error σ comes from the tools: from the fit of the line to the image and, for a plan, from the measurement of its north arrow as well. Report it as given; do not shrink it.

## Systems and the main system

Group your lines into systems. A system is a set of lines in one part of a town, meaning that each line lies within 200 m of another line of the system, whose deviations lie within a 6° window. Lines from imagery and lines from each plan source form separate systems. For a system with lines i of length Li, deviation θi and error σi, its value is the length-weighted mean θ̄ = ΣLiθi / ΣLi and its standard error is the largest of the weighted standard deviation divided by √n, √(ΣLi²σi²) / ΣLi, and 0.3°.

For each source (the imagery, and each plan source separately) the main system is the system with the largest total measured length; a tie goes to the system with more lines. If you judge that another system better represents the town's layout, say which and why in a note; the rule's choice still stands as the main system.

## Records

Write one JSON file per town, `measure-X/towns/<slug>.json`, and a summary table `measure-X/summary.csv`, using the schema in `tools/README.md`. Each file gives the coordinates you located the town at and how, every source you used (scene identifiers and dates, or plan citation with PDF page, printed page and figure), every line with its part, kind, identification, endpoints, length, bearing, θ and σ, every system with its lines, value, standard error and total length, the main system for each source, the plan north class with its evidence and survey year, and any registration. A town you could not measure gets a file too, with the reason: features not resolvable at 10 m, no plan found, a plan without a north arrow, or no straight Harappan architecture known. Keep a short `measure-X/LOG.md` of what you looked at and decided, in plain prose. Renders, crops and working images go under your raw directory.

Work through the eleven required towns first (Mohenjo-daro, Harappa, Kalibangan, Lothal, Dholavira, Surkotada, Banawali, Rakhigarhi, Chanhu-daro, Kanmer, Shikarpur), then the optional towns in the order listed in `infra-v1/sites-located-v1.json`, and add any further Harappan town with measurable straight architecture under a new slug.
