"""Assemble one new source/derivative manifest; never replace an existing endpoint."""
from pathlib import Path
import hashlib,json,fitz,subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-02-source-recovery/oxus'
TARGET=OUT/'source-manifest.json'
if TARGET.exists():
    raise FileExistsError('Frozen source manifest exists. Use a new endpoint for a later run.')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records=json.loads((OUT/'source-acquisition-initial.json').read_text(encoding='utf-8'))['sources']
records+=json.loads((OUT/'source-acquisition-landing-pages.json').read_text(encoding='utf-8'))['sources']
records+=[json.loads((OUT/'sarianidi-download.json').read_text(encoding='utf-8')),json.loads((OUT/'sarianidi2005-download.json').read_text(encoding='utf-8'))]
for rec in records:
    path=ROOT/rec['path']
    assert path.is_file() and digest(path)==rec['sha256']
    if path.suffix=='.pdf':
        doc=fitz.open(path);rec['pdf_page_count']=len(doc)
        if path.name=='sarianidi1998.pdf':
            rec.update(title='Margiana and Protozoroastrism',author='Victor Sarianidi',year=1998,publisher='Athens: Kapon Editions',isbn='9607254619',stable_public_url='https://cloud.mail.ru/public/YRbv/maWz94TRz',rights_notice='Copyright Victor Sarianidi/Kapon Editions; all rights reserved, scan PDF page4',download_url_status='ordinary public share download; dispatcher and final redirect URLs may expire')
        elif path.name=='kircho2008.pdf':
            rec.update(title='The technical and technological potential of the Eneolithic population of Altyn-Depe as the basis of the rise of an early urban civilization',authors=['L. B. Kircho','G. F. Korobkova','V. M. Masson'],year=2008,publisher='St Petersburg: European House; Proceedings of IIMK RAS XXVIII',isbn='978-5-8015-0248-9',rights_notice='Copyright authors, IIMK RAS and European House, PDF page5; no verified open license')
        else:
            rec.update(title='Gonur-Depe: City of Kings and Gods',author='Victor Sarianidi',year=2005,publisher='Ashgabat',rights_notice='Official expedition site copyright notice; no verified open license for book')

derivatives=[]
for path in sorted(RAW.iterdir()):
    if path.suffix=='.txt':
        if path.name.startswith('sarianidi-native-'):
            parent=path.with_suffix('.png');method='Tesseract English OCR of native page image; location aid, visually checked for cited claims'
        else:
            parent=path.with_name(path.name.replace('-text.txt','.pdf'));method='PyMuPDF text extraction, PDF page separators retained'
        derivatives.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'bytes':path.stat().st_size,'parent':parent.relative_to(ROOT).as_posix(),'parent_sha256':digest(parent),'transformation':method,'handling':'local-only'})
    elif path.name.startswith('sarianidi-survey-'):
        parent=RAW/'sarianidi1998.pdf'
        derivatives.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'bytes':path.stat().st_size,'parent':parent.relative_to(ROOT).as_posix(),'parent_sha256':digest(parent),'transformation':'50-page thumbnail survey sheet with PDF page labels; navigation aid only','handling':'local-only'})
derivatives+=json.loads((OUT/'derived-image-manifest.json').read_text(encoding='utf-8'))['images']
for rec in derivatives:
    rec['handling']='local-only'

payload={'status':'frozen source recovery endpoint','sources':records,'derivatives':derivatives,'preread_protocol':{'path':(OUT/'PROTOCOL.md').relative_to(ROOT).as_posix(),'sha256':digest(OUT/'PROTOCOL.md')},'observation_path':(OUT/'observations.json').relative_to(ROOT).as_posix(),'rights_policy':'knowledge/provenance/REDISTRIBUTION.md','software':{'pymupdf':fitz.VersionBind,'tesseract':subprocess.check_output(['tesseract','--version'],text=True).splitlines()[0]},'handling':'All acquired sources and derivative images/OCR remain local-only.'}
TARGET.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Saved {len(records)} source records and {len(derivatives)} derivative records.")
