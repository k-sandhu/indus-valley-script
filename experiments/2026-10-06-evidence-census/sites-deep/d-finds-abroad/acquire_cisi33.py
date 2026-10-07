"""Acquire or verify the institutional CISI 3.3 excerpt without replacing witnesses."""
import hashlib, json, os, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad'
URL = 'https://orbi.uliege.be/bitstream/2268/333796/1/Desset%20F%202022%20in%20CISI%203.3%201763.pdf'

def preserve(path, payload):
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError('Existing witness differs: ' + str(path))
    else:
        path.write_bytes(payload)

def main():
    temp = RAW / 'tmp'
    temp.mkdir(exist_ok=True)
    for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
        os.environ[key] = str(temp)
    import fitz
    pdf = RAW / 'cisi33-excerpt2022.pdf'
    if not pdf.exists():
        with urllib.request.urlopen(URL, timeout=60) as response:
            payload = response.read()
        if not payload.startswith(b'%PDF'):
            raise ValueError('Response is not a PDF')
        preserve(pdf, payload)
    doc = fitz.open(pdf)
    text = '\n'.join('[PDF PAGE %d]\n' % (i + 1) + page.get_text()
                     for i, page in enumerate(doc)).encode('utf-8')
    txt = RAW / 'cisi33-excerpt2022.txt'
    # Windows text-mode acquisition used CRLF. Verify content without replacing it.
    if txt.exists():
        if txt.read_bytes().replace(b'\r\n', b'\n') != text:
            raise RuntimeError('Existing extraction content differs: ' + str(txt))
    else:
        preserve(txt, text)
    record = dict(id='cisi33', url=URL, acquisition_date='2026-10-07',
                  manifest_date='2026-10-07', pages=len(doc), status='acquired',
                  handling='local-only', pdf=pdf.relative_to(ROOT).as_posix(),
                  sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                  text=txt.relative_to(ROOT).as_posix(),
                  text_sha256=hashlib.sha256(txt.read_bytes()).hexdigest(),
                  scope='Contents, preface, essay and bibliography; catalogue plates absent')
    preserve(RAW / 'cisi33-acquisition.json',
             (json.dumps(record, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(record, indent=2))

if __name__ == '__main__':
    main()
