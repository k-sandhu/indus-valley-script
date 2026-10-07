# Protocol: foreign-find site census, batch D

Recorded 7 October 2026 before this package's web searches and aggregate calculations. The assignment is dated 6 October; acquisition dates use the actual session date.

## Question and inputs

Which published objects outside South Asia carry Indus inscriptions, which related objects use other scripts, and how much of their evidence appears in the local Lipi export? The required frame contains 23 named sites, supplemented by every label assigned to Mesopotamia, Persian Gulf, Iranian Plateau or Central Asia in `experiments/2026-10-06-research-program/local-site-coverage.json`. Girsu and Tello are combined as aliases; Tell Umma and Tell Jokha are resolved against Umma. Region labels and South Asian places assigned to these regions remain explicit cross-reference rows rather than being silently discarded.

Reuse the earlier `sites-and-publications` register, the local coverage file, the external phonetic-anchor audit, the Frenez lecture check and the original Oxus source-recovery records. Search the registry before revisiting a failed acquisition; a retry must name a new source or route. Preserve all earlier outputs.

## Method and selection

Run at least three distinct live searches per row: inscription/count literature, excavation/publication history, and geography or later finds. Open at least one primary or substantial secondary source relevant to each row. A shared regional publication can support several sites only when its inspected text names those sites. Save web-tool response witnesses, downloads, extraction text and query logs locally under the raw directory; source manifests, paraphrased findings and aggregates belong in the owned directory.

Record exact bibliographic metadata and page/figure/object locators when supplied. Mark snippets separately from opened text; an opened landing page does not constitute inspection of its linked book. Failed searches and downloads remain in the record. Use source identifiers consistently in every row. Each unresolved field points to the row's query IDs and describes the information that those searches did or did not recover. No quotation is needed; any later quotation is limited to one passage shorter than 15 words per source.

Distinguish imported canonical Indus seals, locally produced Indus-style seals with Indus signs, Gulf-type seals with Indus signs, inscribed pottery/graffiti, sealings, and related seals bearing cuneiform or Linear Elamite. Uninscribed Indus-style objects and uncertain single marks are comparison evidence, with their classification stated. Counts retain their date, source, unit and inclusion rule. Object counts, faces, impressions and texts are never summed together. Illustrations can establish a minimum documented specimen count but cannot establish a complete site inventory.

Record geography with a source and precision. Region labels have no archaeological-site coordinates. Do not infer holdings from the nationality of the excavation team. Record metadata availability as yes, partial or no for the inspected publication, with a locator. Unavailable publication content receives an explicit unresolved status and search record, not a fabricated assessment.

## Comparisons and negative outcomes

Copy the coordinator's local figures exactly. Combine alias-label counts only as sums of export rows, retaining constituent labels and warning that overlapping archaeological objects have not been deduplicated. Report local CISI prefix/maximum information as an identifier diagnostic. Test the near-contiguous-site-number premise against catalogues where readable; accession numbers, plate numbers and external catalogue numbers are not CISI site sequences.

A coverage fraction requires a published complete object inventory and a reviewed object join. Without both, report the two counts side by side and leave the fraction undefined. A later publication date alone does not establish a post-CISI discovery. Record later finds only when discovery season and catalogue cutoff can be supported; otherwise retain them as later-publication reconciliation targets.

A negative result is failure to locate an authenticated inscription, count, geographic identification or final-report witness after the specified searches. It is an acquisition result, not proof of archaeological absence. The census is Exploratory; reproducible local arithmetic may be Verified computation. Aggregate the number of rows, source-supported final-report identifications, firmly documented post-CISI finds and class-specific published minima without implying a total of all excavated objects.

## Checks and amendments

The build script must validate unique rows, mandatory fields, source references, three query IDs per row, an opened substantial-source association, exact local totals and JSON/CSV agreement. Run the repository prose checker without writes. A separate reviewer should repeat source samples and rerun the build. Record any change to these rules in a dated amendment before changing the endpoint; keep affected results exploratory.

### Amendment, 7 October 2026: CISI 3.3

A live search recovered the 2022 CISI 3.3 preface and contents through an author’s institutional repository. Add this volume to the comparison sources: the assignment’s four-volume list ends in 2019. Its contents authenticate Alt-90, TY-106 and Sh-69 as catalogue identifiers. Their large numbers cannot measure missing Indus inscriptions because these site sequences include other glyptic classes and graffiti. The preface places West Asia and the Gulf in a planned CISI 3.4 and says Gonur’s corpus was not supplied for 3.3. Do not describe a Gulf discovery as post-CISI coverage without establishing that coverage. This addition changes the catalogue comparison; all resulting assessments remain Exploratory.
