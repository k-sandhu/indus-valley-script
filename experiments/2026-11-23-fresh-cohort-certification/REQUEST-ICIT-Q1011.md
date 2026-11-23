# Institutional data-access request draft: ICIT (Q-1011)

This is an unsent request draft prepared for maintainer approval under question card [Q-1011](../../knowledge/questions/Q-1011-icit-access-and-fuls-wells-corpora.md). No database administrator, author or institution has been contacted.

## Target and provenance basis

- **Target resource**: *Interactive Corpus of Indus Texts* (ICIT), hosted at `indus.epigraphica.de` (maintained by Andreas Fuls and Bryan K. Wells; CAA 2023 abstract 76, p. 281, reports 4,665 inscribed objects, 5,650 texts, 17,966 legible sign occurrences and 16,015 photographs or drawings across 29 relational tables).
- **Current access state**: Verified HTTP 401 on `indus.epigraphica.de` (check W05 in [knowledge/DATA.md](../../knowledge/DATA.md)); the landing page directs researchers to request access from the administrator, and the held 2010 help file notes guest access limited to ten records.
- **Why this request is prioritized**: Our 23 November 2026 fresh-cohort certification (`experiments/2026-11-23-fresh-cohort-certification/summary-v1.json`) established that 207 post-catalogue Dholavira rows in Bisht's 2015 preliminary report cannot be separated from the local export's 230 Dholavira object families because 187 of those 230 families lack an excavation registration. Across the entire 4,695-object local register, only 28.8% carry all three dimensions, 50.6% a depth, 55.8% a period or phase label and 5.8% a baseline museum number (rising to 51.6% after CISI 1 and 2 basic-data extraction). An official ICIT research login or permitted metadata export is the direct non-purchase route to resolve the Dholavira accession crosswalk and align our local register against ICIT's 2023 baseline.

## Draft email / message (for maintainer review and sending)

**Subject:** Research access request for the Interactive Corpus of Indus Texts (ICIT): metadata concordance and Dholavira crosswalk

Dear Dr. Fuls and Dr. Wells,

We are maintaining an open-methodology research knowledge base on Indus Valley archaeology and the Indus script, focused on source-linked object metadata, archaeological context and reproducible statistical evaluation of script hypotheses. We are writing to request scholarly read access to the *Interactive Corpus of Indus Texts* (ICIT) at `indus.epigraphica.de`, or, if preferred, a permitted read-only metadata export under your stated terms of use.

Our immediate research need is object-level metadata reconciliation rather than republication of your corpus. Specifically, we would like to consult ICIT for:

1. **Object identifiers and crosswalks**: ICIT object and text identifiers mapped to CISI catalogue numbers, excavation registration numbers and museum accession numbers, especially for Dholavira (where our derivative export carries 230 provisional object families, 187 of them without an excavation registration, blocking reconciliation with R. S. Bisht's 2015 seal and sealing tables).
2. **Archaeological context and physical attributes**: site, area, trench or grid square, depth or stratum, period or phase, object type, material, preservation state, iconography class and dimensions.
3. **Corpus coverage baseline**: the current scope of post-1987 Indian and Pakistani excavations represented in ICIT (including Dholavira, Farmana, Gola Dhoro (Bagasra), Kanmer, Bhirrana, Khirsara, Shikarpur, Rakhigarhi, Dhalewan, Juni Kuran and Lakhanjo-daro), so we can determine which recently published finds are genuinely absent from existing corpora and eligible for prospective out-of-sample tests.
4. **Image and source citations**: bibliographic pointers to published plates and photographs, without requesting redistribution rights for third-party institutional photographs.

**Handling and redistribution commitments:**

- Any ICIT data, query results or images accessed under your permission will remain strictly local-only and will not be uploaded to public Git repositories, mirrored or redistributed.
- Public repository outputs will contain only our own code, aggregate coverage counts, evaluation metrics and explicit scholarly citations to ICIT (and to your 2011, 2015 and 2023 publications) with the exact database version or access date.
- We will record and enforce whatever licence, attribution or non-redistribution terms you specify in our data provenance manifest (`data/MANIFEST.json` and `knowledge/provenance/REDISTRIBUTION.md`).

We also note the related printed reference volumes (Fuls, *Corpus of Indus Inscriptions*, Mathematica Epigraphica 3, 2nd ed., 2023; Fuls, *A Catalog of Indus Signs*, Mathematica Epigraphica 4, 2023; Wells, *Epigraphic Approaches to Indus Writing*, 2011; and Wells, *The Archaeology and Epigraphy of Indus Writing*, 2015), which we plan to record with full bibliographic and acquisition metadata alongside any ICIT access terms.

Please let us know whether scholarly read access or a bounded metadata table (starting with the Dholavira excavation-number crosswalk) can be arranged, and what terms apply.

With thanks for your work building and maintaining ICIT,

[Maintainer Name]  
[Affiliation / Project Contact]

## Maintainer checklist before sending

- [ ] Confirm sender identity, institutional affiliation or project URL to include in the signature.
- [ ] Decide whether to request full ICIT web-interface read access, a bounded Dholavira + post-catalogue metadata extract, or both.
- [ ] Log the sent date, response and exact terms in `data/MANIFEST.json` and update `knowledge/questions/Q-1011-icit-access-and-fuls-wells-corpora.md` once an answer is received.
- [ ] If access is granted, record the ICIT version and date before opening any inscription sign sequences for post-catalogue candidate objects so prospective-test blinding is preserved.
