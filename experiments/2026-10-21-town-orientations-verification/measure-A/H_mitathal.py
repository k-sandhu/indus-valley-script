import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess
own=Path(sys.argv[1]);raw=Path(sys.argv[2]);tool=Path(sys.argv[3]);base=own/'picks/mitathal'
specs=[(1,'plan-01-east-v2.png','unspecified',[[1273,277],[1268,172]],[[102,811],[241,810]],1,[
 ('39-west','IIA-3',[[278,396],[323,695]],'west envelope of the brick face of Structure 39 (II A,3)'),
 ('39-east','IIA-3',[[308,399],[352,770]],'east envelope of Structure 39 (II A,3); same wall as 39-west, with correlated errors'),
 ('40-west','IIA-3',[[944,239],[985,410]],'west face of thin brick wall 40 (II A,3), excluding the broken lower continuation'),
 ('48-west','IIA-4',[[710,156],[722,282]],'west face of Structure 48 (II A,4), excluding upper corner and lower break')]),
 (2,'plan-02-100-v2.png','magnetic',[[563,678],[517,578]],[[698,833],[966,830]],2,[
 ('11-west','IIA-3-central',[[694,445],[739,696]],'western brick-face envelope of Structure 11 (II A,3), before lower break'),
 ('11-east','IIA-3-central',[[744,439],[790,693]],'eastern brick-face envelope of Structure 11 (II A,3); opposite face of the same wall, with correlated errors'),
 ('16-north','IIA-3-central',[[835,236],[1085,210]],'northern outer face of Structure 16 (II A,3), excluding adjacent trench dash'),
 ('8-west','IIA-3-central',[[91,630],[117,771]],'western brick-face envelope of Structure 8 (II A,3), before the bottom turn'),
 ('19-east','IIA-3-east',[[1286,330],[1301,684]],'eastern face of Structure 19 (II A,3), excluding upper and lower transverse junctions'),
 ('19-west','IIA-3-east',[[1192,343],[1186,689]],'western face of Structure 19 (II A,3); separate brick-run face, drawn differently from its eastern side'),
 ('3-north','IIB-1',[[191,175],[395,167]],'northern face of Structure 3 (II B,1), Late Harappan, before the wall 4 junction'),
 ('4-west','IIB-1',[[396,178],[392,495]],'western face of Structure 4 (II B,1), Late Harappan; gaps between surviving bricks are retained'),
 ('3-south','IIB-1',[[237,277],[375,279]],'southern surviving face of Structure 3 (II B,1), Late Harappan')])]
for n,png,north,arrow,scale,length,rows in specs:
 evidence=("Fig.3, far right: unlabelled open north-point symbol. No true, magnetic or grid words accompany it; treated as an unspecified arrow." if n==1 else "Fig.4, left of centre: exact label 'N' above a long needle-like north point with a transverse bar and asymmetric needle head. Classified magnetic under the needle-symbol rule; no true/grid qualification is printed.")
 p=dict(source_id=f'mitathal-0{n}',location=[28.89194444,76.16972222],igrf_coefficients='data/raw/2026-10-21-town-orientations-verification/infra/igrf/igrf14coeffs.txt',north=dict(**{'class':north},evidence=evidence,survey_year=1968,survey_year_evidence="Exact internal figure title 'MITATHAL 1968: PLAN MTL 1' or 'MITATHAL 1968: PLAN MTL 2'.",line=dict(endpoints_px=arrow,mode='manual',pick_sigma_px=2,feature='trough',corridor_half_width_px=4)),scale=dict(endpoints_px=scale,length_m=length),manual_reason='Separate eroded brick outlines and gaps do not make a continuous brightness edge. We pick the outer envelope of a named wall face, with two-pixel endpoint sigma on this 100 dpi render. These are drawn face directions, with paper and survey errors outside the conditional sigma.',lines=[])
 for id,system,pts,ident in rows:
  p['lines'].append(dict(id=id,part='MTL-'+str(n)+' '+system,system=system,kind='house wall',identification=f'Suraj Bhan 1975, Excavation at Mitathal (1968) and Other Explorations in the Sutlej-Yamuna Divide, PDF p.{32 if n==1 else 34}, unnumbered foldout following printed p.12, Fig.{3 if n==1 else 4}: '+ident,endpoints_px=pts,mode='manual',pick_sigma_px=2,feature='edge',corridor_half_width_px=4))
 path=base/f'plan-0{n}-picks-v1.json';result=base/f'plan-0{n}-lines-v1.json'
 with path.open('x') as f:json.dump(p,f,indent=2)
 subprocess.run([sys.executable,'-I',str(tool/'measure_lines.py'),str(path),str(raw/'mitathal'/png)+'.json',str(result)],check=True)
 subprocess.run([sys.executable,'-I',str(own/'H_work.py'),'overlay',str(raw/'mitathal'/png),str(result),str(raw/'mitathal'/f'plan-0{n}-check-v1.png')],check=True)
