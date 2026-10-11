"""Build an attributed, bounded public catalogue from the frozen diagnostics.

The full corpus, MW definition index and unlicensed font remain local inputs.
Public examples contain at most three consecutive codes, chosen to illustrate
the reviewed candidates. The viewer embeds data and also works without a server.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, importlib.util, sys
from PIL import Image
from hypotheses import PROPOSALS, SENSES, LOOKUP_HEADWORDS

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
    parser.add_argument('--run', default='run-v6')
    args = parser.parse_args()
    out = HERE / args.run
    if out.exists(): raise SystemExit('Preserve existing catalogue runs; choose another --run.')
    prior = read(OLD / 'run-2026-10-09-v5/candidates.json')['rows']
    before = {r['code']: r for r in prior}
    positions = {r['code']: r for r in read(CORE/'position-audit.json')['rows']}
    robust = {r['code']: r for r in read(HERE/'diagnostics-v3/robustness.json')['selected']}
    context = {r['code']:r for r in read(HERE/'context-diagnostics-v1/catalogue-summary.json')['rows']}
    site_sensitivity = {r['code']:r['site_final_sensitivity'] for r in read(HERE/'diagnostics-v3/position-site-sensitivity.json')['rows']}
    substitutes = {r['code']: r for r in read(CORE/'substitution-audit.json')['rows']}
    graphic = {r['code']: r for r in read(CORE/'graphic-sensitivity.json')['rows']}
    lexical = {r['code']: r for r in read(CORE/'lexical-adversarial.json')['rows']}
    repaired_lexical = {r['code']:r for r in read(HERE/'lexical-diagnostics-v3/RESULTS.json')['cases']}
    clean = [json.loads(x) for x in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    by_record = {r['record_id']:r for r in clean}
    dictionary = read(ROOT/'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json')
    senses = {}
    for word, (entry, page, meaning, period) in SENSES.items():
        headword = LOOKUP_HEADWORDS.get(word,word)
        key = old.slp(headword)
        matches = [x for x in dictionary.get(key, []) if x['entry_id']==entry]
        assert len(matches)==1, (word, entry)
        assert matches[0]['page_column']==page, (word, page, matches[0])
        senses[word] = dict(word=word, slp1=old.slp(headword), comparison_headword=headword,
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
    leading_order = ['151','400','154','156','158','161','527','142','130']
    order = {c:i for i,c in enumerate(leading_order)}
    order.update({c:100+i for i,p in enumerate(PROPOSALS) for c in p['codes'] if c not in order})
    pictures = {
        '151':'Person-like figure beneath a crossbar with two suspended loops; shoulder-pole/carrier is the leading picture, balance apparatus a rival.',
        '154':'Carrier-like figure with added hook-like head marks. Public W154/W156/W158 pictures use the same P004/V145 class, hiding the local font distinctions.',
        '156':'Carrier-like figure with additional internal body/arm strokes in the local font. The public shared P004/V145 image cannot show that difference.',
        '158':'Raised-arm carrier-like variant in the local font. Its public P004/V145 class image is shared with W154/W156 and does not depict that exact variant.',
        '161':'Carrier-like figure with triangular head feature; a rank or enclosure function is not supplied by the picture.',
        '400':'A spine with parallel teeth: comb, rake or harrow-like design. Group/class is a separate functional proposal.',
        '527':'A divided/barred panel; it resembles a comb with another side closing the bar ends. Door, rack, box and related closing design remain alternatives.',
        '142':'Person-like figure holding a tall vertical staff. The staff is direct; the office or name is open.',
        '130':'Person-like figure holding a horizontal toothed implement, also visible on M-16. Harrow/rake compares more closely than a specific plough.',
        '617':'Two separate adjacent grids with a visible gap on M-81. The schematic is not to cell count; the token boundary is unresolved.'}

    for r in prior:
        c=r['code']; p=reviewed.get(c); stat=dict(positions[c]); stat['site_final_sensitivity']=site_sensitivity[c]
        drawings=r['reference_class_drawings'][:1]
        rows.append(dict(code=c, sign_id='W'+c,
            meaning=p['meaning'] if p else r['preferred_meaning'],
            tier=p['tier'] if p else 'inherited' if r['inherited'] else 'unreviewed',
            group_codes=p['codes'] if p else [c],
            argument=p['argument'] if p else 'Retained from the earlier catalogue for navigation; no semantic upgrade in this review.',
            decision=p['decision'] if p else 'Consult the earlier run for the original proposal and its assumptions.',
            rivals=p['rivals'] if p else r.get('alternatives',[]),
            anchors=[dict(senses[w],role=p.get('anchor_roles',{}).get(w,'Semantic comparison')) for w in p['sanskrit']] if p else [],
            picture_evidence=pictures.get(c,'Earlier drawing/class reference; no new component-level review in this iteration.'),
            context_review=context.get(c),
            prior_meaning=r['preferred_meaning'], prior_priority=r['priority'],
            inherited_proposals=r['inherited_proposals'],
            drawings=drawings, schematic=c=='617', graphic_classes=r['graphic_classes'],
            statistics=stat, robust=robust.get(c), substitutions=substitutes.get(c),
            graphic_review=graphic.get(c), lexical_review=lexical.get(c),
            lexical_sensitivity=repaired_lexical.get(c),
            examples=[e for e in examples if c in e['supports'] and c in e['codes']],
            order=order.get(c,1000+int(c))))
    rows.sort(key=lambda r:(r['order'],r['code']))
    data=dict(title='Reviewed Indus sign hypotheses', run=args.run, date='2026-10-11',
        scope='Working meanings compare visible components, inscription contexts and Sanskrit senses. Picture, structural role and lexical fit are reported separately. Sanskrit is the comparison vocabulary; no posterior probability of a meaning was calculated.',
        external_review=dict(model='claude-opus-5-5',authentication='claude.ai subscription, no API key',source='../claude-review.md',integration='../review-decisions-v2.json'),
        image_scope='1979 CC BY chart cells represent graphic classes. Their printed V numbers and graphic variants differ from Wells W codes. W617 is an authored schematic. No artifact photograph or unlicensed font is redistributed.',
        counts=dict(Counter(r['tier'] for r in rows)), shortlist_families=sum(p['tier']=='shortlist' for p in PROPOSALS),
        diagnostics=dict(distinct_sequences=1859, complete_faces=2930, object_families=2469, permutations=5000,
            position_tests=1788, new_codes_with_BH_q_below_05=40), rows=rows)
    out.mkdir(exist_ok=False)
    write(out/'catalogue-data.json', data)
    write(out/'example-provenance.json',dict(scope='Selected short examples only; no bulk corpus. Source-derived code windows remain outside the licence for our original prose/code.',examples=examples))
    write(out/'sanskrit-senses.json',dict(scope='Authored short paraphrases with selected dictionary sense identifiers. Early dictionary citations do not establish Bronze Age attestation.', rows=list(senses.values())))
    # Focus selected licensed chart drawings for legibility. These rectangles
    # were checked against the public-class contact sheet; no glyph is redrawn.
    focused = {r['code'] for r in rows if r['tier']=='shortlist'} | {c for e in examples for c in e['codes']}
    rectangles = {'151':(122,26,180,102),'154':(126,30,183,103),'156':(126,30,183,103),
        '158':(126,30,183,103),'161':(118,25,180,105),'400':(98,31,151,109),'142':(128,29,185,109),
        '527':(115,25,174,106),'130':(122,28,190,107)}
    crops = []
    for r in rows:
        if r['code'] not in focused or not r['drawings']: continue
        drawing = r['drawings'][0]
        source = ROOT/drawing['path']
        im = Image.open(source)
        rect = rectangles.get(r['code'], (105,30,min(192,im.width),min(109,im.height)))
        dest = out/'focused-drawings'/('W'+r['code']+'.png')
        dest.parent.mkdir(exist_ok=True)
        im.crop(rect).save(dest)
        drawing['focused_path'] = dest.relative_to(ROOT).as_posix()
        crops.append(dict(code=r['code'],source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
            pixel_rectangle=list(rect),output=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),license='CC BY 4.0',
            attribution='Koskenniemi and Parpola, Corpus of Texts in the Indus Script (1979), University of Helsinki edition',
            transformation='Rectangular detail crop for display; no stroke alteration. Class correspondence, not exact Wells variant identity.'))
    write(out/'chart-crop-manifest.json',dict(rows=crops, source='output/chart_atlas/reference.json'))
    # Rewrite data only inside this new, not-yet-completed build to include
    # detail-crop pointers; completed earlier run directories are untouched.
    write(out/'catalogue-data.json', data)
    template=(HERE/'catalogue-template.html').read_text(encoding='utf-8')
    embedded=json.dumps(data,ensure_ascii=False).replace('</',r'<\/')
    (out/'catalogue.html').write_text(template.replace('__CATALOGUE_DATA__',embedded),encoding='utf-8')
    write(out/'build-manifest.json',dict(status='Exploratory final review iteration',core='run-v2',
        inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [CORE/'position-audit.json',HERE/'diagnostics-v3/robustness.json',HERE/'diagnostics-v3/position-site-sensitivity.json',HERE/'context-diagnostics-v1/catalogue-summary.json',HERE/'lexical-diagnostics-v3/RESULTS.json',CORE/'substitution-audit.json',CORE/'lexical-adversarial.json',CORE/'graphic-sensitivity.json',HERE/'claude-review.md',HERE/'claude-review-execution.json',HERE/'review-decisions-v2.json',HERE/'hypotheses.py',HERE/'catalogue-template.html',Path(__file__)]],
        sources=[dict(path=p,sha256=sha(ROOT/p)) for p in ['data/normalized/lipi_clean_rtl_singleline.jsonl','data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json']],
        outputs=[dict(path=p.relative_to(out).as_posix(),sha256=sha(p)) for p in out.rglob('*') if p.is_file()]))
    for name in ['hypotheses.py','build_catalogue.py','catalogue-template.html']:
        (out/name).write_bytes((HERE/name).read_bytes())
    print(json.dumps(dict(run=args.run,signs=len(rows),shortlist_codes=data['counts']['shortlist'],families=data['shortlist_families'],examples=len(examples),senses=len(senses)),ensure_ascii=False))

if __name__=='__main__': main()
