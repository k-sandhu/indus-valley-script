"""Locate plan captions in allowed local PDFs without printing surrounding text."""
import sys,re
import fitz
for path in sys.argv[1:]:
    with fitz.open(path) as doc:
        print(path,'PAGES',len(doc))
        for i,page in enumerate(doc,1):
            if 'jansen_urban1987_interim2' in path and 36<=i<=47:continue
            text=page.get_text()
            hits=[s.strip() for s in text.splitlines() if re.search(r'\bplan\b',s,re.I) and len(s.strip())<180]
            if hits:print(i,repr(hits[:5]))
