"""Corrected attributed metadata; source strings and payloads stay traceable."""
import json
import re
from common import OWN, ROOT, PATHS, cisi, missing, site
from build import Builder, empty, cell, LOTHAL_URL, PERIOD_URL
from revision_schema import OBJECT_EXTRA, CONTEXT_EXTRA
from revision_selection import external_identity

FACTS_PATH = 'data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-observations.json'
LOTHAL_ASSERTIONS = 'experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json'
PLATES = {135:270,151:274,152:274,154:275,155:275,156:275,158:276,159:276,160:276,171:278,173:278,174:279,175:279,185:281,186:281,194:284,195:284,203:285,209:287,214:289,215:289,141:272}

def split_excavation(value):
    s = str(value).strip()
    match = re.search(r'(?i)\b(?:figure|fig\.?|plate|pl\.?)(?=\s|\d|[IVX])', s)
    # Joined forms such as H97-3319Figure 12.11 have no word boundary.
    if not match:
        match = re.search(r'(?i)(?:figure|plate)\s*\d', s)
    registration = s[:match.start()].strip(' -;,') if match else s.strip(' -;,')
    citation = s[match.start():].strip() if match else None
    lot = registration if re.match(r'(?i)^Lot\s*\d', registration) else None
    if lot or missing(registration):
        registration = None
    return registration, citation, lot

def dimensions(text):
    """Explicit units only; labelled axes are separate from unlabelled arrays."""
    unit = r'(mm\.?|cms?\.?|centimet(?:er|re)s?\.?|inches|inch|in\.)'
    factor = lambda u: 1 if u.lower().startswith('mm') else 25.4 if u.lower().startswith('in') else 10
    text = str(text).strip()
    labelled = re.findall(r'(Height|Width|Depth|Thickness|Diameter|Length)\s*:\s*(\d+(?:\.\d+)?)\s*(' + unit + r')?', text, re.I)
    if labelled:
        units = re.findall(unit, text, re.I)
        if not units:
            return []
        shared = units[-1]
        axes = {'height':'vertical','width':'horizontal','length':'horizontal','depth':'thickness','thickness':'thickness','diameter':'diameter'}
        return [(axes[label.lower()], round(float(n)*factor(u or shared), 8), 'labelled_'+label.lower()+'; explicit_unit_converted_to_mm') for label,n,u,_ in labelled]
    m = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*[xX\u00d7]\s*(\d+(?:\.\d+)?)(?:\s*[xX\u00d7]\s*(\d+(?:\.\d+)?))?\s*'+unit+r'\s*', text, re.I)
    if m:
        return [('dimension_'+str(i), round(float(m[i])*factor(m[4]), 8), 'unlabelled_axis; explicit_unit_converted_to_mm') for i in range(1,4) if m[i] is not None]
    return []

class RevisedBuilder(Builder):
    def __init__(self, *args):
        super().__init__(*args)
        self.facts = {f['id']:f for f in json.loads((ROOT/FACTS_PATH).read_text(encoding='utf-8'))}
        self.source('gadd1932','Seals of ancient Indian style found at Ur',['C. J. Gadd'],1932,'Proceedings of the British Academy 18: 191-210','https://ignca.gov.in/Asi_data/33779.pdf','1932; reprint printed13-14, PDF24-25','opened_primary_local_pdf_pages')

    def fact(self, oid, field, name, fields=None, priority=False):
        f = self.facts[name]
        if fields is not None:
            return self.add(fields,oid,field,f['value'],f['source_id'],FACTS_PATH,'id='+name,'value',f['page'],f['method'],priority=priority,confidence='derived' if 'interpretation' in f['method'] or 'count_' in f['method'] else 'source-reported')
        return self.assertion(oid,field,f['value'],f['source_id'],FACTS_PATH,'id='+name,'value',f['page'],f['method'])

    def populate(self):
        super().populate()
        self.add_lothal_source_assertions(ROOT/LOTHAL_ASSERTIONS)
        self.d['schema_version'] = '2.0'
        for s in self.d['sources']:
            s['creator_role'] = 'editor' if s['id']=='cisi1' else 'repository contributor' if s['id'] in {'ledger','census_v6','lipi','mayig'} else 'author'
        objects = {o['id']:o for o in self.d['objects']}
        contexts = {c['object_id']:c for c in self.d['contexts']}
        for o in self.d['objects']:
            o['fields'].update({f:empty() for f in OBJECT_EXTRA})
        for c in self.d['contexts']:
            c['fields'].update({f:empty() for f in CONTEXT_EXTRA})
        # Keep every source string, with the typed registration/citation derivations separate.
        excavation = [a for a in self.d['assertions'] if a['field']=='excavation_identifier' and a['source_id']=='lipi']
        for oid in objects:
            of,cf = objects[oid]['fields'],contexts[oid]['fields']
            retained = [a for a in self.d['assertions'] if a['object_id']==oid and a['field']=='excavation_identifier' and a['source_id']!='lipi']
            of['excavation_identifier'] = cell(retained[0]['value'],[a['id'] for a in retained]) if retained else empty('no_registration_after_separating_citations_and_lots')
        for a in excavation:
            oid=a['object_id'];of=objects[oid]['fields'];cf=contexts[oid]['fields'];loc=a['locator'];raw=a['value']
            a['field']='export_excavation_identifier'
            if of['export_excavation_identifier']['value'] is None:
                of['export_excavation_identifier']=cell(raw,[a['id']])
            else:
                of['export_excavation_identifier']['assertion_ids'].append(a['id'])
            for alias in self.d['identifiers']:
                if alias['assertion_id']==a['id']:
                    alias['scheme']='reported_export_identifier_string'
            registration,citation,lot=split_excavation(raw)
            for fld,val,target in [('excavation_identifier',registration,of),('bibliographic_locator',citation,of),('lot_identifier',lot,cf)]:
                if val:
                    aid=self.add(target,oid,fld,val,a['source_id'],loc['path'],loc['record'],loc['field'],loc['page_or_url'],'parsed_source_identifier_string; no_new_identity_join',confidence='derived')
                    if fld=='excavation_identifier':
                        self.identifier(oid,'excavation_registration',val,aid)
        for r in self.s['objects']:
            oid=r['object_id'];of=objects[oid]['fields'];cf=contexts[oid]['fields'];key=r['key']
            if r['family'] is None:
                for fld in ['object_type','material']:
                    for aid in of[fld]['assertion_ids']:
                        self.assertion_by_id[aid]['confidence']='derived'
                for aid in cf['region']['assertion_ids']:
                    self.assertion_by_id[aid]['confidence']='derived'
            if r['primary_selection']=='Harappa_22_tablets':
                self.add(cf,oid,'calendar_interval',{'bce_oldest':2450,'bce_youngest':2200},'harappa2010',PATHS['periods'],'label=Period 3B','bce_oldest,bce_youngest',PERIOD_URL+'#printed-xlv;Table1','full_3B_interval_for_late_3B_caption; narrower_late_interval_unresolved',priority=True,confidence='derived')
                self.add(cf,oid,'dating_basis','caption deposit assigned late 3B; full approximate 3B interval used','harappa2000',PATHS['harappa_caption'],'description_assertions[1]','dating_basis','PDF14;author13;mapped-book333','caption_period_scope_with_HARP_interval',priority=True,confidence='derived')
            if r['site']=='Harappa' and cf['period_label']['value']:
                self.add(cf,oid,'periodization_scheme','HARP; Kenoyer and Meadow 2010 Table 1','harappa2010',PATHS['periods'],'label=Period 3B' if r['primary_selection']=='Harappa_22_tablets' else 'label='+str(cf['period_label']['value']),'label',PERIOD_URL+'#printed-xlv;Table1','attributed_periodization_scheme',confidence='derived')
            if r['region'] in {'Persian Gulf','Mesopotamia','Iranian Plateau','Central Asia'}:
                canonical,country,src=external_identity(r['site'],self.i,key)
                if src:
                    self.add(cf,oid,'country',country,'census_v6',PATHS['external'],'site='+src,'identity.country.value',method='census_country_attribution')
                    if canonical!=r['site'] and key!='BM-123208':
                        self.add(cf,oid,'site',canonical,'census_v6',PATHS['external'],'site='+src,'identity.canonical_name',method='canonical_census_site_alias',priority=True)
            if key=='BM-123208':
                self.fact(oid,'site','BM-123208-findspot',cf,True)
                self.fact(oid,'findspot_site','BM-123208-findspot',cf,True)
                self.fact(oid,'excavation_identifier','BM-123208-registration',of,True)
                self.fact(oid,'stratum_phase','BM-123208-context',cf,True)
                self.add(cf,oid,'region','Mesopotamia','census_v6',PATHS['external'],'site=Ur','region',method='findspot_region_from_census',priority=True)
                self.add(cf,oid,'reported_production_place','Dilmun','census_v6',PATHS['external'],'site=Dilmun','identity.canonical_name',method='reported_production_attribution; not_excavation_location',priority=True)
            if key=='PBM-1':
                self.fact(oid,'excavation_identifier','PBM-1-registration',of,True)
                self.fact(oid,'holding','PBM-1-holder',of,True)
                for a in self.d['assertions']:
                    if a['object_id']==oid and a['field']=='excavation_identifier' and a['value']=='PMB 024':
                        a['field']='candidate_registration_variant';a['confidence']='candidate'
                        of['excavation_identifier']['assertion_ids'].remove(a['id'])
                        for alias in self.d['identifiers']:
                            if alias['assertion_id']==a['id']:alias['status']='candidate';alias['scheme']='registration_variant'
                aid=of['excavation_identifier']['assertion_ids'][-1]
                self.identifier(oid,'excavation_registration','PBM 024',aid,'CISI 1 (1987), printed375')
                for overlay in self.d['correction_overlays']:
                    if overlay['correction_id']=='B3-V6-016':overlay['applied_action']='PBM-1_registration_PBM024_and_dated_holder_KC_applied; PMB024_candidate_variant_retained'
            if key in {'L-141','L-174'}:
                self.fact(oid,'impression_count',key+'-corrigendum-count',cf,True)
                if key=='L-174':self.fact(oid,'impression_count','L-174-plate-count',cf)
                else:self.fact(oid,'plate_caption_evidence','L-141-plate-witness')
            if key in {'L-173','L-174','L-175'}:
                self.fact(oid,'design_classification',key+'-design',cf,True)
            if not any(l['object_id']==key for l in self.i['lothal']):
                for fld in ['impression_count','context_code','physical_contact_category']:
                    if cf[fld]['value'] is None:cf[fld]=empty('not_applicable_to_source_table_sealing_fields')
        # Add dimensions skipped by the old parser, without duplicating existing source axes.
        for j in self.i['joins']:
            r=next((r for r in self.s['objects'] if r['family']==j['family']),None)
            if not r:continue
            oid=r['object_id'];m=next(m for m in self.i['museum'] if m['institution']+'|'+m['accession']==j['key']);source='museum-'+m['record_id']
            if any(a['object_id']==oid and a['field']=='measurement' and a['source_id']==source for a in self.d['assertions']):continue
            for dim,value,method in dimensions(m.get('dimensions','')):
                self.measurement(oid,dim,value,source,PATHS['museum'],'record_id='+m['record_id'],'dimensions',objects[oid]['fields'],m['url'],method)
        for v in self.d['images']:
            o=objects[v['object_id']];key=o['selection_key'];match=re.fullmatch(r'L-(\d+)',key)
            if v['kind']=='catalogue_section_pointer' and match and int(match[1]) in PLATES:
                p=PLATES[int(match[1])]
                v['locator']=f'research/literature/sources/joshi_parpola_1987_cisi1.pdf#PDF{p+36};printed{p};{key}'
                v['kind']='catalogue_plate_page_pointer'
                v['inspection_status']='page_pointer_from_review; reopened_only_for_L141_L174_L175'
        # Rights-rule locators refer to a real heading, instead of internal source ids.
        for a in self.d['assertions']:
            if a['locator']['path']=='knowledge/provenance/REDISTRIBUTION.md' and a['field']=='rights_pointer':
                a['locator']['record']='heading=Current handling'
        for rights in self.d['rights']:
            if rights['source_id']=='lothal2005':
                asset=next(v for v in self.d['images'] if v['id']==rights['asset_ref'])
                aid=self.fact(asset['object_id'],'license','Lothal-Zenodo-license')
                rights['license']=cell('CC-BY-4.0',[aid]);rights['status']='explicit-license';rights['notice_locator']=LOTHAL_URL+';reviewer-verified-record-license'
        return self.d
