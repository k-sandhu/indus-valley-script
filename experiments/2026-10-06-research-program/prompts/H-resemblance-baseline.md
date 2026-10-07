# Package H: a chance baseline for cross-script sign resemblance

Owned directory: `experiments/2026-10-06-resemblance-baseline/`. Local raw directory: `data/raw/2026-10-06-resemblance-baseline/`. Use live web search for precedents and comparison inventories.

## Question

K. Rajan and R. Sivanantham's 2025 study, *Indus Signs and Graffiti Marks of Tamil Nadu: A Morphological Study*, was reported by PTI as finding Indus parallels for about 90% of graffiti marks from Tamil Nadu; other reports give 42 base signs, 544 variants and 1,521 composite forms. A literature check on 6 October 2026 found no published matching rule, chance baseline or formal critique. Simple marks recur across unrelated writing systems (Changizi, Zhang, Ye and Shimojo 2006, *American Naturalist*), so a resemblance rate means little without knowing how often an unrelated inventory of similar complexity would match under the same rule. Build that baseline as a design and a feasibility pilot.

## Inputs

The local folder `data/raw/2026-10-02-connections-and-priority/south-india/` holds the 2025 morphological study PDF, both 2026 *Inscribed Potsherds of Tamil Nadu* volumes, the base-sign and concordance JSON from the TNSDA/RMRL portal and related files; the analyses in `experiments/2026-10-02-connections-and-priority/south-india/` describe them. Indus sign references include the 687-cell chart atlas (`output/chart_atlas/`, `research/chart_reference/manual_numeric_reference.json`) and the Mayig sign schema (`data/normalized/mayig_sign_schema.json`). For comparison inventories, find openly available sign lists with images for scripts unrelated to both (for example Proto-Elamite, Linear A, Cypro-Minoan, Ogham, Old Turkic, Tifinagh, Vinča-type marks) and record their sources and licences.

## Steps

1. Read the 2025 study and extract, with page references, how it defines a parallel, which signs it compares and what figures it reports. Record exactly what it does and does not specify.
2. Write `PROTOCOL.md` before computing outcomes. Define an explicit shape descriptor that can be coded by eye and checked by a second coder: stroke count, closed loops, junction types (L, T, X and others), terminal count, symmetry and orientation. Define one or more matching rules of increasing strictness that a reader could apply to the published drawings.
3. Code the Tamil Nadu base signs, a declared Indus subset or the full Indus list, and at least two unrelated inventories with the same descriptor. Have a second, independent pass on a sample and report agreement.
4. Compute match rates of the graffiti against the Indus list and against each unrelated inventory under each rule, plus a null in which descriptor-matched random marks are generated from the inventories' own complexity distributions. Report how the expected chance match rate depends on inventory size and sign complexity, with intervals.
5. State what the pilot shows, what it cannot show (for example, positional or combinatorial evidence, dating, and composite structure are outside a shape-only test), and how a full study should proceed.

## Notes

This is a methods pilot about how much a resemblance rate can establish. Attribute the 2025 study's claims to its authors and describe its method from its own text. Keep the result neutral in wording: a high chance rate would show the descriptor-level resemblance is weak evidence for transmission; a low chance rate would make the reported resemblance worth a fuller test with positional and dated evidence.
