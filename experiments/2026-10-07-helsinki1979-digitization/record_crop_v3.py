"""Compare reused v2 development targets and retain readers' exact crop observations."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import numpy as np
import evaluate as E

HERE=Path(__file__).resolve().parent
V2=HERE/'repair/2026-10-07-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def tags(text):
    result=[];s=text.lower()
    if ('underline' in s or 'dash' in s) and any(w in s for w in ['own','target','excluded','below','missing','bottom','cut off']):result.append('own_underline_missing_or_cut')
    if any(w in s for w in ['above','below','neighbour','neighbor','previous','following','next row']):result.append('neighbour_ink')
    if any(w in s for w in ['number','digit','classification','field']):result.append('number_or_classification_ink')
    if any(w in s for w in ['drawing','sign','figure','glyph','stroke','patch']) and any(w in s for w in ['cut','clip','excluded','missing','truncat']):result.append('drawing_cut')
    return result or ['other_or_unclear']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--development',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    devpath=args.development.resolve();out=args.out.resolve()
    if not devpath.is_relative_to(HERE) or not out.is_relative_to(HERE) or out.exists():raise ValueError('Use owned development and a new output')
    dev=read(devpath);v2=read(V2/'evaluation-2026-10-07-adjudicated/metrics.json');refs={r['sample_index']:r for r in read(V2/'blind/adjudicated-reference.json')['rows']}
    rejected=[r['sample_index'] for r in v2['rows'] if not r['crop_correct']]
    first_crop=[r['sample_index'] for r in v2['rows'] if not r['crop_correct'] and not r['strict_top5']['whole_row_compatible']]
    assert len(rejected)==36 and len(first_crop)==34 and len(dev['rows'])==80 and dev['code_unchanged_during_run']
    observations=[];groups={}
    for reader in ['a','b']:
        found=[]
        for p in sorted((V2/'blind'/f'reader-{reader}').glob('rows*.json')):
            for row in read(p)['rows']:
                if row['sample_index'] not in rejected:continue
                for tag in row.get('crop_issues',[]):
                    family=tags(tag);found.append((row['sample_index'],family))
                    observations.append(dict(reader=reader,sample_index=row['sample_index'],verbatim_crop_issue=tag,families=family,
                        source=f'{p.relative_to(HERE).as_posix()}: rows[sample_index={row["sample_index"]}].crop_issues'))
        groups[reader]={name:sorted({i for i,fs in found if name in fs}) for name in sorted({f for i,fs in found for f in fs})}
    rows=dev['scored_rows'];by_section={}
    sections={r['sample_index']:r['section'] for r in dev['rows']}
    for s in sorted(set(sections.values())):by_section[s]=E.aggregate([r for r in rows if sections[r['sample_index']]==s])
    repairs=[]
    for i in [3,25,50,52,58]:
        r=next(r for r in rows if r['sample_index']==i)
        repairs.append(dict(sample_index=i,pdf_page=r['pdf_page'],count_agrees=r['count_agrees'],top5_whole_row=r['strict_top5']['whole_row_compatible'],
            reference_units=r['reference_count'],proposed_units=r['predicted_count']))
    rng=np.random.default_rng(2026100882);boot=[]
    for _ in range(2000):
        a=E.aggregate([rows[i] for i in rng.integers(0,80,80)])
        boot.append([a['strict_top1']['aligned_recall']['rate'],a['strict_top5']['aligned_recall']['rate'],a['calibration']['brier'],a['calibration']['ece10']])
    names=['unit_top1_aligned','unit_top5_aligned','calibration_brier','calibration_ece10']
    result=dict(status='Exploratory',development_only=True,all_v2_targets_reused=80,new_reference_created=False,
        inputs=dict(development=devpath.relative_to(HERE).as_posix(),development_sha256=E.sha(devpath),v2_metrics_sha256=E.sha(V2/'evaluation-2026-10-07-adjudicated/metrics.json'),
            reference_sha256=E.sha(V2/'blind/adjudicated-reference.json')),
        v2_rejected_crops=rejected,v2_top5_failure_starts_at_crop=first_crop,
        distinction='36 crop rejections in all 80 targets; 34 crop rejections among the 40 incompatible top-five rows.',
        crop_issue_observations=observations,crop_issue_family_rows_per_reader=groups,
        tag_classification='Overlapping text-search families for finding observations; exact reader strings retained. No new crop correctness reference is inferred.',
        method_repairs=['Remove clipped components at field-search edges before field pairing','Fit repeated classification bounds per page column',
            'Mask every column field and clamp row padding inside glyph-column bounds','Own glyph components and dashed underlines by source anchors',
            'Separate continuation lines with provisional preceding-number ownership','Remove underlines for body segmentation and restore their whole slots for matching',
            'Retain loss-rectangle strokes; separate short ticks next to tall drawings'],
        development_summary=dev['summary'],development_by_section=by_section,
        development_intervals={name:np.nanquantile(np.array(boot)[:,i],[.025,.975]).tolist() for i,name in enumerate(names)},
        interval_note='Wilson and row bootstrap describe reused development rows; parameter selection prevents a held-out accuracy interpretation.',
        prior_five_segmentation_underline_failures=repairs,
        development_numbered_recall=dev['development_numbered_row_recall'],development_count_pages=dev['development_count_pages'],
        unresolved_crop_accuracy='No new independent crop labels on the development boxes; crop acceptance is reserved for the fresh blind evaluation.',
        reference_process='Earlier adjudicated v2 reference reused unchanged; no fresh reader or adjudicator invoked by this package.')
    out.mkdir(parents=True);(out/'diagnosis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(development_summary=dev['summary'],repairs=repairs,numbered_recall=dev['development_numbered_row_recall'])))
if __name__=='__main__':main()
