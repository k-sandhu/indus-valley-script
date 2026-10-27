# Checks for the architectural explorer

The current endpoint is run-v5. [verification-v5.json](verification-v5.json) passes 769 deterministic checks and [browser-verification-v5.json](browser-verification-v5.json) passes 32 browser checks. These are author checks within the same collaboration. They verify geometry, source integrity, packaging and browser behaviour.

The deterministic check reads all mesh indices and coordinates, checks metric rulers against declared values, checks the basin, gateway, city and hall invariants, independently parses all seven OBJ files and verifies their extents. It also checks all nine locally held source hashes, the frozen artifact hashes, JavaScript syntax and the absence of remote runtime assets. The source hash check needs the local D: inputs; the builder itself uses tracked metadata and code.

The browser recipe is [browser_check_v5.js](browser_check_v5.js). It inspects every model, checks nonempty WebGL pixels, operates surface picking, accessible feature selection, focus, keyboard orbit, Plan, zoom, optional layers and the assumed-height slider, and downloads an OBJ and JSON. It also switches a model with browser networking disabled and checks a 390 px layout. We separately followed the stable entry with `#model=dholavira-reservoir&view=plan` and confirmed that it preserves both parameters while opening run-v5. Physical touch hardware was not available for this check.

All seven final model screenshots, the Dholavira Plan screenshot and the full mobile screenshot were visually inspected. Their D: paths and SHA-256 hashes appear in the delivery manifest. The browser reports no script errors. Large plane occlusion in the earlier Canvas renderer is repaired by WebGL depth buffering; the earlier endpoints remain preserved.

The manual prose scan found one flag in the frozen protocol: the unquoted `data/raw` junction name. This is a filesystem path, and we retained it. The knowledge check reports: `PASS; 672 items; 0 errors; 0 warnings; 2 maintainer notes; 12 reviewed local-only targets; 139 Markdown files.` The notes concern regenerated registry and map files, which remain for maintainers.

The [broader repository verifier](repository-verification-v1.json) reports 59 errors outside this package, including historical links and its treatment of the existing `data/MANIFEST.json` path. None names an owned file. The check summary records that scope; no unrelated file was repaired as part of this contribution.

Commands run from the repository root:

```text
python experiments/2026-10-26-indus-living-atlas/reconstruction/build_models.py --out run-v5
python experiments/2026-10-26-indus-living-atlas/reconstruction/verify_models.py --run run-v5 --out verification-v5.json
npx --yes --package @playwright/cli playwright-cli -s=indus3d run-code --filename experiments/2026-10-26-indus-living-atlas/reconstruction/browser_check_v5.js
python tools/review_prose.py --path experiments/2026-10-26-indus-living-atlas/reconstruction --no-write
python tools/kb.py check
python tools/verify_knowledge_repo.py --output experiments/2026-10-26-indus-living-atlas/reconstruction/repository-verification-v1.json
```

Use new run names and output paths when reproducing. The browser recipe uses the root collaboration's loopback server at port 8766. Its separate temporary architecture server was stopped, and the root server was left running. No CI/CD, scheduled task, deployment or external publication was added.
