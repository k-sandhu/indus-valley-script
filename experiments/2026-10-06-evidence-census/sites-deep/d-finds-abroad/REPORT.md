# Indus-related finds abroad: site census D

The 36-row census covers every requested site and local regional label. Published counts and local counts often describe different object classes. The local export contains **42 faces and 42 object-family labels across 26 rows**. Selected published specimen minima sum to **36 across 22 rows**, including Gulf signs or pseudo-signs and two provisional locality identifications. A complete inventory and an object-level join were not recovered for any row, so all coverage fractions remain undefined. The fields `published_counts`, `local_corpus.records` and `count_comparison` in [site-rows.json](site-rows.json) preserve these distinctions.

## Batch totals and scope

[aggregate-results.json](aggregate-results.json) records 23 named sites, one literature addition, five other local site rows, two regional provenance labels and five South Asian cross-references. Babylon was added through Steffen Terp Laursen's 2010 Table 1, which assigns Gadd no. 17 to Babylon using Collon 1994. Karzakan, Janabiyah, Hajar and Kalba were already present in the local export. Luristan denotes a provenance region; Dilmun is retained as an export label. Five Pakistani cross-references receive only the checks needed to resolve their local classification.

Fourteen rows have a bibliographically identified final excavation synthesis or specialist catalogue, including 12 named sites. Some identifications come through a bibliography or publisher record, without full-book inspection. Nine rows have sourced coordinates. Modern province assignments are provisional, even where a monument coordinate was recovered. The Failaka coordinate describes the island, and the Hili coordinate describes the archaeological park. Source locations and precision are recorded in `identity.coordinates`.

Four rows have later inscription-related reports: Umma, Salut, Shahr-i Sokhta and Tepe Hissar. Umma and Salut concern Indus-related material; the latter two concern other or disputed writing. **Zero** rows have both a dated discovery and a supported applicable CISI cutoff. This is the number of established matches in this census. Searches did not establish current publication of CISI 3.4, which the 2022 preface assigns to West Asia and the Gulf.

## Published specimens and local export

The table uses `aggregate-results.json.published_vs_local`. An empty-minimum marker means no selected Indus-related object minimum was established. It carries no archaeological absence claim. “Published” counts retain the inclusion limits described below; “local” counts are export faces, with one object-family label per face in this batch.

| Row | Published selected object minimum | Local faces |
|---|---:|---:|
| Ur | 6 | 5 |
| Kish | 2 | 2 |
| Nippur | 1 | 1 |
| Tell Asmar | unresolved | 0 |
| Girsu/Tello | 3 | 2 |
| Umma | 1 | 1 |
| Babylon | 1 | 0 |
| Susa | 2 | 2 |
| Tepe Yahya | 1 | 1 |
| Shahr-i Sokhta | unresolved | 0 |
| Konar Sandal/Jiroft | unresolved | 0 |
| Tepe Hissar | unresolved | 0 |
| Failaka | 2 | 2 |
| Qala'at al-Bahrain | 2 | 1 |
| Saar | 1 | 1 |
| Tell Abraq | unresolved | 0 |
| Hili | unresolved | 0 |
| Ras al-Jinz | 1 | 4 |
| Salut | 2 | 2 |
| Bat | unresolved | 0 |
| Umm an-Nar | unresolved | 0 |
| Altyn Depe | 1 | 1 |
| Gonur Depe | 1 | 1 |
| Sarazm | unresolved | 0 |
| Karzakan | 3 | 3 |
| Hajar | 1 | 1 |
| Luristan | 1 | 1 |
| Janabiyah | 1 | 1 |
| Kalba | unresolved | 1 |
| Dilmun | unresolved | 1 |
| Shortughai | 1 | 1 |
| Nindowari-damb | 1 | 2 |
| Miri Qalat | unresolved | 2 |
| Sibri | unresolved | 1 |
| Ornach area | 1 | 1 |
| Murda Sang | unresolved | 1 |

## Corrections supported by inspected sources

C. J. Gadd's *Seals of ancient Indian style found at Ur* (1932, *Proceedings of the British Academy* 18: 191–210) catalogues 18 numbered items, with 16 attributed to Ur. They include uninscribed objects and a cuneiform-only seal. Laursen's *The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC* (2010, *Arabian Archaeology and Epigraphy* 21: 96–134), Table 1 and Figs. 14–15, supplies the selected six round Ur specimens used here. The class-specific decisions are in the Ur row. [Gadd PDF](https://ignca.gov.in/Asi_data/33779.pdf), [Laursen PDF](https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf).

The local Dilmun identifier BM123208 is a British Museum accession for a seal found at Ur. Gadd no. 16 gives excavation number U.17649 and the 1931–1932 season; the live museum snippet identifies Dilmun as its production place. The museum page returned 403 when opened. The Dilmun row therefore adds no separate object minimum, while the unresolved join to the five local Ur families remains visible. [Museum record, snippet only](https://www.britishmuseum.org/collection/object/W_1932-1008-178).

Richard L. Zettler's *Nippur III: Kassite Buildings in Area WC-1* (1993, OIP 111), pp. 81–82 and plate 89a–d, documents one inscribed faience seal, 13 N 506 / IM 78230. Its Level III, Locus 6, Floor 3 context belongs to later use of the building. The two Kish specimens and two classic Girsu/Tello specimens are also discussed there. Henri Frankfort's *Tell Asmar, Khafaje and Khorsabad: Second Preliminary Report of the Iraq Expedition* (1933, OIC 16), pp. 50–52, illustrates As. 31-22 without Indus signs. It remains an uninscribed style comparison. [Nippur publication](https://isac.uchicago.edu/publications/nippur-iii-kassite-buildings-area-wc-1), [Tell Asmar publication](https://isac.uchicago.edu/publications/tell-asmar-khafaje-and-khorsabad-second-preliminary-report-iraq-expedition).

Laursen's Table 1 and Fig. 15 give seven Bahrain specimens: Qala'at al-Bahrain two, Karzakan three, Saar Cemetery one and Janabiyah one. Karzakan includes pseudo-signs and two V-shaped marks. Failaka's Kjaerum catalogue nos. 279 and 319 belong to different Dilmun/Gulf types; no. 279 has pseudo-writing. The Saar Cemetery specimen must be joined separately from the Saar Settlement seal catalogue. Tell Abraq's ivory seal and the cited Hili relief supply contact evidence without an authenticated Indus text. These classifications and their count bases remain separate in each row's `published_counts`. [Laursen, Table 1 and Figs. 10, 15](https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf).

The Louvre's current record for SB 2425 / AS 41 / CCO S. 299 identifies an inscribed steatite cylinder from Susa, excavated in 1898–1906. Its record was updated on 27 March 2026 and places it in Richelieu room 231, case 4. The selected Susa minimum also includes one Gulf-type seal from Laursen; additional square seals require reconciliation. [Louvre record](https://collections.louvre.fr/en/ark%3A/53355/cl010176471).

The 2022 *Corpus of Indus Seals and Inscriptions*, 3.3, edited by Asko Parpola and Petteri Koskikallio, authenticates TY-106, Alt-90 and Sh-69 as catalogue identifiers. Its contents give Tepe Yahya pp. 1–40; Konar Sandal pp. 42–136; Shahr-i Sokhta's continuation pp. 197–284; Tepe Hissar pp. 296–358; Altyn Depe pp. 370–404; Sarazm pp. 496–498; and Shortughai pp. 509–523. The acquired excerpt contains contents, preface, an essay and bibliography, with no catalogue plates. These ranges establish where to inspect the objects; they do not give site totals of Indus inscriptions. [Institutional excerpt](https://orbi.uliege.be/bitstream/2268/333796/1/Desset%20F%202022%20in%20CISI%203.3%201763.pdf).

The CISI 3.3 preface, p. xi, identifies Alt-90 as the inscribed Altyn seal and Alt-49 as uninscribed. Its mixed Altyn series ends at 142. Tepe Hissar's series grows from 109 to 280 entries through archival material; p. xvi questions whether the cracks on H76-122 / TH-132 represent writing. François Desset's essay, pp. xx–xxii, distinguishes Tepe Yahya's 26 or 27 Proto-Elamite tablets and four Konar Sandal Linear Elamite documents from Indus-related finds. Sarazm's five entries include possible stamps and a cylinder, with no authenticated Indus text established by the inspected excerpt. The highest local number has no supported interpretation as an Indus coverage denominator. [CISI 3.3 excerpt, preface and essay](https://orbi.uliege.be/bitstream/2268/333796/1/Desset%20F%202022%20in%20CISI%203.3%201763.pdf).

Viktor I. Sarianidi's *Gonur-Depe: City of Kings and Gods* (2005), pp. 258–259, Fig. 114, reports the elephant seal from autumn 2004 in room 19, Area 9 of the Water Temple. Fig. 115 describes a separate cuneiform cylinder found three years earlier. The Gonur row counts each class independently. The CISI 3.3 preface reports that the proposed Gonur corpus was not supplied for that volume. [Original 2005 book](https://margiana.su/publication/book/Gonur-Depe_City_of_Kings_and_Gods_2005.pdf).

Dennys Frenez, Michele Degli Esposti, Sophie Méry and Jonathan Mark Kenoyer's *Bronze Age Salūt (ST1) and the Indus Civilization: new insights on regional interaction* (2016, *Proceedings of the Seminar for Arabian Studies* 46: 107–124), pp. 116–118, distinguishes a chlorite seal from two seal-impressed rim fragments. Both fragments may come from one jar. The selected minimum is two objects: a seal and one pottery vessel. The local TAG label needs correction through an object join. Ras al-Jinz has a separately documented copper seal, while its three local pottery families still lack a matched published inventory. [Salut paper](https://www.harappa.com/sites/default/files/pdf/Bronze-Age-Indus-Connections.pdf).

The historical Umma clay impression and the post-2016 survey finds have different evidence histories. Drahoslav Hulínek's 2021 project report describes Harappan seal impressions without an itemised total. The earlier COMM-02 acquisition of the illustrated 2017 find remains incomplete; the newly opened project account supplies a further witness. [Project SAHI-Tell Jokha](https://iaassyriology.com/in-the-field-the-project-sahi-tell-jokha/).

## Remaining gaps and verification

All 36 rows have at least four live searches and an associated opened substantial source. The 1,013-record source manifest includes incidental snippets; 46 sources appear in the row source lists. A site mention in a regional article can support a classification while leaving campaigns, custody and specimen metadata unresolved. Eight metadata fields are individually populated or search-linked in every row. No inspected site subtotal from Mahadevan 1977 or ICIT was recovered. Provinces and most coordinates need dedicated authority checks, and complete final-report content was not acquired for several bibliographically identified reports.

The largest object-level gaps are the three Ras al-Jinz pottery families, Girsu/Tello alias deduplication, the Saar cemetery/settlement join, the Hajar/al-Hajjar prism identification, and the Kalba pseudo-sign specimen. Murda Sang's damaged pottery face has no matched published inscription inventory. Ornach's Kinneru caption supplies a candidate locality whose connection to the local fragment remains unverified. Missing or inaccessible catalogues prevent reliable holdings and excavation-registration joins at many sites.

[review-checks.json](review-checks.json) confirms the CSV round trip, 779 source-reference checks and eight acquired-PDF hashes. [validation.json](validation.json) verifies the row frame, query minimum, associated opened sources and copied local labels. The local metadata totals are **0 period/time faces, 5 room/grid faces, 15 dimension faces and 10 excavation-number faces**. Source sampling should repeat the numbered objects and locators above, then inspect actual CISI plates and Kjaerum's catalogue before calculating coverage.
