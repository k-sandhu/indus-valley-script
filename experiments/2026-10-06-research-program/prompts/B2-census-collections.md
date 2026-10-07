# Package B2: census of museum collections, digital datasets and image archives

Owned directory: `experiments/2026-10-06-evidence-census/collections-and-datasets/`. Local raw directory: `data/raw/2026-10-06-evidence-census/collections-and-datasets/`. Use live web search.

## Question

Is all findable evidence for the Indus script indexed somewhere, and with how much metadata? This package covers where the objects and their records now sit: museum collections with online catalogues, digital corpora and datasets, and photographic, RTI or 3D archives. A parallel package (B1) covers sites and excavation publications; a later synthesis joins both.

## Starting points

Read `experiments/2026-10-02-dataset-landscape/` (README, `landscape.json`, `SCHEMA.md`, `DATASET_PLAN.md`) without editing it; extend it rather than repeating it. Read `knowledge/provenance/SOURCES.md` and `REDISTRIBUTION.md`.

## What to build

A collection register (`collection-register.json` and `.csv`) with one row per institution holding inscribed Indus objects or impressions, including at least: National Museum New Delhi, the Archaeological Survey of India site museums (Harappa-era sites such as Lothal, Kalibangan, Dholavira, Rakhigarhi), CSMVS Mumbai, Indian Museum Kolkata, Allahabad Museum, the National Museum of Pakistan in Karachi, Lahore Museum, the Harappa and Mohenjo-daro site museums, the British Museum, the Louvre, the Metropolitan Museum of Art, the Penn Museum, the Museum of Fine Arts Boston, the Peabody Museum, the Ashmolean, the Musée Guimet, the Brooklyn Museum, the Cleveland Museum of Art, the Royal Ontario Museum, Berlin's Museum für Asiatische Kunst and Vorderasiatisches Museum, the Iraq Museum, the Bahrain National Museum, the Kuwait National Museum (Failaka), and museums in Iran, Oman, the UAE, Turkmenistan and Afghanistan where relevant. For each: whether an online catalogue exists; a documented search for Indus seals, sealings, tablets or inscribed objects with the query and result count; record fields provided (accession number, findspot, excavation number, date, dimensions, material, photographs and views, bibliography); image and data licence; API or bulk download; and whether objects can be joined to CISI or excavation numbers.

A dataset and archive register (`dataset-register.json`) covering ICIT, Mahadevan's IM77 application and the RMRL resources, Lipi, Mayig, the epachayan repository, Hugging Face, Kaggle, Zenodo, GitHub, harappa.com and HARP material, the Helsinki CISI photographs and editions, Sketchfab or museum 3D scans, RTI captures and any 2024–2026 release. Record content, size with its count basis, metadata fields, licence, versioning and whether the content is original observation or derived from another listed source.

A field matrix (`metadata-field-matrix.csv`) comparing which fields each collection and dataset provides, and a sample audit: for 30 objects that appear both in a museum catalogue and in a corpus (for example British Museum or Met objects with CISI numbers), compare the recorded fields and note disagreements.

## Method notes

Search each collection directly where it has a public search page or API, and save the query, date and raw response in the local raw directory. Keep counts tied to their bases and dates, and mark snippet-only information. Record failed searches and inaccessible catalogues. Do not download images in bulk; a few witnesses per collection suffice to document fields and licence.

`REPORT.md` should say which holdings are openly searchable, how many inscribed objects each exposes online, which metadata fields are most often absent, which collections permit reuse of images or data, and which institutions hold large unindexed groups.
