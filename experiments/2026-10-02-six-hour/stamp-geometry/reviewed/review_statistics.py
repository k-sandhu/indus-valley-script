"""Reproduce the empty-pool representation review without editing endpoints."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


def review(parent):
    result = deepcopy(parent)
    changes = []
    for minimum, layouts in result['minimum_visible_graphics_pools'].items():
        for slots, groups in layouts.items():
            for name, group in groups.items():
                defined = group['mean_selected_row_probability'] > 0
                group['endpoint_distribution_defined'] = defined
                if not defined:
                    for field in ('first_class_distribution', 'last_class_distribution',
                                  'visible_class_distribution', 'left_right_endpoint_tv'):
                        group[field] = None
                    changes.append({'minimum': int(minimum), 'slots': int(slots),
                                    'pool': name})
    return result, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError('Preserve the existing reviewed result.')
    parent = json.loads(args.parent.read_text(encoding='utf-8'))
    result, changes = review(parent)
    result['parent_results_path'] = '../analytic-refinement/results.json'
    result['parent_results_sha256'] = hashlib.sha256(args.parent.read_bytes()).hexdigest()
    result['reviewed_status'] = 'Empty selected populations have undefined endpoint distributions and total variation.'
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'undefined_pools': changes}, indent=2))


if __name__ == '__main__':
    main()
