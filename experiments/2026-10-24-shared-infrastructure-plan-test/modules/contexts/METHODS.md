# Reading and reproducing the context audit

Start with `RESEARCH.md`, then use an assessment ID in `context-joins.json` to follow its deposit, feature, phase, source locator, spatial bound and rejected date candidates. `date-evidence.json` preserves source-specific determinations and calibration conventions. `eligibility-summary.json` states what is assembled for C0018/C0019. `dholavira225-summary.json` and `lothal-denominators.json` report separate source-row denominators.

`sources.json` pins 20 held witness records with 19 distinct file hashes. Two names refer to the same Dholavira PDF. One Kanmer witness is an HTML landing page and is excluded from article facts; `source-access.json` records that failure and the unheld Chapter 8 lead. A held witness is not a claim that every page was read. The exact chapters, passages, tables and figures supporting this audit are identified in the assessments and dates.

`visual-assets.json` lists 17 original-publication witnesses with D: paths, hashes, captions, source titles, URLs and printed/PDF locators. These are tables, figure panels and two bounded prose witnesses that audit an actual disagreement or dating claim. `plan-anchors.json` gives defensible room, courtyard, trench or passage bounds and the missing north/coordinate information. It supplies no exact registered-object point. `local-assets.json` inventories source text, failed extractions, detailed row derivatives, renders and review sheets under the D: raw directory.

Run these scripts in order from the repository root with Python 3.13:

```text
python experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/prepare_sources.py
python experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/build_records.py
python experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/build_dates.py
python experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/render_witnesses.py
python experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/polish_prose.py
python experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/finish_module.py
```

The environment needs PyMuPDF and Pillow. The source pinning step uses the previous comparison's source manifest and verifies the physical D: junction and frozen protocol hash before extraction. Original witnesses remain where acquired; all new full source text and detailed catalogue derivatives go to the new D: package. No new download or rights permission is implied by extraction.

The Dholavira gates are literal source-label predicates. Whitespace-only normalization recognizes III A as IIIA; mixed or questioned stages remain outside the unqualified gate. A usable grid/stratum/depth/area label excludes empty cells, dashes, question marks, Unst and Nil. The raw labels survive unchanged, and a separate count retains literal nonplaceholder Nil cells so that earlier coverage counts remain interpretable. Room, pit, reservoir and secondary/disturbed flags can overlap. A catalogue cell cannot establish an operational surface, an independent construction date or physical-object identity by itself.

The date audit does not recalibrate or pool source chronologies. The 78 records contain 76 determinations/TL results and two later rice-age paragraphs without raw BP values. Harappa laboratory pairs A-7523/QL-4733 and A-7529/QL-4730 repeat the same respective physical samples; two editions of a Kanmer table repeat lab IDs. These records must not become independent observations merely because laboratories, papers or calculations differ. Lothal's parenthesized ages use an alternate half-life convention rather than a calibrated interval.

`context-freeze.json` records the pre-join endpoint. Its combined SHA-256 is `e574bfea349db809810cdb8b7fb06f832af41549f79f0b2de5e271fca7faddec`. The frozen protocol SHA-256 is `11c69454d6e50304b5704db0865f76abca8d84363a67a21d42e8573e256cdb6e`. We had not received or read the new architectural outcomes when these context files were frozen. The finishing script refuses a changed frozen core; an archaeological correction needs a dated amendment or a new version preserving this endpoint. Prose, inventories and executable checks are outside the core freeze. Computational validation checks provenance and internal consistency; an independent reader must still adjudicate the source interpretation and recount the Lothal table.
