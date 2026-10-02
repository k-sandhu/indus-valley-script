"""Source-only raster geometry diagnostics; no predicted glyph codes read.

The fixed source windows select the labelled row's drawn ink for visual
inspection. They do not infer original physical side/line boundaries.
"""
from pathlib import Path
import json, hashlib
import fitz
import numpy as np

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
SOURCE = BASE.parent / 'koskenniemi_parpola1979.pdf'
FROZEN = ROOT/'research/visual_digitization/font_fresh20/predictions_before_gold.json'
out = BASE/'geometry_audit'
out.mkdir(exist_ok=True)
page = fitz.open(SOURCE)[29]
pix = page.get_pixmap(matrix=fitz.Matrix(4,4),colorspace=fitz.csGRAY)
arr = np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
diagnostics=[]
for row in json.loads(FROZEN.read_text())['rows']:
    # Read geometry and identifiers only, never tokens/cost/predictions.
    ident,c,r,box = row['id'],row['column'],row['row'],row['crop_xyxy_2x']
    x0,y0,x1,y1=box
    center=79.5+19.8*r
    lo,hi=center-9.6,center+9.6
    sx0,sx1=int(x0*2),int(x1*2)
    sy0,sy1=int(lo*4),int(hi*4)
    occupied=np.nonzero((arr[sy0:sy1,sx0:sx1]<160).any(axis=1))[0]
    bounds=[round((sy0+int(occupied.min()))/4,2),round((sy0+int(occupied.max())+1)/4,2)] if len(occupied) else None
    # Wider original context retains source row label and both neighbours.
    cx0,cx1=(64,285) if c==0 else (313,548)
    clip=[cx0,lo-11,cx1,hi+11]
    name=f'original_row_{ident}_context_4x.png'
    page.get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(clip)).save(out/name)
    diagnostics.append({'id':ident,'column':c,'row':r,'frozen_crop_xyxy_2x':box,
        'frozen_pdf_y_interval':[y0/2,y1/2],
        'manual_row_selection_pdf_y_interval':[round(lo,2),round(hi,2)],
        'drawn_ink_y_bounds_within_window':bounds,
        'ink_window_is_geometry_diagnostic_only':True,
        'top_ink_above_frozen_crop_pt':round(max(0,y0/2-bounds[0]),2) if bounds else None,
        'bottom_ink_below_frozen_crop_pt':round(max(0,bounds[1]-y1/2),2) if bounds else None,
        'original_context_image':name,'original_context_clip_pdf_points':clip})
payload={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'frozen_predictions_sha256':hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
    'method':'Original PDF30 raster geometry, no token/cost fields inspected. Broad labelled-row windows are for manual verification, not accepted segmentation.',
    'rows':diagnostics}
(out/'raster_diagnostics.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps(diagnostics,indent=2))
