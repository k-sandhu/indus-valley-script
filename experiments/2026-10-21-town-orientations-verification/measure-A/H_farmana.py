import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, subprocess
base=Path(sys.argv[1]); raw=Path(sys.argv[2]); tool=Path(sys.argv[3])
def wall(id,part,system,pts,ident):
 return dict(id=id,part=part,system=system,kind='house wall',identification=ident,endpoints_px=pts,mode='fit',feature='edge',corridor_half_width_px=4)
loc='Shinde, Osada, Uesugi and Kumar 2008, A Report on Excavations at Farmana 2007-08, '
specs=[
 (1,[[830,1453],[830,1427]],[[659,1510],[855,1510]],2,[
 ('3X-west','Trench 3X','3X-walls',[[405,1045],[405,1195]],'PDF p.28, printed p.16, Fig.11: eastern face of western mud-brick wall above cross wall.'),
 ('3X-cross','Trench 3X','3X-walls',[[411,1207],[493,1207]],'PDF p.28, printed p.16, Fig.11: northern face of horizontal mud-brick cross wall, ending at its step.'),
 ('3X-east','Trench 3X','3X-walls',[[606,1119],[607,1195]],'PDF p.28, printed p.16, Fig.11: east face of northern right-hand mud-brick wall segment.'),
 ('3X-south','Trench 3X','3X-walls',[[391,1459],[480,1459]],'PDF p.28, printed p.16, Fig.11: southern face of bottom horizontal mud-brick wall, before irregular joint.')]),
 (2,[[798,1070],[798,1043]],[[625,1135],[821,1135]],2,[
 ('3A3-lower-north','Trench 3A3 lower layer','3A3-lower',[[546,383],[811,284]],'PDF p.31, printed p.19, Fig.14, lower-layer panel: straight north face of mud-brick wall; no trench edge.'),
 ('3A3-upper-north','Trench 3A3 upper layer','3A3-upper',[[498,649],[812,526]],'PDF p.31, printed p.19, Fig.14, upper-layer panel: long north face of mud-brick wall, excluding pit and buried jar.'),
 ('3A3-upper-south','Trench 3A3 upper layer','3A3-upper',[[704,630],[812,592]],'PDF p.31, printed p.19, Fig.14, upper-layer panel: straight eastern stretch of south face of the same wall. Opposite faces share the wall and are correlated.')]),
 (3,[[815,1101],[815,1075]],[[642,1542],[838,1542]],2,[
 ('st1-north','Structure complex 1','st1-walls',[[449,1141],[615,1070]],'PDF p.34, printed p.22, Fig.17: inner northern wall face of Structure no.1, excluding post-hole.'),
 ('st1-east','Structure complex 1','st1-walls',[[675,1143],[792,1387]],'PDF p.34, printed p.22, Fig.17: long inner eastern wall face, stopping at inner corner.'),
 ('st1-west','Structure complex 1','st1-walls',[[441,1210],[535,1415]],'PDF p.34, printed p.22, Fig.17: inner western wall face, below gap in surviving northern segment.'),
 ('st1-south','Structure complex 1','st1-walls',[[638,1461],[787,1392]],'PDF p.34, printed p.22, Fig.17: inner southern wall face, excluding southern break and corner damage.')]),
 (4,[[1011,1103],[1011,1055]],[[685,1073],[937,1073]],10,[
 ('c3-court-west','Structure complex 3','complex3',[[433,437],[510,611]],'PDF p.37, printed p.25, Fig.19: eastern face of west courtyard wall of 3G, below antechamber; stop before kink.'),
 ('c3-court-east','Structure complex 3','complex3',[[607,437],[645,524]],'PDF p.37, printed p.25, Fig.19: western face of eastern 3G courtyard wall beside 3I, before southern junction.'),
 ('c3-north','Structure complex 3','complex3',[[455,326],[570,284]],'PDF p.37, printed p.25, Fig.19: southern face of wall bounding 3A, between house-wall junctions.'),
 ('c3-j-north','Structure complex 3','complex3',[[281,475],[402,432]],'PDF p.37, printed p.25, Fig.19: south face of northern wall of central courtyard 3J.'),
 ('c3-t-south','Structure complex 3','complex3',[[311,889],[390,861]],'PDF p.37, printed p.25, Fig.19: southern house-wall face by 3T, bordering Lane no.1.'),
 ('c3-lane','Structure complex 3','complex3',[[336,914],[489,856]],'PDF p.37, printed p.25, Fig.19: northern wall face bordering Lane no.1, below 3T and 3S; exclude lane label.'),
 ('c2-north','Structure complex 2','complex2',[[846,300],[926,270]],'PDF p.37, printed p.25, Fig.19: inside northern wall face of 2A.'),
 ('c2-west','Structure complex 2','complex2',[[856,328],[886,400]],'PDF p.37, printed p.25, Fig.19: inside western wall face beside 2A and 2B.'),
 ('c2-south','Structure complex 2','complex2',[[916,432],[995,402]],'PDF p.37, printed p.25, Fig.19: southern outside wall face of 2B, above open gap.'),
 ('c2-east','Structure complex 2','complex2',[[973,307],[992,359]],'PDF p.37, printed p.25, Fig.19: western inside face of long eastern wall beside PL.2.'),
 ('c4-north','Structure complex 4','complex4',[[275,972],[681,817]],'PDF p.37, printed p.25, Fig.19: long northern exterior face of complex 4 beside Lane no.1; continuation ends at bend by 4B.'),
 ('c4-east','Structure complex 4','complex4',[[705,859],[730,917]],'PDF p.37, printed p.25, Fig.19: eastern wall face of 4B above junction at 4A.'),
 ('c4-f-north','Structure complex 4','complex4',[[287,991],[359,965]],'PDF p.37, printed p.25, Fig.19: inner northern wall face of room 4F; distinct from long exterior face.')])]
for n,arrow,scale,length,lines in specs:
 picks=dict(source_id=f'farmana-0{n}',north=dict(**{'class':'unspecified'},evidence=f"Fig.{[11,14,17,19][n-1]}: exact label 'N' above a triangular north pointer in a circle (Figs.11,14,17) or four-point compass (Fig.19). No reference qualification is printed.",survey_year=2008,survey_year_evidence="Report title 'A Report on Excavations at Farmana 2007-08'; 2008 is the end of the stated excavation season, not an independently documented arrow survey date.",survey_year_range=[2007,2008],line=dict(endpoints_px=arrow,mode='manual',pick_sigma_px=1,feature='trough',corridor_half_width_px=3)),scale=dict(endpoints_px=scale,length_m=length),lines=[wall(a,b,c,d,loc+e) for a,b,c,d,e in lines])
 pp=base/f'plan-0{n}-picks-v1.json';rr=base/f'plan-0{n}-lines-v1.json'
 with pp.open('x') as f:json.dump(picks,f,indent=2)
 result=subprocess.run([sys.executable,'-I',str(tool/'measure_lines.py'),str(pp),str(raw/f'plan-0{n}-v1.png.json'),str(rr)],capture_output=True,text=True)
 print(n,result.returncode,result.stdout,result.stderr[-600:])
 if result.returncode:continue
 subprocess.run([sys.executable,'-I',str(base.parents[1]/'H_work.py'),'overlay',str(raw/f'plan-0{n}-v1.png'),str(rr),str(raw/f'plan-0{n}-check-v1.png')],check=True)
