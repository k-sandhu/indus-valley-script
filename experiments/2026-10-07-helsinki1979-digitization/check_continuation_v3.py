"""Development continuation matches against the unchanged old 21-page source count."""
import argparse
import hashlib
import json
from pathlib import Path
import evaluate as E

HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned output')
    frame=HERE/'repair/2026-10-08-v3/frame.json';reference=HERE/'repair/2026-10-07-v2/blind/adjudicated-counts.json'
    frame_data=read(frame if frame.exists() else HERE/'repair/2026-10-08-development-record-v1/continuation-source-geometry.json')
    rows=frame_data['rows'];pages=read(reference)['pages'];matches=[];total_true=total_detected=physical_detected=0
    for page in pages:
        predicted=[r for r in rows if r['pdf_page']==page['pdf_page']];physical_detected+=len(predicted)
        cont=[r for r in predicted if r['line_kind']=='continuation'];total_detected+=len(cont)
        expected=page.get('continuation_lines',[]);total_true+=len(expected);used=set()
        by_key={r['occurrence_key']:r for r in predicted}
        for truth in expected:
            col=truth['column_index']-1;center=truth['ink_center_pdf']
            pool=[r for r in cont if r['pdf_column']==col and r['occurrence_key'] not in used]
            closest=min(pool,key=lambda r:abs((r['glyph_pdf_box'][1]+r['glyph_pdf_box'][3])/2-center)) if pool else None
            distance=abs((closest['glyph_pdf_box'][1]+closest['glyph_pdf_box'][3])/2-center) if closest else None
            good=closest is not None and distance<=9
            parent=by_key.get(closest['continuation_of']) if closest else None
            numbered=[r for r in predicted if r['pdf_column']==col and r['line_kind']=='numbered']
            parent_index=next((i+1 for i,r in enumerate(numbered) if parent and r['occurrence_key']==parent['occurrence_key']),None)
            if good:used.add(closest['occurrence_key'])
            matches.append(dict(pdf_page=page['pdf_page'],source_column_one_based=truth['column_index'],source_center_pdf=center,
                matched=good,distance_pdf_points=distance,proposed_key=closest['occurrence_key'] if closest else None,
                source_preceding_numbered_row_one_based=truth['follows_row_index'],proposed_preceding_numbered_row_one_based=parent_index,
                parent_agrees=good and parent_index==truth['follows_row_index']))
    matched=sum(r['matched'] for r in matches);parents=sum(r['parent_agrees'] for r in matches)
    result=dict(status='Exploratory',development_only=True,reference_reused=True,new_reference_created=False,
        frame_sha256=frame_data.get('source_frame_sha256') or E.sha(frame),old_count_reference_sha256=E.sha(reference),count_pages=21,
        physical_lines_detected=physical_detected,physical_lines_in_old_source_count=read(reference)['total_physical_lines'],
        continuation_recall=E.wilson(matched,total_true),continuation_precision=E.wilson(matched,total_detected),
        preceding_numbered_parent_agreement=E.wilson(parents,total_true),rows=matches,
        scope='Ten continuations on reused count pages; source parent row indices treated as one-based within numbered rows. Full-edition continuation coverage remains unverified.')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
