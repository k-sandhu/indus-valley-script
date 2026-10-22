"""Log every byte removed, then delete only named, regenerable owned scratch."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,shutil
from common import write_json,utc
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('output');a=ap.parse_args();root=Path(a.raw).resolve();rows=[];directories=[]
    for name in ['temp-plan-review','synthetic-resume-development-1','synthetic-resume-development-2','synthetic-final-v1']:
        d=(root/name).resolve();assert d.is_relative_to(root) and d!=root
        if not d.exists():continue
        directories.append(d)
        for p in sorted(d.rglob('*')):
            if p.is_file():rows.append(dict(path=p.as_posix(),bytes=p.stat().st_size,reason='Regenerable temporary plan review or synthetic validation scratch; final locators and aggregate checks retained'))
    for p in (root/'imagery').rglob('stac-search-*.json'):
        if p.stat().st_size==0:rows.append(dict(path=p.resolve().as_posix(),bytes=0,reason='Zero-byte STAC response truncated in the first storage interruption'))
    write_json(a.output,dict(created_utc=utc(),deletions=rows,logical_bytes=sum(r['bytes'] for r in rows)))
    for row in rows:
        p=Path(row['path']);assert p.resolve().is_relative_to(root);p.unlink()
    for d in directories:
        for sub in sorted([p for p in d.rglob('*') if p.is_dir()],key=lambda p:len(p.parts),reverse=True):sub.rmdir()
        d.rmdir()
    print('deleted',len(rows),'bytes',sum(r['bytes'] for r in rows),'free',shutil.disk_usage(root).free)
if __name__=='__main__':main()
