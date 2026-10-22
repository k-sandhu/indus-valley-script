# Codex run 2D: extract post-catalogue inscribed objects for Dholavira

## Your part

Part letter `D`. Owned paths: `experiments/2026-10-21-post-catalogue-finds/extraction/D/` and `data/raw/2026-10-21-post-catalogue-finds/run2D/`. Output files are named with `D` in place of `<part>`.

One site: `DHV`, Dholavira (alias Kotada), Gujarat, baseline CISI 1, 1987. CISI 1 catalogued two Dholavira seals found before the 1989 campaign (Dlv-1 and Dlv-2); the matching run checks containment. The local corpus holds 230 Dholavira objects, few with registrations, so the registration, findspot, stage and plate fields matter most here.

Sources. The primary source is `bisht-2015-held`, a 938-page PDF with a text layer at `data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf`. It was uploaded to the Internet Archive as a preliminary January 2015 Dholavira report, and the project uses it as the witness for Bisht 2015, *Excavations at Dholavira (1989–90 to 2004–05)*; its identity with the ASI publication is unconfirmed, so cite it by its source id and PDF page and record the printed page where the text shows it. Its inscribed-object chapters lie around printed pages 228–333 (seals, sealings, tablets and other inscribed material). Find the exact range from its contents pages and read the whole range, including catalogue tables and plate lists. Its overview and detailed chapters give different totals for some classes (60 and 61 sealings); record every printed total as a count statement with its page.

Then read the Dholavira entries in the IAR volumes for 1989–90 to 2005–06 (run 1A page text under `data/raw/2026-10-21-post-catalogue-finds/run1a/text/`, and the run 1B downloads `iar-2001-02`, `iar-2002-03`, `iar-2004-05` and `iar-2005-06` under `data/raw/2026-10-21-post-catalogue-finds/run1b/sources/<id>/`, whose page text you extract into `data/raw/2026-10-21-post-catalogue-finds/run2D/text/<id>/`), and the Dholavira pages of *Puratattva* and *Man and Environment* marked in `acquisition/candidate-pages-1a.csv`. These give seasons and registrations that the report may omit, and they become `other_publications` for objects the report lists.

The museum harvest of 13 October recorded three Dholavira registrations held by the National Museum, New Delhi, that the local corpus lacks: DHR-22198, DHR-6032 and DHR-7860 (`experiments/2026-10-13-museum-open-access/joins/join-table.csv`). Look for them in the report and, if found, note their row ids in your site notes.

The report's seal chapter describes each seal's device and inscription. Copy only the identity fields and skip every description. If the report numbers seals in a catalogue sequence, keep that number in `other_numbers` and the registration (DHR or similar) in `registration`.
