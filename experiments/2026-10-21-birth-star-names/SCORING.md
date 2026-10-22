# Scoring the birth-star predictions on fresh seals

These instructions are for whoever acquires seal texts that no analysis in this project has used. The predictions, the scorer and its reference data were frozen on 21 October 2026 at 03:36 UTC ([freeze record](freeze-v1.json), [hashes](PREDICTIONS.sha256)). Check the hashes before scoring; a changed file means the frozen test no longer exists, and a revised test needs a new dated package.

## Which objects count

An object counts when it is a seal (object type beginning `SEAL`) whose text was not in the pinned corpus `data/normalized/lipi_observed_faces.jsonl` (SHA-256 `1220f559…`). Two sources are expected to supply such seals:

- **CISI 3.1 and 3.2.** The [range-coverage package](../2026-10-13-cisi3-range-coverage/README.md) lists 1,127 catalogue numbers absent from the corpus, 244 of them between seals, tablets or sealings in CISI 3.1 and 73 in CISI 3.2 (`run-2026-10-13/absent-numbers.csv`). Classify every absent number from its photograph, as that package proposes, and transcribe each absent seal. Numbers M-1931–1952 lie in a block of Mohenjo-daro seals; H-1205–1258 lies inside a block of tablets and will contribute few seals.
- **Objects published after the catalogues.** [Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md) lists the sites and reports. The 225 Dholavira seals outside CISI would supply most of the material if their texts are published legibly. Objects reserved by the [fresh-test collection](../2026-10-20-fresh-test-collection/REPORT.md) are eligible when that program's reservation rules allow them to be opened.

Do not add objects chosen because they carry fish signs; take every legible seal in each source block, so that the share of legends with fish runs is not inflated. Record seals without fish signs too: they supply the opening vocabulary for P1.

## How to transcribe

Write one JSON object per inscribed face to a new JSONL file under `data/raw/YYYY-MM-DD-<package>/`, with these fields:

| Field | Content |
|---|---|
| `record_id` | Your identifier for the face |
| `source_cisi` | The CISI number when there is one, in the corpus form (`M-1931`, `H-1210`); otherwise empty |
| `signs_reading_rtl` | The signs as Wells numbers (the ICIT sign list used by the corpus), in reading order, right to left |
| `object_type` | Corpus object-type code, beginning `SEAL` for seals |
| `clean_rtl_singleline` | `true` only when the text is complete, legible, written in one line and read right to left |
| `site` | Find site |
| `fresh_source` | Publication, plate or figure and page from which the text was read |

Transcribe from the photograph with a second reader for every sign in the fish family (Wells 219–237 and 240–244, base B220 in `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv`) and for stroke groups directly before a fish. Record disagreements; score with the first reader and report the second reader's result beside it.

## How to score

Run from the repository root with Python 3.13 and NumPy:

```text
python -X utf8 experiments/2026-10-21-birth-star-names/score_fresh.py --fresh data/raw/YYYY-MM-DD-<package>/fresh-faces.jsonl --out experiments/YYYY-MM-DD-<package>/birthstar-score.json
```

The scorer refuses faces whose CISI number or full text is already in the pinned corpus and faces without `fresh_source`, and reports the counts. It reads the pinned corpus only to make that check. It scores only when at least 40 fish runs stand in name position (followed by at least one sign); below that it writes `scorable: false` and nothing else. The first scorable run is the frozen outcome. Later material is a replication: score it with the same code into a new file and report it separately.

## What the outcome means

The output gives each prediction's statistic and pass decision and the credence for [C-0013](../../knowledge/conjectures/C-0013-fish-runs-are-birth-star-names.md) under the frozen joint rule. P2 decides whether the claim survives: if more than 15% of fresh fish runs are of types absent from the discovery inventory, the fish runs are not a closed class and the claim is dead. P3 and P4 decide how far it rises: whether the fresh runs have the evenness and dominant-member share of the Brāhmī asterism names, and whether the four commonest discovery runs keep their share at the new sites. P1 and P5 are the direction note's N1 and N3 as written; both failed on the discovery half. Report every prediction, passed or failed, and enter the outcome and the new credence in the card's record.
