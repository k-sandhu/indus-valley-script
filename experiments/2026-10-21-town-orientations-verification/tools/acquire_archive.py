"""Download a named Internet Archive report and preserve its item metadata."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,requests
from urllib.parse import quote
from common import record,write_json
from acquire import download
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('item');p.add_argument('destination');p.add_argument('output');a=p.parse_args();d=Path(a.destination);d.mkdir(parents=True,exist_ok=False);url='https://archive.org/metadata/'+a.item;r=requests.get(url,timeout=60);r.raise_for_status();(d/'metadata.json').write_bytes(r.content);files=[record(d/'metadata.json',url,'rights-unverified','Internet Archive uploader metadata')];data=r.json();pdfs=[f for f in data.get('files',[]) if f['name'].lower().endswith('.pdf')];pdfs.sort(key=lambda f:int(f.get('size',10**12)))
    if not pdfs:raise ValueError('No anonymous PDF listed')
    u='https://archive.org/download/'+a.item+'/'+quote(pdfs[0]['name']);files.append(download(u,d/'source.pdf','rights-unverified','Report scan on Internet Archive; rights of report unverified'));write_json(a.output,dict(item=a.item,files=files))
if __name__=='__main__':main()
