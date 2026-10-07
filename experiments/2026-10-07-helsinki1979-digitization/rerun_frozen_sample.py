"""Recompute only the 60 selected rows with frozen layout, OCR and recognition."""
import argparse
import json
import math
from pathlib import Path
import pymupdf as fitz
import pipeline as p


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--predictions-out',type=Path,default=p.RAW/'reviewer-sample-v1.json')
    ap.add_argument('--audit-out',type=Path,default=p.HERE/'verification/sample-rerun-v1.json');args=ap.parse_args()
    out=args.predictions_out.resolve();audit=args.audit_out.resolve()
    if not out.is_relative_to(p.RAW) or not audit.is_relative_to(p.HERE) or out.exists() or audit.exists():
        raise ValueError('Use new predictions under local raw and a new audit under the owned directory')
    p.check_freeze();selection=json.loads((p.HERE/'blind/selection.json').read_text())['rows']
    freeze=json.loads((p.HERE/'prediction-freeze.json').read_text());original_path=p.ROOT/freeze['predictions_path']
    assert p.sha(original_path)==freeze['predictions_sha256']
    original={r['sample_index']:r for r in json.loads(original_path.read_text(encoding='utf-8'))['rows']}
    recognizer=p.Recognizer(p.templates(),p.HERE/'development/classifier.pt');recomputed=[];comparisons=[]
    with fitz.open(p.PDF) as doc:
        for page in sorted({r['pdf_page'] for r in selection}):
            gray,rows,_=p.process_page(doc,page,recognizer=None)
            for selected in selection:
                if selected['pdf_page']!=page:continue
                row=next(r for r in rows if r['pdf_column']==selected['pdf_column'] and r['row_index']==selected['row_index'])
                x0,y0,x1,y1=row['glyph_xyxy_2x'];units,cost=recognizer.segment(gray[y0:y1,x0:x1])
                row['units']=units;row['sample_index']=selected['sample_index'];row['segmentation_cost']=cost;recomputed.append(row)
                before=original[row['sample_index']]
                fields=('inscription_number','classification_code','glyph_xyxy_2x','page_rotation','margin_side')
                matching_fields=all(row[k]==before[k] for k in fields)
                matches=len(units)==len(before['units']);max_confidence_delta=0.
                if matches:
                    for new,old in zip(units,before['units']):
                        matches=matches and new['x_bounds']==old['x_bounds']
                        matches=matches and [(a['template_key'],a['codes']) for a in new['alternatives']]==[(a['template_key'],a['codes']) for a in old['alternatives']]
                        if new.get('confidence') is not None and old.get('confidence') is not None:
                            max_confidence_delta=max(max_confidence_delta,abs(new['confidence']-old['confidence']))
                comparisons.append(dict(sample_index=row['sample_index'],fields_match=matching_fields,
                                        unit_boundaries_and_top5_match=bool(matches),maximum_confidence_delta=max_confidence_delta))
    out.parent.mkdir(parents=True,exist_ok=True);recomputed.sort(key=lambda r:r['sample_index'])
    out.write_text(json.dumps(dict(rows=recomputed,freeze_sha256=p.sha(p.HERE/'freeze-manifest.json')),indent=2),encoding='utf-8')
    checks=dict(sixty_recomputed=len(comparisons)==60,fields_all_match=all(r['fields_match'] for r in comparisons),
                units_all_match=all(r['unit_boundaries_and_top5_match'] for r in comparisons),
                confidence_tolerance_1e6=all(r['maximum_confidence_delta']<=1e-6 for r in comparisons))
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,
                original_sha256=p.sha(original_path),recomputed_sha256=p.sha(out),script_sha256=p.sha(__file__),rows=comparisons)
    audit.parent.mkdir(parents=True,exist_ok=True);audit.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(checks))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
