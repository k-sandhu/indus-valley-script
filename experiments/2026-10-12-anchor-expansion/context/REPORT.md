# Fixed families in complete inscription contexts

Twenty-one of the 53 constrained visual families meet the declared five-string and two-split directional rule. Seventeen further families are unconstrained. At the individual-code level, 62 of the 539 constrained assigned codes meet that rule. Family pooling therefore cannot supply a supporting status for every member. The [complete summary](summary.json) retains every code, every fixed role, empty samples and actual contradictions.

The frozen map has 70 families and 673 assigned codes. Run-v2 reads its single-string `role_predictions` field explicitly and preserves the generic run-v1. The shared frame remains 1,859 complete strings and 8,535 tokens from 2,930 faces; closure and split details are in [the first frame report](REPORT-v1.md). Every calculation keeps the whole reading-order string, including repeated candidate codes and all other slots.

Supporting direction means matching-token count exceeds its conditional bag-shuffle expectation in both nonempty discovery and transfer frames. At least five distinct strings are additionally required. These are fixed structural prioritization rules; picture and Sanskrit-sense qualification are reviewed during integration. There is no estimated probability of vocabulary correctness. The raw rates and complete-inscription pass counts remain available alongside the directional flags.

The selected family results show why those fields matter:

| Family | Declared role | Matching tokens | Analytic expectation | Entire inscription's family occurrences all match | Inscriptions with a contradiction |
|---|---|---:|---:|---:|---:|
| Carrier/yoke | closing | 154/170 | 56.689 | 153/169 | 16 |
| Staff bearer | nonfinal_entity | 41/43 | 30.784 | 41/43 | 2 |
| Flag panel | closing | 53/59 | 16.649 | 53/59 | 6 |
| Toothed-tool bearer | counted_entity | 3/22 | 1.369 | 3/22 | 19 |
| Fish shapes | counted_entity | 150/892 | 59.673 | 118/706 | 588 |
| Plant branch | counted_entity | 40/186 | 27.367 | 38/181 | 143 |
| Binding/bowtie | internal_connector | 84/153 | 81.975 | 80/148 | 68 |
| Grid compartments | closing | 37/70 | 18.784 | 36/69 | 33 |
| Rim-marked vessel | closing | 749/1,106 | 254.416 | 644/982 | 338 |
| Terminal qualified vessel | closing | 82/106 | 28.742 | 81/105 | 24 |
| Human agent | nonfinal_entity | 137/214 | 168.066 | 121/198 | 77 |
| Diamond enclosure | counted_entity | 3/224 | 30.340 | 2/220 | 218 |

Carrier, staff and flag-panel families have both directional evidence and relatively few whole-inscription contradictions. The counted-tool, fish and plant families exceed their bag expectations while most containing inscriptions lack an immediately preceding selected stroke. The strict counted-entity definition is therefore far from a universal constraint for these families. W130 itself has no W001–W005 predecessor, despite the pooled toothed-tool family's directional result. W031–W035 and dotted W060 remain separately counted. Binding/bowtie's transfer match count is 29 against 28.935 expected, so its directional flag has only a small margin.

Among constrained member codes, 104 have no complete-frame observations, 226 have an empty discovery or transfer frame, 68 have fewer than five distinct strings after excluding those earlier categories, and 79 have enough support but fail the two-split directional rule. These categories are mutually exclusive in that ordering. The remaining 62 meet the rule. Individual status still requires the documented drawing and selected sense; a successful pooled family does not fill a sparse member's empty frame.

## Intact records and verification

Every family has all-string, length-at-least-three, discovery, transfer and representative-object summaries. Member rows carry the same five frames. Whole-inscription compatibility requires every occurrence of that family to satisfy the declared role; one violating occurrence makes the inscription contradictory. A string containing several different family members enters the family denominator once. Token matches, token contradictions, positional expectations and role expectations equal the sums of member-code contributions in every frame; inscription counts use the union of records.

The complete-register closure is independently equivalent, component for component, to the earlier grammar implementation: both give 2,819 components across 5,680 records. [Cross-check](closure-crosscheck-v1.json). The physical/CISI addition introduces no extra merge in this pinned register. All prior whole-string position counts reproduce; fourteen real source-witness substitution comparisons pass the one-difference check. These checks use existing source records and saved methods, with no grammar refitting, dictionary residual search or new random draws.

The [local companion schema](SCHEMA.md) describes all 2,930 complete source faces, 1,859 distinct complete-example candidates, full templates, source identifiers, component/split assignments and one-based code occurrences. Family example candidates retain contradictions for every declared role. The files remain in the ignored local directory, where the complete-inscription viewer can apply the same global map without cropping the calculation.

Run-v1 remains the generic endpoint. [Run-v2](run-v2/summary.json) is the family-integrated endpoint; this directory's `summary.json` is an identical copy for integration. The [output manifest](run-v2/output-manifest.json) records all public and local hashes. The context calculation does not choose Sanskrit words, fit a semantic likelihood or remove inconvenient inscriptions.
