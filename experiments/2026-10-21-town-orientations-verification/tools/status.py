"""Read-only progress, storage and PDF identity diagnostics; paths are arguments."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,shutil,json
from common import read_json
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw');p.add_argument('--infra');p.add_argument('--pdf',nargs='*');a=p.parse_args()
    if a.raw:
        root=Path(a.raw);print('free_MiB',round(shutil.disk_usage(root).free/1048576,1));print('raw_logical_MiB',round(sum(p.stat().st_size for p in root.rglob('*') if p.is_file())/1048576,1))
        complete=[]
        for pth in sorted((root/'imagery').glob('*/acquisition-v*/acquisition-result.json')):
            try:
                r=read_json(pth)
                if r.get('composite'):complete.append((r['slug'],len(r['scenes'])))
            except ValueError:pass
        print('complete_town_composites',complete)
    if a.infra:
        root=Path(a.infra)
        for name in ['selftest-development-3.json','selftest-v1.json','runway-validation-development-1.json','validation-v1/summary.json']:
            pth=root/name
            if pth.exists():
                try:
                    r=read_json(pth);print(name,r.get('overall_pass',r.get('aggregate',r.get('ready_for_measurement'))));print('failed_checks',[c for c in r.get('checks',[]) if not c['pass']])
                except ValueError:print(name,'incomplete JSON')
    if a.pdf:
        import pymupdf
        from plan_support import guard
        for path in a.pdf:
            guard(path)
            with pymupdf.open(path) as d:print(path,dict(pages=len(d),metadata=d.metadata,page_one_rect=list(d[0].rect)))
if __name__=='__main__':main()
