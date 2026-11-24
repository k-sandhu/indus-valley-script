# Website generator

The website presents the repository's research record for both human readers and AI research agents. Git selects the source files. Python 3.13, Markdown 3.8.2 and Jinja2 3.1.6 build the pages. Templates use `.jinja` so the repository's downloaded-HTML exclusion does not hide them.

Run these commands from the repository root:

```text
python tools/build_site.py --out _site
python tools/build_site.py --worktree --out _site
python tools/build_site.py --check _site
```

Use an empty output directory or a previous build directory. A build reads HEAD by default. `--worktree` reads files selected by `git ls-files --cached --others --exclude-standard` for a preview. The preview banner identifies that mode; its source links still name HEAD. The check reports how many preview targets are absent at that commit. Commit the source before publishing so those links resolve on GitHub. All generated HTML belongs in the ignored output directory or on `gh-pages`. The generator adds no workflow.

The `data/` directory and public omissions are excluded. The manifest metadata table is the sole read exception: `data/MANIFEST.json` must be tracked, and its source file is never copied. Explore image assets must be tracked even in a preview. Missing document links become text labelled "not in the public repository". External hyperlinks remain usable; pages load local resources only.

## Navigation, sharing and visual structure

The masthead has seven entries: Home, Explore, Findings, Ideas, Questions, Record and Participate, plus links to site-wide Search and the GitHub repository. Ideas opens Working model and Conjectures. Record opens Papers, Registry, Data and Timeline. Participate opens the Agent hub, Agent rules (`AGENTS.md`), Contribute and Reuse & licence. Native HTML `<details>` menus keep every dropdown usable without JavaScript, and every existing page URL is retained.

Every page except `404.html` emits canonical, Open Graph and Twitter Card metadata backed by the local `assets/social-card.png` and `assets/favicon.svg`. Regenerate `site/static/social-card.png` with `python site/make_social_card.py`. Longer documents and cards include breadcrumbs, reading times and an on-page table of contents built from level-2 headings after stripping any repeated leading `#` title. `404.html` uses site-root `/indus-valley-script/` asset and navigation paths so missing nested URLs still render cleanly.

The home page opens with the project's purpose and commit counts, followed by four audience entry cards and visual cards for the interactive explorers. Below that sit all nine finding themes, visual credence bars for active working claims paired with dropped or weakened conjectures, the agent coordination summary with public-data open tasks, and the eight newest research runs.

## Research listings and conjecture views

Findings reads `knowledge/findings/README.md` when the selected source contains it. The guide supplies introductory prose, level-2 themes, their descriptions and ordered card lines, each a list item that links the card ID to its file and follows it with a result sentence and an italic status class. A card's path and status must match its indexed record. The final `Results recorded in packages but not yet carded` section supplies a separate list of report links through the ordinary publication gate. Cards absent from the guide appear under Other findings. If the guide is absent or does not parse, Findings groups all cards by area and records the fallback reason in `site-build.json`.

Open questions, Findings, Conjectures and the Experiment registry render their full lists in HTML when JavaScript is disabled. With JavaScript enabled, quick-filter chips, dropdown filters and search update the list and synchronize filter state into URL query parameters. Open and claimed question cards link to both the GitHub issue search (to check active claims) and the claim form, and include a task-specific agent prompt; completed and dropped question cards omit those controls. Conjecture listings display credence bars, and conjecture cards render an inline SVG credence trajectory chart whenever two or more history entries exist.

## Agent coordination and machine-readable feeds

The Agent coordination hub (`agents/index.html`) pairs with the full rendered rules (`agents/rules.html`) to provide a copyable bootstrap prompt, parallel contribution steps, verbatim status-class definitions from `knowledge/registry/VOCABULARY.md`, data-access definitions, repository skills, and a starter queue restricted to open tasks with `data_access: public` or `none-needed`.

All JSON indexes (`findings/index.json`, `questions/index.json`, `conjectures/index.json`, `attempts/index.json`) emit absolute public URLs. The build also emits:

- `llms.txt`: concise map linking `AGENTS.md` to its commit-pinned GitHub Markdown file alongside absolute public links to every section and JSON index.
- `llms-full.txt`: single-file Markdown digest of standing constraints, data-access definitions, working-model claims, findings by theme, conjectures and priority open questions.
- `api/summary.json`: machine-readable snapshot with counts, endpoints, bootstrap prompt and the public-data starter task queue.
- `search-index.json` and `search/index.html`: site-wide search across findings, conjectures, open questions, draft manuscripts and interactive explorers.

## Explore, the living atlas and visual packages

Explore publishes the self-contained interactive viewers tracked in the public repository at their repository paths, injecting description and social preview metadata into each viewer page:

- The **Indus living atlas** (`experiments/2026-10-26-indus-living-atlas/index.html`), its research reader (`research.html`), and its seven 3D city and building reconstructions (`reconstruction/index.html`). The site copy strips the optional online OpenStreetMap street basemap control and handler so every resource stays local.
- The **Reviewed sign catalogue** (`experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html`) and the **1979 chart atlas** (`output/chart_atlas/index.html`), retaining their embedded rows, tracked images, attribution and `<noscript>` tables.
- When `presentations/2026-10-13-relay-visualization/run-v1/index.html` is tracked in the public source, **The teaching relay** is published locally with external font links stripped; otherwise Explore links its GitHub README alongside the contemporary Bronze Age civilisations study.

## Local preview and publication

Start a local HTTP server to test search, filters and viewers:

```text
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. `site-build.json` records the source commit, inputs, copied assets, omitted links and unavailable pages. `--check` verifies these records, internal links, fragment IDs, absolute public URLs in JSON, text and sitemap feeds, assets, pinned GitHub links, heading order, `alt` text and the absence of external resource loads.

After reviewing and committing the source files, publish to the local `gh-pages` branch:

```text
python tools/build_site.py --publish
```

This command builds and checks HEAD, writes a new `gh-pages` commit with Git plumbing, and updates that local branch while preserving the current branch, index and working tree. A later invocation uses the existing `gh-pages` commit as its parent, and commit metadata uses the source commit's date. It does not push. Review the result before pushing.

The base URL is `https://k-sandhu.github.io/indus-valley-script/`. Page links are relative (except on `404.html`); canonical tags, social images, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `api/summary.json` and JSON indexes use absolute public URLs. The build output is deterministic for a fixed source commit and pinned dependencies.
