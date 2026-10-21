# Proposed source and coverage additions

We reused held sources and added a derived source layer for 2,879 of the 4,695 Lipi object families. No external source or physical object was acquired. The new fields keep the evidence path visible at the point where graphic variants are analyzed.

| Added field | Objects with the field | Source and status |
|---|---:|---|
| CISI basic-data table locator and volume | 2,602 | One-family joins in the October 13 full transcription, with printed page, PDF page and source block; `catalogued` |
| Unbracketed excavation-source qualification | 1,897 | The same source, restricted to unbracketed usable excavation fields with no unresolved identity or excavation-column uncertainty; `catalogued` |
| Excavation report and table-row locator | 1,134 | The October 13 Mackay and Marshall join; `catalogued` |
| Exact parsed museum-key candidate | 1,840 | A parsed holding code and number with no query, former holding, unresolved museum-column reading or unsupported punctuation; this is a candidate key, not an identity adjudication |
| Automatic repeated museum-key flag | 30 | Fifteen keys from the frozen source layer; audit classifies two keys as parser fragments and thirteen as repeated source values requiring plates |

The denominators are all object families in the held export, rather than all known Indus objects. The CISI table locator covers 1,239 objects from volume 1 and 1,363 from volume 2. The 277 remaining objects in the source layer have an excavation-table link but no one-family join to these two CISI basic-data transcriptions.

The new layer retains earlier identities and source assertions. It adds neither a calendar date nor a workshop identification. Source volume is not an independent transcription. The museum-key audit found that comma punctuation inside some ASI accession values is split by the upstream parser, producing a repeated numeric prefix. We preserved the frozen flags and recorded their two false candidates in [candidate-source-identities.csv](audit-v1/candidate-source-identities.csv). The other thirteen repeated values remain candidate identity conflicts; no physical objects were merged.

The [plate notes](PLATE-NOTES.md) propose a verified link from record `3706.2` to M-1419 A and an inferred link from `3706.1` to B. They also record H-775 B as an uninscribed reverse. Those observations can enter the shared face index after integration. Their photograph files and complete transcriptions stay local.

Exact source hashes, source-derived row locations and output hashes are in [coverage.json](source-v1/coverage.json), [summary.json](run-v1/summary.json), [support.json](audit-v1/support.json) and `data/raw/2026-10-20-script-variation/`. All CISI and Lipi payloads remain local under the redistribution record. The tracked source candidate table contains identifiers, locators and this project's dispositions. The transcribed excavation data retain attribution to Nitin Stephen Koshy, *Indus script: seal catalogues and text-structure analysis* (2026), repository `epachayan/indus-script` at `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f`, CC BY 4.0. This package carries no bulk table values.
