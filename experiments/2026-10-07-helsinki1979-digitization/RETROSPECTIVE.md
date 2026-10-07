# Retrospective: Helsinki 1979 digitization

The first pipeline failed its frozen test of **60 numbered-section rows from PDF 31–79 (3,460/11,369 detected occurrences; no sorted target)**: 33 matching counts, 23 exact numbers and 24 top-five compatible whole rows. The full first run preserved 11,369 provisional occurrences across 159 pages. Its source witnesses, predictions, references and numerical endpoints remain unchanged. Original prose is retained in `follow-up/2026-10-07/*.before-follow-up.txt`.

## First run and review evidence

The first run replaced fixed vertical pitch with observed number bands and glyph whitespace, reused the 687-cell chart and known page-30 reference, and combined sparse chamfer distances with chart-only CNN augmentation. A dense development matcher was interrupted for speed; a sparse implementation was frozen before source reading. The final development counts were 17/20 with 6/20 and 12/20 top-one/five whole rows. Static horizontal regions and a density-based orientation score remained.

Three readers supplied disjoint primary groups; original OCR strings accidentally remained in 22 locators. Those strings were removed from a separate copy, exposure was disclosed and the initial references retained. Six fixed convenience repeats, two per primary group, exposed glyph and crop disagreements; no random selection rule was recorded.

The Sonnet review confirmed 43 headline numbers and independently matched 30 source rows for count, number and classification. It found all 17 rotated pages upright, 1,223 inverted strips, asymmetric field drift and missing/fragmented crops. A/B accepted 7/40 crops; C accepted 16/20, including nine with objective defects under a 1-point tolerance. The objective audits pass 14/60 and 21/60 with that tolerance in the same original numbered-section frame. These results are appended as corrections, not substituted into the frozen evaluation.

## Coordinator corrections, 7 October 2026

Copied the frozen prediction bytes into an owned portable input root, retained digits/crops/chart sheets, listed tracking exceptions and added a retrospective evaluator-hash supplement. Two portable replays match the original metrics SHA256 exactly. Replaced the active universal queue with 9,584 triaged rows, retaining 1,785 outside triage and all 11,369 in quarantine. The separate orientation overlay flags all 1,223 inverted occurrences. The row-recall record lists 20 short pages, page 62 column 0's 21 detections against 36 printed rows and the compact multi-column pages 129–130.

The review's eleven code corrections are a dated overlay. Codes 2/25 need vertical position; narrow/wide hatching and underlines need separate labels. Original references were not edited. Calibration excluding three inverted selected rows uses 126 positions and yields Brier 0.1262 and ten-bin error 0.1183, with row-bootstrap intervals, without refitting or applying adjudications. These are Exploratory sensitivities of the original numbered-section frame.

## Repair attempts and preserved problems

The layout repair measures field coordinates from OCR boxes and print components, keeps pages upright from header content, and detects observed row bands without fixed counts. The first compact-column attempt discarded columns where no field/glyph gap was visible; retaining those columns with a flagged page-level gap estimate produced eight columns/288 rows on page 129 and six/201 on 130. An OCR batch exceeding Tesseract's image-height limit failed; batches of 96 rows fixed it. Development page 30 has 17/20 matching counts, 19/20 numbers, 6/20 top-one and 12/20 top-five whole rows. These are development observations.

The v1 candidate was frozen and sampled, then its unlabelled frame exposed glyph-like OCR strings as extra columns on ordinary pages. No reader received it. Its full artifacts remain under `repair/2026-10-07-v1/`, marked Superseded. The v2 replacement restricts ordinary margin clusters to a 35-point neighbourhood while retaining native compact-column discovery. Its code and evaluator were frozen at 2026-10-07T16:54:51.431467+00:00; 80 predictions were frozen at 2026-10-07T16:58:06.116694+00:00. The seeded frame includes 28 numbered, 26 end-sorted and 26 beginning-sorted rows, excluding development pages and previous targets. It also retains 21 source-count pages. No fresh reference or new accuracy outcome exists.

A shell-quoting attempt to prepare v2 failed before creating files; a small Python construction helper replaced it. Shared Windows volume/process queries were denied. No dependency was installed in this follow-up, and no other package or repository history was changed. The revised L importer was exercised on 63 existing occurrences, including three provisional letter-suffixed strings: all schema checks passed and all remained quarantined without concordances.

## Disk stop and exact unfinished work

The first check found 896,548,864 bytes free, below the user's 1 GB cutoff. Free space subsequently recovered to about 2.65 GB and development resumed. During v2 sampling it fell to 917,327,872 and then 256,331,776 bytes. The helper had already serialized its 60,522,244-byte frame by the failed pre-frame check, and finished before interruption could take effect; CIM process inspection was denied. Space recovered after the helper exited. The cause of the fluctuations is unverified. A future gate must run inside the active process after library/model loading and immediately before each large serialization; checking outside that process was insufficient.

Further repair/evaluation work stopped at that trigger. The completed freeze, sample, predictions, positional chart cards and source-count pages are preserved. The following work remains:

1. Two independent readers must read all 80 rows and count/match all 21 source pages without predictions or OCR numbers.
2. A third source-only reader must adjudicate disagreements, preserving both initial readings and final source counts.
3. Run the frozen evaluator for row segmentation/counts, exact sequences, candidates, numbers, classification, row recall and calibration with intervals, beside the first endpoint and its different frame.
4. If every criterion passes, implement a fresh full transcription with an in-process disk gate and the frozen confidence release rule. If any stage fails, preserve quarantine and report the limiting stage.
5. A reviewed identity concordance and per-occurrence surface alignment are still required for actual Package L imports; the local 1980 lookup supplies no verified carrier join.

The coordinator must also apply the listed tracking exceptions before claiming clean-checkout recovery. Finish small documentation and integrity checks without starting another large write or deleting frozen evidence.
