# Observation units, controls and reproduction

The initial [protocol](PROTOCOL.md), [cohort specification](COHORT-SPEC.md), [pre-score parser amendment](PARSER-AMENDMENT.md), [boundary-concealed control](AMENDMENT-SIGN-CONTROL.md) and [post-result source repair](SOURCE-MARKUP-AMENDMENT.md) preserve the actual selection history. Current endpoints use normalized-v4, run-v2 and sign-control-v2. Earlier datasets and fits remain unchanged.

## Acquisition and representation

Source URLs come from primary institutional editions and documented download routes. `acquire.py` records requests failures as well as responses. Its Python TLS route could not validate ORACC's certificate chain in this environment; `acquire_curl.py` obtained the same public sources with native certificate validation. No certificate check was disabled. The native route obtained a 561,755,376-byte Ur III archive, larger than the first Python downloader's acquisition bound; it is retained locally and is not a tracked repository asset.

The Ur III sample selects the 3,000 lowest SHA256 values of `20261012:<textid>`. Greek acquisition selects the 96 lowest values per catalogue site, including every entry in smaller site inventories. Corpus-entry selection precedes scoring. Failed, missing or excluded documents are not replaced. Egyptian acquisition requests all 1,160 archive text IDs represented by the selected period label. Every request has a timestamp and payload hash.

Cuneiform GDL words provide ordered reading units, numerals, language and POS tags. An account, an envelope and a seal module remain associated with the same document but are not concatenated into one artificial inscription. A blank or ruling is layout; unresolved text and restoration exclude the affected object/module, while separately readable lines survive in a named extension. Numeral forms remain grouped source reading units rather than newly inferred individual strokes.

Egyptian archive entries provide editorial lexical tokens and source POS categories. Complete edited vessel texts require object type Gefäß, matching sentence-ID sets and source word-ID coverage in AED-TEI. The tomb extension supplies glyph sequences only where every source word has a complete glyph encoding. Numeric HTML entities are decoded before extracting Egyptian Unicode glyphs. Word and glyph populations remain separate.

LiBER supplies display text and a search query for each written element. The final parser checks certainty in both because search queries can omit restoration brackets and underdots. Uninterpreted arrow/bullet notation remains unresolved. Hyphen-separated syllabic spellings are expanded into syllabic units; logograms and numbers retain their source grouping. Punctuation and word-boundary conventions belong to the edition. The resulting strings preserve a documented reading order, not the full two-dimensional layout of a photograph.

The IVS population reuses the earlier loader's full-register physical/identical-string closure before eligibility. The 1,596 earlier distinct eligible texts yield 1,593 of length 3–12, comprising 7,970 observed codes. No IVS word boundary or meaning is introduced.

## Structural statistic

For a sequence of length L, position j has normalized value j/(L−1), for j = 0,…,L−1. Let F(u) count a unit u and let m(u) be its mean normalized position across distinct retained sequences. Restrict to units with at least five occurrences. With D equal to their total occurrences, the statistic is

`T = Σ_u F(u) [m(u) − 0.5]² / D`.

The reference independently permutes positions within each sequence, retaining its length and multiset. There are 1,999 draws using the fixed seed and a cohort-specific deterministic offset. The tail is `(1 + exceedances)/2000`. Holm adjustment covers every testable structural cohort. This is a conditional allocation reference; it does not fit a historical production process or establish independent sampling of related inscriptions.

The separate verifier derives the exact reference mean. A sequence containing n copies of u contributes variance `n(L−n)/(L−1) × (L+1)/(12(L−1))` to the sum of u's normalized positions. Add these contributions over sequences, divide by F(u), sum over retained units and divide by D. The Monte Carlo mean is compared with that exact expectation using its estimated mean standard error.

## Known-category calibration

Source tags map to NAME, NUMBER, VERB, FUNCTION, NOMINAL or UNKNOWN. NAME includes the source's several named-entity categories; NOMINAL combines nouns/adjectives. These are broad annotation categories. They do not specify the social purpose of an artifact. Greek has a separate key: SYLLABIC, LOGOGRAM or NUMBER. Its score does not test personal-name recognition.

The word control replaces each lexical identity with a random anonymous categorical ID. Inputs are identity, neighboring identities, one of five normalized-position bins and a length band. A naive Bayes predictor with pseudocount 1 receives training category tags. Position/length-only, identity-only, majority and training-label-permutation controls use the same held-out records. Source glosses, readable words and letter shapes are unavailable to prediction. This is supervised calibration with held-out meanings; the researcher did not claim ignorance of published readings.

All aliases and complete repeated sequences form transitive groups before five greedy token-balanced folds. Test groups and exact sequences cannot appear in training. No score selects the model or smoothing. UNKNOWN targets are counted and excluded from accuracy. Micro accuracy weights tokens; balanced accuracy averages recall over represented classes. Known and unseen identities are reported separately.

The sign control expands each source word category over the units writing that word, then removes the word boundaries from features. The source word segmentation supplies its private answer key. Length filters now count signs/readings, so its eligible objects differ from the word control. Accuracy differences between the two controls cannot be attributed solely to removing boundaries. Each comparison is assessed against its own matched baselines.

## Lexical compatibility

Replace each distinct unit in a word spelling by its order of first appearance. For example, three different units give pattern (0,1,2); a repeated first unit gives (0,1,0). Test the equality patterns of 1,522 distinct IVS faces of length 3–8 against source-observed lexical spellings of length 2–8. NUMBER and UNKNOWN entries are excluded.

This construction assumes one IVS face is one word and permits a new bijection for each face/candidate pair. It does not enforce a shared reading key. Natural dictionaries retain their actual sizes. The matched calculation draws 200 entries without replacement, 500 times per corpus. Intervals describe reference-subset variation, not historical confidence in a language. Matching entry count does not match phonology, glyph inventory, genre, frequency or segmentation conventions.

A separate cardinality check asks whether a shared injection into the observed lexicon could even accommodate all 536 target units. Passing this bound supplies no solution; failing it rejects only that strict injection into that incomplete source inventory. The existing Sanskrit dictionary-letter windows have different units and mapping premises, so this study does not combine them into a language score.

## Manual reproduction

Python 3.13, NumPy, requests and BeautifulSoup were used. The input edition pins, code hashes and seeds accompany every endpoint. The following commands require the captured local witnesses and write new outputs:

```powershell
python -X utf8 experiments/2026-10-12-bronze-age-comparison/reference_sources.py normalized-replay-new
python -X utf8 experiments/2026-10-12-bronze-age-comparison/analyze.py replay-new normalized-replay-new
python -X utf8 experiments/2026-10-12-bronze-age-comparison/sign_control.py signs-replay-new normalized-replay-new
python -X utf8 experiments/2026-10-12-bronze-age-comparison/verify.py replay-new normalized-replay-new
```

Entry points refuse existing output directories. Fresh live downloads may differ from captured source bytes; a replay must either use the stored hashes or declare the changed source version. Acquisition plans describe the observed original routes, rather than promising future availability. The public checkout contains the code and aggregates, with raw input exclusions documented in [SOURCES.md](SOURCES.md).
