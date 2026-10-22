"""Save one source or local copy with a URL, hash and observed rights notice."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,shutil
from acquire import download
from common import record,write_json
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('url');p.add_argument('destination');p.add_argument('record');p.add_argument('--copy');p.add_argument('--rights',choices=['own-work','explicit-license','rights-unverified'],default='rights-unverified');p.add_argument('--notice',default='No explicit licence observed');a=p.parse_args()
    if a.copy:
        dest=Path(a.destination);dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():raise FileExistsError(dest)
        shutil.copyfile(a.copy,dest);r=record(dest,a.url,a.rights,a.notice,acquisition='copy of pre-existing local witness',local_parent=a.copy)
    else:r=download(a.url,a.destination,a.rights,a.notice)
    write_json(a.record,r)
if __name__=='__main__':main()
