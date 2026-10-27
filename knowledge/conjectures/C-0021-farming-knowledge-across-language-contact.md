---
id: C-0021
title: Language contact carried regional farming knowledge into early Indo-Aryan communities
status: open
credence: 0.50
credence_history:
  - {date: 2026-10-25, value: 0.50, reason: "Starting judgment for the specific regional transmission mechanism; crop continuity alone supplies no language identity"}
risk: stretch
area: language
authors: ["GPT-6, Codex API workspace harness; exact model build unavailable"]
prior_proposals: ["Witzel 1999, Substrate Languages in Old Indo-Aryan", "Fuller and Murphy 2018, The origins and early dispersal of horsegram", "EARLY-INDIAN-CONTINUITY-PROGRAM-2026-10-11"]
builds_on: [CROP-CONTINUITY-2026-10-25, CULTURAL-TRANSMISSION-THEORIES-2026-10-25]
tests: []
---

# Claim

Early Indo-Aryan-speaking communities acquired some regional crop knowledge and agricultural vocabulary through contact with farming communities carrying older South Asian practices. This contact contributed to the agricultural world described in Vedic texts. The transmitted knowledge crossed language boundaries.

# Why we think this

The [crop audit](../../experiments/2026-10-25-crop-continuity/REPORT.md) identifies a surviving practical repertoire. Historical linguistics independently proposes borrowing in regional plant and agricultural vocabulary. Fuller and Murphy discuss reconstructed Dravidian horsegram forms alongside Sanskrit *kulattha* and Juang *kulto*, while also presenting archaeological evidence for more than one domestication trajectory. Their proposal is a case to investigate, not a dated transmission route from Jognakhera. [Source and claim register](../../experiments/2026-10-25-continuity-theories/CLAIM-EVIDENCE.json).

The claim leaves the donor language open. A word with an unresolved Indo-European etymology does not automatically become a Dravidian or Munda loan, and a later crop word does not establish the language of the Indus inscriptions.

# Predictions

| ID | Prediction | New data and pass rule | Status |
|---|---|---|---|
| P1 | Agricultural vocabulary shows a regional contact component beyond inherited Indo-Iranian vocabulary | Freeze the textual corpus, semantic classes and frequency-matched basic-vocabulary controls. Independent etymological coding must separate secure inheritance, supported loans, innovations and unknowns. The lower-bound excess of supported local-contact roots in agriculture must remain positive under plausible reclassification and resampling by root family and text layer. | untested |
| P2 | At least one reserved crop or processing term has a chronology and distribution consistent with a specific regional operation already present in pre-Vedic and intermediate contexts | Freeze the term and proposed route before opening new lexical and archaeological sources. Require regular sound correspondences, a supported botanical or technical identification, source-specific attestations and dated intermediate material. Iranian inheritance, later borrowing and an alternate regional route must be evaluated under the same rules. | untested |

P1 alone raises credence to 0.60 and supports general contact. A source-verified P2 is needed to raise it to 0.75 for the specific older regional carrier. A powered P1 failure lowers it to 0.25. Shared evidence is updated once under the [program rule](../../experiments/2026-10-25-continuity-theories/TEST-DESIGN.md).

# Kill condition

Reject the registered regional route if the decisive terms are securely inherited from Indo-Iranian, demonstrably borrowed only much later, or geographically and chronologically incompatible with the proposed carrier. A lack of known etymology or a missing ancient lexicon cannot count as a pass or a failure.

# Record

25 October 2026: proposed, with all cited material treated as discovery. The [synthetic shots output](../../experiments/2026-10-25-continuity-theories/bench-shots-synthetic-v1.json) verifies procedural guards and supplies no historical or linguistic score. No sign values or translations are proposed. Real testing requires the lexical and context data specified in the [design](../../experiments/2026-10-25-continuity-theories/TEST-DESIGN.md).
