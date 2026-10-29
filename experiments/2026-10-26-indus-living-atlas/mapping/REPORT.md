# A modern map of Indus places and later towns

26 October 2026. Exploratory cartographic tooling and source review. Verification tier: submitted.

We built a source-linked map from the project's earlier 115-place register. Search, chronological overlap, country and evidence filters replace a single undifferentiated view. Every place retains its location source, dated phases and missing values. The map links directly to the city and building viewer and to the two new historical reviews.

## What changed

The [8 October map](../../../presentations/2026-10-08-site-map-and-overview/README.md) supplied 115 place entities and 112 coordinates. These include finds outside South Asia and three unlocated entries: Wattoowala, Luristan and the regional label Dilmun. We preserve all of them. The initial South Asia view shows 84 located entries and one unlocated entry; the full view exposes all 115. The corpus behind the old map is a record of finds, not a census of every ancient city.

The [24 October architectural register](../../2026-10-24-q1032-town-axis-register/REPORT.md) supplies competing coordinate assertions for matched towns. We retain those alternatives and explicitly select its later Surkotada and Farmana reference coordinates. The older map already used coordinates close to those selected points; these overlays are small harmonizations, not new multi-kilometre discoveries. The original coordinates and each selection's source remain in the data snapshot. Allahdino retains a disagreement of 0.10 degrees in latitude. Earlier build notes also identify Nindowari and Tell Abraq location or locator issues. Their warnings remain with the inherited points.

The [town review](../living-towns/REPORT.md) adds eighteen assessed cases. Sixteen candidate town or named-place anchors enter the green map layer. The abandoned Dholavira and Mohenjo-daro comparisons remain in the table and link to their archaeological points. Approximate civic or sacred-place anchors do not supply ancient excavation boundaries.

The [3D viewer](../reconstruction/index.html) provides top-down plans and orbitable geometry. We link Mohenjo-daro, Dholavira and Lothal from their map panels. City scenes give schematic spatial context; individual buildings contain the dimension-backed architectural detail. This geographic map and the reconstruction scenes use different coordinate systems and purposes. We supply no artificial georeferencing transformation between them.

## Cartography and chronology

The offline background uses the pinned Natural Earth country geometry already held by the satellite atlas. We acquired its public-domain modern river layer at the same repository commit. The first 1:110 million file contains thirteen major rivers and omits the Indus and Ganges. We preserved that acquisition, then used the 1:50 million layer, which includes both rivers. The raw files and hashes are in the D: store; [river-acquisition.json](river-acquisition.json) and [river-acquisition-v2.json](river-acquisition-v2.json) record both attempts. The displayed drainage is contemporary regional context. Ancient river and coastline reconstructions require their own dated geomorphic evidence.

Leaflet 1.9.4 comes from the project's pinned, licensed runtime. The atlas loads no remote fonts, scripts, images or tiles by default. Optional OpenStreetMap street tiles use ordinary browser requests, visible attribution and normal caching, following the [tile policy](https://operations.osmfoundation.org/policies/tiles/). They are enabled only over HTTP and have no prefetch or archival function. Their contemporary buildings are unrelated to the schematic ancient structures in the model viewer.

Period filters test overlap with each original site-phase range. The presets are defined comparison windows: 4000–2600, 2600–1900 and 1900–1300 BCE. A nonzero overlap is required for two intervals; sharing the 1900 BCE boundary alone does not put a Mature-only site in the Late window. Point dates and the single-date control use inclusive containment. A site without a numerical phase range is visible under “All periods” and drops out of a date-specific view. The town layer stays visible across archaeological date changes, and its own dated sequence appears in the panel.

The source register includes radiocarbon, typological, report-assigned, regional-convention and weaker inherited dating statements. “Site-specific” describes the attribution's scope, not an audit of chronological quality. The map has not reopened every cited work. Mohenjo-daro's inherited news-based wall chronology is marked as such. Dholavira's rechecked UNESCO occupation envelope is a separate assertion beside the retained detailed phasing. No numerical phase date is transferred to an individual inscription.

## Outputs and limits

The current viewer reads `mapping/current-data.js`, copied from a recorded snapshot. The JSON companion preserves assertions for reuse. Its export contains only the filtered point features and their source metadata, plus a list of unlocated matches. Modern town points have a separate layer and category. Selection, legend, scale, keyboard-accessible result buttons and responsive layout were checked in a real browser.

We add no newly discovered site, excavated wall, inscribed object, face, sample date or measured city footprint. A location disagreement needs a primary locator or surveyed control. Detailed accurate city maps need openly usable, georeferenced plans and feature-level excavation joins. The [data update](../DATA-UPDATE.md) lists those gaps for the shared knowledge base.

The strongest reading supported by the combined atlas is a landscape of settlements with different material and occupational histories. Its urban boundary requires separate tests for administrative markers and ordinary activity. The deciding evidence is a set of independently dated occupation sequences with comparable recovery, linked to surveyed city features and their source plans.
