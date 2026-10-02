# Six-hour investigation record

The requested session began at 01:15:09 EDT on 2 October 2026. Its minimum completion time is 07:15:09 EDT. The [session record](session.json) retains UTC and local times. Work is still active; the entries below record completed observations as they become available.

## Completed comparisons

The conventional first-order [Markov comparison](markov-baseline/README.md) uses exactly the earlier 8,009 held-out known-slot queries and their connected-component folds. Its top-one accuracy is 34.59%, compared with 33.81% for the position-and-neighbour model. Its top-five score and bucketed log loss also improve. The paper now includes this comparator, its parameter selection and paired intervals. The independent review checks every saved prediction.

The [mechanism study](markov-ablation/README.md) removes learned start and end factors and shuffles training order while retaining declared boundaries. The end factor accounts for a measurable final-slot gain. Preserving endpoints while scrambling interiors retains part of the overall predictive score; the unmodified order supplies further information. The study retains every shuffled replicate and per-position result.

The [reference-uncertainty study](reference-uncertainty/FINDINGS.md) enumerates eight-symbol mappings in 2,592 synthetic trials across 24 new systems. Integrating reference parameters reduces confident errors in unchanged administrative systems. Changing the record process and supplying one erroneous identity leaves saved failures. Independent sequential scores match all 216 reviewed conditions.

The [identity-acquisition study](active-identities/FINDINGS.md) measures observation cost and confidence stopping in 48 new systems. Entropy selection reduces recovery cost and increases wrong stopping decisions in several changed-process conditions. A separate [reserved-verification study](reserved-verification/FINDINGS.md) freezes each proposal and checks its predictions on additional identities. Its 4,032 audit records and exact subset probabilities distinguish efficient error detection from a model-independent sampling bound.

The [physical-membership experiment](physical-information/README.md) uses exact linear relations from complete and incomplete containers. Complete membership plus one counted object identifies all six quantities in 24/24 simulated collections. Incomplete membership leaves seven alternative positive integer assignments even after a count. Preparing separate solver inputs exposed a badge-versus-object measurement error; both the original and corrected endpoints are preserved.

The [physical-acquisition study](physical-acquisition/README.md) now has 360 main policy records and 96 refinement records. Information/rank identifies absolute quantities in 23/24 complete and 22/24 incomplete worlds. A new interval-overlap policy identifies six exact vectors on fresh interval worlds where each original policy identifies none. Exact certificates and positive ambiguity witnesses preserve the accepted, wrong and unresolved cases.

## Source and sample audits

The [metadata audit](context-audit/README.md) distinguishes excavation observations from placeholders and measures how published physical-use objects enter the statistical corpus. Only two of 69 source-defined Harappa objects enter the main length-at-least-three population. The [object-frame extension](harappa-object-frame/README.md) now joins 24 source-illustrated targets, restoring excavation-unit/item keys for all 22 copied tablets. Nineteen readable lower-face pairs occupy all eight declared arrangement classes. Its 97 integrity, accounting and replay checks pass.

The [Lothal branch](lothal-physical-use/README.md) acquired the full 2005 Frenez–Tosi chapter and inspected its table and figures. Two independent pixel transcriptions agree on all 465 compared cells: 93 physical objects and 133 seal impressions; the prose reports 130. Its context totals also differ. The refined corpus join contains 68 objects and 29 objects in the main clean-sequence population. These form nine strings, with 21 objects in two groups. Table transcription and detailed joins remain local; aggregate audits and source coordinates are kept here. The independent computation and witness checks pass.

## Active work

The numerical branch is calibrating the full nested statistic under declared known sampling laws. It includes exact small conditional spaces and larger Monte Carlo studies, with duplicate copies, nonidentical object faces and uniqueness-conditioned populations. The physical source branch has begun a documented khipu comparison. The geometry branch is modelling contact between flat stamps and curved clay. Each new analysis has its own protocol and endpoint.

## Repository preservation

The private repository's first complete package was pushed as commit `4c941af5d39b1b88c1c150efcb793be26517ecf1`. It contains the manuscript, reusable methods, experiment registry, source provenance and retrospectives. GitHub Actions is disabled. Further completed branches will be reviewed and pushed during this session.
