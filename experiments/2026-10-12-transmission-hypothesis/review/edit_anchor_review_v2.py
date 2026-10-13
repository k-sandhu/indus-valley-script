"""Create an editorial successor without changing source pins or judgments."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = HERE / 'additional-anchor-review.json'
    target = HERE / 'additional-anchor-review-v2.json'
    if target.exists():
        raise SystemExit('Refusing existing editorial endpoint')
    original = json.loads(source.read_text(encoding='utf-8'))
    result = deepcopy(original)
    changes = {
        (0, 'inspected'): 'Printed pp. 30, 118, 120, 122; PDF pp. 55, 154, 156, 158. All four contributor renders independently viewed; original report identifies their catalogue and society loci.',
        (1, 'finding'): 'The page describes 133 objects in a later collection with contents from all occupation phases. Duplicate image-alt occurrences are the same caption.',
        (2, 'inspected'): 'Printed p. 232/PDF p. 244; full contributor render independently viewed.',
        (3, 'inspected'): 'Original publisher supplementary Word XML: all Table S2 rows, its 95.4% heading, and comparison with Table S1 context fields. Main PDF not independently inspected in this additional pass.',
        (3, 'finding'): 'The three newly dated specimen rows give 2471–2298, 1880–1691 and 1517–1428 cal BCE for barley, Vigna and rice. Their Table S2 contexts say Jognakhera rather than assigning individual layers.',
        (4, 'inspected'): 'All 11 RV 10.71 paired stanzas; Sanskrit 10.71.2 and its Griffith translation also checked in actual parent HTML.',
    }
    for (index, field), value in changes.items():
        result['records'][index][field] = value
    result['additional_textual_anchor'] = 'One complete 11-stanza hymn in two editions; one lineage, not two ancient observations'
    restored = deepcopy(result)
    for index, field in changes:
        restored['records'][index][field] = original['records'][index][field]
    restored['additional_textual_anchor'] = original['additional_textual_anchor']
    assert restored == original, 'Non-editorial data changed'
    result['editorial_successor'] = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'original_endpoint': source.name,
        'original_sha256': sha(source),
        'editorial_code_sha256': sha(Path(__file__)),
        'note': 'EDITORIAL-ANCHOR-NOTE.md',
        'changed_record_fields': [{'record_index': i, 'field': f} for i, f in changes],
        'changed_top_level_fields': ['additional_textual_anchor'],
        'scope': 'Authored spacing only; source and derivative pins, dates and substantive judgments unchanged.',
    }
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'endpoint': target.name, 'record_fields': len(changes), 'noneditorial_equality': True}))


if __name__ == '__main__':
    main()
