# Graph-search development record

The earlier eight-symbol experiments enumerated every candidate map. They could assess the score's recovery but supplied no larger-inventory search method. We followed the directed transition objective into the numerical optimization literature and chose the existing FAQ and 2-opt implementation in SciPy. The protocol fixed its starts, tolerances, seeds and selection rule before the pilot.

Boundary probabilities posed an implementation detail. A transition-only graph would omit the first and last factors used by the record likelihood. We added start and end nodes with fixed matches. Direct record likelihood and the matrix objective agreed for every fitted pilot and main candidate. These matches describe corpus boundaries and impose no symbol identity anchor.

The pilot covered eight conditions and 32 candidate outputs. Its six checks passed, including fixed boundaries, objective direction, exhaustive small-score bounds and multistart dominance. The main grid then generated 384 conditions and 1,536 outputs. No pilot repair or parameter change was made. [Pilot review](pilot/review.json), [main result](main/results.json).

The independent review regenerated records from the preserved seeds and counted adjacent pairs using a separate Counter-based route. It calculated scalar scores for every returned map and used a flattened matrix product for exhaustive eight-symbol maxima. All ten checks passed. Numerical subtraction leaves tiny negative gaps around zero; the report uses a declared tolerance for optimum attainment and positive gaps for descriptive means. Frozen result fields retain the original floating-point values.

A frequency start helped some transition conditions but lowered recovery in the small administrative family. Retaining both starts and randomized alternatives avoided selecting an initialization after seeing its outcome. The multistart pool also retains every unrefined candidate, so a 2-opt refinement cannot remove a better candidate from selection.

The study found two exact search failures and four cases in which the exact optimum preferred a wrong map. It preserves their separate identities for later work. At twenty symbols, full recovery was often incomplete even when many identities matched. These outcomes argue for reporting partial identity accuracy, held-out predictions and score certificates together.

The compact frozen protocol has several missing spaces between prose and numbers. The findings use ordinary spacing without changing its design or bytes. The tracked corpus counts and ledgers are our generated data; the experiment adds no third-party corpus. Further work should supply a new solver, new likelihood or independently observed relation before rerunning these fixed inputs.
