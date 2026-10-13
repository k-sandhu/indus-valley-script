"""Normalize primary editions into explicit, separately named observation units.

Normalized records and lexical spellings are local-only. This module publishes no
source corpus and never infers a word boundary in an Indus inscription.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from bs4 import BeautifulSoup

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
LOCAL=ROOT/'data/raw/2026-10-12-bronze-age-comparison'
NS={'t':'http://www.tei-c.org/ns/1.0'}
XMLID='{http://www.w3.org/XML/1998/namespace}id'

def metadata(name):
    return json.loads((PACKAGE/'acquisition'/f'{name}.json').read_text(encoding='utf-8'))
def source_path(name):
    return ROOT/metadata(name)['local_path']
def source_json(name):
    return json.loads(source_path(name).read_bytes())
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()
def clean(form):
    return bool(form.strip()) and not re.search(r'[\[\]?#⸢⸣…<>]|(^|[- .])x($|[- .])|\.\.\.',form)

def category(pos, egypt=False, name=None):
    if egypt:
        if pos=='entity_name': return 'NAME'
        if pos in {'numeral','number'}: return 'NUMBER'
        if pos=='verb': return 'VERB'
        if pos in {'pronoun','preposition','particle','adverb','conjunction','interjection'}: return 'FUNCTION'
        if pos in {'substantive','adjective'}: return 'NOMINAL'
    else:
        if pos in {'PN','DN','GN','RN','TN','EN','MN','SN','WN','CN'}: return 'NAME'
        if pos=='n': return 'NUMBER'
        if pos in {'V','V/t','V/i'}: return 'VERB'
        if pos in {'PRP','P','DET','CONJ','CNJ','MOD','AV','ADV','IP','REL','NEG','DEM','POS','PRO','POSS'}: return 'FUNCTION'
        if pos in {'N','NU','AJ','ADJ'}: return 'NOMINAL'
    return 'UNKNOWN'

def gdl_units(nodes):
    result=[]
    uncertain=False
    for node in nodes:
        if any(node.get(key) for key in ['break','queried','supplied','uncertain']): uncertain=True
        if node.get('n')=='n':
            unit=node.get('form')
            if unit: result.append('NUM:'+unit)
            else: uncertain=True
        elif 'c' in node and node.get('form'):
            result.append(node['form'])
        elif node.get('seq'):
            children,bad=gdl_units(node['seq']);result.extend(children);uncertain|=bad
        elif node.get('group'):
            children,bad=gdl_units(node['group']);result.extend(children);uncertain|=bad
        elif node.get('v') or node.get('s'):
            result.append(str(node.get('v',node.get('s'))))
        else:
            uncertain=True
    return result,uncertain

def oracc(name, corpus, limit=None):
    archive=zipfile.ZipFile(source_path(name))
    catalogue=json.loads(archive.read(next(n for n in archive.namelist() if n.endswith('/catalogue.json'))))['members']
    entries=[n for n in archive.namelist() if '/corpusjson/' in n and n.endswith('.json')]
    entries.sort(key=lambda n:hashlib.sha256(f'20261012:{Path(n).stem}'.encode()).hexdigest())
    if limit: entries=entries[:limit]
    records=[];counts=Counter();language_counts=Counter();pos_counts=Counter();licenses=Counter()
    examples=[]
    for entry in entries:
        try:
            data=json.loads(archive.read(entry))
        except json.JSONDecodeError:
            counts['invalid_source_json']+=1;continue
        if 'textid' not in data:
            counts['missing_source_textid']+=1;continue
        text=data['textid'];info=catalogue.get(text,{})
        licenses[data.get('license','unverified')]+=1
        obj='tablet';objnum=0;line='';objects=defaultdict(list);lines=defaultdict(list);bad_objects=set();bad_lines=set()
        def walk(nodes):
            nonlocal obj,objnum,line
            for node in nodes:
                if node.get('node')=='d':
                    if node.get('type')=='object':
                        objnum+=1;obj=f"{node.get('subtype','object')}:{objnum}";line=''
                    if node.get('type')=='line-start':line=node.get('label',node.get('ref','line'))
                    if node.get('type') in {'nonx','non-text'} and node.get('subtype') not in {'ruling','blank','space'}:
                        bad_objects.add(obj);bad_lines.add((obj,line))
                elif node.get('node')=='l':
                    fields=node.get('f',{});form=fields.get('form',node.get('frag',''))
                    units,bad=gdl_units(fields.get('gdl',[]))
                    bad|=not clean(form) or not clean(node.get('frag',form)) or not units
                    token={'form':form,'units':units,'tag':category(fields.get('pos')),
                           'source_pos':fields.get('pos'),'language':fields.get('lang','unknown'),
                           'source_ref':node.get('ref'),'dirty':bad}
                    language_counts[token['language']]+=1;pos_counts[str(token['source_pos'])]+=1
                    objects[obj].append(token);lines[(obj,line)].append(token)
                    if bad:bad_objects.add(obj);bad_lines.add((obj,line))
                if node.get('cdl'):walk(node['cdl'])
        walk(data.get('cdl',[]))
        has_language=any(t['language'].startswith('sux' if corpus=='sumerian' else 'akk') for ts in objects.values() for t in ts)
        declared=info.get('languages',info.get('language',''))
        if not has_language and not (corpus=='akkadian' and 'Akkadian' in declared):
            counts['no_confirmed_target_language']+=1;continue
        counts['documents_parsed']+=1
        physical=[text]
        museum=info.get('museum_no')
        if museum:physical.append('museum:'+museum)
        common={'corpus':corpus,'document':text,'aliases':physical,'source':name,
                'source_url':f"https://oracc.museum.upenn.edu/{data['project']}/{text}",
                'date':info.get('period','unknown'),'genre':info.get('genres',info.get('genre','unknown')),
                'site':info.get('provenience','unknown')}
        def add(tokens,identity,unit_kind):
            counts[unit_kind+'_total']+=1
            if any(t['dirty'] for t in tokens):counts[unit_kind+'_dirty']+=1;return
            units=[unit for token in tokens for unit in token['units']]
            if not units:return
            records.append(dict(common,id=f'{name}:{text}:{identity}',kind=unit_kind,
                          encoding='cuneiform-sign-readings',units=units,words=[t['form'] for t in tokens],
                          gold=[t['tag'] for t in tokens],word_units=[t['units'] for t in tokens],
                          source_word_refs=[t['source_ref'] for t in tokens]))
        for object_key,tokens in objects.items():
            kind='seal' if object_key.startswith('seal:') else 'whole_tablet'
            if object_key not in bad_objects:add(tokens,object_key,kind)
            else:counts[kind+'_dirty']+=1
        for key,tokens in lines.items():
            if key not in bad_lines:add(tokens,'/'.join(key),'natural_line')
        if len(examples)<4:
            examples.append({'textid':text,'edition':entry,'period':common['date'],'genre':common['genre'],
                             'source_url':common['source_url'],'parsed_word_count':sum(map(len,objects.values()))})
    return records,{'archive_entries':len([n for n in archive.namelist() if '/corpusjson/' in n and n.endswith('.json')]),
                    'selected_entries':len(entries),'counts':dict(counts),'token_languages':dict(language_counts),
                    'source_pos':dict(pos_counts),'embedded_licenses':dict(licenses),'inspection_examples':examples}

def egyptian_extent(text):
    name=f'aed-text-{text.lower()}-v1'
    file=PACKAGE/'acquisition'/f'{name}.json'
    if not file.exists() or metadata(name)['status']!='acquired':return None
    try:
        tree=ET.fromstring(source_path(name).read_bytes())
    except ET.ParseError:return None
    obj=tree.find('.//t:objectType',NS); support=tree.find('.//t:supportDesc',NS)
    sentence_ids={el.get(XMLID,'').removeprefix('id').removeprefix('tla') for el in tree.findall('.//t:s',NS)}
    return {'object_type':obj.text.strip() if obj is not None and obj.text else None,
            'physical_id':support.get(XMLID) if support is not None else None,'sentence_ids':sentence_ids,
            'source_word_ids':{el.get(XMLID,'').removeprefix('id').removeprefix('tla') for el in tree.findall('.//t:w',NS)},
            'dates':[dict(el.attrib,text=el.text) for el in tree.findall('.//t:origDate/t:date',NS)],
            'source_url':metadata(name)['url']}

def egyptian():
    records=[];counts=Counter();pos_counts=Counter();examples=[]
    for name in ['egyptian-aes-archive-v1','egyptian-aes-grab-v1']:
        data=source_json(name);bytext=defaultdict(list)
        for identity,row in data.items():
            if row.get('date')!='OK & FIP':counts['date_excluded']+=1;continue
            bytext[row['text']].append((identity,row))
        for text,sentences in sorted(bytext.items()):
            extent=egyptian_extent(text) if name=='egyptian-aes-archive-v1' else None
            if extent:counts['texts_with_extent_metadata']+=1
            ids={identity for identity,_ in sentences}
            full=bool(extent and ids==extent['sentence_ids'] and extent['object_type']=='Gefäß')
            combined_words=[];combined_tags=[];combined_word_units=[];combined_refs=[];full_clean=True
            for identity,row in sentences:
                tokens=row['token'];forms=[t.get('written_form','') for t in tokens]
                tags=[category(t.get('pos'),egypt=True,name=t.get('name')) for t in tokens]
                pos_counts.update(str(t.get('pos')) for t in tokens)
                usable=all(clean(form) for form in forms)
                word_units=[[c for c in t.get('hiero_unicode','') if 0x13000<=ord(c)<=0x1342F] for t in tokens]
                refs=[t['_id'] for t in tokens]
                if extent and not set(refs)<=extent['source_word_ids']:full=False;counts['extent_word_mismatch']+=1
                common={'corpus':'egyptian','document':text,'aliases':[text]+([extent['physical_id']] if extent and extent['physical_id'] else []),
                        'source':name,'source_url':extent['source_url'] if extent else f'https://github.com/simondschweitzer/aes/tree/35276d2527cca1a055e31ed5f6683e777717170f',
                        'date':row['date'],'genre':'jar_inscription' if name=='egyptian-aes-archive-v1' else 'tomb_text',
                        'site':row.get('findspot','unknown'),'id':identity,'words':forms,'gold':tags,
                        'word_units':word_units,'source_word_refs':refs,'dates':extent['dates'] if extent else []}
                counts['sentences_seen']+=1
                if usable:
                    records.append(dict(common,kind='source_sentence',encoding='editorial-word-tokens',units=forms))
                    if all(word_units):
                        records.append(dict(common,id=identity+':glyph',kind='glyph_sentence',encoding='Egyptian-Unicode-glyphs',
                                            units=[c for group in word_units for c in group]))
                        counts['complete_glyph_sentences']+=1
                else:counts['dirty_sentences']+=1
                combined_words.extend(forms);combined_tags.extend(tags);combined_word_units.extend(word_units);combined_refs.extend(refs)
                full_clean&=usable
            if full and full_clean:
                records.append(dict(common,id=text+':jar',kind='whole_jar_inscription',encoding='editorial-word-tokens',
                                    units=combined_words,words=combined_words,gold=combined_tags,word_units=combined_word_units,
                                    source_word_refs=combined_refs))
                counts['verified_complete_jar_texts']+=1
                if len(examples)<5:
                    examples.append({'textid':text,'source_url':extent['source_url'],'object_type':extent['object_type'],
                                     'word_count':len(combined_words),'source_sentence_count':len(sentences),'dates':extent['dates']})
    return records,{'counts':dict(counts),'source_pos':dict(pos_counts),'inspection_examples':examples}

def greek_token(anchor):
    text=anchor.get_text('',strip=True)
    query=urllib.parse.parse_qs(urllib.parse.urlparse(anchor.get('href','')).query).get('q',[''])[0]
    raw=query or text
    if not raw.strip() or raw in {'sup.','inf.','mut.','vac.','vacat','vest.','lat.','reliqua','mutila'}:return None
    if not query and raw.endswith('.'):return None
    raw=unicodedata.normalize('NFC',raw)
    certain=clean(raw) and not any(0x300<=ord(c)<=0x36F for c in unicodedata.normalize('NFD',raw))
    lexical=raw.replace('$','')
    if re.fullmatch(r'\d+(?:[.,/]\d+)?',lexical):tag='NUMBER';units=['NUM:'+lexical]
    elif re.search(r'[A-Z]|\*\d',lexical):tag='LOGOGRAM';units=[lexical]
    else:tag='SYLLABIC';units=lexical.split('-')
    return {'form':raw,'units':units,'tag':tag,'certain':certain,'source_ref':anchor.get('data-pk')}

def greek():
    catalogue=source_json('liber-tablet-data-v1')['data'];info={int(row[1]):row for row in catalogue}
    selected={int(re.search(r'liber-doc-(\d+)-',row['id']).group(1)) for row in json.loads((PACKAGE/'acquisition-plan-v5.json').read_text()) if row['id'].startswith('liber-doc-')}
    if json.loads((PACKAGE/'cohort-selection-v1.json').read_text())['preexisting_fixture_201_in_selected']:selected.add(201)
    records=[];counts=Counter();examples=[]
    for identity in sorted(selected):
        name='liber-tablet-201-v1' if identity==201 else f'liber-doc-{identity}-v1'
        mfile=PACKAGE/'acquisition'/f'{name}.json'
        if not mfile.exists() or metadata(name)['status']!='acquired':counts['failed_acquisitions']+=1;continue
        row=info[identity];soup=BeautifulSoup(source_path(name).read_bytes(),'html.parser')
        table=soup.select_one('table.table-text')
        if table is None:counts['missing_transcription_table']+=1;continue
        common={'corpus':'mycenaean','document':str(identity),'aliases':[str(identity)],'source':name,
                'source_url':f'https://liber.cnr.it/tablet/view/{identity}','date':row[7],'genre':row[9],
                'site':row[2],'designation':row[3]}
        all_tokens=[];all_clean=True;line_count=0
        for index,tr in enumerate(table.find_all('tr')):
            cells=tr.find_all('td',recursive=False)
            if len(cells)<3:continue
            tokens=[t for anchor in cells[2].find_all('a',attrs={'data-pk':True}) if (t:=greek_token(anchor))]
            if not tokens:continue
            label=' '.join(c.get_text(' ',strip=True) for c in cells[:2]);line_count+=1
            certain=all(t['certain'] for t in tokens)
            all_clean&=certain;all_tokens.extend(tokens)
            if certain:
                records.append(dict(common,id=f'{identity}:line:{index}',kind='natural_line',encoding='Linear-B-syllables-logograms-numbers',
                                    units=[u for t in tokens for u in t['units']],words=[t['form'] for t in tokens],
                                    gold=[t['tag'] for t in tokens],word_units=[t['units'] for t in tokens],source_word_refs=[t['source_ref'] for t in tokens],line_label=label))
            else:counts['dirty_lines']+=1
        if all_tokens and all_clean:
            records.append(dict(common,id=f'{identity}:whole',kind='whole_document',encoding='Linear-B-syllables-logograms-numbers',
                                units=[u for t in all_tokens for u in t['units']],words=[t['form'] for t in all_tokens],gold=[t['tag'] for t in all_tokens],
                                word_units=[t['units'] for t in all_tokens],source_word_refs=[t['source_ref'] for t in all_tokens],source_lines=line_count))
            counts['clean_whole_documents']+=1
            if len(examples)<5:examples.append({'id':identity,'designation':row[3],'source_url':common['source_url'],
                                              'site':row[2],'date':row[7],'lines':line_count,'words':len(all_tokens)})
        counts['documents_parsed']+=1
    return records,{'counts':dict(counts),'inspection_examples':examples}

def indus():
    file=ROOT/'experiments/2026-10-11-two-approaches/grammar/grammar.py'
    spec=importlib.util.spec_from_file_location('prior_indus_grammar',file)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    rows,census=module.load_corpus(ROOT/'data/normalized/lipi_observed_faces.jsonl')
    result=[{'corpus':'indus','document':str(r['group']),'aliases':[str(r['group'])],
             'id':r['record_id'],'kind':'whole_face','encoding':'Wells-observed-sign-codes','units':list(r['seq']),
             'words':[],'gold':[],'word_units':[],'source':'local-lipi-observed-faces',
             'site':r.get('site'),'date':'source object chronology not joined in this benchmark'} for r in rows]
    return result,census

def normalize(output):
    output.mkdir(parents=True,exist_ok=False)
    records=[];census={}
    for name,corpus,limit in [('sumerian-ur3-v1','sumerian',3000),('akkadian-atletters-v1','akkadian',None),('akkadian-rimanum-v1','akkadian',None)]:
        rows,summary=oracc(name,corpus,limit);records.extend(rows);census[name]=summary
        print(json.dumps({'source':name,'normalized_units':len(rows)}),flush=True)
    for name,function in [('egyptian',egyptian),('mycenaean',greek),('indus',indus)]:
        rows,summary=function();records.extend(rows);census[name]=summary
        print(json.dumps({'source':name,'normalized_units':len(rows)}),flush=True)
    target=output/'records.jsonl'
    with target.open('x',encoding='utf-8') as handle:
        for record in records:handle.write(json.dumps(record,ensure_ascii=False)+'\n')
    inputs={path.name:json.loads(path.read_text(encoding='utf-8')) for path in sorted((PACKAGE/'acquisition').glob('*.json'))}
    manifest={'census':census,'normalized_records':len(records),'records_sha256':digest(target),
              'code_sha256':digest(__file__),'protocol_sha256':digest(PACKAGE/'PROTOCOL.md'),
              'cohort_spec_sha256':digest(PACKAGE/'COHORT-SPEC.md'),'source_hashes':{name:r.get('sha256') for name,r in inputs.items()},
              'handling':'source-derived records remain local-only','lexical_units_are_not_common_across_scripts':True}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    normalize(LOCAL/'normalized-v1')
