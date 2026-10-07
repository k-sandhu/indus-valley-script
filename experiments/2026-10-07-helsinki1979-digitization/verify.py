"""Read-only package audit; save the audit only to a new owned file."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from evaluate import align,aggregate

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'verification/2026-10-07-v1.json');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Audit output must be new and owned')
    frozen=json.loads((HERE/'freeze-manifest.json').read_text());checks={}
    paths={'code_sha256':HERE/'pipeline.py','chart_sha256':HERE/'chart-snapshot.json',
           'model_sha256':HERE/'development/classifier.pt','digit_classifier_sha256':HERE/'development/digits.npz',
           'calibration_sha256':HERE/'development/calibration.json',
           'source_sha256':ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf'}
    for key,path in paths.items():checks[key]=sha(path)==frozen[key]
    selection=json.loads((HERE/'blind/selection.json').read_text());ids=[r['sample_index'] for r in selection['rows']]
    checks['sixty_unique_selected_rows']=len(ids)==len(set(ids))==60
    checks['development_page_disjoint']=not ({r['pdf_page'] for r in selection['rows']}&set(frozen['parameters']['development_pages']))
    checks['page80_overview_excluded']=all(r['pdf_page']!=80 for r in selection['rows'])
    checks['crop_hashes']=all(sha(HERE/'blind'/r['source_crop'])==r['source_crop_sha256'] for r in selection['rows'])
    pfreeze=json.loads((HERE/'prediction-freeze.json').read_text());ppath=ROOT/pfreeze['predictions_path']
    checks['predictions_hash']=sha(ppath)==pfreeze['predictions_sha256']
    checks['selection_hash']=sha(HERE/'blind/selection.json')==pfreeze['selection_sha256']
    checks['insert_delete_alignment']=align([{1},{2}],[{1},{3},{2}])['edits']==1
    checks['ambiguous_set_alignment']=align([{1,2},{3}],[{2},{3,4}])['edits']==0
    checks['unresolved_reference_never_matches']=align([{1}],[set()])['edits']==1
    metrics=HERE/'evaluation/2026-10-07-frozen-v1/metrics.json'
    if metrics.exists():
        result=json.loads(metrics.read_text());computed=aggregate(result['rows'])
        checks['aggregate_metrics_reproduced']=computed==result['summary']
        checks['evaluator_hash']=sha(HERE/'evaluate.py')==result['evaluator_sha256']
        checks['reference_hashes']=all(sha(HERE/'blind'/name)==value for name,value in result['reference_sha256'].items())
    coverage=HERE/'runs/2026-10-07-full-v1/coverage.json'
    if coverage.exists():
        recorded=json.loads(coverage.read_text());path=coverage.parent/'occurrences.jsonl'
        numbers=units=unmatched=review=0;occurrences=[];page_counts={}
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                row=json.loads(line);occurrences.append(row['occurrence_key']);numbers+=row['inscription_number'] is not None
                units+=len(row['units']);unmatched+=sum(not u['alternatives'] for u in row['units']);review+=bool(row['flags'])
                page_counts[row['pdf_page']]=page_counts.get(row['pdf_page'],0)+1
                assert len(row['glyph_pdf_box'])==4 and row['serialization']=='visual_left_to_right'
        checks['full_unique_occurrences']=len(occurrences)==len(set(occurrences))
        checks['full_counts']=recorded['counts']==dict(printed_rows=len(occurrences),drawn_unit_candidates=units,
                        numbers_read=numbers,review_rows=review,unmatched_units=unmatched)
        checks['full_page_counts']=all(page_counts.get(p['pdf_page'],0)==p['rows'] for p in recorded['pages'])
        checks['all_corpus_pages_attempted']=[p['pdf_page'] for p in recorded['pages']]==list(range(22,181))
        checks['full_payload_hash']=sha(path)==recorded['occurrence_file_sha256']
    sizes={str(p.relative_to(ROOT)):sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) for p in (HERE,RAW)}
    # Installed package growth is measured from distribution records, not guessed.
    from importlib.metadata import distribution
    dependency_sizes={}
    for name in ('pymupdf','opencv-python-headless','jsonschema','attrs',
                 'jsonschema-specifications','referencing','rpds-py'):
        dist=distribution(name)
        dependency_sizes[name]=sum(dist.locate_file(p).stat().st_size for p in dist.files or [] if dist.locate_file(p).is_file())
    total=sum(sizes.values())+sum(dependency_sizes.values());checks['storage_below500MB']=total<500_000_000
    broken_links=[]
    for markdown in HERE.rglob('*.md'):
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',markdown.read_text(encoding='utf-8')):
            if re.match(r'^(?:https?://|#)',target):continue
            target=target.strip('<>').split('#',1)[0]
            local=(markdown.parent/target).resolve()
            # This audit itself is created after all checks finish.
            if local==out:continue
            if not local.exists():
                broken_links.append(dict(document=str(markdown.relative_to(HERE)),target=target))
    checks['local_markdown_links_exist']=not broken_links
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,
                broken_local_links=broken_links,
                local_link_note='The audit output itself is allowed as a pending target until this result is written.',
                storage=dict(paths_bytes=sizes,new_dependency_distribution_bytes=dependency_sizes,total_new_bytes=total,
                             limit_bytes=500_000_000),missing_checks=[] if metrics.exists() and coverage.exists() else ['Fresh evaluation or full endpoint absent'])
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
