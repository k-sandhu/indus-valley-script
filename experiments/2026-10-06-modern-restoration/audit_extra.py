"""Independent breadth-first reachability audit of the extra-text exclusions."""
import json
import argparse
from collections import defaultdict, deque
from data import Corpus, ROOT, OWN, RAW, save

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', default='extra-graph-audit.json')
    p.add_argument('--witness-name', default='extra-graph-witnesses.json')
    args = p.parse_args()
    c = Corpus()
    rows = []
    for r in c.raw:
        r = dict(r)
        r['seq'] = tuple(map(str, r.get('signs_reading_rtl', [])))
        r['artifact'] = str(r.get('object_family_id', r.get('artifact_id', r['record_id'])))
        r['artifact_aliases'] = list(map(str, r.get('artifact_aliases', [r['artifact']])))
        if r['artifact'] not in r['artifact_aliases']:
            r['artifact_aliases'].append(r['artifact'])
        rows.append(r)
    rawcount = len(rows)
    rows += c.rows
    nodes = defaultdict(list)
    row_nodes = []
    for i, r in enumerate(rows):
        keys = [('object', a) for a in r['artifact_aliases']]
        if r['seq']:
            keys.append(('string', r['seq']))
        row_nodes.append(keys)
        for key in keys:
            nodes[key].append(i)
    def reach(held):
        selected = {rawcount + j for j, r in enumerate(c.rows) if r['record_id'] in held}
        queue = deque(selected); touched = set()
        while queue:
            current = queue.popleft()
            for key in row_nodes[current]:
                if key in touched:
                    continue
                touched.add(key)
                for neighbor in nodes[key]:
                    if neighbor not in selected:
                        selected.add(neighbor); queue.append(neighbor)
        return selected
    result = {'status': 'Verified computation', 'algorithm': 'Breadth-first row/object/string graph traversal', 'outer': [], 'inner': []}
    witnesses = []
    eligible_ids = {r['record_id'] for r in c.candidates}
    for f in range(5):
        train, test, more, detail = c.outer(f)
        reached = reach({r['record_id'] for r in test})
        excluded_ids = {rows[i]['record_id'] for i in reached if i < rawcount and rows[i]['record_id'] in eligible_ids}
        assert len(excluded_ids) == detail['excluded_connected_faces']
        assert not {r['record_id'] for r in more} & excluded_ids
        joined = [rows[i]['record_id'] for i in reached if i >= rawcount and rows[i]['record_id'] in {r['record_id'] for r in train}]
        result['outer'].append({'fold': f, 'excluded_candidate_faces_bfs': len(excluded_ids),
            'added_distinct_texts': len(more), 'added_tokens': sum(len(r['seq']) for r in more),
            'benchmark_training_texts_connected_under_full_export_graph': len(joined),
            'extra_connected_violations': 0})
        witnesses.append({'fold': f, 'benchmark_train_ids_connected': joined,
            'excluded_extra_candidate_ids': sorted(excluded_ids)})
        for inner, (fit, val, extra, current) in enumerate(c.inner(f)):
            reached = reach({r['record_id'] for r in test + val})
            excluded = {rows[i]['record_id'] for i in reached if i < rawcount and rows[i]['record_id'] in eligible_ids}
            assert len(excluded) == current['excluded_connected_faces']
            assert not {r['record_id'] for r in extra} & excluded
            result['inner'].append({'fold': f, 'inner': inner, 'excluded_faces': len(excluded),
                'added_texts': len(extra), 'added_tokens': sum(len(r['seq']) for r in extra), 'violations': 0})
    save(RAW / args.witness_name, witnesses)
    save(OWN / args.output, result)
    print(json.dumps(result['outer'], indent=2))

if __name__ == '__main__':
    main()
