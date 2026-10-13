# Independent finite-model reconstruction

11 October 2026, before independent enumeration. The coordinator supplied the following law by message while freezing its model protocol. This checker will use the declared law directly and will not import coordinator model code.

States are (a,b,k) in {0,1,2} × {0,1,2} × {0,1,2,3}. Safe states have a,b ≥ 1. Each action is a subset of renewA, renewB and train, with unit cost per chosen operation and total cost at most B in {0,1,2,3}. Nonempty actions require current k > 0. Empty action remains available. Assets first age by one, clamped at zero; selected renewal resets its asset to 2. Skill ages by δ in {0,1}, clamped at zero; training resets it to 3. A shock then subtracts one from its targeted assets. The four supports are {none}, {none,A}, {none,AB} and {none,A,B,AB}. There are no shock probabilities.

The initial safe set is K. A horizon h includes the initial state and h transitions. The possible predecessor requires an action and a supported shock with a successor in the target set. The robust predecessor requires one selected action whose successors lie in the target set for every supported shock. The action precedes observation of the current shock. The infinite set is the greatest fixed point inside K.

Enumerate 32 worlds and horizons 0–12. Compute successors independently, finite sets and the infinite set by repeated elimination. Retain full state sets and witnesses where small. Compare coordinator outputs after their file format is available, recording hashes and any mismatch. Do not infer a correlation rate from the shock-support labels.

Two additional sensitivity laws are declared here before their outcomes: (1) shocks remove two asset units instead of one; (2) nonempty action eligibility requires skill remaining after its ordinary aging, rather than current skill before aging. Keep their outputs separate from the reconstruction. They test the stated safety margin and last-period training assumption. They are invented alternatives, not evidence that either law governed a historical society.
