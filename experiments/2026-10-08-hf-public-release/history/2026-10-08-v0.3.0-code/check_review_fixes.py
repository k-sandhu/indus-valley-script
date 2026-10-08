"""Check licensing, CFF, privacy, prediction failures and passing replay."""
from pathlib import Path
import argparse
import json
import math
import re
import subprocess
import sys
import yaml
import jsonschema
import pyarrow.parquet as pq
from build_release import HERE, RAW, dump, read, environment, sha
from release_policy import AUTHOR,DATASET_ID,ISSUES_URL

def main():
    environment();p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');p.add_argument('--out',type=Path,default=HERE/'review-fixes-check-2026-10-08-v6.json');p.add_argument('--raw-out',type=Path,default=RAW/'cf6');a=p.parse_args()
    if a.out.exists() or a.raw_out.exists():raise ValueError('Choose fresh report paths')
    a.raw_out.mkdir(parents=True)
    schema=read(RAW/'review-fixes-2026-10-08-sources/cff-schema-1.2.0.json');cff=yaml.safe_load((a.release/'CITATION.cff').read_text())
    errors=[e.message for e in jsonschema.Draft7Validator(schema).iter_errors(cff)]
    license_files={n:sha(a.release/'LICENSES'/n)==sha(RAW/'review-fixes-2026-10-08-sources'/n) for n in ['CC0-1.0.txt','CC-BY-4.0.txt','Unlicense.txt']}
    pat=re.compile(r'indus-valley-script|indus-research-data|[A-Za-z]:[/\\]Users|OneDrive|(?<![\w/])(?:experiments|data/(?:raw|normalized))/|\.\./|\bTODO\b|NAMESPACE/|metbron|gmail|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|hf_[A-Za-z0-9]{20,}',re.I)
    hits=[]
    for f in a.release.rglob('*'):
        if not f.is_file():continue
        if f.suffix=='.parquet':text=json.dumps(pq.read_table(f).to_pylist(),default=lambda x:'PNG bytes')
        elif f.suffix!='.png':text=f.read_text(encoding='utf-8-sig')
        else:continue
        for m in pat.finditer(text):hits.append(dict(file=f.relative_to(a.release).as_posix(),match=m.group()))
    cases=[]
    for version in ['v2','v3']:
        rows=pq.read_table(a.release/'data'/f'benchmark_rows_{version}.parquet').to_pylist();pred=[json.loads(r['prediction_json']) for r in rows]
        for name in ['missing-confidence','missing-section','invalid-confidence','invalid-section','passing']:
            copy=json.loads(json.dumps(pred))
            if name=='missing-confidence':copy[0]['units'][0].pop('confidence')
            if name=='missing-section':copy[0].pop('section')
            if name=='invalid-confidence':copy[0]['units'][0]['confidence']=1.1
            if name=='invalid-section':copy[0]['section']='unknown'
            input_path=a.raw_out/(version+'-'+name+'.json');dump(input_path,copy);score=a.raw_out/(version+'-'+name+'-scores.json')
            cmd=[sys.executable,'-B',str(a.release/'code/score_benchmark.py'),'--release',str(a.release),'--benchmark',version,'--predictions',str(input_path),'--out',str(score)]
            result=subprocess.run(cmd,capture_output=True,text=True);(a.raw_out/(version+'-'+name+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
            expected_pass=name=='passing';ok=(result.returncode==0)==expected_pass
            record=dict(benchmark=version,case=name,returncode=result.returncode,passed=ok,output_created=score.exists())
            if expected_pass:
                d=read(score);expected=read(a.release/'benchmark/expected-metrics.json')[version]
                from validate_release import equal
                mismatch=equal(expected,{k:d[k] for k in expected});finite=all(math.isfinite(x) for interval in d['row_bootstrap_95'].values() for x in interval)
                record.update(score_mismatches=len(mismatch),finite_bootstrap_intervals=finite,calibration_n=d['summary']['calibration']['n']);record['passed']=ok and not mismatch and finite
            else:record['passed']=ok and not score.exists() and ('confidence' in result.stderr if 'confidence' in name else 'section' in result.stderr)
            cases.append(record)
    names={x.relative_to(a.release).as_posix() for x in a.release.rglob('*') if x.is_file()}
    prohibited={'RELEASE-CHECKLIST.md','LICENSE-MIT','provenance/rights-audit.json','provenance/input-manifest.json'}
    result=dict(status='Verified computation',cff=dict(schema='CFF 1.2.0',schema_sha256=sha(RAW/'review-fixes-2026-10-08-sources/cff-schema-1.2.0.json'),validator='jsonschema Draft7Validator',errors=errors,authors=cff['authors']),official_license_texts_equal=license_files,privacy=dict(hits=hits,authorized_public_identifiers=[AUTHOR,DATASET_ID,ISSUES_URL]),excluded_private_files_absent=not bool(names&prohibited),prediction_cases=cases,local_only=True)
    if errors or hits or not all(license_files.values()) or not result['excluded_private_files_absent'] or not all(c['passed'] for c in cases):result['status']='Failed'
    dump(a.out,result);print(json.dumps(result,indent=2))
    if result['status']=='Failed':raise SystemExit(1)

if __name__=='__main__':main()
