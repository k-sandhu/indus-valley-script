"""Exercise the frozen loader and hidden-slot invariance on local sample strings."""
import json
import argparse
import numpy as np
from data import Corpus, OWN, RAW, save, digest
from inference import FrozenPredictor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', default='frozen-inference')
    args = parser.parse_args()
    corpus = Corpus()
    selected = sorted(corpus.rows, key=lambda r: (len(r['seq']), r['record_id']))
    rows = [selected[0], selected[len(selected) // 2], selected[-1]]
    predictor = FrozenPredictor()
    lineage = []
    for name in ['data.py', 'models.py', 'run.py']:
        snapshot = OWN / 'main/code-snapshots' / name
        assert (OWN / name).read_bytes() == snapshot.read_bytes()
        lineage.append({'file': name, 'matches_pre_fit_snapshot': True,
            'sha256': digest(snapshot)})
    probabilities = predictor.predict_all_slots(rows)
    assert np.isfinite(probabilities).all()
    assert np.all(probabilities >= 0)
    assert np.allclose(probabilities.sum(axis=1), 1, atol=1e-6)
    checks, offset, largest, batch_difference = 0, 0, 0.0, 0.0
    for row in rows:
        reference = predictor.predict_all_slots([row])
        batch_difference = max(batch_difference, float(np.max(np.abs(
            probabilities[offset:offset + len(row['seq'])] - reference))))
        assert np.allclose(probabilities[offset:offset + len(row['seq'])], reference,
            atol=1e-6, rtol=1e-6)
        for slot in range(len(row['seq'])):
            changed = dict(row)
            seq = list(row['seq'])
            seq[slot] = '__hidden_replacement__'
            changed['seq'] = seq
            replaced = predictor.predict_all_slots([changed])[slot]
            difference = float(np.max(np.abs(reference[slot] - replaced)))
            largest = max(largest, difference)
            assert np.array_equal(reference[slot], replaced)
            checks += 1
        offset += len(row['seq'])
    witness = RAW / f'{args.prefix}-sample.jsonl'
    if witness.exists():
        raise FileExistsError(witness)
    witness.write_text(''.join(json.dumps({k: row.get(k) for k in
        ['record_id', 'seq', 'object_type', 'site', 'region', 'symbol']}) + '\n'
        for row in rows), encoding='utf-8')
    save(OWN / f'{args.prefix}-verification.json', {
        'status': 'Verified computation',
        'purpose': 'Loader, payload hash, normalization and replacement checks; no evaluation score.',
        'sample_strings': len(rows), 'sample_slots': checks,
        'maximum_probability_change': largest,
        'maximum_batch_probability_change': batch_difference,
        'hidden_replacement_exactly_unchanged': True,
        'refinement_status': 'Exploratory verification refinement: separate mixed-batch rounding from fixed-batch hidden replacement.',
        'payload_and_code_hashes_passed': True,
        'fitting_source_correspondence': lineage,
        'sample_witness': str(witness.relative_to(OWN.parents[1])).replace('\\', '/'),
    })
    print(json.dumps({'sample_strings': len(rows), 'sample_slots': checks,
        'maximum_probability_change': largest}))


if __name__ == '__main__':
    main()
