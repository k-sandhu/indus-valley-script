# A browsable twenty-target object catalogue

We consolidated the agreed twenty targets, recovered fourteen crop-to-catalogue view links and separately reviewed the new image relations and the register's structure. The [local catalogue](../../data/raw/2026-10-26-object-pilot/integration-v2/catalogue-integrated-v2-polished.html) supports site filtering, identifier and metadata search, images, source links, retained disagreements and missing fields. Its [machine-readable projection](../../data/raw/2026-10-26-object-pilot/integration-v2/pilot-integrated-v2.json) and [missing-evidence queue](../../data/raw/2026-10-26-object-pilot/integration-v2/missing-evidence-integrated-v2.json) remain on D:.

Three gpt-6.1-sol workers ran the register, image and conflict tasks in parallel. A fourth gpt-6.1-sol contributor performed the separate review. The image worker then integrated the three outputs and prepared the local catalogue. The parent reviewed the returned prose and display, checked preservation and integrated the scoped inventory additions.

## What changed

The frame contains ten Dholavira accession targets, five Harappa catalogue targets and five Lothal catalogue targets. It preserves 539 inherited source assertions and adds two integration summaries of the identity conflicts, for 541 displayed assertions. The Dholavira targets retain all 62 candidate corpus families and 274 candidate relationships. No physical identity is merged. The [register report](../2026-10-26-object-pilot-register/REPORT.md) and [coverage table](../2026-10-26-object-pilot-register/coverage-v4.json) give the field definitions and denominator of twenty.

Fifteen targets have material assertions, sixteen have some dimensions, fourteen have findspot assertions and fifteen have stratum or phase assertions. These counts include retained qualifications and disagreements. Seventeen targets have local images or illustrated-page files; H-1657 has an additional web photograph pointer. H-2587 and H-1688 have held drawing pages. Narrative pages for H-1682 and H-1692 are not counted as images. Complete all-face coverage remains unestablished.

The [image pass](../2026-10-26-image-recovery/REPORT-v2.md) adds fourteen asset-to-catalogue view links against the 13 October image-files.csv table. They involve thirteen held assets and twelve catalogue keys. The shared crop named for L-164 and L-165 also contains captioned L-163 A and C. Those L-163 photographs were already held in source-page records; the gain is their explicit crop-index link. This pass establishes zero newly available pilot photographs. L-163 and L-207 become newly indexed keys in that particular table; earlier photograph availability for L-207 was not comprehensively audited.

The image census distinguishes the application map from the fuller research index. Of 2,152 filenames missing from the application map, 2,084 already had research-index assignments. Of 284 anonymous filenames, 229 were already assigned. Among twenty-one inspected unresolved anonymous crops, twelve received verified catalogue-view links, eight show headings, margins or scan traces, and one remains a candidate. Thirty-four unresolved anonymous crops remain uninspected. Three additional pilot assets brought the inspection to twenty-four assets and twenty source pages.

Both [source conflicts](../2026-10-26-source-conflicts/REPORT.md) remain unresolved. Rao assigns CLXI F to 1864 in one passage and 1830 in another; CISI identifies these as different catalogue objects. We retain the disputed plate as a candidate page and block transfer of its disputed context to L-164. H-2587 retains the 7158 and 7458 registration alternatives. The 2010 source directly supplies its steatite material and maximum diameter of 15.29 mm, while its registration remains disputed. L-174's held catalogue row supplies its identifiers and preserves an unknown museum cell and conflicting impression counts.

## Review and inventory

The [separate review](../2026-10-26-object-pilot-review/REVIEW.md) checked all fourteen new image relations against crop pixels, original plate pages and the prior index. It also checked the selected new Harappa and Lothal source claims. The register review has thirteen passing checks and 209 hash bindings; the integration review has eleven passing checks and 96 bindings. Those 305 bindings include repeated references to the same files. The review structurally checks the inherited assertions; it does not retranscribe every historical cell from its primary source.

The final projection differs from reviewed integration v1 only in review metadata. All twenty object records and their assertion values remain unchanged. The final HTML uses readable field labels and collapsed source details. Browser checks confirmed the twenty-card view, a five-card Lothal filter, a one-card L-163 search, image navigation and readable desktop and narrow-screen layouts. The temporary preview served only an explicit local asset list on 127.0.0.1 and was stopped after inspection.

We added three scoped output entries to [data/MANIFEST.json](../../data/MANIFEST.json), preserving its 104 earlier entries, and added the subset account to [knowledge/DATA.md](../../knowledge/DATA.md). The manifest now lists 107 sources. Historical global object and metadata coverage counts were not recomputed or replaced. [Inventory integration](inventory-integration-v1.json), [preservation and storage checks](final-audit-v1.json).

## Next evidence, in priority order

1. Obtain a source-qualified Dholavira accession-to-CISI concordance or registered matching photographs, starting with the four leading dimensional candidates PCF-DHV-010 through PCF-DHV-013. This can decide identities before candidate-family metadata is attached to a target.
2. Locate the ASI original negative register for Lothal CLXI F and labelled cards for 1864 and 1830. This decides which object owns the photograph and its reported context.
3. Locate the HARP original object cards and database records for the disputed 1996 lots, together with the drawing and photo registration history for H-2587. The manuscript identifies the underlying object and photo databases but does not supply their records.
4. Recover the field sequence and phase evidence for Harappa lots 3166 and 8796. This can turn published phase assignments into chronology supported by the excavation relations.
5. Continue the remaining thirty-four anonymous crops with the same plate-and-index checks. The narrow M-1202 F fragment remains a separate candidate requiring a clearer distinguishing view.

The strongest supported conclusion is that held photographs and excavation records can now be inspected together at the target level, with verified image relations and unresolved identity claims kept explicit. Registered accession and photograph records would decide the remaining bridges and make the catalogue suitable for stronger object-use and chronology tests.
