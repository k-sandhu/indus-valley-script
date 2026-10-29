# Protocol: what the empty motif values on seals mean (Q-0009 pilot)

Written on 15 October 2026 before any photograph in the sample was viewed. Contributor: Claude Code (Claude Opus 5.5), desktop app, working as a newcomer for the route test in [../../maintenance/2026-10-15-route-test/](../../maintenance/2026-10-15-route-test/). Status class on completion: `source-review`.

## Question and why it is open

[Q-0009](../../knowledge/questions/Q-0009-distinguish-missing-motif-from-no-motif.md) asks whether the motif fields of the pinned Lipi export separate a seal that carries no animal or scene from a seal whose motif was never recorded. The 12 October data inventory fixed a rule for this without checking it against the objects: its [protocol](../2026-10-12-data-inventory/PROTOCOL.md) treats `None` in `symbol` and `cult` as an asserted absence that counts as a usable value, and treats `-`, `?` and `Unknown` as placeholders. Under that rule `None` is the commonest value of `symbol` (2,635 of 5,680 faces) and lifts motif coverage to 89.4% of objects ([DATA.md](../../knowledge/DATA.md), section 2). If `None` on a seal often hides an animal that is visible on the photograph, both the coverage figure and every motif comparison that reads `None` as "text only" are wrong. Neither prior attempt named on the card ([SIGN-CONTEXT-SEALS-01](../../knowledge/registry/attempts/SIGN-CONTEXT-SEALS-01.json), [OBJECT-LEDGER-PILOT-01](../../knowledge/registry/attempts/OBJECT-LEDGER-PILOT-01.json)) compared the placeholder labels with the photographs.

## Inputs

All inputs are local-only and stay local. The worktree used for this run has no `data/` directory, so the inputs are read from the maintainer's checkout at `../../../data/` relative to the worktree root, and their hashes are recorded in the run directory.

- `data/normalized/lipi_observed_faces.jsonl`, SHA-256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`, the file the 12 October inventory measured.
- The face-level image index of 13 October, [face-image-links.csv](../2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv) (tracked), which links each face to its CISI photograph crops and records whether a crop shows the face's own side (`relation = face-side`) and whether it is a photograph of the object or of an impression (`kind`).
- The crops themselves, `data/lipi/public/seal_images/<file>`, viewed one at a time.

## Population and fixed sample

The population is every seal face (export `type` beginning `SEAL`). For each face the motif label is the `symbol` value. A face is eligible for the sample when the image index links it to at least one crop with `relation = face-side` and `kind = object`; for each sampled face we view the first such crop in file-name order.

The sample has six strata. Within a stratum, eligible faces are ordered by the SHA-256 of `Q-0009-2026-10-15|` followed by the face's `record_id`, and the first n are taken.

| Stratum | Seal type | `symbol` value | n |
|---|---|---|---:|
| A | `SEAL:S` (square) | `None` | 12 |
| B | `SEAL:S` | `-` | 8 |
| C | `SEAL:R` (rectangular) | `None` | 8 |
| D | `SEAL` (no shape code) | `-` | 4 |
| E | any seal | `?` or `Unknown` | all eligible |
| K | `SEAL:S` | any named motif | 4 (control) |

Stratum K checks that the reader can see a motif on these crops at all. The counts of eligible faces per stratum were seen before this protocol was written; no image was.

## What is recorded for each crop

One code per crop, read by eye:

- `motif-present`: an animal, scene, plant or other pictorial device, beyond signs, border lines and strokes, is visible on the face.
- `motif-absent`: the whole face is visible and carries only signs, with or without a border.
- `not-decidable`: the face is broken, worn or cut off where a motif would be, the crop shows another side or the boss, or the image is too small to judge.

A short free-text note records what is seen, in our words. Motif names are not assigned; this pilot asks only whether a motif is there.

## Decision rules

For each stratum we report the counts of the three codes and, for the share of decidable crops coded `motif-present`, an exact Clopper–Pearson 95% interval.

- A label behaves as an asserted absence in a stratum when at least 90% of its decidable crops are `motif-absent` and at least five crops are decidable.
- A label behaves as a missing value when at least half of its decidable crops are `motif-present`.
- Anything between is mixed, and the label maps to "unknown" in that stratum, because Q-0009 rejects any normalization that merges a recorded absence with an unknown observation.
- If fewer than three of the four control crops are coded `motif-present`, the reading method fails and no stratum is interpreted.

The output is a versioned mapping from each label and seal type to a value status (`asserted-absent`, `missing-unrecorded`, `missing-unknown`) and a reason, together with the coverage figure the mapping implies for `symbol` on seals.

## Stopping rule and scope

Stop after the 34 sampled crops plus the census of stratum E. The pilot covers seals only; `None` on tablets, tags and pottery, and the `cult` field, are counted but not checked against photographs. A wider block or a second reader is the next step and is named in the report.
