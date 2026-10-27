# Data additions and unresolved fields

This record proposes additions for maintainer integration into `knowledge/DATA.md` and `data/MANIFEST.json`. Those shared files were left unchanged.

We recorded the newly inspected Swaroop et al. 2026 source, its metadata, publicly readable methods and results, and failed access to its supplementary tables. This is a partly held source. The local publisher response is a client-challenge page, not the article. The complete PDF was readable through the web tool but could not be downloaded locally. The acquisition log's initial HTTP-200 classification is corrected in [source-manifest.json](source-manifest.json); the original request record is preserved.

The Petrie and Bates 2017 accepted manuscript with supplement was already held. Our new download has the identical SHA-256 `5256db827a8c3fa54961964ccb9894cc99d103772c319f7343e81ca57ea011f9`. It adds no independent source or excavation. We newly extracted nine phase summaries at five sites and two detailed crop-proportion tables for this question. Full tables, extracted text and page images remain local. The published article records CC BY 4.0; the replot credits the authors, DOI and transformation.

The new fields are sample and trench counts, sieve size, source-reported crop date ranges, summary crop season, original percentage denominator, phase, source table and page, and the identity of the underlying excavation dataset. The focal taxon-by-layer counts, sample volumes, laboratory identifiers, dated-specimen counts and full local phase joins remain missing. They are null in the result, not zero. No crop sample is joined to an inscribed object.

Coverage change: one newly inspected primary study partly held; one previously held comparison file reused; nine phase-summary rows extracted from five sites; zero new excavations, laboratory measurements, inscribed objects or object-calendar joins. The three focal date ranges are published observations newly recorded here.

Logical raw path: `data/raw/2026-10-25-crop-continuity/`. Physical path: `D:/projects/indus_valley_script/data/raw/2026-10-25-crop-continuity/`. The checked junction connects those paths. The [manifest](source-manifest.json) records source versions, access failures, rights and hashes. A DOI, title, site label, cultural phase or plant name does not by itself add a physical-object identity.
