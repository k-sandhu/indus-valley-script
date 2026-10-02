# Selecting second-order smoothing by probability loss

Written after MARKOV-03's top-one-selected endpoint and before this fit. That model improved exact top-one accuracy but increased bucket cross-entropy relative to first order. The new comparison changes the inner selection objective while retaining the same model class, fixed first-order backoff strength, candidate grid, query population and folds.

Select the second-order strength from 5, 20, 100, 500, 2000 and backoff-only by minimizing total inner held-out bucket loss over all masked slots. The inner folds remain restricted to outer training components. Ties prefer stronger shrinkage and then backoff-only. Record both inner top-one and mean bucket loss for every candidate. A selected backoff-only model exactly reproduces the first-order restorer with strength 20.

Run the existing likelihood/masking self-checks, then all five outer folds into a new endpoint. Compare the loss-selected second-order outputs with saved first-order, PMB and top-one-selected second-order outputs on the same 8,009 queries. Retain exact top-k, bucket loss, calibration and component-bootstrap contrasts. This is a post-outcome model-selection comparison on a reused benchmark. Its outer predictions remain excluded from fitting and hyperparameter selection; choosing to run this objective follows the earlier result.

Use the same independent full-record likelihood review and explicit exact-tie handling. Preserve the previous model, failed review and rational tie witnesses. Detailed predictions stay local. A further adaptive choice needs a separate protocol and fresh evaluation design.
