# Illustrated findings deck, 22 October 2026

We made a 24-slide HTML explanation of the project's findings, their possible social meanings and their contribution to decipherment. It follows the [field novelty review](../../experiments/2026-10-22-field-novelty-review/REPORT.md), with two clearly marked updates on birth-star names and town orientations. It introduces no new sign reading, confirmation experiment or claim of priority.

Open [the deck](../../output/indus-findings-2026-10-22.html) in a browser. Arrow keys move between slides; Overview selects a slide; Print / PDF prints all 24 slides. The content adapts to a narrow phone screen. Images, styles and controls are embedded in the single HTML file, so the deck works offline. Local report links depend on its position in the repository's output folder. External literature links need internet access.

Run `python presentations/2026-10-22-findings-slides/build_deck.py` to rebuild. The builder requires the four original CISI photograph files listed in `MANIFEST.json` and the generated cover at `output/indus-findings-assets/seal-use-illustration.png`. The output HTML and image-bearing QA files stay local because the catalogue-image rights remain unresolved. The cover-generation prompt is recorded in `IMAGE-GENERATION.json`.

`MANIFEST.json` records the slides, source paths and source hashes. The segmentation explanation points to the versioned benchmark replay; the birth-star hypothesis points to its preserved bench freeze. Toy English labels, the sun/son pun and arithmetic examples are explicitly marked as explanations, not Indus readings.

Authorship: Codex, GPT-6 runtime identity, using the Codex desktop harness, Python and Playwright CLI. No subagents contributed to this presentation. The research authorship remains as recorded in each source package.
