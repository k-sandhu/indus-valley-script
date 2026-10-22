"""Record the independent page inventory and the limits of enumeration."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,csvrows,save,savecsv,interval,references

# Identity-only readings made from the seeded pages. An unresolved page is
# retained in the sample and is never silently counted as omission-free.
UNRESOLVED={
 ('iar-2013-14','106'):'Caption text does not identify an eligible object independently.',
 ('chanhu-surface2017-held','155'):'The held witness does not yield an independently identifiable object inventory.',
 ('chanhu-surface2017-held','195'):'The held witness does not yield an independently identifiable object inventory.',
 ('chanhu-surface2017-held','187'):'The held witness does not yield an independently identifiable object inventory.',
 ('chanhu-surface2017-held','203'):'The held witness does not yield an independently identifiable object inventory.',
 ('iar-2003-04-asi','62'):'Existing rows cite this page, but the continuation and the additional object group cannot be enumerated independently with the available identity cues.',
 ('iar-1997-98-archive','329'):'Script wording is present, but an object identity cannot be recovered independently from the permitted text fragments.',
 ('puratattva-33','188'):'Pottery and script wording occur without enough identity evidence to enumerate eligible objects safely.',
 ('puratattva-35-held','85'):'Figure numbers are recoverable; object identities are not.'
}
NOTES={
 ('puratattva-29','7'):'No individually identified eligible object or eligible enumerated group in the permitted text.',
 ('iar-1994-95','73'):'The recovered excavation headings concern another archaeological context; no eligible Indus object is identified.',
 ('iar-2003-04-asi','2'):'Front matter and contents references do not report an additional physical object.',
 ('iar-1987-88','107'):'The recovered excavation headings and object discussion do not identify an additional eligible Indus object.',
 ('man-environment-32','125'):'Bibliographic and general discussion does not identify an additional eligible object.',
 ('nuhato-2018-held','119'):'Reference material does not report an additional physical object.',
 ('man-environment-24','266'):'The catalogue discussion concerns sites and publications before their CISI 3 baselines; Amendment 1 requires no new rows from it.',
 ('farmana-2006-08','9'):'Front matter and section references do not identify an additional physical object.',
 ('man-environment-27','259'):'The Harappa discussion predates the CISI 3.1 baseline; Amendment 1 requires no new rows from it.',
 ('nuhato-2018-held','114'):'The pottery captions do not call an individually identified object an Indus-script object.',
 ('kanmer-ch6','53'):'The pottery discussion and figure reference do not identify an additional eligible object.',
}

def main():
    ass=csvrows(OUT/'omission-assignments.csv');obj=csvrows(BASE/'objects.csv');reg={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')}
    evidence=json.loads((OUT/'omission-page-evidence.json').read_text(encoding='utf-8'))['pages']
    by={(r['source_id'],r['pdf_page']):r for r in evidence}
    out=[];page_results=[]
    for a in ass:
        key=a['source_id'],a['pdf_page'];e=by[key]
        r={'source_id':key[0],'pdf_page':key[1],'parts':a['parts'],'site':'','source_object_identifier':'','object_type':'','citing_rows':';'.join(e['primary_page_rows']),'elsewhere_identified_rows':'','result':'no additional eligible object identified','omitted':'no','assessment':'assessed','note':NOTES.get(key,'No individually identified eligible object or eligible enumerated group in the permitted text.')}
        if key in UNRESOLVED:
            r.update(result='unresolved page inventory',omitted='unknown',assessment='unresolved',note=UNRESOLVED[key])
        if key==('farmana-2006-08','391'):
            r.update(site='Farmana',source_object_identifier='S-1',object_type='seal',elsewhere_identified_rows='PCF-FRM-001',result='object already listed; page citation gap',omitted='no',note='Figure 7.10 identifies S-1. The same object is listed from its identity table at PDF page 385. No row cites PDF page 391 explicitly.')
        # Include every secondary page citation that can be tied explicitly to this page.
        for x in obj:
            for source,pg,raw in references(x,reg):
                if source==key[0] and key[1] in re.findall(r'\d+',pg):
                    cited=set(filter(None,r['citing_rows'].split(';')));cited.add(x['row_id']);r['citing_rows']=';'.join(sorted(cited))
        out.append(r)
        page_results.append({'source_id':key[0],'pdf_page':key[1],'assessment':r['assessment'],'omission_confirmed':False,'object_count_found_absent_from_list':0,'note':r['note']})
    complete=sum(r['assessment']=='assessed' for r in out);u=len(out)-complete
    summary={'sampled_pages':len(out),'assessed_pages':complete,'unresolved_pages':u,'confirmed_omitted_objects':0,'pages_with_confirmed_omission':0,'omitted_objects':[],
      'all_sample_omission_rate':None,'reason':'Unresolved page inventories prevent an omission-rate estimate for the full sample.',
      'assessed_page_rate':0.0,'assessed_page_exact_binomial_95':interval(0,complete),
      'all_sample_sensitivity':{'if_no_unresolved_page_has_an_omission':{'rate':0,'exact_binomial_95':interval(0,len(out))},'if_every_unresolved_page_has_an_omission':{'rate':u/len(out),'exact_binomial_95':interval(u,len(out))}},
      'page_results':page_results,'locator_gaps':[{'site':'Farmana','source_id':'farmana-2006-08','pdf_page':'391','object_type':'seal','listed_at_pdf_page':'385','source_object_identifier':'S-1'}],
      'interpretation':'The conditional interval describes assessed pages only. The unresolved pages remain in the original random sample; no substitute pages were drawn. An illustration of an object listed elsewhere is a page-citation gap, not a new physical object.'}
    savecsv('omission-sample.csv',out,list(out[0]));save('omission-summary.json',summary)
    print('OMISSION',len(out),'sampled;',complete,'assessed;',u,'unresolved; confirmed omissions 0; conditional interval',summary['assessed_page_exact_binomial_95'])

if __name__=='__main__':main()
