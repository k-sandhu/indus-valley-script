"""Build the tools-disabled targeted revision-review packet from authored files."""
from pathlib import Path
import hashlib
import json

BASE=Path(__file__).resolve().parent
target=BASE/'review/claude-packet-v2.txt'
if target.exists():
    raise FileExistsError(target)
sources=json.loads((BASE/'sources-v4.json').read_text(encoding='utf-8'))
regions=json.loads((BASE/'candidates-v3.json').read_text(encoding='utf-8'))
intro='''You are the author-commissioned adversarial reviewer of a revised Indus settlement working paper.
The user explicitly requested Claude Code Opus-5.5 review. Your earlier review is preserved separately.
Review the supplied revision BEFORE the final version is written. Tools are disabled. Do not claim
independent source retrieval, execution, field validation or formal peer review. Use only this packet.

Give a readiness verdict and only material unresolved issues, with stable IDs V2-F1 etc, precise
passages and concrete repairs. Limit your response to 1,800 words. Recheck attribution, chronology,
sampling/demotion, numerical logic and what the study actually did. Identify reviewer knowledge as
unverified if needed. Do not assume an inaccessible source says more than its registered reading.
Do not invent fieldwork, discovery, accuracy or a final site total. Evaluate whether the prior major
issues were addressed; avoid demanding that a literature/design paper execute unapproved fieldwork.

Main earlier revisions: repeat-survey table added with selection/period units; capture-recapture,
dependence and effort curves discussed; regions renamed and units/comparisons/demotion specified;
ordinal information/preservation/next-action assessments added; exact field allocation except one
illustrative24block pilot deferred to calibrated local design; primary omitted anchors added;
P18 extended to includeGhaziShah/Kai; coastal uplift and Khambhat cores acknowledged; cap/substrate
versus occupation ages separated; reachability and preservation denominators separated; dates
put on calendar scale with reservoir status; numeric find-yield examples and inscription metadata
removed from manuscript but preserved as supplements; review provenance identified as commissioned
AI-model reviews. The valid deduplicated union is a minimum observed count; naive capture-recapture
is not a guaranteed floor. Code flaws were repaired in a preserved v3 endpoint,64bookkeepingchecks.

Read the revised manuscript below. References resolve within it. Relative image paths are intended
for its final papers/005-settlement-survey-gaps/ location. You cannot inspect image pixels here.
'''
parts=[intro,'\n--- REVISED MANUSCRIPT ---\n',(BASE/'review/revised-v3.md').read_text(encoding='utf-8'),
       '\n--- SOURCE OBSERVATIONS AND ACTUAL ACCESS ---\n']
for row in sources['sources']:
    parts.append(json.dumps({k:row.get(k) for k in ('id','year','title','access_depth','locator','observation','limits')},ensure_ascii=False)+'\n')
parts.append('\n--- REGION DESIGN FIELDS ---\n')
for row in regions['targets']:
    parts.append(json.dumps({k:row.get(k) for k in ('id','name','bbox_lonlat','evidence_class','source_ids','sampling_unit','minimum_comparison','effort','demotion_rule','information_value','preservation_assessment','next_action','geographic_validation')},ensure_ascii=False)+'\n')
parts.extend(['\n--- BOUNDED DESIGN REVIEW ---\n',(BASE/'review/revised-design-review-v2.md').read_text(encoding='utf-8'),
              '\n--- NUMERICAL RE-SURVEY OUTPUT ---\n',(BASE/'run-v3/resurvey-descriptives.json').read_text(encoding='utf-8')])
content='\n'.join(parts)
target.write_text(content,encoding='utf-8')
print(json.dumps(dict(path=str(target),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest())))
