"""Make static map figures from the exact rasters and geometry supplied to the atlas."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math
import numpy as np
from PIL import Image
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely.ops import transform
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,patheffects
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
FORWARD=Transformer.from_crs(4326,3857,always_xy=True);INVERSE=Transformer.from_crs(3857,4326,always_xy=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def outline(ax,g,color,width=1,alpha=1):
    polys=list(g.geoms) if g.geom_type=='MultiPolygon' else [g] if g.geom_type=='Polygon' else []
    for polygon in polys:
        xx,yy=np.array(polygon.exterior.coords).T;ax.plot(xx,yy,color=color,lw=width,alpha=alpha)

def figure(block,overlay,features,source,out):
    asset=(source.parent/overlay['path']).resolve()
    if sha(asset)!=overlay['sha256']:raise ValueError(asset)
    image=Image.open(asset)
    xmin,ymin,xmax,ymax=overlay['bounds_display_m']
    fig,ax=plt.subplots(figsize=(10.5,10.7));fig.subplots_adjust(left=.09,right=.96,bottom=.145,top=.88)
    ax.imshow(image,extent=[xmin,xmax,ymin,ymax],interpolation='nearest')
    geomframe=box(xmin,ymin,xmax,ymax);records=[]
    for f in features:
        p=f['properties'];g=transform(FORWARD.transform,shape(f['geometry']))
        if not g.intersects(geomframe) or p.get('kind')=='historical_map_coverage':continue
        if p['status']=='control':continue
        kind=p.get('kind','');status=p['status']
        core=kind=='published_sediment_core';reference=kind=='known_archaeological_reference'
        if core:color='#38a5ff';symbol='o';label=p['id'].replace('CORE-','')
        elif reference:color='#00ffff';symbol='^';label=p['id']
        elif status=='screening_lead':color='#ffd42b';symbol='*';label=p['id']
        elif p.get('desk_check_reserve'):color='#ed82ff';symbol='D';label=p['id']+' reserve'
        elif status=='known':color='#00ffff';symbol='s';label=None if p['id']=='B04-T0136' else p['id']
        elif status=='rejected':color='#ededed';symbol='x';label=None
        else:color='#ed82ff';symbol='.';label=None
        if g.geom_type!='Point':outline(ax,g,color,.8 if status=='rejected' else 1.5,.55 if status=='rejected' else 1)
        if p.get('lon') is not None:x,y=FORWARD.transform(p['lon'],p['lat'])
        else:x,y=g.centroid.x,g.centroid.y
        ax.scatter(x,y,c=color,marker=symbol,s=25 if status=='rejected' else 70,linewidths=.8,edgecolors=None if symbol=='x' else '#172c30',zorder=5)
        if label:
            right_edge=x>xmin+.75*(xmax-xmin)
            artist=ax.annotate(label,(x,y),xytext=(-5 if right_edge else 5,6),ha='right' if right_edge else 'left',textcoords='offset points',fontsize=8,color=color,zorder=6)
            artist.set_path_effects([patheffects.withStroke(linewidth=2,foreground='#243237')])
        records.append(p['id'])
    ax.set_xlim(xmin,xmax);ax.set_ylim(ymin,ymax)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{INVERSE.transform(x,(ymin+ymax)/2)[0]:.3f} E'))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y,p:f'{INVERSE.transform((xmin+xmax)/2,y)[1]:.3f} N'))
    ax.tick_params(labelsize=8);ax.set_xlabel('Longitude (WGS84)',fontsize=10);ax.set_ylabel('Latitude (WGS84)',fontsize=10)
    ax.grid(color='white',alpha=.15,lw=.6)
    centre_lat=INVERSE.transform((xmin+xmax)/2,(ymin+ymax)/2)[1]
    length=2000/math.cos(math.radians(centre_lat));bx=xmin+(xmax-xmin)*.055;by=ymin+(ymax-ymin)*.045
    ax.plot([bx,bx+length],[by,by],color='black',lw=6);ax.plot([bx,bx+length],[by,by],color='white',lw=3)
    t=ax.text(bx,by+(ymax-ymin)*.015,'2 km (approx. ground distance)',fontsize=9,color='white');t.set_path_effects([patheffects.withStroke(linewidth=2,foreground='black')])
    ax.annotate('N',xy=(.955,.95),xytext=(.955,.875),xycoords='axes fraction',textcoords='axes fraction',ha='center',color='white',fontsize=12,arrowprops={'arrowstyle':'-|>','color':'white','lw':2},path_effects=[patheffects.withStroke(linewidth=2,foreground='black')])
    legend=[Line2D([],[],marker='*',linestyle='None',color='#e4ae00',label='Conditional landform lead',markersize=10),Line2D([],[],marker='D',linestyle='None',color='#b733d6',label='Desk-check reserve',markersize=6),Line2D([],[],marker='^',linestyle='None',color='#00828a',label='Published archaeological reference',markersize=7),Line2D([],[],marker='o',linestyle='None',color='#177bd0',label='Published geological core',markersize=6),Line2D([],[],marker='x',linestyle='None',color='#687478',label='Rejected reviewed anomaly',markersize=6)]
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.51,.055),ncol=2,frameon=False,fontsize=8)
    fig.suptitle(block['id']+': '+block['name'],fontsize=15,y=.969)
    fig.text(.09,.918,('Acquired Sentinel-2 optical image: '+overlay['date']) if overlay['kind']=='rgb' else 'Copernicus surface elevation; principal acquisition epoch 2011-2015',fontsize=10)
    fig.text(.09,.025,'Features are plotted on acquired, georeferenced pixels. Threshold polygons do not define archaeological boundaries.',fontsize=8)
    fig.text(.09,.010,'Sentinel: modified Copernicus data (2026). Terrain: derived Copernicus WorldDEM-30. Full notices accompany this study.',fontsize=7)
    path=out/(block['id']+'-'+overlay['kind']+'-annotated.png');fig.savefig(path,dpi=180);plt.close(fig)
    return {'path':rel(path),'sha256':sha(path),'block_id':block['id'],'source_overlay_id':overlay['id'],'source_overlay_sha256':overlay['sha256'],'bounds_display_m':overlay['bounds_display_m'],'feature_ids':records,'display_crs':'EPSG:3857','scale_note':'2 km approximated at block centre using Web Mercator latitude scale'}

def overview(data,out):
    source=BASE/'atlas/vendor/natural-earth/ne_110m_admin_0_countries.geojson'
    countries=json.loads(source.read_text(encoding='utf-8'))['features']
    fig,ax=plt.subplots(figsize=(10.5,8.2));fig.subplots_adjust(left=.08,right=.96,top=.90,bottom=.12)
    ax.set_facecolor('#d7e9ed')
    for f in countries:
        g=shape(f['geometry'])
        polys=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        for poly in polys:
            xx,yy=np.array(poly.exterior.coords).T;ax.fill(xx,yy,color='#edf0df',edgecolor='#819291',lw=.5)
    short_names={'B01':'B01 Cholistan reference block','B02':'B02 Harappa countryside','B03':'B03 western Kutch catchment','B04':'B04 Kalibangan-Pilibanga'}
    for block in data['study_blocks']:
        w,s,e,n=block['bbox_lonlat'];ax.fill([w,e,e,w,w],[s,s,n,n,s],color='#ad5b17',alpha=.9)
        ax.plot((w+e)/2,(s+n)/2,'o',color='#ad5b17',ms=5)
        ax.annotate(short_names[block['id']],((w+e)/2,(s+n)/2),xytext=(8,12 if block['id']!='B04' else -18),textcoords='offset points',fontsize=9)
    for label,xy in [('Pakistan',(67.5,29.0)),('India',(75.7,25.5)),('Arabian Sea',(65.7,23.6))]:ax.text(*xy,label,color='#536f75',fontsize=12)
    ax.set_xlim(64.6,78);ax.set_ylim(22.2,33.6);ax.set_aspect(1/math.cos(math.radians(28)))
    ax.set_xlabel('Longitude (WGS84)');ax.set_ylabel('Latitude (WGS84)');ax.grid(alpha=.22)
    fig.suptitle('Four acquired study blocks in real geographic context',fontsize=16,y=.966)
    fig.text(.08,.055,'Total metric study area: 740 km². Each block has four acquired optical dates, a DSM and a WorldCover window.',fontsize=10)
    fig.text(.08,.020,'Made with Natural Earth, 1:110 million public-domain countries/coastline. Boundaries are geographic context.',fontsize=8)
    path=out/'real-geographic-overview.png';fig.savefig(path,dpi=180);plt.close(fig)
    return {'path':rel(path),'sha256':sha(path),'geographic_source':rel(source),'source_sha256':sha(source),'crs':'EPSG:4326 plotted with latitude-adjusted aspect; geographic overview only'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True)
    data=json.loads(a.input.read_text(encoding='utf-8'));records=[overview(data,a.output)]
    for block in data['study_blocks']:
        overlays=[o for o in data['overlays'] if o['block_id']==block['id']]
        for selected in [max([o for o in overlays if o['kind']=='rgb'],key=lambda o:o['date']),next(o for o in overlays if o['kind']=='terrain')]:
            records.append(figure(block,selected,data['feature_collection']['features'],a.input,a.output))
    save(a.output/'manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'code_sha256':sha(Path(__file__)),'input':rel(a.input),'input_sha256':sha(a.input),'figures':records})
    print(json.dumps({'figures':len(records),'input':rel(a.input)}))
if __name__=='__main__':main()
