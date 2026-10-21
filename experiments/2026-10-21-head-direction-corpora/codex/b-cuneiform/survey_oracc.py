"""Survey an ORACC archive into local data; run with python -I.

Usage: python -I survey_oracc.py --archive ZIP --out NEW_DIRECTORY
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from normalize_cuneiform import safe_archive, oracc_groups


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=False)
    archive=safe_archive(a.archive)
    cat=json.loads(archive.read(next(n for n in archive.namelist() if n.endswith('/catalogue.json'))))
    (a.out/'catalogue.json').write_text(json.dumps(cat,ensure_ascii=False),encoding='utf-8')
    counts,license_counts,words=Counter(),Counter(),Counter()
    with (a.out/'groups.jsonl').open('x',encoding='utf-8') as f:
        for name in archive.namelist():
            if '/corpusjson/' not in name or not name.endswith('.json'): continue
            counts['entries']+=1
            try: data=json.loads(archive.read(name))
            except json.JSONDecodeError: counts['invalid_json']+=1; continue
            if 'textid' not in data: counts['missing_textid']+=1; continue
            license_counts[data.get('license','unverified')]+=1
            info=cat['members'].get(data['textid'],{})
            for group in oracc_groups(data,info):
                counts['seal_groups']+=1
                f.write(json.dumps(dict(text=data['textid'],metadata=info,group=group),ensure_ascii=False)+'\n')
                for t in group['tokens']: words[(t['cf'],t['gw'],str(t['pos']))]+=1
    summary=dict(counts=counts,licenses=license_counts,vocabulary=[[*k,n] for k,n in words.most_common(70)])
    (a.out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True))


if __name__=='__main__': main()
