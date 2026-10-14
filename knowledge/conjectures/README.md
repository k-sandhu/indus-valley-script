# Conjectures

This directory holds our own claims about what the Indus inscriptions are and what they say, stated at full strength. The evidence record elsewhere in the repository reports what has been measured; this directory states what we currently think is true and how we would find out that it is wrong. Working readings and meanings of signs belong here.

Each conjecture is one file, `C-NNNN-short-name.md`, copied from [TEMPLATE.md](TEMPLATE.md). The claim is written plainly, as if true, with no qualifying phrases. Its uncertainty is carried by the single `credence` number, the author's probability that the claim holds as stated, and by the predictions that would move that number.

A conjecture needs predictions that could fail, each with a pass rule, and a kill condition, the outcome that would make it dead. Earlier proposals of the same idea are listed in `prior_proposals`; a conjecture can be valuable without being new. When a test runs, its outcome and the revised credence are added to the card's record. A conjecture becomes a finding in the evidence record only when predictions frozen before the data were examined pass on that data, or when a prospective prediction about new material comes true. Dead conjectures stay in the directory with their record, so later contributors can see what failed and why.

Tests follow the two-stage design of [the conjecture shots](../../experiments/2026-10-12-conjecture-shots/DESIGN.md). The corpus is split into two halves. A shot explores the discovery half without restriction, then freezes its predictions and tests them once on the confirmation half. The first two shots led to [seven further rules](../../experiments/2026-10-12-conjecture-shots/REVIEW-RESPONSE.md#rules-for-the-next-shots):

- All shots that share a confirmation half freeze their predictions before any of them reads it.
- Predictions that share objects carry a joint rule for changing the credence.
- Pass rules for small groups include an influence criterion: a rank statistic or a leave-one-out condition.
- Power is stated for effects of plausible size, not only for large ones.
- Site tests exclude Mohenjo-daro, which supplies most of the seals, or stratify by pairs of sites.
- Shots that withhold site strip the catalogue numbers of the Corpus of Indus Seals and Inscriptions (CISI), whose prefixes reveal the site.
- The confirmation half of the October 12 split is spent for seal size, site and motif: new tests of those need new material or a new partition.

The credence computed by a test's frozen rules and the credence after review can differ. The card's `credence` field holds the current best estimate, and the history keeps both.

The `risk` field records how unlikely the author thinks the claim is at the outset. We aim for about a third of open conjectures to be long shots.

| ID | Claim | Status | Credence |
|---|---|---|---|
| [C-0001](C-0001-rank-written-twice.md) | A legend closing in sign 820 marks an upper grade, cut on a larger seal | strengthened | 0.15 |
| [C-0002](C-0002-working-reading.md) | A working reading of Indus legends as household, name and office | dead | 0.02 |
| [C-0003](C-0003-unicorn-affiliation.md) | The unicorn marks one affiliation present in every city | open | 0.45 |
| [C-0004](C-0004-m895-office-text.md) | The text shared by Lothal L-161 and Mohenjo-daro M-895 names an office | strengthened | 0.6 |
| [C-0005](C-0005-tablet-tiers.md) | Tall strokes before sign 700 count tiers on Harappa tokens | open | 0.5 |
