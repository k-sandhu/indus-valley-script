"""Map revised manuscript claims to source observations and exact outputs."""
from pathlib import Path
import json, argparse

BASE=Path(__file__).resolve().parent
records=[
 ('C01','3.1','Historical1022/approximately96 and1056/96 counts are different attributed inventories;142Early+Mature through2024 extends Uesugi and cannot form a current ratio with either old denominator.',['R01','R02','R38'],['published-count-arithmetic.json'],'Historical inventory audit; no current regional percentage'),
 ('C02','3.2','The ICOMOS charter supports selective investigation/maintenance; UNESCO2026 reports Moenjodaro conservation constraints.',['R03','R04'],[],'The general charter and site-specific report have different scopes'),
 ('C03','3.3','Ganweriwala postponement in2007 and excavation activity in2024 are dated observations.',['R05','R06'],[],'No2026field status inferred'),
 ('C04','4.1','Ganweriwala81.5,66.7 and33ha use different area definitions.',['R07','R08'],['published-count-arithmetic.json'],'Not an uncertainty interval or measured area loss'),
 ('C05','4.1','Square-equivalent dimensions describe1,5,30 and200ha areas.',[],['square-equivalent-geometry.csv'],'Geometry only; no measured settlement shapes'),
 ('C06','4.1','Kotada/Morodharo name concordance and0.6ha enclosure illustrate alias and feature-area issues.',['R19'],[],'Enclosure is not total phase-specific settlement area'),
 ('C07','4.2/4.3','Cholistan2020proposals number337with71legacy matches including25references;266unmatched and46/312non-reference matches.',['R08'],['published-count-arithmetic.json','resurvey-descriptives.json'],'Remote proposals; later confirmation status not exhaustively reconciled'),
 ('C08','4.2','246of337proposals are below5ha; source Discussion andFig9identify six>20ha.',['R08'],['published-count-arithmetic.json'],'Detectable visible mound population; no unexcavated all-site area distribution'),
 ('C09','4.2','Proximity to a large city alone does not identify unseen site area.',['R23','R29'],[],'Methodological inference; no fitted predictor'),
 ('C10','5.1','Rakhigarhi has village overlay; Sukkur construction damaged upper levels while some lower contexts survived.',['R21','R62'],[],'Known locality evidence, not every modern city'),
 ('C11','5.2','Alluvium can bury or truncate; Dales1965reported cultural evidence to39ftbelowMoenjodaro plain.',['R11','R17','R61'],[],'Historical depth and water observations, not current or continuous dated footprint'),
 ('C12','2.2/5.2','Sutlej avulsion and late foothill floods reflect different periods/processes.',['R15','R16'],[],'Approximate age orientation, no universal channel date'),
 ('C13','4.3/5.3','GreenTable1positive counts uniquely reconstruct199/779and symbol/size partitions.',['R10'],['historical-map-checks.json','historical-map-checks-by-symbol.csv','historical-map-checks-by-size-class.csv'],'Changing selected all-period sample; not regional probability'),
 ('C14','4.3','Green64off-map encounters and169unlinked positives describe study-local omissions.',['R10'],['resurvey-descriptives.json'],'Encounter selection and coordinate/identity uncertainty retained'),
 ('C15','4.2','Cholistan reference selection, iterations and threshold constrain performance claims.',['R08'],[],'No held-out all-site recall or calibrated site probability'),
 ('C16','5.4','Mehrgarh is a pre-Indus burial-process comparison; Nausharo supplies local-to-Indus sequence.',['R39','R40','R45'],[],'No transfer of Neolithic cemetery dates to Bronze Age fans'),
 ('C17','5.4','Known GhaziShah archaeology and2025abstract support piedmont work; Kai/northernBalochistan shelter chronology is unresolved.',['R37','R41','R42','R43','R44','R49'],[],'No authenticated Indus cave settlement or new2025stratigraphy'),
 ('C18','5.5','Lothal2022local environmental transition uses calibrated reservoir-corrected ages;2026Khambhat study assesses index-point eligibility.',['R32','R34'],[],'Local relative sea level, approximate tidal constraints;2026abstract depth'),
 ('C19','source audit','Srivastava2023association of3000BPand2800–1800BCEis excluded as inconsistent.',['R33'],[],'Formation-process synthesis retained; no adoption of that age association'),
 ('C20','6/AppendixA','21overlapping regions have evidence classes, units, comparisons and demotion decisions.',[],[],'Authored proposals, not executed survey/discoveries; exact candidate-v3 register'),
 ('C21','7.1','Find yield identity relates area/fraction/thickness/in-grounddensity/recovery.',[],['synthetic-scenarios.json'],'Mathematical planning identity; no calibrated density or artifact forecast'),
 ('C22','7.1','Harappa report describes almost1millionpotsherds in five seasons and contextual variation.',['R30'],[],'Empirical scale, not transferable density'),
 ('C23','7.2','Fine plant recovery and preservation-dependent lipid/protein results can change information gained.',['R24','R36'],[],'No guaranteed assay success or sample-count extrapolation'),
 ('C24','8.1','Nqobservation chain and independent-repeat identity expose missing observation assumptions.',[],['synthetic-scenarios.json','synthetic-repeat-detection.csv'],'Assumed examples, no empirical p/q/N'),
 ('C25','Supplementary run notes','Inscription-oriented metadata and record-level aliases are outside settlement-coverage inference.',[],['metadata-coverage.json','cohort-comparison.json'],'Different selected record cohorts; removed numeric metadata from manuscript'),
 ('C26','AppendixB','Run-v3records64implementation/preservationchecks.',[],['verification.json','manifest.json'],'Bookkeeping and implementation verification, not independent scientific evidence'),
 ('C27','4.3','PAS123/240matches, Cholistan proportions andMasudpur13/4mound units are local descriptive comparisons.',['R08','R11','R29'],['resurvey-descriptives.json'],'No pooling or regional site-total extrapolation'),
 ('C28','3.3/5.4/5.5','Railway removal, Manda/Ropar/Shortugai/Dholavira andMakranuplift provide additional documented anchors.',['R63','R64','R65','R66','R67','R68','R69','R72'],[],'Their chronology/process scope remains locality-specific'),
 ('C29','8.1','Capture-recapture and effort curves require common frames/matching and cannot identify arbitrary invisible classes.',['R56','R57','R58','R59','R60'],[],'Proposed methods; naive estimate is not a guaranteed minimum'),
 ('C30','5.5','Khambhat2003report includes cores and datedwood but does not establish wood-to-specific-built-feature association.',['R71'],[],'Reported observations plus author-commissioned source-review inference; no city-date adoption'),
 ('C31','5.2','2025institutional abstract reportsKotDijiroots;2026participant account traces anunretrievedpreliminaryreport.',['R51','R52','R53'],[],'No revised precise foundation date;2026Antiquityarticle has different methods'),
]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=BASE/'claims-v2.json')
    p.add_argument('--source-register',type=Path,default=BASE/'sources-v4.json')
    p.add_argument('--candidate-register',type=Path,default=BASE/'candidates-v3.json')
    a=p.parse_args()
    target=a.output
    if target.exists():raise FileExistsError(target)
    sources=json.loads(a.source_register.read_text(encoding='utf-8'))
    observations={r['observation_id'] for r in sources['sources']}
    result=[]
    from revise_registers import prose_spacing
    for cid,section,text,sids,outputs,limit in records:
        obs=[sid+'-O1' for sid in sids]
        assert set(obs)<=observations
        paths=['experiments/2026-10-11-settlement-prospection/run-v3/'+p for p in outputs]
        for p in outputs:assert (BASE/'run-v3'/p).exists()
        limit=limit.replace('candidate-v3 register',a.candidate_register.name)
        inline={'C06':['IA03'],'C11':['IA01'],'C12':['IA06','IA07'],'C17':['IA02'],'C18':['IA04','IA05']}.get(cid,[])
        if inline:
            paths.append('experiments/2026-10-11-settlement-prospection/run-v3-inline-arithmetic/arithmetic.json')
        result.append(dict(id=cid,section=section,claim=prose_spacing(text),source_observations=obs,
          analysis_outputs=paths,limits=prose_spacing(limit),evidence_kind='Proposal/mathematical inference' if not sids else 'Source-attributed observation or bounded inference'))
        if inline:result[-1]['inline_arithmetic_rows']=inline
    result.append(dict(id='C32',section='2.3/8.3/Appendix A',
         claim='The unrun pilot treats blocks as inferential units and profiles as nested observations. Descriptive preservation summaries use all adequately resolved blocks; eight holdout blocks evaluate a locked prediction rule. Shared-frame cells enter once across every overlapping region.',
         source_observations=[],analysis_outputs=[],
         protocol_files=['experiments/2026-10-11-settlement-prospection/PILOT-DESIGN-v4.md','experiments/2026-10-11-settlement-prospection/'+a.candidate_register.name],
         limits='Proposed workload and editorial design; no power calculation, field result or calibrated survival probability',evidence_kind='Unrun proposal'))
    obj=dict(version='v3' if target.name=='claims-v3.json' else 'v2',source_register=a.source_register.name,numerical_endpoint='run-v3',region_register=a.candidate_register.name,
             preceding_claim_map='claims-v2.json' if target.name=='claims-v3.json' else 'claims-v1.json',claims=result)
    target.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(str(len(result))+' revised claims with valid source and output references.')

if __name__=='__main__':main()
