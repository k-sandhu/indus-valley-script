"""Full nested metadata null conditioned on complete-string uniqueness.

Post-pilot sampling-rule sensitivity; no historical result is overwritten.
Rejection samples the ordinary exact-column permutation reference conditional
on all resulting whole texts being distinct. Physical aliases remain retained.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np

from conditional_structure import digest, load_records, shuffle_positions
from nested_joint_null import fit


def main(args):
    started = time.monotonic()
    rows, excluded = load_records(args.input, 3, True, False, None)
    assert len({r['seq'] for r in rows}) == len(rows)
    observed, grouping = fit(rows, args.seed)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    result = {'design': 'Post-pilot full nested metadata permutation reference conditioned on whole-string uniqueness',
              'parameters': vars(args), 'input_sha256': digest(args.input),
              'source_sha256': digest(__file__),
              'loader_source_sha256': digest(Path(__file__).with_name('conditional_structure.py')),
              'nested_source_sha256': digest(Path(__file__).with_name('nested_conditional.py')),
              'fit_source_sha256': digest(Path(__file__).with_name('nested_joint_null.py')),
              'exclusions': excluded, 'observed': observed, 'observed_grouping': grouping,
              'scope': 'One original representative per global complete string, retaining all physical aliases. Exact length-position-site-type column permutations are rejection-sampled conditional on no resulting identical complete strings. Grouping, fold allocation, inner smoothing selection and all held-out prediction repeat for every accepted corpus. This tests the selected unique-text transcription population, not a random archaeological population or linguistic status.'}
    values, accepted_seeds, group_counts, sizes = [], [], [], []
    attempts = 0

    def save(complete=False):
        null = {'in_progress': not complete, 'permutations': len(values),
                'attempts': attempts, 'accepted_seeds': accepted_seeds,
                'uniqueness_conditioned': True, 'values': values,
                'p_one_sided': (1 + sum(v >= observed['gain_bits_per_noninitial_sign'] for v in values))/(1+len(values))}
        if values:
            null.update({'mean': float(np.mean(values)),
                         '95pct_range': [float(x) for x in np.quantile(values,[.025,.975])],
                         'null_group_count_range': [min(group_counts), max(group_counts)],
                         'null_largest_group_range': [min(sizes), max(sizes)],
                         'mobility': mobility})
        result['null_position_metadata'] = null
        result['elapsed_seconds'] = time.monotonic() - started
        (output/'joint_nested_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

    save()
    print(json.dumps({'stage':'observed_unique_conditioned', 'gain':observed['gain_bits_per_noninitial_sign'], 'grouping':grouping}),flush=True)
    for p in range(args.permutations):
        while True:
            null_seed = args.seed + 10000 + attempts
            attempts += 1
            shuffled, mobility = shuffle_positions(rows,null_seed,True)
            if len({r['seq'] for r in shuffled}) == len(shuffled):
                break
            if attempts >= args.max_attempts:
                raise RuntimeError('Declared rejection attempt budget exhausted')
        score, info = fit(shuffled,args.seed)
        values.append(score['gain_bits_per_noninitial_sign'])
        accepted_seeds.append(null_seed)
        group_counts.append(info['groups']); sizes.append(info['largest_group'])
        if (p+1)%25 == 0:
            save()
            print(json.dumps({'stage':'unique_conditioned_nested_null','done':p+1,'total':args.permutations,'attempts':attempts,'seconds':result['elapsed_seconds']}),flush=True)
    save(True)
    print(json.dumps({'stage':'complete_unique_conditioned_nested_null','output':str(output),'null':{k:v for k,v in result['null_position_metadata'].items() if k not in {'values','accepted_seeds'}},'seconds':result['elapsed_seconds']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--permutations',type=int,default=1000)
    parser.add_argument('--seed',type=int,default=20261001)
    parser.add_argument('--max-attempts',type=int,default=1000000)
    main(parser.parse_args())
