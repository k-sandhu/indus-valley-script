# Dating brief: when each planned Harappan town was laid out

Brief of 21 October 2026, given verbatim to one research agent. We are compiling a table of Harappan towns with an orthogonal layout of walls and streets. Other agents measure the directions of those walls and streets; this task records when each layout was built and on what evidence. The towns are listed in [towns-v1.json](towns-v1.json): all eleven `required` towns, then as many `optional` towns as the literature allows.

## What to record

For each town, identify the layout phase: the excavator's phase or period in which the Harappan fortification walls, platforms or street grid that are exposed today were first built. Many towns were occupied before the layout (Harappa in the Ravi and Kot Diji phases, Kalibangan in Period I, Dholavira in Stage I, Banawali in Period I, Rakhigarhi in its early phases), and several towns have more than one part built at different times. Record the layout phase of each part separately, with the excavator's description of what was built in it and the page where this is stated, and record the phase of first occupation as well.

Then collect the dating evidence for the start of each layout phase:

- every published radiocarbon determination from the layout phase and from the phase immediately before it: laboratory number, material, context and depth, the conventional radiocarbon age in years BP with its one-sigma error, and the calibrated range as published with the calibration curve used. Note the half-life on which an age is quoted; older Indian determinations (TF and PRL laboratories) were often published on the 5730-year half-life, and the conventional age on the 5568-year half-life is the published value divided by 1.03. Record exactly what the source prints and add the converted value in a separate field;
- any published Bayesian model of phase boundaries, with the start boundary's median and 95% range;
- the excavator's own date range for the layout phase and for first occupation, and its basis (radiocarbon, cross-dating of pottery or seals, or stratigraphic estimate);
- later re-datings or syntheses (for example Possehl's 1999 and 2002 radiocarbon compilations, the Harappa Archaeological Research Project's reports, Sengupta and colleagues on Dholavira, Kharakwal and colleagues on Kanmer, Shinde and colleagues on Rakhigarhi) and where they disagree with the excavator.

Record every source with author, year, title, journal or series, volume and page, and a URL or local path. Many reports are held locally: search `data/MANIFEST.json`, `research/literature/sources/` and `data/raw/2026-10-06-evidence-census/sites-deep/`. Save any file you download under `data/raw/2026-10-21-town-axes/dating/` with its URL, retrieval time and SHA-256. Web search and fetch tools may be deferred; load them with ToolSearch if you need them.

## Output

Write one JSON file per town to `experiments/2026-10-21-town-axes/dating-v1/towns/<slug>.json`:

```json
{
  "town": "slug", "compiled_utc": "...",
  "parts": [{"part": "citadel|lower town|whole town|...", "layout_phase": "excavator's label", "what_was_built": "...", "locator": "source id and page",
             "excavator_range_bce": [0, 0], "excavator_basis": "...",
             "radiocarbon": [{"lab_no": "...", "material": "...", "context": "...", "phase": "...", "age_bp_printed": 0, "sigma_printed": 0, "half_life_printed": 5568, "age_bp_5568": 0, "sigma_5568": 0, "calibrated_published": "...", "curve": "...", "source": "src1", "page": "..."}],
             "bayesian_start": null, "syntheses": [], "conflicts": "..."}],
  "first_occupation": {"phase": "...", "range_bce": [0, 0], "basis": "...", "locator": "..."},
  "sources": [{"id": "src1", "citation": "...", "url_or_path": "...", "sha256": null}],
  "notes": "..."
}
```

Write years BCE as positive numbers in fields ending `_bce`, and `null` where a source gives no value. Write `METHOD.md` in `dating-v1/` describing in connected prose how you searched, what you could and could not find, and the conflicts you met, and `sources.json` with every source. Put any scripts in `dating-v1/code/`.

## Independence

Read only this brief, `towns-v1.json`, the `dating-v1/` directory and your sources. Do not open any other file or directory under `experiments/2026-10-21-town-axes/`, the file `knowledge/directions/parpola-forward-2026-10-20.md`, or any directory `experiments/2026-10-20-*`. If a source states the orientation of a town's walls or streets, ignore it; it belongs to the other agents. Write only in `dating-v1/` and `data/raw/2026-10-21-town-axes/dating/`. Do not commit, stash or switch branches. When you finish, reply with the list of towns written and the paths of your files.

## Writing

Write `METHOD.md` and the `notes` fields for a reader who has not seen this brief: maximise comprehension, explain each step directly in connected prose, keep the shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the explanation. Use "we" for the project's actions.
