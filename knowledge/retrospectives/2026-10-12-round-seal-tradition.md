# Round-seal follow-up, 12 October 2026

Claude Opus 5.5 ran this package in a git worktree (`claude/wonderful-turing-fe8ea0`) after the user asked for a follow-up to Study B of the published-claim tests: joins to Laursen's Gulf Type catalogue and to CISI, image checks of the round-seal transcriptions, a frozen test of a shared round-seal sequence tradition and an image-checked test of the "twins"-initial pattern. The package owns `experiments/2026-10-12-round-seal-tradition/`, `data/raw/2026-10-12-round-seal-tradition/` and this file. It adds one registry entry and one index paragraph, and it reads the Study B package without modifying it.

## Where the work ran

Study B, its local raw outputs and every acquired corpus existed only as uncommitted or ignored files in the main checkout, while the session ran in a clean worktree. The harness refused file writes into the main checkout. Tracked files were therefore written in the worktree, and `paths.py` resolves inputs in the main checkout through `git rev-parse --git-common-dir`. Local-only outputs (source renders, per-sign check records, Reader 2's readings, matched-set selections) were written by scripts into the main checkout's ignored `data/raw/2026-10-12-round-seal-tradition/`, where the other raw data live and where they survive removal of the worktree. The registry and index in the worktree predate the main checkout's uncommitted October 11–12 entries, so merging the branch will need those files reconciled.

## Order of work

The protocol was written after a metadata-only audit and after reading Laursen's Table 1, his text and the captions of his figures, and after viewing his Figs. 8 and 9 at page resolution to learn which seals they show. It was frozen with hashes before any sign was compared with an image. The joins and Reader 1's sign-by-sign comparisons came next, then a dated amendment, then the analysis code, whose hash was recorded before the first run. Reader 2, a subagent, read 28 code-free images in a shuffled order while Reader 1 worked and returned its readings after Reader 1's records and the amendment were saved.

## Sources and access

Laursen 2010 and Gadd 1932 were already local. Gadd's IGNCA scan is image only; its catalogue pages were read with Tesseract, which supplied the excavation and museum numbers for the Ur joins. The first render of Gadd's Plate III used PDF page 25, which is text; the plate is on page 26. Lipi ships CISI photographs filed by siglum, which covered the South Asian circular seals except M-2039 and the Dholavira seal. The British Museum returned HTTP 403, as it had to the census. The Louvre's record served two photographs of the Susa cylinder and its modern impression. CISI 3.3 defers the Gulf, West Asia and Dholavira to a volume 3.4 that a search did not find in print, so no West Asian seal has a CISI number.

Lipi's font is WOFF2, and the environment lacks the Brotli decoder. The TTF decoded from the same file by the Bonta-extension package was used instead.

## What the checks exposed

Laursen's drawings and Gadd's photographs matched Lipi's sign counts and layouts closely enough to join 25 of Laursen's 27 Indus-inscribed Gulf Type seals, his no. 56 and three Fig. 10 objects; five joins rest on burial-mound, excavation or plate numbers in Lipi's metadata. The check found few outright transcription errors and more structural problems. Lipi's sign order for two Gulf seals is the mirror image of the impressions; Lipi's direction field and its parse disagree for a third; Lipi codes Laursen's pseudo-script strokes on Karzakan seal no. 11 as stroke numerals; and Failaka no. 13 shows about seven signs where Lipi codes four. Laursen's "500" for Mohenjo-daro seal no. 5 is Mackay's number, which Lipi stores with M-415, not CISI M-500. The amendment added a sensitivity that re-orients the mirrored texts and wrote down the populations of the S3 and S4 sensitivities and the control seeds, which the protocol had left implicit.

## Computation

The Kneser–Ney implementation was checked against Study B's model class on twenty South Asian training sets and agreed exactly. One null draw took 0.34 s alone. Other sessions were running 21 worker processes during the full run, which slowed it several-fold without changing the design.

## Outcomes

Under the frozen rules the round seals form a shared tradition (other round seals predict a held-out one 1.28 bits per transition better than matched South Asian text, p at the 1/1,001 floor). A unigram model reproduces 1.22 of those bits, and the excess of shared transitions (+2.8 points, p = 0.27) does not meet the rule for a sequence tradition, so the shared element is sign inventory. Every sensitivity agrees. The Mohenjo-daro copper tablets, the positive control, give a similar total with a 25-point transition excess, which shows the transition measure can detect formulae at this size. Models trained on one region's circular seals do not predict the other region's after Holm correction. The twins-initial pattern holds with both readers' identifications (4 of 22 against 2 of 2,122), and both readers agreed on all 28 items; two of the four West Asian texts are pseudo-inscriptions by Laursen's account. The independent verifier passed 14 of 14 checks. The report names exploratory attributions separately.

## Errors found during review

The protocol counted 43 round faces; the export has 42, and the report says so. The amendment described the nine West Asian known-start texts outside Reader 2's set as non-round, but one is the Susa cylinder, whose Louvre witness arrived after the blind set was built. A first draft of the report counted the Susa circular seal among the 13 texts both readers saw, although its first sign is illegible in Lipi and it is not in the test set. These were corrected in the report; the frozen files were left unchanged.
