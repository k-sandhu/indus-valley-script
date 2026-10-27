"""Serialize source-defined architectural cases; these are not independent trials."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=[]

def case(number,town,part,before,after,panels,sources,locators,observations,connectivity,dating,missing,cluster,kind='architectural sequence'):
    CASES.append({
        'id':f'PW-E{number:02d}','town':town,'record_class':kind,'named_architectural_part':part,
        'phase_before':before,'phase_after':after,'panel_ids':panels,'source_ids':sources,'source_locators':locators,
        'observations':observations,'connectivity_evidence':connectivity,'dating_basis':dating,
        'missing_fields':missing,'independence_cluster':cluster,
        'complete_common_exposure_window':False,'comparable_internal_partition_inventory':False,
        'C0017_P1_eligible':False,'C0017_P1_missing_reason':'No complete comparable inventory of shared routes and internal partitions through a matched phase pair.',
        'C0017_P2_eligible':False,'C0017_P2_missing_reason':'Repair is not directly joined to independently coded local components across a complete usable connection.',
        'C0017_P3_eligible':False,'C0017_P3_missing_reason':'No independent date resolves this repair or access-change event for a prediction against distance and engineering.',
        'C0018_eligible':False,'C0018_missing_reason':'Architectural audit does not establish a primary-use documentary deposit, custody change and matched recovery denominator.',
        'C0019_eligible':False,'C0019_missing_reason':'No independently discriminating physical evidence of shared work is established by this architectural record.',
        'new_documentary_overlay_received':False,'fresh_confirmation':False
    })
    return CASES[-1]

case(1,'harappa','Area C north-south street NS2355','legacy Period 2','Period 3 and later upper street exposure',
    ['PW-P01','PW-P02'],['W-S04'],['p.49 Fig.4.12, PDF index22','p.50, PDF index23','p.54 Fig.4.16, PDF index27','p.56, PDF index29'],
    [
      {'status':'source excavation observation','assertion':'Natural-soil cart-track depressions were exposed in a narrow Period 2 window; the later north-south street lay directly above the earlier street.'},
      {'status':'registered location relation','assertion':'Independent grid controls locate the earlier cart-track set within the upper street corridor. PW-R01 uses six controls and two held-out crosses on each drawing.'},
      {'status':'source plan observation','assertion':'The upper plan labels encroachment paving, an encroachment drain, ghost walls and mud-brick foundations. It combines street levels and a house exposure.'}
    ],
    'The source describes a continuing corridor and later street-level encroachment. The pair alone does not establish uninterrupted access throughout every intervening level.',
    'Source relative stratigraphy; no date sample independently resolves the cart-track-to-upper-street transition. The 1991 period namespace is retained.',
    {'matched_internal_walls':'The early natural-soil window supplies no comparable internal-wall population.','phase_separation':'The upper drawing combines several exposed street levels.','source_survey_error':'Unknown despite small grid-fit residuals.'},
    'HAR-AreaC')
CASES[-1]['registration_id']='PW-R01'
CASES[-1]['common_geometric_window_metres']={'easting':[2355.30,2357.00],'northing':[1015.40,1019.70]}

case(2,'harappa','Area C southern wall, gateway and drains','Period 3A decay','Period 3B rebuilding',
    ['PW-P03','PW-P04'],['W-S04'],['p.52 Fig.4.14, PDF index25','p.53 Fig.4.15, PDF index26','pp.55-56, PDF indices28-29'],
    [
      {'status':'source excavation observation','assertion':'Clogged drains and street sewage accompanied decay of the Period 3A wall and gateway.'},
      {'status':'source reconstruction from excavation','assertion':'The author attributes new drains, houses and rebuilding of the southern wall and gateway to Period 3B.'},
      {'status':'published dimension','assertion':'The rebuilt wall was traced for 73 m; reported width varied from 5.4 to 11 m, with uncertainty over repairs or towers in wider portions.'},
      {'status':'source section observation','assertion':'Wall [40] lies below wall [30]; the figure retains unexcavated regions.'}
    ],
    'The drain first ceased functioning and was then replaced. Persistent position alone would hide this interruption.',
    'Source construction sequence and subperiod attribution; no directly linked independent repair date.',
    {'matched_phase_plans':'The overall drawing superimposes gateway and wall stages.','repair_date':'No independent sample tied to the rebuilding.'},
    'HAR-AreaC')

case(3,'harappa','Area C formerly 5 m north-south street','Period 3B','Period 3C',
    ['PW-P02','PW-P03'],['W-S04'],['p.50, PDF index23','p.54 Fig.4.16, PDF index27','p.56, PDF index29'],
    [{'status':'source excavation observation','assertion':'Brick pavings and drains encroached on a formerly 5 m wide street during Period 3C; upper levels were affected by brick robbing.'}],
    'Narrowing is source-supported; the remaining passable width and its continuity through all 3C rebuilding are unreported.',
    'Source relative sequence and Period 3C attribution.',
    {'later_clear_width':'Not given in the report and not isolated as one dated state in the composite plan.','preservation':'Upper walls have been robbed.'},
    'HAR-AreaC')

e=case(4,'harappa','Extension of Mound E perimeter to enclose Mound ET','occupation and hearths below wall [15]','initial enclosure and gateway',
    ['PW-P05'],['PW-HAR1997'],['pp.142-143 Table1, PDF indices3-4','pp.143-144, PDF indices4-5','p.145 Fig.3, PDF index6'],
    [
      {'status':'source stratigraphic observation','assertion':'Wall [15] of the Mound ET extension overlies hearth deposits; the gateway joined the existing Mound E perimeter to the new enclosure.'},
      {'status':'source chronological interpretation','assertion':'The authors infer initial enclosure sometime after ca.2470 B.C. from A-8047 and A-8048, while noting the later A-8049 result from a related context.'}
    ],
    'Initial enclosure creates a named gate connection; it is distinct from the later drain rerouting through that gate.',
    'Reported radiocarbon determinations from below wall [15] provide a terminus post quem for initial enclosure, subject to source outlier treatment. They do not date a later repair.',
    {'sample_material':'Table1 does not specify material for these three rows.','modern_calibration':'No recalibration is performed.','precise_construction_date':'Below-wall hearth dates are earlier bounds, not direct construction dates.'},
    'HAR-MoundET-enclosure')
e['independent_date_evidence']=[
 {'laboratory_id':'A-8047','additional_laboratory_id':'AA 16461','sample_identity':'H94/5383 [64]','context':'Trench22, Hearth64, below wall15','determination_bp':3965,'plus_bp':55,'minus_bp':55,'bp_convention':'5568 half-life, as printed','reported_calibrated_bc':'2558 (2465) 2404','reported_interval_convention':'+1-sigma (intercept[s]) -1-sigma, as printed','sample_material':None,'source_flag':None},
 {'laboratory_id':'A-8048','sample_identity':'H94/5384 [66]','context':'Trench22, Hearth64, below wall15','determination_bp':3975,'plus_bp':110,'minus_bp':105,'bp_convention':'5568 half-life, as printed','reported_calibrated_bc':'2589 (2467) 2320','reported_interval_convention':'+1-sigma (intercept[s]) -1-sigma, as printed','sample_material':None,'source_flag':None},
 {'laboratory_id':'A-8049','sample_identity':'H94/5385 [67]','context':'Trench22, Hearth68, below wall15; same stratigraphic context as A-8047/A-8048 according to source','determination_bp':3785,'plus_bp':145,'minus_bp':140,'bp_convention':'5568 half-life, as printed','reported_calibrated_bc':'2457 (2195, 2152, 2149) 1976','reported_interval_convention':'+1-sigma (intercept[s]) -1-sigma, as printed','sample_material':None,'source_flag':'single asterisk: source says these dates seem somewhat aberrant'}
]

case(5,'harappa','Mound ET gateway and successive western drains','gateway entrance and western drain sequence','late 3C central corbelled drain and crossing street',
    ['PW-P05'],['PW-HAR1997'],['pp.143-146, PDF indices4-7','p.145 Fig.3, PDF index6'],
    [
      {'status':'source construction observation','assertion':'Brick bonding and construction discontinuities define three major gateway building stages.'},
      {'status':'source excavation observation','assertion':'Three earlier drains [116], [144] and [50] ran near the east face of the Mound E wall; the last became clogged with silty refuse.'},
      {'status':'source excavation observation','assertion':'A later central drain [51] and corbelled culvert partly blocked the earlier gateway; an east-west street crossed above it and linked streets on either side of the channel.'},
      {'status':'published dimensions','assertion':'The earlier gateway street is reported as 2.6 m wide. The later covered culvert is reported as 6.5 m long and 0.60 m wide internally, with internal height 1.62/1.66 m and a 0.17 m fall over 6.5 m.'}
    ],
    'Shared drainage was renewed while the gate route changed. The older north-south gate opening and later east-west crossing must be coded separately.',
    'Construction sequence and ceramics identify early and late 3C stages. No independent sample dates the drain rerouting; the enclosure hearth dates belong to an earlier event.',
    {'dated_before_after_plans':'One composite drawing; the individual architectural states are not separately mapped in full.','independent_repair_date':'Unknown.'},
    'HAR-MoundET-gateway')

case(6,'harappa','Wall [296], perimeter [250], streets and Room92','earlier occupation and prepared surface; Period3B architecture','late 3C channel cut',
    ['PW-P06','PW-P07','PW-P14'],['PW-HAR1997','HARP-MOUND-E-ET'],['pp.151-153, PDF indices12-14','p.153 Fig.6, PDF index14','Harappa Excavations1995-2001 slide72'],
    [
      {'status':'source stratigraphic observation','assertion':'Wall [296] was built parallel to perimeter wall [250] after a compacted surface was prepared. Street and dumped deposits later buried both walls.'},
      {'status':'source excavation observation','assertion':'A late 3C drain cut the western part of the Room92 block and destroyed earlier architecture.'},
      {'status':'source interpretation with unresolved join','assertion':'The report proposes that this channel could connect to the gateway culvert farther south; no excavated continuous link is demonstrated.'}
    ],
    'The local channel cut is observed. Connectivity to the gateway remains conditional and is not converted into an observed town-wide drain.',
    'Wall [296] is placed near the beginning of Period3B by source sequence and attribution. Room92 hearth dates concern room occupation; they do not directly date wall [296] or the late channel cut.',
    {'gateway_connection':'Intervening physical connection is unverified.','construction_sample':'No sample directly dates wall [296] or the later channel cut.','common_exposure':'Plan and section do not supply two complete partition inventories.'},
    'HAR-MoundET-eastwall')

case(7,'harappa','Trenches54,39 and11 source coverage','several Period2/3 contexts','later walls, robbing and excavation windows',
    ['PW-P08','PW-P09','PW-P10','PW-P11','PW-P12','PW-P13'],['HARP-TR54-TOP','HARP-TR54-DETAIL','HARP-TR54-WEST-SECTION','HARP-TR39-P2','HARP-TR39-P3','HARP-INSIDE-WALL250'],
    ['Harappa2000-2001 slides46,48,83','Harappa Excavations1995-2001 slides26,63,85'],
    [
      {'status':'source coverage observation','assertion':'The Trench54 top plan combines Period2,3A,3B and3C areas and identifies robbed brick walls, wall voids and a deeper southern extension.'},
      {'status':'source coverage observation','assertion':'The two Trench39 drawings have different extents. The Period2 drawing includes a later drain for reference; the later drawing combines 3B drain [8], 3C wall [50] and later fragments.'},
      {'status':'source coverage observation','assertion':'The Trench11 plan shows superimposed 3C levels; 1999 and2001 identify excavation seasons.'},
      {'status':'measurement check','assertion':'PW-M02 reads the source-labelled 2.18 m robber-trench width as 2.167 m with a conditional reading bound of 2.075-2.263 m.'}
    ],
    'No complete before-and-after access network is supplied by these drawings.',
    'Source relative phase labels and excavation-season labels are kept in separate fields.',
    {'full_pair':'No two complete comparable exposures were found.','lost_wall_vs_unobserved':'Robbing and partial exposure prevent blank areas from being coded as ancient absence.'},
    'HAR-source-coverage','source eligibility case')

case(8,'dholavira','Castle southern defence','Stage I basal wall','Stage II and III additions',
    ['PW-P15'],['W-S01'],['pp.95-99, PDF indices111-115','p.96 Fig.5.1, PDF index112'],
    [
      {'status':'published section dimensions','assertion':'The source describes an 11 m basal wall in Stage I, a 2.8 m inward addition in Stage II and a 4.5 m addition in Stage III.'},
      {'status':'source schematic sequence','assertion':'Fig.5.1 orders wall additions and deposits across seven stages and marks unexcavated regions and collapsed masonry.'}
    ],
    'Successive additions retain the earlier defence as part of a thicker structure. This section does not define a circulation route or an internal-wall denominator.',
    'Source stratigraphic stages; no direct independent repair dates from these panels.',
    {'new_metric_dimension':'Figure is explicitly schematic; source dimensions are transcribed, not remeasured.','whole_boundary_survival':'The selected southern section cannot stand for the entire enclosure.'},
    'DHO-Castle-defence')

case(9,'dholavira','Castle East Gate','earlier gate passage and terrace','Stage V/VI changes around the gate; later blockings phase unknown',
    ['PW-P16'],['W-S01'],['pp.115-116, PDF indices131-132','p.116 Fig.6.9, PDF index132'],
    [
      {'status':'source plan observation','assertion':'Fig.6.9 labels later blocking at both ends of the passage without assigning each blocking to a stage.'},
      {'status':'source excavation observation','assertion':'Stage V domestic or industrial buildings occupied the terrace, and Stage VI access steps were added outside the gate. The report says the earlier approach remains concealed by later structures.'},
      {'status':'local drawing measurement','assertion':'PW-M03 reads one interior clear section as 2.518 m, with a conditional endpoint-reading bound of 2.270-2.790 m.'}
    ],
    'The local clear section is present in the composite. The two blocked ends prevent that line from certifying open passage through the gate in every stage.',
    'Source stages for surrounding buildings and steps; the drawn blockings have no exact stage key or independent repair date.',
    {'blocking_stage':'The plan labels the blockings only as later.','open_access_date':'Not determined for each building stage.','earlier_approach':'Concealed under later structures.'},
    'DHO-Castle-EastGate')

case(10,'dholavira','Castle North Gate and ceremonial approach','Stage III gate, as interpreted by source','continued use through VI; approach narrowing in V or VI',
    ['PW-P17'],['W-S01'],['pp.119-122, PDF indices135-138','p.121 Fig.6.19, PDF index137'],
    [
      {'status':'source plan observation','assertion':'The North Gate plan combines central passage, flanking chambers, earlier wall plaster and Late Harappan structures. Its compass points north down.'},
      {'status':'source phase interpretation','assertion':'The report describes the gates other than the south gate as in use from Stage III to VI. It attributes narrowing of a 9 m ceremonial approach to Stage V or VI.'},
      {'status':'local drawing measurement','assertion':'PW-M04 reads the central passage at one section as 2.704 m, with a conditional bound of 2.240-3.224 m from the coarse source image.'}
    ],
    'Gate use is the source interpretation; the approach changed. The drawing alone does not establish the passage condition in every stage.',
    'Source relative stages; the approach change remains V-or-VI, with no independently dated repair sample.',
    {'exact_narrowing_stage':'V or VI unresolved.','display_primary_use_join':'The selected plan gives neither an original mounting nor a primary-use deposit relationship for the display.','resolution':'Source crop419 by526 pixels limits endpoint reading.'},
    'DHO-Castle-NorthGate')

case(11,'dholavira','Lower Town trench15x24 north-south street','earlier 5.25 m street','Stage V wall encroachment',
    ['PW-P19'],['W-S01'],['pp.131-137, PDF indices147-153','p.133 Fig.6.26, PDF index149','p.137, PDF index153'],
    [
      {'status':'source excavation observation','assertion':'In trench15x24, a Stage V wall encroached on an earlier 5.25 m wide north-south street.'},
      {'status':'source coverage observation','assertion':'Most Lower Town excavation reached only about1.5 m and one or two phases. Only trenches15x24,35x24 and25x83 reached natural soil.'},
      {'status':'source limitation','assertion':'The arterial-street photograph has no surveyed connection to trench15x24; it cannot identify the particular encroaching wall.'}
    ],
    'Street width decreased at the named trench. Remaining width and whether passage stayed open are unreported.',
    'Source Stage V attribution; no independently dated repair sample.',
    {'matching_plan':'No phase-keyed plan of the named trench was located.','later_width':'Not reported.','photograph_join':'No surveyed link joins Fig.6.26 to trench15x24.'},
    'DHO-LowerTown-15x24')

case(12,'dholavira','Castle well, tanks, channels and steps','well in use by Stage IV; first construction unknown','use into Stage VI; repeated step changes unkeyed',
    ['PW-P20'],['W-S01'],['p.138, PDF index154','pp.142-144, PDF indices158-160','p.144 Fig.6.32, PDF index160'],
    [
      {'status':'source plan observation','assertion':'Fig.6.32 shows the well, two tanks, connecting channels and dashed continuations without a phase legend. North points down.'},
      {'status':'source excavation observation','assertion':'The well was used from Stage IV into VI; the source leaves its initial construction unresolved because the vicinity has poor deep stratigraphy. Access steps were rebuilt as the adjacent broadway rose.'},
      {'status':'published dimensions','assertion':'The distorted opening is reported as 4.00 m east-west and4.25 m north-south. The source proposes4.125 m as an original diameter.'},
      {'status':'local drawing measurement','assertion':'PW-M05 reads the horizontal opening as3.797 m with a conditional endpoint-reading bound of3.403-4.208 m.'}
    ],
    'A well-to-tank arrangement is drawn; dashed continuations and unassigned repair phases prevent a dated connection history for each channel.',
    'Source Stage IV-VI attribution and relative step rebuilding. No independently dated channel or step repair.',
    {'initial_construction':'Deep investigation outside the well is identified by the source as necessary.','repair_stage':'Individual channel and step changes are not keyed.','primary_function':'Basin use is an archaeological interpretation, not established by the line measurement.'},
    'DHO-Castle-water')

case(13,'lothal','Town blocks, houses and drainage','Phase II rebuilding after flood','Phase III rebuilding',
    [],['W-S02'],['pp.85-87, PDF indices95-97'],
    [
      {'status':'source reconstruction from excavation','assertion':'The author describes coordinated raising of platforms after a flood and repeated Phase II-III rebuilding that retained the block and house layout with little room subdivision.'},
      {'status':'source coverage limitation','assertion':'Phase I layout remains poorly known because flood mud and limited excavation obscure the earlier town.'},
      {'status':'source reporting conflict','assertion':'Pages86 and87 reverse the compass directions attributed to Streets1 and6. Neither bearing is selected.'}
    ],
    'Reported retention is a textual claim awaiting the missing matched phase plans.',
    'Source phase sequence and flood attribution; no independently dated individual repair in the inspected plans.',
    {'plan_pair':'Original plate volume and whole-town street plateXXXVIII are absent from the held VolumeI scan.','bearing':'Conflicting source assignments for Streets1/6.','PhaseI_plan':'Not recovered well enough to reconstruct.'},
    'LOT-town-plan')

case(14,'lothal','Phase IV street encroachment and Block B','reported II-III order','Phase IV, including IVa houses171/172',
    ['PW-P21','PW-P22'],['W-S02'],['p.87, PDF index97','p.101 Fig.16, PDF index111','p.109 Fig.17, PDF index119'],
    [
      {'status':'source excavation observation','assertion':'The report describes encroachments in Phase IV after earlier efforts to keep the alignment. Nine streets and twelve lanes are exposed-report counts with no full contemporaneous denominator.'},
      {'status':'source plan observation','assertion':'Fig.17 provides a phase-labelled plan of houses171.IVa and172.IVa, Streets2/3, a passage, entrances, a verandah, drain and soakage jar.'},
      {'status':'local drawing measurements','assertion':'PW-M06 reads a passage as1.123 m[0.989,1.261]; PW-M07 reads the northern entrance of172.IVa as2.207 m[2.057,2.363]. Brackets are conditional endpoint-reading bounds.'},
      {'status':'source illustration limitation','assertion':'Fig.16 combines isometric, section and plan views of public drain15A. Its sockets and groove are interpreted as screen or door fittings; no dated before/after pair is supplied.'}
    ],
    'Phase IV local openings are measurable. Their existence does not determine the amount of prior encroachment or a change of institutional custody.',
    'Source Phase IV labels in Fig.17. Drain15A has no phase-separated drawing in Fig.16.',
    {'earlier_BlockB_plan':'Not present in the held scan.','encroachment_width_change':'No registered earlier/later bank pair.','denominator':'No town-wide contemporaneous route or structure inventory.'},
    'LOT-town-plan')

case(15,'lothal','Large basin inlet and western drains, called dock by source','Phase IIIb damage and earlier inlet arrangement','Phase IV eastern inlet and western drain closure',
    ['PW-P23'],['W-S02'],['p.124 Fig.19, PDF index134','pp.125-126, PDF indices135-136'],
    [
      {'status':'source isometric reconstruction','assertion':'Fig.19 labels first and second inlet arrangements, basin, embankment, spillway and western drain.'},
      {'status':'source sequence interpretation','assertion':'The report attributes an eastern inlet replacing the earlier arrangement and closure of western drains to rebuilding after Phase IIIb damage.'}
    ],
    'The source supports ordered hydraulic rerouting. The isometric reconstruction does not supply a measured plan-survival proportion.',
    'Source relative Phase IIIb-to-IV sequence; no independent repair date established here.',
    {'orthogonal_plan_pair':'Only an isometric reconstruction is available in the selected figure.','function':'The title calls the basin a dock; this audit does not resolve that functional interpretation.','source_engineering_error':'Original reconstruction error unquantified.'},
    'LOT-basin-inlets')

def main():
    # Restore ordinary spacing without altering catalogue, trench or phase identifiers.
    import re
    def clean(value):
        if isinstance(value,list):return [clean(v) for v in value]
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
        if not isinstance(value,str):return value
        t=value
        for a,b in [('about1.5','about 1.5'),('as3.797','as 3.797'),('of3.403','of 3.403'),('as1.123','as 1.123'),('as2.207','as 2.207'),('as2.167','as 2.167'),('and4.25','and 4.25'),('proposes4.125','proposes 4.125')]:
            t=t.replace(a,b)
        t=re.sub(r'\b(Period|Periods|Stage|Phase|Fig\.|Street|Streets|Room|Hearth|Trench|Trenches|Table|Volume|drain|wall|trenches|houses|Pages|and|slide|slides)(?=\d)',r'\1 ',t)
        t=re.sub(r'(?<=[a-z])(?=\d{4}\b)', ' ',t)
        t=re.sub(r',(?=\d)', ', ',t)
        t=re.sub(r'\b(p|pp)\.(?=\d)',r'\1. ',t)
        return t
    CASES[:]=clean(CASES)
    payload={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),'status_class':'exploratory','episodes':CASES,
      'counting_rule':'Fifteen source-defined cases include one source-eligibility case. They are not fifteen independent repair episodes, and repeated views retain their cluster. No case is eligible for the registered P1 contrast.',
      'module_architecture_frozen_before_new_documentary_overlay':True,
      'authors':[{'model':'GPT-6 family; exact serving variant unknown','harness':'Codex desktop','agent':'western_towns'}]}
    (HERE/'episodes.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'case_records':len(CASES),'source_eligibility_cases':sum(e['record_class']=='source eligibility case' for e in CASES),'P1_eligible':sum(e['C0017_P1_eligible'] for e in CASES)}))

if __name__=='__main__':main()
