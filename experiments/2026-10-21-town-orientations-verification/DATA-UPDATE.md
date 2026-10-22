# Data update for maintainers

This package extends the object record to the places objects came from: for 34 Harappan towns it records located coordinates, axis bearings measured from open imagery and from published plans, the meaning of each plan's north arrow, layout phases with their dates and radiocarbon evidence, and horizon profiles. The records below are for folding into `knowledge/DATA.md` and `data/MANIFEST.json`. Raw acquired material stays local under `data/raw/2026-10-21-town-orientations-verification/` (about 4.5 GB at the end of the work, including a 384 MB Python environment).

## New sources

| Source | What we hold | Rights | Locator |
|---|---|---|---|
| Copernicus Sentinel-2 L2A, Earth Search STAC (AWS open data) | Five- or nine-scene median composites and scene windows, 5 km × 5 km at 10 m, for 33 towns and 7 airport runways; 557 GeoTIFFs, DEFLATE-compressed | Copernicus Sentinel data terms; "Contains modified Copernicus Sentinel data 2018–2026" | [infra-v1/imagery-manifest-v1.json](infra-v1/imagery-manifest-v1.json) |
| Copernicus DEM GLO-30 and GLO-90 (AWS open buckets) | 13 GLO-30 and 103 GLO-90 tiles within 250 km of the eleven required towns | Copernicus DEM licence; attribution in [astro-v1/COPERNICUS-ATTRIBUTION-v1.txt](astro-v1/COPERNICUS-ATTRIBUTION-v1.txt) | [astro-v1/SOURCE-MANIFEST-v1.json](astro-v1/SOURCE-MANIFEST-v1.json) |
| SIMBAD (CDS) | Positions, proper motions, parallaxes and radial velocities of Alcyone, Aldebaran, Procyon and Thuban | SIMBAD acknowledgement | [astro-v1/stars-retrieved-v1.json](astro-v1/stars-retrieved-v1.json) |
| IntCal20 curve; ERFA test file; IGRF-14 coefficients (NOAA NCEI) | Calibration curve, precession test vectors, geomagnetic coefficients with three calculator checks | Open; ERFA BSD notice kept in `astronomy/LICENSE-ERFA.txt` | `astro-v1/`, [infra-v1/igrf-validation-v1.json](infra-v1/igrf-validation-v1.json) |
| OurAirports and AAI eAIP | Runway thresholds and true bearings for validation | OurAirports public domain; eAIP rights unverified | [infra-v1/official-runway-references-v1.json](infra-v1/official-runway-references-v1.json) |
| Published site plans | Plan library of 26 plans for 18 towns, with citation, PDF and printed page, figure, caption, north-arrow evidence and survey year; measurers added further scans (Marshall 1931 vol. III and Mackay 1938 vol. II from IGNCA, *Pakistan Archaeology* 2, Khirsara S1 Fig., Trivedi 2009 and others) | Mostly rights-unverified, local only; Khirsara figure CC BY | [infra-v1/plan-library-v1.json](infra-v1/plan-library-v1.json), `measure-A/sources-*.json`, `measure-B/sources-*.json` |
| Dating literature | 58 sources for phase sequences and radiocarbon determinations, with locators and access routes | Mixed; downloads local only | [dating-v1/sources.json](dating-v1/sources.json) |

## New fields

For each town and measurer: located point and method; every measured line with source, part, kind, identification, endpoints (pixel, UTM, geographic or plan metres), length, bearing, folded deviation and error; systems with value, standard error and total length; the main system per source; plan north class (`true`, `magnetic`, `grid`, `unspecified`) with the exact evidence and survey year, and the IGRF declination where applied ([measure-A/towns/](measure-A/towns/), [measure-B/towns/](measure-B/towns/)). For each town: the combined deviation under the frozen rule with its error and part ([table-v1/town-values.json](table-v1/town-values.json)). For each town and part: phase sequence, layout phase, candidate start by level of evidence, radiocarbon determinations (laboratory code, age, error, material, context, phase, relation to the layout phase) and first occupation ([dating-v1/](dating-v1/)); the strict and liberal layout dates ([dates-v1/](dates-v1/)). For each of the eleven required towns: the apparent horizon from 45° to 135° and 225° to 315° at 0.1° ([astro-v1/horizon/](astro-v1/horizon/)).

## Coverage change

Before this package and the town-axes package, the project held no settlement-level orientation, horizon or layout-date record. Here, 33 towns have located coordinates and Sentinel-2 composites, and measurer B added a 34th, Tarkhanewala-Dera, from plans; 2 have an imagery bearing within the 2° rule (Lothal from both measurers, Dholavira from one); 23 have at least one plan bearing relative to a drawn arrow (16 from measurer A, 22 from measurer B); none has a plan with a stated true north; 10 towns (17 parts) have a layout date under the strict reading of the dating rule and 21 towns (36 parts) under the liberal reading.

## Gaps and corrections

- **No open sub-metre imagery.** Sentinel-2 resolves walls only when they are several hundred metres long; Landsat panchromatic imagery could not be read without an account. A true-north bearing for most towns needs a ground or drone survey, or plans registered to surveyed control points.
- **Plan arrows.** No plan in our library states true north; Mackay's Chanhu-daro plates name magnetic north (2 November 1935). The legend of Vats 1940, Plate I, gives the 1930 magnetic declination, which may fix the meaning of the Harappa plates' arrows and should be read.
- **Dating.** No Bayesian model of a layout boundary exists for any town. Dholavira's individual radiocarbon table was not obtained. Mohenjo-daro's early wall date (2708–2576 cal BC, 2025–26 excavations) is known here only from a 2026 article quoting the preliminary report.
- **Held file with the wrong content.** `research/literature/sources/kenoyer_1998_ancient_cities.pdf` contains a text headed "Decipherment of the Indus script", not Kenoyer's *Ancient Cities of the Indus Valley Civilization*; its retrieval log gives `https://sindhilanguagelibrary.com/books/download_pdf/6`. The file was left unchanged.
- **Duplicated pages in a held scan.** `research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf` contains *Interim Reports* vol. 2 twice; Wanzke's printed pages 33–44 sit at PDF pages 36–47 and again at 228–239.
- **Conflicting site coordinates.** Gola Dhoro has published longitudes about 10 km apart, and Kanmer, Khirsara and Farmana have published coordinates that conflict with Wikidata ([infra-v1/sites-located-v1.json](infra-v1/sites-located-v1.json)).
