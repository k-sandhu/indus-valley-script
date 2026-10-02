"""Fix a second, exhaustive restoration candidate frame without model scores."""
from pathlib import Path
import json, re, hashlib, fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'research/corpus/plate_audit/restoration_slots/lipi_internal'
OUT.mkdir(exist_ok=True)
source = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
rows = [json.loads(x) for x in source.read_text(encoding='utf-8').splitlines()]
selected = []
for row in rows:
    match = re.fullmatch(r'M-(\d+)([A-C]?)', row['source_cisi'])
    signs = row['signs_reading_rtl']
    if (match and 1 <= int(match[1]) <= 650 and signs.count('000') == 1
            and signs[0] != '000' and signs[-1] != '000' and row['single_line']):
        selected.append(row)
locator = json.loads((ROOT / 'research/primary_index/cisi1/artifact_locator_unverified.json').read_text())
pages = set()
for row in selected:
    row['unverified_locator_pages'] = locator.get(row['source_cisi'], [])
    pages.update(p for p in row['unverified_locator_pages'] if 40 < p <= 215)
manifest = {
    'rule': 'Every M1–M650 observational row with one internal W000, at least one known code on each side, and single_line true. No model restoration scores inspected.',
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'decision_rule': 'Source photographs must independently establish exactly one glyph span with visible partial carving. W000 count is not accepted as proof. Historical alternative readings, if consulted, are recorded after the source judgment and make any exact reconstruction a postdiction.',
    'candidates': selected,
    'locator_status': 'Root OCR locator is used only to find pages. Every object caption and side must be visually verified.'
}
(OUT/'candidate_frame.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
pdf = ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
doc = fitz.open(pdf)
for page in sorted(pages):
    doc[page-1].get_pixmap(matrix=fitz.Matrix(3,3)).save(OUT/f'cisi1_pdf{page}.png')
print(json.dumps({'candidates': len(selected), 'locator': {r['source_cisi']: r['unverified_locator_pages'] for r in selected}, 'rendered_pages': sorted(pages)}, indent=2))
