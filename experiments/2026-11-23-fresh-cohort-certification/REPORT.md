# Fresh post-catalogue cohort certification

We audited all 503 rows of the post-catalogue inventory and all 358 rows of the candidate identity and exposure audit against every local corpus and join register without inspecting any inscription sign sequence. Exactly **8 post-catalogue inscribed objects** pass strict certification as `certified_absent_sealed`: **3 seals**, **3 sealings** and **2 tablets**, each verified absent from all 4,695 Lipi families, all 1,146 Mackay and Marshall seal-table joins, all 3,680 CISI 1 and 2 basic-data rows (2,602 joined to Lipi) and `bench/spent.json`, with a confirmed local PDF plate or figure page ready for blind transcription. Separately, the Farmana 2011 reserve in [2026-10-20-fresh-test-collection](../2026-10-20-fresh-test-collection/REPORT.md) holds 15 absent marked-pottery rows outside the 503-row table and zero absent seals.

Three certified seals are far too small a pool to fire the frozen prospective predictions P1 to P4 in [PREDICTIONS.md](../2026-10-20-seal-legend-units/PREDICTIONS.md). At three single-line seals, P2 has **0.000** power, P1 passes **50.2%** of the time on shuffled signs, P3 passes **100%** of the time even on formulaic openings, and the P1 kill condition is inactive. Firing the post-catalogue shot now would spend the pool on an uninformative test. Reaching a decisive test requires either plate checks across the smaller post-catalogue sites plus acquiring the *Man and Environment* 35 PDF, or resolving the 207 blocked Dholavira rows through an ICIT crosswalk ([REQUEST-ICIT-Q1011.md](REQUEST-ICIT-Q1011.md)), or acquiring CISI 3.1.

## Certification counts across the 503 and 358 rows

Every row of [objects.csv](../2026-10-21-post-catalogue-finds/objects.csv) (503 rows) joins one-to-one with `fresh-cohort-v1.json` and `fresh-cohort-v1.csv`. The 145 rows already catalogued in CISI 1 or 2 sit outside the 358-row audit in `data/raw/2026-10-22-candidate-identity-exposure/run-v3/reconciled-dispositions.csv`; the remaining 358 rows reconcile one-to-one across both inventories.

| Certification tier | All 503 rows | Within 358 audit | Seals | Sealings | Tablets | Pottery | Tools and other |
|---|---:|---:|---:|---:|---:|---:|---:|
| `certified_absent_sealed` | 8 | 8 | 3 | 3 | 2 | 0 | 0 |
| `conditionally_absent_needs_plate_check` | 88 | 88 | 30 | 11 | 2 | 37 | 8 |
| `blocked_by_alias_ambiguity` | 230 | 230 | 147 | 51 | 3 | 27 | 2 |
| `already_present_or_exposed` | 177 | 32 | 63 | 5 | 65 | 2 | 42 |
| **Total** | **503** | **358** | **243** | **70** | **72** | **66** | **52** |

Source: [summary-v1.json](summary-v1.json) and [fresh-cohort-v1.csv](fresh-cohort-v1.csv).

The 177 `already_present_or_exposed` rows break down into five exact groups: 145 objects catalogued in CISI 1 or 2, one Mohenjo-daro rod flagged as possibly in CISI 3, 24 post-catalogue rows with verified Lipi identifier matches, five Farmana objects (four seals and one sealing, `PCF-FRM-001` through `PCF-FRM-005`) independently verified as Lipi families 149 to 153 in [2026-10-20-fresh-test-collection](../2026-10-20-fresh-test-collection/REPORT.md), and two Bagasra rows (`PCF-GDH-013` and `PCF-GDH-014`) whose cited page carries a recorded historical image display in the 22 October exposure audit.

The 230 `blocked_by_alias_ambiguity` rows come from two structural bottlenecks. At Dholavira, 207 post-catalogue rows cannot be separated from the local export's 230 Dholavira families because 187 of those local families carry no excavation registration. This total includes `PCF-DHV-141` (registration 33693, grid square `35x63x4`, Lower Town, Stage VI), which the October inventory listed as absent after filtering on area name. Re-checking all 230 local Dholavira families shows that unregistered rectangular seal family `4277` sits in the exact grid square `35 x 63 x 4` and Period `6` under the adjacent label `Middle Town-`, and eight further unregistered Dholavira seal families carry no spatial coordinates at all. Without an accession crosswalk, `PCF-DHV-141` stays blocked. The other 23 blocked rows are Surkotada potsherds from Joshi (1990) that compete against four unnumbered CISI 1 Surkotada potsherds.

The 88 `conditionally_absent_needs_plate_check` rows consist of two parts. First, 17 rows are verified absent from Lipi but fail one sealing requirement: eight have uncertain inscription status (`PCF-BTD-001`, `PCF-DHL-001`, `PCF-GDH-009`, `PCF-GDH-010`, `PCF-IDN-001`, `PCF-KNM-005`, `PCF-KNM-016`, `PCF-KNM-017`), one is a secondary unillustrated IAR duplicate of `PCF-GDH-002` (`PCF-GDH-012`), two have only OCR text files locally with no PDF or image file (`PCF-MTL-001` at Mitathal in *Man and Environment* 35 and `PCF-BTD-002` at Bet Dwarka in *Man and Environment* 22–23), two cite no plate (`PCF-NGW-001` at Nagwada and `PCF-SKP-003` at Shikarpur), two have interleaved image-only plate leaves in scanned IAR PDFs whose captions lack an OCR text layer (`PCF-GDH-008` in IAR 1995–96 PDF pages 27–29 and `PCF-GDH-011` in IAR 1996–97 PDF pages 32 and 34), and two cite a Bhirrana tool figure (`PCF-BHR-002` and `PCF-BHR-003`, `fig. 2[1]`) not located by blind caption search in IAR 2003–04. Second, 71 rows belong to small local-corpus sites (Bhirrana, Khirsara, Kanmer, Rakhigarhi, Shikarpur, Rupar, Tarkhanewala Dera, Baror, Karanpura, Ganweriwala, Nuhato and Farmana `PCF-FRM-006`) where a direct plate check against one to seven local objects can resolve absence.

## The eight certified absent sealed objects

All eight certified objects have definite reported inscriptions post-dating CISI 1 or 2, zero overlap with any local family or spent split, no recorded inscription-image display, and a held PDF on disk whose SHA-256 matches `source-register.csv` and whose plate or figure page carries both a matching caption token and embedded raster imagery.

| Row ID | Site | Class | Registration | Held source | Cited plate or figure | Verified PDF page | Absence proof basis |
|---|---|---|---|---|---|---:|---|
| `PCF-DHL-002` | Dhalewan | seal | `1371` | `new-dhalewan-report.pdf` | `Pl. 6.1` | 294 | Zero Lipi and CISI entries at Dhalewan |
| `PCF-GDH-002` | Gola Dhoro (Bagasra) | seal | `BSR 5555` | `gdh-jamison-2017.pdf` | `Figure 6` | 9 | All 6 Bagasra Lipi seals carry distinct `BSR` registrations |
| `PCF-JKR-001` | Juni Kuran | seal | none published | `iar-2004-05.pdf` | `pl.13` (`Plates 13-14`) | 42 | Zero Lipi and CISI entries at Juni Kuran |
| `PCF-DHL-003` | Dhalewan | sealing | `890` | `new-dhalewan-report.pdf` | `Pl. 6.3` | 298 | Zero Lipi and CISI entries at Dhalewan |
| `PCF-SKP-005` | Shikarpur | sealing | none published | `SHIKARPUR2009.pdf` | `fig 4d` (`Fig. 4`) | 8 | Zero Shikarpur sealings in Lipi and CISI |
| `PCF-SKP-006` | Shikarpur | sealing | none published | `SHIKARPUR2009.pdf` | `fig.4c` (`Fig. 4`) | 8 | Zero Shikarpur sealings in Lipi and CISI |
| `PCF-LKD-001` | Lakhanjo-daro | tablet | none published | `lkd-biagi-2022.pdf` | `Fig. 8: 12` (`Figure 8`) | 13 | Copper tablet; both Lakhanjo-daro Lipi tablets are terracotta |
| `PCF-SKP-007` | Shikarpur | tablet | none published | `SHIKARPUR2009.pdf` | `fig.4a` (`Fig. 4`) | 8 | Zero Shikarpur tablets in Lipi and CISI |

Source: [summary-v1.json](summary-v1.json) and `data/raw/2026-11-23-fresh-cohort-certification/pdf-access-log.jsonl`.

Each certified object retains its participant-scoped exposure history from [2026-10-22-candidate-identity-exposure](../2026-10-22-candidate-identity-exposure/REPORT.md). None of the eight objects was ever read by the 20 October `seal-legend-units` model or scored in `bench/spent.json`. Four (`PCF-LKD-001`, `PCF-SKP-005`, `PCF-SKP-006`, `PCF-SKP-007`) have only identity or bibliographic display recorded. The other four (`PCF-DHL-002`, `PCF-DHL-003`, `PCF-GDH-002`, `PCF-JKR-001`) sat on pages screened by `gpt-6.1-sol` extraction runs on 21 October for text-layer metadata. Any blind transcription of those pages must therefore assign fresh transcribers outside the 21 October Codex extraction sessions.

## Statistical power against frozen predictions P1 to P4

We evaluated the certified seal cohort and five expansion scenarios using the exact bounds in [predictions.json](../2026-10-20-seal-legend-units/predictions.json) and the simulation model in [make_predictions.py](../2026-10-20-seal-legend-units/make_predictions.py) (40,000 draws for P1 and P3; 20,000 multinomial draws for P2; exact binomial tail for P4).

| Pool scenario | Single-line seals | P1 bound (pass if H rate / shuffle null) | P1 kill active | P2 power (H rate / null) | P3 upper bound (H rate / 0.90 formulaic) | P4 expected divided faces |
|---|---:|---|---|---:|---|---:|
| Certified sealed (60% yield) | 2 | 0.000 (1.000 / 1.000) | No | 0.000 / 0.000 | 1.000 (1.000 / 1.000) | 0.08 |
| Certified sealed (100% yield) | 3 | 0.333 (0.986 / 0.502) | No | 0.000 / 0.000 | 1.000 (1.000 / 1.000) | 0.13 |
| Plus Mitathal PDF (`PCF-MTL-001`) | 4 | 0.250 (0.997 / 0.603) | No | 0.000 / 0.000 | 0.667 (0.995 / 0.277) | 0.17 |
| Plus Bhirrana (2) and Khirsara (5) lower bound | 11 | 0.455 (0.995 / 0.059) | No | 0.093 / 0.012 | 0.500 (0.995 / 0.005) | 0.46 |
| Minimum full-weight threshold | 20 | 0.550 (0.990 / 0.001) | Yes | 0.215 / 0.023 | 0.429 (0.996 / 0.000) | 0.83 |
| Reference expected pool (`PREDICTIONS.md`) | 50 | 0.620 (0.991 / 0.000) | Yes | 0.570 / 0.034 | 0.333 (0.995 / 0.000) | 2.08 |

Source: [summary-v1.json](summary-v1.json), `P1_to_P4_power_analysis`.

The power table settles the strategic question cleanly. At $n = 3$ (or $n = 2$ under the 60% single-line completeness yield seen in CISI 3.1), exact one-sided McNemar $p < 0.05$ is algebraically unreachable because even $b = 4, c = 0$ yields $p = 0.0625$, so P2 has zero power until $n \ge 5$. At $n = 3$, P1 passes half the time on random sign permutations and P3 passes unconditionally. Only when the fresh seal pool reaches roughly 11 to 20 single-line legends do P1 and P3 cleanly separate from their nulls, and only at $n \ge 20$ does P1's kill rule take effect with full credence weight.

## Method, blinding assumptions and verification

This audit froze [PROTOCOL.md](PROTOCOL.md) (`PROTOCOL.sha256` `ffeba2bbec064b196915cdf2b58e3aac74de215650a3afa54c2d807add206902`) before opening any candidate row or PDF. All shared assumptions stay explicit: we treat Lipi families as provisional objects, accept absence only when site exhaustion, site-and-type exhaustion, or exhaustive registration or material disjointness excludes every local family, and refuse to accept prose pages without embedded images as verified plates.

The deterministic pipeline ([code/certify_fresh_cohort.py](code/certify_fresh_cohort.py)) logged all 27 PDF checks to `data/raw/2026-11-23-fresh-cohort-certification/pdf-access-log.jsonl` with zero sign sequences read and zero images displayed to any agent. Independent verification ([code/verify.py](code/verify.py), results in [verification-v1.json](verification-v1.json)) passed **10 of 10** checks, confirming all 19 source hashes, exact 503-row and 358-row bijections, zero overlap between the 8 certified objects and Lipi (4,695), Mackay and Marshall (1,146), CISI 1 and 2 basic data (3,680 rows, 2,602 joined) or `bench/spent.json`, verified embedded raster imagery on every certified PDF page, absence of `prospective-access.jsonl`, and exact agreement with `predictions.json`.

To address the structural gaps that cap the non-purchase pool at three seals, we also prepared two unsent institutional access drafts for maintainer approval: [REQUEST-ICIT-Q1011.md](REQUEST-ICIT-Q1011.md) (targeting ICIT's Dholavira excavation-number crosswalk and corpus baseline) and [REQUEST-HARP-Q1017.md](REQUEST-HARP-Q1017.md) (targeting HARP excavation units, lots, deposit types and the disputed H-2587 and lots 3166 and 8796 records).

## Boldest supported claim and blind-transcription protocol for the first fresh shot

Our boldest supported claim is that held, zero-purchase post-catalogue publications already supply **eight genuinely absent, unspent Indus inscribed objects** with verified local PDF plates (**three seals, three sealings and two tablets**, alongside Farmana's 15 separately reserved marked sherds), **but cannot by themselves support a decisive prospective test of P1 to P4** until plate checks on the small-site candidates (Bhirrana, Khirsara, Shikarpur, Baror, Karanpura, Rakhigarhi, Tarkhanewala Dera and Nuhato) and either an ICIT Dholavira crosswalk or CISI 3.1 expand the certified seal pool from 3 to at least 20 single-line legends.

When the certified fresh seal pool reaches at least 11 (for a preliminary half-weight P1 and P3 test) or 20 (for the full-weight P1–P4 test with kill condition active), execute the first fresh shot under the following blind-transcription protocol:

1. **Freeze the cohort manifest**: hash the final list of `certified_absent_sealed` seal `row_id`s and their exact verified PDF page numbers into a new dated experiment directory before rendering a single crop.
2. **Assign two independent unexposed transcribers**: recruit two human or fresh model transcribers who had zero access to the 21 October extraction logs or the 20 October closing-stock files (`closing-stock.json` and `inventory.json`). Give them only cropped photographs or drawings of the sealed plates, the standard Wells sign chart, and the instruction to output `lines_reading` (Wells sign numbers in reading order, `000` for illegible signs, `[` and `]` for damaged edges) and `direction`.
3. **Adjudicate transcription agreement while still blind**: compare the two independent transcriptions on sign codes, line divisions and completeness; resolve disagreements solely from the plate image before unlocking the scorer, and record exact inter-transcriber agreement.
4. **Fire one frozen read**: run `python -P experiments/2026-10-20-seal-legend-units/score_prospective.py --pool post_catalogue --input <sealed-jsonl> --out <dated-result.json>` exactly once, letting the script verify `PREDICTIONS.sha256` and append the read to `prospective-access.jsonl`, and then record the spent family in `bench/spent.json`.
