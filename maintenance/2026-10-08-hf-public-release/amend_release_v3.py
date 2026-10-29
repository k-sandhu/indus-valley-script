"""Recorded one-time source edits for the 0.3.0 build; do not rerun on amended files."""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def replace(text, old, new):
    assert old in text, old[:100]
    return text.replace(old, new)


def main():
    p = HERE/'build_release.py';text=p.read_text(encoding='utf8')
    text=replace(text,"V2 = M / 'repair/2026-10-07-v2'", "V2 = M / 'repair/2026-10-07-v2'\nV3 = M / 'repair/2026-10-08-v3'\nP = ROOT / 'experiments/2026-10-08-chart-reference-audit'")
    text=replace(text,"'benchmark_rows_v2':[('context_image_path','context_image'),('exact_image_path','exact_image')]", "'benchmark_rows_v2':[('context_image_path','context_image'),('exact_image_path','exact_image')],\n                 'benchmark_rows_v3':[('context_image_path','context_image'),('exact_image_path','exact_image')]")
    start=text.index('    def chart(self):');end=text.index('    def benchmarks(self):')
    text=text[:start]+'''    def chart(self):
        from chart_changes import ChartChanges, cell_key
        manual = self.json(ROOT/'research/chart_reference/manual_numeric_reference.json', True)
        current = self.json(P/'chart-reference-v2.1.json', True)
        comparison = self.json(P/'comparison-v2.1.json', True)
        impact = self.json(P/'impact-v2.1.json', True)
        self.input(P/'RECOMMENDED-USE.md')
        self.chart_changes = ChartChanges(manual, current, comparison, impact)
        atlas = self.json(ROOT/'output/chart_atlas/reference.json', True)
        assert len(current['rows']) == len(atlas['rows']) == 687
        rows=[]
        numeric_fields=['rank','code','alternatives','rank_alternatives','numeric_confidence']
        for a in atlas['rows']:
            cell=cell_key(a);m=self.chart_changes.new[cell];old=self.chart_changes.old[cell]
            changed={k:dict(old=old.get(k),new=m.get(k)) for k in numeric_fields if old.get(k)!=m.get(k)}
            assert changed == self.chart_changes.changes.get(cell, {})
            path=self.image(ROOT/'output/chart_atlas'/a['image'],'images/chart/'+Path(a['image']).name,'chart_reference','chart_cell',a['pdf_page'])
            previous={'previous_'+k:old.get(k) if k in changed else None for k in numeric_fields}
            note='; '.join(f"{k}: {v['old']} to {v['new']}" for k,v in changed.items()) or None
            rows.append(dict(cell_id=cell,pdf_page=a['pdf_page'],column=a['column'],row=a['row'],
                **{k:m.get(k) for k in numeric_fields},**previous,changed_fields=list(changed),change_note=note,
                dashed_auxiliary=m.get('dashed_auxiliary'),source_crop_pdf_points=a.get('source_crop_pdf_points'),image_path=path,
                annotation_method='AI chart reading; second AI blind reading of 63 cells and whole-chart pixel check; no expert review',
                reference_version='2.1',source_url=SOURCE,source_pdf_sha256=atlas['source_sha256'],status='Exploratory'))
        import pyarrow as pa
        types={k:pa.list_(pa.int64()) for k in ['alternatives','rank_alternatives','previous_alternatives','previous_rank_alternatives']}
        types.update(previous_rank=pa.int64(),previous_code=pa.int64(),changed_fields=pa.list_(pa.string()),source_crop_pdf_points=pa.list_(pa.float64()))
        self.table('chart_reference',rows,types,license=MIXED_LICENSE,description='687 reviewed chart cells: 8 code and 2 class corrections, 16 settled ambiguities; 33 medium-confidence cells.')
        dump(self.out/'provenance/chart-changes.json',self.portable.value(dict(status='Exploratory',reference_version='2.1',
            reference_sha256=sha(P/'chart-reference-v2.1.json'),comparison_summary=comparison['summary'],changes=comparison['changes'],
            mapping_policy=impact['mapping_policy'],reference_impact=impact['M_references'],locator_conflicts=impact['M_v3_reported_location_conflicts'],
            corrected_label_rescoring='Deferred pending candidate identity and locator review; frozen scores use original card labels.')))

'''+text[end:]
    text=replace(text,"reading_json=compact(row),source_file=", "reading_json=compact(row),chart_correction_flags_json=compact(self.chart_changes.reference_flags(row,version,kind=='adjudicated')),source_file=")
    text=replace(text,"for version,selection,preds,refs,base in [('v1',selection1,preds1,refs1,M/'blind'),('v2',selection2,preds2,refs2,V2/'blind')]:", """preds3=self.json(V3/'predictions.json',True)['rows']
        pfreeze3=self.json(V3/'prediction-freeze.json')
        assert sha(V3/'predictions.json')==pfreeze3['prediction_sha256']
        selection3=self.json(V3/'blind/selection.json',True)
        refs3=add_reading(V3/'blind/adjudicated-reference.json','v3','C','adjudicated')
        for letter in 'ab':
            for part in [1,2]:add_reading(V3/f'blind/reader-{letter}/rows-part{part}.json','v3',letter.upper(),'independent')
        for version,selection,preds,refs,base in [('v1',selection1,preds1,refs1,M/'blind'),('v2',selection2,preds2,refs2,V2/'blind'),('v3',selection3,preds3,refs3,V3/'blind')]:""")
    text=replace(text,"reference_kind='initial_disjoint_AI_reading'", "reference_chart_correction_flags_json=compact(self.chart_changes.reference_flags(ref,version,True)),\n                    prediction_chart_correction_flags_json=compact(self.chart_changes.prediction_flags(pred)),\n                    reference_kind='initial_disjoint_AI_reading'")
    text=replace(text,"self.table('benchmark_readings',readings,", "self.table('benchmark_readings',[r for r in readings if r['benchmark']!='v3'],")
    text=replace(text,"        cards=[]", "        self.table('benchmark_readings_v3',[r for r in readings if r['benchmark']=='v3'],split='test',license=MIXED_LICENSE,description='240 v3 readings: two independent readers and adjudication for all 80 rows.')\n        cards=[]")
    text=replace(text,"('v2',V2/'blind/position-chart')]:", "('v2',V2/'blind/position-chart'),('v3',V3/'blind/position-chart')]:")
    anchor="        for path,name in [(V2/'blind/CONVENTIONS.md'"
    extra='''        countref3=self.json(V3/'blind/adjudicated-counts.json',True)
        detections3=self.json(V3/'count-page-detections.json',True)
        dmap3={r['pdf_page']:r for r in detections3['pages']};counts3=[];countreadings3=[]
        for ref in countref3['pages']:
            page=ref['pdf_page'];images=[]
            for p in sorted((V3/'blind/page-count-source').glob(f'*{page}*')):
                if p.suffix=='.png':images.append(self.image(p,'images/counts/v3_'+p.name,'benchmark_count_pages_v3','page_count_context',page))
            det=[{k:r[k] for k in ['line_kind','row_anchor_y_2x','margin_pdf_box','glyph_pdf_box']} for r in dmap3[page]['rows']]
            counts3.append(dict(pdf_page=page,frame='random' if page in selection3['random_count_pages'] else 'stress',image_paths=images,
                reference_json=compact(ref),detections_json=compact(det),status='Frozen evaluation'))
        for letter in 'ab':
            path=V3/f'blind/reader-{letter}/counts.json';d=self.json(path,True)
            metadata.append(dict(benchmark='v3',reader=letter.upper(),kind='count',source_file=path.relative_to(ROOT).as_posix(),metadata={k:v for k,v in d.items() if k!='pages'}))
            for row in d['pages']:countreadings3.append(dict(pdf_page=row['pdf_page'],reader=letter.upper(),reading_json=compact(row),source_file=path.relative_to(ROOT).as_posix()))
        assert len(counts3)==21 and len(countreadings3)==42
        self.table('benchmark_count_pages_v3',counts3,license=MIXED_LICENSE,description='21 v3 pages: 18 fresh count pages and 3 stress pages; numbered and physical-line geometry.')
        self.table('benchmark_count_readings_v3',countreadings3,license=MIXED_LICENSE,description='42 v3 independent numbered/physical-line page inventories.')
        self.input(M/'evaluate_crop_v3.py','own-work','include-selected','Project-authored v3 physical-line recall rule; Unlicense.',['recall_page'])
        source=(M/'evaluate_crop_v3.py').read_text(encoding='utf8')
        section=source[source.index('def recall_page('):source.index('def count_summary(')]
        (self.out/'code/score_recall_v3.py').write_text(section,encoding='utf8')
        self.input(V3/'blind/CONVENTIONS.md')
        shutil.copyfile(V3/'blind/CONVENTIONS.md',self.out/'benchmark/CONVENTIONS-v3.md')
'''
    text=replace(text,anchor,extra+anchor)
    text=replace(text,"('v2',V2/'evaluation-2026-10-07-adjudicated/metrics.json')]:", "('v2',V2/'evaluation-2026-10-07-adjudicated/metrics.json'),('v3',V3/'evaluation-2026-10-08-adjudicated/metrics.json')]:")
    text=replace(text,"if version=='v2':expected[version]['source_row_recall']=d['source_row_recall']", "if version in ['v2','v3']:expected[version]['source_row_recall']=d['source_row_recall']\n            if version=='v3':expected[version]['physical_line_recall']=d['physical_line_recall']")
    text=replace(text,"        dump(self.out/'benchmark/expected-metrics.json',expected)", "        dump(self.out/'benchmark/expected-metrics.json',expected)\n        dump(self.out/'benchmark/v3-selection.json',self.portable.value(selection3))")
    text=replace(text,"(V2/'freeze-manifest.json','v2-freeze-manifest.json'),", "(V3/'blind/adjudication-notes.json','v3-adjudication-notes.json'),(V3/'freeze-manifest.json','v3-freeze-manifest.json'),(V3/'prediction-freeze.json','v3-prediction-freeze.json'),\n                (V2/'freeze-manifest.json','v2-freeze-manifest.json'),")
    text=text.replace("description='949 licensed PNGs", "description='Licensed PNGs")
    p.write_text(text,encoding='utf8')
    p=HERE/'extract_images.py';text=p.read_text(encoding='utf8')
    text=replace(text,"('benchmark_rows_v2',[('context_image_path','context_image'),('exact_image_path','exact_image')])", "('benchmark_rows_v2',[('context_image_path','context_image'),('exact_image_path','exact_image')]),\n                        ('benchmark_rows_v3',[('context_image_path','context_image'),('exact_image_path','exact_image')])")
    p.write_text(text,encoding='utf8')


if __name__=='__main__':main()
