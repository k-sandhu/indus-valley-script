# Crop survival and changing farming after Harappan urban decline

25 October 2026. Initial independent source audit and descriptive reanalysis. Status class: `source-review`; verification tier: `submitted`. GPT-6, Codex API workspace harness; exact model build unavailable.

The evidence supports survival of an established crop repertoire alongside changes in its composition. We completed a bounded audit of the Jognakhera claim and extracted nine published phase summaries from five comparison sites. At Bahola, winter crops remain present across the Late Harappan-to-Painted Grey Ware sequence while their reported share rises from 6.87% to 17.29%. Crop survival and stable crop proportions are therefore separate questions. The published authors already described variation; our contribution checks the source chain, reconstructs selected calculations and defines the data needed for a stronger comparison.

The current [summary](run-v2/summary.json), [second extraction and arithmetic check](run-v2/validation.json), [figure](run-v2/seasonal-comparison.svg) and [protocol](PROTOCOL.md) contain the exact endpoint. This is our reanalysis of others' excavated observations. We have collected no new plant specimens or dates.

## What the Jognakhera paper establishes

Swaroop and colleagues report eight flotation samples from layers 5–12 of trench YA1/IV, recovered with a 0.5 mm sieve. Their main text gives three crop date ranges: barley, 2471–2298 cal BCE; green gram, 1880–1691 cal BCE; and rice, 1517–1428 cal BCE. The latter two lie after the conventional 1900 BCE urban transition. These dates support crop presence after that transition. [Methods, PDF p. 5; chronology, PDF p. 7](https://www.researchgate.net/profile/Mansi-Swaroop/publication/410751986_Archaeobotanical_data_from_a_Baran_settlement_4300-3400_yrs_bp_in_the_Ghaggar_basin_northwestern_India_reveals_continuity_of_the_Indus_crop_package_after_the_Meghalayan_stage_drought/links/6a6308e8a487f668c31bde5e/Archaeobotanical-data-from-a-Baran-settlement-4-300-3-400-yrs-bp-in-the-Ghaggar-basin-northwestern-India-reveals-continuity-of-the-Indus-crop-package-after-the-Meghalayan-stage-drought.pdf?origin=institution).

All three reported ranges precede the 1200 BCE reference used in the news article's PGW date bracket. The youngest interval ends 228 years before that reference. This is an interval comparison, not a new radiocarbon model or a universal date for the beginning of PGW. The plant sequence's extension into a specifically identified local PGW context still needs a layer-to-phase join. The presence of PGW pottery at a settlement alone cannot supply that join.

The paper reports pooled counts and percentages, but its supplementary tables were inaccessible in this session. We cannot yet reconstruct the focal 0.2% millet figure, compare every crop across layers, or check laboratory identifiers, dated specimen numbers, sediment volumes and model code. The 950 and 867 totals remain source-reported quantities. Adding the published category percentages to 100 is only an internal closure check. It is not a replication of the counts.

One sampling trench is not a regional population of farms. A pooled collection containing crops from two growing seasons also leaves open how land, years and fields were organized. Weed associations, processing remains and independently dated deposits would distinguish particular management practices.

## A reporting error

ThePrint's article describes maize, sugarcane, mustard and sunflower as excavated crops. The corresponding list in the paper appears in its account of the modern environment, before the archaeological methods and results. That paragraph does not establish those plants as ancient finds at Jognakhera. The error is in the article we read; we have not checked the video's complete spoken wording. [ThePrint, Archaeobotany section](https://theprint.in/opinion/can-you-dig-it/the-indus-valley-civilisation-declined-its-crops-survived-and-adapted/3075386/), [paper, PDF p. 4, “The study site and its environment”](https://doi.org/10.1007/s00334-026-01140-4).

## What we independently recalculated

The Cambridge accepted manuscript of Petrie and Bates (2017) includes its supplement. We extracted all nine seasonal summaries in Tables S5, S8, S9, S12, S19 and S23. They cover Dabli vas Chugta, Burj, Masudpur VII, Masudpur I and Bahola. The PDF matches the hash of a copy held by the project since 11 October. These publications and their underlying thesis share a data lineage; additional papers do not create additional excavations.

| Bahola assemblage | Winter crops, % | Summer crops, % | Tree or orchard crops, % | Unassigned, % |
|---|---:|---:|---:|---:|
| Late Harappan | 6.87 | 88.24 | 0.46 | 4.43 |
| Painted Grey Ware | 17.29 | 72.88 | 4.81 | 5.02 |
| Change, percentage points | +10.42 | -15.36 | +4.35 | +0.59 |

These are proportions of recovered crop remains, not cultivated area, calories or yields. They describe a changing balance within a surviving seasonal repertoire. [Petrie and Bates (2017), Table S23](https://api.repository.cam.ac.uk/server/api/core/bitstreams/4c711d77-f084-41ae-848f-141a31a2b855/content) is on PDF pp. 91–92. [Our replot](run-v2/seasonal-comparison.svg) also shows the three Masudpur VII phases. Burj's Early Harappan and PGW occupations are separated by a reported abandonment and cannot be treated as a continuous local transition.

We also reconstructed the denominator behind two regional millet percentages cited by the 2026 paper:

| Late Harappan assemblage | Millets as % of all reported crop remains | Cereals as % of all reported crop remains | Millets within cereals, % |
|---|---:|---:|---:|
| Masudpur VII | 17.23 | 31.88 | 54.05 |
| Bahola | 60.41 | 84.64 | 71.37 |

The last column rounds to the paper's 54% and 71%. These reconstructions use the rounded entries in S12 and S23. They show why the denominator must accompany every comparison. The 2026 supplementary denominator remains uninspected. The Masudpur VII Late Harappan table itself warns that only three samples were available. Its summer share also includes a large fruit component, so a seasonal percentage is not a millet percentage.

We preserved small source-table discrepancies. The four printed seasonal categories at Dabli vas Chugta total 99.72%, with the unassigned summary differing from its listed indeterminate legume entry. We have not silently normalized that row. The detailed extraction keeps blanks and the printed 1.659% mustard value in the Masudpur table. Neither is repaired into a preferred source value.

## How we checked the result

The protocol preceded our supplementary-table extraction but followed exposure to the focal paper's headlines. This run is an exploratory source audit. PyMuPDF extracted source columns; a separate pdfplumber route reread the numerical cells, and exact rational arithmetic checked the sums and differences. All 52 checks passed. Source tables S12 and S23 and the other seasonal-summary pages were visually inspected. The focal PDF was readable through the web tool, but its screenshot results supplied no pixels and its direct download failed; its figures have not received a local visual check.

Run-v1 is preserved with its code snapshot. Run-v2 changes the naming of the local detailed output so later reruns can use new output names. Its archaeological quantities match run-v1. These are same-contributor computational checks. Independent scholarly reproduction and review remain open.

## The independent study this makes possible

The [next-study design](NEXT-STUDY.md) tests which crop groups survived locally and how their occurrence and composition changed across settlement reorganization. It requires sample-level counts, recovery volumes, depositional contexts, local phase assignments and direct dating evidence. Comparisons will retain excavation dependence and use ecology-matched sites. The nine familiar phase summaries are discovery material; a new confirmation set must have its own exposure record.

The next acquisition is the Jognakhera supplement and its layer-to-phase mapping, followed by the existing comparison thesis's sample tables. A cross-site test must wait for comparable recovery and chronology. The [data update](DATA-UPDATE.md) records exactly what we added and what remains missing. No inscribed object gained a context or date through this work.

The strongest supported reading is that farming communities retained parts of the Harappan crop repertoire while changing their balance of crops. A dated sequence of comparable plant samples across local settlement transitions, with the same crop groups and management evidence recorded in every phase, would decide how much of the farming system itself persisted.
