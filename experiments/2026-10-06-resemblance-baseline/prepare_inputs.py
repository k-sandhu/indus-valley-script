"""Reproduce seeded selection and source contact sheets in a new local raw folder."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    args=parser.parse_args()
    target=(RAW/args.directory).resolve()
    assert target.parent==RAW.resolve()
    target.mkdir(exist_ok=False)
    for k in ('TMP','TEMP','MPLCONFIGDIR'):
        os.environ[k]=str(target/'tmp')
    (target/'tmp').mkdir()
    from PIL import Image, ImageDraw
    import fitz
    atlas=json.loads((ROOT/'output/chart_atlas/reference.json').read_text(encoding='utf-8'))
    assert len(atlas['rows'])==687
    indices=sorted(random.Random(20261006).sample(range(687),42))
    rows=[dict(atlas['rows'][k],atlas_index=k,pilot_position=j,id=f'I{j:02d}') for j,k in enumerate(indices)]
    pinned=json.loads((RAW/'indus-selection.json').read_text(encoding='utf-8'))
    assert rows==pinned, 'Atlas reference changed from pilot source.'
    (target/'indus-selection.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    for batch in range(3):
        canvas=Image.new('RGB',(1400,800),'white')
        draw=ImageDraw.Draw(canvas)
        for j,row in enumerate(rows[batch*14:(batch+1)*14]):
            img=Image.open(ROOT/'output/chart_atlas'/row['image']).convert('RGB')
            img.thumbnail((175,320))
            col,line=j%7,j//7
            canvas.paste(img,(col*200,line*400+45))
            draw.text((col*200+5,line*400+8),row['id']+' '+row['image'],fill='black')
        canvas.save(target/f'indus-sheet-{batch}.png')
    brochure=ROOT/'data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf'
    assert hashlib.sha256(brochure.read_bytes()).hexdigest()=='f42670932eb8328494d61de1d4652534ac94f4c3ab82684f8c3fff1c91954c52'
    p=fitz.open(brochure)
    p[3].get_pixmap(matrix=fitz.Matrix(2,2)).save(target/'tamil-base-page.png')
    for name in ('ogham','tifinagh'):
        p=fitz.open(RAW/f'{name}-current.pdf')
        p[1].get_pixmap(matrix=fitz.Matrix(2,2)).save(target/f'{name}-chart.png')
    print('Verified seeded selection and regenerated source sheets:',target.name)

if __name__=='__main__':
    main()
