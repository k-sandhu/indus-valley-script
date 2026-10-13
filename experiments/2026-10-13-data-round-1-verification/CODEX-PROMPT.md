# Data round 1 verification: instructions for GPT-6.1-Sol

You are the independent verifier of two data packages written early on 13 October 2026 in the Indus script research repository at `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows; Python 3.13 as `python` with numpy, pandas, PyMuPDF and PIL; Git Bash and PowerShell). A coordinating Claude session wrote these instructions and will review your result before anything is committed. The packages are complete drafts that have never been checked by anyone other than their authors, and they are about to be committed to a public repository and folded into the project's data page. Your job is to find out whether their numbers are right, whether their scripts reproduce their outputs, and whether anything in their tracked files breaks the project's rights rules.

The two packages are:

- `experiments/2026-10-13-museum-open-access/` (question cards Q-1018 and Q-1019). It harvested open museum APIs and downloads (Metropolitan, Cleveland, Art Institute of Chicago, Smithsonian, Penn, V&A, British Museum) and joined museum records to local corpus objects. Its local data are in `data/raw/2026-10-13-museum-open-access/`. A separate Claude reviewer is writing `experiments/2026-10-13-museum-open-access/verification/` right now to check each join by eye; leave that directory alone and do not repeat that work.
- `experiments/2026-10-13-cisi2-basic-data-pilot/` (question card Q-1006). It transcribed 327 entries of the CISI 2 basic-data table (M-621 to M-947) by double blind AI reading and joined them to the local corpus. The transcribed values are local only, in `data/raw/2026-10-13-cisi2-basic-data-pilot/`, because CISI 2 is under copyright with reuse unverified.

Both packages followed `experiments/2026-10-13-data-round-1/COMMON.md`. Read it; its rights and record rules are the standard you check against.

## 1. Read first

`AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, `REUSE.md`, `LICENSE`, `knowledge/DATA.md`, `experiments/2026-10-13-data-round-1/COMMON.md`, the README, PROTOCOL, DATA-UPDATE.md, manifest-additions.json, question-updates.md and registry-entry.json of each package, the CISI 2 package's AMENDMENT-1.md and PROCEDURE.md, and the data inventory's coverage code `experiments/2026-10-12-data-inventory/coverage.py` with its outputs in `experiments/2026-10-12-data-inventory/run-2026-10-12/`. The question cards are `knowledge/questions/Q-1006-*.md`, `Q-1018-*.md` and `Q-1019-*.md`.

## 2. What to check

### 2.1 Reproduction

Before running anything, copy both package directories to `data/raw/2026-10-13-data-round-1-verification/snapshot/` and record a SHA256 for every file in each package in `data/raw/2026-10-13-data-round-1-verification/before-hashes.json`. Then rerun the offline steps of each package from the repository root, exactly as each README gives them, and compare every regenerated file with the snapshot.

- Museum package: run `build_joins.py`, `coverage_museum.py`, `harvest_summary.py`, `acquisition_record.py` and `write_manifest_additions.py`. Do not run any `harvest_*.py` script other than `harvest_summary.py`, and make no network request of any kind: the harvests are done and their caches must not be refreshed. If a script you are allowed to run would reach the network, stop it, record that, and move on.
- CISI 2 package: run `build_final.py`, then `python -I experiments/2026-10-13-cisi2-basic-data-pilot/join.py data/raw/2026-10-13-cisi2-basic-data-pilot/final.jsonl`, then `score.py score` and `score.py score --full`. Do not run `render.py`, `sample.py` or `parse.py`; the pass files are frozen and `PROTOCOL.sha256` must still match. Check that hash file against `PROTOCOL.md` and `AMENDMENT-1.md`.

Any regenerated file that differs from the snapshot is a finding: report the difference and restore the snapshot copy, so that the package directories end byte-identical to how you found them. Record the after-hashes in `data/raw/2026-10-13-data-round-1-verification/after-hashes.json` and confirm they equal the before-hashes.

### 2.2 Numbers

Every number in each package's README, DATA-UPDATE.md, question-updates.md and registry-entry.json should trace to an output file or to a count you can compute from the local data. Check them all, recomputing independently where you can rather than reading the package's own summary file. In particular:

- Museum package: the per-museum harvest counts; the class counts (confirmed, exact, ambiguous, unmatched, uninscribed) overall and for the 46 Q-1019 records; the 86 records decided; museum-accession coverage of 274 (5.84%), 324 (6.90%) and 339 of 4,695 (7.22%); the 15 families gaining a first museum number; the two families gaining a first dimension and six gaining an axis; the five candidate additions.
- CISI 2 package: 327 entries, 283 joined, 44 without a Lipi family; the agreement figures in both accuracy tables, recomputed from the pass files and adjudication files in its local directory; the coverage table (museum number 74 to 276, holding institution 74 to 283, FC number 0 to 283, excavation 278); the excavation comparison table (40, 182, 8, 4, 4, 2, 1, 1, 1, 35); the corpus-wide museum number rise from 274 to 476.

### 2.3 Combined coverage

Both packages measure museum-number coverage from the same baseline of 274 objects, and each reports its own after-figure (339 and 476). The data page needs one combined figure. Using the data inventory's usable-value rules, compute the set of Lipi object families with a museum number from any source: the older website export, the October 6 evidence census joins the museum package counted, the museum package's own joins, and the CISI 2 pilot's joined objects with a usable museum number (count separately with and without a bracketed digit). Report the union, each pairwise overlap, and the families that gain their first museum number from each package. Do the same for holding institution, if the inventory's coverage table has that field. Save the per-family membership as `data/raw/2026-10-13-data-round-1-verification/combined-museum-coverage.csv` and the counts as `experiments/2026-10-13-data-round-1-verification/combined-coverage.json` (counts and family ids only).

### 2.4 Rights and privacy audit of the files that would be tracked

The coordinator will commit each package directory as it stands, minus `__pycache__`. Check every file in both directories:

- No transcribed CISI 2 value (FC number, excavation number, museum or registration number, photograph source as read from the page) in any tracked file of the CISI 2 package, including code comments, docstrings, examples and test strings in `join.py`, `parse.py`, `schema.json`, `PROCEDURE.md` and `PROTOCOL.md`. The README says the protocol "contains two unattributed code examples written before this rule was applied to it"; find them and say whether they reproduce CISI values. The pilot's author was checking `join.py` for example values such as "MJD", "NMP 50", "1027" and "2019" when its session was cut off. Identifiers the project already treats as its own keys (CISI numbers such as M-621, Lipi family ids) are allowed.
- No acquired corpus text or sign sequence from Lipi (`data/normalized/lipi_observed_faces.jsonl` holds the sign sequences) in either package. Search tracked files for runs of four or more sign codes that match a Lipi inscription.
- Museum record text: Met, Cleveland and Smithsonian records are CC0 and may be tracked in full; Penn data are CC BY 4.0 and need the attribution the README gives; Art Institute of Chicago description fields are CC BY 4.0. V&A, British Museum, Louvre, MFA and Indian museum records are not openly licensed: tracked files may hold identifiers, numbers, short field names, classifications and flags, but no description, title or other record prose. Check `harvest/vam-records.json`, `harvest/bm-records.json`, `joins/decisions.py`, `joins/join-table.csv` and the README for such text, and quote the field names (not the text) of anything you find.
- No email address, personal name of the repository owner, credential, token or absolute path under `C:\Users\` in a tracked file. Note absolute paths as a minor finding.
- File sizes: list any tracked file over 1 MB.

Do not run `tools/audit_git_payload.py`; it writes a shared file.

### 2.5 Prose

Run `python tools/review_prose.py --path <package> --no-write` on each package directory and report the flags. Do not fix them.

## 3. Rules

- Write only these paths: `experiments/2026-10-13-data-round-1-verification/**` (this prompt and `launch.sh` stay unchanged) and `data/raw/2026-10-13-data-round-1-verification/**`. During the reproduction step you may let the packages' own scripts write their usual outputs, provided you restore the snapshot afterwards. Do not edit any package file, `knowledge/DATA.md`, `data/MANIFEST.json`, question cards, the registry, `AGENTS.md`, `.gitignore` or any other shared file. Other sessions may be editing shared files while you work.
- No network access. No `git commit`, `push`, `checkout`, `reset`, `stash`, `clean` or `add`.
- Tracked files you write hold counts, identifiers, verdicts and your own prose, never transcribed CISI values, Lipi sign sequences or non-open museum record text. Detailed evidence goes under `data/raw/2026-10-13-data-round-1-verification/`.
- Write `PLAN.md` first and `RETROSPECTIVE.md` at the end (approaches, problems, fixes and outcome).

## 4. Deliverables

In `experiments/2026-10-13-data-round-1-verification/`:

- `REPORT.md`: the verification report. Start with the verdict for each package (ready to commit as is, ready after named fixes, or not ready) and the list of findings ordered by severity, each with the file, the line or field, what is wrong and the fix you recommend in exact terms (for a wrong number, the right number and its source). Then the reproduction result, the numbers checked with their status, the combined coverage, the rights and privacy audit and the prose flags. State what you could not check.
- `findings.json`: one entry per finding with `package`, `file`, `location`, `severity` (`blocking`, `should-fix`, `minor`), `finding`, `fix`.
- `combined-coverage.json` as described in 2.3.
- `registry-entry.json`: fields `id` (use `DATA-ROUND-1-VERIFICATION-2026-10-13`), `theme`, `status`, `question`, `outcome`, `challenge`, `remedy`, `evidence`, `retry_when`, `status_class` and `area`, following `knowledge/registry/VOCABULARY.md`.
- `PLAN.md`, `RETROSPECTIVE.md`.

## 5. Writing

Follow `knowledge/editorial/WRITING.md`. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Use concrete observations and numbers, no promotional adjectives or stock phrases. Run `python tools/review_prose.py --path experiments/2026-10-13-data-round-1-verification --no-write` on your own directory and fix what it flags.

## 6. Final message

Every path you created; the verdict per package; the blocking and should-fix findings with their fixes; the reproduction result (files identical, files that differed); the combined coverage figures; and anything the coordinator must decide.
