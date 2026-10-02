# Object quality shared across slots

Written October 2, 2026, after completion and independent audit of the original calibration, imperfect-face, channel and component-bound studies. Their outcomes and paper 002's current draft have been read. This is a fresh synthetic study of an observed measurement-quality class held fixed for an object. No population or fitted outcome for this study has been generated when this protocol is written.

## Population and comparison

Generate twenty independent objects, ten at each of two sites. Each object supplies two ordered faces with three homologous slots and eight sign categories. Within a site, the first five objects have observed quality `low_error` and the next five `high_error`. These labels stay fixed on their objects. Latent slots are independent, with probabilities obtained by rotating [.20,.16,.14,.12,.11,.10,.09,.08] by `site + 2*slot`. They have the same distribution in both quality classes.

A face retains its latent sign with probability `1−ε`; otherwise it chooses uniformly among the other seven signs. Replacement rates are .025 for low-error and .60 for high-error objects. Conditional on latent signs and the supplied class, all face/slot replacement draws are independent. Sharing that class across the three slots gives a common measurement mechanism even though the latent slots are independent.

Compare two references on the same observed populations. Both move complete ordered two-face vectors separately at each slot, keep object aliases and all metadata fixed, and preserve broad site/type vector margins. `broad_vectors` moves them among all ten objects at a site. `quality_vectors` moves them among the five objects with the same site/type/quality label. The latter also preserves the quality-specific vector margins. The score's supplied fitting stratum remains `(site,type)` for both references; its preserved model does not read `quality`.

For quality q, an ordered vector has probability `r_q(a,b)=Σ_x p(x)K_q(a|x)K_q(b|x)`. Fixed q-specific vector counts make the product of these probabilities constant over compatible labeled tables, so quality-stratified vector permutations draw uniformly from that conditional space. Broad vector counts allow products to vary when vectors move between classes. The comparison measures a reference's handling of a specified observation mechanism. Its outcome concerns these generated records and this statistic.

## Statistic, support and endpoints

Use the four immutable nested-method snapshots and the frozen original wrapper. Rebuild physical/text components, five outer folds and three inner folds, and select smoothing over 5/20/100/500/2000 at fit seed 20261001. For a table with at least five components, use its unchanged held-out dependent-minus-selected-independent gain in bits per noninitial sign. Give every table with fewer than five components an explicit gain of zero, preserve its actual grouping and label it `guarded`. Abstain from rejecting when the observed table is guarded. Reference proposals are never rejected for fitting feasibility. An unexpected fit exception stops the run and preserves the partial trial.

The proposed main budget is 300 fresh populations, with 99 references per law. First run a two-population timing pilot with nine draws per law. Use elapsed time alone to confirm or reduce the main count in a separate budget note before main generation. The fitting statistic, generator, rates, comparison and thresholds remain fixed. Preserve every observed row, latent sign, replacement flag, quality label, proposal seed, grouping, selected model and score.

Compute `(1 + count(reference gain ≥ observed gain))/100` with inclusive ties. Report rejection at .01, .05 and .10 over all generated observations with abstentions counted as nonrejections. Also report the number of usable observations and rates conditional on usability, with that different denominator named. Report Wilson intervals across generated populations and a 20,000-draw paired population-bootstrap interval for broad-minus-quality rejection, seed 2026100210. Report observed/reference component ranges, guarded counts and how often broad proposals change the quality-specific margins. No result selects a preferred threshold or a revised measurement rate.

Main generator seeds are 60,261,002 + 1,009i. Main reference bases are sixty and eighty billion + 1,000,000i, followed by draw index. Pilot generator seeds are 70,261,002 + 1,009i, with reference bases one hundred and one hundred twenty billion + 1,000,000i. These namespaces are disjoint from the earlier main reference runs. Source and protocol hashes enter each endpoint.

## Independent and exact checks

Check all saved generation and replacement flags, fixed object/quality correspondence, each proposal through a separate vector-shuffle implementation, all metadata/margins, independent graph/fold calculations, p-value counts, abstention, aggregates and selected complete fit replays. Inspect the frozen model source and change quality labels on a supplied table to confirm that its fitting statistic ignores the field.

For a separate small sampler example, use four objects with two fixed quality labels each and a broad vector multiset containing two `(0,0)` and two `(0,1)` entries. Enumerate all six distinct columns with rational probabilities from the declared eight-category kernel. Enumerate the sixty-four three-slot tables with one of each vector in each quality class, checking their equal conditional masses. Retain 20,000 quality-stratified draws at seeds 140,000,000,000 + draw. This exact example verifies the table law without fitting the four-object nested statistic. Its broad conditional probabilities expose the extra quality constraint and the unequal weights.

Preserve timing pilots, failures and source snapshots in separate endpoints. The final report records prior outcome exposure, observations, fixes and a next test supported by the measured result.
