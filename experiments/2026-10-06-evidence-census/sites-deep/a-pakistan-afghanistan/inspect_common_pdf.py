"""Render and OCR shared image-only witnesses, keeping all derivatives local-only."""
from pathlib import Path
import os
import subprocess
import json
import fitz

OWN = Path(__file__).resolve().parent
ROOT = next(p for p in OWN.parents if (p / 'knowledge/INDEX.md').exists())
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision'
for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[key] = str(RAW / 'tmp')

doc = fitz.open(RAW / 'sib-ri-santoni-report.pdf')
rows = []
for index, page in enumerate(doc):
    png = RAW / f'sibri-report-pdf{index+1:02d}.png'
    page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(png)
    result = subprocess.run(['tesseract', str(png), 'stdout', '-l', 'eng'], capture_output=True, check=True)
    rows.append({'pdf_page': index + 1, 'text': result.stdout.decode('utf-8'), 'method': 'Tesseract English OCR; locator aid, visually check claims'})
(RAW / 'sibri-report-ocr.pages.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print('OCR pages:', len(rows))
