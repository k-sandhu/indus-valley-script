"""Small source witnesses for the second D2 follow-up; no package installation."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
from pypdf import PdfReader

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'
URLS = {
    'jamison-cambridge': 'https://www.cambridge.org/core/books/abs/seals-and-sealing-in-the-ancient-world/understanding-indus-sealcarving-traditions-a-stylistic-and-metric-approach/2B6D58E6FC5257DD4786194AA71FB40C',
    'green-cambridge': 'https://www.cambridge.org/core/books/abs/seals-and-sealing-in-the-ancient-world/operational-sequences-and-stamp-seals-a-preliminary-report-on-an-experimental-and-microtopographic-framework-for-identifying-groups-of-seal-carvers-in-the-indus-civilization/FD79DDCF0576675460E2061DF0BB2EAC',
    'jamison-contents': 'https://archaeopress.venuetoolbox.com/Archaeopress/Products/9781784919177',
    'ameri2013': 'https://www.harappa.com/sites/default/files/pdf/Ameri-%20Regional%20Variation%20in%20the%20Indus%20with%20front%20matter.pdf',
    'frenez2018-full': 'https://www.harappa.com/sites/default/files/pdf/private-person.pdf',
}


def run():
    folder = RAW / 'sources-second-followup-2026-10-07'
    folder.mkdir(exist_ok=False)
    attempts = []
    for name, url in URLS.items():
        item = {'id': name, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                'rights': 'rights-unverified; raw local-only', 'maximum_bytes': 4 * 1024 * 1024}
        try:
            with requests.get(url, timeout=(15, 45), stream=True) as response:
                item.update(http_status=response.status_code, final_url=response.url)
                suffix = '.pdf' if 'pdf' in response.headers.get('Content-Type', '') else '.html'
                path = folder / (name + suffix)
                with path.open('xb') as handle:
                    total = 0
                    for chunk in response.iter_content(65536):
                        total += len(chunk)
                        if total > item['maximum_bytes']:
                            raise ValueError('Acquisition exceeded the small-witness size cap.')
                        handle.write(chunk)
                item.update(local_path=path.relative_to(ROOT).as_posix(), bytes=total,
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                response.raise_for_status()
                if suffix == '.pdf':
                    reader = PdfReader(path)
                    text = '\n\n'.join(f'PDF PAGE {i+1}\n{p.extract_text() or ""}'
                                       for i, p in enumerate(reader.pages))
                    extracted = folder / (name + '.txt')
                    extracted.write_text(text, encoding='utf-8')
                    item.update(pages=len(reader.pages), extracted_path=extracted.relative_to(ROOT).as_posix())
                item['status'] = 'downloaded; inspect before citation'
        except Exception as error:
            item.update(status='Failed', error=str(error))
            if 'size cap' in str(error) and path.exists():
                item['discarded_partial_bytes'] = path.stat().st_size
                item['discarded_partial_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                path.unlink()
        attempts.append(item)
        print(name, item['status'], item.get('bytes'), flush=True)
        (folder / 'manifest.json').write_text(json.dumps(attempts, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    run()
