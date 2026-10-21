"""Convert a local coding file to the input of independent_check.py, keyed by the tree's own tip labels.

    python -I experiments/2026-10-21-dravidian-root-meanings/verify/to_tree_labels.py CODINGS.json TREE_SUMMARY.json OUT.json
"""
import json
import sys

codings_path, summary_path, out_path = sys.argv[1:4]
labels = json.load(open(summary_path, encoding="utf-8"))["tip_labels"]   # tree label -> variety name
by_variety = {v: k for k, v in labels.items()}
codings = json.load(open(codings_path, encoding="utf-8"))
out = {m: {by_variety[t]: row["state"] for t, row in c["tips"].items()} for m, c in codings.items()}
json.dump(out, open(out_path, "x", encoding="utf-8"), indent=1)
