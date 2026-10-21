"""Independent arithmetic, source integrity and population checks; no scorer import."""
from collections import Counter, defaultdict
from fractions import Fraction
import csv
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-20-h912-tablet-series'


def read(path):return json.loads(path.read_text(encoding='utf8'))
def rows(path):return [json.loads(l) for l in path.read_text(encoding='utf8').splitlines()]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
 checks=[]
 def check(name,ok):checks.append({'check':name,'pass':bool(ok)})
 frozen=read(HERE/'bench-freeze-v1.json')['frozen']
 for path,h in frozen['artifacts'].items():check('frozen '+Path(path).name,sha(Path(path))==h)
 check('predictions hash',sha(HERE/'PREDICTIONS.json')==frozen['predictions_sha256'])
 access=rows(HERE/'round.access.jsonl')
 confirmation=[r for r in access if r['half']=='confirmation' and r['allowed']]
 check('one confirmation read',len(confirmation)==1)
 check('freeze before confirmation',frozen['utc']<confirmation[0]['utc'])
 check('historical exposure declared',not confirmation[0]['fresh_claim_allowed'])
 fs={half:rows(RAW/run/'faces.jsonl') for half,run in [('discovery','discovery-v1'),('confirmation','confirmation-v1')]}
 check('all 5680 faces retained',sum(map(len,fs.values()))==5680)
 check('component separation',not ({r['component'] for r in fs['discovery']}&{r['component'] for r in fs['confirmation']}))
 table={}
 with (ROOT/'experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv').open(encoding='utf8') as f:
  table={r['code']:r for r in csv.DictReader(f,delimiter='\t')}
 independent={}
 for half,faces in fs.items():
  found=[]
  for r in faces:
   seq=[str(s).zfill(3) for s in r['signs_reading_rtl']]
   if not r['clean_rtl_singleline'] or len(seq) not in (2,3):continue
   a=table.get(seq[0],{})
   if a.get('base') not in ('B001','B031') or not a.get('count'):continue
   vs=[i for i,s in enumerate(seq[1:],1) if table.get(s,{}).get('base')=='B700']
   if len(vs)!=1:continue
   others=[s for i,s in enumerate(seq) if i not in (0,vs[0])]
   if others and table.get(others[0],{}).get('base') in ('B001','B031'):continue
   found.append((r['record_id'],int(a['count'])))
  saved=rows(RAW/('discovery-v1' if half=='discovery' else 'confirmation-v1')/'events.jsonl')
  check(half+' event extraction',sorted(found)==sorted((r['record_id'],r['value']) for r in saved))
  independent[half]=saved
 all_events=independent['discovery']+independent['confirmation']
 fish=[r for r in all_events if r['fish'] and r['harappa_tablet'] and r['v_code']=='700' and r['strict_stroke']]
 check('four core catalogue entries',{r['source_cisi'] for r in fish}=={'H-302','H-912','H-1191','H-1192'})
 check('four in every core entry',all(r['value']==4 and r['stroke']=='B001' and r['item']=='220' for r in fish))
 check('three after and one before',Counter(r['v_position'] for r in fish)=={1:3,2:1})
 check('two dependency components in full series',len({r['component'] for r in fish})==2)
 confirmed=[r for r in fish if r in independent['confirmation']]
 check('three reserved objects one component',len(confirmed)==3 and len({r['component'] for r in confirmed})==1)
 # Construct source-wide carrier signatures independently for the empirical references.
 training=[];seen=set()
 for e in sorted(independent['discovery'],key=lambda r:r['record_id']):
  if not (e['harappa_tablet'] and e['v_code']=='700' and e['strict_stroke']):continue
  key=(e['object_type'],tuple(tuple(x) for x in e['prototype']),tuple(e['seq']))
  if key in seen:continue
  seen.add(key)
  if not e['fish']:training.append(e)
 counts=Counter(e['value'] for e in training)
 q=Fraction(2*counts[4]+1,2*len(training)+24)
 short=[e for e in training if e['stroke']=='B001']
 qs=(sum(e['value']==4 for e in short)+2*q)/(len(short)+2)
 expected=[math.log2(float(Fraction(9,10)/q)),math.log2(float(Fraction(9,10)/qs))]
 result=read(HERE/'confirmation-v1/comparison.json')
 for name,gain in zip(('pooled','stroke_conditioned'),expected):
  got=result['comparisons'][name]
  check(name+' gain independently recovered',abs(got['mean_bits']-gain)<1e-12)
  check(name+' exact tail and minimum-size failure',got['p_one_sided']==float(Fraction(1,2)) and not got['pass'])
 model=read(HERE/'discovery-v1/model.json')
 check('nonfish counts recovered',{str(k):v for k,v in counts.items()}==model['nonfish_counts'])
 for name,dist in [('pooled',model['pooled']),('short',model['stroke_conditioned']['B001']),('long',model['stroke_conditioned']['B031']),('fixed_four',model['fixed_four'])]:
  check(name+' probabilities sum to one',abs(sum(dist.values())-1)<1e-12 and all(v>0 for v in dist.values()))
 check('fixed-quota exact tie',result['comparisons']['fixed_quota']['mean_bits']==0 and result['comparisons']['fixed_quota']['ties']==1)
 check('broad non-four example preserved',any(e['source_cisi']=='M-928' and e['value']==1 and e['v_code']=='705' and e['item']=='243' for e in all_events))
 reg=rows(RAW/'register-v1/objects.jsonl');coverage=read(HERE/'register-v1/coverage.json')
 check('767 unique related families',len(reg)==len({r['object_family_id'] for r in reg})==767)
 check('1350 related faces',sum(len(r['faces']) for r in reg)==1350)
 check('register hash',sha(RAW/'register-v1/objects.jsonl')==coverage['register_sha256'])
 refs={c:r for r in reg for c in r['cisi']}
 a,b=refs['H-912'],refs['H-1191']
 check('identity collision retained without merge',a['object_family_id']!=b['object_family_id'] and a['faces'][0]['metadata']['excavation-idno']==b['faces'][0]['metadata']['excavation-idno']=='8650c448')
 for source in read(HERE/'sources-v1.json')['sources']:
  check('witness '+source['id'],sha(ROOT/source['path'])==source['sha256'])
 for im in read(HERE/'inspection-v1.json')['image_inputs']:
  check('inspection hash '+Path(im['file']).name,sha(ROOT/im['file'])==im['sha256'])
 check('synthetic guard passed',read(HERE/'shots-synthetic-v1.json')['pass'])
 output={'verification_tier':'submitted; author arithmetic and source-integrity checks',
    'pass':all(c['pass'] for c in checks),'checks_count':len(checks),'checks':checks,
    'independent_gain_bits':dict(zip(('pooled','stroke_conditioned'),expected)),
    'scope':'No imported scoring implementation. This checks arithmetic and preserved source identity; it does not authenticate literal meanings, physical joins or model freshness.',
    'code_sha256':sha(Path(__file__))}
 with (HERE/'verification-v1.json').open('x',encoding='utf8') as f:json.dump(output,f,indent=2);f.write('\n')
 print(json.dumps({k:output[k] for k in ('pass','checks_count','independent_gain_bits')}))
 if not output['pass']:raise SystemExit(1)


if __name__=='__main__':main()
