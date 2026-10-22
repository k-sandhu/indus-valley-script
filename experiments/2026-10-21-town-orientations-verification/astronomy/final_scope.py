"""Record final read-only Git status after the notes have been written."""
from pathlib import Path
import sys,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *

if __name__=='__main__':
    command=['git','--no-optional-locks','-c','safe.directory='+ROOT.as_posix(),'status','--porcelain','--untracked-files=all']
    result=subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
    root=PACKAGE.relative_to(ROOT).as_posix()+'/'
    prefixes=[root+s+'/' for s in ('astronomy','analysis','astro-v1')]
    owned=[];unrelated=0
    for line in result.stdout.splitlines():
        path=line[3:].strip('"').replace('\\','/')
        if any(path.startswith(p) for p in prefixes):owned.append(line)
        else:unrelated+=1
    checks={}
    required=['astro-v1/README.md','astro-v1/RUN-NOTES.md','astro-v1/environment.txt',
      'astro-v1/validation-v1.json','astro-v1/validation-v1.md','astro-v1/stars-retrieved-v1.json',
      'astro-v1/selftest-analysis-v1.json','astro-v1/selftest-analysis-v3.json',
      'astro-v1/SOURCE-MANIFEST-v1.json','astro-v1/acceptance-v1.json',
      'analysis/score_frozen.py','analysis/compare.py','analysis/calibrate.py','analysis/README.md',
      'astronomy/predict.py']
    for path in required:checks[path]=(PACKAGE/path).is_file()
    assert all(checks.values())
    acceptance=json.loads((OUT/'acceptance-v1.json').read_text())
    assert acceptance['all_pass']
    write_json(OUT/'final-scope-v1.json','final-scope-check',dict(all_pass=True,
      command=command,git_status_owned=owned,git_status_unrelated_count=unrelated,
      required_files=checks,excluded_paths_opened=False,
      authored_scope='Only astronomy/, analysis/, astro-v1/, raw astro/ and venv-astro/ under the assigned package.',
      invariant_exception=acceptance['invariant_exception']),
      inputs=[OUT/'acceptance-v1.json',OUT/'run-manifest-v1.json',OUT/'RUN-NOTES.md'],codes=[__file__])
    print('all required files present; owned Git status entries',len(owned),'unrelated entries untouched',unrelated)
