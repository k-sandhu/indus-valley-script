"""Display local review packets for manual comparison.

Usage: python -I show_check_packets.py --packets JSONL --corpus CORPUS
"""
import argparse
import json
from pathlib import Path
import sys

ap=argparse.ArgumentParser()
ap.add_argument('--packets',required=True,type=Path)
ap.add_argument('--corpus',required=True)
a=ap.parse_args()
sys.stdout.reconfigure(encoding='utf-8')
for line in a.packets.open(encoding='utf-8'):
    p=json.loads(line); r=p['record']; s=p['source']
    if r['corpus']!=a.corpus: continue
    source=s['edition_lines']
    if r['source']=='cdli-data':
        start=next((i for i,l in enumerate(source) if l.strip().startswith('@seal')),0)
        source=source[start:]
    display=dict(record_id=r['record_id'],source=r['source'],object_kind=r['object_kind'],site=r['site'],die_id=r['die_id'],
        language=r['language'],language_basis=r['language_basis'],completeness=r['completeness'],doubtful=r['reading_doubtful'],
        output_lines=r['lines'],units=r['units'],tags=r['tags'],gold=r['gold'],source_lines=source,
        source_provenience=s['catalogue'].get('provenience'),source_object_type=s['catalogue'].get('object_type'),source_seal_id=s['catalogue'].get('seal_id'),
        source_edition_language=r.get('atf_edition_language'),source_catalogue_language=s['catalogue'].get('language'))
    print(json.dumps(display,ensure_ascii=False))
