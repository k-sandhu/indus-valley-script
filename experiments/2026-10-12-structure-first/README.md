# Structure before meaning

12 October 2026. A six-step program testing the sign list, image–text pairing, segmentation, numerals, method calibration on readable scripts and structural language comparison, using only material already held. It follows the [diagnosis and plan](../../knowledge/directions/structure-first-2026-10-12.md) and the [interactive research map](https://claude.ai/artifact/PN2ShkmWxYKnMS5XV77dHD).

| Read | File |
|---|---|
| Integrated results and the hypothesis ledger | [REPORT.md](REPORT.md) |
| Protocol recorded before outcomes, and its starting hashes | [PROTOCOL.md](PROTOCOL.md), [starting-manifest.json](starting-manifest.json) |
| Step 1, sign families and modifiers | [report](step1-signs/REPORT.md), [coding table](step1-signs/sign_components_v1.tsv), [second coder](step1-signs/second-coder/NOTES.md), [amendment](step1-signs/AMENDMENT-2026-10-12.md) |
| Step 2, images and texts | [report](step2-image-text/REPORT.md), amendments [1](step2-image-text/AMENDMENT-2026-10-12.md) and [2](step2-image-text/AMENDMENT-v3-2026-10-12.md) |
| Step 3, line divisions and alternation | [report](step3-segmentation/REPORT.md), amendments [1](step3-segmentation/AMENDMENT-linebreaks-2026-10-12.md) and [2](step3-segmentation/AMENDMENT-linebreaks-v3-2026-10-12.md) |
| Step 4, stroke numerals | [report](step4-numerals/REPORT.md) |
| Step 5, rehearsal on readable scripts | [report](step5-rehearsal/REPORT.md) |
| Step 6, structural comparison | [report](step6-language/REPORT.md), [typology](step6-language/typology.json), [amendment](step6-language/AMENDMENT-2026-10-12.md) |
| Independent recomputation, review and responses | [verification](verification/VERIFICATION.md), [review](review/REVIEW.md), [responses](review/RESPONSE.md) |
| Observable work, problems and repairs | [RETROSPECTIVE.md](RETROSPECTIVE.md) |

## Reproduce

Each script refuses to overwrite an existing run directory. Inputs are the local normalized Lipi files under `data/normalized/`, the local Lipi font, and the Bronze Age normalized records under `data/raw/2026-10-12-bronze-age-comparison/normalized-v4/`; none of these are in Git.

```powershell
python -X utf8 experiments/2026-10-12-structure-first/step1-signs/render_sheets.py
python -X utf8 experiments/2026-10-12-structure-first/step1-signs/analyze_step1.py --out <new step1 run> --coder2 experiments/2026-10-12-structure-first/step1-signs/second-coder/components_coder2.tsv
python -X utf8 experiments/2026-10-12-structure-first/step2-image-text/analyze_step2.py --out <new step2 run>
python -X utf8 experiments/2026-10-12-structure-first/step5-rehearsal/rehearse_segmentation.py --out <new rehearsal run>
python -X utf8 experiments/2026-10-12-structure-first/step3-segmentation/linebreaks.py --out <new line-break run>
python -X utf8 experiments/2026-10-12-structure-first/step3-segmentation/analyze_step3.py --rehearsal <rehearsal summary.json> --out <new step3 run>
python -X utf8 experiments/2026-10-12-structure-first/step4-numerals/analyze_step4.py --out <new step4 run>
python -X utf8 experiments/2026-10-12-structure-first/step6-language/analyze_step6.py --segments data/raw/2026-10-12-structure-first/step3-ivs-segments.json --out <new step6 run>
```

The map page is rebuilt with `python -X utf8 experiments/2026-10-12-structure-first/map/build_map.py . <output.html>`.

## Ownership and scope

This program owns this directory, `data/raw/2026-10-12-structure-first/` and the linked direction memo. It did not modify the concurrent [published-claim tests](../2026-10-12-published-claim-tests/PROTOCOL.md) or the Codex packages for anchor expansion, satellite screening and transmission. Published files contain authored code, aggregate outputs, sign codes and short examples; inscription sequences and rendered glyphs stay local.
