"""Normalise archived ORACC and CDLI seal legends, retaining every source witness.

Command line (all data locations are explicit):
  python -I normalize_cuneiform.py --ur3-archive ZIP --ur3-manifest JSON
    --held-records JSONL [--oakk-archive ZIP] --cdli-cat CSV --cdli-atf ATF
    --lexicon TSV --output-dir DIR --scratch-dir NEW_DIR --counts JSON
    --acquisition-record JSON [--acquisition-record JSON ...]

Output names inside output-dir are sux-ur3.jsonl, akk-sargonic.jsonl,
sux-sargonic.jsonl and cuneiform-* review files. Existing output files are
refused. The shared ORACC traversal, clean predicate, GDL units and legacy
categories were copied after reading reference_sources.py (12 October).
No source module is imported. Only the Python standard library is used.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import random
import re
import time
import unicodedata
import zipfile

AUTHOR = 'Codex GPT-6 family (exact model identifier not exposed), Codex API tool harness'
CORPORA = ('sux-ur3', 'akk-sargonic', 'sux-sargonic')
SUBSCRIPTS = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
POS_TAG = dict(PN='NAME', RN='NAME', DN='DIVINE', GN='PLACE', SN='PLACE', TN='PLACE', WN='PLACE', NU='NUMBER', n='NUMBER')
GRAM_POS = {'PRP', 'P', 'DET', 'CONJ', 'CNJ', 'MOD', 'AV', 'ADV', 'IP', 'REL', 'NEG', 'DEM', 'POS', 'PRO', 'POSS', 'RP'}


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        f.write(unicodedata.normalize('NFC', json.dumps(value, ensure_ascii=False, indent=1)) + '\n')


def jsonl(path, rows):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(unicodedata.normalize('NFC', json.dumps(row, ensure_ascii=False)) + '\n')


def clean(form):
    return bool(form.strip()) and not re.search(r'[\[\]?#⸢⸣⸤⸥〈〉⟨⟩…<>]|(^|[- .])x($|[- .])|\.\.\.', form)


def legacy_category(pos):
    if pos in {'PN','DN','GN','RN','TN','EN','MN','SN','WN','CN'}: return 'NAME'
    if pos == 'n': return 'NUMBER'
    if pos in {'V','V/t','V/i'}: return 'VERB'
    if pos in GRAM_POS - {'RP'}: return 'FUNCTION'
    if pos in {'N','NU','AJ','ADJ'}: return 'NOMINAL'
    return 'UNKNOWN'


def gdl_units(nodes):
    result, uncertain = [], False
    for node in nodes:
        if any(node.get(key) for key in ('break','queried','supplied','uncertain')): uncertain = True
        if node.get('n') == 'n':
            if node.get('form'): result.append('NUM:' + node['form'])
            else: uncertain = True
        elif 'c' in node and node.get('form'): result.append(node['form'])
        elif node.get('seq'):
            child, bad = gdl_units(node['seq']); result.extend(child); uncertain |= bad
        elif node.get('group'):
            child, bad = gdl_units(node['group']); result.extend(child); uncertain |= bad
        elif node.get('v') or node.get('s'): result.append(str(node.get('v',node.get('s'))))
        else: uncertain = True
    return result, uncertain


def flatten(nodes):
    for node in nodes:
        yield node
        if node.get('cdl'): yield from flatten(node['cdl'])


def safe_archive(path):
    archive = zipfile.ZipFile(path)
    for name in archive.namelist():
        if PurePosixPath(name).is_absolute() or PureWindowsPath(name).is_absolute() or PureWindowsPath(name).drive or '..' in PurePosixPath(name.replace('\\','/')).parts:
            archive.close(); raise ValueError('unsafe archive path')
    return archive


def token(node):
    f = node.get('f', {})
    form = f.get('form', node.get('frag', ''))
    units, bad = gdl_units(f.get('gdl', []))
    missing_gdl = not units
    if missing_gdl and form: units=atf_units(form)
    return dict(form=form, printed=node.get('frag', form), units=units,
                dirty=bad or missing_gdl or not clean(form) or not clean(node.get('frag', form)) or not units,
                pos=f.get('pos'), lang=f.get('lang', 'unknown'), cf=f.get('cf',''), gw=f.get('gw',''),
                ref=node.get('ref'), gdl=f.get('gdl', []))


def legacy_seals(data, info, source):
    obj, objnum, objects, bad_objects = 'tablet', 0, defaultdict(list), set()
    for node in flatten(data.get('cdl', [])):
        if node.get('node') == 'd':
            if node.get('type') == 'object':
                objnum += 1; obj = f"{node.get('subtype','object')}:{objnum}"
            if node.get('type') == 'surface' and node.get('subtype','').startswith('seal'):
                obj = 'seal:' + node.get('ref', node['subtype'])
            if node.get('type') in {'nonx','non-text'} and node.get('state',node.get('subtype')) not in {'ruling','blank','space'}:
                bad_objects.add(obj)
        elif node.get('node') == 'l':
            t = token(node); objects[obj].append(t)
            if t['dirty']: bad_objects.add(obj)
    if not any(t['lang'].startswith('sux') for ts in objects.values() for t in ts): return []
    text = data['textid']; aliases = [text]
    if info.get('museum_no'): aliases.append('museum:' + info['museum_no'])
    rows = []
    for key, ts in objects.items():
        if key.startswith('seal:') and key not in bad_objects and any(t['units'] for t in ts):
            rows.append(dict(corpus='sumerian', document=text, aliases=aliases, source=source,
                source_url=f"https://oracc.museum.upenn.edu/{data['project']}/{text}", date=info.get('period','unknown'),
                genre=info.get('genres',info.get('genre','unknown')), site=info.get('provenience','unknown'),
                id=f'{source}:{text}:{key}', kind='seal', encoding='cuneiform-sign-readings',
                units=[u for t in ts for u in t['units']], words=[t['form'] for t in ts],
                gold=[legacy_category(t['pos']) for t in ts], word_units=[t['units'] for t in ts],
                source_word_refs=[t['ref'] for t in ts]))
    return rows


def oracc_groups(data, info):
    groups, current, body, number, line = {}, None, None, 0, None
    def create(key, kind, is_seal):
        if key not in groups: groups[key] = dict(key=key, type=kind, seal=is_seal, tokens=[], events=[], line_labels=[])
        return key
    for node in flatten(data.get('cdl', [])):
        if node.get('node') == 'd':
            kind, subtype = node.get('type'), node.get('subtype','')
            if kind == 'object':
                number += 1
                matrix = 'seal' in subtype.lower() and 'sealing' not in subtype.lower()
                body = create(f'{subtype}:{number}', subtype, matrix)
                current, line = body, None
            elif kind == 'surface':
                line = None
                if subtype.startswith('seal'):
                    current = create('seal:' + node.get('ref',subtype), 'impression', True)
                    groups[current]['support_type']=groups[body]['type'] if body else ''
                else:
                    current = body
            elif kind == 'line-start':
                line = node.get('label',node.get('ref','line'))
                if current and line not in groups[current]['line_labels']: groups[current]['line_labels'].append(line)
            elif kind in {'nonx','non-text'} and current:
                if node.get('state',subtype) not in {'ruling','blank','space'}: groups[current]['events'].append(('damage', node))
        elif node.get('node') == 'l':
            if current is None:
                body = current = create('tablet:0','tablet',False)
            t = token(node); t['line'] = line
            groups[current]['tokens'].append(t); groups[current]['events'].append(('word',t))
    # Catalogue matrices and direct sealings may lack a seal-surface directive.
    kind=info.get('object_type','').lower()
    catalogue_seal=('seal (not impression)' in kind or 'cylinder seal' in kind or 'stamp seal' in kind or 'sealing' in kind)
    if catalogue_seal and not any(g['seal'] for g in groups.values()):
        if not groups:
            create('catalogue-seal-no-readable-json',kind,True)
        for g in groups.values():
            g['seal']=True
            if not g['tokens'] and not g['events']: g['edition_status']='no-readable-json-legend'
    return [g for g in groups.values() if g['seal']]


def norm_atf(text):
    return text.replace('sz','š').replace('SZ','Š').replace('s,','ṣ').replace('S,','Ṣ').replace('t,','ṭ').replace('T,','Ṭ').replace('g~','ĝ').replace('G~','Ĝ').translate(SUBSCRIPTS)


def bare(form):
    return re.sub(r'[\[\]⸢⸣⸤⸥?#*!_<>〈〉⟨⟩]', '', form)


def atf_units(form):
    text = bare(form)
    pattern = r'\|[^|]+\||\d+(?:/\d+)?\([^)]*\)|\{[^}]*\}|[^\s.\-:{}+]+'
    result = []
    for match in re.finditer(pattern, text):
        value = match.group()
        if value.startswith('{'): result.extend(atf_units(value[1:-1])); continue
        if re.match(r'^\d+(?:/\d+)?\(', value):
            number,reading=value.split('(',1); value='NUM:'+number+'('+norm_atf(reading)
        else: value=norm_atf(value)
        result.append(value)
    return result


class Lexicon:
    def __init__(self, path):
        self.rows = list(csv.DictReader(path.open(encoding='utf-8-sig'), delimiter='\t'))
        self.lookup = {norm_atf(r['form']).casefold():r for r in self.rows}
        self.entries=defaultdict(list)
        for r in self.rows: self.entries[norm_atf(r['form']).casefold()].append(r)
        self.review, self.vocab = Counter(), Counter()

    def tag(self, t, source):
        pos, form = t.get('pos'), t['form']
        self.vocab[(t.get('cf',''),t.get('gw',''),str(pos),form)] += 1
        if pos in POS_TAG: tag, basis = POS_TAG[pos], 'editor-pos'
        else:
            keys = [norm_atf(t.get('cf','')).casefold(),norm_atf(bare(form)).casefold()]
            gw=t.get('gw','')
            row=next((r for k in keys for r in self.entries.get(k,[]) if not gw or r['guide_word']==gw or not r['guide_word']),None)
            if row is None and not pos and re.match(r'^\d+(?:/\d+)?\(',bare(form)):
                row=self.lookup['@number']
            if row: tag, basis = row['tag'], 'lexicon'
            elif pos:
                rule=self.lookup.get('@pos:'+pos.casefold(),self.lookup['@pos:*'])
                tag, basis = rule['tag'], 'lexicon'
            else: tag, basis = 'NAME', 'default-name'
        if basis != 'editor-pos': self.review[(form,t.get('cf',''),t.get('gw',''),str(pos or ''),tag,basis,source)] += 1
        return tag, basis


def site_value(value):
    if not value or re.search(r'\?|uncertain|unknown|unidentified|unproven|not known|\bor\b|possibly|probably|perhaps', value, re.I):
        return None, 'provenience absent or explicitly uncertain'
    if re.search(r'\bArch\.',value): return None,'archive label does not establish an archaeological site'
    if '\ufffd' in value: return None,'source site spelling contains replacement characters'
    return re.sub(r'\s*\([^)]*\)', '', value).strip(), None


def object_kind(info, group):
    catalogue_type=info.get('object_type','').lower()
    meta=(catalogue_type+' '+info.get('subgenre','')).lower()
    support=group.get('support_type',group.get('type','')).lower()
    value=meta+' '+support
    if 'seal (not impression)' in meta or 'cylinder seal' in meta or 'stamp seal' in meta or ('object seal' in support and 'sealing' not in support):
        return ('stamp-seal' if 'stamp' in value else 'cylinder-seal' if 'cylinder' in value else 'seal-die'), 'seal'
    if 'envelope' in catalogue_type and 'tablet' not in catalogue_type: return 'sealed-envelope','sealing'
    if 'bulla' in catalogue_type: return 'bulla','sealing'
    if 'tablet' in catalogue_type and 'envelope' not in catalogue_type: return 'sealed-tablet','sealing'
    if 'envelope' in support: return 'sealed-envelope','sealing'
    if 'bulla' in support: return 'bulla','sealing'
    if 'tablet' in support: return 'sealed-tablet','sealing'
    if 'envelope' in value: return 'sealed-envelope','sealing'
    if 'bulla' in value: return 'bulla','sealing'
    if 'tablet' in value: return 'sealed-tablet','sealing'
    return 'clay-sealing','sealing'


def completeness(group):
    ts, events = group['tokens'], group['events']
    printed = [t['printed'] for t in ts]
    if not ts:
        return 'no-legend' if group.get('no_legend') else 'illegible'
    if not any(re.search(r'[A-Za-zšĝṣṭŠĜṢṬ]', bare(t['printed']).replace('x','')) for t in ts): return 'illegible'
    def damaged(t, side):
        text = t['printed'].strip()
        unit = t['units'][0 if side == 'first' else -1] if t['units'] else ''
        leaves=[n for n in flatten_gdl(t.get('gdl',[])) if n.get('v') or n.get('s') or n.get('n')=='n' or ('c' in n and n.get('form'))]
        edge=leaves[0 if side=='first' else -1] if leaves else {}
        pieces=re.findall(r'\|[^|]+\||\d+(?:/\d+)?\([^)]*\)|\{[^}]*\}|[^\s.\-:{}+]+',text)
        edge_text=pieces[0 if side=='first' else -1] if pieces else ''
        return unit.lower() in {'x','...','…'} or edge.get('break') in {'damaged','missing'} or '#' in edge_text or (text.startswith(('x','[','⸢','...','…')) if side == 'first' else text.endswith(('x',']','⸣','...','…')))
    if damaged(ts[0],'first') or damaged(ts[-1],'last'): return 'damaged-edge'
    if events and (events[0][0] == 'damage' or events[-1][0] == 'damage'): return 'damaged-edge'
    if any(re.search(r'(^|[- .{}])x($|[- .{}])|\.\.\.|…|#|⸢|⸣', p) for p in printed) or any(kind=='damage' for kind,_ in events) or any(n.get('break')=='damaged' for t in ts for n in flatten_gdl(t.get('gdl',[]))): return 'damaged-internal'
    if any('[' in p or '⸢' in p for p in printed) or any(n.get('break')=='missing' or n.get('supplied') for t in ts for n in flatten_gdl(t.get('gdl',[]))): return 'restored'
    return 'complete'


def language_assignment(ts, declared='', atf_language=None):
    langs = Counter(t.get('lang','unknown').split('-')[0].split('/')[0] for t in ts)
    known = Counter({k:v for k,v in langs.items() if k in {'sux','akk'}})
    if atf_language and atf_language not in {'sux','akk'}: return None,'editor',langs,'edition language outside target languages'
    if known:
        if known['sux'] == known['akk']: return None,'token-language',langs,'equal Sumerian and Akkadian word counts'
        return ('sux' if known['sux']>known['akk'] else 'akk'),'token-language',langs,None
    if atf_language in {'sux','akk'}: return atf_language,'editor',langs,None
    d = declared.lower()
    if ('sumerian' in d) != ('akkadian' in d): return ('sux' if 'sumerian' in d else 'akk'),'catalogue',langs,None
    return None,'catalogue',langs,'no decisive word language or single-language edition declaration'


def make_record(text, group, info, source, period, lexicon, locator, oracc=False, edition_language=None):
    ts = group['tokens']; lang,basis,langs,reason = language_assignment(ts, info.get('language',info.get('languages','')), edition_language)
    if not oracc and basis=='token-language': basis='editor'
    corpus = ('sux-ur3' if lang == 'sux' else 'cuneiform-ur3-akkadian') if period == 'Ur III' else ('sux-sargonic' if lang == 'sux' else 'akk-sargonic')
    if lang is None: corpus = 'cuneiform-language-unresolved'
    site, site_reason = site_value(info.get('provenience',''))
    kind, genre = object_kind(info,group)
    lines, line_labels, line_of_word = [], [], []
    for t in ts:
        label = t.get('line')
        if not line_labels or label != line_labels[-1]: line_labels.append(label); lines.append([])
        lines[-1].append(t['form']); line_of_word.append(len(lines)-1)
    words = [t['form'] for t in ts]
    tags, bases = [], []
    for t in ts:
        tag, tag_basis = lexicon.tag(t,source); tags.append([tag]); bases.append([tag_basis])
    aliases = [text]
    for key, prefix in [('museum_no','museum:'),('designation','designation:'),('accession_no','accession:'),('external_id','external:')]:
        if info.get(key): aliases.append(prefix + info[key])
    seal_ids = re.findall(r'S\d{6}(?:\.\d+)?', info.get('seal_id',''))
    die = seal_ids[0] if len(set(seal_ids)) == 1 else None
    mixed = langs.get('sux',0)>0 and langs.get('akk',0)>0
    row = dict(record_id=f"{corpus}:{source}:{text}:{group['key']}", corpus=corpus, source=source,
        source_locator=locator, object_id=text, object_kind=kind, genre=genre, die_id=die,
        aliases=sorted(set(aliases)), site=site, site_as_printed=info.get('provenience',''),
        site_unknown_reason=site_reason, period=period, date_as_printed=info.get('date_of_origin') or info.get('period',period),
        language='mixed' if mixed else {'sux':'Sumerian','akk':'Akkadian'}.get(lang,edition_language or 'undetermined'),
        majority_language={'sux':'Sumerian','akk':'Akkadian'}.get(lang), mixed_language=mixed,
        language_basis=basis, token_language_counts=dict(langs), language_unresolved_reason=reason,
        source_word_languages=[t.get('lang') for t in ts],
        script='cuneiform', rights='explicit-license' if oracc else 'rights-unverified',
        legend_as_printed='\n'.join(' '.join(t['printed'] for t in ts if t.get('line')==label) for label in line_labels),
        lines=lines, line_labels=line_labels, line_division_basis='atf' if any(x is not None for x in line_labels) else 'none',
        words=words, members=[[w] for w in words], units=[u for t in ts for u in t['units']],
        word_units=[t['units'] for t in ts], line_of_word=line_of_word, tags=tags, tag_source=bases,
        gloss=[[t.get('gw') or None] for t in ts], gold=[t.get('pos') for t in ts],
        source_word_refs=[t.get('ref') for t in ts], completeness=completeness(group),
        reading_doubtful=any('?' in t['printed'] or any(n.get('queried') for n in flatten_gdl(t.get('gdl',[]))) for t in ts),
        text_genre=info.get('genres',info.get('genre','')), transcription=dict(method='digital-edition',by=AUTHOR),
        source_object_type=info.get('object_type',''), source_language=info.get('language',''),
        source_seal_id=info.get('seal_id',''), edition_notes=group.get('notes',[]))
    for key in ('material','museum_no','collection','primary_publication','publication_history','excavation_no','stratigraphic_level','findspot_square','findspot_remarks','height','width','thickness','seal_information','period_remarks','date_remarks'):
        if info.get(key): row[key] = info[key]
    if group.get('edition_status'): row['edition_status']=group['edition_status']
    if 'composite' in group.get('type','').lower() or any('@object composite' in n.lower() for n in group.get('notes',[])):
        row['object_identity_status']='unresolved-composite-edition'
        row['object_identity_reason']='catalogue labels a seal, but the edition labels a composite; physical identity requires review'
    if group.get('translations'): row['translation_as_printed']='\n'.join(group['translations'])
    if info.get('stratigraphic_level'): row['stratum_or_level']=info['stratigraphic_level']
    dims={k:info[k] for k in ('height','width','thickness') if info.get(k)}
    if dims: row['dimensions_as_printed']=dims
    if info.get('museum_no') or info.get('collection'): row['museum']={k:info[k] for k in ('museum_no','collection') if info.get(k)}
    return row


def flatten_gdl(nodes):
    for node in nodes:
        yield node
        for key in ('seq','group'):
            yield from flatten_gdl(node.get(key,[]))


def read_catalogue(path):
    wanted, all_rows = {}, {}
    with path.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            identity = 'P' + row['id_text'].zfill(6)
            if row['period'].startswith('Old Akkadian'): wanted[identity] = row
            # Ur III metadata supplements are looked up by P-number only.
            if row.get('seal_id') or row.get('object_type') in {'tablet','bulla','seal (not impression)'}: all_rows[identity] = row
    return wanted, all_rows


def read_blocks(path):
    identity, lines, start = None, [], 0
    with path.open(encoding='utf-8-sig') as f:
        for number,line in enumerate(f,1):
            if line.startswith('&'):
                if identity: yield identity,lines,start
                identity,lines,start = line[1:8],[line.rstrip('\r\n')],number
            else: lines.append(line.rstrip('\r\n'))
    if identity: yield identity,lines,start


def cdli_groups(identity, lines, info):
    groups, current, edition_lang, serial, current_lang = [], None, None, 0, 'unknown'
    section, surface, column, support = '', '', '', info.get('object_type','')
    physical = info.get('object_type','') == 'seal (not impression)'
    def create(key, kind):
        g = dict(key=key,type=kind,support_type=support,tokens=[],events=[],notes=[],translations=[]); groups.append(g); return g
    if physical: current = create('physical-seal','object seal')
    for offset,line in enumerate(lines):
        stripped = line.strip()
        lang_match = re.match(r'#atf:\s*lang\s+(\w+)',stripped)
        if lang_match: edition_lang = current_lang = lang_match[1]
        if stripped.startswith('@seal'):
            serial += 1; section=stripped[1:]; surface=column=''; current = create(f'seal-{serial}', 'impression'); continue
        if stripped.startswith('@object'):
            support=stripped[len('@object'):].strip()
            if not physical: current = None
            elif current is not None: current['notes'].append(stripped)
            continue
        if stripped.startswith(('@obverse','@reverse','@edge','@envelope')) and not physical:
            current = None; continue
        if stripped in {'@tablet','@bulla','@envelope'}: support=stripped[1:]
        if current is None: continue
        if stripped.startswith('#tr.en:'):
            current['translations'].append(stripped.partition(':')[2].lstrip()); continue
        if stripped.startswith('@surface'): surface=stripped[1:]; column=''
        if stripped.startswith('@column'): column=stripped[1:]
        if stripped.startswith('@'): current['notes'].append(stripped)
        if stripped.startswith('$'):
            if 'no linguistic content' in stripped: current['no_legend'] = True
            elif re.search(r'broken|missing|illegible|effaced|traces',stripped,re.I): current['events'].append(('damage',stripped))
            current['notes'].append(stripped); continue
        match = re.match(r"^(\d+['a-zA-Z]*|[a-z])\.\s*(.*)$",stripped)
        if not match: continue
        label, body = match.groups()
        body = re.sub(r'\(\$.*?\$\)', '',body)
        for index,form in enumerate(body.split()):
            if form in {'+','-','=','|','%sux','%akk','%s','%a'}:
                if form.startswith('%'): current_lang = {'%sux':'sux','%s':'sux','%akk':'akk','%a':'akk'}[form]
                continue
            t = dict(form=form,printed=form,units=atf_units(form),pos=None,lang=current_lang,
                cf='',gw='',ref=f'{identity}:{offset+1}:{index+1}',line=' '.join(x for x in (section,surface,column,label) if x)+f' [ATF {offset+1}]',dirty=not clean(form))
            current['tokens'].append(t); current['events'].append(('word',t))
    return groups,edition_lang


def validate(rows):
    ids = set()
    required = {'record_id','corpus','source','source_locator','object_id','object_kind','genre','aliases','site','language','language_basis','script','rights','legend_as_printed','lines','line_division_basis','words','members','units','word_units','line_of_word','tags','tag_source','completeness','reading_doubtful','transcription'}
    for r in rows:
        assert required <= r.keys(), r['record_id']
        assert r['record_id'] not in ids; ids.add(r['record_id'])
        assert r['units'] == [u for w in r['word_units'] for u in w]
        n = len(r['words'])
        assert n == len(r['word_units']) == len(r['line_of_word']) == len(r['members']) == len(r['tags']) == len(r['tag_source']) == len(r['gold'])
        assert r['words'] == [w for line in r['lines'] for w in line]
        assert all(0<=x<len(r['lines']) for x in r['line_of_word'])
        assert all(len(m)==len(t)==len(s) for m,t,s in zip(r['members'],r['tags'],r['tag_source']))
        assert r['site'] is not None or r['site_unknown_reason']
    return dict(records=len(rows), failures=0)


def corpus_counts(rows):
    seq = {tuple(r['units']) for r in rows}
    sources = Counter(s for r in rows for ss in r['tag_source'] for s in ss)
    by_site = Counter(r['site'] for r in rows if r['site'] is not None)
    top = by_site.most_common(15)
    result = dict(records=len(rows), distinct_objects=len({r['object_id'] for r in rows}),
        distinct_sign_unit_sequences=len(seq), distinct_sequences_at_least_two_signs=sum(len(s)>=2 for s in seq),
        distinct_sequences_at_least_two_words=len({tuple(r['units']) for r in rows if len(r['words'])>=2}),
        distinct_word_sequences_at_least_two_words=len({tuple(r['words']) for r in rows if len(r['words'])>=2}),
        distinct_sign_sequences_with_at_least_two_words=len({tuple(r['units']) for r in rows if len(r['words'])>=2}),
        records_site_null=sum(r['site'] is None for r in rows), records_with_die_id=sum(r['die_id'] is not None for r in rows),
        records_with_line_divisions=sum(r['line_division_basis']!='none' for r in rows),
        sites_top_15=dict(top), sites_other=sum(by_site.values())-sum(n for _,n in top),
        members_by_tag_source=dict(sources), share_members_editor_pos=sources['editor-pos']/sum(sources.values()) if sources else None,
        mixed_language_records=sum(r['mixed_language'] for r in rows),
        field_coverage={k:sum(r.get(k) is not None and r.get(k) not in ('',[]) for r in rows) for k in sorted({k for r in rows for k in r})})
    for key in ('genre','object_kind','language_basis','completeness','source'):
        result['records_by_'+key] = dict(Counter(r[key] for r in rows))
    result['records_by_tag_source'] = dict(Counter(s for r in rows for s in {v for xs in r['tag_source'] for v in xs}))
    return result


def main():
    start = time.monotonic()
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('ur3-archive','ur3-manifest','held-records','cdli-cat','cdli-atf','lexicon','output-dir','scratch-dir','counts'):
        ap.add_argument('--'+name,required=True,type=Path)
    ap.add_argument('--oakk-archive',type=Path)
    ap.add_argument('--acquisition-record',type=Path,action='append',default=[])
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True); a.scratch_dir.mkdir(parents=True,exist_ok=False)
    expected = json.loads(a.ur3_manifest.read_text(encoding='utf-8'))['source_hashes']['sumerian-ur3-v1.json']
    actual = digest(a.ur3_archive)
    assert actual == expected, 'held archive hash mismatch'
    acquisitions = []
    for p in a.acquisition_record:
        rec = json.loads(p.read_text(encoding='utf-8'))
        assert Path(rec['local_path']).stat().st_size == rec['bytes']
        assert digest(rec['local_path']) == rec['sha256']
        if Path(rec['local_path']).stat().st_size < 1000:
            assert not Path(rec['local_path']).read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1')
        acquisitions.append(dict(source_id=rec['source_id'],bytes=rec['bytes'],sha256=rec['sha256'],matches=True))
    lex = Lexicon(a.lexicon)
    old_akkadian, all_cdli = read_catalogue(a.cdli_cat)
    rows, legacy, census, errors = [], {}, {}, []
    oracc_oakk_ids, oracc_seal_ids = set(), set()
    for path,source,period in [(a.ur3_archive,'sumerian-ur3-v1','Ur III'),(a.oakk_archive,'oracc-oakk','Old Akkadian')]:
        if path is None:
            census[source] = dict(available=False,reason='archive unavailable after validated TLS acquisition failures'); continue
        archive = safe_archive(path)
        catalogue_name = next(n for n in archive.namelist() if n.endswith('/catalogue.json'))
        cat = json.loads(archive.read(catalogue_name))
        dump(a.scratch_dir/(source+'-catalogue.json'),cat)
        names = [n for n in archive.namelist() if '/corpusjson/' in n and n.endswith('.json')]
        sample = set(sorted(names,key=lambda n:hashlib.sha256(f'20261012:{Path(n).stem}'.encode()).hexdigest())[:3000])
        license_counts, counts = Counter(), Counter()
        for index,name in enumerate(names):
            try: data = json.loads(archive.read(name))
            except json.JSONDecodeError:
                errors.append(dict(source=source,entry=name,reason='invalid JSON')); counts['invalid_json']+=1; continue
            if 'textid' not in data:
                errors.append(dict(source=source,entry=name,reason='missing textid')); counts['missing_textid']+=1; continue
            license_counts[data.get('license','unverified')]+=1
            text=data['textid']; info=dict(cat['members'].get(text,{}))
            supplement=all_cdli.get(text,{})
            for k,v in supplement.items():
                if not info.get(k): info[k]=v
            if source=='oracc-oakk': oracc_oakk_ids.add(text)
            if source=='sumerian-ur3-v1' and name in sample:
                # The reproduction projection uses only original catalogue metadata.
                for old in legacy_seals(data,cat['members'].get(text,{}),source): legacy[old['id']]=old
            groups=oracc_groups(data,info)
            for group in groups:
                locator=dict(oracc_text=text,cdli_artifact=text,entry=name,seal_section=group['key'])
                row=make_record(text,group,info,source,period,lex,locator,oracc=True)
                row['source_url']=f"https://oracc.museum.upenn.edu/{data['project']}/{text}"
                if text in supplement: row['aliases'].extend(['cdli:'+text])
                rows.append(row)
                if source=='oracc-oakk': oracc_seal_ids.add(text)
            counts['seal_groups']+=len(groups); counts['entries_parsed']+=1
            if index and index%10000==0: print(json.dumps(dict(source=source,entries=index,seal_records=counts['seal_groups'])),flush=True)
        census[source]=dict(available=True,archive_entries=len(names),counts=dict(counts),embedded_licenses=dict(license_counts),catalogue_license=cat.get('license'))
        archive.close()
    held={}
    with a.held_records.open(encoding='utf-8') as f:
        for line in f:
            # Filter the permitted source before parsing any other corpus payload.
            if '"source": "sumerian-ur3-v1"' not in line or '"kind": "seal"' not in line: continue
            old=json.loads(line)
            if old['source']=='sumerian-ur3-v1' and old['kind']=='seal': held[old['id']]=old
    differences=[]
    for key,old in held.items():
        new=legacy.get(key)
        if new!=old: differences.append(dict(id=key,fields=[k for k in old if new is None or old[k]!=new.get(k)],reason='missing' if new is None else 'field mismatch'))
    extra=set(legacy)-set(held)
    reproduction=dict(held_records=len(held),reconstructed_records=len(legacy),records_matched_exactly=len(held)-len(differences),records_differing=len(differences),extra_records=len(extra),
        held_distinct_sequences_at_least_two_signs=len({tuple(r['units']) for r in held.values() if len(r['units'])>=2}),
        comparison='all original fields before schema extension; raw POS is separately retained in new gold',new_records_retaining_held_units=sum(any(r['object_id']==old['document'] and r['source_word_refs']==old['source_word_refs'] and r['units']==old['units'] and r['words']==old['words'] for r in rows) for old in held.values()))
    dump(a.scratch_dir/'reproduction.json',dict(summary=reproduction,differences=differences,extra_ids=sorted(extra)))
    seen, cdli_counts, alternates = set(), Counter(), []
    for text,lines,start_line in read_blocks(a.cdli_atf):
        if text not in old_akkadian: continue
        info=old_akkadian[text]; seen.add(text)
        groups,edition_language=cdli_groups(text,lines,info)
        for group in groups:
            if text in oracc_seal_ids:
                cdli_counts['sections_superseded_by_oracc']+=1
                alternates.append(dict(object_id=text,source='cdli-data',source_locator=dict(atf_file_line=start_line,entry=group['key']),metadata=info,group=group,reason='ORACC edition preferred for shared P-number'))
                for r in rows:
                    if r['source']=='oracc-oakk' and r['object_id']==text:
                        r.setdefault('cdli_alias_sections',[]).append(group['key'])
                continue
            locator=dict(cdli_artifact=text,entry=group['key'],atf_file_line=start_line)
            row=make_record(text,group,info,'cdli-data','Old Akkadian',lex,locator,edition_language=edition_language)
            row['source_url']='https://cdli.earth/artifacts/'+text[1:]
            if text in oracc_oakk_ids: row['edition_notes'].append('ORACC text supplied no seal section; CDLI seal section retained')
            row['atf_edition_language']=edition_language
            rows.append(row); cdli_counts['records']+=1
    for text,info in old_akkadian.items():
        if text not in seen and text not in oracc_seal_ids and info['object_type']=='seal (not impression)':
            group=dict(key='physical-seal-no-atf',type='object seal',tokens=[],events=[],notes=['No ATF block in the pinned dump'])
            row=make_record(text,group,info,'cdli-data','Old Akkadian',lex,dict(cdli_artifact=text,entry='catalogue-only'))
            row['edition_status']='missing-atf'; rows.append(row); cdli_counts['catalogue_only_seals']+=1
    census['cdli-data']=dict(old_akkadian_catalogue_objects=len(old_akkadian),objects_with_atf=len(seen),counts=dict(cdli_counts))
    validation=validate(rows)
    for corpus in CORPORA:
        jsonl(a.output_dir/(corpus+'.jsonl'),[r for r in rows if r['corpus']==corpus])
    for corpus in ('cuneiform-ur3-akkadian','cuneiform-language-unresolved'):
        jsonl(a.output_dir/(corpus+'.jsonl'),[r for r in rows if r['corpus']==corpus])
    jsonl(a.output_dir/'cuneiform-site-unknown.jsonl',[r for r in rows if r['site'] is None])
    jsonl(a.output_dir/'cuneiform-source-errors.jsonl',errors)
    jsonl(a.output_dir/'cuneiform-edition-alternates.jsonl',alternates)
    jsonl(a.output_dir/'cuneiform-mixed-language.jsonl',[r for r in rows if r['mixed_language'] or r['language_unresolved_reason']])
    with (a.output_dir/'cuneiform-tag-review.tsv').open('x',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,delimiter='\t'); writer.writerow(['form','citation_form','guide_word','pos','tag','tag_source','source','count'])
        for key,n in sorted(lex.review.items()): writer.writerow([*key,n])
    with (a.output_dir/'cuneiform-vocabulary.tsv').open('x',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,delimiter='\t'); writer.writerow(['citation_form','guide_word','pos','form','count'])
        for key,n in sorted(lex.vocab.items()): writer.writerow([*key,n])
    rng=random.Random('b-check')
    samples=[]
    for corpus in CORPORA:
        selected=[r for r in rows if r['corpus']==corpus]
        for r in rng.sample(selected,min(10,len(selected))): samples.append(dict(record=r,check_status='pending manual comparison against archived digital edition'))
    jsonl(a.output_dir/'cuneiform-hand-check-sample.jsonl',samples)
    summary=dict(authors=[dict(agent='Codex',model='GPT-6 family; exact model identifier not exposed',harness='Codex API tool harness')],
        corpus_coverage_complete=a.oakk_archive is not None,held_archive=dict(bytes=a.ur3_archive.stat().st_size,sha256=actual,matches_manifest=True),
        acquisitions=acquisitions,corpora={c:corpus_counts([r for r in rows if r['corpus']==c]) for c in CORPORA},
        outside_corpora={c:corpus_counts([r for r in rows if r['corpus']==c]) for c in ('cuneiform-ur3-akkadian','cuneiform-language-unresolved')},
        census=census,reproduction=reproduction,validation=validation,normalization_seconds=round(time.monotonic()-start,3))
    dump(a.counts,summary)
    dump(a.scratch_dir/'run.json',dict(arguments={k:str(v) for k,v in vars(a).items()},code_sha256=digest(__file__),lexicon_sha256=digest(a.lexicon),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=summary))
    print(json.dumps(dict(corpora={c:summary['corpora'][c]['records'] for c in CORPORA},reproduction=reproduction,seconds=summary['normalization_seconds'])),flush=True)


if __name__=='__main__': main()
