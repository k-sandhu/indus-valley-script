# Data update for maintainers

This package adds sources, per-object fields and coverage that belong in [knowledge/DATA.md](../../knowledge/DATA.md) and [data/MANIFEST.json](../../data/MANIFEST.json). We changed neither file; the records below are for the maintainer who merges the package.

## New sources

[manifest-proposals.json](manifest-proposals.json) holds 156 proposed manifest entries, one per acquired file (1.70 GB in all), each with URL, file name, byte count, SHA256 and, for Internet Archive files, the archive's MD5 and SHA1. All are `rights-unverified` and local-only under `data/raw/2026-10-21-post-catalogue-finds/`. They fall into these groups:

| Group | Sources | Route | Notes |
|---|---|---|---|
| Excavation reports | Shinde, Osada and Kumar 2011, *Excavations at Farmana* (854 pp.); the Farmana 2007–08 report; Nath, *Excavations at Rakhigarhi, 1997–2000* (draft); Joshi 1990, MASI 87 (Surkotada); Kanmer 2012, chapter 6; Trivedi 2009, *Excavations at Tarkhanewala-Dera and Chak 86*; Bala and Kant 2018 (Dhalewan); Dikshit 2020 (Hulas) | Internet Archive; ASI publication index | Farmana necropolis volume held as unusable OCR only |
| *Indian Archaeology – A Review* | 1992–93 to 2000–01, 2006–07, 2010–11 and 2012–13 from the ASI Aurangabad Circle mirror; 1997–98 and 1996–97 from the Internet Archive; 2001–02, 2002–03, 2003–04, 2004–05, 2005–06, 2008–09 and 2011–12 from the ASI publication index | Mirror, Internet Archive, `asi.nic.in` | With the census's held copies, every volume from 1987–88 to 2013–14 is now held; none after 2013–14 was found online |
| Journal issues (OCR text) | *Puratattva* 18–37; *Man and Environment* 10–11, 13–14, 16, 17, 22–23, 24, 26, 27, 28, 31, 32, 33, 35, 36 | Internet Archive (Digital Library of India uploads) | Text and per-page OCR only; no PDFs fetched |
| Articles and notices | Seal studies of Farmana (Uesugi and Jamison 2020, 2024), Bhirrana (Uesugi et al. 2016) and Bagasra (Jamison et al. 2017); Biagi 2022 (Lakhan-jo-daro); Parpola and Gulzar 2016 (Ganweriwala); Parpola 2019 (inscribed rods); Didier 2017 (Chanhu-daro); Shikarpur 2007–08 and 2008–09 reports; Khirsara articles of 2014; and others in `acquisition-web/source-candidates-1b.csv` | Open publisher and institutional copies | Several downloads are covers or contents pages only, recorded as such |

The combined source register, including leads that could not be downloaded, is [matching/source-register.csv](matching/source-register.csv) (258 source ids).

## Corrections to existing manifest entries

- `farmana-2006-08`, `rakhigarhi-nath` and `surkotada-1990` are now held; their proposals give paths and hashes. The Internet Archive Rakhigarhi file is a draft dated 31 December 2014 without a seal catalogue, and the ASI download offered for the published edition (`ePublicationReportsDetails/download/12`) returns a two-page cover.
- `kanmer-final-report`: chapter 6 is now held as well as the chapter 8 capture.
- `bisht-2015`: the ASI routes to *Excavations at Dholavira (1989–2005)* return only a two-page cover (run 1B), so the 938-page preliminary upload remains the only witness.
- The census copy `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/rakhigarhi_inventory.pdf` is the 1998 *Inventory of Monuments and Sites*, Chandigarh Circle, not an excavation report (question [Q-1029](../../knowledge/questions/Q-1029-local-literature-index.md)).
- The ASI Aurangabad Circle mirror's `1996-1997.pdf` contains IAR 1997–98, and its `1997-1998.pdf` is a byte-identical copy.

## New per-object fields and coverage

[objects.csv](objects.csv) gives 503 inscribed objects a publication locator (source, printed and PDF page, plate or figure), with the registration, season, findspot, depth or layer and period as printed. Joined to the local corpus by registration, cited plate or a find context that picks out one object, 92 local objects gain their first publication reference; 59 of them gain a registration, 43 a depth with stratum, 3 a period and 1 a findspot (75 of the 92 are at Dholavira, which DATA.md section 2 lists as the worst-described major site). These values come from rights-unverified reports; the identifiers and locators are facts we can track, and the full table is tracked in this package.

Suggested text for DATA.md section 3, replacing the closing sentence of "Studies with object-level data, and recent material": "The objects published after the CISI site ranges closed are listed object by object in the [post-catalogue finds package](../experiments/2026-10-21-post-catalogue-finds/README.md): 301 post-catalogue objects with a stated inscription at 21 sites, of which 10 match a local object by registration or cited plate and between 55 and 291 are absent from the local corpus (77 and 55–224 when joins on find context are accepted), most of the uncertainty lying in Dholavira rows that the corpus records without registrations." In the excavation-reports table, the rows for Farmana, Rakhigarhi, Surkotada and Kanmer chapter 6 become held, and section 5's rank 16 (Q-1026) is done.

## Leads for other cards

- *Excavations at Kalibangan: The Harappans (1960–69), Part I*, the volume with the Kalibangan inscription catalogue, is offered by the ASI excavation-report index as `ePublicationReportsDetails/download/60` (Part II is `download/61`). It predates CISI 3.2 and so lies outside this list, but it is the source card [Q-1016](../../knowledge/questions/Q-1016-kalibangan-catalogue.md) asks for.
- The same index (`https://asi.nic.in/pages/Publications/excavationReports`) offers MASI 78, Rao's *Lothal*, Part 1 and volume 2 ([Q-1015](../../knowledge/questions/Q-1015-lothal-rao-1985-tables.md)), Daimabad 1976–79, and Part II of the Tarkhanewala Dera report (`download/32`).
- For Dholavira ([Q-1014](../../knowledge/questions/Q-1014-dholavira-inventory.md)): 3 report rows join a local object by registration and 59 by a one-to-one grid square, and 13 more by registration among seals the report's table leaves without an inscription statement. The 145 unregistered local Dholavira objects are the remaining gap.
- Unread sources worth acquiring for this list: Mughal 1997, *Ancient Cholistan*; the Kuntasi monograph (1996); Nath and Kumaran 2012, "Inscribed Material from Khirsara"; *Puratattva* 42 and 43 (Khirsara, Kotada Bhadli, Karanpura); the Lakhan-jo-daro excavation reports; the 2021 Chanhu-daro preliminary report and the correct file of Desset 2022.
