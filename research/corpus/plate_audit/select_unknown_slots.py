"""Fix a restoration audit frame before inspecting any model predictions.

All Mayig faces containing exactly one P000 are enumerated. This is a
candidate frame only: photographs determine whether it is really one slot.
"""
from pathlib import Path
import json, hashlib, fitz
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'research/corpus/plate_audit/restoration_slots'
OUT.mkdir(exist_ok=True)
rows = [json.loads(l) for l in (ROOT/'data/normalized/mayig_faces.jsonl').read_text().splitlines()]
candidates = [r for r in rows if r['signs_reading_rtl'].count('P000') == 1]
manifest = {
    'selection_rule': 'Enumerate every Mayig face with exactly one P000, prior to source inspection. No model restoration scores or candidate predictions consulted. P000 does not itself establish a one-glyph physical gap.',
    'source_faces_sha256': hashlib.sha256((ROOT/'data/normalized/mayig_faces.jsonl').read_bytes()).hexdigest(),
    'candidates': candidates,
    'decision_rule': 'Accept only if the primary photograph independently constrains exactly one glyph span and preserves partial carving or an intact surrounding surface. Reject unbounded broken ends and holes with unknown lost span. Record historical/editorial reconstructions separately as postdiction.'
}
(OUT/'candidate_frame.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
src = ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
d = fitz.open(src)
for n in [50,51,52,53,56,59,60,61,62,63,64,75,76,78,79,86,87]:
    d[n-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT/f'cisi1_pdf{n}.png')
print('Fixed',len(candidates),'candidate faces and rendered locator pages.')
