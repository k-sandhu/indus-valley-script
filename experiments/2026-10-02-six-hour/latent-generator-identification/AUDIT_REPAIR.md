# Support-count assertion in the first review

The first review failed before rank reconstruction because it required five positive symbols in every zero-alpha slot under both probability conventions. The normalized-weight convention has those five symbols. Under the separately declared cumulative-threshold convention, a rounded sum below one can assign the final-symbol clamp a small extra probability. A slot can therefore have six positive symbols in that convention.

The failed source and exception remain in [review](review/). The revised verifier keeps full independent probability reconstruction and checks the resulting saved support counts, allows five or six at zero alpha for the threshold convention, and retains twenty at positive alpha. It writes to a new [review-v2](review-v2/) endpoint. Main profiles, rank witnesses, controls and the protocol remain unchanged.
