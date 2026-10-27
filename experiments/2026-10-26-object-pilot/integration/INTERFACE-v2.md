# Reviewed integration delivery

The final reviewed JSON is `D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot/integration-v2/pilot-integrated-v2.json`. The final display is `catalogue-integrated-v2-polished.html` beside it. The first reviewed `catalogue-integrated-v2.html` remains preserved. Both use the same twenty records and local source paths.

Review status and review-reference hashes are the only JSON changes from integration v1. Every object field and assertion remains exactly equal. The queue is an unchanged copy of v1. The independent review passed eleven checks, retaining 539 inherited assertions and 96 source hash bindings. It directly checked the fourteen new image joins against primary plate and crop pixels. It did not retranscribe all 539 metadata assertions from original sources. Maintainer acceptance remains separate.

The display states that source and integration review are complete and links to the independent REPORT-v2.md. Missing fields use readable labels. Dholavira cards state that identity links remain unresolved. Image captions show page and panel labels, with internal metadata and source paths under collapsed Source details. The final polish gives a singular target count and generic source-page titles for shared Lothal plates. An inline favicon avoids the preview request for a missing icon. All exact metadata remain in the reviewed JSON.

Launch the existing read-only preview code against the final HTML, using an unused port after stopping any earlier preview:

```text
python -B -X utf8 experiments/2026-10-26-object-pilot/integration/preview_catalogue.py --html D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot/integration-v2/catalogue-integrated-v2-polished.html --port 8765
```

No server was started or stopped by this finalization. `validation-v2.json` records eleven passing diff and display checks; `polish-manifest-v1.json` records five passing display checks and identical image source paths. `manifest-v2.json` pins the reviewed inputs, first v2 outputs and finalizer code. The polish manifest separately pins the final display. The standalone HTML remains a local-only file deliverable.
