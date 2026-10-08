---
pretty_name: Indus research private backup
tags:
- indus-script
- private-backup
- research-outputs
---

# Indus research private backup

`ksaw008/indus-research-data` is a private backup for large outputs from the private `k-sandhu/indus-valley-script` research repository. It stores 1,038 manifest-listed files totaling 3,406,008,409 bytes. The inventory below comes from the locally preserved hosting manifest, SHA256 `1408f92bbe38555e32a55aa1371a334fa70fc35dffe499a59d5d7d9f270103a2`. Its `verified` flags describe the earlier upload verification; Package O did not query the remote backup again.

| Set | Repository-relative path | Files | Bytes |
|---|---|---:|---:|
| restoration-predictions | `data/raw/2026-10-06-modern-restoration/main/` | 1029 | 3083272144 |
| restoration-frozen-model | `data/raw/2026-10-06-modern-restoration/frozen-model/` | 5 | 3214711 |
| helsinki1979-provisional-occurrences | `experiments/2026-10-07-helsinki1979-digitization/runs/2026-10-07-full-v1/occurrences.jsonl` | 1 | 105510364 |
| helsinki1979-provisional-ledger-import | `experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl` | 1 | 91947028 |
| helsinki1979-repair-v1-frame | `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v1/frame.json` | 1 | 61541918 |
| helsinki1979-repair-v2-frame | `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/frame.json` | 1 | 60522244 |


The 1,029 restoration-prediction files include per-fold/query JSONL, probability arrays, fitted counts and neural checkpoints. The five frozen-model files hold counts, three seed weights and a training register. These depend on the pinned Lipi export, whose licence was not found, and must remain private. The four Helsinki files are large backup copies of provisional occurrences, a provisional ledger import and the v1/v2 repair frames. Their 1979 source is CC BY 4.0, but the transcription failed its evaluations and remains quarantined. No third-party PDF scans are listed in this backup manifest.

The GitHub repository preserves code, protocols, aggregate results and research documentation. This backup preserves large generated payloads omitted from Git. Its path layout mirrors the local repository; it is not a set of `load_dataset` configurations. The separate public-release candidate selects licensed source derivatives and authored tables. Making that new dataset public would not change this backup’s rights or status.

## Restore and verify

Use an authenticated owner session with `huggingface_hub`. Do not embed tokens in research files. Run from the repository root:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py restore --repo ksaw008/indus-research-data
```

The existing `restore` implementation downloads **only** `data/raw/2026-10-06-modern-restoration/main/**` and `data/raw/2026-10-06-modern-restoration/frozen-model/**`. It does not restore the four Helsinki backups. It writes into the original repository paths and uses the current remote revision. Use a separate restore folder and a chosen revision with `snapshot_download` when checking a backup before replacing local files:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    "ksaw008/indus-research-data", repo_type="dataset",
    revision="COMMIT_SHA_FROM_OWNER", local_dir="RESTORE_DIRECTORY",
    allow_patterns=[
        "data/raw/2026-10-06-modern-restoration/main/**",
        "data/raw/2026-10-06-modern-restoration/frozen-model/**",
        "experiments/2026-10-07-helsinki1979-digitization/runs/2026-10-07-full-v1/occurrences.jsonl",
        "experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl",
        "experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v1/frame.json",
        "experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/frame.json",
    ],
)
```

To restore one part, retain only its path/pattern in `allow_patterns`. Restore paths must preserve their repository-relative layout. The local manifest does not record a remote commit SHA; obtain it from the backup repository before a pinned restore. The above example deliberately requires the owner to supply it.

[checksums-manifest.json](checksums-manifest.json) lists every file’s path, byte count and SHA256, including `backed_up_files_kept_locally`. After downloading, verify all 1,038 files against it with the read-only checker:

```powershell
python -B experiments/2026-10-08-hf-public-release/verify_private_store.py --root RESTORE_DIRECTORY --out experiments/2026-10-08-hf-public-release/private-restore-check.json
```

Missing or mismatched files fail that check. The original `hf_host.py verify --repo ksaw008/indus-research-data` checks the two restoration directories against the Hub; it does not check the four Helsinki backup files. Its `upload` command also regenerates a short README, so a coordinator installing this fuller card should do so after any such upload. No restore, verification against the Hub, upload or file deletion was performed during this documentation task.

Author/contact: TODO: owner-confirmed details. Keep this card and checksum manifest attached to the private backup. Source provenance and public-release exclusions are documented in the GitHub repository’s `knowledge/provenance/REDISTRIBUTION.md` and Package O’s rights audit.
