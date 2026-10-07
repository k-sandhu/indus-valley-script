# Findings

## Coverage cannot be expressed as one fraction

The public evidence located here does not support a percentage of all excavated inscribed objects that appears in an accessible index. ICIT's 2023 abstract reports 4,665 objects, 5,650 texts, 17,966 legible sign occurrences and 16,015 photographs/drawings (CAA 2023 abstract 76, p.281; source record `ICIT-COUNT`). Those are four different units and are a dated database total. The denominator of all published finds is not known, and the current ICIT records cannot be enumerated without access permission. CISI volumes are photographic catalogues, not a single deduplicated object total. Therefore the accessible-index fraction is **not estimable** from this source set.

## Site and local-file counts

The register has **89 site and region labels**: **78** literal values occur in the pinned Lipi observed-face export and eleven follow-up leads were added. Four rows are explicitly labelled as an unresolved value, region or survey area rather than a confirmed individual site. The number of distinct archaeological sites represented by these labels is therefore not verified. Lipi contains **5,680 rows** with a nonempty literal `site` field across 78 values. Mayig contains **179 rows**, all for Mohenjo-daro. The overlap between annotations is substantial, so these counts cannot be summed as objects. The exact rows by label and source are in `site-register.json` and `site-register.csv`; `build_registers.py` reproduces the local counts from the normalized inputs.

Eleven locations added beyond the Lipi values are Tell Jokha, Shahr-i Sokhta, Mundigak, Tell Abraq, Umm an-Nar, Hili, Ra's al-Jinz, Bet Dwarka, Manda, Kotada Bhadli and Binjor. Their inclusion records a bibliography/search lead, not a claim that each has a verified Indus-script object. In this exploratory register, **78/89 rows (87.6%)** have a Lipi site label and **1/89 (1.1%)** has a Mayig row; the remaining 11/89 (12.4%) have no record in either counted file. This is coverage of site names in these two local files, not coverage of archaeological evidence.

Seven site-specific excavation-report volumes were identified by title for four sites: two Lothal volumes, two Farmana reports, two Kanmer report publications and one Dholavira report. A fifth site, Harappa, has a source-linked primary 2000 chapter in the reviewed frame. This is a lower-bound bibliographic count from the bounded source set, not a review of every site's excavation history. The 17-item publication register also includes five CISI parts, one broad ICIT conference abstract, a site-focused Lothal study and a Kanmer article. CISI 3.2 names Shahr-i Sokhta, Mundigak, Mehrgarh, Nausharo, Sibri, Dauda-damb, Chanhudaro, Ahar, Balathal, Gilund, Kalibangan and Rojdi in its official title. CISI 3.3's Indo-Iranian Borderlands publication is confirmed by a 2022 institutional chapter record; the full contents were not inspected.

## Counts that can be compared without merging denominators

| Site/source | Reported quantity | Unit and basis | Index relation established here |
|---|---:|---|---|
| Harappa, Meadow and Kenoyer 2000 | 22 objects; 66 drawn faces | Figure 4 specimens 2–23; three drawn faces per tablet. Faces are illustrations, not extra objects. | Lipi has 2,717 Harappa rows; tablet-to-row joins were not recomputed in this census |
| Lothal, Frenez and Tosi 2005 | ~100 | Approximate terracotta sealings; authors' study summary; no page-by-page recount | ICIT-based 2023 discussion says about 90 sealings at Lothal; definitions and membership were not joined |
| Kanmer, Agrawal et al. 2010 | 3 | Clay sealings with central holes; text and Fig.3a-b | Site occurs in the 2023 ICIT-based list; exact object join not checked |
| Farmana, Shinde et al. 2008 | 2 seals + 2 terracotta impression objects | Reported categories in the seal/sealing section, printed p.101; one seal was from the preceding season | Farmana occurs in the 2023 ICIT-based list; the report objects were not joined individually |
| Dholavira, Bisht 2015 | Not extracted | Primary report title and official cover identified; complete report not acquired or page-audited | Dholavira appears in Lipi and an ICIT-based secondary summary; CISI volume coverage and object-level joins were not checked |

The Lothal values (~100 and ~90) may use different object definitions or updates. The independent object lists needed to reconcile them were not inspected. Farmana's four reported categories are not treated as four newly found inscriptions because one seal was recovered in a previous season and the report distinguishes impression objects from seals.

## Metadata availability

This package distinguishes `Present` from `Not assessed`. Across the four site-focused source passages inspected in detail (Farmana, Kanmer, Lothal and Harappa), material/type information appears in **4/4**, photographic evidence in **3/4**, drawings in **2/4**, and a find-location plan, a figure scale or registration keys in **1/4** each. Harappa's source is a primary 2000 chapter; its Figure 4 shows 22 tablets as 66 drawn faces, its Figure 2 supplies a location plan, and its captions give excavation registration/unit/item identifiers. These proportions describe four inspected source passages, not all publications or objects. The exact source associations are in the site `metadata` fields and count records in `site-register.json`.

For the **87-label** register as a whole, the corresponding source fields are not assessed in **85 or more rows**. This run cannot quantify how often excavation publications report stratigraphic phase, absolute dates or complete object dimensions. The most visible gap in this sample is the absence of object-level joins from later reports to corpus identifiers. Coordinates, campaign lists, precise CISI page ranges and field-by-field metadata completeness remain incomplete for most labels.

## Candidate unindexed finds

The gap register contains three candidates and **zero findings confirmed absent from all checked indexes**. Farmana's 2008 report and Kanmer's illustrated three-sealing report are concrete source-to-record reconciliation targets. The published 2023 discussion lists both in ICIT's site coverage, so neither can be called unindexed based on the current evidence. The 2015 Dholavira excavation monograph is another reconciliation target, but this run did not identify a particular reported object absent from CISI, ICIT and the local corpus.

## Access, search failures and limitations

The 2010 Cambridge article and 2005 Lothal chapter metadata were opened. The accessible Dholavira PDF was a derivative extract rather than an official complete report; no count was taken from it. Searches restricted to ASI's website did not surface usable Rakhigarhi or Kanmer records. The Rakhigarhi search returned reproductions of older excavation reports, not a season-by-season new-object census. The complete CISI 2 volume and CISI 3.3 contents were not inspected. `sources.json` retains these outcomes and the basis for each bibliographic item.

The register's added sites and country assignments are discovery aids. Coordinates, all excavation seasons, CISI page ranges and per-source specimen metadata have not been collected site-by-site. This work answers that the public evidence is indexed in multiple overlapping resources and records several measurable source counts; it does not establish that all findable evidence has been indexed.





