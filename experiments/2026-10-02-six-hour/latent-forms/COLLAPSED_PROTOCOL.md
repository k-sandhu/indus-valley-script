# Post-outcome coincident-component control

The mixture and its independent review are frozen. A three-component MAP fit whose profiles coincide has uniform mixture weights and slot probabilities `(count + 3)/(reference_records + 60)`. This control measures that smoothing without estimating separate forms.

On the same 144 conditions, fit the closed-form six-slot profile with pseudocount 3, use exact linear assignment and certify each optimum with the independent dual program. Recalculate direct training/held-out likelihoods. Score this profile on the same three reference folds, then record a separate four-model reference selector in which it joins the frozen graph, pseudocount-1 slot and latent-mixture candidates. Exact score ties prefer graph, ordinary slot, collapsed profile, then mixture. Preserve the primary three-model selector.

Compare profile-control recovery with the fixed mixture and its three-model selector, and record the mixture's continuous component separation and reference-CV score difference from this control. Use the same twelve-system bootstrap seed 1510261002 and keep four conditions per system together. No true forms, pools or identities enter fitting or selection. Save a separate endpoint and all input hashes.
