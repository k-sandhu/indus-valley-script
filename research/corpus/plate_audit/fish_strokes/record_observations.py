"""Preserve manual, approximate image observations; no recoding of corpora."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
selected=json.loads((OUT/'selection.json').read_text(encoding='utf-8'))
manifest=json.loads((OUT/'band_manifest.json').read_text(encoding='utf-8'))
# Each box is [x0,y0,x1,y1] in the unretouched 6x crop, estimated manually
# from displayed primary plate pixels. Relief edge/shadow boundaries are fuzzy.
spec={
 'M-7A':([1565,112,1695,264], [[1288,112,1540,447]], 'short',
         'Two strokes occupy the upper part of the text band, beside the whiskered fish. Mayig and Lipi differ in other segmentation, so adjacency indices are not aligned across exports.'),
 'M-35A':([775,62,859,181], [[632,61,786,373]], 'short',
          'The two strokes are clearly shorter than the adjacent fish, near its upper end.'),
 'M-42A':([736,109,814,235], [[487,62,734,466]], 'short',
          'The upper pair is much shorter than the whiskered fish. Relief shadows broaden the lower stroke ends.'),
 'M-43A':([550,91,650,199], [[375,64,578,435]], 'short with grouping ambiguity',
          'Short strokes occur beside the fish at the top of a compound array. The first pair and following top row touch or share a horizontal baseline in the impression; exact independent-sign segmentation is not resolved by height alone.'),
 'M-46A':([643,79,727,228], [[449,76,625,401],[694,111,873,409]], 'short',
          'The upper pair lies between two fish glyphs. It is shorter than either fish. The right fish lacks the left fish\'s caret-shaped top feature.'),
 'M-81A':([522,142,621,253], [[293,149,510,424]], 'short',
          'The short pair is distinct above the right side of the whiskered fish. The subsequent two visible grid glyphs are compound-coded as one Lipi W617 but two Mayig P268 units.'),
 'M-86A':([571,55,663,188], [[407,69,602,398]], 'short',
          'The pair lies in the upper portion beside the fish; it is substantially shorter than the fish.'),
 'M-89A':([532,39,621,309], [[619,51,801,288]], 'tall',
          'The pair between the preceding complex figure and the hat-bearing fish occupies essentially the full text height. The fish itself is locally smaller, so the pair is slightly taller.'),
 'M-91A':([466,82,548,301], [[358,69,469,317]], 'tall',
          'A full-height pair follows the plain fish; another separate short pair follows it at the top. Both heights are visible on the same inscription.'),
 'M-107A':([526,151,591,280], [[327,148,538,478]], 'short',
           'The upper pair beside the crossbar fish occupies well under half its full graphic height.'),
 'M-140A':([418,79,486,181], [[465,80,613,347]], 'short',
           'The two strokes between the stacked-array sign and fish occupy the upper part of the band. The primary plate supports the short-height observation used by Lipi W002; Mayig labels P145/full-height. Both raw readings are retained.'),
 'M-144A':([633,109,717,211], [[483,140,661,437]], 'short',
           'Two upper strokes beside the whiskered fish are substantially shorter than the fish.'),
 'M-147A':([442,205,520,299], [[479,233,627,503]], 'short',
           'The strokes preceding the plain fish occupy its upper band; their lower ends finish near the fish\'s shoulder rather than its feet.'),
}
rows=[]
for r in selected['rows']:
    ident=r['mayig_id']
    stroke,fish,category,note=spec[ident]
    sh=stroke[3]-stroke[1]
    fh=[b[3]-b[1] for b in fish]
    # Each selected top/bottom edge has approximately +/-10 crop pixels of
    # uncertainty; height uncertainty is conservatively +/-20 pixels.
    ratios=[{'point':round(sh/h,3),'conservative_interval':
             [round(max(0,sh-20)/(h+20),3),round((sh+20)/max(1,h-20),3)]}
            for h in fh]
    crop=next(c for c in manifest['crops'] if c['id']==ident)
    rows.append({**r,'primary_crop':crop,'observed_height_category':category,
                 'approximate_stroke_pair_box_px':stroke,
                 'approximate_adjacent_fish_boxes_px':fish,
                 'approximate_stroke_height_px':sh,
                 'approximate_fish_heights_px':fh,
                 'height_ratios':ratios,'observation':note})
out={
 'scope':'All 13 selected objects, not a random corpus-wide sample. Fourteen candidate adjacencies, because M46 has a fish on both sides of its pair.',
 'method':'Manual visual observation of unretouched official CISI1 impression photographs. The candidate frame and catalogue labels were known; this is not a blinded expert transcription. Pixel boxes are approximate relief/shadow extents, not physical metrology. Each top/bottom edge has about +/-10 pixels of uncertainty; conservative height ranges use +/-20 pixels.',
 'source':{k:v for k,v in manifest.items() if k!='crops'},
 'observed_counts':{'short':10,'short_with_grouping_ambiguity':1,'tall':2},
 'catalogue_disagreement':'M140 is P145/full-height in Mayig and W002/short-height in Lipi. The primary impression supports a short pair. This observation does not change either raw transcription.',
 'limits':['Height alone neither assigns numerical values nor identifies an Indus language, word or phonetic value.',
           'The small, selected seal sample does not establish two semantic signs rather than allographs.',
           'M43 illustrates attached or touching array components: graphic grouping may change tokenization even when stroke height is obvious.',
           'Any downstream correction must be versioned separately from the preserved observational exports.'],
 'rows':rows}
(OUT/'observations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out['observed_counts']))
for r in rows: print(r['mayig_id'],r['observed_height_category'],r['height_ratios'])
