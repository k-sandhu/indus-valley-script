"""Acquire literature witnesses locally, preserving failed downloads."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from data import RAW, save, digest

URLS = {
    'yadav2010.html': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0009506',
    'rao2009.pdf': 'https://homes.cs.washington.edu/~rao/PNASIndus.pdf',
    'venkatesh2023.pdf': 'https://emerginginvestigators.org/articles/22-256/pdf',
    'tiwari2026.pdf': 'https://aclanthology.org/2026.nlp4dh-1.28.pdf',
    'linearb2024.pdf': 'https://aclanthology.org/2024.ml4al-1.13.pdf',
    'ithaca2022.html': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8907065/',
    'aeneas2025.pdf': 'https://www.nature.com/articles/s41586-025-09292-5.pdf',
    'aeneas2025-author.pdf': 'https://wrap.warwick.ac.uk/191253/1/s41586-025-09292-5.pdf',
    'chen-goodman1998.pdf': 'https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-10-98.pdf'}

def main():
    output = RAW / 'literature'
    output.mkdir(exist_ok=True)
    records = []
    for name, url in URLS.items():
        path = output / name
        info = {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'path': str(path)}
        try:
            if path.exists():
                raise FileExistsError(path)
            request = urllib.request.Request(url, headers={'User-Agent': 'Research source verification/1.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
                info.update(final_url=response.url, content_type=response.headers.get('Content-Type'), status=response.status)
            path.write_bytes(payload)
            info.update(bytes=len(payload), sha256=digest(path), successful=True)
            if name.endswith('.pdf') and not payload.startswith(b'%PDF'):
                info.update(successful=False, error='Response is not a PDF; retained as a failed witness.')
        except Exception as error:
            info.update(successful=False, error=f'{type(error).__name__}: {error}')
        records.append(info)
        print(json.dumps(info), flush=True)
    save(output / 'downloads.json', records)

if __name__ == '__main__':
    main()
