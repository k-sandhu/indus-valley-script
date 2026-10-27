# Data update proposed for integration

We added source review for all 24 lexical forms in the current proposed-identification table. The local review contains 56 exact Tamil Lexicon candidates and 38 selected senses or contextual entries, with stable entry identifiers, original page hashes and character spans. Four relationships have limited source-attested scope: aṟu/āṟu in aṟu-mīṉ, eḻu/ēḻu in eḻu-mīṉ, iru/iraṇṭu in iru-kaṇ and kāvu/kāvu- as a verb citation form. They do not change exact written-form counts.

Two source-attribution corrections are ready for the next version of the Tamil alternatives: āvu belongs to the cited Kannada and Telugu forms in Parpola 1997 p.171; tōḷ belongs to Toda in Parpola 2009 p.63. Keep their original language information. Source selections for the remaining forms distinguish picture names, picture actions, target senses and grammatical comparisons. Printed citations are retained as citations; no earliest attestation has been assigned.

The compound review contains forty prospectively selected source-audit rows and three previously known regression cases. Of twenty accepted parser splits, seventeen have source-supported boundaries, one is wrong and two remain unresolved. Of twenty rejected rows, two are directly supported missed compounds, nine remain unresolved and nine fall outside two-noun or two-member scope. These stratified counts do not establish global extraction recall. The later Tamil Lexicon sometimes cites Winslow, and its agreement is recorded as a lexical cross-check rather than an independent attestation.

The general wrapper repairs a grammatical-letter header omission and preserves parent origin marks separately from a whole-entry loan judgment. It is available for a later full extraction. Increment morphology, the aintaru boundary and complete dictionary coverage remain open.

Integration resources:

| Resource | Location and key |
|---|---|
| Sense review | `data/raw/2026-10-22-lexical-source-review/run-v1/sense-review.jsonl`; unique `form` |
| Compound review | `data/raw/2026-10-22-lexical-source-review/run-v1/compound-review.jsonl`; unique `entry_id`, with `sample_id`, `sample_stratum`, `review_decision` |
| Limited form relations | `data/raw/2026-10-22-lexical-source-review/run-v1/accepted-relations.json` |
| Local source packets | Same directory, `sense-packets.json`, `sense-supplements.json`, `additional-member-witnesses.json`, `compound-packets-v2.json` |
| Reuse provenance | [source-manifest-v1.json](source-manifest-v1.json), [FREEZE.json](FREEZE.json) |

Every review row names the AI reviewer, qualifications, provisional status and uncertainty. In the sense resource, `accepted_for_tamil_picture_alternative` records only whether the source requires exclusion for wrong language; a true value does not approve a picture identification or resolve every sense. Consumers must inspect `review_decision`, role-specific `selected_senses` and the rationale. Store these as linguistic-source review resources, separate from archaeological assertions or proposed sign meanings. All detailed third-party text and derivatives remain local under the existing redistribution rules. No new source was downloaded.

The strongest supported update is a source-cited correction record for every current lexical form and every sampled compound. Expert adjudication and a complete corrected extraction are the next requirements for a scientific effect calculation.
