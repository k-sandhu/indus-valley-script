"""Inspect acquired formats; output goes to the console, not a corpus release."""
from pathlib import Path
import json
import zipfile
from collections import Counter
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
ACQUISITION = ROOT/'data/raw/2026-10-12-bronze-age-comparison/acquisition'
def path(name):
    return ROOT/json.loads((ACQUISITION/name/'request.json').read_text(encoding='utf-8'))['local_path']

data=json.loads(path('liber-tablet-data-v1').read_bytes())
print('Greek records',len(data['data']),'sites',Counter(row[2] for row in data['data']))
soup=BeautifulSoup(path('liber-tablet-201-v1').read_bytes(),'html.parser')
print('Greek table markup',str(soup.select_one('table.table-text'))[:4500])
for name in ['egyptian-aes-grab-v1','egyptian-aes-archive-v1']:
    data=json.loads(path(name).read_bytes())
    print(name,'dates',Counter(row.get('date') for row in data.values()))
    print('Optional keys',Counter(key for row in data.values() for word in row['token'] for key in word if 'hiero' in key.lower()).most_common())
for name in ['sumerian-ur3-v1','akkadian-atletters-v1']:
    archive=zipfile.ZipFile(path(name))
    catalogue=json.loads(archive.read(next(item for item in archive.namelist() if item.endswith('/catalogue.json'))))
    print(name,'catalog keys',list(catalogue))
    print('Catalogue example',str(next(iter(catalogue.get('members',{}).values())))[:1300])
soup=BeautifulSoup(path('damos-home-v1').read_bytes(),'html.parser')
print('DAMOS scripts',[item.get('src') for item in soup.find_all('script',src=True)])
print('DAMOS iframe',[item.get('src') for item in soup.find_all('iframe')])
