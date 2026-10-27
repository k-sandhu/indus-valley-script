from collections import Counter
from datetime import datetime,timezone
from functools import cache
from prepare import *
@cache
def file_record(path):
 logical=('data/raw/2026-10-24-lexical-evidence-pass2/'+path.relative_to(RAW).as_posix()) if path.is_relative_to(RAW) else path.relative_to(ROOT).as_posix()
 return dict(logical_path=logical,physical_path=str(path.resolve()),bytes=path.stat().st_size,sha256=sha(path))
def main():
 packets=read(RAW/'source-packets-v2.json');review=read(RAW/'source-review-v1.json');results=read(PKG/'results-v1.json')
 originals={}
 for r in packets:
  witnesses=[r['winslow_witness']]+[x['witness'] for x in r['lexicon_entries']]+[w for d in r['dedr_entries'] for w in d['witnesses']]
  for w in witnesses:originals[w['logical_path']]=file_record(ROOT/w['logical_path'])
 originals_by_source={}
 for name in ['winslow','tamil-lex','dedr']:
  parent=ROOT/('experiments/2026-10-22-rebus-winslow/SOURCES.json' if name=='winslow' else 'experiments/2026-10-21-rebus-base-rate/SOURCES.json')
  original=read(parent)
  metadata=original['source'] if name=='winslow' else original['sources'][name]
  originals_by_source[name]=dict(parent_manifest=file_record(parent),metadata=metadata,
   pages=[r for path,r in sorted(originals.items()) if '/'+name+'/' in path])
 acquisition=read(RAW/'grammar-acquisition-v1.json')
 for r in acquisition:
  if 'physical_path' in r:r['logical_path']='data/raw/2026-10-24-lexical-evidence-pass2/'+Path(r['physical_path']).name
 titles={'annamalai-sandhi.html':dict(author='E. Annamalai',title='13. Sandhi',date_basis='Copyright 2017 shown on institutional page',source_type='University of Chicago Tamil Course, Grammar Aid',locator='Compound words; paragraph before Adjacent words'),
 'wilden-grammar.pdf':dict(author='Eva Wilden',title='Grammar of Old Tamil for Students',edition='1st Edition, NETamil Series 1',date_basis='Preface signed Hamburg, Dezember 2016; publication year not independently verified',source_type='Published grammar acquired from mirror',locator='Printed pp.17–18; PDF pp.27–28; cover PDF p.1')}
 for r in acquisition:
  if 'physical_path' in r:r.update(titles[Path(r['physical_path']).name],rights_status='rights-unverified',handling='local-only original and derivatives')
 outputs=[file_record(p) for p in sorted(RAW.glob('*')) if p.is_file()]
 save(PKG/'source-manifest-v1.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
  held_sources=originals_by_source,new_source_acquisition=acquisition,local_files=outputs,
  selection_sha256=sha(RAW/'case-selection-v1.json'),review_sha256=sha(RAW/'source-review-v1.json'),
  imported_code=[file_record(ROOT/p) for p in ['experiments/2026-10-22-lexical-source-review/code/source_blocks.py','experiments/2026-10-22-rebus-winslow/code/parse_winslow.py','experiments/2026-10-21-rebus-base-rate/code/parse_tamil_lex.py','experiments/2026-10-21-rebus-base-rate/code/parse_dedr.py']]))
 exposure=dict(case_count=16,case_source='FREEZE-v1.json',all_cases_previously_exposed_source_material=True,
  lexical_processing=dict(winslow_case_blocks=16,tamil_lexicon_case_records=116,dedr_case_records=76,selected_lexicon_sense_references=35,selected_dedr_unique_entries=23),
  display=dict(winslow_blocks='16 original blocks displayed as text',lexicon='Selected 35 sense references reviewed as source text; broader packet diagnostics were truncated and do not establish full display of all 116 records',dedr='23 selected original numbered entries displayed as text; long entries sometimes excerpted',
   grammar_visual_pdf_pages=[1,27,28],grammar_text_pdf_pages=[1,3,4,5,27,28],grammar_text_search='All 223 PDF pages extracted and searched; additional hit excerpts displayed with truncation',institutional_html='Compound words section read through web tool and downloaded byte witness preserved'),
  new_indus_confirmation_objects=0,substantive_statistic_reruns=0,specialist_adjudications=0)
 save(PKG/'EXPOSURE-v1.json',exposure)
 search=dict(queries=['Tamil grammar am increment tree names compounds Nannul','Pope Tamil grammar euphonic increment am names trees','site.archive.org Tamil grammar increment மரம் சாரியை'],query_count=3,
  useful_sources=['https://tamilcourse.uchicago.edu/node/121','https://gokulam.net/mirrors/Eva_files/readers/Grammar_of_Classical_Tamil_for_Students.pdf'],
  failures=['Tamil Digital Library candidate PDF content length 81385350 exceeds frozen 50 MB cap','Web reader could not access Wilden mirror; direct download then succeeded'],scope='Search snippets used as locators only')
 save(RAW/'bounded-search-record-v1.json',search)
 commands=['python experiments/2026-10-24-lexical-evidence-pass2/code/prepare.py','python experiments/2026-10-24-lexical-evidence-pass2/code/packets.py','python experiments/2026-10-24-lexical-evidence-pass2/code/review.py','python experiments/2026-10-24-lexical-evidence-pass2/code/validate.py','python experiments/2026-10-24-lexical-evidence-pass2/code/package.py']
 save(PKG/'commands-v1.json',dict(commands=commands,versions='Packet v1 failed on repeated DEDR number; source packets v1 then v2 preserved; validation-v1 missing import; validation-v2 passes',
  grammar_acquisition='Direct urllib GET to the two recorded URLs; max 50000000 bytes; raw requests and hashes in grammar-acquisition-v1.json',
  pdf_render='PyMuPDF Matrix(1.3,1.3), PDF pages1,27,28; full text extracted to Wilden-pages-v1.json'))
 prefix=PKG.relative_to(ROOT).as_posix()
 entry=dict(id='LEXICAL-EVIDENCE-PASS2-2026-10-24',theme='Printed sense and increment evidence for sixteen lexical cases',status='completed-bounded-source-review; specialist-adjudication-pending',status_class='source-review',area='language',
 question='Which unresolved increment and homograph cases can be qualified by actual dictionary and grammatical source entries for Q-0039?',
 outcome='Reviewed 16 frozen cases with 35 Lexicon sense references and 23 distinct DEDR entries. Eight cases have printed boundary or contextual increment support, one generated candidate contradicts its ten-parts source sense, six conflicts separate homographs, and one material-noun case has conflicting grammatical labels. Acquired Annamalai institutional Sandhi lesson and Wilden grammar PDF; inspected m-assimilation rules, without establishing a universal u-to-am rule. Existing candidates, exact subset and scorer flags unchanged.',
 challenge='Exact forms pool different senses and origins. DEDR can preserve Sanskrit comparisons and agree through shared lexicographical sources. A nominal material sense can differ from a parent grammatical label; printed citations do not verify earliest dates.',
 remedy='Froze 16 cases; bound original Winslow/Lexicon/DEDR witnesses and preserved repeated numbered entries; selected explicit senses; inspected published grammar pages; recorded size-limited acquisition failure and retained unresolved ancestry and historical questions.',
 evidence=[prefix+'/'+x for x in ['PROTOCOL.md','FREEZE-v1.json','REPORT.md','RETROSPECTIVE.md','DATA-UPDATE.md','results-v1.json','validation-v2.json','source-manifest-v1.json','EXPOSURE-v1.json','commands-v1.json']],
 retry_when='A qualified Dravidianist reviews these exact cases, competing etymologies and noun labels, and the cited literary and grammar passages are checked directly for the proposed rules and attestation dates.',
 authors=[dict(model='gpt-6.1-sol',harness='Codex collaboration',agent='lexical evidence pass2 worker',qualifications='AI source reviewer without specialist Tamil credentials')],verification_tier='submitted',package=prefix)
 save(ROOT/'knowledge/registry/attempts/LEXICAL-EVIDENCE-PASS2-2026-10-24.json',entry)
 print(json.dumps(dict(source_pages=len(originals),new_downloads=2,case_count=16,validation_pass=read(PKG/'validation-v2.json')['pass_all'])))
if __name__=='__main__':main()
