"""List every package-owned and local raw file, with hashes for review."""
import argparse
from pathlib import Path
import workflow as W


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    output = W.owned(args.out)
    if output.exists():
        raise FileExistsError('Choose a fresh inventory file')
    rows = []
    for base, kind in ((W.HERE, 'owned-code-prose-and-aggregate'), (W.RAW, 'local-only-payload-or-fixture')):
        for file in sorted(base.rglob('*')):
            if file.is_file() and file != output:
                rows.append(dict(path=W.relative(file), bytes=file.stat().st_size, sha256=W.sha(file), disposition=kind))
    rows.append(dict(path=W.relative(output), bytes=None, sha256=None, disposition='own-inventory',
                     note='Self entry has no recursive size/hash'))
    W.write(output, dict(status='Verified computation', created_utc=W.now(), files=rows,
                         files_total=len(rows), owned_files=sum(r['disposition'] != 'local-only-payload-or-fixture' for r in rows),
                         local_raw_files=sum(r['disposition'] == 'local-only-payload-or-fixture' for r in rows),
                         hashed_bytes=sum(r['bytes'] or 0 for r in rows),
                         writes_outside_owned_directories=0, source_readings_performed=0,
                         note='All payloads are local. Synthetic directories contain constructed test readings/costs, not pilot outcomes.'))
    print(f'Inventoried {len(rows)} files')
