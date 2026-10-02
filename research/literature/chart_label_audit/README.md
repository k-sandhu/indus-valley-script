# Independent 1979 chart numeric-label audit

Thirty sampled cells were read visually from the original scanned PDF and crops rendered directly from that PDF. No project numeric OCR, sign templates, matches, or expected label tables were inspected. This validates printed labels only; it does not validate glyph transcription or any semantic/phonetic correspondence.

Input: `research/corpus/primary/koskenniemi_parpola1979.pdf`, SHA-256 `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`,180 PDF pages. The audited PDF pages20/21 bear printed page numbers19/20. Both have35 row levels, with10 columns. PDF21 column9 has occupied rows0–21, followed by blanks; its row20 has rank400 but no evident lower code. That occupied cell remained eligible but was not drawn in this sample.

Sampling uses one Python `random.Random(20261002)` generator sequentially for page20 then21. Eligible cells are enumerated column-major then row-major. PDF20 column0 is excluded because another agent already audited it. PDF21 includes all occupied cells. Fifteen cells are sampled without replacement on each page, then sorted for presentation. Full selection, geometry and source hashes are in `sampling_manifest.json`; rerun `select_and_render.py` to reproduce selection and original-PDF crops.

`manual_numeric_labels.csv` and `.json` are the independent readings. All30 upper ranks are clear. Twenty-eight lower codes are clear; PDF21 column4,row6 has best reading435 with436 possible, and PDF21 column9,row9 has best reading406 with405 possible. Both are explicitly medium confidence. Agreement should be reported separately for the28 clear cells and the two ambiguous cells, retaining alternatives; do not choose among alternatives solely to agree with a tested extraction.

`save_manual_labels.py` serializes the manually entered readings; it performs no recognition. Contact sheets and individual high-resolution crops provide the original-image evidence behind each result. No glyph identities were transcribed or adjudicated in this audit.
