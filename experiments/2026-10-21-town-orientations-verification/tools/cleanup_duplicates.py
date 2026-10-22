"""Remove only owned, byte-identical copies whose held originals remain intact."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,shutil
from common import read_json,write_json,sha256,utc
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args()
    root=Path(a.raw).resolve();infra=Path(a.infra);rows=[]
    for src in read_json(infra/'source-acquisition-v1.json')['sources']:
        if not src.get('copy') or not src.get('file'):continue
        p=Path(src['file']['path']).resolve();parent=Path(src['copy']).resolve()
        assert p.is_relative_to(root)
        if p.exists() and parent.exists() and sha256(p)==sha256(parent):
            rows.append(dict(path=p.as_posix(),bytes=p.stat().st_size,reason='Byte-identical duplicate of held source; original retained',retained_path=parent.as_posix(),sha256=sha256(parent)))
    write_json(infra/'duplicate-cleanup-v1.json',dict(created_utc=utc(),deletions=rows))
    for r in rows:Path(r['path']).unlink();print(r['bytes'],r['path'])
    print('free',shutil.disk_usage(root).free)
if __name__=='__main__':main()
