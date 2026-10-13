"""Respect JATS author type inherited from contrib-group; preserve v1 extraction."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'data/raw/2026-10-11-societal-persistence/literature'

if __name__=='__main__':
    for ident,tag in [('L09-smith2021','capture-v2'),('L10-lawrence2025','capture-v2'),('L11-pichancourt2025','capture-v3')]:
        source=RAW/f'{ident}-{tag}.bin'
        old=RAW/f'{ident}-xml-extraction-v1.json'
        target=RAW/f'{ident}-xml-extraction-v2.json'
        if target.exists():raise FileExistsError(str(target))
        tree=ET.fromstring(source.read_bytes())
        authors=[]
        for group in tree.findall('.//article-meta/contrib-group'):
            for contributor in group.findall('contrib'):
                name=contributor.find('name')
                kind=contributor.get('contrib-type',group.get('content-type'))
                if kind=='author' and name is not None:
                    authors.append(' '.join((name.findtext('given-names',''),name.findtext('surname',''))).strip())
        assert authors, ident
        result=json.loads(old.read_text(encoding='utf-8'))
        result.update(authors=authors,metadata_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),prior_extraction_path=old.relative_to(ROOT).as_posix(),prior_extraction_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),amendment='v1 required contrib-type=author on each contributor; these witnesses inherit it from contrib-group content-type=author. Paragraph extraction is unchanged.')
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(ident,authors)
