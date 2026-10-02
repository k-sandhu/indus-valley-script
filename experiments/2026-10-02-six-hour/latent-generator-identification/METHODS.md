# Grouped products and their exact rank witnesses

The inputs are the completed overlapping-forms endpoint's twelve parameter systems and generator snapshot. The common-length variants use three forms, six slots and twenty codes. For each form c and slot j, its calculated vector is `(1-alpha)*extended[c,j]+alpha*background`. The frozen source's variant list contains alpha 0/.35/.70. A separate alpha 1 endpoint provides the collapsed control. The two form-population shifts retain the slot distributions and use positive weights `(1-shift)*mixture+shift*roll(mixture,1)` at shifts 0/.35.

## Exact population conventions

Binary64 entries are converted with Fraction, retaining their exact integer ratios. In the normalized convention, divide each slot vector by its exact rational sum and normalize the mixing vector the same way. The largest per-entry change from the raw binary64 value is 2.22×10⁻¹⁶. Normalization multiplies each grouped conditional row by a positive scalar, preserving its row rank and Kruskal rank.

The threshold convention follows the source's binary64 cumulative sums. For codes 0 through 18, subtract consecutive cumulative thresholds clipped to [0,1]; code 19 receives the remaining interval up to one. This includes the source's final-code clamp. The largest difference from a raw weight is 4.16×10⁻¹⁶. At zero alpha, some rounded sums below one give an extra positive interval to code 19, increasing the slot support from five symbols to six. At positive alpha all twenty symbols retain positive probability under both conventions. These are explicit independent-continuous-uniform population models.

## Identification argument

Write the normalized slot probabilities as q(c,j,a), where c indexes the three forms and a indexes the twenty codes. Conditional independence gives

`P(X0=a0,...,X5=a5 | form=c) = product_j q(c,j,aj)`.

Set Y1=(X0,X1), Y2=(X2,X3) and Y3=(X4,X5). Each grouped matrix has three rows and four hundred columns. Its row c, column (a,b), is `M1[c,(a,b)]=q(c,0,a)*q(c,1,b)`, with corresponding formulas for M2 and M3. Each row sums to one. The six-slot product is exactly the product of those three paired factors, so the Y variables are conditionally independent given the form. Their population tensor is

`T[u,v,w] = sum_c pi[c]*M1[c,u]*M2[c,v]*M3[c,w]`.

For each matrix, exact minor tests select independent columns in ascending code-pair order. A nonzero 3-by-3 determinant certifies row rank three. With exactly three rows, full row rank also gives row Kruskal rank three: every subset of those independent rows is independent. All 216 main matrices have such a witness. Positive mixing weights and rank sum nine satisfy the threshold eight in [Allman, Matias and Rhodes, Corollary 2](https://arxiv.org/pdf/0809.5032v2). Consequently, the exact tensor determines pi and all three grouped matrices up to one common row permutation.

Recover each original slot distribution by marginalizing its identified pair row. For example, `q(c,0,a)=sum_b M1[c,(a,b)]` because the second slot vector sums to one. Repeating that operation recovers all six slot distributions under the same form permutation. This is the grouped-product construction and marginal recovery described by the paper's Lemmas 12 and 14. The proof identifies the product-model parameters at these supplied parameter points; the count of three components is part of its premises.

## Collapsed control and independent checks

At alpha 1, all conditional vectors equal a common nonzero background distribution b. Each grouped matrix then repeats the same row `b(a)*b(b)` three times, giving ordinary and Kruskal rank one. For any positive weights summing to one, the full population law reduces to `product_j b(aj)`. The two saved weight vectors (.2,.3,.5) and (.3,.3,.4) therefore give equal laws and different parameters beyond label permutation. The separate endpoint verifies this equality symbolically through the identical component factors and their unit weight sums.

The main implementation uses direct small determinant formulas. The independent implementation constructs probabilities with scalar binary64 operations and rational arithmetic, builds every grouped entry, and uses Gaussian elimination for matrix rank and each saved determinant. It checks all recovered slot marginals, profile identities, source hashes, support counts, shifted weights and representative exact product equalities. The full product factorization above supplies the all-cell argument without allocating a 400-by-400-by-400 tensor.

The executed [main source](../../../src/six_hour/latent_generator_identification.py) and [review source](../../../src/six_hour/latent_generator_identification_verify.py) have endpoint snapshots. Main input SHA256 values are `88a6390d425a971e7e8518800b1da30651cbdbfbba635e5829231cdac97d68c1` for parameters and `709eb292076c757795165071fa5ba85a6428635f579ff49f28ad39fa5ffb54b2` for generator code. The protocol hash is `f032515def45bc4b467a498755297d2bb63fb360eebec46baa97e7d85a039d28`. The result and review record their own source/output hashes.
