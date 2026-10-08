"""Compare a restored tree to the preserved backup manifest; no network or mutations of inputs."""
import argparse
import json
from pathlib import Path
import sys
from build_release import HERE, read, sha, dump

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Choose a new report in Package O.')
    manifest=read(HERE/'private-store/checksums-manifest.json');results=[]
    for row in manifest['files']+manifest['backed_up_files_kept_locally']:
        path=(args.root/row['path']).resolve()
        if not path.is_relative_to(args.root.resolve()):raise ValueError('Manifest path escapes restore root.')
        exists=path.is_file();matches=exists and path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
        results.append(dict(path=row['path'],present=exists,passed=matches))
    result=dict(status='Verified computation' if all(r['passed'] for r in results) else 'Failed',files=len(results),passed=sum(r['passed'] for r in results),results=results)
    dump(out,result);print(json.dumps({k:v for k,v in result.items() if k!='results'}))
    if result['status']=='Failed':sys.exit(1)

if __name__=='__main__':main()
