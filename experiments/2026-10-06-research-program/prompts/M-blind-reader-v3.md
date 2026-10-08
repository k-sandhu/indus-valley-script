# Blind source reading for the v3 crop rebuild of the 1979 digitization

You are one independent reader in a blind evaluation of a transcription pipeline for Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979), University of Helsinki, CC BY 4.0. The repository is `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. The sample folder is `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-08-v3/blind/` (BLIND below).

Read `BLIND/CONVENTIONS.md` first and follow it exactly; it defines what to record and the JSON format, including the continuation-line rules, the complete-underline rule for crop judgments and the 597/598 spacing rule. The selection of rows and pages is in `BLIND/selection.json` (fields `rows`, `count_pages`, `random_count_pages`, `stress_pages`). For each row it names `source_crop` (wider context), `exact_crop` and a `printed_line_crops` list (the proposed boxes for the numbered line and any proposed unnumbered continuation lines). Position-chart cards are in `BLIND/position-chart/`, the source pages for counting are in `BLIND/page-count-source/`, and the sign chart is printed on PDF pages 20–21 of `research/corpus/primary/koskenniemi_parpola1979.pdf`. You may render wider areas of the original PDF pages with Python and PyMuPDF (`import fitz`) at two pixels per point; write renders and helper scripts only under `data/raw/2026-10-07-helsinki1979-digitization/reader-tmp-v3-{READER}{PART}/` (create it; never use any shared scratchpad) and delete that folder when you finish. You can view PNG images with the Read tool.

## Blindness rules

Do not open, list the contents of, or search inside: `predictions.json`, `frame.json`, `prediction-freeze.json`, `count-page-detections.json`, `full-summary.json`, any other file under `experiments/2026-10-07-helsinki1979-digitization/` outside BLIND (the original PDF and its chart pages are permitted), anything under `data/raw/` other than your own scratch folder, any other reader's folder (`BLIND/reader-a/`, `BLIND/reader-b/`), the earlier evaluation references in `repair/2026-10-07-v2/` or `evaluation/`, the row-verification pilot under `data/raw/2026-10-08-helsinki1979-row-verification/`, or the PDF's text/OCR layer. Read only the original page images, the supplied crops and cards, and the chart. If you accidentally see a prediction or another reading, say so in your notes.

## Your assignment

You are reader **{READER}**, part **{PART}**: {SCOPE}

Write your output to `BLIND/reader-{READER_LOWER}/{OUTFILE}` and nothing else (besides temporary files in your scratch folder). Use the JSON format in `CONVENTIONS.md`, include every assigned index or page, record uncertainty and candidate sets honestly, keep `crop_issues` for every rejected crop, and add top-level `reader`, `part`, `started_utc`, `finished_utc`, `files_opened` (a list of the paths you actually opened) and `notes` fields. Work carefully: a wrong confident code is worse than a candidate set with a stated reason.

Finish with a short reply: how many rows or pages you read, how many you could not resolve, any convention you found hard to apply, and whether you saw anything you should not have.
