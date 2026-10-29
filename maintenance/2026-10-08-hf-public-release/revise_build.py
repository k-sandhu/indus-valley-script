"""Apply the review revision to the original builder without modifying parent packages."""
from pathlib import Path
p=Path(__file__).parent/'build_release.py'
s=p.read_text(encoding='utf8')
def replace(a,b):
    global s
    if a not in s:raise ValueError('Missing replacement anchor: '+a[:100])
    s=s.replace(a,b)
replace('import sys\n','import sys\nfrom release_policy import Portable, MIXED_LICENSE, bytes_safe\n')
replace('json.dumps(data, ensure_ascii=False, sort_keys=True, separators=', 'json.dumps(bytes_safe(data), ensure_ascii=False, sort_keys=True, separators=')
replace('        self.image_rows = []','        self.image_rows = []\n        self.portable = Portable()\n        self.embedded = {}\n        self.records = HERE / "build-records" / out.name\n        self.records.mkdir(parents=True, exist_ok=False)')
replace('proposed CC BY 4.0.', 'CC0 1.0 own contributions.')
replace('Project contributions use CC0 1.0 own contributions.', 'Project additions are waived under CC0 1.0; edition content retains CC BY 4.0.')
replace("        shutil.copyfile(path, target)\n        self.image_rows", "        embedded = component=='chart_reference' or component.startswith('benchmark_rows_')\n        if embedded:self.embedded[dest] = path.read_bytes()\n        else:shutil.copyfile(path, target)\n        self.image_rows")
replace("sha256=sha(target), bytes=target.stat().st_size,", "sha256=sha(path), bytes=path.stat().st_size,\n            storage='embedded' if embedded else 'loose_png',")
replace("license='CC BY 4.0 proposed for own work'", "license='CC0 1.0'")
replace('        types = types or {}','''        types = types or {}
        rows = self.portable.value(rows)
        pairs = {'chart_reference':[('image_path','image')],
                 'benchmark_rows_v1':[('context_image_path','context_image')],
                 'benchmark_rows_v2':[('context_image_path','context_image'),('exact_image_path','exact_image')]}.get(name,[])
        image_type=pa.struct([pa.field('bytes',pa.binary()),pa.field('path',pa.string())])
        for path_key,image_key in pairs:
            for row in rows:
                row[image_key]={'bytes':self.embedded[row[path_key]],'path':None} if row[path_key] else None
            types[image_key]=image_type''')
replace("        pq.write_table(table, target, compression='zstd')", """        if pairs:
            from datasets import Features, Image
            features=Features.from_arrow_schema(schema)
            for _,image_key in pairs:features[image_key]=Image()
            table=table.replace_schema_metadata(features.arrow_schema.metadata)
        pq.write_table(table, target, compression='zstd')""")
replace("license='CC BY 4.0 source; project annotations proposed CC BY 4.0'", "license=MIXED_LICENSE")
replace("license='CC BY 4.0 source; project readings proposed CC BY 4.0'", "license=MIXED_LICENSE")
for config in ['benchmark_readings','benchmark_chart_cards','benchmark_count_pages','benchmark_count_readings','image_assets']:
    replace(f"self.table('{config}',",f"self.table('{config}',") if False else None
    # Add an explicit licence argument at each single-line call.
    lines=s.splitlines()
    for i,line in enumerate(lines):
        if f"self.table('{config}'," in line:
            lines[i]=line.replace(',description=',',license=MIXED_LICENSE,description=')
    s='\n'.join(lines)+'\n'
replace("proposed data CC BY 4.0 / code MIT", "data CC0 1.0 / code Unlicense")
replace("proposed MIT.","Unlicense.")
replace("                text=text.split('\\ndef main():')[0]+'\\n'", """                text=text.split('\\ndef main():')[0]+'\\n'
                text=text.replace("HERE=Path(__file__).resolve().parent\\nROOT=HERE.parents[1]\\nRAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization'",'')""")
replace("for code in ['score_benchmark.py']:","for code in ['score_benchmark.py','extract_images.py']:")
replace("dump(self.out/'benchmark/reader-metadata.json',metadata)","dump(self.out/'benchmark/reader-metadata.json',self.portable.value(metadata))")
replace("            shutil.copyfile(path,self.out/'benchmark'/dest)","""            d=read(path)
            if 'code_hashes' in d:d.pop('code_hashes')
            dump(self.out/'benchmark'/dest,self.portable.value(d))""")
start=s.index("        assert len(rows)==68")
end=s.index('        source_rows=[]',start)
s=s[:start]+'''        excluded=[];included=[]
        for row in rows:
            if row['cisi'] in ('-', '', None) or row['join_method']=='shared_field_and_published_plate':
                excluded.append(dict(row=row, reason='Identifier join rests only on the unlicensed Lipi excavation-idno comparison; no independent published concordance retained.'))
                continue
            row={k:(None if v in ('','-','--','N/A') else v) for k,v in row.items()}
            evidence=row['join_evidence'] or ''
            evidence=evidence.split('; raw/')[0]
            row['join_evidence']=evidence
            row['identifier_sources_json']=compact(dict(museum_record_id=row['museum_url'] or 'Published museum catalogue record',
                museum_accession=row['museum_url'] or 'Published museum catalogue accession',
                cisi='CISI 1 (1987) catalogue identifier; '+evidence,
                shared_identifier=evidence if row['shared_identifier'] else None))
            included.append(row)
        assert len(excluded)==19 and len(included)==49
        dump(RAW/('museum-joins-excluded-'+self.out.name+'.json'),excluded)
        self.audit.append(dict(path=path.relative_to(ROOT).as_posix(),rights_status='own-work',decision='include-selected-49-exclude-19',
            basis='Coordinator decision 8 October 2026: publish small cited extracts of identifier facts from CISI 1 concordance and Marshall composite; omit 14 placeholder-CISI and five Penn Lipi-only joins. No museum prose or images.',
            included_rows=49,excluded_rows=19,identifier_sources='Citation per identifier in identifier_sources_json'))
        self.table('evidence_museum_joins',included,description='49 independently cited museum-to-CISI identifier correspondences: 42 earlier pairs and seven supplement rows.')
        summary=self.json(S/'join-summary.json')
        dump(self.out/'provenance/census-summary.json',self.portable.value(dict(coverage=coverage['summary'],museum_joins=dict(confirmed_identifier_joins=49, earlier_pairs=42,supplement_rows=7,excluded_Lipi_only=19))))
''' +s[end:]
replace("                row['method_path']='experiments/2026-10-06-weight-metrology/REPORT.md'", "                if 'null' in row:row['null_model']=row.pop('null')\n                row['method_path']='docs/METHODS.md#weight-metrology'")
replace("dump(self.out/'provenance/input-manifest.json',list(self.pins.values()))", "dump(self.records/'input-manifest.json',list(self.pins.values()))\n        dump(self.records/'portable-source-map.json',self.portable.mapping)")
replace("dump(self.out/'provenance/rights-audit.json'", "dump(self.records/'rights-audit.json'")
replace("licences_for_own_work='Proposed; awaiting user confirmation'", "licences_for_own_work='Owner confirmed 8 October 2026: data/documentation CC0 1.0; code Unlicense'")
replace("license=['cc-by-4.0','mit']", "license=['cc0-1.0','cc-by-4.0','unlicense'],language=['en']")
replace("'datasets==5.1.0\\npyarrow==25.0.1\\nnumpy==2.5.3\\nPyYAML==6.0.3\\nPillow>=12\\n'", "'numpy>=1.24,<3\\npyarrow>=14,<26\\n# Loading tables/images additionally uses datasets>=3,<6 and Pillow>=10.\\n'")
replace('    b=Builder(out);b.chart();b.benchmarks();b.census();b.aggregates();b.finish()', '''    b=Builder(out);b.chart();b.benchmarks();b.census();b.aggregates();b.finish()
    from write_documents import generate
    generate(out, b)
    dump(b.records/'portable-source-map.json',b.portable.mapping)''')
p.write_text(s,encoding='utf8')
print('Builder revised')
