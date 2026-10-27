"""Recount Dholavira placeholder labels without modifying the pre-join endpoint."""
from pathlib import Path
import collections, hashlib, json

HERE=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/contexts')
INHERITED=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/inscriptions/dholavira-context-table-v1.json')
EXPECTED='e574bfea349db809810cdb8b7fb06f832af41549f79f0b2de5e271fca7faddec'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=read(HERE/'context-freeze.json')
    assert freeze['combined_sha256']==EXPECTED
    before={r['path']:sha(HERE/r['path']) for r in freeze['frozen_files']}
    assert all(before[r['path']]==r['sha256'] for r in freeze['frozen_files'])
    detail=RAW/'dholavira225-join-gates-v1.json'
    rows=[r['source_row'] for r in read(detail)['rows']]
    assert rows==read(INHERITED)['rows']
    assert len(rows)==225
    definitions={
      'loose_nonplaceholder':{'normalisation':'Strip surrounding whitespace and casefold only.','excluded_values':['','-','?','unst'],
        'interpretation':'Counts Unst. because the punctuation-bearing label is not in this exclusion set.'},
      'strict_nonplaceholder_including_nil':{'normalisation':'Strip surrounding whitespace and casefold only.','excluded_values':['','-','?','unst','unst.'],
        'interpretation':'This is the frozen literal_nonplaceholder_counts_including_Nil definition.'},
      'frozen_usable_label':{'normalisation':'Strip surrounding whitespace and casefold only.','excluded_values':['','-','?','unst','unst.','nil'],
        'interpretation':'This is the frozen supplied() predicate. It is a source-label gate, not a numeric measurement or operational-context gate.'}}
    counts={}
    for field in ('stratum','depth_as_printed'):
        assert all(isinstance(r[field],str) for r in rows)
        c=collections.Counter(r[field].strip() for r in rows)
        result={'source_rows':len(rows),'nonempty_cells':sum(v for k,v in c.items() if k!=''),
          'marker_counts_as_printed':{k:c[k] for k in ('','-','?','Unst','Unst.','Nil','Unstratified','Surface')},
          'predicate_counts':{},'difference_from_loose_to_frozen':{'excluded_label':'Unst.','count':c['Unst.']},
          'nil_exclusion_effect':c['Nil']}
        for name,d in definitions.items():
            result['predicate_counts'][name]=sum(r[field].strip().casefold() not in d['excluded_values'] for r in rows)
        counts[field]=result
    assert counts['stratum']['predicate_counts']=={'loose_nonplaceholder':213,'strict_nonplaceholder_including_nil':211,'frozen_usable_label':211}
    assert counts['depth_as_printed']['predicate_counts']=={'loose_nonplaceholder':202,'strict_nonplaceholder_including_nil':201,'frozen_usable_label':201}
    summary=read(HERE/'dholavira225-summary.json')
    assert summary['literal_nonplaceholder_counts_including_Nil']=={'stratum':211,'depth_as_printed':201}
    out={'id':'CLARIFICATION-01','date':'2026-10-24','status':'post-freeze metadata clarification; no frozen record changed',
      'subject':'Dholavira stratum/depth label counts and correction of completion message',
      'correction':'The completion message incorrectly attributed the 213/202 versus 211/201 difference to Nil. There are no Nil cells in either column. The difference is two stratum cells and one depth cell labelled Unst. with a final full stop.',
      'authoritative_frozen_counts':{'stratum':211,'depth_as_printed':201},
      'meaning_of_213_202':'The looser predicate counts punctuation-bearing Unst. labels. It is not a second data-coverage result or the stored including-Nil count.',
      'frozen_endpoint_combined_sha256':EXPECTED,
      'input_witnesses':[{'physical_path':str(detail),'sha256':sha(detail),'role':'Frozen gate derivative; source_row fields recounted'},
        {'physical_path':str(INHERITED),'sha256':sha(INHERITED),'role':'Inherited extraction; all 225 source_row dictionaries match exactly'},
        {'logical_path':'experiments/2026-10-24-shared-infrastructure-plan-test/modules/contexts/dholavira225-summary.json',
         'sha256':sha(HERE/'dholavira225-summary.json'),'role':'Frozen summary being clarified'}],
      'definitions':definitions,'recounts':counts,
      'scope_limit':'Counts concern literal source labels. Surface, Unstratified and compound survey/depth expressions remain labels under this predicate; passing it does not establish a usable numeric depth.',
      'source_locators':{'source_id':'BISHT2015-PRELIM','printed_pages':'247–260','pdf_indices':'263 onward; row-specific locators remain in the local derivative'},
      'frozen_integrity':{'all_frozen_file_hashes_match':True,'raw_source_rows_equal_inherited_extraction':True,
        'C0018_C0019_eligibility_changed':False,'new_archaeological_values':False},
      'authors':[{'model':'GPT-6 family; exact variant unavailable','harness':'Codex desktop collaboration'}]}
    after={r['path']:sha(HERE/r['path']) for r in freeze['frozen_files']}
    assert before==after
    target=HERE/'CLARIFICATION-01.json'
    if target.exists():assert read(target)==out,'Preserve an existing clarification; create a new version for a changed result.'
    else:target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'counts':{k:v['predicate_counts'] for k,v in counts.items()},'frozen_integrity':True},indent=2))
if __name__=='__main__':main()
