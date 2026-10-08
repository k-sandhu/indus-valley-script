---
pretty_name: Indus research private backup
tags:
- indus-script
- private-backup
---

# Indus research private backup

`ksaw008/indus-research-data` backs up large outputs from the private `k-sandhu/indus-valley-script` research repository. The manifest lists 1,038 files totaling 3,406,008,409 bytes. The 1,034 restoration files were removed locally with free-local after verification; the Hub now holds their only copy. The prediction/model groups total 3,083,272,144 and 3,214,711 bytes respectively. The four Helsinki backups remain locally.

| Set | Repository-relative path | Files | Bytes |
|---|---|---:|---:|
| restoration-predictions | `data/raw/2026-10-06-modern-restoration/main/` | 1029 | 3083272144 |
| restoration-frozen-model | `data/raw/2026-10-06-modern-restoration/frozen-model/` | 5 | 3214711 |
| helsinki1979-provisional-occurrences | `experiments/2026-10-07-helsinki1979-digitization/runs/2026-10-07-full-v1/occurrences.jsonl` | 1 | 105510364 |
| helsinki1979-provisional-ledger-import | `experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl` | 1 | 91947028 |
| helsinki1979-repair-v1-frame | `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v1/frame.json` | 1 | 61541918 |
| helsinki1979-repair-v2-frame | `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/frame.json` | 1 | 60522244 |


The 1,029 restoration files include query/fold JSONL, arrays, fitted counts and checkpoints; five frozen-model files hold counts, three seed weights and a training register. They derive from the Lipi export, for which no licence was found, and remain private. Four Helsinki outputs hold provisional occurrences, a ledger import and v1/v2 repair frames. Their 1979 source is CC BY 4.0; the full transcription failed evaluation and remains quarantined. No third-party PDF scans appear in the manifest.

GitHub holds code, protocols and aggregate research outputs; this backup holds large payloads omitted from Git, in matching repository-relative paths. It is a restore layout. The separate ksaw008/indus-reference-benchmarks dataset selects licensed edition derivatives and own compilations; its release leaves this backup's rights and visibility unchanged.

## Restore and verification

From the private repository root, use an authenticated owner session:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py restore --repo ksaw008/indus-research-data
```

restore downloads only the two restoration directories. For the four Helsinki files or a pinned restore to a separate folder:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    "ksaw008/indus-research-data", repo_type="dataset",
    revision="OWNER_SELECTED_COMMIT", local_dir="RESTORE_DIRECTORY",
    allow_patterns=['data/raw/2026-10-06-modern-restoration/main/**', 'data/raw/2026-10-06-modern-restoration/frozen-model/**', 'experiments/2026-10-07-helsinki1979-digitization/runs/2026-10-07-full-v1/occurrences.jsonl', 'experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl', 'experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v1/frame.json', 'experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/frame.json'],
)
```

Retain only the needed pattern to restore one part. Obtain the remote commit before a pinned restore; the local manifest does not record one. [checksums-manifest.json](checksums-manifest.json) lists all paths, sizes and SHA-256 values, including four locally retained backups. After downloading, check all 1,038 files:

```powershell
python -B experiments/2026-10-08-hf-public-release/verify_private_store.py --root RESTORE_DIRECTORY --out experiments/2026-10-08-hf-public-release/private-restore-check.json
```

hf_host.py verify checks local restoration copies against the Hub. Since those files were removed, it currently finds nothing to check. The coordinator added verify-remote, which compares every manifest entry with Hub-reported size/SHA-256 and downloads/hashes the 122 small non-LFS files:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py verify-remote --repo ksaw008/indus-research-data
```

The coordinator reports that this matched 1,038/1,038 files on 8 October 2026. Package O read the implementation and manifest but did not repeat the remote check. The coordinator's new publish-card command uploads this README:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py publish-card --repo ksaw008/indus-research-data --card experiments/2026-10-08-hf-public-release/private-store/README.md
```

## Owner note

Whether Hugging Face's rights terms permit continued private storage of Lipi-derived files is an open owner decision. This card records recovery steps without resolving that question.

Author: k-sandhu. Full source/rights decisions remain in the private research provenance records. This documentation revision performed no restore, upload, repository creation or visibility change.
