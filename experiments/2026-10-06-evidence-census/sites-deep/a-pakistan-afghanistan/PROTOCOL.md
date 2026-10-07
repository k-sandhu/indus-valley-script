# Protocol: Pakistan and Afghanistan Indus-site census

Date: 2026-10-06. Status: Proposed before site-specific source searches and count extraction.

## Question and scope

For every named site in the batch and every local-corpus site label in the Lower Indus, Upper Indus, and Inter-Riverine regions located in Pakistan, what excavation history, publication record, inscribed-object counts, context metadata, later finds, present holding and digital reuse evidence can be recovered from live web sources? Add other sites in these same geographic regions only when a source reports an inscribed Indus object.

## Inputs

The prior broad census at `experiments/2026-10-06-evidence-census/sites-and-publications/` provides an exploratory 89-label register, source records, the ICIT 2023 summary and three site-count examples. Reuse its correct records and links; it did not assess most fields, and its counts are not treated as complete. The local starting values come from `experiments/2026-10-06-research-program/local-site-coverage.json`; they count Lipi faces, object families and distinct CISI identifiers by literal site label, not independently verified physical objects. CISI coverage is checked against the cited CISI volumes and page ranges where accessible.

## Method

For each site, record at least three distinct live-web queries with date, search place, query and returned lead or failure. Open at least one primary or substantial secondary source. Prefer excavation monographs, primary reports, institutional catalogues and CISI pages. Preserve source titles, authors, years, venue, stable URL and exact page, figure or catalogue locator. State whether the source was opened or only seen in a snippet. Keep objects, faces, texts, impressions and illustrations as distinct count units. Do not sum overlapping publications. Count disagreements remain side by side with source-specific dates and definitions.

Record coordinates and administrative location with a source. For metadata availability, use yes, partial or no only for the inspected publication and cite the locator; distinguish fields not assessed. Compare each local corpus count and CISI prefix maximum with published site lists or counts; do not infer completeness from a sequence maximum alone. Record later claims with their documentation level and distinguish excavated finds from reports, news or unverified leads. Note present holdings and digital availability/reuse terms only when a source states them.

## Comparisons and selection

Reuse the previous census's Harappa tablet, Lothal sealing, Kanmer sealing, Farmana and Dholavira records when applicable, preserving their stated count bases. Compare count bases before comparing magnitudes. Treat ICIT's reported object, text, sign-occurrence and image totals as different measures. Include additional same-region sites only with an explicit source trail for an inscribed Indus object. Keep unresolved publication ranges and unavailable rights statements explicit.

## Negative results

A negative result is limited to the recorded query set and sources opened. Record the actual searches and access failures; absence from a search result or local corpus is not evidence that the site has no finds. A count without a reconciled inventory is a source-reported value, not an independently verified total. If post-CISI finds cannot be dated or tied to an excavation report, label the evidence accordingly.

## Planned outputs

Produce one row per in-scope site in JSON and CSV, a source ledger, a search ledger, an aggregate report and a proposed registry entry. Claims must resolve to a source ID plus exact source location or an output file and field. Raw downloaded pages and third-party material remain under the package's local raw directory.

## Amendment: 2026-10-07, completion after coordinator review

Status: Exploratory. The coordinator found that the first pass left publication, coordinate, campaign, count and metadata checks incomplete. Before editing, all 25 top-level first-pass files were copied byte for byte into `first-pass/`. The revised outputs retain the original observations and add source inspection, new queries and explicit field-level failure records. The archive remains the historical witness, including its encoding defects.

Run at least three new distinct live queries per in-scope site, open a primary or substantial secondary source for each, and retain exact page or catalogue locators. A bibliographic landing page counts as bibliographic access only. For an unavailable full source, record the access route, failure and affected fields. Unknown values must point to the targeted queries that failed to recover them. Inspect CISI, Mahadevan 1977 and excavation publications wherever accessible; a later corpus-derived site summary is a separate count basis.

Each revised row will distinguish a verified final excavation report from a preliminary report or catalogue. Post-CISI totals will count only rows with a dated, documented inscribed find after that site's latest inspected CISI coverage. Leads and catalogue republications remain recorded separately. Metadata availability uses yes, partial or no with the inspected source location; inaccessible source fields are recorded as unresolved with failure evidence, rather than inferred from a book title.

Write active files as UTF-8. Repair reversible encoding damage mechanically and check irrecoverable characters against source titles. Recompute query, source, publication, post-CISI and missing-field totals from the revised rows. Preserve physical-object, face, text, impression and mark denominators in comparisons. The first-pass outcome is not a frozen evaluation; these revisions respond to its observed gaps.

### Further amendment: 2026-10-07, country and publication classification

The local aggregate places Miri Qalat, Sibri, Ornach area and Murda Sang under Iranian Plateau. Their geographical locations or reported provenances are in Pakistan. Inspect these neighbouring labels and include a row when an opened source or the local corpus records a marked or inscribed object, retaining unresolved site identity and script classification in the row. This expands the site list after inspecting the local regional categories; the affected rows and totals are Exploratory. Run at least three distinct live searches for each added label and record the source that motivated inclusion.

Separate final excavation monographs and final exploration publications from identified seasonal or short reports whose comprehensive status remains unresolved. The latter include Gumla, Mehrgarh, Naru-Waro-dharo, Rehman Dheri and Sarai Khola in the inspected sources. Report the categories separately and keep the original bibliographic observations. Copy local figures directly from the coordinator aggregate after spelling joins, rather than accepting a missing match as zero. A requested alias remains a row but shares a catalogue locality identifier where the catalogue explicitly joins it.
