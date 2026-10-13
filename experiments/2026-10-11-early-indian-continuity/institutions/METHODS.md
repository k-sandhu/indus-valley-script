# Curating component histories and checking their constraints

The unit of evidence is an observation tied to a locus, context or source table. The unit of proposed continuity is a practice or relationship with a possible carrier. These units let agricultural knowledge, specific crafting operations, priestly duties, patron support and meeting procedures have different histories.

The protocol preceded assembly of the new ledgers. Source selection was purposive and bounded to 14 works or editions and 30 observations. Texts were selected for exact, interpretable loci, with family-book and later material distinguished. Modern archaeological and philological studies were selected for component detail and competing explanations. The study is an exploratory synthesis, not a representative literature census. Neither observation counts nor repeated passages estimate historical prevalence.

`sources.json` records editions, versions, URLs, access date, inspected scope, rights and local witness hashes. A single work can have several files; overlapping J&B excerpts count once. The 2026 Jamison commentary supplies technical notes rather than a complete translated text. The restored RV is a modern edited text, not an ancient manuscript. Wilson's later commentary and Eggeling's translator notes are kept distinct from the cited verses. The source checks preserve a mislabeled RV download and a challenged HTML download with a PDF extension as excluded acquisitions.

`observations.json` contains our paraphrases and inference limits. Every row carries five separate date axes: composition, collection/redaction, manuscript witness, narrated time and archaeological context. Several axes are deliberately unresolved. We do not fill them with a generic date for a whole tradition. J&B's RV assessment is attributed and qualified; Brahmana prose is placed relatively after the RV; the three Pali suttas receive no single invented composition date. The DN 5 inner legendary king and DN 16 transferred monastic analogy are explicitly identified.

`claims.json` contains five candidate component histories, one carrier mechanism and one numerical sensitivity statement. A candidate can have an intermediate archaeological observation without a diagnostic match to its textual component. For example, the PGW rice occurrence supports regional agricultural persistence, while the ploughing verses specify neither rice nor its management. That gap is represented as an explicit false cross-domain diagnostic flag rather than silently filled by a broad label such as agriculture.

## Executable audit

Run the corrected endpoint in a new path:

```powershell
C:/Python313/python.exe -B experiments/2026-10-11-early-indian-continuity/institutions/audit-v2.py --output experiments/2026-10-11-early-indian-continuity/institutions/run-reproduction --check-witnesses
```

The script refuses any existing output directory. Without `--check-witnesses`, its categorical and numerical calculations use the tracked ledgers and run without local-only source files. Witness verification additionally requires the files listed in `sources.json`. `assemble-ledger.py` recreates the explicitly curated inputs only in a fresh directory with the same raw witnesses; it refuses existing input files. Its data are human-readable coding decisions and source-table percentages, not a scraped corpus.

The audit checks identifier uniqueness, reference integrity, date-axis presence, nonempty loci and limits, explicit competing mechanisms and hashes/bytes of available witnesses. The code cannot authenticate a date or a historical interpretation merely because the associated field exists. Those judgements remain open to source review.

Sensitivity removes flagged late RV, later RV, Brahmana and Buddhist observations; then also removes family-book observations lacking locus-specific core authentication. Further policies require a supplied intermediate archaeological witness and then a diagnostic feature joining it to the textual locus. A candidate must retain at least one textual observation it references. Eligibility is a property of the selected evidence and named requirements, not an ordinal strength score.

The first implementation omitted the surviving-text requirement. The corrected script and endpoint preserve run-v1 and record the change in `AMENDMENT-eligibility.md`. No source selection or rice input was changed after the first audit. Both endpoints hash their inputs; v2 additionally hashes the actual running script and amendment.

## Rice classification sensitivity

Published percentages are transcribed from accepted-manuscript Tables 2–4, checked visually against PDF pp. 13–14. Masudpur VII has one retained Mature and one retained Late context. Masudpur I and Bahola have six retained contexts each. The tables report standardized densities per 20 litres and their derived percentages; those densities are not raw independent-trial counts.

For each assemblage the lower domesticated percentage is the reported domesticated value. The upper adds its reported uncertain value. The other published categories stay fixed. A 0.02-point tolerance permits published rounding in the category sum; no renormalization is hidden. The code checks whether a Late lower bound exceeds the compared Mature upper bound. It reports that the one-context-per-phase Masudpur VII comparison disappears when either context is removed, and that the PGW spikelet endpoint is absent from the retained table analysis. It fits no trendline, significance test or population confidence interval.

Raw scans, complete texts, OCR, extracted pages and acquisition logs are local-only. The tracked package contains our prose, bibliographic metadata, selected published aggregate percentages and executable checks. Nothing is committed, pushed or published as part of this subtask.
