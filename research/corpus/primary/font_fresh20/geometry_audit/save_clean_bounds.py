"""Preserve source-only recommended crops for a labelled development sensitivity."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import fitz

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[4]
PDF=BASE.parents[1]/'koskenniemi_parpola1979.pdf'
FROZEN=ROOT/'research/visual_digitization/font_fresh20/predictions_before_gold.json'
GAPS={
 1023:((451,458),(493,498)),1024:((493,498),(529,538)),
 1025:((529,538),(568,577)),1026:((568,577),(608,617)),
 1034:((886,894),(929,934)),1035:((929,934),(965,974)),
 1036:((965,974),(1009,1013)),1037:((1009,1013),(1044,1052)),
 1048:((1444,1449),(1480,1488)),1059:((449,456),(491,496)),
 1060:((491,496),(527,536)),1062:((567,575),(606,614)),
 1063:((606,614),(646,654)),1065:((686,694),(730,734)),
 1068:((804,810),(844,852)),1070:((883,892),(923,931)),
 1071:((923,931),(963,971)),1072:((963,971),(1002,1011)),
 1074:((1042,1050),(1081,1089)),1084:((1436,1445),(1476,1484)),
}
page=fitz.open(PDF)[29]
rows=[]
for original in json.loads(FROZEN.read_text())['rows']:
    ident=original['id'];x0,_,x1,_=original['crop_xyxy_2x']
    upper,lower=GAPS[ident]
    y0=(upper[0]+upper[1]+1)//2
    y1=(lower[0]+lower[1]+1)//2
    box=[x0,y0,x1,y1]
    clip=[v/2 for v in box]
    png=BASE/f'clean_source_row_{ident}_4x.png'
    page.get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(clip)).save(png)
    rows.append({'id':ident,'column':original['column'],'row':original['row'],
      'original_frozen_crop_xyxy_2x':original['crop_xyxy_2x'],
      'recommended_crop_xyxy_2x':box,'clean_y0_2x':y0,'clean_y1_2x_exclusive':y1,
      'recommended_clip_pdf_points':clip,
      'upper_blank_gap_y_2x_inclusive':upper,'lower_blank_gap_y_2x_inclusive':lower,
      'horizontal_bounds_unchanged':True,
      'source_context_and_named_row_visually_verified':True,
      'rendered_clean_source_crop':png.name,'rendered_crop_sha256':hashlib.sha256(png.read_bytes()).hexdigest()})
payload={'status':'Source-only clean crop recommendation AFTER reference release; development sensitivity, not new held-out validation.',
  'coordinate_units':'2x original-PDF pixels; x0/y0 inclusive, x1/y1 exclusive. PDF-point coordinates supplied separately by dividing by2.',
  'method':'All20 original labelled-row contexts checked visually. Blank raster runs separating the named target from previous/following rows were identified from source projection (gray<190, fewer than2 black pixels). Clip boundaries are gap midpoints, retaining at least1pixel margin for target ink when possible. No predicted glyph, numerical identity, score or sequence prior selected a boundary.',
  'original_pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
  'frozen_predictions_sha256':hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
  'manual_reference_sha256_unchanged':hashlib.sha256((BASE.parent/'manual_reference.json').read_bytes()).hexdigest(),
  'rows':rows,'created_utc':datetime.now(timezone.utc).isoformat()}
(BASE/'recommended_clean_bounds.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'bounds':[(r['id'],r['clean_y0_2x'],r['clean_y1_2x_exclusive']) for r in rows]}))
