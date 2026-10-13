"""Print compact research outcomes without source-derived sequences."""
from pathlib import Path
import json
PACKAGE=Path(__file__).resolve().parent
for key,value in json.loads((PACKAGE/'run-v1/structural-results.json').read_text()).items():
    print('STRUCTURE',key,{k:value.get(k) for k in ['eligible_records','distinct_sequences','tokens','types','statistic','reference_mean','holm_p_all_structural_cohorts']})
for key,value in json.loads((PACKAGE/'run-v1/category-results.json').read_text()).items():
    if value['status']!='complete':print('CATEGORIES',key,value);continue
    print('CATEGORIES',key,'rows',value['rows'],'groups',value['groups'],'tokens',value['overall']['tokens'],
          'accuracy',{m:round(s['accuracy'],4) for m,s in value['overall']['models'].items()},
          'unseen',value['unseen_identity']['tokens'],value['unseen_identity']['models']['CONTEXT']['accuracy'],
          'class support',value['overall']['class_support'])
print('LEXICAL',json.dumps(json.loads((PACKAGE/'run-v1/lexical-ambiguity.json').read_text()),indent=2))
