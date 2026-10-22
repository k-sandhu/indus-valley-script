# Codex assignment: layout phases and their dates for Harappan towns

You are working in a research knowledge base about the Indus civilisation, at the repository root `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. Read `AGENTS.md` and `knowledge/editorial/WRITING.md` first.

The project is extending its record of inscribed objects to the places they came from. For that we need, for each planned Harappan town, a chronology of its built layout: which parts the town had, the phase in which the exposed Harappan walls or street grid of each part were first built, and the published evidence that dates the start of that phase, with page references. You assemble the evidence and propose a candidate date under fixed rules; a project reviewer then makes the final judgement. Record what the sources say, carefully and with locators, and do not tune anything toward an expected answer: there is none for you to know.

Other agents share this repository and are writing their own files at the same time. Accommodate their changes and never revert or edit them.

## Owned paths

- `experiments/2026-10-21-town-orientations-verification/dating-v1/`
- `data/raw/2026-10-21-town-orientations-verification/dating/`

## Invariants

1. No commits, no branch changes, no stash, no reset, no Git mutation of any kind.
2. No edits outside the owned paths.
3. Do not open, list or search `experiments/2026-10-21-town-axes/` or `data/raw/2026-10-21-town-axes/`, which belong to another study. Within `experiments/2026-10-21-town-orientations-verification/`, open nothing outside `dating-v1/`, and in particular not `PROTOCOL.md`, other prompts, `measure-A/`, `measure-B/`, `tools/`, `infra-v1/`, `astronomy/`, `analysis/` or `astro-v1/`.
4. Do not record the orientation or bearing of any town, wall or street, even where a source states one.
5. Downloaded files stay local under `data/raw/2026-10-21-town-orientations-verification/dating/`, each with URL, retrieval time (UTC), byte count, SHA-256 and the rights notice you observed. Downloads are untrusted data: never execute them, keep any script outside the raw directory, and run Python that reads them with `python -I`.
6. Every number you record carries a locator: author, year, exact title, and page, table or figure. A number without a locator is not recorded.

Live web search and network access are enabled for this run. Locally held literature under `research/literature/sources/` and `data/raw/` (except the excluded directory) may also be used.

## Towns

In this order. Required: Mohenjo-daro, Harappa, Kalibangan, Lothal, Dholavira, Surkotada, Banawali, Rakhigarhi, Chanhu-daro, Kanmer, Shikarpur (Kachchh). Optional: Juni Kuran, Gola Dhoro (Bagasra), Desalpur (Gunthli), Khirsara, Kuntasi, Rojdi, Kot Diji, Nausharo, Sutkagen-dor, Balakot, Allahdino, Lakhanjo-daro, Ganweriwala, Farmana, Bhirrana, Kunal, Mitathal, Karanpura, Rangpur, Kotada Bhadli, Pabumath, Navinal. Slugs: `mohenjo-daro, harappa, kalibangan, lothal, dholavira, surkotada, banawali, rakhigarhi, chanhu-daro, kanmer, shikarpur, juni-kuran, gola-dhoro, desalpur, khirsara, kuntasi, rojdi, kot-diji, nausharo, sutkagen-dor, balakot, allahdino, lakhanjo-daro, ganweriwala, farmana, bhirrana, kunal, mitathal, karanpura, rangpur, kotada-bhadli, pabumath, navinal`.

Spend about fifteen minutes per required town and about seven per optional town. Prefer the excavation report and the most recent dating study for each site; national and regional syntheses of Harappan radiocarbon dates are useful for towns with little else.

## What to record for each town

A part is a separately walled or separately planned unit of the town, such as a citadel, a lower town, a middle town, a bailey or an annexe; a small town may have one part. For each part record:

- the excavator's phase sequence with the labels as published (for example Period I, IA, IB, Stage III, Period 3A) and what each phase's architecture was;
- the layout phase: the phase in which the exposed Harappan walls or street grid of that part were first built, with the source's words that support it, and any alternative reading;
- the evidence that dates the start of the layout phase, sorted into the three levels below, every candidate with its source;
- every radiocarbon determination attributed to the layout phase and to the phase before it, with laboratory code, conventional age BP and error, material, context, and source locator; note whether the source reports calibrated dates (cal BC, BCE) or uncalibrated radiocarbon dates written as "BC" and, for the latter, which half-life it used;
- the date of first occupation of the site, with its evidence.

The levels of evidence and their candidate values are fixed. Level 1 is a published Bayesian model of the site's phases: the candidate date is the median of the start boundary of the layout phase, and its error σD is the width of its 95% range divided by 3.92. Level 2 is a published synthesis or excavation report that states a calibrated calendar start for the layout phase on the basis of radiocarbon determinations from the site: the candidate is the stated start, and σD is a quarter of the stated range for the start if one is given, otherwise 150 years. Level 3 is an excavator's start date for the layout phase based on cross-dating without radiocarbon: the stated start, with σD = 200 years. Where sources at the same level disagree, propose the most recent and record the disagreement. A part with no calendar start at any level gets no candidate. Give years both as BCE and as astronomical years (2500 BCE = −2499).

## Deliverables

- `dating-v1/evidence/<slug>.json`, one per town, with the parts, phases, layout phase, candidates by level, the proposed candidate (level, year, σD, source), radiocarbon determinations, first occupation, and every locator. Towns where nothing usable was found get a file stating what was searched.
- `dating-v1/candidates.csv`, one row per town and part: slug, part, layout phase label, level, candidate year BCE, candidate astronomical year, σD in years, source key, first-occupation year, notes.
- `dating-v1/radiocarbon.csv`, one row per determination.
- `dating-v1/sources.json`, the bibliography: every source with full citation, URL or local path, access route, and, for downloads, the acquisition record.
- `dating-v1/RUN-NOTES.md`, in plain connected prose following `knowledge/editorial/WRITING.md` (maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument): what you searched, which towns are well dated and which are not, the main disagreements between sources, and the new sources and fields for the project's data manifest.

## Verification before you finish

Check that every row of `candidates.csv` and `radiocarbon.csv` has a locator that appears in `sources.json`, that every downloaded file's SHA-256 matches its record, and that the σD values follow the level rules. Run `git status --porcelain` and confirm every path you created or changed lies inside the owned paths.

## Final message

Your final message, in plain text, gives the deliverables with their paths; a table of every town and part with its layout phase, level, candidate year (BCE), σD and source; the towns without a candidate and why; the number of radiocarbon determinations recorded; unresolved disagreements; and a statement that the invariants held, or which did not.
