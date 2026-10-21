"""Remove only explicitly selected, unread A1 scratch renders after disk exhaustion.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/clear_unused_renders.py --raw data/raw/2026-10-21-head-direction-corpora
Acquisitions, displayed page images and transcriptions are retained. The deletion journal lists every removed scratch path.
"""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw',type=Path,required=True)
    a = ap.parse_args()
    raw = a.raw.resolve()
    specifications = [
        ('1913-14','dli35545',[9,10,11,163,164,*range(166,176),*range(182,195)]),
        ('1903-04','ignca21816',[1,2,3,4,9,10,11,12,194,195,196,197,198,202,209,211,212,213,214]),
        ('1903-04','dli207529',[1,2,4,5,8,9,10,193,195,199,221,223])]
    deleted = []
    for year,scan,pages in specifications:
        directory = (raw/('pages-asi-'+year)).resolve()
        if directory.parent != raw:
            raise ValueError('Unexpected directory')
        for page in pages:
            path = (directory/(scan+'-p'+str(page).zfill(4)+'.png')).resolve()
            if path.parent != directory:
                raise ValueError('Unexpected target')
            if path.exists():
                deleted.append({'path':path.as_posix(),'bytes':path.stat().st_size,'page_pdf':page,'scan':scan,'reason':'unread scratch render'})
                path.unlink()
    journal = raw/'codex-a1'/'scratch-cleanup.json'
    journal.write_text(json.dumps(deleted,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'removed_unread_renders':len(deleted),'bytes_released':sum(r['bytes'] for r in deleted)}))


if __name__=='__main__':
    main()
