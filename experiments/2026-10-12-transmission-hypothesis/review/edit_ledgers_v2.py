"""Preserved successor presentation; leave source IDs and frozen anchors intact."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from acquire_controls import REPO

HERE = Path(__file__).resolve().parent
FIELDS = {'reading_scope', 'edition_note', 'composition_date', 'publication_date', 'last_updated',
          'statement', 'locus', 'scope'}
MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edit(text):
    text = re.sub(r'\b(pp?\.|Fig\.)\s*(?=\d)', r'\1 ', text)
    text = re.sub(r'(?<=[a-z])(?=\d)', ' ', text)
    text = re.sub(r'(?<=\d)(?=(?:BCE|pages|page|' + MONTHS + r')\b)', ' ', text)
    return text


def walk(value):
    if isinstance(value, list):
        return [walk(item) for item in value]
    if isinstance(value, dict):
        return {key: edit(item) if key in FIELDS and isinstance(item, str) else walk(item)
                for key, item in value.items()}
    return value


if __name__ == '__main__':
    sources = json.loads((HERE / 'sources.json').read_text(encoding='utf-8'))
    observations = json.loads((HERE / 'observations.json').read_text(encoding='utf-8'))
    sources = walk(sources)
    observations = walk(observations)
    for source in sources['sources']:
        for witness in source['witnesses']:
            if 'inherited_from' not in witness:
                continue
            ledger_name, sid = witness['inherited_from'].split('#')
            prior = json.loads((REPO / ledger_name).read_text(encoding='utf-8-sig'))
            rows = prior['sources'] if isinstance(prior, dict) else prior
            record = next(row for row in rows if row.get('source_id', row.get('id')) == sid)
            captures = record.get('captures', record.get('witnesses', []))
            match = next(row for row in captures if row.get('path', row.get('local_path')) == witness['path'])
            for key in ['retrieved_utc', 'status_code', 'content_type', 'final_url', 'tls_verification']:
                if key in match:
                    witness[key] = match[key]
            witness['inherited_record_sha256'] = sha(REPO / ledger_name)
    for name, value in [('sources-v2.json', sources), ('observations-v2.json', observations)]:
        value['presentation_revision'] = {'created_utc': datetime.now(timezone.utc).isoformat(),
                                          'preserved_prior_sha256': sha(HERE / name.replace('-v2', '')),
                                          'code_sha256': sha(Path(__file__)),
                                          'note': 'EDITORIAL-LEDGER-NOTE.md'}
        with (HERE / name).open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
    assert {r['observation_id'] for r in observations['observations']} == {
        r['observation_id'] for r in json.loads((HERE / 'observations.json').read_text(encoding='utf-8'))['observations']}
    print(json.dumps({'canonical_ledgers': ['sources-v2.json', 'observations-v2.json'], 'observations': 19}))
