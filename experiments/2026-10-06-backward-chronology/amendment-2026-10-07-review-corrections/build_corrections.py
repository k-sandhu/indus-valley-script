"""Apply the dated review corrections without changing either earlier input endpoint."""
from __future__ import annotations
import argparse, copy, csv, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
PKG = OWN.parent
OLD = PKG / 'amendment-2026-10-07-frenez'
RAW = ROOT / 'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# Restore analyst prose only. Identifiers, paths, URLs, keys and bibliographic titles are protected.
PROTECTED = {'id', 'source_id', 'source_ids', 'continuity_claim_ids', 'evidence_row_ids', 'identifiers', 'lab_numbers',
             'local_witness', 'sha256', 'url', 'title', 'anchor_audit', 'radiocarbon_transcription', 'ids_without_script'}
WORDS = r'Nearly|nearly|about|around|circa|into|has|comprise|remains|and|of|to|at|from|within|over|before|after|period|Period|Level|level|Layer|layer|Catalogue|catalogue|Fig|fig|Figure|figure|Table|table|item|number|chapter|locators|Quivron|Coningham|Durrani|Kenoyer|Meadow|Miller|Frenez|Gadd|Laursen|Possehl|Winkelmann|Studies|India|Orientalia|Series|Antiqua'
def tidy(value, field=''):
    if field in PROTECTED or field.endswith('_ids'): return value
    if isinstance(value, dict): return {k: tidy(v,k) for k,v in value.items()}
    if isinstance(value, list): return [tidy(v,field) for v in value]
    if isinstance(value,str) and not re.match(r'^(https?://|data/|experiments/|research/)',value):
        value = re.sub(r'\b(' + WORDS + r')(?=\d)', r'\1 ', value)
        value = re.sub(r'(?<=[a-zéà])(?=\d)', ' ', value)
        value = re.sub(r'\b(PDF|CISI|Tables)(?=\d)', r'\1 ', value)
        value = re.sub(r'\b(et al\.)(?=\d)', r'\1 ', value)
        value = value.replace('LouvreAO', 'Louvre AO').replace('citingQuivron', 'citing Quivron').replace('RoomCXVIII', 'Room CXVIII').replace('NausharoII', 'Nausharo II')
        value = re.sub(r'(?<=json\.)(?=\d{4}\b)', ' ', value)
        value = re.sub(r'(?<=[IVX])(?=\d{3,})', ' ', value)
        value = re.sub(r'\b(pp?\.|no\.)(?=\d)', r'\1 ', value)
        value = re.sub(r'([,;])(?=\w)', r'\1 ', value)
        value = re.sub(r'([.!?])(?=[A-Z][a-z])', r'\1 ', value)
        value = re.sub(r'\b(Period|Level|Layer|Table)(?=[IVX]+[ABC]?\b)', r'\1 ', value)
        value = re.sub(r'\b(pp?\.)(?=[ivxlc]+\b)', r'\1 ', value)
        value = re.sub(r'\b(Figure|Fig)(?=[A-Z]\b)', r'\1 ', value)
    return value

def date(lo, hi, method, locator, grade='C', strength='low', selected=False, labs=None, measurement=None, note=''):
    return dict(start_year=lo,end_year=hi,method=method,grade=grade,calendar_strength=strength,
                selected_for_coverage=selected,source_location=locator,note=note,
                lab_numbers=labs or [],published_measurement=measurement)

def newrow(rid, label, sites, region, sources, locators, assessments, classes=None, count=None,
           kind='unknown', basis='No marked-object census recovered.', additive=True, images=False, limitation=''):
    return dict(id=rid,label=label,region=region,sites=sites,object_classes=classes or ['pottery graffiti'],
                marked_object_count=count,count_kind=kind,count_unit='marked specimens',count_basis=basis,
                repertoire_size=None,repertoire_basis='No normalized repertoire total recovered.',
                dating_assessments=assessments,source_ids=sources,source_locations=locators,
                image_corpus_verified=images,access='Opened local source sections; see sources.json for access and hashes.',
                continuity_claim_ids=[],limitations=limitation,include_in_additive_coverage=additive,
                adjacent_region=False,status='Exploratory',documentary_revision='2026-10-07 review correction')

def rows_corrected(rows):
    rr={r['id']:r for r in rows}
    # Pirak's pooled date is superseded. The captioned specimens are separate period rows.
    r=rr['pirak'];r['include_in_additive_coverage']=False
    for d in r['dating_assessments']:
        d['selected_for_coverage']=False;d['grade']='C';d['calendar_strength']='low'
        d['note']='Superseded for these specimens: Kenoyer gives this pooled bracket, but Fig. 3 assigns them to Period II and IIIA.'
        d['source_location']='Kenoyer 2009 printed p. 10; Fig. 3 caption p. 21 (PDF 19)'
    r['limitations']='Non-additive parent of pirak-II and pirak-IIIA. CISI 2 p. 381 Pk-15–17 is Period IB, so those numbers cannot be assigned to these two later specimens from that citation.'
    r['source_ids'] += ['petrie-magee2012','cisi2-1991','jarrige-santoni1979','magee-petrie2010','dumarcay1980']
    r['source_locations']=['Kenoyer Fig. 3, printed p. 21/PDF 19; CISI 2 pp. 381–385, 446; Petrie and Magee 2012 pp. 4, 11']
    rows.extend([
        newrow('pirak-II','Pirak Period II terracotta button seal (Kenoyer Fig. 3b)',['Pirak'],'Indus northwest',r['source_ids'],r['source_locations'],[
            date(-1500,-1150,'Provisional envelope: assumed Period II start to latest proposed Period III start', 'Petrie and Magee 2012 p. 4; reviewer scenario',note='1500 BCE is a scenario assumption, not a recovered primary boundary. Unselected.'),
            date(-1300,-1150,'Alternative scenario based on the published report review', 'Dumarçay 1980 p. 341; Petrie and Magee 2012 p. 4',note='Unselected; the two chronologies have not been reconciled.')],
            ['terracotta button seal'],1,'exact','One captioned specimen; no site seal census.',images=True,
            limitation='Period attribution is opened in the caption and primary catalogue series, but an exact catalogue concordance and primary absolute boundary remain unrecovered. No selected calendar interval.'),
        newrow('pirak-IIIA','Pirak Period IIIA bronze compartmented seal (Kenoyer Fig. 3a)',['Pirak'],'Indus northwest',r['source_ids'],r['source_locations'],[
            date(-1460,-760,'Broad possible Period III envelope summarized by the recalibration authors; IIIA specimen allocation unresolved', 'Petrie and Magee 2012 pp. 4, 11; Kenoyer Fig. 3a',selected=True,
                 note='Start of III probably 1460–1150 BCE; its end possibly 1300/1200–760 BCE. This envelope is not a confidence interval for IIIA or the seal. Original 2010 recalibration table not opened.')],
            ['bronze compartmented seal'],1,'exact','One captioned specimen, distinct from the Period II seal.',images=True,
            limitation='C/low because only a broad period envelope can be assigned; IIIA is not separately bounded. No new radiocarbon measurement or exact catalogue concordance.')])
    r=rr['perumbalai'];r['source_locations']=['Volume I printed pp. 132, 143–144; Table 3.1 p. 226; Volume II Table 10.1 p. 1175']
    r['dating_assessments'][0].update(source_location='Volume I pp. 143–144; Volume II p. 1175',calendar_strength='low',
        note='B deposit association below Floor I; calendar strength low because midpoint labels and BP/BCE labels conflict, confidence convention is unstated, and graffiti from layers 4–2 lack specimen depths. The 649–499 span is the authors\' midpoint bracket, not a probability interval.')
    r['dating_assessments'].append(date(-682,-493,'Alternative envelope of the four printed calibrated sample ranges', 'Volume II Table 10.1 p. 1175',grade='B',
        labs=['Beta-640429','Beta-640430','Beta-640431','Beta-640432'],note='Unselected alternative; not merged with Volume I midpoints. Sample ranges 499–493, 630–621, 682–620, 649–570 BCE; curve/probability not stated.'))
    for rid in ['perumbalai','keeladi','kodumanal']:
        rr[rid]['count_kind']='exact, temporally unaligned'
        rr[rid]['count_basis']+=' Site-wide count excluded from numeric century bounds because the dated-layer distribution is unavailable.'
    r=rr['kodumanal'];r['marked_object_count']=1955
    r['count_basis']='Table 3.1 reports 2,632 yielded graffiti sherds, of which 1,955 were documented. Site-wide documented total excluded from numeric century bounds; grave/phase distribution and overlap with Tamil letters are unavailable.'
    r['source_locations']=['Volume I pp. 95, 101–102; Table 3.1 p. 224; Tamil-Brahmi documentation p. 229']
    r=rr['keeladi'];r['source_locations']=['Volume I pp. 53, 57; Table 3.1 p. 224; Volume II Table 10.1 p. 1175']
    r['dating_assessments'][0].update(source_location='Volume I pp. 53, 57',lab_numbers=['Beta-519476'],note='Occupation envelope; Beta-519476 is 2530±30 BP, printed 679–531 BCE. No specimen-to-sample join or per-layer count; 3,782 collected versus 2,132 documented.')
    r['dating_assessments'][1]['source_location']='Volume I p. 57'
    r=rr['porunthal-I'];r['marked_object_count']=1;r['count_kind']='minimum documented, conflicting total'
    r['count_basis']='One inscribed ringstand in Volume I p. 153, Volume II p. 1165 and Porunthal_001; Volume I p. 167 says two. Preserve this conflict; no exact two-object total enters numeric bounds.'
    r['dating_assessments']=[date(-580,-520,'Published calibrated rice range for MEG-I; grave association contested', 'Volume II Table 10.1 p. 1175 and p. 1165',selected=True,labs=['Beta-302854'],
        measurement={'bp':2440,'sigma':30,'material':'paddy in four-legged jar adjacent to ringstand','reported_calibrated_bce':[580,520],'reported_calibrated_point_bce':520},note='Curve and confidence level unstated; C/low association. Conventional 490 BCE is separate and is not a calibration.'),
        date(None,None,'Conventional radiocarbon age', 'Volume I p. 167',labs=['Beta-302854'],measurement={'bp':2440,'sigma':30,'conventional_bce':490})]
    r['source_ids'].append('rajan-sivanantham2026-II');r['source_locations']=['Volume I pp. 153, 167; Volume II pp. 1165, 1175; catalogue Porunthal_001']
    r=rr['porunthal-IV'];r['dating_assessments'][0].update(start_year=-560,end_year=-410,selected_for_coverage=False,
        method='Published calibrated rice range; no marked specimen joined',source_location='Volume II pp. 1165, 1175',grade='D',
        note='560–410 BCE, point label 410 BCE; curve/probability unstated. Conventional 450 BCE separate. No marked-object association, so this is a dated comparator only.')
    r['include_in_additive_coverage']=False;r['source_ids'].append('rajan-sivanantham2026-II');r['source_locations']=['Volume I p. 167; Volume II pp. 1165, 1175']
    for rid,count in [('kilnamandi-burials',43),('kilnamandi-habitation',45)]:
        r=rr[rid];r['count_kind']='exact, temporally unaligned'
        r['count_basis']=f'Narrative count {count}; burial p. 69 and habitation p. 74. Tables 3.1 and 4.1 give 103 site-wide sherds; Table 4.3 gives 101. 43+45=88, so 15 relative to 103 remains unallocated. None is a MEG-III specimen count.'
        r['source_locations']=['Volume I pp. 11, 69, 74; Tables 3.1 and 4.1; Table 4.3']
    rr['kilnamandi-burials']['dating_assessments'][0]['note']='The authors assert graffiti-bearing pots accompany the MEG-III sarcophagus (p. 11); no specimen register supports allocation of the narrative 43. Published interval 1769–1615 BCE at 93.3%; C/low remains.'
    r=rr['sivagalai-habitation'];r.update(marked_object_count=150,count_kind='exact, temporally unaligned',
        count_basis='150 post-firing graffiti sherds (p. 192, Table 3.1) and five Tamil-Brahmi sherds separately. No period-specific count; do not add the letter count without overlap control.',source_locations=['Volume I pp. 183, 192, 194; Table 3.1 p. 226'])
    r=rr['sivagalai-early-burials'];r['count_basis']='Volume I p. 295 reports no graffiti on grave goods in opened Sivagalai urns; it does not restrict this statement to early urns.'
    r['dating_assessments'][0]['lab_numbers'].append('Beta-600726');r['dating_assessments'][0]['note']+=' A2-Urn-3 paddy, Beta-600726: 2950±30 BP, reported calibrated point 1155 BCE, separate OSL 1284 BCE. The point has no published interval here.'
    r['source_locations']=['Volume I Table 2.1 pp. 181, 183; p. 295']
    r=rr['inamgaon'];r['source_locations']=['Kenoyer 2004 English manuscript PDF p. 15 (ranges), p. 38 (caption)']
    r['dating_assessments'][0].update(selected_for_coverage=False,source_location='PDF p. 38',note='Editorial century bin for circa 1500 BCE; kept unselected beside separately reported cultural ranges.')
    r['dating_assessments'] += [date(-1600,-700,'Sankalia\'s Early Jorwe cultural range reported by Kenoyer', 'Kenoyer 2004 PDF p. 15',selected=True,note='Cultural attribution; no specimen carbon determination.'),date(-1500,-1050,'Allchins\' alternative Early Jorwe cultural range', 'Kenoyer 2004 PDF p. 15',note='Unselected alternative; not averaged with the Sankalia bracket.')]
    r=rr['harappa-ravi'];r['source_locations']=['Kenoyer 2006 printed p. 14 (PDF 5), Table 1 p. 10, Table 2 p. 12; Kenoyer and Meadow 2010 Table 1']
    if len(r['dating_assessments'])>1:r['dating_assessments'][1].update(method='Earliest Ravi graffiti date, not the full Ravi phase bracket',source_location='Kenoyer 2006 Table 1 p. 10')
    r['dating_assessments'].append(date(-3900,-2800,'Separate published Ravi cultural phase estimate','Kenoyer 2006 p. 11',grade='B',strength='moderate',note='Unselected alternative to the 3700–2800 table estimate; not the earliest-graffiti interval.'))
    for rid in ['daimabad-II','daimabad-III']:
        for d in rr[rid]['dating_assessments']:
            if not d['selected_for_coverage']:
                d['calendar_strength']='low'
                d['note']+=' Low strength also applies to the unselected conventional bracket; Sali pp. 209–210 accepts only PRL-426 for Phase II and finds Phase III determinations inconsistent.'
    rr['harappa-late']['dating_assessments'].append(date(-1900,-1300,'Alternative Late Harappan phase span; low incidence/disappearance of writing', 'Kenoyer 2006 p. 11, Table 1',note='Broad phase estimate; not a continuous sequence of dated inscriptions.'))
    r=rr['lothal-late'];r['dating_assessments']=[date(-1900,-1400,'Rao\'s Lothal B bracket from reported radiocarbon/phase comparisons', 'Rao 1963 p. 181; Thapar pp. 20–22',grade='B',selected=True,note='Old radiocarbon summary; marked material phase-linked through Lal. No specimen/lab association or modern calibration recovered.')]
    r['source_locations']=['Lal pp. 21–22; Rao 1963 p. 181; Thapar pp. 20–22'];r['limitations']='Calendar strength low; cannot establish a sequence of inscriptions through the whole bracket.'
    # Remaining locator and alternative-assessment slips.
    rr['rojdi']['dating_assessments'].append(date(-1500,-1000,'Alternative pottery correlation spans Rangpur IIB–IIC', 'Rao 1963 p. 186',note='Does not locate the illustrated bowl within either phase.'))
    rr['rangpur']['source_locations']=['Rao 1963 pp. 25–27 (chronology), 128 (222 total), 130 (26+188+8)']
    rr['bet-dwarka']['limitations']+=' Sundaresh and Gaur pp. 77, 81 give earliest settlement about 1400 BCE and compare pottery with Rangpur IIC–III; neither dates the marked shell specimens.'
    rr['prakash-I']['dating_assessments'].append(date(-1600,-1000,'Jorwe Ware comparative cultural range', 'Thapar p. 22',note='Three of ten marks on Jorwe Ware; specimen contexts remain unresolved.'))
    rr['navdatoli']['source_locations']=['Thapar pp. 20, 22; Rao pp. 26, 198; Lal bridge discussion']
    rr['nbpw']['image_corpus_verified']=True;rr['nbpw']['source_locations'].append('Lal Plate XXXIV B, grey ware and NBPW sherds')
    rr['south-megalithic-lal']['sites']=[s for s in rr['south-megalithic-lal']['sites'] if s!='Brahmagiri']
    rr['south-megalithic-lal']['limitations']+=' Brahmagiri is a discussion comparator on p. 22, not a listed study site on p. 5.'
    rr['tamil-cave']['dating_assessments'] += [date(0,100,'Dani\'s first-century CE alternative', 'Salomon p. 35 n. 103'),date(-300,-200,'Third-century BCE cave assignment in the Tamil volume', 'Volume II p. 1155',note='Separate author assessment for Mangulam, Puhalur and Jambai; no merge.')]
    rr['ashoka-kharosthi']['count_unit']='edict sites';rr['tn-pooled']['count_kind']='reported aggregate with counting convention'
    r=rr['anuradhapura'];r['dating_assessments'][0]['method']='Beginning-fourth-century statement in opened abstract; dating method not specified there'
    r['dating_assessments'].append(date(-450,-350,'Allchin/Coningham 1995 radiocarbon placement, recovered second-hand', 'Allchin/Coningham 1995 p. 176, through review and indexed book text',note='Original chapter not opened. Record extends into the fifth century; no numerical lab/sample table recovered.'))
    r['source_ids'].append('allchin-coningham1995');r['source_locations'].append('Allchin/Coningham 1995 p. 176 (second-hand)')
    r=rr['mehrgarh-failed-firing'];r['count_basis']='Quivron 1980 p. 275 reports 142 jars on about 24 m². Miller 1997 pp. 46–47 describes about 140 jars and estimates an original load near 200. These are batch denominators, not marked-object counts.'
    r['dating_assessments']=[date(-3000,-2700,'Miller Period VI approximate phase and before-2700 failed firing', 'Miller 1997 pp. 46–47, 52',note='Unselected approximate phase envelope, replacing the erroneous after-2700 century bin.'),date(None,None,'Quivron printed Period IV versus Miller Period VI', 'Quivron p. 275; Miller pp. 46–47',grade='D',note='Phase labels remain distinct; no forced reconciliation.')]
    rr['nausharo-kiln-II']['limitations']+=' Miller p. 56 also places Lal Shah updraft kilns in Mehrgarh VIIC, 2700–2500 BCE; this overlaps the reported mark peak/decline and is not a verified single replacement event.'
    rr['mehrgarh-nausharo1997']['source_locations']=['Coningham 2002 pp. 93–94, citing Quivron 1997 pp. 45, 53, 55, 61 second-hand; Quivron chapter not opened']
    rr['mehrgarh-pottery1980']['limitations']+=' Quivron p. 279 compares about twenty of 396 Harappan characters with incised marks, not pottery shapes.'
    r=rr['rehman-dheri-stratified'];r['repertoire_size']=None;r['repertoire_basis']='94 main catalogue numbers with lettered variants are not a normalized sign repertoire.'
    r['limitations']+=' Printed phase counts 7+12+14+19+111=163 versus 190; 41−14=27 and replacing 14 by 41 yields 190. A transposition is plausible, not an authenticated emendation. Build/recount the object-by-phase matrix from registrations before using 41.'
    r=rr['rehman-dheri-pendant54'];r['dating_assessments']=[d for d in r['dating_assessments'] if 'PeriodII' not in d['method'] and 'Period II' not in d['method']]
    r['dating_assessments'][1]['note']='BIV/25 Layer 6, Level 19 belongs to IA in Introduction Table 1 and p. vii; earlier prose says IB. Remove the erroneous Period II trench correlation. No selected narrow interval until IA/IB reconciliation.'
    r['limitations']='Called an ivory button seal by Frenez 2018 p. 171 n. 5 and Kenoyer/Meadow 2010 p. liv (Rhd-1); bone seal in the 1995 catalogue. IA/IB assignments differ; the former Period II alternative was a misread trench correlation. Figure-to-caption identity is supported by Frenez\'s own description; northwestern Baluchistan remains geographically wrong.'
    r['source_ids'] += ['frenez2018','kenoyer-meadow2010'];r['source_locations'].append('Frenez 2018 p. 171 n. 5; Kenoyer and Meadow 2010 p. liv; CISI 2 p. 352 Rhd-1')
    for rid in ['harappa-ravi-bone1521','harappa-kot-diji-elephant1533']:
        rr[rid]['count_unit']='motif-bearing specimen without surviving script';rr[rid]['limitations']+=' Counted as motif-bearing, not an authenticated inscription.'
    rr['harappa-ravi-bone1521']['count_basis']='One geometric bone seal fragment H-1521. H98-3503/8514-07 is a probable concordance from the unique fragment, not a printed concordance.'
    # New contexts: mark absence and unknown sample joins stay visible.
    tn=['rajan-sivanantham2026-I'];tn2=['rajan-sivanantham2026-II']
    rows.extend([
        newrow('daimabad-V','Daimabad Phase V Jorwe marked pottery and cylinder seal',['Daimabad'],'Deccan',['sali1986'],['Sali pp. 206, 208, 211, 399–400, 508'],[
            date(-1400,-1000,'Excavated Phase V with conventional Jorwe bracket and old radiocarbon comparisons','Sali pp. 206, 208, 211',grade='B',selected=True,labs=['BS-179','PRL-656','BS-178'],
                measurement={'reported_conventional_bce':[1100,1100,1090]},note='Sali calls the three dates stratigraphically inconsistent but within the bracket; not modern calibrated dates.'),
            date(-1640,-1110,'Separate old MASCA correction envelope','Sali p. 211',grade='B',note='Alternatives 1600/1640–1110/1140; unselected and not averaged.')],
            ['pottery marks from Kiln 1 and house 38 floor 2','terracotta cylinder seal, house 38 floor 4'],images=True,limitation='Count unknown; the seal has a chariot motif, no reported script. Illustrated mark numbers are not a complete specimen census.'),
        newrow('thulukkarpatti-I','Thulukkarpatti Iron Age Period I graffiti',['Thulukkarpatti'],'South India',tn,['Volume I pp. 196, 198, 201, 226'],[
            date(-900,-700,'Iron Age cultural phase based on ceramics and pre-Brahmi levels','Volume I p. 196',selected=True),
            date(-1150,-950,'Tentative comparison with Sivagalai and Adichanallur','Volume I p. 198',note='Explicitly tentative alternative; not a laboratory date.')],count=4797,kind='exact, temporally unaligned',
            basis='4,797 documented site-wide graffiti sherds in Table 3.1; 4,820 collected in p. 201 narrative. Concentrated pre-Brahmi, but Period I count unavailable; exclude from object bounds.',images=True),
        newrow('sivagalai-II','Sivagalai cultural Period II (Iron Age)',['Sivagalai'],'South India',tn,['Volume I pp. 192, 194'],[
            date(-1200,-700,'Published cultural period; possible habitation marks not allocated among periods','Volume I p. 192',selected=True)],
            basis='150 habitation sherds belong to the parent row; no Period II count assigned.',limitation='C/low cultural possible coverage only; no registered mark/sample join. Parent habitation row has no usable interval, so the 150 are not duplicated.'),
        newrow('sivagalai-A2-Urn-3','Sivagalai A2-Urn-3 dated paddy context without graffiti',['Sivagalai'],'South India',tn,['Volume I Table 2.1 pp. 181, 183; p. 295'],[
            date(None,None,'Reported calibrated point for urn paddy','Volume I p. 183',grade='D',labs=['Beta-600726'],measurement={'bp':2950,'sigma':30,'reported_calibrated_point_bce':1155},note='No full calendar interval; no graffiti on opened urn grave goods.'),
            date(None,None,'Separate OSL point','Volume I p. 183',grade='D',measurement={'reported_osl_bce':1284},note='Not merged with AMS.')],count=0,kind='exact',basis='Scope-specific absence on opened urn grave goods, p. 295.',additive=False),
        newrow('adichanallur-urn-burials','Adichanallur dated urn burial contexts without graffiti',['Adichanallur'],'South India',tn,['Volume I pp. 22, 27 Fig. 2.13; p. 295'],[
            date(None,None,'AMS sample-point labels from urn-burial chart; mark absence','Volume I p. 27 Fig. 2.13',grade='D',measurement={'reported_calibrated_point_bce':[885,908,1052,1257,1384,1810]},note='Samples differ; no artificial continuous bracket or laboratory identifiers inferred.')],count=0,kind='exact',basis='No graffiti on opened urn grave goods, p. 295; 933 habitation sherds p. 27 belong to a different context.',additive=False),
        newrow('adichanallur-habitation','Adichanallur Early Historic habitation graffiti',['Adichanallur'],'South India',tn,['Volume I pp. 22, 27'],[
            date(-467,-201,'Published Early Historic AMS phase envelope; individual mark joins unresolved','Volume I p. 22',selected=True,note='Six non-contaminated Early Historic dates among 18 accepted samples. Separate from unmarked urn burials.')],count=933,kind='exact, temporally unaligned',basis='933 habitation graffiti sherds p. 27; no specimen distribution within the dated phase.',images=True),
        newrow('kodumanal-MEG-19','Kodumanal MEG-19 burial date and graffiti association claim',['Kodumanal'],'South India',tn,['Volume I pp. 101–102'],[
            date(None,None,'Burial AMS age; only a calibrated midpoint recovered','Volume I p. 102',measurement={'bp':2718,'sigma':30,'printed_conventional_bce':978,'reported_calibrated_midpoint_bce':863},note='978 is the printed label; BP minus 1950 would be 768, so the source conversion conflicts. No full calibrated range or lab identifier recovered.')],
            additive=False,limitation='p. 101 says every burial pottery carries graffiti, but MEG-19 objects are not itemized. Do not invent a century interval from a midpoint.'),
        newrow('korkai-KRK-4','Korkai KRK-4 hearth date and marked trench contexts',['Korkai'],'South India',tn,['Volume I pp. 107, 109'],[
            date(None,None,'Uncalibrated hearth charcoal age, rejected in original cultural assignment','Volume I p. 109',measurement={'bp':2755,'sigma':95,'printed_conventional_bce':785,'depth_m':2.69},note='No laboratory number, calibration or marked-shard feature association recovered.')],additive=False,
            limitation='Graffiti and eight Tamil-Brahmi sherds occur in KRK-4–6, but not explicitly in the dated hearth. Site-wide 422 documented graffiti cannot be allocated to KRK-4.'),
        newrow('kongu-Iron-Age','Kongu regional ceramic sequence with graffiti',['Karur','Kodumanal','Perur','Boluvampatti','Nedungur','Porunthal'],'South India',tn2,['Volume II p. 1162'],[
            date(-1500,-700,'Regional thin black-and-red ware cultural phase with graffiti','Volume II p. 1162',note='Non-additive regional synthesis overlaps site rows; no independent specimen corpus.')],additive=False,
            limitation='A regional sequence is not an independently dated assemblage; held as a non-additive comparator.')])
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Use a fresh output directory.')
    original={name:read(OLD/name) for name in ['evidence-table.json','sources.json','continuity-claims.json','lecture-claim-audit.json','contact-items.json','dating-details.json','visual-checks.json']}
    data=copy.deepcopy(original)
    data['evidence-table.json']['rows']=rows_corrected(tidy(data['evidence-table.json']['rows']))
    from correct_metadata import correct_sources, correct_claims, correct_audits
    data['sources.json']['sources']=correct_sources(tidy(data['sources.json']['sources']))
    data['continuity-claims.json']['claims']=correct_claims(tidy(data['continuity-claims.json']['claims']))
    correct_audits(data)
    data = {name: tidy(value) for name, value in data.items()}
    out.mkdir(parents=True)
    for name,value in data.items():
        value['status']='Exploratory';value['amendment_date']='2026-10-07 review correction';write(out/name,value)
    rows=data['evidence-table.json']['rows'];fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'evidence-table.csv').open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False)if isinstance(v,(list,dict))else ''if v is None else v for k,v in r.items()})
    changes=[]
    for name in original:
        old=original[name];new=data[name]
        def diff(a,b,path):
            if a==b:return
            if isinstance(a,dict)and isinstance(b,dict):
                for k in sorted(set(a)|set(b)):diff(a.get(k),b.get(k),path+'/'+k)
            elif isinstance(a,list)and isinstance(b,list)and all(isinstance(x,dict)and'id'in x for x in a+b):
                aa={x['id']:x for x in a};bb={x['id']:x for x in b}
                for k in sorted(set(aa)|set(bb)):diff(aa.get(k),bb.get(k),path+'/'+k)
            else:changes.append(dict(file=name,field=path,before=a,after=b))
        diff(old,new,'')
    write(out/'correction-log.json',dict(status='Exploratory',review='experiments/2026-10-06-backward-chronology/REVIEW.md',changes=changes))
    write(out/'build-verification.json',dict(status='Verified computation',documentary_status='Exploratory',
        rows=len(rows),source_records=len(data['sources.json']['sources']),claims=len(data['continuity-claims.json']['claims']),
        changed_fields=len(changes),parent_sha256={n:digest(OLD/n)for n in original},
        added_row_ids=[r['id']for r in rows if r['id']not in {x['id']for x in original['evidence-table.json']['rows']}]))
    print(json.dumps({'rows':len(rows),'changes':len(changes),'output':str(out)}))

if __name__=='__main__':main()
