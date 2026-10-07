"""Load the fixed carry-forward payloads and predict slots without tuning."""
import argparse
import json
import pickle
from pathlib import Path
import numpy as np
import torch
from data import ROOT, OWN, RAW, UNKNOWN, digest
from models import MaskedNet, DEVICE, predict_net
from run import geometric

class FrozenPredictor:
    def __init__(self, manifest=None):
        self.record = json.loads(Path(manifest or OWN / 'frozen-model/manifest.json').read_text(encoding='utf-8'))
        for name, expected in self.record['code_sha256'].items():
            assert digest(OWN / name) == expected, f'Frozen code changed: {name}'
        dependencies = json.loads((OWN / 'frozen-model/code-dependencies.json').read_text(encoding='utf-8'))
        for entry in dependencies['repository_dependencies']:
            assert digest(ROOT / entry['path']) == entry['sha256'], f'Frozen dependency changed: {entry["path"]}'
        self.classical, self.neural = None, []
        for entry in self.record['files']:
            path = ROOT / entry['path']
            assert digest(path) == entry['sha256']
            if path.suffix == '.pkl':
                with path.open('rb') as f:
                    self.classical = pickle.load(f)
            else:
                # These are our own local checkpoints, identified by the manifest hash.
                checkpoint = torch.load(path, map_location=DEVICE, weights_only=False)
                encoder = checkpoint['encoder']
                model = MaskedNet(encoder, **checkpoint['config']).to(DEVICE)
                model.load_state_dict(checkpoint['state_dict'])
                self.neural.append((model, encoder))
        self.signs = self.classical.signs if self.classical is not None else self.neural[0][1].signs
        assert self.signs[-1] == UNKNOWN
        assert all(e.signs == self.signs for _, e in self.neural)

    def predict_all_slots(self, rows):
        a = self.classical.predict(rows) if self.classical is not None else None
        b = np.mean([predict_net(m, e.dataset(rows)) for m, e in self.neural], axis=0) if self.neural else None
        if a is not None and b is not None:
            return geometric(a, b, self.record['recipe']['ngram_weight'])
        return a if a is not None else b

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Local JSONL with seq arrays and optional metadata.')
    parser.add_argument('--output', required=True, help='New JSONL inside the assigned raw directory.')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    assert output.is_relative_to(RAW.resolve())
    if output.exists():
        raise FileExistsError(output)
    rows = [json.loads(s) for s in Path(args.input).read_text(encoding='utf-8').splitlines() if s.strip()]
    assert rows and all(row.get('seq') and all(isinstance(code, str) for code in row['seq']) for row in rows), 'seq must contain string graphic codes.'
    predictor = FrozenPredictor()
    probs = predictor.predict_all_slots(rows)
    records, j = [], 0
    for row in rows:
        for slot in range(len(row['seq'])):
            order = np.argsort(-probs[j], kind='stable')[:10]
            records.append({'record_id': row.get('record_id'), 'slot': slot,
                'suggestions': [{'code': predictor.signs[k], 'mass': float(probs[j, k])} for k in order]})
            j += 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')

if __name__ == '__main__':
    main()
