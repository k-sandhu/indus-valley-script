# CISI3-RANGE-COVERAGE-2026-10-13: how much of the CISI 3.1 and 3.2 number ranges the local corpus holds

Status class: `verified-computation`.

Date and contributors: 13 October 2026; Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app, for k-sandhu.

Owned directory: `experiments/2026-10-13-cisi3-range-coverage/`. Registry entry: [CISI3-RANGE-COVERAGE-2026-10-13.json](../../knowledge/registry/attempts/CISI3-RANGE-COVERAGE-2026-10-13.json).

## Result

The pinned Lipi export cites 1,291 of the 2,040 numbers that follow CISI 2 in the Mohenjo-daro and Harappa series (63.3%), and 172 of the 550 numbers that follow CISI 1 and 2 for Kalibangan, Chanhu-daro, Nausharo and Rojdi (31.3%). These later numbers belong to CISI 3.1 (2010) and CISI 3.2 (2019), which the project does not hold. The absent numbers are not spread evenly. Most hundred-number blocks of seals and tablets are 89–100% present (M-1700–1899, H-1100–1199, H-1800–2199), and the long absent runs sit mostly between marked potsherds. Of the 749 absent CISI 3.1 numbers, 340 lie between present pottery numbers and 244 between present seals, tablets or sealings; of the 378 absent CISI 3.2 numbers, 294 lie between pottery and 73 between seals or tablets.

| Prefix | Site | Later volume | Slots | Present | Share | Absent between pottery | Absent between seals, tablets, sealings | Absent, other or mixed neighbours |
|---|---|---|---:|---:|---:|---:|---:|---:|
| M-1660–2129 | Mohenjo-daro | CISI 3.1 | 470 | 389 | 82.8% | 3 | 51 | 27 |
| H-1020–2589 | Harappa | CISI 3.1 | 1,570 | 902 | 57.5% | 337 | 193 | 138 |
| K-123–476 | Kalibangan | CISI 3.2 | 354 | 101 | 28.5% | 217 | 27 | 9 |
| C-51–94 | Chanhu-daro | CISI 3.2 | 44 | 36 | 81.8% | 1 | 5 | 2 |
| Ns-11–87 | Nausharo | CISI 3.2 | 77 | 32 | 41.6% | 4 | 41 | 0 |
| Rjd-2–76 | Rojdi | CISI 3.2 | 75 | 3 | 4.0% | 72 | 0 | 0 |
| CISI 3.1 total | | | 2,040 | 1,291 | 63.3% | 340 | 244 | 165 |
| CISI 3.2 total | | | 550 | 172 | 31.3% | 294 | 73 | 11 |

Source: [range-coverage.csv](run-2026-10-13/range-coverage.csv) and [summary.json](run-2026-10-13/summary.json), `by_volume`. Every present number maps to exactly one object family, so present numbers equal objects; the 1,291 CISI 3.1 objects carry 1,788 faces.

Seventeen absent runs of ten or more numbers hold 736 of the 1,127 absent slots. The pottery runs are H-1562–1585, H-2290–2333, H-2352–2361, H-2376–2396, H-2406–2547 (142 numbers), K-191–231, K-233–323, K-325–372 and Rjd-4–75. The runs between seals or tablets are M-1931–1952 (22), H-1061–1074, H-1205–1258 (54, inside a tablet block), H-1693–1703, K-123–144 and Ns-11–45; the last two start at the end of the CISI 1 or 2 range, so only their upper neighbour is known. H-1523–1537 and H-1587–1656 (70) have pottery or other objects on one side and seals on the other.

## Why this is new work

The evidence census measured coverage only for CISI 1 and 2 (1,032 of 3,620 entries unmatched, [catalogue-coverage.csv](../2026-10-06-evidence-census/synthesis/catalogue-coverage.csv)), and [DATA.md](../../knowledge/DATA.md) recorded CISI 3 only as an unheld source. No package had asked how much of the later volumes the corpus already contains. The answer bounds what buying CISI 3.1 ([Q-1008](../../knowledge/questions/Q-1008-acquire-cisi-3-1.md)) and 3.2 ([Q-1009](../../knowledge/questions/Q-1009-acquire-cisi-3-2.md)) would add, and it gives a first measured denominator for the objects published after CISI 2.

## Inputs and method

The count reads `data/normalized/lipi_observed_faces.jsonl` (SHA256 `1220f559…`, the 12 October inventory's pinned file, derived from Lipi commit `fc8813a`) and the census table `catalogue-coverage.csv`. For each catalogue prefix whose CISI 1 or 2 range the census measured, the slots run from the highest CISI 1 or 2 number plus one to the highest base number in the export; a slot is present when a local face cites it, with letter suffixes dropped (H-1951A counts as 1951). Six prefixes have numbers above their CISI 1 or 2 range: M and H, which CISI 3.1 covers, and K, C, Ns and Rjd, whose sites are named in the title of CISI 3.2. Fourteen other prefixes with 19 numbers (Gumla, Shortughai, Tepe Yahya and others) have no CISI 1 or 2 range in the census table and are listed without slots in [outside-measured-ranges.csv](run-2026-10-13/outside-measured-ranges.csv). The 666 faces without a parsable CISI reference (661 written `-`, 5 `?-n`) are outside the count.

Each absent slot takes the object class of the nearest present numbers below and above it when the two agree, and `mixed` otherwise. Classes come from the first segment of the export's `type` code: `POT` is pottery; `SEAL`, `TAB` and `TAG` are seals, tablets and sealings; everything else is other. The class of an absent number is an inference from its neighbours, which rests on the present numbers falling in blocks of one kind (H-1800–2199 are all tablets, H-1400–1499 all pottery); no absent object has been seen.

The slot rule was first applied in a chat answer on 13 October, which gave the Harappa range as H-1021–2589 from the lowest local number; this package starts every range at the number after CISI 1 or 2 and so counts 1,570 Harappa slots. The neighbour classification was added after the per-hundred counts showed pottery-dominated blocks, so it is an exploratory description written after the first outcome.

## Commands and outputs

```text
python -P experiments/2026-10-13-cisi3-range-coverage/count_ranges.py --out experiments/2026-10-13-cisi3-range-coverage/run-2026-10-13 --local data/raw/2026-10-13-cisi3-range-coverage/run-2026-10-13
python -P experiments/2026-10-13-cisi3-range-coverage/check_raw.py --run experiments/2026-10-13-cisi3-range-coverage/run-2026-10-13 --local data/raw/2026-10-13-cisi3-range-coverage/run-2026-10-13
```

Python 3.13, standard library only. The tracked outputs in [run-2026-10-13/](run-2026-10-13/) are `range-coverage.csv` (one row per prefix), `absent-numbers.csv` (the 1,127 absent numbers with their nearest present numbers and context), `outside-measured-ranges.csv`, `summary.json` (input and script hashes, rule, totals) and `verification.json`. They hold CISI numbers and counts and no Lipi field values. The full per-number table, `number-slots.csv` (2,590 slots with Lipi family ids, faces and the object class of each present number), is local in `data/raw/2026-10-13-cisi3-range-coverage/run-2026-10-13/` under the Lipi rule in [REDISTRIBUTION.md](../../knowledge/provenance/REDISTRIBUTION.md); its SHA256 is in `summary.json`.

## Verification

[check_raw.py](check_raw.py) recomputes the counts from the raw export `data/lipi/src/assets/data/inscriptions.csv` (SHA256 `c36d0c26…`) with its own parser, family ids taken from the `id` column, CISI 1 and 2 end numbers typed from the printed ranges, and its own walk to the nearest present numbers. It agrees with the run on slots, present numbers, families and faces for all six prefixes and on the context of all 1,127 absent slots ([verification.json](run-2026-10-13/verification.json), `all_agree: true`). This is the author's independent implementation; another contributor has not reproduced it.

## Scope and limits

The slot bounds come from the export, so a range may start later in CISI 3 than the number after CISI 2, run past the export's highest number, skip numbers or use some numbers for extra photographs. The Kalibangan and Nausharo runs at the start of their ranges (K-123–144, Ns-11–45, 57 slots) depend most on that assumption. A present number does not show that the export holds every face, image or field CISI 3 prints for that object. Slots measure published catalogue numbers, so finds never catalogued in CISI, such as most of Dholavira and the later Indian excavations, are outside this count ([Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md)).

## Decision and next evidence

The CISI 3.1 gap is about 750 numbers, and fewer than a third of them (244) sit among seals and tablets. CISI 3.1 would therefore add more to the record of seals and tablets already in the corpus (all faces photographed, excavation numbers) than to their count. The 244 seal- and tablet-context numbers, H-1205–1258 above all, are the objects to look up first when the volume arrives. Kalibangan's and Rojdi's gaps are almost entirely marked pottery. Rerun this count into a new dated directory when the export, the census ranges or a CISI 3 volume changes; keep this run unchanged.

The boldest reading this result supports is that the Lipi/ICIT transcription corpus holds nearly every seal, tablet and sealing published in CISI 3.1 and 3.2 apart from about 317 numbers in a few blocks, and that the rest of the unmatched range is marked pottery left out of the transcription corpus. The test is a plate check once CISI 3.1 is held (Q-1008): classify each of the 749 absent numbers from its photograph. The reading predicts that at least 80% of the 340 pottery-context numbers are potsherds or vessels and at least 80% of the 244 seal-tablet-context numbers are seals, tablets or sealings; it fails if either share is below 60%.
