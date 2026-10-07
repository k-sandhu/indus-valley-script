# Additional Pakistani localities, 7 October 2026

The three added labels contribute three local faces and three object families: one seal each for Ornach area and Sibri, and one pottery face for Murda Sang. The local figures are copied from the coordinator's country check of the Iranian Plateau category. [The rows](revision-additional-pakistan.json) preserve the distinction between a catalogue object, a photographed minimum and a published inventory.

Sibri has the strongest catalogue record. CISI 2 lists three objects, Sb1–3, on pages 411–413, with basic data on page 447. The local identifier is Sb4. Its CISI 3.2 plate page 103 and basic-data page 329 are cited by Fuls (2024), page 12; those original 2019 pages were not inspected. Santoni's excavation account reports at least three triangular compartmented seals and one cylinder seal, plus one terracotta cake carrying several impressions. It also illustrates a marked terracotta rattle. These selections include comparative seals and marks, so their counts cannot serve as a denominator for the single local Indus-corpus face. Source identifiers and count units are in `Sibri.reported_object_counts`.

The Ornach review caption identifies one humped-bull Indus seal from Kinneru. DOAM gives Kinneru Damb a gazetteer point of 27.05° N, 66.2° E. The separate Ornach area gazetteer centroid is 27.01683° N, 66.19072° E. The local face has no CISI identifier, and its physical identity with the pictured Kinneru seal remains unverified. Murda Sang has one published photograph caption identifying a graffito sherd from trench III-1, layer 17. The investigator account dates discovery to 1997 and trial trenching to 1998. Searches found no independent report or gazetteer coordinate for Murda Sang. Its Wikipedia-derived coordinate candidate is retained as an unaccepted lead.

No completed site excavation report was verified in full for these three labels. The de Cardi regional survey report was identified and its introduction inspected through a publisher preview; it is recorded as `identified`, with the limited scope stated. No dated post-coverage authenticated Indus inscription was located for the three labels. Murda Sang's 1998 trenching followed CISI 2 publication in 1991, but its latest site-specific catalogue coverage is unresolved. The common gaps are complete class inventories, current custody, exact excavation coordinates and object-level registration outside Sibri's 1991 basic data.

The revision reused the coordinator's full CISI 2 PDF and Santoni chapter. Thirty live search runs covered 27 distinct query strings; the first three Murda Sang queries were repeated after a truncated tool response. The [search ledger](revision-additional-pakistan-searches.json) records their results, including failed coordinate, final-report, inventory and recent-find searches. The [source ledger](revision-additional-pakistan-sources.json) contains 22 source records and distinguishes opened text from snippets and blocked downloads. Temporary renders and the compilation script remain in the owned local raw subdirectory. No third-party payload was added to tracked outputs.

The reviewer should compare Santoni pages 56–57 with the separate units in the Sibri counts, check the Sb1–3 rows and EXB owner key on CISI 2 pages 447 and 434, obtain the original Sb4 pages in CISI 3.2, and resolve the local Ornach-face join before calculating completeness. The Murda Sang photograph establishes a marked sherd; authentication of its signs requires a separate object review.

## Rerun

From the repository root:

```powershell
python data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/afghan-minor-revision/build_additional.py
python tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/revision-additional-pakistan-notes.md --no-write
```
