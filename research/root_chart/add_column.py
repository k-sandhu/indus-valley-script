import argparse,json
from pathlib import Path
p=Path(__file__).with_name('manual_columns.json')
ap=argparse.ArgumentParser(); ap.add_argument('column',type=int); ap.add_argument('ranks'); ap.add_argument('codes'); ap.add_argument('--dashed',default=''); args=ap.parse_args()
data=json.loads(p.read_text(encoding='utf-8'))
ranks=[int(x) for x in args.ranks.split(',')]
codes=[None if x=='NA' else int(x) for x in args.codes.split(',')]
assert len(ranks)==len(codes)==(22 if args.column==9 else 35)
data['columns'][str(args.column)]={'ranks':ranks,'codes':codes,'dashed_annotation_rows':[int(x) for x in args.dashed.split(',') if x]}
p.write_text(json.dumps(data,indent=2),encoding='utf-8')
