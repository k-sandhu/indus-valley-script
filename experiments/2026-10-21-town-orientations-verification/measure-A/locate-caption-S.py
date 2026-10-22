"""Find named-town caption pages, excluding restricted source scans entirely."""
import sys,re
import fitz
path=sys.argv[1]
if 'jansen_urban1987' in path:raise RuntimeError('Restricted report needs explicit page selection')
with fitz.open(path) as doc:
    print('PAGES',len(doc), 'METADATA',doc.metadata)
    for i,pg in enumerate(doc,1):
        lines=pg.get_text().splitlines()
        hits=[l.strip() for l in lines if re.search('|'.join(re.escape(v) for v in sys.argv[2:]),l,re.I)]
        if hits:print(i,repr(hits[:8]))
