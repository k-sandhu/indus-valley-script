"""Verify the selected evidence and preservation, without recomputing old tests."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',default='run-v6')
    parser.add_argument('--output',default='verification-v2.json')
    args=parser.parse_args()
    dest=HERE/args.output
    run=HERE/args.run
    if dest.exists():raise SystemExit('Preserve verification endpoints')
    old=read(HERE/'run-v2/preservation-inputs.json')['files']
    changed=[r['path'] for r in old if not (ROOT/r['path']).exists() or sha(ROOT/r['path'])!=r['sha256']]
    data=read(run/'catalogue-data.json')
    examples=read(run/'example-provenance.json')['examples']
    source={r['record_id']:r for r in [json.loads(x) for x in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]}
    for e in examples:
        r=source[e['record_id']];i=e['start_slot_one_based']-1
        assert r['signs_reading_rtl'][i:i+len(e['codes'])]==e['codes']
        assert r['source_cisi']==e['cisi'] and r['object_family_id']==e['object_family_id']
    assert len(data['rows'])==713 and data['counts']['shortlist']==9 and data['shortlist_families']==7
    assert len(examples)==20 and max(len(e['codes']) for e in examples)<=3
    assert len({r['code'] for r in data['rows']})==713
    medial=source['2162.1']['signs_reading_rtl'];assert 0<medial.index('142')<len(medial)-1
    variant=source['834.2']['signs_reading_rtl'];assert variant[-2:]==['158','400']
    for r in data['rows']:
        for d in r['drawings']:
            assert d['path'].startswith('output/chart_atlas/cells/')
            assert (ROOT/d.get('focused_path',d['path'])).is_file()
    for c in read(run/'chart-crop-manifest.json')['rows']:
        assert sha(ROOT/c['source'])==c['source_sha256'] and sha(ROOT/c['output'])==c['sha256']
    for r in read(run/'build-manifest.json')['inputs']:
        assert sha(ROOT/r['path'])==r['sha256'],r['path']
    report=(HERE/'REPORT.md').read_text(encoding='utf-8')
    positions={r['code']:r for r in read(HERE/'run-v2/position-audit.json')['rows']}
    for c in ['151','154','156','161','400','527','617']:
        r=positions[c];f=r['positions']['final'];s=r['family_sensitivity']
        expected=f"| W{c} | {f['observed']}/{r['non_singleton_tokens']} | {f['shuffle_expected']:.3f}"
        assert expected in report,(c,expected)
        assert f"| {s['final']}/{s['tokens']} |" in report
    assert not changed,changed
    out=dict(status='pass',preserved_prior_files=len(old),changed_prior_files=changed,
        codes=713,shortlist_codes=9,shortlist_families=7,selected_examples=20,
        distinct_example_families=len({e['object_family_id'] for e in examples}),
        exact_sanskrit_senses=len(read(run/'sanskrit-senses.json')['rows']),
        example_validation='All selected windows, CISI and family identifiers matched pinned local input',
        public_images='Reviewed detail crops of CC BY chart cells; one authored SVG schematic; no font or artifact image',
        browser_checks={'desktop_cards':9,'all_code_filter':713,'sanskrit_search_bharin_codes':['151','154','156','158','161'],
            'shortlist_loaded_images':'See browser-qa-v6.json for the measured count','broken_images':0,'mobile_viewport':[390,844],'horizontal_overflow':False,
            'scope':'Playwright manual UI checks. Screenshot inspected. An earlier draft generated a favicon-only 404, fixed in the final template.'},
        browser_qa=read(HERE/'browser-qa-v6.json'),
        diagnostic_files_hashed=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for directory in ['run-v2','diagnostics-v3','context-diagnostics-v1','lexical-diagnostics-v3'] for p in sorted((HERE/directory).rglob('*')) if p.is_file()],
        saved_permutation_file=dict(path='data/raw/2026-10-11-bonta-adversarial/run-v2/position-permutations.npz',sha256=sha(ROOT/'data/raw/2026-10-11-bonta-adversarial/run-v2/position-permutations.npz')),
        claude_review=read(HERE/'claude-review-execution.json') if (HERE/'claude-review-execution.json').is_file() else 'No completed external review',
        output_hashes=[dict(path=p.relative_to(HERE).as_posix(),sha256=sha(p)) for p in sorted(run.rglob('*')) if p.is_file()],
        scope='Evidence pointers, figures, selected arithmetic and endpoint preservation; semantic choices remain hypotheses')
    dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['status','preserved_prior_files','codes','shortlist_codes','selected_examples','exact_sanskrit_senses']}))
if __name__=='__main__':main()
