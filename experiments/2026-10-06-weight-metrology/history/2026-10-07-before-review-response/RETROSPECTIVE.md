# Weight metrology retrospective

The package produced a complete 2,058-entry catalogue frame, a recorded 60-entry visual audit, alternative mass fits, strata and western compatibility scores. The fitted precision changed substantially with the source's Dholavira class and recorded material. Full source access and archaeological classification remain the main limits on further interpretation. The work began on 6 October and continued into 7 October 2026.

## Prior work consulted and reused

Read the repository instructions, README, knowledge index, writing rules, redistribution policy and the contribution assessment. Registry searches covered the regional numerical/weight route (`REGIONNUM-01`), Susa recovery (`SUSA-SOURCE-02`) and the metrological identifiability control `ROOT-14`. The corresponding regional-west and Susa reports and retrospectives were read before extraction. The mass analysis uses new evidence from the complete catalogue frame; it does not rerun the earlier marked-weight calibration path.

The existing PDF and extracted text were retained at `data/raw/2026-10-02-connections-and-priority/regional-west/`. The framing and dehyphenation approach in `experiments/2026-10-02-connections-and-priority/regional-west/indus_weight_audit.py` informed the new parser. Its `indus-weight-audit.json` supplied the expected eight-site totals. `census.py` informed +x and mark handling. Earlier regional-west/Susa outputs supplied the three accession collisions and three historical mass disagreements used in the western selection/sensitivity. No earlier evidence or endpoint was edited.

## Extraction and validation problems

Early framing attempts stopped before a complete extraction, leaving empty local version directories. Source irregularities included cat. 395 lacking the usual catalogue punctuation, lowercase shape names, marks before material, an omitted condition comma, missing masses and unusual dimensions. Explicit handling produced extraction v3, then v4–v6. All versions remain available locally, and each successful extraction has an owned aggregate audit.

The fixed random sample was rendered in ten six-entry sheets and inspected by eye. Five sampled period fields were missing or truncated; mass and +x transcription errors were not observed in those 60 entries. Seven crops were clipped because decimal dimensions were mistaken for numbered headings. The crop rule was narrowed, the entries were rerendered, and the seven complete crops were inspected. Period recognition was repaired before fitting. Material-before-mark ordering and the absent condition comma received systematic fixes after that review. [Validation](parser-validation-v2.json) records the original 5/60 entry error rate and the repaired sample's 0/60 remaining errors.

The first analysis attempt failed its ID-order assertion before fitting: the source lists Kish cat. 874 after 875–886. Extraction v6 sorts the complete ID set. The audit was then keyed by catalogue ID; none of the 60 sampled IDs fell in the reordered segment. The protocol's pre-fit clarification records this repair. The source's Dholavira potential-class arithmetic and contextual total were preserved as discrepancies rather than resolved by mass fit.

## Computation and endpoint preservation

The main run fitted 45 site/model combinations, 36 strata, 1,800 bootstrap refits and ten quantograms. It completed in 136.997 seconds with zero reported main optimizer failures. Its manifest freezes the input, protocol, analysis code, versions, denominational supports and seeds. Completion hashes cover its numerical files. [Completion](runs/2026-10-06-main/completion.json).

The first independent verification comparison failed because in-memory date ranges were tuples while their JSON witnesses were lists. There were 713 representation differences and zero differences after JSON canonicalization. The verifier was corrected; source rows and fitted outputs were unchanged. Independent normal-density calculations, scalar cosine sums and nearest-series scoring then passed. [Verification](verification.json).

A complete rerun in `runs/2026-10-07-reproduction/` took 131.189 seconds. All 18 numerical files and nine local derivative files were byte-identical to the first endpoint, including bootstrap draws and Monte Carlo envelopes. [Reproduction comparison](reproduction.json). This same-code check complements the independent arithmetic verification.

Report preparation exposed the Monte Carlo seed deviation: code used successive site seeds, while the protocol named a single seed. The additional all-class quantogram was also beyond the specified quantogram frame. The numerical endpoint was preserved. [Implementation notes](IMPLEMENTATION-NOTES.md) and [annotations](endpoint-annotations.json) label affected comparisons Exploratory. No result was replaced with a more favourable one.

## Literature recovery and Gulf supplement

Live title/author searches checked the requested precedents and found additional earlier methods. Hemmy's 1935 treatment already discusses log distributions, proportional error, mixture curves and Susa/Indus assignment ambiguity. Rahmstorf's accessible 2020 abstract/figure excerpts already apply CQA to Harappan weights. The 2024 CQARCHAEO article supplies an earlier Python implementation. This package makes no claim of methodological or historical priority over these studies.

Five PDF downloads succeeded, including Hemmy 1931, Bibby 1970, the two Ialongo papers and the issue containing CQARCHAEO. Kenoyer 2010, Vahia/Yadav 2007 and Laursen 2016 were opened in full through the web tool. Several original chapters remained unavailable. The exact metadata and access levels are in [sources.json](sources.json), and failures are in [research-log.json](research-log.json). Raw PDFs, extracted text and web witnesses remain local. A plotting-library availability check found no Matplotlib installation; tabular outputs were sufficient, so no package was installed.

Bibby's primary English summary provided seven published Qala'at al-Bahrain weights. PDF p. 11 was rendered and checked by eye. A first image-view attempt named an unrendered page; the correct p. 11 was then viewed. A separate amendment declared the source-derived Gulf levels before supplemental residual calculation. The first supplement attempt failed when hashing a string path; the second failed on NumPy integer serialization. Their local score witnesses were retained. The corrected script completed with ordinary Python integer counts and recorded its code/source/amendment hashes. All seven source-selected observations were retained; the added 50-fold level and post-endpoint status remain explicit.

## Review and remaining work

The reviewer should repeat the page sample, the complete parser and numerical run, inspect the 18 western driving objects and source class ranges, and review the full-text access gaps. The arithmetic is reproducible within declared models. Precise manufacturing accuracy, a reconciled 505-object contextual set, complete analytical unit assignments, broad Gulf prevalence and object provenance remain unverified. Further measurements and conditions are specified beside the affected claims in the report.
