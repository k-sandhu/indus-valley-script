---
id: Q-1019
title: Resolve the 46 museum records not yet joined to a local object
status: done
area: data
kind: metadata
priority: 3
data_access: local-only
compute: hours
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01, EVIDENCE-CENSUS-SYNTHESIS-01, MUSEUM-OPEN-ACCESS-2026-10-13]
related: [Q-0005, Q-1005, Q-1018]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/join-summary.json, experiments/2026-10-06-evidence-census/synthesis/review/museum-join-check.md]
---

# Question

Which local object, if any, does each of the 46 unresolved museum records describe?

# Why it matters

The project's evidence census saved 114 museum records of original objects from six museums and confirmed 68 joins, that is, records checked to describe a particular local object. The remaining 46 split into 13 whose identifier strings failed to match, 2 with a usable identifier that was never tried, and 31 without a usable identifier in the first pass. Each new join adds an accession number, a museum photograph and often dimensions to an object that lacks them.

# What is needed

Read [DATA.md](../DATA.md). Inputs: the saved records under `data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/` and the candidate list in `data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/candidate-object-joins.json`; the CISI 1 basic data (Q-1005), whose museum column links entries of the *Corpus of Indus Seals and Inscriptions* to accession numbers; Marshall's p. 402 table for British Museum seals. Start with the two untried identifiers and the 13 failed strings, then look for a published concordance that links each of the 31 records without an identifier to a catalogue number. Record each decision with its basis.

# How to decide

Done when each of the 46 records is joined, has a candidate set, or is recorded as unjoinable with the sources searched. Report the new lower bound of confirmed joins beside the census's 68.

# Prior attempts

The museum batch of the census and the synthesis review produced the 68 confirmed joins and left these 46 open.

13 October 2026, outcome: Each of the 46 records has a decision with its basis ([q1019-decisions.csv](../../experiments/2026-10-13-museum-open-access/joins/q1019-decisions.csv)). Sixteen are confirmed through CISI 1 basic-data rows read by eye (Lothal LTH SRG numbers, National Museum (NMI) and Indian Museum (IM) numbers, Banawali and Chanhu-daro rows), the Marshall 1931 and Mackay 1938 seal tables, and numbers written on the objects in CISI photographs (L-29 B "SRG 989", L-122 B "2845"). Twenty-one have candidate sets (the Met seals, seven Indian Museum seals without a confirmed identifier join, the Louvre seals from Susa and Girsu, two British Museum seals and three National Museum records), eight are unmatched and one is uninscribed. The confirmed lower bound rises from 68 to 84 for the census's 114 records. Five unmatched records are candidate additions to the corpus: CISI H-224 (NMI 1296), Banawali 3714 and Dholavira DHR-22198, DHR-6032 and DHR-7860. The National Museum record DK12995 shares its number with CISI H-13, a Harappa unicorn seal, and is not that object. The independent reviewer added Indian Museum 10377/A7252/C.2803 as Lipi family 2194 (M-1809), the local corpus's record group for that object, through Marshall 1931 vol. II p. 403 row 199. A substring search of identifiers for missed joins leaves 10 unjoined records with hits, four of them pointing to a single family; printed-page checks are pending. Retry when CISI 3.1 or the British Museum object pages are available, or with better copies of the Mackay 1943 plates.
