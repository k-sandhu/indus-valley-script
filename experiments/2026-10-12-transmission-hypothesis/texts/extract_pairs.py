"""Extract the fixed RV frame and paired controls into ignored local records."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/texts'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def soup(name):return BeautifulSoup((RAW/name).read_bytes(),'lxml')


def rv_pairs():
    result=[]
    for book,hymn,count,engname in [(9,112,4,'rv9112-griffith-v1.html'),(10,71,11,'rv10071-griffith-v1.html'),(10,101,12,'rv10101-griffith-v1.html')]:
        sanname=f'rv{book}-sanskrit-v1.html'
        lines=soup(sanname).get_text('\n').splitlines();stanzas={}
        for line in lines:
            match=re.match(rf'^RV_{book},{hymn:03d}\.(\d+)([a-z])\s+(.*)$',line.strip())
            if match:
                num=int(match.group(1));stanzas.setdefault(num,[]).append(dict(pada_label=match.group(2),source_line=line.strip(),text=match.group(3)))
        body=soup(engname).find('h1').find_next_sibling('div').get_text('\n',strip=True)
        translated={}
        for match in re.finditer(r'(?m)^(\d+)\.?\s+(.*?)(?=^\d+\.?\s|\Z)',body,re.S):translated[int(match.group(1))]=match.group(2).strip()
        if set(stanzas)!=set(range(1,count+1)) or set(translated)!=set(stanzas):raise ValueError((book,hymn,stanzas.keys(),translated.keys()))
        for num in range(1,count+1):
            result.append(dict(pair_id=f'RV{book}.{hymn}.{num}',source_language='Vedic Sanskrit',translation_language='English',
                source_locus=f'RV_{book},{hymn:03d}.{num:02d}',sanskrit_padas=stanzas[num],translation_locus=f'Griffith hymn{book}.{hymn}, stanza{num}',translation=translated[num],
                source_parent=dict(path=(RAW/sanname).relative_to(ROOT).as_posix(),sha256=sha(RAW/sanname)),
                translation_parent=dict(path=(RAW/engname).relative_to(ROOT).as_posix(),sha256=sha(RAW/engname))))
    return result


def avestan_sections(name,chapter,start,end):
    s=soup(name)
    h=next(x for x in s.find_all(['h2','h3']) if re.fullmatch(rf'(?:YASNA\s*-\s*)?(?:Chapter|Fargard)\s+{chapter}\.?',x.get_text(' ',strip=True),re.I))
    texts=[]
    for sibling in h.next_siblings:
        if getattr(sibling,'name',None) in ['h2','h3']:break
        if hasattr(sibling,'get_text'):texts.append(sibling.get_text('\n',strip=True))
    body='\n'.join(texts);out={}
    for match in re.finditer(r'(?m)^(\d+)\s+(.*?)(?=^\d+\s|\Z)',body,re.S):
        n=int(match.group(1))
        if start<=n<=end:out[n]=match.group(2).strip()
    if set(out)!=set(range(start,end+1)):raise ValueError((name,chapter,out.keys()))
    return out


def avestan_pairs():
    out=[]
    san=avestan_sections('yasna9-avestan-corrected-v2.html',9,1,8)
    s=soup('yasna-mills-v2.html');h=s.find('h2',id='y9');eng={}
    for tr in h.parent.parent.find_next_siblings('tr'):
        if tr.find('h2'):break
        td=tr.find('td');text=td.get_text(' ',strip=True) if td else ''
        m=re.match(r'^(\d+)\.\s+(.*)',text,re.S)
        if m and int(m.group(1))<=8:eng[int(m.group(1))]=m.group(2)
    if set(eng)!=set(san):raise ValueError(('Y9 translation',eng.keys()))
    for n in sorted(san):out.append(dict(pair_id=f'Y9.{n}',source_language='Younger Avestan',source_text=san[n],translation=eng[n],translation_locus=f'Mills Yasna9.{n}',
        source_parent=dict(path=(RAW/'yasna9-avestan-corrected-v2.html').relative_to(ROOT).as_posix(),sha256=sha(RAW/'yasna9-avestan-corrected-v2.html')),
        translation_parent=dict(path=(RAW/'yasna-mills-v2.html').relative_to(ROOT).as_posix(),sha256=sha(RAW/'yasna-mills-v2.html'))))
    san=avestan_sections('vendidad-avestan-corrected-v2.html',3,23,33)
    s=soup('vendidad3-darmesteter-v2.html');eng={}
    for td in s.find_all('td'):
        if 'NOTE' in td.get('class',[]):continue
        text=td.get_text(' ',strip=True);m=re.match(r'^(\d+(?:,\d+)?)\.\s+(.*)',text,re.S)
        if m:
            nums=[int(x) for x in m.group(1).split(',')]
            for n in nums:
                if 23<=n<=33:eng[n]=dict(text=m.group(2),translation_group=m.group(1))
    if set(eng)!=set(san):raise ValueError(('V3 translation',eng.keys()))
    for n in sorted(san):out.append(dict(pair_id=f'V3.{n}',source_language='Younger Avestan',source_text=san[n],translation=eng[n]['text'],translation_group=eng[n]['translation_group'],translation_locus=f'Darmesteter Vendidad3.{eng[n]["translation_group"]}',
        source_parent=dict(path=(RAW/'vendidad-avestan-corrected-v2.html').relative_to(ROOT).as_posix(),sha256=sha(RAW/'vendidad-avestan-corrected-v2.html')),
        translation_parent=dict(path=(RAW/'vendidad3-darmesteter-v2.html').relative_to(ROOT).as_posix(),sha256=sha(RAW/'vendidad3-darmesteter-v2.html'))))
    return out


def greek_pair():
    ns={'t':'http://www.tei-c.org/ns/1.0'}
    gr=ET.parse(RAW/'odyssey-greek-v2.bin').getroot();en=ET.parse(RAW/'odyssey-english-corrected-v3.bin').getroot()
    book=next(x for x in gr.findall('.//t:div',ns) if x.get('n')=='17')
    lines=[dict(line=int(x.get('n')),text=' '.join(' '.join(x.itertext()).split())) for x in book.findall('.//t:l',ns) if 382<=int(x.get('n','0'))<=386]
    text=next(x for x in en.findall('.//t:div',ns) if x.get('n')=='380' and x.get('type')=='textpart')
    return dict(pair_id='Od17.382-386',source_language='Ancient Greek',source_lines=lines,translation=' '.join(' '.join(text.itertext()).split()),
        translation_locus='Murray book17, translation card beginning380; includes surrounding dialogue beyond selected Greek lines',
        source_parent=dict(path=(RAW/'odyssey-greek-v2.bin').relative_to(ROOT).as_posix(),sha256=sha(RAW/'odyssey-greek-v2.bin')),
        translation_parent=dict(path=(RAW/'odyssey-english-corrected-v3.bin').relative_to(ROOT).as_posix(),sha256=sha(RAW/'odyssey-english-corrected-v3.bin')))


def pali_pairs():
    san=json.loads((RAW/'dn1-pali-v2.bin').read_text('utf8'));eng=json.loads((RAW/'dn1-sujato-v2.bin').read_text('utf8'))
    result=[]
    for n in range(21,28):
        keys=[k for k in san if k.startswith(f'dn1:1.{n}.')]
        if not keys or not set(keys)<=eng.keys():raise ValueError((n,keys))
        result.append(dict(pair_id=f'DN1.1.{n}',source_language='Pali',segments=[dict(segment_id=k,source_text=san[k],translation=eng[k]) for k in keys],
            source_parent=dict(path=(RAW/'dn1-pali-v2.bin').relative_to(ROOT).as_posix(),sha256=sha(RAW/'dn1-pali-v2.bin')),
            translation_parent=dict(path=(RAW/'dn1-sujato-v2.bin').relative_to(ROOT).as_posix(),sha256=sha(RAW/'dn1-sujato-v2.bin'))))
    return result


def main():
    target=RAW/'paired-passages-v1.json'
    if target.exists():raise FileExistsError(target)
    rv=rv_pairs();av=avestan_pairs();greek=greek_pair();pali=pali_pairs()
    doc=dict(script_sha256=sha(Path(__file__)),frozen_selection_sha256=sha(HERE/'selection-v1.json'),
        scope='Full RV main frame; bounded controls. Complete source-language/translation pairs remain local-only. Unequal translation groups preserve their source grouping.',
        main_pairs=rv,iranian_pairs=av,greek_pair=greek,pali_pairs=pali)
    target.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(main=len(rv),iranian=len(av),greek=len(greek['source_lines']),pali_sections=len(pali),pali_segments=sum(len(x['segments']) for x in pali))))


if __name__=='__main__':main()
