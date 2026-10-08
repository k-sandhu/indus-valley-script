# Owner checklist and upload steps

The owner confirmed own data/documentation CC0 1.0 and code Unlicense on 8 October 2026. Edition content retains CC BY 4.0. Author: k-sandhu, no affiliation or other personal details. The scorer and public methods are included. No upload, repository creation or visibility change was performed.

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
api.create_repo(repo_id, repo_type="dataset", private=True, exist_ok=False)
assert api.repo_info(repo_id, repo_type="dataset").private
commit = api.upload_folder(
    repo_id=repo_id, repo_type="dataset",
    folder_path="experiments/2026-10-08-hf-public-release/release",
    commit_message="Prepare reference benchmarks for private owner review",
)
print(commit.oid)
```

If that ID exists, inspect its contents/visibility before selecting an update; this recipe refuses an existing ID. Record the uploaded commit, download that private revision, compare every file against provenance/file-manifest.json and repeat loading/scoring. Inspect all 19 viewer configurations and embedded chart/row images. Confirm the issues URL and CFF citation, then upload the final reviewed revision while still private.

After owner approval, use the dataset Settings visibility control to make **ksaw008/indus-reference-benchmarks** public and record its released commit. Keep ksaw008/indus-research-data and the current GitHub research repository private. Instructions follow https://huggingface.co/docs/huggingface_hub/guides/upload and https://huggingface.co/docs/hub/repositories-settings.

The public EXCLUSIONS.md lists omitted material. Full decisions/hashes remain in rights-audit.json and build-records/. The 19 removed joins are local raw records. Review the new dated validation and reviewer reruns before upload.
