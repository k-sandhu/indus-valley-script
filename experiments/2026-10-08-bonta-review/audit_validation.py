"""Source inspection corrections to v1's ICIT source-history proxy.

These annotations were made after the numerical run. They do not change v1.
Run from the repository root; the default output refuses replacement.
"""
from pathlib import Path
import argparse, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='validation-audit.json')
    args = ap.parse_args()
    dest = OWN / args.output
    if dest.exists(): raise FileExistsError(dest)
    examples = json.loads((RAW/'run-2026-10-08-v1/paper-examples.json').read_text(encoding='utf-8'))
    observations = [
      {'ICIT':'3084', 'CISI':'M-634', 'MH':'2069', 'ICIT_segment':216, 'MH_segments':[86,94,147],
       'classification':'confirmed_same_catalogue_object',
       'observation':'Both entries name M-634 and propose the same devatideva/sudeva-based reading.'},
      {'ICIT':'3656', 'CISI':'M-1357', 'MH':'2356', 'ICIT_segment':192, 'MH_segments':[212],
       'classification':'confirmed_same_catalogue_object',
       'observation':'The standalone MH2356 entry and ICIT3656 entry both name M-1357. Segment 122 also carries this object as an adjacent example.'},
      {'ICIT':'2816', 'CISI':'M-296', 'MH':'1387', 'ICIT_segment':165, 'MH_segments':[199],
       'classification':'confirmed_same_catalogue_object',
       'observation':'Both descriptions name M-296 and its unusual paired bull heads. The segment-165 occurrence is an iconographic observation, not a separately scored reading.'},
      {'ICIT':'2717', 'CISI':'M-1714', 'MH':'2612', 'ICIT_segment':185, 'MH_segments':[141,158],
       'classification':'conflicting_ICIT_label',
       'observation':'Segment 185 associates ICIT2717 with M-1714. MH2612 entries instead associate that object with ICIT2346. The current Lipi alias join also points to 2346. The primary plate is needed.'},
      {'ICIT':'1802', 'CISI':'H-922', 'MH':'4474', 'ICIT_segment':120, 'MH_segments':[],
       'classification':'parser_false_overlap_adjacent_example',
       'observation':'The parser adds the next, unlabelled M-1687/ICIT2485 example. That object, not H-922, creates the MH-primary intersection. H-922 still has an explicit MH4474 cross-reference in its own entry.'},
      {'ICIT':'415', 'CISI':'H-1832', 'MH':None, 'ICIT_segment':151, 'MH_segments':[],
       'classification':'parser_false_overlap_adjacent_example',
       'observation':'The parser adds the next H-642/ICIT1557 example, which appears as MH4266 elsewhere. The paper also calls MH4266 the reverse of H-1832, creating a separate catalogue conflict. No certified physical-object overlap follows.'}
    ]
    refs = [
      ('1114','H-55','4107',120),('1562','H-647','4291',110),
      ('1802','H-922','4474',120),('2135','L-219','7282',90),
      ('2260','M-1710','1101',157),('2646','M-119','2018',115),
      ('3355','M-960','2280',91),('3506','M-1139','1341',167)
    ]
    checks=[]
    for icit,cisi,mh,seg in refs:
        matched=[e for e in examples if e['primary']=='ICIT'+icit and e['segment']==seg]
        assert matched and cisi in matched[0]['cisi_candidates'] and mh in matched[0]['MH_ids']
        checks.append({'ICIT':icit,'CISI':cisi,'MH':mh,'segment':seg,
                       'classification':'explicit_same_entry_MH_reference',
                       'qualifier':'MH2280 is explicitly uncertain' if icit=='3355' else None})
    source = RAW/'papers/page-segments.json'
    result={'status':'Exploratory','scope':'Post-outcome manual source-history audit; no reconstructed held-out validation set',
            'source':str(source.relative_to(ROOT)), 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'original_parser_object_overlaps':6,'confirmed_catalogue_object_overlaps':3,
            'conflicting_label_overlaps':1,'parser_false_overlaps':2,
            'original_explicit_MH_ids':9,'same_entry_explicit_MH_ids':8,
            'same_entry_explicit_MH_ids_without_question_mark':7,
            'one_disputed_reverse_reference':'ICIT415/H-1832 versus MH4266/H-642',
            'observations':observations,'explicit_references':checks,
            'validation_membership_known':False,'attempt_denominator_known':False,
            'failure_denominator_known':False,'lecture_range':[12,15],
            'conclusion':'Some ICIT-labelled paper examples concern objects already represented by MH identifiers. The overlap and success rate of the lecture validation experiment cannot be calculated.'}
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['observations','explicit_references']},indent=2))

if __name__=='__main__':main()
