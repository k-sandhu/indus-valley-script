# Evidence guide for Paper 006

Every number in the [manuscript](manuscript.md) comes from a saved output in `experiments/2026-10-12-published-claim-tests/`. Paths in the output table are relative to that directory. The [claim–evidence map](claim-evidence-map.md) traces every principal claim to its exact file and JSON key, and the [submission checklist](SUBMISSION-CHECKLIST.md) gives the ordered reproduction steps and human-review items. The study's [report](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/REPORT.md), [protocol](../../experiments/2026-10-12-published-claim-tests/PROTOCOL.md), amendments 1–4, [adversarial review](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/review/REVIEW.md) and [response](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/review/RESPONSE.md) record the order in which analyses were designed and which were added after their results had been seen.

## Pinned source versions and checksums

All raw third-party sources and per-inscription files remain local under `data/lipi/`, `data/normalized/` and `data/raw/2026-10-12-decipherment-claim-tests/` and are not redistributed.

| Source | Version or commit | Local path | SHA-256 |
|---|---|---|---|
| Yajnadevam (2024) preprint, *A cryptanalytic decipherment of the Indus script* | Compiled 13 November 2024, Rare Book Society of India copy (variant with N = 439, d = 627 noted via Raghavendra 2026) | `data/raw/2026-10-12-decipherment-claim-tests/papers/yajnadevam_cryptanalytic_decipherment.pdf` | `81c026b78a66a13d1bbc14d9c145bdd5ecabda0ada9b6d14a3ea206a1c68c599` |
| Lipi key table (`yajnadevam/lipi`, `xlits.csv`, 716 rows) | Commit `fc8813a52e183d19c441631dc26c33a4dccbea39` (short `fc8813a5`) | `data/lipi/src/assets/data/xlits.csv` | `02dd0efdc79813ae7fe94d33e4d0bbddc612d5a8ca540546974cd84c7fdbe103` |
| Lipi corpus table (`yajnadevam/lipi`, `inscriptions.csv`, 5,680 faces) | Commit `fc8813a52e183d19c441631dc26c33a4dccbea39` | `data/lipi/src/assets/data/inscriptions.csv` | `c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c` |
| Lipi lemma glossing (`yajnadevam/lipi`, `glossing.csv`, 3,491 rows) | Commit `fc8813a52e183d19c441631dc26c33a4dccbea39` | `data/lipi/glossing.csv` | `db71537fe8976a0b8c061603c55ce0fbd0d953f8f310150940cd2968c2e5e4f5` |
| Normalized clean single-line corpus (2,930 records) | Derived from `inscriptions.csv` at `fc8813a5` | `data/normalized/lipi_clean_rtl_singleline.jsonl` | `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8` |
| Digital Corpus of Sanskrit (`OliverHellwig/sanskrit`, CoNLL-U release, 6 texts, 2,465 files) | Commit `8aeed5a1343d0e48b64eb32af8c00e8c6eb29359` (short `8aeed5a1`) | `data/raw/2026-10-12-decipherment-claim-tests/dcs-sanskrit/` | Git tree at `8aeed5a1343d0e48b64eb32af8c00e8c6eb29359` |
| Monier-Williams (`sanskrit-lexicon/csl-orig`, `v02/mw/mw.txt`, 116,151 `k1` skeletons) | Cologne Digital Sanskrit Dictionaries snapshot (50,163,993 bytes) | `data/raw/2026-10-12-decipherment-claim-tests/mw/mw.txt` | `555ecf5aadaaf21e5965d6b3b419f428fc9ab9237f563627001ceca468d0cff8` |
| Perseus Latin XMLs (Caesar, Cicero, Vergil, Livy) | Perseus Digital Library `perseus-lat2` TEI XML | `data/raw/2026-10-12-decipherment-claim-tests/other-languages/phi*.xml` | Caesar `15ec3ef2…`, Cicero `3e0f7f8d…`, Vergil `e639e6a0…`, Livy `9088fefb…` |
| Old Tamil Sangam corpus (`sangam.parquet`) | Public Sangam poetry table (8,236,173 bytes) | `data/raw/2026-10-12-decipherment-claim-tests/other-languages/sangam.parquet` | `8a1011a882abff092fba0bb38265d82af26fcef8cb927ed5eadda42210763bbb` |
| Sumerian Ur III administrative archive (ORACC, 12,000 sampled tablets) | Local ORACC archive `sumerian-ur3-v1/response.bin` | `data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin` | `b220f3ee0707912d3c9c7dd5532b00a55248ba5f7b9c81ff5df121c53da69d92` |
| Mayig graphic crosswalk | Project normalized crosswalk | `data/normalized/mayig_wells_class_crosswalk.json` | `9fea45e16be1218d148473dad440f806a2f0c12c954c79347db2584324cc1f71` |
| Raghavendra (2026) preprint (`arXiv:2608.02999v1`, 4 August 2026) | Version 1 PDF consulted locally | `data/raw/2026-10-12-decipherment-claim-tests/papers/raghavendra_2608.02999.pdf` | `3334b2fc8998d1a37b922a77e3438a989ce7346d756d52d30957a276ace95c9a` |

## Saved outputs by manuscript section

| Manuscript section | Claim | Output |
|---|---|---|
| 2 | Population of 1,859 distinct texts and 577 sign types; DCS split sizes | `sanskrit-key/stage3/summary.json`, `sanskrit-key/stage1/summary.json` |
| 4.1 | 69.2% exact skeleton agreement; departure counts; glossing lemma lengths | `sanskrit-key/stage0/summary.json` |
| 4.2 | Random-string readability by length and lexicon; key and rearrangement shares | `sanskrit-key/stage2/summary.json` |
| 4.2 | Fitted readability 99.4–99.6% (DCS) and 99.5–99.6% (Monier-Williams) | `sanskrit-key/stage2/fitted_readability.json` |
| 4.2 | Segmentation of the twelve longest texts under a random rearrangement of the key | `sanskrit-key/stage4/demo.json` |
| 4.3 | Cross-entropy and redundancy by order; unigram redundancy; recomputed distance | `sanskrit-key/stage1/summary.json` |
| 4.3 | Fifty longest clean texts supply 473 key consonants (504 across all distinct records) | `sanskrit-key/stage3/summary.json` (`key.longest50.n`); local check `data/raw/2026-10-12-decipherment-claim-tests/review/r11_longest.py` |
| 4.3 | Effective redundancy of the dictionary criterion by length and lexicon | `sanskrit-key/stage2/summary.json` |
| 4.4 | Key −0.393, rearrangements −0.463 (sd 0.057), references | `sanskrit-key/stage3/summary.json` |
| 4.4 | Single held-out words (+0.35), word-level references and readings by length | `sanskrit-key/verification.json`, `sanskrit-key/stage3/validation.json` |
| 4.4 | Exhaustive *n* or *m* choice | `sanskrit-key/stage3/sensitivity_exhaustive.json` |
| 4.4 | Training-text and projection variants; order-only statistic | `sanskrit-key/stage3/sensitivity_training.json` |
| 4.5 | Best arrangements within frequency strata, fits to shuffled inscriptions, half-split transfer | `sanskrit-key/stage3g/summary.json`, `sanskrit-key/stage3g/derived.json` |
| 4.5 | Sign tokens that unconstrained optima turn into vowels, deleting them from the skeleton | `sanskrit-key/stage3/token_check.json` |
| 4.5 | Local ranks by both rankings | `sanskrit-key/stage3f/summary-v2.json` |
| 4.6 | Transfer z-scores and gap shares by language | `sanskrit-key/stage3g/derived.json` |
| 4.6 | Near-duplicate control | `sanskrit-key/stage3g/novel_transfer.json` |
| 4.6 | Failed unconstrained comparison | `sanskrit-key/stage3e/summary.json`, `sanskrit-key/AMENDMENT-2.md` |
| 4.7 | True-key separation, recovery, transfer by seed | `sanskrit-key/stage5/derived.json`, `sanskrit-key/stage5/summary.json`, `sanskrit-key/stage3g/novel_transfer.json` |
| 4.7 | Trigram reuse across halves | `sanskrit-key/stage5/ngram_reuse.json` |
| 4.8 | Homophone, graphic-variant and adjacent-Wells-code substitution | `allographs/run-2026-10-12/summary.json`, `allographs/run-2026-10-12/value_groups.csv`, `allographs/run-2026-10-12/diagnostics.json` |
| All | Independent recomputation | `sanskrit-key/verification.json`, `allographs/run-2026-10-12/verification.json` |

Figures are generated by `sanskrit-key/make_figures.py` from these outputs. The printable version is rendered by [render_paper.py](render_paper.py) from this manuscript; it rasterizes the SVG figures locally before layout.

The analyses use Python 3.13 with NumPy 2.2 and Matplotlib 3.11. Raw sources (DCS texts, Monier-Williams, Latin, Old Tamil, Sumerian, the preprints and Lipi files) and per-inscription outputs are kept locally under `data/lipi/` and `data/raw/2026-10-12-decipherment-claim-tests/` and are not redistributed.
