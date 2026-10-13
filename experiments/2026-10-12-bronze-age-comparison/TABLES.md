# Exact aggregate tables

Current endpoints: run-v2 and sign-control-v2. All percentages are rendered directly from frozen numeric outputs.

## Structured short records

Lengths 3–12 count the stated encoding units. Distinct sequences are used for this statistic.

| Cohort | Eligible edited records | Distinct sequences | Units | Inventory | Position statistic | Shuffle mean | Holm p |
|---|---:|---:|---:|---:|---:|---:|---:|
| akkadian/natural_line | 3735 | 2743 | 19791 | 666 | 0.026938 | 0.002053 | 0.0055 |
| akkadian/seal | 1 | 1 | 12 | 11 | unavailable | unavailable | unavailable |
| akkadian/whole_tablet | 3 | 3 | 23 | 17 | 0.090000 | 0.018760 | 0.0250 |
| egyptian/glyph_sentence | 1444 | 1227 | 8318 | 335 | 0.025225 | 0.002230 | 0.0055 |
| egyptian/source_sentence | 5882 | 5105 | 26940 | 4725 | 0.050720 | 0.004968 | 0.0055 |
| egyptian/whole_jar_inscription | 302 | 288 | 1415 | 174 | 0.054322 | 0.005975 | 0.0055 |
| indus/whole_face | 1593 | 1593 | 7970 | 548 | 0.059784 | 0.003253 | 0.0055 |
| mycenaean/natural_line | 177 | 158 | 1084 | 147 | 0.048093 | 0.008141 | 0.0055 |
| mycenaean/whole_document | 36 | 28 | 172 | 77 | 0.054645 | 0.018026 | 0.0055 |
| sumerian/natural_line | 27662 | 16701 | 94839 | 1103 | 0.041498 | 0.000899 | 0.0055 |
| sumerian/seal | 427 | 259 | 2385 | 266 | 0.017270 | 0.003946 | 0.0055 |
| sumerian/whole_tablet | 189 | 185 | 1671 | 284 | 0.013712 | 0.005586 | 0.0055 |

Egyptian vessel rows count editorial lexical tokens. Egyptian glyph sentences count glyphs. Cuneiform rows count readings and grouped numeral forms; Greek rows count syllables/logograms/grouped numbers. These are separate encoding populations. [Exact results](run-v2/structural-results.json).

## Word-category calibration

Complete edited object/module texts, 3–12 source lexical tokens. Training tags are available; held-out tags and readable identities are hidden from prediction.

| Cohort | Records | Groups | Scored tokens | Majority | Position | Identity | Context | Context balanced | Unseen-ID context |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sumerian | 759 | 514 | 3806 | 51.37% | 69.73% | 81.79% | 90.41% | 66.49% | 70.26% |
| Akkadian document cohort | 8 | 8 | 50 | 32.00% | 42.00% | 50.00% | 50.00% | 41.67% | 42.11% |
| Egyptian | 302 | 288 | 1202 | 54.08% | 67.30% | 95.09% | 97.00% | 91.99% | 78.33% |
| Mycenaean Greek | 25 | 25 | 143 | 62.24% | 65.73% | 69.23% | 83.92% | 78.03% | 74.65% |

Greek predicts SYLLABIC/LOGOGRAM/NUMBER, rather than the five word/POS categories. Unknown-category targets are excluded and separately counted in the endpoint. [Exact results and class support](run-v2/category-results.json).

## Categories with word boundaries concealed

Lengths 3–12 now count sign/readings or glyphs. Each category applies to units within a source-annotated word. These populations differ from the word table.

| Cohort | Records | Groups | Scored units | Majority | Identity | Context | Context balanced |
|---|---:|---:|---:|---:|---:|---:|---:|
| sumerian/whole | 616 | 412 | 5633 | 65.97% | 94.67% | 94.37% | 53.78% |
| akkadian/whole | 4 | 4 | unavailable | unavailable | unavailable | unavailable | unavailable |
| egyptian/glyph_sentence | 1444 | 539 | 7455 | 54.97% | 64.48% | 69.38% | 48.23% |
| mycenaean/whole | 36 | 28 | 197 | 82.74% | 82.74% | 91.37% | 76.83% |

The complete Akkadian sign-length population has four groups and cannot support the declared five-fold control. Its line extension remains a separate evaluated outcome. [Exact results](sign-control-v2/results.json).

## Equality-pattern compatibility

Target: 1,522 distinct IVS faces of length 3–8, with 47 equality patterns. Each face/candidate correspondence is considered independently.

| Source spelling inventory | Natural entries | Compatible faces, natural inventory | Median candidates per face | Mean compatible fraction, 200 entries | Mean multiple-candidate fraction, 200 entries |
|---|---:|---:|---:|---:|---:|
| Sumerian | 5918 | 1500/1522 | 538 | 92.02% | 86.98% |
| Akkadian document cohort | 2885 | 1505/1522 | 478 | 97.13% | 96.19% |
| Egyptian | 2016 | 1511/1522 | 233 | 96.93% | 94.07% |
| Mycenaean Greek | 285 | 1430/1522 | 41 | 91.16% | 83.58% |

A compatible pattern is not a translation. The assumed per-face key may conflict with every other face. These observed spellings retain corpus/encoding differences, including Sumerian formulae in the Akkadian document cohort. [Exact outcomes and subset intervals](run-v2/lexical-ambiguity.json).

## Extension populations

Natural lines and sentences are reported separately from complete object texts.

| Word-control extension | Rows | Groups | Largest group, rows | Scored tokens | Identity accuracy | Context accuracy | Context balanced accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| akkadian/extension | 2007 | 115 | 754 | 7271 | 72.96% | 73.28% | 65.11% |
| egyptian/extension | 5882 | 2845 | 258 | 23874 | 90.64% | 88.54% | 87.20% |
| mycenaean/extension | 156 | 59 | 13 | 849 | 93.52% | 89.05% | 90.56% |
| sumerian/extension | 15436 | 561 | 12563 | 68322 | 94.68% | 91.94% | 81.85% |

The largest Sumerian extension component contains 12,563 rows; its fold carries 55,488 of 68,322 scored tokens. That grouped outcome is dominated by a particular connected source population. Its rows are not independent tests.

