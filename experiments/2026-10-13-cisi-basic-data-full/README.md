# The CISI 1 and CISI 2 basic-data tables, transcribed in full

13–14 October 2026. Question cards Q-1005 (CISI 1) and Q-1006 (CISI 2). This package continues the [CISI 2 pilot](../2026-10-13-cisi2-basic-data-pilot/README.md) to the whole of both tables under a [protocol](PROTOCOL.md) frozen by hash before any reading, with two amendments: [tail strips](AMENDMENT-1.md) for lines the first strips missed, and a [bracketed merge](AMENDMENT-2.md) for the CISI 2 blocks left unadjudicated. Transcribed values stay local in `data/raw/2026-10-13-cisi-basic-data-full/`; this directory holds the code, the counts and per-object field flags.

## Result

Both basic-data tables now have a row for every printed entry: 1,543 in CISI 1 (Joshi and Parpola 1987, printed pp. 366–375) and 2,139 in CISI 2 (Shah and Parpola 1991, pp. 435–447, including the pilot's 327), each read twice by separate Claude instances. Joined to the local corpus by CISI number, 2,602 of the 3,680 entries match one Lipi family each and 1,078 match none. Among the joined objects, a museum number rises from 226 to 2,373, a holding institution from 226 to 2,560 and an FC concordance number from 0 to 2,599; excavation numbers, which Lipi already carries, rise from 2,459 to 2,483 ([coverage.json](coverage.json)).

Across the corpus, combined with the older export, the census and the museum joins of 13 October, objects with a museum number rise from 340 (7.2%) to 2,450 of 4,695 (52.2%) when cells with an uncertain digit count, to 2,079 (44.3%) when at least one number in the cell is definite, and to 1,994 (42.5%) when the whole cell is free of brackets ([combined-coverage.json](combined-coverage.json)).

CISI 1 reads cleanly. The two readings agree on 98.6% of its 7,715 cells, all 112 disagreements were adjudicated against the page, and each reader gave a definite wrong reading in 7 cells or fewer across all columns (under 0.1% in the CISI, FC and excavation columns); 5 cells stay bracketed. CISI 2 does not. Its later pages are blurred or survive at low resolution, the readers bracketed freely, and the two readings agree on 65.3% of 9,075 cells, against 90.5% in the pilot block. Three CISI 2 blocks (pp. 437L, 438L, 439L; 256 decisions) were adjudicated before adjudication was stopped for cost; the other 2,870 disagreements keep every candidate either reader allowed ([Amendment 2](AMENDMENT-2.md)). The CISI 2 table is therefore complete in its rows and identifiers but carries many bracketed digits.

## The three frozen predictions

All three hold ([predictions.json](predictions.json)).

1. **The FC number encodes the excavators' catalogue numbers.** For Mohenjo-daro entries outside the pilot block that join a row of the Mackay 1938 or Marshall 1931 tables and have a definite FC number, FC = 2000 + Mackay No. or 1000 + Marshall No. holds for 560 of 573 (97.7%; the threshold was 95%). The 13 exceptions (M-9, M-107, M-955, M-963, M-973, M-975, M-1010, M-1061, M-1196, M-1278, M-1315, M-1316, M-1370) were not re-read against the page; the pilot's four exceptions were records crossed in CISI 2 ([swap check](../2026-10-13-data-round-1-verification/swap-check.md)).
2. **Long shot: Harappa follows the same construction.** For Harappa entries whose Lipi `excavation-idno` extends the printed excavation number, the appended digits equal the FC number without its first digit in 221 of the 226 entries that can be scored (97.8%), and in 221 of all 276 extensions (80.1%) if every entry with an uncertain FC number is counted against the rule; the threshold was 80% and the kill line 50%. This shows that Lipi built its Harappa registrations the same way as its Mohenjo-daro ones; that the Harappa FC numbers are Vats's 1940 catalogue numbers, as the CISI 2 key implies, is not tested here because Vats's table is not transcribed.
3. **CISI 1 reads at least as cleanly as the pilot's CISI 2 block**: 98.6% cell agreement against 90.5%.

## Accuracy

| Volume | Cells | Agreement | Disagreements | Adjudicated | Definite wrong readings, pass 1 / pass 2 | Cells bracketed after adjudication or merge |
|---|---:|---:|---:|---:|---:|---:|
| CISI 1 | 7,715 | 98.6% | 106 (plus 6 corrigenda lines) | all | 7 / 7 | 5 |
| CISI 2 (new blocks) | 9,075 | 65.3% | 3,146 | 256 (pp. 437L–439L) | 54 / 29 in the 1,205 cells of the adjudicated blocks | 2,946 (72 of them in the adjudicated blocks) |

Per column and per block figures are in [accuracy-summary.json](accuracy-summary.json) and `accuracy/`. In CISI 1 the commonest disagreement was one reader bracketing a digit that the other read definitely and rightly; the definite errors are mostly separators (comma against full stop in museum registration numbers). In the adjudicated CISI 2 blocks most definite errors are in the photograph column.

The merge lists catalogue numbers missing between the lowest and highest number of each site prefix: 10 in CISI 1 (H-266 to H-275, printed as "see Vol. 2") and 131 in CISI 2, mostly the Harappa numbers that CISI 1 holds ([merge-summary.json](merge-summary.json)). CISI 1 prints two pointers to CISI 2, a bracketed cross-reference "{H-356}" and "M-595 deleted, see vol. 2"; they are kept in the table and left out of joins.

The non-blind cross-check against Lipi, the older export and the FC rule flags 1,206 cells on 1,144 rows ([crosscheck-summary.json](crosscheck-summary.json)); 1,076 are excavation cells, about half of them cells that the merged table prints with an uncertain digit. Under Amendment 2 these were not re-read and nothing was corrected from them.

## How it was done

[make_strips.py](make_strips.py) rendered the pages (CISI 2 at zoom 8.34, CISI 1 at zoom 4) and cut each half-column into overlapping strips of about fourteen lines; [blocks.json](blocks.json) lists the 43 blocks. It ended blocks at the last line it could detect, which missed faint lines at the foot of 17 CISI 2 pages; [make_tail_strips.py](make_tail_strips.py) cut tail strips for them and two further instances read them ([tails.json](tails.json)). Sixteen readers worked under [READER-BRIEF.md](READER-BRIEF.md): eight for pass 1 and eight for pass 2, in separate instances, with the second pass reading column bands in two sweeps. Codex (GPT-6.1-Sol) was tried as a second reader on 30 pilot entries and rejected for confident misreadings; it wrote the pipeline instead ([TOOLS.md](TOOLS.md), selftest 53/53, reproducing the pilot's coverage exactly).

[assemble_passes.py](assemble_passes.py) prepared each pass for comparison without changing the readers' files: it applied the tails, joined four CISI 1 entries printed across a block boundary, and set a reader's bracketed CISI number or site prefix to the candidate that fits the printed order, keeping the reading as written in a comment. [compare_passes.py](compare_passes.py) listed the disagreements, adjudicators decided them under [ADJUDICATOR-BRIEF.md](ADJUDICATOR-BRIEF.md), [normalize_outcomes.py](normalize_outcomes.py) made each outcome label agree with the bracket rule (keeping the adjudicator's label), [auto_adjudicate.py](auto_adjudicate.py) applied Amendment 2, and [build_finals.py](build_finals.py), [merge_volumes.py](merge_volumes.py), [crosscheck.py](crosscheck.py) and [join_full.py](join_full.py) built, merged, checked and joined the tables.

## Limits

Readers and adjudicators are instances of one model, so shared misreadings are possible. CISI 2's error rate is measured only for three blocks, and its unadjudicated cells keep the union of two readings, which is safe for the true value but leaves many digits open. Coverage gains counted with brackets include numbers whose digits are not settled; the three counting rules above bound them. The CISI values stay local until the rights in CISI are decided.

## Files

Protocol and amendments: [PROTOCOL.md](PROTOCOL.md), [PROTOCOL.sha256](PROTOCOL.sha256), [AMENDMENT-1.md](AMENDMENT-1.md), [AMENDMENT-1.sha256](AMENDMENT-1.sha256), [AMENDMENT-2.md](AMENDMENT-2.md). Briefs: [READER-BRIEF.md](READER-BRIEF.md), [ADJUDICATOR-BRIEF.md](ADJUDICATOR-BRIEF.md), [CODEX-PROMPT.md](CODEX-PROMPT.md). Code: the scripts named above, [cisi_common.py](cisi_common.py), [cisi_parse.py](cisi_parse.py), [selftest.py](selftest.py). Outputs: [blocks.json](blocks.json), [tails.json](tails.json), `accuracy/`, [compare-summary.json](compare-summary.json), [accuracy-summary.json](accuracy-summary.json), [merge-summary.json](merge-summary.json), [crosscheck-summary.json](crosscheck-summary.json), [coverage.json](coverage.json), [combined-coverage.json](combined-coverage.json), [object-flags.csv](object-flags.csv), [predictions.json](predictions.json), [selftest.json](selftest.json). Records: [RETROSPECTIVE.md](RETROSPECTIVE.md), [DATA-UPDATE.md](DATA-UPDATE.md), [question-updates.md](question-updates.md), [registry-entry.json](registry-entry.json).

## Boldest reading and the test that would decide it

The FC concordance number is a key to the excavators' own catalogues at both major sites: 2000 + Mackay No. or 1000 + Marshall No. at Mohenjo-daro, and very probably the Vats 1940 number at Harappa. If so, every CISI entry for these two sites can be linked to its excavation-report row by arithmetic, independently of any later database. The decisive test is to transcribe Vats's Harappa catalogue table and check whether the Harappa FC numbers, less one fixed offset, give the Vats catalogue numbers of the joined entries; a second, cheaper test is to re-read the 13 Mohenjo-daro exceptions on the page and see whether each is a crossed record or a misreading.
