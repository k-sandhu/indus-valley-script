"""Small integrity checks added for the second-review polish; no acquisition."""
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SKIP_KEYS = {'id','sha256','witness_sha256','url','witness_path','acquisition_log','path','final_url',
             'source_id','old_source_id','replacement_source_id','source_ids','repository_links','extraction_path'}

def strings(value, key=''):
    if isinstance(value, dict):
        for k,v in value.items():
            yield from strings(v,k)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v,key)
    elif isinstance(value,str) and key not in SKIP_KEYS:
        yield value

def fused_tokens(text):
    text = re.sub(r'https?://\S+','',text)
    text = re.sub(r'\]\([^)]*\)',']',text)
    text = re.sub(r'`[^`]*`','',text)
    return re.findall(r'\b[A-Za-z]*[a-z]{2,}\d[\d.,\-]*[A-Za-z%]*',text) + re.findall(r'\d(?!(?:st|nd|rd|th)\b)[A-Za-z]{2,}\b',text)

class BodyText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[]
    def handle_data(self,data):
        self.parts.append(data)

def check(coded):
    rows=coded['recommendations']
    all_rows={r['id']:r for r in rows+coded['positions']}
    all_rows['F55']=next(x for x in coded['coverage'] if x.get('legacy_row_id')=='F55')
    counts=Counter()
    by_source=Counter()
    for i in range(1,60):
        rid=f'F{i:02d}'
        row=all_rows[rid]
        anchor=row['anchor']
        assert 0<len(anchor['text'].split())<15, rid
        p=ROOT/anchor['witness_path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==anchor['sha256'], rid
        selector=anchor['selector']
        if selector=='visual':
            assert p.suffix=='.png'
            counts['visually_read_images']+=1
        else:
            data=p.read_text(encoding='utf-8')
            if isinstance(selector,int):
                data=next(x['text'] for x in json.loads(data) if x['pdf_page']==selector)
            elif selector=='html':
                parser=BodyText();parser.feed(data);data=' '.join(parser.parts)
            elif selector.startswith('F'):
                data=next(x['text'] for x in json.loads(data)['rows'] if x['id']==selector)
            elif p.suffix=='.json':
                data=json.loads(data)
                assert isinstance(data,str)
            norm=lambda s:' '.join(s.split())
            assert norm(anchor['text']) in norm(data), f'Anchor not in selected text: {rid}: {anchor["text"]}'
            counts['exact_text_matches']+=1
        counts['anchors']+=1
        by_source[row['source_id']]+=len(anchor['text'].split())
    assert max(by_source.values())<=25, by_source
    for action in coded['action_ranking']['actions']:
        assert action['score']==2*action['availability']+action['autonomy']+action['reuse']
        for rid in action['recommendation_ids']:
            r=next(r for r in rows if r['id']==rid)
            assert not r['testable_with_existing_data'].startswith('Limited'),rid
    for r in rows:
        assert r['shared_or_disputed'] and r['n_independent_sources']==len(r['independent_author_groups'])
        assert all(c['source_id']!=r['source_id'] for c in r['comparisons']),r['id']
    report=(HERE/'REPORT.md').read_text(encoding='utf-8')
    section=report.split('## Recommendations by theme\n',1)[1].split('## Ranked work with current data\n',1)[0]
    mentions={r['id']:set() for r in rows}
    for block in re.split(r'(?m)^### ',section)[1:]:
        heading,body=block.split('\n',1)
        for match in re.finditer(r'\bF(\d{2})(?:-F(\d{2}))?\b',body):
            start=int(match[1]);end=int(match[2]) if match[2] else start
            for i in range(start,end+1):
                rid=f'F{i:02d}'
                if rid in mentions:
                    mentions[rid].add(heading.lower())
    for r in rows:
        assert r['theme'] in mentions[r['id']], f'Missing own-theme report discussion: {r["id"]}'
    # F41 is cross-referenced as the input requirement for mobility modelling.
    cross_refs={rid:sorted(themes-{next(r['theme'] for r in rows if r['id']==rid)})
                for rid,themes in mentions.items() if len(themes)>1}
    assert set(cross_refs)<={'F41'},cross_refs
    return dict(counts,largest_total_anchor_words_per_source=max(by_source.values()),
                ranking_actions_checked=len(coded['action_ranking']['actions']),
                recommendation_author_group_counts_checked=len(rows),
                report_rows_in_own_theme=len(rows),explicit_cross_theme_input_references=cross_refs)

def check_file(path,text):
    if path.suffix=='.json':
        candidates=list(strings(json.loads(text)))
    elif path.suffix=='.md':
        candidates=[text]
    else:
        return
    bad=[token for s in candidates for token in fused_tokens(s)]
    assert not bad, f'Fused prose or locator tokens: {path.name}: {bad[:10]}'

def preserved_reviews():
    records=json.loads((HERE/'review-preservation.json').read_text(encoding='utf-8'))
    for row in records:
        assert hashlib.sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    return len(records)
