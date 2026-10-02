from pathlib import Path
import urllib.request, hashlib, json, datetime
base = Path(__file__).resolve().parent / 'primary'
url = 'https://researchportal.helsinki.fi/files/176353520/indus_corpus_1979.pdf'
path = base / 'koskenniemi_parpola1979.pdf'
request = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
try:
    with urllib.request.urlopen(request, timeout=45) as r:
        data=r.read()
        status=r.status
    if not data.startswith(b'%PDF'):
        raise RuntimeError(f'Not PDF, bytes={len(data)}, prefix={data[:50]!r}')
    path.write_bytes(data)
    report={'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'license_portal_label':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
            'portal':'https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/',
            'authors':['Kimmo Koskenniemi','Asko Parpola'],'year':1979,
            'title':'Corpus of Texts in the Indus Script'}
    (base/'koskenniemi_parpola1979_provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
except Exception as e:
    print(type(e).__name__,str(e))
