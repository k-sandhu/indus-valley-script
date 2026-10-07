# Backward chronology protocol

Recorded 6 October 2026, before assembling the table or computing coverage. Status: Proposed. This package asks how far a dated record of South Asian writing and other marks reaches backwards from the early historic scripts toward Indus material, and which observations could distinguish transmission from repeated invention.

## Inputs and selection

Read the repository instructions, index, writing and redistribution rules, experiment registry, literature retrospective, October 6 contribution assessment, and both October 2 South India reports and retrospectives. Reuse the preserved 2025 brochure, both 2026 *Inscribed Potsherds of Tamil Nadu* volumes, their acquisition manifests, and the reviewed aggregate results. Do not rerun the earlier stroke analysis. Its missing specimen-to-date joins remain acquisition targets.

Search the live web for excavation reports, dated assemblages, original continuity arguments, and reviews of Brahmi origins. Include all named cultural/site targets in Package E, even if a usable primary source or marked-object count cannot be recovered. Such rows record a missing observation; they do not fill a chronological gap. Add adjacent-region writing where it supplies a dated comparator or an explicit proposed route. Coverage is a bounded source inventory, not an archaeological census. Record successful and failed queries and downloads. Source entries distinguish full text opened, abstract opened, catalogue opened, search snippet only, and a reference encountered in another source.

Keep third-party downloads, extracts, page renders and response witnesses under `data/raw/2026-10-06-backward-chronology/`. Track our summaries, bibliographic metadata, code and aggregate outputs in this package. Quote no passage unless needed, with fewer than 15 words per source.

## Evidence schema and dating rules

Each row identifies a corpus or assemblage, region, sites, object classes, marked-object count and count unit, repertoire count, source locations, dating assessments, relation claims and access. Use null for an unrecovered quantity. A published approximate corpus total, a sign-occurrence total and a marked-object total have different units. Do not treat a site-wide occupation date as a dated inscription without an explicit context link. Do not combine radiocarbon, stratigraphic, typological and palaeographic dates into an averaged interval. Alternative datings stay in separate assessments with a named basis and an explicit decision on inclusion in coverage. Preserve lab identifiers and calibrated/uncalibrated distinctions when the opened source provides them; otherwise record the missing field.

Use astronomical negative years internally: -3500 denotes 3500 BCE. The 33 bins are [-3500,-3400) through [-300,-200). A boundary observation at -200 falls outside the bins. Source ranges are converted to half-open intervals for calculation; this endpoint convention does not assert one-year archaeological precision.

Grade dating links as A (marked specimen/deposit explicitly joined to a radiometric determination or independently dated historical inscription), B (excavated marked material joined to a reported stratigraphic phase with a stated chronology), C (cultural/typological/palaeographic attribution or unresolved specimen-to-sample join), or D (no verified marked context, unopened evidence, or uncertain provenance). A grade measures the observed link, not a universal judgment about a culture or publication. Radiocarbon dates of charcoal/rice date that sample and its association, not the incision directly. Contested associations are C until this package recovers the required join.

## Coverage computation

For each century count distinct included assemblage rows whose selected date ranges overlap it, separately for A, B, C and D. This is possible temporal coverage: a broad range does not prove a mark existed in every overlapping century. Record rows with image corpora separately from rows without verified images. Exclude pooled parent corpora from additive coverage when they overlap site rows; record the exclusion and retain their aggregate counts as reference data.

For marked objects report a lower assignable count only when an exact count's complete selected dating range lies within a bin, and an upper possible count when that range overlaps the bin. Unknown counts remain unknown; approximate counts and sign occurrences stay in separate fields. Counted objects in broad ranges are possible contributors to several bins and must never be summed across centuries. These bounds apply only to inventoried rows with known exact counts. They do not bound the archaeological population. Report unknown-count assemblages in every bin.

Compute longest runs of empty bins for the A-only series and for A+B, globally and by region. Report these as gaps in this selected source record. Also give regional row density, known count coverage and image accessibility. Do not infer transmission from overlap. Separate a chronological possibility from an observed chain of diagnostic forms.

## Comparisons and negative results

For each published continuity claim, identify the source examples and intermediate sites/periods it uses. Record missing dates, images, specimen joins and diagnostic shared combinations. Review Indus derivation, West Asian/Aramaic derivation and mixed/adaptation accounts of Brahmi as attributed positions.

The source-assembly question has a negative outcome if a securely dated, diagnostic sequence linking late Indus and later marks cannot be demonstrated from the recovered sources. Absence from this bounded inventory is not proof of ancient absence. A resemblance claim remains untested if it has no declared matching rule and chance comparator.

Write proposed tests for rare compound/positional persistence, feature-level shape comparison with complexity-matched null inventories, chronological seriation, and positional/combinatorial transfer. Name required data, controls, support/rejection criteria and which inputs already exist locally. Changizi, Zhang, Ye and Shimojo (2006) supplies a reason to model common shape configurations; its result is not itself a test of an Indus connection.

## Reproduction and amendments

Implement deterministic coverage and source/schema checks in Python, runnable from the repository root. Preserve computation outputs in a new run directory. Run the required prose review and inspect its findings. Any methodological change after an outcome is dated below and affected outputs are Exploratory. All documentary rows remain source assessments; Verified computation applies only to checked arithmetic and source integrity.
