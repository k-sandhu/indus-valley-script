"""Preserve v1; add explicit asset rights, missing-field reasons and source controls."""
from collections import Counter,defaultdict
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fish_study',HERE/'study.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)


def main():
    dest=HERE/'register-v2';dest.mkdir(exist_ok=False)
    local=s.RAW/'register-v2';local.mkdir(exist_ok=False)
    objects=s.read_rows(s.RAW/'register-v1/objects.jsonl')
    assertions=s.read_rows(s.RAW/'register-v1/assertions.jsonl')
    for a in assertions:
        # Brackets retain a transcription candidate; they are not an archaeological conflict.
        if a.get('uncertain'):
            a['value_status']='catalogued'
            a['reading_status']='uncertain digit or candidate retained from the source-table transcription'
        if not s.usable(a['value']):
            a['value_status']='unknown';a['unknown_reason']='not-reported-or-placeholder'
    metadata_coverage=Counter();image_count=0
    for r in objects:
        aliases=[]
        for c in r['cisi']:aliases.append({'namespace':'CISI','value':c,'relation':'same-provisional-object'})
        for b in r['basic_data_records']:
            if b['parsed']['fc_number']:
                aliases.append({'namespace':'Helsinki concordance','value':b['parsed']['fc_number'],
                                'relation':'catalogue-concordance','uncertain':'[' in b['col2_fc'],
                                'source':b['volume'],'printed_page':b['printed_page']})
        for t in r['excavation_table_rows']:
            aliases.append({'namespace':t['source'],'value':t['catalogue_no'],'relation':'source-table-join',
                            'join_status':t['disposition'],'field_number':t['field_no'],'printed_page':t['printed_page']})
        r['identifier_assertions']=aliases
        for im in r['images']:
            im['asset_rights']={'status':'rights-unverified','licence':None,
                                'source':'CISI photograph reproduced in Lipi; source-specific terms retained'}
            im['local_path']='data/lipi/public/seal_images/'+im['file']
            im['view_polarity']=im['kind']
            im['printed_page']=(int(im['cisi_pdf_page'])-(36 if im['cisi_volume']=='1' else 35)
                                if im['cisi_pdf_page'].isdigit() and im['cisi_volume'] in ('1','2') else None)
            image_count+=1
        fields={}
        for field,key in [('material','material'),('findspot_area','area-section'),('house_or_block','block-house'),
                          ('room_or_grid','room-grid'),('depth','depth'),('period','period'),('phase','phase'),
                          ('width_mm','horizontal(mm)'),('height_mm','vertical(mm)'),('thickness_mm','thickness(mm)')]:
            vals=sorted({str(m.get(key,'')) for m in r['metadata_by_face'].values() if s.usable(m.get(key))})
            fields[field]={'values':vals,'value_status':'catalogued' if vals else 'unknown',
                           'source':'pinned observational Lipi metadata; source-table assertions retained separately'}
            if not vals:fields[field]['unknown_reason']='not-reported-in-held-export'
            if vals:metadata_coverage[field]+=1
        for field in ['mass_g','calendar_date','deposit_associations','measured_quantity','independently_named_owner']:
            fields[field]={'values':[],'value_status':'unknown','unknown_reason':'no-joined-primary-observation'}
        r['field_status']=fields
        r['record_version']='fish-context-register-v2'
    s.dump_jsonl(local/'objects.jsonl',objects)
    s.dump_jsonl(local/'assertions.jsonl',assertions)

    # Source comparison controls are retained alongside, outside the fish-bearing denominator.
    all_rows=[]
    for half,folder in [('discovery','discovery-v2'),('confirmation','confirmation-v1')]:
        all_rows+=s.read_rows(s.RAW/folder/(half+'-faces.jsonl'))
    controls=[]
    for c in ['H-902','H-912','M-478']:
        rs=[r for r in all_rows if c in s.base_cisi(r['source_cisi'])]
        controls.append({'cisi':c,'fish_register_member':any(c in r['cisi'] for r in objects),'faces':rs})
    s.dump_jsonl(local/'source-controls.jsonl',controls)
    result={'objects':len(objects),'source_assertions':len(assertions),'image_links_with_rights_and_polarity':image_count,
            'metadata_coverage':dict(metadata_coverage),
            'source_controls':[{'cisi':c['cisi'],'faces':len(c['faces']),'fish_register_member':c['fish_register_member']} for c in controls],
            'change_from_v1':'Added explicit aliases, per-image rights/polarity/page fields and missing reasons; bracketed source readings remain catalogued and uncertain rather than called conflicting.',
            'new_physical_objects':0,'phonetic_or_semantic_values_added':0,
            'hashes':{str(p.relative_to(s.ROOT)):s.sha256(p) for p in [Path(__file__),local/'objects.jsonl',local/'assertions.jsonl',local/'source-controls.jsonl']}}
    s.write_json(dest/'coverage.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
