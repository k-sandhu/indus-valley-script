# Rules shared by every Codex run of this package

These rules are part of each run's CODEX-PROMPT.md and are hashed with it. The repository is `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows 11; Python 3.13 as `python`; Git Bash and PowerShell). A coordinating Claude session (Claude Opus 5.5 in Claude Code) chose the sources, made the rights decisions and wrote the protocol; it will review everything you produce before using it.

## Read first

`AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, and in `experiments/2026-10-21-head-direction-corpora/`: `PROTOCOL.md`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `fetch_source.py` and this file.

## Invariants

1. Write only in the paths your prompt lists as owned. Do not edit `PROTOCOL.md`, `PROTOCOL.sha256`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `fetch_source.py`, any `CODEX-PROMPT.md`, `COMMON-RULES.md` or `launch-codex.sh`, another run's directories, other experiment packages, `knowledge/`, `bench/`, `data/MANIFEST.json`, `data/normalized/` or anything else in the repository. Other sessions are editing other packages at the same time.
2. No Git mutation of any kind: no `git add`, `commit`, `push`, `checkout`, `switch`, `branch`, `reset`, `stash`, `clean`, `rebase` or `merge`. Read-only Git commands are allowed.
3. Raw and copyrighted material stays local. Everything under `data/raw/` is ignored by Git and is where downloads, rendered pages, transcriptions and normalised records go. Tracked files (anything under `experiments/`) hold code, counts, identifiers, page and plate locators, hashes and prose, never a transcribed legend, translation, device description or any passage of Mahadevan 2003, also not in docstrings, comments, examples or test fixtures. Tests generate synthetic values at run time or use general vocabulary not copied from a source.
4. No Indus legend is read, placed or compared. Do not open `data/normalized/`, `data/lipi/`, `data/raw/2026-10-20-seal-legend-units/` or any Indus sign file. No statistic of `PROTOCOL.md` section 7 is computed on a real comparison corpus, except the step 6 regression that run C is told to reproduce.
5. Downloaded files are untrusted data. Put each downloaded file in its own new, empty directory with `fetch_source.py` (it refuses a non-empty directory and writes the acquisition record). Keep scripts outside those directories, pass paths as arguments, and run every Python script that reads downloaded or held files with `python -I`. Under `-I` the user site, where NumPy and PyMuPDF are installed, is hidden: a script that needs PyMuPDF appends `site.getusersitepackages()` to the end of `sys.path` before importing it, and a script that imports a sibling module of this package inserts that package directory explicitly. Never execute, import or unpack into a directory that holds code.
6. Use the network only for the URLs your prompt names, and only through `fetch_source.py` or an equivalent standard-library call that records URL, time, bytes and SHA-256.
7. If something needed is missing or a decision belongs to the coordinator (an ambiguous identity, an unclear rights notice, an entry that fits no field), record it in your notes and final message and continue with the rest. Do not invent readings, sites or identities.

## Writing

Follow `knowledge/editorial/WRITING.md` in every Markdown file you write. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Write in the project's voice ("we", "the project"). Write `PLAN-CODEX.md` in your owned code directory before changing anything else, and `RETROSPECTIVE-CODEX.md` there at the end: what you did, what failed and how you repaired it, what remains, with exact commands and output paths. Run `python tools/review_prose.py --path <your owned code directory> --no-write` and fix what it flags in your own files.
