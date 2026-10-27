# Proposed source and coverage update

26 October 2026. Maintainers can integrate this record into `knowledge/DATA.md` and `data/MANIFEST.json` after review.

The [source register](sources.json) contains twelve works, with inspected scope, publication dates, dependence, original URLs and twelve local witnesses. The [evidence register](evidence.json) contains sixteen source-located observations. These records add marker history, regional chronology and preservation information to the atlas. They add zero inscribed-object identities, zero object-specific calendar dates and zero new excavation contexts to the corpus.

Four primary witnesses were downloaded in this run: the Kenoyer and Meadow 2004 chapter, Kenoyer's 2010 weight study, Neogi and colleagues' accepted geoarchaeological manuscript, and Suryanarayan and colleagues' publisher XML. These are acquisitions for this package, not claims that the publications or all their observations are new to the repository. Other sources reuse preserved project witnesses or primary web text. The acquisition manifests retain failed Giosan XML and PDF routes and the unsuccessful direct Alamgirpur retrieval. The existing complete Giosan HTML supplies the local witness.

The D: storage root and checkout `data/raw` junction were verified before writing. New raw inputs, OCR, text extraction and page images use logical path `data/raw/2026-10-26-indus-living-atlas/continuity/` and physical path `D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/continuity/`. Source hashes and byte counts are in [acquisition-v1.json](acquisition-v1.json), [acquisition-v2.json](acquisition-v2.json), [sources.json](sources.json) and [derivatives-v1.json](derivatives-v1.json). All raw files remain local-only under their individual rights.

Fields added to the reusable evidence rows are marker domain, observation versus interpretation, region, source chronology, display date bracket, confidence, field lineage and the competing history addressed. A null date bracket is deliberate when only a relative phase or landscape association is justified. Display phase ranges must not become a date assigned to every object or a continuously occupied interval.

The most useful missing data are the last stratified occurrences of inscribed objects and weights in each Dholavira stage, direct dates associated with those deposits, the Alamgirpur transition samples and failed-dating records, the Jognakhera supplement, original recovery volumes, and phase-specific survey footprints. These would permit new measurements of the difference between marker loss and occupation loss.

The [prospective design](TEST-DESIGN.md) extends the earlier crop and settlement studies. Generated navigation, the shared coverage page, the manifest, the working model and all prior outputs remain for maintainers to integrate.
