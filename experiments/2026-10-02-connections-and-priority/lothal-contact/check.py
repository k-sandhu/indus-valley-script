"""Verify source-linked visual records and compute the bounded summaries."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image, ImageChops
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
checks=[]
def check(name,condition):
    checks.append({'name':name,'passed':bool(condition)})
    if not condition: raise AssertionError(name)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
obs=read(HERE/'first-pass-observations.json')
check('protocol hash retained',digest(HERE/'PROTOCOL.md')==obs['protocol_sha256'])
check('PDF source hash retained',digest(ROOT/obs['source']['local_pdf'])==obs['source']['sha256'])
coverage=ROOT/obs['membership_source']
check('membership endpoint retained',digest(coverage)==obs['membership_source_sha256'])
groups={g['group_id']:g for g in read(coverage)['groups']}
records=obs['objects']
check('unique physical objects',len(records)==len({r['object_id'] for r in records})==21)
for gid in ['G01','G02']:
    check(f'{gid} exact frozen target frame',set(r['object_id'] for r in records if r['string_group']==gid)==set(groups[gid]['object_ids']))
manifests=[read(HERE/'crop-manifest.json'),read(HERE/'additional-crop-manifest.json')]
crops=[c for m in manifests for c in m['crops']]
check('unique crop IDs',len(crops)==len({c['crop_id'] for c in crops})==24)
lookup={c['crop_id']:c for c in crops}
for c in crops:
    src=ROOT/c['source_path']; out=ROOT/c['path']
    check(c['crop_id']+' source hash',digest(src)==c['source_sha256'])
    check(c['crop_id']+' crop hash',digest(out)==c['sha256'])
    im=Image.open(src); piece=Image.open(out); box=c['box_xyxy_source_pixels']
    check(c['crop_id']+' unscaled dimensions',list(piece.size)==[box[2]-box[0],box[3]-box[1]]==c['size'])
    check(c['crop_id']+' source pixel identity',ImageChops.difference(im.crop(box),piece).getbbox() is None)
    check(c['crop_id']+' local-only status',c['rights_status']=='rights-unverified; local-only')
check('unique object/view keys',len(obs['views'])==len({(v['object_id'],v['crop_id']) for v in obs['views']}))
for v in obs['views']:
    check(v['crop_id']+' correct object join',lookup[v['crop_id']]['object_id']==v['object_id'].replace('-',''))
for r in records:
    check(r['object_id']+' separate unresolved die',r['same_die']=='unresolved in this image audit')
    check(r['object_id']+' no whole object total',r['whole_object_cut_total'] is None)
    c=r['cut_interval']
    if c:
        check(r['object_id']+' selected crop belongs to object',lookup[c['selected_crop']]['object_id']==r['object_id'].replace('-',''))
        check(r['object_id']+' incomplete whole counting surface',c['counting_surface_complete'] is False)
        check(r['object_id']+' ordered interval',(c['lower'] is None and c['upper'] is None) or (0<=c['lower']<=c['upper']))
check('unlabelled inset excluded',obs['unlabelled_inset']['contributes_objects']==0 and obs['unlabelled_inset']['count'] is None)
g1=[r for r in records if r['string_group']=='G01']
g2=[r for r in records if r['string_group']=='G02']
diagnostic=[r['object_id'] for r in g1 if r['contact'] and (r['contact']['curved_contact'] or r['contact']['angular_junction'])]
board_bad=[r['object_id'] for r in g1 if r['single_angular_board_edge_geometry']=='incompatible']
cylinder_bad=[r['object_id'] for r in g1 if r['single_smooth_cylinder_geometry']=='incompatible']
intervals={r['object_id']:[r['cut_interval']['lower'],r['cut_interval']['upper']] for r in g2 if r['cut_interval'] and r['cut_interval']['lower'] is not None}
common=[max(v[0] for v in intervals.values()),min(v[1] for v in intervals.values())]
summary={
 'status':'bounded source-informed exploratory image test',
 'G01':{'target_objects':len(g1),'pictured_objects':sum(r['pictured_in_figures_3_to_7'] for r in g1),
       'new_pictured_object':'L-190','development_reinspections':['L-124','L-126','L-193','L-206'],
       'diagnostic_curvature_or_edge_objects':diagnostic,
       'board_edge_only_incompatible_objects':board_bad,'single_cylinder_geometry_incompatible_objects':cylinder_bad,
       'two_distinct_diagnostic_object_threshold_met':len(diagnostic)>=2,
       'unresolved_topology_pictured':[r['object_id'] for r in g1 if r['pictured_in_figures_3_to_7'] and r['object_id'] not in diagnostic],
       'unpictured_in_target_figures':[r['object_id'] for r in g1 if not r['pictured_in_figures_3_to_7']]},
 'G02':{'target_objects':len(g2),'pictured_objects':sum(r['pictured_in_figures_3_to_7'] for r in g2),
       'finite_visible_zone_intervals':intervals,'arithmetic_only_first_pass_interval_intersection':common if common[0]<=common[1] else [],
       'zone_comparability_established':False,'pooled_cross_object_count_variable':None,
       'pictured_cut_boundaries_unresolved':[r['object_id'] for r in g2 if r['cut_interval'] and r['cut_interval']['lower'] is None],
       'whole_object_totals_observed':0,'unlabelled_inset_objects':0,
       'unpictured_in_target_figures':[r['object_id'] for r in g2 if not r['pictured_in_figures_3_to_7']]},
 'sources_unchanged':True,'protocol_sha256':obs['protocol_sha256'],
 'first_pass_sha256':digest(HERE/'first-pass-observations.json'),
 'checker_sha256':digest(Path(__file__)),
 'scope':'Visible-zone intervals are observations under image limits; no quantity value, function, whole-object tally or physical die identification is assigned.'}
secondary=HERE/'secondary-view-audit.json'
if secondary.exists():
    audit=read(secondary)
    check('secondary same finite cut-zone objects',set(audit['cut_intervals'])==set(intervals))
    envelopes={obj:[min(intervals[obj][0],value[0]),max(intervals[obj][1],value[1])] for obj,value in audit['cut_intervals'].items()}
    envelope_common=[max(v[0] for v in envelopes.values()),min(v[1] for v in envelopes.values())]
    for obj, value in audit['cut_intervals'].items():
        check(obj+' secondary ordered interval',0<=value[0]<=value[1])
        check(obj+' readers agree on clear lower count',value[0]==intervals[obj][0])
    summary['secondary_model_audit']={'sha256':digest(secondary),'status':audit['status'],'contact_concordance':audit['contact_concordance'],'cut_intervals':audit['cut_intervals'],'validation_scope':audit['validation_scope']}
    summary['G02']['reader_envelope_visible_zone_intervals']=envelopes
    summary['G02']['arithmetic_only_reader_envelope_interval_intersection']=envelope_common if envelope_common[0]<=envelope_common[1] else []
    summary['G02']['reader_envelope_scope']='Range covering both readers stated candidate counts; not a statistical confidence interval or complete-object total.'
    summary['G02']['intersection_scope']='Arithmetic intersection only. Selected upper/side margins have different incomplete coverage. No pooled count variable is defined; even under added comparability, intervals leave equal counts possible.'
    observation_record={'status':'Source-informed observational record with preserved first pass and secondary audit',
        'first_pass_path':'first-pass-observations.json','first_pass_sha256':digest(HERE/'first-pass-observations.json'),
        'secondary_path':'secondary-view-audit.json','secondary_sha256':digest(secondary),
        'protocol_sha256':obs['protocol_sha256'],'objects':records,'views':obs['views'],
        'reader_envelope_visible_zone_intervals':envelopes,'zone_comparability_established':False,'pooled_cross_object_count_variable':None,
        'unlabelled_inset':obs['unlabelled_inset'],
        'same_die_status':'Unresolved for all 21 target objects in this audit'}
    (HERE/'observations.json').write_text(json.dumps(observation_record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
report=HERE/'REPORT.md'
if report.exists():
    text=report.read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if not link.startswith(('http:','https:')):
            check('report local link '+link,(HERE/link).resolve().exists())
check('bounded one-object contact result',diagnostic==['L-206'] and board_bad==['L-206'] and not cylinder_bad)
check('four visible cut zones',len(intervals)==4)
check('first-pass intervals share 3',common==[3,3])
(HERE/'results.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(HERE/'verification.json').write_text(json.dumps({'all_passed':True,'checks':checks,'check_count':len(checks)},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'all_passed':True,'checks':len(checks),'diagnostic_G01_objects':diagnostic,'visible_zone_intervals':intervals,'whole_object_totals':0}))
