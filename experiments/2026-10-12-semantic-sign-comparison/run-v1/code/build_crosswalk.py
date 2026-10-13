"""Build an auditable meaning crosswalk and its local graphic companion.

The named run directory is new each time. Source corpora, glyph renders and token
observations stay local. Public JSON contains own selections and short, attributed
lexical facts rather than complete inscriptions.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import html
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import fitz
from counterpart_specs import (SUMERIAN, AKKADIAN, EGYPTIAN_WORDS, EGYPTIAN_LIST,
                               LINEAR_B, FAMILY_CONCEPTS, REVIEWED_CODES)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = ROOT / 'data/raw/2026-10-12-semantic-sign-comparison'
PREVIOUS = ROOT / 'experiments/2026-10-12-bronze-age-comparison'
SL = {'s': 'http://oracc.org/ns/sl/1.0'}

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def acquired(name):
    meta = read(PACKAGE / 'acquisition' / (name + '.json'))
    return ROOT / meta['local_path'], meta

def prior(name):
    meta = read(PREVIOUS / 'acquisition' / (name + '.json'))
    return ROOT / meta['local_path'], meta

def unicode_egyptian(code):
    match = re.fullmatch(r'([A-Z]+)(\d+)([A-Z]?)', code)
    assert match, code
    query = 'EGYPTIAN HIEROGLYPH ' + match[1] + match[2].zfill(3) + match[3]
    return unicodedata.lookup(query)

def leaves_gdl(value):
    if isinstance(value, list):
        for child in value:
            yield from leaves_gdl(child)
    elif isinstance(value, dict):
        if value.get('gdl_sign'):
            yield value
        else:
            for key in ['seq','group','gdl']:
                if key in value:
                    yield from leaves_gdl(value[key])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='run-v1')
    args = parser.parse_args()
    run = PACKAGE / args.run
    figures = LOCAL / args.run / 'figures'
    run.mkdir(exist_ok=False)
    figures.mkdir(parents=True, exist_ok=False)
    frozen = read(PACKAGE / 'starting-manifest.json')
    inputs = {Path(m['snapshot']).name: ROOT / m['snapshot'] for m in frozen['inputs']}
    for item in frozen['inputs']:
        assert digest(ROOT / item['snapshot']) == item['sha256']
    assigned = read(inputs['run-v6-assigned-meanings.json'])['rows']
    visual = read(inputs['oct12-visual-families.json'])
    families = visual['rows']
    family_by_code = {}
    for family in families:
        for code in family['codes']:
            assert code not in family_by_code, code
            family_by_code[code] = family
    suppressed = {r['code'] for r in visual['chart_conflicts'] if r.get('suppress_public_glyph')}

    sl_path, sl_meta = acquired('oracc-sign-xml-v1')
    signs = {}
    for sign in ET.fromstring(sl_path.read_bytes()).findall('s:sign', SL):
        signs[sign.get('n')] = {'unicode':sign.findtext('s:utf8', '', SL),
                              'values':[v.get('n') for v in sign.findall('s:v', SL)]}
    font_path = Path('C:/Windows/Fonts/seguihis.ttf')
    font_chars = TTFont(font_path).getBestCmap()
    glyph_font = ImageFont.truetype(str(font_path), 96)
    graphic_manifest = []

    def graphic(id, text):
        if not text or not all(ord(c) in font_chars for c in text):
            return None
        bounds = glyph_font.getbbox(text)
        image = Image.new('RGB', (max(170, bounds[2]-bounds[0]+32), 160), 'white')
        draw = ImageDraw.Draw(image)
        draw.text(((image.width-(bounds[2]-bounds[0]))/2-bounds[0],
                   (image.height-(bounds[3]-bounds[1]))/2-bounds[1]), text,
                  fill='#16221f', font=glyph_font)
        file = figures / (id + '.png')
        image.save(file)
        record = {'id':id,'path':file.relative_to(ROOT).as_posix(),'sha256':digest(file),
                  'operation':'Modern Unicode rendering with system Segoe UI Historic; local-only',
                  'unicode':text,'font_path':str(font_path),'font_sha256':digest(font_path)}
        graphic_manifest.append(record)
        return record['path']

    def sum_glyph(names):
        for name in names:
            assert name in signs, ('Missing canonical sign', name)
        text = ''.join(signs[n]['unicode'] for n in names)
        assert text, names
        return text

    sum_path, sum_meta = prior('sumerian-ur3-v1')
    with zipfile.ZipFile(sum_path) as archive:
        gloss = json.loads(archive.read('epsd2/admin/ur3/gloss-sux.json'))
        catalogue = json.loads(archive.read('epsd2/admin/ur3/catalogue.json'))['members']
    local_observations = LOCAL / 'lexical-observations-v2'
    sum_tokens = [json.loads(s) for s in (local_observations / 'sumerian.jsonl').read_text(encoding='utf-8').splitlines()]
    akk_tokens = [json.loads(s) for s in (local_observations / 'akkadian-rimanum.jsonl').read_text(encoding='utf-8').splitlines()]
    eg_tokens = [json.loads(s) for s in (local_observations / 'egyptian.jsonl').read_text(encoding='utf-8').splitlines()]
    counterparts = []

    for id, concept, cf, gw, mng, reading, names in SUMERIAN:
        entries = [e for e in gloss['entries'] if e['cf']==cf and e['gw']==gw and e['pos'] not in ['PN','DN','GN']]
        assert len(entries)==1, (id, 'lemma selection', len(entries))
        entry = entries[0]
        senses = [s for s in entry['senses'] if s['mng']==mng]
        assert len(senses)==1, (id, 'sense selection', [s['mng'] for s in entry['senses']])
        sense = senses[0]
        matches = [r for r in sum_tokens if r['lemma']==cf and r['guideword']==gw and r['sense']==mng]
        matches.sort(key=lambda r:(len(r['form']),r['token_id'] or ''))
        exemplar = matches[0] if matches else None
        observation = None
        if exemplar:
            cat = catalogue[exemplar['text_id']]
            observation = {'text_id':exemplar['text_id'],'token_id':exemplar['token_id'],
                           'form':exemplar['form'],'period':cat.get('period'),
                           'designation':cat.get('designation'),'object_type':cat.get('object_type'),
                           'provenience':cat.get('provenience'),'source_member':exemplar['member']}
        glyph = sum_glyph(names)
        unit = 'single-sign word' if len(names)==1 else 'multi-sign word'
        counterparts.append({'id':id,'language':'Sumerian','tradition':'cuneiform',
                             'period':'Ur III','concept':concept,'meaning':mng,'reading':reading,
                             'sign_codes':names,'unicode':glyph,'writing_unit':unit,
                             'role':'lexical writing; optional determinatives belong to the source spelling',
                             'source_id':'sumerian-ur3-v1','source_url':f"https://oracc.museum.upenn.edu/epsd2/admin/ur3/cbd/sux/{entry['id']}.html",
                             'locator':{'zip_member':'epsd2/admin/ur3/gloss-sux.json','lemma_id':entry['id'],
                                        'sense_id':sense['oid'],'source_reported_sense_instances':int(sense['icount'])},
                             'edition_observation':observation,
                             'image_path':graphic(id,glyph),
                             'graphic_scope':'Modern canonical glyphs. Dated edition establishes the word use, not this font ductus.'})

    for id, concept, token_id, meaning in AKKADIAN:
        matches = [r for r in akk_tokens if r['token_id']==token_id]
        assert len(matches)==1, id
        row = matches[0]
        assert row['sense']==meaning, (id, row['sense'])
        leaves = list(leaves_gdl(row['gdl']))
        assert leaves, id
        names = [g['gdl_sign'] for g in leaves]
        glyph = sum_glyph(names)
        damaged = [g.get('id') for g in leaves if g.get('break')]
        is_logo = all(g.get('role')=='logo' for g in leaves)
        unit = ('single-sign logogram' if len(names)==1 else 'multi-sign logographic writing') if is_logo else 'multi-sign phonetic word'
        counterparts.append({'id':id,'language':'Akkadian','tradition':'cuneiform',
                             'period':'Old Babylonian; later comparison','concept':concept,'meaning':meaning,
                             'reading':row['form'],'lexeme':row['lemma'],'sign_codes':names,'unicode':glyph,
                             'writing_unit':unit,'role':'Sumerian logographic spelling in an Akkadian edition' if is_logo else 'syllabic spelling',
                             'source_id':'akkadian-rimanum-v1','source_url':f"https://oracc.museum.upenn.edu/rimanum/{row['text_id']}",
                             'locator':{'zip_member':row['member'],'token_id':token_id},
                             'damaged_components':damaged,'edition_observation':{'text_id':row['text_id'],'token_id':token_id},
                             'image_path':graphic(id,glyph),
                             'graphic_scope':'Modern canonical glyphs; any damaged components remain marked.'})

    for id, concept, lemma_id, mdc, meaning in EGYPTIAN_WORDS:
        matches = [r for r in eg_tokens if r['lemma_id']==lemma_id and r['mdc']==mdc]
        assert matches, (id, lemma_id, mdc)
        matches.sort(key=lambda r:(r['sentence_id'],r['token_id'] or ''))
        row = matches[0]
        glyph = row['unicode']
        # A119 has no glyph in the pinned AES Unicode encoding; use a source table detail.
        image_path = graphic(id,glyph) if glyph else None
        if id=='E-carry-A119':
            pdf_path, pdf_meta = acquired('unicode-egyptian-database-v1')
            doc = fitz.open(pdf_path)
            clip = fitz.Rect(166,1966,207,2042)
            file = figures / (id + '.png')
            doc[13].get_pixmap(matrix=fitz.Matrix(4,4),clip=clip,alpha=False).save(file)
            image_path = file.relative_to(ROOT).as_posix()
            graphic_manifest.append({'id':id,'path':image_path,'sha256':digest(file),
                                     'operation':'Source-table crop, local-only; no redrawing',
                                     'parent_sha256':pdf_meta['sha256'],'source_id':pdf_meta['id'],
                                     'pdf_leaf':14,'rect_pdf_points':list(clip)})
        counterparts.append({'id':id,'language':'Egyptian','tradition':'hieroglyphic',
                             'period':'Source tag OK & FIP','concept':concept,'meaning':meaning,
                             'source_gloss':row['gloss'],'reading':row['form'],'sign_codes':mdc.split('-'),
                             'unicode':glyph,'writing_unit':'single-sign word' if '-' not in mdc else 'multi-sign word',
                             'role':'Whole-word reading supplied by the edition; individual sign roles require a separate sign reference',
                             'source_id':'egyptian-aes-grab-v1','source_url':f"https://simondschweitzer.github.io/aed/{lemma_id}.html",
                             'locator':{'sentence_id':row['sentence_id'],'token_id':row['token_id'],'text_id':row['text_id'],'lemma_id':lemma_id},
                             'edition_observation':{'mdc':mdc,'word':row['form'],'period':row['date']},
                             'image_path':image_path,
                             'graphic_scope':'Edition glyph encoding rendered in a modern font.' if glyph else 'A119 reference drawing from the 2023 proposal table, distinct from the dated AES token.'})

    _, gardiner_meta = acquired('gardiner-mirror-v1')
    for id, concept, code, page, leaf, meaning, role in EGYPTIAN_LIST:
        glyph = unicode_egyptian(code)
        counterparts.append({'id':id,'language':'Egyptian','tradition':'hieroglyphic',
                             'period':'Middle Egyptian sign-list reference; date of each use requires its own witness',
                             'concept':concept,'meaning':meaning,'reading':code,'sign_codes':[code],
                             'unicode':glyph,'writing_unit':'one sign with documented uses','role':role,
                             'source_id':gardiner_meta['id'],'source_url':gardiner_meta['url'],
                             'locator':{'printed_page':page,'pdf_leaf':leaf,'entry':code},
                             'edition_observation':None,'image_path':graphic(id,glyph),
                             'graphic_scope':'Modern Unicode rendering; reference use is not a newly dated object.'})

    for sign, source, col, line, abbreviation, concept, meaning in LINEAR_B:
        image_file, meta = acquired(source)
        image = Image.open(image_file)
        # First chart has seven columns and fourteen rows; the second has six and fourteen.
        columns = 7 if source=='liber-logograms-100-v1' else 6
        left, top, right, bottom = 5, 5, image.width-5, image.height-5
        width, height = (right-left)/columns, (bottom-top)/14
        box = (int(left+col*width+5),int(top+line*height+3),
               int(left+col*width+width*.36),int(top+(line+1)*height-3))
        file = figures / (sign + '.png')
        image.crop(box).save(file)
        graphic_manifest.append({'id':sign,'path':file.relative_to(ROOT).as_posix(),
                                 'sha256':digest(file),'operation':'Source-chart crop, local-only; no tracing',
                                 'source_id':source,'parent_sha256':meta['sha256'],'rect_pixels':list(box)})
        counterparts.append({'id':sign,'language':'Mycenaean Greek','tradition':'Linear B',
                             'period':'Later Bronze Age administrative comparison','concept':concept,
                             'meaning':meaning,'reading':abbreviation,'sign_codes':[sign],
                             'writing_unit':'commodity/person logogram','role':'source conventional logogram',
                             'source_id':source,'source_url':'https://liber.cnr.it/credits',
                             'locator':{'chart':meta['title'],'column_zero_based':col,'row_zero_based':line},
                             'edition_observation':None,'image_path':file.relative_to(ROOT).as_posix(),
                             'graphic_scope':'Modern reference-chart drawing. No dated artifact glyph is supplied by this crop.'})

    lookup = {r['id']:r for r in counterparts}
    decisions = read(PACKAGE / 'reviewed_decisions.json')
    assert sorted(r['code'] for r in decisions)==sorted(REVIEWED_CODES)
    for decision in decisions:
        assert all(id in lookup for id in decision['counterparts'])
    crosswalk = []
    for family in families:
        concepts = FAMILY_CONCEPTS.get(family['family_id'], [])
        ids = [r['id'] for r in counterparts if r['concept'] in concepts]
        crosswalk.append({'family_id':family['family_id'],'codes':family['codes'],
                          'picture_observation':family['picture_observation'],
                          'family_proposed_meaning':family['working_meaning'],
                          'comparison_concepts':concepts,'counterparts':ids,
                          'status':'candidate semantic comparisons' if ids else 'no verified counterpart selected in this source set',
                          'relation_scope':'Possible objects, components or actions in the family proposal; no code-specific meaning is established.',
                          'visual_support':family.get('visual_support'),
                          'rivals':family.get('graphic_rivals',[])})
    inventory = []
    for row in assigned:
        code = row['code']
        family = family_by_code.get(code)
        drawing = None
        if code not in suppressed:
            candidates = [d.get('focused_path',d['path']) for d in row.get('drawings',[]) if d.get('confidence')=='high']
            drawing = next((d for d in candidates if (ROOT/d).exists()),None)
        family_row = next((f for f in crosswalk if family and f['family_id']==family['family_id']), None)
        inventory.append({'code':code,'sign_id':row['sign_id'],'earlier_assigned_meaning':row['meaning'],
                          'earlier_review_tier':row['tier'],'earlier_rivals':row.get('rivals',[]),
                          'family_id':family['family_id'] if family else None,
                          'recent_family_meaning':family['working_meaning'] if family else None,
                          'counterpart_ids':family_row['counterparts'] if family_row else [],
                          'match_scope':'Family-level alternatives, separate from the earlier assigned meaning.',
                          'drawing_path':drawing,'drawing_suppressed_for_conflict':code in suppressed,
                          'drawing_note':'Shared P004/V145 chart class; exact Wells variant is not shown.' if code in ['154','156','158'] else 'Published chart-class drawing; inspect the recorded code/class crosswalk.',
                          'reviewed_decision':next((d for d in decisions if d['code']==code),None)})
    inventory.sort(key=lambda r:(r['code'] not in REVIEWED_CODES, int(r['code'])))
    summary = {'run':args.run,'created_utc':datetime.now(timezone.utc).isoformat(),
               'assigned_codes':len(inventory),'earlier_tiers':dict(Counter(r['earlier_review_tier'] for r in inventory)),
               'recent_visual_families':len(families),'codes_with_recent_family':len(family_by_code),
               'codes_without_recent_family':len(inventory)-len(family_by_code),
               'counterparts':len(counterparts),'counterparts_by_language':dict(Counter(r['language'] for r in counterparts)),
               'families_with_candidate_counterparts':sum(bool(f['counterparts']) for f in crosswalk),
               'families_without_selected_counterpart':sum(not f['counterparts'] for f in crosswalk),
               'suppressed_conflicted_code_drawings':sorted(suppressed),
               'reviewed_codes':len(decisions),'meaning_validation_accuracy':None,
               'qualification':'Coverage is an inventory audit and retrieval map. It is not the share of authenticated or individually reviewed meanings.'}
    save(run/'counterparts.json',counterparts)
    save(run/'family-crosswalk.json',crosswalk)
    save(run/'inventory.json',inventory)
    save(run/'reviewed-signs.json',decisions)
    save(run/'summary.json',summary)
    save(run/'graphics-manifest.json',graphic_manifest)
    save(run/'build-manifest.json',{'inputs':frozen['inputs'],'scripts':{
        p.name:digest(p) for p in [Path(__file__),PACKAGE/'counterpart_specs.py',PACKAGE/'reviewed_decisions.json']},
        'sources':{'sumerian':sum_meta['sha256'],'signlist':sl_meta['sha256']},
        'outputs':{p.name:digest(p) for p in run.glob('*.json') if p.name!='build-manifest.json'}})
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
