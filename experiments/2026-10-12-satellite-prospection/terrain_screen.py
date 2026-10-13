"""Second exploratory screen: compact relative DSM rises with land-cover controls.

The method was introduced after inspection of the first colour detector. It
ranks geometric features on the existing approximately 30 m metric DSM grids.
Source imagery is used for review panels, never as a second independent score.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from scipy import ndimage as ndi
import rasterio
from rasterio import features
from rasterio.transform import Affine
from rasterio.warp import reproject, transform_bounds, Resampling
from rasterio.windows import Window, from_bounds
from rasterio.merge import merge
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform as geometry_transform
from shapely import make_valid

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
RAW = ROOT / "data/raw/2026-10-12-satellite-prospection"
CENSUS = ROOT / "experiments/2026-10-08-site-map-and-overview/data/sites-census.json"

PARAMETERS = {
    "method_status": "second exploratory terrain screen after first colour-result inspection",
    "grid_m": 30.0,
    "smoothing_sigma_pixels": 1.0,
    "background_sigma_pixels": 8.0,
    "positive_component_threshold_m": 1.0,
    "low_support_threshold_m": 0.5,
    "minimum_peak_residual_m": 2.0,
    "minimum_annulus_prominence_m": 2.0,
    "minimum_area_ha": 0.5,
    "maximum_area_ha": 30.0,
    "maximum_axis_ratio": 4.0,
    "minimum_pixel_perimeter_compactness": 0.15,
    "ridge_low_support_area_ha": 30.0,
    "ridge_support_expansion_ratio": 4.0,
    "maximum_component_built_fraction": 0.10,
    "built_distance_mask_fraction": 0.30,
    "minimum_peak_distance_to_built_m": 60.0,
    "maximum_component_water_fraction": 0.10,
    "minimum_landcover_valid_fraction": 0.95,
    "minimum_ring_valid_fraction": 0.95,
    "annulus_inner_min_m": 180.0,
    "annulus_gap_from_equivalent_radius_m": 90.0,
    "annulus_width_m": 300.0,
    "edge_margin_m": 1000.0,
    "maximum_review_features_per_block": 6,
    "minimum_review_peak_separation_m": 500.0,
    "random_context_points_per_block": 8,
    "negative_control_examples_per_kind": 2,
    "reference_context_radii_m": [200.0, 500.0, 1000.0],
    "random_seed": 20261012,
    "panel_halfwidth_m": 750.0,
    "rank_formula": "annulus_peak_prominence_m * sqrt(compactness) / sqrt(axis_ratio)",
    "rank_meaning": "geometric review ordering only; no archaeological probability or dating",
    "WorldCover_product": "ESA WorldCover 10 m 2021 v200",
    "WorldCover_fraction_method": "binary source classes projected with area-averaging onto the 30 m DSM grid; categorical display uses nearest neighbour",
    "WorldCover_controls": {"built": 50, "cropland": 40, "tree": 10, "water": 80},
}


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def fingerprint(path):
    path = Path(path)
    data = path.read_bytes()
    return {"path": rel(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(clean(value), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def weighted_gaussian(array, sigma):
    valid = np.isfinite(array)
    weight = ndi.gaussian_filter(valid.astype(float), sigma, mode="nearest")
    numerator = ndi.gaussian_filter(np.where(valid, array, 0.0), sigma, mode="nearest")
    return np.divide(numerator, weight, out=np.full(array.shape, np.nan), where=weight > 0.99)


def terrain_fields(dem):
    smooth = weighted_gaussian(dem, PARAMETERS["smoothing_sigma_pixels"])
    background = weighted_gaussian(dem, PARAMETERS["background_sigma_pixels"])
    return smooth, background, smooth - background


def sanity_checks():
    rows, cols = np.indices((121, 121))
    hill = 7.0 * np.exp(-((rows-60)**2+(cols-60)**2)/(2*3.0**2))
    _, _, residual = terrain_fields(hill)
    _, _, translated = terrain_fields(hill + 100.0)
    plane = 0.03 * rows + 0.02 * cols
    _, _, detrended = terrain_fields(hill + plane)
    core = np.s_[35:-35, 35:-35]
    checks = [
        {"name": "constant_vertical_offset_preserves_residual", "passed": bool(np.allclose(residual, translated, atol=1e-10)),
         "maximum_absolute_difference": float(np.nanmax(abs(residual-translated)))},
        {"name": "planar_trend_preserves_interior_residual", "passed": bool(np.allclose(residual[core], detrended[core], atol=1e-10)),
         "maximum_core_difference": float(np.nanmax(abs(residual[core]-detrended[core])))},
        {"name": "synthetic_hill_has_local_positive_peak", "passed": bool(residual[60,60] > 5 and residual[60,60] == np.nanmax(residual)),
         "peak_residual_m": float(residual[60,60])},
        {"name": "hectare_conversion_for_native_support", "passed": 6*30*30/10000 == 0.54, "six_grid_cells_ha": 0.54},
    ]
    if not all(c["passed"] for c in checks):
        raise AssertionError(checks)
    return checks


def worldcover_windows(block, transform, destination_shape, stamp):
    bounds = block["bbox_lonlat"]
    epsg = block["native_epsg"]
    fractions = {k: np.zeros(destination_shape, np.float32) for k in ["valid", "built", "cropland", "tree", "water"]}
    classes = np.zeros(destination_shape, np.uint8)
    records = []
    w,s,e,n = bounds
    for lat in range(math.floor(s/3)*3, math.floor(n/3)*3+1, 3):
        for lon in range(math.floor(w/3)*3, math.floor(e/3)*3+1, 3):
            tile = ("N" if lat >= 0 else "S") + f"{abs(lat):02d}" + ("E" if lon >= 0 else "W") + f"{abs(lon):03d}"
            clip = [max(w,lon), max(s,lat), min(e,lon+3), min(n,lat+3)]
            if clip[0] >= clip[2] or clip[1] >= clip[3]:
                continue
            url = f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=1, GDAL_HTTP_TIMEOUT=40):
                with rasterio.open(url) as source:
                    fractional = from_bounds(*clip, transform=source.transform)
                    left = max(0, math.floor(fractional.col_off)-2)
                    top = max(0, math.floor(fractional.row_off)-2)
                    right = min(source.width, math.ceil(fractional.col_off+fractional.width)+2)
                    bottom = min(source.height, math.ceil(fractional.row_off+fractional.height)+2)
                    window = Window(left,top,right-left,bottom-top)
                    data = source.read(1, window=window)
                    affine = source.window_transform(window)
                    profile = source.profile.copy()
                    profile.update(width=data.shape[1], height=data.shape[0], transform=affine, compress="deflate", tiled=True,
                                   blockxsize=256, blockysize=256)
                    path = RAW / f"SPATIAL_CONTROL_{stamp}_{block['id']}_WorldCover_{tile}.tif"
                    if path.exists():
                        raise FileExistsError(path)
                    with rasterio.open(path, "w", **profile) as target:
                        target.write(data,1)
                    records.append({"block_id": block["id"], "tile": tile, "source_url": url, **fingerprint(path),
                                    "source_window": [left,top,right-left,bottom-top], "native_crs": str(source.crs),
                                    "native_transform": list(affine)[:6], "source_nodata": source.nodata,
                                    "native_shape": list(data.shape), "product": "WorldCover 2021 v200", "license": "CC BY 4.0",
                                    "acquisition": "Unsigned COG range window; no complete remote object downloaded",
                                    "parent_object_checksum_verified": False})
    # Mosaic on the common geographic source grid before averaging. Independently
    # normalised per-tile averages could double count a 30 m cell crossing a seam.
    mosaic, affine = merge([str(ROOT/r['path']) for r in records], nodata=0)
    data = mosaic[0]
    reproject((data != 0).astype(np.float32), fractions['valid'], src_transform=affine, src_crs=4326,
              dst_transform=transform, dst_crs=epsg, resampling=Resampling.average, src_nodata=None)
    for name, code in PARAMETERS['WorldCover_controls'].items():
        reproject((data == code).astype(np.float32), fractions[name], src_transform=affine, src_crs=4326,
                  dst_transform=transform, dst_crs=epsg, resampling=Resampling.average, src_nodata=None)
    reproject(data, classes, src_transform=affine, src_crs=4326, dst_transform=transform, dst_crs=epsg,
              resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
    for name in fractions:
        fractions[name] = np.clip(fractions[name],0,1)
    return fractions, classes, records


def local_description(dem, residual, row, col, fractions, radius=60.0, annulus_inner=180.0, annulus_outer=480.0):
    grid = PARAMETERS["grid_m"]
    k = math.ceil(annulus_outer/grid)
    r0=max(0,row-k); r1=min(dem.shape[0],row+k+1)
    c0=max(0,col-k); c1=min(dem.shape[1],col+k+1)
    rr,cc = np.indices((r1-r0,c1-c0)); distance = np.hypot(rr+r0-row,cc+c0-col)*grid
    inner = distance <= radius
    ring = (distance >= annulus_inner) & (distance <= annulus_outer)
    values = dem[r0:r1,c0:c1]
    expected = np.count_nonzero((np.hypot(*np.indices((2*k+1,2*k+1))-k)*grid >= annulus_inner) &
                                (np.hypot(*np.indices((2*k+1,2*k+1))-k)*grid <= annulus_outer))
    valid = ring & np.isfinite(values)
    baseline = float(np.median(values[valid])) if np.any(valid) else math.nan
    inner_values = values[inner & np.isfinite(values)]
    return {"point_elevation_m": float(dem[row,col]), "inner_radius_m": radius,
            "inner_elevation_median_m": float(np.median(inner_values)) if len(inner_values) else math.nan,
            "annulus_inner_m": annulus_inner,"annulus_outer_m": annulus_outer,
            "annulus_elevation_median_m": baseline, "point_minus_annulus_m": float(dem[row,col]-baseline),
            "ring_valid_fraction": float(np.count_nonzero(valid)/max(expected,1)),
            "point_residual_m": float(residual[row,col]),
            "inner_WorldCover_fractions": {name:float(np.mean(layer[r0:r1,c0:c1][inner])) for name,layer in fractions.items()}}


def component_features(block, dem, transform, fractions, classes):
    smooth, background, residual = terrain_fields(dem.astype(np.float64))
    labels, label_count = ndi.label(np.isfinite(residual) & (residual > PARAMETERS["positive_component_threshold_m"]),
                                    structure=np.ones((3,3),np.uint8))
    low_labels,_ = ndi.label(np.isfinite(residual) & (residual > PARAMETERS["low_support_threshold_m"]),
                             structure=np.ones((3,3),np.uint8))
    low_counts = np.bincount(low_labels.ravel())
    built_distance = ndi.distance_transform_edt(fractions["built"] < PARAMETERS["built_distance_mask_fraction"])*30
    slices = ndi.find_objects(labels)
    togeo = Transformer.from_crs(block["native_epsg"],4326,always_xy=True)
    result=[]; tiny_count=0
    for label, slc in enumerate(slices, start=1):
        if slc is None:
            continue
        mask=labels[slc] == label
        count=int(mask.sum()); area=count*900/10000
        if area < PARAMETERS["minimum_area_ha"]:
            tiny_count += 1
            continue
        rr,cc=np.where(mask); rr=rr+slc[0].start;cc=cc+slc[1].start
        best=int(np.argmax(residual[rr,cc]));r=int(rr[best]);c=int(cc[best])
        x,y=transform*(c+0.5,r+0.5);lon,lat=togeo.transform(x,y)
        geometries=[shape(g) for g,value in features.shapes(mask.astype(np.uint8),mask=mask,
                    transform=transform*Affine.translation(slc[1].start,slc[0].start),connectivity=8) if value==1]
        if len(geometries)!=1:
            raise AssertionError("A connected component must return one raster geometry")
        geom=make_valid(geometries[0])
        if not math.isclose(geom.area,count*900,abs_tol=1e-6):
            raise AssertionError('Polygon support must preserve the 30 m cell area')
        # Pixel area is the primary support measure; polygon perimeter is resolution-dependent.
        covariance=np.cov(np.stack([cc*30,rr*30]),bias=True)+np.eye(2)*30**2/12
        eigenvalues=np.linalg.eigvalsh(covariance);axis=float(math.sqrt(eigenvalues[-1]/eigenvalues[0]))
        compact=float(4*math.pi*geom.area/max(geom.length**2,1))
        inner=max(PARAMETERS["annulus_inner_min_m"],math.sqrt(count*900/math.pi)+PARAMETERS["annulus_gap_from_equivalent_radius_m"])
        outer=inner+PARAMETERS["annulus_width_m"]
        local=local_description(dem,residual,r,c,fractions,annulus_inner=inner,annulus_outer=outer)
        low_id=int(low_labels[r,c]);low_area=float(low_counts[low_id]*900/10000) if low_id else area
        expansion=low_area/area
        ridge_connected=low_area>PARAMETERS["ridge_low_support_area_ha"] and expansion>PARAMETERS["ridge_support_expansion_ratio"]
        cover={name:float(np.mean(layer[rr,cc])) for name,layer in fractions.items()}
        left,bottom,right,top=block['bounds_native_m']
        margin=min(x-left,right-x,y-bottom,top-y)
        reasons=[]
        if area>PARAMETERS['maximum_area_ha']:reasons.append('oversize connected support')
        if float(residual[r,c])<PARAMETERS['minimum_peak_residual_m']:reasons.append('weak local residual')
        if not math.isfinite(local['point_minus_annulus_m']):reasons.append('unresolved annulus prominence')
        elif local['point_minus_annulus_m']<PARAMETERS['minimum_annulus_prominence_m']:reasons.append('weak annulus prominence')
        if axis>PARAMETERS['maximum_axis_ratio']:reasons.append('elongated support')
        if compact<PARAMETERS['minimum_pixel_perimeter_compactness']:reasons.append('low perimeter compactness')
        if ridge_connected:reasons.append('connected to extensive lower-threshold height support')
        if cover['built']>PARAMETERS['maximum_component_built_fraction']:reasons.append('built-land overlap')
        if float(built_distance[r,c])<PARAMETERS['minimum_peak_distance_to_built_m']:reasons.append('near built-land pixels')
        if cover['water']>PARAMETERS['maximum_component_water_fraction']:reasons.append('water overlap')
        if cover['valid']<PARAMETERS['minimum_landcover_valid_fraction']:reasons.append('unresolved land-cover coverage')
        if local['ring_valid_fraction']<PARAMETERS['minimum_ring_valid_fraction']:reasons.append('incomplete surrounding ring')
        if margin<PARAMETERS['edge_margin_m']:reasons.append('block-edge context')
        score=max(local['point_minus_annulus_m'],0)*math.sqrt(max(compact,0))/math.sqrt(axis) if math.isfinite(local['point_minus_annulus_m']) else 0.0
        props={'id':f"{block['id']}-T{label:04d}",'block_id':block['id'],'source_component_label':label,
               'lon':lon,'lat':lat,'peak_native_xy':[x,y],'peak_row_col':[r,c],
               'support_area_ha':area,'support_grid_cells':count,'equivalent_radius_m':math.sqrt(count*900/math.pi),
               'peak_residual_m':float(residual[r,c]),'component_residual_median_m':float(np.median(residual[rr,cc])),
               'pixel_perimeter_compactness':compact,'axis_ratio':axis,'lower_threshold_support_area_ha':low_area,
               'support_expansion_ratio':expansion,'ridge_connectivity_flag':ridge_connected,
               'WorldCover2021_fractions':cover,'distance_to_built_mask_m':float(built_distance[r,c]),
               'edge_margin_m':margin,'local_measurement':local,'geometric_rank_score':score,
               'review_eligible':not reasons,'screening_flags':reasons,
               'status':'geometric feature pending independent visual/context review',
               'coordinate_support':'30 m metric grid from approximately 1 arcsec DSM; footprint is threshold support, not settlement boundary',
               'scene_ids':[s['id'] for s in block['scenes']], 'DEM_tiles':[s['tile_id'] for s in block['dem_tiles']],
               'archaeological_probability':None,'occupation_date':None,'WorldCover_product':'2021 v200'}
        result.append({'type':'Feature','geometry':mapping(geometry_transform(togeo.transform,geom)),'properties':props})
    result.sort(key=lambda f:(-f['properties']['geometric_rank_score'],f['properties']['id']))
    selected=[]
    for f in result:
        p=f['properties']
        if not p['review_eligible']:continue
        if any(np.linalg.norm(np.array(p['peak_native_xy'])-np.array(g['properties']['peak_native_xy']))<PARAMETERS['minimum_review_peak_separation_m'] for g in selected):continue
        selected.append(f)
        if len(selected)>=PARAMETERS['maximum_review_features_per_block']:break
    summary={'connected_components':label_count,'subminimum_support_components':tiny_count,'retained_support_components':len(result),
             'review_eligible_components':sum(f['properties']['review_eligible'] for f in result),'selected_for_review':len(selected),
             'screening_flag_counts':{reason:sum(reason in f['properties']['screening_flags'] for f in result)
                                     for reason in sorted({r for f in result for r in f['properties']['screening_flags']})}}
    return result,selected,summary,residual,labels


def reference_and_controls(block, dem, transform, residual, fractions, feature_rows, census):
    inverse=~transform;togeo=Transformer.from_crs(block['native_epsg'],4326,always_xy=True)
    toxy=Transformer.from_crs(4326,block['native_epsg'],always_xy=True)
    references=[]
    names={'B01':{'ganweriwala'},'B02':{'harappa'},'B03':{'juna-khatiya'},'B04':{'kalibangan'}}
    sites=[s for s in census['sites'] if s['id'] in names[block['id']]]
    sites.append({'id':block['id']+'-block-reference','name':block['name']+' selection point','lon':block['center_lonlat'][0],
                  'lat':block['center_lonlat'][1],'coord_source_id':'block-selection','coord_locator':block['selection_basis']})
    for site in sites:
        x,y=toxy.transform(site['lon'],site['lat']);col,row=inverse*(x,y);r=int(row);c=int(col)
        if not(0<=r<dem.shape[0] and 0<=c<dem.shape[1]):continue
        descriptions=[]
        for radius in PARAMETERS['reference_context_radii_m']:
            yy,xx=np.indices(dem.shape);mask=np.hypot(xx-c,yy-r)*30<=radius
            descriptors={'radius_m':radius,'grid_cells':int(mask.sum()),'context_area_ha':float(mask.sum()*900/10000),
                         'elevation_10_90_percentile_m':np.percentile(dem[mask],[10,90]).tolist(),
                         'maximum_residual_m':float(np.nanmax(residual[mask])),
                         'positive_support_fraction':float(np.mean(residual[mask]>PARAMETERS['positive_component_threshold_m'])),
                         'WorldCover2021_fractions':{name:float(np.mean(a[mask])) for name,a in fractions.items()}}
            descriptions.append(descriptors)
        nearest=sorted([{'feature_id':f['properties']['id'],'distance_m':float(np.linalg.norm(np.array(f['properties']['peak_native_xy'])-[x,y])),
                         'review_eligible':f['properties']['review_eligible'],'support_area_ha':f['properties']['support_area_ha']}
                        for f in feature_rows],key=lambda z:z['distance_m'])[:3]
        references.append({'id':site['id'],'name':site['name'],'lon':site['lon'],'lat':site['lat'],
                           'coordinate_source_id':site.get('coord_source_id'),'coordinate_locator':site.get('coord_locator'),
                           'coordinate_status':site.get('coord_status','published block selection reference'),
                           'footprint_status':'No authenticated site-footprint polygon supplied. These radii are context windows, not occupied or excavated boundaries.',
                           'context_windows':descriptions,'nearest_terrain_supports':nearest})
    rng=np.random.default_rng(PARAMETERS['random_seed']+int(block['id'][1:]))
    controls=[];margin=math.ceil(PARAMETERS['edge_margin_m']/30)
    for k in range(PARAMETERS['random_context_points_per_block']):
        row=int(rng.integers(margin,dem.shape[0]-margin));col=int(rng.integers(margin,dem.shape[1]-margin));x,y=transform*(col+.5,row+.5);lon,lat=togeo.transform(x,y)
        controls.append({'id':f"{block['id']}-RC{k+1:02d}",'kind':'seeded frame context point','lon':lon,'lat':lat,
                         'local_measurement':local_description(dem,residual,row,col,fractions),
                         'meaning':'Diagnostic context, not verified archaeological absence'})
    kinds={
        'built_land_height':lambda p:p['WorldCover2021_fractions']['built']>0.3,
        'extended_or_elongated_height':lambda p:p['ridge_connectivity_flag'] or p['axis_ratio']>4 or p['support_area_ha']>30,
        'cropland_height':lambda p:p['WorldCover2021_fractions']['cropland']>0.5,
    }
    for kind,predicate in kinds.items():
        chosen=[f for f in feature_rows if predicate(f['properties'])][:PARAMETERS['negative_control_examples_per_kind']]
        for f in chosen:
            controls.append({'id':f['properties']['id']+'-'+kind,'feature_id':f['properties']['id'],'kind':kind,
                             'lon':f['properties']['lon'],'lat':f['properties']['lat'],'local_measurement':f['properties']['local_measurement'],
                             'meaning':'Source-land-cover or geometry rival example; final visual classification is separate'})
    return references,controls


def scene_patch(block, scene, bounds):
    data={}; records={r['band']:r for r in scene['bands']};out_shape=(150,150)
    for band in ['red','green','blue']:
        record=records[band]
        with rasterio.open(ROOT/record['local_path']) as src:
            local_bounds=transform_bounds(block['native_epsg'],src.crs,*bounds,densify_pts=21)
            window=from_bounds(*local_bounds,transform=src.transform)
            values=src.read(1,window=window,out_shape=out_shape,boundless=True,fill_value=0,resampling=Resampling.bilinear).astype(float)
            metadata=record['raster_bands'][0];mask=values==metadata.get('nodata',0)
            values=values*metadata['scale']+metadata.get('offset',0);values[mask]=np.nan;data[band]=values
    rgb=np.dstack([data['red'],data['green'],data['blue']]);rgb=np.clip(rgb/.45,0,1)**.8
    return np.nan_to_num(rgb)


def panel(block, feature, dem, residual, classes, transform, output):
    p=feature['properties'];x,y=p['peak_native_xy'];half=PARAMETERS['panel_halfwidth_m'];bounds=[x-half,y-half,x+half,y+half]
    fig,axes=plt.subplots(2,3,figsize=(12,8))
    for ax,scene in zip(axes.flat[:4],block['scenes']):
        ax.imshow(scene_patch(block,scene,bounds),extent=[bounds[0],bounds[2],bounds[1],bounds[3]])
        ax.plot(x,y,'+',color='#ff273f',markersize=10);ax.set_title(scene['datetime'][:10])
    c,r=(~transform)*(x,y);k=math.ceil(half/30);r0=max(0,int(r)-k);r1=min(dem.shape[0],int(r)+k+1);c0=max(0,int(c)-k);c1=min(dem.shape[1],int(c)+k+1)
    extent=[transform.c+c0*30,transform.c+c1*30,transform.f-r1*30,transform.f-r0*30]
    ax=axes.flat[4];vmax=max(3,float(np.nanpercentile(np.abs(residual[r0:r1,c0:c1]),98)))
    image=ax.imshow(residual[r0:r1,c0:c1],cmap='RdBu_r',vmin=-vmax,vmax=vmax,extent=extent);ax.plot(x,y,'+',color='black',markersize=10)
    fig.colorbar(image,ax=ax,fraction=.045,label='Relative height (m)');ax.set_title('DSM high-pass, 30 m grid')
    codes=[0,10,20,30,40,50,60,70,80,90,95,100]
    colors=['#ffffff','#006400','#ffbb22','#ffff4c','#f096ff','#fa0000','#b4b4b4','#f0f0f0','#0064c8','#0096a0','#00cf75','#fae6a0']
    values=classes[r0:r1,c0:c1];indexed=np.zeros(values.shape,int)
    for i,code in enumerate(codes):indexed[values==code]=i
    ax=axes.flat[5];ax.imshow(indexed,cmap=ListedColormap(colors),vmin=-.5,vmax=len(codes)-.5,extent=extent);ax.plot(x,y,'+',color='black',markersize=10)
    ax.set_title('WorldCover 2021: red built; pink crop')
    native=geometry_transform(Transformer.from_crs(4326,block['native_epsg'],always_xy=True).transform,shape(feature['geometry']))
    for ax in axes.flat:
        if native.geom_type=='Polygon':geoms=[native]
        else:geoms=list(native.geoms)
        for g in geoms:
            xx,yy=np.array(g.exterior.coords).T;ax.plot(xx,yy,color='#fff73d',lw=.9)
        ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[1],bounds[3]);ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=6)
    title=f"{p['id']}: {p['lat']:.5f} N, {p['lon']:.5f} E; support {p['support_area_ha']:.2f} ha; prominence {p['local_measurement']['point_minus_annulus_m']:.2f} m"
    fig.suptitle(title,fontsize=12)
    fig.text(.5,.015,'Yellow: threshold support; cross: DSM peak. Contains modified Copernicus Sentinel data (2025, 2026).\nDSM: produced using Copernicus WorldDEM-30; DLR/Airbus/EU/ESA source notice in manifest. © ESA WorldCover project 2021 / modified Sentinel data (2021).',ha='center',fontsize=7)
    fig.tight_layout(rect=[0,.055,1,.955]);path=output/'panels'/f"{p['id']}.png";fig.savefig(path,dpi=140);plt.close(fig)
    return fingerprint(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=BASE/'outputs-terrain-v1')
    args=parser.parse_args();output=args.output.resolve()
    if output.exists():parser.error('Output exists. Preserve it and use a new endpoint.')
    checks=sanity_checks()
    inputs=[];blocks=[]
    for run in ['raster-run-v1','raster-run-v2']:
        path=RAW/run/'manifest.json';inputs.append(fingerprint(path));blocks.extend(load(path)['blocks'])
    inputs.append(fingerprint(CENSUS));census=load(CENSUS)
    for block in blocks:inputs.append(fingerprint(RAW/'processed-v1'/f"{block['id']}.npz"))
    for block in blocks:
        inputs.extend(fingerprint(ROOT/r['local_path']) for r in block['dem_tiles'])
    prior=[]
    for dirname in ['outputs-v1','outputs-v2']:
        m=load(BASE/dirname/'manifest.json');prior.append({'endpoint':dirname,'manifest':fingerprint(BASE/dirname/'manifest.json'),'files':m['files']})
    output.mkdir(parents=True,exist_ok=False);(output/'panels').mkdir()
    started=datetime.now(timezone.utc).isoformat();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    write(output/'parameters.json',{'recorded_before_terrain_extraction_utc':started,**PARAMETERS})
    all_features=[];review=[];reports=[];acquisitions=[];all_controls=[];all_references=[];derived_records=[]
    for block in sorted(blocks,key=lambda b:b['id']):
        print(json.dumps({'stage':'terrain','block':block['id']}),flush=True)
        with np.load(RAW/'processed-v1'/f"{block['id']}.npz",allow_pickle=False) as data:
            dem=data['dem'].astype(np.float64);transform=Affine(*data['dem_transform'])
        if transform.a!=30 or transform.e!=-30 or transform.b!=0 or transform.d!=0:
            raise ValueError('Terrain grid must have approximately native 30 m metric support; no 10 m elevation enlargement.')
        fractions,classes,records=worldcover_windows(block,transform,dem.shape,stamp);acquisitions+=records
        rows,selected,summary,residual,labels=component_features(block,dem,transform,fractions,classes)
        references,controls=reference_and_controls(block,dem,transform,residual,fractions,rows,census)
        for f in rows:
            f['properties']['nearest_reference_distance_m']=min((np.linalg.norm(np.array(f['properties']['peak_native_xy'])-np.array(Transformer.from_crs(4326,block['native_epsg'],always_xy=True).transform(a['lon'],a['lat']))) for a in references),default=math.nan)
        # Selected diagnostic rival features get panels in addition to the review budget.
        panel_ids={f['properties']['id'] for f in selected}
        panel_ids.update(c['feature_id'] for c in controls if 'feature_id' in c)
        for f in rows:
            if f['properties']['id'] in panel_ids:f['properties']['panel']=panel(block,f,dem,residual,classes,transform,output)
        derived=RAW/f"SPATIAL_CONTROL_{stamp}_{block['id']}_derived.npz"
        np.savez_compressed(derived,residual=residual.astype(np.float32),component_labels=labels,WorldCover_classes=classes,
                            **{f'WorldCover_fraction_{k}':v for k,v in fractions.items()},transform=np.array(list(transform)[:6]))
        derived_records.append(fingerprint(derived))
        metric_bounds=rasterio.transform.array_bounds(*dem.shape,transform)
        reports.append({'block_id':block['id'],'block_name':block['name'],'scene_ids':[s['id'] for s in block['scenes']],
                        'grid_shape':list(dem.shape),'grid_transform':list(transform)[:6],'grid_epsg':block['native_epsg'],
                        'processed_bounds_m':list(metric_bounds),'analysis_inner_area_km2':max(block['width_m']-2000,0)*max(block['height_m']-2000,0)/1e6,
                        'summary':summary,'WorldCover_block_fractions':{name:float(np.mean(a)) for name,a in fractions.items()},
                        'terrain_percentile_2_98_m':np.percentile(dem,[2,98]).tolist(),'reference_points':references,'diagnostic_controls':controls})
        all_features+=rows;review+=selected;all_controls+=controls;all_references+=references
        print(json.dumps({'stage':'terrain-complete','block':block['id'],**summary}),flush=True)
    write(output/'all-terrain-supports.geojson',{'type':'FeatureCollection','features':all_features})
    write(output/'review-targets.geojson',{'type':'FeatureCollection','features':review})
    write(output/'block-analysis.json',{'method':PARAMETERS['method_status'],'blocks':reports,'control_interpretation':'Selected references and rival examples are diagnostic; no held-out detector performance or archaeological absence is measured.'})
    write(output/'WorldCover-acquisition.json',{'generated_utc':datetime.now(timezone.utc).isoformat(),'windows':acquisitions,
             'derived_local_arrays':derived_records,'license':'CC BY 4.0','dataset_DOI':'10.5281/zenodo.7254221'})
    csvpath=output/'review-targets.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as stream:
        fields=['id','block_id','lon','lat','support_area_ha','peak_residual_m','annulus_peak_prominence_m','axis_ratio','compactness','built_fraction','cropland_fraction','geometric_rank_score','panel_path']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for f in review:
            p=f['properties'];writer.writerow({'id':p['id'],'block_id':p['block_id'],'lon':p['lon'],'lat':p['lat'],'support_area_ha':p['support_area_ha'],
                'peak_residual_m':p['peak_residual_m'],'annulus_peak_prominence_m':p['local_measurement']['point_minus_annulus_m'],
                'axis_ratio':p['axis_ratio'],'compactness':p['pixel_perimeter_compactness'],'built_fraction':p['WorldCover2021_fractions']['built'],
                'cropland_fraction':p['WorldCover2021_fractions']['cropland'],'geometric_rank_score':p['geometric_rank_score'],'panel_path':p['panel']['path']})
    # Verify earlier results and all used inputs after writing this independent endpoint.
    for record in inputs:
        observed=fingerprint(ROOT/record['path']);checks.append({'name':'input_hash_preserved:'+record['path'],'passed':observed['sha256']==record['sha256']})
    for previous in prior:
        observed=fingerprint(ROOT/previous['manifest']['path']);checks.append({'name':'prior_manifest_preserved:'+previous['endpoint'],'passed':observed['sha256']==previous['manifest']['sha256']})
        for record in previous['files']:
            checks.append({'name':'prior_output_preserved:'+record['path'],'passed':fingerprint(ROOT/record['path'])['sha256']==record['sha256']})
    checks.append({'name':'all_review_supports_within_declared_area','passed':all(.5<=f['properties']['support_area_ha']<=30 for f in review)})
    checks.append({'name':'all_review_targets_pass_explicit_geometry_and_landcover_flags','passed':all(not f['properties']['screening_flags'] for f in review)})
    checks.append({'name':'all_probability_and_date_fields_unassigned','passed':all(f['properties']['archaeological_probability'] is None and f['properties']['occupation_date'] is None for f in all_features)})
    failed=[c for c in checks if not c['passed']]
    write(output/'verification.json',{'checks':checks,'passed_count':len(checks)-len(failed),'failed_count':len(failed),'count_interpretation':'Implementation bookkeeping, not archaeological validation'})
    files=[fingerprint(path) for path in sorted(output.rglob('*')) if path.is_file()]
    write(output/'manifest.json',{'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),'status':'second exploratory terrain-screening endpoint',
             'code':fingerprint(Path(__file__)),'inputs':inputs,'outputs':files,'parameters':fingerprint(output/'parameters.json'),
             'counts':{'blocks':len(blocks),'terrain_supports':len(all_features),'review_targets':len(review),'WorldCover_native_windows':len(acquisitions),
                       'reference_context_points':len(all_references),'diagnostic_controls':len(all_controls)},
             'source_notice':'Contains modified Copernicus Sentinel data (2025, 2026). Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.',
             'licence_pointer':'research/data-source-register.json; WorldCover DOI 10.5281/zenodo.7254221; GLO-30-F Article 6 obligations apply to transformed DSM products.',
             'pipeline_relation':'The first colour code and outputs-v1/v2 are preserved. This screen was introduced after their inspection and is not a held-out confirmation.',
             'inference_scope':'Threshold supports and diagnostic context, with no occupation date, archaeological probability or new-site attribution.',
             'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,'rasterio':rasterio.__version__}})
    if failed:raise AssertionError(failed)
    print(json.dumps({'stage':'complete','output':rel(output),'terrain_supports':len(all_features),'review_targets':len(review),'checks_passed':len(checks)}),flush=True)


if __name__=='__main__':main()
