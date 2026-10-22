"""Write a plan picks file from selected wall candidates plus a JSON header (north, scale, ids, identification).
Usage: cands2picks.py <cands.json> <header.json> <out-picks.json>
header: {source_id, render, north, scale, location?, igrf_coefficients?, part, kind, identification_prefix,
         select: [cand ids], corridor_half_width_px, feature, extra_lines: [...], notes_by_cand: {id: text}}"""
import json, sys
from pathlib import Path
c = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
h = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
out = Path(sys.argv[3])
if out.exists(): raise SystemExit('exists')
by = {x['cand']: x for x in c['candidates']}
lines = []
for cid in h['select']:
    x = by[cid]
    note = h.get('notes_by_cand', {}).get(cid, '')
    lines.append(dict(id=f"{h['line_prefix']}-{cid}", part=h['part'], kind=h['kind'],
                      identification=f"{h['identification_prefix']} Candidate {cid} of {Path(sys.argv[1]).name}." + (f' {note}' if note else ''),
                      system=h.get('default_system', 'unassigned'),
                      endpoints_px=[[round(x['p0'][0], 1), round(x['p0'][1], 1)], [round(x['p1'][0], 1), round(x['p1'][1], 1)]],
                      corridor_half_width_px=h['corridor_half_width_px'], feature=h['feature'], mode='fit'))
lines += h.get('extra_lines', [])
pk = {k: h[k] for k in ['source_id', 'render', 'north', 'scale'] if k in h}
for k in ['location', 'igrf_coefficients']:
    if k in h: pk[k] = h[k]
pk['candidate_file'] = Path(sys.argv[1]).as_posix()
pk['lines'] = lines
out.write_text(json.dumps(pk, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(out, len(lines))
