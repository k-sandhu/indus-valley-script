"""Save source responses or hashes and PDF extracts locally; never write bulk text to Git."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07'

def record(path, **extra):
    data = path.read_bytes()
    row = dict(path=str(path.relative_to(ROOT)).replace('\\', '/'),
               bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
               recorded_utc=datetime.now(timezone.utc).isoformat(), rights='rights-unverified')
    row.update(extra)
    if path.suffix.lower() == '.pdf' and data.startswith(b'%PDF'):
        import fitz
        doc = fitz.open(path)
        pages = [dict(pdf_page=i+1, text=page.get_text()) for i, page in enumerate(doc)]
        extracted = RAW / (path.stem + '.pages.json')
        extracted.write_text(json.dumps(pages, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        row['page_count'] = len(pages)
        row['extraction_path'] = str(extracted.relative_to(ROOT)).replace('\\', '/')
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='append', default=[])
    parser.add_argument('--fetch', nargs=2, action='append', default=[], metavar=('NAME', 'URL'))
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = RAW / 'acquisition-log.json'
    rows = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    for rel in args.local:
        rows.append(record(ROOT / rel, route='reused-local-witness'))
    if args.fetch:
        import requests
        for name, url in args.fetch:
            target = RAW / name
            if target.exists():
                raise FileExistsError(target)
            try:
                response = requests.get(url, timeout=50, headers={'User-Agent':'IndusResearchSourceAudit/1.0'})
                target.write_bytes(response.content)
                rows.append(record(target, url=url, final_url=response.url,
                                   http_status=response.status_code, content_type=response.headers.get('Content-Type'),
                                   route='direct-http'))
            except Exception as exc:
                rows.append(dict(url=url, error=str(exc), recorded_utc=datetime.now(timezone.utc).isoformat(), route='direct-http'))
    manifest.write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{'path':r.get('path'), 'status':r.get('http_status'), 'error':r.get('error')} for r in rows[-(len(args.local)+len(args.fetch)):]], indent=2))

if __name__ == '__main__':
    main()
