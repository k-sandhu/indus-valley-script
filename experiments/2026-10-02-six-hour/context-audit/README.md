# What the context tables can support

The existing prediction sample represents very little of three published Harappa groups that have useful production or physical-use descriptions. The groups contain 69 published objects, of which 60 join to the preserved export. Only two of those 60 objects enter the complete right-to-left single-line population with at least three signs. The audit also found that the earlier summary treated 2,870 missing depth strings and zero-valued dimensions as present. These results identify a better sample frame for studying what people did with inscribed objects.

The [availability endpoint](main/results.json) covers all 5,680 Lipi rows and 4,695 numeric families. The [published-cohort endpoint](source-cohorts/results.json) follows an original archaeological source into those rows. The [refined identifier endpoint](join-keys-refined/results.json) examines practical context keys. The protocols were recorded separately; the cohort and identifier extensions followed the first audit and source inspection.

## Available fields

| Field | Rows with an informative value | Percentage of 5,680 rows | Families with an informative value |
|---|---:|---:|---:|
| Site | 5,652 | 99.5% | 4,668 |
| Material | 4,706 | 82.9% | 3,871 |
| Area or section | 4,260 | 75.0% | 3,469 |
| Room or grid | 2,191 | 38.6% | 1,865 |
| Time label | 3,067 | 54.0% | 2,380 |
| Period label | 2,318 | 40.8% | 1,887 |
| Phase label | 2,653 | 46.7% | 2,039 |
| Depth | 2,810 | 49.5% | 2,375 |
| Positive horizontal dimension in millimetres | 3,870 | 68.1% | 3,158 |
| Positive vertical dimension in millimetres | 3,999 | 70.4% | 3,195 |
| Positive point thickness in millimetres | 1,563 | 27.5% | 1,246 |

The original missingness rule recognized a small set of literal placeholders. Depth often uses `- -`, which that rule missed. The millimetre columns use zero for many missing measurements: 1,810 horizontal values, 1,681 vertical values and 3,586 thickness values. A further 531 thickness strings are reported as ranges or other nonnumeric forms. The point-measurement count leaves those strings in a separate category; future geometric work can parse and use their interval information.

There are 2,506 reported motif values, 2,635 literal `None` values and 539 missing or unknown values in `symbol`. Keeping catalogued absence separate allows a comparison of objects bearing pictures with objects bearing text alone. The 74 literal motif categories also contain subtypes and spelling distinctions that require a source-linked coding map before pooling.

Every audited metadata field is identical across all faces within each numeric family. Row counts therefore repeat object-level assertions when an object has several surfaces. The family columns in the table give a more useful unit for archaeological availability. This agreement also makes the export convenient to join, while a future image table should retain the sides' separate graphic observations.

The table gives catalogue availability. Field verification is recorded in [source assertions](source-assertions.json). The earlier 25-object plate audit examined graphics and layout, and offers no general estimate of the metadata's accuracy.

## Joint coverage and dependence

Site, type and material occur together on 4,702 rows from 3,867 families. Area, room/grid, excavation label, depth and at least one chronological label occur together on 1,444 rows from 1,163 families. Of those rows, 751 are from Harappa and 682 from Mohenjo-daro. The remaining 11 rows come from other sites. A comparison requiring this full field set would mostly be a study of those two excavated collections.

Some within-site chronological comparisons have usable class sizes. Among Mohenjo-daro square-seal families, the period field records 29 Early, 277 Intermediate and 230 Late cases. Among Dholavira square seals, it records 28 Period 4, 10 Period 4/5 and 26 Period 5 cases, alongside smaller classes. These counts support a source-audited study of graphic or carving changes within one site and manufacture class. The next coding table needs the dating basis for each object, because the HARP introduction describes both context-based and style-based chronological assignments. That separation makes a test of style through time interpretable.

The 2,107 eligible faces connect into 1,526 physical-family/identical-whole-text components. Thirty-three components span several sites; 38 span several object types; 34 span several reported materials. Ninety-one span several area/section values. A train/test split that places the same component on both sides would carry those repeated texts across archaeological labels. These figures reproduce the dependence unit used in the earlier prediction work and add its context composition.

All 179 Mayig faces join uniquely to a Lipi family. Mayig supplies a fixed Mohenjo-daro unicorn-seal block with five annotator description classes, numbered I–V, and graphic features. Its site and broad object type have no variation. Its five classes map to several Lipi unicorn subtypes, so the existing categories offer an annotation-comparison task. For example, all nine class-I faces have `Bull1:W`, while the 96 class-IV faces are distributed across nine Lipi labels. A new observer can code the pictures on a fixed sample to learn which visual features each category is capturing.

## Published objects through the filters

The full public witness of [Kenoyer and Meadow's 2010 introduction](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf), printed p. l / PDF p. 9, identifies the following groups. Its text was checked against the rendered page. The [retrieval record](source-retrieval.json) preserves the URL, byte count and hash; the downloaded PDF and renders remain local.

| Source group | Published objects | Objects joined to export | Matched faces | Complete RTL single-line faces | Eligible faces of length ≥3 | Eligible objects |
|---|---:|---:|---:|---:|---:|---:|
| Copied incised tablets, H2218–H2239 | 22 | 22 | 66 | 66 | 0 | 0 |
| Sealings and jar-stopper, H1719–H1725 | 7 | 6 | 8 | 0 | 0 | 0 |
| Stamped vessel sherds, H1727–H1766 | 40 | 32 | 32 | 5 | 2 | 2 |
| Total | 69 | 60 | 106 | 71 | 2 | 2 |

All 66 faces in the copied-tablet block have exactly two signs. The length threshold removes the whole block, although its inscriptions are complete in the export. The sealing block contains seven incomplete faces and only one complete face; that complete face has unspecified direction. The stamped-vessel block has 18 one-sign faces, ten two-sign faces and four three-sign faces, with several direction and preservation categories.

The object-identifier ledger in the endpoint lists the nine absent references, including H1724 and eight stamped-vessel identifiers. It also records that H1537 and H1539, two source-mentioned re-examination cases, are absent from this observation table. That targeted check produced no correction to the corpus.

This selection result matters when choosing an archaeological experiment. The earlier ≥3-sign benchmark was designed to estimate sequential dependence. To study production batches, container sealing or vessel marking, use an object frame drawn from the source groups and retain short inscriptions, incomplete faces and their original boundaries. Each task can then declare the graphic evidence that it actually needs.

## Context keys

The refined identifier audit distinguishes registration from excavation-unit information. Of 1,921 Harappa families, four strings contain the documented registration-plus-lot/item syntax, 124 contain a hyphenated year-number-item chain, and 643 contain a registration-shaped prefix without either of those recognizable forms. There are 1,098 other reported identifiers, 49 missing values and three figure locators without an object identifier. Across all sites, four rows from four families have figure-only locators.

The first syntax parser placed the 124 hyphenated chains among registration prefixes. Inspection of its examples showed that some may encode excavation-unit/item pairs in a changed separator format. The [refinement record](JOIN-KEY-REFINEMENT.md) preserves that correction, and the first endpoint remains in [join-keys/](join-keys/results.json). A basic-data table is needed to resolve the middle number in these chains. A simple apparent shortage of slash-separated lot keys would overstate what punctuation alone can establish.

## Next source experiment

A useful post-audit design starts with the stamped-vessel group, H1727–H1766. Acquire the CISI3.1 object plates and basic-data entries for all 40 identifiers, alongside the contemporary long rectangular seals H1704–H1715. Code source coordinates, full registration/lot/item links, vessel or sealing material, impression polarity, stamp boundaries, scale, breakage and visible sign components. Retain the 18 one-sign faces and the missing source identifiers in the collection ledger.

The first endpoint should be image correspondence: whether the sign layout and carved detail on an impression can be matched to a candidate seal or to another impressed vessel. Compare normalized image geometry with a reference using sign count, size and layout alone; keep close graphic alternatives in the candidate set. Publish the correspondence scores, source coverage and unresolved matches. This gives an empirical route from a writer's or potter's physical action to a reproducible observation, and provides a foundation for a later study of circulation between find locations.

The present public introduction supplies the target list and production description. The full plates, basic-data entries and comparison photographs are the required new inputs. The six joined sealing objects are a useful companion source block for coding attachment surfaces and preservation, with too few cases here for a broad function classifier.

## Assumptions and scope

Numeric families and matching CISI bases supply the export join. Exact excavation-unit and physical-side links need their own source checks. Chronological labels retain site-specific terminology and dating basis. Point dimensions and interval dimensions are distinct observations. Component grouping protects repeated whole texts in sign-based evaluation, while an archaeological object table still preserves each physical object's location and material. The source groups were chosen after the availability audit, so this extension is a documented descriptive result and the next image test is a proposed design.

## Challenges, fixes and unsuccessful checks

| Issue | Action and outcome |
|---|---|
| Placeholder strings inflated completeness | Added explicit hyphen/whitespace and zero-dimension rules. Preserved the original summary and recorded both raw and informative counts. |
| Thickness ranges failed point parsing | Kept 531 reported unparsed strings visible. Interval parsing is a separate follow-up task. |
| Face rows duplicated context assertions | Counted availability by both face and numeric family. All within-family metadata values agree. |
| HARP witness had a different page count | Acquired and hashed the 17-page public file. It is the same published introduction as the prior 15-page witness, with preliminary book pages and different scan properties. |
| Identifier syntax permitted several readings | Preserved the first endpoint, specified a refinement, and separated hyphenated chains and figure-only locators. |
| Source cautions H1537/H1539 might affect this export | Checked both bases. Neither occurs, so that path produced no corpus correction. |
| Physical-use targets were poorly represented by the sign-model population | Counted every face in source-defined cohorts. The resulting object frame becomes the proposed next source-coding sample. |

Run the [audit code](../../../src/six_hour/metadata_audit.py) with a fresh output path. The endpoint snapshots retain the exact code used in each run. The [verification record](verification.json) checks input/snapshot hashes, accounting, placeholder examples and the source-cohort totals.

```powershell
python src/six_hour/metadata_audit.py --output experiments/YYYY-MM-DD-context-audit/main
python src/six_hour/metadata_audit.py --source-cohorts --output experiments/YYYY-MM-DD-context-audit/source-cohorts
python src/six_hour/metadata_audit.py --harp-keys --key-refinement --output experiments/YYYY-MM-DD-context-audit/join-keys
```
