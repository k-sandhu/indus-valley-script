# Numerical results

The published UR068-to-UR067 alignment matched 16 of 20 quantity columns. Its total absolute error was 16, equal to its signed total difference. The three lower rows totalled 3498; the upper reference row totalled 3482. Every coordinate-changing control preserved the same lower total, so the scalar total error was 16 throughout. Column comparisons supplied the discrimination. [Exact source output](source-aggregate.json) and [verification](source-verification.json).

| Representation | Cases | Mean exact columns of 20 | Mean absolute error | Lowest absolute error |
|---|---:|---:|---:|---:|
| Published grouping and order | 1 | 16 | 16 | 16 |
| Ordered flat list, known dimensions | 1 | 16 | 16 | 16 |
| Within-row reversals | 8 | 2 | 3457.25 | 16 |
| Relative cyclic shifts | 400 | 0.7425 | 3658.405 | 16 |
| Within-row shuffles | 10,000 | 0.3213 | 6152.7848 | 738 |
| Unordered-bag allocations | 10,000 | 0.3161 | 6147.406 | 828 |
| Sorted-bag allocation | 1 | 0 | 5918 | 5918 |

The published alignment was the unique minimum-error case among the 400 fixed relative shifts. Its values remained four columns short of full agreement. The result quantifies the contribution of coordinate correspondence in an already published account relation. The flat-list result identifies exactly which information was sufficient: the ordered sixty values, their start and the width of 20.

## Generated decimal accounts

The complete-account simulation recovered the hidden positional values in 299 of 300 worlds after eight relations. Sibling reordering produced identical results at every prefix. [Aggregate results](endpoints/main-v1/aggregate.json).

| Representation at eight relations | Complete accounts | Incomplete memberships | Unrelated ownership records |
|---|---|---|---|
| Position and membership retained | 299 correct unique, 1 ambiguous | 300 rejected | 300 rejected |
| Siblings rearranged | 299 correct unique, 1 ambiguous | 300 rejected | 300 rejected |
| Membership removed | 300 ambiguous | 300 ambiguous | 300 ambiguous |
| Positions collapsed | 300 rejected | 300 rejected | 300 rejected |
| Membership scrambled | 300 rejected | 300 rejected | 300 rejected |

In the unresolved complete world, seven nonzero account equations were multiples of `-10u - 9t + h = 0`; the eighth was zero. The counted object fixed `u = 1`. Every positive choice of `t` gives `h = 10 + 9t`, so eight observed accounts supplied only one independent ratio equation. The integer, increasing value systems `(1, 2, 28)` and `(1, 10, 100)` both satisfy these observations. This case is saved under seed 2026100442 with exact rank and witnesses.

Among complete worlds, 183 first became uniquely correct after two relations, 65 after three, 24 after four, 15 after five, 8 after six, 2 after seven and 2 after eight. One world remained ambiguous. Relation diversity, represented by rank, determined when the values became identifiable.

The incomplete and ownership conditions also show why a sequence of checks matters. Under full assumed membership, 97 of 300 incomplete worlds and 47 of 300 ownership worlds produced at least one false unique decoder before later relations rejected it. Scrambled membership produced a false unique decoder in 48 of 300 complete worlds before final rejection. All these intermediate answers remain in the endpoint, with their exact equations and inferred values.

These measurements support collecting a relation that adds an independent constraint and reserving later physical relations for checking an inferred numerical code. They also explain the failure of a simple feature reduction: adding digit counts loses the carries that connect positional values.
