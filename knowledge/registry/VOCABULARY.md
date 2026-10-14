# Controlled vocabularies

Use one area per item and one status class per attempt or finding. Preserve an attempt’s original free-text `status`.

## Areas

- `corpus`: Transcriptions, sign inventories, sampling frames and the representation of inscribed records.
- `data`: Acquisition, metadata, joins and completeness of object, surface, image and source records.
- `structure`: Order, recurrence, boundaries, prediction and distributions of signs or units.
- `seals`: Seal legends, sealings, stamps, motifs and the physical use of seals.
- `tablets`: Inscribed tablets, their complete faces, production series and object relationships.
- `numerals`: Proposed numerical notation, quantities, metrology and arithmetic constraints.
- `images`: Photographs, drawings, graphic features, recognition and visual annotation.
- `meaning`: Semantic and functional hypotheses and their independent tests.
- `language`: Phonetic keys, lexical comparisons and proposed linguistic identifications.
- `archaeology`: Find contexts, strata, chronology, material evidence and settlement observations.
- `comparative`: Known writing systems, cultural transmission and cross-society comparisons.
- `methods`: Evaluation, inference, mathematical controls and reusable research procedures.

## Status classes

The seven definitions below are copied exactly from [INDEX.md](../INDEX.md). Their field values are `proposed`, `synthetic`, `exploratory`, `frozen-evaluation`, `failed`, `superseded` and `verified-computation`.

Each attempt and finding has one status class. An endpoint is the result an attempt was designed to report; a reference is the baseline or chance model it is compared with.

- Proposed: not run.
- Synthetic: simulated or constructed data.
- Exploratory: a result or refinement chosen after earlier outcomes were seen.
- Frozen evaluation: the reference, data split and method were fixed before that particular outcome, not necessarily before the whole project.
- Failed: the stated approach did not pass its test or beat its reference.
- Superseded: a documented defect or design change prevents use of the endpoint as the current result.
- Verified computation: numerical and source-integrity checks passed; this does not establish archaeological meaning or peer review.

Two further classes are used. Source review (`source-review`) is an audit, survey, census or literature review whose output is a source record, not a computation. Record (`record`) is a coordination, release or preservation record.

For mixed work, choose the class of the main endpoint and explain the choice. The [status mapping](STATUS-MAPPING.md) records every existing decision. A checked simulation stays `synthetic`; a failed frozen evaluation can keep `frozen-evaluation` when the main fact to preserve is its prespecified endpoint.

## Questions and conjectures

Question statuses: `open`, `claimed`, `done`, `dropped`. Task kinds: `analysis`, `data-acquisition`, `metadata`, `verification`, `literature`, `fieldwork`, `tooling`. Priority is an integer from 1 (highest) to 5. Data access: `none-needed`, `public`, `local-only`, `acquire`, `fieldwork`. Compute: `minutes`, `hours`, `days`. Difficulty: `starter`, `standard`, `expert`.

Conjecture statuses: `open`, `strengthened`, `weakened`, `dead`. Risk: `safe`, `stretch`, `long-shot`. Credence is a probability from 0 to 1; follow [the conjecture rules](../conjectures/README.md).

Verification tiers describe contributor review separately from status class: `submitted`, `reproduced`, `reviewed`, `accepted`.

## Paths and frontmatter

Frontmatter paths in `evidence` and `sources` are relative to repository root. To point at one field of a JSON evidence file, append a JSON Pointer such as `#/field/subfield`; write a slash inside a field name as `~1`. Body links are relative to the Markdown file. Use quoted scalars, flow lists, block lists of scalars or block lists of flow mappings. The command-line tool keeps unsupported structures as raw strings and reports invalid required fields.
