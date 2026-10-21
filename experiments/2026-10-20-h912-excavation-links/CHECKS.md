# Checks and source handling

[Verification](verification-v1.json) passed 58 checks with zero failures. It checks every primary-source and render hash, the frozen protocol and observations, all fourteen registration joins, field and disposition accounting, the synthetic bench result and four byte-identical replay files. This is an author integrity check; another contributor has not independently reproduced the source coding.

The [scoped check](scoped-checks-v1.json) found no broken owned link among fifteen links then present, and Python and JSON files parsed successfully. The prose scan reported zero flags. The source-observation v1 file is unchanged from the hash recorded by the parent tablet study.

`python tools/kb.py check` reported 506 items, two errors, zero warnings and two generated-file maintainer notes. Both errors concern the concurrent town-axis package. Its missing attempt and README are outside this contribution. The [repository integrity result](repository-integrity-v1.json) reported 59 link errors elsewhere and no error naming this package. Those workspace-wide failures were preserved without editing another contributor's files.

The [source and coverage manifest](source-coverage-manifest.json) lists the acquired OCR and metadata, existing primary PDFs, exact page images, rights handling and changed coverage. Acquired sources and detailed export metadata remain local. No shared card, generated registry, data manifest, identity graph or spending ledger was edited.

Commands for the endpoint and replay:

```text
python experiments/2026-10-20-h912-excavation-links/build.py --out experiments/2026-10-20-h912-excavation-links/run-v1 --local-out data/raw/2026-10-20-h912-excavation-links/run-v1
python experiments/2026-10-20-h912-excavation-links/build.py --out experiments/2026-10-20-h912-excavation-links/replay-v1 --local-out data/raw/2026-10-20-h912-excavation-links/replay-v1
python -m bench shots --synthetic --directory data/raw/2026-10-20-h912-excavation-links/shots-fixtures --out experiments/2026-10-20-h912-excavation-links/shots-synthetic-v1.json
python experiments/2026-10-20-h912-excavation-links/verify.py --out experiments/2026-10-20-h912-excavation-links/verification-v1.json
python tools/kb.py check
python tools/review_prose.py --path experiments/2026-10-20-h912-excavation-links --no-write
python tools/verify_knowledge_repo.py --output experiments/2026-10-20-h912-excavation-links/repository-integrity-v1.json
```
