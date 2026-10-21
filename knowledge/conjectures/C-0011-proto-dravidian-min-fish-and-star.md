---
id: C-0011
title: "Proto-Dravidian mīn meant both fish and star"
status: strengthened
credence: 0.20
credence_history:
  - {date: 2026-10-21, value: 0.15, reason: "Starting estimate, recorded in the frozen protocol before any dictionary entry was read"}
  - {date: 2026-10-21, value: 0.35, reason: "Frozen rule: P1, P2 and P3 pass; parsimony places star absent at the root, which caps the pass at 0.35"}
  - {date: 2026-10-21, value: 0.20, reason: "Review: the homophone that the pun needs reaches the root at 0.41 and the North node at 0.22, and the northern star words may belong to viṇ 'sky'"}
risk: long-shot
area: meaning
authors: ["k-sandhu", "Claude Opus 5.5 (claude-opus-5-5), Claude Code desktop app", "Codex CLI 0.160.1, gpt-6.1-sol, mechanical acquisition and code"]
prior_proposals: ["Henry Heras 1953, Studies in Proto-Indo-Mediterranean Culture: the fish sign read as Dravidian mīn 'star'", "Yu. V. Knorozov and colleagues 1965 and the Helsinki group of Koskenniemi, Parpola, Parpola and Aalto 1969: fish = mīn 'star'", "Asko Parpola 1994, Deciphering the Indus Script; 2010, A Dravidian solution to the Indus script problem, pp. 15–28"]
builds_on: ["knowledge/directions/parpola-forward-2026-10-20.md", "FISH-CONTEXT-2026-10-20", "knowledge/conjectures/C-0008-fish-numerals-asterism-coverage.md"]
tests: ["experiments/2026-10-21-dravidian-root-meanings/REPORT.md", "experiments/2026-10-21-dravidian-root-meanings/results-v1/results.json"]
---

# Claim

Proto-Dravidian *mīn* meant both "fish" and "star". The ancestor of all Dravidian languages, spoken about 4,400 years ago, called a star "the shining one" with a word built on *miṉ* "to shine", and that word had the same form as *mīn* "fish", so a writer of the third millennium BCE could draw a fish to write "star". Parpola's astral reading of the Indus fish sign rests on this pun.

# Why it might be true

Tamil *mīṉ* means both fish and star in the oldest Tamil literature. In the *Dravidian Etymological Dictionary* the two senses belong to separate entries: 4885 gives *mīn* "fish" in thirteen of the twenty languages of the dated tree of Kolipakam and colleagues (*Royal Society Open Science* 5: 171504, 2018), and 4876, headed *miṉ* "flash, lightning", gives a star sense in Tamil, Malayalam, Kannada, Kota, Toda, Gondi, Kurukh and Malto. On that tree, whose root is 4,433 years old, the star sense reaches the root with a maximum-likelihood probability of 0.524 and the North Dravidian node with 0.681, and the meanings Parpola's readings need reach the root far more often than unproposed meanings from the same entries ([report](../../experiments/2026-10-21-dravidian-root-meanings/REPORT.md), [results](../../experiments/2026-10-21-dravidian-root-meanings/results-v1/results.json)). Kodava *boḷḷi mi·nï* "morning star", literally "white star", has the form of Parpola's *veḷ-mīn* "Venus", with a second member identical to Kodava *mi·nï* "fish".

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | "Star" reaches the root of the Dravidian tree | DEDR entry for *mīn* "star" coded on the 20 tips of the Kolipakam MCC tree | Mk1 maximum-likelihood root probability above 0.5 | With P2: 0.45 (0.35 if P3 fails or the parsimony root score is 0); without P2: 0.30 | passed, 0.524; parsimony places star absent at the root |
| P2 | Parpola's needed meanings reach the root more often than unproposed meanings from the same entries | 14 needed meanings with nonempty pools and 10,000 reference sets | Count above 0.5 exceeds the reference mean, one-sided p ≤ 0.05 | Joint with P1 as above | passed, 7 against a mean of 0.54, p = 0.0001 |
| P3 | "Star" is present at the North Dravidian node | Same coding | ML probability above 0.5 | Lowers a P1–P2 pass from 0.45 to 0.35 if it fails | passed, 0.681 |
| P4 | A lexical source independent of DEDR records a *mīn* form meaning "star" in a North or Central Dravidian language | Dictionaries and fieldwork published after 1984, the Merriam and Fuls Dravidian lexicon, new field elicitation | At least one attestation, form and gloss cited, not marked as a loan from South Dravidian or Indo-Aryan | Raise to at least 0.30 | prospective |
| P5 | Northern *b-* continues Proto-Dravidian *m-* before a long front vowel, so Kurukh *bīnkō* and Malto *bínḍke* "star" continue *mīn-k-* | Every DEDR entry with a Tamil initial *m-* or *v-* and a Kurukh or Malto reflex | At least two entries outside 4876 where northern *b-* answers Tamil *m-*; failure if northern *b-* answers only Tamil *v-* | Pass: raise to 0.30; failure: lower to 0.10 | prospective |

# Kill condition

The claim is dead if "star" is confined to South Dravidian, with no Central or North language coded for it, and its maximum-likelihood root probability is below 0.2. The frozen test did not meet it: two North languages carry the star sense in DEDR. Removing them, as a failure of P5 would, leaves the root probability at 0.34–0.47 because Gondi keeps the star word, so P5 alone cannot kill the claim; it would reduce it to a South Dravidian pun.

# Record

21 October 2026: registered at 0.15 before any dictionary entry was opened (protocol hash `07b40ad5…`, 01:49 UTC). The study [DRAVIDIAN-ROOT-MEANINGS-2026-10-21](../../experiments/2026-10-21-dravidian-root-meanings/REPORT.md) froze its code at 05:16 UTC and computed once. P1, P2 and P3 passed and the kill condition failed; parsimony places "star" absent at the root, so the frozen rule set the credence to 0.35. The posterior trees (mean 0.520, 89% above 0.5) and the two-rate model (0.51–0.53) agree with the primary estimate, which is close to the model's uninformative value. Review lowered the credence to 0.20: a star form homophonous with *mīn* reaches the root at 0.41 and the North node at 0.22, the fieldwork word lists of DravLex use a *mīn* form for "star" only in Tamil, and the Kurukh and Malto star words begin with *b-*, which in the coded entries answers Tamil *v-* (DEDR cross-refers entry 4876 to *viṇ* "sky"). P5 was added after the result to test that last point. An independent implementation reproduces every root probability. Verification tier: submitted.
