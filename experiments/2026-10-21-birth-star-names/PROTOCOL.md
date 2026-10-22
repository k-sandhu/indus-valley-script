# BIRTH-STAR-NAMES-2026-10-21: do fish compounds form a closed, evenly used class of names?

Recorded on 21 October 2026 (UTC) before any donor name was extracted from Lüders's list and before the discovery half of the new split was created or read. Author: Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app, for k-sandhu. Owned directory: `experiments/2026-10-21-birth-star-names/`; local derivatives in `data/raw/2026-10-21-birth-star-names/`. This is study 3 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md).

## Claim under test

The fish compounds on Indus seals are personal names given from the asterism the moon occupied at birth. Because the moon passes through every asterism once a sidereal month, such names form a closed set of about 27 or 28 members, used at nearly equal frequency. Ordinary name vocabularies are open and steeply skewed. A closed, flat class of fish compounds is therefore the signature the claim predicts, and an open, skewed class is the signature that would kill it.

## Prior exposure

The fish signs are among the most examined features of this corpus. The Bonta review of 8–9 October measured fish adjacency, NUMERAL-BEHAVIOUR-2026-10-12 measured stroke fixity, and FISH-CONTEXT-2026-10-20 learned a fish order and a stroke model on its discovery half and read its confirmation half on 21 October UTC (`bench/spent.json`, split `2dc777c1…`, spent families `fish_compound_order`, `fish_numeral_prediction`, `motif`, `object_type`, `seal_size`, `site`). Before writing this protocol we had read that study's aggregate report: fish variants combine in a fixed order, two strokes precede a fish in 77 of 102 reserved numeral events, the two-stroke prefix occurs on nine fish codes, and short strokes before the plain fish took the values three or six in 11 of 17 groups. We had also read the coding table of the fish family (24 codes of base B220 with modifiers `double`, `encl`, `dots`, `side`, `top`, `inner`, `bar`, `cap`, `hatch`) but no frequency of any fish compound. A new seed over these objects restores no freshness, so every Indus statistic in this package is exploration, and the frozen predictions are scored only on texts no analysis has used (see "Scoring material").

## Part 1. Calibration on a known naming system

**Source.** Heinrich Lüders, *A List of Brahmi Inscriptions from the Earliest Times to about A.D. 400 with the Exception of those of Asoka*, Appendix to *Epigraphia Indica* vol. 10 (Calcutta: Superintendent Government Printing, 1912). We use two independent archive.org scans, `acc.-no.-14283-epigraphia-indica-volume-x-1912` (Archaeological Survey of India library copy, marked public domain) and `in.ernet.dli.2015.49008` (Digital Library of India), with their OCR text. Lüders states in his preface that he quotes every proper name in the inscriptions and adds the Sanskrit equivalent of Prakrit names where he can.

**Donor names.** A donor occurrence is a personal name standing as the giver in a "gift of" clause of a numbered entry ("Gift of the nun (bhichhuni) Giriguta (Girigupta)"). The extractor takes the first capitalised name after "gift of", skipping lowercase role words and their parenthesised originals, and a second name joined by "and". It records no donor when the clause names a relative instead ("Gift of the mother of Namdigiri") or a collective ("the village of …"); those names go to a separate list of non-donor names. Honorific prefixes (Aya-, Arya-) are removed. The two scans are parsed separately and compared entry by entry; disagreements are resolved against the page image and logged. The primary unit is the donor occurrence. A sensitivity counts each name once per site heading, to limit the weight of donors who made many gifts at one monument.

**Marking.** [MARKING-RULE.md](MARKING-RULE.md) was written before extraction. Two markers apply it independently to the same list: marker A is a script that encodes the stem table; marker B is a separate agent that receives only the rule and the list. We report their agreement (Cohen's kappa on asterism versus not, and on the asterism label) and resolve disagreements in a logged third pass. The strict marking is primary.

**Name elements.** A name's element is its asterism label when it is marked, and otherwise its first member: the normalised name with honorifics removed, then one second member from the list in the marking rule removed, then one hypocoristic suffix removed when at least three letters remain. Full normalised names are a secondary unit.

**Statistics.** For asterism elements and for non-asterism elements separately: tokens N, distinct types S, the bias-corrected Chao1 estimate S + f1(f1 − 1)/(2(f2 + 1)) with f1 and f2 the numbers of types seen once and twice, the Shannon entropy H in nats, normalised entropy H/ln S, the share of the commonest type, the singleton share f1/S, and the Zipf slope, the least-squares slope of ln frequency on ln rank over all types. The share of donor occurrences formed from asterisms is reported with a Wilson 95% interval. Comparisons at matched size draw N tokens without replacement from the non-asterism elements 9,999 times and report where the asterism value falls. A discrimination curve repeats both classes at sample sizes 30, 60, 120, 240 and the full asterism N, so that we learn which statistics separate a known birth-star class from an open name vocabulary at the sample sizes the Indus test will have.

## Part 2. Exploration on the discovery half

**Split.** `python -m bench shots --action create` with seed `2026-10-21-birth-star-names` on `data/normalized/lipi_observed_faces.jsonl` (SHA-256 `1220f559…`), one registered shot named `birthstar`. Only `bench.shots.load_half(..., "discovery", "birthstar")` is called. The confirmation half is never read by this study.

**Population.** Seal faces (object type beginning `SEAL`) with `clean_rtl_singleline` true. Identical full texts within the half are collapsed to one representative after the loader's alias and identical-text closure, as in the fish-context study.

**Fish compounds.** The fish family is base B220 in `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv` (SHA-256 `c2d55fb5…`); stroke groups are bases B001 and B031. In reading order, a fish compound is a maximal run of consecutive fish-family signs together with the single stroke group immediately before the run, if there is one. Its type is the prefix code, or none, followed by the run's codes in order (unit T1). Two declared alternatives are reported: T3 treats each fish sign as its own unit, with a stroke prefix only for the first sign of a run, and T0 is the run without its prefix.

**Name position.** In the working model a seal legend is a name followed by a title from a small closing stock, so the last sign of a legend belongs to the title slot. A fish compound is in name position when at least one sign follows its last fish sign. Compounds that end a legend are reported separately and joined to the primary set in a sensitivity.

**Comparison vocabulary.** The opening vocabulary of the same legends consists of every sign that is neither a fish nor a stroke group and is followed by at least one sign, each with the stroke group immediately before it as a prefix when there is one. A declared alternative uses only the first unit of each legend, built by the same rule, excluding units headed by a fish.

**Statistics and predictions explored.** The statistics of Part 1 are computed for fish compounds and for the comparison vocabulary, and the comparison is drawn at the fish compounds' token count 9,999 times. We explore the three predictions of the direction note:

- N1. Chao1 of fish compounds in name position lies between 24 and 45, while the matched opening vocabulary keeps growing: its Chao1 exceeds 45 and its Good–Turing novelty f1/N exceeds that of fish compounds in at least 95% of draws.
- N2. Normalised entropy of fish compounds exceeds that of the matched opening vocabulary in at least 95% of draws and falls within the range measured for the Brāhmī asterism elements at the same token count.
- N3. One modifier contrast of the fish coding table applies to exactly three bases, a contrast applying to a base when both the base and the base with the modifier occur in name position at least twice, and the members of each of the three pairs occur at similar frequency (ratio between one third and three).

Exploration may refine the unit, the position rule and the thresholds after seeing discovery results, and every refinement is recorded with its reason in the package before freezing.

## Part 3. Freezing

`PREDICTIONS.json` holds each frozen prediction with statistic, null and pass rule, the statistic families and a joint credence rule. The scoring script, the frozen discovery inventory of fish compounds, this protocol and the marking rule are passed as `--artifact` to `python -m bench shots --action freeze`, and their SHA-256 hashes are recorded in `PREDICTIONS.sha256` and the freeze output. Power at plausible effect sizes is simulated before freezing from closed classes calibrated on the Brāhmī asterism names and open vocabularies calibrated on the discovery opening vocabulary.

## Scoring material

Predictions are scored only on texts that no analysis has used: the 244 CISI 3.1 numbers absent from the local corpus that lie between seals, tablets or sealings ([range coverage](../2026-10-13-cisi3-range-coverage/README.md)), the other absent CISI 3.1 and 3.2 numbers that turn out to be seals, and inscribed objects published after the catalogues ([Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md)). `SCORING.md` tells whoever acquires them how to transcribe, filter and score. The scorer refuses objects already in the pinned corpus.

## Deliverables

Source provenance and copyright notes, the extracted donor list (local), both markings and their agreement, calibration outputs, discovery outputs, frozen predictions with hashes and a bench freeze record, scoring instructions, a conjecture card, an attempt entry with status `frozen-prediction`, a retrospective and a data-update note for `knowledge/DATA.md`. The study changes one shared file through the bench workflow: `bench/spent.json` gains a ledger entry for the new split.
