"""Pin held primary sources and extract page text to D: for context review."""
from pathlib import Path
import hashlib
import json
import fitz

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
ROOT=BASE.parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/contexts')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    assert (ROOT/'data/raw').resolve()==Path('D:/projects/indus_valley_script/data/raw')
    assert sha(BASE/'PROTOCOL.md')=='11c69454d6e50304b5704db0865f76abca8d84363a67a21d42e8573e256cdb6e'
    RAW.mkdir(parents=True,exist_ok=True)
    previous=json.loads((ROOT/'experiments/2026-10-24-urban-form-and-inscription-ecology/run-v3/sources.json').read_text(encoding='utf8'))
    wanted=['EAST-SHINDE2011','EAST-KHARAKWAL2011','EAST-BISHT1999','EAST-IAR1986','KENOYER2005','MK2000','MK1997','KM2010-MS','BISHT2015-PRELIM','W-S01','RAO1979','RAO1985','FT2005','CISI1','W-S04']
    result=[]
    for source in previous:
        if source['source_id'] not in wanted:continue
        p=Path(source['physical_path']).resolve()
        if not p.exists():p=(ROOT/source['logical_path']).resolve()
        record={k:source[k] for k in ['source_id','title','authors','author','year','url','acquisition_url','logical_path','sha256','bytes'] if k in source}
        assert sha(p)==source['sha256']
        record.update(physical_path=str(p),source_class='excavator, original analyst or primary catalogue',rights_status='rights-unverified; inherited source-specific terms retained',local_only=True,new_acquisition=False,source_lineage=source.get('source_lineage','Same excavation source as earlier comparison; no independent evidence from repeated edition'))
        out=RAW/(record['source_id'].lower()+'.pages.json')
        with fitz.open(p) as doc:
            if not out.exists():write(out,[{'pdf_index':i,'pdf_page':i+1,'box_points':list(page.rect),'text':page.get_text()} for i,page in enumerate(doc)])
            record['pages']=len(doc)
        record.update(extraction_physical_path=str(out),extraction_logical_path='data/raw/2026-10-24-shared-infrastructure-plan-test/contexts/'+out.name,extraction_sha256=sha(out))
        result.append(record)
        print(record['source_id'],record['pages'],flush=True)
    extras=[{'source_id':'KANMER2013','title':'Subsistence System, Paleoecology, and 14C Chronology at Kanmer, a Harappan Site in Gujarat, India','authors':['Pankaj Goyal','Anil K. Pokharia','Jeewan Singh Kharakwal','Pramod Joglekar','Y. S. Rawat','Toshiki Osada'],'year':2013,'url':'https://doi.org/10.1017/S003382220004786X','logical_path':'data/raw/2026-10-21-town-orientations-verification/dating/kanmer2013.pdf'},
    {'source_id':'KANMER-CH6','title':'Chapter 6: Pottery','authors':['Akinori Uesugi','Shiv Meena'],'year':2012,'url':'https://www.harappa.com/sites/default/files/pdf/Excavations%20at%20Kanmer,%202005-09,%20ch%206%20-%20A%20Uesugi%20%26%20S%20Meena.pdf','logical_path':'data/raw/2026-10-21-town-axes/dating/kanmer/kanmer2012ch6-uesugi-meena.pdf'},
    {'source_id':'KUSUMGAR1963','title':'Radiocarbon Dating: Results','authors':['S. Kusumgar','D. Lal','R. P. Sarna'],'year':1963,'url':'https://www.ias.ac.in/public/Volumes/seca/058/03/0141-0152.pdf','logical_path':'data/raw/2026-10-21-town-axes/dating/lothal/kusumgar1963pias.pdf'},
    {'source_id':'BISHT1982-P117','title':'Excavations at Banawali: 1974-77','authors':['R. S. Bisht'],'year':1982,'url':'https://archive.org/download/rlcp-harappan-civilization-a-contemporary-perspective-g/page/n139.jpg','logical_path':'data/raw/2026-10-21-town-axes/dating/banawali/bisht1982_p117_n139.bin','witness_type':'single original-publication page image','printed_page':117,'archive_page_image_index':139},
    {'source_id':'POKHARIA2011','title':'Archaeobotany and archaeology at Kanmer, a Harappan site in Kachchh, Gujarat: evidence for adaptation in response to climatic variability','authors':['Anil K. Pokharia','Jeewan Singh Kharakwal','R. S. Rawat','Toshiki Osada','C. M. Nautiyal','Alka Srivastava'],'year':2011,'url':'https://www.currentscience.ac.in/Volumes/100/12/1833.pdf','logical_path':'data/raw/2026-10-21-town-orientations-verification/dating/kanmer-botany2011.pdf'}]
    for record in extras:
        p=(ROOT/record['logical_path']).resolve()
        record.update(physical_path=str(p),bytes=p.stat().st_size,sha256=sha(p),local_only=True,new_acquisition=False,rights_status='rights-unverified; local-only',source_class='original excavation-project analysis')
        out=RAW/(record['source_id'].lower()+'.pages.json')
        if not p.read_bytes().startswith(b'%PDF'):
            record['witness_type']=record.get('witness_type','HTML publisher landing page; not the requested article')
            record['source_class']='original-publication page image' if record['source_id']=='BISHT1982-P117' else 'failed full-article acquisition; publisher metadata only'
            record['usable_for_sample_or_object_facts']=record['source_id']=='BISHT1982-P117'
            if record['source_id']=='KANMER2013':
                record['failure_reason']='The inherited .pdf file contains HTML. A permissive renderer produced pages, but these are not the article. Prior attempted extraction is retained as a failed witness and excluded.'
                if out.exists():record['excluded_failed_extraction']={'path':str(out),'sha256':sha(out)}
            result.append(record)
            print(record['source_id'],record['witness_type'],flush=True)
            continue
        with fitz.open(p) as doc:
            if not out.exists():write(out,[{'pdf_index':i,'pdf_page':i+1,'box_points':list(page.rect),'text':page.get_text()} for i,page in enumerate(doc)])
            record['pages']=len(doc)
        record.update(extraction_physical_path=str(out),extraction_logical_path='data/raw/2026-10-24-shared-infrastructure-plan-test/contexts/'+out.name,extraction_sha256=sha(out))
        result.append(record)
        print(record['source_id'],record['pages'],flush=True)
    write(HERE/'sources.json',{'sources':result,'protocol_sha256':sha(BASE/'PROTOCOL.md'),'new_downloads':0,'handling':'All full source text remains local-only; source records do not establish context eligibility.'})

if __name__=='__main__':main()
