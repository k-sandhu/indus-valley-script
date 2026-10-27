"""Record changed paths and verify the final report's local links."""
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
REGISTRY = 'knowledge/registry/attempts/OBJECT-PILOT-INTEGRATION-2026-10-26.json'

def write(name,data):
    with (PKG/name).open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write('\n')

def main():
    baseline=set((PKG/'baseline-status.txt').read_text(encoding='utf-8').splitlines())
    now=subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    packages=['experiments/2026-10-26-'+s+'/' for s in ('object-pilot','object-pilot-register','image-recovery','source-conflicts','object-pilot-review')]
    entries=['knowledge/registry/attempts/'+s+'-2026-10-26.json' for s in ('OBJECT-PILOT-INTEGRATION','OBJECT-PILOT-REGISTER','IMAGE-RECOVERY','SOURCE-CONFLICTS','OBJECT-PILOT-REVIEW')]
    added=sorted(set(now)-baseline)
    owned_shared=['data/MANIFEST.json','knowledge/DATA.md']
    outside=[x for x in added if x[3:] not in owned_shared and not any(x[3:].startswith(p) for p in packages+entries)]
    write('worktree-review-v2.json',{'new_status_lines':added,'new_outside_owned_paths':outside,'handling':'Outside paths belong to concurrent work and were not edited by this contribution. Version2 correctly includes the two authorised shared inventory paths in ownership.'})
    links=[]
    for p in PKG.glob('*.md'):
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            target=match[1].split('#',1)[0].strip('<>')
            if not target or '://' in target:
                continue
            f=(p.parent/unquote(target)).resolve()
            links.append({'document':p.relative_to(ROOT).as_posix(),'target':target,'exists':f.exists()})
    files=[p.relative_to(ROOT).as_posix() for p in PKG.rglob('*') if p.is_file()]
    files+=['knowledge/DATA.md','data/MANIFEST.json',REGISTRY]
    files += [(PKG/x).relative_to(ROOT).as_posix() for x in ('changed-paths-v2.json','closure-v2.json')]
    write('changed-paths-v2.json',{'paths':sorted(set(files)), 'contributor_packages':packages[1:], 'detailed_output_root':'D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot', 'committed':False})
    reg=json.loads((ROOT/REGISTRY).read_text(encoding='utf-8'))
    missing=[p for p in reg['evidence'] if not (ROOT/p).exists()]
    result={'all_parent_report_links_resolve':all(x['exists'] for x in links),'links_checked':len(links),'missing_links':[x for x in links if not x['exists']], 'registry_evidence_missing':missing, 'changed_paths_count':len(set(files)), 'new_outside_owned_paths':outside}
    write('closure-v2.json',result)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
