"""Process actual scenes and extract an exploratory, fully retained anomaly set."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math,warnings
import numpy as np
import rasterio
from rasterio.warp import reproject,transform_bounds,calculate_default_transform,Resampling
from rasterio.transform import from_origin
from rasterio.features import shapes
from scipy import ndimage as ndi
from shapely.geometry import shape,mapping,Point
from shapely.ops import transform as geom_transform
from pyproj import Transformer
from PIL import Image
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def finite(v):return None if not np.isfinite(v) else float(v)

def grid_band(record,b,transform,shape_,resampling):
    path=ROOT/record['local_path']
    with rasterio.open(path) as src:
        dest=np.full(shape_,np.nan,dtype=np.float32)
        reproject(rasterio.band(src,1),dest,src_transform=src.transform,src_crs=src.crs,src_nodata=src.nodata,dst_transform=transform,dst_crs=b['native_epsg'],dst_nodata=np.nan,resampling=resampling)
    return dest

def smooth_masked(data,mask,sigma):
    numerator=ndi.gaussian_filter(np.where(mask,data,0).astype(np.float32),sigma)
    denominator=ndi.gaussian_filter(mask.astype(np.float32),sigma)
    return np.divide(numerator,denominator,out=np.full(data.shape,np.nan,np.float32),where=denominator>.05)

def mercator_png(array,mask,b,transform,path):
    # Warping is solely for map display. Analyses retain the native10m UTM grid.
    h,w=mask.shape;bounds=b['bounds_native_m']
    dst_transform,dw,dh=calculate_default_transform(b['native_epsg'],3857,w,h,*bounds)
    source=np.moveaxis(array,-1,0).astype(np.float32)
    channels=[]
    for channel in source:
        dest=np.zeros((dh,dw),dtype=np.float32)
        reproject(channel,dest,src_transform=transform,src_crs=b['native_epsg'],dst_transform=dst_transform,dst_crs=3857,resampling=Resampling.bilinear)
        channels.append(dest)
    alpha=np.zeros((dh,dw),np.uint8)
    reproject(mask.astype(np.uint8)*255,alpha,src_transform=transform,src_crs=b['native_epsg'],dst_transform=dst_transform,dst_crs=3857,resampling=Resampling.nearest)
    rgba=np.dstack([np.clip(np.dstack(channels),0,255).astype(np.uint8),alpha])
    Image.fromarray(rgba).save(path)
    bounds_m=list(rasterio.transform.array_bounds(dh,dw,dst_transform));lonlat=list(transform_bounds(3857,4326,*bounds_m))
    return dict(path=rel(path),bounds_lonlat=lonlat,display_crs='EPSG:3857',bounds_display_m=bounds_m,display_transform=list(dst_transform)[:6],display_shape=[dh,dw],sha256=sha(path),bytes=path.stat().st_size)

def rgb_scale(red,green,blue):
    return 255*np.power(np.clip(np.dstack([red,green,blue])/.45,0,1),.8)

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--parameters',type=Path,default=BASE/'screening-parameters-v1.json');a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True);(a.output/'maps').mkdir();(a.output/'panels').mkdir()
    params=json.loads(a.parameters.read_text(encoding='utf-8'));blocks=[]
    for path in a.input:blocks+=json.loads(path.read_text(encoding='utf-8'))['blocks']
    all_features=[];review_features=[];overlays=[];block_reports=[];rng=np.random.default_rng(params['random_seed'])
    for b in blocks:
        print(json.dumps(dict(stage='process',block=b['id'])),flush=True)
        left,bottom,right,top=b['bounds_native_m'];h=b['height_pixels'];w=b['width_pixels'];transform=from_origin(left,top,10,10)
        togeo=Transformer.from_crs(b['native_epsg'],4326,always_xy=True)
        scene_arrays=[];qa=[];zs=[];land_masks=[]
        for scene in b['scenes']:
            records={r['band']:r for r in scene['bands']};arr={}
            for key,record in records.items():
                data=grid_band(record,b,transform,(h,w),Resampling.nearest if key=='scl' else Resampling.bilinear)
                if key!='scl':
                    band=record['raster_bands'][0];data=data*band['scale']+band.get('offset',0)
                arr[key]=data
            valid=np.isin(arr['scl'],params['valid_scl_for_optical_descriptors'])
            valid &= np.isfinite(arr['red'])&np.isfinite(arr['green'])&np.isfinite(arr['nir'])
            land=np.isin(arr['scl'],params['land_scl_for_screening'])&valid
            denom=arr['nir']+arr['red'];ndvi=np.divide(arr['nir']-arr['red'],denom,out=np.full((h,w),np.nan,np.float32),where=valid&(denom>.001))
            denom=arr['red']+arr['green'];colour=np.divide(arr['red']-arr['green'],denom,out=np.full((h,w),np.nan,np.float32),where=land&(denom>.001))
            mask=land&np.isfinite(colour)
            background=smooth_masked(colour,mask,params['local_background_gaussian_sigma_pixels'])
            residual=colour-background;values=residual[mask];median=float(np.nanmedian(values));mad=float(np.nanmedian(np.abs(values-median)))
            scale=max(1.4826*mad,.005);z=(residual-median)/scale;z[~mask]=np.nan
            arr.update(valid=valid,land=mask,ndvi=ndvi,colour=colour,z=z)
            scene_arrays.append(arr);zs.append(z);land_masks.append(mask)
            classes={str(int(v)):int(n) for v,n in zip(*np.unique(np.nan_to_num(arr['scl'],nan=0).astype(np.uint8),return_counts=True))}
            qa.append(dict(scene_id=scene['id'],date=scene['datetime'],tile_cloud_cover=scene['tile_cloud_cover'],usable_optical_fraction=float(valid.mean()),usable_land_fraction=float(mask.mean()),scl_counts=classes,colour_residual_median=median,mad=mad,normalization_scale=scale,scale_offset_source='Per-asset raster:bands; rawDN0 masked by raster nodata before conversion'))
            rgb=rgb_scale(arr['red'],arr['green'],arr['blue']);rgb[~valid]=0
            overlay=mercator_png(rgb,valid,b,transform,a.output/'maps'/f'{b["id"]}-{scene["id"]}-rgb.png')
            overlay.update(id=b['id']+'-'+scene['id']+'-rgb',block_id=b['id'],kind='rgb',date=scene['datetime'][:10],source_item_ids=[scene['id']],native_pixel_m=10,attribution=f'Contains modified Copernicus Sentinel data {scene["datetime"][:4]}; ESA/Copernicus, EarthSearch C1',limits='Fixed reflectance/.45 and gamma.8 display, cloud/invalid pixels transparent; no archaeological dating')
            overlays.append(overlay)
        last=scene_arrays[-1]
        fc=rgb_scale(last['swir16'],last['nir'],last['red']);fc[~last['valid']]=0
        overlay=mercator_png(fc,last['valid'],b,transform,a.output/'maps'/f'{b["id"]}-false-colour.png')
        overlay.update(id=b['id']+'-false-colour',block_id=b['id'],kind='false_colour',date=b['scenes'][-1]['datetime'][:10],source_item_ids=[b['scenes'][-1]['id']],native_pixel_m='20mSWIR,10mNIR/red',attribution='Contains modified Copernicus Sentinel data2026; ESA/Copernicus, EarthSearch C1',limits='SWIR/NIR/red;20mSWIR resampled for display, not extra10m information')
        overlays.append(overlay)
        # Native DSM pixels are retained. Warp to30m metric grid for descriptors.
        dem_transform=from_origin(left,top,30,30);demshape=(math.ceil(h/3),math.ceil(w/3));dem=np.full(demshape,np.nan,np.float32)
        for record in b['dem_tiles']:
            piece=grid_band(record,b,dem_transform,demshape,Resampling.bilinear);dem[np.isfinite(piece)]=piece[np.isfinite(piece)]
        dmask=np.isfinite(dem);gy,gx=np.gradient(np.nan_to_num(dem,nan=float(np.nanmedian(dem))),30)
        slope=np.arctan(np.sqrt(gx*gx+gy*gy));aspect=np.arctan2(-gx,gy);hill=.5+.5*(np.cos(math.radians(45))*np.cos(slope)+np.sin(math.radians(45))*np.sin(slope)*np.cos(math.radians(315)-aspect))
        lo,hi=np.nanpercentile(dem,[2,98]);terrain=plt.get_cmap('terrain')(np.clip((dem-lo)/max(hi-lo,.1),0,1))[...,:3]*(.65+.35*hill[...,None])*255
        td=b.copy();td['bounds_native_m']=[left,top-demshape[0]*30,left+demshape[1]*30,top]
        overlay=mercator_png(terrain,dmask,td,dem_transform,a.output/'maps'/f'{b["id"]}-terrain.png')
        overlay.update(id=b['id']+'-terrain',block_id=b['id'],kind='terrain',date='DSM source epoch approximately2010–2015; release tile metadata separately',source_item_ids=[r['tile_id'] for r in b['dem_tiles']],native_pixel_m='~30m;1arcsec source',attribution='Copernicus DEM GLO-30; generated height colour/hillshade, Airbus/ESA/Copernicus',limits=f'DSM includes objects;EGM2008. Display2–98% stretch{lo:.1f}–{hi:.1f}m;small relief is not archaeological evidence')
        overlays.append(overlay)
        stack=np.stack(zs);count=np.sum(np.isfinite(stack),axis=0);above=np.sum(np.abs(stack)>params['absolute_contrast_threshold'],axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',RuntimeWarning);med_ndvi=np.nanmedian(np.stack([x['ndvi'] for x in scene_arrays]),axis=0);mean_abs=np.nanmean(np.abs(stack),axis=0)
        active=(count>=params['minimum_usable_dates'])&(above>=params['required_above_threshold_dates'])&(med_ndvi<params['median_ndvi_max'])
        active=ndi.binary_opening(active,structure=np.ones((3,3)))
        labels,nlabels=ndi.label(active);component_rows=[]
        score=mean_abs*np.divide(above,np.maximum(count,1))
        objects=ndi.find_objects(labels)
        for number,slices in enumerate(objects,1):
            if slices is None:continue
            sub=labels[slices]==number;area=int(sub.sum())*.01
            if not params['minimum_component_area_ha']<=area<=params['maximum_component_area_ha']:continue
            rr,cc=np.where(sub);rr=rr+slices[0].start;cc=cc+slices[1].start
            covariance=np.cov(np.stack([rr,cc]));eigen=np.linalg.eigvalsh(covariance);ratio=math.sqrt(float(eigen[-1]/max(eigen[0],1)))
            if ratio>params['maximum_eigenvalue_axis_ratio']:continue
            x=left+(float(cc.mean())+.5)*10;y=top-(float(rr.mean())+.5)*10;lon,lat=togeo.transform(x,y)
            patchmask=sub.astype(np.uint8)
            sub_transform=transform*rasterio.Affine.translation(slices[1].start,slices[0].start)
            polygons=[shape(g) for g,v in shapes(patchmask,mask=sub,transform=sub_transform) if v==1]
            polygon=max(polygons,key=lambda g:g.area);geo=geom_transform(togeo.transform,polygon)
            dc=(x-left)/30;dr=(top-y)/30;radius=max(45,math.sqrt(area*10000/math.pi));distance=np.hypot((np.arange(demshape[0])[:,None]-dr)*30,(np.arange(demshape[1])[None,:]-dc)*30)
            inside=dmask&(distance<=radius);annulus=dmask&(distance>=radius+100)&(distance<=radius+400)
            inside_med=float(np.nanmedian(dem[inside]));ring_med=float(np.nanmedian(dem[annulus]));relief=inside_med-ring_med
            sid=f'{b["id"]}-A{number:04d}'
            metrics=dict(apparent_patch_area_ha=round(area,2),native10m_pixels=int(sub.sum()),axis_ratio=ratio,review_score=finite(np.nanmean(score[rr,cc])),usable_dates_mean=finite(np.mean(count[rr,cc])),above_threshold_dates_mean=finite(np.mean(above[rr,cc])),median_ndvi=finite(np.nanmedian(med_ndvi[rr,cc])),dsm_patch_median_m=finite(inside_med),dsm_annulus_median_m=finite(ring_med),dsm_relative_difference_m=finite(relief),dsm_patch_pixels=int(inside.sum()),dsm_annulus_pixels=int(annulus.sum()))
            props=dict(id=sid,name=sid,status='unreviewed_anomaly',block_id=b['id'],lon=round(lon,5),lat=round(lat,5),native_center_xy=[x,y],observation_ids=[sid+'-O1'],source_item_ids=[s['id'] for s in b['scenes']],dates=[s['datetime'][:10] for s in b['scenes']],coordinate_uncertainty_m=30,metrics=metrics,explanation='Exploratory persistent compact soil-colour anomaly; natural/modern alternatives unresolved',next_test='Inspect imagery/terrain/records before shortlisting; grounddatingneeded for archaeological attribution')
            feature=dict(type='Feature',geometry=mapping(geo),properties=props);component_rows.append(feature);all_features.append(feature)
        component_rows.sort(key=lambda f:f['properties']['metrics']['review_score'],reverse=True)
        selected=[]
        for f in component_rows:
            xy=np.array(f['properties']['native_center_xy'])
            if any(np.linalg.norm(xy-np.array(g['properties']['native_center_xy']))<params['minimum_review_center_separation_m'] for g in selected):continue
            selected.append(f)
            if len(selected)>=params['maximum_review_targets_per_block']:break
        review_features+=selected
        # Actual surrounding comparison points, selected with a fixed seed.
        controls=[]
        while len(controls)<params['random_comparison_points_per_block']:
            c=int(rng.integers(70,w-70));r=int(rng.integers(70,h-70))
            if count[r,c]<params['minimum_usable_dates']:continue
            x=left+(c+.5)*10;y=top-(r+.5)*10;lon,lat=togeo.transform(x,y)
            controls.append(dict(id=f'{b["id"]}-C{len(controls)+1:02d}',lon=lon,lat=lat,native_center_xy=[x,y],date_colour_z=[finite(z[r,c]) for z in zs],ndvi=[finite(s['ndvi'][r,c]) for s in scene_arrays]))
        # Four-date visual panels for targets, plus terrain and localcontext.
        for f in selected:
            props=f['properties'];x,y=props['native_center_xy'];c=(x-left)/10;r=(top-y)/10;half=70
            r0=max(0,int(r)-half);r1=min(h,int(r)+half);c0=max(0,int(c)-half);c1=min(w,int(c)+half)
            fig,axes=plt.subplots(2,3,figsize=(12,8))
            for ax,scene,arr in zip(axes.ravel()[:4],b['scenes'],scene_arrays):
                im=rgb_scale(arr['red'][r0:r1,c0:c1],arr['green'][r0:r1,c0:c1],arr['blue'][r0:r1,c0:c1]);im=np.nan_to_num(im).astype(np.uint8)
                ax.imshow(im,extent=[left+c0*10,left+c1*10,top-r1*10,top-r0*10]);ax.set_title(scene['datetime'][:10]);ax.plot(x,y,'+',color='#ff264d',ms=12,mew=1.5)
                xx,yy=np.array(shape(f['geometry']).exterior.coords).T;back=Transformer.from_crs(4326,b['native_epsg'],always_xy=True);xx,yy=back.transform(xx,yy);ax.plot(xx,yy,color='#fff83a',lw=.9);ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=6)
            ax=axes.ravel()[4];d0=max(0,int(r/3)-half//3);d1=min(demshape[0],int(r/3)+half//3);e0=max(0,int(c/3)-half//3);e1=min(demshape[1],int(c/3)+half//3)
            ax.imshow(dem[d0:d1,e0:e1],cmap='terrain',extent=[left+e0*30,left+e1*30,top-d1*30,top-d0*30]);ax.plot(x,y,'+',color='#ff264d',ms=12);ax.set_title('DSM~30m;surfaceobjects');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=6)
            ax=axes.ravel()[5];ax.axis('off');m=props['metrics'];ax.text(0,.96,f'{props["id"]}\n{props["lat"]:.5f}N,{props["lon"]:.5f}E\nOpticalpatch{m["apparent_patch_area_ha"]:.2f}ha\nMeanusable dates{m["usable_dates_mean"]:.1f}\nRelativeDSM{m["dsm_relative_difference_m"]:.2f}m\nMedianNDVI{m["median_ndvi"]:.2f}\n\nYellow:detectorpatch\nRedcross:patchcentroid\nThisdoesnotdateoccupation.\nNatural/modernrivalsrequire review.',transform=ax.transAxes,va='top',fontsize=11)
            fig.suptitle('Actual Sentinel-2 C1 scenes: '+props['id']+' — exploratory review target',fontsize=13)
            fig.tight_layout();path=a.output/'panels'/(props['id']+'.png');fig.savefig(path,dpi=140);plt.close(fig)
            props['panel_path']=rel(path);props['panel_sha256']=sha(path)
        # Persist only processing arrays locally; reusable outputs are aggregates.
        local=ROOT/'data/raw/2026-10-12-satellite-prospection/processed-v1';local.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(local/(b['id']+'.npz'),red=last['red'],green=last['green'],blue=last['blue'],nir=last['nir'],swir=last['swir16'],ndvi=last['ndvi'],valid=last['valid'],dem=dem,transform=np.array(list(transform)[:6]),dem_transform=np.array(list(dem_transform)[:6]))
        block_reports.append(dict(id=b['id'],name=b['name'],region_ids=b['region_ids'],bbox_lonlat=b['bbox_lonlat'],bounds_native_m=b['bounds_native_m'],native_epsg=b['native_epsg'],area_km2=b['width_m']*b['height_m']/1e6,scene_ids=[s['id'] for s in b['scenes']],scene_qa=qa,land_usable_atleast3dates_fraction=float((count>=3).mean()),connected_components_before_area_shape_filter=nlabels,retained_components=len(component_rows),review_targets=len(selected),comparison_points=controls,terrain_range_2_98_m=[float(lo),float(hi)],processed_local_path=rel(local/(b['id']+'.npz'))))
        print(json.dumps(dict(stage='processed',block=b['id'],retained=len(component_rows),review=len(selected))),flush=True)
    save(a.output/'all-anomalies.geojson',dict(type='FeatureCollection',features=all_features))
    save(a.output/'review-targets.geojson',dict(type='FeatureCollection',features=review_features))
    save(a.output/'block-analysis.json',dict(blocks=block_reports,parameters=params,parameters_sha256=sha(a.parameters),overlays=overlays))
    files=[dict(path=rel(path),sha256=sha(path),bytes=path.stat().st_size) for path in sorted(a.output.rglob('*')) if path.is_file()]
    save(a.output/'manifest.json',dict(processed_utc=datetime.now(timezone.utc).isoformat(),code_path=rel(Path(__file__)),code_sha256=sha(Path(__file__)),inputs=[dict(path=rel(path),sha256=sha(path)) for path in a.input],parameter_path=rel(a.parameters),parameter_sha256=sha(a.parameters),files=files,counts=dict(blocks=len(blocks),scenes=sum(len(b['scenes']) for b in blocks),anomalies=len(all_features),review_targets=len(review_features)),status='Exploratory processing endpoint; candidate attribution/visual review not yet completed'))
    print(json.dumps(dict(stage='complete',blocks=len(blocks),anomalies=len(all_features),review_targets=len(review_features))),flush=True)

if __name__=='__main__':main()
