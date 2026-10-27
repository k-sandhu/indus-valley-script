# Validation

[results-v1.json](results-v1.json) records seven passing checks: all 29 dispositions exist; the first visual-pass hash is unchanged; source-font rendering follows the visual seal; all inspected source images match their hashes; primary group boxes lie inside the original images; no historical reading traversal is accepted; and the duplicate impression payloads have the same hash. Preparation also checked all alternate-view boxes against their image dimensions before sealing.

The local review file contains every selected face exactly once. Its source-alignment assertions cite the normalized face-file hash and source record ID, and image witnesses retain their original dimensions. No source photograph was cropped, reflected or rotated for this review. Group orientations in the catalogue alignment describe observed relationships to the source drawings.

Commands run from the repository root:

```text
python -X utf8 -B experiments/2026-10-22-face-adjudication/prepare.py
python -X utf8 -B experiments/2026-10-22-face-adjudication/render_codes.py
python -X utf8 -B experiments/2026-10-22-face-adjudication/build_reviews.py
python -X utf8 -B tools/review_prose.py --path experiments/2026-10-22-face-adjudication --no-write
python -X utf8 -B tools/kb.py check
```

The preparation, rendering and final builder refuse existing endpoints. The two observation files between these steps are authored visual records, not automated predictions. Reproducing the joins does not recreate an independent visual judgment. The parent integration records a separately sealed reader and reviews the proposed source maps and image-identity repairs.

The task is source review, so it produces no new segmentation benchmark or real confirmation read. Record-level observations remain local. The whole-repository verifier is run into a new package output; its earlier unrelated link failures are recorded without editing their source packages.

`kb.py check` passes with 560 items, no errors, no warnings and two maintainer notes. The [whole-repository result](repository-verification.json) records 58 earlier broken links and none in this package. The prose check flags only `Lipi/CISI` in the frozen protocol as a slash compound. We retain that frozen wording and its hash; it names the source holdings. Source-specific supplemental observations were moved out of the tracked builder into a local authored input after payload review. The exact code that produced `results-v1.json` is preserved locally as `build-reviews-v1.py` with its recorded hash.
