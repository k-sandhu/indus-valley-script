# Observable approach and outcomes

This branch followed the identity-acquisition and verification studies. Those earlier controls queried an exact identity oracle. The archaeological audits exposed a different problem: claims often inherit a source, and two mistakes can arise from one swapped interpretation. We specified both dependencies before generating this branch's outcomes.

The implementation reused the frozen integrated mapping score from CRYPTO-03 and added 29 latent source states: identity plus 28 transpositions. A first channel check normalized every one- and two-code response distribution and compared all single-code marginals. The four-system pilot produced 1,536 records. Its successful serialization and channel checks preceded the 48-system main grid, which finished in about 150 seconds and produced 73,728 records. [Pilot](pilot/results.json), [main endpoint](main/results.json).

The main results preserve every source state, query order, response and selected mapping. They include empty hard-constraint sets when two sources disagree. Keeping that outcome separate avoids assigning a default candidate after an incompatible set of claims.

The review used a different calculation of the source likelihood. The main routine transforms a candidate's identities through each swap. The reviewer transforms observed responses back through each swap and checks the candidate preimage. It also rebuilds integrated sequence scores using separately indexed counts. Replaying 18,432 outcomes and checking all 73,728 row keys found no numerical or accounting discrepancy beyond floating-point rounding. [Checks](review/checks.json).

Exact copies leave source-once scores unchanged, so that invariance is an implementation property. The main empirical contrasts quantify how a copied likelihood changes recovery and confidence at finite sample sizes. The coupled channel also restricts possible mistakes to its declared support. A retry should change the error family, add measured source reliability or use a new source-linked relation; repeating this exact grid would reproduce the current endpoint.

The protocol's compact probability expressions have missing spaces in two sentences. Its bytes remain frozen. The findings explain the same law with ordinary spacing and separate paragraphs. All generated data here are our own simulations. No acquired corpus or archaeological image is part of the tracked endpoint.
