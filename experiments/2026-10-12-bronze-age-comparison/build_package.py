"""Build source-linked aggregate tables and a claim map from frozen endpoints."""
from pathlib import Path
import json
import hashlib

P=Path(__file__).resolve().parent
def read(name):return json.loads((P/name).read_text(encoding='utf-8'))
def save(name,value):
    with (P/name).open('x',encoding='utf-8') as handle:
        if isinstance(value,str):handle.write(value)
        else:json.dump(value,handle,indent=2);handle.write('\n')
def pct(value):return 'unavailable' if value is None else f'{100*value:.2f}%'

struct=read('run-v2/structural-results.json');roles=read('run-v2/category-results.json')
signs=read('sign-control-v2/results.json');lex=read('run-v2/lexical-ambiguity.json');census=read('run-v2/normalization-census.json')
names={'sumerian':'Sumerian','akkadian':'Akkadian document cohort','egyptian':'Egyptian','mycenaean':'Mycenaean Greek','indus':'IVS'}
text=['# Exact aggregate tables\n','Current endpoints: run-v2 and sign-control-v2. All percentages are rendered directly from frozen numeric outputs.\n',
      '## Structured short records\n','Lengths 3–12 count the stated encoding units. Distinct sequences are used for this statistic.\n',
      '| Cohort | Eligible edited records | Distinct sequences | Units | Inventory | Position statistic | Shuffle mean | Holm p |',
      '|---|---:|---:|---:|---:|---:|---:|---:|']
for key,row in struct.items():
    text.append(f"| {key} | {row['eligible_records']} | {row['distinct_sequences']} | {row['tokens']} | {row['types']} | {row['statistic']:.6f} | {row['reference_mean']:.6f} | {row.get('holm_p_all_structural_cohorts',0):.4f} |" if row['statistic'] is not None else f"| {key} | {row['eligible_records']} | {row['distinct_sequences']} | {row['tokens']} | {row['types']} | unavailable | unavailable | unavailable |")
text+=['\nEgyptian vessel rows count editorial lexical tokens. Egyptian glyph sentences count glyphs. Cuneiform rows count readings and grouped numeral forms; Greek rows count syllables/logograms/grouped numbers. These are separate encoding populations. [Exact results](run-v2/structural-results.json).\n',
       '## Word-category calibration\n','Complete edited object/module texts, 3–12 source lexical tokens. Training tags are available; held-out tags and readable identities are hidden from prediction.\n',
       '| Cohort | Records | Groups | Scored tokens | Majority | Position | Identity | Context | Context balanced | Unseen-ID context |',
       '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for key in ['sumerian/whole','akkadian/whole','egyptian/whole','mycenaean/whole']:
    row=roles[key];models=row['overall']['models']
    text.append(f"| {names[key.split('/')[0]]} | {row['rows']} | {row['groups']} | {row['overall']['tokens']} | {pct(models['MAJORITY']['accuracy'])} | {pct(models['POSITION']['accuracy'])} | {pct(models['IDENTITY']['accuracy'])} | {pct(models['CONTEXT']['accuracy'])} | {pct(models['CONTEXT']['balanced_accuracy'])} | {pct(row['unseen_identity']['models']['CONTEXT']['accuracy'])} |")
text+=['\nGreek predicts SYLLABIC/LOGOGRAM/NUMBER, rather than the five word/POS categories. Unknown-category targets are excluded and separately counted in the endpoint. [Exact results and class support](run-v2/category-results.json).\n',
       '## Categories with word boundaries concealed\n','Lengths 3–12 now count sign/readings or glyphs. Each category applies to units within a source-annotated word. These populations differ from the word table.\n',
       '| Cohort | Records | Groups | Scored units | Majority | Identity | Context | Context balanced |',
       '|---|---:|---:|---:|---:|---:|---:|---:|']
for key in ['sumerian/whole','akkadian/whole','egyptian/glyph_sentence','mycenaean/whole']:
    row=signs[key]
    if row['status']!='complete':text.append(f"| {key} | {row['rows']} | {row['groups']} | unavailable | unavailable | unavailable | unavailable | unavailable |");continue
    models=row['overall']['models'];text.append(f"| {key} | {row['rows']} | {row['groups']} | {row['overall']['tokens']} | {pct(models['MAJORITY']['accuracy'])} | {pct(models['IDENTITY']['accuracy'])} | {pct(models['CONTEXT']['accuracy'])} | {pct(models['CONTEXT']['balanced_accuracy'])} |")
text+=['\nThe complete Akkadian sign-length population has four groups and cannot support the declared five-fold control. Its line extension remains a separate evaluated outcome. [Exact results](sign-control-v2/results.json).\n',
       '## Equality-pattern compatibility\n','Target: 1,522 distinct IVS faces of length 3–8, with 47 equality patterns. Each face/candidate correspondence is considered independently.\n',
       '| Source spelling inventory | Natural entries | Compatible faces, natural inventory | Median candidates per face | Mean compatible fraction, 200 entries | Mean multiple-candidate fraction, 200 entries |',
       '|---|---:|---:|---:|---:|---:|']
for corpus in ['sumerian','akkadian','egyptian','mycenaean']:
    natural=lex['natural'][corpus];matched=lex['matched'][corpus]
    text.append(f"| {names[corpus]} | {lex['natural_lexicon_sizes'][corpus]} | {natural['compatible_faces']}/1522 | {natural['median_candidates_per_face']:.0f} | {pct(matched['mean_compatible_fraction'])} | {pct(matched['mean_multiple_candidate_fraction'])} |")
text+=['\nA compatible pattern is not a translation. The assumed per-face key may conflict with every other face. These observed spellings retain corpus/encoding differences, including Sumerian formulae in the Akkadian document cohort. [Exact outcomes and subset intervals](run-v2/lexical-ambiguity.json).\n',
       '## Extension populations\n','Natural lines and sentences are reported separately from complete object texts.\n',
       '| Word-control extension | Rows | Groups | Largest group, rows | Scored tokens | Identity accuracy | Context accuracy | Context balanced accuracy |',
       '|---|---:|---:|---:|---:|---:|---:|---:|']
for key,row in roles.items():
    if key.endswith('/extension'):
        model=row['overall']['models'];text.append(f"| {key} | {row['rows']} | {row['groups']} | {row['largest_group_rows']} | {row['overall']['tokens']} | {pct(model['IDENTITY']['accuracy'])} | {pct(model['CONTEXT']['accuracy'])} | {pct(model['CONTEXT']['balanced_accuracy'])} |")
text+=['\nThe largest Sumerian extension component contains 12,563 rows; its fold carries 55,488 of 68,322 scored tokens. That grouped outcome is dominated by a particular connected source population. Its rows are not independent tests.\n']
save('TABLES.md','\n'.join(text)+'\n')

old=read('run-v1/structural-results.json');oldroles=read('run-v1/category-results.json');oldsigns=read('sign-control-v1/results.json')
comparisons={'structural':{k:v==struct[k] for k,v in old.items() if not k.startswith('mycenaean/')},
             'word_categories':{k:v==roles[k] for k,v in oldroles.items() if not k.startswith('mycenaean/')},
             'sign_categories':{k:v==signs[k] for k,v in oldsigns.items() if not k.startswith('mycenaean/')},
             'Greek_source_repair':{'whole_short_distinct_sequences_before':old['mycenaean/whole_document']['distinct_sequences'],
                                    'whole_short_distinct_sequences_after':struct['mycenaean/whole_document']['distinct_sequences'],
                                    'word_context_accuracy_before':oldroles['mycenaean/whole']['overall']['models']['CONTEXT']['accuracy'],
                                    'word_context_accuracy_after':roles['mycenaean/whole']['overall']['models']['CONTEXT']['accuracy']}}
assert all(v for family in ['structural','word_categories','sign_categories'] for v in comparisons[family].values())
save('source-correction-comparison.json',comparisons)

observations=[{'id':'O01','source':'S01','observation':'Source object/surface/line structure and source tags are machine-readable; seal surfaces must remain separate from their parent accounts.','witness':'acquisition/sumerian-ur3-v1.json','output':'run-v2/normalization-census.json'},
 {'id':'O02','source':'A01,A02','observation':'The acquired Akkadian cohort includes letters, administrative accounts, damaged passages and Sumerian formulae. Whole edited records and readable lines have different coverage.','output':'run-v2/normalization-census.json'},
 {'id':'O03','source':'E01,E02','observation':'The inspected Qubbet el Hawa vessel No. 89/136 (259) has a five-token source text including a commodity and named people linked by kinship terminology. Its source dating bounds are -2363 and -2187.','source_text':'22QMKN7KS5CDNE7TCYA3AW4LC4','witness':'acquisition/egyptian-archive-fixture-v1.json','source_url':census['egyptian']['inspection_examples'][0]['source_url']},
 {'id':'O04','source':'E01,E02','observation':'Edition extent and source token IDs do not always agree across the two transformed Egyptian corpora. The complete-vessel cohort requires agreement.','output':'run-v2/normalization-census.json'},
 {'id':'O05','source':'G01','observation':'Displayed uncertainty/restoration can be absent from normalized search-link strings. Final eligibility checks both representations.','amendment':'SOURCE-MARKUP-AMENDMENT.md','output':'source-correction-comparison.json'},
 {'id':'O06','source':'D01','observation':'Fischer presents Old Kingdom seals combining royal names and official titles with decorative figures. These supply a qualitative name/title comparison, outside the measured jar cohort.','locus':'printed pp. 5-9','witness':'acquisition/egyptian-seal-paper-v1.json'},
 {'id':'O07','source':'M01','observation':'Rao et al. already compared IVS with Sumerian, Old Tamil and Vedic Sanskrit. Their supplementary Sumerian dataset is drawn from literary compositions.','locus':'main p. 1165, supplement datasets pp. 2-4','source_url':'https://homes.cs.washington.edu/~rao/ScienceIndus.pdf'},
 {'id':'O08','source':'I01','observation':'The existing full-register clean-text benchmark supplies 1,593 distinct IVS faces of length 3-12, with 7,970 codes and no supplied meanings.','output':'run-v2/structural-results.json'}]
save('observations.json',observations)
claims=[{'id':'C01','claim':'All eleven testable structural cohorts depart from within-record shuffled position references at the adjusted 5% level; one tiny Akkadian seal cohort has no testable frequent type.','observations':['O01','O02','O03','O05','O08'],'evidence':['run-v2/structural-results.json','run-v2/verification.json'],'scope':'conditional allocation statistic, encoding populations kept distinct'},
 {'id':'C02','claim':'Known word categories can be predicted from anonymous identity/context on source-group held-out Sumerian and Egyptian edited records; identity-only controls account for much of the success.','evidence':['run-v2/category-results.json','category-replay-verification-v2.json'],'scope':'source-segmented words and source training tags; Greek has a different three-class task'},
 {'id':'C03','claim':'Category prediction from anonymous sign/readings with word boundaries concealed has measured positive and negative outcomes; complete Akkadian records are too few for its five-fold control.','evidence':['sign-control-v2/results.json','sign-control-v2/verification.json','category-replay-verification-v2.json'],'scope':'post-word-outcome exploratory refinement; populations differ from word controls'},
 {'id':'C04','claim':'All four 200-entry spelling inventories match most target faces under a per-face equality-pattern construction, generally with several candidates.','evidence':['run-v2/lexical-ambiguity.json'],'scope':'one-face/one-word assumption; no phonetic anchor or shared key'},
 {'id':'C05','claim':'Per-face pattern compatibility does not supply a consistent global mapping. The necessary injection bound is tested separately against incomplete observed inventories.','evidence':['run-v2/lexical-ambiguity.json'],'scope':'no historical language is selected or excluded'},
 {'id':'C06','claim':'Source repairs preserve previous endpoints and leave all non-Greek numerical cohort outcomes unchanged in the successor run.','evidence':['PARSER-AMENDMENT.md','SOURCE-MARKUP-AMENDMENT.md','source-correction-comparison.json','baseline-v1.json'],'scope':'preservation of named inputs and outputs, not an exhaustive whole-workspace audit'}]
save('CLAIM-EVIDENCE.json',claims)
print(json.dumps({'tables':'TABLES.md','observations':len(observations),'claims':len(claims),'non_Greek_numeric_outcomes_unchanged':True}))
