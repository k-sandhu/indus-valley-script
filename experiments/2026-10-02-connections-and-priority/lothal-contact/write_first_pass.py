"""Save the main reader's visual coding, before the second model audit."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
coverage=ROOT/'experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json'
groups={g['group_id']:g for g in json.loads(coverage.read_text(encoding='utf-8'))['groups']}

contacts={
 'L-124': {'crops':['L124-rear'],'texture':'Crossing short ribbed patches occur on the rear. Relief direction changes across the patch; fine fibres are unresolved.','geometry':'The cropped rear preserves an irregular textured surface. Its cross-section and any junction of contact planes are unresolved.','curved_contact':False,'angular_junction':False},
 'L-126': {'crops':['L126-rear'],'texture':'Broad roughly parallel, uneven ridges and folds cross the rear. The fine texture cannot establish the material.','geometry':'The rear is folded and irregular. One continuous cylindrical surface or an angular junction cannot be certified.','curved_contact':False,'angular_junction':False},
 'L-190': {'crops':['L190-contact','L190-profile','L190-end'],'texture':'At least two broad transverse recessed bands cross finer, roughly parallel furrows on the contact view.','geometry':'The side and end have relief and projecting margins. The photographs do not resolve the dihedral angle or distinguish the recess boundaries from all damaged edges.','curved_contact':False,'angular_junction':False},
 'L-193': {'crops':['L193-profile','L193-rear','L193-stamp'],'texture':'Some parallel marks are visible on the dark rear. The rear photograph provides weak separation of ridges and halftone grain.','geometry':'The profile has adjoining projecting regions, but the actual contact-plane junction remains unreadable. The earlier angular-surface description is retained only as a development/source-informed interpretation.','curved_contact':False,'angular_junction':False},
 'L-206': {'crops':['L206-profile','L206-rear'],'texture':'The broad inner contact is smoother than the broken outer margins; fine grain remains unresolved.','geometry':'Two views preserve a deep open concavity. The profile follows a broad curved arc between projecting margins, and the rear shows the corresponding smooth inner recess.','curved_contact':True,'angular_junction':False},
}
cuts={
 'L-161': {'selected_crop':'L161-upper-margin','crops':['L161-group','L161-cut-zone','L161-upper-margin'],'lower':2,'upper':3,'zone':'Upper margin of the left/stamped view','observation':'Two short curved depressions can be followed separately near the high margin; one neighbouring short depression remains uncertain under the dark halftone texture.','uncertainty':'Close spacing and scan grain blur one proposed separation. Other margins are dark or not exposed.'},
 'L-162': {'selected_crop':'L162-upper-margin','crops':['L162-group','L162-left','L162-upper-margin'],'lower':3,'upper':4,'zone':'Upper-left margin of the left/stamped view','observation':'Three nested arcuate depressions are separately visible; a shorter neighbouring segment at the damaged outer margin could be another cut.','uncertainty':'The marginal segment may belong to the edge or a merged cut. The reverse view does not supply a complete counting surface.'},
 'L-163': {'selected_crop':'L163-side','crops':['L163-group','L163-side','L163-rear'],'lower':3,'upper':4,'zone':'Side strip in the lower-left view','observation':'Three separated curved cuts traverse the side strip; a shorter dark mark beside them is uncertain. The rear view shows a long recessed route, recorded separately.','uncertainty':'The right end of the group has damage/texture that can merge a short cut with a chipped region. The side photograph covers one strip.'},
 'L-165': {'selected_crop':'L165-right-margin','crops':['L165-group','L165-side','L165-right-margin'],'lower':None,'upper':None,'zone':'Right margin of the first view; side checked separately','observation':'Long narrow marks occur near the right margin, but this image does not securely distinguish short manipulation cuts from a contact groove, damaged edge and image grain.','uncertainty':'Individual cut boundaries remain unreadable. This is unresolved visibility, not an observed count of zero.'},
 'L-168': {'selected_crop':'L168-cut-zone','crops':['L168-group','L168-cut-zone'],'lower':2,'upper':3,'zone':'Right margin of the upper view','observation':'Two curved depressions can be followed separately along the projecting margin; a narrow neighbouring depression is uncertain.','uncertainty':'The dark outer strip and halftone grain obscure one separation. Other surfaces are not fully exposed.'},
}
objects=[]
views=[]
for gid in ['G01','G02']:
 for obj in groups[gid]['object_ids']:
  row={'object_id':obj,'string_group':gid,'same_string_basis':'Existing frozen graphic-coverage corpus join','same_die':'unresolved in this image audit','same_die_basis':'No complete calibrated stamp comparison across objects; L193 has overlapping impressions.','pictured_in_figures_3_to_7':obj in contacts or obj in cuts,'whole_object_cut_total':None}
  if obj in contacts:
   q=contacts[obj]; row['audit_role']='new pictured object' if obj=='L-190' else 'development view reinspection'
   row['contact']={k:v for k,v in q.items() if k!='crops'}
   row['single_smooth_cylinder_geometry']='compatible' if q['curved_contact'] else 'unresolved'
   row['single_angular_board_edge_geometry']='incompatible' if q['curved_contact'] else 'unresolved'
   row['cut_interval']=None
   for crop in q['crops']:
    views.append({'object_id':obj,'crop_id':crop,'purpose':'stamp overlap check' if crop.endswith('stamp') else 'contact geometry','coding_scope':'Selected source pixels; full figure also inspected','visibility_limit':'Halftone reproduction, shadow, broken margins and incomplete surface coverage'})
  elif obj in cuts:
   q=cuts[obj]; row['audit_role']='object-linked cut-zone audit'; row['contact']=None
   row['cut_interval']={'lower':q['lower'],'upper':q['upper'],'scope':'selected visible zone only','zone':q['zone'],'selected_crop':q['selected_crop'],'morphological_status':'short arcuate/slit-like depressions compatible with manipulation' if q['lower'] is not None else 'unresolved','observation':q['observation'],'uncertainty':q['uncertainty'],'counting_surface_complete':False}
   for crop in q['crops']:
    views.append({'object_id':obj,'crop_id':crop,'purpose':'counted zone' if crop==q['selected_crop'] else 'source linkage / other view','coding_scope':'No added count from repeated views','visibility_limit':q['uncertainty']})
  else:
   row['audit_role']='target without labelled photograph in Figures3–7'; row['contact']=None; row['cut_interval']=None
   if gid=='G01': row['single_smooth_cylinder_geometry']=row['single_angular_board_edge_geometry']='unresolved'
  objects.append(row)
out={'status':'frozen main-reader visual coding before secondary model audit','created_utc':datetime.now(timezone.utc).isoformat(),
 'source':{'title':'The Lothal Sealings: Records from an Indus Civilization Town at the Eastern End of the Maritime Trade Circuits across the Arabian Sea','authors':['Dennys Frenez','Maurizio Tosi'],'year':2005,'local_pdf':'data/six-hour/lothal/frenez-tosi2005.pdf','sha256':'b0694314c9b91321dc85e90a9c66c1cf410fe46387efd0e2dffeb747fa7ddcd3','rights_status':'rights-unverified; source pixels local-only'},
 'observer_status':'Source-informed model reader; prior author interpretations and four development traces read before coding. No archaeologist/laboratory blind validation.',
 'protocol_sha256':hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest(),
 'membership_source':coverage.relative_to(ROOT).as_posix(),'membership_source_sha256':hashlib.sha256(coverage.read_bytes()).hexdigest(),
 'group_lengths':{gid:groups[gid]['length'] for gid in ['G01','G02']},'objects':objects,'views':views,
 'unlabelled_inset':{'object_id':None,'count':None,'contributes_objects':0,'reason':'No specimen identity assigned by the plate; excluded from object and count denominators.'}}
dest=HERE/'first-pass-observations.json'
assert not dest.exists(), 'Preserve the saved first pass'
dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'objects':len(objects),'views':len(views),'intervals':{o['object_id']:[o['cut_interval']['lower'],o['cut_interval']['upper']] for o in objects if o['cut_interval']}}))
