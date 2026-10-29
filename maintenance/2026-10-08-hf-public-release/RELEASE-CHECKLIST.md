# Owner checklist and upload steps

The owner confirmed own data/documentation CC0 1.0 and code Unlicense on 8 October 2026. Edition content retains CC BY 4.0. Author: k-sandhu, no affiliation or other personal details. The scorer and public methods are included. The coordinator uploaded version 0.3.0 privately. REVIEW-0.3.0.md verifies all 23 configurations (3,308 rows), decoded images and 136 local/Hub files at commit 541766d5ea8a4c3b3ec5fcc416ee764af8763afb. Package O performs no upload, repository creation or visibility change.

Three decisions remain open:

- [ ] Confirm the public issues repository and `https://github.com/k-sandhu/indus-reference-benchmarks/issues`. Update the single ISSUES_URL constant in release_policy.py and rebuild if another repository is chosen. The issue link must open before public release.
- [ ] Decide whether Hugging Face's rights terms permit the Lipi-derived files to remain in the private backup.
- [ ] Approve the final revision and visibility switch after private hosted review.

## Upload privately first

Use an authenticated owner session; upload only release/, excluding this checklist, rights-audit.json, build records, history, review/, private-store/ and raw records. This is a future manual recipe:

```python
from huggingface_hub import HfApi
api = HfApi()
repo_id = "ksaw008/indus-reference-benchmarks"
# The private preview repository already exists; inspect it before updating.
assert api.repo_info(repo_id, repo_type="dataset").private
commit = api.upload_folder(
    repo_id=repo_id, repo_type="dataset",
    folder_path="maintenance/2026-10-08-hf-public-release/release",
    commit_message="Update reference benchmarks to 0.3.1 for private owner review",
)
print(commit.oid)
```

The existing private preview holds verified 0.3.0. Record the updated uploaded commit, download that private revision, compare every file against provenance/file-manifest.json and repeat loading/scoring. Inspect all configurations, including v3 and the corrected chart, and embedded images. Confirm the issues URL and CFF citation while still private. Repeat these hosted checks for 0.3.1 after the coordinator updates the private preview. The private datasets-server viewer returned HTTP 501 during the 0.3.0 review; check every image-bearing viewer table after public visibility is approved.

After owner approval, use the dataset Settings visibility control to make **ksaw008/indus-reference-benchmarks** public and record its released commit. Keep ksaw008/indus-research-data and the current GitHub research repository private. Instructions follow https://huggingface.co/docs/huggingface_hub/guides/upload and https://huggingface.co/docs/hub/repositories-settings.

The public EXCLUSIONS.md lists omitted material. Full decisions/hashes remain in rights-audit.json and build-records/. The 19 removed joins are local raw records. Review the new dated validation and reviewer reruns before upload.
