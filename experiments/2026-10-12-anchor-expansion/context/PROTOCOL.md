# Complete-inscription context diagnostics

October 12, 2026. This exploratory diagnostic reuses the already exposed Lipi register. The candidate families are being fixed by the visual contributor before their role results are integrated. This file fixes the frame, split and role arithmetic before the new context tables are calculated. No dictionary residual search or new permutation sampling is included.

The input register is `data/normalized/lipi_observed_faces.jsonl`, SHA256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`. Eligibility requires the existing clean reading-order single-line flag, a complete observed face, no unknown or blank token, no recorded damage/uncertainty and at least two codes. The eligible record identifiers and strings must match `data/normalized/lipi_clean_rtl_singleline.jsonl`, SHA256 `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`. Reading order follows `signs_reading_rtl` without an additional reversal. Every calculation retains the whole sequence.

## Identity and deterministic stability split

Construct physical closure across the complete 5,680-record register using current family identifiers, declared artifact aliases and simple CISI object bases. A simple CISI base accepts a trailing side letter, following the existing administrative audit. Record unresolved nonblank references. Then connect physical components through every identical nonempty reading-order string in the complete register, including placeholder-bearing strings as a conservative link. A graph census without placeholder-string links is a sensitivity, not a replacement split.

Name each final closure component by the SHA256 of its sorted record-ID list. The split hash is SHA256 of the UTF-8 string `indus-anchor-expansion-2026-10-12-context-v1|<component_id>`. Assign the whole component to discovery when that digest, interpreted as a 256-bit integer, is below 70% of the 256-bit range; otherwise assign it to transfer. The 70/30 fraction concerns components and does not force a 70/30 text or token balance. Record actual loads, largest components and zero shared physical or string identities across the split. These partitions measure stability on known data.

The primary summary deduplicates complete strings after closure. Additional frames retain strings of length at least three, the discovery and transfer partitions, and one longest eligible face per physical component, with smallest record ID breaking ties. The representative-object frame can reintroduce identical strings from separate physical components. Its denominator remains distinct from the unique-string frame.

## Fixed role definitions and expectations

Each candidate occurrence is scored in its intact inscription. Record matching and contradicting tokens, inscriptions with every candidate occurrence matching, mixed inscriptions and inscriptions with any contradiction. Empty samples and observed zero matches are separate statuses. The roles are fixed:

| Role | Matching occurrence |
|---|---|
| closing | Last, or directly before terminal W400/W740 |
| counted_entity | Immediately after W001–W005 |
| nonfinal_entity | Any position except last |
| internal_connector | Strictly between the first and last positions |
| opening | First |
| unconstrained | No correctness or supporting-direction score |

For a code occurring n times in a length-L string, the conditional bag-shuffle expected matching counts are n/L for opening, n(L−1)/L for nonfinal, n(L−2)/L for internal, n(S−I[c∈strokes])/L for counted entity, and n/L + n(C−I[c∈closers])/[L(L−1)] for closing. S is the number of W001–W005 tokens; C counts W400/W740 tokens. Expectations add across complete strings. Family expectations sum their code contributions. No Monte Carlo probability is inferred from these means.

Every fixed role and every declared family role alternative remains in the outputs. Supporting direction means observed matching tokens exceed the analytic expectation in both nonempty split frames. Context-supported prioritization additionally needs a documented picture, a selected anchor and at least five distinct complete strings. Keep individual-code support and contradictions even when a pooled family passes. Unconstrained families have no such grade.

Report W031–W035 and dotted W060 predecessor counts separately from the narrow W001–W005 set. These are declared conditional graphic groups, not authenticated quantities. Anchor co-occurrence uses every run-v6 code with a selected sense record and retains its prior tier. It counts shared complete strings, not an asserted compound or translation.

## Templates, local records and verification

Exact substitution templates replace one token while holding the whole remaining string, length and slot fixed. Report template counts, lengths, short versus longer templates and alternative-code counts publicly. Store complete templates, all source records, one-based occurrence indices, split identities, contradictions and complete-example candidates under the ignored local companion directory.

Public outputs contain authored methods, aggregates and selected source-ID metadata. They contain no full corpus strings or exhaustive residual templates. The final `summary.json` exposes all 713 `code_rows` and the frozen visual map's `family_rows`. Generic outputs and later family integration receive separate versioned directories; earlier endpoints remain unchanged.

Verification compares the eligible frame with the pinned clean input, reconstructs existing positional results, checks full-register closure and split isolation, and checks actual recorded exact-substitution witnesses with an independent one-difference comparison. Code, protocol, inputs, the frozen visual map and both public/local outputs receive hashes. No implementation-mirror test suite is added.
