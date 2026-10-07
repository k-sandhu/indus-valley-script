"""Replay original modules locally, using their preserved protocol prefix hash."""
import hashlib
import importlib
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
from common import OWN, RAW, digest, fresh

def main():
    stage=sys.argv[1].removesuffix('.py')
    if stage not in {'select_pilot','build','analyze','check_pilot'}:raise ValueError('Unknown original stage')
    original=RAW/'review-response-2026-10-07/original-root/PROTOCOL.md'
    expected=json.loads((OWN/'selection-2026-10-07-v1/selection.json').read_text(encoding='utf-8'))['protocol_sha256']
    prefix=original.read_bytes()
    if hashlib.sha256(prefix).hexdigest()!=expected or not (OWN/'PROTOCOL.md').read_bytes().startswith(prefix):raise ValueError('Original protocol prefix changed')
    module=importlib.import_module(stage)
    module.digest=lambda p:expected if Path(p).resolve()==OWN/'PROTOCOL.md' else digest(p)
    def local_fresh(p,unused_root):return fresh(p,RAW)
    module.fresh=local_fresh
    sys.argv=[str(OWN/(stage+'.py')),*sys.argv[2:]]
    module.main()

if __name__=='__main__':main()
