"""Build abbreviation review table: python -I code/tips.py. Run again after parsing."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import re
from common import LOCAL,RUN,ENTRY,read,write,sha

BASE={'Ta.':'Tamil','Ma.':'Malayalam','Ko.':'Kota','To.':'Toda','Ka.':'Kannada','Koḍ.':'Kodava',
      'Tu.':'Tulu','Te.':'Telugu','Kol.':'Kolami','Pa.':'Parji','Go.':'Gondi','Kuwi':'Kuwi',
      'Kur.':'Kurukh','Malt.':'Malto','Br.':'Brahui','Kurub.':'Betta Kurumba'}
NOT={'Ir.':'Irula','PāKu.':'Palu Kurumba','PālKu.':'Palu Kurumba','ĀlKu.':'Alu Kurumba','AlKu.':'Alu Kurumba',
     'Bel.':'Belari','Kor.':'Koraga','Nk.':'Naikri or Naiki of Chanda','Konḍa':'Konda',
     'Pe.':'Pengo','Manḍ.':'Manda','Kui':'Kui'}
PAGES={'Ta.':'xxi–xxii','Ma.':'xxii','Ir.':'xxii–xxiii','PāKu.':'xxiii','ĀlKu.':'xxiii–xxiv',
       'Kurub.':'xxiv','Ko.':'xxiv','To.':'xxiv','Ka.':'xxiv–xxv','Koḍ.':'xxv–xxvi',
       'Tu.':'xxvi','Te.':'xxvi–xxvii','Kol.':'xxvii','Nk.':'xxvii–xxviii','Pa.':'xxviii',
       'Ga.':'xxviii','Go.':'xxviii–xxix','Konḍa':'xxix','Pe.':'xxix','Manḍ.':'xxix',
       'Kui':'xxix','Kuwi':'xxix–xxx','Kur.':'xxx','Malt.':'xxx–xxxi','Br.':'xxxi'}

def map_form(language,dialect=''):
    notes=[]
    if language=='Ga.':
        oll='Oll.' in dialect
        other=bool(re.search(r'(?:S\.|S[23]|P\.)',dialect))
        if not oll and not other: notes.append('Gadba without a variety label; left unmapped')
        return (['Ollari Gadba'] if oll else []),notes
    if language=='Go.':
        explicit='Koya' in dialect
        ko=bool(re.search(r'(?<!\w)Ko\.',dialect))
        if ko: notes.append('Go. (Ko.) assigned to Koya; front matter delegates this siglum to Voc.; verify there')
        if explicit or ko:
            remaining=re.sub(r'Koya\s*(?:Su\.|T\.)?|(?<!\w)Ko\.','',dialect).strip(' .')
            return (['Koya','Gondi'] if remaining else ['Koya']),notes
        return ['Gondi'],notes
    if language=='Ka.' and re.search(r'Badaga|Hock\.',dialect): return ['Badaga'],notes
    if language in BASE: return [BASE[language]],notes
    if language not in NOT: notes.append('Unknown language label; left unmapped')
    return [],notes

def describe(language,dialect):
    if language=='Ga.':
        return 'Ollari Gadba source' if 'Oll.' in dialect else 'Salur or Kondekor Gadba source' if dialect else 'Gadba without a variety label'
    if language=='Go.' and ('Koya' in dialect or 'Ko.' in dialect): return 'Koya source within the Gondi section'
    if language=='Ka.' and re.search(r'Badaga|Hock\.',dialect): return 'Badaga fieldnotes or Hockings source within Kannada'
    return BASE.get(language,NOT.get(language,'Unidentified language'))+(' dialect or source '+dialect if dialect else '')

def main():
    front=LOCAL/'dedr/frontmatter/new_frontmatter.html'
    text=front.read_text(encoding='utf-8')
    for token in ['Kurub.','Koya Su.','Koya T.','Oll.','Badaga']:
        if token not in text: raise ValueError('Missing front-matter evidence '+token)
    pairs={(k,'') for k in list(BASE)+list(NOT)}|{('Ga.','Oll.'),('Ga.','S.'),('Ga.','S.2'),('Ga.','S.3'),('Ga.','P.'),
          ('Go.','Ko.'),('Go.','Koya Su.'),('Go.','Koya T.'),('Ka.','Badaga'),('Ka.','Hock.')}
    parsed=[LOCAL/'parsed'/(key+'.json') for key in set(ENTRY.values()) if (LOCAL/'parsed'/(key+'.json')).exists()]
    if (LOCAL/'s4-entries.json').exists(): parsed.extend(LOCAL/'parsed/s4'/(key+'.json') for key in read(LOCAL/'s4-entries.json'))
    for p in parsed:
        for f in read(p).get('forms',[]): pairs.add((f['language'],f['dialect']))
    rows=[]
    for language,dialect in sorted(pairs):
        tips,notes=map_form(language,dialect)
        rows.append(dict(label=language+(' ('+dialect+')' if dialect else ''),language=language,dialect=dialect,
                         identification=describe(language,dialect),frontmatter_page=PAGES.get(language,'xxxv, xxxviii'),
                         frontmatter_section={'Ga.':30,'Go.':31,'Ka.':20,'Kurub.':17}.get(language,46),
                         tip=tips if tips else 'not a tip',rule='pool dialects and sources to language, with named variety exceptions',
                         uncertain=notes))
    write(RUN/'language-tip-map.json',dict(source_sha256=sha(front),labels=rows,
          coverage_notes=dict(Badaga='Ka. (Badaga) and Ka. (Hock.); no independent language siglum',
                              Yeruva='No label found in the language list or source sections; always missing',
                              Betta_Kurumba='Kurub.; section 17 identifies Betta Kuruba',
                              Gondi_Koya='Explicit Koya Su. and Koya T.; Ko. requires Voc. verification'),
          absent_tip_labels=['Yeruva']))

if __name__=='__main__': main()
