---
id: Q-1013
title: Build the cross-catalogue identifier crosswalk for every held object
status: open
area: data
kind: metadata
priority: 1
data_access: local-only
compute: days
difficulty: expert
claimed_by: ""
claim_expires: ""
prior_attempts: [ROOT-19, OBJECT-LEDGER-PILOT-01, EVIDENCE-CENSUS-SYNTHESIS-01, CISI2-BASIC-DATA-PILOT-2026-10-13]
related: [Q-0001, Q-1003, Q-1005, Q-1006, Q-1007, Q-1012, Q-1030]
sources: [knowledge/DATA.md, knowledge/provenance/catalogue-caveats.md, experiments/2026-10-06-evidence-census/synthesis/join-summary.json]
---

# Question

For each local object, which identifiers name it in each catalogue and record: CISI number with side and photograph suffixes, Mahadevan 1977 text number, Koskenniemi and Parpola 1979 text number, ICIT/Lipi number, excavation registration, museum accession, and excavation-report figure or table entry? Which links are confirmed physical identities and which are candidates?

# Why it matters

Every other enrichment depends on joins. The local export has a CISI number for 86.8% of objects and a usable excavation string for 89.6%, but the excavation field mixes registrations, citations and lot numbers, and no local file holds the Mahadevan 1977 or 1979 numbers per object. Without one crosswalk, each study re-derives joins and repeats earlier mistakes; the object ledger pilot had to separate 149 excavation strings into 126 registrations and other kinds by hand.

# What is needed

Read [DATA.md](../DATA.md) and the identity rules in [catalogue-caveats.md](../provenance/catalogue-caveats.md). Inputs: Lipi and website exports; CISI basic data (Q-1005, Q-1006); the Mahadevan 1977 PDF (held) and its concordance or site tables; the 1979 and 1980 Helsinki editions (held; the 1980 volume documents sources and duplicates); museum joins from the census and Q-1019; excavation tables from Q-1003, Q-1014 and Q-1016. Store one row per identifier assertion with source, page, relation type (`same-object`, `same-side`, `extra-photo`, `impression-of`, `possible-match`, `repeated-text`) and confidence. Never merge transitively through candidate links.

# How to decide

Done when every local object has all identifiers that the held sources assert, each with a locator, and the summary reports for each catalogue the share of local objects linked by confirmed and by candidate relations. A blind second check of 100 random links reports an error rate; above 3% for confirmed links, revise the rules.

# Prior attempts

ROOT-19 resolved several historical joins by primary witnesses. The object ledger pilot built source-qualified aliases for 200 carriers. The census matched catalogue keys by exact string.

13 October 2026. The CISI basic data gives an FC number (the 1979–1982 Helsinki concordance number) for every entry; the CISI 2 pilot holds 327 CISI-to-FC links for M-621 to M-947 locally. For Mohenjo-daro the FC number encodes the excavator's catalogue number: 1000 plus Marshall's 1931 number or 2000 plus Mackay's 1938 number, which holds for 216 of 219 objects joined in both the CISI 2 pilot and the [Mackay and Marshall join](../../experiments/2026-10-13-mackay-marshall-tables/README.md) ([cross-check](../../experiments/2026-10-13-data-round-1-verification/fc-crosswalk.json)). The three exceptions belong to two pairs of objects whose CISI 2 basic-data rows are crossed, as plate measurements show ([swap check](../../experiments/2026-10-13-data-round-1-verification/swap-check.md)); the rule holds for every checkable object whose CISI 2 row is right. The FC number therefore links CISI numbers to the excavators' tables without going through Lipi's registration strings, and the digits Lipi appends to its registrations are the same catalogue numbers.
