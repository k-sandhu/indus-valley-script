# Distinguish a normalization from an acquired count

Recorded after `pilot-complete-v1` and before the next run.

The four complete-data pilot worlds recovered relative values under the information/rank policy, but acquired no absolute value solution. All four random-policy runs acquired an absolute solution. Inspection of the recorded scores found a selection error: the rank calculation for a prospective count included `sum(values) = 1`, the artificial gauge used to represent relative vectors. Once the relative vector was determined, the gauge made the coefficient matrix appear full rank. Every physical count was consequently scored as adding no information about scale.

The repair keeps the observed equality rows separately from the normalization row. Prospective physical counts are scored against observed equalities. A count replaces the relative normalization with measured units.

An accompanying computational simplification uses the identified relative vector directly. Every compatible further homogeneous membership equation is already determined by that vector. Membership inspections therefore have zero quantity-identification score once the relative vector is unique. Their compatible planning outcomes can be checked by exact substitution, which avoids repeated linear programs. Model validation remains assessed on the separate withheld observations.

Preserve the first pilot and its source snapshot. Rerun the same four pilot seeds in a new directory, then use separate main seeds. The repaired policy retains the original three comparisons, costs, availability, budget, outcome menus and uncertainty conditions.
