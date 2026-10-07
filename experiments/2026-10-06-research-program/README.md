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

## Status

| Package | Run | Review | Main result |
|---|---|---|---|
| A–H | Started 2026-10-07 03:56 UTC | Pending | Pending |
