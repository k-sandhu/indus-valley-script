# Protocol: research recommendations survey

Date: 6 October 2026. Status: Exploratory literature survey.

## Question

Which published recommendations, research priorities and explicit future-work proposals from Indus archaeology, epigraphy and computation can the project act on with its current sources and scripts?

## Inputs

Live web searches; the Frenez YouTube record at https://youtu.be/1i9q17ld_jU; primary publications, institutional records, recorded talks and interviews located in those searches; repository `knowledge/INDEX.md`, `knowledge/experiments/registry.json`, relevant retrospectives, context data plan and dataset landscape. `sources.json` records bibliographic data, URL, access level and the locator supplied by the search.

## Method and comparisons

Collect one row for each discrete recommendation or explicit research priority. Keep the source statement separate from this report’s assessment. For every row, record the named author, exact title, year, venue, URL, page/section/timestamp, data or collaboration required, feasibility with current holdings, published agreement or disagreement, and repository overlap. Mark whether source text was opened, returned as a snippet, or remained a citation lead. Treat positions as contested when a source explicitly argues against them. Do not infer consensus from silence.

Compare rows across six themes: corpora and data; context and chronology; linguistic/structural models; computation; collaboration and access; new excavation and scientific measurements. Prioritize work that has available inputs, clear comparison groups, and a stopping result.

## Selection rules

Include published or institutionally recorded material from 1990–2026 by the named researchers or coauthors. A row with no located recommendation documents a search gap but must say that no recommendation is being attributed. Use the user’s summary as the record of Frenez’s talk only if a transcript cannot be obtained; distinguish that summary from independently checked publication claims. Use exact publication metadata when available and expose unresolved bibliographic details.

## Negative result

A recommendation is not actionable now when the required independent observations, context, rights, or specialist access are absent. The survey is negative for the lecture transcript if no transcript or timed text can be retrieved, and negative for consensus if only one source supports a proposal or the opposing view is unlocated.

## Search limitation and amendment

The search was exploratory before this protocol was written; no predictive or numerical endpoint was calculated. This protocol was written before final thematic synthesis and prioritization. The source list and recommendations table therefore remain exploratory. YouTube’s page and timed-text endpoint returned throttling errors. Search results identified the title and speaker but did not expose event date, full venue metadata, transcript, or timestamps. Search-result snippets and citation-only leads are identified in `sources.json` and must not be read as opened evidence.


# Amendment, 7 October 2026: rebuild after source review

The first pass is preserved in `first-pass/`. The review found unsupported attributions, bibliographic errors and encoding damage. This rebuild is Exploratory and follows the row audit rather than a fresh prospective literature sample.

Read each source before admitting a recommendation. Include an explicit future-work statement, research priority or stated project aim with a printed page, named section or timestamp. A demonstrated method, descriptive finding or catalogue scope alone does not qualify. Keep interpretations such as the oligopoly argument in a separate position table when they are needed to check the lecture. Document named researchers with no qualifying statement in a coverage table, outside the recommendations table.

Reuse source witnesses in `research/literature/sources/` before acquisition. Save hashes and page locators for reused files, and save new responses and extraction files under `data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07/`. The coordinator's caption check supplies the four lecture statements and timestamps, with that mediation identified. Each agreement or dispute must cite an opened source and its own passage; remove surname matching as an attribution method. Read the published Sproat and Farmer-Sproat-Witzel replies before describing those debates.

Correct the reviewed source metadata, drop the nonexistent Miller citation, and use Miller's actual institutional project page only if it can be read. Add the missing recommendations where the primary text contains an explicit agenda; log exclusions where it does not. Link project coverage to the October 6 chronology/region (D1), sign/context/seals (D2), backward chronology (E), resemblance baseline (G), byproduct inventory (H) and evidence census packages, distinguishing completed results from plans.

Write active deliverables as UTF-8 without a byte-order mark. The builder must reject invalid UTF-8, a BOM, replacement characters, suspicious question marks inside words, and common mojibake sequences. Check source and repository references, export identity, preserved-file hashes and the required prose scan. Numerical checks verify export integrity, not source interpretation.

## Continuation after disk interruption, 7 October 2026

The coordinator reported Windows error 112 and subsequently freed disk space. Before further edits, the continuation checked the preserved snapshot hashes, Python syntax, JSON parsing and source-witness hashes. No truncated file was found. Keep existing witnesses, avoid redundant downloads and record the state check in the retrospective. All revised outputs remain Exploratory.

### Additional source selection, 7 October 2026

A final bounded search for the remaining roster gaps located Green's 2021 review, *Killing the Priest-King: Addressing Egalitarianism in the Indus Civilization*. Read its explicit future-work passages before deciding whether to admit additional rows. The extension follows the same prescription rule and remains Exploratory. Preserve the exclusion of inferred recommendations from Green's 2016 method paper. The same search located an author-deposited 2005 Lothal chapter record; use it to resolve metadata separately from recommendation selection.
