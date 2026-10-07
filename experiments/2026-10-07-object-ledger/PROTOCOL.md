# Object-ledger pilot protocol

Frozen design, 7 October 2026, before row construction or completeness computation. Status: Frozen evaluation for the selection and descriptive comparisons below. Source assertions and AI-prepared identity links remain Exploratory until specialist review.

## Question and inputs

Can a 200-carrier local pilot connect catalogue identifiers, corpus faces, museum records and archaeological observations while preserving conflicting assertions, missing fields and asset rights? Reuse the October 2 dataset schema and stage 2 plan; the October 6–7 census registers, v6 corrections and museum joins; the pinned Lipi and Mayig face exports; the Harappa object frame; the Lothal physical-use frame; and the chronology package's Harappa period mapping. Consult the Kanmer, Susa and Oxus audits for source conventions and available external identity evidence. Hash each actual input. No new acquisition or web search is part of this package.

The census defines a face as one normalized inscription record, which can combine lines or source boundaries. The local corpus is the pinned 5,680-row Lipi export; Mayig is a separate annotation layer. An absent key is a reviewed catalogue base identifier missing from that export, not proof of an undiscovered or independently excavated object. A catalogue-only carrier is a published object assertion with identity and inscription eligibility awaiting review where the source does not resolve them.

## Entity and provenance model

Use separate tables for physical objects, surfaces, source-qualified transcription records, image witnesses, source editions, identifier assertions, contexts, measurements, assertions, asset rights and identity relationships. One physical carrier can have several surfaces, transcriptions and photographs. `bis`, `ter` and `quater` are photographic witnesses; seal impressions illustrated beside seals do not create another carrier without a separately registered object. Excavation item identifiers and deposit/lot identifiers occupy separate fields. Candidate joins retain candidate status and cannot merge objects. A unique catalogue base plus one export family supports an operational join, whose expert-review status is recorded separately.

Each factual value is an assertion with source ID, exact file/record/field locator, original page or URL when available, method, confidence and review status. Context includes site, region, area, room/grid, stratum/phase, period label, calendar interval and dating basis. Measurements include value, dimension, unit, source and method. Every requested empty field has a reason: not recorded in inspected source, placeholder, unavailable witness, unresolved identity, not applicable, restricted payload, or unverified source mapping. Calendar intervals use positive BCE endpoints, oldest >= youngest; period conversions remain attributed ranges and never imply a dated specimen. Rights attach to individual image/transcription assets and distinguish reference-only pointers from redistributed payloads.

The public-safe view contains identifiers, observations, citations, missingness and transcription metadata. All sign sequences from Lipi and Mayig remain local, including sequences reachable through copied raw records. The validator must reject sequences in the public tables, broken foreign keys, invalid units, nonpositive measurements, reversed intervals and missing reasons. Unknown surface alignment between annotation sources is explicit.

## Deterministic selection

Create a candidate frame before populating observations. Retain one operational carrier per unique Lipi family with an unambiguous catalogue base. Exclude catalogue-caption corrections that duplicate another carrier. All sorting uses SHA256 of `object-ledger-20261007|<candidate key>` with the key as tie-breaker; select only distinct carriers. Mandatory groups are processed in this order:

1. All 22 Harappa tablets H2218–H2239 from the inspected source frame.
2. Harappa objects carrying explicit Period 3A, 3B and 3C labels: one 3A, eight 3B and eight 3C, with suffix labels admitted for 3B/3C. Keep the one-row 3A limitation visible.
3. Twenty-four confirmed museum joins, round-robin across institutions, excluding carriers already selected. This exceeds the required twenty.
4. Twenty-five Lothal sealings with corpus joins, round-robin across source context/category combinations.
5. Twenty catalogue-only CISI 1 keys from the census absent-key register, prioritizing Lothal sealings in the inspected L124–L216 frame, then reviewed non-pottery catalogue sections. Require published carrier evidence and exclude known corrigendum duplicates. Keep unverified inscription eligibility explicit.
6. External finds: up to five carriers per group (Gulf, Mesopotamia, Iran and Central Asia), round-robin across sites, requiring an object identifier. Include all available if a group has fewer than five. Never substitute comparative Susa weights or Oxus tokens lacking an Indus inscription link.
7. Fill to exactly 200 by round-robin across `(region, site, normalized object type, maximum face-length bin, damage flag, multi-face flag)`. Length bins are 0, 1–2, 3–5, 6–9 and 10+. Damage means an unknown marker or a noncomplete preservation/condition assertion; preserve the underlying fields. Do not require prediction eligibility.

If required inputs or candidate quotas are unavailable, record the failure and make a dated pre-outcome amendment before changing selection. Save the actual ordered IDs, source memberships and selection reasons before enriching rows or computing results. Record overlaps and quotas in the selection manifest; the sample is purposive and cannot estimate global completeness.

## Population and comparisons

Populate only from local witnesses. Apply relevant v6 census batch corrections as attributed overlays; preserve original source assertions. Compare each field on the same 200 carriers, assigning corpus coverage zero to the catalogue-only carriers. Also report a matched-corpus denominator excluding those carriers. A field is present if at least one nonplaceholder, source-located assertion exists; this measures traceability and does not validate its archaeological accuracy. Separate period labels, attributed calendar intervals and independent dating-sample links. Count image pointers separately from inspected photographs.

Report confirmed and candidate joins by source and method. Reuse museum pair adjudications on the selected subset with their exact denominators; unadjudicated additional pairs remain missing. Preserve within-family disagreements and compare normalized fields only by explicit normalization rules. Count source lookups as unique `(input file, record locator)` witnesses consulted per carrier, with total, median, range and field-level provenance. This is computational lookup cost, not elapsed human review time or a new page-reading count.

Create a review queue with carrier, specific unresolved question, field, evidence pointer and reviewer role. Negative outcomes include unmet mandatory groups, ambiguous accepted merges, missing provenance, invalid foreign keys, restricted sequence leakage, or no field gains over the matched corpus. Report these outcomes with the affected denominator.

## Helsinki 1979 import interface

Define a source-qualified text-number crosswalk interface. A 1979 text number joins through an inspected concordance such as Koskenniemi, Parpola and Parpola's 1980 Documentation and Duplicates or explicit CISI cross-references. Numeric equality with a CISI or Lipi ID is insufficient. Require edition, text number, concordance source/page, target identifier, surface relation, rights/license and review status. Accept confirmed unambiguous object joins; quarantine candidate, collided or missing joins. Preserve inventory, version, editorial markers and order on each imported transcription. Test the interface using clearly labelled synthetic fixtures, outside the archaeological counts. Actual Package M rows require its delivered payload and reviewed crosswalk.

## Preservation and verification

Use fresh dated run directories, refuse existing output endpoints, and keep temporary files under the package's raw directory. Supply a machine-checkable schema, referential/unit/interval/rights validator and independent reconstruction checks. Rebuild into a fresh reviewer directory; compare normalized output hashes. Run the repository prose scanner. No shared file, repository history, publication, contact or automation is modified.

## Pre-outcome clarification, 7 October 2026

Input discovery found that most external export rows have no CISI reference. Admit these rows to the external mandatory pools by their source-qualified pinned export family, and keep physical identity confidence at `source-reported`. Require at least one cited export identifier; missing published aliases enter the review queue. Core filler still requires an unambiguous CISI base. All three Central Asian families enter the pool, so the external target is eighteen before overlaps. This clarification changes no completed selection or measurement. The census synthesis raw inputs are in its `main-2026-10-07-v6` directory. The Lothal table is in `data/six-hour/`; it will be referenced in place.

For unjoined museum records, create low-confidence candidate links only when normalized site and coarse carrier type agree and at most five selected carriers meet those conditions. This is a review search bucket with no accepted identity implication. Record its full denominator and evidence. Do not copy museum descriptions or map dates by stylistic prose. Parse numerical BCE ranges when explicitly given. Museum dimensions with unlabelled axes remain `dimension_1`, `dimension_2` and `dimension_3`; do not equate them to corpus horizontal/vertical/thickness by position. Preserve the census's existing dimension adjudications separately. A site-level census statement never fills an individual object's room, date or registration.
