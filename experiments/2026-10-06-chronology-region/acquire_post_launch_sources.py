"""Acquire bounded follow-up witnesses into a fresh local-only directory."""
from pathlib import Path
import argparse, datetime, hashlib, json, os
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-chronology-region'
for key in ['TMP', 'TEMP', 'MPLCONFIGDIR']:
    os.environ[key] = str(RAW / 'tmp')
import requests
import fitz

URLS = {
    'vidale2005': 'https://publications.dainst.org/books/dai/catalog/view/2043/2440/4491',
    'vidale2004': 'https://www.harappa.com/sites/default/files/201402/Vidale-Indus-Mesopotamia.pdf',
    'kenoyer2020': 'https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script-2.pdf',
    'parpola2005': 'https://tuhat.helsinki.fi/ws/portalfiles/portal/127257571/Parpola_A_2005._Contact_between_Harappans_Bactrians._SAA_2001.pdf'
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='sources-post-launch-2026-10-07-v1')
    args = parser.parse_args()
    if Path(args.run).name != args.run:
        raise ValueError('Use one fresh directory name.')
    out = RAW / args.run
    out.mkdir(exist_ok=False)
    manifest = {'origin': 'post-launch amendment', 'rights_status': 'rights-unverified; local-only witnesses', 'sources': []}
    for key, url in URLS.items():
        entry = {'id': key, 'url': url, 'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            response = requests.get(url, timeout=55)
            data = response.content
            suffix = '.pdf' if data.startswith(b'%PDF') else '.html'
            path = out / (key + suffix)
            path.write_bytes(data)
            entry.update(http_status=response.status_code, path=path.relative_to(ROOT).as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            if response.ok and suffix == '.pdf':
                with fitz.open(path) as document:
                    text_path = out / (key + '.txt')
                    text_path.write_text('\n'.join(f'[PDF PAGE {i+1}]\n{page.get_text()}' for i, page in enumerate(document)), encoding='utf-8')
                    entry.update(status='downloaded', pages=len(document), extracted_text=text_path.relative_to(ROOT).as_posix())
            else:
                entry['status'] = 'Failed'
        except Exception as error:
            entry.update(status='Failed', error=str(error))
        manifest['sources'].append(entry)
        (out / 'acquisition.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: entry.get(k) for k in ['id', 'status', 'http_status', 'bytes', 'pages']}), flush=True)


if __name__ == '__main__':
    main()
