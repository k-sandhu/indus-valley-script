# Proposed card updates

For maintainers to apply after merging; this package edits no card.

**Q-0037** (design a head-direction seal comparison). Its "How to decide" asks us to stop at the protocol and a feasibility ledger. Both exist: [PROTOCOL.md](PROTOCOL.md) with four amendments, and [FEASIBILITY.md](FEASIBILITY.md). Proposed status `done`, with `prior_attempts` gaining `HEAD-DIRECTION-CORPORA-2026-10-21`. The frozen test ran and could not keep or reject a statistic, because the Old Akkadian corpus has 11 eligible legends and the Tamil-Brahmi corpus 23.

**STRUCTURAL-TYPOLOGY-2026-10-12.** Its retry condition is met in part. Two head-final corpora and two head-initial corpora are now normalised and measured with the same code, but only one of each is large enough for the keep rule. The new entry's `retry_when` takes over.

**New data question (proposed).** "Assemble a second head-initial and a larger Tamil-Brahmi seal-legend corpus." Kind `data-acquisition`, area `comparative`. Needed: at least 25 eligible Akkadian seal legends with object and site (Tell Brak and Tell Mozan excavation reports; Old Assyrian seals of Kültepe) or a West Semitic stamp-seal corpus with proveniences (a library copy of Avigad and Sass 1997; the DASI archive), and at least 25 Tamil-Brahmi seal and ring legends with sites (the revised *Early Tamil Epigraphy*; Karur and Keeladi reports). The record form is [SCHEMA.md](SCHEMA.md). Done when the frozen protocol can run at threshold 25 with two corpora per group.

**Proposed conjecture** for `knowledge/conjectures/`, credence 0.6. "Final-sign concentration in a seal legend marks a closing formula, not a head-final language; head direction shows in the order of title and name." Prediction: on enlarged corpora the sign-level edge statistics fail the keep rule, with Akkadian on the head-final side, and title before name is kept. Kill condition: the enlarged Akkadian corpus falls below the Ur III range on `sign.S1` at matched size. Evidence: [REPORT.md](REPORT.md), sections 3 and 5.
