# Data update: full-corpus alias closure and near-variant clustering

Date: 22 November 2026. Scope: derived split registers and leakage audits over existing local corpus files. This study adds no new inscribed objects, photographs, or catalogue fields to the project corpus; all metadata coverage figures in [DATA.md](../../knowledge/DATA.md) remain unchanged.

## Inputs verified

| Source | Logical path | SHA-256 | Role |
|---|---|---|---|
| Clean RTL single-line benchmark | `data/normalized/lipi_clean_rtl_singleline.jsonl` | `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8` | 1,596 unique complete strings (8,009 slot queries) |
| Full observed face register | `data/normalized/lipi_observed_faces.jsonl` | `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db` | 5,680 faces used for full-corpus transitive alias closure |
| Base-shape family table (`F-0010`) | `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv` | `c2d55fb56e25b8d7f630f2680f9b85b9122cfa15b8718e08fa5b72c11f509f7d` | Maps all 548 benchmark sign codes into 77 base classes (0 unmapped) |

## Corpus linkage observations for Q-0010

1. **CISI base key consistency:** Across all 5,680 faces in `lipi_observed_faces.jsonl`, `source_cisi` and `metadata.cisi` are identical on every row. Two values carry trailing spaces (`L-78 `, `M-929 `), 661 carry `-`, and 4 carry uncertain prefixes (`?-3` to `?-6`). After trimming and normalizing to `<prefix>-<number>`, zero CISI base keys span more than one `object_family_id`.
2. **Excavation-number cross-family collisions:** After stripping whitespace and punctuation, uppercasing, and excluding placeholders (`-`, `--`, `- -`, `?`, `Unknown`) and digit-free site prefixes (`BNL`), 19 `(site, excavation-idno)` keys span two or more `object_family_id` values (including 13 Harappa families under `G256`, and paired families such as Harappa `8650c448` linking `H-912` and `H-1191`, Harappa `-470a` and `470a`, and Mohenjo-daro `VS-N 83-609`). Including these edges in Split 2 performs 14 additional union-find merges across the 5,680-face register and adds 2 benchmark strings (7 queries) to the 192 strings (748 queries) already bridged by short face strings, bringing total Split 1 full-corpus alias leakage to 194 strings and 755 queries (9.43%).
3. **Near-variant structure:** Across the 1,596 unique benchmark strings, there are 876 unordered pairs at Levenshtein edit distance 1 and 295 unordered pairs with identical `F-0010` base-shape sequences. Merging these edges onto Split 2 reduces the component count from 1,361 to 964 and produces one large connected cluster of 493 strings (1,872 slots, 23.4% of queries) formed by the densely connected core of short seal formulas.

## Local derived files written

Per-query predictions and fold assignment tables are stored locally under the D: raw storage junction and remain untracked in Git:

- Logical directory: `data/raw/2026-11-22-restoration-leak-free/`
- Physical directory: `D:\projects\indus_valley_script\data\raw\2026-11-22-restoration-leak-free\`
- Contents: 3 fold registers under `folds/` (`split1_baseline.jsonl`, `split2_alias_clean.jsonl`, `split3_near_variant_clean.jsonl`) and 18 per-query prediction files under `predictions/<split>/<model>.jsonl` (8,009 rows each). Exact SHA-256 digests of all 21 local files are recorded in [results-v1/summary.json](results-v1/summary.json).
