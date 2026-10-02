"""Post-photographic-audit sensitivity; leave fitted models and main sample intact."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from independent_annotator import bootstrap

source=ROOT/'results/independent_annotator/candidate_event_test.json'
data=json.loads(source.read_text(encoding='utf-8'))
for r in data['records']:r['p_sequence']=tuple(r['p_sequence'])
flagged={'M-62','M-81','M-140','M-181'}
records=[r for r in data['records'] if r['artifact'] not in flagged]
result={
    'design':'Exploratory post-source-audit exclusion of independently flagged photo/segmentation discrepancies; fitted training models unchanged.',
    'flagged_source_objects':sorted(flagged),
    'flag_selection':'M81 compound versus segmented grids; M140 tall/short disagreement; M181 decorated-variant crosswalk omission; M62 tall/short disagreement (not in scored test). These are selected source flags, not a random error sample.',
    'removed_scored_records':[r['record_id'] for r in data['records'] if r['artifact'] in flagged],
    'primary_result_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'all_remaining':bootstrap(records),
    'unique_P_sensitivity':bootstrap(records,unique=True),
    'all_supported_remaining':bootstrap([r for r in records if not r['has_unsupported_candidate']]),
    'limitation':'Outcomes were already known before this quality sensitivity. No independent significance or fine-glyph gold standard is claimed.'}
out=ROOT/'results/independent_annotator/photo_quality_sensitivity.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
