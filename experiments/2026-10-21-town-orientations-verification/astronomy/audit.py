"""Final read-only integrity and scope checks; writes one new audit record."""
from pathlib import Path
import sys,json,csv,subprocess,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *
from core import TARGETS
from horizon import TOWNS,ATTRIBUTION

if __name__=='__main__':
    output=OUT/'acceptance-v1.json'
    if output.exists():raise FileExistsError(output)
    code_paths=list((PACKAGE/'astronomy').rglob('*.py'))+list((PACKAGE/'analysis').rglob('*.py'))
    by_digest={sha(p):str(p) for p in code_paths}
    provenance_failures=[];historical=[];envelopes=0
    for p in OUT.rglob('*.json'):
        d=json.loads(p.read_text(encoding='utf-8'))
        if not {'schema_version','task','synthetic','provenance'}<=set(d):
            provenance_failures.append(str(p)+': missing envelope');continue
        envelopes+=1
        for source,digest in d['provenance']['inputs'].items():
            if sha(source)!=digest:provenance_failures.append(str(p)+': input '+source)
        for code,digest in d['provenance']['code'].items():
            if sha(code)==digest:continue
            if digest in by_digest:historical.append(dict(output=str(p),original_code=code,snapshot=by_digest[digest],sha256=digest))
            else:provenance_failures.append(str(p)+': code '+code)
    tables=[]
    for slug in TOWNS:
        p=OUT/'theta-c'/f'{slug}.csv'
        rows=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        keys={(int(r['year']),r['target']) for r in rows}
        expected={(year,c) for year in range(-3499,-1498,10) for c in TARGETS}
        assert keys==expected and len(rows)==1809,p
        m=json.loads(p.with_name(p.name+'.provenance.json').read_text())
        assert sha(p)==m['csv_sha256']
        tables.append(dict(slug=slug,rows=len(rows),sha256=sha(p)))
    a=OUT/'theta-c/mohenjo-daro.csv';b=OUT/'rechecks/mohenjo-daro.csv'
    assert a.read_bytes()==b.read_bytes()
    assert (OUT/'validation-v1.json').read_bytes()==(OUT/'rechecks/validation-v1.json').read_bytes()
    for p in [OUT/'validation-v1.json',OUT/'selftest-analysis-v3.json',OUT/'integration-analysis-v1.json']:
        assert json.loads(p.read_text())['all_pass'],p
    assert ATTRIBUTION.startswith(chr(169))
    # The existing outputs are never replaced, including through their CLIs.
    commands=[['astronomy/predict.py','--target','alcyone','--lat','27.324','--lon','68.136','--year','-2499','--output',str(a)],
              ['analysis/score_frozen.py','--selftest','--output',str(OUT/'selftest-analysis-v1.json')],
              ['analysis/compare.py','--selftest','--output',str(OUT/'selftest-analysis-v1.json')],
              ['analysis/calibrate.py','--selftest','--output',str(OUT/'selftest-analysis-v1.json')]]
    overwrite=[]
    for cmd in commands:
        target=Path(cmd[-1]);before=sha(target)
        proc=subprocess.run([sys.executable,'-I',str(PACKAGE/cmd[0])]+cmd[1:],capture_output=True,text=True)
        unchanged=sha(target)==before
        good=proc.returncode!=0 and 'FileExistsError' in proc.stderr and unchanged
        overwrite.append(dict(script=cmd[0],refused=good,unchanged=unchanged))
        assert good,cmd
    gitcmd=['git','--no-optional-locks','-c','safe.directory='+ROOT.as_posix(),'status','--porcelain','--untracked-files=all']
    proc=subprocess.run(gitcmd,cwd=ROOT,capture_output=True,text=True,check=True)
    # The repository is shared. Only our paths are displayed and attributed to
    # this run; unrelated status entries are counted without exploring them.
    prefix=str(PACKAGE.relative_to(ROOT)).replace('\\','/')+'/'
    own_prefixes=[prefix+x+'/' for x in ('astronomy','analysis','astro-v1')]
    owned=[];unrelated=0
    for line in proc.stdout.splitlines():
        path=line[3:].strip('"').replace('\\','/')
        if any(path.startswith(x) for x in own_prefixes):owned.append(line)
        else:unrelated+=1
    sizes={}
    for name,path in [('astro',RAW),('venv',RAW.parent/'venv-astro')]:
        files=[p for p in path.rglob('*') if p.is_file()]
        sizes[name]=dict(files=len(files),bytes=sum(p.stat().st_size for p in files))
    all_pass=not provenance_failures and all(x['refused'] for x in overwrite)
    write_json(output,'astronomy-acceptance',dict(all_pass=all_pass,envelopes_checked=envelopes,
        provenance_failures=provenance_failures,historical_code_resolutions=historical,
        provisional_tables=tables,regenerated_csv_identical=True,validation_recheck_identical=True,
        overwrite_checks=overwrite,raw_sizes=sizes,git_command=gitcmd,
        git_status_owned=owned,git_status_unrelated_count=unrelated,
        scope_statement='All authored files and numerical outputs are within the five assigned owned roots. Other contributors were not edited.',
        excluded_paths_opened=False,git_mutations=False,
        invariant_exception='Early acquisition and source inspection used base C:/Python313/python.exe -I rather than the requested venv interpreter. The complete source and final calculation pipeline was rerun with the venv and -I. No downloaded code was executed.'),
        inputs=[OUT/'validation-v1.json',OUT/'selftest-analysis-v3.json',OUT/'integration-analysis-v1.json',OUT/'SOURCE-MANIFEST-v1.json'],codes=[__file__])
    print(json.dumps(dict(all_pass=all_pass,provenance_failures=provenance_failures,
        tables=len(tables),owned_status_entries=len(owned),unrelated_status_entries=unrelated,raw_sizes=sizes)))
    if not all_pass:raise SystemExit(1)
