# Question card updates proposed by the CISI 2 basic-data pilot

## Q-1006 (Transcribe the CISI 2 basic-data pages for the Pakistan collections)

Status: stays `open`; the pilot block is done and the remaining blocks are listed for claiming.

Dated outcome note to append under "Prior attempts":

> 13 October 2026, [CISI 2 basic-data pilot](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md). The basic data occupies printed pp. 434–447 (PDF 469–482) and prints five columns: CISI number, FC number, excavation number, museum and registration numbers, and photograph sources. It has no findspot, depth, material or dimension column. The scan's page order holds at both ends of the catalogue (printed page = PDF − 35 for pp. 1–447; 418 of 447 page headers confirm it). The pilot transcribed M-621 to M-947, 327 entries on pp. 435–436, read twice in full by independent readers and adjudicated against the page. The readings agree on 90.5% of cells (excavation numbers 91.4%, museum numbers 85.6%); the sampled first-pass error rate for excavation numbers was 3.0% (1 of 33), above the 2% limit of Q-1005, so double reading of every row is the rule; 119 of 1,635 cells stay bracketed because the scan cannot separate some digits. Joined to 283 Lipi families, the block adds a museum number to 202 objects (corpus museum coverage 5.8% to 10.1%) and an FC number to all 283, and finds that Lipi's `excavation-idno` appends the FC number without its first digit to the printed excavation number for 182 objects with four-digit FC numbers, and finds two pairs of objects whose records are crossed, which plate measurements later placed in CISI 2's table. Values are local. The remaining 22 half-column blocks and the double-reading rule are in the package's [PROCEDURE.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/PROCEDURE.md).

Proposed text changes to the card: in "Why it matters" and "How to decide", replace "museum number, excavation number, findspot and dimensions" with "museum number, NMP accession, excavation number and FC number", since the section prints no findspot or dimensions. Add `prior_attempts: CISI2-BASIC-DATA-PILOT-2026-10-13`.

## Q-1005 (Transcribe the CISI 1 basic-data pages)

Status: stays `open`.

Dated note:

> 13 October 2026. The CISI 2 pilot's schema and procedure apply to CISI 1 unchanged: printed p. 366 (PDF 402) shows the same five columns, with (o) and (t) markers in column 3 for the number written on the object and the number in the excavation report's tabulation. CISI 1's basic data prints no findspot, depth, material or dimensions either, so the card's "material and dimensions" and "dimensions" in "How to decide" should be dropped. The basic data runs from printed p. 365 to p. 375 (PDF 401–411), about 1,533 entries by the census count, in about 20 half-column blocks. At the CISI 2 pilot's rate (5.7 seconds of agent time per entry for two blind readings, adjudication and cross-check) the section needs about 2.4 hours; a double-read pilot block should come first, since CISI 1's scan differs in resolution and type.

## Q-1007 (Disposition of unmatched CISI entries)

Dated note:

> 13 October 2026. In M-621 to M-947 the basic data has rows for all 327 numbers; 44 of them have no Lipi family. Their excavation, museum and FC numbers are now in the local pilot table and can be used to look for them in other sources. The CISI numbers are listed in the pilot's [object-flags.csv](../../experiments/2026-10-13-cisi2-basic-data-pilot/object-flags.csv) with `join = no-lipi-family`.

## Q-1013 (Cross-catalogue identifier crosswalk)

Dated note:

> 13 October 2026. The CISI basic data gives an FC number (the 1979–1982 Helsinki concordance number) for every entry; the pilot table holds 327 CISI-to-FC links for M-621 to M-947 locally. The CISI 2 key states that FC numbers for Mohenjo-daro and Harappa are keyed to object numbers in the excavation reports' plates, which makes the FC number a route to Marshall and Mackay seal numbers.
