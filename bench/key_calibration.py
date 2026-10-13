"""Compare a key with frequency-matched rearrangements under independent language models."""
from collections import Counter
import math
from pathlib import Path

import numpy as np

from .common import (KEY_SOURCE, ROOT, digest, envelope, key_common, legacy,
                     null_summary, permutation_indices, positive_int, read_json, read_rows)


class Model:
    """The published Kneser-Ney score, with the same greedy option choice."""
    def __init__(self, alphabet, order, unigram, table=None, kn=None):
        self.alphabet = list(alphabet)
        self.cid = {c: i for i, c in enumerate(self.alphabet)}
        self.order = order
        self.V = len(alphabet)
        self.base = self.V + 1
        self.mod = self.base ** (order - 1)
        self.bos = self.mod - 1
        u = np.asarray(unigram, dtype=float)
        if len(u) != self.V or np.any(u <= 0) or not np.isclose(u.sum(), 1):
            raise ValueError("Model unigram must be positive and sum to one")
        self.U = np.log2(u).tolist()
        self.table = table.tolist() if isinstance(table, np.ndarray) else table
        self.kn = kn
        self.cache = {}

    def lp(self, ctx, value):
        if self.table is not None:
            return self.table[ctx][value]
        k = (ctx, value)
        if k not in self.cache:
            c, digits = ctx, []
            for _ in range(self.order - 1):
                digits.append(c % self.base)
                c //= self.base
            self.cache[k] = math.log2(self.kn.prob(tuple(reversed(digits)), value))
        return self.cache[k]

    def encode_key(self, key):
        return {s: tuple(tuple(self.cid[c] for c in option) for option in values)
                for s, values in key.items()}

    def score(self, texts, key):
        opts = self.encode_key(key)
        gain = likelihood = n = 0
        counts = Counter()
        for text in texts:
            ctx = self.bos
            for sign in text:
                values = opts[sign]
                if len(values) == 1:
                    chosen = values[0]
                else:
                    candidates = []
                    for value in values:
                        c, g = ctx, 0.
                        for v in value:
                            g += self.lp(c, v) - self.U[v]
                            c = (c * self.base + v) % self.mod
                        candidates.append(g)
                    chosen = values[int(np.argmax(candidates))]
                for v in chosen:
                    lp = self.lp(ctx, v)
                    likelihood += lp
                    gain += lp - self.U[v]
                    counts[self.alphabet[v]] += 1
                    n += 1
                    ctx = (ctx * self.base + v) % self.mod
        return {"G": gain / n if n else float("nan"),
                "LL": likelihood / n if n else float("nan"), "values": n, "texts": len(texts),
                "value_counts": dict(counts)}


def normalize_key(obj):
    obj = obj.get("key", obj)
    if not isinstance(obj, dict) or not obj:
        raise ValueError("Key must be a nonempty sign-to-value JSON object")
    result = {}
    for sign, value in obj.items():
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list) or not value or not all(isinstance(v, (str, list)) for v in value):
            raise ValueError("A key value is a string or a nonempty list of string options")
        result[str(sign)] = tuple(tuple(v) for v in value)
    return result


def train_model(obj):
    alphabet = list(obj["alphabet"])
    if len(set(alphabet)) != len(alphabet) or not alphabet:
        raise ValueError("Model alphabet must contain distinct values")
    cid = {c: i for i, c in enumerate(alphabet)}
    seqs = [[cid[c] for c in seq] for seq in obj["training"] if seq]
    if not seqs:
        raise ValueError("Language model training data are empty")
    order = int(obj.get("order", 3))
    if not 1 <= order <= 5:
        raise ValueError("Model order must be between one and five")
    kn = key_common().KneserNey(order, len(alphabet)).fit(seqs)
    cnt = Counter(c for seq in seqs for c in seq)
    u = np.array([cnt[c] + .5 for c in range(len(alphabet))], dtype=float)
    return Model(alphabet, order, u / u.sum(), kn=kn)


def load_model(path, alphabet):
    if Path(path).suffix == ".npz":
        if not alphabet or len(set(alphabet)) != len(alphabet):
            raise ValueError("Dense model alphabet must contain distinct values")
        with np.load(path, allow_pickle=False) as data:
            table, uni = data["table"], data["unigram"]
        order = 1
        while (len(alphabet) + 1) ** (order - 1) < len(table):
            order += 1
        if order > 5:
            raise ValueError("Dense model order must be at most five")
        if table.shape != ((len(alphabet) + 1) ** (order - 1), len(alphabet)):
            raise ValueError("Dense model shape does not match alphabet")
        return Model(alphabet, order, uni, table=table)
    return train_model(read_json(path))


def evaluate(texts, key, model, draws=199, seed=20261013, alpha=.01, groups=None):
    if not 0 < alpha < 1 or draws < 1:
        raise ValueError("Require 0 < alpha < 1 and positive permutation count")
    if not texts or any(not t for t in texts):
        raise ValueError("Key calibration requires nonempty texts")
    signs = sorted({s for t in texts for s in t})
    if set(signs) - set(key):
        raise ValueError("Key omits observed signs")
    key = {s: key[s] for s in signs}
    kc = key_common()
    strata = kc.frequency_strata(texts)
    bands = [strata[s] for s in signs]
    vals = [key[s] for s in signs]
    rng = np.random.default_rng(seed + 1)
    shuffled = [tuple(t[i] for i in rng.permutation(len(t))) for t in texts]
    if groups is None:
        groups = [digest(t) for t in texts]
    if len(groups) != len(texts):
        raise ValueError("One closure group is required per text")
    # Close aliases and duplicate texts transitively, even when supplied group ids differ.
    from .shots import assignment
    closure_rows = [{"object_family_id": str(g), "source_cisi": None,
                     "complete_observed": True, "has_unknown_sign": False,
                     "length": len(t), "signs_reading_rtl": list(t), "object_type": "SEAL"}
                    for t, g in zip(texts, groups)]
    closed = assignment(closure_rows, str(seed))
    groups = [closed[str(g)]["component"] for g in groups]
    half = [int(digest([seed, g]), 16) % 2 for g in groups]
    sets = {"all": texts, "A": [t for t, h in zip(texts, half) if h == 0],
            "B": [t for t, h in zip(texts, half) if h == 1]}
    if not sets["A"] or not sets["B"]:
        raise ValueError("Closure leaves an empty held-out half")
    scores = {k: model.score(v, key) for k, v in sets.items()}
    score_shuffle = model.score(shuffled, key)
    actual_order = scores["all"]["G"] - score_shuffle["G"]
    null = {k: [] for k in sets}
    null_counts = []
    order_null = []
    for perm in permutation_indices(bands, draws, seed):
        pk = dict(zip(signs, (vals[i] for i in perm)))
        for k, ts in sets.items():
            scored = model.score(ts, pk)
            null[k].append(scored["G"])
            if k == "all":
                null_counts.append(scored["values"])
        order_null.append(null["all"][-1] - model.score(shuffled, pk)["G"])
    comparisons = {k: null_summary(scores[k]["G"], v, alpha) for k, v in null.items()}
    order = null_summary(actual_order, order_null, alpha)
    passed = all(c["pass"] and c.get("distance_sd", 0) >= 3 for c in comparisons.values()) and order["pass"]
    return {"seed": seed, "permutations": draws, "alpha": alpha,
            "population": {"texts": len(texts), "sign_types": len(signs),
                           "frequency_bands": dict(Counter(bands)), "closure_groups": len(set(groups))},
            "score": scores["all"], "rearrangements": comparisons["all"],
            "rearrangement_distribution": null["all"], "order_only": order,
            "null_emitted_value_counts": {"min": min(null_counts), "mean": float(np.mean(null_counts)), "max": max(null_counts)},
            "transfer": {"kind": "fixed supplied key, grouped halves; no refit",
                         "A": {"score": scores["A"], "comparison": comparisons["A"]},
                         "B": {"score": scores["B"], "comparison": comparisons["B"]}},
            "pass": passed, "pass_rule": "p <= alpha and z >= 3 overall and in both grouped halves; order-only p <= alpha"}


def synthetic(seed=20261013, draws=199):
    """Known generated plaintext, 577 homophones and 1,859 short distinct texts."""
    rng = np.random.default_rng(seed)
    alphabet = list("kgcjtdnpbmyrlvs")
    V = len(alphabet)
    def plaintext(n, reverse=False):
        x = int(rng.integers(V))
        text = [alphabet[x]]
        for _ in range(n - 1):
            x = (x + (-1 if reverse else 1)) % V if rng.random() < .82 else int(rng.integers(V))
            text.append(alphabet[x])
        return text
    model = train_model({"alphabet": alphabet, "order": 3, "training": [plaintext(20) for _ in range(3000)]})
    rival = train_model({"alphabet": alphabet, "order": 3, "training": [plaintext(20, True) for _ in range(3000)]})
    key = {f"S{i:03}": ((alphabet[i % V],),) for i in range(577)}
    choices = {c: [s for s, v in key.items() if v[0][0] == c] for c in alphabet}
    weights = {c: np.arange(1, len(ss) + 1, dtype=float) ** -.9 for c, ss in choices.items()}
    texts, seen = [], set()
    probabilities = np.array([.14, .20, .22, .17, .11, .07, .04, .03, .02])
    while len(texts) < 1859:
        n = int(rng.choice(np.arange(2, 11), p=probabilities))
        plain = plaintext(n)
        text = tuple(str(rng.choice(choices[c], p=weights[c] / weights[c].sum())) for c in plain)
        if text not in seen:
            seen.add(text)
            texts.append(text)
    actual = evaluate(texts, key, model, draws, seed)
    strata = key_common().frequency_strata(texts)
    signs = sorted(strata)
    perm = next(permutation_indices([strata[s] for s in signs], 1, seed + 90))
    scrambled = dict(zip(signs, (key[signs[i]] for i in perm)))
    random_key = {s: ((str(rng.choice(alphabet)),),) for s in signs}
    controls = {"scrambled": evaluate(texts, scrambled, model, draws, seed),
                "random": evaluate(texts, random_key, model, draws, seed)}
    other = evaluate(texts, key, rival, draws, seed)
    original = read_json(ROOT / KEY_SOURCE / "stage5/derived.json")["true_key_separation_sd"]
    return {"generator": "Independent cyclic plaintext with 18% random transitions; known homophonic encoding",
            "correct": actual, "controls": controls,
            "unrelated_models": {"reverse_cycle": other},
            "published_power_reference_sd": original,
            "published_power_reference_source": KEY_SOURCE + "/stage5/derived.json",
            "pass": actual["pass"] and not any(v["pass"] for v in controls.values()) and not other["pass"]}


def configure(ap):
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--local-published", action="store_true", help="Read the preserved published key/model/corpus")
    ap.add_argument("--corpus", type=Path)
    ap.add_argument("--key", type=Path)
    ap.add_argument("--model", type=Path)
    ap.add_argument("--word-list", type=Path, help="One independent word per line; trains order-3 Kneser-Ney")
    ap.add_argument("--other-model", action="append", type=Path, default=[])
    ap.add_argument("--alphabet", default="kgcjtdnpbmyrlvs", help="Dense NPZ model alphabet in original order")
    ap.add_argument("--permutations", type=positive_int, default=199)
    ap.add_argument("--seed", type=int, default=20261013)
    ap.add_argument("--alpha", type=float, default=.01)


def run(args):
    sources = [KEY_SOURCE + "/common.py", KEY_SOURCE + "/stage3_fit.py", KEY_SOURCE + "/stage5_power.py"]
    if args.synthetic:
        return envelope("key-calibration", synthetic(args.seed, args.permutations), True, sources)
    kc = key_common()
    if args.local_published:
        texts = kc.unique_texts()
        key = normalize_key({s: list(v) for s, v in kc.key_options().items()})
        model_path = ROOT / "data/raw/2026-10-12-decipherment-claim-tests/sanskrit-key/models/skeleton_kn5.npz"
        model = load_model(model_path, args.alphabet)
        sources += [kc.CLEAN_JSONL, kc.KEY_CSV, model_path]
        groups = None
    else:
        if not args.corpus or not args.key or not (args.model or args.word_list):
            raise ValueError("Supply --corpus, --key and --model or --word-list")
        rows = read_rows(args.corpus)
        texts = [tuple(r.get("signs", r.get("signs_reading_rtl", []))) for r in rows]
        groups = [r.get("component", r.get("group", r.get("object_family_id", digest(t)))) for r, t in zip(rows, texts)]
        key = normalize_key(read_json(args.key))
        if args.word_list:
            words = [w.strip() for w in args.word_list.read_text(encoding="utf-8-sig").splitlines() if w.strip()]
            model = train_model({"alphabet": sorted(set("".join(words))), "training": words})
            model_path = args.word_list
        else:
            model_path = args.model
            model = load_model(model_path, args.alphabet)
        sources += [args.corpus, args.key, model_path]
    result = evaluate(texts, key, model, args.permutations, args.seed, args.alpha, groups)
    result["unrelated_models"] = {}
    for path in args.other_model:
        rival = load_model(path, args.alphabet)
        if rival.alphabet != model.alphabet:
            raise ValueError("Cross-language comparisons require the same declared projection alphabet")
        result["unrelated_models"][path.name] = evaluate(texts, key, rival, args.permutations, args.seed, args.alpha, groups)
        sources.append(path)
    result["language_identification_pass"] = (result["pass"] and bool(args.other_model)
                                                and all(not r["pass"] for r in result["unrelated_models"].values()))
    return envelope("key-calibration", result, paths=sources)
