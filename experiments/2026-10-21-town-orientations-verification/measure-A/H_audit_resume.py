"""Resume in fresh audit outputs after unrelated infrastructure hashes changed."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
source=Path(__file__).with_name('H_audit.py').read_text(encoding='utf-8')
source=source.replace("AUDIT=OWN/'audit-H-v1'","AUDIT=OWN/'audit-H-v2'")
start=source.index('# Preserve the first endpoint')
end=source.index('checks=[];final_paths={};full_selection=[]')
source=source[:start]+source[end:]
source=source.replace('checks=[];final_paths={};full_selection=[]','checks=[];final_paths={};full_selection=[];infrastructure_changes=[]')
source=source.replace("assert actual==prior, f'line refinement mismatch: {slug} {admission[\"source_id\"]}'", "assert {k:v for k,v in actual.items() if k!='provenance'}=={k:v for k,v in prior.items() if k!='provenance'}, f'line refinement mismatch: {slug} {admission[\"source_id\"]}'\n  changed=[k for k in set(actual['provenance'])|set(prior['provenance']) if actual['provenance'].get(k)!=prior['provenance'].get(k)]\n  assert not set(changed)&{'common.py','measure_lines.py','render_plan.py','systems.py','igrf.py'}, 'core measurement code changed'\n  if changed:infrastructure_changes.append(dict(town=slug,source_id=admission['source_id'],changed_metadata_keys=sorted(changed)))")
source=source.replace('tool_mutations=False,git_mutations=False','owned_tool_mutations=False,git_mutations=False,infrastructure_provenance_changes=infrastructure_changes')
exec(compile(source,str(Path(__file__).with_name('H_audit.py')),'exec'))
