"""Write attributed case assessments and query/access records to a fresh directory."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez'

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def dating(lo,hi,basis,location,note='',point=None):
    return dict(start_year=lo,end_year=hi,approximate_year=point,method=basis,grade='C',calendar_strength='low',
                source_location=location,note=note,selected_for_South_Asian_coverage=False)

def contacts():
    return dict(status='Exploratory',anchor_audit='research/literature/external_phonetic_anchor_audit.md',
      individually_illustrated_cases=4,additional_abstract_only_cohorts=1,
      aligned_Indus_and_foreign_script_pairs_authenticated=0,
      count_interpretation='Four illustrated physical seals plus a separate three-token cohort. Two impressed seal matrices are not two additional recovered seals. This is a bounded case selection, not a corpus total.',
      cases=[
       dict(id='ur-bm120573',identifiers=['BM120573','1928,1009.56','U7683','Gadd1932 no.1'],
            label='Ur square Indus-style stamp with cuneiform above a bull',region='Mesopotamia',
            provenance='Diqdiqqah near Ur; museum indexed field says surface. Gadd reports worn inscription; no dated sealed deposit authenticated.',
            observed_scripts=['cuneiform'],Indus_text_observed=False,object_count=1,images_reviewed=True,
            source_ids=['gadd1932','bm120573','frenez2018'],
            source_locations=['Gadd1932 no.1 pp.5–6, PDF12–13','Frenez2018 Figure10a p.177','BM indexed fields, web-14.json'],
            dating_assessments=[dating(None,-2500,'Gadd’s legacy pre-Sargonic palaeographic terminus','Gadd1932 p.6','Do not translate the old historical chronology into a modern excavated bound.'),
                                dating(None,None,'museum approximate attribution','BM indexed date field','Catalogue opened only as indexed result.',point=-2500)],
            limitation='Worn foreign legend; no aligned Indus text. Gadd no.6/BM122947 is a different cylinder.'),
       dict(id='bnf-cuneiform-stamp',identifiers=['Frenez2023 Figure3F','Cabinet des Médailles/Bibliothèque nationale de France; inventory number unrecovered'],
            label='Collection stamp with Indus-related bovid imagery and cuneiform',region='unknown; possibly Gulf-related in Laursen’s discussion',
            provenance='Unprovenanced collection item; do not assign a Bahrain findspot.',
            observed_scripts=['cuneiform, as attributed in published caption'],Indus_text_observed=False,object_count=1,images_reviewed=False,
            source_ids=['frenez2023-caption','laursen2010'],source_locations=['Frenez2023 public Figure3F caption','Laursen2010 p.119, citing Vidale2005 and Glassner2002'],
            dating_assessments=[dating(None,None,'unprovenanced stylistic association; no usable date recovered','Laursen2010 p.119')],
            limitation='Published image/caption identified; inventory, full epigraphic publication and precise date unavailable. Personal-name formula remains the cited authors’ claim.'),
       dict(id='linear-elamite-round-stamp',identifiers=['Laursen2010 no.28','Winkelmann1999 Abb.2','Winkelmann2004 II.1-02','Frenez2018 Figure10f','Frenez2023 Figure3O'],
            label='Round Indus-style bovid stamp with Linear Elamite legend',region='western/southwestern Iranian plateau, attributed',
            provenance='Unknown archaeological findspot; formerly Bailey collection, later Ligabue collection per Laursen p.104 n.4. Bahrain attribution rejected in that note.',
            observed_scripts=['Linear Elamite, as identified by cited publications'],Indus_text_observed=False,object_count=1,images_reviewed=True,
            source_ids=['laursen2010','winkelmann1999','winkelmann2004','frenez2018','frenez2023-caption'],
            source_locations=['Laursen Table1 p.100,no.28; p.104 n.4; Figure9 p.110; pp.119,121','Frenez2018 Figure10f p.177','Frenez2023 Figure3O caption'],
            dating_assessments=[dating(-2112,-2095,'author’s proposed historical/script-horizon inference','Laursen2010 p.121',
                'Depends on restricting Linear Elamite to one ruler/horizon; no independent dated object context. Retain as a hypothesis, not a secure historical bound.')],
            limitation='1999 article and2004 catalogue not opened. Reproductions are treated as one example; full registration/provenance and current epigraphic edition remain to acquire.'),
       dict(id='shu-ilishu-cylinder',identifiers=['LouvreAO22310'],label='Shu-ilishu interpreter cylinder, contact comparator',region='Mesopotamia, attributed by style',
            provenance='Acquired through de Clercq collection; no excavated dated context authenticated.',
            observed_scripts=['cuneiform'],Indus_text_observed=False,object_count=1,images_reviewed=True,
            source_ids=['possehl2006','louvre-shu-ilishu'],source_locations=['Possehl2006 pp.42–43,rollout p.43','LouvreAO22310 date/origin/inscription fields'],
            dating_assessments=[dating(-2340,-2200,'Louvre stylistic Akkad attribution','Louvre date and attributed-origin fields'),
                dating(-2200,-2113,'Porada Late Akkadian alternative as reported','Possehl2006 p.42'),
                dating(-2113,-2004,'possible UrIII alternative','Possehl2006 p.42'),
                dating(None,None,'low-chronology approximate attribution reported by author','Possehl2006 p.42',point=-2020)],
            limitation='Interpreter role attests a contact claim in known script. This is not a paired Indus legend or an authenticated graphic translation.'),
       dict(id='bahrain-tokens2026',identifiers=['DOI10.1086/739820; token registration numbers unrecovered'],
            label='Three Bahrain tokens impressed by two cuneiform seals, abstract-only comparator',region='Gulf/Bahrain',
            provenance='Bahrain in institutional primary abstract; individual find contexts not reviewed.',
            observed_scripts=['cuneiform as reported in abstract'],Indus_text_observed=None,object_count=3,seal_matrices_reported=2,images_reviewed=False,
            source_ids=['laursen2026-abstract'],source_locations=['institutional abstract and embargo field'],
            dating_assessments=[dating(None,None,'early2nd millennium/Middle Bronze Age wording; numeric dates not recovered','Laursen et al.2026 title/abstract')],
            limitation='Full article/plates embargoed in institutional repository until1April2027. Indus-style imagery is not established by the abstract. No link to Frenez’s forthcoming study authenticated.')])

def lecture():
    def a(cid,time,statement,result,sids,locs,missing,rows):
        return dict(id=cid,caption_location=time,statement_attributed_to='Dennys Frenez through coordinator caption check',
                    statement=statement,assessment=result,source_ids=sids,source_locations=locs,missing=missing,evidence_row_ids=rows,status='Exploratory')
    return dict(status='Exploratory',video_independently_watched=False,
      source='experiments/2026-10-06-research-program/frenez-talk-check.md',
      quote_words=0,claims=[
       a('early-distribution','17:05–24:00','Pre-firing marks occur at most Indus sites in the second half of the fourth millennium BCE.',
         'Recovered Mehrgarh and Harappa records support early marks at those sites; Rehman Dheri has a stratified incised series. The proportion of all Indus sites is not established.',
         ['quivron1980','kenoyer2006','durrani1995'],['Quivron269,274–276;Kenoyer Ravi section;Durrani208–217'],
         'A dated site census and common pre/post-firing classification.', ['mehrgarh-pottery1980','harappa-ravi-prefire-subset','rehman-dheri-stratified']),
       a('firing-function','17:05–24:00','Mehrgarh marks identify potter or owner during a shared firing.',
         'Quivron proposes production/workshop identification; Coningham discusses communal ownership/risk using Quivron1997. Function has a published precedent but is not independently authenticated.',
         ['quivron1980','quivron1997','coningham2002'],['Quivron1980 pp.275,278;Coningham2002 pp.93–94 citingQuivron1997 pp.53,55,61'],
         'Primary1997 chapter and joined batch/vessel/mark registers.', ['mehrgarh-pottery1980','mehrgarh-nausharo1997','mehrgarh-failed-firing']),
       a('kiln-change','17:05–24:00','Marks nearly disappear when a new kiln type appears.',
         'Quivron1980 notes a decline by around2400 BCE; Coningham reports a peak near2700 and later decline. Miller documents contemporary open-air/updraft methods, including NausharoII. A causal replacement comparison was not recovered.',
         ['quivron1980','coningham2002','miller1997'],['Quivron p.278;Coningham p.93;Miller pp.42–43,47–49,57'],
         'Mark-frequency denominators by dated firing technology, sampling and ware controls.', ['mehrgarh-failed-firing','nausharo-kiln-II']),
       a('same-repertoire','17:05–24:00','The same early mark repertoire appears on seals in the late fourth to early third millennium BCE.',
         'Quivron1980 p.275 explicitly describes contemporary seals as having a different, restricted repertoire. Durrani/Kenoyer propose selected similarities. The full shared repertoire needs a sign-level test.',
         ['quivron1980','durrani1988','kenoyer2020'],['Quivron pp.275,279;Durrani p.28;Kenoyer pp.220–226'],
         'Fixed feature mapping, rare compounds, independent chronology and complete mark/seal comparison population.', ['mehrgarh-pottery1980','rehman-dheri-pendant54']),
       a('site-correction','17:05–24:00','Caption name Rakandere, an ivory button seal from northwestern Baluchistan.',
         'Probable identification is Rehman Dheri in the Gomal Valley near Dera Ismail Khan, historically NWFP, now Khyber Pakhtunkhwa. Durrani’s rectangular object is ivory in1988 prose and bone in1995 catalogue54. Reported dates/context assignments conflict.',
         ['durrani1988','durrani1995','durrani1995-intro','kenoyer2020'],['1988 pp.17–18,25,28;1995 catalogue54 p.201,photo p.206;Introduction p.vii;Kenoyer Table2 p.221'],
         'Independent lecture-image match; original field registration and a resolution of layer6/level19 versus layer12 and PeriodIB.', ['rehman-dheri-pendant54']),
       a('harappa-2800','17:05–24:00','Harappa has shared signs on seals/pottery before2800 BCE and a sealing from a fireplace radiocarbon-dated near2800.',
         'Ravi pottery marks and a carved bone fragment predate the Kot Diji phase. Published intaglio seals and clay sealings begin in2800–2600 BCE. Gallery confirms hearth find/circa2800 label; direct radiocarbon join is missing.',
         ['kenoyer2006','kenoyer-meadow1999','kenoyer-meadow2010-published','meadow-kenoyer2005','harappa-hearth-gallery'],
         ['1999 Figure4 item6;2006 Figure5:9;2010 p.li/Table1;2005 p.209/Table2;gallery136–137'],
         'Sample number, lab determination, calibration and deposit/specimen join establishing a before2800 endpoint.',
         ['harappa-ravi-bone1521','harappa-kot-diji-hearth-sealing','harappa-kot-diji-elephant1533']),
       a('oral-merchants','48:25–48:55','Later priests preferred oral transmission; Buddhist merchants reintroduced writing in the fifth century BCE.',
         'Recorded as Frenez’s historical account. Existing early Brahmi dates differ by source and dating basis; no agent/cause of reintroduction is established by the coverage table.',
         ['frenez2026-lecture','coningham1996','deraniyagala','salomon1998','rajan-sivanantham2026-I'],
         ['parent dating assessments for anuradhapura,porunthal-I,kodumanal,keeladi,ashoka-brahmi'],
         'Evidence joining the earliest inscriptions to particular transmitters, routes and institutions.',
         ['anuradhapura','porunthal-I','kodumanal','keeladi','ashoka-brahmi']),
       a('contact-paper','16:20–17:05','A forthcoming group paper concerns Indus-style cuneiform and Linear Elamite seals.',
         'Published examples are identified separately in contact-items.json.2024 CV lists the related paper in preparation; live title searches found no final published paper. The talk’s claim is retained as forthcoming.',
         ['frenez2026-lecture','frenez2024-cv','frenez2018','frenez2023-caption','laursen2010','laursen2026-abstract'],
         ['CV PDF7;2018 Figure10;2023 Figure3;Laursen no.28;2026 primary abstract'],
         'Final publication and complete object catalogue; authenticated paired Indus/foreign-script inscription.',
         ['contact-period-foreign-legends','bahrain-cuneiform-tokens2026'])])

def searches():
    records=[]
    for f in sorted(RAW.glob('web-*.json')):
        x=load(f);req=x.get('request',x.get('requests'))
        response=x.get('response','')
        records.append(dict(witness=f.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
            requests=req,response_saved=('response' in x),
            tool_error_present='Internal Error' in str(response),preservation_note=x.get('response_status')))
    return dict(status='Exploratory',search_batches=len(records),records=records,
      failed_or_unresolved_targets=[
        dict(target='Quivron1997 primary chapter',result='No full chapter recovered; exact reference and observations found through Coningham2002 and author bibliography.',witnesses=['web-04.json','web-05.json','web-06.json','web-07.json','coningham-original.pdf']),
        dict(target='Audouze/Jarrige1979 original firing report;1995 Mehrgarh full field report',result='Exact references/secondary page locators recovered, full registers not opened.',witnesses=['web-09.json','miller-kilns.pdf']),
        dict(target='Durrani official OJS interface',result='Timeout/poor initial retrieval; official Google Sites archive exposed public PDFs.1988 report,1995 seals paper and introduction recovered.',witnesses=['durrani1988-index.html','durrani1995-index.html']),
        dict(target='Direct Quivron1980 PDF',result='HTTP403; complete12-page public image recovery succeeded with12HTML and12image responses200.',witnesses=['quivron1980.acquisition.json','quivron1980-pages/pages.json']),
        dict(target='British Museum120573 record',result='Direct opens403; indexed fields and independently opened Gadd witness retained.',witnesses=['bm-120573.acquisition.json','web-14.json','web-15.json']),
        dict(target='Frenez/Marchesi/Vidale final Hybrid identities paper',result='No final article, DOI or catalogue authenticated in live searches.2024 CV/2026 lecture status kept separate.',witnesses=['web-12.json','web-13.json','frenez2024-cv-reuse.pages.json']),
        dict(target='Harappa circa2800 sealing radiocarbon join',result='Hearth caption and registration recovered, no laboratory/sample-to-feature-to-sealing join.',witnesses=['kenoyer-meadow1999.pdf','meadow-kenoyer2005.pdf','harappa-sealing-find.html']),
        dict(target='Bahrain2026 full article/plates',result='Institutional abstract HTTP200; browser open failed; file embargo notice until1April2027. No forms/contact used.',witnesses=['web-21-recovery.json','laursen2026-abstract.html'])])

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():p.error('Choose a fresh directory.')
    out.mkdir()
    write(out/'contact-items.json',contacts());write(out/'lecture-claim-audit.json',lecture());write(out/'search-log.json',searches())
    write(out/'dating-details.json',dict(status='Exploratory',
      radiocarbon_transcription='data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/radiocarbon-source-rows.json',
      rehman_dheri=dict(laboratory_determinations=12,source='Durrani1988 FigureD p.139 (PDF144)',
        phase_link='Durrani et al.1995 Introduction p.vii; seals/sherds pp.208,216–217',
        selected_phase_envelope=[-3300,-1900],grade='B',calendar_strength='low',
        calibration_missing=['curve/version','probability interval','sample material/context identifier for each determination'],
        limitations='Published legacy calibrated endpoints are retained as source observations. No recalibration, pooling or mark-incision date is computed.'),
      rehman_object54=dict(selected_interval=None,alternatives=['1988 p.28 PeriodIB3100–2850','1995 p.201 Level19 →IA','1988 p.25 Layer6 →mainLevel12/PeriodII','2020 Table2 comparison2800–2600'],
        next_check='Resolve original field registration BIV25/Layer6; confirm photo/registration match before choosing an absolute date.'),
      harappa=dict(sealing_registration='H98-3485/8437-01',selected_phase=[-2800,-2600],grade='B',calendar_strength='moderate',
        specimen_join_missing=True,source='1999 Figure4 item6;2006 Figure5:9;2005 p.209/Table2',
        limitation='Site-phase radiocarbon chronology and a gallery circa2800 label do not establish a dated hearth/sample join for this particular object.'),
      count_audit=dict(status='Verified computation',registered_rehman_sherds=314,stratified_rehman_sherds=190,
        remaining_unstratified_difference=314-190,printed_phase_signs=[7,12,14,19,111],printed_phase_sign_sum=sum([7,12,14,19,111]),
        stratified_minus_printed_phase_difference=190-sum([7,12,14,19,111]),
        unit_warning='190 sherds at p.208 versus phase signs at pp.216–217. Arithmetic difference does not identify27 missing objects or a date allocation.'),
      no_new_A_specimen_association_authenticated=True))
    print(json.dumps({'audit_files':4,'contact_cases':5,'lecture_claims':8}))

if __name__=='__main__':main()
