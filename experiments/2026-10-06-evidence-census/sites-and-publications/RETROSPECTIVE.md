# Retrospective

The local census was straightforward to reproduce: both normalized JSONL files have populated `site` fields, and counting literal values gave 78 Lipi names and one Mayig name. This produces a useful comparison frame while retaining the distinction between source rows and physical objects. A nine-location supplement records sites appearing in the source search but missing from these two files.

Live search found site-level counts in a 2005 Lothal sealing study, a 2010 Kanmer article and a 2008 Farmana excavation report. It also verified official bibliographic records for CISI 3.2 and an institutional chapter reference for CISI 3.3. These records do not provide a shared identifier key or a complete list of catalogue entries, so the package records source counts without summing them or asserting that later reports are absent from ICIT.

The attempted search for newer Rakhigarhi and ASI-hosted Kanmer evidence did not return usable primary records. A Dholavira full-text result led to a derivative PDF containing added interpretive material; only its existence as a report lead was retained, and no count was extracted. The official ASI report cover was then located. Those access outcomes are recorded in `sources.json`.

The main unresolved problem is joining a publication's physical finds to ICIT/CISI/local entries while respecting different object, impression, text and image units. This package preserves three such follow-up candidates and records zero confirmed index omissions. A complete census requires permissioned ICIT object access, full CISI site indexes and the relevant excavation volumes, followed by a reviewed object-level crosswalk. No source payloads were copied into the owned directory.
