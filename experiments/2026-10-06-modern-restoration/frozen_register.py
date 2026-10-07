"""Preserve training identities locally for future contamination screening."""
import json
from data import Corpus, ROOT, OWN, RAW, save, digest

def main():
    record = json.loads((OWN / 'frozen-model/manifest.json').read_text(encoding='utf-8'))
    c = Corpus()
    extra, detail = c.extra([])
    rows = c.rows + (extra if record['chosen']['extra'] else [])
    path = RAW / 'frozen-model/training-register.jsonl'
    if path.exists():
        raise FileExistsError(path)
    values = [{'record_id': r['record_id'], 'artifact_aliases': r.get('artifact_aliases', [r['artifact']]),
        'seq': r['seq'], 'object_family_id': r.get('object_family_id')} for r in rows]
    path.write_text(''.join(json.dumps(r) + '\n' for r in values), encoding='utf-8')
    save(OWN / 'frozen-model/training-register.json', {'status': 'Frozen evaluation',
        'training_register': str(path.relative_to(ROOT)).replace('\\', '/'), 'sha256': digest(path),
        'texts': len(rows), 'tokens': sum(len(r['seq']) for r in rows),
        'rule': 'A fresh evaluation must screen objects, aliases and complete-string overlaps against this register, plus broader source-register links, before calling cases independent.'})
    save(OWN / 'frozen-model/code-dependencies.json', {
        'status': 'Frozen evaluation',
        'repository_dependencies': [{'path': str(p.relative_to(ROOT)).replace('\\', '/'),
            'sha256': digest(p)} for p in [ROOT / 'src/six_hour/markov_baseline.py',
                ROOT / 'src/methods/conditional_structure.py', OWN / 'inference.py']],
        'rule': 'The frozen loader rejects changes to these imported helpers or its interface.'})

if __name__ == '__main__':
    main()
