"""Read a local plan-input record, compute bounds and show every successful reading."""
from pathlib import Path
import sys
import hashlib
import json
from fractions import Fraction

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[1]))
from measurement_math import metric_length

RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/mohenjo-control')
OUT = RAW / 'measured-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    inventory = json.loads((P/'INVENTORY-v1.json').read_text())
    pin = json.loads((P/'inputs-v1.json').read_text())
    detail = Path(pin['detail_physical_path'])
    assert sha(detail) == pin['sha256']
    inputs = {r['id']:r for r in json.loads(detail.read_text())['items']}
    rows = []
    checks = []
    panels = []
    for panel in inventory['inventory']:
        r = inputs[panel['id']]
        assert sha(panel['image_physical_path']) == panel['image_sha256']
        row = {k:panel[k] for k in ['id','pdf_index0','plate','phase_raw']}
        row.update(town='mohenjo-daro', source_id='MACKAY-VOL2',
                   feature='First Street beside Block 5, local transect',
                   phase_attribution='Source-level relative phase; XX combines Late Ia and II',
                   p1_wall_survival_eligible=False,
                   north_reference='Source N arrow, type unspecified; no true-north inference',
                   cross_panel_same_geodetic_transect=False)
        if r['feature'] is None:
            row.update(status='unmeasurable', estimate_m=None,
                       reading_lower_m=None, reading_upper_m=None,
                       missing_reason=r['missing_reason'])
        else:
            result = metric_length(r['feature'],r['bar'],r['bar_metres'],r['feature_radius_px'],r['bar_radius_px'])
            row.update(status='measured-local-chord', **result)
            # Separate exact rational calculation for a horizontal source chord.
            # The bar length is checked against squared integer coordinates.
            dx = r['bar'][1][0] - r['bar'][0][0]
            dy = r['bar'][1][1] - r['bar'][0][1]
            exact_feature = abs(r['feature'][1][0] - r['feature'][0][0])
            independent = float(Fraction(exact_feature * 1524,100)) / ((dx*dx + dy*dy)**.5)
            checks.append({'id':r['id'], 'estimate_independent_fraction_check':abs(independent-result['estimate_m']) < 1e-12})
            if r.get('alternative_feature'):
                alt = metric_length(r['alternative_feature'],r['bar'],r['bar_metres'],r['feature_radius_px'],r['bar_radius_px'])
                row.update(alternative_edge=alt, alternative_reason=r['alternative_reason'],
                           combined_reading_lower_m=min(result['reading_lower_m'],alt['reading_lower_m']),
                           combined_reading_upper_m=max(result['reading_upper_m'],alt['reading_upper_m']))
            image = Image.open(panel['image_physical_path'])
            w,h = image.size
            fig,axes = plt.subplots(1,2,figsize=(14,8.8),gridspec_kw={'width_ratios':[1.35,1]})
            for ax in axes:
                ax.imshow(image)
                ax.plot(*zip(*r['feature']),color='#B54932',linewidth=3,marker='o',markersize=5)
                if r.get('alternative_feature'):
                    ax.plot(*zip(*r['alternative_feature']),color='#D5A02E',linewidth=2,linestyle='--')
                ax.set_axis_off()
            axes[0].set_xlim(0,w);axes[0].set_ylim(h,0)
            fx=[point[0] for point in r['feature']];fy=r['feature'][0][1]
            axes[1].set_xlim(min(fx)-85,max(fx)+85);axes[1].set_ylim(fy+120,fy-120)
            axes[0].plot(*zip(*r['bar']),color='#197D82',linewidth=3,marker='o',markersize=4)
            axes[0].set_title('Original plan and scale reading',loc='left',fontsize=13)
            axes[1].set_title('Local bank-to-bank chord',loc='left',fontsize=13)
            fig.suptitle(f"Mohenjo-daro | {panel['phase_raw']} | Plate {panel['plate']}",x=.045,ha='left',fontsize=19,fontweight='bold',color='#183336')
            bounds=(row.get('combined_reading_lower_m',result['reading_lower_m']),row.get('combined_reading_upper_m',result['reading_upper_m']))
            fig.text(.045,.055,f"Reading: {result['estimate_m']:.2f} m; sensitivity {bounds[0]:.2f}–{bounds[1]:.2f} m. Original survey error is unknown.",fontsize=12)
            fig.text(.045,.025,'Mackay, Further Excavations at Mohenjo-daro, Vol. II. Source N type unspecified. Local-only attributed plan annotation.',fontsize=10,color='#53676B')
            fig.subplots_adjust(top=.87,bottom=.11,left=.035,right=.98,wspace=.06)
            path=OUT/(r['id'].lower()+'-overlay.png');fig.savefig(path,dpi=220,facecolor='white');plt.close(fig)
            panels.append({'id':r['id'],'physical_path':str(path),'sha256':sha(path),'title':f"First Street beside Block 5: {panel['phase_raw']}",
                           'source_id':'MACKAY-VOL2','locator':f"Vol. II plate {panel['plate']}, PDF index {panel['pdf_index0']}",
                           'kind':'Original plan with source-reading annotation','local_only':True})
        rows.append(row)
    measured=[r for r in rows if r['status']=='measured-local-chord']
    result={'status_class':'exploratory','rows':rows,'measured_local_chords':len(measured),'missing_chords':len(rows)-len(measured),
            'independent_episodes_for_p1':0,'continuous_access_demonstrated_from_widths':False,
            'scope':'Four source-plan chord readings. Different local frontages, shared source, no common-window wall-survival denominator. No calendar repair chronology or test of institutional cause.',
            'controls':checks,'passed':all(r['estimate_independent_fraction_check'] for r in checks),
            'inventory_sha256':sha(P/'INVENTORY-v1.json'),'detail_sha256':sha(detail),'code_sha256':sha(Path(__file__))}
    (P/'measurements.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (P/'plan-panels.json').write_text(json.dumps({'panels':panels},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'measured':len(measured),'missing':len(rows)-len(measured),'readings_m':[round(r['estimate_m'],3) for r in measured],'checks_passed':result['passed']},indent=2))


if __name__ == '__main__':
    main()
