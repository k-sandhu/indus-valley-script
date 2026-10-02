"""Exact label-symmetry demonstration on synthetic data, not an Indus decoder."""
from collections import Counter
from itertools import permutations
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]

def score(texts):
    unigram = Counter(sign for text in texts for sign in text)
    starts = Counter(text[0] for text in texts)
    pairs = Counter(pair for text in texts for pair in zip(text, text[1:]))
    outgoing = Counter()
    for (first, _), count in pairs.items():
        outgoing[first] += count
    k = len(unigram)
    bits = 0.0
    for text in texts:
        bits -= math.log2((starts[text[0]] + 1) / (len(texts) + k))
        for first, second in zip(text, text[1:]):
            bits -= math.log2((pairs[first, second] + 1) / (outgoing[first] + k))
    total = sum(unigram.values())
    entropy = -sum((count / total) * math.log2(count / total) for count in unigram.values())
    return bits, entropy, sorted(pairs.values())

def main():
    texts = [[0,1,2,5], [0,1,3,5], [0,4,2,5], [4,1,2,5], [0,3,5], [4,3,2,5]] * 3
    reference = score(texts)
    diffs = []
    entropy_diffs = []
    graph_equal = []
    count_with_two_anchors = 0
    for perm in permutations(range(6)):
        encoded = [[perm[sign] for sign in text] for text in texts]
        candidate = score(encoded)
        diffs.append(abs(reference[0] - candidate[0]))
        entropy_diffs.append(abs(reference[1] - candidate[1]))
        graph_equal.append(reference[2] == candidate[2])
        count_with_two_anchors += perm[0] == 0 and perm[5] == 5
    result = {
        "experiment_id": "CRYPTO-01", "population": "synthetic six-symbol sequences",
        "status": "exact demonstration; not archaeological evidence",
        "texts": len(texts), "tokens": sum(map(len,texts)), "bijections": len(diffs),
        "max_fitted_markov_score_difference_bits": max(diffs),
        "max_unigram_entropy_difference_bits": max(entropy_diffs),
        "all_edge_count_multisets_equal": all(graph_equal),
        "remaining_maps_with_two_fixed_sign_identities": count_with_two_anchors,
        "assumption": "relabel observations and fitted model consistently; no external semantic grounding",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "interpretation": "self-fitted permutation-equivariant structural scores cannot identify arbitrary semantic labels; external constraints may reduce this ambiguity",
        "limitations": "does not establish exact symmetry for a multimodal grounded model, nor impossibility of Indus decipherment",
    }
    assert result["bijections"] == math.factorial(6)
    assert max(diffs) < 1e-12 and max(entropy_diffs) < 1e-12
    assert all(graph_equal) and count_with_two_anchors == math.factorial(4)
    output = ROOT / "experiments/2026-10-02-cryptography-framing/results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
