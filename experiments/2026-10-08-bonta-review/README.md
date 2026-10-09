# Package Q: Steven Bonta review

The corpus reproduces Bonta’s strong positional observations, with substantial exceptions; the lexical panel largely reuses dictionary-derived values, and the available sources leave validation rates, full field boundaries and physical metrology unresolved.

On **2,469 objects**, jar 740 is final **838/1,196 (70.07%)** and arrow 520 **192/225 (85.33%)**. Their **358** and **33** non-final tokens rule out categorical sequence-final use. Of the jar exceptions, **241** are followed by 400 or 090, mostly on Harappa and Mohenjo-daro objects. The new fish adjacency calculation gives **135** pairs against a shuffle mean **54.5505** (95% range **44–65**). The old zero-repeat/maximum-three result is withdrawn as structural support because text composition limits it. [Report](REPORT.md); [exceptions](response-2026-10-08-v2/terminal-exceptions.json); [fish test](response-2026-10-08-v2/fish-adjacency.json).

The selected panel has **9/10 exact dictionary matches**. All **13** permutations reaching nine normalized matches keep Bonta’s PU bundle; **0/600** moving it reaches nine. **Eight of ten** strings contain PU or PATI, values he reports obtaining by searching the same dictionary against those contexts. The **13/720** tail is therefore close to circular for those signs. Normalization is broader than Table 18’s individual value lists. The new Exploratory calculation holds PU/PATI fixed: **8/24 normalized**, **2/24 exact** reach nine. Dropping their eight strings leaves **2/2** matches, with tails **8/24 normalized**, **4/24 exact**. [Sensitivities](response-2026-10-08-v2/lexical-sensitivities.json), `endpoints`; [review census](review/role-pair-census.json).

The corrected audit finds **three repeated objects**, **zero conflicting labels** among the six candidates and **three parser false overlaps**. Only ICIT3656 is an ICIT-first reading; ICIT3084 is an alias in an MH-first entry, and ICIT2816 is an iconography remark. The lecture’s **12–15** readable checks and attempted/failure denominators remain unknown. Physical metrology has **zero** usable quantity joins. [Successor audit](response-2026-10-08-v2/validation-audit-v2.json); [metrology gate](run-2026-10-08-v1/metrology.json).

The revised ledger has **130 records**. All **126 original rows** were source-checked, including all **74 outside the review sample**. All **74** changed, chiefly through precise Table 18 labels and narrowed evidence fields; two changes only correct section labels. The itemized audit distinguishes each correction and retained sampled row. [Claims](claims.md); [audit](claim-source-audit-2026-10-08-v2.json), `counts`; [coverage](ledger-coverage.json). The [selection erratum](response-2026-10-08-v2/selection-errata.json) corrects M212/M898 to **M-1688/M-958**. Only **M-1688** of the three PU–TRA examples shows PU590 followed by full-height 033; **M-958** and **M-979** show short-stroke 003.

## Reproduce from the repository root

System Python 3.13.5 and NumPy 2.2.6 were used. The local pinned corpora and Cologne dictionary are required. Both response output directories must be new; the script restricts them to this package’s owned and local raw trees.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/review_response.py --output-root experiments/2026-10-08-bonta-review/response-replay-2026-10-08-02 --raw-output-root data/raw/2026-10-08-bonta-review/response-replay-2026-10-08-02
python -B -X utf8 experiments/2026-10-08-bonta-review/verify_response.py --replay response-replay-2026-10-08-02 --output response-checks-replay-2026-10-08-02.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

The response script reuses the reviewer’s independently implemented form generation, dictionary parsing and fish shuffle. It writes six aggregate JSON files, including the corrected validation audit and selection erratum, plus four local derivatives. Its [manifest](response-2026-10-08-v2/manifest.json) pins inputs and protected-file hashes. The verifier compares the response with the review, checks replay equality, quotes, ledger changes and preservation; it passed **110/110** checks in [the completed response replay](response-checks-2026-10-08-v4.json).

The original numerical run, original selection, registered protocol and reviewer files remain preserved. The review reproduced all six original aggregates and seven local derivatives and independently reproduced the lexical endpoints; its numerical verifier passed **54/54**. [Review](REVIEW.md); [independent review results](review/review-checks.json). Historical verification and package-check files apply to the earlier package state. The original verifier’s all-quotations-null condition predates the requested short quotations; the response verifier uses source-checked quote limits instead.

[revise_claims.py](revise_claims.py) rebuilds the revised ledger and itemized audit from the preserved pre-response snapshot. Earlier `curate.py`, `source_updates.py` and `audit_validation.py` describe the initial package; the delivered ledger and dated successor audit supply the revised annotations. [PROTOCOL.md](PROTOCOL.md) gives the dated amendment. [FILES.json](FILES.json) inventories the package; [RESPONSE-FILES.json](RESPONSE-FILES.json) lists every path created or changed during this response.

## Source limits and remaining work

[sources.json](sources.json) retains **47 source entries**, including the failed Kalyanaraman HTTP 403, now marked unverified. Captions remain unchecked against audio. The full manuscript PDF, exact historical validation set and rejected attempts, certified field boundaries, complete manuscript-reading inventory, Helsinki/object concordance and independent physical-quantity joins remain missing. [RETROSPECTIVE.md](RETROSPECTIVE.md) records the fixes and [registry-entry.json](registry-entry.json) proposes integration without changing the shared registry.

Source sampling should prioritize Lecture 4 at 45:40, Lecture 7 at 23:14–23:36, Lecture 11 at 14:10 and 19:26–24:00, letter page 5, Table 18 segments 78–81, and the corrected ICIT aliases in segments 141, 158, 185 and 216. Repeat the new sensitivities, confirm protected-file hashes, and check the dictionary licence at its pinned commit.
