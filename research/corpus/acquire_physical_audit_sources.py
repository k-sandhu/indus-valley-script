"""Acquire public primary publications needed for the narrow object audit."""
from pathlib import Path
import datetime, hashlib, json, urllib.request
import fitz
OUT = Path(__file__).resolve().parent / 'primary'
specs = [
    ('parpola2020_bone_rods', 'https://helda.helsinki.fi/server/api/core/bitstreams/5994c972-f2c5-4520-954d-8a9b63d27b25/content'),
    ('parpola2011_unicorn', 'https://www.harappa.com/sites/default/files/pdf/Parpola_A_2011_unicorn%20%281%29.pdf'),
    ('kenoyer_meadow2010_inscribed_objects', 'https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf'),
]
for name, url in specs:
    path = OUT / (name + '.pdf')
    if not path.exists():
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=35) as r:
                b = r.read()
            assert b.startswith(b'%PDF'), f'Not a PDF: {name}'
            path.write_bytes(b)
        except Exception as exc:
            failure = {'url': url, 'attempted_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       'exception': type(exc).__name__, 'error': str(exc),
                       'status': 'No PDF acquired by this request; no authentication or warning bypass attempted.'}
            (OUT / (name + '_request_failure.json')).write_text(json.dumps(failure, indent=2)+'\n', encoding='utf-8')
            print(name, 'not acquired:', type(exc).__name__)
            continue
    b = path.read_bytes()
    d = fitz.open(path)
    txt = '\n\n'.join(p.get_text() for p in d)
    (OUT / (name + '.txt')).write_text(txt, encoding='utf-8')
    row = {'url':url, 'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'filename':str(path.name), 'sha256':hashlib.sha256(b).hexdigest(), 'bytes':len(b), 'pages':len(d), 'license':'No explicit reuse license verified. Retain locally for research; no bulk public redistribution.', 'method':'Public URL request, no authentication. PDF unchanged; native text extraction is an inspection aid.'}
    # Preserve original acquisition time and any verified browser-download route.
    provenance = OUT / (name + '_provenance.json')
    if not provenance.exists():
        provenance.write_text(json.dumps(row, indent=2)+'\n', encoding='utf-8')
    print(name, len(d), row['sha256'])
    for i, p in enumerate(d):
        if any(s in p.get_text() for s in ['H-697','H-2139','H-2200','H-2238','H-1897','H-1100','AD-3','Ad-3']):
            p.get_pixmap(matrix=fitz.Matrix(3,3)).save(OUT / (name + f'_p{i+1}.png'))
            print('Candidate page', i+1)
