# Field recommendations

Status: **Exploratory**. Rebuilt and polished 7 October 2026 after two reviews and a disk-full interruption.

The catalogue contains **56 recommendations from 27 sources**, **35 source records**, **nine positions** and recommendations for **21 of 25 requested researchers**. It prioritizes object/context joins and reuse of regional/site/type analyses. Seven actions have explicit scores. [REPORT.md](REPORT.md), [summary.json](summary.json), [action-ranking.json](action-ranking.json).

F03 states the speaker's site-size/context proposal, with controls in an implementation note. F04/F53 are positions; F55 is a coverage note. F24 applies the comparative second-hand seal problem to Indus symbols/users. Rows now include short anchors, shared/disputed classification and author-group counts. Overlapping authors count together. [recommendations.json](recommendations.json), [positions.json](positions.json), [coverage.json](coverage.json), [author-groups.json](author-groups.json).

## Outputs

- [recommendations.json](recommendations.json) and [recommendations.csv](recommendations.csv): 56 recommendations, priorities or project aims with evidence, feasibility and scoped comparisons.
- [sources.json](sources.json): 35 source records, read scope, limits and witness hashes. The report's lecture section states its evidence limit.
- [positions.json](positions.json): nine interpretations/findings/expectations, including Frenez's written oligopoly model and F04/F53.
- [action-ranking.json](action-ranking.json): seven actions, criteria, scores, reasons and package links.
- [author-groups.json](author-groups.json): conservative author components and count definition.
- [summary.json](summary.json), [coverage-counts.json](coverage-counts.json), [roster-coverage.json](roster-coverage.json): counts and roster gaps.
- [row-rebuild.json](row-rebuild.json), [source-corrections.json](source-corrections.json), [missing-item-disposition.json](missing-item-disposition.json): original-row disposition, 14 source corrections and 16 missing-item leads.
- [polish-checks.json](polish-checks.json), [validation.json](validation.json), [audit-checks.json](audit-checks.json), [prose-check.json](prose-check.json): corrections, anchors, preservation, exports, links and prose.
- [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [registry-entry.json](registry-entry.json): selection, amendments, problems and proposed registry entry.
- [CHANGED-PATHS.json](CHANGED-PATHS.json), [FILE-MANIFEST.json](FILE-MANIFEST.json): changed paths and two-directory inventory with hashes.

The **19 first-pass files** and **18 reviewer witnesses** remain byte for byte unchanged. Active authored files use UTF-8 without BOM and LF endings. Third-party witnesses remain local or reuse existing literature holdings.

## Reproduce from the repository root

Exporter/audit require Python's standard library and the local source/anchor witnesses, including the acquisition log. **A fresh clone lacks the Git-ignored raw directory**; restore those witnesses before running. `curation.py` holds initial manual coding and `polish_coding.py` its dated corrections. Exporting repeats coding, counts and integrity checks; source interpretation needs reading.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python experiments/2026-10-06-field-recommendations/build_tables.py
python experiments/2026-10-06-field-recommendations/audit_catalogue.py
python experiments/2026-10-06-field-recommendations/build_tables.py --check
python tools/review_prose.py --path experiments/2026-10-06-field-recommendations --no-write
```

`build_tables.py --check` compares **ten exports** without writing. It checks 35 source hashes, 59 anchors, group fields, score arithmetic, references, encoding, fused prose/locators and preserved files. Two image anchors need visual review. Run `audit_catalogue.py` last after files change to refresh coverage/inventory. Optional acquisition uses `capture_sources.py`, requests and PyMuPDF, confined to local raw storage.

Review corrected rows, group counts and ordinal scores. Wright/Shinde/Bisht have no qualifying opened recommendation; Ratnagar's remark is outside this agenda. Full lecture transcription and Sproat's 2014 main article remain unavailable. Access failures and the disk interruption are recorded in the retrospective.
