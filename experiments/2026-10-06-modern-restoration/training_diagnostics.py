"""Aggregate fit durations, training caps and parameters without model retuning."""
import argparse
from collections import defaultdict
from data import OWN, save
from run import read_json
import numpy as np

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', default='main')
    p.add_argument('--output', default='training-diagnostics.json')
    args = p.parse_args()
    groups = defaultdict(list)
    files = []
    for path in sorted((OWN / args.run).glob('*-s*.json')):
        record = read_json(path)
        if 'history' not in record or 'config' not in record:
            continue
        config = record['config']
        phase = 'inner' if '-inner' in path.name else 'curve' if path.name.startswith('curve') else 'outer'
        family = config['family'] + ('+metadata' if config.get('metadata') else '')
        width = config['width']; extra = 'extra1' if '-extra1-' in path.name else 'extra0'
        groups[family, width, extra, phase].append(record)
        files.append(path.name)
    result = {'fit_records': len(files), 'groups': {}}
    for key, values in groups.items():
        epochs = [v['epochs'] for v in values]
        key_name = '/'.join(map(str, key))
        result['groups'][key_name] = {'fits': len(values), 'selected_epoch_min': min(epochs),
            'selected_epoch_median': float(np.median(epochs)), 'selected_epoch_max': max(epochs),
            'selected_at_maximum_45': sum(e == 45 for e in epochs),
            'training_ran_45': sum(len(v['history']) == 45 for v in values),
            'seconds_sum': sum(v['seconds'] for v in values),
            'parameters_min': min(v['parameters'] for v in values), 'parameters_max': max(v['parameters'] for v in values)}
    save(OWN / args.output, result)
    print(result['fit_records'])

if __name__ == '__main__':
    main()
