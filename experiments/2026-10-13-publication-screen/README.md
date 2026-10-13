# Publication screen of untracked files, 13 October 2026

Three files should stay local, one needs a one-line edit, and the remaining 3,572 files can be committed to the public repository. The screen covered every untracked, non-ignored file and every modified tracked file in the working tree frozen at 05:18 UTC on 13 October 2026 (HEAD `0f8a1734`): 3,563 untracked and 13 modified tracked files, 206,992,283 bytes, of which 163,535,274 bytes are distinct content. The method was fixed in [PROTOCOL.md](PROTOCOL.md) before any file was screened. [decisions.json](decisions.json) assigns each file to one of 37 entries with its reason and scan evidence, and [summary.json](summary.json) totals them.

| Decision | Files | Bytes |
|---|---:|---:|
| track | 3,572 | 206,696,078 |
| track-after-edit | 1 | 10,609 |
| keep-local | 3 | 285,596 |

## What stays local or changes

The three allograph pair tables in `experiments/2026-10-12-published-claim-tests/allographs/run-2026-10-12/` (`pairs_k1.csv`, `pairs_k3.csv`, `pairs_k5.csv`) give each sign pair's root and letter value in the key published in the Lipi repository (`xlits.csv`, commit `fc8813a5`). Across its 2,259 rows, `pairs_k1.csv` names 440 of the key's 681 lettered signs; the roots agree with the key for 412 and the letter values for 311, and the k3 and k5 tables are subsets. The Lipi repository has no licence, so these tables stay local. The run's `summary.json`, `verification.json` and `REPORT.md` hold the aggregate results and stay tracked. Because `REPORT.md` links the tables, they are listed in [proposed-public-omissions.json](proposed-public-omissions.json). The proposed ignore lines are below; `proposed-gitignore.txt` holds the same lines but is itself local under the existing `*.txt` rule. A check with that file as `core.excludesFile` removed exactly the three tables from the untracked list.

```text
/experiments/2026-10-12-published-claim-tests/allographs/run-2026-10-12/pairs_k1.csv
/experiments/2026-10-12-published-claim-tests/allographs/run-2026-10-12/pairs_k3.csv
/experiments/2026-10-12-published-claim-tests/allographs/run-2026-10-12/pairs_k5.csv
/.claude/worktrees/
```

`experiments/2026-10-12-seal-text-identity/review/REVIEW.md` quotes one complete four-sign Lipi text with its CISI number, L-161, on line 32. The October 11 rule allows complete texts of at most three signs. The edit in decision D02 replaces the code string with a pointer to the local record and adds a dated publication note. The original bytes are preserved in `data/raw/2026-10-13-publication-screen/originals/`.

## Checks and results

**Lipi sequences.** The reference index holds 8,979 distinct four-code windows from the 5,680 Lipi faces and 5,804 single lines, in reading and visual order, and 3,992 complete texts of four or more codes. Every text file (3,543) was tokenized into runs of three-digit codes joined only by separators and compared window by window. As a positive control the scanner recovered 21 distinct complete texts from the quarantined `research/corpus/plate_audit/comparisons.json`, which the October 11 review recorded as holding 22 full sequences, and none from the twenty published catalogue windows. In the screened files, two had strict matches: the seal-text review above and a structure-first frequency table (`step3-segmentation/run-alternation-2026-10-12/summary.json`) whose list of the commonest segmented units includes one four-code unit counted 15 to 18 times. That entry is a recurrent formula count with no record identifier, so the file is tracked. Two discovery passes, added after the first run, accepted `W`-prefixed codes and underscore joins, and joined any codes within 80 characters to find context windows split across fields. The proximity pass matched 15 files; on inspection every match was dictionary keys of per-sign tables or code lists in prose, with no context windows.

Sixteen files contain five or more distinct complete Lipi texts of two or three codes. The largest sets are the anchor-expansion example ledgers and catalogue data: 36 attributed examples per run, each at most three codes with CISI number, commit pin and stated purpose, 44 distinct across the two runs and 42 of them not among the twenty published on October 11. They fit the bounded-example rule, but the notices still describe twenty windows.

**Lipi key and readings.** A separate pass looked for the key itself (a code next to its exact Lipi letter) and for Lipi readings from `glossing.csv` (72 forms of at least eight characters, 21 translations of at least three words). Only the three pair tables reproduced the key at scale. `sanskrit-key/stage3f/summary.json` lists twenty key entries as examples. The only translation match was the phrase "at the end" in ordinary prose.

**Third-party text and images.** The Bronze Age package's 1,703 acquisition files are access logs, byte-identical to the local request records; its census examples are identifiers, URLs, counts and dates, and no edition text from ORACC, AES, AED-TEI or LiBER is present. A sweep for transliteration diacritics found dense Sanskrit only in the anchor-expansion sense files, which follow the October 11 practice of short paraphrases with Monier-Williams entry and line pointers. `sanskrit-key/stage4/demo.json` instead copies 115 first-gloss fragments (78 distinct, at most 60 characters) from the Cologne `csl-orig` edition, which is CC BY-SA 4.0. The long-quotation candidates, found in 29 files, were our own prose, review quotations of our drafts, registry strings and bibliographic titles. No screened file embeds a raster image except Leaflet's icons inside `leaflet.js`. The 18 PNG files and the settlement PDF hold the project's own charts and editorial rectangles with no basemap. The satellite package derives its geometry from Copernicus Sentinel-2, Copernicus GLO-30 and ESA WorldCover (CC BY 4.0) with notices in its `THIRD-PARTY-NOTICES.md`; OpenStreetMap tiles load only at view time and are not packaged, and Natural Earth (public domain) and Leaflet (BSD-2-Clause) carry their notices. No screened file is a byte copy of an acquired response, a Lipi file or an October 11 omission target.

**Credentials and personal data.** No file matched the October 11 token patterns or the added AWS, Google, Slack, bearer-header, cookie, password-assignment and signed-URL patterns. Two text files contain email addresses, both placeholders: a `users.noreply.github.com` bot committer in `tools/build_site.py` and `example.invalid` in the site-generator test. Neither the owner's personal address nor its local part appears in any screened file; the address was supplied at run time through `SCREEN_OWNER_EMAIL` and is not stored here. Claude CLI records carry session and message UUIDs and usage, with no account identifiers. Six screened files contain the local Windows path with the user name, which 89 files already published at HEAD also contain.

**Size.** No file exceeds 50 MB. The largest are the anchor-expansion context summaries (38.2 MB, two byte-identical copies sharing one blob) and catalogue data (23.9 MB, two runs). The nine files over 2 MB compress to about 8 MB together. They are frozen endpoints computed from the local Lipi export and cannot be regenerated from a public checkout, so they are tracked as the October 11 review did for large frozen outputs.

**Earlier decisions.** No screened path is on the October 11 omission list. The pending `.gitignore` change only adds exceptions (settlement figures, viewers, packets and PDF, `data/MANIFEST.json`) and an `/_site/` exclusion. `tools/audit_git_payload.py` still forbids every `data/` path except `data/README.md`, so `knowledge/provenance/git-payload-review.json` currently reports `review-required` for `data/MANIFEST.json`.

## Conditions and owner decisions

Decisions D04, D06, D07, D09, D12 and D13 carry conditions. `THIRD_PARTY_NOTICES.md` and `knowledge/DATA.md` section 7 need to cover the 44 new Lipi examples, the twenty key examples, the CC BY-SA Cologne fragments and the Copernicus and WorldCover derivatives. `REUSE.md`, changed during this screen, now dedicates project material to CC0; it should exclude these components alongside the catalogue examples it already names. The payload audit tool needs `data/MANIFEST.json` allowed.

The owner should decide three questions. The satellite exports publish 30 m coordinates of screened anomalies and two reconnaissance prospects near Ganweriwala, and the package does not discuss whether candidate locations should be public. The site generator's `--publish` command writes a local `gh-pages` branch; it adds no workflow, but AGENTS.md rules out deployment scaffolding. The four-sign text in the seal-text review could instead be accepted as one more bounded, attributed example.

Outside this screen's scope, five files already published at HEAD (the privacy scanners and `check_review_fixes.py` in `experiments/2026-10-08-hf-public-release/`, including two history copies) contain the local part of the owner's personal address next to the word `gmail` inside regular expressions. The full address does not appear. Removing it from the public record would need edits to tracked files and a decision about history.

The satellite viewer's `index.html` and its Sentinel-derived panel images are ignored by extension rules, so a fresh checkout has the viewer's scripts and data but cannot display it. Exceptions for them would be an owner choice; they are open-licensed derivatives with notices.

## After the final freeze

Contributors added 28 files and changed 8 after 05:18 UTC: the licence texts, `CITATION.cff`, `llms.txt`, the revised `REUSE.md`, `THIRD_PARTY_NOTICES.md`, `public-omissions.json` and `tools/audit_git_payload.py`, site-generator records, and the edited seal-text review. The same three scanners found no sequence, key, credential or address match in them, and the review now carries the D02 edit exactly. In commit `feacf405` the notices, `DATA.md` section 7 and the audit tool meet conditions D04, D06, D07 and D12, and the coordinator withheld the satellite candidate exports, which `THIRD_PARTY_NOTICES.md` now states. A sweep of every file added since `0f8a1734` for anomaly identifiers within 150 characters of coordinates at four or more decimals found one remaining case: line 29 of `experiments/2026-10-12-satellite-prospection/research/terrain-audit.md` gives B04-T0136 to six decimals, a terrain support whose peak lies 167 m from the Kalibangan census reference. These checks are outside `decisions.json`; their outputs are in the raw directory under `delta-post/`.

## Files

| File | Content |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Method written before screening |
| [freeze_inventory.py](freeze_inventory.py) | Writes the frozen file list with sizes and hashes to the raw directory |
| [scan_sequences.py](scan_sequences.py), [sequence-scan.json](sequence-scan.json) | Lipi window counts per file |
| [scan_lipi_key.py](scan_lipi_key.py), [lipi-key-scan.json](lipi-key-scan.json) | Lipi key and reading counts per file |
| [scan_payloads.py](scan_payloads.py), [payload-scan.json](payload-scan.json) | Credentials, addresses, embedded images, record fields, quotation candidates, earlier omissions and size |
| [build_decisions.py](build_decisions.py), [decisions.json](decisions.json), [summary.json](summary.json) | Decision rules, per-entry evidence and totals |
| `proposed-gitignore.txt` (local), [proposed-public-omissions.json](proposed-public-omissions.json) | Lines and targets for the coordinator |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approach, problems and repairs |

Matched stretches, quotation candidates, key matches, the inventories and the backed-up originals are in the ignored `data/raw/2026-10-13-publication-screen/`. To reproduce from the repository root with the local corpora present: `python experiments/2026-10-13-publication-screen/freeze_inventory.py inventory-final.json`, then each scanner with `inventory-final.json` and its output name, then `build_decisions.py`. The scans find the encodings they were written for, and a file was opened by hand wherever a check fired or an asset's origin was not recorded.
