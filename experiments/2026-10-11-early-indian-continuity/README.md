# Early Indian institutions and cultural memory

This dated research package addresses two problems beyond script decipherment: transmission of practical and institutional knowledge through settlement change, and preservation or reconstruction of the past in early Indian texts. Its working thesis is selective inheritance combined with intellectual recombination.

Start with the [integrated findings](REPORT.md) or [manuscript](MANUSCRIPT.md). The [protocol](PROTOCOL.md) records scope and responsibilities. The [claim–evidence map](CLAIM-EVIDENCE.json) links coordinator claims to exact observations and outputs.

| Package | Contents |
| --- | --- |
| [Institutions](institutions/README.md) | Farming, craft, ritual roles, patronage and collective deliberation; source ledger, classification bounds, corrected eligibility filters and prospective tests |
| [Memory](memory/README.md) | Manu, rivers and social origins; typed chronology graph, synthetic compression example, source control and tests |
| [Coordinator control](coordinator/CONTROL-AND-MODEL.md) | RV 10.95 and Śatapatha 11.5.1; exact synthetic retention model |
| [Developed mechanisms](coordinator/DEVELOPED-PROPOSALS.md) | Carriers, selective survival, differential preservation and observations that could reject particular routes |
| [Independent review](review/REVIEW.md) | Source scope, chronology, arithmetic and adversarial assessment |
| [Review response](REVIEW-RESPONSE.md) | Corrections, preserved endpoints and unresolved questions |
| [Retrospective](RETROSPECTIVE.md) | Externally observable approaches, problems, repairs and outcomes |

## Repeat the calculations

Run commands manually from the repository root. Python 3.13 was used. The calculations use the standard library and authored JSON ledgers; the full institutional audit also verifies its local raw witnesses. Choose a fresh output path for every run. The scripts refuse to replace an existing endpoint.

```powershell
C:\Python313\python.exe -B experiments/2026-10-11-early-indian-continuity/institutions/audit-v2.py --help
C:\Python313\python.exe -B experiments/2026-10-11-early-indian-continuity/memory/analyze.py --help
C:\Python313\python.exe -B experiments/2026-10-11-early-indian-continuity/coordinator/retention_model.py --help
```

The package-specific guides give exact invocations and input requirements. [Institutional methods](institutions/METHODS.md), [memory methods](memory/METHODS.md), [retention-model protocol](coordinator/MODEL-PROTOCOL.md). The coordinator source checker additionally needs `pypdf` and the local acquired witnesses. Review source extraction and rendering use PyMuPDF (`fitz`). The independent retention check needs only the declared model artifacts. The final [program checks](verification.json) and [manifest](manifest.json) record the delivered files and integrity scope.

Some records are manual interpretations of source loci. Arithmetic reproduction does not independently reproduce those scholarly judgments. The source ledgers identify access scope, editions, dependency groups and witness hashes so another reader can inspect them.

## Preservation and reuse

Raw PDFs, HTML, source-language exports and unresolved-rights witnesses stay under `data/raw/2026-10-11-early-indian-continuity/`, which Git ignores. Repository artifacts contain authored prose, reusable code, metadata and bounded numerical summaries. Overlapping excerpts, alternate editions and copied witnesses remain dependent sources. The package does not redistribute acquired publications.

[baseline-v1.json](baseline-v1.json) inventories tracked and unignored files present at the start. Thirteen selected files also have exact local starting-byte snapshots. This does not provide byte backups for the entire inventory or for ignored corpora. The final verification distinguishes this package's navigation changes from concurrent work.

The first institutional eligibility output remains in `institutions/run-v1/`; the corrected filter and output are in `institutions/audit-v2.py` and `institutions/run-v2/`. The [amendment](institutions/AMENDMENT-eligibility.md) describes the defect. This program did not overwrite acquired sources, earlier manuscripts or frozen numerical endpoints to improve their results. No publication, deployment, scheduled automation or CI/CD was performed for this task.
