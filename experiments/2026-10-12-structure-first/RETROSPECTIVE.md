# Retrospective: structure before meaning

The user asked for the diagnosis to be saved and for steps 1–6 of its plan to be run unattended, with no questions. This account records the observable approach, the problems met and how each was handled. It does not reconstruct internal reasoning.

## Setting up

The session read the registry, the retrospectives, the direction memos and the packages begun on 11–12 October before writing anything. A concurrent Claude session had started the [published-claim tests](../2026-10-12-published-claim-tests/PROTOCOL.md) about forty minutes earlier, including a study of allographs in Yajnadevam's key and a study of inscriptions found outside South Asia. Step 1 was therefore scoped to a different question (whether graphic families and modifiers predict context) and foreign finds were left to that package. Codex packages for anchor expansion, satellite screening and transmission were also running; their files were read and not modified.

The diagnosis was saved as a direction memo, the map generator was preserved in `map/`, and the protocol was written after inspecting input formats and sizes and before any outcome. A starting manifest hashed the protocol, the first coding table and every input. One refinement was made to the plan before data were examined: the draft rule for merging signs (merged signs never contrast in otherwise identical texts) was replaced by held-out prediction against random groupings, because a substitution in an identical frame cannot distinguish allographs from contrasting members of a paradigm without meanings.

## Sign coding

The Lipi font maps each Wells code to a catalogue drawing at U+E000 plus the code. The interpreter in use lacked the Brotli module needed to read WOFF2, so the renderer reused the 9 October decompression of the same font and recorded its hash. Sixteen contact sheets, in Wells order with code and count labels, were inspected and every code was coded by hand. A second coder, an agent launched by the session, received only the sheets and the vocabulary. The review later showed that both codings follow the Wells order closely and that contiguous cuts of that order recover most of the family gain, so the agreement between two instances of one model on ordered sheets is reported as procedural consistency.

## Problems found and fixed

- **Run order.** Steps 2–5 were run in parallel while the second coder worked, before step 1's endpoint fixed the representation, and used Wells codes alone. The step 1 amendment records this and corrects the adopted layer to the coarser of the two passing family partitions.
- **Copper specificity rule (step 2).** The first run counted copper tablets with no recorded image as a rival class, which removed every specific sign group for four classes. The output had been printed and read when this was noticed. The rule was corrected to follow the protocol; the result stayed null. The verifier and reviewer later found the odds-ratio reporting and the permutation count wrong; run v3 fixes both.
- **Line-order control and line counts (step 3).** Pooling crossing windows from both line orders biased the control, so a conservative per-face order was added. The verifier found interior lines counted twice and the reviewer found boustrophedon faces misread; run v3 fixes both. The protocol's segmenter agreement with line divisions was omitted and was computed in review.
- **Segmenter bugs caught before use.** The Dirichlet-process sampler first used the wrong utterance-final count in two factors; a toy test with known words (boundary F1 0.976 after the fix) preceded any real run, and the review confirmed the sampler against the exact model. The rehearsal loader first read Egyptian transliterations where glyph units were needed; it was corrected before the run.
- **Rehearsal changed step 6.** Unsupervised segmentation barely beat a trivial baseline on average, so segment statistics became descriptive under the protocol's own rule, and an amendment recorded before step 6 ran substituted whole-text statistics. The review then showed the whole-text asymmetry changes sign with unit and genre in the comparison corpora, so it too is descriptive.
- **Numeral values.** The Ur III value definition dropped units and truncated compound numbers, which made the numeral-order calibration fail on Ur III. The review's unit-aware rerun passes the calibration, and the step 4 contrast with Ur III survives every repair.
- **Overstated conclusions.** The first integrated report applied auxiliary assumptions to one hypothesis only, drew a copper conclusion outside the frozen rule and omitted prior work. The reports were rewritten against the frozen predictions, with Mahadevan, Parpola, Koskenniemi, Yadav and colleagues, Farmer, Sproat and Witzel, Sproat and Rao and colleagues cited.

## Verification and review

A separate agent recomputed seven headline checks from written definitions without reading the analysis code first; all agreed, with two small faults reported. A separate adversarial reviewer ran fourteen post-outcome scripts and reported 17 findings. Every finding was accepted; [the responses](review/RESPONSE.md) list the changes.

## Stopping point

The program stopped after the six frozen endpoints, their amendments, one labelled numeral exploration and the review corrections. Each step report names the next observation that would change its conclusion. No CI/CD, recurring automation, publication or Git commit was made by this program.
