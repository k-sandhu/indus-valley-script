"""Write the run 2P extraction tables from reviewed identity fields."""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

OBJECT_FIELDS = 'row_id,site_code,site,site_as_published,country,baseline_volume,baseline_year,excavation,season,registration,other_numbers,findspot,depth_or_layer,period_or_phase,object_type,object_subtype,material,primary_publication,publication_year,page,pdf_page,plate_or_figure,photo_published,drawing_published,transcription_published,other_publications,row_basis,inscription_status,catalogue_status,excavated_before_baseline,possible_duplicate_of,extraction_note,extracted_by'.split(',')
SITE_FIELDS = 'site_code,site,sources_read,best_publication,rows_individual,rows_enumerated,rows_uncertain_status,rows_possibly_in_cisi3,season_blocks,count_statements,marks_outside_scope,groups_without_count,unread_sources,notes'.split(',')
SITES = {'NHT':'Nuhato','TJB':'Taloor Ji Bhit','LKD':'Lakhanjo-daro','GNW':'Ganweriwala','CHN':'Chanhu-daro','WTW':'Wattoowala','CHL':'Cholistan sites','RJP':'Rajanpur','HRP':'Harappa','MHJ':'Mohenjo-daro','new':'Other Pakistani sites'}

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, fields, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def ranges(nums):
    nums = sorted(set(map(int,nums)))
    out = []
    for n in nums:
        if out and n == out[-1][-1]+1:
            out[-1].append(n)
        else:
            out.append([n])
    return ','.join(str(v[0]) if len(v)==1 else f'{v[0]}-{v[-1]}' for v in out)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser()
    p.add_argument('package',type=Path)
    p.add_argument('raw_parent',type=Path)
    a=p.parse_args()
    package=a.package.resolve()
    raw_parent=a.raw_parent.resolve()
    out=package/'extraction/P'
    raw=raw_parent/'run2P'
    held=raw_parent/'run1a/text'
    acquired=raw/'text'
    candidates=read_csv(package/'acquisition/candidate-pages-1a.csv')
    registers=read_csv(package/'acquisition/source-register-1a.csv')+read_csv(package/'acquisition-web/source-candidates-1b.csv')
    objects=[]
    merges=[]
    def add(code,source,pdf,**fields):
        baseline=('CISI 3.1',2010) if code in ('HRP','MHJ') else ('CISI 3.2',2019) if code=='CHN' else ('CISI 2',1991)
        row={key:'' for key in OBJECT_FIELDS}
        row.update(site_code=code,site=SITES[code],site_as_published=SITES[code],country='Pakistan',baseline_volume=baseline[0],baseline_year=str(baseline[1]),primary_publication=source,pdf_page=str(pdf),photo_published='unknown',drawing_published='unknown',transcription_published='unknown',row_basis='individual',inscription_status='stated',catalogue_status='post-catalogue',excavated_before_baseline='unknown',extracted_by='codex gpt-6.1-sol run 2P')
        row.update(fields)
        objects.append(row)
        return row

    old=add('NHT','nuhato-2018-held',41,season='1973',object_type='seal',object_subtype='rectangular',publication_year='2018',page='41-42',plate_or_figure='Figure35',transcription_published='no',excavated_before_baseline='yes',extraction_note='Earlier find; figure caption on p. 42')
    recent=add('NHT','nuhato-2018-held',41,season='March2018',object_type='seal',object_subtype='square',material='terracotta',publication_year='2018',page='41',plate_or_figure='Figure 34',findspot='Trench#1; eastern slopes of Mound “C”',depth_or_layer='almost ten centimeters',transcription_published='no',excavated_before_baseline='no',extraction_note='Same discovery described on p. 14')
    add('LKD','lkd-biagi-2022',13,site_as_published='Lakheen-Jo-Daro',season='1996',other_numbers='12',findspot='Mound A, Trench D',object_type='tablet',object_subtype='rectangular',material='copper',publication_year='2022',page='14',plate_or_figure='Fig. 8: 12',drawing_published='yes',transcription_published='yes',excavated_before_baseline='no',extraction_note='Catalogue item 12; context on PDF p. 6; table on PDF p. 18')
    add('GNW','gnw-parpola-2016',1,season='2007',object_type='tablet',material='terracotta',publication_year='2016',page='7',transcription_published='no',excavated_before_baseline='no',extraction_note='Earlier surface-survey find distinguished from the 2015 find')
    add('GNW','gnw-parpola-2016',1,season='November-December 2015',object_type='tablet',material='terracotta',publication_year='2016',page='7',transcription_published='no',excavated_before_baseline='no',extraction_note='Surface-survey find')

    # Explicit catalogue references in the comparative article. Ranges lacking
    # separately identified members remain site-level groups.
    skip={'H-311','H-318'}
    seals=set('H-543 H-544 H-670 H-1037 H-585 H-407 H-1027 M-1233 M-715 M-896 M-915 M-1367 M-77 M-729 M-395 M-161 M-1080 M-939 M-35 M-875 M-179 M-749 M-224 M-178 M-673 M-32 M-712 M-984 M-1063 M-956 M-1781'.split())
    rods={f'M-{n}' for n in range(2086,2116)}|{'M-1650','M-1651','M-1652','H-2570','H-1016','H-1517'}
    type_unknown={'M-1017','M-1430','H-1971'}
    seen={}
    article_rows=[]
    for n in range(2,8):
        text=(acquired/'hrp-parpola-2019'/f'p{n:04}.txt').read_text(encoding='utf-8')
        for m in re.finditer(r'\b[HM]-\d+(?:[A-Z])?\b',text):
            ident=m.group()
            if ident in skip:
                continue
            if ident in seen:
                merges.append({'kept_row_id':seen[ident],'merged_source':'hrp-parpola-2019','merged_page':f'PDF {n}','basis':f'Repeated explicit catalogue identifier {ident} within the same publication'})
                continue
            code='HRP' if ident.startswith('H-') else 'MHJ'
            kind='other' if ident in rods else 'seal' if ident in seals else 'inscribed-pottery' if ident=='H-1398' else 'uncertain' if ident in type_unknown else 'tablet'
            omitted={'M-1652','M-2100','M-2101','M-2105','M-2114','M-2115'}
            row=add(code,'hrp-parpola-2019',n,other_numbers=ident,object_type=kind,object_subtype='rod' if ident in rods else '',material='faience' if ident in {'H-1808','H-1942'} else '',publication_year='2019',catalogue_status='in-baseline-catalogue',photo_published='no',drawing_published='no',transcription_published='no' if ident in omitted else 'yes',extraction_note='Explicit CISI reference; comparative citation' if kind!='uncertain' else 'Explicit CISI reference; class not resolved at this citation')
            article_rows.append(row)
            seen[ident]=row
    # The additional object is explicitly distinguished from the CISI references.
    extra=add('MHJ','hrp-parpola-2019',2,other_numbers='Fig. 1, no. 26',object_type='other',object_subtype='rod',publication_year='2019',plate_or_figure='Fig. 1, no. 26',catalogue_status='possibly-in-cisi3',photo_published='no',drawing_published='no',transcription_published='yes',extraction_note='Dales find cited without a CISI identifier; season not specified for this object')
    # Later paper contains two additional, explicit comparative CISI references.
    for ident in ('M-874','M-1126'):
        add('MHJ','lkd-biagi-2022',13,other_numbers=ident,object_type='uncertain',publication_year='2022',page='14',catalogue_status='in-baseline-catalogue',transcription_published='yes',extraction_note='Comparative CISI reference; object class not stated at this citation')

    # Number sites in primary-source reading order. The additional rod belongs
    # immediately after the first six references on PDF p. 2.
    at=next(i for i,r in enumerate(objects) if r.get('other_numbers')=='M-2115')+1
    objects.remove(extra)
    objects.insert(at,extra)
    counters=Counter()
    for row in objects:
        code=row['site_code'];counters[code]+=1
        row['row_id']=f'XP-{code}-{counters[code]:03}'
    for record in merges:
        record['kept_row_id']=record['kept_row_id']['row_id']
    merges.insert(0,{'kept_row_id':recent['row_id'],'merged_source':'nuhato-2018-held','merged_page':'14','basis':'Same excavation discovery in Trench 1, season 2018; compatible type and material; catalogue discussion and trench account'})
    write_csv(out/'objects-P.csv',OBJECT_FIELDS,objects)
    write_csv(out/'merge-log-P.csv',['kept_row_id','merged_source','merged_page','basis'],merges)

    pages={}
    for sid in ('nuhato-2018-held','chanhu-surface2017-held'):
        for path in (held/sid).glob('p*.txt'):
            pages[sid,int(path.stem[1:])]='candidate'
    for folder in acquired.iterdir():
        for path in folder.glob('p*.txt'):
            pages[folder.name,int(path.stem[1:])]='candidate'
    journal_sites=defaultdict(lambda:defaultdict(set))
    for r in candidates:
        if r['site_code'] in ('HRP','MHJ') and r['source_id'].startswith(('puratattva-','man-environment-')):
            key=(r['source_id'],int(r['pdf_page']))
            pages[key]='candidate'
            journal_sites[r['site_code']][r['source_id']].add(int(r['pdf_page']))
    for sid,n in list(pages):
        if sid in ('chn-desset-2022','nht-journal-2019','lkd-doam-notice','rjp-doam-notice'):
            pages[sid,n]='context'
    pages['lkd-biagi-2022',18]='table'
    write_csv(out/'pages-read-P.csv',['source_id','pdf_page','purpose','image_viewed'],[dict(source_id=sid,pdf_page=n,purpose=purpose,image_viewed='no') for (sid,n),purpose in sorted(pages.items())])
    source_pages=defaultdict(list)
    for sid,n in pages:
        source_pages[sid].append(n)
    exposure=[]
    for sid,nums in sorted(source_pages.items()):
        exposure.append(dict(source_id=sid,agent='codex gpt-6.1-sol run 2P',access='automated page-text scan; filtered metadata output',pages=ranges(nums),purpose='Object eligibility and identity extraction' if not sid.startswith(('man-environment-','puratattva-')) else 'Amendment 1 pre-baseline scope and count-candidate scan'))
    for sid,nums,purpose in [
        ('nuhato-2018-held',[14,20,28,41,42,43,46,47,52,53,94,108,109,113,117,121],'Overbroad filtered preview exposed restricted descriptive or numeric material; filter subsequently narrowed'),
        ('gnw-parpola-2016',[1],'Overbroad filtered preview exposed restricted descriptive material; filter subsequently narrowed'),
        ('chn-desset-2022',[1,2,3,4,5,6,7,8,9,10,11,20,21,22,23,24,25],'Witness identification and overbroad preview; restricted descriptive or numeric material exposed'),
    ]:
        exposure.append(dict(source_id=sid,agent='codex gpt-6.1-sol run 2P',access='agent-visible text preview; exposure deviation',pages=ranges(nums),purpose=purpose))
    exposure.append(dict(source_id='chn-desset-2022',agent='codex gpt-6.1-sol run 2P',access='temporary render and automated OCR; no human image view',pages='1-2,4',purpose='Missing usable text layer; renders removed after text saved'))
    exposure.append(dict(source_id='chanhu-surface2017-held',agent='codex gpt-6.1-sol run 2P',access='temporary render and automated OCR; no human image view',pages='2,52,126,140,172,196,198,236',purpose='Integrity check of empty held page-text files; renders removed after text saved'))
    write_csv(out/'exposure-log-P.csv',['source_id','agent','access','pages','purpose'],exposure)

    count_candidates=[]
    count_pat=r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred)\s+(?:(?:inscribed|Harappan|Indus|steatite|terracotta|faience|clay|square|rectangular|copper|ivory|bone|miniature|intact|broken|complete|stone|seal)\s+){0,4}(?:seals?|sealings?|tablets?|rods?|graffiti|sherds?)\b'
    journal_keys=defaultdict(set)
    for code,by_source in journal_sites.items():
        for sid,nums in by_source.items():
            for n in nums:
                journal_keys[sid,n].add(code)
    for (sid,n),codes in sorted(journal_keys.items()):
        txt=(held/sid/f'p{n:04}.txt').read_text(encoding='utf-8',errors='replace')
        for val in dict.fromkeys(re.sub(r'\s+',' ',m.group()) for m in re.finditer(count_pat,txt,re.I)):
            count_candidates.append(dict(source_id=sid,pdf_page=n,candidate_site_codes=';'.join(sorted(codes)),count_phrase=val,attribution='unresolved; same-page site co-occurrence does not assign a count to a site',row_action='no rows; Amendment 1'))
    write_csv(out/'count-candidates-P.csv',['source_id','pdf_page','candidate_site_codes','count_phrase','attribution','row_action'],count_candidates)

    best={'NHT':'nuhato-2018-held','LKD':'lkd-biagi-2022','GNW':'gnw-parpola-2016','CHN':'chn-didier-2017','RJP':'rjp-doam-notice','HRP':'hrp-parpola-2019','MHJ':'hrp-parpola-2019'}
    unread={
        'NHT':'nht-routes-2025: full text not held, paywalled; nht-journal-2019: report PDF not held, landing page only',
        'TJB':'nht-routes-2025: full text not held, paywalled',
        'LKD':'lkd-dawn-2014: not downloaded in run 1B; no download attempted in run 2P; excavation reports cited by lkd-biagi-2022 not supplied',
        'CHN':'chn-desset-2022: acquired 40-page witness contains CISI 3.3 front matter and an unrelated essay, not the named Chanhu-daro contribution; chn-preliminary-2021: institutional record offers no document; chn-didier-2017-crai: retrieval failed in run 1B',
        'WTW':'wtw-dawn-2012: not downloaded in run 1B; no download attempted in run 2P',
        'CHL':'chl-mughal-1997: no open full copy held',
    }
    coverage={'NHT':'nuhato-2018-held:PDF 1-121; nht-journal-2019:HTML 1','LKD':'lkd-biagi-2022:PDF 1-26; lkd-doam-notice:HTML 1','GNW':'gnw-parpola-2016:PDF 1','CHN':'chanhu-surface2017-held:PDF 1-237; chn-didier-2017:PDF 1-41; chn-desset-2022:PDF 1-40','RJP':'rjp-doam-notice:HTML 1','HRP':'hrp-parpola-2019:PDF 1-7','MHJ':'hrp-parpola-2019:PDF 1-7; lkd-biagi-2022:PDF 13'}
    seasons={'NHT':'1973; March2018: nuhato-2018-held','LKD':'1996: lkd-biagi-2022; 2017 context references not individually itemised','GNW':'2007; November-December 2015: gnw-parpola-2016','CHN':'2015-2017: chn-didier-2017, pre-baseline count-only; later seasons remain unread','HRP':'Historical catalogue references; seasons not supplied in comparative citations','MHJ':'Historical catalogue references; Dales find season not specified at the individual citation'}
    counts={'NHT':'seal=2 plus seal blank=1 (nuhato-2018-held pp. 41-42); two inscribed finds represented by two rows; blank excluded','GNW':'tablet=1 from 2007 and tablet=1 from 2015 (gnw-parpola-2016 p. 7)','CHN':'seal=0 in renewed excavations to that point (chn-didier-2017 PDF 25, printed 24); an earlier-excavation fragment is discussed on PDF 30; no qualifying post-baseline count available','MHJ':'rod=1 cited without a CISI identifier (hrp-parpola-2019 PDF 2)'}
    marks={'NHT':'graffiti sherds=2 (nuhato-2018-held p. 42); surface graffiti sherd=1 (p. 53); no individual attribution to Indus script at those locators','CHN':'No qualifying bulk count established; general ceramic assemblage counts excluded'}
    groups={'NHT':'Potsherds linked generally to Indus script, without an object count or identifier link (nuhato-2018-held p. 53)','LKD':'Indus stamp seals mentioned without an object count or individual script attribution (lkd-biagi-2022 PDF 6)','HRP':'Comparative CISI range H-311 to H-318 (hrp-parpola-2019 PDF 2); not expanded into object rows'}
    notes={
        'NHT':'The 1973 object is proposed post-catalogue by report date and flagged earlier than the baseline; containment is reserved for run 3. The blank and undifferentiated tablet groups do not yield rows.',
        'TJB':'No readable object source supplied. Coverage remains open.',
        'LKD':'Only catalogue item 12 is explicitly attributed to Indus writing. Other catalogue entries are not counted merely because they share an object class. Official notice contains no object list.',
        'GNW':'Two physical survey finds are distinguished by year; no individual identifiers printed.',
        'CHN':'Both readable excavation publications predate CISI 3.2 and give no rows under Amendment 1. The assigned inclusion override for the 2022 contribution could not be applied to an absent contribution.',
        'WTW':'Coverage remains open because the identified news source is unread.',
        'CHL':'Coverage remains open for all assigned settlement aliases because the monograph is unread.',
        'RJP':'The official notice identifies a Faisalabad District settlement and cites a 1996 inventory. Its equation with the intended Rajanpur find lead is unresolved; no inscribed object is reported in the notice.',
        'HRP':'Every explicit CISI number is in-baseline-catalogue by instruction. Comparative mentions are audit rows, not post-catalogue finds. The author deposit cover says 2020; article footer says 2019, retained as publication_year. Journal sweep retained count candidates without assigning ambiguous comparative counts to this site.',
        'MHJ':'Every explicit CISI number is in-baseline-catalogue by instruction. The additional Dales find lacks a CISI identifier and a specific season, so is possibly-in-cisi3. Repeated references within a paper merge by identifier only. Two further references occur in lkd-biagi-2022. Journal count candidates remain unassigned.',
        'new':'No additional Pakistani site with a qualifying individually located find was established from the assigned sources. This is a coverage statement for these sources.'
    }
    site_rows=[]
    for code,site in SITES.items():
        subset=[r for r in objects if r['site_code']==code]
        src=coverage.get(code,'')
        journal='; '.join(f'{sid}:PDF {ranges(nums)}' for sid,nums in sorted(journal_sites[code].items()))
        if journal:
            src+='; '+journal
        counttext=counts.get(code,'')
        if code in ('HRP','MHJ'):
            counttext+=('; ' if counttext else '')+'Pre-baseline journal count candidates: count-candidates-P.csv; site attribution unresolved; no rows under Amendment 1'
        site_rows.append(dict(site_code=code,site=site,sources_read=src,best_publication=best.get(code,''),rows_individual=sum(r['row_basis']=='individual' for r in subset),rows_enumerated=sum(r['row_basis']=='enumerated-count' for r in subset),rows_uncertain_status=sum(r['inscription_status']=='uncertain' for r in subset),rows_possibly_in_cisi3=sum(r['catalogue_status']=='possibly-in-cisi3' for r in subset),season_blocks=seasons.get(code,''),count_statements=counttext,marks_outside_scope=marks.get(code,''),groups_without_count=groups.get(code,''),unread_sources=unread.get(code,''),notes=notes[code]))
    write_csv(out/'site-notes-P.csv',SITE_FIELDS,site_rows)

    audit=[]
    for rec in json.loads((raw/'text-extraction.json').read_text()):
        sid=rec['source_id'];entry=next(r for r in registers if r['source_id']==sid)
        source=Path(entry['local_path'])
        digest=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
        assert digest==entry['sha256'],sid
        blanks=[]
        for path in sorted((acquired/sid).glob('p*.txt')):
            if not path.read_text(encoding='utf-8').strip():
                blanks.append(int(path.stem[1:]))
        assert not blanks or sid=='chn-desset-2022' and blanks==[2,4]
        audit.append(dict(source_id=sid,pages=rec['pages'],source_sha256=digest,hash_verified=True,blank_pages=blanks,ocr_pages=[1,2,4] if sid=='chn-desset-2022' else [],retained_renders=0))
    repaired=[{'pdf_page':int(p.stem[1:]),'bytes':p.stat().st_size,'blank_after_ocr':not p.read_text(encoding='utf-8').strip()} for p in sorted((acquired/'chanhu-surface2017-held').glob('p*.txt'))]
    (out/'source-audit-P.json').write_text(json.dumps({'saved_file_integrity':'pass','protocol_hash':hashlib.sha256((package/'PROTOCOL.md').read_bytes()).hexdigest(),'sources':audit,'held_empty_pages_ocr_checked':repaired},indent=2)+'\n',encoding='utf-8')

    lines=['We extracted the assigned readable sources into part P’s object and site tables. Counts below describe source records; catalogue containment is left to run 3.','', '| Site | Individual | Enumerated | Stated | Uncertain | Post-catalogue | Possibly in CISI 3 | In baseline | Best readable publication |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
    for row in site_rows:
        subset=[r for r in objects if r['site_code']==row['site_code']]
        cats=Counter(r['catalogue_status'] for r in subset)
        lines.append(f"| {row['site']} ({row['site_code']}) | {row['rows_individual']} | {row['rows_enumerated']} | {sum(r['inscription_status']=='stated' for r in subset)} | {row['rows_uncertain_status']} | {cats['post-catalogue']} | {cats['possibly-in-cisi3']} | {cats['in-baseline-catalogue']} | {row['best_publication'] or 'None held'} |")
    lines+=['','No comparable printed total disagrees with the extracted count. Nuhato’s total includes one excluded blank. The earlier Chanhu-daro count covers earlier excavation work and cannot establish the later total. Journal count candidates are retained separately because same-page site mentions do not establish their attribution.','', 'The unread sources are listed by site below.']
    for code,value in unread.items():
        lines.append(f'- {SITES[code]}: {value}.')
    lines+=['','The 2022 Chanhu-daro contribution is missing from the acquired witness. Its objects therefore remain unextracted. No new download was attempted. The RJP inventory notice’s relationship to the intended find lead also remains unresolved.','', 'Selftest: see selftest-P.json. It checks artifact structure, identifiers, locators, counts and restricted-content rules. The source audit verifies all eight acquired-file hashes and all 118 extracted page files. The two blank page files are deliberate. Eight empty held page-text files were checked by OCR, with results saved separately in run2P. Temporary OCR renders were removed.','', 'Deviation: early text previews exposed restricted descriptive or numeric source material before the filters were narrowed. The exposure log identifies affected sources and pages. This agent must be treated as exposed for those pages in later confirmation work. The extraction files retain identity and context fields only. All work stayed within the owned paths; no packages, downloads or git mutations were made.','', 'Outputs: objects-P.csv, site-notes-P.csv, merge-log-P.csv, pages-read-P.csv, exposure-log-P.csv, count-candidates-P.csv, source-audit-P.json, selftest-P.json and this final.md are under experiments/2026-10-21-post-catalogue-finds/extraction/P/. Reusable scripts are in the same directory. The eight sources’ page text and extraction manifest are under data/raw/2026-10-21-post-catalogue-finds/run2P/.']
    (out/'final.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'object_rows':len(objects),'per_site':dict(counters),'pages_read':len(pages),'merge_records':len(merges),'count_candidates':len(count_candidates),'source_hashes':'pass'}))

if __name__=='__main__':
    try:
        main()
    except OSError as exc:
        if exc.errno in (28,112):
            print('Disk write failed; stop the run at the current output step.',file=sys.stderr)
        raise
