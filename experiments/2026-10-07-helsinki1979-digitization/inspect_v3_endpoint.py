"""Render source-window overlays for post-outcome v3 segmentation inspection."""
from pathlib import Path
import argparse
import json
import fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'
RUN = HERE / 'repair/2026-10-08-v3'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=RAW / '2026-10-08-endpoint-inspection-v1')
    args = ap.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(RAW) or out.exists():
        raise ValueError('Use a new local raw inspection directory')
    p = json.loads((RUN / 'predictions.json').read_text())['rows']
    rows = {r['sample_index']: r for r in p}
    refs = {r['sample_index']: r for r in json.loads((RUN / 'blind/adjudicated-reference.json').read_text())['rows']}
    out.mkdir(parents=True)
    doc = fitz.open(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf')
    for i in [3, 14, 31, 32, 35, 41, 60, 65, 68, 70]:
        row = rows[i]; b = row['glyph_pdf_box']
        clip = fitz.Rect(b[0]-3, b[1]-3, b[2]+3, b[3]+3)
        pix = doc[row['pdf_page']-1].get_pixmap(matrix=fitz.Matrix(8, 8), clip=clip, alpha=False)
        source = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        result = Image.new('RGB', (source.width, source.height*2+115), 'white')
        result.paste(source, (0, 50)); result.paste(source, (0, source.height+100))
        d = ImageDraw.Draw(result)
        d.text((4, 4), f'Post-outcome source inspection: sample {i}, PDF {row["pdf_page"]}; source above, windows below', fill='black')
        d.text((4, 21), f'Reference units: {[u["strict_candidate_codes"] for u in refs[i]["units"]]}', fill='black')
        for j, u in enumerate(row['units']):
            box = u['unit_pdf_box']
            xy = [(box[0]-clip.x0)*8, (box[1]-clip.y0)*8+source.height+100,
                  (box[2]-clip.x0)*8, (box[3]-clip.y0)*8+source.height+100]
            d.rectangle(xy, outline='red', width=2)
            d.text((xy[0]+2, xy[1]+2), str(j), fill='red')
        result.save(out / f'row_{i:03}.png', optimize=True)
    print(str(out))


if __name__ == '__main__':
    main()
