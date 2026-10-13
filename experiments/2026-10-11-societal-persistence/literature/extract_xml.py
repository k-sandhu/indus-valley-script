"""Extract local primary-archive XML with section and paragraph locators."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'data/raw/2026-10-11-societal-persistence/literature'

if __name__=='__main__':
    for ident,tag in [('L09-smith2021','capture-v2'),('L10-lawrence2025','capture-v2'),('L11-pichancourt2025','capture-v3')]:
        source=RAW/f'{ident}-{tag}.bin'
        target=RAW/f'{ident}-xml-extraction-v1.json'
        if target.exists(): raise FileExistsError(str(target))
        tree=ET.fromstring(source.read_bytes())
        parent={child:node for node in tree.iter() for child in node}
        paras=[]
        for index,p in enumerate(tree.findall('.//body//p'),start=1):
            node=p
            sections=[]
            while node in parent:
                node=parent[node]
                if node.tag=='sec':
                    title=node.find('title')
                    sections.append(dict(id=node.get('id'),title=' '.join(title.itertext()) if title is not None else None))
            paras.append(dict(body_paragraph_1based=index,id=p.get('id'),sections=list(reversed(sections)),text=' '.join(p.itertext())))
        meta=tree.find('.//article-meta')
        authors=[]
        for contributor in meta.findall('.//contrib'):
            name=contributor.find('name')
            if contributor.get('contrib-type')=='author' and name is not None:
                authors.append(' '.join((name.findtext('given-names',''),name.findtext('surname',''))).strip())
        license_node=meta.find('.//license')
        result=dict(parent_path=source.relative_to(ROOT).as_posix(),parent_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),title=' '.join(meta.find('title-group/article-title').itertext()),authors=authors,license_notice=' '.join(license_node.itertext()) if license_node is not None else None,article_ids={x.get('pub-id-type'):x.text for x in meta.findall('article-id')},paragraphs=paras)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(ident,len(paras),'paragraphs')
