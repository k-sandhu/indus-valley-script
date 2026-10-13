"""Inspect a frozen prefix prediction without revealing future target codes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from grammar import Alphabet, Grammar, Markov, Position, SignCounts, digest, load_corpus
import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]


def main(args):
    manifest = json.loads((PACKAGE / "carry-forward.json").read_text())
    source = ROOT / manifest["input_path"]
    if digest(source) != manifest["input_sha256"]:
        raise ValueError("The local input differs from the frozen corpus pin.")
    rows, _ = load_corpus(source)
    weights_path = ROOT / manifest["local_class_model_path"]
    if digest(weights_path) != manifest["local_class_model_sha256"]:
        raise ValueError("The full descriptive class model differs from the frozen arrays.")
    saved = np.load(weights_path, allow_pickle=False)
    grammar = object.__new__(Grammar)
    grammar.alphabet = Alphabet(rows)
    assert grammar.alphabet.signs == saved["signs"].tolist()
    grammar.states, grammar.emission_strength, contextual = saved["configuration"].tolist()
    grammar.contextual = bool(contextual)
    grammar.initial, grammar.transition, grammar.emission = saved["initial"], saved["transition"], saved["emission"]
    grammar.context_initial = {int(key.split("L")[1]): saved[key] for key in saved.files if key.startswith("initial_L")}
    grammar.context_transition = {(int(key.split("L")[1].split("_")[0]), int(key.split("j")[1])): saved[key]
                                  for key in saved.files if key.startswith("transition_L")}
    counts = SignCounts(rows)
    markov = Markov(counts, *manifest["markov_configuration"])
    position = Position(counts, manifest["position_strength"])
    prefix = tuple(code.strip().removeprefix("W") for code in args.prefix.split(",") if code.strip())
    if len(prefix) >= args.length or args.length < 1:
        raise ValueError("The assumed length must exceed the supplied prefix length.")
    pg = grammar.distribution(prefix, args.length)
    pm = markov.distribution(prefix, args.length)
    pp = position.distribution(prefix, args.length)
    class_weight = manifest["class_mixture_weight"]
    position_weight = manifest["position_mixture_weight"]
    distributions = {"MARKOV": pm, "CLASS_GRAMMAR": pg,
                     "MARKOV_PLUS_CLASS": (1 - class_weight) * pm + class_weight * pg,
                     "MARKOV_PLUS_POSITION": (1 - position_weight) * pm + position_weight * pp}
    assert all(abs(float(prob.sum()) - 1) < 1e-10 for prob in distributions.values())
    answer = {"prefix": list(prefix), "assumed_length": args.length,
              "unknown_prefix_codes": [code for code in prefix if code not in grammar.alphabet.index],
              "scope": "Conditional code-bucket prediction from the known prefix and assumed length. This supplies no sign meanings.",
              "predictions": {name: [{"code": grammar.alphabet.signs[int(i)], "probability": float(prob[i])}
                                     for i in np.argsort(-prob, kind="stable")[:args.top]]
                              for name, prob in distributions.items()}}
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="", help="Comma-separated Wells codes, in normalized reading order.")
    parser.add_argument("--length", type=int, required=True)
    parser.add_argument("--top", type=int, default=5)
    main(parser.parse_args())
