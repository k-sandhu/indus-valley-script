# Collections and datasets census

The survey found public object records across several museum portals, but it could not establish how many inscribed objects each institution exposes. The register covers **37 collection rows** and **15 dataset/archive entries**. Core live searches were run on 6 October 2026, with targeted source checks on 7 October. The `search_status` field distinguishes institutions surfaced in live search batches from institutions retained as targets without a separate query. Only one numeric total was returned by a direct collection search in this pass: the British Museum's Indus Valley Civilisation term page showed **724 related objects of all types**, so that number is not an inscribed-object count. Harappa.com's secondary museum directory reports 94 Met Indus Valley results, but the live Met total was not retrieved. One Lothal seal record, two Louvre records, two Met object pages, an Indian Museum seal-amulet record and a Cleveland seal record provide individual examples; these records do not form a complete inventory.

The sampled field matrix shows accession numbers on 13 of 37 institution rows, findspots on 10, dates on 13, dimensions and materials on 11 each, photographs on 12, multiple views on 0, bibliography on 5, and excavation numbers on 0. These are counts of fields documented in the records captured for this survey, not estimates of each museum's underlying database. The paired audit validated **0 of 30** planned museum-to-corpus records because no explicit shared join key was established for 30 pairs.

The 2 October dataset landscape supplies the prior ICIT/CISI, Lipi and Mayig baseline. Its prior local audit reported Lipi's **5,680 records / 4,695 provisional families / 19,946 token positions**, and Mayig's **179 faces / 1,003 token positions**. This package reuses those figures rather than recounting the local payload. Andreas Fuls's 2023 ICIT abstract reports **4,665 inscribed objects, 5,650 texts, 17,966 legible sign occurrences and 16,015 photo/drawing images**; these are historical published figures, not a current export ([abstract book, p. 281](https://2023.caaconference.org/wp-content/uploads/sites/29/2023/04/abstract_book_v13.pdf#page=281)).

## Files and reproduction

- [Collection register JSON](collection-register.json) and [CSV](collection-register.csv): 37 institution/group rows, queries, observed fields, rights and access notes.
- [Dataset and archive register](dataset-register.json): 15 corpora, portals and imaging routes, with count bases and derivative/original status.
- [Metadata field matrix](metadata-field-matrix.csv): fields documented in the sampled records.
- [Paired sample audit](paired-sample-audit.csv): 30 sampling slots; none passed the explicit-key join rule.
- [Protocol](PROTOCOL.md), [report](REPORT.md), [retrospective](RETROSPECTIVE.md), [sources](sources.json), and proposed [registry entry](registry-entry.json).
- [Generator](build_registers.py) creates the registers and matrices from the embedded observations.

Run from the repository root:

```powershell
python experiments/2026-10-06-evidence-census/collections-and-datasets/build_registers.py
```

Live-search discovery notes and failed direct downloads are kept in `data/raw/2026-10-06-evidence-census/collections-and-datasets/`. No image collection was downloaded. Counts remain null where a public result total was not captured. The current census does not establish that all findable evidence is indexed.
