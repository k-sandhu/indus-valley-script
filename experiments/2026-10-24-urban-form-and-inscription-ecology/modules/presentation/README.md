# Towns rebuilt over centuries

We created a 26-slide local PowerPoint from the reviewed urban-form and inscription-ecology study. It contains 13 editable charts, 13 editable tables and editable sequence diagrams. The presentation follows the earlier cream, teal and rust town-axis deck. All 26 slides carry notes; source-backed slides retain assertion IDs, exact titles, URLs, locators, dating evidence, uncertainty and local source hashes. The presentation embeds no acquired plans or images.

The final file is `D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/presentation/output/indus-urban-form-2026-10-24-v2.pptx`. Its logical path is `data/raw/2026-10-24-urban-form-and-inscription-ecology/presentation/output/indus-urban-form-2026-10-24-v2.pptx`. It remains local-only. `artifact-manifest.json` records its size, hash, authoring implementation, native elements and validation witnesses.

We corrected the manifest titles for slides 13 and 16 by extracting their exact text from the final PowerPoint's UTF-8 XML. The submitted manifest is preserved as `artifact-manifest-submitted-v1.json`, and `metadata-correction-v1.json` records the changes and hashes. The PowerPoint file is unchanged.

The slides cover twelve town histories, both directions of layout change, structural materials, named enclosure dimensions, one-source Dholavira chronology, the five published Mohenjo-daro residential phase samples, Dholavira's seal-context table, building and deposit relations, conflicting Lothal populations and earlier positive and failed research paths. The closing slides distinguish rival institutional explanations, label the three conjectures as untested subjective judgments and show the prospective evidence and power gate before confirmation. The Q4 chart is explicitly synthetic. Enclosure ratios compare six named architectural parts at three towns; they do not establish whole-town shape or a canonical module.

We preserved the denominators attached to each source. The 287 assertions and 42 source-use records describe the register. They do not count independent excavation projects or publications. Dholavira's 225 context rows include damaged, uninscribed and unidentified cases; 139 carry an explicit inscription label. Mohenjo-daro's changing phase samples retain their own residence counts. Point estimates for the Gini plot are shown with the source's untranscribed 80% intervals disclosed. No calibrated regional chronology or cross-town structure total is constructed.

The input snapshot is `input-manifest-v2.json`, with 21 input hashes. The assembled authoring data and full slide index are on D under `presentation/build/evidence-v2.json` and `presentation/build/v2/slide-index.json`. They include the repaired conjectures and prospective test design. No new primary source was acquired for this presentation; its contribution to coverage is an additional visual representation of the already reviewed observations.

The retained v1 deck preceded the addition of the six enclosure ratios. We authored v2 as a new endpoint, removed the lower-priority synthetic power plot to keep 26 slides and retained the sufficiency and power gate in the test sequence. We also changed line interpolation to straight segments and made the inscription-label and interval captions more explicit. Neither endpoint was overwritten.

`verification-v2.json` reports 71 chart numeric points checked against the frozen register or an explicit derivation, 26 notes pages, 13 embedded chart workbooks and zero images. The artifact-tool finalizer passed package integrity, import and native-chart workbook checks. Its five estimated table-overflow warnings were checked in Microsoft's native PowerPoint renders: all five tables fit, and every slide was inspected at 1280 × 720. Three charts were edited and resized in a private test copy, saved and reopened successfully. The final deck remained unchanged.

Authoring uses the bundled Node runtime and `@oai/artifact-tool`. The presentation skill's operation marker was run once immediately before the first authoring command. The finalizer and PowerPoint COM supplied the verification path. The implementation does not use python-pptx.

To author a subsequent endpoint, choose a new run label and execute each step separately from the repository root. The existing run labels intentionally reject replacement.

```powershell
C:/Python313/python.exe experiments/2026-10-24-urban-form-and-inscription-ecology/modules/presentation/prepare_deck.py v3
Copy-Item -LiteralPath experiments/2026-10-24-urban-form-and-inscription-ecology/modules/presentation/build_deck.mjs -Destination D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/presentation/build/build_deck.mjs
```

Run the copied JavaScript from its D: build directory with the bundled Node executable and the same run label. The build directory's `node_modules` junction resolves the bundled artifact-tool package. Then run `render_powerpoint.ps1` with the new final path and a new render directory, inspect every slide and run `verify_deck.py` with the new run label. Chart and table owner-slide expectations in the verifier and COM sample selections must change if the structure changes.

The strongest reading is that Indus towns repeatedly rebuilt shared frameworks while local construction changed. Independently dated sequences of the same streets, adjoining plots and primary-use deposits could decide whether the apparent persistence survives coherent phases and whether documentary objects add institutional information beyond ordinary storage, workshop debris and recovery conditions.
