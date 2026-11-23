# Institutional data-access request draft: HARP (Q-1017)

This is an unsent request draft prepared for maintainer approval under question card [Q-1017](../../knowledge/questions/Q-1017-harp-harappa-context-registers.md). No excavation director, project archivist or institution has been contacted.

## Target and provenance basis

- **Target institution**: Harappa Archaeological Research Project (HARP), directed by Jonathan Mark Kenoyer (University of Wisconsin–Madison) and Richard H. Meadow (Peabody Museum, Harvard University), in collaboration with the Department of Archaeology and Museums, Government of Pakistan.
- **Published foundation already held locally**: Kenoyer and Meadow (2010), introduction to *Corpus of Indus Seals and Inscriptions 3.1* (held in both the 15-page printed excerpt and the 17-page HARP version); Meadow and Kenoyer (2000), *The 'Tiny Steatite Seals' (Incised Steatite Tablets) of Harappa: Some Observations on Their Context and Dating*; Meadow and Kenoyer (2001, 2005) excavation summaries; and our object-level coding of 24 published HARP objects (`experiments/2026-10-02-six-hour/harappa-object-frame/README.md`, covering copied steatite tablets H-2218 through H-2239 plus rectangular seals H-1710 and H-1714).
- **Why this request is prioritized**: Harappa is the largest site in our local register (1,921 provisional objects), yet only 14.1% carry all three dimensions, 38.6% carry a depth, and outside the 22 published Meadow and Kenoyer (2000) tablets no object carries a lot number, deposit type (primary floor versus secondary dump) or associated artefact assemblage. In addition, our 26 October 2026 object pilot (`experiments/2026-10-26-object-pilot/REPORT.md`) flagged three specific Harappa archival gaps: the disputed 1996 registration alternatives (`7158` vs. `7458`) for H-2587, and the stratigraphic field sequences for Harappa lots `3166` and `8796`. Finally, testing conjecture C-0005 (whether incised tablets sharing a descriptor and tier co-occur in the same excavation units or primary deposits) requires unit, lot and deposit-type fields across the HARP inscribed assemblage.

## Draft email / message (for maintainer review and sending)

**Subject:** Research inquiry regarding HARP excavation context registers for inscribed Harappa objects (1986–2001 seasons)

Dear Professor Kenoyer and Professor Meadow,

We are assembling a source-linked archaeological metadata register of inscribed Indus objects to study find contexts, workshop production groups and stratigraphic phasing across Harappa and contemporary Indus sites. We have already incorporated the published context data from your 2000 study of the incised steatite tablets H-2218–H-2239 (restoring their `H{year}-{registration}/{unit}-{item}` keys and the Unit 8040 clump versus nearby and scattered deposits), your 2001 and 2005 reports for H-1710 and H-1714, and your 2010 introduction to CISI 3.1.

We are writing to ask whether an existing non-image context register (or a bounded extract from the HARP object and lot databases) for the inscribed objects excavated by HARP since 1986 can be consulted for academic research, under whatever access and citation terms HARP specifies.

**Specific metadata fields sought (text and tabular metadata only; no unpublished photographs requested unless separately permitted):**

1. **Identifier crosswalk**: HARP registration number (`H{year}-{item}`), excavation lot and feature or unit number, and CISI 3.1 catalogue number (where published) for inscribed seals, tablets, sealings and stamped pottery.
2. **Stratigraphic and spatial context**: mound and trench, locus or stratum, deposit type (for example primary floor, hearth or craft area, street fill, or secondary dump and slope wash), and HARP period and sub-period assignment (3A, 3B, 3C and transitional labels).
3. **Physical measurements**: material, object class and recorded length, width and thickness (mm) where tabulated.
4. **Priority conflict and chronology checks (if a small initial extract is more practical than a full table)**:
   - Object cards and registration history for **H-2587** (resolving the `7158` vs. `7458` registration ambiguity recorded across published sources);
   - Stratigraphic context and phase basis for Harappa **lots 3166 and 8796** (linked to published seals and tablets in our 2026 object pilot);
   - Unit, lot and deposit-type records for the remaining HARP incised and bas-relief tablets beyond the Unit 8040 clump (H-2218–H-2239), to test whether repeated tablet series co-occur in primary contexts or secondary dumps.

**Handling and redistribution commitments:**

- All unpublished HARP register files or extracts will be kept strictly local and private, and will not be redistributed, posted to public repositories or bundled into public datasets.
- Any public research outputs will cite HARP and your relevant publications explicitly, report only derived aggregate statistics and published catalogue identifiers, and preserve any embargo or citation wording you request.
- If a formal archival access procedure, institutional agreement or collaboration framework is required (for example through the HARP archive or Peabody Museum / UW–Madison collections), we would be glad to follow that process.

Thank you very much for your time and for making so much of the Harappa excavation record accessible through your publications.

Sincerely,

[Maintainer Name]  
[Affiliation / Project Contact]

## Maintainer checklist before sending

- [ ] Confirm sender identity, institutional affiliation and preferred contact email.
- [ ] Verify whether to request the narrow priority extract first (H-2587, lots 3166 and 8796, and HARP tablet units and lots) or the full inscribed-object context table.
- [ ] Attach or link our published 24-object Harappa context coding table (`experiments/2026-10-02-six-hour/harappa-object-frame/README.md`) if helpful to demonstrate concrete scholarly use.
- [ ] Record the sent date, response and exact terms in `data/MANIFEST.json` and `knowledge/questions/Q-1017-harp-harappa-context-registers.md`.
