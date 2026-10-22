"""Copy allowlisted held plans and acquire explicitly listed source URLs only."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,shutil,concurrent.futures
from common import write_json,read_json,record
from acquire import download
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');p.add_argument('raw');p.add_argument('output');a=p.parse_args()
    def run(row):
        dest=Path(a.raw)/row['destination']
        try:
            if row.get('copy'):
                if '2026-10-21-town-axes' in row['copy']:raise ValueError('excluded source')
                dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():raise FileExistsError(dest)
                shutil.copyfile(row['copy'],dest);rec=record(dest,row['url'],'rights-unverified','Held scan; no explicit reuse licence verified',local_parent=row['copy'])
            else:rec=download(row['url'],dest,row.get('rights_status','rights-unverified'),row.get('rights_notice','No explicit reuse licence observed'))
            return dict(**row,file=rec)
        except Exception as e:return dict(**row,failure=str(e))
    with concurrent.futures.ThreadPoolExecutor(5) as pool:r=list(pool.map(run,read_json(a.config)))
    write_json(a.output,dict(sources=r))
    for row in r:print(row['destination'],row.get('failure',row.get('file',{}).get('bytes')),flush=True)
if __name__=='__main__':main()
