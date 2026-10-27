"""Author replay of known regressions and source boundaries; no reading scores."""
from collections import Counter
import io
import json
import unittest
import extract as e

def main():
    records=e.rows(e.RAW/'run-v1/winslow-entries.jsonl')
    index={e.identifier(r):r for r in records}
    packets=json.loads((e.ROOT/'data/raw/2026-10-22-lexical-source-review/run-v1/compound-packets-v2.json').read_text(encoding='utf8'))
    reviewed=[]
    for packet in packets:
        r=index[e.identifier(packet['entry'])]
        blocks=packet['witnesses']
        assert len(blocks)==1
        source=e.ROOT/blocks[0]['source_path']
        assert e.sha(source)==blocks[0]['source_sha256']
        for ref in r['lexicon_boundary_sources']:
            path=e.TLRAW/f'page-{ref["page"]:05d}.html'
            assert e.sha(path)==ref['source_sha256']
            source_rows=e.w.parse_tamil_lex.parse_page(path.read_text(encoding='utf8'),ref['page'])
            assert any(t['head']==r['head'] and t['translit']==ref['translit'] and
                       t['hom']==ref['hom'] and t['members']==ref['members'] for t in source_rows)
        reviewed.append(dict(sample_id=packet['sample_id'],head=r['head'],page=r['page'],
            old_members=r['original_members'],new_members=r['members'],
            boundary_status=r['boundary_review_status'],increment_candidates=r['increment_candidates'],
            parent_origin_mark_present=r['parent_origin_mark_present'],source_identity_and_hash=True))
    def find(form,page):
        hits=[r for r in records if r['translit_plain']==form and r['page']==page]
        assert len(hits)==1,(form,page,len(hits))
        return hits[0]
    checks={
        'known_ja_letter_root_suppressed':find('jamīṉ',528)['members']==[],
        'known_aintaru_boundary_corrected':find('aintaru',195)['members']==['ai','taru'],
        'known_aintaru_second_parent_recovered':find('aintaru',553)['members']==['ai','taru'],
        'known_increment_flower_candidate_only':find('murukkampū',883)['members']==[] and len(find('murukkampū',883)['increment_candidates'])==1,
        'known_increment_wood_candidate_only':find('murukkañcettal',501)['members']==[] and len(find('murukkañcettal',501)['increment_candidates'])==1,
        'all_comparative_scorer_eligibility_false':not any(r['comparative_scorer_eligible'] for r in records),
        'full_row_population_preserved':len(records)==len(e.rows(e.OLD)),
        'all_reviewed_source_identities_bound':len(reviewed)==43,
        'synthetic_segmentation_pass':json.loads((e.PKG/'segmentation-synthetic-v1.json').read_text())['pass'],
        'synthetic_shots_pass':json.loads((e.PKG/'shots-synthetic-v1.json').read_text())['pass']}
    suite=unittest.defaultTestLoader.discover(str(e.PKG/'code'),pattern='test_extract.py')
    stream=io.StringIO()
    tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    checks['focused_tests_pass']=tests.wasSuccessful()
    # Retain the grammatical increment's full original source block locally.
    am=[]
    for source,page in [(e.WRAW/'page-00031.html',31),(e.TLRAW/'page-00094.html',94)]:
        for block in e.w.DIV_RE.findall(source.read_text(encoding='utf8')):
            if '<hw>' not in block:continue
            if ('<b>அம்</b>' in block or '<tam>அம்³</tam>' in block):
                am.append(dict(source=str(source.resolve()),page=page,sha256=e.sha(source),raw_html=block))
    e.dump(e.RAW/'run-v1/known-regressions-and-prior-sample.json',reviewed)
    e.dump(e.RAW/'run-v1/increment-source-blocks.json',am)
    result=dict(pass_all=all(checks.values()),checks=checks,tests_run=tests.testsRun,
        test_output=stream.getvalue(),reviewed_rows=len(reviewed),
        revised_status_counts=dict(Counter(r['boundary_status'] for r in reviewed)),
        known_regressions=True,independent_linguistic_validation=False,
        source_blocks_reparsed_for_every_Lexicon_reference_in_known_review=True,
        real_confirmation_access=False,substantive_rebus_recomputed=False)
    e.dump(e.PKG/'validation-v1.json',result)
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['pass_all'] else 1

if __name__=='__main__':raise SystemExit(main())
