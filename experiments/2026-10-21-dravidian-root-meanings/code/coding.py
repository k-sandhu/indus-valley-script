"""Code meanings locally: python -I code/coding.py [--recode LOCAL_JSON]. No reconstruction."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse
import csv
import re
import unicodedata
from common import LOCAL,RUN,DOWNLOADS,ENTRY,TIPS,folded,read,write
from dedr_parse import head

KEYWORDS=dict(zip(ENTRY,['fish','star','six','seven','three','banyan','north','earring','youth',
                            'squirrel','child','space','white','murukan','spindle','ray']))
STAR_HEADS={'star','planet','constellation','asterism','nakshatra','naksatra','natcattiram','comet','meteor'}
STAR_NAMES=['venus','jupiter','mars','mercury','saturn','sirius','canopus','arcturus','aldebaran','antares',
            'spica','regulus','capella','vega','pleiades','orion','ursa major','great bear','seven sages',
            'seven rishis','rohini','krttika','ardra','mrgasiras','revati','asvini']

def words(s,options):
    return any(re.search(r'(?<!\w)'+re.escape(x)+r'(?!\w)',s) for x in options)

def STAR(s):
    h=folded(head(s)); f=folded(s)
    if h in {'sun','moon','sky'} or words(f,['pisces','fish sign']): return False
    if words(f,['fish']) and words(f,['zodiac','constellation','sign']): return False
    if any(x in f for x in ['starfish','star-anise','star apple','star-shaped']): return False
    if words(f,['star']) and words(f,['mark','spot','blaze','forehead']): return False
    return h in STAR_HEADS or bool(re.fullmatch(r'na(?:ksh|ks|kṣ|t[cs]c?)atra',h)) or any(
        phrase in f for phrase in ['lunar mansion','shooting star','morning star','evening star','pole star','polar star','north star']) or words(f,STAR_NAMES)

def FISH(s): return head(s)=='fish'
def SIX(s): return s in {'six','6'}
def SEVEN(s): return s in {'seven','7'}
def THREE(s): return s in {'three','3'}
def BANYAN(s): return bool(re.search(r'banyan|banian|ficus benghalensis|f\. bengalensis|f\. indica',s))
def NORTH(s): return words(s,['north','northern','northward','northwards','northerly'])
def EARRING(s):
    return head(s) in {'earring','ear-ring','ear ornament','ear-ornament','ear-pendant','ear-drop','eardrop','ear jewel','bangle','bracelet'} or (words(s,['ring']) and words(s,['ear']))
def YOUTH(s): return any(x in s for x in ['youth','youthful','youthfulness','young','juvenile','juvenility','adolescence','adolescent','tender age'])
def SQUIRREL(s): return 'squirrel' in s
def CHILD(s):
    return head(s) in {'child','children','infant','baby','boy','girl','son','daughter','offspring','young one'} or s in {'young','young one','young ones'} or s.startswith('young of')
def SPACE(s): return head(s) in {'space','interval','gap','interspace','void','vacuum','vacancy','emptiness','expanse'} or s in {'open place','open ground','open air'}
def WHITE(s): return any(x in s for x in ['white','whiteness','whitish'])
def VELGOD(s):
    f=folded(s)
    return words(f,['murukan','murugan','muruga','muruka','muruk','skanda','subrahmanya','subrahmanya','kama','cupid','god of love']) or f in {'god','deity'}
def SPINDLE(s): return 'spindle' in s
def LIGHT(s):
    return head(s) in {'ray','beam','sunbeam','light','lustre','luster','radiance','brightness','brilliance','splendour','splendor','gleam','glitter','shine','shining','glow','effulgence'} or bool(re.match(r'^(?:shine|glitter|gleam|glisten|glow|sparkle|flash)',s))
CLASSES={name:globals()[name] for name in ENTRY}

def code_entry(entry,predicate,exclude_doubtful=False,recode=None,meaning=None):
    result={t:dict(state=None,evidence=[],forms=[]) for t in TIPS}
    for form in entry['forms']:
        if form['loan'] or (exclude_doubtful and form['doubtful']): continue
        for tip in form['tips']:
            r=result[tip]
            r['forms'].append(dict(entry=entry['entry'],language=form['language'],dialect=form['dialect'],form_index=form['index']))
            if r['state'] is None: r['state']=0
            for i,seg in enumerate(form['segments']):
                if seg['dropped']: continue
                key=(meaning,entry['entry'],form['index'],i)
                matches=recode[key] if recode is not None and key in recode else predicate(seg['normalised'])
                if matches:
                    r['state']=1
                    r['evidence'].append(dict(entry=entry['entry'],language=form['language'],dialect=form['dialect'],form_index=form['index'],segment_index=i))
    return dict(entry=entry['entry'],tips=result)

def s4_normalise(s):
    s=unicodedata.normalize('NFD',s.lower())
    s=''.join(c for c in s if c not in '\u0301\u0300··ː')
    return unicodedata.normalize('NFC',s)

def s4_coding(entries,fish):
    result=code_entry(fish,lambda s:False)
    result['entry']='S4 search'
    for entry in entries:
        filtered=dict(entry,forms=[f for f in entry['forms'] if re.match(r'^m[iī][nṉṇ]',s4_normalise(f['form']))])
        c=code_entry(filtered,STAR)
        for tip,r in c['tips'].items():
            if r['state']==1:
                result['tips'][tip]['state']=1
                result['tips'][tip]['evidence'].extend(r['evidence'])
    return result

def dravlex():
    if not read(RUN/'sources-dravlex.json')['usable']: return None
    paths=list((DOWNLOADS/'dravlex/extracted').glob('*/cldf/forms.csv'))
    if len(paths)!=1: raise ValueError('Expected one pinned CLDF forms table')
    base=paths[0].parent
    def rows(name):
        with (base/name).open(encoding='utf-8-sig',newline='') as stream: return list(csv.DictReader(stream))
    params={r['ID'] for r in rows('parameters.csv') if r['Name'].strip().lower()=='star' or r.get('Concepticon_Gloss','').strip().lower()=='star'}
    aliases={re.sub('[^a-z]','',t.lower()):t for t in TIPS}
    aliases['badga']='Badaga'
    result={t:dict(state=None,evidence=[],forms=[]) for t in TIPS}
    for row in rows('forms.csv'):
        if row['Parameter_ID'] not in params or not row['Form'].strip() or row['Form'] in {'-','?'}: continue
        key=re.sub('[^a-z]','',row['Language_ID'].lower())
        if key not in aliases: raise ValueError('Unmapped DravLex language')
        tip=aliases[key]; r=result[tip]
        if r['state'] is None: r['state']=0
        evidence=dict(cldf_id=row['ID'],language_id=row['Language_ID'],parameter_id=row['Parameter_ID'])
        r['forms'].append(evidence)
        if re.search(r'm[iīɪ]ː?[nṉɳ]',unicodedata.normalize('NFC',row['Form']).lower()):
            r['state']=1; r['evidence'].append(evidence)
    if not params: raise ValueError('No STAR concept in pinned DravLex')
    return dict(entry='DravLex STAR',tips=result)

def make_variants(entries,recode=None):
    variants={}
    for variant in ['primary','S1','S6','S7']+(['S8'] if recode is not None else []):
        codes={}
        for meaning,key in ENTRY.items():
            if variant=='S7': key={'STAR':'4885','EARRING':'4978'}.get(meaning,key)
            predicate=(lambda s,k=KEYWORDS[meaning]:head(s)==k) if variant=='S6' else CLASSES[meaning]
            codes[meaning]=code_entry(entries[key],predicate,variant=='S1',recode if variant=='S8' else None,meaning)
        variants[variant]=codes
    return variants

def main(recodefile=None):
    entries={k:read(LOCAL/'parsed'/(k+'.json')) for k in set(ENTRY.values())}
    manual=None
    if recodefile:
        manual={}
        for row in read(recodefile):
            key=(row['meaning'],str(row['entry']),int(row['form_index']),int(row['segment_index']))
            if row['meaning'] not in ENTRY or key in manual or type(row['member']) is not bool: raise ValueError('Invalid manual recode')
            if key[1]!=ENTRY[row['meaning']] or key[2]<0 or key[3]<0: raise ValueError('Recode does not address an assigned entry segment')
            entry=entries[key[1]]; form=entry['forms'][key[2]]; seg=form['segments'][key[3]]
            if row.get('segment_sha256'):
                import hashlib
                if hashlib.sha256(seg['normalised'].encode()).hexdigest()!=row['segment_sha256']: raise ValueError('Recode segment hash mismatch')
            manual[key]=row['member']
    variants=make_variants(entries,manual)
    variants['S4']={'STAR':s4_coding([read(LOCAL/'parsed/s4'/(key+'.json')) for key in read(LOCAL/'s4-entries.json')],entries['4885'])}
    extra=dravlex()
    if extra is not None: variants['S3']={'STAR':extra}
    for name,data in variants.items(): write(LOCAL/'codings'/(name+'.json'),data)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--recode',type=Path)
    main(ap.parse_args().recode)
