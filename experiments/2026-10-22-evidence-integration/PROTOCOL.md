# Integrating held-source reviews

Date: 22 October 2026. Status: source review and data integration. Contributors: Codex (GPT-6, desktop collaboration harness), with separate face, lexical and candidate-record reviewers.

We will review the three fixed queues from the first execution block and write a new register version. The inputs are the 29 imaged divided faces without an accepted physical-order label, all 24 proposed Tamil forms plus a prespecified compound sample, and all 358 nonbaseline candidate inventory rows. The base register is `data/raw/2026-10-22-object-register/run-v2/`. Earlier source records, code and outputs remain unchanged.

## Independent face observations

The face reviewer and integrating contributor will inspect the same held images independently. Before consulting catalogue sign sequences or the other reader's decisions, each records visible spatial groups, approximate original-image bounds, preservation, alternative interpretations and confidence. The first pass is sealed by hash. The readers know these are previously examined objects with unresolved order; the review is therefore masked to current decisions and model predictions, not historically unexposed.

After both visual records are sealed, catalogue order and source captions may be used to map observed groups to the export's segments. Physical arrangement and reading traversal remain separate fields. Agreement requires compatible visible groups and a source-supported segment correspondence. A spatial grouping alone does not establish linguistic reading order. Disagreements, weak images and uncertain panel identity remain unresolved. These are AI source observations; expert acceptance is a separate review state.

Every one of the 29 faces receives a disposition, including cases with insufficient evidence. Source-derived geometry, photographs and detailed annotations remain local. Display transforms, source hashes and image sizes are recorded. We will also retain any image-identity correction supported by the held photographs or captions.

## Lexical review

The lexical contributor checks all 24 forms against held source entries and the source's proposed picture or rebus senses. Homographs remain separate entries; a supported written-form or sense relation is an attributed dictionary observation. Neither a dictionary entry nor a proposed picture identification authenticates an Indus meaning. A deterministic stratified compound sample is fixed before outcomes, with the three known Winslow failures kept in a separate diagnostic set. The contributor records source-supported analyses, uncertain cases and the limits of sample denominators.

Lexical review records form a separately versioned resource beside the object register. They will not be inserted as archaeological meanings of signs or objects. Any accepted form alias requires explicit source evidence, an entry identifier and an uncertainty record.

## Candidate identities and exposure

The candidate contributor first reviews existing metadata, matching evidence and access logs without opening candidate inscription images or descriptive source passages. Each row receives an identity disposition, alias or duplicate relations where supported, and an exposure assessment at the finest supported source-page and participant level. Scripted extraction and content displayed to a model remain distinct events. Missing logs and unmatched pages do not establish freshness.

Existing confirmed catalogue or registration links can connect a candidate record to the base register. Candidate relations and source rows are retained separately; matching sign sequences cannot merge physical objects. Every new source access is logged. A source-page access alone does not imply that every object on the page was inspected.

## Register integration and checks

Each reviewer owns a new dated package and one attempt record. This package owns the integrating code, independent second face record, combined report, and a new local output under `data/raw/2026-10-22-evidence-integration/`. The original register's object and face populations remain intact. New review assertions, candidate records, source locators and exposure events are added with stable IDs and source hashes. The build refuses existing outputs and records every change from its parent version.

Acceptance requires complete accounting for 29 faces, 24 lexical forms and 358 candidate rows; referential integrity; hashes of input and review records; explicit reasons for unresolved cases; and an unchanged base object and face population. Accepted physical-layout updates need the independent visual records and a documented adjudication. Candidate identity and exposure changes must cite the exact evidence used. The source review does not submit a segmentation model or reading, calculate a new rebus effect, or open confirmation through the shared bench.

We will verify the resulting register and update coverage in this package. Shared data inventory and generated knowledge files receive proposed updates for maintainer integration. The strongest possible conclusion is that specific source gaps have been closed and remaining uncertainty has been localized. The next deciding evidence is independent expert review and enough eligible objects for a frozen, calibrated test.
