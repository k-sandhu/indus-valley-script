# Indus Valley script repository: structure and code-layout review

## 1. Verdict

The repository has a sound knowledge layer built on 12–13 October (`knowledge/`, `tools/kb.py`, `bench/`) sitting on top of two earlier, unconsolidated layers from 1–11 October (`research/`, `src/`, `results/`, `output/`, and the nested `experiments/2026-10-02-six-hour/` tree), and a newcomer still has to cross all three layers to follow most pre-12-October claims to their evidence. The 12 October restructure deliberately moved nothing, so the duplication of outputs, plans, reports and code across at least four homes each is deferred work rather than an accident, and it is now the main tax on cloning, searching and agent orientation. Nothing here needs a history rewrite or a change to the frozen-evidence rule: the layout can be consolidated by labelling and freezing the legacy layers where they stand, adding a machine-readable path map before anything moves, and then moving only non-evidence material first. File counts below are the brief's measurements (19,835 tracked files, 17,745 in `experiments/`); my shell access timed out in this session, so I verified structure by reading tracked files and did not independently re-measure counts or byte sizes.

## 2. Observations

1. **Three eras share the top level without era markers.** The generated map lists 18 top-level directories, five of them described only as "local support directory; inspect before use" (`knowledge/MAP.md:11-28`). The README layout table admits `research/`, `results/` and `archive/` are "Earlier plans, outputs and documentation, kept unchanged" (`README.md:71-86`), and `archive/2026-10-01-investigation/README.md:5` confirms the original 1 October paths under `research/`, `src/`, `results/` and `output/` were retained in place. The top-level `PLAN.md:3` is still the original four-hour plan of 1 October, unmarked as superseded. A newcomer cannot tell from names alone which directories receive new work and which are frozen strata.

2. **Following a claim to its evidence crosses all three eras.** `AGENTS.md:24` promises a four-layer route (AGENTS → map → card → experiment package), and that route works for work after 12 October. For earlier work it does not: finding F-0001's evidence points not to an experiment package but to `research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json` (`knowledge/findings/F-0001-sequential-prediction-on-unique-texts.md:8`), and Paper 001's claim–evidence map draws single claims from `research/methods/results/…`, `results/restoration/…`, `src/methods/…`, `experiments/2026-10-02-six-hour/…` and the local-only `data/normalized/…` in adjacent rows (`papers/001-artifact-aware-prediction/claim-evidence-map.md:7-25`). The card system faithfully records these paths, which is why they must stay resolvable, but the physical scatter is real.

3. **Each kind of thing has several homes.** Outputs live in `results/` (35 files), inside `research/` at `research/methods/results/…` (see observation 2), in `output/` (705 files, including reports, PDFs, `output/environment.json` and `output/evidence_manifest.json` cited at `REPRODUCING.md:17,25`), and in each experiment package. Plans live in `PLAN.md`, `knowledge/directions/`, `research/NEXT_TESTS.md` (via `knowledge/INDEX.md:12`) and per-package `PLAN.md` files. Retrospectives live in `knowledge/retrospectives/` and throughout `experiments/**/RETROSPECTIVE.{md,json}`, both swept up by one glob in `tools/kb.py:171-173`; the six-hour tree alone fills most of the map's retrospective list with paths nested four deep (`knowledge/MAP.md:457-493`). The registry has two homes with confusing names: source entries in `knowledge/registry/attempts/*.json` and the generated aggregate at `knowledge/experiments/registry.json` (`tools/kb.py:259-261`).

4. **The October 12 restructure was additive by design.** Its plan states "No files are moved or deleted" (`maintenance/2026-10-12-repo-restructure/PLAN.md:12`), and its retrospective closes by proposing that an independent contributor test the new route and report missing prerequisites (`maintenance/2026-10-12-repo-restructure/RETROSPECTIVE.md:47`). So the current layout is a navigation layer over an untouched legacy layout. Any second restructure that only adds another index will repeat the pattern; consolidation has to involve moving or retiring things, with redirects.

5. **`src/` is described as reusable code but is mostly frozen history.** The map generator labels it "reusable analysis code" (`tools/kb.py:214`) and the README calls it "Analysis code" (`README.md:79`), yet 89 of its 141 files are in `src/six_hour/` (brief's count), snapshots tied to `experiments/2026-10-02-six-hour/` (`REPRODUCING.md:59-61`). The reproduction guide warns that the `src/` entry points write to default directories that can overwrite old results (`REPRODUCING.md:42`), require local inputs, and in places contain the original host's absolute paths (`REPRODUCING.md:86`). There is no test suite for `src/`; verification is a set of ad-hoc scripts (`src/verify_root.py`, `src/methods/verify_methods.py` at `REPRODUCING.md:31-34`).

6. **`bench/` is the first real library, but it is pinned to frozen experiment directories.** It has the properties a library should have: versioned output schema, refusal to overwrite, a self-test, and documented exit codes (`bench/README.md:19`). However `bench/common.py:18-22` hard-codes `experiments/2026-10-13-bench` and four other experiment packages as its source locations, and its plan says earlier code is imported from those packages with hashes (`experiments/2026-10-13-bench/PLAN.md:5`). Moving or renaming any of those packages breaks the harness, and the same pattern appears in the site builder, which hard-codes an experiment package for its omissions list and explore pages (`tools/build_site.py:30-33`). Frozen packages have quietly become load-bearing infrastructure.

7. **There is a good experiment template but no enforced minimum package shape.** `templates/EXPERIMENT.md` and `CONTRIBUTING.md:9,31-36` specify protocol, inputs, commands, outputs and retrospective, yet `kb.py check` validates cards, registry entries and links only in a hard-coded list of "new" Markdown files (`tools/kb.py:311-319,447-452`); it does not check package contents. Observed shapes vary accordingly: the restructure package carries a plan, retrospective, `CHANGES.json` and roughly ten verification artefacts (`maintenance/2026-10-12-repo-restructure/RETROSPECTIVE.md:33-41`); the bench package is a short plan whose code lives outside the package in `bench/`; the six-hour package is a tree of dozens of sub-packages, each with its own README, findings, `main/` results, reviews and repairs nested inside earlier directories (`experiments/2026-10-02-six-hour/SESSION_LOG.md:5-80`). Because frozen outputs cannot be overwritten, every repair tends to nest deeper (`…/integration-review/physical-and-reference/delta-review-2026-10-02/`, `knowledge/MAP.md:462`), and intermediate `run-v1`…`run-v6` material is indistinguishable from endpoints by path alone.

8. **The file count is a working cost, and the repository already works around it.** With an estimated 89% of tracked files under `experiments/`, every `git ls-files`, full-text search and agent glob pays for frozen intermediates; `kb.py` itself globs `experiments/**` on every index build (`tools/kb.py:172-173`), and the generated `knowledge/MAP.md` runs past 500 lines, mostly registry and retrospective listings with titles truncated to 95 characters (`tools/kb.py:201-203`). The README already teaches a blobless sparse clone for readers who only want documents (`README.md:55-63`), which is an admission that the default clone carries more than most readers need. I could not measure byte sizes in this session, so I make no claim about which trees dominate by bytes as opposed to file count.

9. **`.gitignore` has become a per-package exception list.** At 139 lines it encodes one-off allowlist entries for individual packages and figures, for example the Helsinki digitization crops, catalogue HTML files and settlement figures (`.gitignore:74-139`). Each new package that needs a binary in Git must edit this shared file, which cuts against the project's own parallel-work rule that contributors own distinct files (`AGENTS.md:55`, `CONTRIBUTING.md:17`).

10. **The data-pointer pattern is the best structural idea in the repository, but its tooling is buried.** `data/` tracks only `README.md` and `MANIFEST.json` while bulk inputs stay local (`.gitignore:2-4`, `knowledge/DATA.md:231-247`), and `knowledge/DATA.md` gives a complete account of holdings, coverage and gaps. Yet updating the project's first-priority artefact depends on scripts inside an experiment package, `experiments/2026-10-12-data-inventory/build_manifest.py` and `coverage.py` (`knowledge/DATA.md:247`), while the user-facing tool is `tools/fetch_data.py` (referred to at `knowledge/DATA.md:235`). Top-priority tooling should not live in a dated package.

11. **Generated files are tracked and create a maintainer bottleneck, for a defensible reason.** `knowledge/MAP.md` and `knowledge/experiments/registry.json` are generated by `kb.py build` (`tools/kb.py:259-273`), contributors are forbidden to edit them, and drift is expected (`CONTRIBUTING.md:17,44`). Tracking them lets read-only readers and agents navigate without running anything, which this review relied on. The cost is that every merged card leaves the tree failing `kb.py check` until a maintainer rebuilds (`tools/kb.py:450-452`).

12. **Loose top-level files duplicate each other.** `llms.txt` (18 lines) restates links already in `AGENTS.md` and `README.md` and will stale independently. `CITATION.cff:9` declares a single CC0 licence while `REUSE.md:3` and `LICENSE` describe a three-way split (Unlicense, CC0, CC BY 4.0), so the machine-readable citation understates the actual terms. `CLAUDE.md` is a one-line pointer to `AGENTS.md`, which is the right pattern and a model for the rest.

## 3. Recommendations

### R1. Freeze and label the legacy layers in place; move nothing yet

What: declare `research/`, `results/`, `src/` and `output/` (except the chart atlas, see R5) frozen historical layers, and say so at each directory root and in the entry documents.

Steps: add a short `README.md` stub to `research/`, `results/`, `src/` and `output/` stating the era, that no new work lands there, and where the modern equivalent lives (`experiments/` for outputs, `bench/` or `tools/` for code, `papers/` for reports). Move `PLAN.md` to `archive/2026-10-01-investigation/PLAN.md` with a one-line redirect stub left at the top level, or simply retitle it in place as the 1 October plan. Update the layout table in `README.md:71-86` and the directory descriptions in `tools/kb.py:212-217` to use the word "frozen" for these trees. Add one hard rule to `AGENTS.md`: new outputs go only to a new `experiments/YYYY-MM-DD-*/` directory, new reusable code only to `bench/` or `tools/`.

Cost and breakage: almost none. No evidence path changes, the registry and `kb.py` need only a description-string edit followed by one maintainer `kb.py build`, and the site build is unaffected because it reads from Git paths that still exist (`site/README.md:13`).

Success test: a fresh agent given only `AGENTS.md` can state, without searching, where a new output, a new reusable function and a new report go, and `kb.py search` results in the frozen trees stop growing.

### R2. Build the path map before any future move

What: create `knowledge/registry/path-map.json`, a list of `{old, new, reason, date}` records, initially empty, and teach the two consumers that resolve evidence paths to consult it.

Steps: extend `kb.py check`'s target resolution (`tools/kb.py:337-362`) so a missing path that appears as an `old` entry resolves to its `new` location (including the `#/` JSON-pointer suffix defined in `knowledge/registry/VOCABULARY.md:48`). Extend `tools/build_site.py` (path handling at `tools/build_site.py:55-60,100-105`) to emit a redirect page or rewritten link for mapped paths. Record in `CONTRIBUTING.md` that no tracked evidence file may be moved without a path-map entry in the same change.

Cost and breakage: one focused change to each of `tools/kb.py` and `tools/build_site.py`, plus tests; no content moves, so nothing can break until the mechanism is first used. Agent instructions gain one sentence.

Success test: move one harmless non-evidence file as a pilot, and show `kb.py check` passing, the site check passing, and the old path still resolving through the map.

### R3. Define and enforce a minimum experiment package shape, for new packages only

What: a package is `README.md` (from `templates/EXPERIMENT.md), one protocol file recorded before outcomes, one or more dated `run-*/` output directories, `RETROSPECTIVE.md`, and a registry attempt whose `evidence` names the exact outputs. Repairs create a new sibling `run-*` or a new dated package, never a directory nested inside a run.

Steps: state the shape in `CONTRIBUTING.md` beside the existing directory rule (`CONTRIBUTING.md:9`). Add a `kb.py check` rule, applied only to packages dated after the rule lands, that the five elements exist and that no package nests deeper than two levels below `experiments/<package>/`. Grandfather everything existing, including `experiments/2026-10-02-six-hour/`. Name the noise explicitly in the template: superseded intermediate runs stay (the frozen rule requires it) but the README must mark which `run-*` is the endpoint.

Cost and breakage: a small `kb.py` addition and template edit; existing packages, evidence links and the registry are untouched because the rule is prospective.

Success test: the next three packages pass the new check, and a reader can find the endpoint of each from its README alone without listing the directory.

### R4. Promote buried and duplicated code into the two code homes; stop treating `src/` as a library

What: `bench/` for shared evaluation code, `tools/` for repository operation (knowledge base, data fetching and manifest building, site build, verification). Code used by a second package gets promoted out of its experiment package at that moment, with the package keeping a hashed snapshot reference as `CONTRIBUTING.md:33` already requires.

Steps: move (with R2 path-map entries, or copy-and-deprecate to be safer) `experiments/2026-10-12-data-inventory/build_manifest.py`, `coverage.py` and `not_held.py` into `tools/`, updating `knowledge/DATA.md:247`. When `bench/` next changes, replace its imports from experiment packages (`bench/common.py:18-22`) with vendored, hash-recorded copies inside `bench/`, so the harness no longer depends on frozen package paths; keep the source paths and hashes in provenance output as `bench/README.md:27` describes. Add the only tests that matter to a small `tools/tests/` and `bench` self-test routine that maintainers run by hand: the eight CLI behaviour tests recorded in `maintenance/2026-10-12-repo-restructure/RETROSPECTIVE.md:33` should live with `tools/kb.py`, not only in that package's record. Relabel `src/` per R1; do not refactor it, since its value is as hashed historical snapshots (`REPRODUCING.md:70,86`).

Cost and breakage: moderate and localised. `bench` provenance hashes change once, which requires a new self-test endpoint per `CONTRIBUTING.md:46`. Evidence links to `src/` files (for example in `papers/001-artifact-aware-prediction/claim-evidence-map.md`) stay valid because `src/` does not move.

Success test: `python -m bench selftest` and the `kb.py` tests pass from a sparse clone containing only `knowledge/`, `papers/`, `tools/`, `bench/` and `templates/`, with no `experiments/` code imported at runtime.

### R5. Stop growing Git with regenerable binaries; externalise new bulk, keep old paths as pointers

What: apply the `data/` pattern to large generated artefacts. The chart atlas images in `output/chart_atlas/` (689 files per the brief), the Helsinki evaluation crops allowed by `.gitignore:74-81`, and generated catalogue HTML are derivable from tracked references plus local sources, and the project already hosts bulk this way for the 3.09 GB package A outputs (`REPRODUCING.md:76-80`).

Steps: for new packages, require generated images and HTML viewers to be published as a release asset or Hugging Face dataset with a tracked manifest (paths, SHA-256, build command), mirroring `data/MANIFEST.json`. For the existing atlas, keep `output/chart_atlas/index.html` and the numeric reference tracked, publish the PNG set as a versioned asset, and record the move in the path map (R2) so `README.md:36` and the site's explore page (`tools/build_site.py:32-33`) keep resolving. Simplify `.gitignore` to directory-level rules (binaries denied everywhere except named, reviewed asset directories) and delete the per-package exceptions that the new rule subsumes, in the same change that externalises each tree. Do not rewrite Git history to purge existing blobs: commit hashes are cited as evidence (`experiments/2026-10-02-six-hour/SESSION_LOG.md:84`) and the frozen rule treats history as part of the record. This explicitly argues against the "leave Git history" option for existing files, while achieving the same effect for future growth.

Cost and breakage: the largest item here. The site build expects explore assets to be tracked (`site/README.md:15`), so `tools/build_site.py` needs an asset-manifest input; evidence links into `output/chart_atlas/` rely on the R2 map. Estimate: this stops an estimated several thousand files per future digitization-style package from entering Git, but saves nothing in existing clone size until combined with the sparse-clone guidance already in `README.md:55-63`.

Success test: a new package with generated images adds zero binary files to Git; the atlas page still renders from the published site; `kb.py check` and the site `--check` pass.

### R6. Target top-level layout (eight directories), reached by R1–R5 rather than a big-bang move

Proposed end state, reached incrementally with path-map entries at each step:

| Directory | Contents | Absorbs |
|---|---|---|
| `knowledge/` | Cards, registry, DATA, working model, editorial and provenance | `templates/` → `knowledge/templates/` |
| `experiments/` | Dated frozen packages, unchanged paths | — |
| `papers/` | Manuscripts with methods and claim–evidence maps | — |
| `bench/` | Shared evaluation harness (library, self-tested) | reusable parts of `src/methods/` |
| `tools/` | `kb.py`, data fetch/manifest, site build, checks, tests | `site/` → `tools/site/` templates |
| `data/` | Pointers only: `README.md`, `MANIFEST.json` | — |
| `archive/` | All frozen pre-12-October layers, entered via one index | `research/`, `results/`, `src/`, `output/`, `PLAN.md` |
| `assets/` | Tracked manifests for externalised bulk (R5) | atlas and catalogue manifests |

Top-level files reduce to `AGENTS.md`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `REPRODUCING.md`, `REUSE.md`, `THIRD_PARTY_NOTICES.md`, `LICENSE`, `LICENSES/`, `CITATION.cff` and `requirements.txt`. Generate `llms.txt` from `kb.py build` (it is a link list, `llms.txt:5-18`) or delete it; fix `CITATION.cff:9` to reflect the actual licence split or point to `LICENSE`.

Migration path: first R1 labels `research/`, `results/`, `src/` and `output/` as archive-in-place, which delivers most of the comprehension benefit with zero moves. Physically moving them under `archive/` is optional and last, done one tree at a time with path-map entries, because evidence strings in cards are root-relative (`knowledge/registry/VOCABULARY.md:48`) and claim–evidence maps use relative links that `kb.py check` only partly covers (`tools/kb.py:311-319` checks a fixed file list, not `papers/`). Until link checking covers `papers/` and all cards, a physical move of `research/` risks silent breakage in exactly the files that justify the manuscripts. `templates/` and `site/` are non-evidence and can move first, keeping thin compatibility shims (`python tools/kb.py` must keep working because `AGENTS.md:41-49` and every skill cite it).

Cost and breakage: the label-only version costs a day; the full physical version costs link-checker coverage work in `tools/kb.py`, path updates in `tools/build_site.py:30-33`, `REPRODUCING.md:3,40-56` and the `.claude/skills/` guides, plus one maintainer rebuild of `knowledge/MAP.md` and the registry.

Success test: `git ls-files` at the top level shows the eight directories; an agent starting from `AGENTS.md` reaches the evidence for F-0001 and for a Paper 001 claim with every link resolving through files or the path map; `kb.py check` passes with link checking extended to `papers/`.

### R7. Split the generated map so it stays readable

What: keep generated files tracked (observation 11), but have `kb.py build` emit `knowledge/MAP.md` as a short index (directories, entry documents, findings, questions, conjectures) plus generated companions for attempts and retrospectives, which currently dominate its length (`knowledge/MAP.md:199-500`).

Steps: change `map_document` and `generated` in `tools/kb.py:206-261` to write `knowledge/MAP-ATTEMPTS.md` and `knowledge/MAP-RETROSPECTIVES.md` and link them from `MAP.md`. Update the two citations of the map's role in `AGENTS.md:24` and `knowledge/INDEX.md:3` only if wording requires it.

Cost and breakage: small; one generator change and one rebuild. External links to sections inside `MAP.md` may need the R2 map if any exist.

Success test: `MAP.md` fits the orientation task in `AGENTS.md:24` without scrolling past hundreds of attempt lines, and `kb.py check` still verifies all three generated files byte-for-byte.

## 4. Keep as is

The dated, never-overwritten experiment directories and the rule that repairs get new endpoints (`AGENTS.md:11`, `CONTRIBUTING.md:34`) are the repository's core evidential mechanism and should not be traded for tidiness. The card layer with root-relative evidence paths and JSON-pointer field references (`knowledge/findings/F-0001-sequential-prediction-on-unique-texts.md:8`, `knowledge/registry/VOCABULARY.md:48`) gives every claim a checkable address, and `kb.py check` verifying those pointers (`tools/kb.py:354-362`) is exactly the right enforcement. The `data/` pointer pattern (`.gitignore:2-4`), the manifest, and the rights handling in `knowledge/DATA.md:249-265` correctly separate what Git may carry from what it may not. `bench/`'s versioned, overwrite-refusing, self-tested design (`bench/README.md:19`) is the model for any future shared code. The hand-built, Git-selected site with its public-path gate (`tools/build_site.py:78-105`, `site/README.md:13-15`) respects the no-CI constraint while preventing local-only material from leaking, and the sparse-clone recipe (`README.md:55-63`) is an honest answer to repository size. The one-line `CLAUDE.md` pointer to a single `AGENTS.md` avoids duplicated instructions and should stay the pattern for agent entry.

## 5. First week

1. **Label the frozen layers (R1).** Add era stubs to `research/`, `results/`, `src/` and `output/`, mark `PLAN.md` as the superseded 1 October plan, add the "new work goes to `experiments/`, `bench/` or `tools/`" rule to `AGENTS.md`, update `README.md:71-86` and `tools/kb.py:212-217`, rebuild once, and confirm `kb.py check` passes.
2. **Land the path map with a pilot move (R2).** Add `knowledge/registry/path-map.json`, teach `kb.py check` and `tools/build_site.py` to resolve through it, then prove it by moving `templates/` to `knowledge/templates/` with map entries and updated references in `AGENTS.md:33` and `CONTRIBUTING.md:9,19`.
3. **Write the minimum package shape into `CONTRIBUTING.md` and `templates/EXPERIMENT.md`, and add the prospective `kb.py check` rule (R3)**, including the two-level nesting limit and the requirement that each README name its endpoint run.
4. **Promote the data-inventory tooling to `tools/` (R4)** — `build_manifest.py`, `coverage.py`, `not_held.py` from `experiments/2026-10-12-data-inventory/` — update `knowledge/DATA.md:247`, and relocate the eight CLI behaviour tests beside `tools/kb.py` so the first-priority workflow no longer depends on a dated package.
5. **Split the generated map (R7) and fix the two stale top-level files**: emit attempts and retrospectives as companion generated files from `tools/kb.py:206-261`, generate or delete `llms.txt`, and correct the licence line in `CITATION.cff:9`. End the week by running the route test the restructure retrospective asked for (`maintenance/2026-10-12-repo-restructure/RETROSPECTIVE.md:47`): one metadata task and one reproduction task performed by someone who did not do this week's work, starting from `AGENTS.md` alone.
