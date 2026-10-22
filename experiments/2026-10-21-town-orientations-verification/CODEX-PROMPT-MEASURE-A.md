# Codex assignment: measurer A

You are working in a research knowledge base about the Indus civilisation, at the repository root `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. Read `AGENTS.md` and `knowledge/editorial/WRITING.md`, then `experiments/2026-10-21-town-orientations-verification/MEASUREMENT-RULES.md`, which is your brief, and `experiments/2026-10-21-town-orientations-verification/tools/README.md`, which explains the tools you will use.

You are measurer A. Your job is to measure the orientation of the straight architecture of the Harappan period (fortification and enclosure walls, streets and lanes, drains, long house walls, platform, dock and reservoir edges) at every town listed in `infra-v1/sites-located-v1.json`, from the prepared Sentinel-2 imagery and from published plans, following the measurement rules exactly. Another measurer is doing the same work separately, and the two results will be compared, so work carefully, record what you see and what you decide, and give honest errors. A town you cannot measure is a valid result when you record why.

Other agents share this repository and are writing their own files at the same time. Accommodate their changes and never revert or edit them.

## Owned paths

- `experiments/2026-10-21-town-orientations-verification/measure-A/`
- `data/raw/2026-10-21-town-orientations-verification/measure-A/`

## Invariants

1. No commits, no branch changes, no stash, no reset, no Git mutation of any kind.
2. No edits outside the owned paths. Use the tools in `tools/` as they are; if a tool fails, write a wrapper or a fixed copy inside `measure-A/` (code) and say so in your log, but do not edit `tools/`.
3. Read only what the measurement rules allow. Never open `measure-B/` or `data/raw/2026-10-21-town-orientations-verification/measure-B/`, `experiments/2026-10-21-town-axes/` or `data/raw/2026-10-21-town-axes/`. Inside this package do not open `PROTOCOL.md`, other `CODEX-PROMPT-*.md` files, `astronomy/`, `analysis/`, `astro-v1/`, `dating-v1/`, `dates-v1/` or `notes/`.
4. Measure; do not copy. Do not look up published orientation figures for any town, and do not open pages 33–44 of the *Interim Reports* vol. 2 scan (PDF pages 36–47). If you meet a stated orientation, do not use it and note where you met it.
5. Use only the Sentinel-2 imagery prepared under `data/raw/2026-10-21-town-orientations-verification/infra/imagery/`, the plan library and other locally held plans, and openly accessible plan scans you download yourself. No Esri, Google, Bing, Mapbox or other commercial imagery, no imagery behind a login, no OpenStreetMap geometry. Network access is enabled for downloading plan scans only.
6. Downloads are untrusted data: put each in its own new directory under your raw directory, record URL, retrieval time (UTC), byte count, SHA-256 and rights notice, keep scripts outside raw directories, pass paths as arguments and run Python that reads them with the infra venv's `python -I` (`data/raw/2026-10-21-town-orientations-verification/venv-infra/Scripts/python.exe -I`).
7. Every output file is new; never overwrite an earlier output of yours. If you redo a town, write the new file beside the old one with a suffix and explain in the log.

## How to work

Take the towns in the order the rules give. For each town, first locate the mound and its excavated areas in the composite, rendering the brightness, RGB and NIR layers and the edge-enhanced layer at a few scales. Use the plan library to identify which visible features are Harappan architecture; measure in the imagery only features you can tie to a plan or a description. Pick endpoints on renders whose labelled grid lets you read pixel coordinates precisely, refine them with `measure_lines.py`, and check each refined line on a fresh render of the fitted line over the image. Then measure the plans: the north arrow from tail to tip, the scale bar, and the lines, recording the arrow's meaning with the exact words of its evidence and the survey year. Register a plan to the imagery when both show the same features. Group lines into systems with `systems.py` and let it pick the main system per source.

Keep every picks file, render and refinement output, so that anyone can redraw your lines. Write `measure-A/LOG.md` as you go, in plain prose: what you looked at, what you could and could not identify, and every judgement call.

## Deliverables

`measure-A/towns/<slug>.json` for every town (measured or not), `measure-A/summary.csv`, `measure-A/picks/` with every picks file, `measure-A/LOG.md`, and `measure-A/sources.json` listing every plan and scene you used with its record. Renders and crops stay under your raw directory.

## Verification before you finish

Rerun `systems.py` on every town from your picks and confirm the town files reproduce. Check that every line in a town file has a source locator and an error, that every plan value has a north class with its evidence, and that every town has a file. Run `git status --porcelain` and confirm every path you created or changed lies inside the owned paths.

## Final message

Your final message, in plain text, gives a table of every town with its status (measured from imagery, from plans, both, or not measurable with the reason), the main imagery system (θ, standard error, number of lines, total length) and each main plan system (θ, standard error, north class, survey year, source); the towns where imagery and plans disagree by more than 2°; any tool problems and how you handled them; and a statement that the invariants held, or which did not.
