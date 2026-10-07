"""Occurrence-qualified concordances and payload-free ledger projection."""
import argparse
import collections
import copy
import hashlib
import json
import re
from pathlib import Path
import jsonschema
from common import OWN, RAW, ROOT, cisi, fresh, write
from import_helsinki1979 import EDITION, LICENSE, read_rows
from build import empty, cell
from schema import SURFACE_FIELDS, TRANSCRIPTION_FIELDS

def interface_schema():
    s=json.loads((OWN/'interface-schema.json').read_text(encoding='utf-8'))
    number={'anyOf':[{'type':'string','pattern':r'^\d+[A-Za-z]*$'},{'type':'integer','minimum':1}]}
    for name in ['digitized_row','crosswalk_row']:
        s['$defs'][name]['properties']['text_number']=number
        if 'segment_id' not in s['$defs'][name]['required']:s['$defs'][name]['required'].append('segment_id')
    return s

def canonical_target(scheme,value):
    if scheme in {'CISI','CISI1','reported_catalogue_reference'}:
        return 'CISI',cisi(value)
    return scheme,str(value)

def expand_crosswalk(rows,crosswalk):
    """Expand M text-level rows; alignment evidence must cover each occurrence."""
    if isinstance(crosswalk,dict):crosswalk=crosswalk['rows']
    converted=[]
    for c in crosswalk:
        base=copy.deepcopy(c)
        if 'source_edition' in c:
            surface=c.get('surface_relation',{})
            if not isinstance(surface,dict):surface={'relation':surface}
            base={'edition_id':c['source_edition'],'text_number':c['text_number'],
                  'target_identifier':{'scheme':c.get('target_scheme'),'value':c.get('target_identifier')},
                  'concordance_source':c.get('concordance_source'),'concordance_page':str(c.get('concordance_page') or ''),
                  'source_access':c.get('source_access','unverified_access'),
                  'status':'confirmed' if c.get('review_status')=='confirmed' else c.get('review_status'),
                  'review_status':'reviewed_object_identity' if c.get('review_status')=='confirmed' else c.get('review_status'),
                  'rights_status':c.get('rights_status'),**surface}
            for key in ['segment_id','occurrence_surfaces','surface_scope']:
                if key in c:base[key]=c[key]
        if base.get('segment_id'):
            converted.append(base);continue
        for row in rows:
            if row.get('edition_id')==base.get('edition_id') and str(row.get('text_number'))==str(base.get('text_number')):
                occurrence=copy.deepcopy(base);segment=row.get('segment_id');occurrence['segment_id']=segment
                mapping=base.get('occurrence_surfaces',{}).get(segment)
                if mapping:occurrence.update(mapping)
                elif base.get('surface_scope')!='all_verified_occurrences':
                    occurrence['surface_id']=None;occurrence['surface_review_status']='unresolved_occurrence_alignment'
                converted.append(occurrence)
    return converted

def to_package_m(crosswalk):
    """Round-trip explicit occurrence rows, keeping review evidence and rights."""
    rows=[]
    for c in crosswalk:
        surface={k:c[k] for k in ['surface_id','surface_review_status','relation','create_surface','source_surface_label'] if k in c}
        rows.append({'source_edition':c.get('edition_id'),'text_number':c.get('text_number'),'segment_id':c.get('segment_id'),
                     'target_scheme':c.get('target_identifier',{}).get('scheme'),'target_identifier':c.get('target_identifier',{}).get('value'),
                     'concordance_source':c.get('concordance_source'),'concordance_page':c.get('concordance_page'),
                     'source_access':c.get('source_access'),'surface_relation':surface,'rights_status':c.get('rights_status','unverified'),
                     'review_status':'confirmed' if c.get('review_status')=='reviewed_object_identity' and c.get('status')=='confirmed' else 'candidate'})
    return {'rows':rows}

def import_rows(rows,crosswalk,ledger,allow_synthetic=False):
    schema=interface_schema();validator=jsonschema.Draft202012Validator({'$ref':'#/$defs/digitized_row','$defs':schema['$defs']})
    crosswalk=expand_crosswalk(rows,crosswalk);lookup=collections.defaultdict(list)
    for c in crosswalk:lookup[(c.get('edition_id'),str(c.get('text_number')),c.get('segment_id'))].append(c)
    identifiers=collections.defaultdict(set)
    for i in ledger['identifiers']:
        if i['status']=='confirmed':identifiers[canonical_target(i['scheme'],i['value'])].add(i['object_id'])
    surfaces={s['id']:s for s in ledger['surfaces']};accepted=[];quarantined=[];seen=set()
    for row in rows:
        reasons=[e.message for e in validator.iter_errors(row)]
        key=(row.get('edition_id'),str(row.get('text_number')),row.get('segment_id'))
        if key in seen:reasons.append('duplicate source occurrence')
        seen.add(key)
        if row.get('synthetic') and not allow_synthetic:reasons.append('synthetic fixture forbidden in archaeological import')
        links=lookup.get(key,[]);link=links[0] if len(links)==1 else {}
        if len(links)!=1:reasons.append('no unique occurrence-qualified concordance')
        if links:
            if link.get('status')!='confirmed' or link.get('review_status')!='reviewed_object_identity':reasons.append('object identity unconfirmed or unreviewed')
            if link.get('source_access')!='opened_primary_concordance' or not link.get('concordance_source') or not link.get('concordance_page'):reasons.append('primary concordance not opened and located')
            if link.get('relation')!='same_physical_object':reasons.append('concordance does not establish physical carrier')
        target=link.get('target_identifier',{});hits=identifiers.get(canonical_target(target.get('scheme'),target.get('value')),set())
        oid=next(iter(hits)) if len(hits)==1 else None
        if len(hits)!=1:reasons.append('target does not resolve one carrier')
        sid=link.get('surface_id');definition=None
        if link.get('create_surface'):
            if not link.get('source_surface_label'):reasons.append('new surface requires reviewed source face/line label')
            if sid in surfaces:reasons.append('new source surface collides with existing surface')
            if not sid and oid:sid='S-H79-'+hashlib.sha256((oid+'|'+str(key)).encode()).hexdigest()[:16]
            definition={'id':sid,'object_id':oid,'source_label':link.get('source_surface_label'),'segment_id':row.get('segment_id')}
        elif not sid or sid not in surfaces or surfaces[sid]['object_id']!=oid:reasons.append('source surface unresolved or owned by another carrier')
        if link.get('surface_review_status')!='reviewed_source_surface_alignment':reasons.append('occurrence surface alignment unreviewed')
        if reasons:
            quarantined.append({'source_row':row,'crosswalk_candidates':links,'reasons':sorted(set(reasons))});continue
        accepted.append({'transcription_id':'H79-'+hashlib.sha256(str(key).encode()).hexdigest()[:18],'object_id':oid,'surface_id':sid,'surface_definition':definition,
                         'source_edition':EDITION,'source_text_number':str(row['text_number']),'segment_id':row['segment_id'],'source_page':row['source_page'],
                         'inventory':row['inventory'],'inventory_version':row['inventory_version'],'digitization_version':row['digitization_version'],
                         'glyph_tokens':row['glyph_tokens'],'auxiliary_markers':row['auxiliary_markers'],'order':row['order'],'boundary_status':row['boundary_status'],
                         'rights':row['rights'],'review_status':row['review_status'],'concordance':link,'status':'Synthetic' if row.get('synthetic') else 'Exploratory'})
    return accepted,quarantined

def project_layer(ledger,accepted,local_layer_path,allow_synthetic=False):
    """Add metadata, rights and any reviewed new surfaces; retain payloads locally."""
    p=Path(local_layer_path).resolve()
    if not p.is_relative_to(RAW) or not p.is_file():raise ValueError('Layer witness must exist under local raw')
    layer=copy.deepcopy(ledger);source='helsinki1979'
    def assertion(row,field,value):
        aid='A-H79-'+hashlib.sha256((row['transcription_id']+'|'+field).encode()).hexdigest()[:18]
        layer['assertions'].append({'id':aid,'object_id':row['object_id'],'field':field,'value':value,'source_id':source,
            'locator':{'path':str(p.relative_to(ROOT)).replace('\\','/'),'record':'transcription_id='+row['transcription_id'],'field':field,'page_or_url':'PDF'+str(row['source_page']),'page_missing_reason':None},
            'method':'concordance_gated_1979_layer_projection','confidence':'derived','review_status':'not-expert-reviewed'})
        return cell(value,[aid])
    for row in accepted:
        if row['status']=='Synthetic' and not allow_synthetic:raise ValueError('Synthetic layer prohibited')
        if row['object_id'] not in {o['id'] for o in layer['objects']}:raise ValueError('Layer carrier absent')
        if row['rights'].get('license')!=LICENSE or row['concordance'].get('surface_review_status')!='reviewed_source_surface_alignment':raise ValueError('Layer review/rights invalid')
        definition=row.get('surface_definition')
        if definition:
            if any(s['id']==row['surface_id'] for s in layer['surfaces']):raise ValueError('Surface collision')
            fs={f:empty('source_field_not_recorded') for f in SURFACE_FIELDS};fs['label']=assertion(row,'label',definition['source_label']);fs['alignment']=assertion(row,'alignment','reviewed source occurrence alignment')
            layer['surfaces'].append({'id':row['surface_id'],'object_id':row['object_id'],'fields':fs})
        if not any(s['id']==row['surface_id'] and s['object_id']==row['object_id'] for s in layer['surfaces']):raise ValueError('Layer surface invalid')
        tid=row['transcription_id'];rid='R-'+tid
        if any(t['id']==tid for t in layer['transcriptions']):raise ValueError('Duplicate imported occurrence')
        fs={f:empty('source_field_not_recorded') for f in TRANSCRIPTION_FIELDS}
        for f,val in [('length',len(row['glyph_tokens'])),('order',row['order']),('boundaries',row['boundary_status']),('inventory_version',row['inventory_version'])]:fs[f]=assertion(row,f,val)
        layer['rights'].append({'id':rid,'source_id':source,'asset_ref':tid,'status':'explicit-license','license':assertion(row,'license',LICENSE),'scope':'1979 derived transcription; attribution and modifications retained locally','disposition':'local-only','notice_locator':row['rights']['source_url']})
        layer['transcriptions'].append({'id':tid,'object_id':row['object_id'],'surface_id':row['surface_id'],'source_id':source,'inventory':row['inventory'],'source_version':row['digitization_version'],'rights_id':rid,'payload_disposition':'local-only','fields':fs})
    return layer

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rows',required=True);ap.add_argument('--crosswalk',required=True);ap.add_argument('--ledger',required=True);ap.add_argument('--raw-dir',required=True);ap.add_argument('--project',action='store_true');a=ap.parse_args()
    rows=read_rows(a.rows);cross=json.loads(Path(a.crosswalk).read_text(encoding='utf-8'));ledger=json.loads(Path(a.ledger).read_text(encoding='utf-8'))
    accepted,quarantine=import_rows(rows,cross,ledger);out=fresh(a.raw_dir,RAW);path=out/'accepted-transcriptions.json';write(path,accepted);write(out/'quarantine.json',quarantine)
    if a.project:write(out/'ledger-projection.json',project_layer(ledger,accepted,path))
    print(json.dumps({'status':'Exploratory','accepted':len(accepted),'quarantined':len(quarantine)}))

if __name__=='__main__':main()
