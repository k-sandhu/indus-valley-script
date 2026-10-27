"""Author accounting and source-integrity checks; no corpus reads."""
import json
import hashlib
from collections import Counter
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-tablet-use-evidence')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    checks = []
    def check(name, condition):
        checks.append({'check': name, 'pass': bool(condition)})
    manifest = json.loads((PKG/'source-manifest-v1.json').read_text(encoding='utf-8'))
    summary = json.loads((PKG/'summary-v1.json').read_text(encoding='utf-8'))
    objects = json.loads((RAW/'objects-v1.json').read_text(encoding='utf-8'))
    relations = json.loads((RAW/'relations-v1.json').read_text(encoding='utf-8'))
    check('physical raw root and junction', (ROOT/'data/raw').resolve() == RAW.parent)
    for asset in manifest['assets']:
        path = Path(asset['physical_path'])
        check('asset exists ' + path.name, path.is_file())
        check('asset hash ' + path.name, sha(path) == asset['sha256'])
        check('asset byte size ' + path.name, path.stat().st_size == asset['bytes'])
        check('logical physical agreement ' + path.name, (ROOT/asset['logical_path']).resolve() == path.resolve())
    check('complete object identifiers', {o['object_id'] for o in objects} == {f'H-{n}' for n in range(2218,2240)})
    check('22 distinct registrations', len({o['registration']['literal'] for o in objects}) == len(objects) == 22)
    check('22 distinct caption specimens', {o['source_specimen'] for o in objects} == set(range(2,24)))
    check('unique inherited joins', all(o['join_status'] == 'unique-object' for o in objects))
    check('recovery accounting', Counter(o['association'] for o in objects) == {'clump':16,'nearby':2,'scattered':4})
    check('clump unit agrees per item', all((o['registration']['excavation_unit'] == '8040') == (o['association']=='clump') for o in objects))
    check('manufacturing group counts', Counter(o['manufacturing_group'] for o in objects) == {1:6,2:9,3:7})
    check('all group labels attributed', all(o['manufacturing_group_status']=='inferred-by-source-authors' for o in objects))
    check('secondary deposits retained', all(o['deposit_class']=='secondary-dump' for o in objects))
    check('no source face alignment invented', all(o['physical_source_sides_aligned_to_corpus_faces'] is False for o in objects))
    check('308 assertions', len(relations) == 308)
    check('assertions unique', len({r['assertion_id'] for r in relations}) == 308)
    check('14 assertions per object', set(Counter(r['object_id'] for r in relations).values()) == {14})
    check('every assertion joined', all(r['object_id'] in {o['object_id'] for o in objects} for r in relations))
    nulls = [r for r in relations if r['relation']=='use-null']
    check('132 use-null assertions', len(nulls)==132)
    check('null means unknown', all(r['value'] is None and r['value_status']=='unknown' for r in nulls))
    check('wear series control', all('different-series' in r['basis'] for r in relations if r['field']=='use_wear'))
    check('cutting direction scope', sum(r['field']=='incision_direction' and r['basis']=='published-microscopic-mould-observation' for r in relations)==22)
    check('stroke order scope', sum(r['field']=='incision_sequence' and r['basis']=='published-microscopic-mould-observation' for r in relations)==22)
    check('utility and reading assumptions attributed', all(r['value_status']=='inferred' for r in relations if r['relation']=='use-interpretation'))
    check('production event unresolved', all(r['value'] is None and r['value_status']=='unknown' for r in relations if r['field']=='single_production_event'))
    check('source pages bounded', all(set(r['pdf_pages_one_based']) <= set(range(1,22)) for r in relations))
    for key, path in [('protocol_sha256',PKG/'PROTOCOL.md'),('code_sha256',PKG/'build.py'),
                      ('local_object_register_sha256',RAW/'objects-v1.json'),('local_relation_register_sha256',RAW/'relations-v1.json')]:
        check(key, summary['provenance'][key] == sha(path))
    check('no confirmation access declared', summary['confirmation_access'] is False)
    check('no new-object claim', summary['new_objects']==summary['new_registration_joins']==0)
    check('no use fact from null fields', summary['direct_attachment_records']==summary['direct_content_records']==summary['independent_quantity_records']==0)
    check('source exposure correctly retained', summary['source_already_exposed'] is True)
    check('bounded text page count', len((RAW/'chapter-layout.txt').read_text(encoding='utf-8').split('\f'))-1==21)
    out = {'schema_version':'1.0','verification_tier':'submitted','review':'author validation',
        'passed':sum(c['pass'] for c in checks),'total':len(checks),'checks':checks}
    target = PKG/'validation-v1.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':out['passed'],'total':out['total']}))
    raise SystemExit(0 if out['passed']==out['total'] else 1)

if __name__=='__main__':
    main()
