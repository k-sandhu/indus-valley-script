"""Run preserved reviewer checks with outputs redirected; never edit review/."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import pyarrow.parquet as pq
from build_release import HERE, ROOT, RAW, environment, dump, read, sha
from extract_images import embedded_images

def main():
    environment()
    parser=argparse.ArgumentParser();parser.add_argument('--release',type=Path,default=HERE/'release');parser.add_argument('--out',type=Path,default=RAW/'rr6');parser.add_argument('--records',type=Path,default=HERE/'build-records'/'r6')
    a=parser.parse_args();release=a.release.resolve();out=a.out.resolve()
    if not out.is_relative_to(RAW) or out.exists():raise ValueError('Choose a new raw output directory')
    out.mkdir(parents=True);view=out/'view'
    shutil.copytree(release,view)
    embedded=dict(embedded_images(release))
    for name,data in embedded.items():
        p=view/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    table=pq.read_table(view/'data/image_assets.parquet');rows=table.to_pylist();mapping=read(a.records/'portable-source-map.json')
    for row in rows:row['source_path']=mapping[row['source_path']]
    pq.write_table(__import__('pyarrow').Table.from_pylist(rows,schema=table.schema),view/'data/image_assets.parquet',compression='zstd')
    adaptations=['Redirect output paths and scratch caches in memory; original scripts remain unchanged.',
        'Load/image checks and legacy snippets read a raw materialized snapshot with all embedded PNGs extracted.',
        'Parent image audit restores source_path from the private portable-source map in that raw view only.',
        'Privacy, field definitions, rights scans and manifest check read the actual public release.',
        'Hosted card examples are exercised through local-only Hub function substitutions. No network repository is created or queried.']
    for v in ['v1','v2']:
        result=subprocess.run([sys.executable,'-B',str(release/'code/score_benchmark.py'),'--release',str(release),'--benchmark',v,'--out',str(out/f'staged-{v}.json')],capture_output=True,text=True)
        (out/f'score-{v}.log').write_text(result.stdout+result.stderr,encoding='utf8')
        if result.returncode:raise RuntimeError(result.stderr)
    summary={}
    scripts=['load_check.py','readme_snippets.py','image_audit.py','rights_scan_sequences.py','rights_scan_prose.py','rights_scan_fields.py','privacy_scan.py','field_definitions_check.py','compare_scores.py','manifest_check.py']
    for name in scripts:
        script=HERE/'review'/name;source=script.read_text(encoding='utf8');code=source
        # Redirect all original reviewer output files, retaining their computation.
        code=re.sub(r'(?:PKG|REL\.parent) / "review/([^\"]+)"',r'OUT / "\1"',code)
        code=re.sub(r'ROOT / "experiments/2026-10-08-hf-public-release/review/([^\"]+)"',r'OUT / "\1"',code)
        code=code.replace('ROOT / "data/raw/2026-10-08-hf-public-release/review-scan"','OUT / "scan"')
        code=code.replace('ROOT / "data/raw/2026-10-08-hf-public-release/review-scores"','OUT')
        code=code.replace('ROOT / "data/raw/2026-10-08-hf-public-release/review-cache"','OUT / "cache"')
        target=view if name in ['load_check.py','image_audit.py','readme_snippets.py'] else release
        code=code.replace('PKG / "release"','TARGET')
        code=code.replace('ROOT / "experiments/2026-10-08-hf-public-release/release"','TARGET')
        code=code.replace('repo = "experiments/2026-10-08-hf-public-release/release"','repo = str(TARGET)')
        if name=='readme_snippets.py':
            code=code.replace('raw = os.path.abspath("data/raw/2026-10-08-hf-public-release")','raw = str(OUT / "snippets")')
        os.chdir(ROOT);stream=io.StringIO();error=None
        try:
            with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                exec(compile(code,str(script),'exec'),{'__file__':str(script),'__name__':'__main__','OUT':out,'TARGET':target})
        except Exception as e:error=repr(e)
        (out/(name+'.log')).write_text(stream.getvalue()+('\nERROR: '+error if error else ''),encoding='utf8')
        summary[name]=dict(source_sha256=sha(script),executed_source_sha256=hashlib.sha256(code.encode()).hexdigest(),completed=error is None,error=error)
        print(name, 'completed' if error is None else error,flush=True)
    # Execute the current hosted snippets against local equivalents.
    os.chdir(RAW)
    import datasets,huggingface_hub
    original_load=datasets.load_dataset;original_names=datasets.get_dataset_config_names;original_snapshot=huggingface_hub.snapshot_download
    from release_policy import DATASET_ID
    datasets.load_dataset=lambda repo,*args,**kwargs:original_load(str(release) if repo==DATASET_ID else repo,*args,cache_dir='snippet6',**kwargs)
    datasets.get_dataset_config_names=lambda repo,*args,**kwargs:original_names(str(release) if repo==DATASET_ID else repo,*args,**kwargs)
    huggingface_hub.snapshot_download=lambda repo,**kwargs:str(view) if repo==DATASET_ID else (_ for _ in ()).throw(ValueError('Unexpected repository'))
    snippet_result=[];namespace={}
    try:
        for i,block in enumerate(re.findall(r'```python\n(.*?)\n```', (release/'README.md').read_text(encoding='utf8'),re.S)):
            if 'my-predictions.jsonl' in block:
                snippet_result.append(dict(block=i,checked='CLI format separately tested with complete/incomplete prediction files'));continue
            exec(compile(block,'public-card-snippet','exec'),namespace)
            snippet_result.append(dict(block=i,passed=True))
    finally:
        datasets.load_dataset=original_load;datasets.get_dataset_config_names=original_names;huggingface_hub.snapshot_download=original_snapshot
    dump(out/'hosted-snippets-local.json',snippet_result)
    dump(out/'rerun-summary.json',dict(scripts=summary,adaptations=adaptations,hosted_snippets=snippet_result))
    if any(not v['completed'] for v in summary.values()):raise SystemExit(1)

if __name__=='__main__':main()
