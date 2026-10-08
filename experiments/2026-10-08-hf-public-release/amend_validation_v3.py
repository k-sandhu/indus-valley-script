"""Recorded one-time changes to include P and M v3 in the release checker."""
from pathlib import Path
from amend_release_v3 import replace
HERE=Path(__file__).resolve().parent

def main():
    p=HERE/'validate_release.py';text=p.read_text(encoding='utf8')
    text=replace(text,'RAW, M, V2, B, S','RAW, M, V2, V3, P, B, S')
    text=text.replace("['benchmark_rows_v1','benchmark_rows_v2']", "['benchmark_rows_v1','benchmark_rows_v2','benchmark_rows_v3']")
    text=replace(text,"chart=read(ROOT/'research/chart_reference/manual_numeric_reference.json')['rows']", "chart=read(P/'chart-reference-v2.1.json')['rows']")
    text=replace(text,"==16,'lower-code alternatives retained'", "==0,'all 16 earlier lower-code ambiguities provisionally settled'")
    text=replace(text,"    cov=read(S/'coverage.json')", """    from chart_changes import ChartChanges,cell_key
    changes=ChartChanges(read(ROOT/'research/chart_reference/manual_numeric_reference.json'),read(P/'chart-reference-v2.1.json'),read(P/'comparison-v2.1.json'),read(P/'impact-v2.1.json'))
    previous_ok=True
    for row in tables['chart_reference']:
        old=changes.old[row['cell_id']];changed=changes.changes.get(row['cell_id'],{})
        for key in ['code','rank','alternatives','rank_alternatives','numeric_confidence']:
            previous_ok=previous_ok and row['previous_'+key]==(old.get(key) if key in changed else None)
        previous_ok=previous_ok and set(row['changed_fields'])==set(changed) and bool(row['change_note'])==bool(changed)
    check('chart_previous_fields',previous_ok,'All five numeric previous-value columns and notes match P field deltas.')
    cov=read(S/'coverage.json')""")
    text=replace(text,"[('v1',M),('v2',V2)]", "[('v1',M),('v2',V2),('v3',V3)]")
    text=replace(text,"else V2/'predictions.json'", "else base/'predictions.json'")
    text=replace(text,"else:refs=read(V2/'blind/adjudicated-reference.json')['rows']", "else:refs=read(base/'blind/adjudicated-reference.json')['rows']")
    anchor="        check('benchmark_'+version+'_parent_records',ok,'Every substantive frozen reference, prediction and locator field matches; repository-only pointers use portable labels.')"
    text=replace(text,anchor,anchor+"""
        flags_ok=all(json.loads(r['reference_chart_correction_flags_json'])==changes.reference_flags(refs[r['sample_index']],version,True)
            and json.loads(r['prediction_chart_correction_flags_json'])==changes.prediction_flags(preds[r['sample_index']]) for r in rows)
        check('benchmark_'+version+'_chart_flags',flags_ok,'All unit flags match P explicit joins or template-key changed-cell joins; frozen payloads remain unchanged.')""")
    text=replace(text,"['benchmark_readings','benchmark_count_readings']", "['benchmark_readings','benchmark_readings_v3','benchmark_count_readings','benchmark_count_readings_v3']")
    text=text.replace("if config=='benchmark_readings'", "if config.startswith('benchmark_readings')")
    text=replace(text,"    scores={}\n", """    countref3=read(V3/'blind/adjudicated-counts.json')['pages'];detection3=read(V3/'count-page-detections.json')['pages']
    lookup3={r['pdf_page']:r for r in countref3};dlookup3={r['pdf_page']:r for r in detection3}
    keys=['line_kind','row_anchor_y_2x','margin_pdf_box','glyph_pdf_box']
    check('v3_count_page_parent_geometry',all(json.loads(r['reference_json'])==portable.value(lookup3[r['pdf_page']])
        and json.loads(r['detections_json'])==[{k:v[k] for k in keys} for v in dlookup3[r['pdf_page']]['rows']]
        for r in tables['benchmark_count_pages_v3']),'All 21 adjudicated page records and numbered/physical-line geometry fields.')
    check('v3_frame',read(release/'benchmark/v3-selection.json')==portable.value(read(V3/'blind/selection.json')),'Every selection field matches the frozen v3 packet.')
    old_pages={r['pdf_page'] for v in ['v1','v2'] for r in tables['benchmark_rows_'+v]}
    check('v3_fresh_target_pages',not old_pages.intersection(r['pdf_page'] for r in tables['benchmark_rows_v3']),'No v3 target page occurred among the earlier 140 benchmark targets.')
    scores={}
""")
    text=replace(text,"for version in ['v1','v2']:", "for version in ['v1','v2','v3']:")
    text=replace(text,"unverified=['Hosted dataset viewer and remote loading: no upload performed.'", "unverified=['Hosted 0.3.0 loading/viewer awaits coordinator update; coordinator reports 0.2.0 all 19 configs load.'")
    p.write_text(text,encoding='utf8')
    p=HERE/'check_review_fixes.py';text=p.read_text(encoding='utf8')
    start=text.index("    rows=pq.read_table(");end=text.index('    names={',start)
    block=text[start:end]
    block=block.replace("'benchmark_rows_v2.parquet'", "f'benchmark_rows_{version}.parquet'").replace("'--benchmark','v2'", "'--benchmark',version").replace("['v2']", "[version]")
    block=block.replace("    cases=[]\n",'')
    block=block.replace("(name+'.json')", "(version+'-'+name+'.json')").replace("(name+'-scores.json')", "(version+'-'+name+'-scores.json')").replace("(name+'.log')", "(version+'-'+name+'.log')")
    block=block.replace("dict(case=name", "dict(benchmark=version,case=name")
    text=text[:start]+"    cases=[]\n    for version in ['v2','v3']:\n"+'\n'.join('    '+line if line else '' for line in block.splitlines())+'\n'+text[end:]
    p.write_text(text,encoding='utf8')
    p=HERE/'rerun_review.py';text=p.read_text(encoding='utf8').replace('907 embedded PNGs','all embedded PNGs')
    # Retain original reviewer semantics; new validation checks v3 scores separately.
    p.write_text(text,encoding='utf8')

if __name__=='__main__':main()
