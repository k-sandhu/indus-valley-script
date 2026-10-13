"""Render new, legible evidence panels without changing frozen analysis endpoints."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, textwrap
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling
from pyproj import Transformer
from shapely.geometry import shape
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from process_rasters import grid_band, rgb_scale

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-satellite-prospection'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path): return path.resolve().relative_to(ROOT).as_posix()
def save(path, obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def scenes_for(block):
    cache=RAW/'display-caches-v1'/(block['id']+'.npz')
    if cache.exists():
        data=np.load(cache)
        return [data['scene'+str(i)] for i in range(len(block['scenes']))]
    left,bottom,right,top=block['bounds_native_m']
    transform=from_origin(left,top,10,10)
    output=[]
    for scene in block['scenes']:
        arrays={}
        for record in scene['bands']:
            key=record['band']
            if key not in ('red','green','blue','scl'): continue
            data=grid_band(record,block,transform,(block['height_pixels'],block['width_pixels']),Resampling.nearest if key=='scl' else Resampling.bilinear)
            if key!='scl':
                band=record['raster_bands'][0]
                data=data*band['scale']+band.get('offset',0)
            arrays[key]=data
        valid=np.isin(arrays['scl'],[4,5,6,7])
        rgb=np.nan_to_num(rgb_scale(arrays['red'],arrays['green'],arrays['blue'])).astype(np.uint8)
        output.append(np.dstack([rgb,valid.astype(np.uint8)*255]))
    cache.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(cache,**{'scene'+str(i):v for i,v in enumerate(output)})
    return output

def coords(feature,block):
    props=feature['properties']
    transformer=Transformer.from_crs(4326,block['native_epsg'],always_xy=True)
    if 'native_center_xy' in props: return props['native_center_xy']
    geo=shape(feature['geometry']).centroid
    return transformer.transform(geo.x,geo.y)

def outline(ax,feature,block):
    geom=shape(feature['geometry'])
    transformer=Transformer.from_crs(4326,block['native_epsg'],always_xy=True)
    polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom] if geom.geom_type=='Polygon' else []
    for poly in polys:
        xx,yy=np.array(poly.exterior.coords).T
        xx,yy=transformer.transform(xx,yy)
        ax.plot(xx,yy,color='#fff83a',lw=1)

def panel(feature,block,images,dem,out):
    props=feature['properties']; x,y=coords(feature,block)
    left,bottom,right,top=block['bounds_native_m']
    h,w=images[0].shape[:2]; half=int(props.get('panel_half_width_m',700)/10)
    c=(x-left)/10; r=(top-y)/10
    r0=max(0,int(r)-half);r1=min(h,int(r)+half);c0=max(0,int(c)-half);c1=min(w,int(c)+half)
    if r1<=r0 or c1<=c0: return None
    extent=[left+c0*10,left+c1*10,top-r1*10,top-r0*10]
    fig=plt.figure(figsize=(13.6,9.1)); grid=fig.add_gridspec(2,3,left=.055,right=.965,bottom=.09,top=.88,wspace=.21,hspace=.28)
    axes=[fig.add_subplot(grid[i//3,i%3]) for i in range(6)]
    for ax,scene,image in zip(axes[:4],block['scenes'],images):
        ax.imshow(image[r0:r1,c0:c1],extent=extent,interpolation='nearest')
        ax.set_title(scene['datetime'][:10],fontsize=12)
        ax.plot(x,y,'+',color='#ff264d',ms=12,mew=1.5);outline(ax,feature,block)
    d0=max(0,int((top-extent[3])/30));d1=min(dem.shape[0],math.ceil((top-extent[2])/30))
    e0=max(0,int((extent[0]-left)/30));e1=min(dem.shape[1],math.ceil((extent[1]-left)/30))
    ax=axes[4]
    image=ax.imshow(dem[d0:d1,e0:e1],cmap='terrain',extent=[left+e0*30,left+e1*30,top-d1*30,top-d0*30],interpolation='nearest')
    ax.set_xlim(extent[:2]);ax.set_ylim(extent[2:]);ax.plot(x,y,'+',color='#ff264d',ms=12);outline(ax,feature,block)
    ax.set_title('Surface elevation, approximately 30 m pixels',fontsize=10)
    fig.colorbar(image,ax=ax,shrink=.63,pad=.01).set_label('m above EGM2008',fontsize=8)
    for ax in axes[:5]:
        ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7)
        ax.set_xlabel('UTM easting (m)',fontsize=8);ax.set_ylabel('UTM northing (m)',fontsize=8)
        # A fixed 200 m metric scale within the analysed UTM image.
        bx=extent[0]+(extent[1]-extent[0])*.055; by=extent[2]+(extent[3]-extent[2])*.06
        ax.plot([bx,bx+200],[by,by],color='white',lw=3);ax.text(bx,by+22,'200 m',color='white',fontsize=8)
    ax=axes[5];ax.axis('off');m=props.get('metrics',{})
    ll=shape(feature['geometry']).centroid
    lat=props.get('lat',ll.y);lon=props.get('lon',ll.x)
    lines=[props['id'],f'{lat:.5f} N, {lon:.5f} E',f'Status: {props.get("status","context")}',f'Native map grid: EPSG:{block["native_epsg"]}']
    if 'apparent_patch_area_ha' in m: lines.append(f'Optical patch: {m["apparent_patch_area_ha"]:.2f} ha')
    if 'area_ha' in m: lines.append(f'Terrain patch: {m["area_ha"]:.2f} ha')
    if 'dsm_relative_difference_m' in m: lines.append(f'DSM circle median minus ring: {m["dsm_relative_difference_m"]:+.2f} m')
    if 'relative_height_m' in m: lines.append(f'DSM peak minus ring median: {m["relative_height_m"]:+.2f} m')
    if feature['geometry']['type']=='Point':
        lines+=['','Red cross: supplied source/context point.']
    else:lines+=['','Yellow outline: threshold support.','Red cross: analysis centre or DSM peak.']
    explanation=props.get('explanation',props.get('name',''))
    lines+=['',*textwrap.wrap(explanation,49),'','Optical pixels: 10 m. The DSM includes','vegetation and structures. The threshold','support does not define site extent.']
    ax.text(0,.98,'\n'.join(lines),transform=ax.transAxes,va='top',fontsize=9,linespacing=1.22)
    fig.suptitle(props.get('name',props['id']),fontsize=14,y=.974)
    fig.text(.055,.925,'Four acquired Sentinel-2 C1 scenes and independently acquired Copernicus GLO-30 surface elevation',fontsize=10)
    fig.text(.055,.025,'Contains modified Copernicus Sentinel data (2025, 2026). Terrain derived from Copernicus WorldDEM-30. Full notices: THIRD-PARTY-NOTICES.md.',fontsize=8)
    path=out/(props['id']+'.png');fig.savefig(path,dpi=150);plt.close(fig)
    return dict(id=props['id'],path=rel(path),sha256=sha(path),scene_ids=[s['id'] for s in block['scenes']],block_id=block['id'],crs=block['native_epsg'],extent_native_m=extent)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--features',type=Path,nargs='+',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    blocks=[]
    inputs=[RAW/'raster-run-v1/manifest.json',RAW/'raster-run-v2/manifest.json']
    for path in inputs: blocks+=json.loads(path.read_text(encoding='utf-8'))['blocks']
    features=[]
    for path in args.features: features+=json.loads(path.read_text(encoding='utf-8'))['features']
    records=[]
    for block in blocks:
        selected=[f for f in features if f['properties'].get('block_id')==block['id']]
        if not selected:continue
        print(json.dumps(dict(stage='render',block=block['id'],features=len(selected))),flush=True)
        images=scenes_for(block);dem=np.load(RAW/'processed-v1'/(block['id']+'.npz'))['dem']
        for feature in selected:
            item=panel(feature,block,images,dem,args.output)
            if item:records.append(item)
    save(args.output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),code_path=rel(Path(__file__)),code_sha256=sha(Path(__file__)),processing_helper_sha256=sha(BASE/'process_rasters.py'),inputs=[dict(path=rel(p),sha256=sha(p)) for p in inputs+args.features],panels=records,scope='New layout of acquired data and supplied feature geometry; no alteration of original analysis outcomes'))
    print(json.dumps(dict(stage='complete',panels=len(records))),flush=True)

if __name__=='__main__':main()
