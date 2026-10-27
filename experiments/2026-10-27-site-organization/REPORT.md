# Website organization

27 October 2026. Authors: GPT-6.1-Sol through Codex CLI. Status class: record. Verification tier: submitted. Publication follows review of a committed-source build.

We group the existing website pages under Home, Findings, Ideas, Questions, Record, Explore and About. Ideas contains the working model and conjectures; Record contains the registry, timeline, papers and data; About contains contribution and reuse guidance. Native HTML disclosures retain all destinations without JavaScript, open the current group and mark its current page or section. A reader can follow Home to Findings to a card in two links.

Findings reads the shared guide's introduction, ten themes, theme prose and ordered result sentences. Each entry shows its card ID, title and status. Package results without cards remain a separate list with gated links. Any unlisted card enters Other findings. Missing or malformed guides fall back to the previous area grouping, with the reason in site-build.json. The guide itself routes to the index, and theme and result fields enter the complete JSON index. Search can combine theme and status.

Home retains the purpose, counts, Where things stand, model headlines, conjecture table and For agents bootstrap. It adds a conjecture count and ten recent attempts with date, status and report link. A link near the counts jumps to Recent work. The registry retains all attempts, orders dated records newest first, groups by date and supplies date links above search. An explicit record date takes priority over the experiment package date; equal dates use ascending attempt ID and undated entries come last. The timeline still renders its source document at its existing URL.

Explore gives the existing sign catalogue and chart atlas a sentence of description. The catalogue sentence comes from its package README. The frozen chart atlas has no adjacent README, so we use its description in the root README. Their embedded rows, attribution, tracked images and no-script tables remain intact.

## Living atlas decision

The living atlas is not copied or listed on Explore. Its `mapping/atlas.js` can request optional OpenStreetMap tiles from https://tile.openstreetmap.org. The site's runtime resources must be local and tracked. The checker now catches external tileLayer calls as well as the external loaders it already recognized; the skipped viewer and reason appear in site-build.json. [The asset review](atlas-review.json) records the tracked static resource closure and component notices.

The atlas README assigns project code to the Unlicense, authored prose and geometry to CC0, Leaflet to BSD-2-Clause with the full notice, and Natural Earth geometry to the public domain. It redistributes no source photographs or scanned plans. These terms support the local components; they do not make the remote tile service a tracked resource.

The research reader has no external runtime resources. The reconstruction entry selects the embedded run-v5 page, whereas viewer.html is an unfilled build template. We leave those pages in the repository with the rest of the bundle. A successor offline site integration needs an offline entry, the ordinary source-link gate applied to external-script links and embedded source records, and complete no-script place and model lists. The current atlas's no-script map fallback links to reports instead of listing its places. No publication gate was weakened to admit it.

## Verification

The [committed baseline check](baseline-check.txt) passes with 164 pages and 904 files. All 140 HTML page paths in the locally available origin/gh-pages tree are in the baseline; [the comparison](baseline-comparison.json) records the 24 pages added since that publication. [The final check](final-check.txt), [page comparison](page-diff.json), [determinism record](determinism.json), [parser checks](parser-test.json), [injected-resource check](gate-test.json) and [browser check](browser-check.md) give the final verification results. The final preview passes with 173 pages and 913 files: 47 findings, 22 conjectures and 266 attempts in the complete indexes. All 164 baseline pages, all 904 baseline output files and every published output path remain. The parallel findings contribution supplies the nine additional card pages. The two fixed-snapshot builds are byte-identical across all 913 files. All 34 parser and publication-gate regression checks and all 69 browser checks pass. An injected external tile loader makes the checker fail as required.

All output belongs under _site because tmp points to the excluded D: store. The final preview is _site/site-preview-final. The repeat-build harness freezes the Git-selected inventory and reuses exactly the source bytes read by the first build, so concurrent edits cannot silently change the comparison. It hashes every output file, including site-build.json, indexes and assets. It does not make a commit or alter the index.

The original public omissions, data exclusion and tracked manifest read exception remain. Excluded and absent report links receive the ordinary unavailable label; Explore assets still require tracked status in a preview. Repository source links remain pinned to the selected HEAD. Preview links to new uncommitted cards will resolve on GitHub after the selected inputs are committed and rebuilt.

We add no dependencies, data, CI/CD or recurring automation. We do not publish or touch gh-pages. [Changed paths](changed-paths.json) identify this contribution and exclude the two parallel runs, the supplied prompt and launch files. Before publishing, review the new guide, commit the chosen sources, build and check HEAD, and inspect that build. Atlas publication needs a separate offline bundle review.

The implemented navigation puts every card two links from Home and gives returning readers dated entry points. The deciding check is a reader following those routes in the final committed build; automated browser checks establish that the links, lists and filters work at the tested widths.
