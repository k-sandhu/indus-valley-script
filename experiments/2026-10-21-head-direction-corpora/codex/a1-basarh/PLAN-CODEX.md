# Basarh acquisition and transcription plan

We will acquire the six named files and four item metadata records with `fetch_source.py`. Each download has a new directory and an acquisition record. The six fixed files will be checked against the supplied byte counts and SHA-1 digests. Item metadata will preserve the observed rights information. We use the requested run date, 21 October 2026 UTC.

We will locate the title pages, corrigenda, seal lists, register and plates with the OCR drafts, render every page read at 300 dpi with PyMuPDF, and inspect the images. The larger scans are the default. The smaller scans supply a second view where required. The transcription records will name the scan and use one-based PDF page numbers.

We will transcribe the two complete numbered lists and their sub-entries into local JSONL files. We will record line divisions, impression counts, duplicates, cross-references, findspots, uncertainties and printed corrections. We will then extract seal-related records from Spooner's field register. Source text and images remain under the owned `data/raw/` paths; tracked files contain code, counts, identifiers, locators, hashes and our prose.

We will validate JSONL fields, scan page bounds and number coverage, then independently read ten entries selected with seed `a1-check` a second time. Counts will distinguish completed image review from draft extraction. We will record every unresolved reading and coordinator decision in the source notes, write the source table and retrospective, run the prose check, and compare the final Git status with the initial state using read-only commands.

The author is Codex, based on GPT-6, running in the Codex Windows workspace harness. No comparison statistic or Indus record will be read or computed in this run.
