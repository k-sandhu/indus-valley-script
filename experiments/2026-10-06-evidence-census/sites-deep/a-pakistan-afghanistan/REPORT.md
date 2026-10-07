# Pakistan and Afghanistan: revised census

The census now records 37 requested or added site labels and 36 site entities after the catalogue alias join. Gharo Bhiro and Nuhato remain separate rows because the local corpus uses both labels; CISI 2 describes them as one locality. 28 rows have a numerical coordinate, with source precision and unresolved archaeological identification retained. 30 rows contain a numerical class observation, including historical subsets, comparative catalogue entries and scoped zero-find statements. These figures come from [aggregate.json](aggregate.json) and the individual `coordinates` and `reported_counts_by_class` fields in [site-rows.json](site-rows.json).

## Publications and later finds

Final excavation monographs are identified for 8 sites: Amri, Chanhu-daro, Harappa, Mohenjo-daro, Mundigak, Nindowari, Pirak, Shortughai. Final exploration publications cover 5 further labels: Jhukar, Lohumjo-daro, Ornach area, Sotka Koh, Sutkagen-dor. Only Chanhu-daro’s full final-report scan was inspected during this revision, primarily its title, preface and recording information. Five further reports have unresolved final or comprehensive status: Gumla, Mehrgarh, Naru-Waro-dharo, Rehman Dheri, Sarai Khola. This classification uses each row’s `final_report.publication_assessment`; bibliographic identification does not establish a completed modern inscription inventory.

The strict post-CISI tally is **0**. 24 rows have no dated later find recovered by their recorded query sets; 13 have an unresolved cutoff or later-find history. Ganweriwala’s 2015 tablet is documented in the opened 2016 account, but its latest catalogue inclusion is unresolved. Chanhu-daro’s renewed 2015–17 work is documented; exact inscription pages and counts remain inaccessible. The Harappa 1998–2000 tablets belong to later CISI coverage, and the earlier first-pass Nausharo attribution was corrected. Balakot’s 1976 excavation is earlier than CISI 2. See those rows’ `post_cisi_finds`, `post_cisi_assessment` and source locations, rather than treating publication dates as discovery dates.

## Published counts and local coverage

Mahadevan’s *The Indus Script: Texts, Concordance and Tables* (1977), page 6, includes objects whose inscriptions were wholly or partly legible. Page 7 supplies a class table for Mohenjo-daro, Harappa and Chanhu-daro. The scan was inspected visually, and the exact extracted totals are in [revision-common-counts.json](revision-common-counts.json), source RCO-M77. Zero cells apply to that included historical inventory.

| Site | Included objects,1977 | Local faces | Local families | Local CISI IDs |
|---|---:|---:|---:|---:|
| Harappa | 985 | 2,717 | 1,921 | 1,733 |
| Mohenjo-daro | 1,540 | 1,923 | 1,795 | 1,745 |
| Chanhu-daro | 66 | 74 | 72 | 72 |
| Kot Diji | 1 | 11 | 10 | 10 |
| Amri | 2 | 5 | 5 | 3 |
| Jhukar | 1 | 1 | 1 | 1 |
| Lohumjo-daro | 1 | 1 | 1 | 1 |
| Total | 2,596 | 4,732 | 3,805 | 3,565 |

The local aggregate is a later derivative of catalogue records. Faces, families, identifiers and published physical objects have different definitions. The table therefore supports a dated inventory comparison; a pooled completeness percentage would require a reconciled object crosswalk. The seven comparison records and their units are in [site-count-comparison.json](site-count-comparison.json).

Inspected catalogue ranges expose more specific gaps. Rehman Dheri has 270 catalogue entries: 1 bone seal, 266 marked pottery objects and 3 objects captioned as tentative scrapers, against 2 local identifiers. Sarai Khola has 68 marked sherds reported in Halim 1972, with 10 photographed in CISI 2 and none in the local aggregate. Naru-Waro-dharo has 3 CISI 2 entries and 3 local identifiers. These are mark-inclusive catalogue comparisons, supported by the rows’ count records and CISI 2 pp.352–378,410–411,406,445–447. The numbering checks establish those printed ranges without asserting that every number represents an accepted Indus-script object.

CISI classifications also change the smaller-site comparisons. Nausharo has five clearly script-bearing seal identifiers Ns5–9 in the inspected 1991 plates. Mehrgarh’s Mr1–17 are comparative geometric seal or amulet forms and Mr18 is a bowl graffito. The approximate 850 Mehrgarh figure counts incised marks from early excavation seasons. Pirak’s introduction reports three Mature Harappan surface seals while the plates illustrate Pk1–2. The catalogue’s fragment-number convention prevents a direct conversion of every numbered view into a separate physical object. The exact observations and exclusions remain beside their source pages in `reported_object_counts`.

## Missing fields and source access

The most frequently unresolved fields below count label rows. A recorded numeric class observation can be a limited subset; it does not fill a complete site inventory. Metadata labels apply to the inspected publication portion. An inaccessible report field is unresolved, rather than an asserted absence.

| Field | Unresolved rows |
|---|---:|
| present_holding | 37 |
| icit_count | 36 |
| counts.metal | 34 |
| counts.sealings | 33 |
| counts.tablets | 33 |
| counts.other_inscribed_objects | 32 |
| mahadevan_1977_count | 30 |
| final_report | 24 |
| counts.inscribed_pottery_and_graffiti | 21 |
| cisi | 14 |
| counts.seals | 14 |
| post_cisi_finds | 13 |

Later CISI 3.1/3.2 pagination, complete excavation class inventories and modern custody remain the largest substantive gaps. Current custody was not reverified for any site; dated holding codes and Harappa’s2010storage statement remain in `present_holding`, with the unresolved current check in `holding_assessment`. The CISI 3.3 selected excerpt gives Shortughai Sh1–84 on pp.509–523 and Mundigak supplementary Mgk63–66 on p.528, but omits the full object pages needed to audit those mixed inventories. Nuhato’s 2018 report remains inaccessible. Rajanpur Chak 585 coordinates describe a candidate early settlement, whose identity with the local tablet’s label has not been established. These limits appear in the relevant row fields with the exact searches that failed to resolve them.

The source ledger distinguishes an opened body, a bibliographic record, a search snippet and failed access. It retains irrelevant search leads for an auditable search history. The merged source count is a ledger size, not a count of independent excavation publications. Raw acquisitions stay local because no general redistribution permission was established. CISI 2 p.ii assigns separate rights to the volume and object photographs.

## Reviewer checks

Repeat the Mahadevan page 6–7 transcription and three class-table column sums. Recheck the Rehman Dheri scraper captions and Sarai Khola 68-versus-10 basis. Open the latest site-specific CISI 3.2 entries before changing the post-CISI tally. Resolve Sibri Sb4 provenance, Rajanpur’s homonym and Gharo Bhiro/Nuhato object identities. Compare gazetteer coordinates and campaign disagreements with original report maps. Rerun the README commands and sample every source ID used for numerical counts.
