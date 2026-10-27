# Indus Valley script research knowledge base

The Indus script is the writing of the Indus, or Harappan, civilisation, which flourished from about 2600 to 1900 BCE in what is now Pakistan and northwest India. The largest database lists about 4,700 inscribed objects. Nearly half are small carved stamp seals; most of the rest are small tablets, marked pottery and clay tags. The texts are very short, usually three or four signs, and use roughly 400 to 700 different signs depending on how variants are counted. The script has never been deciphered. No bilingual text has been found, and the language it records is unknown.

This project gathers what can be sourced about every inscribed object and tests ideas about the script with statistics. Most of the work is done by AI agents, and we are using the project to find out whether many agents working from shared evidence can make real progress on a problem this hard. We count as progress only results that someone else can check: new facts about the objects tied to their sources, patterns that hold on inscriptions the analysis did not see, and proposed readings that do better than shuffled versions of themselves. Every attempt is kept on record, including the ones that failed, so the next person or agent starts from what is already known.

## Where things stand

Most results below come from held-out tests: we fit a model on some of the inscriptions, score it on the rest, and compare the score with what chance would give. Each link opens a card with the exact numbers, the objects counted and the chance comparison used. A p-value says how often chance alone would produce a result at least this strong.

- No two of the 445 seals with six or more signs carry the same full text. [Finding](knowledge/findings/F-0027-long-seal-texts-do-not-repeat.md)
- A sealing is the impression a seal leaves in clay, for example on a closed container. Of 16 sealings or tags whose text matches a known seal, 13 match only seals found at other sites. [Finding](knowledge/findings/F-0030-sealings-match-seals-from-other-cities.md)
- Line breaks fall between recurring units. On 69 seals where the catalogue shows how the text was split across lines, the text of each line recurs elsewhere more often than a stretch of the same length that crosses the break: 23 seals favour the lines, 4 favour the crossing stretches and 42 tie (p = 0.0003). [Finding](knowledge/findings/F-0018-lines-recur-more-than-crossing-windows.md)
- Signs follow each other predictably. On 1,596 distinct complete texts, a model that knows the previous sign gives the correct next sign, on average, about 1.8 times the probability given by a model that knows only the sign's position and the object's site and type (a gain of 0.848 bits per sign). [Finding](knowledge/findings/F-0001-sequential-prediction-on-unique-texts.md)
- When we hide one sign in an intact text and ask a model to fill the gap, a model that uses two signs of context gets it exactly right in 37.3% of 8,009 trials, against 34.6% for a model that uses one. [Finding](knowledge/findings/F-0002-second-order-known-slot-restoration.md)
- Grouping sign variants that share a base shape improves prediction by 0.022 bits per sign, more than random groups of the same sizes do (p = 0.005). [Finding](knowledge/findings/F-0010-graphic-base-families-improve-prediction.md)
- Groups of short strokes look like numbers. Before a given sign they take 3.61 different values on average, fewer than real counts take in samples of the same size from Mesopotamian accounts of about 2100–2000 BCE (4.53 to 5.15). The stroke values are tied to the sign that follows them more tightly than counted quantities are. [Finding](knowledge/findings/F-0024-stroke-values-are-tied-to-following-items.md)
- The digital corpus we work from is incomplete. Of 493 numbers in 19 sections of volume 1 of the *Corpus of Indus Seals and Inscriptions* (CISI), the main printed catalogue, 166 have no matching entry. Some of these are the same objects under other numbers; others are objects missing from the corpus. [Finding](knowledge/findings/F-0007-catalogue-identifiers-missing-from-export.md)
- Of 114 original museum records we inspected, 68 could be linked with confidence to objects in the corpus. [Finding](knowledge/findings/F-0008-museum-joins-are-a-lower-bound.md)
- Some methods fail. Our estimate of how many signs are lost in a damaged gap was right 46.3% of the time, worse than always guessing one sign (51.1%). [Finding](knowledge/findings/F-0005-gap-count-estimator-loses-to-constant-one.md)

No sign yet has an established sound or meaning, and the language of the script is still unknown.

## What we currently think

We write our ideas as plain claims, each with a credence (our probability that it is right), predictions that could fail and a kill condition, the result that would make us drop it. The [working model](knowledge/WORKING-MODEL.md) puts them together into one account. Its central claim is that the script did three different jobs: seals carry identity legends, Harappa's tablets are standard tokens made in series, and marks on pottery label contents or owners (credence 0.6). A seal legend, on this account, is a name followed by a title (0.45), and the short legends that recur on seals in many cities are the titles of offices (0.55). Each claim under test has its own [conjecture card](knowledge/conjectures/).

We test a claim in two stages. First we explore freely on one half of the inscriptions. Then we freeze a single prediction and check it once against the other half. The first two tests ran on 12 and 13 October 2026:

- A working reading that gave roles such as name, household or office to the 118 commonest signs did no better than shuffled versions of itself at predicting where seals were found or how large they were. [Report](experiments/2026-10-12-conjecture-shots/shot-b-reading/REPORT.md)
- Seals whose legend ends in one of four signs were predicted to be larger than comparable seals, and they were (p = 0.021). An independent review found that three very large seals ending in sign 820 carry most of the result, so we hold the idea at a credence of 0.15. [Report](experiments/2026-10-12-conjecture-shots/shot-a-rank/REPORT.md), [review and response](experiments/2026-10-12-conjecture-shots/REVIEW-RESPONSE.md)
- A check of the published photographs found that ten clay sealings from Lothal, in Gujarat, carry the same four-sign legend as the seal M-895 from Mohenjo-daro, but were stamped by a different seal. [Plate check](experiments/2026-10-13-plate-checks/README.md)

## Start exploring

The [project website](https://k-sandhu.github.io/indus-valley-script/) presents the findings, open questions and working model as web pages. The [sign catalogue](experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html) shows signs with example inscriptions and the meanings proposed for them, each with its evidence. The [chart atlas](output/chart_atlas/index.html) shows the 687 sign drawings and numbers in Koskenniemi and Parpola's 1979 *Corpus of Texts in the Indus Script*, each linked to its page and marked where the reading of the chart is uncertain. The [repository map](knowledge/MAP.md) lists every finding, question, attempt, paper and retrospective.

| Manuscript draft | Question |
|---|---|
| [001](papers/001-artifact-aware-prediction/manuscript.md) | How well can a model predict the next sign or restore a missing one, when copies of the same inscription are kept apart? |
| [002](papers/002-conditional-reference-laws/manuscript.md) | How do statistical tests go wrong when one inscription is counted several times? |
| [003](papers/003-physical-observations/manuscript.md) | What physical evidence would a numerical reading need? Tested against Inca khipu records |
| [004](papers/004-reference-model-selection/manuscript.md) | How should a model of the records be chosen before matching signs to another system? Tested on simulated scripts |
| [005](papers/005-settlement-survey-gaps/manuscript.md) | Why have so few Indus sites been excavated, and how could surveys find hidden settlements? |
| [006](papers/006-sanskrit-key-calibration/manuscript.md) | Does a published Sanskrit decipherment do better than shuffled versions of its own key? |

PDFs of the [original research report](output/pdf/indus_script_research_report.pdf) and the [settlement paper](output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf) are also available.

## Data

On this workstation, bulk local inputs live at `D:\projects\indus_valley_script`. Existing checkout paths reach them through junctions and file links. Read [LOCAL_STORAGE.md](LOCAL_STORAGE.md) before acquiring or restoring inputs.

Our first priority is a complete record of every inscribed object: all of its catalogue numbers, every face and photograph, its size and material, where and in which layer it was found, its date, its museum number and where it has been published. [DATA.md](knowledge/DATA.md) lists what we hold, what exists elsewhere and what is still missing.

Much of the source material belongs to others. A copy of this repository contains our text, code, protocols, summary results and pointers to the sources, together with some third-party material we are allowed to share. The digital corpora, most photographs and the downloaded publications have to be obtained separately under their own terms. [REPRODUCING.md](REPRODUCING.md) explains how to obtain them and rerun a study, and the [rights records](knowledge/provenance/REDISTRIBUTION.md) say what can be shared.

To download only the documents and tools, without the experiment outputs:

```text
git clone --filter=blob:none --sparse https://github.com/k-sandhu/indus-valley-script.git
cd indus-valley-script
git sparse-checkout set knowledge papers tools templates
```

Add the experiment directories and their inputs later if you want to inspect outputs or rerun a study.

## Contribute

You can [open an issue](https://github.com/k-sandhu/indus-valley-script/issues/new/choose), take up one of the [open questions](knowledge/questions/) or check a recorded result yourself. Corrections to the data and metadata help most. [CONTRIBUTING.md](CONTRIBUTING.md) explains how to claim a question, which files you own, how work is reviewed and what to check before a pull request. Discussion takes place in [GitHub Discussions](https://github.com/k-sandhu/indus-valley-script/discussions).

For agents: Clone https://github.com/k-sandhu/indus-valley-script, read AGENTS.md and follow it.

## Repository layout

| Directory | Contents |
|---|---|
| `knowledge/` | Findings, open questions, conjectures, the working model, the data page and the record of every attempt |
| `experiments/` | One dated folder per study, with its plan, outputs, review and retrospective |
| `papers/` | Manuscript drafts with their methods and the evidence behind each claim |
| `output/` | Reports, the chart atlas and summaries |
| `src/` | Analysis code |
| `bench/` | The shared harness that scores proposed readings and keys |
| `tools/` | Scripts for the knowledge base, checks and the website, all run by hand |
| `data/` | Records of where each input came from; the large inputs are kept out of Git |
| `templates/` | Templates for experiments, findings, questions and source reviews |
| `research/`, `results/`, `archive/` | Earlier plans, outputs and documentation, kept unchanged |
| `.claude/skills/` | Short task guides for agents, linked from AGENTS.md |
| `.github/ISSUE_TEMPLATE/` | Forms for claiming questions and reporting data or result errors |

## Reuse and licence

Code written for the project is released under the [Unlicense](LICENSES/Unlicense.txt), and our text, data, cards and documentation under [CC0 1.0](LICENSES/CC0-1.0.txt), so both can be reused without asking. Material derived from the 1979 Helsinki edition of the Indus texts is under [CC BY 4.0](LICENSES/CC-BY-4.0.txt) and needs its attribution ([LICENSE](LICENSE)). Third-party material keeps its own terms. Contributions are accepted under the same terms. [REUSE.md](REUSE.md), the [third-party notices](THIRD_PARTY_NOTICES.md) and the [asset review](experiments/2026-10-11-public-release/ASSET-REVIEW.md) give the details. The manuscripts are drafts written with AI assistance and have not been peer reviewed.

## History

The [research timeline](knowledge/TIMELINE.md) keeps the summaries and links from the earlier README. The [knowledge index](knowledge/INDEX.md) and the [retrospectives](knowledge/retrospectives/README.md) record results, failures and repairs in detail.
