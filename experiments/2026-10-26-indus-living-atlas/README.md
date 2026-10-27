# Indus Atlas: cities and their afterlives

We extend the earlier map into a geographic explorer, build city and building reconstructions, and review settlement persistence and the histories of towns inhabited today. Four contributors worked in separate directories. Earlier maps, scientific outputs and source witnesses remain intact.

Open [the atlas](index.html). Search places, inspect their dated phases and location sources, switch to present-day town anchors, compare the two layers, or export the filtered points as GeoJSON. The core map works offline. Modern street tiles are optional and require an HTTP preview and an internet connection.

| Product | Contents |
|---|---|
| [Regional atlas](index.html) | 115 inherited place entities, 112 located; date, country and evidence filters; coordinate assertions; sources and export |
| [City and building viewer](reconstruction/index.html) | Orbitable 3D and top-down plans, source-linked features, modelling assumptions, cutaways and geometry exports |
| [Readable research page](research.html) | Both source reviews rendered with their evidence links |
| [Marker-continuity study](continuity/REPORT.md) | Twelve sources and sixteen observations on regional persistence, changing markers and detection |
| [Living-town review](living-towns/REPORT.md) | Sixteen candidates and two abandoned-city comparisons, with dates, footprints and occupation gaps |

The historical result is regional persistence through urban reorganization. Its scale varies by place and practice. A source's early date, an overlapping modern settlement and an uninterrupted sequence are separate assertions in the town register. The models distinguish published dimensions from approximate placement and assumed heights.

## Local preview

Run from the repository root:

```text
python -m http.server 8766 --bind 127.0.0.1
```

Open `http://127.0.0.1:8766/experiments/2026-10-26-indus-living-atlas/index.html`. Stop the server when finished. Opening `index.html` directly also supports the offline map and self-contained 3D models; the street-tile option remains disabled for file URLs.

## Evidence and reproduction

The [protocol](PROTOCOL.md), [map report](mapping/REPORT.md), [source register](mapping/sources.json) and each parallel package describe inputs and scope. `mapping/prepare_data.py` builds a new evidence snapshot and refuses an existing output directory. `mapping/build_reader.py` renders the original reviews using the installed Markdown package. The map's frozen endpoint and the browser and package checks are recorded in [VALIDATION.md](VALIDATION.md).

To build a successor, choose fresh output names:

```text
python experiments/2026-10-26-indus-living-atlas/mapping/acquire_rivers.py
python experiments/2026-10-26-indus-living-atlas/mapping/prepare_data.py --run mapping/NEW-RUN
python experiments/2026-10-26-indus-living-atlas/mapping/build_reader.py --run reader/NEW-RUN
```

Copy the new `atlas-data.js` to `mapping/current-data.js` and the new `research.html` to this directory only when deliberately selecting the successor for the current viewer. Preserve the old run. The checks are manual; no CI or publishing configuration is added. Shared knowledge maps and coverage documents remain for maintainer integration.

New raw witnesses, acquisition derivatives and screenshots are local-only at logical `data/raw/2026-10-26-indus-living-atlas/`, physically `D:\projects\indus_valley_script\data\raw\2026-10-26-indus-living-atlas\`. Each contributor records its own sources and hashes. The [data update](DATA-UPDATE.md) proposes the combined coverage changes without changing inscription counts.

Project code follows the Unlicense and original project prose follows CC0. Leaflet retains its complete BSD-2-Clause notice. Natural Earth geometry is public domain. Source photographs, archaeological plans, publications and optional map tiles retain their own terms. We redistribute no source photographs or scanned plans in this atlas.

Authors: GPT-6 through the Codex desktop workspace harness, with separate map, reconstruction, continuity and living-town contributors. The exact runtime model build was unavailable. Verification is submitted and computationally checked; no independent archaeological review or field survey is claimed.
