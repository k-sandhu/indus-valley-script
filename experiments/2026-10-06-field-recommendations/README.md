# Field recommendations

Status: Exploratory. Rebuilt 7 October 2026 after the source review and resumed after a disk-full interruption.

The catalogue contains **59 recommendations drawn from 28 sources**, with **35 source records** including comparisons and background, across six themes. It admits a recommendation for **22 of the 25 requested researchers**. Rita Wright, Vasant Shinde and R. S. Bisht have no admitted recommendation in the material opened here. These are access or selection gaps, documented in [roster-coverage.json](roster-coverage.json) and [coverage.json](coverage.json).

The strongest repeated priorities in the read sample are regional and chronological analysis, separation of object classes and production stages, and collaboration with accessible data. The report ranks work possible with current holdings and links packages D1, D2, E, G, H and the evidence census. Fuls's 2023 abstract already compares sign frequencies against per-site artefact counts; improving those comparisons requires defining the sample and its missing context. See [REPORT.md](REPORT.md).

## Outputs and evidence

- [recommendations.json](recommendations.json) and [recommendations.csv](recommendations.csv): one explicit recommendation, future priority or stated project aim per row, with source locator, feasibility, scoped comparisons and repository links. Every row is Exploratory.
- [sources.json](sources.json): exact metadata, opened/read scope, access limits and local witness hashes. Four lecture rows use the coordinator's caption check; this package did not independently read a full transcript.
- [positions.json](positions.json): seven interpretations or observations, including Frenez's written oligopoly argument on printed pp. 186-187. They are separate from recommendations.
- [summary.json](summary.json), [coverage-counts.json](coverage-counts.json), [row-rebuild.json](row-rebuild.json), [source-corrections.json](source-corrections.json) and [missing-item-disposition.json](missing-item-disposition.json): counts, disposition of all 33 old rows, 14 reviewed source corrections and all 16 missing-item leads.
- [validation.json](validation.json): encoding, witness hashes, repository links, export identity and historical preservation checks. These checks verify file integrity; source interpretation requires review.
- [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md) and [registry-entry.json](registry-entry.json): selection rules, changes, problems and proposed registry entry.
- [audit-checks.json](audit-checks.json) and [prose-check.json](prose-check.json): acquisition hashes, local Markdown links and the required prose scan.
- [CHANGED-PATHS.json](CHANGED-PATHS.json): paths created or changed during the rebuild and continuation.
- [FILE-MANIFEST.json](FILE-MANIFEST.json): every file in the owned and raw directories, with path, size, hash and role. The manifest excludes itself.

The 19 files in [first-pass/](first-pass/) preserve the original outputs and reviewer witnesses byte for byte. The active reviewer files are also unchanged. Historical files retain their original encoding; newly authored files are UTF-8 without a byte-order mark.

## Reproduce from the repository root

The exporter and audit use the Python standard library and existing witnesses. They need no network access or installation. `curation.py` is the manually coded authority; rerunning exports does not repeat source reading.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python experiments/2026-10-06-field-recommendations/build_tables.py
python experiments/2026-10-06-field-recommendations/audit_catalogue.py
python experiments/2026-10-06-field-recommendations/build_tables.py --check
python tools/review_prose.py --path experiments/2026-10-06-field-recommendations --no-write
```

`build_tables.py --check` compares eight exports without writing and checks source hashes, links, encoding and the preserved snapshot. `audit_catalogue.py` regenerates coverage and the inventory. Run it last if files have changed. Optional acquisition uses `capture_sources.py`, requests and PyMuPDF; downloads and extraction files stay in `data/raw/2026-10-06-field-recommendations/`. That directory also holds the acquisition log, failed responses and source qualifications.

The reviewer should sample the cited passages, especially the four mediated lecture rows, the undated Possehl and Miller pages, and the conditional agendas in Farmer-Sproat-Witzel. Full lecture transcription, Sproat's 2014 main article and the three roster gaps remain unresolved.
