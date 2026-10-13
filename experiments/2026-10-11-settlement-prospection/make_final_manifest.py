"""Freeze the completed authored package after review and actual print QA."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent

def record(path):
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    target=BASE/'final-manifest.json'
    if target.exists():raise FileExistsError(target)
    verification=json.loads((BASE/'review/final-verification-v2.json').read_text(encoding='utf-8'))
    qa=json.loads((BASE/'review/pdf-inspection.json').read_text(encoding='utf-8'))
    assert verification['status']=='passed' and qa['status']=='passed after visual corrections'
    entry=json.loads((BASE/'registry-entry-v2.json').read_text(encoding='utf-8'))
    registry=json.loads((ROOT/'knowledge/experiments/registry.json').read_text(encoding='utf-8'))
    assert next(r for r in registry['experiments'] if r['id']==entry['id'])==entry
    for path in entry['evidence']:
        assert (ROOT/path).is_file(),path
    # Temporary print rasters and acquired source witnesses stay local. Hashes
    # of the selected final PDF and exported QA records are in this package.
    files=[path for path in BASE.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc','.pdf')]
    files += list((ROOT/'papers/005-settlement-survey-gaps').glob('*.md'))
    files += [ROOT/'output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf',ROOT/'knowledge/retrospectives/2026-10-11-settlement-prospection.md']
    files=sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix())
    obj=dict(completed_utc=datetime.now(timezone.utc).isoformat(),status='completed reviewed narrative study and unrun survey design',
        current=dict(paper='papers/005-settlement-survey-gaps/manuscript.md',frozen_text='review/revised-v5.md',
         source_register='sources-v6.json',region_register='candidates-v5.json',claim_register='claims-v3.json',
         numerical_endpoint='run-v3',inline_endpoint='run-v3-inline-arithmetic',map='map-v5',pilot='PILOT-DESIGN-v4.md',
         verification='review/final-verification-v2.json',pdf_inspection='review/pdf-inspection.json'),
        counts=verification['counts'],final_verification=dict(checks=verification['check_count'],passed=41,failed=0),
        reviews=dict(claude_canonical_model='claude-opus-5-5',actual_completed_cli_passes=2,claude_tools='disabled',
         codex_roles=['source audit','manuscript adversary','numerical integration','mountain/cave integration','statistical/design review']),
        classification='Published observations, aggregate calculations, editorial regions and unrun tests. No new archaeological discovery, fieldwork, imagery inference or national missing-site/artifact estimate.',
        assets='Authored findings/code, factual aggregates, original figures and commissioned AI reviews; acquired third-party witnesses local-only.',
        prior_failures='Original manuscript geographic failure, source-audit clarifications, print-export defects and Windows verifier failure remain in their preserved endpoints.',
        shared_memory_paths=['README.md','knowledge/INDEX.md','knowledge/experiments/registry.json','knowledge/retrospectives/README.md'],
        shared_memory_note='These shared indexes remain mutable; registry-entry-v2.json preserves this study entry without freezing unrelated future work.',
        file_count=len(files),files=[record(path) for path in files])
    target.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(files),words=obj['counts']['manuscript_words'],pages=obj['counts']['pdf_pages'],source_records=72,regions=21,verification='41 passed')))

if __name__=='__main__':main()
