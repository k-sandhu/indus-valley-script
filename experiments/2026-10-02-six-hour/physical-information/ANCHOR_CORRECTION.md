# Count the selected object in the ownership control

Written after the first run and before the corrected run on 2 October 2026.

While preparing separate blind inputs, the observation trace exposed a control error. The first run supplied `quantity_values[badge_code]` as the independent measurement in the ownership condition. A shuffled badge identifies a category, so its code does not supply the quantity of the object bearing it. The measured count must come from that object's original physical quantity.

The correction selects the first object in the recorded inventory bearing each observed code. Its actual quantity is read from the concealed object answer key. The same preselected objects supply the random-code and active-code measurement comparisons. Save the selected object IDs and six measured values for every condition. Selection uses labels and inventory order before counts are accessed.

Repeat all 24 seeds, relations, prefixes and controls unchanged. Keep `main/`, its code snapshot and `main-review.json`. Write the corrected endpoint to `main-corrected-anchor/` with the correction hash and code snapshot. This correction affects ownership-condition measurement diagnostics; its unanchored matrices and all other conditions are unchanged.

The original run remains useful for the complete/incomplete membership and unanchored control calculations. Use the corrected run for the common result table and all ownership measurement claims.
