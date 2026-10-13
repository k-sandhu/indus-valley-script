"""Author a coordinate diagram and GeoJSON from coarse proposed search windows."""
from pathlib import Path
import argparse, json, html, hashlib

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists(): raise FileExistsError('Use a new output directory.')
    data=json.loads(a.input.read_text(encoding='utf-8'))
    rows=data['targets'];a.output.mkdir(parents=True)
    colors={'A':'#086b66','B':'#bd7715','C':'#71509a'}
    x=lambda lon:60+(lon-61)/17*570
    y=lambda lat:640-(lat-20)/12*560
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="730" viewBox="0 0 1120 730">',
         '<rect width="1120" height="730" fill="#ffffff"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#233237} .small{font-size:12px} .key{font-size:14px}</style>',
         '<text x="40" y="30" font-size="22">Proposed survey windows: coordinate diagram</text>',
         '<text x="40" y="52" class="key">Editorial rectangles, rounded to0.1 degrees; no terrain, coastline or suitability model.</text>']
    for lon in range(62,79,2):
        svg.append(f'<path d="M{x(lon):.1f},80 V640" stroke="#dde4e3"/><text x="{x(lon)-12:.1f}" y="662" class="small">{lon}E</text>')
    for lat in range(20,33,2):
        svg.append(f'<path d="M60,{y(lat):.1f} H630" stroke="#dde4e3"/><text x="24" y="{y(lat)+4:.1f}" class="small">{lat}N</text>')
    for row in rows:
        w,s,e,n=row['bbox_lonlat'];c=colors[row['priority_class']]
        svg.append(f'<g><title>{html.escape(row["id"]+": "+row["name"]+". "+row["missingness_mechanism"])}</title><rect x="{x(w):.1f}" y="{y(n):.1f}" width="{x(e)-x(w):.1f}" height="{y(s)-y(n):.1f}" fill="{c}" fill-opacity="0.10" stroke="{c}" stroke-width="1.3"/></g>')
        # Offset text deterministically where rectangles overlap; label leader is editorial.
        shifts={'P01':(-19,-13),'P02':(0,4),'P04':(16,-4),'P07':(16,3),'P08':(-13,-5),'P09':(-10,9),'P15':(2,-3),'P20':(8,3),'P17':(0,-4),'P19':(0,5)}
        dx,dy=shifts.get(row['id'],(0,0));cx=x((w+e)/2);cy=y((s+n)/2)
        svg.append(f'<path d="M{cx:.1f},{cy:.1f} l{dx},{dy}" stroke="{c}"/><text x="{cx+dx:.1f}" y="{cy+dy:.1f}" font-size="11" font-weight="bold" stroke="white" stroke-width="3" paint-order="stroke">{row["id"]}</text>')
    for i,row in enumerate(rows):
        c=colors[row['priority_class']];yy=92+i*25
        label=row['name'] if len(row['name'])<49 else row['name'][:46]+'...'
        svg.append(f'<rect x="680" y="{yy-11}" width="12" height="12" fill="{c}"/><text x="704" y="{yy}" class="key">{row["id"]}  {html.escape(label)}</text>')
    svg.extend(['<text x="40" y="700" class="key">A: published/known-feature follow-up   B: preservation comparison   C: chronology or cultural attribution first</text>','</svg>'])
    content='\n'.join(svg)
    (a.output/'survey-windows.svg').write_text(content,encoding='utf-8')
    import fitz
    doc=fitz.open(stream=content.encode(),filetype='svg')
    doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(a.output/'survey-windows.png')
    features=[]
    for row in rows:
        w,s,e,n=row['bbox_lonlat']
        features.append({'type':'Feature','geometry':{'type':'Polygon','coordinates':[[[w,s],[e,s],[e,n],[w,n],[w,s]]]},'properties':row})
    (a.output/'survey-windows.geojson').write_text(json.dumps({'type':'FeatureCollection','name':'exploratory editorial sampling windows','features':features},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cards=[]
    for row in rows:
        fields=['origin','missingness_mechanism','target','competing_explanation','falsification_test','comparison_stratum','field_feasibility']
        body=''.join(f'<p><strong>{html.escape(k.replace("_"," ").capitalize())}:</strong> {html.escape(row[k])}</p>' for k in fields)
        cards.append(f'<details data-class="{row["priority_class"]}"><summary>{row["id"]} · {html.escape(row["name"])} · Class {row["priority_class"]}</summary>{body}<p>Sources: {html.escape(", ".join(row["source_ids"]))}. Bounding rectangle west/south/east/north: {row["bbox_lonlat"]}.</p></details>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Indus survey hypotheses</title><style>body{max-width:1120px;margin:32px auto;font:17px/1.5 system-ui;color:#233237;padding:0 20px}svg{max-width:100%;height:auto}details{border-top:1px solid #cfd8d6;padding:12px 0}summary{cursor:pointer;font-weight:600}select{font:inherit;padding:6px}strong{color:#086b66}</style><h1>Indus survey hypotheses</h1><p>Twenty-one coarse sampling windows assembled from published research and additional preservation hypotheses. These are proposed tests; this study inspected no new imagery and discovered no new sites. Rectangles overlap and cannot be summed into a survey area. Source IDs resolve in sources-v2.json / the paper bibliography.</p>'''+content+'''<p>Filter: <select id="filter"><option value="all">All classes</option><option value="A">A: archaeological feature follow-up</option><option value="B">B: preservation comparisons</option><option value="C">C: chronology first</option></select></p>'''+''.join(cards)+'''<script>document.querySelector('#filter').addEventListener('change',e=>document.querySelectorAll('details').forEach(d=>d.hidden=e.target.value!=='all'&&d.dataset.class!==e.target.value));</script></html>'''
    (a.output/'survey-hypotheses.html').write_text(page,encoding='utf-8')
    (a.output/'manifest.json').write_text(json.dumps({'input':a.input.as_posix(),'sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'method':'coordinate diagram of authored editorial rectangles; no remote sensing analysis'},indent=2)+'\n',encoding='utf-8')
    print('Created map, original SVG/PNG, GeoJSON and offline hypothesis viewer.')

if __name__=='__main__':main()
