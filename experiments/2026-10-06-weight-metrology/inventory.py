"""Inventory this package's two owned roots and check artifact references."""
import argparse
import hashlib
import json
from pathlib import Path

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    owned=Path(__file__).resolve().parent; root=owned.parent.parent
    raw=root/'data/raw/2026-10-06-weight-metrology'
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/FILES.json')
    args=ap.parse_args(); output=root/args.output
    if output.exists(): raise FileExistsError(output)
    files=[]; dirs=[]; json_n=0
    for base,kind in [(owned,'owned: original code, prose and aggregate output'),(raw,'local-only: third-party/source-derived or temporary witness')]:
        for p in sorted(base.rglob('*')):
            if p.is_dir(): dirs.append(p.relative_to(root).as_posix()); continue
            assert p.resolve().is_relative_to(base.resolve())
            if p.suffix=='.json': json.loads(p.read_text(encoding='utf-8')); json_n+=1
            files.append({'path':p.relative_to(root).as_posix(),'kind':kind,'bytes':p.stat().st_size,'sha256':digest(p)})
    # A self hash cannot be embedded in its own payload.
    files.append({'path':output.relative_to(root).as_posix(),'kind':'owned: inventory itself','bytes':None,'sha256':None})
    result={'scope':'All files in the two package roots were created during this work package; no other paths were edited.',
        'roots':[owned.relative_to(root).as_posix(),raw.relative_to(root).as_posix()],
        'files':files,'directories':dirs,'file_count':len(files),'json_files_parsed_before_self':json_n,
        'source_input_reused_read_only':'data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf',
        'self_hash_note':'The inventory lists itself without a recursive hash.',
        'inventory_code_sha256':digest(Path(__file__))}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'file_count':len(files),'owned_files':sum(f['path'].startswith('experiments/') for f in files),
                      'local_raw_files':sum(f['path'].startswith('data/') for f in files),'json_files_parsed':json_n}))

if __name__=='__main__': main()
