"""Download public witnesses into the assigned local-only directory."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, time
import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'
URLS = {
    'kenoyer1997': 'https://www.columbia.edu/itc/anthropology/v3922/pdfs/kenoyer.pdf',
    'kenoyer2005': "https://www.treccani.it/enciclopedia/l-archeologia-del-subcontinente-indiano-dal-neolitico-all-eta-del-bronzo-la-civilta-della-valle-dell-indo_(Il-Mondo-dell'Archeologia)/",
    'kenoyer2009': 'https://www.harappa.com/sites/default/files/pdf/Kenoyer2009%20Indus%20Seals_0.pdf',
    'rao2018': 'https://arxiv.org/pdf/1812.00049',
    'rao2009': 'https://homes.cs.washington.edu/~rao/PNASIndus.pdf',
    'ameri2022': 'https://www.tandfonline.com/doi/abs/10.1080/02666030.2022.2051825?role=tab&scroll=top&tab=permissions',
    'lothal2014': 'https://whc.unesco.org/en/tentativelists/5918/',
    'bookcontents2018': 'https://www.archaeopress.com/ArchaeopressShop/DMS/DE4B542271BF4AE8884FCF8A28E31F16/9781784919177-WalkingwiththeUnicorn-Frenez-Contents.pdf',
    'smith2025': 'https://www.heritageuniversityofkerala.com/JournalPDF/Volume10/1.pdf',
    'kenoyer1989': 'https://www.harappa.com/sites/default/files/pdf/Kenoyer1989_Harappan%20Craft%20Specialization%20and%20the%20Question%20o.pdf',
    'yadav2013': 'https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf',
    'oakes': 'https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download',
    'dholavira2020': 'https://whc.unesco.org/uploads/nominations/1645.pdf',
    'kalibangan2020': 'https://api.repository.cam.ac.uk/server/api/core/bitstreams/515b5736-fa26-4c70-9ffb-7d5e9292221b/content',
    'mahesh2026v1': 'https://arxiv.org/html/2604.23582v1',
    'mahesh2026current': 'https://arxiv.org/abs/2604.23582',
    'mukhopadhyay2019': 'https://www.nature.com/articles/s41599-019-0274-1',
    'mukhopadhyay2023': 'https://www.nature.com/articles/s41599-023-02320-7',
    'green2021': 'https://link.springer.com/article/10.1007/s10814-020-09147-9',
    'frenez2018': 'https://www.researchgate.net/publication/347150488_Private_Person_or_Public_Persona_Use_and_Significance_of_Standard_Indus_Seals_as_Markers_of_Formal_Socio-Economic_Identities',
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', default='source-downloads-2026-10-06-01')
    ap.add_argument('--only', nargs='*')
    args = ap.parse_args()
    dest = RAW / args.batch
    dest.mkdir(parents=True, exist_ok=False)
    manifest = []
    for key, url in URLS.items():
        if args.only and key not in args.only:
            continue
        item = {'id': key, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                'rights': 'rights-unverified', 'route': 'requests GET; no authentication'}
        try:
            r = requests.get(url, timeout=45)
            item.update(http_status=r.status_code, final_url=r.url, content_type=r.headers.get('Content-Type'))
            ext = '.pdf' if r.content.startswith(b'%PDF') else '.html'
            p = dest / (key + ext)
            p.write_bytes(r.content)
            item.update(local_path=str(p.relative_to(ROOT)), bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest())
            r.raise_for_status()
            if ext == '.pdf':
                reader = PdfReader(p)
                item['pages'] = len(reader.pages)
                text = '\n'.join(f'\n--- PDF page {i+1} ---\n' + (page.extract_text() or '') for i, page in enumerate(reader.pages))
                (dest / (key + '.txt')).write_text(text, encoding='utf-8')
            item['status'] = 'downloaded; inspect content before citation'
        except Exception as exc:
            item.update(status='Failed', error=str(exc))
        manifest.append(item)
        print(key, item['status'], item.get('bytes'), flush=True)
        (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
