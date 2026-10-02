"""Write bounded authored source locators and an unsent observation packet."""
from pathlib import Path
import datetime
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RAW=ROOT/'data/raw/2026-10-02-source-recovery/physical-views'


def record(path):
    p=ROOT/path
    return {'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}


def save(path,value):
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def main():
    acquired=json.loads((HERE/'access-log.json').read_text(encoding='utf8'))
    sources=[]
    for a in acquired:
        if a['status']=='acquired':
            sources.append({'source_kind':'new ordinary-public acquisition',**a,
                            'pdf_page_count':__import__('fitz').open(ROOT/a['path']).page_count})
    for path,title,url,coordinates,purpose in [
        ('research/literature/sources/joshi_parpola_1987_cisi1.pdf','Joshi and Parpola 1987, Corpus of Indus Seals and Inscriptions 1: Collections in India','https://ignca.gov.in/Asi_data/76884.pdf','Printed 276–278, 282–283, 286, 365–366, 373; first-scan PDF312–314, 318–319, 322, 401–402, 409','Newly inspected original catalogue views and registration/photograph key'),
        ('research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf','Kenoyer and Meadow 2010, Inscribed Objects from Harappa Excavations 1986–2007','https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf','Standalone PDF3 / displayed author page 3, footnote 4','Original registration syntax and 2010 reserve-collection statement'),
        ('research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf','Meadow and Kenoyer 2000, The Tiny Steatite Seals and Tablets of Harappa','https://www.harappa.com/sites/default/files/pdf/Kenoyer2000_The%20Tiny%20Steatite%20Seals%20of%20Harappa.pdf','Figure 4, caption PDF16 / displayed author page 15 / mapped book335','Earlier caption-ledger joins reused; previous pixels not recoded')]:
        sources.append({'source_kind':'existing local witness; new stated use',**record(path),
                        'title':title,'url':url,'coordinates':coordinates,'purpose':purpose,
                        'rights_status':'third-party witness local-only'})
    web={'source_kind':'original author-deposit text inspected with web reader; PDF unacquired',
         'title':'Frenez 2024, Were the Cretulae (Clay Sealings) from the Indus Port Town of Lothal Part of an Administrative Archive? Contextual, Interpretive, and Comparative Evidence',
         'citation':'South Asian Studies 40(2), 214–234; online 12 September 2024',
         'doi':'10.1080/02666030.2024.2401206',
         'publisher_url':'https://www.tandfonline.com/doi/full/10.1080/02666030.2024.2401206',
         'author_deposit_url':'https://www.academia.edu/127571731/Were_the_Cretulae_Clay_Sealings_from_the_Indus_Port_Town_of_Lothal_Part_of_an_Administrative_Archive_Contextual_Interpretive_and_Comparative_Evidence',
         'catalogue_route':'https://www.harappa.com/content/were-cretulae-clay-sealings-indus-port-town-lothal-part-administrative-archive-contextual',
         'pdf_sha256':None,'source_pixels_inspected':False,
         'source_coordinates':[{'printed_page':225,'figure':9,'objects':['L190','L206','L163'],
             'caption_interpretations':{'L190':'wooden cages','L206':'door peg on wall','L163':'wooden boxes'}},
             {'printed_pages':[228,229],'section':'Acknowledgements','locator':'ASI 2005 and National Museum India 2006 research licences for original documentation'}],
         'use':'Named original figure and archive routes for acquisition; caption interpretations retained as published assertions.'}
    sources.append(web)
    save(HERE/'source-manifest.json',{'sources':sources,
        'protocol':record((HERE/'PROTOCOL.md').relative_to(ROOT).as_posix()),
        'protocol_file_modified_utc':datetime.datetime.fromtimestamp((HERE/'PROTOCOL.md').stat().st_mtime,datetime.timezone.utc).isoformat(),
        'coordinate_pilot':{**record((RAW/'coordinate-pilot-observations.json').relative_to(ROOT).as_posix()),
            'failure':'The three initial 2020 crops used page-layout estimates rather than native montage coordinates and included L145. Native-image inspection caught the error. Corrected L190 crops have v2 filenames and observations-v2.json; the pilot contributes zero accepted views.'},
        'source_disagreements':[{'source':'Frenez 2020','coordinates':'PDF13 printed33 and PDF14 printed34',
            'observation':'The photographed montage caption is Figure 9; the following prose calls the L190 montage Figure 8.'},
            {'source':'Frenez chapter cited 2018','coordinates':'PDF14 printed173',
            'observation':'The page footer displays copyright 2017. Bibliographic citation year and displayed footer year remain separate.'}]})
    loc=json.loads((ROOT/'experiments/2026-10-02-connections-and-priority/harappa-short-records/main-v2/source-locators.json').read_text(encoding='utf8'))
    wanted=['H2238','H2230','H2234','H2237','H2231','H2232','H2233','H2239']
    targets=[]
    for key in wanted:
        item=next(x for x in loc['registered_crop_locators'] if x['target_id'].replace('-','')==key)
        reg=item['registration']; year=2000+int(reg[1:3])-100
        targets.append({'object_id':key,'registration':reg,'specimen':item['specimen'],
            'role':'primary target' if key in wanted[:4] else ('cross-group visibility comparison' if key=='H2239' else 'same-production Group 3 control'),
            'museum_locator':'Harappa Museum reserve collection, per 2010 introduction; current loan/storage location unconfirmed',
            'record_locator':f'HARP {year} registration register and excavation-unit record {reg.split("/")[1].split("-")[0]}',
            'new_registered_photograph':False})
    save(HERE/'record-locators.json',{'harappa':targets,
        'lothal':{'target_ids':['L161','L162','L163','L165','L168','L190','L193','L206'],
            'catalogue_registration_source':'CISI1 printed 373 / PDF409; column key printed 365–366 / PDF401–402',
            'catalogue_holding':'ASI Lothal Site Museum, Saragwala, as recorded in 1987',
            'detailed_rows_local':record((RAW/'cisi1-target-basic-data.json').relative_to(ROOT).as_posix()),
            'photographic_archives':['Helsinki University CISI photograph archive: Finnish Concordance numbers and HU photograph keys in basic data',
                'ASI Lothal / Lothal Revisitation Project documentation, January 2005',
                'National Museum, New Delhi documentation, February 2006'],
            'archive_dates_source':'Frenez university-hosted CV, PDF2 / printed2; original 2024 article acknowledgement corroborates licence years'},
        'interpretation_of_locators':'Historical catalogue/storage statements and archive sessions guide a request; current holding and original-file availability need confirmation.'})
    packet='''# Observation request packet — saved locally, unsent

This packet identifies the existing object records and the particular surfaces needed for the next physical tests. It can be used after the owner decides to request collection access. The registrations should be checked against the current collection record before photography. The linked historical holding statements date to 1987 for Lothal and 2010 for Harappa; loan and storage changes may have followed.

## Harappa registered tablets

Priority targets are H2238 (H95-2613/6560-01), H2230 (H97-3311/8040-10), H2234 (H97-3322/8040-16) and H2237 (H96-3125/6937-16). Same-production controls are H2231 (H97-3320/8040-14), H2232 (H97-3321/8040-15) and H2233 (H97-3341/8039-10). H2239 (H96-3046/6951-04) supplies a separate Group 2 visibility comparison. The original Figure 4 caption in Meadow and Kenoyer 2000 fixes these registrations and specimen numbers; CISI3.1 plate/basic-data pages should confirm the catalogue joins.

Seek the current registration record, original HARP camera files, CISI photographs and any existing moulds or microscopic documentation for each named tablet. Include a photograph of its registration tag in the same acquisition series. Request all three long faces and both ends, plus overlapping oblique views that link each long face to its neighbours. Keep the same physical end visible in each adjoining-face pair. A scale and an unambiguous physical orientation reference should accompany the series.

For H2238, expose the complete diamond-like module and adjoining grooves from two opposing light directions. The question is whether three grooves occupy the whole prepared face or whether a fourth groove is obscured, fractured or absent. For H2237, expose the cup/C-form construction at sufficient resolution to distinguish its branches and tool cuts. Record preparation lines, fractures and cutting traces on the three same-production controls in the same views. The prior drawing display does not establish the physical ordering of all three faces, so the adjoining-face sequence is part of the requested information. Keep full photographs and original pixel dimensions beside any crop.

The registration and excavation-unit designations identify HARP's 1995, 1996 and 1997 object registers and field unit records. The 2010 introduction, PDF3 footnote 4, describes these links and the Harappa Museum reserve collection. It also describes fieldbooks with unit relationships and object coordinates. Request the relevant unit record, find coordinate and phase assignment with its stratigraphic basis. These records would test deposition and production associations independently of the graphic counts.

## Lothal clay sealings

Priority G01 objects are L190, L193 and L206. Priority G02 objects are L161, L162, L163, L165 and L168. Their source-derived museum registrations, excavation numbers and archive keys are preserved in the adjacent local file cisi1-target-basic-data.json. CISI1 printed 373 is the individual registration source. Its key on printed 365–366 identifies LTH as the ASI Lothal Site Museum at Saragwala and HU as the Helsinki CISI photograph archive.

Seek the original negatives/camera files for the named HU or ASI photographs, then the 2005 ASI and 2006 National Museum documentation sessions identified by Frenez's CV and the 2024 article. Frenez 2024 Figure 9 on printed 225 names L190, L206 and L163 contact photographs. The original large file or a permitted high-quality scan of that figure would be a specific next acquisition. Confirm its object labels and photography dates before joining it to the catalogue.

For L190 and L193, request complete stamp, rear, side and end views, with overlapping views that follow each recess and ridge around the body. Obtain a profile through the most distinct junction, preferably an existing three-dimensional model or a calibrated surface scan. The test asks whether two contact planes meet at a consistent angle or whether the contact follows a broad curve. L206 provides the existing curved-contact comparison. Preserve cracks and detached fragments in the model rather than smoothing them across a junction.

For G02, request the whole upper, rear and lateral marked surfaces in one registered series. Use diffuse light and opposing raking light, and include adjoining faces so repeated photographs can be assigned to the same depression. Each proposed cut needs its endpoints and relation to cracks, channels and stamped borders. The current photographs give partial-zone lower counts. A complete surface series would let us test whether the repeated stamp string accompanies a fixed or variable cut total. A physical quantity claim would additionally need an independent object/container measurement or record that predicts the count.

Keep the stamp panels separately available at native resolution for a die comparison. L190 and L193 have several numbered impressions; the particular impression joined to G01 must be identified before a same-die claim. Provide scale, preservation history, whether surfaces are original or casts, and the current registration location. No external message has been sent from this branch.
'''
    p=RAW/'OBSERVATION-REQUEST.md'
    if p.exists():raise FileExistsError(p)
    p.write_text(packet,encoding='utf8')
    save(HERE/'request-packet.json',{'status':'locally saved; unsent','packet':record(p.relative_to(ROOT).as_posix()),
        'purpose':'Registered views, original camera files and source records for the Harappa exceptions and Lothal contact/cut tests',
        'harappa_targets':4,'harappa_same_production_controls':3,'harappa_cross_group_comparison':1,'lothal_targets':8})


if __name__=='__main__':main()
