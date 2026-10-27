"""Source-specific date evidence. No recalibration, pooled axis or inferred repair dates."""
from pathlib import Path
import collections, hashlib, json, re
HERE=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/contexts')
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    records=[]
    def add(id,town,lab,material,provenience,phase,determination,calibration,source,page,index,relationship,reason,**extra):
        records.append(dict(id=id,town=town,lab_id=lab,sample_material=material,provenience_as_reported=provenience,
          phase_as_reported=phase,determination_as_reported=determination,calibration_as_reported=calibration,
          source_id=source,locator={'printed_page':page,'pdf_index':index,'pdf_page':index+1},
          relation_to_construction=relationship,object_use_join_established=False,usable_as_specific_repair_date=False,
          missing_or_rejection_reason=reason,**extra))
    farm='''15051|Central Tr.1D5|2|3925±25|2476–2338BC(93.4%);2322–2309BC(2.0%)
15052|Central Tr.1D5|2|3975±25|2571–2513BC(50.3%);2503–2462BC(45.1%)
15054|Central Tr.1D5|2|3905±25|2469–2335BC(89.1%);2324–2301BC(6.3%)
15048|Central Tr.1D5|3|3900±25|2469–2335BC(88.3%);2324–2301BC(7.1%)
15049|Central Tr.1D5|3|3905±25|2470–2332BC(86.9%);2326–2299BC(8.5%)
15050|Central Tr.1D5|3|3905±25|2469–2335BC(89.1%);2324–2301BC(6.3%)
16340|Central Tr.1C11|1|3850±20|2459–2417BC(10.4%);2410–2273BC(68.8%);2256–2207BC(16.2%)
16341|Central Tr.1C11|1|3880±20|2461–2296BC(95.4%)
16342|Central Tr.1C11|1|3885±20|2462–2299BC(95.4%)
16343|Central Tr.1C11|1|3940±20|2560–2536BC(4.2%);2491–2344BC(91.2%)
16344|Central Tr.1C11|1|3895±20|2466–2332BC(85.9%);2326–2299BC(9.5%)
16349|Central Tr.1C11|1|3905±20|2470–2335BC(90.5%);2324–2307BC(4.9%)
16348|Central Tr.1C11|2|3925±20|2477–2342BC(95.4%)
12424|Central Tr.1A3 / Pit no.1; sample08-003|5|3860±25|2461–2280BC(87.8%);2251–2230BC(5.7%);2220–2211BC(1.9%)
12425|Central Tr.1C1 &1C2; sample08-004|5|3845±20|2458–2418BC(8.0%);2407–2376BC(9.9%);2351–2205BC(77.5%)
15057|East Tr.2XD3-SW|4|4035±25|2621–2476BC(95.4%)
15056|North Ex. Tr.2D9-SE|1|3945±25|2564–2533BC(9.7%);2495–2395BC(68.2%);2385–2346BC(17.5%)
16350|North Ex. Tr.2D9|2|3870±20|2463–2286BC(94.9%);2247–2244BC(0.5%)
9491|North Area Tr.3; sample07-009|3|3930±35|2560–2536BC(3.7%);2492–2298BC(91.7%)
9492|North Area Tr.3; sample07-010|3|3870±35|2467–2278BC(88.3%);2251–2229BC(5.0%);2221–2210BC(2.1%)
9493|North Area Tr.3; sample07-011|2|3940±35|2566–2525BC(9.7%);2497–2335BC(82.1%);2324–2301BC(3.6%)
15046|Central Tr.1C7|Gupta|1485±20|AD545–624(95.4%)
15047|Central Tr.1C8-NW|Gupta|1515±20|AD442–484(7.1%);AD533–606(88.3%)
15055|Central Tr.1D9-SE,SW|Gupta|1450±20|AD575–648(95.4%)
12422|Central Tr.1E1 / St.no.3N; sample08-001|Gupta|1390±20|AD616–666(95.4%)
12423|Central Tr.1E3 / St.no.30; sample08-002|Late Medieval|205±20|AD1651–1682(26.9%);AD1738–1751(2.7%);AD1762–1803(45.1%);AD1937–1955(20.7%)'''
    fp=json.loads((RAW/'east-shinde2011.pages.json').read_text(encoding='utf8'))
    full=fp[846]['text']+'\n'+fp[847]['text']
    chunks={m.group(1):full[m.start():(next_start if (next_start:=full.find('PLD-',m.end()))!=-1 else len(full))] for m in re.finditer(r'PLD-(\d+)',full)}
    for i,line in enumerate(farm.splitlines()):
        lab,prov,phase,bp,cal=line.split('|');idx=846 if i<16 else 847
        bps=re.findall(r'(?<![\d.])(\d{3,4})±(\d+)',chunks[lab])
        unrounded='±'.join(bps[0]) if bps else None
        relationship='Source structural phase, not a named repair or construction deposit. Fig.13.1 shows section/phase relations, not a demonstrated sample-to-object-use join.'
        if lab=='12424':relationship='Pit fill; no demonstrated date for an original room construction or for a seal use event.'
        if lab=='12425':relationship='Grid vicinity overlaps the S6 trench and Phase5, but no shared depositional unit or installation relationship is reported.'
        if lab=='12422':relationship='The sample label names Structure3N, but the calibrated date is Gupta; the route of intrusion/reuse is not independently resolved.'
        if lab=='12423':relationship='The sample label names Structure30, but the calibrated date is later than Harappan; installation relationship unresolved.'
        add('FAR-PLD'+lab,'Farmana','PLD-'+lab,'charred material' if lab=='15057' else 'carbonized wood',prov,
          {'namespace':'structural phase/cultural assignment','label':phase},
          {'conventional_BP_rounded':bp,'conventional_BP_unrounded':unrounded,'uncertainty':'±1σ'},
          {'method':'OxCal4.1, IntCal09','reported_2sigma_intervals':cal,'coverage_percent':95.4,'recalibrated':False},
          'EAST-SHINDE2011',833 if idx==846 else 834,idx,relationship,
          'No sample is joined to a specific construction/repair and original documentary-use context.',
          material_locator={'printed_page':832,'pdf_index':845,'table':'13.1'},
          pretreatment='AAA: HCl1.2N / NaOH1N / HCl1.2N' if lab in ('16340','16350') else 'AAA: HCl1.2N / NaOH0.1N / HCl1.2N',
          short_lived_material_demonstrated=False)
    # Kanmer: AMS table reproduced in two publications; count one determination per lab ID.
    kan='''14748|AA-17/6/3.63m|3780±25|2292–2137BC(95.4%)
14749|FF-29/3/3.85m|3750±25|2279–2250BC(7.2%);2230–2220BC(1.5%);2211–2121BC(68.2%);2095–2041BC(18.5%)
14750|FF-29/3/3.85m|3770±25|2287–2133BC(92.7%);2079–2061BC(2.7%)
14751|Z-30/12/9.72m|3985±25|2571–2513BC(56.2%);2504–2466BC(39.2%)
14752|Z-30/10/9.04m|3935±25|2560–2536BC(3.2%);2491–2341BC(92.2%)
14753|EE-30/4/4.58|3680±25|2141–2011BC(89.2%);2001–1977BC(6.2%)
14754|Q-28/11/8.00m|3895±25|2467–2299BC(95.4%)
14755|Q-28/12/8.20m|3865±25|2464–2281BC(90.4%);2250–2231BC(3.9%);2219–2212BC(1.1%)
14756|Z-28/12/8.91m|3875±25|2465–2286BC(94.9%);2247–2243BC(0.5%)
14757|AA-28/9/788|3810±25|2337–2323BC(2.2%);2308–2196BC(86.7%);2172–2146BC(6.5%)
14758|Q-28/13/8.45m|3890±25|2466–2298BC(95.4%)
14759|Q-28/11/8.09m|3900±20|2468–2335BC(87.9%);2324–2301BC(7.5%)
14760|AA-28/8/7.11m|3875±25|2464–2288BC(95.4%)
14761|Q-28/10/8.03m|3885±25|2466–2292BC(95.4%)
14762|A-28/12/9.24|3815±25|2344–2196BC(90.6%);2172–2146BC(4.8%)
16352|Y-30/20/9.30m|3880±20|2461–2298BC(95.4%)'''
    kp=json.loads((RAW/'pokharia2011.pages.json').read_text(encoding='utf8'))[4]['text']
    for i,line in enumerate(kan.splitlines()):
        lab,prov,bp,cal=line.split('|')
        start=kp.index('PLD-'+lab);end=kp.find('PLD-',start+5)
        bps=re.findall(r'(?<![\d.])(\d{3,4}) ± (\d+)',kp[start:end if end!=-1 else len(kp)])
        unrounded='±'.join(bps[0]) if bps else None
        add('KAN-PLD'+lab,'Kanmer','PLD-'+lab,'grain, taxon unspecified in this table' if lab=='16352' else 'charcoal',prov,
          {'namespace':'table stratigraphy','label':'phase not explicit per AMS row'},
          {'conventional_BP_rounded':bp,'conventional_BP_unrounded':unrounded,'uncertainty':'±1σ'},
          {'method':None,'missing_reason':'Calibration algorithm/curve not stated in the bounded table or the radiocarbon section read.','reported_2sigma_intervals':cal,'recalibrated':False},
          'POKHARIA2011',1837,4,'Grid/layer/depth sample; no seal registration, room feature and construction relationship crosswalk.',
          'Matching layer numbers across different grids would invent a seal-to-date join.',
          same_determination_other_locator={'source_id':'EAST-KHARAKWAL2011','printed_page':368 if i<4 else 369,'pdf_index':13 if i<4 else 14},
          units_note='Depth string retained as printed; no metre unit invented for 788,4.58 or9.24.')
    conv='''2619|Y-30/930cm/layer20|4190±80|2850–2623BC
3028|Z-30/942–967cm/layer12|4630±90|3099–3600BC
3042|Z-30/900–923cm/layer11|4750±100|3100–3600BC
2685|Y-30/307cm/layer8|4200±120|2875–2581BC
2627|R-21/466cm/layer7|3870±100|2470–2149BC
2699|HH-20/529cm/layer4|4720±180|3660–3345BC
3027|Z-18/395cm/layer4|4660±110|3037–3600BC
2628|HH-30/280cm/layer3|3610±90|2130–1785BC
2698|R-20/320cm/layer2|4290±80|3006–2877BC'''
    for line in conv.splitlines():
        lab,prov,bp,cal=line.split('|')
        add('KAN-BS'+lab,'Kanmer','BS-'+lab,'wood charcoal',prov,{'namespace':'table stratigraphy','label':'source layer retained'},
          {'conventional_BP':bp,'uncertainty':'source ± value'},
          {'method':None,'reported_BC_interval':cal,'interval_sigma':None,'missing_reason':'No curve/version or interval probability in Table1; inconsistent endpoint order is retained.','recalibrated':False},
          'POKHARIA2011',1836,3,'Sample in a source layer, without a named construction or object-use context.',
          'No registered seal/deposit/construction join; early results and source inconsistencies are retained rather than removed.')
        if lab=='2619':records[-1]['other_source_conflict']={'source_id':'EAST-KHARAKWAL2011','printed_page':368,'pdf_index':13,
          'values':'layer19; calibrated2888–2623BC','handling':'Kept as a source disagreement, not silently harmonised with layer20/2850–2623 in Pokharia2011.'}
    for lab,cal in [('16351','AD335–425(95.4%)'),('16353','AD321–410(80.1% reported component)')]:
        add('KAN-PLD'+lab,'Kanmer','PLD-'+lab,'rice grains','Mature/Late Harappan sample groups; exact grid not given in the bounded paragraph',
          {'namespace':'field association','label':'Mature/Late; later direct age'},None,
          {'method':None,'reported_AD_interval':cal,'missing_reason':'Paragraph omits the determination, full distribution and calibration method.','recalibrated':False},
          'POKHARIA2011',1836,3,'Authors interpret later grains as percolated/reworked into older remains.',
          'Direct age defeats field-phase assignment; raw determination and precise locus not supplied in this paragraph.')

    # Harappa: spatially separate dated hearths cannot date the inscription contexts by site membership.
    har='''A7522|A-7522|H93/4054[13];Tr10W,Rm92,Hearth25lower|3875±55|2457–2207BC;intercepts2390,2389,2333|3
QL4732|QL-4732|H93/4055[26];Tr10W,Rm92,Hearth25lower|3890±20|2453–2323BC;intercepts2397,2379,2348|3
A7523|A-7523|H93/4061[32];Tr10W,Rm92,Hearth25middle|3835±50|2395–2149BC;intercept2283|3
QL4733|QL-4733|H93/4061[32];Tr10W,Rm92,Hearth25middle|3840±20|2320–2206BC;intercept2285|3
A7524|A-7524|H93/4124[128];Tr10W,Rm92,Hearth16|4385+155/−150|3336–2879BC;intercepts3018,2990,2927|3
A7528|A-7528|H93/4315[236];Tr10W,Rm93,Hearth233|3165+190/−185|1629–1168BC;intercept1422|4
QL4734|QL-4734|H93/4194[215];Tr10W,Hearth210upper|3820±60|2393–2142BC;intercepts2277,2225,2207|4
A7529|A-7529|H93/4331[256];Tr10W,Rm93,Hearth210lower|3905±75|2468–2280BC;intercepts2451,2429,2403|4
QL4730|QL-4730|H93/4331[256];Tr10W,Rm93,Hearth210lower|3900±30|2457–2325BC;intercepts2450,2446,2401,2372,2365|4
A7525|A-7525|H93/4208[7];Tr9,Hearth7|3790±85|2391–2043BC;intercept2197|3
QL4731|QL-4731|H93/4209[20];Tr9,Hearth7|3880±40|2455–2284BC;intercepts2393,2386,2338|3'''
    for line in har.splitlines():
        key,lab,prov,bp,cal,ix=line.split('|');idx=int(ix)
        flags=[]
        if key=='A7524':flags.append('Authors flag probable old charcoal; retained.')
        if key=='A7528':flags.append('Authors flag aberrant result/possible contamination; retained.')
        group='H93/4061[32]' if key in ('A7523','QL4733') else 'H93/4331[256]' if key in ('A7529','QL4730') else prov.split(';')[0]
        add('HAR-'+key,'Harappa',lab,'not specified for each row in Table1; source discusses hearth charcoal and old-charcoal effects',prov,{'namespace':'Harappan period','label':'3B source table'},
          {'BP_5568_half_life':bp}, {'method':None,'reported_1sigma_BC_interval_and_intercepts':cal,
          'missing_reason':'Calibration program/curve not specified in this bounded table; do not substitute the method in a later publication.','recalibrated':False},
          'MK1997',139+idx,idx,'Hearth samples; not demonstrated dates of the Tr10E seal room construction or Tr9 jar installation.',
          'The report does not link each documentary object or its use event to this specific hearth deposit.',
          physical_sample_dependency_group=group,source_flags=flags)
    for key,lab,prov,period,bp,cal in [
      ('BETA93757','BETA-93757','H96/7313[18];Tr38,Hearth43upperfill,MoundAB','5','3430±110','1882–1539BC;intercepts1737,1714,1701'),
      ('BETA93756','BETA-93756','H96/7291[100];Tr37,Hearth101,MoundF','3B','3870±50','2455–2207BC;intercept2328'),
      ('WGNEC2525','WG(NEC)-2525','H96/7262[70];Tr37,streetdeposits,MoundF','late3B','3810±60','2329–2140BC;intercepts2272,2258,2204')]:
        add('HAR-'+key,'Harappa',lab,'not specified in Table1; no taxon imputed',prov,{'namespace':'Harappan period','label':period},
          {'BP_5568_half_life_before_AD1950':bp},
          {'method':'University of Washington Quaternary Isotope Laboratory Calibration Program1993,rev.3.0.3c','reported_1sigma_BC_interval_and_intercepts':cal,'recalibrated':False},
          'MK2000',2,2,'Separate MoundAB/MoundF samples; the source describes MoundE excavations about half a kilometre away.',
          'A date from another mound cannot independently date Wall296, Tr54 workshop or their documentary objects.')
    for key,lab,prov,bp,cal in [
      ('A8047','A-8047 / AMS AA-16461','H94/5383[64];Tr22,Hearth64,below Wall15','3965±55','2558–2404BC;intercept2465'),
      ('A8048','A-8048','H94/5384[66];Tr22,Hearth64,below Wall15','3975+110/−105','2589–2320BC;intercept2467'),
      ('A8049','A-8049','H94/5385[67];Tr22,Hearth68,below Wall15','3785+145/−140','2457–1976BC;intercepts2195,2152,2149')]:
        add('HAR-'+key,'Harappa',lab,'not specified for each row in Table1; hearth sample',prov,
          {'namespace':'Harappan period','label':'3B source table'}, {'BP_5568_half_life':bp},
          {'method':None,'reported_1sigma_BC_interval_and_intercepts':cal,'recalibrated':False,
           'missing_reason':'Calibration method not specified in the bounded table.'},
          'MK1997',143,4,'Underlying hearth supplies a terminus after which Wall15 was built; it does not date the tablet application or later repair.',
          'Tablet context conflicts between the Trench22 prose and Trench7/8,wash caption; no repair/use-event pair.',
          source_flags=['A-8049 is source-flagged somewhat aberrant; retained.'] if key=='A8049' else [],
          physical_sample_dependency_group=prov.split(';')[0])
    # Dholavira chronological evidence is a source-model constraint, not a gate-panel date.
    for key,lab,stage,bc in [('TL4','DHR93/TL/4','III','2809±461BCE'),('TL8','DHR93/TL/8','II','2302±480BCE')]:
        add('DHO-'+key,'Dholavira',lab,'material not specified in bounded chronology entry',
          'Stage '+stage+'; exact sample grid, stratum, depth and feature not reported in the bounded entry',
          {'namespace':'Dholavira stage','label':stage},{'TL_date_as_reported':bc},
          {'method':'thermoluminescence; dose and model not supplied here','calendar_reference':'source BCE result; no radiocarbon calibration','recalibrated':False},
          'BISHT2015-PRELIM','104–105',120,'Broad stage attribution, without physical relation to the inscription, gate mounting or a named repair.',
          'Source reports four TL determinations, calls two erratic, and presents these two as useful; sample/event detail and anomalous stage ordering remain unresolved.')
    # Lothal: two half-life outputs are alternate conventions, not calibrated ranges.
    lot='''23|SRG54;XLIII–XLVIII/4;1.22m;Field28|VA,PeriodII|3705±105|3815±110|Posthole of mud wall of PhaseVA built on PhaseIV flood debris.|7
19|SRG11;Locus5B;2.19–2.25m;Field6|VA,PeriodII|3650±135|3750±40|Debris sealing western embankment wall of source dock.|7
29|SRG55;XII–XVIII/7;2.11m;Field53|IVA,PeriodI|3740±110|3845±115|Waterlogged cesspool debris; source suggests sullage accumulation.|7
22|SRG2;E13/9;1.88m;Field29|endIIIB,PeriodI|3845±110|3960±115|Loose ashy layer sealing PhaseIIIB flood debris and wall.|8
27|SRG2;D13/7A;1.98m;Field32A|IIIB,PeriodI|3840±110|3950±115|Flood debris/loam accumulated against PhaseIIIB wall.|8
26|SRG2;D13/7A;1.98–2.26m;Field32|IIIB,PeriodI|3830±120|3950±125|Flood debris/loam accumulated against PhaseIIIB wall.|8'''
    for line in lot.splitlines():
        lab,prov,phase,bp,alt,rel,ix=line.split('|');idx=int(ix)
        add('LOT-TF'+lab,'Lothal','TF-'+lab,'charcoal mixed with mud/soil; rootlets manually removed',prov,
          {'namespace':'Rao phases as submitted to laboratory','label':phase},
          {'BP_AD1950_half_life5568±30':bp,'alternate_BP_half_life5730±40':alt},
          {'method':None,'status':'uncalibrated radiocarbon ages; parenthesized result is a half-life convention, not a calendar confidence interval','recalibrated':False},
          'KUSUMGAR1963',141+idx,idx,rel,
          'All six samples are from trenches other than the SRG3 warehouse sealing deposit. They cannot directly date its destruction, floor or closure use.',
          old_wood_and_root_contamination_control='No short-lived taxon identified; manual rootlet removal and chemical treatment reported. Waterlogging acknowledged.')
    assert len({r['id'] for r in records})==len(records)
    write(HERE/'date-evidence.json',{'protocol_sha256':hashlib.sha256((HERE.parents[1]/'PROTOCOL.md').read_bytes()).hexdigest(),
      'status':'Published determinations and source-specific calibrations; no pooled calendar model and no recalibration.',
      'record_counts_by_town':dict(collections.Counter(r['town'] for r in records)),
      'banawali_missing_reason':'No laboratory determination with a demonstrated relation to the reported sitting-room seal or the named rebuilding episodes was located in the bounded held sources.',
      'records':records})
    write(RAW/'date-transcription-checks-v1.json',{'farmana_lab_row_text':chunks,
      'method':'Exact native-text chunks retained locally; rounded and unrounded values are labelled in authored evidence. Calibrated intervals in date-evidence are a manual transcription.',
      'record_count':len(records)})
    print(len(records),dict(collections.Counter(r['town'] for r in records)))
if __name__=='__main__':main()
