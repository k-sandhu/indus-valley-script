"""Update the initial source-comparison checker for the reviewed schema."""
from pathlib import Path
p=Path(__file__).parent/'validate_release.py';s=p.read_text(encoding='utf8')
def replace(a,b):
    global s
    if a not in s:raise ValueError(a[:100])
    s=s.replace(a,b)
replace('import score_benchmark','from release_policy import Portable\nfrom extract_images import embedded_images\nimport score_benchmark')
replace("inputs=read(release/'provenance/input-manifest.json')", """records=HERE/'build-records'/release.name
    if not records.exists():records=HERE/'build-records'/'release-revision-2026-10-08-v1'
    inputs=read(records/'input-manifest.json')
    portable=Portable();portable.mapping=read(records/'portable-source-map.json')""")
replace("table=data[spec['split']];rows=table.to_list();tables[name]=rows", """table=data[spec['split']]
        for key,feature in table.features.items():
            if isinstance(feature,datasets.Image):table=table.cast_column(key,datasets.Image(decode=False))
        rows=table.to_list();tables[name]=rows""")
start=s.index('    images=[]\n');end=s.index("    dump(rawout/'image-checks.json',images)",start)
s=s[:start]+'''    images=[];embedded=dict(embedded_images(release))
    import io
    for row in tables['image_assets']:
        p=(release/row['image_path']).resolve()
        assert p.is_relative_to(release)
        content=embedded[row['image_path']] if row['storage']=='embedded' else p.read_bytes()
        original=ROOT/portable.mapping[row['source_path']]
        with Image.open(io.BytesIO(content)) as im:
            format=im.format;size=list(im.size);im.verify()
        ok=format=='PNG' and hashlib.sha256(content).hexdigest()==row['sha256'] and original.read_bytes()==content
        if row['storage']=='embedded':ok=ok and not p.exists()
        images.append(dict(path=row['image_path'],storage=row['storage'],size=size,passed=ok))
        if not ok:failures.append('image:'+row['image_path'])
''' +s[end:]
replace("actual=b[k]", "actual=b[k];v=portable.value(v)")
replace("len(tables['evidence_museum_joins'])==summary['museum_joins']['confirmed_identifier_joins']==68", "len(tables['evidence_museum_joins'])==summary['museum_joins']['confirmed_identifier_joins']==49 and all(r['cisi'] and r['cisi']!='-' and r['join_method']!='shared_field_and_published_plate' and 'Lipi' not in r['join_evidence'] and r['identifier_sources_json'] for r in tables['evidence_museum_joins'])")
replace("'61 original + 7 v6 supplement identifiers; no corpus payload'", "'42 independent earlier pairs + 7 printed-catalogue supplement pairs; 19 Lipi-only joins excluded'")
replace("json.loads(r['reference_json'])==refs[r['sample_index']] and json.loads(r['prediction_json'])==preds[r['sample_index']] and json.loads(r['locator_json'])==locators[r['sample_index']]", "json.loads(r['reference_json'])==portable.value(refs[r['sample_index']]) and json.loads(r['prediction_json'])==portable.value(preds[r['sample_index']]) and json.loads(r['locator_json'])==portable.value(locators[r['sample_index']])")
replace("path=row['source_file']", "path=portable.mapping[row['source_file']]")
replace("json.loads(row['reading_json'])==original", "json.loads(row['reading_json'])==portable.value(original)")
replace("original=read(path)[container];rows=tables[config]", """original=portable.value(read(path)[container]);rows=tables[config]
        if config=='evidence_publications':
            from write_release_docs import LOTHAL
            for p in original:
                if 'Lothal Sealings:' in p['title']:p['title']=LOTHAL""")
replace("for k,v in src.items():ok=ok and (float(v)==row[k] if isinstance(row[k],(int,float)) else v==row[k])", "for k,v in src.items():\n                key='null_model' if k=='null' else k\n                ok=ok and (float(v)==row[key] if isinstance(row[key],(int,float)) else v==row[key])")
replace("json.loads(r['reference_json'])==lookup[r['pdf_page']]", "json.loads(r['reference_json'])==portable.value(lookup[r['pdf_page']])")
replace("audit=read(release/'provenance/rights-audit.json')", "audit=read(records/'rights-audit.json')")
replace("required_user_decisions=['Own-work licences','Author/affiliation/contact','Code distribution','Hosted review and final visibility decision']", "required_user_decisions=['Public issues repository','Hub terms for private Lipi-derived store','Final visibility switch']")
replace("'Licences for own work remain proposed.'", "'Public issues repository is awaiting confirmation.'")
replace("'Every staged reference, prediction and locator equals the frozen parent object.'", "'Every substantive frozen reference, prediction and locator field matches; repository-only pointers use portable labels.'")
replace("'Every returned reading equals the original reader file.'", "'Every reading field matches after portable pointer transformation.'")
p.write_text(s,encoding='utf8')
print('Validation revised')
