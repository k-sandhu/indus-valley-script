"""Render the current coverage and compare both preserved endpoints."""
import argparse, json
from pathlib import Path
OWN=Path(__file__).resolve().parent
PKG=OWN.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Choose a fresh output directory.')
    summaries=[read(PKG/'run-2026-10-07-03/summary.json'),read(PKG/'amendment-2026-10-07-frenez/run-01/summary.json'),read(OWN/'run-2026-10-07-04/summary.json')]
    bins=read(OWN/'run-2026-10-07-04/coverage.json')['bins']
    sens=read(OWN/'sensitivity-04/gap-sensitivity.json')
    ranges={}
    for strength in ['low','moderate']:
        vals=[s['gaps']['high_moderate_calendar_AB']['longest_internal']['years'] for s in sens['scenarios']if s['perumbalai_strength']==strength]
        ranges[strength]=dict(min_years=min(vals),max_years=max(vals))
    comparisons=[]
    for name,s in zip(['original','Frenez amendment','review correction'],summaries):
        comparisons.append(dict(endpoint=name,rows=s['inventory_rows'],sources=s['sources'],claims=s['continuity_claims'],dated_rows=s['dated_additive_rows_in_window'],grades=s['window_dating_grades'],high_moderate_gap=s['gaps']['high_moderate_calendar_AB']['longest_internal']))
    text=['# Century coverage, 7 October 2026','',
          'Status: Exploratory; arithmetic: Verified computation. The high/moderate A+B empty run ranges from **400 to 1,600 years** across 80 Pirak/Perumbalai scenarios. The current low ratings give 1,600 years (1900–300 BCE). With Perumbalai hypothetically moderate the range is 400–1,200 years; with it low the range is 400–1,600. Pirak’s date envelope and promotion to B/moderate are assumptions in those scenarios. Broad possible coverage has no empty bin; A+B at any strength has two 100-year empty bins.', '',
          'A is a direct secure association or historical anchor; B is an excavated phase association; C is a cultural, comparative or unresolved association; D is an unjoined comparator. Calendar strength is assessed separately. A selected broad interval contributes possible coverage to each overlapping century. Exact object bounds exclude site-wide counts without layer allocation. Bounds cannot be added across centuries. Image counts identify rows with an opened illustrated publication; they do not measure image quality or completeness.', '',
          'Each cell below is generated from `run-2026-10-07-04/coverage.json`, `bins`; the machine-readable row retains contributing identifiers. The three series and their controlling ratings are in `sensitivity-04/gap-sensitivity.json`.', '',
          '| BCE interval | All assessments | A+B | A+B high/moderate | A | B | C | Illustrated rows | Exact objects lower–possible upper | Unknown counts | Unaligned/other counts |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for b in bins:
        vals=[b['label'],b['assemblages'],b['phase_or_historical_AB'],b['high_moderate_calendar_AB'],b['grade_A'],b['grade_B'],b['grade_C'],b['assemblages_with_verified_images'],f"{b['exact_objects_assignable_lower']}–{b['exact_objects_possible_upper']}",b['unknown_object_count_assemblages'],b['non_object_or_unaligned_count_assemblages']]
        text.append('| '+' | '.join(map(str,vals))+' |')
    text+=['','A-only has no internal empty run: its 3,200-year zero-coverage interval begins at the window edge and ends at 300 BCE. It is not a bracket between two A assemblages.','',
           '| Region | Inventory rows | Dated contributing rows | Rows with images | Exact count rows in coverage |','|---|---:|---:|---:|---:|']
    for r in summaries[-1]['regions']:
        text.append('| '+' | '.join(map(str,[r['region'],r['inventory_rows'],r['dated_additive_rows_in_window'],r['rows_with_verified_images'],r['known_exact_object_count_rows']]))+' |')
    text+=['','The Indus northwest has 12 dated contributing rows; South India has 8. Their dating grades and strengths differ, and broad site phases do not establish an uninterrupted sign lineage. Regional empty runs are retained in `run-2026-10-07-04/regional-gaps.json`.','']
    out.mkdir(parents=True)
    (out/'COVERAGE.md').write_text('\n'.join(text),encoding='utf-8')
    (out/'comparison.json').write_text(json.dumps(dict(status='Exploratory',endpoints=comparisons,sensitivity_by_perumbalai_strength=ranges),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(bins=len(bins),perumbalai_ranges=ranges)))
if __name__=='__main__':main()
