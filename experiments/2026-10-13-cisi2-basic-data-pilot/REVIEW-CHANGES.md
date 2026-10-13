# Changes after the independent verification

13 October 2026, afternoon. The pilot's author session ended before the package was reviewed. The coordinating session had it verified by an independent agent ([report](../2026-10-13-data-round-1-verification/REPORT.md), findings F04–F11 and F18) and applied the corrections below. Every file as it stood before these changes is kept locally in `data/raw/2026-10-13-cisi2-basic-data-pilot/pre-review-2026-10-13/` with a SHA256 list.

The verification reproduced every tracked output and all the agreement, coverage and comparison counts from the local readings. The full builder, including its internal parser step, was then rerun by the coordinator and regenerated `final.jsonl`, the two final page files and `changes.json` byte for byte; `join.py` regenerated `coverage.json` and `object-flags.csv` byte for byte after its docstrings were edited.

## Rights corrections

Tracked files were meant to hold no transcribed CISI value, but four places did. The two code examples in the transcription rules of [PROTOCOL.md](PROTOCOL.md) now read `DK-C nnnn` and `L, P-nnnn`; the first had reproduced the excavation reading of one pilot entry. Docstring examples in [join.py](join.py) that quoted a museum accession, a registration alias and FC numbers of pilot entries now describe the pattern without values; the code is unchanged. The whole-cell alternative in [schema.json](schema.json) is now `[candidate_a/candidate_b]`. The observed FC-number endpoints of two groups were removed from the README, [DATA-UPDATE.md](DATA-UPDATE.md) and [question-updates.md](question-updates.md); the groups are now described by rule (four-digit FC numbers; a later excavation series).

`PROTOCOL.md` was frozen by hash before the first reading, so its edit is recorded here rather than hidden. [PROTOCOL.sha256](PROTOCOL.sha256) still identifies the original, which is kept locally at `data/raw/2026-10-13-cisi2-basic-data-pilot/pre-review-2026-10-13/PROTOCOL.md`; the tracked, redacted text has SHA256 `c1324a60661e04ebf86280eca4a6704738cc0eaffaa030de7db2e1cad53edee9` ([PROTOCOL-public.sha256](PROTOCOL-public.sha256)). The two files differ only in the two examples. `AMENDMENT-1.md` is unchanged and still matches its frozen hash.

## Count corrections

| Place | Before | After | Basis |
|---|---|---|---|
| README, excavation comparison: Lipi adds a DK subarea letter | 8 | 9 | Independent normalization: M-673, M-712, M-722, M-734, M-754, M-755, M-756, M-903, M-920 |
| README, excavation comparison: Lipi drops the DK- prefix | 4 | 3 | M-626, M-672, M-674 |
| README result: holding institution | "All 283 gain" | supplied for 283, added for 209 | 74 joined objects already had one |
| README, PROCEDURE.md, manifest proposal: pages whose header shows the expected number | 412 of 447 (35 unreadable) | 418 of 447 (29 unreadable, not inspected) | Corner-header count in the verification; the claim that no page is missing is narrowed accordingly |

The other numbers in the report were confirmed: the accuracy tables, the coverage table, 119 bracketed cells in 101 rows, the excavation comparison totals and the museum-number gain of 202 (179 without a bracketed digit).

## The appended digits and the FC number

A cross-check made during the review ([fc-crosswalk.json](../2026-10-13-data-round-1-verification/fc-crosswalk.json)) explains the `excavation-idno` construction the README describes. For Mohenjo-daro the FC number is 1000 plus Marshall's 1931 catalogue number or 2000 plus Mackay's 1938 catalogue number: among the objects joined both here and in the [Mackay and Marshall package](../2026-10-13-mackay-marshall-tables/README.md), 216 of 219 with an unbracketed FC number follow that rule. The digits Lipi appends are therefore the excavator's catalogue number. The three exceptions are M-653, M-656 and M-707, members of the two pairs whose excavation numbers differ between Lipi and CISI 2.

The pilot's recheck had taken Lipi to be wrong for those pairs. Measured on the CISI 2 plates, which print seals at 2:1, each of the four seals comes within 0.8 mm of the size printed in the excavator's row that Lipi assigns and misses the row CISI 2 assigns by 3.1 to 4.8 mm, against control seals on the same pages that fit within 0.7 mm (one within 2.2 mm) ([swap check](../2026-10-13-data-round-1-verification/swap-check.md)). CISI 2's basic data therefore has both pairs crossed, in its FC column as well as its excavation column, and the FC rule holds for every checkable object whose CISI 2 row is right. The README, the retrospective and the proposals now say so; the Mackay and Marshall join, which follows Lipi, stands.
