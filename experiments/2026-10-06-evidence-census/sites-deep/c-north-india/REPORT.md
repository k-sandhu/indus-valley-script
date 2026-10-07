# North India census findings

The follow-up covers **25 sites**, with **223 executed queries** and an opened primary or substantial secondary source for each. Six sites have an identified final excavation monograph; nine have reported inscribed discoveries after the 1987 India catalogue baseline. Nine inspected CISI 1 sections contain **176 catalogue objects**. Local coverage totals **290 faces, 271 object families and 232 distinct CISI identifiers**. The bases are [aggregates.json](aggregates.json), `sites`, `followup_queries`, `final_excavation_monograph_count`, `post_1987_inscribed_find_count`, `cisi1_catalogue_objects` and `local_totals`.

## Scope and sources

The supplied list contains 23 sites. Tigrana was added from the Indian Inter-Riverine local coverage row, which contains one TAG-class face. IAR 1987-88 p. 21 documents its excavation; independent primary inscription confirmation remains unlocated. Rohira was added from Rhr1-2 in Joshi and Parpola's *Corpus of Indus Seals and Inscriptions. 1. Collections in India* (1987), p. 361; IAR 1982-83 pp. 65-66 and plate 39 supplies the excavation account. See those rows in [site-rows.json](site-rows.json), `primary_source_opened`, `reported_object_counts` and `open_problems`.

Additional regional queries investigated Mandi, Bargaon, Girawad, Balu and Nagar without establishing an eligible inscription securely attributable to another site. Snippets crossing site-paragraph boundaries were insufficient for inclusion. The selection record is [searches.json](searches.json), `adaptive-search-38-q1` through `q4`; it does not establish archaeological absence.

Every row has at least five distinct follow-up queries. Records give exact strings, dates, service, source IDs and response paths. Grouped results cannot be assigned to individual member queries. The 33 first-pass query records are retained separately and excluded from the follow-up count because their original responses were not saved. The 911 source records include unused and failed leads; `opened`, `access`, `inspected` and `witnesses` identify what was read. Twenty-two failed downloads remain in `searches.json.failed_downloads`; web-opening failures also remain in raw response records.

## Final publications and later discoveries

The six final-monograph sites are Kalibangan, Farmana, Mitathal, Hulas, Tarkhanewala Dera and Bhagwanpura. Relevant full volumes were obtained for Mitathal, Hulas and Bhagwanpura. Kalibangan Part II was inspected, but the inscription catalogue belongs to inaccessible Part I. Farmana's 2011 volume and Trivedi's 2009 *Excavations at Tarkhanewala-Dera and Chak 86 (2003–2004)*, MASI 99, were identified bibliographically; their full inventories were not obtained. Final-report identification therefore does not imply inventory access. Manda and Siswal have published short chapters, counted separately. Rakhigarhi and Sanghol 2014 submissions remain drafts. The basis is each row's `primary_and_final_publications` and `final_excavation_monograph_identified`, plus `aggregates.json.final_monograph_access`.

| Site with discovery after 1987 | Evidence location | Scope limitation |
|---|---|---|
| Rakhigarhi | IAR 1999-2000, pp. 31-33: seals, tablets, sealings and graffiti | Class totals unstated; later seasons unjoined |
| Farmana | 2008 preliminary report, pp. 100-105, figs. 106-109: two seals and two impression objects | One impression has lost its text area; final count unavailable |
| Bhirrana | Puratattva 35, pp. 64-65: four steatite seals, three with legends | Ministry snippet reports five seals and two inscribed copper celts; full count page inaccessible |
| Sanauli | Puratattva 36, plate 21: sherd captioned with a Harappan character | Lower bound from a caption; plate page unnumbered in accessible OCR |
| Ropar (Rupar) | Submitted IAR 2011-12, pp. 74-75, plate 30: three broken sherds with signs and graffiti on a chakla base | Possible overlap in wording; edition status unresolved |
| Karanpura | IAR 2013-14, pp. 116-123: two seals and 157 graffiti instances | 134 sherds, 22 whorls and one ring; not all marks establish texts |
| Binjor (4MSR) | Frontline, 22 July 2016, pp. 72-78: separate 2015 and 2016 seals | Director quotations and object photograph; final catalogue unavailable |
| Baror | Puratattva 35, p. 54: inscribed terracotta sealing | Preliminary account; later inventory unresolved |
| Tarkhanewala Dera | Puratattva 34, pp. 30-34: 2003-04 seal impression | Final 2009 inventory unavailable |

Exact titles, authors, dates and URLs are in [sources.json](sources.json), IDs `iar1999`, `farmana2008`, `puratattva35`, `sanauli2006`, `iar2011`, `iar2013`, `binjor2016` and `puratattva34`; each row also records eligibility and locations in `reported_object_counts` and `post_cisi_finds`. Rakhigarhi, Rupar and Tarkhanewala Dera were already catalogued in CISI 1. The other six use 1987 as a calendar baseline, with no inspected CISI 1 section. A later publication alone does not date the discovery after 1987.

## Published inventory against local coverage

| Site | CISI 1 pages | Catalogue objects | Local faces | Local families | Local distinct CISI IDs |
|---|---:|---:|---:|---:|---:|
| Kalibangan | 298–326 | 122 | 212 | 197 | 197 |
| Banawali | 344–349; modern impression p. 364 | 37 | 26 | 26 | 23 |
| Rakhigarhi | 359–360 | 3 | 13 | 12 | 3 |
| Alamgirpur | 350 | 3 | 3 | 3 | 3 |
| Hulas | 356 | 1 | 1 | 1 | 1 |
| Ropar (Rupar) | 361 | 1 | 5 | 3 | 1 |
| Chandigarh | 351 | 4 | 3 | 3 | 3 |
| Tarkhanewala Dera | 363 | 3 | 3 | 3 | 1 |
| Rohira | 361 | 2 | 0 | 0 | 0 |
| **Total on nine sites** | | **176** | **266** | **248** | **232** |

The table comes from `aggregates.json.comparisons` and `local_totals_on_cisi1_sites`. Its 176 entries comprise **91 seals, 16 sealings, 15 tablets, 52 pottery/graffiti objects and two metal objects**. No entries in these sections were assigned to the residual other class. Page ranges and class boundaries are in `site-rows.json.cisi_coverage` and `reported_object_counts`. Some objects are geometric, blank or indeterminate; 176 is a catalogue total. The inspected 1987 site runs are contiguous.

Banawali's 23 distinct local identifiers against B1-37 give 62.16% of the catalogue run. Chandigarh has 3/4 (75%); Tarkhanewala Dera 1/3 (33.33%); Rohira has no local site label against two catalogue objects. The other four comparable early runs have all catalogue IDs represented. These are identifier comparisons. Archaeological coverage requires registration-number joins and later-find inventories. Kalibangan's 197 local identifiers include numbering through K476, so comparison with K1-122 cannot yield a coverage percentage. CISI 3.2 pages and K123-476 continuity remain unverified. See `within_cisi1_run_count_comparable`, `identifier_fraction` and Kalibangan's `cisi_coverage.later_volume`.

Mahadevan's 1977 main-corpus table gives **118 selected objects across seven batch sites**, with **four more in its addendum**. Kalibangan contributes 99 main objects: 56 seals, 21 sealings, 20 pottery pieces and two bronze implements. The basis is *The Indus Script: Texts, Concordance and Tables*, printed p. 6 section 4, p. 7 section 6.2 and p. 24 section 16, in the opened 48-page excerpt. Appendix V, pp. 816-829, was absent; the ICIT preview exposed contents rather than site-count pages. These selected counts and CISI's later inventory remain separate. See `mahadevan_1977_or_icit_count` and source `m77`.

## Metadata and remaining gaps

For cited inscription samples, the most frequently unlocated fields are absolute dates (**20/25 sites**), drawings (**18/25**), findspot (**18/25**), registration numbers (**17/25**) and dimensions (**12/25**). Stratum/phase, material and photographs are each unlocated at seven sites. These are document-availability counts from `main_publication_metadata`, aggregated in `missing_metadata_fields`. They include sites without a secure inscription sample. A `no` means the field was not located for that sample, or explicitly absent. `partial` includes site-level dates, scales and incomplete contexts.

Numerical counts remain unresolved at 13 sites for seals, 17 for sealings, 22 for tablets, 16 for pottery/graffiti, 23 for metal and 24 for other objects (`aggregates.json.unresolved_counts_by_class`). Reported quantities retain unit, date, eligibility and page; missing classes are search-linked nulls. Kunal's geometric seals, historic Sanghol seals and Bhagwanpura's marked objects cannot be converted wholesale into Indus-text inventories.

Coordinates require selective review. Hulas has inconsistent printed coordinates in its introduction and Appendix III; an opened gazetteer supplies a village proxy. Manda's gazetteer locality is available only in a snippet, while its excavation volume and IAR contain incompatible latitudes. Binjor's paper uses malformed notation; an official register snippet lists two mound points without establishing which is 4MSR. Literal alternatives are retained. Kotla Nihang, Rohira and Lohari Ragho gazetteer points are locality proxies. Masudpur's component renumbering prevents a cluster point from locating every mound. Chandigarh's excavation-point coordinates remain unlocated. Each `coordinates` field links a source or failed searches.

Custody records are dated snapshots, usually CISI 1's 1987 table, pp. 374-375. Present holdings remain unresolved without newer object-specific evidence; generic museum descriptions and souvenirs were insufficient. Most publications and images have no verified open reuse terms and remain local. Gazetteer text/data terms are distinguished from image rights in `current_holding` and `digital_availability_and_reuse`.

## Reviewer checks

Repeat the commands in [README.md](README.md). Sample CISI 1 Kalibangan and Banawali class boundaries, Rohira p. 361 and custody pp. 374-375; Mahadevan pp. 6-7 and 24; Karanpura pp. 116-123; Farmana figs. 106-109; and Rupar's submitted IAR pp. 74-75 without importing the preceding Sisupalgarh sealings. Review coordinate conflicts before mapping. [validation.json](validation.json) checks record structure, encoding, arithmetic and archive preservation; source-page review remains necessary.
