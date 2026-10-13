"""Preserve the 96-sense ledger and fill six named pre-outcome visual gaps."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT/'data/raw/2026-10-12-anchor-expansion/anchors'
VISUAL = HERE.parent/'visual/families.json'
MW = ROOT/'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt'
INDEX = ROOT/'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json'
PIN = '55e8addbd96e8d9001b8789026b026763f4049c1'
URL = f'https://github.com/sanskrit-lexicon/csl-orig/blob/{PIN}/v02/mw/mw.txt'
SOURCE = f'Monier-Williams 1899, Cologne digital edition, pinned csl-orig {PIN}'

SIX = [
 ('śākhā','SAKA','214950','1062,3','branch','Rigveda cited','Branched/forked plant component; a branch school or textual recension is a separate sense'),
 ('daṇḍa','daRqa','89571','466,2','stick, staff, rod or pole','Rigveda cited','Straight or headed upright; punishment, sovereignty and measurement are separate senses'),
 ('iṣu','izu','29463','168,3','arrow','Rigveda, Atharvaveda and Vājasaneyi Saṃhitā cited','Arrow/shaft comparison where a point and shaft are observed; no numerical value assigned'),
 ('śara','Sara','213454','1056,2','arrow or shaft','Muṇḍaka Upaniṣad, Manu and Mahābhārata cited','Arrow comparison, separate from the RV reed/grass record213453'),
 ('jāla','jAla','79046','419,3','net for catching birds or fish','Atharvaveda VIII/X, Kātyāyana Śrauta and Pāraskara Gṛhya cited','Crossing mesh as a net; watery, lattice-window and generic woven-texture senses are separate'),
 ('tantu','tantu','82420','436,1','thread, cord, filament or warp of a web','Rigveda cited','Thread/warp component; lineage and sacrificial-series senses are separate'),
]

SCAN_PAGES = [
 ('168','https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0168-imaka.pdf','resolved'),
 ('466','https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0466-dakSiNAzA.pdf','resolved'),
 ('419','https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0419-jAnevAdika.pdf','resolved'),
 ('436','https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0436-tanUhrada.pdf','resolved'),
 ('1056','https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw1056-zayanagRha.pdf','resolved'),
 ('1062','https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw1062-zAkaMdheya.pdf','timeout'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):
    if path.exists():
        raise RuntimeError('Refusing overwrite '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    prior = json.loads((HERE/'senses.json').read_text(encoding='utf-8'))['rows']
    old_links = json.loads((HERE/'family-links.json').read_text(encoding='utf-8'))['families']
    visual = json.loads(VISUAL.read_text(encoding='utf-8'))
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    text = MW.read_text(encoding='utf-8')
    lines = text.splitlines()
    line_by_id = {}
    for number,line in enumerate(lines,1):
        m = re.match(r'<L>(.*?)<pc>(.*?)<k1>(.*?)<k2>',line)
        if m:
            line_by_id[m[1]]=(number,m[2],m[3])
    records = {}
    for rec in text.split('<LEND>'):
        m = re.search(r'<L>(.*?)<pc>(.*?)<k1>(.*?)<k2>',rec)
        if m:
            records[m[1]]=rec.strip()
    supplement=[]
    for word,key,identity,page,meaning,period,role in SIX:
        number,actual_page,actual_key=line_by_id[identity]
        assert (actual_page,actual_key)==(page,key)
        body=records[identity]
        hits=[r for r in index[key] if r['entry_id']==identity]
        assert len(hits)==1 and hits[0]['page_column']==page
        supplement.append(dict(word=word,slp1=key,comparison_headword=word,entry_id=identity,page_column=page,
                               meaning=meaning,period=period,source=SOURCE,url=URL,role=role,
                               addition_status='new-requested-gap-sense-2026-10-12',sense_id='MW-'+identity,
                               source_record_url=URL+'#L'+str(number),
                               dictionary_citations=re.findall(r'<ls(?: [^>]*)?>(.*?)</ls>',body)))
    assert len(supplement)==6
    combined=prior+supplement
    by={r['word']:r for r in combined}
    assert len(by)==102
    # A request under the canonical headword can have several deliberately
    # selected sense rows, such as koṣṭha(granary/enclosure) and yuga(yoke/pair).
    matches={}
    for r in combined:
        for key in {r['word'],r['comparison_headword']}:
            matches.setdefault(key,[]).append(r['word'])
    families={}
    unmatched={}
    for family in visual['rows']:
        fid=family['family_id']
        requests=family['Sanskrit_comparison_words']
        selected=[]
        match_map={}
        missing=[]
        for w in requests:
            found=matches.get(w,[])
            if not found:
                missing.append(w);unmatched.setdefault(w,[]).append(fid)
            else:
                match_map[w]=found
                selected.extend(found)
        # These are authored competing components, with exact sense checks;
        # they do not replace the frozen visual meaning or role prediction.
        alternative_words=old_links.get(fid,{}).get('words',[])
        if fid=='multi_appendage_creature':
            alternative_words+=['makṣikā','śakuni','pakṣin']
        selected=list(dict.fromkeys(selected+alternative_words))
        assert selected, fid
        assert all(w in by for w in selected)
        families[fid]=dict(words=selected,sense_ids=[by[w]['sense_id'] for w in selected],
                           requested_words=requests,matched_requested_words=match_map,
                           unselected_requested_words=missing,
                           picture_observation=family['picture_observation'],
                           graphic_rivals=family['graphic_rivals'],
                           role_prediction=family['role_predictions'],
                           basis='Selected component and functional comparisons for the frozen visual family. Generic geometric forms retain indirect/emblem alternatives.',
                           scope='No new complete-context outcome tables inspected by this contributor.')
    assert set(families)=={r['family_id'] for r in visual['rows']} and len(families)==70
    write(HERE/'supplement-v1.json',dict(scope='Six exact vocabulary gaps requested after all713 graphic witnesses were reviewed, before this contributor inspected new family-context outcomes. The96-sense endpoint remains unchanged.',
                                       previous_sense_ledger='senses.json',additional_senses=6,combined_senses=102,rows=supplement))
    write(HERE/'family-links-v2.json',dict(scope='Exact sense links for all70 frozen visual family IDs. Unselected request spellings are reported, not assigned arbitrary homonyms.',
                                         visual_map={'path':VISUAL.relative_to(ROOT).as_posix(),'sha256':sha(VISUAL),'frozen_at_utc':visual['frozen_at_utc']},
                                         ledgers=['senses.json','supplement-v1.json'],families=families,
                                         unselected_requested_words=unmatched))
    write(RAW/'selected-supplement-records-v1.json',{'rows':[dict(word=r['word'],entry_id=r['entry_id'],record=records[r['entry_id']]) for r in supplement]})
    write(HERE/'sources-supplement-v1.json',dict(scope='Same pinned MW witness and existing derived index as sources.json. Six additional official print-page URLs checked.',
                                               source_record_count=6,print_pages=[dict(page=p,url=u,web_access=s,scope='Page URL from official scan index; no new image verification.') for p,u,s in SCAN_PAGES],
                                               local_selected_records=(RAW/'selected-supplement-records-v1.json').relative_to(ROOT).as_posix()))
    write(HERE/'verification-supplement-v1.json',dict(status='pass',supplement_senses=6,combined_senses=102,matched_families=70,
                                                    unselected_hint_spellings=len(unmatched),unselected_requested_words=unmatched,
                                                    selected_senses=[dict(word=r['word'],entry_id=r['entry_id'],page_column=r['page_column'],key_index_page_match=True) for r in supplement],
                                                    inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [MW,INDEX,VISUAL,HERE/'senses.json',HERE/'family-links.json',Path(__file__).resolve()]],
                                                    outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [HERE/'supplement-v1.json',HERE/'family-links-v2.json']],
                                                    scope='Exact source identity and family-key matching. Unselected hints are not claimed absent from Sanskrit.'))
    print(json.dumps({'status':'pass','combined_senses':102,'families':70,'unselected_requested_words':unmatched},ensure_ascii=False))


if __name__=='__main__':
    main()
