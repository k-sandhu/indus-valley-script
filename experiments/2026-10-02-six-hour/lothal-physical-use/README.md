# Lothal inscriptions and the objects they closed

The inspected source frame contains 93 clay sealings. We joined 68 to the preserved corpus and found 29 objects with a clean, complete, single-line inscription of at least three signs. Those 29 objects carry only nine distinct strings. Two strings account for 21 objects, or 72.4% of this eligible frame. This concentration makes the physical object and recurring stamp central to any further comparison. [Refined coverage](join-refined/results.json), [graphic recurrence](graphic-coverage/results.json), [independent review](independent-review/README.md).

The acquired witness is Frenez and Tosi's 2005 chapter, *Lothal Sealings: Records from an Indus Civilization Town at the Eastern End of the Maritime Trade Circuits across the Arabian Sea*. The author deposit's title uses “Networks”; the chapter itself uses “Circuits.” Its 41-page PDF includes two cover pages followed by printed pages 65–103. The saved MD5 matches the deposit's checksum, and the [source record](source-provenance.json) preserves its SHA-256. [Author deposit](https://zenodo.org/records/5514283).

## Source table and prose

Table 1 covers L124–L216 on PDF pages 31–32, printed pages 93–94. Two readers transcribed its 93 rows independently before comparing row-level files. All 465 compared cells agree: impression count, physical category, context code and both page coordinates. The second reader knew the first reader's aggregate results. The table gives 133 impressions and 62 objects with one impression. The prose gives 130 and 63 on PDF page 20, printed page 82. These are retained as separate source assertions.

| Source count | Table | Prose |
|---|---:|---:|
| Impressions | 133 | 130 |
| Single-impression objects | 62 | 63 |
| Warehouse context W | 35 | 35 |
| Warehouse inference W1 | 18 | 18 |
| Area association W2 | 11 | 11 |
| Other context O | 10 | 11 |
| Unspecified context ? | 19 | 17 |

L174 and L179 each have one impression in Table 1 and two in their prose descriptions. The available passages do not reconcile the overall totals. The [independent source assertions](independent-review/source-assertions.json) identify the exact passages. A coordinate correction also places the prose totals one PDF page earlier than the root's frozen coverage notes; the corrected location above follows the independent image review.

Context W1 has a further dependency: the authors assign it through recurrence of stamps already documented in the warehouse group. A comparison using the inscription or stamp to predict W1 would partly reproduce that assignment rule. The field table therefore retains the origin of a context assertion alongside its label.

## Inscription coverage

The table's twelve physical categories include proposed containers, contact materials and attachment mechanisms. The eligible corpus population represents eight of them. Wooden boxes supply 12 eligible objects; structural supports six; parallel canes three; undiagnostic supports three; pottery two; and woven straw, a leather sack and a wall peg one each. Lockers, wicker and the single-rope category have no eligible complete string.

| Eligible string group | Objects | Length | Physical categories represented |
|---|---:|---:|---:|
| G01 | 11 | 8 | 7 |
| G02 | 10 | 4 | 1 |
| G03 | 2 | 3 | 2 |
| Six singleton groups | 6 | See output | One each |

G01 occurs on L124–L129, L190, L191, L193, L197 and L206. Its source categories cover woven straw, wood, leather, undiagnostic surfaces, pottery, a structure and a wall peg. G02 covers L161–L170, all labelled wooden boxes and marked with an elephant motif in the derivative metadata. The source's elephant-stamp cohort has twelve objects, L161–L172; the final two have no joined corpus record. These memberships are explicit in [the recurrence result](graphic-coverage/results.json).

The original chapter already discusses recurrent stamps on varied fastenings and the elephant stamp on wooden surfaces. The present contribution is the checked finite frame, its corpus coverage, the exact repeated-string groups and the source-account differences. Exact inscription identity is a graphic observation; confirming the same physical seal also requires border, motif and incision detail.

## Physical observations to develop next

Figures 3–7 show 35 labelled objects. An independent selected review records twelve objects and an unnumbered inset, preserving visible geometry separately from the authors' interpretations. L124 has crossing ribbed contact marks and curved geometry, compatible with the chapter's proposed vessel cover. This example helped settle the recording scheme: contact texture, support shape and closure action each need their own field. [Selected trace observations](independent-review/selected-trace-observations.json), [field definitions](independent-review/TRACE-FIELDS.md).

A bounded next study would code G01's varied attachments and G02's wooden supports with the same form. It could ask which aspects of the physical operation vary while the inscription remains stable. Cord paths, contact curvature, overlap, clay manipulation and broken-away surfaces provide measurable targets. Experimental impressions on boards, wrapped corners and curved vessel mouths would supply reference traces. A prediction study should withhold an entire recurring stamp or inscription, with source-based context inferences identified in advance.

## Methods and checks

The [source protocol](PROTOCOL.md) preceded table coding; a separate [recurrence protocol](GRAPHIC-COVERAGE-PROTOCOL.md) preceded grouping the eligible strings. No classifier or association test was fitted. The analysis retains all 93 targets and reports missing joins and illegible or short faces. Full table transcriptions, detailed corpus joins and acquired PDF/images remain local. Tracked outputs contain our aggregates, object identifiers, hashes and observation fields.

The independent implementation reproduces the 68-object join, 86 faces, 29 eligible objects and all nine string groups. Its [14 checks](independent-review/main-refined/verification.json) pass. The root's first endpoint and the reviewer's first endpoint each preserve an implementation failure; the [retrospective](RETROSPECTIVE.md) explains both repairs. Code snapshots and fresh output directories keep those records available for later work.
