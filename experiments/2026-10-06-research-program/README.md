# October 6 research program: work packages, models and review

On 6 October 2026 the user asked for a broader program: stronger machine-learning models for the Paper 001 restoration benchmark, a fuller census of where Indus evidence is indexed and with what metadata, an inventory of project results outside decipherment, the research directions proposed by Dennys Frenez in a recorded lecture (https://youtu.be/1i9q17ld_jU) and by other leading researchers, a backward chronology from later South Asian scripts, and new analyses of the Indus civilization beyond the script. The coordinating Claude session planned ten packages and ran them in parallel through the Codex CLI. GPT-6.1-Sol handled packages that need analysis and judgment; GPT-6-Luna handled long reading and search. Claude Sonnet 5.5 reviews each package after it finishes.

## Packages

| Package | Owned directory | Model and effort | Question |
|---|---|---|---|
| A | `experiments/2026-10-06-modern-restoration/` | GPT-6.1-Sol, xhigh | Do Kneser–Ney n-grams, recurrent and transformer models, metadata conditioning or extra out-of-population text improve the saved known-slot restoration benchmark, and is the task data-limited? |
| B1 | `experiments/2026-10-06-evidence-census/sites-and-publications/` | GPT-6-Luna, high | Which sites and publications report inscribed Indus objects, how many, and with which metadata? |
| B2 | `experiments/2026-10-06-evidence-census/collections-and-datasets/` | GPT-6-Luna, high | Which museums, datasets and image archives index the objects, with which fields and licences? |
| C | `experiments/2026-10-06-byproduct-inventory/` | GPT-6-Luna, high | Which project results outside decipherment could be published in their own fields? |
| D1 | `experiments/2026-10-06-chronology-region/` | GPT-6.1-Sol, xhigh | Does sign usage change across Harappa periods and regions, and are inscriptions found outside the Indus region statistically distinct? |
| D2 | `experiments/2026-10-06-sign-context-and-seals/` | GPT-6.1-Sol, xhigh | Does sign 740's frequency follow site size, site type or object type; can the "unbalanced oligopoly" description be tested; are seal sizes standardized? |
| E | `experiments/2026-10-06-backward-chronology/` | GPT-6.1-Sol, xhigh | What dated marked or inscribed material links the Indus phases to early historic scripts, where are the gaps, and how can transmission be tested? |
| F | `experiments/2026-10-06-field-recommendations/` | GPT-6-Luna, high | What do leading researchers recommend, and which recommendations can this project act on? |
| G | `experiments/2026-10-06-weight-metrology/` | GPT-6.1-Sol, xhigh | How precisely do Indus weights realize a common unit across sites and contexts, and where do Indus-standard weights occur in the west? |
| H | `experiments/2026-10-06-resemblance-baseline/` | GPT-6.1-Sol, high | How often would an unrelated sign inventory "match" the Indus list under a declared shape rule, compared with the reported Tamil Nadu graffiti parallels? |

A later synthesis package joins B1 and B2 with the October 2 dataset landscape.

## How the packages ran

Every package received the shared instructions in [COMMON.md](COMMON.md) followed by its own prompt in [prompts/](prompts/). The shared instructions carry the repository's evidence, rights and writing rules, require a protocol before outcomes, and restrict each package to its owned directory and a matching local raw directory under `data/raw/`. [launch.sh](launch.sh) runs one package with `codex exec` in the `workspace-write` sandbox, rooted at the owned directory, with network access and live web search. Writes outside the owned and raw directories are refused by the sandbox; a test write to the user's home directory was denied before launch. Package A also had write access to a separate PyTorch environment at `C:\Users\sandh\.venvs\indus-ml` (PyTorch 2.14.1 with CUDA 12.6, RTX 4070).

Before launch the coordinator saved the uncommitted October 2 dataset-landscape directory, the modified registry and the Git status to the session scratchpad. Packages propose registry entries in their own directories; the coordinator integrates them into shared files after review.

At the user's request, the coordinator commits and pushes the work at milestones on the branch `research/2026-10-06-program`, leaving `main` unchanged: once at the start, again as each package finishes, and after each review and integration. Commits made while a package is still running are labelled in-progress snapshots. Each commit is preceded by a check that only code, protocols, reports and aggregate outputs are staged; third-party payloads stay in the ignored `data/raw/` directories. No timer or recurring automation is used.

## Review

A Sonnet 5.5 reviewer reads each finished package, reruns its scripts or verification where feasible, checks reported numbers against the saved outputs, samples cited sources, and checks scope and wording against the repository rules. Each review is saved as `REVIEW.md` in the package directory. Packages and reviews are summarized below as they finish.

## Additional passes

The coordinator read Frenez's lecture captions after package F could not obtain a transcript; [frenez-talk-check.md](frenez-talk-check.md) confirms the user's summary at each timestamp and lists further testable statements. Follow-up instructions in [prompts/followups/](prompts/followups/) send those statements to packages D1, D2 and E when their first passes finish, using [resume.sh](resume.sh) to continue each Codex session in the same sandbox.

The first census passes were thin: B1 left nearly every metadata field unassessed and found object counts for four sites, and B2 captured one direct catalogue count. B2 was resumed with named museum APIs and search routes. B1 was split into four regional batches with a per-site checklist ([B1-deep-base.md](prompts/B1-deep-base.md)): Pakistan and Afghanistan, Gujarat with Kutch and Maharashtra, and north India on GPT-6-Luna, and finds outside South Asia on GPT-6.1-Sol. The coordinator's [local-site-coverage.json](local-site-coverage.json) gives each batch the local corpus figures per site, including distinct CISI identifiers against the highest CISI number recorded; Dholavira, for example, has 238 local faces of which 2 carry CISI identifiers.

## Hosted data

On 7 October 2026 the local disk was nearly full. At the user's request, [hf_host.py](hf_host.py) moved package A's predictions and frozen model (1,034 files, 3.09 GB, project-generated) to the private Hugging Face dataset `ksaw008/indus-research-data`, verified all files against the Hub, and then removed the local copies; [hf-hosting-manifest.json](hf-hosting-manifest.json) records every path and checksum, and `hf_host.py restore` brings them back. Third-party payloads stay local because their reuse rights are unresolved.

## Status

All packages finished, were reviewed by Claude Sonnet 5.5 and had their required fixes applied in the same Codex session. Results are Exploratory unless a package states otherwise. The answers to the user's questions are collected in [REPORT.md](REPORT.md); the shared registry entries were added by [integrate_registry.py](integrate_registry.py).

| Package | Final model | Review | Main result after review |
|---|---|---|---|
| A, restoration models | GPT-6.1-Sol | [REVIEW.md](../2026-10-06-modern-restoration/REVIEW.md) | Kneser–Ney and GRU ensemble 41.17% top-one against 34.59% and 37.27%; short-text links touch 9.3% of queries |
| B1–B3, evidence census | GPT-6.1-Sol (B1 batches and B2 began on GPT-6-Luna) | [REVIEW.md](../2026-10-06-evidence-census/synthesis/REVIEW.md) | No complete index; 166 of 493 inspected CISI 1 identifiers absent locally; at least 68 of 114 museum records joined |
| C, results outside decipherment | GPT-6.1-Sol (began on GPT-6-Luna) | [REVIEW.md](../2026-10-06-byproduct-inventory/REVIEW.md) | 25 assessed candidates; chart annotation, context completeness, CISI scan notice, numerical premises and catalogue joins ranked first |
| D1, chronology and region | GPT-6.1-Sol | [REVIEW.md](../2026-10-06-chronology-region/REVIEW.md) | Media diversity rises in Period 3C across excavation frames; the length increase does not survive restriction |
| D2, sign context and seals | GPT-6.1-Sol | [REVIEW.md](../2026-10-06-sign-context-and-seals/REVIEW.md) | Sign 740 at 10.0–10.7% and 69.6% final; site inventories follow sample size; no motif change between unambiguous 3B and 3C labels |
| E, backward chronology | GPT-6.1-Sol | [REVIEW.md](../2026-10-06-backward-chronology/REVIEW.md) | 65 dated rows; no empty century in the broad record; no dated transmission chain |
| F, researchers' recommendations | GPT-6.1-Sol (began on GPT-6-Luna) | [REVIEW-2.md](../2026-10-06-field-recommendations/REVIEW-2.md) | 56 recommendations from 27 opened sources |
| G, weight metrology | GPT-6.1-Sol | [REVIEW.md](../2026-10-06-weight-metrology/REVIEW.md) | Dholavira 5–100 g weights fit 13.716 g; no western Indus-standard signal against a chance control |
| H, resemblance baseline | GPT-6.1-Sol | [REVIEW.md](../2026-10-06-resemblance-baseline/REVIEW.md) | Coarse matches: Indus subset 30/42, Ogham 24/42, Tifinagh 31/42; coder agreement 46% |
| L, pilot object ledger (7 October) | GPT-6.1-Sol | [REVIEW.md](../2026-10-07-object-ledger/REVIEW.md) | 200 records across 34 sites; 26 confirmed museum joins; a second hash-ordered selection adds 44 Lower Indus and 10 Kalibangan carriers; validator catches 26/26 review mutations |
| M, 1979 Helsinki digitization (7 October) | GPT-6.1-Sol; blind readers and adjudicator Claude Sonnet 5.5 | [REVIEW.md](../2026-10-07-helsinki1979-digitization/REVIEW.md) | Both frozen evaluations fail; the repaired pipeline reads 62/80 numbers and 40/80 whole rows within top five, with row cropping the limiting stage; all occurrences quarantined |
| M, v3 crop rebuild (8 October) | GPT-6.1-Sol; blind readers and adjudicator Claude Sonnet 5.5 | [REVIEW-V3.md](../2026-10-07-helsinki1979-digitization/REVIEW-V3.md) | Fresh 80 rows: crops 71, numbers 71, counts 72, top-five 62; four criteria fail by 1, 1, 4 and 2 rows; random-page recall 1,289/1,289; all occurrences quarantined |
| N, row verification (8 October) | GPT-6.1-Sol; readers and adjudicators Claude Sonnet 5.5 | [PILOT-RESULTS.md](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md), [PILOT-2-RESULTS.md](../2026-10-08-helsinki1979-row-verification/pilot-2/2026-10-08-v1/PILOT-2-RESULTS.md) | Two pilots, 360 rows; agreement 85.6% then 91.7%; every control correct on number, classification and count after adjudication; full run about 340 million tokens; not started |
| P, chart reference audit (8 October) | GPT-6.1-Sol | [REVIEW.md](../2026-10-08-chart-reference-audit/REVIEW.md) | Eight chart codes and two classes corrected (chart v2.1); a blind second reading of 63 cells agrees |
| O, public dataset candidate (8 October) | GPT-6.1-Sol | [REVIEW.md](../2026-10-08-hf-public-release/REVIEW.md), [REVIEW-0.3.0.md](../2026-10-08-hf-public-release/REVIEW-0.3.0.md) | Release 0.3.1 in a private Hub preview: 23 configurations, 3,308 rows; all three benchmark scores reproduce; public release awaits the owner |

The coordinator's own checks are [frenez-talk-check.md](frenez-talk-check.md), [local-site-coverage.json](local-site-coverage.json) and the two title-trimming scripts, which replaced copied search-result text in census source titles and kept the originals in local-only files.
