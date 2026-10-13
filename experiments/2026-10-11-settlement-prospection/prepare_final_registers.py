"""Apply the targeted second-review repairs in new, preserved versions."""
from pathlib import Path
from datetime import datetime, timezone
import json

BASE=Path(__file__).resolve().parent

def new(path, obj):
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    s=json.loads((BASE/'sources-v4.json').read_text(encoding='utf-8'))
    rows={r['id']:r for r in s['sources']}
    rows['R07']['observation']='December2015total-station/cultural-material survey gives66.7ha; discusses older81.5ha estimate and uncertain boundary procedure. The33ha visible-mound estimate is R08, not this source.'
    rows['R08']['observation']+=' Discussion “Villages and Towns: Mound Size Estimates,” paragraph beginning “Our data suggest,” directly reports Ganweriwala mounded area circa33ha in the2020paper.'
    rows['R41']['observation']+=' Government inventory coordinate26.454762389N67.464134722E lies inside revised P18northbound26.6. This is the inventory point, not a newly surveyed location.'
    rows['R21']['observation']+=' Official account describes construction disturbance in four2017trenches and deep modern pits mixing ancient material with modern garbage; lower contexts preserve archaeological associations locally.'
    # Optional first-source lineage addendum, authored by the source-check pass.
    history=BASE/'research/history-source-addendum.json'
    if history.exists():
        note=json.loads(history.read_text(encoding='utf-8'))
        r=note.get('source',note.get('sources',[{}])[0])
        if r.get('raw_witness'):
            rows['R01']['raw_witness']=r['raw_witness']
        if r.get('access_depth'):
            rows['R01']['access_depth']=r['access_depth']
        if r.get('locator'):
            rows['R01']['locator']=r['locator']
        if r.get('observation'):
            rows['R01']['observation']=r['observation']
    from revise_registers import prose_spacing
    for r in s['sources']:
        for k in ('observation','locator','access_depth'):
            r[k]=prose_spacing(r[k])
    s.update(version='v5',preceding_version='sources-v4.json',authored_utc=datetime.now(timezone.utc).isoformat(),
       revision_basis='Claude second-pass locator/documentation findings and primary rechecks; numeric observations unchanged',
       local_witness_count=sum(bool(r.get('raw_witness')) for r in s['sources']))
    new(BASE/'sources-v5.json',s)

    c=json.loads((BASE/'candidates-v3.json').read_text(encoding='utf-8'))
    c.update(version='v4',preceding_version='candidates-v3.json',
       assessment_author='Editorial judgments of the AI-assisted drafting/research process; not elicited archaeological expert ratings',
       assessment_rubric={
        'information':{'I2':'Documented archaeology or a published candidate/record ambiguity with a specific discriminating comparison',
                       'I1':'Regional process or connection worth testing but local dating/frame remains incomplete',
                       'I0':'Mechanism-only lead without adequate local archaeological or chronological connection'},
        'preservation_evidence':{'P2':'A source documents surviving archaeological contexts somewhere in this region; untested parcels remain unknown',
                                 'P1':'Regional formation/visibility process is documented; target-horizon survival at proposed units remains unknown',
                                 'P0':'Local target-horizon preservation and environmental chronology are not established'},
        'feasibility':{'F0':'Current project-data/parcel access and field permissions unverified',
                       'F1':'Data and named partner confirmed, but intervention/access not fully cleared',
                       'F2':'Relevant access, intervention and conservation arrangements confirmed'}},
       shared_frame_rule='A1km²cell eligible under more than one region belongs to one shared frame, carries every applicable label and is selected once. Correlated contexts remain together. P02known-margin transects are excluded from P01negative draws. Other overlaps follow this same shared-frame rule.',
       review_basis=c['review_basis']+['Claude second targeted review V2-F1–V2-F12'])
    rules={
     'P06':'Demote the tested surface-survival premise where adequate logs establish scour/truncation of the target-age interval or show only younger terrestrial ground was available; older substrate alone leaves later use unresolved.',
     'P07':'Demote a contemporaneous catchment-link prediction if independent context dates show different periods. Demote an off-mound concentration prediction only if equal-effort comparison has adequate sensitivity and precision to exclude the proposed excess.',
     'P09':'Demote contemporaneous active-channel use supplying an occupation if adequately constrained activity and occupation intervals do not overlap. Earlier abandonment does not reject later occupation of the channel margin; a later fill date alone can postdate use.',
     'P13':'Test phase-specific exterior extent: demote a proposed contemporaneous fort/exterior footprint if dated contexts differ or adequate boundary tests contradict its predicted extent. Kotada/Morodharo identity is already resolved in R19.',
     'P14':'Demote an ancient-occupation interpretation if adequate dated deposits support recent wetness or natural sediments. Demote only the Indus attribution if dated cultural deposits belong to another period.',
    }
    p2={'P02','P07','P10','P12','P13','P18'}
    p0={'P11','P14','P21'}
    for t in c['targets']:
        if t['id'] in rules:
            t['demotion_rule']=rules[t['id']]
            t['falsification_test']=rules[t['id']]
        info='I2' if t['information_value'].startswith('High') else 'I1'
        if t['id']=='P18':
            t['component_information_levels']={'piedmont':'I2','cave_attribution':'I0'}
        t.update(information_level=info,preservation_evidence_level='P2' if t['id'] in p2 else 'P0' if t['id'] in p0 else 'P1',
                 feasibility_level='F0',feasibility_assessment='Current data/partner/parcel/permit access unverified; next-action prerequisites remain explicit')
        for k,v in list(t.items()):
            if isinstance(v,str):
                t[k]=v.rstrip().rstrip('.')+'.' if k in ('demotion_rule','falsification_test') else v
    new(BASE/'candidates-v4.json',c)
    print(json.dumps(dict(sources=len(s['sources']),local_witnesses=s['local_witness_count'],regions=len(c['targets']))))

if __name__=='__main__':main()
