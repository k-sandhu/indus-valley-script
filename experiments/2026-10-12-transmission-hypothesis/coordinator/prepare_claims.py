"""Map synthesis claims to exact observations and declared outputs once."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
PREFIX='experiments/2026-10-12-transmission-hypothesis/'


def obs(file,*ids):return {'file':PREFIX+file,'ids':list(ids)}


def output(file,pointer,**checks):return {'file':PREFIX+file,'pointer':pointer,**checks}


def claim(id,statement,status,observations,outputs=(),discussion='MANUSCRIPT.md'):
    return {'id':id,'statement':statement,'status':status,'observations':observations,'outputs':list(outputs),
            'discussion':PREFIX+discussion,'test':PREFIX+'EMPIRICAL-TESTS.md',
            'independent_check':PREFIX+'review/REVIEW.md'}


def main():
    out=PACKAGE/'CLAIM-EVIDENCE.json'
    if out.exists():raise SystemExit('Claim map exists; no overwrite.')
    m='material/observations.json';t='texts/OBSERVATIONS.json';r='review/observations-v2.json';c='coordinator/observations-v2.json'
    claims=[
      claim('P01','Operation, organizing relationship, terminology and explanation can have different histories; a later repertoire can combine multiple contributions.','Developed historical hypothesis with direct methodological and comparative precedents',
            [obs(c,'C-O06','C-O07','C-O08'),obs(r,'O-R07-2','O-R05-1')],discussion='THEORY.md'),
      claim('P02','Bhagwanpura supplies unfinished working-stage beads and an author-attributed local-production inference; BPR-208 remains one accession with conflicting material descriptions.','Source-qualified intermediate object observations and attributed interpretation',
            [obs(m,'MO12','MO13','MO14')]),
      claim('P03','The Harappa bead pot contains objects from several occupation phases; its deposition date cannot independently date every bead operation.','Source-qualified curated-collection control',
            [obs(m,'MO01','MO03','MO04')]),
      claim('P04','Hulas has described forming/joining/trimming traces, while Bhagwanpura already proposes learning between neighboring makers; recipe succession and teaching remain unresolved.','Material reconstruction and credited source-author hypothesis',
            [obs(m,'MO06','MO15','MO16','MO18')]),
      claim('P05','Jognakhera directly dated barley, Vigna and rice at the published ranges, while individual layer joins and same-field rotation remain unresolved in the inspected records.','Published specimen dates and explicit inference limits; no recalculation',
            [obs(m,'MO22','MO23','MO24','MO25')],
            [output(m,'/observations/22/date_evidence/barley_cal_BCE',equals=[2471,2298]),
             output(m,'/observations/22/date_evidence/Vigna_cal_BCE',equals=[1880,1691]),
             output(m,'/observations/22/date_evidence/rice_cal_BCE',equals=[1517,1428]),
             output(m,'/observations/22/date_evidence/probability',equals=0.954)]),
      claim('P06','RV 10.101 represents agricultural and water acts within a full ritual/poetic context; the selected material records do not identify the same linked technical sequence.','Whole-hymn reading and operation-level comparison',
            [obs(t,'TX-RV10.101.3','TX-RV10.101.5','TX-RV10.101.7','TX-RV10.101.11','TX-RV10.101.12'),obs(m,'MO17','MO24')]),
      claim('P07','RV 9.112 depicts differentiated work, clients and household tasks; a narrow uniquely local institutional inference is weakened by other specialist comparisons.','Textual depiction and bounded rival test; broad local compatibility retained',
            [obs(t,'TX-RV9.112.1','TX-RV9.112.3','TX-RV9.112.4','TX-OD17-ROLES'),obs(r,'O-R01-1')],
            [output('coordinator/run-v1/audit.json','/comparisons/3/rival_relations/R1',equals='counter_observation_under_stated_assumption')]),
      claim('P08','RV 10.71 depicts competence, companionship and differentiated collective work; inherited Indo-Iranian poet/ritual-role accounts are independently motivated for part of that repertoire.','Textual observations and attributed comparative reconstruction',
            [obs(t,'TX-RV10.71.4','TX-RV10.71.6','TX-RV10.71.8','TX-RV10.71.10','TX-RV10.71.11'),obs(r,'O-R01-1','O-R02-1','O-R02-2','O-R02-4','O-R07-1')]),
      claim('P09','RV 10.71.2 explicitly uses sifting meal to depict shaping speech, supporting represented practical-to-conceptual incorporation without identifying its donor.','Direct textual association; post-reading refinement within the fixed frame',
            [obs(t,'TX-RV10.71.2','TX-RV10.71.3','TX-RV10.71.11')],
            [output('coordinator/run-v1/audit.json','/comparisons/5/decision',equals='supported_endpoint')]),
      claim('P10','DN 1 classifies varied arts through a livelihood norm at its own textual stage; the classification does not demonstrate a traced Harappan package or a particular earlier-text redaction.','Later non-Vedic textual organization with retained chronology',
            [obs(t,'TX-DN1-NORM','TX-DN1-CALC','TX-DN1-TREAT')]),
      claim('P11','Demographic relationships can constrain contact opportunities without identifying a particular taught recipe, office or literary transfer.','Published scope and inferential distinction, not genetic reanalysis',
            [obs(c,'C-O01','C-O02','C-O03','C-O04'),obs(r,'O-R04-1','O-R04-2','O-R04-3','O-R04-4')]),
      claim('P12','The seven source-based component comparisons record 35 rival statements and assert no traced local Harappan literary descent.','Manual exploratory comparison endpoint; no historical likelihood estimate',
            [],[output('coordinator/run-v1/audit.json','/checks_passed',equals=297),
                 *[output('coordinator/run-v1/audit.json',f'/comparisons/{i}/claims_traced_local_literary_descent',equals=False) for i in range(7)]],discussion='REPORT.md'),
      claim('P13','The validator verifies IDs and declarations, while a deliberate mislabeling fixture passes despite an unsupported teaching interpretation.','Actual software scope test with an expressly hypothetical claim, excluded from historical evidence',
            [],[output('review/validator-scope-v2/interpretation.json','/expected_limitation_observed',equals=True)],discussion='REVIEW-RESPONSE.md'),
      claim('P14','Selective practical survival, recoding and conceptual integration predict component-specific operation and carrier histories that can be tested with new comparisons.','Exploratory mechanism and prospective tests; no authenticated lineage',
            [obs(m,'MO06','MO07','MO17','MO20'),obs(t,'TX-RV10.71.2','TX-RV10.71.6'),obs(c,'C-O05','C-O07')],discussion='THEORY.md')
    ]
    with out.open('x',encoding='utf-8') as stream:
        json.dump({'scope':'Synthesis claims distinguish observed endpoints, attributed arguments, exploratory mechanisms and software checks. Source editions and shared excavation lineages remain dependent.',
                   'claims':claims},stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'claims':len(claims),'exact_output_joins':sum(len(c['outputs']) for c in claims)}))


if __name__=='__main__':main()
