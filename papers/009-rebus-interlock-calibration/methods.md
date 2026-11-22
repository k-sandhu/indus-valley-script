# Methods and reproducibility guide for Paper 009

This guide documents the software, inputs, randomization seeds, normalization algorithms, and execution sequence behind every result reported in [manuscript.md](manuscript.md). All analyses run from the repository root with Python 3.13 and NumPy 2.2.6 (standard library plus NumPy). Raw third-party dictionaries (DSAL DEDR, CDIAL, Madras *Tamil Lexicon*, Winslow 1862, Cologne Monier-Williams `mw.txt`, Project Madurai Sangam HTML files) and local per-compound hit listings remain on local storage (`D:\projects\indus_valley_script\data\raw\`, linked via `data/raw/`) under the repository's redistribution rules; tracked files hold protocols, code, hashes, and aggregate JSON outputs.

## 1. Study sequence and non-overwrite provenance

| Package | Date | Role in Paper 009 | Freeze / protocol |
|---|---|---|---|
| `experiments/2026-10-21-rebus-base-rate/` | 21 Oct 2026 | Single-homophone base rates across five lexicons; *veḷ* (I1) and 4-link network nulls in Madras *Tamil Lexicon* | `PROTOCOL.md`, `FREEZE.json`, `AMENDMENT-1.md`, `results-v2/` |
| `experiments/2026-10-21-dravidian-root-meanings/` | 21 Oct 2026 | Ancestral-state reconstruction of *mīn* "star" and 15 other Parpola meanings on Kolipakam et al. (2018) MCC and posterior trees | `PROTOCOL.md`, `AMENDMENT-1.md`, `FREEZE.json`, `results-v1/results.json` |
| `experiments/2026-10-21-north-b-correspondence/` | 21 Oct 2026 | DEDR-wide count of Kurukh and Malto initials for Tamil *m-* and *v-* | `PROTOCOL.md`, `PARSE-CHECK.md`, `FREEZE.json`, `results-v1/results.json`, `verify/verification-v1.json` |
| `experiments/2026-10-22-rebus-blind-templates/` | 22 Oct 2026 | Frozen 16-sign identifications, 38 blind pairs, 24 gapped pairs, 12 published pairs; original blind-template run | `PROTOCOL.md`, `PREDICTIONS.json`, `FREEZE.json`, `templates-v1.json`, `results-v1/templates.json` |
| `experiments/2026-10-22-rebus-winslow/` | 22 Oct 2026 | First Winslow (1862) cross-dictionary test of I1 and 2010 network; post-outcome equal-target comparison | `PROTOCOL.md`, `FREEZE.json`, `results-v1/interlocks.json`, `exploratory-v1/exploratory.json` |
| `experiments/2026-10-22-reading-eval-readiness/` | 22 Oct 2026 | Audit uncovering prefix-count and *aṟu*-to-*aṟṟu* fallback defects; implementation of `lexical_inputs.py` | `code/lexical_inputs.py`, `run-v1/input-audit.json`, `verification-v2.json` |
| `experiments/2026-10-24-lexical-extraction-extension/` | 24 Oct 2026 | Complete Winslow re-extraction separating raw guarded boundaries (`winslow_guarded_members`) from Lexicon-assisted boundaries (`members`) | `FREEZE-v3.json`, `results-v1.json`, `verification-v1.json` |
| `experiments/2026-11-22-rebus-repaired/` | 22 Nov 2026 | Repaired Tamil blind-template rerun, re-extracted Winslow blind and base-rate runs, and pre-frozen Sanskrit Monier-Williams control | `PROTOCOL.md`, `results-v1/tamil_repaired.json`, `results-v1/winslow_reextracted.json`, `results-v1/sanskrit_control.json`, `verification-v1.json` |

Every earlier frozen output remains intact. No new Indus confirmation split or cohort was read in the 22 November repair package: all template pairs are the exact frozen pairs of `experiments/2026-10-22-rebus-blind-templates/templates-v1.json` (SHA-256 `8ddc7d2a...`), originally drawn through `bench.shots` on split `d1d1b920` (family `rebus_template_pairs`).

## 2. Repaired Tamil lexical lookup and exact written-form counting

The 22 October blind-template scorer counted Sangam frequency by stripping trailing Tamil vowel marks from a dictionary headword and counting every token starting with that string (`prefix_count`), inflating monosyllabic words (*kā* 22,287 tokens; *ā* 4,458 tokens). It also fell back to length- and gemination-free lookup when no exact one-member Lexicon record existed, substituting *aṟṟu* for *aṟu*.

In `experiments/2026-11-22-rebus-repaired/code/run_tamil_repaired.py`, we import `FormCounts`, `tamil_tokens`, and `Lexicon` from `experiments/2026-10-22-reading-eval-readiness/code/lexical_inputs.py`:

1. Each of the 17 Project Madurai Sangam HTML files (`data/raw/2026-10-21-rebus-base-rate/sources-v1/sangam/pmuni*.html`) is stripped of HTML tags (`re.sub(r"<[^>]+>", " ", text)`) and tokenized with `tamil_tokens`, keeping only Tamil Unicode letters and vowel or combining marks (`U+0B80`–`U+0BFF`, Unicode category `L` or `M`, NFC-normalized). This yields 162,436 tokens (37 more splits than the raw-block regex's 162,399, at Tamil numeral symbols; exact counts of *kā* = 9, *ā* = 24, *aṟu* = 23, and *aṟṟu* = 8 are identical under both tokenizers).
2. Every proposed Tamil word and every candidate replacement noun is resolved through `Lexicon.resolve(word, counts)` with zero phonological fallback. Exact and homograph-ambiguous records aggregate exact written-form counts over their distinct NFC Tamil headwords without choosing a sense. Unresolved *aṟu* (zero exact one-member records in `tamil-lex-entries.jsonl`) is matched on compounding productivity alone in `exact_freq_prod`, and receives the direct exact Sangam count of `அறு` (23) in the sensitivity `exact_freq_prod_aru_direct`.
3. A parallel mode `prod_only` removes Sangam frequency altogether, matching candidates solely on `log1p(prod)` (slot-level) or `(log1p(prod_first), log1p(prod_last))` (sign-level).

## 3. Sign-level dependent random keys versus slot-keyed draws

In `2026-10-22-rebus-blind-templates/code/run_templates.py`, joint random keys sampled separate replacement words for `(sign, "first")` and `(sign, "second")`. In `2026-11-22-rebus-repaired`, we enforce unified sign-level dependence across all 38 templates:

- Each word *w* is matched to its `K = 50` nearest candidate nouns (excluding words sharing *w*'s `T1s` stem) in standardized Euclidean distance on `(log1p(prod_first), log1p(prod_last), log1p(freq))` (or without `freq` in `prod_only` and Sanskrit).
- In each of `10,000` joint draws (seed `20261122`), every sign receives one random replacement word per alternative form from its unified pool, and that exact assignment is scored across all templates where the sign occurs in either position.
- Slot-keyed joint draws (`10,000` draws) and marginal per-template expectations (exact enumeration up to 2,500 pairs; 5,000 Monte Carlo draws otherwise; 2,000 template bootstrap resamples) are computed alongside unified sign-level draws to isolate the effect of repairing the frequency proxy from the effect of unifying sign pools.

## 4. Separation of Winslow (1862) boundary layers

From `data/raw/2026-10-24-lexical-extraction-extension/run-v1/winslow-entries.jsonl` (69,310 entries), we construct two separate tables:

- **`raw_guarded`**: reads `winslow_guarded_members` (18,421 two-member compounds; suppresses false splits such as *ja-mīṉ* for *jamīṉ* while importing zero boundaries from the *Tamil Lexicon*). Only this layer is an independent cross-dictionary test.
- **`lexicon_assisted`**: reads `members` (25,653 two-member compounds, incorporating unique exact-headword *Tamil Lexicon* boundaries). Reported strictly as a boundary-recovery sensitivity.

Both layers are scored on the 38 blind pairs, 24 gapped pairs, 12 published pairs, and the 2010 I1/network searches using exact Sangam written-form counts and productivity-only matching.

## 5. Monier-Williams Sanskrit control

In `experiments/2026-11-22-rebus-repaired/code/run_sanskrit_control.py`, Cologne Monier-Williams (`data/raw/2026-10-12-decipherment-claim-tests/mw/mw.txt`, SLP1 encoding) is parsed as follows:

1. **Two-member compounds (`<e>3` main entries only, skipping `3A`/`3B`/`3C` sub-senses and `<e>4` nested compounds):**
   - When the headword `<s>...</s>` before `¦` contains `—˚` and a single `<srs/>`, `—˚` is removed (print abbreviation inside member 1) and the form is split at `<srs/>` (277 unique compounds).
   - Otherwise, when `<k2>` contains exactly one em-dash `—`, `<k2>` is split on `—`, stripping accents, degree marks, internal hyphens, and leading single-letter sandhi connectors (`M-`, `m-`, `n-`, `r-`, `s-`) on member 2 (87,281 unique compounds).
   - Otherwise, when `<k2>` has no `—` and the headword span has one `<srs/>`, standard Sanskrit vowel coalescence is reversed (`A -> a+a`, `I -> i+i`, `U -> u+u`, `F -> f+f`, `e -> a+i`, `o -> a+u`, `E -> a+e`, `O -> a+o`, `ar/Ar -> a+f`; 13,606 unique compounds). Under vowel-length-free `T0s`, each savarṇa or guṇa split (`A, I, U, e, o`) yields a unique normalized pair.
   - Total primary compounds: `101,164`. A sensitivity (`mw_plus_hyphen`) adds 6,216 nominal hyphenated `<e>3` entries lacking `—` and `<srs/>` (excluding derivative suffixes `-tA`, `-tva`, `-maya`, `-vat`, `-mat`, `-tara`, `-tama`, `-ika`, `-ka` and verb entries), totaling `107,380` compounds.
2. **Simplex candidate pool:** unique `<k1>` headwords from `<e>1` and `<e>2` entries lacking `—` and `<info verb=`, having at least one nominal gender code (`m`, `f`, or `n` in `<info lex="..."/>`), deduplicated by `T1s` anchor stem (`35,694` candidates).
3. **Symmetric normalization and sandhi:** SLP1 is mapped to IAST and normalized with the exact `rebus.seg_indic`, `rebus.normalise(..., ["L"])` (`T0s`), and `rebus.stem` (`T1s`) functions used for Tamil. Symmetric first-member Sanskrit sandhi reversal (`skt_sandhi_bases`) restores `-n` truncation (`a/i/A/I -> +n`), `-s` and visarga sandhi (`o -> as`, `r/H/S/z -> s`), stop voicing and retroflex or nasal assimilation (`w/q/R -> z/w/q`, `d -> t`, `g -> k/c`, `k -> c`, `b -> p`, `j -> c`, `M/n -> m`), and *yaṇ* glides (`Cy -> Ci`, `Cv -> Cu`).
4. **Scoring:** the four frozen Sanskrit maps (`primary_single`, `multiplicity_matched`, `primary_antara`, `multiplicity_antara`, declared in `PROTOCOL.md` before any `<e>3` lookup) are scored on the 38 blind pairs, 12 published pairs, and 24 gapped pairs with `K = 50` (and `K = 25, 100`) and `10,000` sign-level dependent random keys (seed `20261122`).

## 6. Independent verification

Every package has an independent verification script written without importing the primary measurement code. For the 22 November package, `experiments/2026-11-22-rebus-repaired/code/verify.py` independently checks all Sangam counts, Tamil Lexicon and Winslow compound totals and hit counts, Monier-Williams compound parsing unit tests and hit counts across all four Sanskrit mappings, and a synthetic planted-versus-unplanted joint-key calibration benchmark (`verification-v1.json`, `all_passed: true`).

Reproduction commands for the 22 November repair and Sanskrit control package:

```text
python experiments/2026-11-22-rebus-repaired/code/run_tamil_repaired.py
python experiments/2026-11-22-rebus-repaired/code/run_sanskrit_control.py
python experiments/2026-11-22-rebus-repaired/code/verify.py
```
