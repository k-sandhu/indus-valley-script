# Preprint submission checklist for Paper 006

Prepared for dated preprint submission of `papers/006-sanskrit-key-calibration/` (GitHub Issue #15). This checklist records the exact reproduction steps, data-redistribution boundaries and technical review points for a human Sanskritist reviewer.

## 1. Local data boundaries and pinned inputs

Do not commit or redistribute raw third-party inputs or per-inscription sequence files. The Lipi export (`yajnadevam/lipi`, commit `fc8813a52e183d19c441631dc26c33a4dccbea39`) carries no licence file at that commit, and the local raw directory (`data/raw/2026-10-12-decipherment-claim-tests/`) holds mixed-rights texts and PDFs. Keep all raw corpora local and distribute only the tracked scripts, aggregate JSON outputs, SVG figures and manuscript files.

Before re-running, confirm these local paths and digests (full SHA-256 values are pinned in [methods.md](methods.md)):

- `data/lipi/src/assets/data/xlits.csv` (`02dd0efd…`), `inscriptions.csv` (`c36d0c26…`), `glossing.csv` (`db71537f…`) at `yajnadevam/lipi` commit `fc8813a52e183d19c441631dc26c33a4dccbea39`.
- `data/normalized/lipi_clean_rtl_singleline.jsonl` (`9e539dae…`) and `data/normalized/mayig_wells_class_crosswalk.json` (`9fea45e1…`).
- `data/raw/2026-10-12-decipherment-claim-tests/dcs-sanskrit/` checked out at `OliverHellwig/sanskrit` commit `8aeed5a1343d0e48b64eb32af8c00e8c6eb29359`.
- `data/raw/2026-10-12-decipherment-claim-tests/mw/mw.txt` (`555ecf5a…`, Cologne `csl-orig` `v02/mw/mw.txt`).
- `data/raw/2026-10-12-decipherment-claim-tests/other-languages/` (four Perseus Latin XMLs and `sangam.parquet`) and `data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin` (`b220f3ee…`).
- Local preprint copies: `yajnadevam_cryptanalytic_decipherment.pdf` (`81c026b7…`, compiled 13 November 2024) and `raghavendra_2608.02999.pdf` (`3334b2fc…`, `arXiv:2608.02999v1`, 4 August 2026).

## 2. Exact reproduction steps

Run from the repository root with Python 3.13, NumPy 2.2, Matplotlib 3.11 and PyArrow (for `sangam.parquet`). Set `WORKERS=8` when running multiprocessing stages on memory-constrained machines.

### Study A (`experiments/2026-10-12-published-claim-tests/sanskrit-key/`)

1. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage0_audit.py` (writes `stage0/summary.json`).
2. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage1_redundancy.py` (writes `stage1/summary.json` and local `skeleton_kn5.npz`).
3. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage2_readability.py` and `stage2b_fitted.py` (write `stage2/summary.json` and `stage2/fitted_readability.json`).
4. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage3_fit.py`, followed by `stage3_validation.py`, `stage3_sens_exhaustive.py`, `stage3_sens_training.py` and `stage3_token_check.py` (write `stage3/*.json`).
5. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage3f_local_v2.py` (writes `stage3f/summary-v2.json`).
6. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage3g_constrained.py`, then `stage3g_derive.py` and `stage3h_novel_transfer.py` (write `stage3g/summary.json`, `derived.json` and `novel_transfer.json`). The preserved failed run `stage3e_languages.py` does not need to be rerun unless reproducing the rare-class failure in Amendment 2.
7. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage4_demo.py` (writes `stage4/demo.json` and `stage4/demo.md`).
8. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/stage5_power.py`, then `stage5_derive.py` and `stage5b_overlap.py` (write `stage5/summary.json`, `derived.json` and `ngram_reuse.json`).
9. `python experiments/2026-10-12-published-claim-tests/sanskrit-key/verify.py` (recomputes headline values independently at 10⁻⁹ tolerance; confirm `checks_pass: true` in `verification.json`).
10. `PREVIEW=data/raw/2026-10-12-decipherment-claim-tests/paper-figures PREVIEW_DPI=200 python experiments/2026-10-12-published-claim-tests/sanskrit-key/make_figures.py` (regenerates the three SVGs and local PNG rasters).

### Study C (`experiments/2026-10-12-published-claim-tests/allographs/`)

1. Run from `experiments/2026-10-12-published-claim-tests/allographs/`: `python allograph_test.py`, then `python diagnostics.py`, then `python verify.py`.
2. Confirm `all_agree: true` across all 43 checks in `run-2026-10-12/verification.json`.

### Printable PDF and prose check

1. Run `python tools/review_prose.py --path papers/006-sanskrit-key-calibration --no-write` and verify zero unresolved flags.
2. Render a dated PDF locally (using a new filename so earlier PDFs are not overwritten):
   `python papers/006-sanskrit-key-calibration/render_paper.py --input papers/006-sanskrit-key-calibration/manuscript.md --output output/pdf/indus_sanskrit_key_calibration_YYYY-MM-DD.pdf --figure-cache data/raw/2026-10-12-decipherment-claim-tests/paper-figures`
3. Inspect the companion `.layout.json` to confirm `margin_issues: 0`.

## 3. Technical checklist for a human Sanskritist reviewer

No human Sanskrit specialist has yet reviewed the projection, text split or lexical emulation. Ask the reviewer to inspect these specific items before posting:

1. **Fifteen-class consonant skeleton projection (`common.py`, lines 57–103).**
   - Confirm that the pooling (`k/kh`, `g/gh`, `c/ch`, `j/jh`, `t/th/ṭ/ṭh`, `d/dh/ḍ/ḍh`, `n/ṇ/ñ/ṅ/ṃ`, `p/ph`, `b/bh`, `m`, `y`, `r/ṛ/ṝ`, `l/ḷ/ḹ/ḻ`, `v`, `s/ś/ṣ/h/ḥ`) accurately mirrors `decipher.csv` and Yajnadevam's stated consonant equivalences.
   - Check whether treating vocalic `ṛ`/`ṝ` as `r` and `ḷ`/`ḹ` as `l` while deleting all other vowels (`a ā i ī u ū e o ai au`) matches how the published readings treat vocalic liquids in practice.
   - Check whether the greedy choice for signs carrying the `an` or `aṃ` value (checked against exhaustive selection in `stage3/sensitivity_exhaustive.json`) omits any legitimate phonetic reading allowed by `xlits.csv`.

2. **Sandhi versus unsandhied DCS splits (`stage1_redundancy.py`, `stage3_sens_training.py`).**
   - Verify the split of the six DCS texts: unsandhied pausa forms with split compounds in the Ṛgveda, Atharvaveda (Śaunaka) and Arthaśāstra (723,483 training consonants) versus sandhied `# text` lines in the Śatapathabrāhmaṇa, Manusmṛti and Rāmāyaṇa (combined total 1,994,107 training consonants).
   - Assess whether external sandhi (especially word-final `-m` written as anusvara `ṃ` before consonants, and final `-s` becoming visarga or zero) introduces any bias not already bounded by the four-way sensitivity (`baseline`, `unsandhied`, `anusvara_m`, `both`, moving the key from 1.2 to 2.4 standard deviations while keeping the order-only statistic between −0.55 and +0.60).
   - Judge whether classical prose, Vedic hymns and technical sūtra text form a fair reference class for evaluating claimed "grammatically correct post-Vedic Sanskrit" seal phrases, or whether an additional nominal-compound or epigraphic Sanskrit reference should be noted as future work.

3. **Dictionary acceptance rules (`stage2_readability.py`, `stage0_audit.py`, `stage4_demo.py`).**
   - Inspect the two lexicons: Monier-Williams `k1` headwords (116,151 skeletons, which retain roots, grammatical terms and lexicographers' words) versus DCS attested lemmas (12,767 skeletons, which exclude unattested headwords in line with the preprint's removal rule).
   - Check the optional final ending set `{∅, s, m, n, y, t, sy}` and the stem-length cutoffs (`m = 1` vs `m = 2`): confirm whether any frequent nominal or verbal inflectional suffix is missing, and whether adding stricter morphological or syntactic filters (as in Nehrdich's March 2025 INDOLOGY dependency-parser check) would alter the claim that the unicity-distance readability criterion itself has near-zero redundancy.
   - Spot-check the departure counts in `stage0/summary.json` (126 inserted *s* or visarga, 57 *m*, 43 *t*, 33 *d*) and the random-key segmentations in `stage4/demo.md` to confirm that the emulated segmentation matches the freedom used in the published `glossing.csv`.

## 4. Remaining pre-submission gates

- [ ] Assign author names, affiliations, correspondence email and target preprint server (e.g. arXiv `cs.CL` or OSF Preprints).
- [ ] Complete the human Sanskritist review in Section 3 and record any resulting clarifications.
- [ ] Run an independent verification outside the original author session to move the underlying experiment packages above the `submitted` verification tier.
- [ ] Confirm no rights-unverified raw files are included in any supplementary archive uploaded with the preprint.
- [ ] Generate and visually inspect the dated submission PDF with `render_paper.py`.
