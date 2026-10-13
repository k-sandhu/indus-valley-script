"""Preserve public full-text witnesses locally with transport and hash records."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-11-settlement-prospection'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('source_id')
    p.add_argument('url')
    p.add_argument('--format', choices=['xml', 'pdf', 'html', 'json'], required=True)
    p.add_argument('--expect', help='Required text in an HTML witness, checked before saving.')
    a = p.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / (a.source_id + '.' + a.format)
    if path.exists():
        raise SystemExit('Witness exists; use a new versioned source_id to preserve it.')
    req = urllib.request.Request(a.url, headers={'User-Agent': 'IndusResearch/1.0 (source preservation)'})
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read()
        final_url = r.url
        ctype = r.headers.get('Content-Type', '')
    if a.format == 'pdf' and not body.startswith(b'%PDF'):
        raise ValueError('Expected PDF, received ' + ctype)
    if a.format == 'xml':
        ET.fromstring(body)
    if a.format == 'html':
        decoded = body.decode('utf-8', errors='replace')
        if 'recaptcha/challengepage' in decoded or '<title>Access Denied</title>' in decoded:
            raise ValueError('Challenge page is not an article witness.')
        if a.expect and a.expect.casefold() not in decoded.casefold():
            raise ValueError('Expected article text was absent.')
    path.write_bytes(body)
    record = {'source_id': a.source_id, 'requested_url': a.url, 'resolved_url': final_url,
              'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'bytes': len(body),
              'sha256': hashlib.sha256(body).hexdigest(), 'content_type': ctype,
              'local_path': path.relative_to(ROOT).as_posix(),
              'rights': 'rights-unverified; local witness only'}
    (RAW / (a.source_id + '.acquisition.json')).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    if a.format == 'xml':
        root = ET.fromstring(body)
        text = '\n'.join(' '.join(el.itertext()) for el in root.iter() if el.tag in ['title','p','caption','article-title'])
        (RAW / (a.source_id + '.txt')).write_text(text, encoding='utf-8')
    elif a.format == 'pdf':
        import fitz
        doc = fitz.open(path)
        pages = [{'pdf_page': i + 1, 'text': page.get_text()} for i, page in enumerate(doc)]
        (RAW / (a.source_id + '.pages.json')).write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record))

if __name__ == '__main__':
    main()
