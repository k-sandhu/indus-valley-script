"""Integrate the reviewed pilot layers without changing earlier source entries."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def entry(identifier, title, paths, fields, size, evidence, notes):
    return {
        'id':identifier, 'title':title, 'kind':'source-join',
        'status':'project-output', 'location':'local-only',
        'local_paths':paths, 'version':{'date':'2026-10-26'}, 'size':size,
        'identifiers':['pilot target ID', 'CISI catalogue key', 'source and page locator'],
        'metadata_fields':fields,
        'rights':{'status':'mixed-assets','licence':None,'detail':'Project code, prose, aggregates and source manifests are retained in the checkout. Source-derived records and third-party images remain local-only under REDISTRIBUTION.md.'},
        'fetch':{'method':'rebuild','steps':['Follow '+evidence[0]+' and its input manifests. Original sources must be available locally.']},
        'hashes':{p:sha(ROOT/p) for p in paths}, 'evidence':evidence, 'notes':notes
    }

def main():
    assert not (PKG/'inventory-integration-v1.json').exists()
    review = read(ROOT/'experiments/2026-10-26-object-pilot-review/integration-review-v2.json')
    assert review['failed'] == 0 and review['passed'] == 11
    assert sha(RAW/'integration-v1/pilot-integrated-v1.json') == review['projection_sha256']
    final = RAW/'integration-v2/pilot-integrated-v2.json'
    assert final.exists()
    data = read(final)
    assert len(data['objects']) == 20
    assert sum(len(x['assertions']) for x in data['objects']) == 541
    assert 'pending' not in str(data['review_status']).lower()
    additions = [
        entry('object-pilot-reviewed-2026-10-26', 'Twenty-target object register with reviewed image joins and conflict dispositions',
              ['data/raw/2026-10-26-object-pilot/integration-v2/pilot-integrated-v2.json', 'data/raw/2026-10-26-object-pilot/integration-v2/catalogue-integrated-v2-polished.html', 'data/raw/2026-10-26-object-pilot/integration-v2/missing-evidence-integrated-v2.json'],
              ['source-qualified assertions','candidate identities','image and face pointers','dimensions and material','findspot and phase','missing evidence','conflicting source assertions'],
              {'target_records':20,'inherited_source_assertions':539,'integration_conflict_summaries':2,'candidate_families':62,'candidate_relationships':274,'new_physical_merges':0},
              ['experiments/2026-10-26-object-pilot/REPORT.md','experiments/2026-10-26-object-pilot-register/INTERFACE.md','experiments/2026-10-26-object-pilot-review/REVIEW.md'],
              'The fixed subset overlaps existing holdings. Independent review checks structure and selected primary claims; it does not retranscribe all 539 historical assertions. No global corpus count changes.'),
        entry('image-recovery-index-2026-10-26', 'Reviewed recovery of fourteen held crop-to-catalogue view links',
              ['data/raw/2026-10-26-image-recovery/image-joins-v2.json'],
              ['asset identity','catalogue key','view label','source plate','prior index status','review disposition'],
              {'assets_censused':8722,'anonymous_assets':284,'assets_inspected':24,'new_index_relations':14,'newly_available_pilot_photographs':0,'new_physical_merges':0},
              ['experiments/2026-10-26-image-recovery/REPORT-v2.md','experiments/2026-10-26-image-recovery/aggregate-v2.json','experiments/2026-10-26-object-pilot-review/REPORT-v2.md'],
              'Gain is measured against the 13 October image-files.csv table. L-163 photographs predate this pass in source-page records. L-163 and L-207 are newly indexed keys in that table; broader L-207 availability was not audited.'),
        entry('object-source-conflicts-2026-10-26', 'Lothal and Harappa source conflicts with exact resolving records',
              ['data/raw/2026-10-26-source-conflicts/conflicts-v2.json'],
              ['competing source assertions','source dependence','safe display','blocked identity claims','ranked resolving records'],
              {'conflicts':2,'affected_pilot_targets':2,'comparison_entities':1,'closed_conflicts':0},
              ['experiments/2026-10-26-source-conflicts/REPORT.md','experiments/2026-10-26-source-conflicts/source-manifest-v2.json','experiments/2026-10-26-object-pilot-review/REVIEW.md'],
              'Both conflicts remain unresolved. L-161 is a comparison entity only. Original registered photographs and object cards are needed; repeated publication labels do not supply independent excavation evidence.')
    ]
    manifest_path = ROOT/'data/MANIFEST.json'
    original_bytes = manifest_path.read_bytes()
    manifest = json.loads(original_bytes.decode('utf-8-sig'))
    assert not {x['id'] for x in additions}.intersection(x['id'] for x in manifest['sources'])
    before_sources = list(manifest['sources'])
    manifest['sources'].extend(additions)
    manifest['updated'] = '2026-10-26'
    manifest['counts'] = dict(Counter(x['status'] for x in manifest['sources']))
    assert manifest['sources'][:len(before_sources)] == before_sources
    ending = '\r\n' if b'\r\n' in original_bytes else '\n'
    serialized = json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'
    data_path = ROOT/'knowledge/DATA.md'
    body = data_path.read_bytes()
    marker = b'## Twenty-target object pilot, 26 October 2026'
    assert marker not in body
    old = b'lists 104 sources (40 held, 14 partly held, 20 project outputs and 30 not held)'
    counts = manifest['counts']
    new = ('lists '+str(len(manifest['sources']))+' sources ('+str(counts['held'])+' held, '+str(counts['partly-held'])+' partly held, '+str(counts['project-output'])+' project outputs and '+str(counts['not-held'])+' not held)').encode('utf-8')
    assert body.count(old) == 1
    body = body.replace(old,new,1)
    appendix = '''

## Twenty-target object pilot, 26 October 2026

We consolidated ten Dholavira accession targets, five Harappa catalogue targets and five Lothal catalogue targets into a local browsable register. Its 539 inherited source assertions retain their original values and qualifiers; two integration summaries make the disputed identity rules explicit. The ten Dholavira targets retain 62 candidate families and 274 comparison relationships. These are twenty target dossiers within existing holdings, with zero physical merges and no change to the global object census. [Integrated report](../experiments/2026-10-26-object-pilot/REPORT.md), [register interface](../experiments/2026-10-26-object-pilot-register/INTERFACE.md).

| Layer | Coverage and qualification | Evidence |
|---|---|---|
| Target metadata | All 20 have identity assertions; 15 have material, 16 some dimensions, 14 a findspot and 15 stratum or phase assertions. These counts include retained source qualifications and disagreements. | [Coverage](../experiments/2026-10-26-object-pilot-register/coverage-v4.json) |
| Image pointers | 17 targets have local image or illustrated-page files; one additional target has a web photograph pointer. Complete all-face coverage is not established. | [Register report](../experiments/2026-10-26-object-pilot-register/REPORT.md) |
| Crop index | 14 asset-to-catalogue view links added against the 13 October image-files.csv table. L-163 and L-207 become keys in that index. L-163 photographs were already held in source-page records; this pass adds zero newly available pilot photographs. | [Corrected image report](../experiments/2026-10-26-image-recovery/REPORT-v2.md), [aggregate](../experiments/2026-10-26-image-recovery/aggregate-v2.json) |
| Identity conflicts | Rao's CLXI F panel remains disputed between 1864 and 1830. H-2587 retains the 7158 and 7458 registration alternatives. Neither conflict is closed. | [Conflict record](../experiments/2026-10-26-source-conflicts/REPORT.md) |
| Separate review | All 14 new image relations were checked against crops, original plates and the prior index. The register and integration were structurally checked; selected primary claims were reread. Historical metadata cells were not all retranscribed. | [Review disposition](../experiments/2026-10-26-object-pilot-review/REVIEW.md) |

The register, detailed image joins, conflict rows, source derivatives and catalogue HTML remain local on D:. Their logical data/raw paths and hashes are recorded in data/MANIFEST.json and the package manifests. The next identity evidence is a Dholavira accession-to-catalogue bridge, the ASI negative register for CLXI F, and the HARP object cards and photo records for the disputed 1996 lots.
'''
    # Check both intended writes before changing either shared file.
    assert manifest_path.read_bytes() == original_bytes
    manifest_path.write_bytes(serialized.replace('\n',ending).encode('utf-8'))
    data_path.write_bytes(body+appendix.encode('utf-8'))
    record = {'added_source_ids':[x['id'] for x in additions], 'earlier_entries_preserved':len(before_sources), 'counts':manifest['counts'], 'source_total':len(manifest['sources']), 'shared_files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (manifest_path,data_path)]}
    with (PKG/'inventory-integration-v1.json').open('x',encoding='utf-8') as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(record))

if __name__ == '__main__':
    main()
