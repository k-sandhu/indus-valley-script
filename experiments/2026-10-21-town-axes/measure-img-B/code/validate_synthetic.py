"""Synthetic check of the gradient-histogram method near the cardinal directions (role img-B).

We draw short wall-like segments in two perpendicular families at a known
deviation on an 8x supersampled canvas, average down to the working resolution
(as a sensor and a resampling step would), add noise, optionally re-encode as
JPEG (quality 90, 75, 50) or sharpen and re-encode, and measure the peak.
Output: ../synthetic_validation.json
"""
import json
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, cv2, math, io, orient
from PIL import Image
rng=np.random.default_rng(2)
SS=8
def synth(b, N=800, spacing=23, width_m=2.0, seglen=(15,50)):
    big=np.full((N*SS,N*SS),140,np.float32)
    for bb in (b, b+90):
        t=math.radians(bb); dx,dy=math.sin(t),-math.cos(t); nx,ny=-dy,dx
        for k in range(-N,N,spacing):
            for s in range(-N,N,40):
                if rng.random()<0.4: continue
                cx,cy=N/2+k*nx+s*dx,N/2+k*ny+s*dy
                L=rng.uniform(*seglen)
                p0=(int(round(cx*SS)),int(round(cy*SS))); p1=(int(round((cx+L*dx)*SS)),int(round((cy+L*dy)*SS)))
                cv2.line(big,p0,p1,90,int(width_m*SS),cv2.LINE_8)
    img=cv2.resize(big,(N,N),interpolation=cv2.INTER_AREA)
    img=img+rng.normal(0,5,img.shape)
    img=np.clip(img,0,255).astype(np.uint8)
    return np.dstack([img]*3)
poly=[[100,100],[700,100],[700,700],[100,700]]
rows=[]
for b in [0.0,0.5,1.0,2.0,3.0,5.0,8.0]:
    rgb=synth(b)
    r0=orient.analyse(rgb,[poly],m_per_px=0.5,n_boot=1)['peak_deviation_deg']
    out=[]
    for q in (90,75,50):
        buf=io.BytesIO(); Image.fromarray(rgb).save(buf,format='JPEG',quality=q)
        rj=np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert('RGB'))
        out.append(round(orient.analyse(rj,[poly],m_per_px=0.5,n_boot=1)['peak_deviation_deg'],3))
    # sharpened then jpeg
    blur=cv2.GaussianBlur(rgb.astype(np.float32),(0,0),1.0); sh=np.clip(rgb+1.0*(rgb-blur),0,255).astype(np.uint8)
    buf=io.BytesIO(); Image.fromarray(sh).save(buf,format='JPEG',quality=75)
    rs=np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert('RGB'))
    out.append(round(orient.analyse(rs,[poly],m_per_px=0.5,n_boot=1)['peak_deviation_deg'],3))
    rows.append({'true_deviation': b, 'measured_raw': round(r0,3), 'jpeg_q90': out[0], 'jpeg_q75': out[1], 'jpeg_q50': out[2], 'sharpened_jpeg_q75': out[3]})
    print(b, round(r0,3), out)
(Path(__file__).resolve().parent.parent / 'synthetic_validation.json').write_text(json.dumps({'description': 'Recovered gradient-histogram peaks for synthetic two-family wall patterns at known deviations; see code/validate_synthetic.py', 'rows': rows}, indent=1))
