# Building a public Indus evidence dataset

Proposed plan, 2 October 2026. The goal is a downloadable collection in which a researcher can follow an inscription back to its original object, photographs, source transcriptions and archaeological context. Existing corpora already supply much of the material. The work consists of obtaining covered inputs, resolving identities, preserving disagreements, adding missing observations and measuring the resulting coverage.

The number of surviving published objects limits the size of the factual corpus. A rich dataset can contain many image views, individual sign observations, source references and contextual measurements per object. Report their counts separately. Comparative material and generated examples have separate configurations and never enlarge the headline count of Indus objects.

## Scope

| Layer | Contents | Rule for inclusion |
|---|---|---|
| Indus objects | Seals, sealings, tablets, pottery, copper/bone objects, inscribed vessels, short records, fragments and exceptional directions. Uninscribed seals and other comparison objects can have their own explicit classes. | Registered or published object with a cited source and a stated authenticity/provenance status. |
| Images and geometry | Original photographs, drawings, impressions, all available faces, scale, image polarity, sign boxes/polygons, RTI or 3D when actually acquired. | Exact object/view link, source coordinates, transformations and asset reuse record. Unavailable views remain missing. |
| Transcriptions | Published readings from different inventories, source variants, editorial markers, gaps, lines and uncertainty sets. | Retain source inventory and version. Record who supplied an annotation and whether it has expert review. |
| Archaeological context | Findspot, unit, room/grid, layer, dates, material, size, manufacture, wear, attachment evidence, contents, associated quantities and inventories. | Attach source and measurement method to each observation. An interpretation-derived class cannot substitute for independently observed contents. |
| Related collections | Marked weights, regional token systems, cuneiform contact documents and later graffiti, with site and chronology. | Independent collection IDs and explicit relationship type. Visual similarity is a comparison, not an object-identity or historical-transmission join. |
| Scholarship and hypotheses | Bibliography, source-backed claims, competing interpretations, criticisms and proposed numerical or phonetic rules. | Attribution and status visible; proposed meanings remain distinct from observed signs. |
| Tools and evaluation | Importers, checks, preserved outputs, grouping rules, documented splits and synthetic controls. | Inputs and transformations pinned. Simulations carry their own supplied truth and generation record. |

## Stage 1 Source register and permissions

Start from the [landscape](landscape.json), the repository's [source inventory](../../knowledge/provenance/SOURCES.md) and [redistribution record](../../knowledge/provenance/REDISTRIBUTION.md). For each edition or collection, inventory what is accessible, already held, permission-covered and missing. Keep separate columns for public source availability and permission to redistribute its payload.

The principal source frame should include CISI volumes 1, 2, 3.1 and 3.2, IM77, Helsinki editions, Wells/Fuls material and subsequent published object catalogues. Check current inventories before freezing coverage. ICIT's 2023 totals are a historical comparator, not a present-day ceiling.

Prioritize the documented open editions and covered JSON material for the first public prototype. Prepare concrete access and permission requests for the maintainers of ICIT, RMRL and photographic archives when needed. Sending those requests requires the user's instruction; this plan sends none. Preserve a source pointer for material whose reuse remains unresolved.

Completion measure: every nominated source has an access result, version, scope and rights record, including sources that could not be obtained. Existing contributors and source authors remain credited.

## Stage 2 Common identifiers and a local pilot

Build a local 200-object pilot before attempting the entire corpus. Select objects across sites, object types, lengths, damage states and multiple faces. Include short Harappa records and sealing contexts so the earlier three-sign prediction filter does not determine dataset coverage. Freeze the pilot selection and rules before evaluating transcription quality.

Give each physical object an internal identifier. Store catalogue, excavation, museum and photographic numbers as separate source-qualified aliases. Keep uncertain object matches as candidate links; do not merge them silently. A copied seal text on two objects preserves two physical identities. A second photograph of one side preserves one object and two image witnesses.

Carry alternative source transcriptions as separate records. Preserve visual order, reading-order assumptions, face and line boundaries, damage extent and blank-space markers. Many-to-many sign correspondences remain candidate crosswalks. Do not use a source's interpretive transliteration table to define the factual sign inventory.

Completion measure: pilot entries pass the proposed identifier and provenance checks, and all conflicts are represented. The prototype remains local until its public payload has been reviewed.

## Stage 3 Image and transcription review

Attach available original views to the pilot and code their quality, scale, polarity and surface coverage. Use cropped views only when parent hashes and crop coordinates are retained. Apply corrected crop geometry from the earlier investigation to a fresh sample; retain the prior failed OCR endpoint. Generated sign drawings stay labelled graphic aids.

Seek two independent reviewers with relevant expertise for the pilot's object joins, line boundaries and disputed sign assignments. AI-produced drafts can prepare annotations, but their completion does not establish expert agreement. Record agreements, disagreements and unresolved cases rather than forcing a single answer.

Completion measure: review at least the proposed 200 objects, report the number of reviewed tokens and views, and report disagreement and error rates with denominators and uncertainty. Quality statements must identify the evaluated sites, classes and source versions. If expert review is unavailable, publish the annotations' actual status.

## Stage 4 Expand and add context

Extend the successful import paths across the source register. Count every source row's disposition: imported, matched to an existing object, unresolved, unavailable or excluded with a reason. Preserve short, damaged and exceptional records with quality flags. Do not require a record to pass one predictor's eligibility rules to exist in the dataset.

Add the independently observed context most useful for testing function: associated counts, measured amounts, vessel contents, complete inventories, attachments and production groups. Reuse our existing Harappa, Lothal, Kanmer and regional source frames, including the later [source-recovery corrections](../../knowledge/directions/source-recovery-2026-10-02.md). A historical mass disagreement remains two attributed measurements until adjudicated.

Completion measure: a source-by-source coverage ledger and a field-completeness report, with no additive claims across overlapping corpora. New archaeological quantities must be traceable to a particular object or assemblage.

## Stage 5 Compare quality

The targets below are proposed acceptance rules. They describe how a future release will be assessed and are not claims about the current collection.

| Measure | Proposed requirement | Comparison to preserve |
|---|---|---|
| Source coverage | Account for 100% of nominated rows in each acquired source, including unresolved and excluded rows. | Exact editions, dates and count conventions for every comparator. |
| Physical identity | All accepted object merges have source evidence; candidate merges stay unresolved. | Added distinct verified objects on a matched source frame. |
| Provenance | Every included observation has a source locator and method; own measurements have a protocol. | Number of matched objects gaining traceable fields. |
| Public reuse | Every redistributed asset has its own documented basis and notices; unresolved payload stays out. | Downloadable, permission-covered objects/views, not merely linked images. |
| Transcription quality | Independently review the 200-object pilot and report token-level results and unresolved cases. | Review existing transcriptions on the same objects using the same rules. |
| Context coverage | Report exact counts for source-backed dates, excavation joins, measurements and independently observed quantities. | Field gains and errors within the matched object set. |
| Computation | No broken internal identifiers; output hashes, transformations and reconstruction commands retained. | A fresh local rebuild reproduces the declared package. |
| Evaluation independence | Split by physical links and declare repeated-text/stamp dependencies for each task. | Explain where identity, copied strings or shared source images connect records. |

Describe the release as better on the measurements it actually improves. A global claim that it exceeds every existing collection requires access to the strongest relevant comparator and a reviewed comparison. If ICIT internals remain unavailable, state that limitation and compare only its documented features and accessible records.

## Stage 6 Package for public use

Keep JSONL tables as inspectable records, Parquet copies for analysis and a SQLite export for joined queries. Supply a data dictionary, dataset card, source and rights tables, attribution notices, coverage report, changelog and package hashes. The [schema](SCHEMA.md) is a specification; these exports are future work.

Make separate configurations for archaeological core data, comparative collections, hypotheses and synthetic controls. Provide image bytes only when covered. Reference-only assets should have source links and access instructions; a gated hosting setting does not establish a missing redistribution basis.

Use [Hugging Face dataset repositories](https://huggingface.co/docs/hub/datasets-overview) for discovery, downloads and compatible table views. Use [Zenodo records](https://help.zenodo.org/docs/deposit/about-records/) for a cited release with a DOI, retaining separate [versions](https://help.zenodo.org/docs/deposit/manage-versions/). Repository code remains manually run. Choose licenses for our own code and annotations separately from inherited assets.

Publication follows the source and payload review, with the account, destination, title, authorship and included assets specified. No account, draft record, website, upload or automation has been created by this planning run.
