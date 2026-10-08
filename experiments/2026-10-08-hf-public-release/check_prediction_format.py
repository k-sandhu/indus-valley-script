"""Exercise the card's minimal format, frozen aliases and missing-field errors."""
import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path
import pyarrow.parquet as pq
from build_release import HERE,RAW,dump,read,environment
from validate_release import equal

def main():
    environment();p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');p.add_argument('--out',type=Path,required=True);p.add_argument('--raw-out',type=Path,required=True);a=p.parse_args()
    if a.out.exists() or a.raw_out.exists():raise FileExistsError('Fresh paths required')
    a.raw_out.mkdir(parents=True)
    card=(a.release/'README.md').read_text(encoding='utf8')
    required=re.search(r'Required row fields are (.*?)\.',card).group(1)
    keys=re.findall(r'`([^`]+)`',required)
    assert keys==['sample_index','occurrence_key','pdf_page','printed_inscription_id','classification_literal','units'],keys
    field_doc=(a.release/'FIELD-DEFINITIONS.md').read_text(encoding='utf8')
    assert all(k in field_doc for k in ['printed_inscription_id','classification_literal','inscription_number','classification_code'])
    expected=read(a.release/'benchmark/expected-metrics.json');cases=[]
    for version in ['v1','v2','v3']:
        source=[json.loads(r['prediction_json']) for r in pq.read_table(a.release/'data'/f'benchmark_rows_{version}.parquet',columns=['prediction_json']).to_pylist()]
        minimal=[]
        for row in source:
            value={k:row[k] for k in keys if k not in ['printed_inscription_id','classification_literal','units']}
            value.update(printed_inscription_id=row['inscription_number'],classification_literal=row['classification_code'],units=[dict(confidence=u['confidence'],alternatives=[dict(codes=x['codes']) for x in u['alternatives']]) for u in row['units']])
            if version!='v1':value['section']=row['section']
            minimal.append(value)
        variants={'card-minimal':copy.deepcopy(minimal),'frozen-alias-minimal':copy.deepcopy(minimal),'null-values':copy.deepcopy(minimal)}
        for row in variants['frozen-alias-minimal']:
            row['inscription_number']=row.pop('printed_inscription_id');row['classification_code']=row.pop('classification_literal')
        variants['null-values'][0].update(printed_inscription_id=None,classification_literal=None)
        for field,alias in [('printed_inscription_id','inscription_number'),('classification_literal','classification_code')]:
            d=copy.deepcopy(minimal);d[0].pop(field);variants['missing-'+field]=d
            d=copy.deepcopy(minimal);d[0][alias]='DIFFERENT';variants['conflicting-'+field]=d
            d=copy.deepcopy(minimal);d[0][field]=123;variants['numeric-'+field]=d
        for name,data in variants.items():
            path=a.raw_out/(version+'-'+name+'.jsonl');path.write_text('\n'.join(json.dumps(r) for r in data)+'\n',encoding='utf8')
            output=a.raw_out/(version+'-'+name+'-scores.json')
            result=subprocess.run([sys.executable,'-B',str(a.release/'code/score_benchmark.py'),'--release',str(a.release),'--benchmark',version,'--predictions',str(path),'--out',str(output)],capture_output=True,text=True)
            (a.raw_out/(version+'-'+name+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
            passing=name in ['card-minimal','frozen-alias-minimal','null-values']
            item=dict(benchmark=version,case=name,returncode=result.returncode,output_created=output.exists(),passed=(result.returncode==0)==passing)
            if passing and result.returncode==0:
                score=read(output);summary=score['summary']
                item.update(number_correct=summary['inscription_number_accuracy']['success'],classification_correct=summary['classification_exact_accuracy']['success'],total=len(data),calibration_n=summary['calibration']['n'])
                if name!='null-values':
                    differences=equal(expected[version],{k:score[k] for k in expected[version]});item.update(mismatches=len(differences),differences=differences)
                    item['passed']=item['passed'] and not differences
            else:
                item['passed']=item['passed'] and not output.exists() and ('printed_inscription_id' in result.stderr if 'inscription' in name else 'classification_literal' in result.stderr)
            cases.append(item)
    passed=all(c['passed'] for c in cases)
    dump(a.out,dict(status='Verified computation' if passed else 'Failed',documented_row_fields=keys,passing_cases=sum(c['returncode']==0 for c in cases),rejected_cases=sum(c['returncode']!=0 for c in cases),cases=cases))
    print(json.dumps(dict(passed=passed,cases=len(cases))))
    if not passed:raise SystemExit(1)

if __name__=='__main__':main()
