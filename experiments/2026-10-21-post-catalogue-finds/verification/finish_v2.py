"""Finish source-review records without changing any frozen first audit."""
import collections
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,csvrows,save,savecsv,interval,ids
P=OUT/'input-v2-2026-10-21'

def containment():
    rows={r['row_id']:r for r in csvrows(P/'objects.csv')};out=[]
    for r in rows.values():
        if r['match_basis']!='catalogue-containment':continue
        accepted=r['site_code']=='NHT'
        if accepted:reason=[]
        elif r['site_code']=='DSL':reason=['The report and baseline family inventory agree at the group level, but the available catalogue text layer does not recover the site-section passage establishing that this is the complete same excavation group. The basic-data excavation identities do not independently identify these report objects. Containment remains unconfirmed in this review.']
        else:reason=['The two report seals and the two proposed baseline seals agree as an excavation group, but the report registration differs from both baseline registrations. The available catalogue text layer does not recover the site-section passage needed to establish the proposed complete-group identity. Containment remains unconfirmed in this review.']
        out.append({'row_id':r['row_id'],'site':r['site'],'cisi_in_baseline':r['cisi_in_baseline'],'would_reach':accepted,'reasons':reason,'scope':'Baseline containment is assessed separately from the stricter local matched identifier rule. A complete documented excavation-group identity could establish containment without a one-to-one registration crosswalk.'})
    save('containment-review-v2.json',{'assessments':out,'held_catalogue_text_checked':['research/literature/sources/joshi_parpola_1987_cisi1.txt','research/literature/sources/joshi_parpola_1987_cisi1.pdf'],'text_layer_result':'The existing text file and a text-layer extraction yield no recoverable Desalpur or Surkotada site heading. No page image was opened and no OCR repeated. Existing basic-data identity records contain every cited baseline number.','prior_objection_refinement':'The first audit treated missing individual registrations as sufficient to reject all five group-containment decisions. This follow-up recognises that documented complete-group identity can establish containment, but could not independently verify the cited site-section premise from the held text.','independent_confirmation_pending':['PCF-DSL-001','PCF-DSL-002','PCF-DSL-003','PCF-SKT-001','PCF-SKT-002']})

def omission():
    out=csvrows(OUT/'pre-v2-reports-2026-10-21/omission-sample.csv');old=json.loads((OUT/'pre-v2-reports-2026-10-21/omission-summary.json').read_text(encoding='utf-8'))
    resolved={('iar-2013-14','106'):'The caption identifies excavation material at Karanpura and does not affirm an eligible inscribed object.',('iar-1997-98-archive','329'):'Separating the PDF text by column places the inscription wording in a different conservation entry. The Dholavira account does not report an additional eligible object.',('puratattva-33','188'):'The book-review discussion concerns early historical pottery. It does not identify an eligible Indus object.',('puratattva-35-held','85'):'The artifact discussion has no affirmative inscription or Indus-script qualification for an individual object.',**{('chanhu-surface2017-held',p):'The complete held text for this page contains no eligible inscription statement, object-class report or named candidate site. Figure references alone do not report an additional eligible object.' for p in ['155','187','195','203']}}
    for r in out:
        key=(r['source_id'],r['pdf_page'])
        if key in resolved:r.update(result='no additional eligible object identified',omitted='no',assessment='assessed',note=resolved[key])
        elif key==('iar-2003-04-asi','62'):
            r.update(site='Bhirrana',object_type='inscribed-tool; seal',note='The page continues an inscribed celt account and reports a group of seals, some affirmatively qualified. The four citing rows cover celts and seals. The remaining eligibility and enumeration cannot be established independently from the permitted identity text, so this inventory remains unresolved.')
    assessed=sum(r['assessment']=='assessed' for r in out);u=len(out)-assessed
    summary={'sampled_pages':len(out),'assessed_pages':assessed,'unresolved_pages':u,'confirmed_omitted_objects':0,'pages_with_confirmed_omission':0,'omitted_objects':[],'all_sample_omission_rate':None,'all_sample_confirmed_omission_fraction':0,'reason':'One page inventory remains unresolved; the full-sample omission rate is not identifiable.','assessed_page_rate':0.0,'assessed_page_exact_binomial_95':interval(0,assessed),'observed_full_sample_fraction_bounds':[0,u/len(out)],'all_sample_sensitivity':{'if_no_unresolved_page_has_an_omission':{'rate':0,'exact_binomial_95':interval(0,len(out))},'if_every_unresolved_page_has_an_omission':{'rate':u/len(out),'exact_binomial_95':interval(u,len(out))}},'exact_interval_envelope_with_unresolved_outcomes':[0,interval(u,len(out))[1]],'original_assessed_pages':old['assessed_pages'],'original_unresolved_pages':old['unresolved_pages'],'resolved_on_revisit':[{'source_id':s,'pdf_page':p,'reason':reason} for (s,p),reason in resolved.items()],'unresolved':[{'source_id':r['source_id'],'pdf_page':r['pdf_page'],'note':r['note']} for r in out if r['assessment']!='assessed'],'locator_gaps':old['locator_gaps'],'page_results':[{'source_id':r['source_id'],'pdf_page':r['pdf_page'],'assessment':r['assessment'],'note':r['note']} for r in out],'interpretation':'No substitute pages were drawn. The conditional exact interval describes assessed pages only. The full-sample envelope covers both possible outcomes on the unresolved page; it is not a point estimate. An object illustrated here but identified elsewhere is a page-citation gap, not a new physical object.'}
    savecsv('omission-sample.csv',out,list(out[0]));save('omission-summary.json',summary)
    save('omission-revisit-v2.json',summary)
    print('OMISSION',assessed,'assessed',u,'unresolved',summary['assessed_page_exact_binomial_95'])

def exposures():
    save('exposure-incidents-v2.json',{'confirmed_filter_failure':True,'prior_incident_record':'exposure-incidents.json','additional_display_set':[{'source_id':'surkotada-1990','pdf_page':382},{'source_id':'puratattva-37','pdf_page':65}],'failure':'A closed-vocabulary display retained quantity words in clauses whose object could be omitted by the filter. The display therefore did not safely isolate object quantities. The filter was changed to withhold all general quantities. No source fragment is repeated here.','images_opened':0,'new_catalogue_ocr_pages':list(range(5,13)),'new_ocr_access_record':'catalogue-locator-access-v2.json','render_cleanup':'Each of eight new catalogue-preface renders was deleted immediately after saving the identity projection. No existing complete page-text file was re-OCRed.','consequence':'The run remains unsuitable for an assertion of zero source-content exposure.'})

def unnamed():
    import search_and_content as search
    search.inputpath=lambda name:P/name
    search.save=lambda name,data:save(name.replace('.json','-v2.json'),data)
    search.savecsv=lambda name,data,fields:savecsv(name.replace('.csv','-v2.csv'),data,fields)
    def pattern(reg):
        reg=reg.strip().strip('-')
        if 'project' in reg.casefold():reg=re.split('project',reg,flags=re.I)[-1]
        reg=re.sub('^DHR[- ]*','',reg,flags=re.I)
        def char(c):
            if c.upper() in '0O':return '[0Oo]'
            if c in '1IiLl':return '[1IiLl]'
            return re.escape(c)
        chars=[]
        for c in reg:
            if c.isalnum():chars.append(char(c))
            elif c not in ' -\t\r\n':chars.append(r'(?:\s*'+re.escape(c)+r'\s*)?')
        return re.compile(r'(?<![A-Za-z0-9])(?:D[Hh][Rr][\s-]*)?'+r'[\s-]*'.join(chars)+r'(?![A-Za-z0-9])',re.I)
    search.pattern=pattern
    search.unnamed()
    summary=json.loads((OUT/'unnamed-summary-v2.json').read_text(encoding='utf-8'))
    summary['search_rule']+=' V2 retains optional literal punctuation at its original positions in composite registrations. It does not introduce decimal punctuation between adjacent registration digits. This corrects a separator omission in the first implementation.'
    save('unnamed-summary-v2.json',summary)

if __name__=='__main__':
    try:{'containment':containment,'omission':omission,'exposures':exposures,'unnamed':unnamed}[sys.argv[2]]()
    except OSError as e:
        try:save('WRITE-FAILURE-v2.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
