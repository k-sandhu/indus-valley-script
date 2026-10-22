# Codex run 2N: extract post-catalogue inscribed objects for north India and Rajasthan

## Your part

Part letter `N`. Owned paths: `experiments/2026-10-21-post-catalogue-finds/extraction/N/` and `data/raw/2026-10-21-post-catalogue-finds/run2N/`. Output files are named with `N` in place of `<part>` (`objects-N.csv`, `site-notes-N.csv` and so on).

Sites (code, project label, aliases, baseline):

| Code | Site | Aliases | Baseline |
|---|---|---|---|
| RGR | Rakhigarhi | Rakhi Garhi, Rakhi Shahpur, Rakhi Khas | CISI 1, 1987 |
| FRM | Farmana | Farmana Khas | CISI 1, 1987 |
| BHR | Bhirrana | Bhirdana | CISI 1, 1987 |
| SNL | Sanauli | Sinauli | CISI 1, 1987 |
| RPR | Rupar | Ropar | CISI 1, 1987 |
| KRP | Karanpura | | CISI 1, 1987 |
| BJR | Binjor | 4MSR, Binjor 1 | CISI 1, 1987 |
| BRR | Baror | | CISI 1, 1987 |
| TKD | Tarkhanewala Dera | Tarkhanewala-dera, Chak 86 | CISI 1, 1987 |
| BNW | Banawali | | CISI 1, 1987 |
| KNL | Kunal | | CISI 1, 1987 |
| KLB | Kalibangan | | CISI 3.2, 2019 |
| BLT | Balathal | | CISI 3.2, 2019 |
| MSD | Masudpur | | CISI 1, 1987 |
| MTL | Mitathal | | CISI 1, 1987 |
| HUL | Hulas | | CISI 1, 1987 |
| DHL | Dhalewan | | CISI 1, 1987 |
| ALG | Alamgirpur | | CISI 1, 1987 |
| CHG | Chandigarh | | CISI 1, 1987 |
| LHR | Lohari Ragho | | CISI 1, 1987 |
| new | any other north Indian or Rajasthan site whose IAR or journal entry reports an Indus inscribed object, for example the leads Brass (District Patiala or Fatehgarh Sahib) and Donder Khera (District Dhaulpur) in `acquisition/new-site-leads-1a.csv` | | CISI 1, 1987 |

For a new site, assign a three-letter code not used in `selection/sites-seed.csv` and record why you included it.

Sources. Use `acquisition/candidate-pages-1a.csv` (rows for your site codes, and `GENERIC` rows that fall in IAR entries under north Indian and Rajasthan headings) with the page text under `data/raw/2026-10-21-post-catalogue-finds/run1a/text/`. Read at least these in full where they cover your sites: `rakhigarhi-nath` (Nath, *Excavations at Rakhigarhi, 1997–2000*), `rakhigarhi-inventory-held` (check whether it is the same work and record the answer), `farmana-2006-08` (the 2011 final report), `farmana-2007-08-report`, `farmana-necropolis`, `tarkhanewala-2009`, `binjor2017-held`, `puratattva-35-held` and `puratattva-36-held`.

Run 1B downloaded these sources into `data/raw/2026-10-21-post-catalogue-finds/run1b/sources/<id>/`, without page text: `frm-uesugi-jamison-2020`, `frm-uesugi-jamison-2024`, `bhr-uesugi-2016`, `bhr-rao-2008`, `bjr-manjul-2017`, `krp-preliminary-report`, `knl-konasukawa-2020`, `msd-petrie-2009`, `new-dhalewan-report`, `new-hulas-report`, `snl-prabhakar-2013` and the IAR volumes `iar-2001-02`, `iar-2002-03`, `iar-2004-05`, `iar-2005-06`, `iar-2008-09` and `iar-2011-12`. Extract their page text into `data/raw/2026-10-21-post-catalogue-finds/run2N/text/<id>/p<NNNN>.txt` (PDF text layer, Tesseract for image-only pages) and locate your sites in them with the same keyword rule; `acquisition-web/candidate-publication-locators-1b.json` lists 1B's own page hits. Bibliographic records for 1B sources are in `acquisition-web/source-candidates-1b.csv`.

Seal studies such as `frm-uesugi-jamison-2020` and `bhr-uesugi-2016` list seals individually and are object-level sources for registrations, findspots and plates; read them for those fields only and skip their stylistic descriptions. The 2011 Farmana report and Nath's Rakhigarhi report are the expected primary publications for their seasons, and the IAR entries for the same seasons become `other_publications`.
