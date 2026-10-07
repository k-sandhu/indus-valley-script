# Gujarat, Kutch and Maharashtra site census

Status: Exploratory. Source audit: 7 October 2026 UTC. This revision replaces the first pass for current use; the original ten files remain unchanged in [first-pass](first-pass/preservation-manifest.json).

The 25-site batch contains 496 local corpus faces in 460 object families, distributed across 13 site labels. Direct inspection of ten CISI 1 site ranges gives 317 catalogue objects. The catalogue includes geometric, pictorial and graffiti material alongside inscriptions; its objects and the local faces have different units and cutoffs. Every site has a read primary or substantial secondary passage and at least three site-specific live searches. There are 130 actual queries: 127 site-specific query records and three shared ICIT queries. These bases are recorded in [aggregate-results.json](aggregate-results.json), fields `sites`, `local_faces`, `local_object_families`, `cisi1` and `minimum_distinct_searches_per_site`.

## Scope and report access

There are 23 Gujarat sites, Daimabad in Maharashtra and the explicitly requested Nuhato cross-reference in Sindh. Pabumath was added from the local coverage list and verified against CISI 1 Pbm 1. Juna Khatiya was added as a local pottery-record lead. Kanewal was found while reading *Indian Archaeology 1977–78 – A Review*, p. 21, item 22: the passage explicitly reports incised Harappan characters on potsherds. Its 1980 final-report bibliography was then verified in the [CiNii record](https://ci.nii.ac.jp/ncid/BA82253260). Addition evidence is in `site-rows.json[].addition_basis`; search bundle B37 contains its three searches.

Twelve sites have a bibliographically identified completed campaign publication, including the 121-page Nuhato 2018 departmental report. Relevant passages from six were read: Lothal, Dholavira, Kanmer, Rangpur, Nuhato and Daimabad. The other six are bibliographic identifications. The 12 sites are listed in `aggregate-results.json.completed_report_sites`; each row’s `final_report` states access. This count does not imply a final publication for all seasons. Nageshwar’s 1990 report date is taken from Rawat 2015, p. 213; the first pass’s 1992 attribution was not independently reproduced.

## Published counts and local coverage

| Site | CISI 1 objects / pages | Local faces / families / CISI IDs |
| --- | --- | --- |
| Lothal | 290 / 238–297 | 208 / 182 / 179 |
| Dholavira | 2 / 355 | 238 / 230 / 2 |
| Surkotada | 6 / 362–363 | 6 / 6 / 6 |
| Kanmer | No site section in inspected contents | 10 / 8 / 0 |
| Shikarpur | No site section in inspected contents | 8 / 8 / 0 |
| Gola Dhoro (Bagasra) | No site section in inspected contents | 6 / 6 / 0 |
| Nageshwar | No site section in inspected contents | 0 / 0 / 0 |
| Khirsara | 2 / 357 | 4 / 4 / 2 |
| Kuntasi | No site section in inspected contents | 0 / 0 / 0 |
| Rojdi | 1 / 361 | 4 / 4 / 4 |
| Desalpar | 3 / 355 | 3 / 3 / 3 |
| Juni Kuran | No site section in inspected contents | 0 / 0 / 0 |
| Kotada Bhadli | No site section in inspected contents | 0 / 0 / 0 |
| Navinal | No site section in inspected contents | 0 / 0 / 0 |
| Nagwada | No site section in inspected contents | 0 / 0 / 0 |
| Padri | No site section in inspected contents | 0 / 0 / 0 |
| Bet Dwarka | No site section in inspected contents | 0 / 0 / 0 |
| Rangpur | 2 / 360 | 0 / 0 / 0 |
| Prabhas Patan | 1 / 359 | 0 / 0 / 0 |
| Pithad | No site section in inspected contents | 0 / 0 / 0 |
| Nuhato | No site section in inspected contents | 5 / 5 / 0 |
| Daimabad | 9 / 352–354 | 2 / 2 / 2 |
| Pabumath | 1 / 358 | 1 / 1 / 1 |
| Juna Khatiya | No site section in inspected contents | 1 / 1 / 0 |
| Kanewal | No site section in inspected contents | 0 / 0 / 0 |

The table’s published counts are CISI 1 identifier slots from the printed site sections and contents, not complete excavation totals. At those ten sites the local export has 466 faces, 432 families and 199 distinct CISI identifiers, including later Dholavira material and Rojdi identifiers extending beyond CISI 1. The local source is [local-site-coverage.json](../../../2026-10-06-research-program/local-site-coverage.json); exact unchanged source fields and hash are copied into each row’s `local_corpus.evidence`. No completeness percentage is calculated across these units. CISI 1’s scan contains a duplicate 431-page sequence; the audit used the first sequence and treated photographic views/impressions separately from object identifiers.

Mahadevan 1977, p. 6, Table 1 gives 175 selected legible inscribed objects across five sites: Lothal 165, Desalpar 2, Dholavira 1, Rojdi 2 and Surkotada 5. Lothal’s class table, p. 7, gives 89 seals, 75 sealings and one pottery object. These objects overlap CISI records and cannot be added to 317. The values and selection rules are in `mahadevan1977` and `counts_by_class`.

Several larger source inventories require separate interpretation. Rangpur’s report, p. 130, counts 26 figurative, 188 linear-symbol and eight combined-sign potsherds, a total of 222 broadly marked sherds; its CISI 1 selection has two objects and the local export has none. Dholavira’s 2015 report, p. 242, marks 139 of 194 analysed seals as inscription-bearing; its overall inventory, p. 232, has 225 seals. The same report gives 60 sealings in its overview and 61 in the detailed chapter, p. 308, whose subtraction is internally inconsistent. Lothal’s 1985 report, p. 305, gives 91 sealings; Frenez and Tosi 2005, pp. 67–68, give 93. These differences are retained side by side in each row’s `count_comparisons`; [sources.json](sources.json) supplies exact bibliographies and witnesses.

Daimabad’s final report, pp. 504–507, explicitly describes two script-bearing terracotta seals and five marked sherds across phases II andIII. CISI 1 catalogues nine objects with different classifications, including a cylinder scene and a crescent scene object. Desalpar’s primary review, p. 10, has two script-bearing seals and one lettered clay sealing. The first pass’s three-seal claim is corrected. Shikarpur’s 2008–09 report, pp. 3–5, has two inscribed sealing objects and one tablet; three impressions on one sealing remain one object. Each observation has its own count unit, date and source page in `reported_counts`.

Fuls 2023’s ICIT-based regional list,§5.3, p. 501, supplies 1446 legible sign occurrences across 13 batch sites. Those are signs, not objects, faces or texts; they are stored in `icit_site_count` and excluded from object totals. No ICIT object denominator was verified. Juna Khatiya’s two signs in that transcription require an original artifact source before archaeological inscription status can be verified.

## Finds after catalogue coverage

Two sites have directly established CISI 1 sections followed by dated new inscribed finds: Dholavira’s 1989–2005 campaign and Khirsara’s 2009–10 campaign. Nuhato adds a third dated later-find case: the 2018 report, pp. 14, 41–42, describes a newly excavated inscribed terracotta seal distinct from the 1973 find. It cites the older seal in CISI 2, p. 390; that catalogue page remains uninspected. Thus the total is two with directly checked catalogue baselines, plus one with a baseline reported by the excavation author. Nuhato is outside the regional-only denominator.

Four further sites have explicit script-material reports published after 1987 and no CISI 1 site section: Kanmer, Shikarpur, Gola Dhoro and Nagwada. Nagwada’s sealing is from the 1987–88 season and the annual review was published in 1993; its excavation date cannot be narrowed to before or after CISI 1 publication. Padri’s later fish-pattern button seal has uncertain inscription status. Bet Dwarka’s two reported protohistoric inscriptions have disputed attribution and unverified recovery dates. Rojdi’s later catalogue publication does not by itself date new inscription discoveries. Details are in `post_cisi_finds`.

## Remaining gaps

All 25 sites have sourced coordinates or a published extent: 24 points and Bet Dwarka’s island bounds. Conflicts are retained in `coordinates.conflicts`, including the erroneous Juni Kuran point removed from the first pass and the differing Prabhas, Pithad, Khirsara and Nageshwar locations.

The fields most often lacking a usable value in the inspected witnesses are ICIT object counts (25 sites), inscribed metal-class totals (24), other-object totals (23) and tablet totals (22). Inscription drawings were not demonstrated in 19 sites’ inspected passages and registrations in 15. These figures describe this audit’s source access, not the contents of all unpublished or inaccessible records. Each unresolved field includes actual search IDs, returned URLs and an inspected passage in `unresolved_fields`; [searches.json](searches.json) links to verbatim local responses.

Rojdi’s CISI 3.2 site pages and count remain unavailable. Nuhato’s CISI 2 page needs direct inspection. Full final object inventories for Surkotada, Nageshwar, Kuntasi, Rojdi, Somnath and Kanewal remain unread. No identified inscribed artifact was verified for Nageshwar, Kotada Bhadli, Navinal or Pithad; Juni Kuran’s steatite seal has unverified script status. Seventeen sites have unresolved current object holdings. `source-access.json` retains 13 failed acquisitions among 45 attempts and three HTTP200 challenge payloads. Successful alternate IAR downloads and the Nuhato departmental PDF are recorded alongside earlier failures. Source rights are retained per publication; raw scans, images and responses remain local.
