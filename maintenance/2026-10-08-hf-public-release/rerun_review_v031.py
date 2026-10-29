"""Reuse the protected 0.3.0 review scripts with local targets and fresh outputs."""
import argparse
import contextlib
import hashlib
import io
import os
from pathlib import Path
import re
import subprocess
import sys
from build_release import HERE,ROOT,RAW,environment,read,dump,sha
from release_policy import DATASET_ID

def main():
    environment();p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');p.add_argument('--out',type=Path,required=True);p.add_argument('--rebuild',type=Path);a=p.parse_args()
    release=a.release.resolve();out=a.out.resolve();rebuild_path=a.rebuild.resolve() if a.rebuild else None
    if not out.is_relative_to(RAW) or out.exists():raise ValueError('Choose a fresh raw folder')
    out.mkdir(parents=True);(out/'scores').mkdir()
    for version in ['v1','v2','v3']:
        result=subprocess.run([sys.executable,'-B',str(release/'code/score_benchmark.py'),'--release',str(release),'--benchmark',version,'--out',str(out/'scores'/('staged-'+version+'.json'))],capture_output=True,text=True)
        (out/('score-'+version+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
        if result.returncode:raise RuntimeError(result.stderr)
    scripts=['hub_load_check.py','chart_check.py','flag_check.py','readings_flag_check.py','v3_content_check.py','readme_snippets_v3.py','image_audit_v3.py','field_definitions_check_v3.py','compare_scores_v3.py','manifest_check_v3.py','privacy_scan_v3.py','rights_scan_fields_v3.py','rights_scan_sequences_v3.py','rights_scan_prose_v3.py']
    if a.rebuild:scripts.append('rebuild_compare_v3.py')
    import datasets,huggingface_hub
    load=datasets.load_dataset;names=datasets.get_dataset_config_names;snapshot=huggingface_hub.snapshot_download
    def local_load(repo,*args,**kwargs):
        kwargs.setdefault('cache_dir','d41')
        return load(str(release) if repo==DATASET_ID else repo,*args,**kwargs)
    datasets.load_dataset=local_load
    datasets.get_dataset_config_names=lambda repo,*args,**kwargs:names(str(release) if repo==DATASET_ID else repo,*args,**kwargs)
    huggingface_hub.snapshot_download=lambda repo,**kwargs:str(release) if repo==DATASET_ID else (_ for _ in ()).throw(ValueError('Unexpected repository'))
    summary={}
    try:
        for name in scripts:
            script=HERE/'review-0.3.0'/name;source=script.read_text(encoding='utf8');code=source
            code=re.sub(r'Path\(__file__\)\.with_name\("([^\"]+)"\)',r'(OUT / "\1")',code)
            code=re.sub(r'(?:PKG|REL\.parent) / "review-0\.3\.0/([^\"]+)"',r'OUT / "\1"',code)
            code=re.sub(r'ROOT / "experiments/2026-10-08-hf-public-release/review-0\.3\.0/([^\"]+)"',r'OUT / "\1"',code)
            code=code.replace('ROOT / "data/raw/2026-10-08-hf-public-release/review-030-tmp/scan"','OUT / "scan"')
            code=code.replace('ROOT / "data/raw/2026-10-08-hf-public-release/review-030-tmp/scores"','OUT / "scores"')
            code=code.replace('"C:/hfc030/ds"','"d41"')
            # Every script's public target; keep the old chart snapshot/source witnesses.
            code=code.replace('PKG / "release/README.md"','TARGET / "README.md"').replace('PKG / "release/data/"','TARGET / "data"')
            code=code.replace('PKG / "release"','TARGET').replace('ROOT / "experiments/2026-10-08-hf-public-release/release"','TARGET')
            code=code.replace('PKG / "release/data/chart_reference.parquet"','TARGET / "data/chart_reference.parquet"')
            code=code.replace('PKG / ("release/data/benchmark_rows_%s.parquet" % v)','TARGET / ("data/benchmark_rows_%s.parquet" % v)')
            # Remaining scripts use literal release paths; final runs target release/.
            if release!=HERE/'release' and '"release/' in code:raise ValueError('Use the final release for '+name)
            argv=[str(script)]
            if name=='hub_load_check.py':argv+=['--cache','d41','--out',str(out/'load-check.json')]
            if name=='readme_snippets_v3.py':argv+=['--work',str(out/'snippets'),'--cache',str(out/'hub-cache')]
            if name=='compare_scores_v3.py':argv+=['--scores',str(out/'scores')]
            if name=='rebuild_compare_v3.py':argv+=['--rebuild',str(rebuild_path)]
            sys.argv=argv;os.chdir(RAW);stream=io.StringIO();error=None
            try:
                with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                    exec(compile(code,str(script),'exec'),dict(__file__=str(script),__name__='__main__',OUT=out,TARGET=release))
            except (Exception,SystemExit) as e:error=repr(e)
            (out/(name+'.log')).write_text(stream.getvalue()+('\nERROR: '+error if error else ''),encoding='utf8')
            summary[name]=dict(source_sha256=sha(script),executed_source_sha256=hashlib.sha256(code.encode()).hexdigest(),completed=error is None,error=error)
            dump(out/'rerun-summary.json',dict(scripts=summary,adaptations=['Original review-0.3.0 scripts are unchanged; output and scratch paths redirected in memory.','Hub loading and card snapshots substitute the local release; no network query.','The private Hub 0.3.0 comparison is reused from the review, not relabelled as a hosted 0.3.1 test.','Reader B union-count differences are separately documented and checked.']))
            print(name,'completed' if error is None else error,flush=True)
    finally:
        datasets.load_dataset=load;datasets.get_dataset_config_names=names;huggingface_hub.snapshot_download=snapshot
    if any(not v['completed'] for v in summary.values()):raise SystemExit(1)

if __name__=='__main__':main()
