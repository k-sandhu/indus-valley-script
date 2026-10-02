# Source-recovery retrospective

The registry and completed regional retrospective defined the starting point. The previous census had a close limestone-duck group and three small cross-marked groups, but lacked independent creation dates and clear mark photographs. This run sought the original catalogues and exact inventory records.

| Approach | Observable result | Change to the research packet |
| --- | --- | --- |
| Search exact Louvre inventories | Found SB 17774 / AS 5724; other inventory searches returned unrelated namespace matches | Retained the SB prefix and checked aliases before accepting joins |
| Use the museum's public search form | Search endpoint returned HTTP 429 | Bounded batch logged; further form requests stopped |
| Recover the BnF Soutzo notice through its author index | Located cb31390239g and Gallica bpt6k62574241 | Original title and 50-page pagination established |
| Open the Gallica witness | HTTP 403 and web fetch failure | Used a different public library scan linked by a Louvre bibliographic record |
| Acquire University of Toronto MDP XII scan | Original pp. 9, 11, 13, 41, 42 and 49 recovered | Mass, mark and locator disagreements became visible |
| Inspect the original render | Confirmed 345 g and four marks on p. 9; 2769 g and 2469 g on p. 13 | OCR numbers checked against printed typography |
| Request independent review | Root visually checked pp. 9 and 13 with the source and proposed discrepancies visible | Recorded as source-informed visual review, rather than a blind transcription exercise |
| Acquire the museum photographs | Public image URLs succeeded through ordinary HTTPS | SB 13677's four depressions resolved; SB 17774 supplied a single view |
| Follow the Met catalogue reference | Publisher PDF acquired; text extraction returned no page text | Exact pp. 401–402 were rendered and read visually |
| Compare context dates | Met entry places SB 17774 deposition in the twelfth century BCE | Creation and deposition separated; foundation/funerary wording retained |
| Inspect modern duck plates | No countable five- or six-stroke group in acquired views | Marked-face photography remains the decisive acquisition |
| Recover Ascalone 2023 | Title-based institutional browse found handle 11587/480232; author-upload page also located | Institution file requires login; author preview unavailable; no full-text claim |

The first acquisition helper accepted any successful HTTP response. Ascalone's institutional file returned a 200 login page, saved with a PDF suffix. The original response and its manifest entry remain preserved. Format verification rejects it as a chapter witness, and the helper now checks PDF magic before accepting future PDF downloads. This defect affected acquisition status only; no analysis used the response.

The museum search batch made nine requests after the same 429 response appeared. This was unnecessary. A later acquisition should stop a same-endpoint batch on the first repeated access failure and continue through independently available sources. Google returned other Louvre inventories carrying the same bare number, which made namespace and alias checks essential.

The original duck descriptions supplied a stronger reason to pause unit fitting than another numerical tolerance calculation. Modern count fields and historical value-mark terminology now require a physical face check. Historical measurements also vary in both directions; a universal loss correction would hide the +298 g discrepancy. The earlier frozen fit remains intact, with this later source audit explaining its changed interpretation.

AS 13855 emerged directly from the same original page as AS 2615. Its four strokes and 335 g mass make it a specific archival target for comparing graphic conventions. Its modern identity remains to recover. The Dholavira context join was deferred after these source discrepancies took priority.

All new work stayed inside the assigned Susa experiment and raw directories. The previous regional outputs were hash-checked without edits. Source downloads, renders and full extracted text remain local-only. Our observations, arithmetic, source metadata, acquisition failures and checks form the reusable record.
