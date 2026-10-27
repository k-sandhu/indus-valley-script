# Readiness for comparing proposed readings

We will repair lexical input handling and identify the evidence required before different proposed readings can enter one prospective evaluation. This is a post-outcome methods and data audit. Earlier Sanskrit-key and rebus results remain frozen. We will not load a new Indus confirmation half or score a new reading.

The observed defect is in the Tamil frequency proxy: `tamil_prefix` removes final Tamil vowel marks and `prefix_count` accepts every token beginning with the remainder. The blind-template scorer also falls back from an unmatched romanisation to a length- and gemination-collapsed key. The Winslow retrospective records omitted compounds and an incorrect loanword split. These observations justify a repair; they do not specify the result of a repaired scientific test.

## Inputs and selection

We will inspect the existing Tamil Lexicon table, Sangam files and published identification list already used by the rebus studies. We will compare the original prefix counts with counts of complete Unicode-normalized written tokens for every distinct proposed word in the identification list. Every absent or ambiguous lexical lookup remains visible. Detailed dictionary and token outputs stay under `data/raw/2026-10-22-reading-eval-readiness/`; tracked outputs contain counts, hashes, source coordinates and our code.

Normalization is NFC plus trimming boundary whitespace. It preserves vowel length, consonant doubling and Tamil combining marks. Romanised lookup is case-insensitive; it does not identify different phonological forms. Multiple exact lexical records remain ambiguous until a reviewed entry is selected. The selection must name a stable entry identifier and evidence. Frequency of a written form can be reported across homographs, but is labelled as a form count and cannot select a meaning. Absence gives an unresolved lookup, not frequency zero. Prefix counts remain available only as a named historical diagnostic. This exact written-form count is not an inflection-aware lemma frequency.

We will verify Winslow examples against existing source pages and retain parser limitations as blockers if general repairs would require linguistic judgments. We will not add selected missing compounds to improve a particular result.

## Checks fixed before implementation

The lexical repair passes if tests show that it preserves vowel length and gemination, treats canonically equivalent Unicode as equal, rejects the prefix substitution, exposes homograph ambiguity, rejects an unreviewed alias, distinguishes missing input from zero attestations, and records every explicitly accepted alias. A deterministic local audit will preserve old and repaired counts with source hashes. It will make no new claim about the blind-template ratio.

Run `python -m bench key-calibration --synthetic`, `python -m bench meaning-map --synthetic`, and `python -m bench shots --synthetic` into this package. Their generated controls check the existing tasks and access guards. They do not validate real dictionary coverage or real population freshness. The participant contract must require an independently trained model or independently measured object outcomes, matched freedom, positive and negative controls, frozen predictions, all participants frozen before confirmation, and a reviewed exposure ledger.

## Prospective evaluation design

Phonetic keys, rebus readings and functional meaning maps answer different questions. They share a registration and evidence contract; each enters its appropriate scorer. A single numerical leaderboard would mix incompatible outcomes. Phonetic keys use likelihood and order tests with the existing default rule in `bench/key-calibration/README.md`. Meaning maps use the joint test and influence checks in `bench/meaning-map/README.md`. Rebus readings first need a source-adjudicated lexical and compound table, a declared matching law and a calibrated scorer; this audit cannot grant that missing task a pass.

All comparison families must declare the same choices available to a correct proposal and its wrong controls: sign coverage, option-list sizes, ignored signs, deleted output, sound mergers, lexical resources, morphological rules, direction alternatives, selected templates, tuning budget and number of attempted maps. A control retains the complete option list when assignments move. Tuning on discovery is repeated for each fitted null under the same budget. Any undeclared choice blocks registration.

The planning targets are at least 80% power at a prespecified minimally useful effect and a nominal false-positive rate no greater than 5% under the stated simulation law. These targets require a separate calibration campaign and interval-based precision plan before a real freeze; one generated example does not establish them. Real-family significance thresholds and multiplicity adjustments must be fixed jointly after the participant count is known and before confirmation opens.

The register supplies `LIPI:` object and surface identifiers, aliases, source assertions, ambiguity and exposure state. Physical identity remains provisional until reviewed. Known aliases, duplicate complete texts and other declared dependencies must remain in one evaluation component. Unknown exposure blocks a fresh claim. The data audit will record specific blockers, owners and acceptance evidence, with proposed updates to shared data records in this directory only.

Stop when the input repair, tests, blocker manifest and proposed participation contract are complete. No result from this package changes a reading's credence. The strongest possible conclusion is that a specified input defect has been repaired and the remaining prospective experiment can be described without hidden choices.
