"""Correct book-qualified Greek alignment; preserve the original extractor/output."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from extract_pairs import ROOT,HERE,RAW,sha,rv_pairs,avestan_pairs,pali_pairs


def corrected_greek():
    ns={'t':'http://www.tei-c.org/ns/1.0'}
    gr=ET.parse(RAW/'odyssey-greek-v2.bin').getroot()
    en=ET.parse(RAW/'odyssey-english-corrected-v3.bin').getroot()
    gb=next(x for x in gr.findall('.//t:div',ns) if x.get('n')=='17')
    eb=next(x for x in en.findall('.//t:div',ns) if x.get('n')=='17')
    lines=[dict(line=int(x.get('n')),text=' '.join(' '.join(x.itertext()).split())) for x in gb.findall('.//t:l',ns) if 382<=int(x.get('n','0'))<=386]
    card=next(x for x in eb.findall('.//t:div',ns) if x.get('n')=='380')
    translated=' '.join(' '.join(card.itertext()).split())
    if not all(x in translated for x in ['prophet','healer','builder','minstrel','Antinous']):raise ValueError('Greek occupation translation identity')
    return dict(pair_id='Od17.382-386',source_language='Ancient Greek',source_lines=lines,translation=translated,
        translation_locus='Murray book17, translation card380; includes surrounding dialogue beyond Greek382–386',
        source_parent=dict(path=(RAW/'odyssey-greek-v2.bin').relative_to(ROOT).as_posix(),sha256=sha(RAW/'odyssey-greek-v2.bin')),
        translation_parent=dict(path=(RAW/'odyssey-english-corrected-v3.bin').relative_to(ROOT).as_posix(),sha256=sha(RAW/'odyssey-english-corrected-v3.bin')))


def main():
    target=RAW/'paired-passages-v2.json'
    if target.exists():raise FileExistsError(target)
    old=RAW/'paired-passages-v1.json'
    doc=dict(script_sha256=sha(Path(__file__)),prior_script_sha256=sha(HERE/'extract_pairs.py'),
        prior_output_path=old.relative_to(ROOT).as_posix(),prior_output_sha256=sha(old),
        frozen_selection_sha256=sha(HERE/'selection-v1.json'),
        correction='Greek translation card qualified by book17; original mismatched book15 derivative retained and excluded.',
        scope='Full RV main frame and bounded control pairs; all source-derived text local-only.',
        main_pairs=rv_pairs(),iranian_pairs=avestan_pairs(),greek_pair=corrected_greek(),pali_pairs=pali_pairs())
    prior=json.loads(old.read_text('utf8'))
    if not all(prior[k]==doc[k] for k in ['main_pairs','iranian_pairs','pali_pairs']):raise ValueError('Unrelated pairing changed')
    target.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Corrected Greek book17 alignment; all27 main,19 Iranian and7 Pali groups unchanged')


if __name__=='__main__':main()
