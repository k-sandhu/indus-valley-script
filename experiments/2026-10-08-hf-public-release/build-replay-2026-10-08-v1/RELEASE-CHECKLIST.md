# Release decisions and manual steps

This is a local candidate. No repository was created, no file was uploaded and no visibility changed. The owner must complete these decisions before public release.

- [ ] Confirm CC BY 4.0 for the project’s annotations, compilations, documentation and aggregates.
- [ ] Confirm MIT for the project’s code and fill the copyright holder in LICENSE-MIT.
- [ ] Fill author name, affiliation (or none), contact and the final repository ID in README, NOTICE and CITATION.cff. The candidate citation date/version must be updated to the actual release.
- [ ] Decide whether to include the scorer here, as currently staged, and whether to publish a reviewed subset of the GitHub code repository. The current GitHub source links require private access. Public dataset release does not require changing the existing GitHub repository’s visibility.
- [ ] Decide whether to include the weight aggregates while their full method/code remains behind private links, or supply a separately reviewed public methods supplement. Those aggregates alone cannot replay the original fit.
- [ ] Review the file-by-file rights audit, table fields, all prose-overlap dispositions and source samples. Confirm the 1979 CC BY attribution and retained numeric ambiguities.
- [ ] Repeat local validation and benchmark scoring. Inspect hosted configurations and image retrieval after private upload.
- [ ] Approve the exact final candidate revision and make the final visibility decision.

## Upload for private review, after coordinator authorization

Choose a **new** dataset ID such as `NAMESPACE/indus-reference-benchmarks`; replace the example with the owner’s choice. Keep `ksaw008/indus-research-data` private. The following is a future manual recipe, not an action performed by Package O. It follows the official [upload guide](https://huggingface.co/docs/huggingface_hub/guides/upload).

```python
from huggingface_hub import HfApi
api = HfApi()  # Use the owner’s authenticated session; do not put a token in this folder.
repo_id = "NAMESPACE/indus-reference-benchmarks"
api.create_repo(repo_id, repo_type="dataset", private=True, exist_ok=False)
assert api.repo_info(repo_id, repo_type="dataset").private
api.upload_folder(
    repo_id=repo_id, repo_type="dataset",
    folder_path="experiments/2026-10-08-hf-public-release/release",
    commit_message="Stage attributed reference tables for private review",
)
```

Upload only the contents of `release/`, not this package’s local raw folder, private-store folder or the repository root. Download the new private snapshot at its returned commit revision, check it against `provenance/file-manifest.json`, and rerun local table loading/scoring. Verify all 19 configuration choices in the hosted viewer. Relative PNG paths are strings; obtain their files with `snapshot_download` and open them with Pillow.

When the owner approves public release, finish the placeholders and pending licence statements, update manifests and validation, upload that final revision to the new repository while it is still private, then inspect it. The owner can change **the new dataset** to public in its Settings tab’s visibility control, as described in [Repository Settings](https://huggingface.co/docs/hub/repositories-settings). Record the released revision. No visibility change for the private backup or GitHub repository follows from that decision.

## Exclusions

| Excluded material | Basis |
|---|---|
| Package A per-query predictions, model weights/counts and training register | Lipi-derived record-level content; no source licence found. Existing private backup stays private. |
| Lipi records/sign sequences and Mayig derivatives | Lipi redistribution basis unresolved; Mayig’s MIT notice does not resolve separate CISI photograph rights. Neither payload is included. |
| Full provisional 1979 transcription, ledger import and repair frames | Recognition criteria failed and the full transcription remains quarantined; carrier/surface concordances remain unresolved. |
| Package N’s future verified rows | Only a proposed protocol was available at the initial source inspection; completed results require a later audited addition. |
| Third-party PDFs and non-CC-BY page images | Only attributed 1979 source-derived PNGs pass the image allowlist. |
| Museum descriptions, photographs, raw API responses and corpus record contents | Unresolved payload rights; accession/CISI identifiers, count aggregates and our join assessments suffice for these tables. |
| Ascalone 2022 catalogue records | Aggregate metrology summaries only; the catalogue rows are not distributed. |
| Lecture transcript and record-level Frenez-test inputs | Not selected; current aggregates here are the small metrology tables. |

The source images and label candidates are available for inspection, but expert review is still pending. The two frozen benchmarks reproduce failed pipeline outcomes; their inclusion does not release the quarantined corpus.
