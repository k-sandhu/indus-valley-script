# A2 acquisition and transcription plan

We will acquire the six named files and four Internet Archive metadata records, preserving each download in a separate local directory. We will check the six supplied byte counts and SHA-1 values and record SHA-256 values, retrieval times and the prescribed rights notes.

We will locate the printed pages in both Bhita scans and in Mahadevan 2003, render every page read with PyMuPDF at 300 dpi, and inspect the images. We will transcribe the numbered Bhita entries and findspot index and the three Mahadevan tables into local JSONL files. Local notes will retain uncertainties, source page references and decisions needed for later inclusion. Tracked files will contain code, identifiers, page locators, hashes and counts only.

We will validate JSONL syntax, page bounds and entry sequences. We will select ten records using the seed `a2-check`, reread their images, and report differing field names. We will scan our tracked files for source text from Mahadevan, run the prose review and compare the final Git status with the starting state. A retrospective will give the commands, outputs, repairs and remaining decisions.

The acquisition date is 21 October 2026 UTC. The transcriber is GPT-6.1-Sol through the Codex tool harness. We will write only within the A2 paths. Other sessions already have changes outside those paths; those changes remain untouched. We will run scripts that read downloaded files with `python -I` and keep executable code outside download directories.
