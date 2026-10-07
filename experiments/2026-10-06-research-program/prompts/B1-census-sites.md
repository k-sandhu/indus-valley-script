# Package B1: census of Indus inscribed evidence by site and publication

Owned directory: `experiments/2026-10-06-evidence-census/sites-and-publications/`. Local raw directory: `data/raw/2026-10-06-evidence-census/sites-and-publications/`. Use live web search.

## Question

Is all findable evidence for the Indus script indexed somewhere, and with how much metadata? This package covers the evidence as excavated and published: every site that has yielded objects with Indus signs, the publications that report those objects, how many objects each reports, and which metadata each source provides. A parallel package (B2) covers museum collections, digital datasets and image archives; a later synthesis joins both.

## Starting points

Read `experiments/2026-10-02-dataset-landscape/` (README, `landscape.json`, `SCHEMA.md`, `DATASET_PLAN.md`); it is uncommitted earlier work, so read it without editing. Read `knowledge/provenance/SOURCES.md`, `knowledge/provenance/catalogue-caveats.md` and the source frames for Harappa, Lothal and Kanmer under `experiments/2026-10-02-six-hour/`. Count the local corpus by site from `data/normalized/lipi_observed_faces.jsonl` (field `site`, 78 values) and `data/normalized/mayig_faces.jsonl`, and use those counts as the comparison column.

## What to build

A site register (`site-register.json` and `.csv`) with one row per site, covering the core Indus region (Pakistan, India, Afghanistan) and finds abroad (Mesopotamia, Iran, the Gulf, Oman, Central Asia and elsewhere). Include sites missing from the local corpus, particularly excavations reported after the CISI volumes, such as later seasons at Rakhigarhi, Dholavira, Kanmer, Khirsara, Kotada Bhadli, Farmana, Bhirrana, Binjor, Lakhan-jo-daro, Ganweriwala and Harappa after 2007. For each site record: country; coordinates if published; excavation campaigns; primary reports and corpus volumes (exact titles and pages, including CISI volume and page ranges where they exist); the number of inscribed objects each source reports, with object types and the count basis; whether the source gives findspot, stratum or phase, absolute dates, dimensions, material, photographs or drawings, and museum or excavation registration numbers; digital availability and stated reuse terms; and the local corpus count.

A publication register (`publication-register.json`) listing every corpus volume, excavation report and catalogue found, with its coverage, metadata fields and access.

A gap list (`unindexed-evidence.json`) naming inscribed finds reported in the literature (news reports, excavation summaries such as *Indian Archaeology – A Review*, conference papers) that are absent from the CISI volumes, ICIT's published counts or the local corpus, with source and the observable evidence for each.

## Method notes

Keep count bases separate: objects, faces, texts, sign occurrences and photographs are different denominators, and the same object can appear under several catalogue numbers. Do not add counts across overlapping corpora. Record the date of each count and its source page. Where a figure comes only from a news report or a snippet, mark it that way. Prefer primary reports and official records; record failed searches and inaccessible sources. Report the total number of sites, how many have a primary report you could identify, and the share of sites and objects with each metadata field available.

`REPORT.md` should state what fraction of reported inscribed evidence appears in accessible indexes, which metadata fields are most often missing, and the largest unindexed pools, with exact numbers and their bases.
