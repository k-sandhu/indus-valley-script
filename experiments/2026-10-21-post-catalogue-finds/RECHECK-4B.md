The coordinator acted on your re-check. The candidate-set conflict rule now covers named excavation areas at Dholavira (Castle, which also covers Citadel, Bailey, Middle Town with the source's spelling "Midle Town", Lower Town and Annexe) as well as compass-named areas, and it is applied to every candidate set, not only to rows with a context join. A row whose every candidate conflicts becomes `absent` with `match_basis = conflict`. The code is the conflict pass in `review/build_list.py`; `objects.csv`, `sites.csv`, `join-decisions.csv` and `local-unnamed.csv` were rebuilt from it. The five containment decisions are unchanged.

Under the same instructions, owned paths and invariants as before, check only these on the rebuilt files, keeping every earlier file unchanged:

1. Count recomputation for both sets of figures, with your own code: `verification/count-check-v3.json`.
2. Candidate-set conflicts, with your own conflict test: list every remaining row and family pair in a candidate set that conflicts on registration, grid square, trench or named area, in `verification/candidate-conflicts-v3.csv`, and confirm that no candidate set is empty and every `matched` row rests on a registration or a cited plate or figure.
3. Locators and identifiers: `verification/locator-check-v3.json`.

Then add a short section on this third check to `verification/VERIFICATION.md` and end with a final message giving the three results.
