# Academic-writing pass of 13 October 2026

We rewrote the project's published prose so that a reader from a neighbouring field, or a newcomer arriving from a search engine, can follow it. The pass changed wording only: every number, link, identifier, registered prediction and claim strength was held fixed and checked mechanically against the previous commit.

## Why

A first-time reader of the README, simulated by a fresh agent given no other context, could not tell what the Indus script was and stopped at almost every result, on terms such as "held export", "known-slot masks" and "crossing windows". We then reviewed recent research on how model-written academic text differs from human writing. The findings, with sources, are now in [WRITING.md](../../knowledge/editorial/WRITING.md#problems-in-ai-assisted-academic-prose). A scan of about 99,700 words of papers, cards and knowledge pages found that the surface habits removed on 2 October (stock words, em dashes) were nearly gone. What remained were the deeper problems the research describes: dense, noun-heavy sentences with slash compounds; labels coined during working sessions and never defined; paragraphs that list results without saying what they show; a template paragraph shared by several paper introductions; repeated statements of what a result does not establish; third-person references to "the owner" and "the user"; and citation labels that describe a source instead of naming it.

## What was done

Nine editing agents (Claude Opus 5.5 in Claude Code) each rewrote a separate set of files under the [brief](BRIEF.md): the six manuscripts with their methods and claim-evidence maps, the working model, timeline, index and conjecture cards, the research-direction and source pages, all finding cards, all question cards except Q-1005 and Q-1006, and the contributor documents. A tenth agent audited every external work cited in the six papers against the committed text; its results are in [CITATION-AUDIT.md](CITATION-AUDIT.md). The coordinating session reviewed each report, checked the edits it judged riskiest against their sources, and applied the citation corrections.

The audit checked 102 cited works. All exist and no link pointed to a different work. Twenty-eight needed correction: nine labels that described rather than named a work, eight metadata errors (for example Gulzar's paper dated 2018 instead of 2020, a wrong title word in R30, wrong page range for Chen and Goodman), eight sentences that said more than their source, two dead links replaced by Internet Archive copies, and one unreachable page.

## Checks

[check_invariants.py](check_invariants.py) compares each edited file with the last commit and reports lost or added numbers, links, inline code and front-matter changes. Across 157 changed Markdown files no link, code span or protected front-matter field was lost except where intended: the README's CI note moved to CONTRIBUTING.md, one publisher URL became its DOI, two dead links became archive copies, and one page number was corrected (394 to 393). Every added number was explained in the editors' reports (citation years, "8..18" written as "8 to 18", a card reference by ID). Line endings were restored line by line to match the committed files, because the repository stores bytes exactly (`* -text`).

The extended [prose scan](../../tools/review_prose.py) over the same files fell from 592 flags to 295: slash compounds from 555 to 285 (most of the rest are inside protected table values and front matter), third-person voice from 15 to 5 (all in author fields, registered records or ancient "users" of seals), template paragraphs from 3 to 0, formal words from 2 to 0, and descriptive link labels from 17 to 4 (labels that follow a complete reference entry). `python tools/kb.py check` passes after rebuilding `knowledge/MAP.md` for the changed card titles, and the website builds.

Total length of the edited files grew from 101,387 to 118,248 words (+16.6%), mostly from definitions and from unpacking compressed phrases.

## Not changed, and open items

Frozen experiment records, protocols, reports and retrospectives keep their original wording. `knowledge/DATA.md`, `data/MANIFEST.json` and cards Q-1005 and Q-1006 were not rewritten because another contributor had uncommitted changes in them; after that work was committed, only DATA.md's "owner decision" wording was changed to "maintainer decision". The PDFs in `output/pdf/` now lag their manuscripts: the settlement paper's PDF came from its own reviewed pipeline, and the Sanskrit-key PDF is rendered locally by `papers/006-sanskrit-key-calibration/render_paper.py`.

These need an author's decision or a separate fix:

- Paper 001 relies on "Fuls's explicit example" for reading direction, but no reference entry names that work.
- Paper 006 uses Perseus texts, a Sangam dataset and ORACC tablets without reference entries.
- Reference R06 (University of Lahore page) could not be reached by any automated route.
- `experiments/2026-10-11-settlement-prospection/sources-v6.json` still carries the dead rio-heritage.org links and the wrong R49 author.
- `experiments/2026-10-12-published-claim-tests/sanskrit-key/stage3h_novel_transfer.py` says 334 of 927 half-B texts in its docstring; its output and paper 006 say 356.
- `SUPPORT_PROTOCOL.md` in the null-calibration package gives 29,160 allocation cases; paper 002 and the package README give 29,169.
- `MATHEMATICS.md` and `MAIN_PROTOCOL.md` link a Hemerik and Goeman paper on PubMed Central (PMC6405018) while paper 002 cites their 2018 *TEST* article; these may be different works.
- `template_comparison.py` defaults to `min_per_component=10`; paper 001's methods say at least five texts per template.
- Q-1004 gives 297 image files named by volume and page and 23 corrected file names, where its own outcome and DATA.md give 299 and 26; its status is still open although it records an outcome.
- Q-1020 asks for a check against the CISI basic data, which DATA.md says has no dimension column.
- `experiments/2026-10-02-six-hour/physical-information/README.md` refers to "the user's alien-artifact idea".

Each editor's report lists the phrases whose meaning was unclear and which were left close to the original wording.
