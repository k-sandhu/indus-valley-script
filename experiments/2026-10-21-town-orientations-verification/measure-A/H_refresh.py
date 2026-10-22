import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import H_work as h
original_write=h.write
def save_new_snapshot(path,value):
 path=Path(path)
 if path.name=='infra-snapshot-v1.json' and path.exists():path=path.with_name('infra-snapshot-v2.json')
 original_write(path,value)
h.write=save_new_snapshot
h.images(sys.argv[1])
