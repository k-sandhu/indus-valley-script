# Shot B: a working reading of the inscriptions

Recorded 12 October 2026 before any outcome of this shot was computed.

## Conjecture

Indus inscriptions are built from a small number of word classes: numerals, counted units or commodities, titles and offices, closing markers, and the elements of personal or group names. The commonest signs can be assigned to these classes and given working English glosses, and the resulting reading of seal legends, tablets and pottery marks predicts properties of the inscribed objects that the reading was not built from.

Starting credence: 0.15 that a gloss map built this way stands clear of its own rearrangements on the withheld variables. The shot revises it before freezing predictions and again after the confirmation outcome.

## Construction evidence and withheld variables

The gloss map may use the picture each sign shows (component descriptions in `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv`, the licensed 1979 chart crops under `output/chart_atlas/`, and the October 11 catalogue), the behaviour of signs inside texts (position, neighbours, stroke numerals, recurring segments) and the object type that carries each text.

These variables are withheld from construction in both halves until `PREDICTIONS.md` is frozen: seal and object dimensions, field animal and cult object (`symbol`, `cult`), site and region, material, period, phase and every find-context field. Load data with `shots_common.load_half("discovery", strip=...)` removing them; keep `object_type`. Do not read Shot A's directory or the size and motif outputs of earlier packages while building the map.

## Exploration on the discovery half

Assign a class and a working English gloss to every sign with at least ten occurrences in the discovery half, and leave the rest as unassigned or as members of a class without a gloss. Write the grammar the map implies for seal legends, tablets and pottery marks, and gloss representative texts as structural readings. Previous projects' meanings may be adopted or rejected with a reason; the October 8–12 Sanskrit catalogues are one source, not a constraint. Be as specific as the evidence allows and bolder where it is silent: a gloss that can fail is worth more than a safe category.

## Predictions to freeze

Each class in the map implies something about the withheld variables. Examples: name elements should be more specific to site than titles; titles or grade terms should sit on larger seals; a sign glossed as naming an animal or emblem should accompany that field animal; counted commodities should be commoner on objects of one material or period. `PREDICTIONS.md` states every such implication with its direction, statistic and population on the confirmation half, then combines them into one score. The primary test compares that score with the scores of at least 1,000 rearrangements of the class and gloss labels among signs of similar frequency and position; the map passes if it exceeds the 95th percentile, and the report gives its distance from the rearrangement mean in standard deviations. Each implication is also reported individually.

Name the kill condition and add prospective predictions, such as the expected glossed reading of newly published texts of a given object type.

## Records

Public files hold the gloss map, the grammar, aggregate scores and object identifiers. Glossed readings of full acquired texts stay in `data/raw/2026-10-12-conjecture-shots/shot-b-reading/`; public prose may quote at most ten texts of three signs or fewer, cited by CISI number.
