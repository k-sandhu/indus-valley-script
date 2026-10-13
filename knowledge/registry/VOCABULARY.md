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

**Proposed** means not run. **Synthetic** means simulated or constructed data. **Exploratory** means a result or refinement selected after prior outcomes. **Frozen evaluation** means the specified reference/split/method was held fixed before that particular outcome, not necessarily before the entire research project. **Failed** means the stated approach did not pass its comparator/test. **Superseded** means a documented defect or design change prevents using that endpoint as the current result. **Verified computation** means numerical/source-integrity checks passed; it does not mean archaeological semantics or peer review are established.

**Source review** (`source-review`) means an audit, survey, census or literature review whose output is a source record rather than a computation. **Record** (`record`) means a coordination, release or preservation record.

For mixed work choose the class of the primary endpoint and explain that choice. The [status mapping](STATUS-MAPPING.md) records every existing decision. A checked simulation remains `synthetic`; a failed frozen evaluation can retain `frozen-evaluation` when preservation of the prespecified endpoint is the primary fact.

## Questions and conjectures

Question statuses: `open`, `claimed`, `done`, `dropped`. Task kinds: `analysis`, `data-acquisition`, `metadata`, `verification`, `literature`, `fieldwork`, `tooling`. Priority is an integer from 1 (highest) to 5. Data access: `none-needed`, `public`, `local-only`, `acquire`, `fieldwork`. Compute: `minutes`, `hours`, `days`. Difficulty: `starter`, `standard`, `expert`.

Conjecture statuses: `open`, `strengthened`, `weakened`, `dead`. Risk: `safe`, `stretch`, `long-shot`. Credence is a probability from 0 to 1; follow [the conjecture rules](../conjectures/README.md).

Verification tiers describe contributor review separately from status class: `submitted`, `reproduced`, `reviewed`, `accepted`.

## Paths and frontmatter

Frontmatter paths in `evidence` and `sources` are relative to repository root. Append `#/field/subfield` to JSON evidence to name a JSON Pointer; escape slash as `~1` in a field name. Body links are relative to the Markdown file. Use quoted scalars, flow lists, block lists of scalars or block lists of flow mappings. The CLI retains unsupported structures as raw strings and reports invalid required fields.
