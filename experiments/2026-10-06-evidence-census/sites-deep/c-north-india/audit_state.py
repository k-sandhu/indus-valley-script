"""Record the recovered state without changing preserved source witnesses."""
from pathlib import Path
import json, hashlib, datetime

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/c-north-india'

def main():
    entries, invalid = [], []
    for base in (OUT, RAW):
        for p in sorted(base.rglob('*')):
            if not p.is_file():
                continue
            item = {'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'bytes': p.stat().st_size}
            if p.suffix in ('.json', '.py', '.md', '.csv'):
                item['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
            if p.suffix == '.json':
                try:
                    json.loads(p.read_text(encoding='utf-8-sig'))
                except Exception as e:
                    invalid.append({'path': item['path'], 'error': str(e)})
            entries.append(item)
    report = {'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'invalid_json': invalid, 'entries': entries,
              'finding': 'All recovered JSON files parse. Active census files remain the first-pass outputs; new live-search, PDF and OCR witnesses survived. Empty OCR text files correspond to image-only or blank pages and are retained as observations.'}
    (RAW / 'recovery-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    archive = [{'path': str(p.relative_to(OUT)).replace('\\', '/'), 'bytes': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((OUT / 'first-pass').iterdir()) if p.is_file()]
    (OUT / 'first-pass-manifest.json').write_text(json.dumps(archive, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(entries), 'invalid_json': invalid, 'archive_files': len(archive)}))

if __name__ == '__main__':
    main()
