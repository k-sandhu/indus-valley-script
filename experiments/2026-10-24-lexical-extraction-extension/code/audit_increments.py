"""Audit frozen increment candidates using exact surface and lemma equality."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[3]
PKG=Path(__file__).resolve().parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-lexical-extraction-extension')

def fold(s):return s.replace('ē','e').replace('ō','o')
def increments(s):return [s[:-1]+end for end in ('am','aṅ','añ','an')] if len(s)>=3 and s.endswith('u') else []
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')

def audit(form,candidate):
    a,b=candidate['surface_members'];left,right=candidate['lemma_candidates']
    checks={'surface_reconstructs_form':a+b==form,
            'left_surface_is_exact_increment':a in increments(left),
            'right_surface_equals_lemma':b==right}
    folded={'surface_reconstructs_form':fold(a+b)==fold(form),
            'left_surface_is_exact_increment':fold(a) in {fold(x) for x in increments(left)},
            'right_surface_equals_lemma':fold(b)==fold(right)}
    return dict(exact_checks=checks,exact_candidate=all(checks.values()),
        folding_dependent=not all(checks.values()) and all(folded.values()),
        failed_exact_checks=[k for k,v in checks.items() if not v],
        unexplained_mismatch=not all(folded.values()),
        morphology_status='unresolved_increment_morphology',scorer_eligible=False)

class AuditTests(unittest.TestCase):
    def candidate(self,a,b,left,right):return dict(surface_members=[a,b],lemma_candidates=[left,right])
    def test_pe_and_pe_long(self):
        self.assertTrue(audit('mārampē',self.candidate('māram','pē','māru','pē'))['exact_candidate'])
        self.assertTrue(audit('mārampē',self.candidate('māram','pē','māru','pe'))['folding_dependent'])
    def test_unaffected(self):
        self.assertTrue(audit('murukkampū',self.candidate('murukkam','pū','murukku','pū'))['exact_candidate'])
    def test_folded_prefix(self):
        self.assertTrue(audit('cērampū',self.candidate('ceram','pū','ceru','pū'))['folding_dependent'])
    def test_folded_right_root(self):
        self.assertTrue(audit('mārampē',self.candidate('māram','pē','māru','pe'))['folding_dependent'])
    def test_other_mismatch(self):
        x=audit('mārampī',self.candidate('māram','pī','māru','pē'))
        self.assertTrue(x['unexplained_mismatch']);self.assertFalse(x['folding_dependent'])

def main():
    source=RAW/'run-v1/winslow-entries.jsonl'
    expected=json.loads((PKG/'results-v1.json').read_text())['output_sha256']
    assert sha(source)==expected
    detailed=[];filtered=[]
    with source.open(encoding='utf8') as f:
        for line in f:
            r=json.loads(line)
            if not r['increment_candidates']:continue
            audited=[];exact=[]
            for candidate in r['increment_candidates']:
                result=audit(r['translit_plain'],candidate)
                assert candidate['scorer_eligible'] is False
                audited.append(dict(original_candidate=candidate,**result))
                if result['exact_candidate']:exact.append(candidate)
            detailed.append(dict(entry_id=r['entry_id'],page=r['page'],head=r['head'],
                form=r['translit_plain'],candidates=audited,original_members_unchanged=r['members']))
            filtered.append(dict(entry_id=r['entry_id'],exact_candidates=exact,
                morphology_status='unresolved_increment_morphology',scorer_eligible=False))
    out=RAW/'increment-audit-v1';out.mkdir(exist_ok=False)
    save(out/'candidate-audit.json',detailed);save(out/'exact-candidate-subset.json',filtered)
    candidates=[x for r in detailed for x in r['candidates']]
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary=dict(input_sha256=expected,rows_with_candidates=len(detailed),candidate_analyses=len(candidates),
        exact_candidate_analyses=sum(x['exact_candidate'] for x in candidates),
        folding_dependent_analyses=sum(x['folding_dependent'] for x in candidates),
        folding_dependent_rows=sum(any(x['folding_dependent'] for x in r['candidates']) for r in detailed),
        rows_retaining_exact_candidates=sum(bool(r['exact_candidates']) for r in filtered),
        unexplained_mismatch_analyses=sum(x['unexplained_mismatch'] for x in candidates),
        failed_equality_counts=dict(Counter(k for x in candidates for k in x['failed_exact_checks'])),
        tests_run=result.testsRun,tests_pass=result.wasSuccessful(),
        original_candidates_unchanged=True,all_morphology_unresolved=True,all_scorer_eligibility_false=True,
        source=source.as_posix(),code_sha256=sha(Path(__file__)),
        protocol_sha256=sha(PKG/'INCREMENT-AUDIT-PROTOCOL-v1.md'),
        outputs=[dict(physical_path=str(p),logical_path='data/raw/2026-10-24-lexical-extraction-extension/increment-audit-v1/'+p.name,
            bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())])
    save(PKG/'increment-audit-v1.json',summary)
    print(json.dumps(summary))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
