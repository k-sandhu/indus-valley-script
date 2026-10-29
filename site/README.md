# Website generator

The website presents the repository's research record. Git selects the source files. Python 3.13, Markdown 3.8.2 and Jinja2 3.1.6 build the pages. Templates use `.jinja` so the repository's downloaded-HTML exclusion does not hide them.

Run these commands from the repository root:

```text
python tools/build_site.py --out _site
python tools/build_site.py --worktree --out _site
python tools/build_site.py --check _site
```

Use an empty output directory or a previous build directory. A build reads HEAD by default. `--worktree` reads files selected by `git ls-files --cached --others --exclude-standard` for a preview. The preview label identifies that mode; its source links still name HEAD. The check reports how many preview targets are absent at that commit. Commit the source before publishing so those links resolve on GitHub. All generated HTML belongs in the ignored output directory or on gh-pages. The generator adds no workflow.

The data directory and public omissions are excluded. The requested manifest table is the sole read exception: `data/MANIFEST.json` must be tracked, and its source file is never copied. Explore image assets must be tracked even in a preview. Missing document links become text labelled "not in the public repository". External hyperlinks remain usable; pages load local resources.

## Navigation and research lists

The navigation has seven entries: Home, Findings, Ideas, Questions, Record, Explore and About. Ideas opens the working model and conjectures. Record opens the registry, timeline, papers and data. About opens contribution and reuse guidance. Native HTML disclosures keep the groups usable without JavaScript; the current section opens and the current page is marked. Existing page paths are retained.

Findings reads `knowledge/findings/README.md` when the selected source contains it. The guide supplies introductory prose, level-2 themes, their descriptions and ordered card lines of the form `- [F-NNNN](card-file.md) Result sentence. *status-class*`. A card's path and status must match its indexed record. The final `Results recorded in packages but not yet carded` section supplies a separate list of report links through the ordinary publication gate. Cards absent from the guide appear under Other findings. Search, theme and status filters use the complete `findings/index.json`, which includes each card's theme and the guide's result sentence.

If the guide is absent or does not parse, Findings groups all cards by area. `site-build.json` records the selected mode and the fallback reason under `findings_guide`. Links to the guide resolve to the Findings index. Theme fragments follow Markdown heading slugs.

Home retains the README purpose, Where things stand, working-model headlines, conjecture table and For agents bootstrap line. Counts now include conjectures. Recent work lists the ten newest research attempts with dates, status classes and gated report links; `record` attempts (coordination, release and preservation) appear only in the registry. The registry includes every attempt, ordered newest first and grouped by date, with date links above the list and undated attempts last. Dates use an explicit ISO record date first, then the date of its experiment package; equal dates use ascending attempt ID. Nested run-directory dates do not replace package dates. The timeline continues to render `knowledge/TIMELINE.md` at its existing URL. All list rows remain in HTML when JavaScript is disabled; filtering hides empty groups when JavaScript is enabled.

## Explore and the living atlas

Explore describes the reviewed sign catalogue using its package README. The frozen chart atlas has no adjacent README, so its description comes from the chart-atlas sentence in the repository README. Their embedded data, tracked images, attribution and no-script tables are preserved.

The 26 October Indus living atlas was reviewed for this change and remains off Explore. Its map script can request optional OpenStreetMap street tiles from a remote service. Those images are outside the tracked source and conflict with the site's local-resource rule. The checker now recognizes external `tileLayer` calls as well as external fetch and related loaders. `site-build.json` records the skipped viewer and its reason. The atlas's own README records project code under the Unlicense, original prose and geometry under CC0, Leaflet under BSD-2-Clause with its full notice, and Natural Earth geometry in the public domain. Source photographs and scanned plans are not redistributed by the atlas.

The research reader has no external runtime resources. The reconstruction entry selects the self-contained `reconstruction/run-v5/index.html`; `reconstruction/viewer.html` is a build template with a payload placeholder. These pages remain in the repository and are not copied as part of an incomplete atlas bundle. A successor site integration needs an offline map entry, gated links in its external scripts and embedded source records, and complete no-script place and model lists.

Start a local HTTP server to use search and filters:

```text
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. Pages also contain their full lists without JavaScript. Explore supplies tables of the viewers' embedded rows when JavaScript is disabled. `site-build.json` records the source commit, inputs, copied assets, omitted links and unavailable pages. `--check` checks these records, page links, assets, pinned repository links and external resource references. It reports size and the largest files.

After reviewing and committing the source files, publish to the local branch:

```text
python tools/build_site.py --publish
```

This command builds and checks HEAD, writes a new gh-pages commit with Git plumbing, and updates that local branch. It preserves the current branch, index and working tree. A later invocation uses the existing gh-pages commit as its parent. Commit metadata uses the source commit's date. It does not push. Review the result before pushing or changing GitHub Pages settings.

The base URL is `https://k-sandhu.github.io/indus-valley-script/`. Page links are relative; the sitemap and llms.txt use absolute public URLs. The build output is deterministic for a fixed source commit and pinned dependencies.
