# Retrospective: blind verification of the town-axes study

This package began as a second run of study 4 of the [direction note of 20 October](../../knowledge/directions/parpola-forward-2026-10-20.md) and became a verification within its first hour. On checking the repository we found the same study already under way in `experiments/2026-10-21-town-axes/`, with a hashed protocol and four measurers at work ([notes/2026-10-21-duplicate-study.md](notes/2026-10-21-duplicate-study.md)). The session that briefed us judged that a second frozen test of the same claim would add cost but not evidence, and asked for an independent measurement made before the first study's results were read. We renamed the package, created no conjecture or question card, read only the other package's protocol, town list and star file, and froze our own protocol at 03:28 UTC on 21 October.

## Approach

The work had five stages, each written to its own directory: tools, imagery and plans (`tools/`, `infra-v1/`), astronomy and scoring (`astronomy/`, `analysis/`, `astro-v1/`), dating evidence (`dating-v1/`) and our date judgement (`dates-v1/`), two blind measurers (`measure-A/`, `measure-B/`), and the combination and comparison (`table-v1/`, `agreement-v1/`, `comparison-v3/`). Mechanical work went to five Codex runs ([RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md)); measurer B was three Claude subagents; design, date judgements, the combination code, the comparison and the prose stayed with the coordinating session. The order of freezes is recorded: protocol and measurement rules at 03:28, dates at 05:38 before any measurer started, all blind outputs at 07:30 before the other package's report was opened, though that report had existed since 05:50.

## Problems and repairs

**The disk filled.** About an hour in, the C: drive, shared with other sessions, reached zero free bytes while the imagery run was downloading. The run stopped acquisition and finished its tools; we deleted our own finished astronomy environment (387 MB) and the synthetic rasters of failed selftest runs (316 MB), logged in `data/raw/2026-10-21-town-orientations-verification/notes/disk-space-log.txt`. A resumption run then verified every raster against truncation, recompressed the imagery losslessly (saving 119 MB, every pixel checked), finished the plan library and validation from files already held, and downloaded new imagery only above a free-space threshold. When space was freed it completed imagery for all 33 towns.

**The bench synthetic run failed once.** `python -m bench shots --synthetic` could not rename a fixture file inside the OneDrive-synced package (`[WinError 5]`); the failed output is kept as `shots-synthetic-v1.stdout.txt`, and the rerun with fixtures outside the synced folder passed (`shots-synthetic-v2.json`).

**A strict dating rule left major towns undated.** Applied as written, the other package's three levels of evidence give a layout date to 17 parts in 11 towns, and none to Mohenjo-daro, Lothal, Surkotada, Banawali or Rakhigarhi. We kept that strict table as primary and added a liberal table that calibrates the oldest radiocarbon determination of each layout phase, both frozen before any bearing existed.

**Measurer runs were split.** To keep each run within a manageable context and to finish in parallel, each measurer worked in three regional shares with separate summary and log files, since several processes appending to one summary file would collide. The combination code at first let an older town file override a redone `-v2` file because of sort order; we fixed the loader before any combination was run.

**The comparison script had two bugs, both found by inspecting its output.** The first version kept only the four primary towns when rerunning the other package's exploratory table (`comparison-v1/`, superseded). The second averaged two plan readings of Rangpur on either side of the ±45° fold as ordinary numbers (`comparison-v2/`, superseded). The third version averages on the 90° circle and is the one reported (`comparison-v3/`). The automatic part matching of dates paired the wrong Harappa mound; `coordinator/compare_dates.py` replaces it with an explicit mapping.

**Excluded pages appear twice in a held scan.** Measurer B found that the *Interim Reports* vol. 2 scan contains the whole volume a second time, so Wanzke's pages also sit at PDF pages 228–239, outside the page guard (36–47) that the tools enforce. B saw them only as illegible thumbnails. The guard should cover both ranges.

**A held file has the wrong content.** The imagery run found that `research/literature/sources/kenoyer_1998_ancient_cities.pdf` contains a text headed "Decipherment of the Indus script", not Kenoyer's book; it was left in place and excluded from the plan library ([DATA-UPDATE.md](DATA-UPDATE.md)).

**One measurer log mixed encodings.** `measure-A/LOG-G.md` was UTF-8 except for 22 Windows-1252 curly quotes, which stopped `tools/verify_knowledge_repo.py` and `tools/review_prose.py`. The original bytes are kept as `measure-A/LOG-G.original-mixed-encoding.txt`, whose hash equals the frozen one, and `LOG-G.md` now holds the same text in UTF-8 ([coordinator/encoding-fix-v1.json](coordinator/encoding-fix-v1.json)). The repository check then ran; its 60 errors all lie in other packages ([repository-integrity-v1.json](repository-integrity-v1.json)).

**Commercial imagery appeared inside published figures.** Two plans available for Kotada Bhadli and Navinal are drawn over commercial satellite images, and measurer B excluded them; one of measurer A's crops of a published Shikarpur figure showed a narrow strip of such an image, disclosed and not measured.

## What we learned

Open 10 m imagery fixes the direction of a Harappan wall only when the wall is several hundred metres long and exposed: the runway validation gives 1.8° for 200 m segments and 0.75° for 400 m. Only the Lothal dock and Dholavira's middle town qualified, so a verification with open data can check the other package's imagery values at two towns of five.

Two measurers who use the same imagery and the same fitting tool agree far more closely than either is accurate. Ours agreed within 0.1° at Lothal, where the empirical error of a 190 m line is near 2°, and the other package's two measurers agreed within 0.08° there on their imagery; the 2° difference between the packages lies between the imagery sources. Independent measurers need independent imagery or tools for their agreement to measure accuracy, and the stated per-line errors were too small by a factor of about 1.5 on runways and on plans alike.

The astronomy and the scoring are the parts that transfer exactly between independent implementations of the same written definitions: 83 predicted deviations within 0.026° and identical statistics on the other package's tables. The fragile parts are the inputs: which walls a measurer takes as a town's main system, what a plan's arrow means, which source a dating rule ranks first, and how a grid near 45° is folded.

Measurer B flagged that the legend of Vats's Plate I gives the 1930 magnetic declination, which suggests that the Harappa plates' arrows have a recoverable meaning. B avoided the legend as a possible stated orientation. A later pass that classifies those arrows from the legend could move Harappa's plans into the primary value.

## Changed paths

All tracked files are under `experiments/2026-10-21-town-orientations-verification/`, plus the registry draft `knowledge/registry/attempts/TOWN-ORIENTATIONS-VERIFICATION-2026-10-21.json`. Raw imagery, elevation tiles, plan scans, renders, environments and Codex logs are under `data/raw/2026-10-21-town-orientations-verification/`. No other file in the repository was changed, nothing was committed, and the other package's files were read only.
