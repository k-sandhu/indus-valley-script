"""Frozen follow-on font acquisition test; truth withheld until completion."""
import json,random,hashlib,time,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import font_pilot as font
OUT=ROOT/'research/visual_digitization/font_fresh20'

def main():
    OUT.mkdir(exist_ok=True)
    selected=sorted(random.Random(20261015).sample([(c,r) for c in range(2) for r in range(8,35)],20))
    selection={'seed':20261015,'frame':'PDF30,columns0/1,rows8..34,column-major','selected':[{'column':c,'row':r,'printed_id':(1015 if c==0 else 1051)+r} for c,r in selected],
        'method':'Python random.Random.sample without replacement, followed by coordinate sort.','reference_release':'No manual counts/codes/details received at plan creation.'}
    (OUT/'selection_manifest.json').write_text(json.dumps(selection,indent=2))
    font.OUT=OUT;labels=ROOT/'research/chart_reference/manual_numeric_reference.json';library=font.crop_library(labels)
    bykey={t['key']:t for t in library};page=font.render(30);rows=[];start=time.monotonic()
    for c,row in selected:
        x0,x1,id0=[(150,512,1015),(680,1036,1051)][c];y=round(155+40.25*row)
        strip=page[y-19:y+20,x0:x1];components,choices=font.candidates(strip,library);tokens,cost=font.paths(components,choices,1)
        for t in tokens:
            for a in t['alternatives']:
                template=bykey[a['template_key']]
                a['manual_numeric_code_candidates']=sorted(set([template['code_manual']]+template['numeric_alternatives']))
        rows.append({'id':id0+row,'column':c,'row':row,'crop_xyxy_2x':[x0,y-19,x1,y+20],'tokens':tokens,'cost':cost,
                     'physical_line_side_boundary':'unknown'})
        Image.fromarray(strip).resize((strip.shape[1]*3,strip.shape[0]*3)).save(OUT/f'row_{id0+row}.png')
        result={'complete':len(rows)==20,'penalty_frozen':1,'selection':selection,'rows':rows,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'font_dependency_sha256':hashlib.sha256((ROOT/'src/font_pilot.py').read_bytes()).hexdigest(),
            'manual_chart_sha256':hashlib.sha256(labels.read_bytes()).hexdigest(),'runtime_seconds':time.monotonic()-start,
            'limitation':'Fine-code numeric alternatives, template uncertainty auxiliaries and physical boundaries remain unresolved. No meaning/sound inferred.'}
        (OUT/'predictions_before_gold.json').write_text(json.dumps(result,indent=2))
        print(json.dumps({'id':id0+row,'tokens':len(tokens),'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
