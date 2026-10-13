# Protocol: data inventory, 12 October 2026

Written before any coverage was computed. The owner asked for one page listing the data the project holds, the data that exists elsewhere, and the metadata available for each inscribed object. From this date the project's first priority is complete data with as much sourced metadata per object as possible. This package measures the present state and ranks the acquisitions that would improve it. It is an inventory with verified computation; it tests no hypothesis about the script.

## Questions

1. Which sources does the project hold, in what version, size, location and rights status?
2. For each metadata field, what share of objects and faces in the local corpus carries a usable value, by object type and by site? Where are the values placeholders, and where do sources or faces disagree?
3. Which known sources are not held or only partly held, what would each add per object, and what does each cost to acquire?
4. What object record should the project aim for, and which source best fills each field?

## Units

A **face** is one row of the pinned Lipi export (`data/normalized/lipi_observed_faces.jsonl`, 5,680 rows), as earlier packages define it. An **object** is one provisional family (`object_family_id`, 4,695 values). Earlier audits showed that families group face rows by the export's numbering; physical identity across catalogues has not been adjudicated, so object counts are provisional. Object type uses the export's raw `type` value, grouped into seal, bas-relief tablet, incised tablet, copper tablet, tag or sealing, pottery and other. The raw value is kept in the full output. Site uses the export's `site` value; the six largest sites are reported separately and the rest pooled, with every site in the full output.

## Usable-value rules

A value is **usable** when it is non-empty after trimming and is not a placeholder. Placeholders are `-`, `--`, `- -`, `?`, `??`, `Unknown`, `unknown`, and a dimension of `0` or `0.0`. `None` in the motif fields (`symbol`, `cult`) is an asserted absence, as the catalogue caveats record; it counts as usable and is reported separately. A depth such as `-3.0 ft` is usable; `surface -` is usable and flagged as a surface find. Placeholder frequencies are reported per field.

An object has a usable value when any of its faces has one. An object has a **conflict** when its faces carry two or more distinct usable values for the same field after case and whitespace normalization. Dimensions are usable when at least one of the three millimetre fields is positive; all-three coverage is reported separately. The inch-style fields `h`, `v`, `th` are compared with the millimetre fields at 25.4 mm per inch, with a tolerance of 0.6 mm, to test whether the millimetre values are conversions.

Derived fields: an object has a **photograph in the local Lipi image set** when its raw CISI key appears in `data/lipi/src/assets/data/seal_id_and_image_mapping.json` and at least one indexed file exists. An object has a **museum or accession value** when the older Indus website export (`data/normalized/indus_website_observed.jsonl`) has a non-empty `MUSEUM` value for the same raw CISI key. No local file carries a calendar date, radiocarbon link, item-level licence or bibliography field; these are reported as structurally absent.

## Cross-source comparisons

For CISI keys present in both Lipi and the older website export, compare site, material and dimensions. For Mayig faces, compare site with Lipi by CISI key. Report agreement, disagreement and incomparable counts. These are internal-consistency checks among derivatives of shared sources; agreement does not verify a value against the object.

## Holdings

Walk `data/`, `research/literature/sources/`, `research/corpus/primary/`, `results/` and `output/` and count files and bytes by package and extension. Hash every PDF with SHA256 to count distinct documents. Harvest records that carry a title and a URL or local path from every `sources.json` and acquisition record under `experiments/`, to estimate how many distinct sources earlier packages acquired. The harvest is heuristic: schemas differ between packages. The complete file list and harvested index stay local under `data/raw/2026-10-12-data-inventory/` because they name third-party files; tracked outputs hold counts.

## Sources not held

Start from the evidence census (`experiments/2026-10-06-evidence-census/`), the dataset landscape (`experiments/2026-10-02-dataset-landscape/`) and package source records. Check uncertain or recent items on the web on 12 October 2026. Record every consulted page in `sources.json` with its exact title, URL, whether it was opened or only seen in a search snippet, and the access date. Earlier package findings stay attributed to those packages.

## Outputs

- `run-2026-10-12/`: `summary.json`, `field-coverage-overall.csv`, `field-coverage-by-type.csv`, `field-coverage-by-site.csv`, `placeholders.csv`, `conflicts.json`, `cross-source.json`, `holdings-summary.json`, `literature-harvest-summary.json`, `input-hashes.json`.
- `data/raw/2026-10-12-data-inventory/`: full file listing, PDF hash table and harvested source index; saved web witnesses.
- `knowledge/DATA.md`, `data/MANIFEST.json`, `tools/fetch_data.py` and question cards `knowledge/questions/Q-1001` onward.

No output contains inscription texts, sign sequences, record-level corpus rows or source images. Runs write to new directories and refuse to overwrite existing ones. The shared registry is not edited; `registry-entry.json` proposes an entry.

## Decision rules

A source counts as **held** when a local file with a recorded hash exists and its content matches the named edition (title page or recorded identity check). It counts as **partly held** when only an excerpt, API snapshot, search view or one of several volumes is local. Priorities rank acquisitions by the number of objects gaining a field, the open questions and conjecture cards that depend on them, and feasibility (public access, cost, rights). The ranking is a judgement recorded with its reasons.
