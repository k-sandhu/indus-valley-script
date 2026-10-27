"""Complete local extraction with explicit cross-dictionary boundary assistance."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-lexical-extraction-extension')
sys.path.insert(0, str(ROOT/'experiments/2026-10-22-lexical-source-review/code'))
import source_guard as guard
w = guard.winslow
BASE_PARSE = w.parse_page
WRAW = ROOT/'data/raw/2026-10-22-rebus-winslow/sources-v1/winslow'
TLRAW = ROOT/'data/raw/2026-10-21-rebus-base-rate/sources-v1/tamil-lex'
OLD = ROOT/'data/raw/2026-10-22-rebus-winslow/derived-v1/winslow-entries.jsonl'
TL = ROOT/'data/raw/2026-10-21-rebus-base-rate/derived-v1/tamil-lex-entries.jsonl'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def rows(p):
    with p.open(encoding='utf8') as f:
        return [json.loads(x) for x in f]

def identifier(r):
    # Identity deliberately excludes derived member decisions.
    return hashlib.sha256(json.dumps([r.get(k) for k in
        ('page','kind','head','translit_plain','root','gloss')],ensure_ascii=False).encode()).hexdigest()

def reviewed_page(text, page):
    ps, ss = [], []
    for block in w.DIV_RE.findall(text):
        if '<hw>' not in block:
            continue
        p, s = BASE_PARSE('<div>'+block+'</div>', page)
        if len(p) != 1:
            raise ValueError('Principal block identity failed')
        parent = p[0]
        parent['grammatical'] = guard.grammatical(parent['gloss'],parent['pos_source'])
        ps.append(parent)
        for child in s:
            child.update(root_grammatical=parent['grammatical'],
                parent_asterisk=parent['asterisk'], parent_foreign_mark=parent['foreign_mark'],
                parent_origin_mark_present=parent['star'])
            ss.append(child)
    return ps, ss

def source_boundaries(records):
    index = defaultdict(list)
    for r in records:
        index[unicodedata.normalize('NFC',r['head'])].append(r)
    return index

def boundary_decision(r, index):
    """Exact-script matching; homographs with incompatible segmentation block use."""
    matches = index.get(unicodedata.normalize('NFC',r['head']),[])
    compatible = [t for t in matches if w.key(re.sub(r'[-\s]+','',t['translit'])) == w.key(r['translit_plain'])]
    analyses = {tuple(t['members']) for t in compatible}
    if not compatible:
        return 'no_exact_cross_source_boundary', None, []
    if len(analyses) != 1:
        return 'conflicting_cross_source_boundaries', None, compatible
    pair = next(iter(analyses))
    if len(pair) != 2:
        return 'cross_source_outside_two_member_scope', None, compatible
    return 'lexicon_assisted_boundary', list(pair), compatible

def increment_forms(root):
    if len(root) < 3 or not root.endswith('u'):
        return []
    return [root[:-1]+ending for ending in ('am','aṅ','añ','an')]

_NOUN_CACHE = {}

def increment_candidates(form, roots, noun_forms):
    """Return every supported surface candidate; never select it as a compound."""
    cache_key=id(noun_forms)
    if cache_key not in _NOUN_CACHE:
        by_key,by_increment = defaultdict(set),defaultdict(set)
        for word in noun_forms:
            by_key[w.key(word)].add(word)
            for surface in increment_forms(word):by_increment[surface].add(word)
        _NOUN_CACHE[cache_key]=(noun_forms,by_key,by_increment)
    _,by_key,by_increment=_NOUN_CACHE[cache_key]
    candidates = set()
    for root in roots:
        if root not in noun_forms:
            continue
        for surface in increment_forms(root):
            if w.key(form).startswith(w.key(surface)):
                rest = form[len(surface):]
                # Nasal assimilation is restricted to its matching stop.
                nasal_stop = {'ṅ':'k','ñ':'c','n':'t','m':'p'}
                if not rest or rest[0] != nasal_stop[surface[-1]]:
                    continue
                for lemma in by_key.get(w.key(rest),[]):
                    candidates.add((surface, rest, root, lemma))
        if w.key(form).endswith(w.key(root)) and len(form)>len(root):
            prefix=form[:-len(root)]
            for lemma in by_increment.get(prefix,[]):
                nasal_stop={'ṅ':'k','ñ':'c','n':'t','m':'p'}
                if root[0] == nasal_stop[prefix[-1]]:
                    candidates.add((prefix,form[-len(root):],lemma,root))
    return [dict(surface_members=list(c[:2]),lemma_candidates=list(c[2:]),
                 status='unresolved_increment_morphology',scorer_eligible=False)
            for c in sorted(candidates)]

def pins():
    paths=[PKG/'PROTOCOL.md',Path(__file__),Path(guard.__file__),Path(w.__file__),
           Path(w.parse_tamil_lex.__file__),Path(w.rebus.__file__),OLD,TL]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}

def freeze():
    progress=RAW/'freeze-pages-v1.jsonl'
    manifests=rows(progress) if progress.exists() else []
    completed={r['logical_path'] for r in manifests}
    for directory in (WRAW,TLRAW):
        for p in sorted(directory.glob('page-*.html')):
            logical=p.relative_to(ROOT).as_posix()
            if logical in completed:continue
            print('hashing '+logical,flush=True)
            record=dict(logical_path=logical,
                physical_path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
            with progress.open('a',encoding='utf8') as f:f.write(json.dumps(record)+'\n')
            manifests.append(record)
    dump(PKG/'FREEZE-v1.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        pins=pins(),pages=manifests,prior_exposure='Known dictionary and reviewed regressions; source work only'))

def run():
    freeze=json.loads((PKG/'FREEZE-v1.json').read_text(encoding='utf8'))
    assert pins()==freeze['pins'], 'Pinned code or input changed'
    for p in freeze['pages']:
        assert sha(ROOT/p['logical_path'])==p['sha256'], 'Source page changed'
    pages=[(int(p.stem.split('-')[1]),p.read_text(encoding='utf8')) for p in sorted(WRAW.glob('page-*.html'))]
    principals,subs=[],[]
    for page,text in pages:
        p,s=reviewed_page(text,page);principals+=p;subs+=s
    original=w.parse_page
    w.parse_page=reviewed_page
    try:
        records=w.build(pages)
    finally:
        w.parse_page=original
    # Build's stable principal-then-subentry order is asserted against source rows.
    parents=[(p,tam,rom) for p in principals for tam,rom in p['forms']]
    children=[(s,tam,w.translit(tam)) for s in subs for tam in s['heads']]
    metadata=parents+children
    assert len(records)==len(metadata)
    tlindex=source_boundaries(rows(TL))
    nouns={rom for p in principals if p['pos']=='n' and not p['grammatical'] for _,rom in p['forms']}
    prior=rows(OLD)
    assert [identifier(r) for r in records]==[identifier(r) for r in prior]
    changes=[]
    for r,old,(source,tam,rom) in zip(records,prior,metadata):
        assert r['head']==tam and r['translit_plain']==rom
        r['entry_id']=identifier(r)
        r['original_members']=old['members']
        r['winslow_guarded_members']=r['members'][:]
        r['source']=dict(logical_path=f'data/raw/2026-10-22-rebus-winslow/sources-v1/winslow/page-{r["page"]:05d}.html',
            sha256=sha(WRAW/f'page-{r["page"]:05d}.html'))
        for k in ('parent_asterisk','parent_foreign_mark','parent_origin_mark_present'):
            r[k]=source.get(k)
        r['whole_entry_loan_status']='unresolved_requires_sense_review'
        r['comparative_scorer_eligible']=False
        blocked=r.get('root_grammatical',r.get('grammatical',False))
        status,pair,refs=boundary_decision(r,tlindex)
        r['boundary_review_status']=status
        r['lexicon_boundary_sources']=[dict(page=t['page'],hom=t['hom'],translit=t['translit'],
            members=t['members'],source_sha256=sha(TLRAW/f'page-{t["page"]:05d}.html'),
            roman_alignment_uses_e_or_o_length_convention=(re.sub(r'[-\s]+','',t['translit'])!=r['translit_plain'])) for t in refs]
        r['roman_alignment_scope']='Exact Tamil headword source alignment only; no lexical substitution'
        if blocked:
            r['members']=[];r['boundary_review_status']='grammatical_root_or_entry_blocked'
        elif pair:
            r['members']=pair;r['seg']='lexicon_assisted'
        elif status=='conflicting_cross_source_boundaries':
            r['members']=[];r['seg']=None
        roots=[rom] if r['kind']=='principal' else [x[1] for x in source['root_forms']]
        r['increment_candidates']=[] if blocked else increment_candidates(rom,roots,nouns)
        r['increment_candidate_status']=('unique_unresolved' if len(r['increment_candidates'])==1 else
            'ambiguous_unresolved' if r['increment_candidates'] else 'none')
        if r['members']!=old['members']:
            changes.append(dict(entry_id=r['entry_id'],page=r['page'],head=r['head'],
                before=old['members'],after=r['members'],status=r['boundary_review_status']))
    out=RAW/'run-v1'
    with (out/'winslow-entries.jsonl').open('x',encoding='utf8') as f:
        for r in records:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    dump(out/'member-deltas.json',changes)
    result=dict(records=len(records),prior_records=len(prior),pages=len(pages),
        prior_two_member=sum(len(r['members'])==2 for r in prior),
        revised_two_member=sum(len(r['members'])==2 for r in records),
        member_changes=len(changes),added_two_member=sum(len(x['before'])!=2 and len(x['after'])==2 for x in changes),
        removed_two_member=sum(len(x['before'])==2 and len(x['after'])!=2 for x in changes),
        changed_two_member=sum(len(x['before'])==len(x['after'])==2 for x in changes),
        boundary_status=dict(Counter(r['boundary_review_status'] for r in records)),
        increment_status=dict(Counter(r['increment_candidate_status'] for r in records)),
        parent_marked_subentries=sum(bool(r['parent_origin_mark_present']) for r in records),
        lexicon_assisted_rows_using_e_or_o_length_alignment=sum(r['boundary_review_status']=='lexicon_assisted_boundary' and
            any(t['roman_alignment_uses_e_or_o_length_convention'] for t in r['lexicon_boundary_sources']) for r in records),
        scorer_eligible=sum(r['comparative_scorer_eligible'] for r in records),
        output_sha256=sha(out/'winslow-entries.jsonl'),delta_sha256=sha(out/'member-deltas.json'),
        provenance='Complete Winslow rows; Lexicon-assisted boundaries explicitly dependent; increments unresolved')
    dump(PKG/'results-v1.json',result)
    print(json.dumps(result))

if __name__=='__main__':
    {'freeze':freeze,'run':run}[sys.argv[1]]()
