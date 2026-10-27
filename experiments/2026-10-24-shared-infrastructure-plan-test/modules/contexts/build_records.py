"""Author context assessments and deterministic catalogue gates; no architecture outcomes."""
from pathlib import Path
import collections
import hashlib
import json
import re
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[1]
ROOT=PACKAGE.parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/contexts')
PROTOCOL='11c69454d6e50304b5704db0865f76abca8d84363a67a21d42e8573e256cdb6e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def loc(source,page,index,detail):return {'source_id':source,'printed_page':page,'pdf_index':index,'pdf_page':index+1,'detail':detail}
def main():
    assert sha(PACKAGE/'PROTOCOL.md')==PROTOCOL
    assert (ROOT/'data/raw').resolve()==RAW.parents[1]
    joins=[]
    def add(id,town,unit,aliases,material,deposit,feature,phase,formation,evidence,locations,spatial=None,date_rejections=None,limits=None,closure=False):
        joins.append({'id':id,'town':town,'object_or_cohort_unit':unit,'aliases':aliases,'material':material,
          'deposit':deposit,'named_feature':feature,'phase_as_reported':phase,'formation':formation,
          'assertion':evidence,'source_locators':locations,'spatial_anchor':spatial,
          'date_evidence_ids':[],'rejected_date_candidates':date_rejections or [],
          'dating_basis':'Source stratigraphy or ceramic/stage association; no independently dated construction-to-object-use chain established for this unit.',
          'physical_closure_contact':closure,'eligible_C0018_matched_pair':False,'eligible_C0019_work_allocation_pair':False,
          'reason_codes':limits or ['NO_SAMPLE_TO_CONSTRUCTION_TO_OBJECT_USE_JOIN','NO_MATCHED_BEFORE_AFTER_PAIR'],
          'missing_reason':'No reported sample and stratigraphic relation independently dates a specific construction or repair associated with this object/cohort.',
          'identity_status':'Publication unit retained; catalogue alias does not itself adjudicate physical uniqueness.'})

    # Farmana: each object is distinct in this local publication, not six clay closures.
    farm=loc('EAST-SHINDE2011',371,384,'Tables 7.2–7.3; compare p.384 Fig.7.18 (index397) and p.385 (index398).')
    farmtext=loc('EAST-SHINDE2011',385,398,'Context and use discussion; source denies a specific structural-context association for the seals.')
    for n,trench,phase,deposit,feature in [
      (1,'North Area Trench 2','4','Reported in association with Structure 1; exact use surface not supplied.','Structure 1, reported vicinity'),
      (2,'East Area Trench 2XD5 (prose: Trench 2XD)','4','Layer sealing the mud-brick structures of structural Phase 4.','Sealed Phase 4 structures; no individually named room'),
      (3,'Central Area Trench 1H8','5','Layer enclosing the mud-brick structures of structural Phase 5.','Phase 5 structures; no individually named room'),
      (4,'Central Area Trench 1B6','5','Layer sealing the mud-brick structures of structural Phase 5.','Phase 5 structures; no individually named room')]:
        add(f'FAR-S{n}','Farmana','one steatite seal',[f'Farmana S{n}'],'steatite',deposit,feature,{'namespace':'structural phase','label':phase},'architectural enclosure/sealing deposit or unresolved proximity; primary use unproven',
          f'S{n} has a trench and source phase, but the report does not establish an operational seal-use floor.',[farm,farmtext],
          {'kind':'bounded trench','as_printed':trench,'point_coordinates':None,'uncertainty':'Trench/area only; Fig.7.18 leaders do not establish an exact registered-object point.'},
          ['FAR-PLD15057' if n==2 else 'FAR-PLD12425'] if n in (2,3,4) else [],
          ['SOURCE_DENIES_SPECIFIC_STRUCTURAL_CONTEXT','DEPOSITION_NOT_ORIGINAL_USE','NO_INDEPENDENT_REPAIR_DATE'])
    add('FAR-S5','Farmana','one impressed terracotta sealing',['Farmana S5'],'fired clay',
      'North Area Trench 3; source structural Phase 4. Exact deposit formation unspecified.',None,{'namespace':'structural phase','label':'4'},'application contact preserved; find deposit unresolved',
      'Reverse grooves are attributed to bamboo/reed; a cloth surface and finger impressions are described. These are physical application traces, without a dated named closure.',[farm,farmtext],
      {'kind':'bounded trench','as_printed':'North Area Trench 3','point_coordinates':None,'uncertainty':'No exact object-to-floor anchor.'},['FAR-PLD9491','FAR-PLD9492','FAR-PLD9493'],
      ['CONTACT_TRACES_WITHOUT_NAMED_CLOSURE','DATES_FROM_DIFFERENT_STRUCTURAL_PHASES','NO_MATCHED_BEFORE_AFTER_PAIR'],True)
    add('FAR-S6','Farmana','one impressed terracotta pendant',['Farmana S6'],'terracotta',
      'Central Area Trench 1C2; source structural Phase 5.',None,{'namespace':'structural phase','label':'5'},'perforated pendant; use and discard location unresolved',
      'The plano-convex object has a horizontal perforation for suspension. A sealing designation would add a closure function that the physical description does not establish.',[farm,farmtext],
      {'kind':'bounded trench','as_printed':'Central Area Trench 1C2','point_coordinates':None,'uncertainty':'Same grid vicinity as PLD-12425, without a shared depositional unit.'},['FAR-PLD12425'],
      ['CLOSURE_FUNCTION_UNESTABLISHED','GRID_AND_PHASE_OVERLAP_NOT_DEPOSIT_JOIN','NO_MATCHED_BEFORE_AFTER_PAIR'])
    add('FAR-ST3N-DATE','Farmana','one named-structure charcoal sample',['08-001','PLD-12422'],'carbonized wood',
      'Trench 1E1 / Structure no.3N; laboratory chapter classifies the age as Gupta.', 'Structure no.3N as sample label',{'namespace':'dated cultural assignment','label':'Gupta'},'later material in a source-labelled structure context; intrusion pathway unresolved',
      'A structure number alone would create a false Harappan construction date: this sample is 1390±20 BP and calibrated AD 616–666.',
      [loc('EAST-SHINDE2011',832,845,'Table13.1 sample08-001; Table13.2 pp.833–834 (indices846–847).')],
      {'kind':'bounded grid','as_printed':'Tr.1E1 / St.no.3N','point_coordinates':None,'uncertainty':'No direct original-construction relation.'},['FAR-PLD12422'],
      ['LATER_DATED_MATERIAL','STRUCTURE_LABEL_NOT_CONSTRUCTION_EVENT'])

    add('KAN-3IMP','Kanmer','source cohort of three terracotta impressions; not three proven users',[], 'terracotta',
      'Harappan attribution in the held 2011 article. An indexed Chapter8 lead gives IIb/layers8–9, but that chapter is not held as a full source.',None,
      {'namespace':'source cultural phase','label':'Harappan in held article; IIb indexed lead remains unverified'},'perforated impressed objects; application and find formation unresolved',
      'Three impressions were made with the same stamp and have eccentric perforations. The identity-card analogy remains a functional proposal; the original article does not join a registered impression to a dated room repair.',
      [loc('EAST-KHARAKWAL2011','369–370',14,'Impressions; description continues at index15. Chapter8 source lead is separately recorded as unheld.')],
      None,['KAN-PLD14757','KAN-PLD14760'],['INDIVIDUAL_REGISTRATIONS_UNHELD','SOURCE_CHAPTER_NOT_HELD','LAYER_NUMBER_ALONE_NOT_DATE_JOIN','NO_NAMED_REPAIR'])
    add('KAN-RICE-INTRUSION','Kanmer','two directly AMS-dated rice samples',['PLD-16351','PLD-16353'],'rice grains',
      'Reported from Mature and Late Harappan sample groups; article interprets historic-age grains as reworked/percolated.',None,
      {'namespace':'field phase versus direct age','label':'Mature/Late assignment; direct dates fourth–fifth century AD'},'later intrusion/reworking inferred from direct age',
      'Direct grain dates show that a cultural-phase label cannot establish the age of every item recovered with it.',
      [loc('POKHARIA2011',1836,3,'Oryza sativa paragraph; two sample IDs and calibrated AD ranges.')],
      None,['KAN-PLD16351','KAN-PLD16353'],['INTRUSIVE_DIRECT_DATES','NO_OBJECT_TO_CONSTRUCTION_LINK'])

    add('BAN-SITTINGROOM','Banawali','horned-tiger seal and associated house assemblage; number of house seals not enumerated',[], 'seal material not specified on the bounded page; weights and pottery also reported',
      'Mud-brick-paved sitting room of house illustrated in Plates10.11a–b. More than one seal and jars half embedded in floors reported for the same house.',
      'Paved sitting room; house in Plates10.11a–b',{'namespace':'cultural period','label':'Mature Harappan house discussion; subphase not supplied on p.117'},'reported room find; exact floor-contact/deposition relation unresolved',
      'This is a positive house/room association. The rich-merchant interpretation is the excavator’s interpretation of seals, weights and jars; it cannot independently validate a merchant reading of the inscription.',
      [loc('BISHT1982-P117',117,139,'Archive page image n139; this is an archive image index, not an index in a held PDF. Plates10.11a–b referenced.')],
      {'kind':'source house photograph/plate reference','as_printed':'Plates10.11a–b; sitting room','point_coordinates':None,'uncertainty':'No survey grid or room number on the held page.'},None,
      ['CATALOGUE_ALIAS_UNVERIFIED','EXACT_PHASE_UNREPORTED','NO_SAMPLE_TO_CONSTRUCTION_TO_OBJECT_USE_JOIN','FUNCTION_FROM_ASSEMBLAGE_NOT_INDEPENDENT'])
    joins[-1]['candidate_alias_rejected']={'alias':'CISI B17 / BNL-9201','status':'not joined','reason':'The held primary page names no registration. Similar animal motif and later attribution do not establish identity.'}
    joins[-1]['source_locators'][0].update(pdf_index=None,pdf_page=None,archive_page_image_index=139)
    add('BAN-IAR-SEALS','Banawali','unquantified seals and sealings reported for a season',[], 'unspecified in summary',
      'PeriodII finds list; no seal/room registration in the bounded annual-review entry.',None,{'namespace':'cultural period','label':'II'},'unresolved',
      'The annual review records rebuilt gate/drain phases and seals/sealings in the same entry. It does not join those objects to one of the three rebuilding episodes.',
      [loc('EAST-IAR1986',33,41,'PeriodII gate/drain rebuilding and important finds; PlatesXIIB–C.')],None,None,
      ['CO_REPORTING_NOT_CONTEXT_JOIN','UNQUANTIFIED_COHORT','NO_INDEPENDENT_EPISODE_DATE'])

    har54loc=loc('KENOYER2005','2–4',1,'Trench54 context, manufacture evidence; Fig.2 index7 and Fig.3 indices8–9.')
    add('HAR-TR54-MANUFACTURE','Harappa','Fig.3 set: five incised tablets, two steatite blanks and eight moulded faience tablets (15 illustration units)',
      ['H2001-5084/2913-07','H2001-5087/2934-01','H2001-5069/2913-02','H2001-5068/2913-01','H2001-5074/2913-04',
       'H2001-5187/2934-270','H2001-5135/2913-210','H2001-5064/2373-01','H2001-5065/2373-02','H2001-5077/2913-05',
       'H2001-5083/2913-06','H2001-5089/2913-08','H2001-5090/2913-09','H2000-5042/2357-13','H2000-5041/2360-01'],
      'steatite and faience','Manufacturing material in fill of a courtyard bounded by walls; wall robbery and erosion exposed the fill.',
      'Trench54 workshop [601]; courtyard bounded by [603]–[606] and other source features',{'namespace':'Harappan period','label':'3B, from pottery; no 3C pointed-base goblets'},
      'manufacturing debris/fill; not an operating tablet-use floor',
      'Unfired and broken tablets, blanks, sawn steatite, faience waste and firing-canister fragments support tablet manufacture within a bounded craft area.',[har54loc],
      {'kind':'bounded survey grid and feature polygon','as_printed':'Fig.2: workshop[601], E2105–2110 vicinity, N1235 to north of N1240','point_coordinates':None,
       'north_reference':'N arrow; survey north reference not specified','scale':'5m scale bar','uncertainty':'Figure2 supports a workshop area. Figure3 registrations lack individual map points.'},
      ['HAR-BETA93756','HAR-WGNEC2525'],['MANUFACTURE_NOT_PRIMARY_DOCUMENT_USE','DISTANT_DATES_NOT_TRANSFERABLE','NO_INDEPENDENT_REPAIR_DATE'])
    add('HAR-TR54-DOWNSLOPE','Harappa','one moulded tablet illustrated separately',['H2000-4483/2342-01'],'faience',
      'Downslope surface find; not part of the bounded Fig.3 workshop set.',None,{'namespace':'source period association','label':'unresolved'},'erosion/surface displacement',
      'The separately illustrated downslope tablet must not enlarge the secure workshop cohort.',[loc('KENOYER2005', 'Fig.4',9,'Fig.4.3 registration; surface/downslope context in prose index1.')],None,None,
      ['DOWNSLOPE_SURFACE_FIND','COHORT_BOUNDARY_EXCLUDES_OBJECT'])
    tiny_aliases=['H2218–H2239 (CISI publication cohort; no fresh object-identity adjudication)',
      'H97-3304/8040-01','H97-3305/8040-02','H97-3312/8040-05','H97-3314/8040-07','H97-3290/8010-03','H97-3315/8040-08',
      'H97-3318/8040-12','H97-3333/8038-01','H97-3317/8040-11','H97-3319/8040-13','H97-3316/8040-09','H97-3313/8040-06',
      'H97-3306/8040-03','H97-3307/8040-04','H96-3046/6951-04','H96-3125/6937-16','H95-2613/6560-01','H97-3311/8040-10',
      'H97-3341/8039-10','H97-3320/8040-14','H97-3322/8040-16','H97-3321/8040-15']
    add('HAR-W296-22','Harappa','22 incised tablets: 16 in clump, two nearby and four scattered (source reconstruction)',tiny_aliases,'steatite',
      'Secondary dump deposited after Wall296 construction, in fill between Walls250 and296; before Period3C material.',
      'Dump beside Wall296, between Walls250 and296',{'namespace':'Harappan period','label':'3B fill before 3C material'},'secondary discard; original manufacture/use location unresolved',
      'A close physical grouping survives, but its deposition postdates construction of Wall296. The grouping cannot directly identify an office operating in the room or the date of that wall.',
      [loc('MK2000',13,13,'Interpretation of discard and Wall296; Fig.2 p.7 index7 and Fig.4 caption p.15 index15.')],
      {'kind':'bounded source plan','as_printed':'Fig.2, E2515–2530, N1172–1202; clump C east of Wall296','point_coordinates':None,'north_reference':'source plan grid; absolute north reference unreported','scale':'5m source bar','uncertainty':'Author plots approximate finds; no individual modern coordinates.'},
      ['HAR-BETA93756','HAR-WGNEC2525'],['SECONDARY_DUMP_AFTER_WALL_CONSTRUCTION','MANUFACTURE_AND_USE_LOCATION_UNKNOWN','DISTANT_DATES_NOT_TRANSFERABLE'])
    add('HAR-W296-SEAL','Harappa','one seal compared with the tablet cohort',['H96-2796/6876-01'],'steatite',
      'Street deposit on the inner side of Wall296, separate from the tablet clump.', 'Street inside Wall296',{'namespace':'Harappan period','label':'3B source discussion'},'street deposit; original use unresolved',
      'Shared terminal signs and nearby excavation areas do not establish that this seal and the 22 tablets belonged to one operator or one use event.',
      [loc('MK2000',15,15,'Fig.4 no.1 and caption; contextual discussion pp.12–13.')],None,None,['SEPARATE_DEPOSIT','SIGN_MATCH_NOT_SHARED_USE_EVENT','NO_INDEPENDENT_REPAIR_DATE'])
    for id,alias,deposit,feature,assertion in [
      ('HAR-TR10E-COURTYARD','H95-2491/4690-01','Prose: courtyard floor; Fig.7.6 caption: floor/fill.','Trench10E courtyard','A complete unicorn seal has a positive courtyard association, with a floor versus floor/fill qualification retained.'),
      ('HAR-TR10E-ROOM','H95-2598/4666-19','Trench10E floor deposits in a room with central hearth, corner bin and broken grindstone.','Trench10E hearth-and-bin room','The source reports an ordinary room assemblage with a seal; the hearth does not supply a reported same-context determination.'),
      ('HAR-TR10E-UPPERFILL','H95-2419/4609-01','Upper fill of Trench10E.','Trench10E upper fill','Wear shows an object history, while its upper-fill deposit leaves its original operating room unresolved.')]:
        add(id,'Harappa','one seal',[alias],'steatite',deposit,feature,{'namespace':'Harappan period','label':'3B/upper-fill3C distinction; individual depositional limits retained'},
          'reported floor/floor-fill' if 'UPPERFILL' not in id else 'upper fill',assertion,
          [loc('MK1997',150,11,'Trench10E discussion; Fig.7 caption p.154 index15, nos.4–6.')],
          {'kind':'named source area','as_printed':feature,'point_coordinates':None,'uncertainty':'No per-object point or room number supplied in the bounded description.'},
          ['HAR-A7522','HAR-QL4732'],['FLOOR_FILL_QUALIFIER' if 'COURTYARD' in id else 'USE_SURFACE_OR_FUNCTION_UNRESOLVED','NEARBY_HEARTH_DATES_NOT_TRANSFERABLE','NO_INDEPENDENT_REPAIR_DATE'])
    add('HAR-TR19-TABLET','Harappa','one incised tablet; registration unresolved within this report passage',[],'steatite',
      'Apparently undisturbed deposits above the floor of a room, among five inscribed objects from Trench19.', 'Trench19 room, unnumbered in passage',
      {'namespace':'Harappan period','label':'earlier domestic levels distinguished from final3C; object subphase unresolved'},'above-floor deposit, source-qualified undisturbed',
      'This is a useful positive room association. Above-floor deposition does not establish the act or place of tablet use.',
      [loc('MK1997',148,9,'Trench19 discussion, five inscribed objects and one above-floor incised tablet.')],None,None,
      ['REGISTRATION_NOT_RESOLVED','ABOVE_FLOOR_NOT_OPERATIONAL_SURFACE','NO_INDEPENDENT_REPAIR_DATE'])
    add('HAR-TR9-SUMP','Harappa','one inscribed jar with four sets of marks',['H95-2661/6640-501'],'black-slipped pottery',
      'Jar sunk into the floor of a Trench9 room, reused as a sump.', 'Trench9 room, installed sump jar',
      {'namespace':'Harappan period','label':'3B source room discussion'},'in-place secondary functional reuse',
      'Installation in a floor supports use as a wastewater sump. Two pre-firing and two post-firing sets of incisions need not date to that final use.',
      [loc('MK1997',151,12,'Trench9 jar discussion; Fig.12.2 and caption p.161 index22.')],
      {'kind':'bounded source room','as_printed':'Trench9; Fig.12.2','point_coordinates':None,'uncertainty':'No object-specific survey point or sample-to-installation join.'},
      ['HAR-A7525','HAR-QL4731'],['INSCRIPTION_EVENT_PRECEDES_OR_SPANS_REUSE','ADJACENT_HEARTH_NOT_INSTALLATION_DATE','NO_MATCHED_BEFORE_AFTER_PAIR'])
    add('HAR-TR9-SURFACE','Harappa','one moulded tablet',['H94-2218/4529-04'],'faience',
      'Trench9 surface/slopewash.',None,{'namespace':'source period association','label':'unresolved'},'surface/slopewash',
      'A tablet from the same excavated area as dated rooms remains a displaced object when its own recorded deposit is surface/slopewash.',
      [loc('MK1997',154,15,'Fig.7.8 caption.')],None,['HAR-A7525'],['SURFACE_SLOPEWASH','AREA_MEMBERSHIP_NOT_DATE_JOIN'])
    add('HAR-TR22-CAPTION-CONFLICT','Harappa','two faience tablets cited in the Trench22 narrative',
      ['H94-2274/5332-01','H94-2283/5332-02'],'faience',
      'Prose: street deposits inside perimeter wall in Trench22. Figure11.4/.6 caption: Trench7/8,wash.',
      'Perimeter-wall/gateway area; precise deposit disputed within the publication',
      {'namespace':'Harappan period','label':'wall founded after dated underlying hearth; tablet subepisode unresolved'},
      'street-deposit versus wash conflict; not adjudicated',
      'This is a promising partial date-to-wall chain whose documentary end fails: actual samples lie below Wall15, while the tablet passage and figure caption disagree about the find deposit.',
      [loc('MK1997',147,8,'Trench22 narrative cites Figure11.4/.6.'),loc('MK1997',160,21,'Figure11 caption gives registrations and Trench7/8,wash.'),
       loc('MK1997',143,4,'Table1: H94/5383[64],H94/5384[66],H94/5385[67] below Wall15; construction inference continues pp.143–144.')],
      None,['HAR-A8047','HAR-A8048','HAR-A8049'],
      ['CONFLICTING_PROSE_AND_CAPTION_CONTEXT','BELOW_WALL_DATE_NOT_TABLET_USE_DATE','NO_MATCHED_BEFORE_AFTER_PAIR'])

    # All 225 Dholavira source rows remain D-only. Gates are literal and deliberately limited.
    inherited=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/inscriptions/dholavira-context-table-v1.json')
    assert sha(inherited)=='94c42d5f1dd0e32e50dca05586da4ba41bae9f71fd969608e693badc2a6b4bcb'
    dhol=json.loads(inherited.read_text(encoding='utf8'))
    derived=[]
    def supplied(v):return str(v or '').strip().lower() not in ('','-','?','unst','unst.','nil')
    for row in dhol['rows']:
        s=row['stratum'].strip(); stage=row['stage_as_printed'].strip()
        room='room' in s.lower()
        secondary=bool(re.search(r'surface|erod|debris|filling|rain|disturb',s,re.I))
        pit=bool(re.search('pit',s,re.I)); reservoir=bool(re.search('reservoir',s,re.I))
        gates={'accession_string':supplied(row['accession']),'grid_label':supplied(row['grid']),
          'stratum_label':supplied(row['stratum']),'depth_label':supplied(row['depth_as_printed']),
          'area_label':supplied(row['area_as_printed']),'unqualified_stage':re.sub(r'\s+','',stage) in ('I','II','III','IIIA','IIIB','IV','V','VI','VII'),
          'explicit_room_label':room,'explicit_pit_label':pit,'explicit_reservoir_label':reservoir,
          'explicit_secondary_or_disturbed_label':secondary,'primary_use_surface_established':False,
          'independent_construction_date_established':False,'C0018_pair_eligible':False,'C0019_pair_eligible':False}
        reasons=['CATALOGUE_ROW_NOT_PHYSICAL_IDENTITY_ADJUDICATION','NO_PRIMARY_USE_SURFACE_OR_CUSTODY_EVENT','NO_INDEPENDENT_CONSTRUCTION_DATE']
        if not gates['unqualified_stage']:reasons.append('STAGE_EMPTY_MIXED_QUESTIONED_OR_UNPARSED')
        if secondary:reasons.append('EXPLICIT_SECONDARY_OR_DISTURBED_LABEL')
        if room:reasons.append('ROOM_LABEL_WITHOUT_USE_SURFACE_OR_BUILDING_EPISODE')
        if pit:reasons.append('PIT_LABEL_WITHOUT_FILL_HISTORY')
        if reservoir:reasons.append('RESERVOIR_LABEL_WITHOUT_OPERATIONAL_EPISODE')
        derived.append({'source_row':row,'gates':gates,'reason_codes':reasons})
    dpath=RAW/'dholavira225-join-gates-v1.json'
    write(dpath,{'source_id':'BISHT2015-PRELIM','inherited_path':str(inherited),'inherited_sha256':sha(inherited),
      'rule':'Literal fields, not archaeological-absence coding. Any positive room/pit/reservoir flag is a source-label lead, not an original-use finding.',
      'rows':derived})
    ds={'source_rows':len(derived),'unique_accession_strings':len({r['source_row']['accession'] for r in derived}),
        'physical_objects_adjudicated':None,'gate_counts':{k:sum(r['gates'][k] for r in derived) for k in derived[0]['gates']},
        'stage_literal_counts':dict(collections.Counter(r['source_row']['stage_as_printed'] for r in derived)),
        'inscription_literal_counts':dict(collections.Counter(r['source_row']['inscription_as_printed'] for r in derived)),
        'detailed_local_path':str(dpath),'detailed_local_sha256':sha(dpath),
        'field_gate_definition':'A usable label excludes empty,-,?,Unst/Unst. and Nil. Raw cells are unchanged. Removing internal whitespace only turns III A into IIIA for the unqualified-stage gate.',
        'literal_nonplaceholder_counts_including_Nil':{field:sum(str(r['source_row'][field] or '').strip().lower() not in ('','-','?','unst','unst.') for r in derived) for field in ('stratum','depth_as_printed')},
        'meaning_of_zero':'Zero is the number passing this document-based gate in the held table, not absence of primary-use contexts at the site.'}
    write(HERE/'dholavira225-summary.json',ds)
    add('DHO-225TABLE','Dholavira','225 source catalogue rows; physical-object total unadjudicated',[], 'seal/tablet catalogue materials vary',
      'Table gives accession, grid, stratum, depth, motif, inscription, area and stage with gaps.', 'Castle/Bailey/MiddleTown and other source area labels',
      {'namespace':'Dholavira stages','label':'raw stage cells retained in local derivative'},'varied; catalogue labels do not establish primary use',
      'Literal field gates identify source leads while retaining mixed phases, blank fields and explicit displaced deposits. No row establishes the complete sample-to-construction-to-object-use chain.',
      [loc('BISHT2015-PRELIM','247–260',263,'Context table, source serials1–225; individual page locators retained in local rows.')],None,
      ['DHO-TL4','DHO-TL8'],['CATALOGUE_ROWS_NOT_ADJUDICATED_OBJECTS','CONTEXT_TABLE_NOT_USE_HISTORY','STAGE_RANGE_NOT_REPAIR_DATE'])
    for serial in (83,140,211):
        row=next(r['source_row'] for r in derived if r['source_row']['table_serial']==serial)
        add(f'DHO-ROOM-{serial}','Dholavira','one source row with explicit room label',[row['accession']],
          'steatite seal' if serial in (83,140) else 'material not adjudicated here',row['stratum'],row['stratum'],
          {'namespace':'Dholavira stage','label':row['stage_as_printed']},'room attribution; floor/use event unresolved',
          'The row supplies a room label, grid, depth and stage. It does not identify the building episode, an original use surface or an independently related sample.',
          [loc('BISHT2015-PRELIM',row['printed_page'],row['pdf_page']-1,f'Context table serial{serial}; accession{row["accession"]}.')],
          {'kind':'grid and room label','as_printed':row['grid']+'; depth '+row['depth_as_printed']+' as printed; '+row['area_as_printed'],
           'point_coordinates':None,'uncertainty':'Grid-cell/room bound only; depth datum/unit not imposed from the cell.'},['DHO-TL4','DHO-TL8'],
          ['ROOM_LABEL_WITHOUT_OPERATIONAL_SURFACE','CONSTRUCTION_EPISODE_UNRESOLVED','NO_INDEPENDENT_REPAIR_DATE'])
        if serial==140:joins[-1]['source_conflict']={'table_inscription_cell':'empty','description':'six signs in catalogue description p.289 index305','handling':'Both statements retained; no silent imputation into the source table.'}
    add('DHO-GATE10','Dholavira','one ten-sign panel reconstructed from fallen inlays',[], 'light-coloured inlay in a decayed wooden support; material analysis not independently redone',
      'Western chamber of north gate of Castle; signs found fallen on floor. Original mounting above the gate is reconstructed from layout and support impression.',
      'Castle north gate, western chamber',{'namespace':'Dholavira stage','label':'panel emplacement not independently tied to a dated stage/repair'},'collapse/fall from mounting, source architectural reconstruction',
      'This is the strongest named public-architecture inscription anchor in this six-town audit. Its recovery position does not independently date the panel’s mounting or establish the authority that installed it.',
      [loc('BISHT2015-PRELIM','228–230',244,'Signboard context and reconstruction; compare gate-narrowing narrative pp.586–587, indices602–603.')],
      {'kind':'named chamber','as_printed':'Western chamber, north gate, Castle','point_coordinates':None,'uncertainty':'Fallen position preserved; original lintel mounting is a reconstruction.'},
      ['DHO-TL4','DHO-TL8'],['ORIGINAL_MOUNTING_RECONSTRUCTED','DATE_NOT_TIED_TO_PANEL_EMPLACEMENT','PUBLIC_LOCATION_NOT_AUTHORITY_SCALE'])
    add('DHO-BAILEY4','Dholavira','one four-sign limestone fragment',[], 'limestone',
      'Secondary position in one of four underground chambers south of Bailey.', 'Bailey, underground chamber group',
      {'namespace':'source stage','label':'original emplacement unresolved'},'secondary reuse/displacement',
      'A monumental-inscription fragment has a bounded recovery area, but an original lintel or institutional location cannot be recovered from this deposit alone.',
      [loc('BISHT2015-PRELIM',230,246,'Stone inscription context.')],None,None,
      ['SECONDARY_MONUMENTAL_FRAGMENT','ORIGINAL_ARCHITECTURAL_POSITION_UNRESOLVED'])

    # Transcribe only the provenance labels of FT2005 Table1 locally; preserve the prose conflict.
    statuses=('W W W W W W W1 W1 W1 W W1 W1 W W W1 W1 W O W ? W2 O O W ? ? O ? W2 ? W2 ? ? W2 W W W W W W W W W W W W W '+
      'W W W O W W2 W2 ? W2 W2 ? ? ? ? ? W1 ? ? W W W1 W1 W W1 W1 W W1 W1 W1 W1 W1 W1 W2 ? O W W O W2 O ? W2 ? ? O O').split()
    assert len(statuses)==93
    lrows=[{'CISI_id':f'L{124+i}','table1_provenance':s,'printed_page':93 if i<47 else 94,'pdf_index':30 if i<47 else 31} for i,s in enumerate(statuses)]
    lp=RAW/'lothal-ft2005-table1-provenance-transcription-v1.json'
    write(lp,{'source_id':'FT2005','method':'Manual reading of the two rendered original Table1 pages, not a new identity reconciliation. Retained for independent checking.',
      'rows':lrows,'counts':dict(collections.Counter(statuses)),'prose_counts':{'W':35,'W1':18,'W2':11,'O':11,'?':17},
      'conflict':'Table transcription O10/?19; prose O11/?17. Neither silently substituted for the other.'})
    lsum={'table_rows':93,'table_literal_counts':dict(collections.Counter(statuses)),
      'prose_counts':{'W':35,'W1':18,'W2':11,'O':11,'?':17},'prose_category_sum':92,
      'table_direct_W_plus_O':45,'prose_direct_W_plus_O':46,'table_W_plus_W1_plus_W2':64,
      'W1_basis':'stamp-based inference; excluded from independent location tests',
      'W2_basis':'broad SRG3 trench, no demonstrated warehouse-room deposit',
      'local_transcription_path':str(lp),'sha256':sha(lp),'independent_transcription_review':'not yet completed'}
    write(HERE/'lothal-denominators.json',lsum)
    add('LOT-WAREHOUSE-COHORT','Lothal','source populations65,69/90 and93; denominators unreconciled',[], 'fired clay sealings',
      'Sealing concentration in passage between warehouse blocks41I and41J, above a baked-brick floor, SRG3.',
      'Warehouse passage41I–41J',{'namespace':'Lothal source phases','label':'assigned warehouse destruction sequence; independent sample/event join absent'},
      'competing archive-discard versus fire/collapse sub-primary hypotheses',
      'Concentration and burnt contacts support a linked deposit, but cancellation/archiving, packaging movement and structural collapse remain competing formation histories.',
      [loc('RAO1979',113,123,'65sealings, successive layers above floor.'),loc('RAO1985',319,69,'69 of90 impressions assigned to warehouse.'),
       loc('FT2005','70–72',7,'93sealing study; deposit alternatives. Table1 pp.93–94 (indices30–31).')],
      {'kind':'bounded named passage','as_printed':'SRG3, passage41I–41J, approximately1sqm source concentration','point_coordinates':None,
       'uncertainty':'Cohort area; individual sealing positions and a single contemporaneous collapse are not established.'},
      ['LOT-TF23','LOT-TF19','LOT-TF29','LOT-TF22','LOT-TF27','LOT-TF26'],
      ['DEPOSIT_FORMATION_ALTERNATIVES','DENOMINATORS_UNRECONCILED','DATED_SAMPLES_FROM_OTHER_TRENCHES','NO_PRIMARY_CUSTODY_CHANGE_EVENT'])
    for id,cisi,aliases,contact,formation in [
      ('LOT-L164','L164',['1864','LTH SRG1232'],'cord and wood-related negative contacts; flat support/box reconstruction is tentative','container/packaging application, subsequent warehouse-associated deposit'),
      ('LOT-L206','L206',[],'negative contact modelled as a peg-on-wall/door fastening','immovable-closure application inferred from contact geometry; subsequent warehouse-associated deposit')]:
        add(id,'Lothal','one CISI-designated sealing',[cisi]+aliases,'fired clay',
          'Table1 categoryW: warehouse provenance, without demonstrated original application place.', 'Warehouse deposit; original named closure unknown',
          {'namespace':'source warehouse sequence','label':'episode unresolved'},formation,
          contact+'. The contact concerns physical use; the later find deposit cannot identify a named recipient, office or labour obligation.',
          [loc('FT2005',93 if cisi=='L164' else 94,30 if cisi=='L164' else 31,'Table1 provenanceW; Fig.3 p.98 index35 supplies closure reconstruction.' if cisi=='L206' else 'Table1 and packaging/contact discussion.')],
          None,['LOT-TF22'],['CONTACT_FUNCTION_WITHOUT_ORIGINAL_APPLICATION_LOCATION','NO_DATED_CUSTODY_CHANGE','NO_LABOUR_ALLOCATION_DIAGNOSTIC'],True)
    add('LOT-W1-INFERRED','Lothal','18 source table rows in provenance classW1',[], 'fired clay',
      'Find context inferred from stamp identities shared with warehouse material.', 'Warehouse by stamp-based inference only',
      {'namespace':'source inferred group','label':'not independently established'},'unresolved',
      'Using W1 rows to correlate seal similarity with a warehouse location would build the tested similarity into the location variable.',
      [loc('FT2005','71–72',8,'Provenance methodology; Table1 pp.93–94.')],None,None,
      ['LOCATION_INFERRED_FROM_TESTED_STAMP_IDENTITY','CIRCULAR_SPATIAL_ASSOCIATION'])

    assert len({r['id'] for r in joins})==len(joins)
    write(HERE/'context-joins.json',{'protocol_sha256':PROTOCOL,'analysis_status':'exploratory context audit, no architecture outcomes read',
      'record_unit':'Authored assessment units can overlap. Their count is not a settlement, object or use-event frequency.',
      'towns':['Farmana','Kanmer','Banawali','Harappa','Dholavira','Lothal'],'joins':joins,
      'rejection_code_meaning':'A failed gate describes the held evidence chain, never the archaeological absence of a feature or practice.'})
    summary={'protocol_sha256':PROTOCOL,'assessment_records':len(joins),
      'records_by_town':dict(collections.Counter(r['town'] for r in joins)),
      'C0018_qualified_matched_pairs':0,'C0019_qualified_work_allocation_pairs':0,
      'qualified_pair_denominator':'No matched before/after pair is assembled in this module; zero is an eligibility result for this fixed source frame.',
      'positive_evidence':{'manufacturing_area':'HAR-TR54-MANUFACTURE','reported_floor_floorfill_seals':['HAR-TR10E-COURTYARD','HAR-TR10E-ROOM'],
        'reported_room_house_seal':'BAN-SITTINGROOM','installed_inscribed_object_reuse':'HAR-TR9-SUMP','public_gate_inscription_anchor':'DHO-GATE10',
        'material_contact_function':['FAR-S5','LOT-L164','LOT-L206']},
      'decisive_missing_join':'Registered object/cohort in a demonstrated original-use or custody context, independently dated against a named construction/repair, then paired with a matched episode.',
      'spatial_anchor_limits':'Room, workshop, trench and chamber bounds are supplied where defensible; no invented point coordinates.',
      'prior_familiarity':'Declared; no new architecture persistence outcomes received or read before this record build.'}
    write(HERE/'eligibility-summary.json',summary)
    print(json.dumps({'assessment_records':len(joins),'towns':summary['records_by_town'],'dholavira':ds['gate_counts'],'lothal':lsum['table_literal_counts']},indent=2))

if __name__=='__main__':main()
