"""Render a metre-sized raster crop with reversible pixel-centre coordinates."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import argparse
import numpy as np
import rasterio
from rasterio.windows import Window, from_bounds
from pyproj import Transformer, Geod
from PIL import Image, ImageDraw, ImageFilter
from common import sha256, write_json, check_space

def render(source, output, point, size=2000., layer="RGB", upsample=2, grid=100., edge=False, percentiles=(2,98)):
    if Path(output).exists() or Path(str(output)+".json").exists():
        raise FileExistsError(output)
    if int(upsample) != upsample or upsample < 1:
        raise ValueError("upsample must be a positive integer")
    with rasterio.open(source) as ds:
        epsg = ds.crs.to_epsg()
        x,y = Transformer.from_crs(4326, ds.crs, always_xy=True).transform(point[1],point[0])
        win = from_bounds(x-size/2,y-size/2,x+size/2,y+size/2, ds.transform)
        win = Window(int(np.floor(win.col_off)), int(np.floor(win.row_off)),int(np.ceil(win.width)),int(np.ceil(win.height)))
        if win.col_off < 0 or win.row_off < 0 or win.col_off+win.width > ds.width or win.row_off+win.height > ds.height:
            raise ValueError("crop exceeds source extent")
        desc = list(ds.descriptions)
        band_names = {name:i+1 for i,name in enumerate(desc) if name}
        choices = {"RGB":["B04","B03","B02"], "NIR":["B08","B04","B03"], "SWIR":["B12","B11","B04"],"brightness":["brightness"]}
        if layer == "brightness" and "brightness" not in band_names and all(b in band_names for b in ["B02","B03","B04","B08"]):
            a=ds.read([band_names[b] for b in ["B02","B03","B04","B08"]],window=win).mean(axis=0)[None]
        else:
            indices = [band_names[b] for b in choices[layer]] if band_names else ([1] if ds.count==1 else {"RGB":[3,2,1],"NIR":[4,3,2],"SWIR":[6,5,3],"brightness":[min(ds.count,7)]}[layer])
            a = ds.read(indices,window=win).astype(float)
        transform = ds.window_transform(win)
        source_affine = list(ds.transform)[:6]
    stretched=[]
    stretches=[]
    for band in a:
        lo,hi=np.nanpercentile(band,percentiles)
        stretches.append([float(lo),float(hi)])
        stretched.append(np.uint8(np.clip((band-lo)/max(hi-lo,1e-9),0,1)*255))
    img=Image.fromarray(stretched[0] if len(a)==1 else np.stack(stretched,axis=-1)).convert("RGB")
    if edge:
        img=img.filter(ImageFilter.UnsharpMask(radius=1.5,percent=150,threshold=3))
    img=img.resize((img.width*upsample,img.height*upsample),Image.Resampling.NEAREST)
    draw=ImageDraw.Draw(img)
    # Integer image coordinates denote pixel centres, including after enlargement.
    m=np.array([[transform.a/upsample,transform.b/upsample,transform.c+transform.a/(2*upsample)+transform.b/(2*upsample)],
                [transform.d/upsample,transform.e/upsample,transform.f+transform.d/(2*upsample)+transform.e/(2*upsample)],[0,0,1]])
    inv=np.linalg.inv(m)
    def px(e,n): return tuple((inv@np.array([e,n,1]))[:2])
    if grid>0:
        left,bottom=transform*(0,a.shape[1]); right,top=transform*(a.shape[2],0)
        for e in np.arange(np.ceil(left/grid)*grid,right,grid):
            q=px(e,top)[0]; draw.line([(q,0),(q,img.height)], fill=(230,180,40),width=1);draw.text((q+2,2),f"E {e:.0f}",fill="yellow",stroke_width=1,stroke_fill="black")
        for n in np.arange(np.ceil(bottom/grid)*grid,top,grid):
            q=px(left,n)[1];draw.line([(0,q),(img.width,q)],fill=(230,180,40),width=1);draw.text((2,q+2),f"N {n:.0f}",fill="yellow",stroke_width=1,stroke_fill="black")
    # A geodesic displaced toward true north determines the arrow in the UTM grid.
    lon2,lat2,_=Geod(ellps="WGS84").fwd(point[1],point[0],0,100)
    ex,ny=Transformer.from_crs(4326,epsg,always_xy=True).transform(lon2,lat2)
    v=np.array(px(ex,ny))-np.array(px(x,y));v=v/np.linalg.norm(v)*60
    tail=np.array([img.width-65.,95.]);tip=tail+v
    draw.line([tuple(tail),tuple(tip)],fill="cyan",width=3)
    normal=np.array([-v[1],v[0]])/np.linalg.norm(v)
    draw.polygon([tuple(tip),tuple(tip-v*.22+normal*6),tuple(tip-v*.22-normal*6)],fill="cyan")
    draw.text((tip[0]-25,tip[1]-18),"True N",fill="cyan",stroke_width=1,stroke_fill="black")
    bar=10**np.floor(np.log10(size/5)); bar*= max(1,int(size/5/bar))
    bl=bar/abs(transform.a)*upsample
    draw.line([(20,img.height-25),(20+bl,img.height-25)],fill="white",width=4)
    draw.text((20,img.height-46),f"{bar:g} m",fill="white",stroke_width=1,stroke_fill="black")
    check_space(output,img.width*img.height*4+10000)
    Path(output).parent.mkdir(parents=True,exist_ok=True);img.save(output)
    side=dict(schema_version=1,kind="imagery",source=str(Path(source).resolve()),source_sha256=sha256(source),png_sha256=sha256(output),epsg=epsg,pixel_to_utm=m.tolist(),source_affine=source_affine,layer=layer,percentile_stretch=stretches,upsample=upsample,pixel_convention="integer coordinates are pixel centres",grid_spacing_m=grid)
    write_json(str(output)+".json",side)
    return side

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("source");p.add_argument("output");p.add_argument("--point",type=float,nargs=2,metavar=("LAT","LON"),required=True);p.add_argument("--size",type=float,default=2000);p.add_argument("--layer",choices=["RGB","NIR","SWIR","brightness"],default="RGB");p.add_argument("--upsample",type=int,default=2);p.add_argument("--grid",type=float,default=100);p.add_argument("--edge",action="store_true");p.add_argument("--percentiles",type=float,nargs=2,default=[2,98]);a=p.parse_args();render(a.source,a.output,a.point,a.size,a.layer,a.upsample,a.grid,a.edge,a.percentiles)
if __name__=="__main__":main()
