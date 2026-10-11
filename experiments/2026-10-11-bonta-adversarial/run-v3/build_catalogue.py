"""Build an attributed, bounded public catalogue from the frozen diagnostics.

The full corpus, MW definition index and unlicensed font remain local inputs.
Public examples contain at most three consecutive codes, chosen to illustrate
the reviewed candidates. The viewer embeds data and also works without a server.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, importlib.util, sys
from hypotheses import PROPOSALS, SENSES

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CORE = HERE / 'run-v2'
OLD = ROOT / 'experiments/2026-10-08-bonta-extension'
sys.path.insert(0, str(OLD))
spec = importlib.util.spec_from_file_location('old_analysis', OLD / 'analyze.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='run-v3')
    args = parser.parse_args()
    out = HERE / args.run
    if out.exists(): raise SystemExit('Preserve existing catalogue runs; choose another --run.')
    prior = read(OLD / 'run-2026-10-09-v5/candidates.json')['rows']
    before = {r['code']: r for r in prior}
    positions = {r['code']: r for r in read(CORE/'position-audit.json')['rows']}
    robust = {r['code']: r for r in read(CORE/'robustness.json')['selected']}
    substitutes = {r['code']: r for r in read(CORE/'substitution-audit.json')['rows']}
    graphic = {r['code']: r for r in read(CORE/'graphic-sensitivity.json')['rows']}
    lexical = {r['code']: r for r in read(CORE/'lexical-adversarial.json')['rows']}
    clean = [json.loads(x) for x in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    by_record = {r['record_id']:r for r in clean}
    dictionary = read(ROOT/'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json')
    senses = {}
    for word, (entry, page, meaning, period) in SENSES.items():
        key = old.slp('atibhāra' if word=='ati' else word)
        matches = [x for x in dictionary.get(key, []) if x['entry_id']==entry]
        assert len(matches)==1, (word, entry)
        assert matches[0]['page_column']==page, (word, page, matches[0])
        senses[word] = dict(word=word, slp1=old.slp(word), comparison_headword='atibhāra' if word=='ati' else word,
            meaning=meaning, entry_id=entry, page_column=page, period=period,
            url='https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc2/index.php',
            source='Monier-Williams 1899, Cologne digital edition, pinned csl-orig 55e8addbd96e8d9001b8789026b026763f4049c1')
    reviewed = {c: p for p in PROPOSALS for c in p['codes']}
    examples = []
    for p in PROPOSALS:
        for record in p['preferred_examples']:
            r = by_record[record]
            seq = r['signs_reading_rtl']
            matching = [i for i,c in enumerate(seq) if c in p['codes']]
            assert matching, (record, p['codes'], seq)
            index = matching[0]
            start = max(0, min(index-1, len(seq)-3)) if len(seq)>3 else 0
            window = seq[start:start+3]
            example = dict(record_id=record, object_family_id=r['object_family_id'], cisi=r['source_cisi'],
                site=r['site'], object_type=r['object_type'], codes=window, start_slot_one_based=start+1,
                complete_text_length=len(seq), excerpt_only=len(seq)>len(window), supports=p['codes'],
                source='Lipi pinned fc8813a52e183d19c441631dc26c33a4dccbea39; source CISI identifier supplied by that derivative',
                source_url='https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39',
                purpose='Short evidence example for a reviewed sign; reading-order transcription, not a photographed seal or a translated sentence.')
            examples.append(example)
    assert len(examples)<=24 and max(map(lambda r:len(r['codes']),examples))<=3
    rows = []
    order = {c:i for i,p in enumerate(PROPOSALS) for c in p['codes']}
    for r in prior:
        c=r['code']; p=reviewed.get(c); stat=positions[c]
        drawings=r['reference_class_drawings'][:1]
        rows.append(dict(code=c, sign_id='W'+c,
            meaning=p['meaning'] if p else r['preferred_meaning'],
            tier=p['tier'] if p else 'inherited' if r['inherited'] else 'unreviewed',
            group_codes=p['codes'] if p else [c],
            argument=p['argument'] if p else 'Retained from the earlier catalogue for navigation; no semantic upgrade in this review.',
            decision=p['decision'] if p else 'Consult the earlier run for the original proposal and its assumptions.',
            rivals=p['rivals'] if p else r.get('alternatives',[]),
            anchors=[senses[w] for w in p['sanskrit']] if p else [],
            prior_meaning=r['preferred_meaning'], prior_priority=r['priority'],
            inherited_proposals=r['inherited_proposals'],
            drawings=drawings, schematic=c=='617', graphic_classes=r['graphic_classes'],
            statistics=stat, robust=robust.get(c), substitutions=substitutes.get(c),
            graphic_review=graphic.get(c), lexical_review=lexical.get(c),
            examples=[e for e in examples if c in e['supports'] and c in e['codes']],
            order=order.get(c,1000+int(c))))
    rows.sort(key=lambda r:(r['order'],r['code']))
    data=dict(title='Reviewed Indus sign hypotheses', run=args.run, date='2026-10-11',
        scope='Exploratory meanings conditional on pictorial interpretation, the corpus/crosswalk and a Sanskrit comparison. Sanskrit words are semantic anchors, not authenticated sounds. No posterior probabilities were calculated.',
        image_scope='1979 CC BY chart cells represent graphic classes. Their printed V numbers and graphic variants differ from Wells W codes. W617 is an authored schematic. No artifact photograph or unlicensed font is redistributed.',
        counts=dict(Counter(r['tier'] for r in rows)), shortlist_families=sum(p['tier']=='shortlist' for p in PROPOSALS),
        diagnostics=dict(distinct_sequences=1859, complete_faces=2930, object_families=2469, permutations=5000,
            position_tests=1788, new_codes_with_BH_q_below_05=40), rows=rows)
    out.mkdir(exist_ok=False)
    write(out/'catalogue-data.json', data)
    write(out/'example-provenance.json',dict(scope='Selected short examples only; no bulk corpus. Source-derived code windows remain outside the licence for our original prose/code.',examples=examples))
    write(out/'sanskrit-senses.json',dict(scope='Authored short paraphrases with selected dictionary sense identifiers. Early dictionary citations do not establish Bronze Age attestation.', rows=list(senses.values())))
    template=(HERE/'catalogue-template.html').read_text(encoding='utf-8')
    embedded=json.dumps(data,ensure_ascii=False).replace('</','<\/')
    (out/'catalogue.html').write_text(template.replace('__CATALOGUE_DATA__',embedded),encoding='utf-8')
    write(out/'build-manifest.json',dict(status='Exploratory final review iteration',core='run-v2',
        inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [CORE/'position-audit.json',CORE/'robustness.json',CORE/'substitution-audit.json',CORE/'lexical-adversarial.json',CORE/'graphic-sensitivity.json',HERE/'hypotheses.py',HERE/'catalogue-template.html',Path(__file__)]],
        sources=[dict(path=p,sha256=sha(ROOT/p)) for p in ['data/normalized/lipi_clean_rtl_singleline.jsonl','data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json']],
        outputs=[dict(path=p.name,sha256=sha(p)) for p in out.iterdir() if p.is_file()]))
    for name in ['hypotheses.py','build_catalogue.py','catalogue-template.html']:
        (out/name).write_bytes((HERE/name).read_bytes())
    print(json.dumps(dict(run=args.run,signs=len(rows),shortlist_codes=data['counts']['shortlist'],families=data['shortlist_families'],examples=len(examples),senses=len(senses)),ensure_ascii=False))

if __name__=='__main__': main()
