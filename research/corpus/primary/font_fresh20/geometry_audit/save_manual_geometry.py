"""Serialize post-freeze, source-only acquisition geometry observations."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import fitz,numpy as np
from PIL import Image

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[4]
PDF=BASE.parents[1]/'koskenniemi_parpola1979.pdf'
FROZEN=ROOT/'research/visual_digitization/font_fresh20/predictions_before_gold.json'
REFERENCE=BASE.parent/'manual_reference.json'
diags=json.loads((BASE/'raster_diagnostics.json').read_text())
frozen=json.loads(FROZEN.read_text())
pix=fitz.open(PDF)[29].get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY)
page=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
next_ink={
  1034:'Upper fork of following printed1035.',
  1035:'Upper jar/other drawing ink of following printed1036.',
  1036:'Upper circle/linear drawings of following printed1037.',
  1037:'Upper linear/block drawings of following printed1038.',
  1048:'Upper U/compound drawings of following printed1049.',
  1062:'Upper rectangle border of following printed1063.',
  1063:'Upper rectangle border of following printed1064.',
  1065:'Upper U/other drawings of following printed1066.',
  1068:'Upper drawings of following printed1069.',
  1070:'Upper fork/groups of following printed1071.',
  1071:'Upper U/figure/curves of following printed1072.',
  1072:'Upper hatching of following printed1073.',
  1074:'Upper compound/fish drawings of following printed1075.',
  1084:'Upper hatching/diamond of following printed1085.',
}
complete={1023,1024}
marginal={1025,1026,1059,1060}
rows=[]
for r in diags['rows']:
    ident=r['id'];x0,y0,x1,y1=r['frozen_crop_xyxy_2x']
    png=ROOT/f'research/visual_digitization/font_fresh20/row_{ident}.png'
    expected=Image.fromarray(page[y0:y1,x0:x1]).resize(((x1-x0)*3,(y1-y0)*3))
    stored=Image.open(png)
    rows.append(dict(r,
      stored_png_matches_frozen_geometry_pixels=bool(np.array_equal(np.array(expected),np.array(stored))),
      stored_png_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),
      manual_target_top_truncated=ident not in complete,
      truncation_severity=('none' if ident in complete else 'marginal raster edge, about0.25pt' if ident in marginal else 'clear source ink loss'),
      manual_target_bottom_truncated=False,
      following_row_ink_visible=ident in next_ink,
      preceding_row_ink_visible=False,
      following_row_note=next_ink.get(ident,'No following-row ink observed within frozen crop.'),
      source_row_identity_checked=True,
      horizontal_target_glyph_cut_observed=False))
result={
  'status':'Post-freeze acquisition diagnosis. No score, truth or predicted glyph changed.',
  'annotator':'/root/corpus, qualitative AI visual review, not expert certification',
  'method':'All20 frozen PNGs compared with labelled original-PDF30 context images. Target row and neighbours identified visually. Approximate ink extents are thresholded raster diagnostics inside broad manual row windows; no physical text boundary or glyph code inferred.',
  'frozen_prediction_sha256':hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
  'manual_reference_sha256_unchanged':hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
  'source_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
  'summary':{'selected_rows':20,'stored_png_geometry_matches':sum(r['stored_png_matches_frozen_geometry_pixels'] for r in rows),
             'target_top_truncated':18,'clear_top_truncations':14,'marginal_top_truncations':4,
             'target_bottom_truncated':0,'following_row_ink':14,'preceding_row_ink':0,
             'complete_target_rows_without_neighbour_ink':[1023,1024]},
  'interpretation':'Fixed40.25px pitch drifts against approximately39.6px source row spacing at2x; both columns have slight vertical offsets. The later crops contain the bottom portion of the selected row and top portion of the following row. Their errors cannot be attributed purely to glyph-shape generalization.',
  'limitations':'Image geometry diagnosis does not guarantee a repaired matcher or valid full-corpus transcription. A subsequent repair/evaluation is development and cannot replace the frozen endpoint.',
  'rows':rows,'created_utc':datetime.now(timezone.utc).isoformat(),
}
(BASE/'manual_geometry_findings.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['summary']))
