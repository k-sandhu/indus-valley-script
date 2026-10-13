# Data round 1: shared instructions

13 October 2026. The coordinator runs four data packages in parallel. The owner's priority is a full and complete record of the inscribed objects with as much metadata per object as can be sourced. Every package reads these instructions first.

## Read first

`AGENTS.md`, `knowledge/DATA.md` (all of it), the question cards named in your package, `knowledge/provenance/REDISTRIBUTION.md`, `knowledge/provenance/catalogue-caveats.md`, `REUSE.md`, `LICENSE` and `knowledge/editorial/WRITING.md`. Use `python tools/kb.py search <terms>` to find earlier work, and reuse the data inventory's code and outputs in `experiments/2026-10-12-data-inventory/`.

## Files you may write

Only your package directory `experiments/2026-10-13-<slug>/` and the matching local directory `data/raw/2026-10-13-<slug>/` (ignored by Git). Other agents and the coordinator are writing other files now. Do not edit `knowledge/DATA.md`, `data/MANIFEST.json`, question cards, the registry, `.gitignore` or any other shared file; propose changes instead, in your package:

- `DATA-UPDATE.md`: the exact text or table rows to add to `knowledge/DATA.md`, with the section each belongs in and the numbers that change.
- `manifest-additions.json`: new or changed entries in the schema of `data/MANIFEST.json`.
- `question-updates.md`: the status and a dated outcome note for each question card you worked on.
- `registry-entry.json`: fields `id`, `theme`, `status`, `question`, `outcome`, `challenge`, `remedy`, `evidence`, `retry_when`, `status_class` and `area` (see `knowledge/registry/VOCABULARY.md`).

Do not run `git commit`, `push`, `checkout`, `reset`, `stash` or `clean`.

## Rights

Public-domain and CC0 data may be tracked. CC BY data may be tracked with its attribution recorded in your README and in `DATA-UPDATE.md`. Material with unclear or restrictive terms, acquired corpus texts and sign sequences, photographs and page images stay in your local directory; tracked files may hold identifiers, counts, coverage, field names, joins between identifiers, and your own judgements. Record the licence of every source you use, with the URL or file where you saw it.

## Network conduct

Use official APIs or downloads where they exist, follow each site's terms and robots rules, keep to about one request per second, and cache responses in your local directory so nothing is fetched twice. Identify requests with the User-Agent `indus-valley-script-research/1.0 (+https://github.com/k-sandhu/indus-valley-script)`. Never put an email address, name or other personal information in a request, header, file or log. Do not create accounts, request API keys, submit forms or contact anyone.

## Method and record

Write `PROTOCOL.md` before acquiring or computing: the question, sources, join rules, what counts as a match, and how you will measure accuracy. Keep ambiguous joins separate from confident ones and never force a match. Verify a sample of your joins or transcriptions independently and report the error rate. Write `README.md` as the package report: the result first, with the numbers that change in DATA.md, then method, sources, licences and limits. Write `RETROSPECTIVE.md` with the approaches, problems, fixes and outcomes. Keep scripts rerunnable from the repository root and give the commands.

Aim to finish within about three hours. If part cannot be done, finish the deliverables for what was done and say exactly what remains.

## Writing requirement

Maximize reader comprehension. Explain the idea directly in connected prose, keep necessary shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the argument. Follow `knowledge/editorial/WRITING.md` and run `python tools/review_prose.py --path <your package> --no-write`.

## Final message

Every path created; the coverage numbers before and after for each metadata field you touched; the join or transcription accuracy; licences of the sources; what remains; and anything the coordinator must decide.
