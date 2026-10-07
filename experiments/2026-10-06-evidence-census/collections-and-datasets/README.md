# Collections and datasets census

The depth pass still cannot answer that all findable Indus-script evidence is indexed. It now records a dated search method and outcome for all **37 collection rows**. Exact upstream HTTP status was captured for **11 rows** (7 returned 200, 1 returned 403, 1 returned 410, and 2 returned 429); the other 26 rows rely on search excerpts or timed-out direct routes whose upstream status was unavailable. The strongest direct count is Cleveland Museum of Art's API: `q=Indus seal` returned **3 unique object IDs**, all titled as Indus seals with inscriptions (147416, 140095, 147417). `q=Indus` returned 10 API records, three of which were these seals. The museum's catalogue is openly searchable, and its designated Open Access assets use CC0 terms. This is a confirmed count for one collection endpoint, not a global or holding total.

Other observed counts have broader units. The British Museum culture-term page excerpt reports **724 related objects of mixed types**; a direct local request returned HTTP 403. Louvre's `q=Indus` search excerpt reports **21 mixed records**; the local query page returned HTTP 429, while the public JSON for SB 2425 returned HTTP 200 and exposes two image URLs with per-image credits. NMMA's Lothal museum page lists **133 Seals & Sealing category entries**, but their inscription status was not individually checked and direct retrieval timed out. The Metropolitan Museum API returned HTTP 410 for six terms; object pages remain accessible through web search. Smithsonian API calls returned HTTP 429 for six terms. Exact per-term API counts/statuses and raw responses are recorded in the local query log.

Across **11 institutional groups**, the files cite at least **17 distinct object-record or official-highlight witnesses** to Indus seals, sealings or script-bearing objects. This is a minimum of named examples, not a sum of catalogue result sets. The paired audit validated **0 of 30 (0%)** museum-to-corpus joins under the explicit-identifier rule. One British Museum/corpus candidate was retained as unconfirmed because `Hr 5635` and `HR 5635345` do not match exactly; a string-prefix resemblance is insufficient.

## Files and reproduction

- [Collection register JSON](collection-register.json) and [CSV](collection-register.csv): 37 rows, each with a `depth_pass` query/method, observed status, count basis, sampled fields and evidence URLs.
- [Dataset and archive register](dataset-register.json): 15 entries carried forward from the 2 October landscape; their original count units and version limits are retained.
- [Metadata field matrix](metadata-field-matrix.csv): 37 collection rows and 15 dataset rows. Dataset rows reflect described schema fields; collection rows reflect sampled catalogue records, not institutional completeness.
- [Museum API query counts](museum-api-query-counts.csv): six terms per API for Met, Cleveland, Art Institute of Chicago and Smithsonian; returned IDs and count bases are explicit.
- [Paired sample audit](paired-sample-audit.csv): one unconfirmed candidate and 29 unfilled slots; confirmed joins = 0.
- [Protocol](PROTOCOL.md), [report](REPORT.md), [retrospective](RETROSPECTIVE.md), [sources](sources.json), and proposed [registry entry](registry-entry.json).
- [First-pass register builder](build_registers.py) preserves the original baseline. The depth scripts add acquisition observations and regenerate the updated register views.

Run from the repository root:

```powershell
python experiments/2026-10-06-evidence-census/collections-and-datasets/depth_queries.py
python experiments/2026-10-06-evidence-census/collections-and-datasets/apply_depth_pass.py
```

Direct API/page response bodies, HTTP errors, and the grouped live-search query log are local-only under `data/raw/2026-10-06-evidence-census/collections-and-datasets/depth-pass/`. `web-search-log.json` records the exact search queries and witness URLs; the web search provider does not expose the upstream HTTP status or full catalogue result counts. No bulk images were downloaded. The British Museum, Louvre, NMMA, Met and Smithsonian counts must not be added together: they use different units and several are mixed-type result sets.
