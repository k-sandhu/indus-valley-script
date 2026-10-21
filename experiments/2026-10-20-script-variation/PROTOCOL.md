# Script variation across cities and source records

Recorded 20 October 2026 before computing the outcomes in this package. We use the repository's orient, add-data, start-study and test-conjecture workflows. Contributor: OpenAI Codex subagent `/root/script_variation`, GPT-6 family; the exact model identifier is not exposed to the agent. Harness: Codex desktop, functions/PowerShell/Python, shared-workspace multi-agent session. Verification tier: submitted.

We ask whether cities prefer different graphic forms while using the same inscription contexts. This distinguishes a shared format with local spellings from a corpus whose regional difference consists mainly of different objects, motifs or catalogue samples. We compare a common language with local scribal conventions, several languages using common written categories, and institutions using a standardized graphic code. These explanations can predict the same distribution of signs. This study measures the shared format and the local choices; a language identification requires an additional observation.

## Changed premise and existing exposure

The October 12 allograph study found that graphic groupings have related distributions. Adjacent Wells numbers can show a similar effect, especially for stroke counts. The earlier chronology and region study found excavation-frame confounding and asked for source-qualified records. We now hold the October 13 full CISI basic-data transcription and the joined Mackay and Marshall tables. They let us attach printed source locations and candidate identity conflicts to the analyzed objects. We do not repeat the earlier allograph-excess, regional divergence, chronology, spatial clustering or segmentation tests.

The entire Lipi corpus, graphic groupings and site distributions have been analyzed before. The October 12 site statistic family and the October 20 fish study are in the spending ledger. This run is exploratory even though its particular method is frozen before scoring. A new seed does not create unexamined objects. We copy `bench/spent.json` to a private package ledger, use the shots loader with explicit spent access and propose a merge of only this run's ledger entry.

## Inputs and source layer

Inputs are `data/normalized/lipi_observed_faces.jsonl`, `data/normalized/mayig_wells_class_crosswalk.json`, CISI 1 and CISI 2 basic-data JSONL in `data/raw/2026-10-13-cisi-basic-data-full/assembled/`, the corresponding `object-flags.csv`, and the October 13 excavation `join-table.csv`. Raw rows, accession values, complete texts and detailed model results remain under `data/raw/2026-10-20-script-variation/`. Code, our source notes, aggregate results and hashes are tracked. The source layer records the CISI volume and table pages, excavation-report source and table number, uncertain fields, unambiguous accession keys and candidate accession collisions. A collision is flagged and excluded in a sensitivity; it is not accepted as a same-object link without further evidence.

We use the October 12 inventory's usable-value rules for metadata. `None` as a motif records asserted absence. Zero dimensions and dash placeholders are missing. Chronological terms remain site-specific source labels; we infer no calendar date. Catalogue volume identifies a source block, not an independent transcription.

## Split and observations

One registered participant, `variant-choice`, uses seed `2026-10-20-script-variation`. We register and freeze every prediction, scoring code and graphic mapping before the first confirmation read. The shared shots loader forms physical-identity and repeated-text components from the full observed register before selection. Discovery fits the models. Confirmation supplies the scored objects. All successful reads remain in the bench access log.

Eligible faces are complete, clean right-to-left single-line records of at least three signs. A target code must have one definite Mayig compatibility class with at least two candidate Wells codes, and its integer Wells code must be at least 200. The exclusion of codes below 200 keeps the fish study and numeral families outside this target selection. Mayig classes describe graphic compatibility; they are not authenticated sound-equivalence classes. Surrounding codes without a mapping retain their Wells identity.

For the primary endpoint we select one eligible target position per component, using the smallest SHA-256 of `seed:component:record_id:position`. This gives every physical/text component one vote. A sensitivity takes one target per physical object and bootstraps text components. Neither the object number nor its order enters a predictor. Candidate code sets are fixed by the mapping; a scored target must belong to a class containing at least two codes observed at least three times each in discovery. The eligibility decision uses no confirmation outcomes.

## Variant prediction

The class prior has one pseudocount per candidate code. The baseline first conditions on class plus carrier, material, motif, preservation and catalogue volume, then on those fields plus length, target position and the graphic classes of the two neighbouring signs. Each distribution is shrunk toward the preceding distribution with a fixed total weight of 20. The site model follows the same hierarchy with site added at every level: class and site, recorded object fields and site, then the neighbouring context and site. Its first level is shrunk toward the common class prior. Missing neighbours have explicit edge labels. We compare the two final distributions by their mean difference in log base 2 probability on confirmation targets. A positive value means knowing the city helps predict which fine variant was written after the common graphic context and recorded objects are known.

The primary comparison includes catalogue volume in the non-site context. We report the same comparison without volume, within Mohenjo-daro versus all other cities, on seals only, on source-qualified CISI joins only, and after excluding candidate accession collisions. A separate source-block comparison adds catalogue volume within a site after the same context fields. These are prespecified diagnostics with no independent significance claims. An effect that depends on source volume cannot be assigned specifically to local speech or scribal convention.

The primary pass rule is at least 0.03 bits per target, a two-sided 95% component-bootstrap interval entirely above zero, at least 100 scored components and at least three sites with 15 scored components each. We use 4,999 bootstrap draws. A failed support threshold is reported as insufficient for this pass rule. The planned influence diagnostic removes each graphic family in turn; support for a general regional convention requires every leave-one-family-out gain to remain positive. No hyperparameter is tuned on confirmation.

## Exact-context test

We also group confirmation targets by their entire fine-code text with the target replaced by its graphic class, together with carrier, motif, preservation and catalogue volume. Within a group, every sign outside the target and the recorded object categories are identical. We report the number of groups containing at least two sites and two target codes, and the number of components they contain. The statistic is summed likelihood-ratio association between site and target code across these groups. We compare it with 4,999 permutations of site labels within the same groups, one target per component. A supporting result requires at least 30 components in at least five informative groups, p at most 0.05, and no group contributing over half the statistic. A secondary version uses the graphic classes of the surrounding signs; it tests a broader common frame and is labelled separately.

The source qualification and dependence rule can make these groups small. We preserve unsupported groups and their counts locally, and report the exact loss of support. We do not relax the primary matching rule after seeing it.

## Controls and interpretation

Generated controls use the same scorer with 1,200 discovery and 1,200 confirmation observations. In a local-spelling control, city changes the variant probability while all context fields stay fixed. In a context-confounding control, city changes only which motifs occur and motif changes variant probabilities. A null control has no city effect. A relabelled copy of the local-spelling control is explicitly interpreted once as one language with local orthography and once as two languages with common conventions. The observable inputs are identical, demonstrating that this statistic alone cannot choose those historical mechanisms. These are simulations, kept separate from actual-source outputs.

We report uncertainty over independent components and all prespecified diagnostics together. A positive regional variant score supports geographic conventions within the recorded sample. Strong exact-frame transfer across cities supports shared written slots. Neither assigns a sound, a word or a language family. We end the report with the strongest working model this evidence supports, a credence and an observation that would overturn it.

## Preservation and checks

Every output directory is new and scripts refuse existing output paths. We record input and code SHA-256 hashes, environment, commands, source/coverage additions, bench JSON and access logs, synthetic controls, a separate numerical check, a report and a retrospective. Corrections require an amendment and a new endpoint. We run the repository knowledge checks and prose scan on the owned package. Shared generated files, the website, Git history and the shared spending ledger are left unchanged.
