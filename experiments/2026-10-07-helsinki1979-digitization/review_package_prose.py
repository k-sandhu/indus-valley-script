"""Run the required repository prose scan and retain its result and input hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=HERE/'verification/prose-review-v1.json')
    args=parser.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Use a new owned output file')
    command=[sys.executable,str(ROOT/'tools/review_prose.py'),'--path',
             str(HERE.relative_to(ROOT)),'--no-write']
    completed=subprocess.run(command,cwd=ROOT,text=True,encoding='utf-8',capture_output=True)
    if completed.returncode:
        raise RuntimeError(completed.stderr or completed.stdout)
    result=json.loads(completed.stdout)
    result['markdown_sha256']={str(path.relative_to(HERE)):sha(path) for path in sorted(HERE.rglob('*.md'))}
    result['review_tool_sha256']=sha(ROOT/'tools/review_prose.py')
    result['code_sha256']=sha(Path(__file__))
    result['status']='Verified computation' if not result['flags'] else 'Exploratory'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
