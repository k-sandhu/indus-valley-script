# A common evaluation of proposed readings: the inputs we must repair

We have implemented exact lexical lookup and written-form counting, and identified ten gates before a prospective comparison of readings. The largest concrete defect is the old Tamil frequency proxy. For *kā* it counted 22,287 tokens beginning with the remaining initial letter; the same source stream contains 9 complete tokens of its written form. For *ā*, the corresponding counts are 4,458 and 24. These measurements use the same 162,399 Tamil tokens from 17 previously held Sangam HTML files, so they isolate the matching rule. They do not estimate the frequency of every inflected form of either lemma.

The [input audit](run-v1/input-audit.json) covers all 24 distinct proposed forms in the blind-template identification list, rather than selecting its successful cases. The Lexicon table contains 117,803 records. Eight queries have one exact one-member record, fifteen have several exact records, and one has none. Prefix and complete-form counts differ for 23 of the 24 queries.

| Query | Historical selected form | Historical prefix count | Complete tokens of that selected form | Exact lexical lookup |
|---|---|---:|---:|---|
| *kā* | *kā* | 22,287 | 9 | Seven records |
| *ā* | *ā* | 4,458 | 24 | Twelve records |
| *aṟu* | *aṟṟu* | 53 | 8 | No exact one-member record for *aṟu* |

The *aṟu* count belonged to another form because the old scorer fell back to an index that collapses vowel length and gemination. The new lookup returns an unresolved state. It will accept a variant only through an explicit adjudication naming an entry, reviewer, source evidence and relation.

Multiple dictionary records often represent homographs. A count of the shared written form can aggregate them without choosing a sense. A proposed meaning, an origin-based candidate filter or a historical attestation needs a reviewed lexeme and sense. Our result preserves every exact candidate and exposes the aggregate written-form counts; it does not select the first dictionary row. Zero complete-form matches means zero matches in this particular token stream. Inflections, sandhi and alternative spellings need their own reviewed inventory.

## What is implemented

[lexical_inputs.py](code/lexical_inputs.py) preserves Tamil vowel marks, vowel length and consonant doubling. NFC handles canonically equivalent Unicode; case folding applies only to romanised lookup. Missing inputs remain separate from observed zero counts. Stable entry hashes make an explicit sense or variant decision auditable. Ten generated counterexamples exercise these rules.

[preflight.py](code/preflight.py) checks a future participant manifest before a prospective read. It rejects missing, null, nonfinite, empty and unknown required declarations, changed or missing pinned files, unreviewed exposure, missing or overlapping controls, duplicate participant IDs, insufficient declared units, unfrozen participants and prior confirmation reads. Eleven tests exercise the gates. A rebus participant currently fails because the shared harness has no reviewed rebus task. The checker validates declarations and file integrity; independent review must establish their truth and equal freedom across participants. The shared shots loader remains the access mechanism.

An [independent count replay](verification-v2.json), implemented without importing the repaired counter or the historical counter, reproduces all 24 diagnostic counts and the token denominator. Source hashes match and all 21 focused tests pass. The old outputs and code are unchanged. We have not integrated the new features into a comparative scorer, recomputed the 1.81 rebus ratio, or examined a new Indus confirmation cohort.

## The remaining source work

The source stream still includes any Tamil front matter and editorial text in the original HTML. Its next version needs line-addressable poetry text and independently reviewed complete-form variants. This can begin from the seventeen files already held. Corpus extraction, lemma frequency and evidence for a particular meaning remain separate tasks.

The Winslow audit confirms two source forms with no recovered compound members: *murukkañcettal* on query page 501 and *murukkampū* on page 883. It also confirms that the parser produces *ja-mīṉ* for the headword *jamīṉ* on page 528, whose source gloss concerns land. The [local evidence manifest](run-v1/source-manifest.json) pins the pages and parsed table. We have left those records unchanged. A general repair needs a stratified, manually adjudicated sample of accepted and rejected compounds, including principals without etymologies, increments and loans. Adding these three selected cases would not measure the parser's coverage.

The current identification table draws on five later Parpola papers and covers sixteen signs. The full 1994 inventory and unresolved sign crosswalks remain a separate acquisition and source-review task. A specialist must adjudicate senses and historical attestations wherever the proposed interpretation or candidate selection depends on them. The full list of tasks, dependencies and acceptance evidence is in [BLOCKERS.json](BLOCKERS.json).

## How the common evaluation will work

The [participation contract](PARTICIPANT-CONTRACT.json) gives each proposal the same registration requirements while retaining the appropriate outcome for its family. Phonetic keys use independent language-model likelihood and sign-order tests. Meaning maps predict independently measured object variables. Rebus readings require a new calibrated scorer with source-adjudicated lexical inputs. Raw p-values from these different questions will not form one ranking.

For each comparison we must match sign coverage, option lists, omitted output, sound mergers, dictionary scope, morphological rules, direction and segmentation choices, and tuning budget. Whole alternative lists move together in key rearrangements. A fitted null repeats the proposal's discovery search. The final Sanskrit-key review supplies concrete reasons for these rules: unconstrained fitting could improve scores by deleting consonants, and projection and training choices changed separation from shuffled keys. Its [review response](../2026-10-12-published-claim-tests/sanskrit-key/review/RESPONSE.md) records the repairs that the next comparison must retain.

Each family needs a known-correct control and wrong controls under the same observation conditions. Our [key](key-synthetic-v1.json), [meaning-map](meaning-synthetic-v1.json) and [shots](shots-synthetic-v1.json) generated checks all pass. The meaning-map null rejected 2 of 30 runs, with a 95% interval of 1.85–21.32%; this smoke test is too small to certify an error rate. The proposed campaign therefore calls for 1,000 null runs and 300 runs per prespecified effect and law, with interval-based acceptance criteria fixed before that campaign starts. Real-data missingness and dependence must enter those laws.

The object register supplies provisional `LIPI:` object and surface identifiers, aliases, assertions and uncertainty. Its current `unreviewed` exposure state blocks a fresh claim. Before reserving a cohort, reviewers must establish physical identity and face assignment, build the separate text-dependence components and inspect the history of object and outcome-family use. Missing entries in `bench/spent.json` cannot prove freshness. Once the source and calibration gates are met, we register every participant, fix the joint testing rule and freeze every map, model and scoring artifact before the first confirmation read.

The boldest supported statement is that the earlier Tamil matching procedure cannot support a fair frequency-matched comparison in its present form: it pools thousands of unrelated initial matches and silently substitutes one lexical form. We now have a tested replacement for those input operations. The deciding next test is a newly versioned comparison with source-adjudicated features for both proposed readings and their controls, followed by one frozen evaluation on reviewed, unexamined object components.
