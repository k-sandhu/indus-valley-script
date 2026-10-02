# Read-only review of the unknown-count gap prototype

The root implementation marginalizes missing fine-code states through row-normalized, position/length/metadata-dependent Markov transitions. Its surviving-glyph likelihood is correct for that model. It conditions on an internal gap, both surviving sides, the candidate count range, and a specified full-text length prior; it does not assign words or sounds.

The artificial benchmark draws a true erased count uniformly from `1..min(3,L-2)`, then an internal start uniformly from `1..L-k-1`. For fixed observed left and right strings, survivor count `m` and start `i` are known, and candidate full length is `L=m+k`. The benchmark observation law therefore contributes

`q(k,i|L) = 1 / [min(3,L-2) * (L-k-1)]`.

The second factor is `1/(m-1)` and cancels across candidates, but `1/min(3,L-2)` does not cancel for candidate lengths three and four. The current predictor uses `P(L|metadata) P(survivors|L,k)` without this design factor. It is a coherent declared predictor, but its benchmark count masses are not the posterior under the artificial masking mechanism. A separate design-matched sensitivity can add `-log(min(3,L-2))` without changing the historical predictor's assumptions. Alternatively, a benchmark restricted to intact length at least five avoids the clipping, but changes the population and should remain a sensitivity.

The saved initial benchmark has local exact-count accuracy 43.05%, independent-slot accuracy 41.92%, and a constant-one design control of 51.07%. Thus it presently offers no count-recovery advantage over the simplest design-aware control. A small local-versus-independent gain cannot be reported as general gap-count restoration success. Historical erosion may have a different count, geometry, and placement law altogether.

The same artifact/identical-text grouped folds protect this benchmark. Smoothing 20 is frozen from the earlier task, so this remains exploratory. Fine-code UNKNOWN pooling and uncalibrated model masses are already disclosed. No root source was edited during this review.

The separate design-matched sensitivity is now complete in `results/gap_design_matched/gap_design_matched.json`. It verifies the source/input hashes and reconstructs all 1,596 query identities and fold assignments before exactly reweighting the saved posteriors. Independent accuracy rises to 45.61% and local accuracy to 46.30%. The local-minus-independent gain is 0.689 percentage points (conditional group-bootstrap interval -0.569 to 1.940), and local-minus-constant-one is -4.762 points (-7.775 to -1.726). Correcting this design mismatch therefore does not rescue gap-count recovery. Historical-prior source and results remain untouched.
