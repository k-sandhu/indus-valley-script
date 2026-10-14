---
id: Q-1014
title: Join the Dholavira objects to Bisht's 2015 seal and sealing inventory
status: open
area: data
kind: metadata
priority: 2
data_access: local-only
compute: days
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-SITES-GUJARAT-01, EVIDENCE-CENSUS-SYNTHESIS-01]
related: [Q-0016, Q-1013, Q-1021, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/compact-object-table.csv, experiments/2026-10-06-evidence-census/synthesis/conflicts.json]
---

# Question

Which entries of the seal and sealing inventory in Bisht's *Excavations at Dholavira (1989–90 to 2004–05)* correspond to the 230 local Dholavira objects, and what registration, findspot, stage (Bisht's phase of the site's occupation) and dimensions does each carry?

# Why it matters

Dholavira is the third-largest site in the local corpus and its worst described: 0.9% of its objects have a CISI number, 18.7% an excavation number and 0.9% a local image. The reason is that the finds post-date CISI 1, the volume of the *Corpus of Indus Seals and Inscriptions* for collections in India, and the local images are crops from the CISI plates. The report gives 225 recovered seals and 60 sealings on p. 233, and different totals on pp. 242 and 308; the project's evidence census recorded these conflicts. The inventory is the only source held locally for the registrations and stages of these objects.

# What is needed

Read [DATA.md](../DATA.md). Input: `data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf`, a 127 MB scan that the Internet Archive labels a preliminary January 2015 Dholavira report (938 pages, no title page). It was acquired after the census, which worked from a mirrored transcription. First confirm that its text matches the published report of the Archaeological Survey of India, then use the page references the census found for the inventory, pp. 246–333. Transcribe registration number, findspot, stage, material, dimensions, motif and plate reference for each inscribed object. Then join each object to the local Dholavira faces (our corpus's rows, one per inscribed side) by text, motif and dimensions, recording the basis of each match; a match on the text alone stays a candidate. Keep the transcription local.

# How to decide

Done when every local Dholavira object has a joined inventory entry, a set of candidate entries or a recorded failure, and every inventory entry with an inscription has a local object or is listed as missing from the local corpus. Report the counts against the p. 233 totals and explain any difference.

# Prior attempts

The Gujarat batch of the census and its synthesis recorded Dholavira's object counts and the conflicts among them from a mirrored copy; no object has been joined yet.
