"""Grouped, metadata-controlled archaeological context tests.

All inputs are observational fields. No language/translation mappings are used.
Run from the workspace root: python src/context_study.py --permutations 1000
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy import sparse
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
BASELINE_INTERACTION = False
UNIQUE_TEXT = False
COLLAPSE_ALLOGRAPHS = False


def solver_matrix(x):
    """liblinear requires 32-bit index arrays; these matrices are tiny."""
    x = sparse.csr_matrix(x)
    x.indices = x.indices.astype(np.int32)
    x.indptr = x.indptr.astype(np.int32)
    return x


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[b] = a


def load_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def principal_rows(rows):
    by_object = defaultdict(list)
    for r in rows:
        if r.get("signs_reading_rtl"):
            by_object[r["object_family_id"]].append(r)
    return [sorted(rs, key=lambda r: (-len(r["signs_reading_rtl"]), r["record_id"]))[0]
            for _, rs in sorted(by_object.items())]


def groups_for(rows):
    uf = UnionFind(len(rows))
    seen = {}
    for i, r in enumerate(rows):
        for key in (("object", r["object_family_id"]),
                    ("sequence", tuple(r["signs_reading_rtl"]))):
            if key in seen:
                uf.union(i, seen[key])
            else:
                seen[key] = i
    return np.asarray([uf.find(i) for i in range(len(rows))])


def symbol_label(raw):
    if raw.startswith("Bull1"):
        return 1
    # Predeclared unambiguous, single animal categories; composite scenes excluded.
    if raw in {"Bull", "Bult", "Gaur", "Gavi", "Zebu", "Elep", "Rhin", "Tigr",
               "Buff", "Goat", "Hare", "Ante", "Deer", "Bird", "Fish", "Turt"}:
        return 0
    return None


def prepare(rows, outcome):
    selected, labels = [], []
    for r in rows:
        typ = r["object_type"]
        if outcome == "seal_tablet":
            label = 1 if typ.startswith("SEAL") else 0 if typ.startswith("TAB") else None
        elif outcome == "bull1_other":
            label = symbol_label(r.get("symbol", "")) if typ.startswith("SEAL") else None
        else:
            raise ValueError(outcome)
        if label is not None:
            selected.append(r)
            labels.append(label)
    return selected, np.asarray(labels, dtype=int)


def independent_text_rows(rows, y, collapse=False):
    """Choose by identifier before interpreting cohort labels; preserve disagreements."""
    mapping = {"861": "817", "405": "390", "706": "705"} if collapse else {}
    cohorts = defaultdict(list)
    for i, r in enumerate(rows):
        seq = tuple(mapping.get(s, s) for s in r["signs_reading_rtl"])
        cohorts[seq].append(i)
    selected, labels, audit = [], [], []
    for seq, ix in sorted(cohorts.items()):
        representative = min(ix, key=lambda i: str(rows[i]["record_id"]))
        row = dict(rows[representative], signs_reading_rtl=list(seq))
        selected.append(row)
        labels.append(int(y[representative]))
        audit.append({"representative": row["record_id"], "members": len(ix),
                      "labels": dict(Counter(map(int, y[ix]))),
                      "sites": dict(Counter(rows[i]["site"] for i in ix))})
    return selected, np.asarray(labels, dtype=int), audit


def feature_dicts(rows, mode):
    features = []
    for r in rows:
        seq = r["signs_reading_rtl"]
        d = {"site=" + r["site"]: 1., "length=" + str(len(seq)): 1.}
        if BASELINE_INTERACTION:
            d["site_length=" + r["site"] + ":" + str(len(seq))] = 1.
        if mode in {"unigram", "boundary", "full"}:
            for sign in set(seq):
                d["sign=" + sign] = 1.
        if mode in {"boundary", "full"}:
            d["first=" + seq[0]] = 1.
            d["last=" + seq[-1]] = 1.
        if mode == "full":
            for a, b in zip(seq, seq[1:]):
                d[f"pair={a}>{b}"] = 1.
        features.append(d)
    return features


def make_cache(rows, groups, modes, seed=20261001, folds=5):
    # Folds depend only on groups, not labels. Vectorizers see training data only.
    splits = list(GroupKFold(folds, shuffle=True, random_state=seed)
                  .split(np.zeros(len(rows)), groups=groups))
    cache = {}
    for mode in modes:
        ds = feature_dicts(rows, mode)
        ms = []
        for train, test in splits:
            dv = DictVectorizer(sparse=True)
            xt = solver_matrix(dv.fit_transform([ds[i] for i in train]))
            xv = solver_matrix(dv.transform([ds[i] for i in test]))
            ms.append((train, test, xt, xv))
        cache[mode] = ms
    return cache


def predict_cache(cache, labels, weights=None):
    pred = np.zeros(len(labels))
    for train, test, xt, xv in cache:
        if len(set(labels[train])) != 2:
            raise ValueError("training fold lacks an outcome class")
        model = LogisticRegression(C=1., solver="liblinear", max_iter=1000,
                                   random_state=20261001)
        model.fit(xt, labels[train], sample_weight=None if weights is None else weights[train])
        pred[test] = model.predict_proba(xv)[:, 1]
    return np.clip(pred, 1e-12, 1. - 1e-12)


def losses(y, p):
    return -y * np.log(p) - (1-y) * np.log1p(-p)


def metrics(y, p, weights=None):
    return {"log_loss_nats": float(log_loss(y, p, sample_weight=weights)),
            "balanced_accuracy": float(balanced_accuracy_score(y, p >= .5,
                                                               sample_weight=weights)),
            "roc_auc": float(roc_auc_score(y, p, sample_weight=weights))}


def cluster_ci(values, groups, weights=None, seed=711, repeats=10000):
    unique = np.unique(groups)
    # Bootstrap ratio of loss sums to counts, so unequal-sized clusters retained.
    by_group = [(values[groups == g].sum(), (groups == g).sum()) for g in unique]
    if weights is not None:
        by_group = [((values[groups == g]*weights[groups == g]).sum(),
                     weights[groups == g].sum()) for g in unique]
    sums, counts = np.asarray(by_group, dtype=float).T
    rng = np.random.default_rng(seed)
    bs = []
    for start in range(0, repeats, 500):
        ix = rng.integers(0, len(unique), size=(min(500,repeats-start),len(unique)))
        bs.extend((sums[ix].sum(axis=1) / counts[ix].sum(axis=1)).tolist())
    return np.quantile(bs,[.025,.975]).tolist()


def permute_within(y, strata, rng):
    yp = y.copy()
    for indices in strata:
        yp[indices] = rng.permutation(y[indices])
    return yp


def site_transfer(rows, y, modes):
    output = []
    ds = {mode: feature_dicts(rows, mode) for mode in modes}
    seqs = [tuple(r["signs_reading_rtl"]) for r in rows]
    for train_site, test_site in [("Harappa","Mohenjo-daro"),("Mohenjo-daro","Harappa")]:
        train = np.asarray([i for i,r in enumerate(rows) if r["site"] == train_site])
        test = np.asarray([i for i,r in enumerate(rows) if r["site"] == test_site])
        test_sequences = {seqs[i] for i in test}
        train = np.asarray([i for i in train if seqs[i] not in test_sequences])
        if len(train)<30 or len(test)<30 or len(set(y[train]))<2 or len(set(y[test]))<2:
            continue
        result = {"train_site":train_site,"test_site":test_site,
                  "train_objects":len(train),"test_objects":len(test),
                  "overlapping_sequences_removed_from_train":True,"models":{}}
        for mode in modes:
            dv = DictVectorizer()
            xt = solver_matrix(dv.fit_transform([ds[mode][i] for i in train]))
            xv = solver_matrix(dv.transform([ds[mode][i] for i in test]))
            model = LogisticRegression(C=1.,solver="liblinear",max_iter=1000)
            model.fit(xt,y[train])
            p = np.clip(model.predict_proba(xv)[:,1],1e-12,1-1e-12)
            result["models"][mode] = metrics(y[test],p)
        output.append(result)
    return output


def fit_coefficients(rows, y, mode):
    dv = DictVectorizer()
    xx = solver_matrix(dv.fit_transform(feature_dicts(rows,mode)))
    model = LogisticRegression(C=1.,solver="liblinear",max_iter=1000)
    model.fit(xx,y)
    names = dv.get_feature_names_out()
    coeff = model.coef_[0]
    ranks = np.argsort(coeff)
    # Descriptive fit to entire discovery population, no confirmatory status.
    return {"low_label": [{"feature":str(names[i]),"coefficient":float(coeff[i])}
                          for i in ranks[:25]],
            "high_label": [{"feature":str(names[i]),"coefficient":float(coeff[i])}
                           for i in ranks[-25:][::-1]]}


def run_outcome(all_rows, outcome, permutations, outdir):
    rows,y=prepare(all_rows,outcome)
    cohort_audit = None
    if UNIQUE_TEXT:
        rows, y, cohort_audit = independent_text_rows(rows, y, COLLAPSE_ALLOGRAPHS)
    groups=groups_for(rows)
    unique,count=np.unique(groups,return_counts=True)
    weights=np.asarray([1./count[np.where(unique==g)[0][0]] for g in groups])
    modes=["baseline","unigram","boundary","full"]
    cache=make_cache(rows,groups,modes)
    preds={mode:predict_cache(cache[mode],y) for mode in modes}
    stats={mode:metrics(y,p) for mode,p in preds.items()}
    gain=losses(y,preds["baseline"])-losses(y,preds["full"])
    result={"outcome":outcome,"positive_label":"seal" if outcome=="seal_tablet" else "Bull1 family",
            "one_representative_per_global_sequence": UNIQUE_TEXT,
            "three_allographs_collapsed": COLLAPSE_ALLOGRAPHS,
            "baseline_site_length_interaction": BASELINE_INTERACTION,
            "objects":len(rows),"groups":len(unique),"labels":dict(Counter(map(int,y))),
            "largest_group":int(max(count)),"site_labels":{},"models":stats,
            "gain_nats_per_object":float(gain.mean()),
            "gain_cluster_bootstrap_95_ci":cluster_ci(gain,groups),
            "unique_sequence_weighted_models":{},"site_transfer":site_transfer(rows,y,modes),
            "exploratory_coefficients":fit_coefficients(rows,y,"full"),
            "permutations":[]}
    if cohort_audit is not None:
        result["cohort_audit"] = cohort_audit
        result["mixed_label_text_cohorts"] = sum(len(a["labels"]) > 1 for a in cohort_audit)
        result["multi_site_text_cohorts"] = sum(len(a["sites"]) > 1 for a in cohort_audit)
    result["permutation_assumption"] = (
        "Representatives are exchangeable within site/length; exact duplicate texts removed. "
        "Residual workshop/institution dependence remains possible."
        if UNIQUE_TEXT else
        "Artifact labels are row-exchangeable within site/length. Duplicate-cohort label "
        "dependence is destroyed by this null; grouped CV alone does not repair it.")
    for site in sorted({r["site"] for r in rows}):
        ix=[i for i,r in enumerate(rows) if r["site"]==site]
        result["site_labels"][site]=dict(Counter(map(int,y[ix])))
    for mode in modes:
        p=predict_cache(cache[mode],y,weights)
        result["unique_sequence_weighted_models"][mode]=metrics(y,p,weights)
    membership=defaultdict(list)
    for i,r in enumerate(rows):
        membership[(r["site"],len(r["signs_reading_rtl"]))].append(i)
    strata=[np.asarray(ix) for ix in membership.values()]
    mixed=[ix for ix in strata if len(set(y[ix]))>1]
    result["permutation_exchangeable_objects"]=sum(map(len,mixed))
    result["permutation_total_strata"]=len(strata)
    rng=np.random.default_rng(20261002)
    null=[]
    started=time.monotonic()
    outdir.mkdir(parents=True,exist_ok=True)
    # Predictions are audit rows local to the research package, not a public bulk corpus.
    with (outdir/f"{outcome}_predictions.jsonl").open("w",encoding="utf-8") as f:
        for i,r in enumerate(rows):
            f.write(json.dumps({"id":r["record_id"],"cisi":r.get("source_cisi"),
                                "group":int(groups[i]),"site":r["site"],"length":r["length"],
                                "label":int(y[i]),"sequence":r["signs_reading_rtl"],
                                "predictions":{m:float(p[i]) for m,p in preds.items()},
                                "gain_nats":float(gain[i])})+"\n")
    print(json.dumps({"outcome":outcome,"observed_gain":result["gain_nats_per_object"],
                      "objects":len(rows),"groups":len(unique),"models":stats}),flush=True)
    for j in range(permutations):
        yp=permute_within(y,strata,rng)
        pb=predict_cache(cache["baseline"],yp)
        pa=predict_cache(cache["full"],yp)
        null.append(float(np.mean(losses(yp,pb)-losses(yp,pa))))
        if (j+1)%25==0 or j+1==permutations:
            result["permutations"]=null
            result["permutation_p_one_sided"]=(1+sum(x>=gain.mean() for x in null))/(1+len(null))
            result["runtime_seconds"]=time.monotonic()-started
            (outdir/f"{outcome}.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
            print(json.dumps({"outcome":outcome,"permutations_done":j+1,
                              "requested":permutations,"null_max":max(null),
                              "p":result["permutation_p_one_sided"],
                              "seconds":result["runtime_seconds"]}),flush=True)
    if permutations==0:
        (outdir/f"{outcome}.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result


def main():
    global BASELINE_INTERACTION, UNIQUE_TEXT, COLLAPSE_ALLOGRAPHS
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",default="data/normalized/lipi_clean_rtl_singleline.jsonl")
    parser.add_argument("--out",default="results/context")
    parser.add_argument("--permutations",type=int,default=1000)
    parser.add_argument("--outcome",choices=["seal_tablet","bull1_other","both"],default="both")
    parser.add_argument("--baseline-interaction",action="store_true",
                        help="Post-pilot sensitivity: include exact site-by-length baseline interactions")
    parser.add_argument("--unique-text", action="store_true",
                        help="One identifier-selected representative per global whole text")
    parser.add_argument("--collapse-allographs", action="store_true",
                        help="Three conservative collapses; requires --unique-text")
    args=parser.parse_args()
    BASELINE_INTERACTION=args.baseline_interaction
    UNIQUE_TEXT=args.unique_text
    COLLAPSE_ALLOGRAPHS=args.collapse_allographs
    if COLLAPSE_ALLOGRAPHS and not UNIQUE_TEXT:
        parser.error("--collapse-allographs requires --unique-text")
    rows=principal_rows(load_rows(ROOT/args.input))
    targets=["seal_tablet","bull1_other"] if args.outcome=="both" else [args.outcome]
    for outcome in targets:
        run_outcome(rows,outcome,args.permutations,ROOT/args.out)


if __name__=="__main__":
    main()
