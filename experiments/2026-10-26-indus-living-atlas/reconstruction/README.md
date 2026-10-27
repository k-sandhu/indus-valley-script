# Indus built world

Open [the architectural explorer](index.html). It contains seven orbitable models: Mohenjo-daro and Dholavira city contexts, the Great Bath, Dholavira's eastern reservoir and west castle gateway, the Pillared Hall and Lothal's large basin. Choose **Plan** for a top-down map, select a surface or a feature name to inspect its source, then use **Focus** to move closer. The explorer works offline and includes keyboard, mouse and touch controls.

The city contexts place named districts and monuments in a schematic framework. Individual buildings carry published dimensions. Every feature separates its dimensional evidence, position and height assumptions. Optional roofs, display water, cutaway walls and an assumed-height slider expose those choices. Published basin depths stay fixed when the assumed superstructures change. The Lothal model retains both dock and irrigation-tank interpretations in its source record.

The current frozen endpoint is [run-v5](run-v5/index.html), a 303 KB standalone HTML file with its data embedded. [scenes.json](run-v5/scenes.json) contains all geometry, units, material colours, feature records, source locators and display assumptions. Seven metric OBJ files and their material file are in [exports](run-v5/exports/). The interface can also download an individual model as OBJ or JSON. OBJ files omit optional roofs and water, retain the base geometry and use metres with X east, Y north and Z up.

We add 49 feature records and 590 mesh parts, including repeated buildings embedded in city contexts. These counts describe the display. The contribution adds eight local HTML source witnesses, checks one previously held excavation-report scan and records one further bibliographic pointer. It adds no inscribed objects or object findspots.

[REPORT.md](REPORT.md) explains the source choices and limits. [SOURCES.json](SOURCES.json), [DATA-UPDATE.md](DATA-UPDATE.md) and [RETROSPECTIVE.md](RETROSPECTIVE.md) preserve provenance and repairs. The [769 deterministic checks](verification-v5.json) and [32 browser checks](browser-verification-v5.json) pass. Verification was performed by the author in the same collaboration; an independent archaeological review remains open.

Run from the repository root with Python 3.13 and Node.js. The builder uses the standard library; the optional source acquisition uses Python's standard HTTP client. Choose new run and check names because frozen outputs are preserved:

```text
python experiments/2026-10-26-indus-living-atlas/reconstruction/build_models.py --out run-reproduction
python experiments/2026-10-26-indus-living-atlas/reconstruction/verify_models.py --run run-reproduction --out verification-reproduction.json
```

The builder reads the tracked source metadata and template. It does not need the downloaded publications. Checking the source-witness hashes additionally needs the local inputs described in `SOURCES.json`. The browser recipes use Playwright CLI against a loopback server; set their base URL and new output names before a new run. No site was published.

Authors: GPT-6 family through the Codex desktop collaboration harness; exact serving variant unavailable. Project code follows the Unlicense and the project's authored geometry and prose follow CC0 1.0. Acquired publications and photographs retain their own terms and stay local.

The strongest supported reading is that published measurements already let us inspect substantial Indus water works and enclosed architecture at a common metric scale. Registered plans, sections and elevations tied to specific building episodes would decide where these schematic contexts can become survey-based city models.
