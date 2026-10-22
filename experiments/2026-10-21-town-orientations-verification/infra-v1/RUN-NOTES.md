# Infrastructure run notes

We are preparing source material and tools for independent measurements of straight architectural features. This run measures synthetic features and modern runways. It does not measure archaeological features. We work only in this package's `tools/` and `infra-v1/` directories and the assigned raw and environment directories. The model is GPT-6 in the Codex API harness; no subagents were used.

We read the repository entry point, writing rules, data coverage, source redistribution and reuse records, the literature retrospective, the experiment registry and the measurement rules. We used the repository's orient and add-data guides and the PDF skill's render-and-inspect workflow. The source search starts with held reports and continues to public report scans and author or institutional copies. The optional-town search record is `optional-plan-search-v1.json`.

## Acquisition and repairs

Wikidata's API initially returned HTTP 403 to a generic client. A descriptive research User-Agent succeeded. The first rapid series of requests then returned HTTP 429, so subsequent requests were spaced and retried, with successful responses cached. Two incomplete coordinate attempts remain in this directory. `sites-located-v1.json` reconciles the cached responses and gives all 33 towns starting points; seven records carry flags. Kanmer, Khirsara and Farmana have published site coordinates that conflict with Wikidata. The first OSM search for Allahdino returned an unrelated railway station. We rejected it and used the published coordinate in Fuls's catalogue sample. Missing coordinates for Lakhanjo-daro and Karanpura were supplied by an excavator's lecture abstract and the ASI review respectively. The mounds remain for the measurers to locate.

Earth Search requests with 1,000-item pages returned HTTP 502 for many points. Reducing pages to 100 allowed retrieval. STAC responses and failed attempt records remain local. Windows GDAL could not establish its Schannel credentials for HTTPS COG access. A Python VSI opener now obtains verified HTTPS byte ranges through requests, checks HTTP 206 and Content-Range, and exposes read, seek and tell to Rasterio. TLS certificate verification remains enabled. The opener rejects ancillary-file probes and its cleanup handles partially initialized objects.

The first imagery acquisition used Rasterio's reprojection routine to place data on the target grid. We replaced that extra warp with a fractional window read in the common UTM projection. The native 20 m SWIR bands are read bilinearly to the 10 m target; SCL uses nearest-neighbour sampling. Every accepted window must pass the SCL check for missing, defective, shadow, cloud, cirrus and snow pixels and a separate spectral no-data check. The target window covers 5 km by 5 km. Up to nine scenes are selected across years and months, below the assignment's maximum of sixteen. The manifest retains every selected scene, asset URL, transformation, local hash and attribution.

Visual inspection found that the held file named `kenoyer_1998_ancient_cities.pdf` contains a text headed “Decipherment of the Indus script”. It is excluded from the plan library. The earlier retrieval log gives `https://sindhilanguagelibrary.com/books/download_pdf/6` as its acquisition URL. We preserve the copy and record the mismatch; we do not alter the repository's held file. The preliminary Dholavira scan lacks a title page, so its identity with the ASI publication remains unconfirmed. Source filenames and uploader labels are not treated as verified citations.

The first synthetic run showed that differentiating bilinear samples with too little profile smoothing pulled short edge fits toward pixel phases. The current code smooths over one native pixel before locating profile peaks. The original development rasters and partial output remain available. That run also exposed NumPy Boolean values in JSON output; the shared writer now converts NumPy scalar types and serializes before opening an exclusive output file.

The IGRF wrapper converts the official NOAA coefficient table to an SHC representation in a temporary local directory. It interpolates coefficients in decimal years before evaluating the field, so leap-day weighting does not alter interpolation. Three saved BGS calculator outputs test 1900, 2025 and 2030 at locations outside the towns. All three declinations agree within 0.00032 degrees. The 2030 response begins with a model-range message before its JSON; the comparison preserves that response and parses the JSON object after the message.

The AAI eAIP supplies true runway bearings and threshold coordinates for Ahmedabad, Kandla and Hisar. The OurAirports Hisar threshold coordinates describe a much shorter runway than its stated length, while the current eAIP describes the extension. The official record is needed before including Hisar. The other OurAirports coordinates with long binary float tails are flagged for doubtful source precision. The requested Pakistan AIS address returned HTTP 404.

## Storage interruption

During acquisition the C: drive fell below 150 MB free and TIFF writes reported insufficient space. We stopped acquisition and the second synthetic run rather than continue filling the drive. Lossless NTFS compression was requested for the two owned raw/environment directories. We asked for at least 5 GB of free space because every allowed output path is on C:. About 1 GB became available after compression and other drive activity. Acquisition resumed in smaller batches with a 200 MiB reserve and an immediate full-array read after every TIFF write. Earlier complete acquisitions retain their nine scenes; new town acquisitions target up to five, still within the specified maximum of sixteen. Any interrupted or partial rasters must be checked before they enter the final manifests. This section will be completed with the resumed run and final verification.

## Independence and source encounters

We have not opened or searched within either excluded study directory. We have not opened the package protocol or any other Codex brief. We have not opened PDF pages 36–47 of the Jansen and Urban volume; that PDF has not been used in this run. Broad Git status output reported the names of other contributors' untracked directories, and their contents were left alone. No Git mutation, communication to other contributors, branch operation or publication was performed.

The text scanner suppressed orientation-related lines and kept page locations alone in local search records. Encounters were recorded in the Dholavira scan (the page list is in `plan-search/dholavira-scan.json`), the Surkotada scan (`surkotada-scan.json`), the Rakhigarhi scan (`rakhigarhi-scan.json`), the Farmana scan (`farmana-scan.json`) and the Kanmer article (`kanmer-scan.json`). Web searches also met orientation-related text in results for Farmana, Banawali, Balakot, Allahdino and Kotada Bhadli; only their source locations are retained. None of those statements supplies a measurement or a reference value for a town in this run.

## Rights and manifest additions

Acquired files and page renders remain local. Tracked records contain source identities, locators, hashes, our observations and aggregate validation. The acquisition records give UTC retrieval times, byte counts, formats and observed notices. The final source and rights table and the reconciled asset inventory will be added after acquisition resumes.

| Source group | Observed notice or status | Proposed manifest fields |
|---|---|---|
| Wikidata searches and P625 responses | CC0 structured data | QID, label, P625, coordinate precision, search query, source and conflict flags |
| OSM coordinate searches | ODbL; coordinates only | Coordinate source, rejected homonyms, selected starting point |
| Copernicus Sentinel-2 | Copernicus Sentinel data terms; “Contains modified Copernicus Sentinel data 2018–2026” | STAC item and self link, acquisition timestamp, cloud cover, MGRS tile, EPSG, window bounds, band resolution and resampling, SCL rejection, scene and composite hashes |
| Held and public report scans | Rights unverified unless a source explicitly states a licence | Citation, source URL, PDF and printed page, figure or plate, exact caption, north label and location, survey year, scale bar, render hash |
| PLOS ONE Khirsara article | Creative Commons Attribution notice | Article identity, site coordinate, figure and plan provenance |
| NOAA NCEI IGRF-14 coefficients | NCEI public-use notice; retained with source record | Model generation, coefficient hash, interpolation and synthesis method |
| BGS IGRF-14 calculator outputs | Rights unverified; public calculator responses | Request URL, input case, reference declination, numerical discrepancy |
| OurAirports | Public domain, no accuracy guarantee | Threshold coordinates, runway length and width, reference bearing method, precision flag |
| AAI eAIP | Rights unverified | Official runway table locator, true bearing, threshold coordinates and source timestamp |
| Synthetic rasters, picks and validation aggregates | Own work, CC0 1.0 | Seed, construction settings, code hashes, bias, RMS error and rejection counts |

This infrastructure adds geographical starting points, an indexed plan collection and calibrated measurement tools. It adds no inscribed object, object identification, find layer or archaeological bearing to the project's data coverage.

## Resumption, 21 October 2026

We completed the imagery and tool package with GPT-6 in the Codex API harness, without subagents. All 33 towns now have Sentinel-2 composites: seven retain nine scenes and 26 have five scenes, for 193 town scenes. Seven runway composites contain nine scenes each. The library indexes 26 plans for 18 towns. The located-site index contains 33 starting points and eight flags. These are source and measurement tools; no archaeological feature was measured.

### Disk audit and recovery

The initial free-space check returned 385,400,832 bytes. We read every band of all 350 held imagery TIFFs and hashed all 35 files in the plan-source directory. Four TIFFs failed full reads: three 474-byte headers and a 4,524,005-byte runway window. Every plan-source hash matched its acquisition record. The failed TIFFs were removed and their paths, sizes and failures remain in `storage-verification-v1.json`.

After the duplicate cleanup, 324 first-run TIFFs remained. Lossless DEFLATE compression with horizontal predictor 2 changed their combined logical size from 832,294,920 to 713,786,026 bytes, saving 118,508,894 bytes. Each temporary replacement was read in full and compared with the original array before replacement. `recompression-v1.json` records every old and new hash and its pixel hash. Final verification checked all 324 surviving pixel hashes again.

Recompression paused three times at the reserve check as other drive activity consumed space. One observation fell to 224,993,280 bytes free while our large writes were stopped. The first pause preceded the final replacement summary, so we added an append-only replacement journal and recovered earlier replacements by comparing their arrays with the audit's original pixel hashes. No imagery download started during this low-space interval. Space later rose above 3 GB and then above 13 GB through activity outside this contribution; we left those directories alone.

We removed nine byte-identical copies of held PDFs, retaining their originals at the paths recorded in `duplicate-cleanup-v1.json`. We also removed 22 duplicate STAC responses, eleven duplicate scene windows and their eleven identical SCL masks, and regenerable inspection and synthetic scratch. The duplicate scene windows came from the same COGs and grids but differed by at most 0.0000500083 reflectance because the earlier read rounded the fractional-window samples before scaling. We retained the later floating-point reads. Their retired hashes remain in the initial audit; this retirement is separate from the pixel-identical recompression.

The complete deletion table below and `deletions-v1.csv` account for 159 explicit file deletions and six automatically removed IGRF coefficient-conversion scratch files, totalling 482,362,114 logical bytes. The IGRF scratch files were 2,114 bytes each. Their random directory suffixes were not logged; their exact serialized size was reconstructed from the unchanged coefficient file. NTFS allocation and other drive activity mean the logical sizes do not measure the change in drive free space.

### Source completion and plans

We first recovered composites offline from held, fully read and SCL-checked windows for Kanmer, Shikarpur, Gola Dhoro, Ahmedabad and Kandla. Once the synthetic and runway validation passed and space allowed acquisition, we topped up Kanmer and Shikarpur first, then worked through the optional towns in the assigned order. All 22 resumed town acquisitions reached five scenes. The downloader checks for 1.5 GB free before starting a town, stops below 1.2 GB, and checks the output bound against the 250 MB write reserve. The final range-reader guard also checks before each HTTP range transfer, and the generic download writer checks its payload size before writing. New TIFFs use DEFLATE and predictor 2 and are immediately read and compared with the source array.

`imagery-manifest-v1-held-only.json` preserves the first reconciled manifest. `imagery-manifest-final-pass.json` preserves the acquisition-complete pass. The final canonical manifest also records the provenance corrections described below. Every final composite was compared with the median of its stated scene members. The three earlier offline town composites remain indexed as archived composites; all 557 retained TIFFs have manifest records. Landsat was not obtained for any town; the held attempt establishes no anonymous Landsat 8/9 Level-1 panchromatic product through the tested service.

Plan inspection used temporary contact sheets at 65 dpi and selected details at 110 or 150 dpi. All review PNGs were deleted. The final library gives PDF page, printed page, figure or plate, caption, north evidence, survey-year evidence, scale status and source hash, with `render_path: null`. Measurers render their own pages with `render_plan.py`. We followed three held Penn Museum links to publisher PDFs of 3,172,130, 2,851,120 and 4,317,082 bytes, each below the 30 MB limit. They supplied the Sutkagen-dor citadel plan, two Balakot plans and the Allahdino settlement plan. A 497,868-byte Shikarpur report supplied the coordinate check below.

The two Chanhu-daro plans explicitly state magnetic north and 2 November 1935. Other selected arrows leave their reference unspecified. Lothal and Kalibangan use an unattributed chapter with ASI figure credits; its book, author and year remain unresolved. Kanmer has a printed scale statement but no conventional scale bar. Allahdino has no visible metric scale, and the Sutkagen-dor bar's numeric labels are illegible in the held scan. Those entries retain the limits on length calibration. Publisher panels using commercial basemaps were excluded from the plan entries.

We corrected source identities through inspection. The file named `kenoyer_1998_ancient_cities.pdf` contains a text titled “Decipherment of the Indus script” and supplies no library plan. The Columbia excerpt is Kenoyer's 1997 city-states chapter. The file under `shikarpur/deshpande2025/` is Abhayan and colleagues' 2025 article. The Kuntasi scan is the complete 1991 volume *Recent Advances in Marine Archaeology*, with a one-page Kuntasi abstract on PDF page 52, printed page 37. The held Rakhigarhi inventory is a monuments list; the inspected excavation-report figures are sections and photographs. The Kalibangan scan is the 2020 Part II report, beginning with Chapter XI. The Dholavira preliminary scan lacks a title page. The initial acquisition labels remain as source witnesses.

The Gola Dhoro longitude in the held 2025 article differs by about 10 km from the earlier excavator coordinate. Bhan and Ajithprasad's Shikarpur report, PDF page 9, agrees with the existing starting point to within about 25 m. We retained that point and added a source-conflict flag. `coordinate-source-review-resume-v2.json` records the two coordinates and the source evidence; `sites-located-v1-before-coordinate-review.json` preserves the earlier seven-flag index.

No qualifying plan was found for: rakhigarhi, desalpur, khirsara, kuntasi, rojdi, kot-diji, nausharo, lakhanjo-daro, ganweriwala, bhirrana, kunal, mitathal, kotada-bhadli, pabumath, navinal. The library retains a missing-plan record for each. No town remains without imagery.

The final provenance review separated generated-file creation times from source retrieval times. We reclassified 148 generated JSON records as own-work creation records. For 45 old STAC responses, original request records were incomplete; pagination URLs were recovered from prior responses where possible, first-page URLs were reconstructed from the retained query code, and UTC times are explicitly approximate filesystem times. Fifty-two held TIFFs lacked preserved first-run capture times. Their `retrieved_utc` is null in the final manifest and inventory, with the gap stated. Their scene observation dates, source URLs, file hashes and pixel hashes are known. `provenance-reconciliation-v1.json` proves that this metadata correction changed no referenced path, byte count or file hash.

### Tool repairs and validation

The plan-review console first failed on PDF ligatures under the Windows text encoding; we set its output to UTF-8. The overwrite-guard probe first failed to launch a relative executable path, then succeeded with the absolute venv path.

The first resumed synthetic run is preserved in `selftest-resume-development-1.json`. Two noisy 50 m cases lacked enough usable profiles for a fit, and the similarity test exposed precision loss from large UTM offsets. We increased the minimum candidate-profile count to twelve while retaining the cap on independent samples. We centred plan and UTM controls before solving the similarity and transformed its covariance back to the original parameter frame. The second development run and final run passed without changing the RMS thresholds.

`selftest-v1.json` passed all 28 checks across 1,620 synthetic imagery cases, plus plan, magnetic-correction, system and registration checks. No profile fit was rejected. Its working files totalled 657,594 bytes, below 50 MB, and were deleted. `selftest-overwrite-guard-v1.json` confirms that an existing result is refused before a working directory is created and that its hash is unchanged. The three saved BGS IGRF comparisons also pass, with a maximum absolute declination discrepancy below 0.000315 degrees.

We added an offline runway-validation mode that reads the reconciled manifest and a `--work` argument for fresh automatic-pick outputs. Official reference overrides now recompute threshold distance, centre, nearest-town distance and eligibility. The final pass used a fresh directory and reproduced every first-pass aggregate exactly. `validation-v1/summary-first-pass.json` preserves the first pass and `validation-v1/summary.json` is the final record. Ahmedabad and Kandla use the held AAI eAIP AD 2.12 bearings and thresholds. The official Hisar table resolves the obsolete short-runway coordinates, but no held Hisar imagery exists and it contributes no fit. Four other runway references retain coordinate-precision flags.

All 14 full edges and 662 segments returned fits. Across seven runways the mean signed residual is -0.041015 degrees and RMS is 0.137144 degrees. RMS by segment length is 4.272758, 1.764927, 0.988215 and 0.746483 degrees for 100, 200, 300 and 400 m. The RMS of residual divided by stated sigma is 1.492410. The three precise-reference runways have full-runway RMS 0.020421 degrees and segment ratio 1.292660. Opposite edges share imagery and length families overlap; the summary retains this dependence.

The final raster audit treats a zero scaled reflectance as a possible valid value. Acquisition rejects raw DN zero and invalid SCL classes before scaling. The audit reports zero counts without treating every physical zero as truncated data. The tools read full arrays; the SCL record supplies the scene-validity evidence.

`verification-v1.json` records 575 distinct manifest file checks and full-band reads of all 557 TIFFs. Every manifest byte count and SHA-256 matches. All TIFFs use DEFLATE and predictor 2, all 324 recompressed originals retain their pixels, and the tested measurement-code hashes match the current tools. The raw directory contains 1,139 files and 2,042,017,230 logical bytes. Git status was read with a command-local `safe.directory` setting after Git rejected the sandbox account's ownership; no Git configuration or repository state was changed.

### Independence and remaining limits

We opened no excluded study, package protocol or other assignment brief, and no excluded Jansen PDF page. Only synthetic features and modern runway edges were measured. Orientation-related source prose was encountered during the Kenoyer chapter review, PDF pages 8–10; no town reference value was collected from it. The first-run encounter locations remain in the earlier notes. Raw imagery and scans remain local, no commercial basemap tiles were acquired, and no message, commit, branch change, publication or recurring automation was made.

One execution invariant was not met in the early diagnostics: raw JSON inventory checks used system Python without `-I`. Subsequent acquired-file production processing used the infrastructure venv with `-I`. The legacy capture-time gaps and the unlogged random names of six IGRF temporary files are preserved as limits, alongside the missing plans, incomplete chapter attribution, scale limits and flagged runway coordinates.

### Rights and proposed data-manifest fields

`asset-inventory-v1.json` records all 1,139 surviving raw files. `source-inventory-v1.json` gives the 41 PDF, HTML, CSV and coefficient-file records, including retained held originals. The final source-file rights table follows; STAC responses and Sentinel-2 windows use the source records and attribution in the imagery manifest. Generated indexes, picks and aggregates are project work under CC0 1.0, and project code is under the Unlicense. Third-party files retain their own terms and remain local.

| Source file | URL | Status | Observed notice |
|---|---|---|---|
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/SHIKARPUR2009.pdf | https://www.harappa.com/sites/default/files/pdf/SHIKARPUR2009.pdf | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/kalibangan_report2020.pdf | https://asi.nic.in/ | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/rakhigarhi_inventory.pdf | https://ignca.gov.in/ | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf | https://archive.org/download/dholavirareportpreliminaryjan2015_860_K/Dholavira%20Report%20%28preliminary%2C%20Jan%202015%29.pdf | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/data/raw/2026-10-13-mackay-marshall-tables/mackay1938/mackay1938_vol1_dli70071.pdf | https://archive.org/details/in.ernet.dli.2015.70071 | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/research/literature/sources/kenoyer_1998_ancient_cities.pdf | https://www.harappa.com/ancient-indus-cities | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/research/literature/sources/mackay_1943_chandaro.pdf | https://archive.org/details/chanhudaroexcava035218mbp | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/research/literature/sources/marshall_1931_govscan_14985.pdf | https://ignca.gov.in/Asi_data/14985.pdf | rights-unverified | Held scan; no explicit reuse licence verified |
| C:/Users/sandh/OneDrive/Projects/indus_valley_script/research/literature/sources/vats_1940_govscan_9842.pdf | https://ignca.gov.in/Asi_data/9842.pdf | rights-unverified | Held scan; no explicit reuse licence verified |
| data/raw/2026-10-21-town-orientations-verification/infra/coordinate-papers/lakhanjo-daro/source.html | https://southasia.wisc.edu/lecture-series-archive-fall-2010-spring-2015/2011-fall-lecture-series/qasid-mallah/ | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/igrf/igrf14coeffs.txt | https://www.ngdc.noaa.gov/IAGA/vmod/coeffs/igrf14coeffs.txt | explicit-license | NOAA NCEI IGRF-14 coefficients; public scientific model. NOAA page states information and software may be used freely; https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/allahdino/fairservis/source.html | https://www.penn.museum/sites/expedition/cattle-and-the-harappan-chiefdoms-of-the-indus-valley/ | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/allahdino/penn-publisher-pdf/source.pdf | https://www.penn.museum/documents/publications/expedition/28-2/Cattle.pdf | rights-unverified | Penn Museum Expedition publisher PDF; no explicit reuse licence verified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/balakot/dales-kenoyer/source.html | https://www.penn.museum/sites/expedition/shell-working-at-ancient-balakot-pakistan/ | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/balakot/penn-publisher-pdf/source.pdf | https://www.penn.museum/documents/publications/expedition/19-2/Shell.pdf | rights-unverified | Penn Museum Expedition publisher PDF; no explicit reuse licence verified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/banawali/bisht-volume/source.pdf | https://ignca.gov.in/Asi_data/85200.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/farmana/excavationsatfarmana200608vshindeetal_212_v/source.pdf | https://archive.org/download/excavationsatfarmana200608vshindeetal_212_v/Excavations%20at%20Farmana%2C%202006-08%20-%20V%20Shinde%20et%20al.pdf | rights-unverified | Archive.org scan; copyright of source report not verified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/farmana/preliminary2008/source.pdf | https://nidanaheights.com/images/Library/ranbirbooks/op6.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/gola-dhoro/slideshow/source.html | https://www.harappa.com/slideshows/gola-dhoro | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/juni-kuran/report2004/source.pdf | https://ignca.gov.in/Asi_data/87942.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/kanmer/kharakwal/source.pdf | https://nichibun.repo.nii.ac.jp/record/1259/files/symp_016__357__355_376__357_378.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/karanpura/prabhakar2017/source.pdf | https://asc.iitgn.ac.in/assets/publications/research_papers/Ground_survey_to_aerial_survey_in_archaeological_explorations_and_excavations_VN_Prabhakar_R_Korisettar_2017.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/khirsara/pokharia2017/source.pdf | https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0185684&type=printable | explicit-license | PLOS ONE article, Creative Commons Attribution licence; https://doi.org/10.1371/journal.pone.0185684 |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/kuntasi/dhavalikar/source.pdf | https://ignca.gov.in/Asi_data/80451.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/lakhanjo-daro/vidale2022/source.pdf | https://iris.unive.it/retrieve/9c27148d-aea7-42a6-b806-9e32280a4baa/Lak%20jo%20daro%202022.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/lothal/rao1979-part1/source.pdf | https://archive.org/download/masi78lothalaharappanporttownraos.r.part1platesmissing_443_k/MASI%2078%20Lothal%20A%20Harappan%20Port%20Town%20Rao%20S.R.%20Part%201%20%28Plates%20Missing%29.pdf | rights-unverified | Report scan on Internet Archive; rights of report unverified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/mohenjo-daro/kenoyer-columbia/source.pdf | https://www.columbia.edu/itc/anthropology/v3922/pdfs/kenoyer.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/navinal/deshpande2025/source.html | https://www.frontiersin.org/journals/environmental-archaeology/articles/10.3389/fearc.2025.1517351/full | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/rakhigarhi/excavationsatrakhigarhi19972000amarendranath_457_Z/source.pdf | https://archive.org/download/excavationsatrakhigarhi19972000amarendranath_457_Z/Excavations%20at%20Rakhigarhi%2C%201997-2000%20-%20Amarendra%20Nath.pdf | rights-unverified | Archive.org scan; copyright of source report not verified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/rangpur/rao1963/source.pdf | https://ignca.gov.in/Asi_data/40421.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/shikarpur/deshpande2025/source.pdf | https://www.frontiersin.org/journals/environmental-archaeology/articles/10.3389/fearc.2025.1517351/pdf | explicit-license | Frontiers article; Creative Commons Attribution (CC BY); article copyright and figure credits retained |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/shikarpur/report2007-source/source.pdf | https://old.harappa.com/goladhoro/Excavations-at-Shikarpur-2007.pdf | rights-unverified | Public excavation report on harappa.com; no reuse licence verified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/surkotada/masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t/source.pdf | https://archive.org/download/masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t/MASI%2087%20Excavations%20at%20Surkotada%20and%20Kutch%20Jagat%20Pati%20Joshi_text.pdf | rights-unverified | Archive.org scan; copyright of source report not verified |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/surkotada/university-chapter/source.pdf | https://www.lkouniv.ac.in/site/writereaddata/siteContent/202003241550006972anil_kumar_HARAPPAN_CIVILIZATION%201.pdf | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/sutkagen-dor/dales1962/source.html | https://www.penn.museum/sites/expedition/a-search-for-ancient-seaports/ | rights-unverified | No explicit reuse licence observed |
| data/raw/2026-10-21-town-orientations-verification/infra/plans/sutkagen-dor/penn-publisher-pdf/source.pdf | https://www.penn.museum/documents/publications/expedition/4-2/A%20Search.pdf | rights-unverified | Penn Museum Expedition publisher PDF; no explicit reuse licence verified |
| data/raw/2026-10-21-town-orientations-verification/infra/validation/official-aip/VAAH.html | https://aim-india.aai.aero/eaip/eaip-v2-06-2026/eAIP/IN-AD%202.1VAAH-en-GB.html | rights-unverified | Airports Authority of India eAIP; rights unverified |
| data/raw/2026-10-21-town-orientations-verification/infra/validation/official-aip/VAKE.html | https://aim-india.aai.aero/eaip/eaip-v2-06-2026/eAIP/IN-AD%202.1VAKE-en-GB.html | rights-unverified | Airports Authority of India eAIP; rights unverified |
| data/raw/2026-10-21-town-orientations-verification/infra/validation/official-aip/VIHR.html | https://aim-india.aai.aero/eaip/eaip-v2-06-2026/eAIP/IN-AD%202.1VIHR-en-GB.html | rights-unverified | Airports Authority of India eAIP; rights unverified |
| data/raw/2026-10-21-town-orientations-verification/infra/validation/ourairports/airports.csv | https://davidmegginson.github.io/ourairports-data/airports.csv | explicit-license | OurAirports public domain: https://ourairports.com/data/ |
| data/raw/2026-10-21-town-orientations-verification/infra/validation/ourairports/runways.csv | https://davidmegginson.github.io/ourairports-data/runways.csv | explicit-license | OurAirports public domain: https://ourairports.com/data/ |

The new sources in this resumption are the three Penn Museum publisher PDFs and Bhan and Ajithprasad’s Shikarpur report, plus 103 additional Sentinel-2 scene windows and their SCL masks. The held source identities and figure captions were checked and corrected in the plan index. The proposed manifest additions are: original and replacement file hashes; pixel hashes and compression; corrupt, duplicate and scratch retirement records; scene membership and exact composite checks; all 33 imagery coverage records; PDF and printed-page locators; north wording, classification and date evidence; scale availability; source-identity limits; the Gola Dhoro coordinate conflict; explicit retrieval-time gaps and approximations; synthetic and runway calibration; and final file and rights inventories. We add no inscribed object, object identity, find layer or archaeological bearing. Maintainers can fold these source and coverage records into the shared data manifest.

### Every deletion

| Removed path | Bytes per file | Count | Reason |
|---|---:|---:|---|
| infra/imagery/kalibangan/acquisition-v3/S2B_43RDN_20190408_1_L2A-window.tif | 474 | 1 | Corrupt or truncated raster: Read failed. See previous exception for details. |
| infra/imagery/mohenjo-daro/acquisition-v3/S2A_42RVR_20180114_1_L2A-window.tif | 474 | 1 | Corrupt or truncated raster: Read failed. See previous exception for details. |
| infra/validation/runway-imagery/imagery/OPFA/acquisition-v3/S2A_43RCQ_20210425_1_L2A-window.tif | 474 | 1 | Corrupt or truncated raster: Read failed. See previous exception for details. |
| infra/validation/runway-imagery/imagery/OPSK/acquisition-v3/S2A_42RVR_20220212_0_L2A-window.tif | 4,524,005 | 1 | Corrupt or truncated raster: Read failed. See previous exception for details. |
| infra/plans/mohenjo-daro/marshall1931-vol1/source.pdf | 38,393,044 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/harappa/vats1940-plates/source.pdf | 17,754,670 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/chanhu-daro/mackay1943/source.pdf | 27,802,606 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/mohenjo-daro/kenoyer1998/source.pdf | 1,058,728 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/mohenjo-daro/mackay1938-vol1/source.pdf | 51,267,309 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/kalibangan/report-part2/source.pdf | 13,694,349 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/dholavira/preliminary2015/source.pdf | 127,352,282 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/shikarpur/report2009/source.pdf | 4,020,404 | 1 | Byte-identical duplicate of held source; original retained |
| infra/plans/rakhigarhi/inventory/source.pdf | 13,628,175 | 1 | Byte-identical duplicate of held source; original retained |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-001.json | 2,087,237 | 1 | Byte-identical duplicate STAC response |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-002.json | 2,088,810 | 1 | Byte-identical duplicate STAC response |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-003.json | 2,119,363 | 1 | Byte-identical duplicate STAC response |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-004.json | 2,131,593 | 1 | Byte-identical duplicate STAC response |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-005.json | 2,138,511 | 1 | Byte-identical duplicate STAC response |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-006.json | 2,104,458 | 1 | Byte-identical duplicate STAC response |
| infra/imagery/lothal/acquisition-v4/metadata/stac-search-007.json | 2,126,737 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-001.json | 2,087,859 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-002.json | 2,122,634 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-003.json | 2,122,086 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-004.json | 2,130,329 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-005.json | 2,134,469 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-006.json | 2,138,992 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-007.json | 2,175,902 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v4/metadata/stac-search-008.json | 1,899,835 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v4/metadata/stac-search-001.json | 2,108,672 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v4/metadata/stac-search-002.json | 2,134,332 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v4/metadata/stac-search-003.json | 2,128,610 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v4/metadata/stac-search-001.json | 2,105,804 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v4/metadata/stac-search-002.json | 2,131,499 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v4/metadata/stac-search-003.json | 2,125,337 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v4/metadata/stac-search-004.json | 1,738,326 | 1 | Byte-identical duplicate STAC response |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v3/S2A_42QZL_20190324_1_L2A-window.tif | 4,516,618 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v3/S2A_42QZL_20190324_1_L2A-scl.tif | 10,230 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v3/S2A_42QZL_20200217_1_L2A-window.tif | 4,612,370 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v3/S2A_42QZL_20200217_1_L2A-scl.tif | 11,214 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v3/S2A_42QZL_20221113_0_L2A-window.tif | 4,631,652 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VAAH/acquisition-v3/S2A_42QZL_20221113_0_L2A-scl.tif | 12,948 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v3/S2A_42QXL_20220410_0_L2A-window.tif | 4,198,748 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v3/S2A_42QXL_20220410_0_L2A-scl.tif | 9,624 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v3/S2A_42QXL_20240409_0_L2A-window.tif | 4,235,044 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v3/S2A_42QXL_20240409_0_L2A-scl.tif | 9,756 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v3/S2B_42QXL_20180317_2_L2A-window.tif | 4,164,048 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VAKE/acquisition-v3/S2B_42QXL_20180317_2_L2A-scl.tif | 8,832 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20190428_1_L2A-window.tif | 3,981,742 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20190428_1_L2A-scl.tif | 4,514 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20200103_1_L2A-window.tif | 4,282,176 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20200103_1_L2A-scl.tif | 13,916 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20210206_1_L2A-window.tif | 4,204,722 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20210206_1_L2A-scl.tif | 12,132 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20221019_0_L2A-window.tif | 4,323,198 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20221019_0_L2A-scl.tif | 24,036 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20231203_0_L2A-window.tif | 4,875,020 | 1 | Duplicate scene acquisition from same COG and grid; retain later fractional-float read instead of earlier integer-rounded read |
| infra/validation/runway-imagery/imagery/VIBT/acquisition-v3/S2B_43RDP_20231203_0_L2A-scl.tif | 10,166 | 1 | Pixel-identical duplicate SCL mask for duplicate scene acquisition |
| infra/plan-search/dholavira-contact.png | 1,028,559 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/farmana-plans.png | 591,560 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/kalibangan-start.png | 1,061,164 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/kanmer-plans.png | 463,204 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/kenoyer-contact.png | 825,393 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/mackay-contact.png | 1,007,478 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/mackay-finalplates-contact.png | 1,394,332 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/mackay-north-crops-page-364.png | 130,774 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/mackay-north-crops-page-366.png | 93,445 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/mackay-plans.png | 644,617 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/mackay-plates-contact.png | 1,351,311 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/marshall-start.png | 2,503,898 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/rakhigarhi-start.png | 1,262,734 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/shikarpur-contact.png | 861,875 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/surkotada-plans.png | 1,636,830 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/university-plans.png | 502,901 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/vats-contact.png | 1,626,853 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/vats-even-contact.png | 2,488,651 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/vats-north-crops-page-14.png | 1,090,844 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/vats-north-crops-page-18.png | 544,183 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/plan-search/vats-north-crops-page-30.png | 194,853 | 1 | Regenerable first-run plan-inspection scratch; source scans and page locators retained |
| infra/temp-plan-review/mackay-arrow-364.png | 67,200 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/mackay-arrow-366.png | 39,005 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-1.png | 2,915,795 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-10.png | 1,738,275 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-11.png | 2,270,605 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-12.png | 5,045,176 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-13.png | 1,737,262 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-14.png | 1,409,180 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-15.png | 3,040,060 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-16.png | 1,618,301 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-17.png | 590,988 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-18.png | 585,650 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-19.png | 997,378 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-2.png | 1,144,111 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-20.png | 3,919,373 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-21.png | 603,496 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-22.png | 1,160,405 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-23.png | 2,874,933 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-24.png | 1,859,441 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-25.png | 1,167,594 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-26.png | 625,702 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-27.png | 932,323 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-28.png | 1,498,259 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-29.png | 1,549,299 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-3.png | 249,270 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-30.png | 2,489,490 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-31.png | 218,647 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-32.png | 267,841 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-33.png | 128,702 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-35.png | 3,640,949 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-36.png | 2,303,074 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-37.png | 381,009 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-4.png | 416,875 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-5.png | 994,510 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-6.png | 1,165,743 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-7.png | 424,557 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-8.png | 272,910 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/plans-9.png | 272,629 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/titles-2.png | 2,114,591 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/temp-plan-review/titles-3.png | 1,069,973 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/central-meridian-example.tif | 71,878 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/central-meridian-render.png | 67,763 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/central-meridian-render.png.json | 972 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/far-central-meridian-example.tif | 71,852 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/far-central-meridian-render.png | 69,612 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/far-central-meridian-render.png.json | 975 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/synthetic-detail.json | 359,177 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/synthetic-plan-render.png | 10,430 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/synthetic-plan-render.png.json | 712 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-1/synthetic-plan.png | 4,119 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/central-meridian-example.tif | 71,878 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/central-meridian-render.png | 67,763 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/central-meridian-render.png.json | 972 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/far-central-meridian-example.tif | 71,852 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/far-central-meridian-render.png | 69,612 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/far-central-meridian-render.png.json | 975 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/synthetic-detail.json | 359,281 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/synthetic-plan-render.png | 10,430 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/synthetic-plan-render.png.json | 712 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-resume-development-2/synthetic-plan.png | 4,119 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/central-meridian-example.tif | 71,878 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/central-meridian-render.png | 67,763 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/central-meridian-render.png.json | 960 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/far-central-meridian-example.tif | 71,852 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/far-central-meridian-render.png | 69,612 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/far-central-meridian-render.png.json | 963 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/synthetic-detail.json | 359,281 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/synthetic-plan-render.png | 10,430 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/synthetic-plan-render.png.json | 700 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/synthetic-final-v1/synthetic-plan.png | 4,119 | 1 | Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained |
| infra/imagery/sutkagen-dor/acquisition-v3/metadata/stac-search-001.json | 0 | 1 | Zero-byte STAC response truncated in the first storage interruption |
| infra/imagery/lothal/acquisition-v3/metadata/stac-search-008.json | 0 | 1 | Zero-byte STAC response truncated in the first storage interruption |
| infra/imagery/lakhanjo-daro/acquisition-v3/metadata/stac-search-001.json | 0 | 1 | Zero-byte STAC response truncated in the first storage interruption |
| infra/imagery/kotada-bhadli/acquisition-v3/metadata/stac-search-001.json | 0 | 1 | Zero-byte STAC response truncated in the first storage interruption |
| infra/temp-plan-review-late/allahdino-detail.png | 1,388,579 | 1 | Regenerable temporary review of newly acquired publisher plans; page locators retained |
| infra/temp-plan-review-late/balakot-detail.png | 1,193,555 | 1 | Regenerable temporary review of newly acquired publisher plans; page locators retained |
| infra/temp-plan-review-late/plans-40.png | 1,775,177 | 1 | Regenerable temporary review of newly acquired publisher plans; page locators retained |
| infra/temp-plan-review-late/plans-41.png | 1,566,878 | 1 | Regenerable temporary review of newly acquired publisher plans; page locators retained |
| infra/temp-plan-review-late/plans-42.png | 2,338,107 | 1 | Regenerable temporary review of newly acquired publisher plans; page locators retained |
| infra/temp-plan-review-late/sutkagen-dor-detail.png | 517,868 | 1 | Regenerable temporary review of newly acquired publisher plans; page locators retained |
| infra/temp-plan-review-final/rakhigarhi.png | 759,489 | 1 | Regenerable final contact sheet; inspected pages are sections and photographs, with no qualifying north-referenced plan |
| data/raw/2026-10-21-town-orientations-verification/infra/igrf/.igrf14-eval-<random>/converted.shc | 2,114 | 6 | Automatically removed regenerable IGRF conversion scratch; size reconstructed exactly from coefficients; random directory names not logged |

The ending free-space observation was 11,425,103,872 bytes (10.640457 GiB) at 2026-10-21T06:51:05.065872Z, recorded in `storage-final-v1.json`. The final hash-only pass in `final-delivery-checks-v1.json` checked all 1,148 unique referenced and inventoried files, including the complete raw inventory and held source originals, with no failures. `FINAL-REPORT.txt` gives the requested plain-text completion record.

These tools recover the directions of the seven modern runways with an RMS of 0.137 degrees, while 100 m segments have an RMS of 4.273 degrees. A new set of runways with surveyed thresholds and independent manual picks would decide how well this calibration transfers to the measurers' inputs.
