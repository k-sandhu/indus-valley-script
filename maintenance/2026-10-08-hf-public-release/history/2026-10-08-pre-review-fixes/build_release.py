"""Build a local, rights-filtered candidate. Never uploads or changes source files."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-08-hf-public-release'
M = ROOT / 'experiments/2026-10-07-helsinki1979-digitization'
V2 = M / 'repair/2026-10-07-v2'
B = ROOT / 'experiments/2026-10-06-evidence-census'
S = B / 'synthesis/main-2026-10-07-v6'
SOURCE = 'https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/'
CC = 'https://creativecommons.org/licenses/by/4.0/'

def environment():
    for key, name in [('TMP','tmp'),('TEMP','tmp'),('MPLCONFIGDIR','mpl'),('HF_HOME','hf'),('HF_DATASETS_CACHE','datasets')]:
        path = RAW / name
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    sys.dont_write_bytecode = True

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def compact(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',',':'))

def csv_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

class Builder:
    def __init__(self, out):
        self.out = out
        self.audit = []
        self.pins = {}
        self.configs = []
        self.tables = {}
        self.image_rows = []

    def input(self, path, status='own-work', decision='include-selected', basis='Project-authored facts, identifiers, aggregates or assessments; proposed CC BY 4.0.', fields=None):
        path = Path(path)
        rel = path.relative_to(ROOT).as_posix()
        if rel not in self.pins:
            self.pins[rel] = dict(path=rel, bytes=path.stat().st_size, sha256=sha(path))
            self.audit.append(dict(**self.pins[rel], rights_status=status, decision=decision, basis=basis, selected_fields=fields))
        return path

    def licensed(self, path, fields=None):
        return self.input(path, 'explicit-license', 'include-selected',
            'Derived solely from Koskenniemi and Parpola 1979; institutional final-version CC BY 4.0. Cropping, numerical annotation or chart-only recognition identified in NOTICE. Project contributions use proposed CC BY 4.0.', fields)

    def json(self, path, licensed=False, fields=None):
        return read(self.licensed(path, fields) if licensed else self.input(path, fields=fields))

    def image(self, path, dest, component, role, pdf_page=None):
        self.licensed(path, ['PNG pixels'])
        target = self.out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        self.image_rows.append(dict(image_path=dest, component=component, role=role, pdf_page=pdf_page,
            source_path=path.relative_to(ROOT).as_posix(), sha256=sha(target), bytes=target.stat().st_size,
            license='CC BY 4.0', source_url=SOURCE))
        return dest

    def table(self, name, rows, types=None, split='train', license='CC BY 4.0 proposed for own work', description=''):
        import pyarrow as pa
        import pyarrow.parquet as pq
        if not rows:
            raise ValueError('Empty configuration: '+name)
        types = types or {}
        keys = list(rows[0])
        if any(set(r)!=set(keys) for r in rows):
            raise ValueError('Inconsistent fields: '+name)
        def infer(k):
            values = [r[k] for r in rows if r[k] is not None]
            if k in types:
                return types[k]
            if not values:
                return pa.string()
            if all(isinstance(v,bool) for v in values):
                return pa.bool_()
            if all(isinstance(v,int) and not isinstance(v,bool) for v in values):
                return pa.int64()
            if all(isinstance(v,(float,int)) and not isinstance(v,bool) for v in values):
                return pa.float64()
            if all(isinstance(v,list) for v in values):
                flat = [a for v in values for a in v]
                if all(isinstance(v,int) for v in flat):
                    return pa.list_(pa.int64())
                return pa.list_(pa.string())
            return pa.string()
        schema = pa.schema([pa.field(k, infer(k)) for k in keys])
        table = pa.Table.from_pylist(rows, schema=schema)
        target = self.out / 'data' / (name+'.parquet')
        target.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, target, compression='zstd')
        self.configs.append(dict(config_name=name, data_files=[dict(split=split,path='data/'+name+'.parquet')]))
        self.tables[name] = dict(rows=len(rows), split=split, schema=[dict(name=f.name,type=str(f.type),nullable=f.nullable) for f in schema],
            data_file='data/'+name+'.parquet', sha256=sha(target), license=license, description=description,
            logical_sha256=hashlib.sha256(compact(rows).encode()).hexdigest())

    def chart(self):
        manual = self.json(ROOT/'research/chart_reference/manual_numeric_reference.json', True)
        atlas = self.json(ROOT/'output/chart_atlas/reference.json', True)
        audit = self.json(ROOT/'research/corpus/primary/chart_complete/consolidated_atlas_audit.json')
        assert len(manual['rows'])==len(atlas['rows'])==audit['frame_cells']==687
        keyed = {(x['pdf_page'],x['column'],x['row']):x for x in manual['rows']}
        rows=[]
        for a in atlas['rows']:
            key=(a['pdf_page'],a['column'],a['row']);m=keyed[key]
            for field in ['rank','code','alternatives','numeric_confidence','rank_alternatives','dashed_auxiliary']:
                assert a.get(field)==m.get(field),(key,field)
            path = self.image(ROOT/'output/chart_atlas'/a['image'], 'images/chart/'+Path(a['image']).name, 'chart_reference','chart_cell',a['pdf_page'])
            rows.append(dict(cell_id=f"p{key[0]}_c{key[1]}_r{key[2]}",pdf_page=key[0],column=key[1],row=key[2],
                rank=m.get('rank'),code=m.get('code'),alternatives=m.get('alternatives',[]),rank_alternatives=m.get('rank_alternatives',[]),
                numeric_confidence=m.get('numeric_confidence'),dashed_auxiliary=m.get('dashed_auxiliary'),
                source_crop_pdf_points=a.get('source_crop_pdf_points'),image_path=path,annotation_method='AI-assisted numeric label reading; no expert certification',
                source_url=SOURCE,source_pdf_sha256=atlas['source_sha256'],status='Exploratory'))
        assert sum(bool(r['alternatives']) for r in rows)==16
        import pyarrow as pa
        self.table('chart_reference',rows,{'alternatives':pa.list_(pa.int64()),'rank_alternatives':pa.list_(pa.int64()),'source_crop_pdf_points':pa.list_(pa.float64())},license='CC BY 4.0 source; project annotations proposed CC BY 4.0',description='687 chart cells and 16 retained lower-code ambiguities.')

    def benchmarks(self):
        readings=[];metadata=[]
        p1=M/'portable-inputs/data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json'
        preds1=self.json(p1,True)['rows']
        pf=self.json(M/'prediction-freeze.json')
        assert sha(p1)==pf['predictions_sha256']
        selection1=self.json(M/'blind/selection.json',True)
        refs1=[]
        def add_reading(path,version,reader,kind):
            d=self.json(path,True)
            data=d['rows'] if isinstance(d,dict) else d
            meta={k:v for k,v in d.items() if k!='rows'} if isinstance(d,dict) else {}
            metadata.append(dict(benchmark=version,reader=reader,kind=kind,source_file=path.relative_to(ROOT).as_posix(),metadata=meta))
            for row in data:
                readings.append(dict(benchmark=version,sample_index=row['sample_index'],reader=reader,kind=kind,
                    reading_json=compact(row),source_file=path.relative_to(ROOT).as_posix(),status='Frozen evaluation'))
            return data
        for letter in 'abc':
            refs1+=add_reading(M/f'blind/reference-{letter}.json','v1',letter.upper(),'primary')
            add_reading(M/f'blind/reference-{letter}-repeat.json','v1',letter.upper(),'convenience_repeat')
        preds2=self.json(V2/'predictions.json',True)['rows']
        pfreeze=self.json(V2/'prediction-freeze.json')
        assert sha(V2/'predictions.json')==pfreeze['prediction_sha256']
        selection2=self.json(V2/'blind/selection.json',True)
        refs2=add_reading(V2/'blind/adjudicated-reference.json','v2','C','adjudicated')
        for letter in 'ab':
            for part in [1,2]:
                add_reading(V2/f'blind/reader-{letter}/rows-part{part}.json','v2',letter.upper(),'independent')
        for version,selection,preds,refs,base in [('v1',selection1,preds1,refs1,M/'blind'),('v2',selection2,preds2,refs2,V2/'blind')]:
            pmap={r['sample_index']:r for r in preds};rmap={r['sample_index']:r for r in refs};rows=[]
            for locator in selection['rows']:
                i=locator['sample_index'];ref=rmap[i];pred=pmap[i]
                context=self.image(base/locator['source_crop'],f"images/{version}/{locator['source_crop']}",f'benchmark_rows_{version}','row_context',locator['pdf_page'])
                exact=None
                if locator.get('exact_crop'):
                    exact=self.image(base/locator['exact_crop'],f"images/{version}/{locator['exact_crop']}",f'benchmark_rows_{version}','exact_proposal_crop',locator['pdf_page'])
                assert sha(base/locator['source_crop'])==locator['source_crop_sha256']
                if exact:assert sha(base/locator['exact_crop'])==locator['exact_crop_sha256']
                rows.append(dict(sample_index=i,occurrence_key=pred['occurrence_key'],pdf_page=locator['pdf_page'],section=pred.get('section','number_order'),
                    context_image_path=context,exact_image_path=exact,locator_json=compact(locator),reference_json=compact(ref),prediction_json=compact(pred),
                    reference_kind='initial_disjoint_AI_reading' if version=='v1' else 'source_adjudication_after_two_AI_readings',
                    original_ocr_locator_exposed=bool(locator.get('ocr_number_witnesses')) if version=='v1' else False,status='Frozen evaluation'))
            assert len(rows)==(60 if version=='v1' else 80)
            self.table('benchmark_rows_'+version,rows,split='test',license='CC BY 4.0 source; project readings proposed CC BY 4.0',description=f'{len(rows)} source rows with immutable references and frozen predictions.')
        self.table('benchmark_readings',readings,split='test',description='Initial, repeated, independent and adjudicated readings; frozen endpoints remain distinct.')
        cards=[]
        for version,base in [('v1',M/'blind/chart_sheets'),('v2',V2/'blind/position-chart')]:
            for p in sorted(base.glob('*.png')):
                image=self.image(p,'images/cards/'+version+'_'+p.name,'benchmark_chart_cards','chart_card')
                cards.append(dict(benchmark=version,card_id=p.stem,image_path=image,source_file=p.relative_to(ROOT).as_posix()))
        self.table('benchmark_chart_cards',cards,description='Original chart-only cards supplied to benchmark readers.')
        countref=self.json(V2/'blind/adjudicated-counts.json',True)
        detections=self.json(V2/'count-page-detections.json',True)
        dmap={r['pdf_page']:r for r in detections['pages']};counts=[];countreadings=[]
        for ref in countref['pages']:
            page=ref['pdf_page']
            # Retain only geometric detections needed by the row-recall scorer.
            det=[{k:r[k] for k in ['row_anchor_y_2x','margin_xyxy_2x']} for r in dmap[page]['rows']]
            images=[]
            for p in sorted((V2/'blind/page-count-source').glob(f'*{page}*')):
                if p.suffix=='.png': images.append(self.image(p,'images/counts/'+p.name,'benchmark_count_pages','page_count_context',page))
            counts.append(dict(pdf_page=page,frame='random' if page in selection2['random_count_pages'] else 'stress',image_paths=images,
                reference_json=compact(ref),detections_json=compact(det),status='Frozen evaluation'))
        for letter in 'ab':
            path=V2/f'blind/reader-{letter}/counts.json';d=self.json(path,True)
            metadata.append(dict(benchmark='v2',reader=letter.upper(),kind='count',source_file=path.relative_to(ROOT).as_posix(),metadata={k:v for k,v in d.items() if k!='pages'}))
            for row in d['pages']:
                countreadings.append(dict(pdf_page=row['pdf_page'],reader=letter.upper(),reading_json=compact(row),source_file=path.relative_to(ROOT).as_posix()))
        self.table('benchmark_count_pages',counts,description='21 source-count pages: 18 random and 3 stress pages; geometric detections for recall.')
        self.table('benchmark_count_readings',countreadings,description='42 independent page inventories from the two readers.')
        for path,name in [(V2/'blind/CONVENTIONS.md','CONVENTIONS.md'),(M/'evaluate.py','score_core.py')]:
            self.input(path,'own-work','include','Project-authored reading rules or scoring code; proposed data CC BY 4.0 / code MIT.')
            target=self.out/('benchmark/'+name if name.endswith('.md') else 'code/'+name)
            target.parent.mkdir(parents=True,exist_ok=True)
            text=path.read_text(encoding='utf8')
            if name=='score_core.py':
                text=text.split('\ndef main():')[0]+'\n'
            target.write_text(text,encoding='utf8')
        # Copy the two unchanged repair geometry functions without its root-bound CLI.
        path=V2.parent.parent/'evaluate_repair.py'
        self.input(path,'own-work','include-selected','Project-authored row-recall functions; proposed MIT.', ['recall_page','page_summary'])
        text=path.read_text(encoding='utf8');start=text.index('\ndef recall_page(');end=text.index('\ndef main():')
        (self.out/'code/score_recall.py').write_text('import score_core as E\n'+text[start:end],encoding='utf8')
        for code in ['score_benchmark.py']:
            shutil.copyfile(HERE/code,self.out/'code'/code)
        expected={}
        for version,path in [('v1',M/'evaluation/2026-10-07-frozen-v1/metrics.json'),('v2',V2/'evaluation-2026-10-07-adjudicated/metrics.json')]:
            d=self.json(path,True)
            expected[version]={k:d[k] for k in ['summary','row_bootstrap_95','negative_result_criteria']}
            expected[version]['rows']=d['rows']
            if version=='v1':expected[version]['exploratory_sensitivities']=d['exploratory_sensitivities']
            if version=='v2':expected[version]['source_row_recall']=d['source_row_recall']
        dump(self.out/'benchmark/expected-metrics.json',expected)
        dump(self.out/'benchmark/reader-metadata.json',metadata)
        for path,dest in [(V2/'blind/adjudication-notes.json','v2-adjudication-notes.json'),
                (M/'follow-up/2026-10-07/analysis-v1/adjudication-overlay.json','v1-exploratory-adjudication-overlay.json'),
                (M/'freeze-manifest.json','v1-freeze-manifest.json'),(M/'prediction-freeze.json','v1-prediction-freeze.json'),
                (V2/'freeze-manifest.json','v2-freeze-manifest.json'),(V2/'prediction-freeze.json','v2-prediction-freeze.json')]:
            self.licensed(path)
            shutil.copyfile(path,self.out/'benchmark'/dest)

    def census(self):
        import pyarrow as pa
        coverage=self.json(S/'coverage.json',fields=['sites: selected site-level counts and identifiers','summary'])
        rows=[]
        fields=['site','assigned_region','local_faces','local_families','local_cisi_identifiers','IM77_main_selected_objects','IM77_count_status','ICIT_object_count','worldwide_missing_objects']
        for i,r in enumerate(coverage['sites']):
            row={k:r.get(k) for k in fields}
            row.update(source_locator=f"experiments/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/coverage.json#/sites/{i}",status='Exploratory')
            rows.append(row)
        self.table('evidence_sites',rows,{'ICIT_object_count':pa.int64(),'worldwide_missing_objects':pa.int64(),'IM77_main_selected_objects':pa.int64()},description='115 site/provenance entities from synthesis v6; aggregate counts in distinct source frames.')
        path=B/'sites-and-publications/publication-register.json'
        pubs=self.json(path,fields=['id','title','authors_editors','year','venue','url','opened'])['publications']
        self.table('evidence_publications',[dict(publication_id=p['id'],title=p['title'],authors_editors=p['authors_editors'],year=p['year'],venue=p['venue'],url=p['url'],access_record=p['opened'],source_locator=path.relative_to(ROOT).as_posix()+f"#/publications/{i}",status='Exploratory') for i,p in enumerate(pubs)],description='17 bibliographic register entries; historical catalogue coverage is documented separately.')
        path=B/'collections-and-datasets/collection-register.json'
        collections=self.json(path,fields=['institution','region','result_count','count_basis','record_fields','source_ids','query_date'])['collections']
        self.table('evidence_collections',[dict(institution=p['institution'],region=p.get('region'),confirmed_record_minimum=p.get('result_count'),count_basis=p.get('count_basis'),record_fields_json=compact(p.get('record_fields')),source_ids=p.get('source_ids',[]),query_date=p.get('query_date'),source_locator=path.relative_to(ROOT).as_posix()+f"#/collections/{i}",status='Exploratory') for i,p in enumerate(collections)],{'confirmed_record_minimum':pa.int64(),'source_ids':pa.list_(pa.string())},description='37 institution observations; null counts are unmeasured, zero counts are bounded queries.')
        path=B/'collections-and-datasets/dataset-register.json'
        datasets=self.json(path,fields=['name','size','count_basis','licence','versioning','source_ids'])['datasets']
        self.table('evidence_datasets',[dict(name=p['name'],size_json=compact(p.get('size')),count_basis=p.get('count_basis'),reported_reuse_terms=p.get('licence'),version_basis=p.get('versioning'),source_ids=p.get('source_ids',[]),source_locator=path.relative_to(ROOT).as_posix()+f"#/datasets/{i}",status='Exploratory') for i,p in enumerate(datasets)],{'source_ids':pa.list_(pa.string())},description='15 dataset observations with dated count bases; no underlying corpora bundled.')
        for file,config,integer,float_fields in [
            ('catalogue-coverage.csv','evidence_catalogue_coverage',['first','last','printed_number_slots','catalogue_entries','local_matching_entries','local_absent_entry_keys'],['fraction']),
            ('catalogue-section-split.csv','evidence_catalogue_sections',[],[]),
            ('field-completeness.csv','evidence_field_completeness',['denominator','present','missing'],['percent'])]:
            path=S/file;self.input(path,fields='All authored aggregate table columns; no row-level corpus or museum payload.')
            rows=csv_rows(path)
            for row in rows:
                for k in integer:
                    if k in row:row[k]=int(row[k]) if row[k] else None
                for k in float_fields:
                    if k in row:row[k]=float(row[k]) if row[k] else None
                row['status']='Exploratory'
            self.table(config,rows,{k:pa.int64() for k in integer}|{k:pa.float64() for k in float_fields},description='Synthesis v6 authored aggregate table; frame and measurement columns define denominators.')
        path=B/'collections-and-datasets/paired-full-audit.csv'
        keep=['institution','museum_record_id','museum_accession','museum_url','cisi','join_method','shared_identifier','join_evidence','status']
        self.input(path,fields=keep)
        rows=[{k:r.get(k) for k in keep} for r in csv_rows(path)]
        for i,row in enumerate(rows):row['source_locator']=path.relative_to(ROOT).as_posix()+f'#data-row={i+1}'
        supplement=ROOT/'data/raw/2026-10-06-evidence-census/synthesis/review-fixes-2026-10-07-v1/museum-join-supplement.json'
        for i,p in enumerate(self.json(supplement,fields=['institution','accession','record_id','source_cisi','method','source_evidence'])):
            url='https://museumsofindia.gov.in/repository/record/'+p['record_id'] if p['record_id'].startswith('nat_del-') else None
            rows.append(dict(institution=p['institution'],museum_record_id=p['record_id'],museum_accession=p['accession'],museum_url=url,cisi=p['source_cisi'],join_method=p['method'],shared_identifier=None,join_evidence=p['source_evidence'],status='Exploratory',source_locator=supplement.relative_to(ROOT).as_posix()+f'#/{i}'))
        assert len(rows)==68
        self.table('evidence_museum_joins',rows,description='68 authored museum-accession to published CISI identifier joins; local corpus record contents excluded.')
        summary=self.json(S/'join-summary.json')
        dump(self.out/'provenance/census-summary.json',dict(coverage=coverage['summary'],museum_joins=summary))
        source_rows=[]
        for path,namespace in [(B/'synthesis/sources.json','synthesis'),(B/'collections-and-datasets/sources.json','collections')]:
            d=self.json(path,fields=['id','title','authors','year','venue','url','access','opened_in_B3','access_in_B3'])
            data=d['sources'] if isinstance(d,dict) else d
            for p in data:
                source_rows.append(dict(source_id=namespace+':'+p['id'],title=p.get('title'),authors=compact(p.get('authors')),year=str(p.get('year')) if p.get('year') is not None else None,
                    venue=p.get('venue'),url=p.get('url'),access_record=p.get('access_in_B3',p.get('access')),opened_by_packager=False,
                    source_locator=path.relative_to(ROOT).as_posix()+'#'+p['id']))
        self.table('evidence_sources',source_rows,description='Bibliographic pointers and inherited access scopes; this packaging run did not reopen each archaeological source.')

    def aggregates(self):
        import pyarrow as pa
        base=ROOT/'experiments/2026-10-06-weight-metrology/summary-tables-review-response'
        self.input(base.parent/'sources.json',fields=['sources/ascalone2022 bibliographic identity and inherited access scope'])
        for file,name in [('mass-band-estimates.csv','weight_mass_bands'),('western-chance-baselines.csv','weight_chance_controls')]:
            path=base/file;self.input(path,fields='All aggregate numerical fields; catalogue rows excluded.')
            rows=csv_rows(path)
            for i,row in enumerate(rows):
                for key,val in list(row.items()):
                    if key in ['group','frame','null'] or key.endswith('interval95'):continue
                    row[key]=int(val) if key=='n' or key=='draws' or key.endswith('_n') else float(val)
                row['method_path']='experiments/2026-10-06-weight-metrology/REPORT.md'
                row['source_locator']=path.relative_to(ROOT).as_posix()+f'#data-row={i+1}'
                row['status']='Exploratory'
            self.table(name,rows,description='Aggregate metrology results after review; no Ascalone catalogue records included.')

    def finish(self):
        self.table('image_assets',self.image_rows,description='Every staged licensed PNG with relative path, parent path and SHA256.')
        self.audit.extend([
            dict(path='data/raw/2026-10-06-modern-restoration/main/**',rights_status='rights-unverified',decision='exclude',basis='Lipi-derived per-query predictions and model files; no source licence found.'),
            dict(path='data/raw/2026-10-06-modern-restoration/frozen-model/**',rights_status='rights-unverified',decision='exclude',basis='Lipi-derived fitted models and training register; existing private backup only.'),
            dict(path='data/normalized/lipi_*.jsonl',rights_status='rights-unverified',decision='exclude-payload',basis='No bulk or record-level contents released. Used read-only by validation for sequence-overlap screening.'),
            dict(path='data/normalized/mayig_*.json*',rights_status='mixed-assets',decision='exclude-payload',basis='MIT source notice exists; separate CISI photograph rights unresolved. No Mayig payload released.'),
            dict(path='experiments/2026-10-07-helsinki1979-digitization/runs/**/occurrences.jsonl',rights_status='explicit-license',decision='exclude',basis='CC BY 4.0 source, but provisional full transcription remains quarantined after failed evaluations.'),
            dict(path='experiments/2026-10-07-helsinki1979-digitization/integration/**/ledger-import.jsonl',rights_status='explicit-license',decision='exclude',basis='Provisional transcription and unresolved carrier joins; not a verified corpus.'),
            dict(path='experiments/2026-10-08-helsinki1979-row-verification/PROTOCOL.md',rights_status='own-work',decision='not-included',basis='Only proposed verification protocol present at initial inspection; no new completed readings.'),
            dict(path='third-party PDFs, non-Helsinki page images, museum descriptions/images and Ascalone2022 catalogue rows',rights_status='rights-unverified',decision='exclude',basis='No permission basis supplied for those payloads. Bibliographic facts and authored aggregates only.'),
        ])
        dump(self.out/'provenance/input-manifest.json',list(self.pins.values()))
        dump(self.out/'provenance/rights-audit.json',dict(status='Verified computation',licences_for_own_work='Proposed; awaiting user confirmation',source_license_url=CC,files=self.audit))
        dump(self.out/'provenance/table-manifest.json',self.tables)
        # The descriptor gives a loader-readable configuration for each table.
        import yaml
        metadata=dict(pretty_name='Indus chart, row-reading benchmarks and evidence census',license=['cc-by-4.0','mit'],
            tags=['indus-script','epigraphy','archaeology','undeciphered-script','image-to-text','research-data'],
            task_categories=['image-to-text'],size_categories=['1K<n<10K'],configs=self.configs)
        header='---\n'+yaml.safe_dump(metadata,sort_keys=False,allow_unicode=True)+'---\n\n'
        (self.out/'README.md').write_text(header+'# Local release candidate\n\nDataset documentation is generated by write_documents.py before validation.\n',encoding='utf8')
        dump(self.out/'provenance/metadata.json',metadata)
        (self.out/'requirements.txt').write_text('datasets==5.1.0\npyarrow==25.0.1\nnumpy==2.5.3\nPyYAML==6.0.3\nPillow>=12\n',encoding='utf8')

def main():
    environment()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'release')
    args=parser.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Choose a new output directory inside Package O.')
    out.mkdir(parents=True)
    b=Builder(out);b.chart();b.benchmarks();b.census();b.aggregates();b.finish()
    print(compact(dict(configurations=len(b.tables),images=len(b.image_rows),rows={k:v['rows'] for k,v in b.tables.items()})))

if __name__=='__main__':
    main()
