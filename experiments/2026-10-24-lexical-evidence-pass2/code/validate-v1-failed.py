import hashlib,json,sys,unittest,re
from functools import cache
from prepare import *
sys.path.insert(0,str(ROOT/'experiments/2026-10-22-lexical-source-review/code'))
import source_blocks as sb
@cache
def checked_hash(path):return sha(Path(path))
class SourceTests(unittest.TestCase):
 def test_frozen_selection_and_inputs(self):
  f=read(PKG/'FREEZE-v1.json');s=read(RAW/'case-selection-v1.json')
  self.assertEqual(sha(PKG/'PROTOCOL.md'),f['protocol_sha256'])
  self.assertEqual(sha(RAW/'case-selection-v1.json'),f['selection_sha256'])
  self.assertEqual(sha(OLD/'run-v1/winslow-entries.jsonl'),f['input_sha256'])
  self.assertEqual(sha(OLD/'increment-audit-v1/candidate-audit.json'),f['audit_sha256'])
  self.assertEqual(len({x['entry']['entry_id'] for x in s}),16)
  self.assertEqual(Counter(x['stratum'] for x in s),dict(folding_dependent=2,exact_candidate=6,boundary_conflict=6,known_increment=2))
 def test_all_source_witnesses(self):
  for p in read(RAW/'source-packets-v2.json'):
   w=p['winslow_witness'];path=ROOT/w['logical_path']
   self.assertEqual(checked_hash(path),w['sha256'])
   self.assertEqual(len(sb.exact_winslow_blocks(path.read_text(encoding='utf8'),p['entry'])),1)
   for t in p['lexicon_entries']:
    w=t['witness'];path=ROOT/w['logical_path'];self.assertEqual(checked_hash(path),w['sha256'])
    parsed=sb.winslow.parse_tamil_lex.parse_page(path.read_text(encoding='utf8'),t['entry']['page'])
    self.assertIn(t['entry'],parsed)
   for d in p['dedr_entries']:
    self.assertTrue(any(form in p['exact_queries'] for g in d['matched_tamil_groups'] for form in g['forms']))
    self.assertTrue(all(g['lang']=='Ta' for g in d['matched_tamil_groups']))
    for w in d['witnesses']:
     path=ROOT/w['logical_path'];self.assertEqual(checked_hash(path),w['sha256'])
     self.assertIn(w['raw_html'],path.read_text(encoding='utf8'))
 def test_review_population_and_admission(self):
  review=read(RAW/'source-review-v1.json');self.assertEqual(len(review),16)
  self.assertTrue(all(not r['specialist_adjudication'] and r['prior_scorer_eligibility_unchanged'] for r in review))
  self.assertEqual(sum(len(x['selected_lexicon_senses']) for x in review),35)
  self.assertEqual(len({d['number'] for x in review for d in x['selected_dedr_entries']}),23)
 def test_regressions_and_wrong_senses_retained(self):
  idx={r['case_id']:r for r in read(RAW/'source-review-v1.json')}
  self.assertEqual(idx['L08']['source_disposition'],'increment_candidate_contradicted_by_source_sense')
  self.assertIn('verbal noun',idx['L15']['judgment'])
  self.assertIn('sweetness',idx['L06']['judgment'])
  self.assertIn('Sanskrit',idx['L14']['judgment'])
 def test_grammar_source_bytes_and_coordinates(self):
  logs=read(RAW/'grammar-acquisition-v1.json')
  for r in logs:
   if 'physical_path' in r:self.assertEqual(sha(Path(r['physical_path'])),r['sha256'])
  pages=read(RAW/'wilden-pages-v1.json')
  self.assertIn('m + k',pages[27]['text']);self.assertIn('m + c',pages[27]['text']);self.assertIn('m + t',pages[27]['text'])
  self.assertIn('Dezember 2016',pages[4]['text'])
  self.assertTrue((RAW/'wilden-pdf-028.png').exists())
def main():
 import io
 output=io.StringIO();tests=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
 save(PKG/'validation-v1.json',dict(pass_all=tests.wasSuccessful(),tests_run=tests.testsRun,output=output.getvalue(),
  author_validation=True,independent_specialist_review=False,source_review_sha256=sha(RAW/'source-review-v1.json')))
 print(output.getvalue());return 0 if tests.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
