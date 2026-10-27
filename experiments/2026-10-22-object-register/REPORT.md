# A complete base population with source-level uncertainty

We can now rebuild a register of all 4,695 provisional Lipi objects and 5,680 exported faces from the held sources. The current run contains 225,223 assertions, 16,434 source-qualified identifiers, 11,993 measurement rows and 6,826 object–image pairs. These are attributed records and repeated source observations, not counts of independent discoveries. [Coverage and table counts](run-v2/coverage.json), [schema and reference checks](run-v2/validation.json).

The base population reproduces the existing inventory exactly: 4,075 families have a usable CISI string and 3,598 have at least one positive dimension, counting a printed range as a dimension. All family and face identifiers survive. We keep each family as `LIPI:<family>` and each face as `LIPI:<record_id>`; no source alias merges two families.

## What entered the build

| Adapter | Imported evidence | Population linked |
|---|---|---:|
| CISI 1 basic data | All 1,543 rows inspected; linked entries retain raw columns, parsed accessions and holding institutions | 1,239 families |
| CISI 2 basic data | All 2,139 rows inspected with the same field treatment | 1,363 families |
| Earlier website export | Exact catalogue-string joins, museum fields, material and raw size values | 2,375 families |
| Mayig | Object identity links for 179 alternate records; face alignment remains unresolved | 179 families |
| Mackay and Marshall table joins | 1,146 inherited joined rows, field numbers, source pages, material, locus, datum and sizes | 1,134 families |
| Museum join table | Accessions, holding institutions and recorded join conflicts from 27 joined rows | 27 families |
| Image index | 8,444 existing face-link rows, preserving side relation and image hashes | 2,562 families |
| Two corrected ledger pilots | 4,302 distinct metadata assertions and original pilot aliases | 236 families |

The two CISI adapters together cover 2,602 families. The museum adapter's 27 rows are the joined rows of the named 13 October table; earlier museum evidence also appears through the pilot. This is a partial museum adapter, so its count is not the earlier census's museum union. The 20 catalogue-only keys in the pilot are retained in the unresolved queue instead of being forced into the Lipi population. The queue has 1,348 rows; repeated entries can concern the same unresolved object. [Adapter counts](run-v2/coverage.json).

## Uncertainty survives the joins

The CISI assembled tables already retain the union of reader candidates under Amendment 2. We additionally import all 3,238 reader-decision rows, including 2,870 automatic merges and 2,943 outcomes labelled undecidable. These sets overlap. The local decision table keeps each original reading, merged reading, decision note and source hash. The accepted object fields exclude automatic merges, undecidable cells, bracketed cells and disputed identities. The original candidate values remain in the assertion table and identifier list, where uncertain identifiers are marked candidate. [CISI policy and counts](run-v2/coverage.json).

There are 1,979 objects with an accepted museum-accession value under this conservative policy. This cannot be compared directly with the earlier figure of 2,450 including bracketed cells: the earlier figure uses more museum sources, while this build excludes whole cells with unresolved reader decisions. Coverage measures the source adapters and acceptance rule actually implemented.

The compact object export marks 2,596 families with unreconciled field variants. Differences include institutional abbreviations, material spellings and archaeological labels from different sources. We preserve the variants and the first-source displayed value; we have not judged which differences are substantive errors. Canonical `value_status` fields distinguish catalogued, inferred, unknown and conflicting values, while bracketed uncertainty is separate. [Interface](INTERFACE.md).

The source inventory contains 3,598 dimension-bearing families. Of these, 3,559 have a positive scalar dimension within the pilot's 1,000 mm plausibility bound; 39 are represented only by a range or an outlier. Additional source assertions supply scalar dimensions for four more families, yielding 3,563 accepted measurement-bearing objects. One reported 3,000 mm value is retained with an implausibility flag and withheld from accepted measurement fields. Printed ranges remain raw observations; the builder does not replace them with their midpoint or upper bound.

The image adapter carries the existing face index. It withholds face-specific acceptance for the keys H-603, M-663, M-1202 and M-1187 until the later plate audit is reconciled image by image. The misleading M-1187-named composite is already linked to M-1189 by the earlier index. It contains panels labelled M-1188 and M-1189; a whole-file pointer still lacks panel geometry for a particular face. Consequently an image link is sufficient for a retrieval queue, but not by itself for a segmented-sign or exact-boundary label.

## What is still needed

The first build covers the entire held Lipi population. It does not yet add all catalogue-only or post-catalogue objects to the population, import every museum harvest field, align Mayig and Helsinki faces, apply all excavation-table print corrections, resolve the later image audit, or reconstruct prior exposure and text-dependency groups. The source-specific queues and the parallel readiness audits determine these next additions. All 4,695 objects have `exposure_status=unreviewed`; zero have been certified fresh. [Deferred adapters](run-v2/coverage.json).

Q-1030 should remain open until the omitted held sources and the physical-object population have been integrated and reviewed. Shared `knowledge/DATA.md`, `data/MANIFEST.json` and generated knowledge indexes were left unchanged; [DATA-UPDATE.md](DATA-UPDATE.md) proposes the additions.

## Validation and supported claim

The unchanged pilot schema passes, and adapted semantic checks enforce complete object and face closure, source references, assertion ownership, missing-value reasons and conservative measurement handling. Twelve synthetic checks catch duplicate identities, missing sources, an assertion belonging to another object, candidate values accepted as facts, invented freshness, missing reasons, invalid dimensions and ambiguous catalogue strings. [Synthetic checks](synthetic-validation.json).

A separate source-value check compared 232,837 copied raw values with their named input records and found no mismatch. It also checked that 6,226 uncertain CISI assertions were absent from accepted fields. Derived values, inherited pilot transformations and composite locators are counted separately in that check's declared scope. [Source verification](source-verification-v2.json).

A second full build reproduced all seven detailed output files byte for byte. [Replay comparison](replay-comparison.json). Source-code snapshots and helper hashes are listed in [code provenance](code-provenance-v2.json). A [saved-note clarification](RUN-V2-NOTES.md) distinguishes imported uncertain accession assertions from the accepted-field count.

The strongest supported claim is that the held corpus can be maintained as one complete, source-attributed provisional register without suppressing unresolved source readings. The deciding next evidence is a reviewed identity and face concordance for the queued catalogue-only objects, together with adjudication of the disputed CISI cells and a documented exposure history for any proposed confirmation cohort.
