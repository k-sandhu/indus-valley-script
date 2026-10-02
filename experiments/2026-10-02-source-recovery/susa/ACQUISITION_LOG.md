# Acquisition log

The chronological request record is [source-acquisition.json](source-acquisition.json). [source-validation.json](source-validation.json) supplies the format-checked outcomes. Raw files remain under `data/raw/2026-10-02-source-recovery/susa/`.

| Source | Access route | Result and rights handling |
| --- | --- | --- |
| Louvre SB 17774 JSON | Official cl010188675 JSON URL | Acquired; museum record includes inventory, creation date and discovery context; rights unverified |
| Louvre SB 13677 photograph | Public image URL in the previously saved official JSON | Acquired, 1500 × 1197 pixels; © 2011 Musée du Louvre / Département des Antiquités orientales |
| Louvre SB 17774 photograph | Public original image URL in the new official JSON | Acquired, 558 × 480 pixels; © 2002 GrandPalaisRmn (musée du Louvre) / Gérard Blot |
| Soutzo BnF record | Author index to cb31390239g | Acquired metadata HTML; Gallica file access failed |
| MDP XII, 1911 | Louvre bibliography links public Internet Archive / University of Toronto scan | Acquired, 268 PDF pages, 18,313,226 bytes; archive metadata records NOT_IN_COPYRIGHT in the US; raw witness kept local |
| Art of the First Cities, 2003 | Public Met publisher download link | Acquired, 566 PDF pages, 190,086,236 bytes; explicit reproduction scope unverified; raw witness kept local |
| Ascalone 2023 institutional record | Title-based browse to 11587/480232 | Acquired metadata; publisher copyright shown; full PDF route redirects to login |
| Ascalone author upload | Public author papers page to Academia upload 107255746 | Located in web tool; ordinary request returned 403; preview unavailable; generated FAQ excluded |

The full 1911 volume and Met catalogue remain local-only. `raw-derivatives.json` records extracted text, inspected page renders, parent hashes and transformation details. Soutzo text extraction produced readable text. The Met PDF supplied images without a text layer; its failed extraction remains recorded and its selected pages were read from rendered images.

The file `ascalone2023.pdf` is a preserved HTML login response from the initial helper defect. Its 200 HTTP status does not establish acquisition of the chapter. Format verification records its rejection. No restricted content was accessed and no copy-request message was sent.

The prior SB 13677 museum JSON and Ascalone 2022 PDF are dependencies in the completed regional run. They were referenced without replacement. New renders from the old PDF have their own transformation manifest.
