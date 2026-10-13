# Complete-context output schema

The public summaries retain complete-inscription counts and analytic expectations. The local companion retains the actual reading-order strings and positions needed for full-record inspection. Both depend on the pinned Lipi derivative and have matching run labels and hashes.

## Public files

`run-vN/input-accounting.json` records the complete register, physical closure, object/text closure, eligibility exclusions, distinct strings, code inventory, actual split loads and the placeholder-link graph sensitivity. `run-vN/input-manifest.json` records the code, protocols and input hashes before calculation. `run-vN/output-manifest.json` identifies public and ignored local outputs by hash.

`run-vN/summary.json` contains `code_rows` for all 713 inventory codes. Each row has `code`, `starting_tier`, `starting_meaning`, `frames` and `substitutions`. The frames are `all_texts`, `length_ge3`, `discovery`, `transfer` and `one_face_per_physical_object`. Each frame gives its entire population size, containing-inscription count, token count, physical/closure support, length distribution, position counts/moments, all fixed role scores, declared stroke predecessors and fixed run-v6 anchor co-occurrences.

Each constrained `role_scores` entry includes matching and contradicting tokens, their analytic conditional expectation, matching fraction, observed minus expected, supporting direction, inscriptions where every occurrence matches, inscriptions with any contradiction and mixed inscriptions. `empty_sample` distinguishes absent evidence; `observed_zero_matches` records actual occurrences with no matches. `unconstrained` has no correctness or supporting-direction score. A numerical tolerance of 1e−12 prevents floating-point equality from creating supporting direction.

`substitutions` gives complete-template counts, two-sign and length-at-least-three counts, the length distribution and alternative-code counts. The remaining complete inscription is held fixed. Source templates themselves are local.

The frozen visual map's `family_rows` records each family's identity, members and declared primary/alternative roles. It contains pooled frame summaries, member-specific summaries for all five frames, exact-template aggregates and `declared_role_stability`. The latter reports the five-string rule, empty split samples and supporting direction in each split. It does not select the most favourable role. Picture and Sanskrit-anchor qualification remain the integration owner's review. The current visual map declares one role string per family; the adapter also accepts explicit role lists without choosing among them.

`verification.json` records pinned-frame reproduction, whole-register split isolation and checks of actual source records and exact one-difference templates. Its witness fields contain source identifiers and lengths, not complete strings. The context-level `summary.json` is an identical copy of the separately frozen run-v2 family-integrated endpoint; the generic run-v1 remains available.

## Ignored local companion

The companion is `data/raw/2026-10-12-anchor-expansion/context/run-vN/`. Git's existing data exclusions cover it. These files must not be included in the public release.

`complete-records.json` has `records` for every eligible face, including repeated strings. A record contains `record_id`, `source_id`, the original `object_family_id`, `physical_component_id`, final object/text `component_id`, `split`, CISI/site/region/object metadata, source direction and orientation basis, full length and `complete_codes_reading_rtl`.

`code-occurrences.json` has all 713 code rows with an `occurrences` list. Every occurrence gives source/record identifiers, both component identities, split, one-based position, whole-record length and fixed `role_matches`. These lists retain duplicate faces. Public primary summaries instead weight each distinct string once.

`complete-templates.json` has each entire placeholder template, its one-based slot and every alternative. An alternative carries its code, representative source record/CISI, split/component and complete reading-order sequence. `complete-example-candidates.json` contains one representative per distinct string, every eligible source record ID for that string and, after family integration, occurrence indices and contradictions for every declared family role. Candidate selection retains contradicting contexts.

`closure-register.json` retains all 5,680 original record IDs with physical and object/text component identities, split, eligibility/exclusion status and unresolved source references. This allows a local reviewer to trace closure through faces excluded from the analytical population.

The split salt and all role definitions are fixed in [the context protocol](PROTOCOL.md). Discovery/transfer labels describe stability on previously exposed material. Source identifiers, copied strings, physical groups and formula groups have different denominators throughout these files.
