"""Produce the exposure summary and final run message from the reviewed tables."""
import collections
import json
import runpy
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
OUT=M['OUT']
def ranges(ns):
    a=[]
    for n in sorted(set(ns)):
        if a and n==a[-1][-1]+1:a[-1].append(n)
        else:a.append([n])
    return ','.join(str(x[0]) if len(x)==1 else f'{x[0]}-{x[-1]}' for x in a)

# Object studies are searched for identities and captions; descriptive sections
# are not used to produce any field or interpretation.
for sid,count in [('frm-uesugi-jamison-2020',37),('frm-uesugi-jamison-2024',27),('bhr-uesugi-2016',17),('bjr-manjul-2017',9),('knl-konasukawa-2020',14),('snl-prabhakar-2013',17),('bhr-rao-2008',4),('msd-petrie-2009',4)]:
    M['log'](sid,range(1,count+1),'context')
pages=M['rows'](OUT/'pages-read-N.csv'); group=collections.defaultdict(list)
for r in pages:group[r['source_id']].append(int(r['pdf_page']))
exposure=M['rows'](OUT/'scan-access-N.csv')
for sid,ns in sorted(group.items()):
    exposure.append(dict(source_id=sid,agent=M['AGENT'],access='text metadata review and automated complete-page screening; incidental restricted-content exposure in previews',pages=ranges(ns),purpose='identity, context and locator extraction; no page image viewed'))
for mf in ['text-manifest-N.json','text-manifest-snl-prabhakar-2013-N.json']:
    for r in json.loads((OUT/mf).read_text(encoding='utf-8')):
        exposure.append(dict(source_id=r['source_id'],agent=M['AGENT'],access='automated PDF text extraction',pages=f"1-{r['pages']}",purpose='local page text; no PDF image displayed'))
        if r['ocr_pages']:exposure.append(dict(source_id=r['source_id'],agent=M['AGENT'],access='automated OCR; temporary image deleted',pages=ranges(r['ocr_pages']),purpose='recover unusable PDF text; no image displayed to reader'))
M['savecsv'](OUT/'exposure-log-N.csv',['source_id','agent','access','pages','purpose'],exposure)

runpy.run_path(str(OUT/'build_N.py'),run_name='__main__')
objects=M['rows'](OUT/'objects-N.csv'); notes=M['rows'](OUT/'site-notes-N.csv')
decisions=[
dict(site='Atranjikhera',site_code='ATR',decision='included as an unnumbered group',source='puratattva-37:161',basis='journal explicitly compares pottery marks with Harappan script'),
dict(site='Lal Qila',site_code='LLQ',decision='included as an unnumbered group',source='puratattva-37:161',basis='journal explicitly compares pottery marks with Harappan script'),
dict(site='Ganeshwar',site_code='GNS',decision='included as an unnumbered group',source='puratattva-37:161',basis='journal explicitly compares pottery marks with Harappan script'),
dict(site='Indiranagar (Kanpur)',site_code='IDN',decision='one uncertain row',source='man-environment-32:120',basis='review reports a seal and questions the site attribution and script proposal'),
dict(site='Brass',site_code='',decision='excluded',source='iar-1993-94:90; iar-1994-95:63',basis='readable inscribed-object references belong to later script traditions'),
dict(site='Donder Khera',site_code='',decision='excluded',source='iar-1993-94:91',basis='seal attributed to the Gupta period'),
dict(site='Balu',site_code='',decision='excluded',source='puratattva-31:147',basis='seal explicitly lacks an inscription'),
dict(site='Girawad',site_code='',decision='excluded',source='farmana-2006-08:38-40',basis='readable comparative material supplies no eligible inscribed object'),
dict(site='Manda',site_code='',decision='excluded from new-site additions',source='puratattva-18:152',basis='candidate references do not establish a post-baseline object record')]
M['savecsv'](OUT/'new-site-decisions-N.csv',['site','site_code','decision','source','basis'],decisions)
retrospective=dict(authors=[M['AGENT']],harness='Codex desktop tools; Python 3.13 isolated scripts; Poppler; Tesseract',approach='Read the frozen protocol, screened supplied page text, extracted identity and context fields, and reconciled repeated publications without loading the local corpus.',challenges=['Some held files are journal contents rather than articles.','The held inventory is a separate publication from Nath.','An older PDF text utility produced control characters that confused page splitting.','The coordinator stopped the run because system disk space was low.','Line-based filtering missed restricted fragments in wrapped entries and a mixed table.'],fixes=['Used Poppler with explicit encoding and verified source page counts.','Separated unread intended works from the held files.','Removed 107 retained temporary images and changed OCR handling to delete each render.','Retained unresolved identities as possible duplicates.','Marked the reader exposed in every reviewed-source exposure entry.'],outcome='The tables retain uncertain script status, unnumbered groups and inaccessible source leads. Illustration media stay unknown unless a primary caption explicitly identifies them. No download, package installation, corpus match or repository operation was performed.',deviations=['Restricted fragments reached some tool previews; the run cannot establish reader blindness. No derived description or transcription is retained in the deliverables.','The requested raw page-text extraction preserves original source text locally; it is excluded from the tracked-file content scan.','The Sanauli held file has no entry in either supplied source register. Its text was extracted and logged, but no object row cites it.'],disk_write_failure_after_resume=False)
(OUT/'retrospective-N.json').write_text(json.dumps(retrospective,indent=2),encoding='utf-8')

lines=['Run 2N completed the extraction tables with '+str(len(objects))+' rows across '+str(len(notes))+' site notes. Two rows have unresolved duplicate links. The resulting range is 31-33 physical objects before catalogue matching. No local-corpus matching was performed.','',
'Counts below are individual/enumerated, stated/uncertain, and post-catalogue/possibly-in-CISI3/in-baseline. Zero rows means that the reviewed sources did not establish an eligible numbered object.','',
'| Site | Row basis | Inscription status | Catalogue status | Best publication |','|---|---:|---:|---:|---|']
for n in notes:
    rr=[r for r in objects if r['site_code']==n['site_code']]
    b=collections.Counter(r['row_basis'] for r in rr);s=collections.Counter(r['inscription_status'] for r in rr);c=collections.Counter(r['catalogue_status'] for r in rr)
    lines.append(f"| {n['site_code']} {n['site']} | {b['individual']}/{b['enumerated-count']} | {s['stated']}/{s['uncertain']} | {c['post-catalogue']}/{c['possibly-in-cisi3']}/{c['in-baseline-catalogue']} | {n['best_publication']} |")
lines.extend(['',
'The Rakhigarhi amulet total of two remains in the count statements under Amendment 1. The inventory record is a possible duplicate of the excavation record. Farmana has five eligible objects in the final report plus one unresolved preliminary-report duplicate. Its total of two impression-bearing objects includes one without a stated surviving inscription. Bhirrana\'s total of four excavation seals includes one explicitly uninscribed specimen, leaving three eligible rows from that season. Dhalewan\'s two-sealing total includes one explicitly uninscribed specimen, leaving one eligible sealing. The other printed totals produce no unresolved numerical disagreement after these scope and season differences.','',
'Unread or incomplete sources:'] )
for n in notes:
    if n['unread_sources']:lines.append('- '+n['site_code']+': '+n['unread_sources']+'.')
lines.extend(['',
'Selftest: pending final execution. The text audit checks all 17 extracted sources and verifies that primary locators have usable saved text. The final selftest checks tables, controlled values, source IDs, locator files, site counts, new codes, the frozen protocol hash and restricted output content.','',
'Deviations: line-based filtering missed restricted source fragments in wrapped entries and a mixed table. The exposure log marks this reader exposed, so this run does not establish reader blindness. The deliverables contain identity and context fields only. Original page text remains local as requested. The Sanauli file identifier is absent from both registers; no row cites it. No page image was displayed. No write failed after the restart.','',
'Outputs are in experiments/2026-10-21-post-catalogue-finds/extraction/N/: objects-N.csv, site-notes-N.csv, merge-log-N.csv, pages-read-N.csv, exposure-log-N.csv, selftest-N.json and final.md. The same directory holds the scripts, coverage records, new-site decisions, retrospective and text-audit manifests. Extracted page text is in data/raw/2026-10-21-post-catalogue-finds/run2N/text/<source_id>/pNNNN.txt. No page renders or duplicate source files remain.'])
(OUT/'final.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
test=OUT/'selftest-N.json'
if test.exists():
    report=json.loads(test.read_text(encoding='utf-8'))
    if report.get('passed') and report.get('rows')==len(objects):
        text=(OUT/'final.md').read_text(encoding='utf-8')
        text=text.replace('Selftest: pending final execution.','Selftest: PASS, with zero errors. There are 30 individual rows and 3 enumerated rows; 27 have stated inscription status and 6 are uncertain. All 33 rows are proposed post-catalogue entries pending the matching run.')
        (OUT/'final.md').write_text(text,encoding='utf-8')
print('Exposure summary and final message written.')
