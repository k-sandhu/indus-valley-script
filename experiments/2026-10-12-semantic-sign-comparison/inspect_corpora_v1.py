"""Extract lexical observations locally, retaining source IDs and graphic structure."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import html
import json
import re
import sys
import zipfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREVIOUS = ROOT / 'experiments/2026-10-12-bronze-age-comparison'
LOCAL = ROOT / 'data/raw/2026-10-12-semantic-sign-comparison'

QUERIES = {
    'carry': r'carry|carrier|porter|load|burden|heben|tragen|Träger|Last',
    'person': r'^worker$|^person$|^man$|^woman$|Arbeiter|Mann|Mensch|Frau',
    'staff': r'staff|scept|Stab|Zepter',
    'comb': r'\bcomb\b|\bKamm\b',
    'harrow': r'harrow|rake|Egge|Rechen',
    'plough': r'plou?gh|Pflug|pflüg',
    'vessel': r'^jar$|^pot$|^vessel$|^container$|Krug|Topf|Gefäß',
    'house': r'^house$|^building$|^room$|^enclosure$|^storehouse$|Haus|Gebäude|Speicher',
    'door': r'^door$|^gate$|Tür|Tor\b',
    'field': r'^field$|Feld|Acker',
    'fish': r'^fish$|Fisch',
    'bird': r'^bird$|Vogel',
    'sheep': r'^sheep$|Schaf',
    'goat': r'^goat$|Ziege',
    'cattle': r'^ox$|^bull$|^cow$|^cattle$|Rind|Stier|Kuh',
    'horn': r'^horn$|Horn',
    'grain': r'^barley$|^grain$|Gerste|Getreide|Korn',
    'plant': r'^reed$|^tree$|^plant$|^grass$|Baum|Pflanze|Rohr|Gras',
    'water': r'^water$|^canal$|^river$|Wasser|Fluss|Kanal',
    'textile': r'^cloth$|^textile$|^wool$|Stoff|Gewebe|Wolle|Kleid',
    'net': r'^net$|Netz',
    'rope': r'^rope$|^cord$|^bond$|Seil|Strick|Schnur',
    'bow': r'^bow$|Bogen',
    'arrow': r'^arrow$|Pfeil',
    'wheel': r'^wheel$|Rad\b',
    'group': r'^group$|^total$|^all$|Gruppe|Gesamtheit|Summe',
}

def prev_path(name):
    meta = json.loads((PREVIOUS / 'acquisition' / (name + '.json')).read_text(encoding='utf-8'))
    return ROOT / meta['local_path'], meta

def walk(value):
    if isinstance(value, dict):
        if value.get('node') == 'l' and isinstance(value.get('f'), dict):
            yield value
        for key, child in value.items():
            if key != 'f':
                yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

def oracc(name, language, bound=None):
    path, meta = prev_path(name)
    rows = []
    invalid = []
    with zipfile.ZipFile(path) as archive:
        files = [n for n in archive.namelist() if '/corpusjson/' in n and n.endswith('.json')]
        if bound:
            files.sort(key=lambda n: hashlib.sha256(('20261012:' + Path(n).stem).encode()).hexdigest())
            files = files[:bound]
        for member in files:
            try:
                doc = json.loads(archive.read(member))
            except (ValueError, KeyError) as exc:
                invalid.append({'member': member, 'error': str(exc)})
                continue
            for token in walk(doc):
                f = token['f']
                if not str(f.get('lang', '')).startswith(language):
                    continue
                gloss = '; '.join(str(f.get(k, '')) for k in ['gw','sense'])
                matched = [k for k, rx in QUERIES.items() if re.search(rx, gloss, re.I)]
                if matched:
                    rows.append({'source': name, 'text_id': Path(member).stem,
                                 'member': member, 'token_id': token.get('ref'),
                                 'form': f.get('form'), 'lemma': f.get('cf'),
                                 'guideword': f.get('gw'), 'sense': f.get('sense'),
                                 'pos': f.get('pos'), 'lang': f.get('lang'),
                                 'gdl': f.get('gdl'), 'queries': matched})
    return rows, {'source': name, 'sha256': meta['sha256'], 'path': meta['local_path'],
                  'text_members_selected': len(files), 'invalid_members': invalid,
                  'selection': 'Prior fixed hash sample of 3,000 Ur III members' if bound else 'All acquired text JSON members'}

def egyptian():
    path, meta = prev_path('egyptian-aes-grab-v1')
    data = json.loads(path.read_bytes())
    rows = []
    for sid, sentence in data.items():
        if sentence.get('date') != 'OK & FIP':
            continue
        for token in sentence.get('token', []):
            gloss = str(token.get('cotext_translation', ''))
            matched = [k for k, rx in QUERIES.items() if re.search(rx, gloss, re.I)]
            if matched:
                rows.append({'source': 'egyptian-aes-grab-v1', 'sentence_id': sid,
                             'text_id': sentence.get('text'), 'date': sentence.get('date'),
                             'token_id': token.get('_id'), 'form': token.get('written_form'),
                             'lemma': token.get('lemma_form'), 'lemma_id': token.get('lemmaID'),
                             'gloss': gloss, 'pos': token.get('pos'),
                             'mdc': token.get('hiero'), 'unicode': html.unescape(token.get('hiero_unicode', '')),
                             'queries': matched})
    return rows, {'source': 'egyptian-aes-grab-v1', 'sha256': meta['sha256'], 'path': meta['local_path'],
                  'selected_period': 'OK & FIP', 'source_sentences': len(data)}

def main():
    directory = LOCAL / 'lexical-observations-v1'
    directory.mkdir(parents=True, exist_ok=False)
    manifests = []
    summaries = {}
    for key, result in [
        ('sumerian', oracc('sumerian-ur3-v1', 'sux', 3000)),
        ('akkadian-rimanum', oracc('akkadian-rimanum-v1', 'akk')),
        ('akkadian-letters', oracc('akkadian-atletters-v1', 'akk')),
        ('egyptian', egyptian()),
    ]:
        rows, meta = result
        file = directory / (key + '.jsonl')
        file.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
        meta.update(output=file.relative_to(ROOT).as_posix(), matched_tokens=len(rows),
                    output_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        manifests.append(meta)
        summary = defaultdict(Counter)
        for r in rows:
            identity = (r.get('lemma'), r.get('guideword', r.get('gloss')), r.get('lemma_id'))
            for q in r['queries']:
                summary[q][identity] += 1
        summaries[key] = {q:[{'lemma':k[0], 'gloss':k[1], 'lemma_id':k[2], 'n':v} for k,v in c.most_common(12)] for q,c in summary.items()}
    (PACKAGE / 'corpus-observation-manifest.json').write_text(json.dumps({'sources':manifests,'query_scope':'Broad lexical search only; manual sense and sign-role review required'}, indent=2) + '\n', encoding='utf-8')
    (directory / 'query-summary.json').write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:len(v) for k,v in summaries.items()}))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
