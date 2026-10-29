"""Build a local, source-linked graphic atlas from the frozen Q-1032 register."""
from __future__ import annotations
import collections
import hashlib
import html
import json
import math
import os
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parents[1]
LOCAL = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-axis-visual-atlas')
RUN = sys.argv[1] if len(sys.argv) > 1 else 'run-v1'
OUT = LOCAL / RUN
if (ROOT / 'data/raw').resolve() != Path('D:/projects/indus_valley_script/data/raw').resolve():
    raise RuntimeError('The D: raw-data junction is unavailable')
OUT.mkdir(parents=True, exist_ok=False)
os.environ['MPLCONFIGDIR'] = str(OUT / 'build/matplotlib')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, Wedge
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

BG, INK, MUTED = '#F7F4ED', '#182C30', '#59686A'
TEAL, RUST, BLUE, GREY = '#207D80', '#BA573B', '#4C7197', '#C6CBC5'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'text.color':INK,
    'axes.labelcolor':INK,'axes.edgecolor':GREY,'xtick.color':MUTED,'ytick.color':MUTED,
    'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,
    'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':21,
    'axes.labelsize':16,'xtick.labelsize':13,'ytick.labelsize':14,
    'svg.fonttype':'none','pdf.fonttype':42,'axes.unicode_minus':True})
for d in ['png','svg','pdf','thumbs','build']:
    (OUT/d).mkdir(parents=True,exist_ok=True)
(OUT/'build/build_atlas.py').write_bytes(Path(__file__).read_bytes())

INPUTS = {}
FIGURES = []
EXPECTED_HASHES = {}
SOURCE_PREFIX = 'experiments/2026-10-24-q1032-town-axis-register/'

def record(relative):
    p = ROOT / relative
    if relative not in INPUTS:
        b = p.read_bytes()
        expected=EXPECTED_HASHES.get(str(p.resolve()).lower().replace('\\','/'))
        if expected and hashlib.sha256(b).hexdigest()!=expected:
            raise ValueError('Held source hash changed: '+relative)
        INPUTS[relative] = {'logical_path':relative,'physical_path':str(p.resolve()),
            'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    return p

def load(relative):
    return json.loads(record(relative).read_text(encoding='utf-8'))

def jsonl(relative):
    return [json.loads(s) for s in record(relative).read_text(encoding='utf-8').splitlines() if s]

towns = load(SOURCE_PREFIX+'run-v5/town-axis-table.json')['towns']
coverage = load(SOURCE_PREFIX+'run-v5/coverage.json')
measurements = jsonl(SOURCE_PREFIX+'run-v5/measurements.jsonl')
published = load(SOURCE_PREFIX+'run-v5/published-wanzke.json')
repaired = load(SOURCE_PREFIX+'horizon-repair-v1/horizons.json')
horizons = jsonl(SOURCE_PREFIX+'run-v5/horizons.jsonl')
picks = load(SOURCE_PREFIX+'new-observations.json')
rc = jsonl(SOURCE_PREFIX+'run-v5/radiocarbon.jsonl')
comparison = load('experiments/2026-10-21-town-orientations-verification/comparison-v3/comparison.json')
transforms = load(SOURCE_PREFIX+'TRANSFORMS.json')
for item in transforms['local_visual_artifacts']:
    EXPECTED_HASHES[str(Path(item['physical_path'])).lower().replace('\\','/')]=item['sha256']
    if item.get('parent') and item.get('parent_sha256'):
        EXPECTED_HASHES[str((ROOT/item['parent']).resolve()).lower().replace('\\','/')]=item['parent_sha256']
record(SOURCE_PREFIX+'REPORT.md')
record('experiments/2026-10-21-plan-registration/REPORT.md')
required = [r for r in towns if r['required']]
new_lines = [r for r in measurements if r['measurement_id'].startswith('new-surkotada:')]
usable_records = [r for r in horizons if r['usable_at_corrected_site']]
usable = list({r['town']:r for r in usable_records}.values())
assert len(towns)==34 and len(required)==11 and len(usable)==20 and len(new_lines)==2

def name(slug):
    return slug.replace('-', ' ').title().replace('Mohenjo Daro','Mohenjo-daro').replace('Chanhu Daro','Chanhu-daro').replace('Sutkagen Dor','Sutkagen-dor')

WREF = 'Wanzke (1987), Axis Systems and Orientation at Mohenjo-Daro, pp. 33-44.'
JREF = 'Joshi (1990), Excavation at Surkotada 1971-72 and Exploration in Kutch, Fig. 8, PDF index 61.'
RCREF = 'Agrawal & Kusumgar (1973), Tata Institute Radiocarbon Date List X, pp. 579-580. DOI: 10.1017/S0033822200009024.'
DREF = 'Copernicus DEM GLO-30/GLO-90. DLR / Airbus, provided under COPERNICUS by EU and ESA. All rights reserved.'
TREF = 'Q-1032 register, run-v5/town-axis-table.json. Counts retain repeated source and observer assertions.'
MREF = 'Q-1032 register, run-v5/measurements.jsonl. Records include repeated readings and source products.'

def base(title,subtitle='',size=(16,10),rect=(.10,.22,.84,.57)):
    fig=plt.figure(figsize=size)
    fig.text(.055,.935,title,fontsize=29,fontweight='bold',va='top')
    if subtitle: fig.text(.055,.875,subtitle,fontsize=16,color=MUTED,va='top')
    ax=fig.add_axes(rect)
    return fig,ax

def footer(fig,caption,source):
    fig.text(.055,.135,'\n'.join(textwrap.wrap(caption,145)),fontsize=12,va='top',linespacing=1.45)
    fig.text(.055,.055,'\n'.join(textwrap.wrap(source,165)),fontsize=10,color=MUTED,va='top',linespacing=1.3)

def finish(fig,slug,title,group,caption,source,refs,rights='own-work',transform=None):
    i=len(FIGURES)+1
    stem=f'{i:02d}-{slug}'
    footer(fig,caption,source)
    paths={}
    for fmt in ('png','svg','pdf'):
        p=OUT/fmt/(stem+'.'+fmt)
        fig.savefig(p,dpi=190)
        paths[fmt]=str(p)
    plt.close(fig)
    im=Image.open(paths['png']).convert('RGB')
    im.thumbnail((640,440),Image.Resampling.LANCZOS)
    im.save(OUT/'thumbs'/f'{stem}.jpg',quality=88)
    row={'number':i,'slug':stem,'title':title,'group':group,'caption':caption,'source':source,
        'source_records':refs,'rights_status':rights,'handling':'local-only','paths':paths}
    if transform: row['transformation']=transform
    FIGURES.append(row)
    print(f'{i:02d} {title}',flush=True)

def bar_labels(ax,values,offset=.3,fmt='{:.0f}'):
    for y,v in enumerate(values): ax.text(v+offset,y,fmt.format(v),va='center',fontsize=14,fontweight='bold')

def horizontal(ax,labels,values,col=TEAL):
    ax.barh(np.arange(len(labels)),values,color=col,height=.62)
    ax.set_yticks(np.arange(len(labels)),labels)
    ax.invert_yaxis();ax.set_axisbelow(True);ax.grid(axis='x',color=GREY,alpha=.5,linewidth=.6)
    ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)

def image_array(relative):
    return np.asarray(Image.open(record(relative)).convert('RGB'))

# 01. A coordinate plot rather than an unverified reconstructed landscape.
fig,ax=base('The 34-town search frame','Site-index coordinates. The eleven required towns carry labels.',rect=(.12,.24,.76,.55))
located=[t for t in towns if t['latitude'] is not None and t['longitude'] is not None]
ax.scatter([t['longitude'] for t in located],[t['latitude'] for t in located],s=55,c=GREY,zorder=2)
offsets={'mohenjo-daro':(-15,-24),'chanhu-daro':(15,-22),'harappa':(8,10),'kalibangan':(-125,20),
 'banawali':(10,32),'rakhigarhi':(22,-5),'lothal':(12,-25),'dholavira':(-140,32),
 'surkotada':(20,24),'kanmer':(28,-10),'shikarpur':(-130,-33)}
for t in required:
    x,y=t['longitude'],t['latitude'];ax.scatter(x,y,s=110,c=TEAL,zorder=3)
    ax.annotate(name(t['town']),(x,y),xytext=offsets[t['town']],textcoords='offset points',fontsize=13,
        arrowprops={'arrowstyle':'-','color':MUTED,'lw':.7})
ax.set(xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)',xlim=(60.7,78.2),ylim=(21.1,32.2))
ax.set_aspect(1/math.cos(math.radians(26)))
ax.grid(color=GREY,alpha=.5,linewidth=.6)
finish(fig,'town-locations','The 34-town search frame','Coverage',
 '33 candidate locations appear. Gola Dhoro has no accepted site point. These are index coordinates with differing source quality; no ancient coast or river course is reconstructed.',TREF,[SOURCE_PREFIX+'run-v5/town-axis-table.json#/towns'])

# 02. Availability matrix.
fig,ax=base('Where the register has evidence','A filled cell indicates availability, with source-specific limits retained.',size=(16,12),rect=(.23,.20,.58,.60))
matrix=np.array([[t['imagery_lines']>0,t['plan_lines']>0,t['missing']['horizon'] is None] for t in towns])
ax.imshow(matrix,aspect='auto',cmap=colors.ListedColormap([BG,TEAL]),vmin=0,vmax=1)
ax.set_yticks(range(34),[name(t['town'])+(' *' if t['required'] else '') for t in towns],fontsize=11)
ax.set_xticks(range(3),['Direct image lines','Plan lines','Usable modern horizon'],fontsize=14)
ax.set_yticks(np.arange(-.5,34,1),minor=True);ax.set_xticks(np.arange(-.5,3,1),minor=True)
ax.grid(which='minor',color=GREY,linewidth=.5);ax.tick_params(which='both',length=0)
finish(fig,'coverage-matrix','Where the register has evidence','Coverage','* Required town. The categories overlap. Twenty towns have a usable modern profile, without a complete horizon error budget.',TREF,[SOURCE_PREFIX+'run-v5/town-axis-table.json#/towns'])

# 03. Shared-denominator coverage.
fig,ax=base('Evidence coverage across 34 towns','Availability is a different question from accuracy or independence.',rect=(.27,.25,.60,.52))
vals=[6,24,20];labs=['Direct imagery','Plans','Usable modern horizons']
horizontal(ax,labs,vals);bar_labels(ax,vals,.4)
ax.set(xlim=(0,37),xlabel='Towns with evidence');ax.set_xticks([0,10,20,30,34])
finish(fig,'coverage-counts','Evidence coverage across 34 towns','Coverage','All eleven required towns enter the register. Thirteen towns have no horizon profile, and Gola Dhoro has an excluded profile at an unverified point.','Q-1032 register, run-v5/coverage.json.',[SOURCE_PREFIX+'run-v5/coverage.json'])

# 04. Required-town line counts, preserving different units.
fig,ax=base('Image and plan lines at the required towns','Repeated source and observer readings remain separate records.',rect=(.22,.24,.67,.55))
y=np.arange(11)
ax.barh(y-.17,[t['imagery_lines'] for t in required],height=.31,color=TEAL,label='Image lines')
ax.barh(y+.17,[t['plan_lines'] for t in required],height=.31,color=RUST,label='Plan lines')
ax.set_yticks(y,[name(t['town']) for t in required]);ax.invert_yaxis();ax.set_xlabel('Line records')
ax.legend(frameon=False,loc='lower right');ax.grid(axis='x',color=GREY,alpha=.5);ax.set_axisbelow(True)
finish(fig,'required-town-lines','Image and plan lines at the required towns','Coverage','A high record count can reflect several observers or many parts. It does not rank towns by evidence quality. Rakhigarhi has dating assertions but no measured lines in this register.',TREF,[SOURCE_PREFIX+'run-v5/town-axis-table.json#/towns'])

# 05. Explicit reasons for absent or conflicting fields.
gap_fields=[('two_independent_imagery_sources','Validated independent imagery'),('horizon_sigma','Horizon uncertainty budget'),('layout_boundary','Dated construction boundary'),('bayesian_start','Bayesian construction start'),('exact_wall_coordinate','Surveyed wall coordinate'),('plan_true_north','Plan tied to true north'),('horizon','Usable modern horizon'),('coordinates','Resolved site coordinate')]
gap_counts=[sum(t['missing'].get(k) is not None for t in towns) for k,_ in gap_fields]
assert sum(gap_counts)==218
fig,ax=base('The next evidence to acquire','Number of towns with a missing or conflicting field.',rect=(.35,.25,.53,.53))
horizontal(ax,[l for _,l in gap_fields],gap_counts);bar_labels(ax,gap_counts,.35);ax.set(xlim=(0,38),xlabel='Towns needing this evidence')
finish(fig,'field-gaps','The next evidence to acquire','Coverage','218 town-field gaps retain reasons. The imagery field requires different products, matched walls and validated errors. Its count does not mean that every town lacks imagery.',TREF,[SOURCE_PREFIX+'run-v5/missing-fields.csv'])

# 06. North labels apply to measurement records, not independent towns.
counts=collections.Counter(m['north_reference'] for m in measurements)
fig,ax=base('What north means in the measurement register','Every line and system retains its original north classification.',rect=(.22,.28,.65,.48))
labs=['True north','Magnetic north','Unspecified north'];vals=[counts[k] for k in ['true','magnetic','unspecified']]
horizontal(ax,labs,vals,col=[TEAL,BLUE,GREY]);bar_labels(ax,vals,8);ax.set(xlim=(0,1050),xlabel='Line and system records')
finish(fig,'north-references','What north means in the measurement register','Methods','1,380 line and system records include repeat readings. An arrow labelled only N remains unspecified. A reported precision does not establish which north the source uses.',MREF,[SOURCE_PREFIX+'run-v5/measurements.jsonl'])

# 07. Record types.
fig,ax=base('How the 1,380 measurement records enter','Line observations and combined systems have different roles.',rect=(.25,.28,.61,.48))
kinds=['plan','imagery','registered-plan','unknown'];labels=['Plan','Imagery','Registered plan','Source kind unknown']
line=[sum(m['source_kind']==k and m['level']=='line' for m in measurements) for k in kinds]
systems=[sum(m['source_kind']==k and m['level']=='system' for m in measurements) for k in kinds]
ax.barh(np.arange(4),line,color=TEAL,label='Lines');ax.barh(np.arange(4),systems,left=line,color=RUST,label='Systems')
ax.set_yticks(range(4),labels);ax.invert_yaxis();ax.set_xlabel('Records');ax.legend(frameon=False)
for i,(a,b) in enumerate(zip(line,systems)):ax.text(a+b+8,i,str(a+b),va='center',fontweight='bold')
ax.set_xlim(0,1270)
finish(fig,'measurement-record-types','How the 1,380 measurement records enter','Methods','The 28 registered-plan records retain the plan-registration study\'s failed frozen validation. Repeated observers on one image do not provide independent georeferencing.',MREF,[SOURCE_PREFIX+'run-v5/measurements.jsonl'])

# 08. All seventeen architectural axes in Wanzke p.33.
md=[r for r in published['rows'] if r['town']=='mohenjo-daro' and r['printed_page']==33]
assert len(md)==17
md=sorted(md,key=lambda r:r['deviation_deg'])
fig,ax=base('Seventeen published Mohenjo-daro axes','True-north survey, printed page 33. One gon equals 0.9 degrees.',size=(16,12),rect=(.36,.22,.50,.57))
ax.scatter([r['deviation_deg'] for r in md],np.arange(17),s=85,c=[TEAL if 'Moneer' in r['part'] else RUST for r in md],zorder=3)
ax.axvline(0,color=MUTED,lw=.8);ax.set_yticks(range(17),[r['part'] for r in md],fontsize=12);ax.invert_yaxis()
for i,r in enumerate(md):ax.text(r['deviation_deg']+.15,i,f"{r['deviation_deg']:+.2f}°",va='center',fontsize=12)
ax.set(xlim=(-1.2,10.7),xlabel='Deviation from the nearest cardinal axis (degrees)');ax.grid(axis='x',color=GREY,alpha=.45)
finish(fig,'mohenjo-daro-17-axes','Seventeen published Mohenjo-daro axes','Bearings','The Moneer axes lie near cardinal. Several street and monumental axes turn clockwise. Wanzke reports no one-sigma errors for these seventeen rows.',WREF+' Printed p. 33 = zero-based PDF index 35.',[SOURCE_PREFIX+'run-v5/published-wanzke.json#/rows'])

# 09. Accurate-angle diagrams, with no layout reconstruction.
fig=plt.figure(figsize=(16,10));fig.text(.055,.935,'Different axes within one town',fontsize=29,fontweight='bold');fig.text(.055,.875,'Measured angles drawn to scale. Segment positions and lengths are schematic.',fontsize=16,color=MUTED)
examples=[next(r for r in md if r['part']==k) for k in ['Moneer N-S 5','Moneer N-S 6','HR First Street']]
for i,r in enumerate(examples):
    ax=fig.add_axes((.07+i*.31,.27,.27,.51));ax.set_aspect('equal');ax.set_xlim(-1.2,1.2);ax.set_ylim(-1.2,1.3);ax.axis('off')
    ax.add_patch(Circle((0,0),1,fill=False,ec=GREY,lw=1));ax.plot([0,0],[-1.02,1.02],color=GREY,lw=1);ax.plot([-1.02,1.02],[0,0],color=GREY,lw=1)
    theta=math.radians(r['deviation_deg']);x,y=math.sin(theta),math.cos(theta)
    ax.plot([-x,x],[-y,y],color=TEAL if i<2 else RUST,lw=5)
    ax.text(0,1.12,'True N',ha='center',fontsize=14);ax.text(0,-1.23,r['part'],ha='center',fontsize=16)
    ax.text(0,-1.47,f"{r['deviation_deg']:+.2f}°",ha='center',fontsize=22,fontweight='bold',clip_on=False)
finish(fig,'mohenjo-daro-directions','Different axes within one town','Bearings','These diagrams compare direction alone. They do not reconstruct the relative locations of the walls. The source gives no one-sigma errors for these rows.',WREF+' p. 33.',[SOURCE_PREFIX+'run-v5/published-wanzke.json#/rows'])

# 10. Topographical-axis bounds remain bounds.
topo=[r for r in published['rows'] if r['town']=='mohenjo-daro' and r['printed_page']==34]
fig,ax=base('Published topographical axes','Wanzke describes these as topographical axes or possible buried streets.',rect=(.38,.25,.48,.52))
ax.errorbar([r['deviation_deg'] for r in topo],np.arange(7),xerr=[r['error_bound_deg'] for r in topo],fmt='o',color=TEAL,markersize=9,capsize=7,elinewidth=2)
ax.set_yticks(range(7),[textwrap.fill(r['part'],31) for r in topo],fontsize=13);ax.invert_yaxis();ax.axvline(0,color=MUTED,lw=.8)
ax.set(xlim=(-1.7,12),xlabel='Deviation from the nearest cardinal axis (degrees)');ax.grid(axis='x',color=GREY,alpha=.45)
finish(fig,'topographical-axis-bounds','Published topographical axes','Bearings','The bars show the stated possible error of ±1 gon, or ±0.9 degrees. They are error bounds, not one-sigma intervals. Reported lengths range from 240 to 1,000 m.',WREF+' p. 34, PDF index 36.',[SOURCE_PREFIX+'run-v5/published-wanzke.json#/rows'])

# 11. Other towns retain unspecified north and a reported range.
other=[r for r in published['rows'] if r['town']!='mohenjo-daro']
fig,ax=base('Other towns in Wanzke’s comparison','The source explicitly leaves north definition and precision unknown.',rect=(.32,.24,.54,.55))
for i,r in enumerate(other):
    if r['deviation_interval_deg']:
        lo,hi=r['deviation_interval_deg'];ax.plot([lo,hi],[i,i],color=RUST,lw=5);ax.plot([lo,hi],[i,i],'|',color=RUST,ms=14)
    else:ax.scatter(r['deviation_deg'],i,s=85,c=TEAL)
ax.set_yticks(range(len(other)),[name(r['town'])+': '+r['part'] for r in other],fontsize=13);ax.invert_yaxis();ax.axvline(0,color=MUTED,lw=.8)
ax.set(xlim=(-17,8),xlabel='Published deviation (degrees, north unspecified)');ax.grid(axis='x',color=GREY,alpha=.5)
finish(fig,'published-other-towns','Other towns in Wanzke’s comparison','Bearings','Wanzke attributes these entries to Jansen (1979). The Harappa street span is the reported range, not an uncertainty interval. We do not pool these values with true-north imagery readings.',WREF+' p. 34, PDF index 36.',[SOURCE_PREFIX+'run-v5/published-wanzke.json#/rows'])

# 12. Lothal disagreement.
lothal=next(r for r in comparison['bearings']['rows'] if r['slug']=='lothal')
fig,ax=base('The Lothal dock differs between imagery products','Both readings identify the dock, with different georeferenced source products.',rect=(.20,.31,.66,.40))
v=[lothal['theirs'],lothal['ours']];err=[lothal['sigma_theirs'],lothal['sigma_ours']]
for x,y,e,col in zip(v,[1,0],err,[TEAL,RUST]):ax.errorbar(x,y,xerr=e,fmt='none',ecolor=col,elinewidth=4,capsize=10)
ax.scatter(v,[1,0],c=[TEAL,RUST],s=130,zorder=3);ax.set_yticks([1,0],['Esri','Sentinel-2']);ax.axvline(0,color=MUTED,lw=.8)
for x,y,e in zip(v,[1,0],err):ax.text(x,y+.22,f'{x:+.2f}° ± {e:.2f}°',ha='center',fontsize=23,fontweight='bold')
ax.set(xlim=(-3,1),ylim=(-.7,1.7),xlabel='Deviation from the nearest cardinal axis (degrees)');ax.grid(axis='x',color=GREY,alpha=.5)
finish(fig,'lothal-product-disagreement','The Lothal dock differs between imagery products','Lothal','The difference is 2.07 degrees. Bars show reported one-sigma errors. The empirical Sentinel-2 error at these short lengths is larger than its nominal ±0.30 degrees.','Independent verification, comparison-v3/comparison.json, /bearings/rows/1.', ['experiments/2026-10-21-town-orientations-verification/comparison-v3/comparison.json#/bearings/rows/1'])

# 13. True-angle directions, not an invented dock plan.
fig,ax=base('Lothal’s small turn changes sign','Schematic direction comparison, drawn to scale.',rect=(.28,.25,.44,.54));ax.set_aspect('equal');ax.axis('off')
ax.add_patch(Circle((0,0),1,fill=False,ec=GREY,lw=1));ax.plot([0,0],[-1.1,1.15],color=GREY,lw=1);ax.text(0,1.2,'True N',ha='center')
for val,col,label in zip(v,[TEAL,RUST],['Esri','Sentinel-2']):
    a=math.radians(val);x,y=math.sin(a),math.cos(a);ax.plot([-x,x],[-y,y],color=col,lw=3,label=f'{label}: {val:+.2f}°')
ax.legend(frameon=False,bbox_to_anchor=(1.06,.55),loc='center left',fontsize=18);ax.set(xlim=(-1.25,1.25),ylim=(-1.2,1.35))
finish(fig,'lothal-direction-comparison','Lothal’s small turn changes sign','Lothal','The two nearly cardinal directions need an independently controlled dock survey. This diagram compares directions without reconstructing the dock or its dimensions.','Independent verification, comparison-v3/comparison.json.', ['experiments/2026-10-21-town-orientations-verification/comparison-v3/comparison.json#/bearings/rows/1'])

# 14. Existing annotated source image, preserved rather than redigitized.
rel='data/raw/2026-10-24-q1032-town-axis-register/surkotada-picks-overlay.png'
fig,ax=base('Surkotada: the two picked wall faces','SK-W is the western rampart. SK-S is the southern face west of the gateway.',rect=(.15,.23,.70,.57))
ax.imshow(image_array(rel));ax.axis('off')
finish(fig,'surkotada-picked-faces','Surkotada: the two picked wall faces','Source plates','These are the two exploratory picks already recorded on 24 October. The overlay retains the original native-mosaic endpoints. One observer read one archived image after seeing the earlier results.','Esri World Imagery Wayback release 8432. Esri, Vantor, Earthstar Geographics and the GIS User Community. Exposure date unknown.',[SOURCE_PREFIX+'new-observations.json#/structures',rel],'mixed-assets',{'kind':'reuse-existing-overlay','prior_transform_record':SOURCE_PREFIX+'TRANSFORMS.json#/local_visual_artifacts/2'})

# 15. Excavation plan, with its north ambiguity visible in the caption.
rel='data/raw/2026-10-24-q1032-town-axis-register/surkotada-fig8.png'
fig,ax=base('Surkotada: the excavation plan','Citadel, residential annexe and the exposed ramparts.',rect=(.17,.22,.66,.59));ax.imshow(image_array(rel));ax.axis('off')
finish(fig,'surkotada-excavation-plan','Surkotada: the excavation plan','Source plates','The plan labels the stone rebuilding IC. Its north arrow reads N without a true or magnetic qualification. The earlier enclosure line begins in IA.',JREF,[rel,SOURCE_PREFIX+'TRANSFORMS.json#/local_visual_artifacts/1'],'rights-unverified',{'kind':'reuse-existing-page-render','pdf_page_index':61})

# 16. Same native crop from two products, with no registration between products.
src=picks['sources'][0]['file']
current='data/raw/2026-10-21-plan-registration/R2-G2/mosaics/surk_main_cur_cur_z18_x182710-182714_y113368-113372.png'
fig=plt.figure(figsize=(16,10));fig.text(.055,.935,'Why the archived Surkotada image was selected',fontsize=29,fontweight='bold');fig.text(.055,.875,'Identical native-pixel window in the current and archived mosaics.',fontsize=16,color=MUTED)
box=(530,550,730,680)
for i,(rel,title) in enumerate([(current,'Current mosaic'),(src,'Archived release 8432')]):
    im=Image.open(record(rel)).convert('RGB').crop(box)
    ax=fig.add_axes((.055+i*.47,.29,.43,.48));ax.imshow(im);ax.axis('off');ax.set_title(title,pad=16)
finish(fig,'surkotada-image-visibility','Why the archived Surkotada image was selected','Source plates','Vegetation obscures the masonry more strongly in the current image. The choice is exploratory. A release number identifies an archive product, not the exposure date.','Esri World Imagery and Wayback. Esri, Vantor, Earthstar Geographics and the GIS User Community.',[current,src],'mixed-assets',{'kind':'native-pixel-crop','box_xyxy':box,'resampling':'display only; no measurement on the resized figure'})

# 17. Bearing vectors preserve both geometry and partial uncertainty.
fig,ax=base('Surkotada’s measured directions','Separate segments share an origin here to compare direction.',rect=(.23,.23,.54,.58));ax.set_aspect('equal')
for i,r in enumerate(new_lines):
    theta=math.radians(r['bearing_deg']);x,y=r['length_m']*math.sin(theta),r['length_m']*math.cos(theta)
    if y<0:x,y=-x,-y
    col=TEAL if i==0 else RUST;ax.plot([0,x],[0,y],lw=4,color=col,label=f"{r['measurement_id'].split(':')[1]}: {r['deviation_deg']:+.2f}°")
    ax.scatter([0,x],[0,y],s=65,c=col)
ax.axvline(0,color=GREY,lw=1);ax.axhline(0,color=GREY,lw=1);ax.set(xlim=(-12,32),ylim=(-8,32),xlabel='East component (m)',ylabel='North component (m)')
ax.legend(frameon=False,loc='upper right');ax.grid(color=GREY,alpha=.4)
finish(fig,'surkotada-bearing-vectors','Surkotada’s measured directions','Surkotada','Vector lengths are 26.70 m and 25.71 m. Bearings use the retained WGS84 geodesic result. Shifting the origins for comparison does not reconstruct the rampart corners.',MREF,[SOURCE_PREFIX+'run-v5/measurements.jsonl#new-surkotada:SK-W',SOURCE_PREFIX+'geodesic-check.json#/rows'])

# 18. Partial uncertainty, not a pooled axis estimate.
fig,ax=base('Surkotada’s digitizing uncertainty','These intervals omit unknown provider and restoration errors.',rect=(.23,.30,.62,.42))
for i,r in enumerate(new_lines):ax.errorbar(r['deviation_deg'],1-i,xerr=r['sigma_digitizing_deg'],fmt='o',color=[TEAL,RUST][i],markersize=12,capsize=11,elinewidth=3)
ax.set_yticks([1,0],['Western face','Southern face']);ax.axvline(0,color=MUTED,lw=.8)
ax.set(xlim=(-22,2),ylim=(-.7,1.7),xlabel='Deviation from the nearest cardinal axis (degrees)');ax.grid(axis='x',color=GREY,alpha=.5)
for i,r in enumerate(new_lines):ax.text(r['deviation_deg'],1-i+.24,f"{r['deviation_deg']:+.2f}° ± {r['sigma_digitizing_deg']:.2f}°",ha='center',fontsize=21,fontweight='bold')
finish(fig,'surkotada-partial-errors','Surkotada’s digitizing uncertainty','Surkotada','Three-pixel endpoint uncertainty gives 4.96 and 5.18 degrees. Total error remains unknown. The adjacent faces share one image and one observer.',MREF,[SOURCE_PREFIX+'run-v5/measurements.jsonl#new-surkotada:SK-W',SOURCE_PREFIX+'new-observations.json'])

# 19. A labelled sensitivity calculation, not an empirical calibration.
fig,ax=base('Short segments amplify endpoint uncertainty','Sensitivity calculation with 3-pixel uncertainty at each endpoint.',rect=(.15,.26,.72,.52))
length=np.linspace(20,400,700);sigma=np.degrees(math.sqrt(2)*3/length)
ax.plot(length,sigma,color=TEAL,lw=3)
for i,(r,structure) in enumerate(zip(new_lines,picks['structures'])):
    a,b=structure['endpoints_px'];lp=math.hypot(b[0]-a[0],b[1]-a[1]);ax.scatter(lp,r['sigma_digitizing_deg'],s=100,c=RUST,zorder=3)
    ax.annotate(f"{structure['id']}: {lp:.1f} px, {r['sigma_digitizing_deg']:.2f}°",(lp,r['sigma_digitizing_deg']),xytext=(95,7.6-i*1.3),fontsize=16,arrowprops={'arrowstyle':'-','color':MUTED})
ax.set(xlabel='Segment length (native image pixels)',ylabel='Small-angle digitizing sigma (degrees)',ylim=(0,13));ax.grid(color=GREY,alpha=.5)
finish(fig,'endpoint-sensitivity','Short segments amplify endpoint uncertainty','Methods','The curve uses the same small-angle formula as the register builder. It holds endpoint uncertainty fixed and supplies no estimate of image-provider orientation accuracy.','build_register.py: degrees(sqrt(2) * 3 / length_px). New observations provide the two plotted segment lengths.',[SOURCE_PREFIX+'code/build_register.py',SOURCE_PREFIX+'new-observations.json'],'own-work',{'kind':'sensitivity-calculation','synthetic':True,'endpoint_sigma_px':3})

# 20. Phase sequence, without unsupported calendar boundaries.
fig,ax=base('The enclosure line and stone walls have different phases','The sequence gives a stratigraphic relation without a calendar construction boundary.',rect=(.07,.24,.86,.55));ax.axis('off')
for x,col,phase,desc in [(.08,TEAL,'IA','First enclosure line'),(.60,RUST,'IC','Exposed stone rebuilding')]:
    ax.text(x,.76,phase,color=col,fontsize=48,fontweight='bold',transform=ax.transAxes)
    ax.text(x,.58,desc,fontsize=23,transform=ax.transAxes)
ax.add_patch(FancyArrowPatch((.32,.73),(.57,.73),transform=ax.transAxes,arrowstyle='-|>',mutation_scale=24,color=MUTED,lw=2))
ax.text(.365,.79,'Later phase',transform=ax.transAxes,fontsize=16,color=MUTED)
ax.plot([.65,.65],[.47,.24],transform=ax.transAxes,color=MUTED,lw=1.5,ls='--')
ax.text(.60,.14,'IC-associated charcoal\nthrough the excavation phase join',fontsize=21,transform=ax.transAxes)
finish(fig,'surkotada-phase-sequence','The enclosure line and stone walls have different phases','Dating','A first occupation, a dated deposit and a wall-construction boundary have different roles. We retain the wall episode explicitly before pairing orientation with dates.',JREF+' '+RCREF,[SOURCE_PREFIX+'run-v5/chronology-parts.jsonl',SOURCE_PREFIX+'run-v5/radiocarbon.jsonl'])

# 21. Four exact printed determinations with reported errors.
selected=[]
for lab in ['TF-1297','TF-1311','TF-1294','TF-1307']:
    r=next(r for r in rc if r['compilation']=='verify-dating' and r['town']=='surkotada' and r['values'].get('lab_code')==lab)
    selected.append(r['values']);assert r['values']['phase_label']=='Period IC'
fig,ax=base('Charcoal associated with Surkotada IC','Conventional radiocarbon ages with reported one-sigma errors.',rect=(.21,.27,.65,.48))
ax.errorbar([r['conventional_age_bp'] for r in selected],range(4),xerr=[r['error_bp'] for r in selected],fmt='o',color=RUST,ms=10,capsize=8,elinewidth=2.5)
ax.set_yticks(range(4),[r['lab_code'] for r in selected]);ax.set(xlim=(3300,3850),ylim=(3.6,-.6),xlabel='Conventional radiocarbon age (BP, 5568-year half-life)')
for i,r in enumerate(selected):ax.text(r['conventional_age_bp'],i-.25,f"{r['conventional_age_bp']} ± {r['error_bp']} BP",ha='center',va='center',fontsize=17)
ax.grid(axis='x',color=GREY,alpha=.45)
finish(fig,'surkotada-charcoal-dates','Charcoal associated with Surkotada IC','Dating','These are four existing laboratory determinations. The excavation join supplies the IC attribution. The plotted ages are uncalibrated, and no wall founding date is inferred.',RCREF,[SOURCE_PREFIX+'run-v5/radiocarbon.jsonl'])

# 22. Compiled assertions, explicitly not sample counts.
fig=plt.figure(figsize=(16,13));fig.text(.055,.95,'Where the chronology assertions accumulate',fontsize=29,fontweight='bold');fig.text(.055,.902,'118 dated-part assertions and 620 radiocarbon assertions across the 34-town frame.',fontsize=16,color=MUTED)
for i,(key,title,col) in enumerate([('dated_part_assertions','Dated-part assertions',TEAL),('radiocarbon_assertions','Radiocarbon assertions',RUST)]):
    ax=fig.add_axes((.23+i*.395,.20,.30,.65));vals=[len(t[key]) if isinstance(t[key],list) else t[key] for t in towns]
    horizontal(ax,[name(t['town']) for t in towns] if i==0 else ['']*34,vals,col);ax.tick_params(axis='y',labelsize=10)
    ax.set_xlabel(title,fontsize=14);ax.set_xlim(0,max(vals)*1.15)
finish(fig,'chronology-assertion-coverage','Where the chronology assertions accumulate','Dating','The radiocarbon assertions include repeated reporting. They contain 298 distinct nonempty town-and-laboratory-label keys, without an adjudicated count of physical samples. Seven assertions lack a lab label.',TREF,[SOURCE_PREFIX+'run-v5/town-axis-table.json#/towns'])

# 23-26. The full 0.1-degree ray profiles, one sector per figure.
for town in repaired['towns']:
    for sector,lo,hi in [('east',45,135),('west',225,315)]:
        rows=[r for r in town['profile'] if lo<=r['az']<=hi];col=TEAL if town['town']=='surkotada' else RUST
        title=f"{name(town['town'])}: the modern {sector}ern horizon"
        subtitle=f"Observer {town['lat']:.4f} N, {town['lon']:.4f} E. Every 0.1-degree ray retained."
        fig,ax=base(title,subtitle,rect=(.14,.27,.73,.50));xs=[r['az'] for r in rows];ys=[r['alt_deg'] for r in rows]
        ax.plot(xs,ys,color=col,lw=2.3);ax.axhline(0,color=MUTED,lw=.8);ax.fill_between(xs,0,ys,color=col,alpha=.10)
        imax=max(range(len(rows)),key=lambda i:ys[i]);r=rows[imax]
        ax.scatter(r['az'],r['alt_deg'],c=col,s=65,zorder=3)
        ax.annotate(f"Sector maximum {r['alt_deg']:+.3f}°",(r['az'],r['alt_deg']),xytext=(.60,.88),textcoords='axes fraction',fontsize=16,arrowprops={'arrowstyle':'-','color':MUTED})
        ax.set(xlim=(lo,hi),xlabel='Azimuth from true north (degrees)',ylabel='Apparent horizon altitude (degrees)');ax.grid(color=GREY,alpha=.45)
        caption='Modern DSM, inner 2 km excluded. Eye height 1.6 m, terrestrial refraction coefficient 0.13. Observer, DSM and palaeohorizon errors remain unquantified.'
        if town['town']=='farmana':caption+=' The Farmana observer coordinate is approximate.'
        finish(fig,f"{town['town']}-{sector}-horizon",title,'Horizons',caption,DREF,[SOURCE_PREFIX+'horizon-repair-v1/horizons.json#/towns'], 'mixed-assets')

# 27-28. Twenty usable modern-location profiles, no ancient sky test.
for key_e,key_w,title,slug in [('east_deg','west_deg','Due-east and due-west modern horizons','twenty-town-cardinal-horizons'),('max_east_deg','max_west_deg','Maximum altitude in each horizon sector','twenty-town-sector-maxima')]:
    rows=sorted(usable,key=lambda r:r['town'])
    fig,ax=base(title,'Thirty usable profiles at twenty towns. Observer points can differ within a town.',size=(16,12),rect=(.25,.21,.55,.59))
    y=np.arange(20)
    for yi,row in enumerate(rows):
        same_town=[r for r in usable_records if r['town']==row['town']]
        for j,r in enumerate(same_town):
            path=r['profile']['path'];marker='D' if '2026-10-24' in path else '^' if 'verification' in path else 'o'
            off=(j-(len(same_town)-1)/2)*.34
            ax.scatter(r[key_e],yi+off-.065,c=TEAL,s=55,marker=marker)
            ax.scatter(r[key_w],yi+off+.065,c=RUST,s=55,marker=marker)
    from matplotlib.lines import Line2D
    handles=[Line2D([],[],marker='o',linestyle='',color=TEAL,label='East'),Line2D([],[],marker='o',linestyle='',color=RUST,label='West')]+[Line2D([],[],marker=m,linestyle='',color=MUTED,label=l) for m,l in [('o','Original'),('^','Verification'),('D','Corrected')]]
    ax.set_yticks(y,[name(r['town']) for r in rows],fontsize=12);ax.invert_yaxis();ax.axvline(0,c=MUTED,lw=.8);ax.set_xlabel('Apparent horizon altitude (degrees)');ax.legend(handles=handles,frameon=False,bbox_to_anchor=(1.02,1),loc='upper left',fontsize=12);ax.grid(axis='x',color=GREY,alpha=.4)
    finish(fig,slug,title,'Horizons','Every usable profile is retained. Due-east and west use 90 and 270 degrees. Sector maxima cover 45-135 and 225-315 degrees. Differing observer locations remain separate. No total uncertainty is available.',DREF,[SOURCE_PREFIX+'run-v5/horizons.jsonl'],'mixed-assets')

# 29. Terrain controlling each ray, as recorded in the sampler.
fig=plt.figure(figsize=(16,10));fig.text(.055,.935,'Distance to the terrain controlling each model ray',fontsize=27,fontweight='bold');fig.text(.055,.875,'The sampler retains the distance of the terrain point with the highest apparent altitude.',fontsize=15,color=MUTED)
for i,(sector,lo,hi) in enumerate([('Eastern sector',45,135),('Western sector',225,315)]):
    ax=fig.add_axes((.09+i*.47,.28,.40,.48))
    for j,t in enumerate(repaired['towns']):
        rows=[r for r in t['profile'] if lo<=r['az']<=hi];ax.plot([r['az'] for r in rows],[r['distance_km'] for r in rows],c=[TEAL,RUST][j],lw=1.8,label=name(t['town']))
    ax.set_title(sector);ax.set(xlabel='Azimuth (degrees)',ylabel='Terrain distance (km)' if i==0 else '');ax.legend(frameon=False,fontsize=12);ax.grid(color=GREY,alpha=.4)
finish(fig,'horizon-terrain-distance','Distance to the terrain controlling each model ray','Horizons','Distance identifies the terrain selected by this modern DSM calculation. The sampler searches from 2 to 250 km and does not reconstruct ancient obstacles or near-site vegetation.',DREF,[SOURCE_PREFIX+'horizon-repair-v1/horizons.json#/towns'],'mixed-assets')

# 30. Source figure, tightly cropped with a reproducible pixel box.
rel='data/raw/2026-10-24-q1032-town-axis-register/wanzke-index-41.png'
im=Image.open(record(rel)).convert('RGB');box=(round(im.width*.51),round(im.height*.12),round(im.width*.935),round(im.height*.50))
fig,ax=base('A published plan of the Great Bath','Source plate, retained as a documentary figure.',rect=(.25,.21,.50,.61));ax.imshow(im.crop(box));ax.axis('off')
finish(fig,'great-bath-source-plan','A published plan of the Great Bath','Source plates','This is Wanzke’s Fig. 2. The plate supplies architectural context, not an additional independent bearing. The numerical axes remain linked to their tabulated source rows.',WREF+' Fig. 2, printed p. 39, zero-based PDF index 41.',[rel,SOURCE_PREFIX+'TRANSFORMS.json'],'rights-unverified',{'kind':'pixel-crop','parent_png':rel,'box_xyxy':box,'original_pdf_page_index':41})

# 31. Location repairs, with explicitly approximate source coordinates.
fig=plt.figure(figsize=(16,10));fig.text(.055,.935,'A site-location error changes the horizon',fontsize=29,fontweight='bold');fig.text(.055,.875,'Old and retained observer coordinates in two previous horizon calculations.',fontsize=16,color=MUTED)
for i,(title,old,new,dist) in enumerate([('Surkotada',(70.8407,23.6304),(70.9174,23.6113),'About 8 km'),('Farmana',(76.5667,29.0667),(76.306,29.040),'About 25 km')]):
    ax=fig.add_axes((.10+i*.47,.29,.38,.46));ax.scatter(*old,c=GREY,s=130,label='Old observer point');ax.scatter(*new,c=TEAL,s=130,label='Retained point')
    ax.annotate('',xy=new,xytext=old,arrowprops={'arrowstyle':'->','color':MUTED,'lw':2});ax.set_title(title+'\n'+dist,pad=18)
    dx=abs(old[0]-new[0]);dy=max(abs(old[1]-new[1]),.03);ax.set(xlim=(min(old[0],new[0])-dx*.25,max(old[0],new[0])+dx*.25),ylim=(min(old[1],new[1])-dy*.5,max(old[1],new[1])+dy*.5),xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)' if i==0 else '')
    ax.ticklabel_format(useOffset=False);ax.grid(color=GREY,alpha=.4);ax.legend(frameon=False,fontsize=12,loc='best')
finish(fig,'corrected-observer-locations','A site-location error changes the horizon','Methods','The retained Farmana coordinate is approximate. Old-coordinate profiles remain preserved with exclusion reasons. We recomputed the modern profiles at the retained locations.','Plan-registration REPORT.md and Q-1032 HORIZON-REPAIR.md.', ['experiments/2026-10-21-plan-registration/REPORT.md',SOURCE_PREFIX+'horizon-repair-v1/horizons.json#/towns'])

# 32. The report's prospective test, visibly separated from observations.
fig,ax=base('The deciding survey','Prospective expectations from the research report.',rect=(.06,.23,.88,.59));ax.axis('off')
ax.text(.00,.94,'The relevant unit is an architectural system in a building episode.',fontsize=25,fontweight='bold',transform=ax.transAxes)
for y,label,desc,col in [(.68,'Mohenjo-daro','Moneer near cardinal, HR First Street turned more than 5°',TEAL),(.48,'Surkotada','IC ramparts anticlockwise by more than 5°',RUST),(.28,'Lothal','A dock survey decides the imagery discrepancy',BLUE)]:
    ax.text(.02,y,label,fontsize=23,fontweight='bold',color=col,transform=ax.transAxes)
    ax.text(.29,y,desc,fontsize=19,transform=ax.transAxes)
ax.text(.02,.05,'True-north angular error below 0.5°. Freeze wall identities and dated phase joins before reading.',fontsize=19,transform=ax.transAxes)
finish(fig,'deciding-survey','The deciding survey','Deciding test','If surveyed phase-linked walls collapse onto one common axis within their errors, this reading fails. Document restorations and stratigraphic joins before reading the survey.','Q-1032 REPORT.md, final paragraph. This atlas spends no new confirmation population.',[SOURCE_PREFIX+'REPORT.md'])

assert len(FIGURES)==32
for row in FIGURES:
    row['files']={}
    for fmt,p in row['paths'].items():
        path=Path(p);row['files'][fmt]={'relative_path':str(path.relative_to(OUT)).replace('\\','/'),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

manifest={'schema_version':'1.0','date':'2026-10-24','run':RUN,'figure_count':32,'figures':FIGURES,
 'inputs':list(INPUTS.values()),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'physical_root':str(OUT),'logical_root':f'data/raw/2026-10-24-town-axis-visual-atlas/{RUN}',
 'new_sources':0,'new_archaeological_measurements':0,'coverage_changes':0,
 'rights_status':'mixed-assets','handling':'local-only','authors':'GPT-6, Codex desktop harness; exact runtime build unavailable',
 'versions':{'python':sys.version,'matplotlib':matplotlib.__version__},
 'notes':'The endpoint sensitivity curve is a labelled calculation. Source imagery and plans retain their existing rights and remain local-only.'}
(OUT/'figures.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(PACKAGE/f'manifest-{RUN}.json').write_text(json.dumps({k:v for k,v in manifest.items() if k!='figures'},indent=2)+'\n',encoding='utf-8')
(PACKAGE/f'figure-index-{RUN}.json').write_text(json.dumps([{k:v for k,v in row.items() if k not in ['paths','files']} for row in FIGURES],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Figure export complete:',OUT,flush=True)
