"""Reviewer sensitivity check of the 1300-700 BCE gap (reads package files, writes only --output).

Imports the package's own coverage functions (amendment-2026-10-07-frenez/analyze_coverage.py) and the
amended evidence table, then recomputes the longest internal empty run of the A+B series restricted to
high/moderate calendar strength (the series behind the headline 600-year gap):
  (a) leave_one_out: with each row of that series removed;
  (b) promote_to_moderate: with each row that has a selected interval and low calendar strength
      promoted to grade B and moderate strength (rows without a selected interval are not changed);
  (c) whatif_pirak and whatif_pirak_grid: with the selected interval of the 'pirak' row replaced by reviewer
      scenarios for the two seals (Period II and Period IIIA), which start between 1500 and 1200 BCE and end
      between 1100 and 760 BCE (these scenarios illustrate sensitivity; they are not findings of date);
  (d) whatif_added_rows: with one extra row added for a marked context that the sources describe and the
      table lacks (Daimabad Phase V, Thulukkarpatti Period I, Sivagalai Period II, a wider Inamgaon range);
      the all-grade series (every grade and strength) is reported beside the two A+B series.
Run from the repository root:
  python experiments/2026-10-06-backward-chronology/review/gap_sensitivity.py --output <fresh directory>
"""
import argparse, copy, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-backward-chronology'
AMD = PKG / 'amendment-2026-10-07-frenez'

spec = importlib.util.spec_from_file_location('cov', AMD / 'analyze_coverage.py')
cov = importlib.util.module_from_spec(spec); spec.loader.exec_module(cov)

def gaps(rows):
    bins = [cov.cover(rows, lo, lo + 100) for lo in range(-3500, -200, 100)]
    out = {}
    for key in ['phase_or_historical_AB', 'high_moderate_calendar_AB', 'assemblages']:
        r = cov.empty_runs(bins, key)
        li = r['longest_internal']
        name = 'all_grades' if key == 'assemblages' else key
        out[name] = dict(longest_internal=(None if li is None else (li['start_year'], li['end_year'], li['years'])),
                         empty_runs=[(x['start_year'], x['end_year'], x['years'], x['internal']) for x in r['empty_runs']])
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output', required=True); a = ap.parse_args()
    out = Path(a.output).resolve()
    if out.exists(): ap.error('exists')
    rows = json.loads((AMD / 'evidence-table.json').read_text(encoding='utf-8'))['rows']
    base = gaps(rows)
    result = dict(baseline=base, leave_one_out=[], promote_to_moderate=[], notes=[])
    # (a) leave-one-out over rows in the high/moderate series
    for r in rows:
        ds = cov.selected(r)
        if cov.eligible(r) and ds and ds[0]['grade'] in 'AB' and ds[0]['calendar_strength'] in ('high', 'moderate'):
            rr = [x for x in rows if x['id'] != r['id']]
            g = gaps(rr)['high_moderate_calendar_AB']
            result['leave_one_out'].append(dict(row=r['id'], interval=(ds[0]['start_year'], ds[0]['end_year']),
                                                longest_internal_without=g['longest_internal'], empty_runs=g['empty_runs']))
    # (b) promote every selected A/B/C row currently low strength to moderate (B grade kept as is; C promoted to B)
    for r in rows:
        ds = cov.selected(r)
        if cov.eligible(r) and ds and ds[0]['calendar_strength'] == 'low':
            rr = copy.deepcopy(rows)
            for x in rr:
                if x['id'] == r['id']:
                    for d in x['dating_assessments']:
                        if d['selected_for_coverage']:
                            d['calendar_strength'] = 'moderate'; d['grade'] = 'B'
            g = gaps(rr)['high_moderate_calendar_AB']
            result['promote_to_moderate'].append(dict(row=r['id'], original=(ds[0]['start_year'], ds[0]['end_year'], ds[0]['grade'], ds[0]['calendar_strength']),
                                                      longest_internal_after=g['longest_internal']))
    # (c) what-if: re-date the Pirak row by the periods of its two seals (reviewer scenarios, not findings of date).
    # The row's own interval (1800-1300 BCE) is the span of Pirak Period I in a published review of the excavation
    # report (Dumarcay 1980); the seals come from Period II and Period IIIA. Period III began between about 1460
    # and 1150 BCE and ended between about 1300/1200 and 760 BCE (Magee and Petrie 2010 as cited by Petrie and
    # Magee 2012). The end of Period I is given as the 13th century BC (Dumarcay 1980) and, in a snippet of a
    # survey chapter (author unconfirmed), as about 1500 BC, so the scenarios for the seals start between 1500 and 1200 BCE.
    def with_pirak(lo,hi):
        rr=copy.deepcopy(rows)
        for x in rr:
            if x['id']=='pirak':
                for d in x['dating_assessments']:
                    if d['selected_for_coverage']:
                        d['start_year']=lo; d['end_year']=hi
        return rr
    result['whatif_pirak']=[]
    for lo,hi,why in [(-1500,-760,'envelope: earliest plausible start of Period II to the late end of Period III'),
                      (-1500,-1100,'both seals in the earlier part of that span'),
                      (-1400,-760,'intermediate start'),
                      (-1300,-760,'Period II starts where Period I ends (13th century BC, Dumarcay 1980); Period III ends at its late end'),
                      (-1300,-1100,'Period II start with an early end of Period III'),
                      (-1200,-760,'Period II starts at the late end of the 13th century BC; Period III ends at its late end')]:
        g=gaps(with_pirak(lo,hi))
        result['whatif_pirak'].append(dict(interval=(lo,hi),basis=why,
            longest_internal_high_moderate_AB=g['high_moderate_calendar_AB']['longest_internal'],
            empty_runs_high_moderate_AB=g['high_moderate_calendar_AB']['empty_runs'],
            longest_internal_AB_any_strength=g['phase_or_historical_AB']['longest_internal']))
    result['whatif_pirak_grid']=[]
    for lo in (-1500,-1400,-1300,-1200):
        for hi in (-1100,-1000,-900,-800,-760):
            g=gaps(with_pirak(lo,hi))['high_moderate_calendar_AB']
            result['whatif_pirak_grid'].append(dict(interval=(lo,hi),longest_internal=g['longest_internal'],empty_runs=g['empty_runs']))
    # (d) what-if: add rows for marked contexts that the sources describe but the table lacks (reviewer scenarios)
    result['whatif_added_rows']=[]
    template=copy.deepcopy([x for x in rows if x['id']=='daimabad-III'][0])
    def added(rid,lo,hi,grade,strength):
        x=copy.deepcopy(template); x['id']=rid; x['include_in_additive_coverage']=True; x['adjacent_region']=False
        x['marked_object_count']=None; x['count_kind']='unknown'
        x['dating_assessments']=[dict(start_year=lo,end_year=hi,method='reviewer scenario',grade=grade,calendar_strength=strength,selected_for_coverage=True,source_location='',note='',lab_numbers=[],published_measurement=None)]
        return x
    for rid,lo,hi,grade,strength,why in [
        ('daimabad-V',-1400,-1000,'B','low','Sali 1986 Phase V (Jorwe), conventional 1400-1000 BC, marked pottery (pp. 399-400), rated as the package rates Phases II and III'),
        ('daimabad-V',-1400,-1000,'B','moderate','the same row rated moderate'),
        ('thulukkarpatti-I',-900,-700,'C','low','Thulukkarpatti Period I, Iron Age 9th-7th century BCE, graffiti-bearing (Vol. I pp. 196, 201)'),
        ('sivagalai-II',-1200,-700,'C','low','Sivagalai cultural Period II, 12th-7th century BCE (Vol. I p. 192); habitation graffiti sherds are not assigned to periods'),
        ('inamgaon-alt',-1600,-700,'C','low','Inamgaon Early Jorwe 1600-700 BC (Sankalia), Kenoyer 2004')]:
        rr=copy.deepcopy(rows)+[added(rid,lo,hi,grade,strength)]
        g=gaps(rr)
        result['whatif_added_rows'].append(dict(row=rid,interval=(lo,hi),grade=grade,strength=strength,basis=why,
            longest_internal_high_moderate_AB=g['high_moderate_calendar_AB']['longest_internal'],
            longest_internal_AB_any_strength=g['phase_or_historical_AB']['longest_internal'],
            empty_runs_AB_any_strength=g['phase_or_historical_AB']['empty_runs'],
            longest_internal_all_grades=g['all_grades']['longest_internal'],
            empty_runs_all_grades=g['all_grades']['empty_runs']))
    out.mkdir(parents=True)
    (out / 'gap-sensitivity.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False)[:6000])

if __name__ == '__main__':
    main()
