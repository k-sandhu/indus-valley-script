# Living towns and Indus-period occupation: protocol

Date: 26 October 2026. Status class: source-review. Contributor: GPT-6 in the Codex API workspace, exact runtime build unavailable. Owned directory: `experiments/2026-10-26-indus-living-atlas/living-towns/`. We apply the repository's orient, start-study, add-data and write-retrospective workflows.

We will assemble a source-linked register of 16 to 20 candidates for long-lived settlement in South Asia, including living towns, modern settlements beside excavated ancient places and abandoned Indus contrasts. The question is which places have evidence of habitation during the Indus period, and which have a dated sequence connecting that habitation to a living town. This is a purposive source review, not a ranking of every South Asian town by age.

## Prior evidence and new contribution

We read AGENTS.md, README.md, knowledge/INDEX.md, knowledge/DATA.md, LOCAL_STORAGE.md, CONTRIBUTING.md, the registry, the editorial rules, redistribution rules, REUSE.md and LICENSE. The October 11 settlement prospection retrospective identified geographic and chronological joins as recurring failure points. The October 24 town-axis register preserves site phases but does not compare them with modern civic settlement. The October 25 continuity package distinguishes practical inheritance from a demonstrated lineage. We will add an explicit modern-place-to-excavated-place relation, evidence dates and continuity claims with their source scope.

The data gap is a joined settlement history: a site's earliest phase, nearby early sites, civic foundation traditions and a modern municipality are often assigned one date in popular accounts. We will preserve these as separate assertions. We will not alter inherited records or generated knowledge files.

## Selection and coding, before the new source search

The initial candidate list is Peshawar, Multan, Taxila, Harappa, Varanasi, Ujjain, Mathura, Patna, Rajgir, Srinagar with Burzahom as the nearby comparison, Rupnagar, Vadnagar, Lumbini, Tilaurakot or Kapilavastu, Anuradhapura and Mahasthangarh with Bogra as the nearby modern city. Dholavira and Mohenjo-daro provide abandoned-city contrasts. A candidate may remain undated where the retrieved primary record does not support a date.

We will use primary excavation reports, peer-reviewed reports by the excavators and official archaeology or UNESCO records. Tourist lists and mythological foundation dates will not supply archaeological dates. UNESCO nomination descriptions remain attributed institutional syntheses, and will not be treated as independent excavations. Each record will distinguish earliest evidence at the actual place, earlier evidence in the region, urban foundation, known gaps and modern civic identity.

BCE dates are positive integers with `earliest >= latest`; an approximate century or broad period is retained as a range. We will record overlap with Mature Indus 2600–1900 BCE and Late Harappan comparison interval 1900–1300 BCE separately. An old sample does not fill the later interval. Indus-period overlap denotes contemporaneity and does not assign an archaeological culture. The statuses will be `documented-sequence-with-hiatus`, `long-sequence-continuity-unproven`, `continuity-asserted-not-demonstrated`, `nearby-modern-settlement`, `later-origin-no-indus-overlap`, `archaeological-or-sacred-place-not-town-continuity`, `abandoned-ancient-city` or `unresolved`.

A statement of uninterrupted occupation requires source-described occupation through every major intervening period at the same bounded place. We will record the source's actual scope and any unexamined interval. Modern coordinates are approximate map anchors, with their precision and basis stated; they do not establish ancient settlement boundaries. We will report no universal absence claim if the search finds no verified Indus-to-present sequence.

## Outputs, checks and stopping rule

Stop after the initial candidates have been source-checked, each has an evidence status and explicit gaps, and the register validates. Deliver towns.json with a schema, sources.json with title, author, year, URL, access depth, locator and rights; a readable table and report; DATA-UPDATE.md; a retrospective; validation code and a versioned JSON result; and one owned attempt entry. New raw source files, if needed, go only to `D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/living-towns/`, reached through `data/raw/`; record both paths, bytes and SHA-256. D: and the checkout junction were checked before this protocol.

The validator will check required fields, unique IDs, source references, geographic bounds, date intervals, period overlap logic, explicit source scope, and the absence of a verified continuity claim without supporting sequence evidence. We will review the prose and run the knowledge checks. No reading, sign key, meaning map, restoration, segmentation or script conjecture is submitted, so no bench scorer measures this endpoint. We read bench/README.md; its five scientific tasks do not evaluate a settlement source register. No confirmation half or spent statistic family will be opened.

End the report with the strongest supported reading and a dated-stratigraphy test that would decide it. Validation confirms the record's internal consistency, not archaeological proof or peer review.
