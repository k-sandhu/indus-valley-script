"""Write the claim-to-observation map; numerical paths identify exact results."""
from pathlib import Path
import json

BASE=Path(__file__).resolve().parent
CLAIMS=[
('C01','3.1','Historical1022/96 and1056/96 summaries disagree;142Early+Mature is a different review scope.','reported observations plus arithmetic',['R01','R02','R38'],['published-count-arithmetic.json'],'No current civilization-wide excavation percentage.'),
('C02','3.2','Conservation and maintenance create obligations after exposing remains.','conservation principle and current site report',['R03','R04'],[],'Charter is not a jurisdiction-specific permit statute; Moenjodaro report is site-specific.'),
('C03','3.3','Ganweriwala access/fieldwork status changed between2007,2015 and2024.','dated reports',['R05','R06','R07'],[],'No inference about2026season activity or completed genetic analysis.'),
('C04','4.1','Ganweriwala81.5,66.7 and33ha describe different observations.','reported area definitions',['R07','R08'],['published-count-arithmetic.json'],'No confidence interval, phase-specific maximum or measured destruction fraction.'),
('C05','4.1','Square-equivalent dimensions give an intuitive area scale.','geometry',[],['square-equivalent-geometry.csv'],'Square equivalence is not measured settlement shape.'),
('C06','4.1','Kotada/Morodharo demonstrates alias and feature-area ambiguity.','site report',['R19'],[],'0.6ha fort is not total settlement extent.'),
('C07','4.2','337remote clusters include71legacy matches;266are unmatched.','reported totals plus arithmetic',['R08'],['published-count-arithmetic.json'],'Unmatched remote candidates are not266validated new Indus sites.'),
('C08','4.2','246of337proposed visible clusters are under5ha; six exceed20ha.','reported distribution plus arithmetic',['R08'],['published-count-arithmetic.json'],'Detection population differs from all archaeological settlements.'),
('C09','4.3','Proximity to a city cannot determine unseen settlement area.','methodological inference',['R23','R29'],[],'No fitted extent model or discovery probability.'),
('C10','5.1','Urban disturbance can remove upper deposits while lower archaeology survives.','reported urban excavation',['R21'],[],'Parcel-level survival/access has not been audited for2026.'),
('C11','5.2','Younger alluvium can bury or cut older surfaces.','regional geoarchaeology',['R11','R17'],[],'A missing surface signal cannot choose burial versus erosion.'),
('C12','5.2','Studied Sutlej avulsion and later foothill floods describe different times/processes.','dated geomorphology',['R15','R16'],[],'No universal channel chronology or constantly dry valley inference.'),
('C13','5.3','Green Table1recovers199positive checks of779.','reported table plus integer reconstruction',['R10'],['historical-map-checks.json','historical-map-checks-by-symbol.csv'],'Changing selected all-period sample; not regional/national detection probability.'),
('C14','5.3','64off-map encounters demonstrate map-only omission without establishing recall.','reported encounters and inference',['R10'],[],'No complete regional ground-truth denominator.'),
('C15','5.3','Cholistan selected validation and visually selected threshold constrain performance inference.','method audit',['R08'],[],'No calibrated site probability or all-site recall.'),
('C16','5.4','Mehrgarh is a pre-Indus regional alluvial burial analogue.','reported archaeology',['R39','R40','R45'],[],'2025cemetery chronology does not date Bronze Age fan surfaces.'),
('C17','5.4','Ghazi Shah has a2025excavation report abstract; cave dates remain weaker.','current primary report and inventories',['R41','R42','R43','R44'],[],'Full2025report unavailable; no newly authenticated Indus cave occupation.'),
('C18','5.5','Local relative sea level and geomorphology are needed for former-coast targets.','coastal evidence and proposed method',['R25','R31','R32','R33','R34'],[],'Former coastline can be inland, eroded or submerged; no new bathymetric/shoreline reconstruction.'),
('C19','5.5','Srivastava2023~3000BP/2800-1800BCE association is chronologically inconsistent.','independent source audit',['R33'],[],'Use mechanisms, exclude that association; original dated records remain needed.'),
('C20','6','21editorial windows specify search questions and rejection tests.','exploratory hypotheses',[],[],'No measured survey coverage, terrain suitability, new images or archaeological discovery.'),
('C21','7.1','Synthetic3000m³ scenario yields12k/120k/1.2m at assumed densities.','synthetic arithmetic',[],['synthetic-scenarios.json','synthetic-fragment-yields.csv'],'Uncalibrated density/recovery; no total or seal/inscription forecast.'),
('C22','7.1','Harappa report describes almost1million potsherds in five seasons.','empirical scale observation',['R30'],[],'Excavated-volume density unavailable; context-specific finds cannot be transferred.'),
('C23','7.2','Fine recovery and newer assays can add information with preservation-dependent failures.','primary methods and results',['R22','R23','R24','R36','R47'],[],'Biomolecular success is not universal; seed cohort/calibration issues remain flagged.'),
('C24','8.1','Recorded counts cannot identify true site totals without observation assumptions.','synthetic demonstration and analytical inference',[],['synthetic-scenarios.json','synthetic-repeat-detection.csv'],'No empirical q,p,N or independence fitted; repeat formula is conditional on iidvisits.'),
('C25','AppendixB','Local register counts are115/85coordinates and86/213phase entries.','metadata computation',[],['metadata-coverage.json'],'Selected different cohorts;49radiocarbon-basis labels are not independent laboratory dates.'),
('C26','AppendixB','49computation/preservation checks passed in run-v2.','verification',[],['verification.json','manifest.json'],'Checks verify arithmetic and provenance, not archaeology or peer review.'),
]

def main():
    output=BASE/'claims-v1.json'
    if output.exists():raise FileExistsError(output)
    sources=json.loads((BASE/'sources-v2.json').read_text(encoding='utf-8'))
    ids={r['id'] for r in sources['sources']}
    result=[]
    for cid,section,claim,kind,sids,paths,limits in CLAIMS:
        assert set(sids)<=ids
        for path in paths:assert (BASE/'run-v2'/path).exists()
        result.append(dict(id=cid,section=section,claim=claim,evidence_kind=kind,source_observations=[s+'-O1' for s in sids],analysis_outputs=['experiments/2026-10-11-settlement-prospection/run-v2/'+p for p in paths],limits=limits))
    output.write_text(json.dumps({'status':'authored claim map; no new field evidence','claims':result},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(result)} claims mapped to existing observations and exact outputs.')

if __name__=='__main__':main()
