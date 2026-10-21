# FISH-CONTEXT-2026-10-20: fish signs, compound labels and object context

Recorded before the discovery half was opened, 20 October 2026. Authors: Codex (GPT-6, Codex desktop harness). Owned directory: `experiments/2026-10-20-fish-context/`. Detailed source-derived data belong in `data/raw/2026-10-20-fish-context/`.

## Question and scope

We test whether the fish family forms ordered compound labels, whether stroke groups before fish behave like variable counts or fixed expressions, and whether fish signs favour seal legends after site and text length are controlled. We compare those observations with Parpola's celestial-name reading and economic, institutional and personal-name readings. These are tests of graphic structure and function. A sound value requires a separate correspondence.

We also assemble every available fish-bearing object, its faces, images and source-qualified context. The register records missing fields and competing assertions. Catalogue rows and photographs of the same object supply different observations about one object.

## Prior attempts and the changed input

The Bonta review of 8–9 October found fish adjacency above its shuffle reference; we reuse that result and do not count another adjacency test as a discovery. NUMERAL-BEHAVIOUR-2026-10-12 measured stroke fixity across the whole sign inventory; its retry condition includes site- and period-stratified contexts. C-0002's broad meaning map failed. The 13–14 October Mackay–Marshall and CISI basic-data packages now supply source-located excavation, museum and concordance assertions. The present contribution links those records to the complete fish population and compares specified models on a discovery/confirmation split.

Before analysis we read AGENTS.md, README.md, knowledge/INDEX.md, knowledge/DATA.md, the experiment registry, corpus and Bonta retrospectives, the numeral report, bench/README.md, bench/spent.json, the shots design, CONTRIBUTING.md, REUSE.md, LICENSE and the redistribution and writing rules. Git status was clean. A read-only search found no open GitHub issue with fish in its indexed text. This directly assigned study creates its own attempt and conjecture records.

## Inputs and inclusion

The main input is the pinned observational `data/normalized/lipi_observed_faces.jsonl`, SHA256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`. Translation, proposed Sanskrit values and Wells's interpretive text classes never enter the analysis.

The fish family is base B220 in the first coder's `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv`. The second coder supplies an intersection sensitivity; neither code list is adjusted to improve results. The plain fish is Wells 220. Stroke values come from B001 and B031, retaining their family and graphic confidence; analyses restricted to unmodified high-confidence strokes are mandatory. A shape family is an annotation, not an established homophone class.

The object register retains all fish-bearing faces, including damaged and uncertain-order ones. Numerical and order scores use complete, clean, right-to-left, single-line faces. Duplicate full texts are collapsed within the scoring half after aliases and identical texts have been grouped by the shared shots loader. Seals are the primary population for inferential tests of compound order and numeral models; all carriers are a declared sensitivity. At most one equal-weight vote per dependency component enters an exact sign test. Traces and detailed sequences remain local.

## Discovery and confirmation

Use `python -m bench shots` with seed `2026-10-20-fish-context`. One registered participant contains all predictions. Before confirmation, freeze its predictions, learned models, fish map and all scoring code. Every read uses `bench.shots.load_half`. Run the synthetic shots and meaning-map modes before real scoring.

The source corpus has extensive prior exposure, including fish adjacency, numeral fixity and the site, seal-size and motif statistic families in bench/spent.json. A new partition does not restore freshness. This study records its real-data comparisons as frozen evaluation on historically examined material, with exploratory source and interpretation work. Use `allow_spent=True` where required and make no claim of an independent new corpus. The new excavation joins improve source traceability; where their values already occur in Lipi they add no independent context observation.

## Three comparisons

**A, ordered compounds.** Learn one total order of at most seven fish codes with at least five discovery occurrences. Exhaustively choose the permutation that agrees with the most adjacent unequal fish pairs on discovery seals; ties use numeric code order. On confirmation seals count each component as positive if more of its pairs follow than oppose that frozen order, negative for the reverse and tied otherwise. The null reverses each component's direction with probability one half. Pass requires at least 15 untied components, at least 75% positive votes and a one-sided exact binomial p at most 0.0166667. Report pair counts, components, reversals and the common-code sensitivity. This tests ordered composition beyond the already known adjacency excess.

**B, fixed expressions versus quantities.** Compare predictive probabilities for the value of the stroke immediately before a fish. Q is a variable-quantity reference fitted to non-fish stroke–item pairs, by object genre and stroke family with Dirichlet half-counts. L adds fish-code-specific discovery counts with eight reference pseudo-observations. Both are normalized on the fixed values 1–10, 12 and 24. C is a narrow astronomical model for plain-fish seals: 90% probability on 3, 6 and 7 (with half-count smoothing of their discovery frequencies), and 10% spread uniformly across the other allowed values. We report all predictive log scores. The prespecified test is L against Q, with one vote from each component's mean log-score difference. Pass requires at least 15 untied components, a positive mean gain, every leave-one-component-out mean positive and one-sided exact binomial p at most 0.0166667. C is a deliberately risky reading: it passes only with at least 20 components, a lower 95% Wilson bound of 0.8 for its canonical-value share, a positive mean gain over Q and L, and no reversal under strict stroke coding. A failure addresses this narrow model; it does not reject every celestial use of fish.

**C, seal-legend preference.** Calibrate the observed fish family against frequency- and position-matched rearrangements of its class labels using `python -m bench meaning-map`. The response is seal versus other carrier, residualized by site and text-length bin. Bands and position bins are built on discovery. Use at least 9,999 rearrangements, the leave-one-component-out influence rule and a minimum of eight components per sign. The pass threshold is p at most 0.0166667 for the single directional contrast. Record discovery reliability, re-split variance and power at effects 0, 0.25, 0.5 and 1 before freezing. This population has historical carrier and site exposure; the outcome measures a carrier association, not an authenticated name or deity.

The three comparisons share objects and are not independent confirmations. A joint credence rule keeps a functional compound-label proposal at 0.35 initially, raises it to 0.55 if A and B both pass, to 0.45 if one passes, and lowers it to 0.20 if both fail. C changes the reading's carrier scope and can add at most 0.05; it cannot establish pronunciation. The narrow astronomical proposal starts at 0.15, rises to 0.30 only if its entire pass rule holds and falls to 0.05 on failure. A lexical mīn or particular divine-name reading receives no numerical update from a structural pass alone. Final conjectures can state a narrower exploratory reading, labelled as post-outcome, with their own prospective tests.

## Context, source work and stopping

Join CISI identifiers to the full basic-data tables, image links and Mackay–Marshall rows. Keep original strings, source locators, ambiguous columns and disputes. Report coverage before and after the join. Inspect a bounded set of photographs selected by discovery and by published examples, with readings recorded as observations and any uncertain face assignment preserved. Acquire Parpola's 2010 paper, Belcher's Harappa fish-resource chapter and the 2023 economic interpretation where accessible, with bytes, hashes, access times and observed rights. A fish-bone deposit supplies a commodity context only when an object-to-deposit join is actually sourced.

No stop depends on a favourable outcome. Stop after the registered comparisons, strict-code and dependence sensitivities, source audit and verification have completed. Preserve failures in separate versioned outputs. No change to a frozen file is permitted after confirmation. Check all calculations with an independently written arithmetic verification, run the repository checks and record the contribution as submitted, without claiming independent review.

## Deliverables

Source and field manifests, local object/face/context/image register, aggregate coverage and model comparisons, synthetic and real bench outputs, frozen predictions and hashes, exact commands, report, retrospective, conjecture cards and an attempt entry. Propose shared DATA and WORKING-MODEL changes inside this package for maintainer integration. End the report with the boldest supported reading and the observation that would decide it.
