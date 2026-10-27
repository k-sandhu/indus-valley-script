# Shared infrastructure through rebuilding

We built a 26-slide illustrated presentation from the frozen source register and the final visual atlas. Eighteen slides contain actual source plans, photographs or context excerpts. Three charts and eight tables remain editable in PowerPoint. Every slide has notes with its evidence references, source locators and the frozen run hash.

The final local file is `D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/presentation/output/shared-infrastructure-plan-test-2026-10-24-v3.pptx`. Its SHA-256 is `6e8b17c3b9f15878efd96822b2e0f1702b18c324efcbf1f11afb726aa2364054`. The file is 23,167,136 bytes. `artifact-manifest.json` records the artifact, exact slide titles extracted from the PowerPoint XML and the validation paths.

The deck follows the six-town primary frame and treats Mohenjo-daro as a supplementary source control. It presents retained routes, renewed drainage, later blockings and compound closures alongside the evidence needed to join an inscription to an operating context and a dated rebuilding event. The charts preserve Lothal's conflicting publication counts, Dholavira's parallel metadata fields and both plausible western edges in Mackay's Plate XIX. The post-freeze Kanmer floor lead is labelled separately; it changes none of the frozen totals. No qualified institutional comparison was found, and the deck reports the effects as unestimated.

## Inputs and storage

The analytical input is root `run-v1.json`, SHA-256 `1217731e249aa6cb51eaeebc9a7346a2ec291dccbbdd6fff7616847d199ddd3d`. The visual input is `modules/visuals/manifest-run-v2.json`, SHA-256 `1db55b6a2e3ef1de7835ff31b14e7c95dcd8122eb66d94f0203c2ffef61a579b`. `input-manifest-v3.json` pins 19 authored input files and 95 local image assets used or inspected during assembly.

All acquired image bytes, display crops, temporary evidence payloads, PowerPoint files and rendered slides remain under the D: presentation directory. This module retains authored code and metadata. Source rights remain those of the original publications; this is a local research edition. The presentation contains no generated archaeological reconstruction.

## Rebuild and checks

`prepare_deck.py --version vN` checks the D: destination and frozen inputs, then prepares a new numbered evidence payload and display crops. Run the authored `build_deck.mjs` copy from the D: build directory with the same version argument, using the bundled Node runtime and `@oai/artifact-tool`. It exports through the presentations skill's finalizer. `render_powerpoint.ps1` renders every final slide in Microsoft PowerPoint and tests chart changes in a separate copy. `verify_deck.py vN` compares chart caches to the frozen source values and checks input hashes, chart workbooks, table placement and notes.

The artifact-operation marker ran once immediately before the first authoring export. Versions 1 and 2 are preserved as layout drafts. Version 2 enlarged source contexts and shortened the eligibility table; version 3 replaces two wrapped unit labels with `m`. These revisions change no archaeological value. PowerPoint rendered all 26 version 3 slides. Twenty-four renders are byte-identical to the individually inspected version 2 renders; slides 6 and 16 were inspected again after the unit-label repair. The final contact sheet was also inspected. `VISUAL-REVIEW.md`, `verification-v3.json` and `finalization-v3.json` record the checks and their limits.

Authors: GPT-6 family, exact serving variant unknown, Codex desktop collaboration. The presentation uses the cream, teal and rust design of the earlier local deck.

People retained or renewed connections while local access changed. A complete, dated comparison must establish whether shared routes outlasted internal divisions under matched preservation. If that preference disappears, or manufacture and secondary disposal explain the documentary pattern, the corresponding claim fails.
