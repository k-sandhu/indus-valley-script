# Codex run 2G: extract post-catalogue inscribed objects for Gujarat and Maharashtra, Dholavira excepted

## Your part

Part letter `G`. Owned paths: `experiments/2026-10-21-post-catalogue-finds/extraction/G/` and `data/raw/2026-10-21-post-catalogue-finds/run2G/`. Output files are named with `G` in place of `<part>`. Dholavira is a separate part (run 2D); do not extract Dholavira objects, but note in your site notes any Dholavira page you happen to read.

Sites (code, project label, aliases). Every site has CISI 1, 1987, as its baseline unless stated.

| Code | Site | Aliases |
|---|---|---|
| KHR | Khirsara | |
| KNM | Kanmer | |
| SKP | Shikarpur | |
| GDH | Gola Dhoro (Bagasra) | Bagasra, Gola Dhoro |
| NGW | Nagwada | |
| PDR | Padri | |
| BTD | Bet Dwarka | |
| KNT | Kuntasi | |
| JKR | Juni Kuran | |
| KBD | Kotada Bhadli | |
| NVN | Navinal | |
| SKT | Surkotada | |
| DSL | Desalpar | Desalpur |
| RJD | Rojdi (baseline CISI 3.2, 2019) | Rodji |
| LTL | Lothal | |
| DMB | Daimabad | |
| JNK | Juna Khatiya | |
| PBM | Pabumath | |
| PTH | Pithad | |
| NGS | Nageshwar | |
| KNW | Kanewal | |
| RNG | Rangpur | |
| PRB | Prabhas Patan | Somnath |
| new | any other Gujarat or Maharashtra site whose IAR or journal entry reports an Indus inscribed object, for example the leads Umta (District Mahesana), Siyot (District Kutch) and Shaktari Timbo, Moti Pipli (District Banaskantha) in `acquisition/new-site-leads-1a.csv` | |

For a new site, assign a three-letter code not used in `selection/sites-seed.csv` and record why you included it.

Sources. Use `acquisition/candidate-pages-1a.csv` (rows for your site codes, and `GENERIC` rows that fall in IAR entries under Gujarat and Maharashtra headings) with the page text under `data/raw/2026-10-21-post-catalogue-finds/run1a/text/`. Read at least these in full where they cover your sites: `surkotada-1990` (Joshi 1990, MASI 87; excavated 1971–72, so `excavated_before_baseline = yes`; CISI 1 catalogued six Surkotada objects, Sktd-1 to Sktd-6, and the matching run checks containment), `kanmer-ch6`, `kanmer-ch8-held`, `shikarpur-2009-held`, `khirsara-2017-held`, `nagwada-2018-held` and `juna-khatiya-2021-held`. The Kanmer witnesses of an earlier package are hashed in `acquisition/source-register-1a.csv` as `kanmer-frame-<n>`; their bibliography is in `experiments/2026-10-02-six-hour/kanmer-physical-use/SOURCES.md` and the `source-register.json` beside it, and they include the registrations of Kanmer seals and sealings.

Run 1B downloaded these into `data/raw/2026-10-21-post-catalogue-finds/run1b/sources/<id>/`, without page text: `khr-nath-2014`, `khr-report-2014`, `skp-report-2008`, `skp-report-2009`, `gdh-bhan-2005`, `gdh-jamison-2017`, `ngw-sonawane-2018`, `btd-gaur-2002`, `puratattva-42-2012`, and the IAR volumes `iar-2001-02`, `iar-2002-03`, `iar-2004-05`, `iar-2005-06`, `iar-2008-09` and `iar-2011-12`. Extract their page text into `data/raw/2026-10-21-post-catalogue-finds/run2G/text/<id>/p<NNNN>.txt` (PDF text layer, Tesseract for image-only pages) and locate your sites in them with the same keyword rule; `acquisition-web/candidate-publication-locators-1b.json` lists 1B's own page hits. Bibliographic records for 1B sources are in `acquisition-web/source-candidates-1b.csv`.

`gdh-jamison-2017` is a seal study that lists the Bagasra seals individually; read it for registrations, findspots and plates only and skip its stylistic descriptions.
