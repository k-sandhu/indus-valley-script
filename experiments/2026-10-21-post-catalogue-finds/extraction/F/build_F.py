"""Write identity rows, coverage notes, and access records for part F."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path


OBJECT_FIELDS='row_id,site_code,site,site_as_published,country,baseline_volume,baseline_year,excavation,season,registration,other_numbers,findspot,depth_or_layer,period_or_phase,object_type,object_subtype,material,primary_publication,publication_year,page,pdf_page,plate_or_figure,photo_published,drawing_published,transcription_published,other_publications,row_basis,inscription_status,catalogue_status,excavated_before_baseline,possible_duplicate_of,extraction_note,extracted_by'.split(',')
NOTE_FIELDS='site_code,site,sources_read,best_publication,rows_individual,rows_enumerated,rows_uncertain_status,rows_possibly_in_cisi3,season_blocks,count_statements,marks_outside_scope,groups_without_count,unread_sources,notes'.split(',')
SID='iar-2003-04-asi'
AGENT='codex gpt-6.1-sol run 2F'


def write(path,rows,fields):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);a=p.parse_args()
    root=a.root.resolve();pkg=root/'experiments/2026-10-21-post-catalogue-finds';out=pkg/'extraction/F';raw=root/'data/raw/2026-10-21-post-catalogue-finds/run2F'
    seeds={r['site_code']:r for r in csv.DictReader((pkg/'selection/sites-seed.csv').open(encoding='utf-8'))}
    extra={'CHG':'Chandigarh','ALG':'Alamgirpur','HUL':'Hulas','RNG':'Rangpur','BLT':'Balathal'}
    names={c:r['site'] for c,r in seeds.items()};names.update(extra)
    objects=[]
    def add(code,n,**kw):
        r=dict.fromkeys(OBJECT_FIELDS,'')
        r.update(row_id=f'XF-{code}-{n:03}',site_code=code,site=names[code],site_as_published={'GDH':'Bagasra','TKD':'Tarkhanewala-Dera'}.get(code,names[code]),country='India',baseline_volume='CISI 1',baseline_year='1987',season='2003-04',primary_publication=SID,publication_year='2011',photo_published='unknown',drawing_published='unknown',transcription_published='no',row_basis='individual',inscription_status='stated',catalogue_status='post-catalogue',excavated_before_baseline='no',extracted_by=AGENT)
        r.update(kw);objects.append(r)
    add('GDH',1,object_type='seal',material='steatite',page='32;34',pdf_page='38;40',extraction_note='context reference; membership in later group unresolved')
    add('GDH',2,object_type='seal',object_subtype='tablet',material='steatite',period_or_phase='phase-II',page='38',pdf_page='44',plate_or_figure='pl. 2[1]e',possible_duplicate_of='XF-GDH-001',extraction_note='ocr-doubtful')
    add('GDH',3,object_type='sealing',material='terracotta',findspot='Trench Eo2',period_or_phase='phase-II',page='38',pdf_page='44',plate_or_figure='pl.21')
    for n in (1,2):
        add('BHR',n,object_type='inscribed-tool',object_subtype='celt',material='copper',page='54;56',pdf_page='60;62',plate_or_figure='fig. 2[1]',row_basis='enumerated-count',extraction_note='ocr-doubtful')
    add('BHR',3,object_type='seal',material='steatite',page='56',pdf_page='62',plate_or_figure='pl. 32',extraction_note='individual reference within seasonal group')
    add('BHR',4,object_type='seal',material='steatite',page='56',pdf_page='62',plate_or_figure='pl. 32',extraction_note='broken specimen individually discussed')
    add('TKD',1,object_type='sealing',material='terracotta',page='206',pdf_page='212',plate_or_figure='pl.171')
    add('BRR',1,object_type='seal',material='steatite',period_or_phase='Mature Harappan',page='243',pdf_page='249',plate_or_figure='pl.207')
    # Order follows the volume; IDs follow each site's publication order.
    objects.sort(key=lambda r:(int(r['pdf_page'].split(';')[0]),r['row_id']))
    write(out/'objects-F.csv',objects,OBJECT_FIELDS)
    counts=collections.defaultdict(collections.Counter)
    for r in objects:
        for field in ['row_basis','inscription_status','catalogue_status']:counts[r['site_code']][r[field]]+=1
    notes=[]
    def note(code,read='',**kw):
        r=dict.fromkeys(NOTE_FIELDS,'');r.update(site_code=code,site=names[code],sources_read=read,best_publication=SID if counts[code] else 'none established for eligible objects in this volume',rows_individual=counts[code]['individual'],rows_enumerated=counts[code]['enumerated-count'],rows_uncertain_status=counts[code]['uncertain'],rows_possibly_in_cisi3=counts[code]['possibly-in-cisi3']);r.update(kw);notes.append(r)
    note('GDH',SID+':PDF 38-45 (pp.32-39)',season_blocks='2003-04:'+SID+'; itemised seal cohort: gdh-jamison-2017 (run 2G coverage)',count_statements='seal=1 (pp.32-34); inscribed seal=4; inscribed sealing=1 (p.38); cumulative seal=5; cumulative inscribed sealing=4 (p.38)',notes='The seasonal seal total remains a statement because the 2017 itemised study covers 2003 and 2004. The context reference and the separately discussed seal remain individual rows with a possible overlap. The sealing has an individual context. Two seal rows do not represent the four-seal seasonal total; the cumulative totals include earlier seasons. Published findspots for the four-seal group are not assigned to the singled-out specimen. Illustration media are unverified.')
    note('BHR',SID+':PDF 48-64 (pp.42-58; some folios unresolved)',season_blocks='2003-04:'+SID+'; excavation seal cohort: bhr-uesugi-2016 (run 2N coverage)',count_statements='inscribed copper celt=2 (pp.54-56); seal=5 (p.56)',notes='Two individually discussed seals have explicit script attribution. The five-seal total is retained as a statement; the later study covers the excavation cohort. The two tools produce count rows because no individually itemised tool catalogue is identified in the other parts. Figure-number OCR is doubtful. No object registration is printed in these passages. Illustration media are unverified.')
    note('TKD',SID+':PDF 211-219 (pp.205-213; some folios unresolved)',season_blocks='2003-04:'+SID+'; itemised campaign: tarkhanewala-2009 (run 2N coverage)',count_statements='script-attributed sealing=1; additional seal=1 (p.206)',marks_outside_scope='tablet=1 (PDF 217): no script attribution in this entry',notes='The sealing is explicitly attributed to the script. The accompanying seal has no separate script attribution in this entry and supplies no row here. The later report itemises the campaign. The plate caption is a repeat reference to the sealing. Illustration media are unverified.')
    note('BRR',SID+':PDF 231-250 (pp.225-244; some folios unresolved)',season_blocks='2003-04:'+SID+'; 2003-2005 report: puratattva-35-held (run 2N coverage)',count_statements='seal=7 (PDF 241; printed folio unresolved); script-attributed seal=1 (p.243)',notes='The seven-seal total includes classes without an explicit script attribution. One individually discussed specimen qualifies. The last seal description continues into the script-attribution sentence. The caption supplies a repeat locator. Illustration media are unverified.')
    note('JKR',SID+':PDF 29-38 (pp.23-32; some folios unresolved)',season_blocks='2003-04:'+SID,notes='The site section and neighbouring pages supply no eligible object statement. Its ceramic comparisons account for the candidate hit.')
    note('DHV',SID+':PDF 32-34',notes='Comparative reference in the Juni Kuran section; no Dholavira campaign object is reported by these pages.')
    note('KLB',SID+':PDF 32-34,52-54,211-213,231-233,390-392,632-635',groups_without_count='Earlier excavated material discussed for laboratory study (pp.627-628); no newly enumerated inscribed group',notes='CISI 3.2 baseline (2019). The 2011 publication produces no object rows under Amendment 1. Comparative references and laboratory work yield no new count of inscribed objects.')
    note('RJD','full-volume keyword sweep',notes='CISI 3.2 baseline (2019). No site hit or eligible count statement located in this volume.')
    note('BLT','full-volume keyword sweep',notes='CISI 3.2 baseline (2019). No site hit or eligible count statement located in this volume.')
    note('CHG',SID+':PDF 61-63,80-82,86',notes='The name denotes an institutional location in the candidate passages. No eligible Chandigarh object is reported.')
    note('RPR',SID+':PDF 303-305',notes='The name occurs in survey context. The keyword hit does not identify a script-bearing object from Rupar.')
    note('ALG',SID+':PDF 302-305',notes='Survey entry read in context; no eligible object statement.')
    note('HUL',SID+':PDF 302-305',notes='Survey entry read in context; no eligible object statement.')
    note('KNT',SID+':PDF 44-45',notes='Comparative reference in survey context; no eligible object statement.')
    note('RNG',SID+':PDF 44-45',notes='Chronological reference in survey context; no eligible object statement.')
    write(out/'site-notes-F.csv',notes,NOTE_FIELDS)
    merges=[dict(kept_row_id=f'XF-BHR-{n:03}',merged_source=SID,merged_page='53;54;56',basis='same paired-tool figure and explicit group of two; continuation supplies no additional object') for n in (1,2)]
    merges.extend([dict(kept_row_id='XF-TKD-001',merged_source=SID,merged_page='209 (PDF 215)',basis='plate 171 repeats the sealing cited on p.206'),dict(kept_row_id='XF-BRR-001',merged_source=SID,merged_page='PDF 250',basis='plate 207 repeats the individually described seal on p.243')])
    write(out/'merge-log-F.csv',merges,['kept_row_id','merged_source','merged_page','basis'])
    reads=list(csv.DictReader((out/'pages-read-F.csv').open(encoding='utf-8')))
    direct={int(r['pdf_page']) for r in csv.DictReader((out/'candidate-pages-F.csv').open(encoding='utf-8')) if r['context_only']=='0'}
    for r in reads:
        n=int(r['pdf_page']);r['purpose']='candidate' if n in direct else 'context';r['image_viewed']='yes' if n==44 else 'no'
    write(out/'pages-read-F.csv',reads,['source_id','pdf_page','purpose','image_viewed'])
    readnums=','.join(r['pdf_page'] for r in reads)
    exposures=[dict(source_id=SID,agent=AGENT,access='script-only text extraction and keyword sweep',pages='1-641',purpose='SHA256 verification; page-text recovery; footer indexing; no graphic interpretation'),dict(source_id=SID,agent=AGENT,access='metadata-filtered source review; reader exposed',pages=readnums,purpose='Extract identity and context; early preview filtering allowed restricted descriptive fragments'),dict(source_id=SID,agent=AGENT,access='cropped image viewed',pages='44',purpose='Printed footer number only; image deleted immediately after inspection'),dict(source_id=SID,agent=AGENT,access='script-only temporary grey renders',pages='see page-basis-v2-F.csv; footer diagnostics',purpose='English OCR at 300 dpi; render deleted after each OCR call')]
    write(out/'exposure-log-F.csv',exposures,['source_id','agent','access','pages','purpose'])
    coordinator=json.loads((pkg/'acquisition-coordinator/manifest-proposals-coordinator.json').read_text(encoding='utf-8'))
    rec=next(r for r in coordinator['sources'] if r['id']==SID)
    supplement=dict(source_id=SID,title=rec['title'],publication_year='2011',volume_year='2003-04',pdf_pages=641,sha256=rec['fetch']['sha256'],url=rec['fetch']['url'],provenance='acquisition-coordinator/manifest-proposals-coordinator.json',rights='rights-unverified',year_confirmation='PDF 1 title; PDF 2 publication statement; PDF 3 foreword',status='local supplemental source record; shared registers unchanged')
    write(out/'source-register-F.csv',[supplement],list(supplement))
    decisions=[]
    for n in sorted(direct):
        if n<5: code='';decision='bibliographic material; no object entry'
        elif 29<=n<=37:code='JKR';decision='ceramic comparison; no eligible object'
        elif 38<=n<=44:code='GDH';decision='object evidence or context in Bagasra section'
        elif 48<=n<=63:code='BHR';decision='object evidence or paired illustration reference'
        elif 211<=n<=218:code='TKD';decision='object evidence; tablet lacks script attribution' if n==217 else 'object evidence or repeated plate locator'
        elif 231<=n<=249:code='BRR';decision='object evidence or ceramic context'
        elif n in (633,634):code='KLB';decision='laboratory-study context; Amendment 1 applies'
        elif n==304:code='RPR';decision='survey context; no eligible object'
        elif n==81:code='CHG';decision='institutional-location and later-period references'
        else:code='';decision='descriptive vocabulary; no script-attributed object'
        decisions.append(dict(source_id=SID,pdf_page=n,assigned_site_code=code,decision=decision))
    write(out/'candidate-decisions-F.csv',decisions,['source_id','pdf_page','assigned_site_code','decision'])
    write(out/'new-site-decisions-F.csv',[dict(site_code=c,site=names[c],basis='Existing code supplied in the part-F instructions; no additional code assigned') for c in extra],['site_code','site','basis'])
    basis=list(csv.DictReader((out/'page-basis-v2-F.csv').open(encoding='utf-8')))
    summary=dict(authors=[AGENT],harness='Codex desktop; Python 3.13 isolated mode; Poppler 24.07; Tesseract English',source_id=SID,pdf_pages=641,text_basis=dict(collections.Counter(r['basis'] for r in basis)),candidate_pages=len(direct),reviewed_pages=len(reads),rows=len(objects),per_site={c:dict(v) for c,v in counts.items() if v},possible_duplicate_pairs=[['XF-GDH-001','XF-GDH-002']],new_fields='641 page texts with basis and hashes; observed folios; seasonal identity references',coverage='Recovery of the previously unread 2003-04 volume',deviations=['Restricted descriptive fragments reached an early tool preview. The exposure log marks the reader exposed.','The explicitly assigned source ID is absent from both shared registers. A local supplemental record cites the coordinator manifest; shared files are outside F ownership.','The raw page texts contain the requested source OCR and remain local. They are excluded from the authored-file content scan.','One cropped footer image was viewed to check a printed page number; it was immediately deleted.'],unread_sources=[],limitations=['Unresolved folios remain blank rather than being inferred.','Illustration media are unknown where text and captions do not establish the medium.'])
    (out/'summary-F.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    retrospective='We verified the source hash and recovered all pages using the requested word threshold. The older system text utility dropped footer tokens, so the final text uses bundled Poppler. Preliminary text and footer probes are preserved locally. Coordinate-based footer extraction and saved OCR identify folios without treating plate labels as page numbers.\n\nWe reviewed candidate pages and their neighbours, then checked complete relevant site sections. The tables retain individual references, overlap warnings and seasonal totals. Count-only groups covered by later itemised studies remain site statements. No local-corpus matching was attempted.\n\nAn early preview filter allowed restricted descriptive fragments. Subsequent previews used closed metadata fields and a restricted vocabulary. The exposure log records the affected review pages. The work cannot establish reader blindness.\n\nAll page text files are non-empty, including after the service interruption. No download or package installation was used. Final text recovery used 292 text-layer pages and 349 OCR pages. Each temporary render was deleted. The source record required a local supplement because the shared registers predate the coordinator acquisition.\n'
    (out/'retrospective-F.md').write_text(retrospective,encoding='utf-8')
    # Keep diagnostic records local, separate from the authored result tables.
    diag=raw/'diagnostics';diag.mkdir(exist_ok=True)
    for name in ['footer-numbers-F.csv','footer-numbers-v2-F.csv','footer-numbers-v3-F.csv']:
        src=out/name;dest=diag/name
        if src.exists():
            assert dest.resolve().is_relative_to(raw.resolve())
            if not dest.exists():src.rename(dest)
    print(json.dumps(dict(rows=len(objects),notes=len(notes),per_site=summary['per_site'])))


if __name__=='__main__':main()
