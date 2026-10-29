# Site table notes

[sites-census.json](sites-census.json) holds one record for each of 115 site entities in the 2026-10-06 evidence census, built by [build_site_table.py](../build_site_table.py) from the four deep batches (A Pakistan and Afghanistan, B Gujarat, Kutch and Maharashtra, C North India, D finds abroad), the local Lipi site register and the synthesis alias joins. Every value is copied from a census row, and each record lists its source rows in `census_row_ref`. Status is Exploratory, as in the rows.

Coordinates come only from the rows. A point the row accepts is `census-verified`. A point the row itself describes as a village proxy, locality, area centroid, island or park extent, or shared report location is `census-partial`; Bakkar Buthi joins this group because its row calls the Fuls 2022 point a secondary corpus coordinate. Bet Dwarka's row gives only the published island extent, so its point is the centroid of that bounding box. Where the row holds only an unaccepted candidate, `lat`/`lon` stay null and the candidate is kept in `candidate_lat`/`candidate_lon` or `candidate_points` (Murda Sang, Rajanpur, and Binjor, whose printed DMS values have seconds above 60). Degree-minute strings in batches C and D were converted arithmetically; Farmana's printed seconds "021" were read as 21. The result is 72 verified, 13 partial, 3 candidate-only and 27 missing.

Fieldwork events are parsed from each row's campaign text. Simple year strings are split on semicolons, two-digit season ends are expanded (1987–88 becomes 1987–1988), and the kind is taken from words such as discovery, survey or trench. Gazetteer year lists ("1955,1957 as listed by 2010 gazetteer") become a start–end span. Seventy-eight campaign entries are curated by hand in `CAMPAIGN_OVERRIDES`, each with the row text quoted in a comment: all C and D paragraphs, and A/B entries where the text mixes director and year groups (Harappa's three year groups with two unpaired directors, Sutkagen-dor's three surveys, Rangpur, Rojdi), records internal discrepancies (Rangpur 1936/1937, Mundigak 1958/1959) or adds caveat clauses that a splitter would turn into events (Dholavira's seasons without work, Kanmer, Khirsara). Fifteen unresolved campaign entries are skipped and listed in `campaigns_unresolved`. `first_fieldwork_year` is the earliest start among discovery, survey, excavation and other events. Where only a report year is earlier or available (Tarkhanewala Dera 1953, Sarazm 1987, Ras al-Jinz 1988) it is used with `first_fieldwork_upper_bound: true`. D's Jarrige sequence for Sibri (1975–2002) covers several sites and is kept out of Sibri's first year. Seventeen entities have no dated event.

Counts are copied without reconciliation: local Lipi faces, families and object classes summed over the entity's literal labels (5,652 faces, matching the synthesis site frame; the 28 `Unknown` faces are not an entity), Mahadevan 1977 counts with their locators, CISI ranges, ICIT values (in batch B these are sign occurrences, not objects), D's published minimum, and all other numeric counts in the rows. `dating_notes` copies stratum and absolute-date statements that rows mark as available or partial; no dating was added.

Seven merges follow `register-joins.json`. Gharo Bhiro (A), Nuhato (A) and Nuhato (B) form one entity named Nuhato, which takes B's coordinate from the 2018 report. Miri Qalat, Murda Sang, Nindowari, Ornach area, Shortughai and Sibri each join an A row with a D row; all six keep A's coordinate. Merged records keep every row's events, counts and coordinate witnesses (`coord_alternatives`). All 88 site labels in the register matched a deep-batch entity, so there are no register-only records.

## Sites without coordinates

These 30 entities need gazetteer coordinates.

| Country | Sites (region) |
|---|---|
| Pakistan | Derawar Ther, Guddal A, Rappwala Ther, Wattoowala, Rajanpur* (Inter-Riverine); Hissam-dheri (Upper Indus); Murda Sang* (Iranian Plateau) |
| India | Chandigarh (Eastern Headwaters); Binjor (4MSR)* (North India) |
| Iraq | Ur, Kish, Nippur, Tell Asmar, Girsu/Tello, Umma, Babylon (Mesopotamia) |
| Iran | Tepe Yahya, Konar Sandal/Jiroft, Luristan (regional provenance label) (Iranian Plateau) |
| Bahrain | Saar, Karzakan, Hajar, Dilmun (regional label) (Persian Gulf) |
| United Arab Emirates | Tell Abraq, Kalba (Persian Gulf) |
| Oman | Ras al-Jinz, Salut, Bat (Persian Gulf) |
| Turkmenistan | Altyn Depe, Gonur Depe (Central Asia) |

An asterisk marks a census candidate point that the row did not accept. Luristan and Dilmun are provenance labels, so a single point would misstate them.
