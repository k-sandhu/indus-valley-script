"""Extract local research witnesses with page numbers; use system Python."""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-modern-restoration/literature'

def main():
    records = []
    for path in sorted(RAW.glob('*.pdf')):
        if not path.read_bytes().startswith(b'%PDF'):
            records.append({'source': path.name, 'success': False, 'error': 'Not a PDF'})
            continue
        reader = PdfReader(path)
        pages = [{'pdf_page': i + 1, 'text': p.extract_text()} for i, p in enumerate(reader.pages)]
        out = path.with_suffix('.pages.json')
        if out.exists():
            raise FileExistsError(out)
        out.write_text(json.dumps(pages, indent=2), encoding='utf-8')
        records.append({'source': path.name, 'success': True, 'pages': len(pages),
            'extracted_path': str(out), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest()})
    (RAW / 'extractions.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()
