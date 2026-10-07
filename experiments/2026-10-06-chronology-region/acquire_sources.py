"""Acquire public witnesses locally; log HTTP failures and hashes without bypasses."""
from pathlib import Path
import argparse, datetime, hashlib, json, os
import requests
import fitz

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-chronology-region'
URLS = {
    'kenoyer_meadow2010': 'https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf',
    'yadav2013': 'https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf',
    'suga2024': 'https://www.lingua.tsukuba.ac.jp/ippan/JGL/2024/GL26-27_3_paper2.pdf',
    'parpola2018': 'https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf',
    'rao2009': 'https://homes.cs.washington.edu/~rao/PNASIndus.pdf',
    'oakes2019': 'https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download',
    'laursen2010': 'https://onlinelibrary.wiley.com/doi/10.1111/j.1600-0471.2010.00329.x/full',
    'frenez_oxford': 'https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia',
    'fuls2022': 'https://www.researchgate.net/profile/Andreas-Fuls/publication/373522666_Corpus_of_Indus_Inscriptions/links/64f044280f7ab20a86674daa/Corpus-of-Indus-Inscriptions.pdf',
    'beas_chronology': 'https://www.harappa.com/beas/chronology',
}

def main():
    p = argparse.ArgumentParser(); p.add_argument('--run', default='sources-2026-10-06-v1'); a = p.parse_args()
    dest = RAW / a.run; dest.mkdir(parents=True, exist_ok=False)
    tmp = RAW / 'tmp'; tmp.mkdir(exist_ok=True)
    for k in ['TMP', 'TEMP', 'MPLCONFIGDIR']: os.environ[k] = str(tmp)
    result = []
    for key, url in URLS.items():
        rec = {'id':key, 'url':url, 'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rights_status':'rights-unverified'}
        try:
            r = requests.get(url, timeout=40)
            rec.update(status_code=r.status_code, final_url=r.url, content_type=r.headers.get('Content-Type'))
            data = r.content; ext = '.pdf' if data.startswith(b'%PDF') else '.html'
            path = dest / (key+ext); path.write_bytes(data)
            rec.update(local_path=str(path.relative_to(ROOT)).replace('\\','/'), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            if r.ok and ext == '.pdf':
                doc = fitz.open(path); rec['pages'] = len(doc)
                txt = dest / (key+'.txt')
                txt.write_text('\n'.join(f'\n[PDF PAGE {i+1}]\n'+page.get_text() for i,page in enumerate(doc)),encoding='utf-8')
                rec['extraction'] = str(txt.relative_to(ROOT)).replace('\\','/'); rec['outcome']='downloaded-pdf'
            elif r.ok: rec['outcome']='downloaded-html-needs-content-check'
            else: rec['outcome']='failed-http'
        except Exception as e: rec.update(outcome='failed-request', error=str(e))
        result.append(rec); print(key, rec['outcome'], flush=True)
        (dest/'acquisition.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
