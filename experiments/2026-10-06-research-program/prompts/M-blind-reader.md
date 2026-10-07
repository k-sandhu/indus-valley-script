# Blind source reading for the repaired 1979 digitization

You are one independent reader in a blind evaluation of a transcription pipeline for Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979), University of Helsinki, CC BY 4.0. The repository is `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. The sample folder is `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/blind/`.

Read `CONVENTIONS.md` in that folder first and follow it exactly; it defines what to record and the JSON format. The selection of rows and pages is in `selection.json` in the same folder (fields `rows`, `count_pages`, `random_count_pages`, `stress_pages`). For each row it names `source_crop` (wider context) and `exact_crop` (the proposed box). Position-chart cards are in `position-chart/`, the source pages for counting are in `page-count-source/`, and the sign chart is printed on PDF pages 20–21 of `research/corpus/primary/koskenniemi_parpola1979.pdf`. You may render wider areas of the original PDF pages with Python and PyMuPDF (`import fitz`) at two pixels per point; write any renders only under `data/raw/2026-10-07-helsinki1979-digitization/reader-tmp-{READER}{PART}/` and delete them when you finish. You can view PNG images with the Read tool.

## Blindness rules

Do not open, list the contents of, or search inside: `predictions.json`, `frame.json`, `prediction-freeze.json`, `count-page-detections.json`, any file under `experiments/2026-10-07-helsinki1979-digitization/` outside `repair/2026-10-07-v2/blind/` (except the original PDF and the chart pages), any other reader's folder (`reader-a/`, `reader-b/`), the earlier evaluation references, or the PDF's text/OCR layer. Read only the original page images, the supplied crops and cards, and the chart. If you accidentally see a prediction, say so in your notes.

## Your assignment

You are reader **{READER}**, part **{PART}**: {SCOPE}

Write your output to `experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/blind/reader-{READER_LOWER}/{OUTFILE}` and nothing else (besides temporary renders). Use the JSON format in `CONVENTIONS.md`, include every assigned index or page, record uncertainty and candidate sets honestly, and add a top-level `reader`, `part`, `started_utc`, `finished_utc` and `notes` field. Work carefully: a wrong confident code is worse than a candidate set with a stated reason.

Finish with a short reply: how many rows or pages you read, how many you could not resolve, any convention you found hard to apply, and whether you saw anything you should not have.
