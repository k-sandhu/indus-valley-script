"""Fetch identity links only from DBpedia; final coordinates require Wikidata or another source."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import re,concurrent.futures,argparse
import requests
from acquire import download
from common import write_json
NAMES=['Mohenjo-daro','Harappa','Kalibangan','Lothal','Dholavira','Surkotada','Banawali','Rakhigarhi','Chanhudaro','Kanmer','Shikarpur,_Gujarat','Juni_Kuran','Gola_Dhoro','Desalpur_Gunthli','Khirsara','Kuntasi','Rojdi','Kot_Diji','Nausharo','Sutkagan_Dor','Balakot_(archaeological_site)','Allahdino','Lakhan_Jo_Daro','Ganweriwala','Farmana','Bhirrana','Kunal,_Haryana','Mitathal','Karanpura','Rangpur,_India','Kotada_Bhadli','Pabumath','Navinal']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw');p.add_argument('output');a=p.parse_args()
    def run(n):
        url='https://dbpedia.org/data/'+n+'.json';dest=Path(a.raw)/'coordinate-identity'/f'{n}.json'
        try:
            rec=download(url,dest,'rights-unverified','DBpedia identity link lookup; licence not checked; coordinates not used')
            t=dest.read_text(encoding='utf-8');q=sorted(set(re.findall(r'www.wikidata.org/entity/(Q[0-9]+)',t)))
            return dict(name=n,qids=q,file=rec)
        except Exception as e:return dict(name=n,error=str(e))
    with concurrent.futures.ThreadPoolExecutor(6) as pool:r=list(pool.map(run,NAMES))
    write_json(a.output,r)
    for row in r:print(row['name'],row.get('qids',row.get('error')))
if __name__=='__main__':main()
