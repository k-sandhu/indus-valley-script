# Indus cities, changing markers and living towns

Status class: exploratory tooling and source review. Recorded 26 October 2026 before new source extraction or map construction. Authors: GPT-6 through the Codex desktop harness; the exact runtime model build is unavailable. Four contributors own separate directories in the shared checkout.

We extend the 8 October find-site map, the 12 October satellite atlas and the 24 October architectural register with a modern, source-linked geographic explorer and a separate 3D viewer. Two parallel source reviews examine the loss of recognizable Harappan markers and the evidence for occupation beneath towns inhabited today. These are linked research products with separate evidence records.

The map contributor owns this directory's top-level files, `mapping/` and `qa/`. The other contributors own `reconstruction/`, `continuity/` and `living-towns/`, respectively, and their own attempt entries. We preserve every earlier endpoint and existing working-tree change. Generated knowledge maps and registries remain for maintainer integration. No publication, deployment configuration or scheduled work forms part of this run.

## Evidence and gaps

The earlier map indexes 115 find-site entities, including labels outside South Asia. Its coordinates and phase assignments have unequal source quality. The later town register preserves competing coordinates and corrects some older locations; a regional marker is never a surveyed building point. We import the earlier records with their provenance and show a separate inherited-evidence status. We apply an explicit overlay only for documented corrections and retain the original value. We expose unlocated entries rather than placing them at guessed coordinates.

Published city plans and architectural dimensions constrain a reconstruction. Heights, missing rooms, roofs, and spatial layouts without surveyed control remain modelling assumptions. The 3D contributor records their provenance at feature level. We do not acquire or redistribute an unresolved-rights plan as a public map layer.

`knowledge/DATA.md` prioritizes physical object records. This contribution improves the geographic and architectural source context; it adds no inscribed object, face, excavation join or calendar date for an inscription. All coverage changes are recorded in this package for maintainer integration.

## Construction and source rules

We preserve the earlier map's named sites, date intervals, source distinctions and missing values. Geographic filters test interval overlap. A point visible at a selected date means that its recorded interval overlaps that date; it establishes neither continuous occupation nor an inscription date. Modern town locations form a separately labelled layer. The source review distinguishes an actual town's excavated footprint from nearby older settlement, and an early date from an uninterrupted sequence.

The core explorer works offline with the already licensed Leaflet runtime and public-domain Natural Earth context. Optional contemporary OpenStreetMap tiles load only after the reader enables them and retain attribution. Modern coastlines and borders provide present-day orientation; no line is asserted as a Bronze Age river or political boundary. The modern basemap is disabled for offline verification.

We browse primary excavation, institutional and official heritage sources for new claims. We retain exact titles, URLs, locators, access depth and uncertainties in source records. Bulk source witnesses, detailed unresolved-rights derivatives and screenshots go to logical `data/raw/2026-10-26-indus-living-atlas/`, physically `D:\projects\indus_valley_script\data\raw\2026-10-26-indus-living-atlas\`, after checking the D: target and checkout junction. Own code, observations, source pointers and licensed map assets may remain in the owned package.

## Checks and stopping rule

Completion requires a usable local map with search, phase and evidence filters, sources, a scale, explicit coordinate quality, a full list of omitted locations, links to the older maps and the new parallel products, and an offline browser check at desktop and mobile sizes. We inspect coordinate changes, counts, source links and date-filter boundaries with a deterministic validator. We check 3D interaction and model provenance, then review both source reports and the living-town schema before integration.

This work scores no sign reading, meaning map, restoration, segmentation or corpus-based conjecture. The tasks in `bench/README.md` do not score archaeological reconstruction or the source-review claims here. We do not manufacture a bench result or spend a confirmation population. Prospective continuity tests remain unrun; their protocol states what observations would decide them.

We finish with package checks, `python tools/kb.py check`, the prose scan and the repository verifier, recording pre-existing failures separately. Success means that the delivered files and claims meet these checks. It does not mean archaeological confirmation of a reconstruction or uninterrupted occupation. New evidence or a correction goes into a successor run rather than silently rewriting a frozen output.
