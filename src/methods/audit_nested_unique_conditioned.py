"""Verify completed unique-conditioned nested null and immutable provenance."""
import json
from pathlib import Path

import numpy as np

from conditional_structure import digest


def main():
    base=Path('research/methods/results/joint_nested_unique_conditioned_1000')
    path=base/'joint_nested_results.json'
    result=json.loads(path.read_text())
    null=result['null_position_metadata']
    assert not null['in_progress'] and null['permutations']==1000
    values=np.array(null['values'])
    assert len(values)==1000 and np.isfinite(values).all()
    assert null['uniqueness_conditioned']
    assert len(null['accepted_seeds'])==1000 and len(set(null['accepted_seeds']))==1000
    assert null['accepted_seeds']==sorted(null['accepted_seeds'])
    transfer=json.loads(Path('research/methods/results/joint_transfer_unique_conditioned/joint_null_results.json').read_text())
    assert null['accepted_seeds']==transfer['null_position_metadata']['accepted_seeds']
    assert null['attempts']==transfer['null_position_metadata']['attempts']
    prior=json.loads(Path('research/methods/results/nested_unique_preserved_aliases/nested_results.json').read_text())
    for key in ['gain_bits_per_noninitial_sign','relative_perplexity','baseline_noninitial_cross_entropy_bits','dependent_noninitial_cross_entropy_bits','records','groups','noninitial_tokens','folds']:
        assert result['observed'][key]==prior['observed'][key]
    current=Path(__file__).parent
    checks={'source_sha256':current/'nested_unique_conditioned.py',
            'loader_source_sha256':current/'conditional_structure.py',
            'nested_source_sha256':current/'nested_conditional.py',
            'fit_source_sha256':current/'nested_joint_null.py',
            'input_sha256':Path(result['parameters']['input'])}
    assert all(digest(p)==result[k] for k,p in checks.items())
    observed=result['observed']['gain_bits_per_noninitial_sign']
    exceedances=int((values>=observed).sum())
    assert null['p_one_sided']==(1+exceedances)/1001
    assert abs(null['mean']-float(values.mean()))<1e-14
    assert np.allclose(null['95pct_range'],np.quantile(values,[.025,.975]),rtol=0,atol=1e-14)
    assert null['null_group_count_range']==[result['observed_grouping']['groups']]*2
    assert null['null_largest_group_range']==[result['observed_grouping']['largest_group']]*2
    audit={'complete_1000_verified':True,'source_and_input_hashes_match':True,
           'observed_fold_scores_equal_alias_preserving_prior':True,
           'all_accepted_seeds_and_attempts_match_previous_rejection_sampler':True,
           'result_sha256':digest(path),'exceedances':exceedances,
           'permutations':len(values),'attempts':null['attempts'],
           'elapsed_seconds':result['elapsed_seconds'],'reference_p':null['p_one_sided'],
           'null_mean':null['mean'],'null_95pct_range':null['95pct_range']}
    (base/'completion_audit.json').write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit,indent=2))


if __name__=='__main__':
    main()
