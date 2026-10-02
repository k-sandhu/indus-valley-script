# The stored latent forms satisfy a population identification condition

All thirty-six common-length generator profiles satisfy Allman, Matias and Rhodes's Corollary 2 with the fixed slot pairs (0,1), (2,3) and (4,5). Each pair's conditional matrix has exact row rank three, giving Kruskal ranks 3+3+3=9 against the required threshold eight. This identifies the three mixing weights and six form-specific slot distributions from their exact population distribution, up to a common permutation of the form labels. The calculation covers all twelve stored systems at shared-mass values 0, .35 and .70 under both declared numerical conventions.

The [protocol](PROTOCOL.md) was frozen before rank checks, after the overlapping-forms mapping outcomes were known. The mathematical model has a supplied component count of three, a named twenty-symbol alphabet, observed slot order and conditional independence of slots given the form. One convention exactly normalizes rational representations of the calculated binary64 slot weights. The other uses the code's rounded cumulative thresholds with independent continuous uniforms. Neither convention describes the PRNG's finite state space. [Methods](METHODS.md) give the product construction and the identification argument.

| Shared mass alpha | Stored systems | Pair ranks in every system | Condition | Smallest singular-value ratio across pairs, normalized convention |
|---|---:|---|---|---:|
| 0 | 12 | 3, 3, 3 | 9 ≥ 8 | 0.435248 |
| .35 | 12 | 3, 3, 3 | 9 ≥ 8 | 0.474789 |
| .70 | 12 | 3, 3, 3 | 9 ≥ 8 | 0.331864 |
| 1, constructed control | 12 | 1, 1, 1 | 3 < 8 | Rank certified by identical rows |

The singular-value ratios are diagnostics. Every rank-three statement is certified by a saved nonzero rational 3-by-3 minor. [Main results](main/results.json) contain all 216 grouped matrices' witnesses, input hashes, supports and positive mixing vectors for both unshifted and .35-rotated populations. [The compact table](main/ranks.csv) provides one row per witness. The smallest supplied mixing probability across both conventions and shifts is about .0257680.

At alpha 1, each form and slot equals the common background. The [separate controls](collapsed-control/results.json) verify identical grouped rows with exact rank one. Mixing vectors (.2,.3,.5) and (.3,.3,.4) have different weight multisets but produce the same population law. The collapsed model therefore has a direct parameter nonidentification witness.

The [independent review](review-v2/verification.json) passed. It reconstructs 345,600 exact grouped entries, checks 34,560 slot marginals and 144 positive mixing vectors, and certifies 288 saved minors by Gaussian elimination. It also verifies 5,760 six-slot/product grouping identities and the collapsed equal-law argument. Main calculation took 1.92 seconds; the review took 2.54 seconds. The first review's support-count assertion failed and is retained with its [repair note](AUDIT_REPAIR.md). Its correction leaves all main witnesses and controls intact.

The result supplies a structural premise for a future latent-form estimator on this synthetic family. That estimator would still need a finite-sample fitting method and an evaluation on fresh systems. Alphabet correspondence is a separate inference task. The identified parameters are the mixing weights and slot distributions; decomposing those slot distributions into the generator's original factors, background and alpha would require additional restrictions.

[The work record](RETROSPECTIVE.md) links source access, the numerical convention and the failed assertion to reusable code. The [primary-source record](sources/primary-source.json) gives the versioned paper, page coordinates and local PDF hash. The acquired PDF stays local; the stored generator parameters are synthetic.
