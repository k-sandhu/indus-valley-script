"""Acquire public primary-paper page assets listed by RMRL's reader.

No viewer JavaScript is executed. Only the JSON page-list configuration is read.
"""
from pathlib import Path
from urllib.parse import quote, urljoin
import concurrent.futures, datetime, hashlib, json, re, subprocess
import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'sources' / 'rmrl'
PAPERS = {
    'mahadevan_1982_terminal': 'Terminal ideograms in the Indus script_1982a',
    'mahadevan_2010_context': 'The Indus Script Text and Context_2010',
    'mahadevan_1985_claims': 'Clamins of decipherment of the Indus script_1985',
    'mahadevan_1986_grammar': 'Towards a grammar of the Indus texts_1986b',
}
BASE = 'https://s3.us-east-1.amazonaws.com/rmrldl.in/RP/IM/'
TESSERACT = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def asset(job):
    ident, number, url, destination = job
    if not destination.exists():
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        destination.write_bytes(response.content)
    raw = destination.read_bytes()
    target = destination.with_suffix('')
    if not target.with_suffix('.txt').exists():
        subprocess.run([TESSERACT, str(destination), str(target), '--psm', '3'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {'paper': ident, 'page_index': number, 'url': url,
            'path': str(destination.relative_to(ROOT)),
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
            'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    jobs, paper_records = [], []
    for ident, folder in PAPERS.items():
        directory = OUT / ident
        directory.mkdir(exist_ok=True)
        base = BASE + quote(folder, safe='') + '/'
        config_url = base + 'javascript/config.js'
        path = directory / 'config.js'
        response = requests.get(config_url, timeout=90)
        response.raise_for_status()
        path.write_bytes(response.content)
        obj = json.loads(re.sub(r'^\s*var htmlConfig\s*=\s*', '', response.text).rstrip().rstrip(';'))
        pages = obj['fliphtml5_pages']
        paper_records.append({'paper': ident, 'reader_url': base+'index.html',
                              'config_url': config_url, 'pages': len(pages),
                              'config_sha256': hashlib.sha256(response.content).hexdigest()})
        for n, page in enumerate(pages, 1):
            url = urljoin(base, page['l'])
            jobs.append((ident, n, url, directory/f'page_{n:02}.png'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        records = list(executor.map(asset, jobs))
    (OUT/'manifest.json').write_text(json.dumps({'papers':paper_records, 'pages':records}, indent=2), encoding='utf-8')
    for ident in PAPERS:
        pages = sorted((OUT/ident).glob('page_*.txt'))
        text = '\n\n'.join(f'--- READER PAGE {n+1} ---\n'+p.read_text(encoding='utf-8') for n,p in enumerate(pages))
        (ROOT/'sources'/f'{ident}.txt').write_text(text, encoding='utf-8')
        print(ident, len(pages), len(text))
