# Amendment 1: the closing junction is the model's strongest boundary

Written 20 October 2026 after the version 1 inventory was built and before the held set H was read or any prediction was frozen. The protocol's sections 3 and 4 and their outcomes are unchanged; this amendment changes how section 5 turns the trained model into an inventory and a closing stock. Version 1 stays on disk with its hashes in [FROZEN-v1.json](FROZEN-v1.json), and [RULES.md](RULES.md) remains its rule text.

## What version 1 produced

Applied to the 1,687 texts of the build corpus B, the frozen cutting rule cut 4.5% of positions, giving units of 3.9 signs on average. Only one unit closed seal legends in three or more components, and it closed 9 of B's 994 seal legends of three or more signs (0.9%). An inventory that leaves 99% of legends without a stock closing cannot carry the predictions the protocol asks for, and it is not a description of the texts: the same model cut 18.9% of the positions of the held-out divided faces.

The cause is the threshold. τ was chosen to separate catalogue divisions from the other positions of divided faces, and a divided face is selected for containing one strong boundary, the place where its scribe broke the line. The rule therefore keeps the strongest boundary of a text and very little else. The readable-script calibration shows the same behaviour where the answer is known: trained on one line division per Ur III seal legend, the model's cuts were 91% correct but found only 47% of word divisions.

## The change

The model was trained as a choice: of all the positions of a face, which one did the scribe break at. Its direct output for a single-line legend is that choice, the position with the highest unit score, and we take this position as the junction between opening and closing. Version 2 of the inventory differs from version 1 in two places:

1. Every text of B of two or more signs is cut at its highest-scoring position as well as wherever its unit score exceeds τ. The inventory rule (units of two or more signs produced in texts of at least two components) is unchanged.
2. The closing of a seal legend of three or more signs in B is the stretch after its highest-scoring position, when that stretch has one to four signs. The closing stock is every such closing found in legends of at least three components.

The rules for scoring a legend do not change: [RULES-v2.md](RULES-v2.md) repeats the text of RULES.md word for word apart from the version, the file names and a sentence on how the stock was made, and `segment_by_rules` in `legend_units.py` is unchanged. The code is the new file `build_inventory_v2.py`; `build_inventory.py` keeps its version 1 hash.

## What was looked at before this choice

After version 1 was built we computed, on B's seal legends only, where the highest-scoring position falls (it leaves a final stretch of one to four signs in 884 of 994 legends) and which final stretches recur in three or more components (49, covering 239 legends, led by 400, 090, 176-740, 621 and 679). No alternative threshold, junction length or recurrence count was tried, and nothing in H, in the fresh pools or in the cross-validation outputs was consulted. The change is a post-outcome refinement on the discovery corpus; the held-set calibration and the prospective predictions that follow use version 2 and are frozen after it.
