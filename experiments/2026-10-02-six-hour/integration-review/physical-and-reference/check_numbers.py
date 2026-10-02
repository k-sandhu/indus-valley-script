"""Read-only integration checks on saved summaries; no scientific refits."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
EXP=ROOT/'experiments/2026-10-02-six-hour'
checks=[];sources={}


def read(relative):
    path=EXP/relative;sources[relative]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return json.loads(path.read_text(encoding='utf-8'))


def check(label,value,expected,source):
    assert value==expected,(label,value,expected)
    checks.append({'claim':label,'actual':value,'expected':expected,'source':source,'passed':True})


def rounded(label,value,digits,expected,source):check(label,round(value,digits),expected,source)


def main():
    name='null-calibration/main/results.json';x=read(name)
    for key,value in [('datasets_per_family',1000),('reference_draws',99),('completed_datasets',3000),('total_fitted_reference_corpora',396000),('total_rejection_proposals',928424)]:check(key,x[key],value,name)
    for family,rates in [('independent_records/record_columns',[.011,.05,.099]),('unique_records/unique_record_columns',[.011,.059,.106]),('physical_copies/block_columns',[.011,.054,.103]),('physical_copies/record_columns',[.048,.159,.27])]:
        check(family+' rejection rates',[x['aggregate'][family]['rejections'][str(c)]['rate'] for c in [.01,.05,.1]],rates,name)
    for family,interval in [('physical_copies/block_columns',[4.162,6.979]),('physical_copies/record_columns',[13.765,18.296])]:check(family+' Wilson percent interval',[round(v*100,3) for v in x['aggregate'][family]['rejections']['0.05']['wilson_95_ci']],interval,name)
    name='null-calibration/paired_seed_audit.json';x=read(name)
    check('literal-copy linked clusters',len(x['linked_trial_pairs']),500,name);check('literal-copy paired interval',x['paired_rejection']['0.05']['cluster_bootstrap_95_interval'],[.085,.126],name);check('literal-copy paired difference',x['paired_rejection']['0.05']['record_minus_block_rate'],.105,name);check('paired bootstrap draws',x['bootstrap_replicates'],20000,name)
    name='null-calibration/noisy-faces/verification_main.json';x=read(name)
    check('imperfect-face populations',x['datasets_checked'],1000,name);check('imperfect-face references',x['reference_corpora_checked'],198000,name);check('noisy paired interval',x['paired_rejection']['0.05']['paired_95_interval'],[.043,.077],name);check('noisy paired cells',[x['paired_rejection']['0.05'][k] for k in ['both','record_only','vector_only','neither']],[41,69,9,881],name)
    for key,value in [('equal_face_slots',48821),('total_object_slots',60000),('equal_face_strings',10817),('total_objects',20000),('replaced_face_slots',11868),('total_face_slots',120000)]:check(key,x[key],value,name)
    name='null-calibration/exact/results.json';x=read(name)
    check('ordinary tables',x['space_summaries']['record_columns']['tables'],8000,name);check('unique tables',x['space_summaries']['unique_columns']['tables'],2880,name);check('unique acceptance',x['unique_acceptance_probability'],.36,name);check('unique nested 5% rate',x['space_summaries']['unique_nested_full_procedure']['exact_rejection_rates']['0.05'],.05,name)
    name='null-calibration/dedup-selection/results.json';x=read(name)
    e=x['endpoints']['nested_full_procedure'];rounded('uniform reference under selected law (%)',100*float(F(e['uniform_reference_under_selected_law']['rates']['0.05'])),4,5.1537,name);rounded('selected reference under selected law (%)',100*float(F(e['selected_reference_under_selected_law']['rates']['0.05'])),4,4.9407,name);rounded('greatest attainable excess (points)',100*float(F(e['uniform_reference_under_selected_law']['greatest_attainable_excess']['departure'])),4,.6046,name)
    name='null-calibration/unequal-copy-counts/results.json';x=read(name)
    check('weighted legal columns',x['both_margin_columns'],6,name);check('weighted tables',x['both_margin_three_column_tables'],216,name);rounded('direct sampling diagnostic is p-value',x['direct_sampling']['diagnostic_p'],5,.01336,name);check('chi-square statistic',x['direct_sampling']['chi_square'],263.51936,name)
    name='null-calibration/domain-support/support-bound/results.json';x=read(name)
    for key,value in [('datasets',3000),('reference_groupings',396000)]:check('support '+key,x[key],value,name)
    check('support allocation cases',x['allocation']['cases'],29169,name);check('independent bound',x['reference_cases']['independent_records/record_columns']['component_bound_range'],[8,8],name);check('copy bound',x['reference_cases']['physical_copies/block_columns']['component_bound_range'],[6,8],name);check('record-copy premise violations',x['reference_cases']['physical_copies/record_columns']['whole_string_physical_premise_violations'],99000,name)
    name='null-calibration/domain-support/guard-exact/results.json';x=read(name)
    for key,value in [('tables',8000),('feasible_tables',5760),('abstentions',2240),('new_fits',2880),('reused_fits',2880)]:check('guard '+key,x[key],value,name)
    for cutoff,expected in [('.01',[.3250,.4514,.4514,.3250]),('.05',[5.,6.9444,4.7917,3.45]),('.1',[9.875,13.7153,9.9653,7.175])]:
        key=str(float(cutoff));check('guard rates '+key,[round(100*v['rate'],4) for v in x['endpoints'][key].values()],expected,name)
    name='null-calibration/noisy-channel/main/results.json';x=read(name)
    check('channel populations',x['populations'],1000,name);check('pairs per population',x['pairs_per_population'],60,name)
    for key,value in [('agreement_bias',.099261),('joint_unknown_bias',.101605)]:rounded('channel mean '+key,.1+x['summary'][key]['mean'],6,value,name)
    for key,value in [('agreement_absolute_error',.023162),('joint_unknown_absolute_error',.022195),('joint_unknown_channel_total_variation',.245280),('agreement_projected_total_variation',.334097),('smoothed_marginal_total_variation',.227690)]:rounded(key,x['summary'][key]['mean'],6,value,name)
    check('known-rate negative components',x['negative_inversions']['known_channel']['components'],10335,name);check('affected cells',x['negative_inversions']['known_channel']['cells'],5466,name)
    rounded('pooled joint TV',x['pooled_frequency_metrics']['joint_unknown_channel']['total_variation'],6,.012236,name);rounded('pooled raw TV',x['pooled_frequency_metrics']['observed_marginal']['total_variation'],6,.020967,name)
    name='physical-information/main-corrected-anchor/results.json';x=read(name)
    for key,value in [('symbols',6),('training_assemblies_per_world',12),('withheld_assemblies_per_world',8)]:check('PHYS-01 '+key,x[key],value,name)
    check('PHYS-01 base collections',len(x['seeds']),24,name)
    for prefix,finite,relative in [(3,12,0),(8,24,23),(12,24,24)]:
        row=next(r for r in x['summary'] if r['scenario']=='complete_membership' and r['training_relations']==prefix);check('finite at '+str(prefix),row['finite_unique_worlds'],finite,name);check('relative at '+str(prefix),row['true_relative_values_recovered_worlds'],relative,name)
    name='physical-acquisition/main-analysis/analysis.json';x=read(name)
    check('PHYS-02 policy paths',x['policy_records'],360,name)
    for condition,counts in [('complete_exact',[23,15,0]),('incomplete',[22,17,1]),('valid_intervals',[1,1,0]),('undercovered_counts',[0,0,0]),('ownership',[0,0,0])]:
        rows=[r for r in x['rows'] if r['condition']==condition]
        check(condition+' recovery',[r['correct_absolute_identified'] for r in rows],counts,name)
    name='physical-acquisition/precision-analysis/analysis.json';x=read(name)
    check('fresh interval paths',x['policy_records'],96,name)
    check('fresh recovery',[r['correct_absolute_identified'] for r in x['rows']],[0,0,0,6],name)
    check('fresh mean widths',[x['rows'][0]['bounded_scale_width_mean'],x['rows'][-1]['bounded_scale_width_mean']],['47/192','1765/10368'],name)
    name='khipu-control/source-verification.json';x=read(name)
    check('source predictions',x['predictions_checked'],20411,name);check('source sums',[x['grand_total_source'],x['grand_total_target']],[3498,3482],name)
    name='khipu-control/robust-decoder/main-v1/aggregate.json';x=read(name)
    check('KHI-03 seeds',x['base_seeds'],300,name);check('KHI-03 prefixes',x['prefix_states'],12000,name)
    for condition,method,c,w,a,r in [('two_swapped','three_quarter',281,4,15,0),('four_swapped','half',200,16,84,0),('four_swapped','three_quarter',1,1,1,297)]:
        row=next(v for v in x['rows'] if v['condition']==condition and v['method']==method and v['prefix']==8);check(condition+'/'+method,[row.get(k,0) for k in ['accepted_correct','accepted_wrong','abstained_ambiguity','rejected_support']],[c,w,a,r],name)
    name='khipu-control/conservation-check/main-v1/aggregate.json';x=read(name)
    check('KHI-04 seeds',x['base_seeds'],200,name);check('KHI-04 worlds',x['worlds'],1400,name);check('KHI-04 prefixes',x['prefix_records'],11200,name)
    for condition,policy,c,w,a,r in [('two_swapped','baseline_half',189,2,9,0),('two_swapped','collective_half',197,0,3,0),('four_swapped','baseline_half',133,9,58,0),('four_swapped','collective_half',190,1,9,0),('missing_pool_misdeclared','collective_half',0,15,1,184)]:
        row=next(v for v in x['rows'] if v['condition']==condition and v['policy']==policy and v['prefix']==8);check(condition+'/'+policy,[row.get(k,0) for k in ['correct_relative','wrong_relative','abstained_ambiguity','rejected_support']],[c,w,a,r],name)
    name='khipu-control/validation-design/main-v1/aggregate.json';x=read(name)
    for view,policy,budget,remaining in [('counted','account_first',3,1),('unmeasured','account_first',3,1),('counted','greedy_rank',2,0),('unmeasured','greedy_rank',3,0),('counted','count_first',1,0),('unmeasured','count_first',1,9),('unmeasured','count_first',2,0)]:
        row=next(r for r in x['rows'] if r['condition']=='four_swapped' and r['fitter_policy']=='baseline_half' and r['view']==view and r['selection_policy']==policy and r['budget']==budget);check('validation wrong remaining '+str((view,policy,budget)),row['metrics'].get('original_wrong_compatible','0'),str(remaining),name)
    wrong=[F(645,23),F(860,23),F(14190,23)];check('first count fits wrong scale',str(6*wrong[1]+8*wrong[2]),'5160',name);check('second count residual',str(6*wrong[0]+6*wrong[1]+3*wrong[2]-2196),'1092/23',name)
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Saved-summary arithmetic and integration checks; no fits or experiments rerun','passed':True,'checks':checks,'source_files':sources,'check_count':len(checks)}
    p=OUT/'numerical-checks.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'checks':len(checks),'source_files':len(sources)}))


if __name__=='__main__':main()
