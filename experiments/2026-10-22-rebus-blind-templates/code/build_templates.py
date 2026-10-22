"""Build the frozen template list from the identifications and the pair counts of both halves.

Primary templates: every ordered adjacent pair of two different identified signs that occurs
in at least two distinct split components across both halves, leaving out the pairs Parpola
published and the pairs whose outcome REBUS-BASE-RATE-2026-10-21 already reported. If fewer
than 20 remain, the threshold drops to one component. Gapped templates: the same rule for
pairs with exactly one unidentified sign between them. Published templates: Parpola's own
pairs, scored separately.

    python experiments/2026-10-22-rebus-blind-templates/code/build_templates.py IDENTS DISCOVERY CONFIRMATION OUT
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from bench.common import sha256  # noqa: E402

MIN_COMPONENTS = 2
MIN_TEMPLATES = 20
EXPOSED_WORDS = ["mīṉ", "muruku"]   # compound sets enumerated by the 2026-10-21 package


def merged(disc, conf, key):
    c = Counter()
    for half in (disc, conf):
        for p in half[key]:
            c[(p["first"], p["second"])] += p["components"]
    return c


def select(counts, banned, threshold):
    return sorted(((a, b, n) for (a, b), n in counts.items() if n >= threshold and (a, b) not in banned),
                  key=lambda x: (-x[2], x[0], x[1]))


def main(idents_path, disc_path, conf_path, out_path):
    out = Path(out_path)
    if out.exists():
        print("refusing to overwrite", out)
        return 1
    idents = json.loads(Path(idents_path).read_text(encoding="utf-8"))
    disc = json.loads(Path(disc_path).read_text(encoding="utf-8"))
    conf = json.loads(Path(conf_path).read_text(encoding="utf-8"))
    if conf["half"] != "confirmation" or disc["half"] != "discovery":
        raise SystemExit("halves swapped")
    published = {(a, b) for a, b, _ in idents["published_pairs"]["pairs"]}
    known = {(a, b) for a, b, _ in idents["known_outcomes"]["pairs"]}
    known_gap = {(a, b) for a, b, _ in idents["known_outcomes"]["gapped"]}
    adj = merged(disc, conf, "adjacent_pairs")
    gap = merged(disc, conf, "gapped_pairs")
    threshold = MIN_COMPONENTS
    primary = select(adj, published | known, threshold)
    if len(primary) < MIN_TEMPLATES:
        threshold = 1
        primary = select(adj, published | known, threshold)
    gapped = select(gap, published | known | known_gap, MIN_COMPONENTS)
    res = {"schema_version": "1.0", "task": "rebus-blind-templates/templates",
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "provenance": {p: {"path": Path(x).resolve().relative_to(ROOT).as_posix(), "sha256": sha256(x)}
                          for p, x in (("identifications", idents_path), ("discovery_pairs", disc_path),
                                       ("confirmation_pairs", conf_path), ("code", __file__))},
           "rule": {"min_components": threshold, "min_templates": MIN_TEMPLATES, "halves": "discovery and confirmation summed"},
           "identifications": {k: {"label": v["label"], "codes": v["codes"], "words": v["words"]}
                               for k, v in idents["identifications"].items()},
           "exposed_second_words": EXPOSED_WORDS,
           "templates": [{"id": f"T{i + 1:02d}", "first": a, "second": b, "shape": "C", "components": n}
                         for i, (a, b, n) in enumerate(primary)],
           "gapped_templates": [{"id": f"G{i + 1:02d}", "first": a, "second": b, "shape": "S", "components": n}
                                for i, (a, b, n) in enumerate(gapped)],
           "published_templates": [{"id": f"P{i + 1:02d}", "first": a, "second": b, "shape": "C", "reading": r,
                                    "components": adj.get((a, b), 0)}
                                   for i, (a, b, r) in enumerate(idents["published_pairs"]["pairs"])]}
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(res["templates"]), "primary;", len(res["gapped_templates"]), "gapped;",
          len(res["published_templates"]), "published; threshold", threshold)
    print("SHA-256", sha256(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
