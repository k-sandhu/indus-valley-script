# Author-ordered nonlinguistic comparison corpora

These files are exploratory comparators, not Indus semantic training data. They preserve the published authors' XML order. No order was reconstructed for two-dimensional scenes. Source archive is [Sproat's author dataset](https://richardsproat.com/data/non-linguistic-symbols/corpora.zip), Apache2.0 notices retained in the XML, ZIP SHA-256 `fb50ff5acb5221ba75e134cc7a36619e1d990b5680ad8681bcde5c447b6b8f73`. Original archive bytes happen to be named `sources/sproat_2014_corpora.html` by the generic retrieval helper; magic/ZIP validity was checked, and unmodified files were safely extracted under `sources/sproat_2014_corpora/corpora/` with a manifest.

Reproduce with `C:\Python313\python.exe research/literature/flatten_nonlinguistic_controls.py`. `flatten_manifest.json` records inputs, exclusions, counts, and output hashes. JSONL has the main loader's `sequence`, `record_id`, `site`, `object_type`, `artifact_id`, and `object_family_id` fields where relevant, plus source bibliography, XML document/unit paths, side ID, source page, original symbols, alternatives, and order basis. Interpret these fields using the caveats below.

## Order and units

[Wu et al.2012](https://journals.linguisticsociety.org/proceedings/index.php/ExtendedAbs/article/download/576/487/637), pp.2–3, describes preserving conventional order where known and explicitly encodes composite figures with `symbolUnit`. [Sproat2014 supplement](https://static.cambridge.org/content/id/urn%3Acambridge.org%3Aid%3Aarticle%3AS0097850714008704/resource/name/S0097850714008704sup001.pdf), s5, likewise discusses simultaneous totem figure groups. We preserve each such group as a single compound token; members are not converted into sequential bigram edges. Plain top-level symbols remain separate tokens. This compound-token encoding is an analysis choice and differs from flattening all component figures individually.

Weather order has an especially clear external basis: successive icons represent successive forecast days (supplement s7). Totem order is the authors' stored vertical-stack order. We preserve their transcription rather than inventing an order, but have not independently rechecked all photographs or asserted a universally traditional spoken reading direction for every pole.

## Counts and dependence

| Corpus | Source documents | Included strings of at least3 units | Tokens | Types | Unique strings | Important exclusions/dependence |
|---|---:|---:|---:|---:|---:|---|
| WeatherIcons | 10,142 | 10,142 | 50,710 | 16 | 4,018 | Five icons each. Repeated forecasts share station and overlapping days. |
| TotemPoles | 326 XML documents | 180 | 878 compound-preserving units | 423 | 176 | 59 uncertain/alternative transcriptions and87 short strings excluded; includes empty XML entry. |

The weather counts agree with supplement s8 TableS2. Earlier Wu2012 counts describe an earlier collection state. Compound-preserving totem counts intentionally differ from the supplement's all-component symbol counts. Do not claim that our 878 tokens or423 types reproduce its counting convention.

Weather station IDs are conservative dependence groups. Under the project's full identical-string-plus-station transitive closure, all 4,018 unique strings connect into one group. Thus station-safe full cross-validation is infeasible for this archive. Reassigning each forecast as an independent object simply to obtain a desired result would hide overlapping-day dependence. A different sampling design would require an explicitly separate analysis.

Totem physical-object identifiers are less complete. Matching nonempty description and origin is conservatively grouped in `object_family_id`; this can overmerge and may still miss aliases with changed descriptions. Unnamed poles keep an XML-document ID. Whole-source-book or origin holdout would be useful sensitivity tests. The resulting assay should be described as exploratory and conditional on this encoding, not as fully verified physical-artifact independence.

Kudurru, barn-star, Asian-emoticon, Vinca, Pictish, and IndusBarSeals XML remains available in the source archive. We did not create sequential strings for their ambiguous nested layouts. Pictish/Vinca/Indus status is disputed and should not be treated as known nonwriting ground truth. Weather icons and totem figures here encode meteorological predictions or heraldic/narrative objects, respectively, rather than phonetic units.

## Historical priority

[Sproat2010](https://aclanthology.org/J10-3012.pdf), pp.588–592, already gives counterexamples to identifying writing from conditional-entropy curves and a classifier falsely assigning writing to deity-symbol arrangements. Farmer, Sproat and Witzel2004, p.20, already discusses positional order outside speech encoding. The project's office-routing control therefore contributes an assay-specific reproducible counterexample; its broad conceptual limit has explicit prior.
