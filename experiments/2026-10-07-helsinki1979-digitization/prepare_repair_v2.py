"""Preserve the unevaluated v1 candidate and prepare a new pre-reference freeze."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
if (HERE/'layout_v3.py').exists() or (HERE/'freeze_repair_v2.py').exists():
    raise FileExistsError('Construction already complete; preserve the frozen replacement files')
code=(HERE/'layout_v2.py').read_text(encoding='utf-8')
needle="result.sort(key=lambda r:r['center'])"
replacement="""result.sort(key=lambda r:r['center'])
    # Ordinary page types have two broad text columns. Row counts remain unconstrained.
    expected=[(c*.443+(.1185 if side=='left' else .4495))*width for c in range(2)]
    result=[min([r for r in result if abs(r['center']-x)<35],key=lambda r:abs(r['center']-x))
            for x in expected if any(abs(r['center']-x)<35 for r in result)]"""
assert needle in code
(HERE/'layout_v3.py').write_text(code.replace(needle,replacement),encoding='utf-8')
driver=(HERE/'freeze_repair.py').read_text(encoding='utf-8')
driver=driver.replace('import layout_v2 as L','import layout_v3 as L')
driver=driver.replace("OUT=HERE/'repair/2026-10-07-v1'","OUT=HERE/'repair/2026-10-07-v2'")
driver=driver.replace("'layout_v2.py','freeze_repair.py'","'layout_v3.py','freeze_repair_v2.py','evaluate_repair.py'")
driver=driver.replace("countfolder=blind/'page-count-source';countfolder.mkdir()", "countfolder=blind/'page-count-source';countfolder.mkdir()\n        count_detections=[]")
driver=driver.replace("for page in count_pages:\n            pix=", "for page in count_pages:\n            _,count_rows,count_meta=L.process(doc,page)\n            count_detections.append(dict(pdf_page=page,rows=count_rows,layout=count_meta))\n            pix=")
driver=driver.replace("predictions.sort(key=lambda r:r['sample_index']);", "P.write(OUT/'count-page-detections.json',dict(status='Frozen evaluation',pages=count_detections))\n    predictions.sort(key=lambda r:r['sample_index']);")
driver=driver.replace("freeze_sha256=P.sha(freeze_path),reference_exists=False,source_count_pages=count_pages)","freeze_sha256=P.sha(freeze_path),reference_exists=False,source_count_pages=count_pages,\n       count_detections_sha256=P.sha(OUT/'count-page-detections.json'))")
(HERE/'freeze_repair_v2.py').write_text(driver,encoding='utf-8')
protocol=HERE/'PROTOCOL.md'
protocol.write_text(protocol.read_text(encoding='utf-8')+'''

### Amendment, 7 October 2026: unlabelled-frame audit before any new reference

The repair/2026-10-07-v1 candidate was frozen and sampled, but no reference was started or released. Its unlabelled frame showed 125 candidate rows on an ordinary page because glyph-like numeric OCR strings formed extra margin clusters. Preserve this whole candidate as Superseded before evaluation. The replacement copies layout_v2.py to layout_v3.py and restricts ordinary-page OCR field candidates to within 35 PDF points of the documented two-column margin neighbourhoods. Native print features still discover the extra columns on compact end-sorted pages; row counts remain unconstrained. Freeze the replacement and evaluator before its source sample or reference. No v1 candidate accuracy is known.
''',encoding='utf-8')
(HERE/'repair/2026-10-07-v1/SUPERSESSION.md').write_text('''# Candidate superseded before reference

Status: Superseded. The unlabelled frame exposed false OCR field columns on ordinary pages. No independent reference or accuracy outcome exists for this candidate. Its code, freeze, frame, source sample and predictions remain unchanged. The replacement is repair/2026-10-07-v2, with a source-layout field-neighbourhood constraint and the same recognizer.
''',encoding='utf-8')
print('Prepared replacement code; original candidate preserved')
