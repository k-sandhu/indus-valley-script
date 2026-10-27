# Proposed coverage update

We add geographic and architectural context and two source reviews. No inscribed-object count, object identity, face, museum accession, excavation join or calendar date for an inscription changes. Maintain the existing shared manifest and `knowledge/DATA.md` until these records are reviewed for integration.

| Component | Addition | Remaining gap |
|---|---|---|
| Geographic atlas | Preserves 115 place entities and 112 located entries; imports later coordinate assertions; two declared coordinate harmonizations; source and date filters | Three unlocated labels, unresolved locators, unequal coordinate accuracy, and no surveyed feature boundaries |
| Geographic context | Two pinned Natural Earth modern-river acquisitions, with the 1:50 million layer selected | The coarse context does not supply ancient channel positions or city-level mapping |
| 3D architecture | Source-linked metric meshes, city-context scenes, top-down views and exportable geometry | Surveyed footprints, building-phase joins, surviving wall heights and roofs remain incomplete; consult the reconstruction source record |
| Marker persistence | Twelve sources and sixteen regional observations, with changed markers and detectability separated | Dated last-use contexts, ordinary-occupation recovery and independent confirmation sites |
| Town history | Eighteen assessed cases, including sixteen candidates and two abandoned comparisons, with civic identity, evidence place, dates and spatial relationship | A complete occupation chain to the present is unresolved for the Indus-overlap candidates in this review |

Root map records are the [map source register](mapping/sources.json), [first river acquisition](mapping/river-acquisition.json) and [selected river acquisition](mapping/river-acquisition-v2.json). Parallel source and acquisition records remain in [reconstruction](reconstruction/README.md), [continuity](continuity/DATA-UPDATE.md) and [living-towns](living-towns/DATA-UPDATE.md). Their precise counts, rights and access depth take precedence over this combined summary.

New raw inputs and screenshots are local-only under logical `data/raw/2026-10-26-indus-living-atlas/` and physical `D:\projects\indus_valley_script\data\raw\2026-10-26-indus-living-atlas\`. The checkout's `data/raw` junction was checked before acquisition. Recorded source hashes identify reused witnesses from older packages. Public-domain geometry and the licensed Leaflet runtime retain their provenance; downloaded publications, source images and plans remain local.

Suggested navigation: add the atlas, city viewer and readable research page to the existing map and settlement direction after maintainer review. Keep the older maps and frozen studies available. A future dataset should join site, surveyed feature, architectural phase, source figure, date assertion and occupation interval as distinct records rather than attaching a single founding date to an entire city.
