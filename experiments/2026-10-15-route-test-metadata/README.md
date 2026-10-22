# What the empty motif values on seals mean (Q-0009 pilot)

Status class `source-review`; verification tier `submitted`. 15 October 2026. Contributor: Claude Code (Claude Opus 5.5) in the Claude desktop app, working as a newcomer for the [route test](../2026-10-15-route-test/REPORT.md). Question: [Q-0009](../../knowledge/questions/Q-0009-distinguish-missing-motif-from-no-motif.md). Registry entry: [ATTEMPT-0001](../../knowledge/registry/attempts/ATTEMPT-0001.json).

## Result

In the Lipi export, `None` in the motif field means "no motif" on rectangular seals and does not on square seals. All 8 sampled rectangular seals marked `None` carry one row of signs and nothing else. Of 12 sampled square seals marked `None`, 6 are broken or worn where the animal would be, 5 carry signs only and 1 shows a device below its signs. The placeholder `-` behaves like `None` on square seals, covering fragments and worn faces, and it also hides at least one recorded animal: M-1005 carries a large animal under a round device on a stand. The 12 October inventory counted every `None` as a recorded absence. With `None` accepted only on rectangular seals, seal motif coverage falls from 2,110 of 2,239 seal objects (94.2%) to 2,013 (89.9%), and 97 seal objects move from "no motif" to "unknown".

The practical consequence is for motif analyses. A comparison that treats square seals marked `None` as text-only seals mixes in damaged seals whose motif field can no longer be seen, and half of the sampled ones are of that kind.

## Method

The [protocol](PROTOCOL.md) was written and hashed ([PROTOCOL.sha256](PROTOCOL.sha256)) before any photograph was viewed. [sample.py](sample.py) counts every motif label by object type and draws a fixed sample of seal faces that have a photograph of their own side in the 13 October [face-image index](../2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv), ordered within six strata by the SHA-256 of a salted record id. One reader looked at each CISI crop and coded it `motif-present`, `motif-absent` or `not-decidable`, with a confidence and a note ([observations.csv](run-2026-10-15/observations.csv)). Thirteen small or dark crops were viewed at two or three times their size with automatic contrast; the protocol did not anticipate this and the flag is recorded per crop. For four faces whose large forms could be signs or a device (K-52, K-54, L-56, Sktd-2), the number of signs the export transcribes was used as a check on the reading. [score.py](score.py) counts the codes, computes exact 95% intervals and applies the decision rules fixed in the protocol ([results.json](run-2026-10-15/results.json)).

The inputs are local-only: `data/normalized/lipi_observed_faces.jsonl` (SHA-256 `1220f559…`, the file the 12 October inventory measured) and the crops in `data/lipi/public/seal_images/`. Their hashes are in [input-hashes.json](run-2026-10-15/input-hashes.json), and the crops' hashes are in [sample.csv](run-2026-10-15/sample.csv). No crop or transcription is copied into the package.

```text
python experiments/2026-10-15-route-test-metadata/sample.py --faces <local lipi_observed_faces.jsonl> --out experiments/2026-10-15-route-test-metadata/run-2026-10-15
python experiments/2026-10-15-route-test-metadata/score.py --faces <local lipi_observed_faces.jsonl> --run experiments/2026-10-15-route-test-metadata/run-2026-10-15
```

## Readings by stratum

| Stratum | Seals | Label | Faces in population | Sampled | Present | Absent | Not decidable | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---|
| A | square | `None` | 76 | 12 | 1 | 5 | 6 | mixed |
| B | square | `-` | 58 | 8 | 1 | 2 | 5 | mixed |
| C | rectangular | `None` | 365 | 8 | 0 | 8 | 0 | asserted absence |
| D | no shape code | `-` | 53 | 4 | 0 | 0 | 4 | mixed |
| E | any | `?`, `Unknown` | 5 | 2 | 0 | 0 | 2 | mixed |
| K (control) | square | named motif | 1,639 | 4 | 4 | 0 | 0 | method passes |

The verdict rule required at least 90% `motif-absent` among at least five decidable crops for an asserted absence, and at least half `motif-present` for a missing value; anything between is mixed and maps to unknown. The interval on the share of rectangular `None` faces with a motif is 0 to 0.37, so a sample of eight rules out a majority of hidden motifs but not a minority. Seven of the 21 decidable readings are low confidence; dropping them leaves stratum C unchanged, stratum A without enough decidable crops to judge and stratum B with only M-1005, whose animal is certain. Two of the four controls (M-1046, a fragment, and H-606, a dark print) needed enlargement before the animal could be seen, so on these crops a worn face can hide a motif from this reader as well as from the cataloguer.

## Mapping and coverage records

[mapping-v1.json](mapping-v1.json) assigns each label and seal type one of three statuses: `recorded`, `asserted-absent` or `missing-unknown`. `None` is `asserted-absent` only on rectangular seals. `None` on square seals, the 31 `None` objects of other or unrecorded seal shapes, and every `-`, `?` and `Unknown` are `missing-unknown`. Tablets, tags, sealings, pottery and the `cult` field are outside the pilot; their 2,161 `None` faces keep the 12 October rule, unverified.

The package records its coverage change in [DATA-UPDATE.md](DATA-UPDATE.md) and [manifest-additions.json](manifest-additions.json), and its card change in [question-updates.md](question-updates.md), for maintainers to fold in after merging. The claim text for the question's issue is in [CLAIM.md](CLAIM.md).

## Boldest reading and the test that decides it

The cataloguers wrote `None` for "no animal seen", whether the seal never had one or lost it: on square seals the label marks damage as often as design. If that holds across the whole block, the 76 square faces marked `None` split roughly evenly between text-only seals and damaged animal seals, and text-only square seals are rarer than the export implies. The deciding test is a blind second reading of all 76 square `None` faces and the 58 square `-` faces against their crops, with the same codes. The reading is refuted if fewer than a quarter of those faces are `not-decidable` or `motif-present`. The same pass should settle M-1005's animal against the CISI 2 plate and check the 31 unsampled `None` seals of other shapes.

## Retrospective

[RETROSPECTIVE.md](RETROSPECTIVE.md) records what went wrong and how it was handled.
