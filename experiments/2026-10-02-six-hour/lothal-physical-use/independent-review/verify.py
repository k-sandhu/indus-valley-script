"""Check the independent review's preserved outputs and local witness hashes."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
checks = []


def check(name, passed):
    checks.append({'check': name, 'passed': bool(passed)})


def read(name):
    return json.loads((BASE / name).read_text(encoding='utf-8'))


result = read('main-refined/results.json')
for name, witness in result['inputs'].items():
    check(name + '_hash', hashlib.sha256((ROOT / witness['path']).read_bytes()).hexdigest() == witness['sha256'])
check('all_computation_checks_pass', all(row['passed'] for row in read('main-refined/verification.json')))
check('failed_initial_count_endpoint_preserved', read('main/results.json')['joined_objects'] == 93
      and read('main/results.json')['verification']['failed'] == 1)
check('refined_join_count', result['joined_objects'] == 68 and result['joined_faces'] == 86)
check('code_snapshot_hash', hashlib.sha256((BASE / 'main-refined/code_snapshot.py').read_bytes()).hexdigest() == result['code_sha256'])
source = read('source-assertions.json')
assertions = {row['id']: row for row in source['assertions']}
check('source_coordinate_correction_preserved', assertions['total-impressions']['pdf_page_one_based'] == 20
      and assertions['total-impressions']['printed_page'] == 82
      and assertions['root-prose-coordinate-correction']['frozen_pdf_page_one_based'] == 21)
check('two_object_count_conflicts_preserved', all(assertions[key]['prose']['count'] == 2
      and assertions[key]['table']['count'] == 1 for key in ['L174-impression-count', 'L179-impression-count']))
traces = read('selected-trace-observations.json')
ids = [obj for row in traces['figure_inventory'] for obj in row['labelled_object_ids']]
check('35_distinct_figure_objects', len(ids) == len(set(ids)) == 35)
check('12_distinct_selected_objects', len({row['object_id'] for row in traces['observations']}) == 12)
check('all_selected_objects_in_figures', all(row['object_id'] in ids for row in traces['observations']))
check('all_observations_have_separate_author_field', all(row['image_observation'] and row['author_assertion'] for row in traces['observations']))
check('inset_identity_and_count_unresolved', traces['unassigned_view']['object_id'] is None
      and traces['unassigned_view']['count'] is None)
manifest = json.loads((ROOT / 'data/six-hour/lothal/independent-review/figure-native-image-record.json').read_text(encoding='utf-8'))
for witness in manifest:
    check('native_figure_' + str(witness['figure']) + '_hash',
          hashlib.sha256((ROOT / witness['path']).read_bytes()).hexdigest() == witness['sha256'])
for path in BASE.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if not target.startswith(('https:', 'http:', '#')):
            check(path.name + '_link_' + target, (path.parent / target).exists())
output = {'checks': len(checks), 'passed': sum(row['passed'] for row in checks),
          'failed': sum(not row['passed'] for row in checks), 'details': checks}
target = BASE / 'verification.json'
if target.exists():
    raise RuntimeError('Preserve verification; write a new endpoint for a later review.')
target.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: output[key] for key in ['checks', 'passed', 'failed']}))
if output['failed']:
    raise SystemExit(1)
