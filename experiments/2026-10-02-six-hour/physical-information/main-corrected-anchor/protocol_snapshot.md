# Physical membership as information

Protocol written on 2 October 2026 before the first run. This is a blind inference simulation. It tests which observations would help an investigator who sees unfamiliar marks on containers and has no linguistic reference corpus.

The concealed system uses six single-mark quantity labels. A large container holds smaller containers whose quantities add to its quantity. The observer receives labels and physical membership, then tries to recover their relative values. An independently counted object supplies one absolute measurement. The linear calculation is borrowed from conservation laws and observability: each inspected assembly contributes a row to a system of equations.

## Concealed objects and observations

The answer key assigns the quantities `{1, 2, 3, 4, 6, 8}` to six randomly renamed codes. Enumerate every multiset of two, three or four child codes whose quantities sum to a parent quantity. In each of 24 fixed seeds, draw 20 assemblies with replacement: 12 training assemblies and eight withheld assemblies. Every parent and child is a separate object with one label. Add unlinked labelled objects until every code occurs equally often across the complete object pool.

The text-only condition receives the balanced pool of single labels, with roles and membership removed. All 720 permutations of the six values have the same text-only compatibility. The observer learns a physical relation when parent and child membership are disclosed. Each complete relation gives

`value(parent) − sum(value(children)) = 0`.

Prefixes of 0, 1, 2, 3, 5, 8 and 12 training relations measure how information accumulates. Evaluate each prefix before looking at withheld relations. Do not select seeds or assemblies to obtain a full-rank system.

## Inference and exact counts

Compute row rank with rational arithmetic. For six unknown values, rank five with a strictly positive one-dimensional nullspace identifies a relative value vector. Report its primitive integer representative and whether it matches the answer key up to scale. Rank below five retains multiple linear degrees of freedom; rank six permits only the zero vector and rejects the positive-quantity model.

As a separate finite diagnostic, enumerate all 720 assignments of the stated value bag. Count training-compatible maps, whether the true map survives, and maps that also fit all eight withheld assemblies. The value bag is an additional known prior in this diagnostic. The rank/nullspace calculation receives no value bag. Record both results so that the finite count cannot silently stand in for unrestricted identifiability.

Add one equation from an independently counted object. Its code is selected uniformly from the six codes by the seed, and its measured quantity is read from the concealed answer key. Report augmented rank, uniqueness and exact recovered values. Also compare measurement choices across all six codes. An active choice minimizes the expected surviving candidate count under a uniform distribution over the current finite candidate set; it is chosen before accessing the actual count. Preserve ties by code order. Record the actual survivors after this measurement and the average over all six possible measurement choices.

## Controls

1. **Scrambled membership.** Preserve parent labels and the multiset of child groups, but randomly reassign child groups to parents separately in training and withheld assemblies. Keep the number of changed groups in the record. This control retains the labels and group-size distribution while changing physical relations.
2. **Incomplete contents, treated as complete.** Remove one randomly chosen child from six randomly chosen training assemblies. Fit all remaining visible contents as exact equalities. Record rejection and loss of the true map.
3. **Incomplete contents, recorded correctly.** Use equality for the six complete assemblies and `value(parent) ≥ sum(value(visible children))` for the six known incomplete assemblies. Report equality rank, the exact finite feasible-map count, anchor effects and withheld complete-assembly predictions. Missing children have no maximum size in this model, so the inequality retains their uncertainty.
4. **Ownership labels.** Keep the same physical assemblies and balanced object pool, but shuffle labels globally across all object slots and unlinked objects. These labels identify categorical badges assigned independently of quantity. Their total frequencies match the quantity-label pool. Test the same arithmetic procedure and preserve any accidental numerical fits.

For each control, a unique positive ray must also satisfy the withheld relations before it is accepted by the unrestricted rank-five procedure. Finite-prior acceptance requires at least one training-compatible map that also fits all eight withheld relations. Report the denominator and both decisions separately.

## Records and checks

Save generated object pools, relation lists, concealed answer keys, matrices, rational rank summaries, all prefix/control results and code hashes in a new `main/` directory. Refuse to overwrite an existing result. Keep a code snapshot with that run.

Check exact balance of the text-only pool, absence of object reuse between assemblies, all concealed complete conservation equations, equality of scrambled label/group multisets, badge-pool frequencies, the direction of incomplete inequalities, enumeration size 720, rank-five recovery up to scale, and anchor recovery. Verify the rational solver against an independently implemented determinant calculation on square submatrices. These checks validate the generated experiment and calculations; results are retained for every seed.

## Archaeological acquisition target

Search original museum or excavation records for envelopes whose exterior marks and enclosed token groups can be linked to the same stable object identifier. Record access level, exact available fields, missing correspondence fields and a collection plan. Keep acquired third-party witnesses local. The simulation's useful output is a specification of which additional physical observations could constrain an unfamiliar label system; archaeological quantities, operations and completeness must be established from their own sources.
