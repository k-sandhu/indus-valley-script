# Primary photographic audit

This folder records an AI visual audit of 25 preselected Mayig faces against the primary photographs in Joshi and Parpola (eds.), *Corpus of Indus Seals and Inscriptions*, vol. 1, 1987. The [scan supplied by IGNCA](https://ignca.gov.in/Asi_data/76884.pdf) is acquired by the literature workstream, with SHA256 `47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d`. No explicit open license was found; these local crops are research excerpts and should not be packaged as a publicly redistributable image corpus.

The seed `20261001` selects 25 from 98 Mayig faces with default damage=0, uncertainty=0 and line_count=1. Selection precedes plate observation. This initial frame proved imperfect: it includes P000 lost-material annotations. It is preserved unchanged as an audit trail. Of the 25, 24 are complete single-line texts according to Lipi and one (M-141A) is a negative control. They all come from the Mohenjo-daro unicorn-seal subset. This is not a representative sample of the full Indus corpus.

The audit is qualitative, covers broad shape inventory, order and selected discrepancies, and is **not expert palaeographic verification**. The first descriptive pass deliberately preceded opening the selected sign sequences, but it made several grouping/count mistakes; these are preserved and acknowledged. Later catalogue-informed notes cannot be treated as blind validation.

The primary images establish that the normalized code direction is visual left-to-right on impressions, with ordinary reading proceeding from the right. Original seals are mirrored. All 25 physical IDs were located. Seventeen of the 24 source-complete objects are token-for-token compatible between Mayig candidate Wells arrays and Lipi. The other seven expose damage, segmentation, allograph or crosswalk differences. This is a compatibility count, **not a 17/24 transcription-accuracy estimate**.

Files:

- `selection.json`: pre-observation frame, seed, IDs and original face records; source hash records the pre-P000-flag normalization.
- `blind_visual_notes.json`: first-pass shape descriptions in impression visual order.
- `comparisons.json`: independent Mayig codes/candidate arrays versus Lipi observational sequences, joined by physical CISI base.
- `adjudications.json`: cautious post-comparison notes; no raw transcription is altered.
- `crop_manifest.json`: source citation, PDF and printed page locators, crop coordinates and image hashes.
- `M-*_impression.png`: context crops retaining the photographed impression and its printed label. Enlarging a scan creates no new glyph detail.
- `page_headers.json`: OCR locator for PDF pages37–124; header OCR is not a glyph transcription.

The material checks that change downstream analysis are:

| Object | Primary observation | Consequence |
|---|---|---|
| M-141A | Two visual rows, loss, and Mayig P000 despite zero default flags | Filter P000 explicitly; line features alone do not establish layout or completeness |
| M-73A | Broken edge and Mayig P000; Lipi marks complete | Treat completeness as a curatorial judgment, not a certainty |
| M-81A | Two adjacent grids; Lipi encodes compoundW617, Mayig twoP268/W615 | Code length is catalogue-dependent; do not label this a copying error |
| M-140A | Two short upper-band strokes; Mayig calls them full-heightW032, LipiW002 | Candidate height discrepancy; raw codes preserved |
| M-150A | Elongated inner element; Mayig dot class versus Lipi inner-strokeW832 | Fine decoration unresolved; raw codes preserved |
| M-181A | Decorated triangle; MayigP207 supports decoration feature but onlyW490 in its crosswalk | Crosswalk omission can create apparent incompatibility |
| M-152A | Dense short strokes decorate a compoundU/W772 | Do not count every short stroke as a separate numeral token |

There is no semantic or phonetic decipherment in this audit. The reusable advance is a documented primary-image quality check and a set of conservative normalization constraints.
