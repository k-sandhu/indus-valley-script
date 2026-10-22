"""Preserve observable repairs, exposure and automated-source access."""
import csv
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,ROOT,csvrows,save,savecsv,page_index,references

ass=csvrows(OUT/'blind-assignments.csv')
pages=sorted({(r['primary_publication'],int(n)) for r in ass for n in re.findall(r'\d+',r['pdf_page'])})
incidents=[{'source_id':s,'pdf_page':p,'agent':'Codex / GPT-6 / API harness','stage':'Initial broad filtered text display','result':'Nonidentity source fragments could appear in tool output. No source excerpt is repeated in this record.','image_viewed':False} for s,p in pages]
save('exposure-incidents.json',{'confirmed_filter_failure':True,'scope':'An early Dholavira display retained nonidentity numeric columns. The subsequent broad page display could also retain descriptive fragments. The affected display set is recorded conservatively in full. Later views used closed identity tokens only.','affected_display_set':incidents,'images_opened':0,'source_words_reproduced_here':False,'consequence':'Run 4 cannot be treated as unexposed for these source pages, and its tool-output exposure restriction did not pass.'})
idx=page_index();obj=csvrows(BASE/'objects.csv');reg={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')}
sources={r['primary_publication'] for r in obj}
sources.update(s for r in obj for s,_,_ in references(r,reg) if s)
records=[]
for s in sorted(sources):
    nums=sorted(p for sid,p in idx if sid==s)
    records.append({'source_id':s,'agent':'Codex / GPT-6 / API harness','access':'Automated word-window hashing; no source words emitted','pages':';'.join(map(str,nums)),'purpose':'Content audit','image_viewed':'no'})
for r in json.loads((OUT/'unnamed-summary.json').read_text(encoding='utf-8'))['exposure']:
    records.append({'source_id':r['source_id'],'agent':'Codex / GPT-6 / API harness','access':'Immediate registration-line classification; coordinates only','pages':r['pdf_page'],'purpose':'Unnamed family '+r['family'],'image_viewed':'no'})
savecsv('exposure-mechanical.csv',records,list(records[0]))
text='''We drew the blind identities before opening the withheld object fields, then froze 60 source-only records. The identity display was too coarse to assess every field: prose references could not always be associated with a row ordinal, and publication indicators often remained unknown. We preserved these gaps and the original comparisons. They limit what the agreement rates establish.

The first text filter retained nonidentity columns and some descriptive fragments in tool output. We replaced the broad display with closed identity tokens and recorded every potentially affected sample page in exposure-incidents.json. We opened no page images. This exposure failure remains part of the run record.

The model service interruption left complete CSV and JSON records and nonempty text for every sampled page. We checked them before resuming. No source conversion, download or package installation was needed. A console encoding error was repaired by selecting UTF-8. A read-only Git command needed a per-command safe-directory setting; no Git configuration was changed.

The first registration search omitted the web register's nested site-to-page map. We preserved that endpoint in prior-search-2026-10-21, repaired the join and repeated the search. The family-level results and 69 occurrence coordinates did not change. We also restricted the catalogue-line classifier so a decimal value could not be mistaken for an entry label. Search hits remain separate from confirmed registrations.

The object list, decision register and site counts changed outside our owned paths during the audit. input-revision.json records the initial and revised hashes, and revised-input-2026-10-21 preserves the revised four CSV inputs. No sampled blind field changed. We kept the initial results separately and audited the revised snapshot. The revised decision register preserves historical joins and gives their applied status in protocol_local_match; we checked that distinction explicitly. The source list itself was never edited by this run.

Alias and CISI-prefix checks initially produced false alarms. We used the declared site aliases and the new explicit baseline identifier column in the revised list. The final locator audit has no failures. The historical context algorithm reproduces, while the current candidate sets retain the separately listed identity conflicts. Nine omission-page inventories remain unresolved; no replacement pages were drawn.

We used new standard-library implementations for sampling, intervals, counts, identifier projection, joins and searches. The coordinator scripts supplied specifications and were read, never run or imported. Only approved corpus identity fields were decoded. The scripts and report outputs are confined to verification/; run4/ contains no new source material. Authors: Codex / GPT-6, API tool harness; an exact model build identifier is not exposed in this session.
'''
(OUT/'RETROSPECTIVE.md').write_text(text,encoding='utf-8')
print('Exposure and retrospective records written.')
