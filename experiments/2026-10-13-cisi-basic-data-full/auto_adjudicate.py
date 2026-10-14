"""Settle unadjudicated disagreements by rule (AMENDMENT-2.md): keep every candidate either reader allowed.

Usage (from the repository root):
  python experiments/2026-10-13-cisi-basic-data-full/auto_adjudicate.py <block> [<block> ...]

For each block given, reads assembled/compare/<block>.todo.json and writes
assembled/adjudication/<block>.adjudication.json, refusing to overwrite an existing file (an
adjudicator's decisions are never replaced).
"""
import difflib
import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cisi_common import consistent  # noqa: E402

RAW = HERE.parents[1] / "data/raw/2026-10-13-cisi-basic-data-full/assembled"
NOTE = "not adjudicated (AMENDMENT-2.md): every candidate either reader allowed"


def ws(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def units(s):
    """Characters, with each bracket group as one unit holding its alternatives (None = wildcard)."""
    out = []
    for part in re.split(r"(\[[^\]]*\])", s):
        if part.startswith("[") and part.endswith("]"):
            inner = part[1:-1]
            out.append(None if "?" in inner else tuple(inner.split("/")))
        else:
            out.extend((c,) for c in part)
    return out


def expand(us, limit=8):
    if any(u is None for u in us):
        return None
    combos = 1
    for u in us:
        combos *= len(u)
        if combos > limit:
            return None
    return sorted({"".join(c) for c in itertools.product(*us)})


def alt(cands):
    """[a/b] for a set of non-empty candidates without separators, else [??]."""
    cands = sorted(set(cands))
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 4 or any((not c) or "/" in c or "[" in c or "]" in c for c in cands):
        return "[??]"
    return "[" + "/".join(cands) + "]"


def show(u):
    if u is None:
        return "[??]"
    return u[0] if len(u) == 1 else "[" + "/".join(u) + "]"


def union(a, b):
    a, b = ws(a), ws(b)
    if a == b or re.sub(r"\s", "", a) == re.sub(r"\s", "", b):   # spacing only: keep the first reading
        return a
    if consistent(a, b):        # a's candidates include b's reading
        return a
    if consistent(b, a):
        return b
    ua, ub = units(a), units(b)
    key = lambda u: "\x00" if u is None else "|".join(u)
    sm = difflib.SequenceMatcher(None, [key(u) for u in ua], [key(u) for u in ub], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out.extend(show(u) for u in ua[i1:i2])
        elif op == "replace" and (i2 - i1) == (j2 - j1):
            for x, y in zip(ua[i1:i2], ub[j1:j2]):
                if x is None or y is None:
                    out.append("[??]")
                else:
                    out.append(alt(set(x) | set(y)))
        else:
            ca, cb = expand(ua[i1:i2]), expand(ub[j1:j2])
            out.append("[??]" if ca is None or cb is None else alt(set(ca) | set(cb)))
    merged = "".join(out)
    merged = re.sub(r"(\[\?\?\])+", "[??]", merged)
    if "[" not in merged:          # the readings differ but no difference survived: keep both visibly
        merged = alt([a, b]) if alt([a, b]) != "[??]" else "[??]"
    return merged


def cells(line):
    c = [x.strip() for x in line.split(" | ")]
    return c + [""] * (5 - len(c))


def decide(block, todo):
    out = []
    rows = [r for r in todo if r["column"] == "row" and not r["cisi"].startswith("line-")]
    one_sided = {"pass1": [r for r in rows if r["pass2"] == "absent"],
                 "pass2": [r for r in rows if r["pass1"] == "absent"]}
    pairs = {}
    for r1, r2 in zip(one_sided["pass1"], one_sided["pass2"]):
        pairs[r1["cisi"]] = r2
        pairs[r2["cisi"]] = None
    for r in todo:
        d = {k: r[k] for k in ("cisi", "column", "pass1", "pass2")}
        if r["column"] != "row":
            d["final"] = union(r["pass1"], r["pass2"])
        elif r["cisi"].startswith("line-"):
            d["final"] = union(r["pass1"], r["pass2"])
        elif r["cisi"] in pairs and pairs[r["cisi"]] is None:
            d["final"] = "absent"
        elif r["cisi"] in pairs:
            c1, c2 = cells(r["pass1"]), cells(pairs[r["cisi"]]["pass2"])
            d["final"] = " | ".join([c1[0]] + [union(x, y) if ws(x) != ws(y) else ws(x) for x, y in zip(c1[1:], c2[1:])])
        else:
            present = r["pass1"] if r["pass1"] != "absent" else r["pass2"]
            d["final"] = present
        if d["final"] == "absent" or "[" not in d["final"]:
            r1, r2 = consistent(r["pass1"], d["final"]) if d["final"] != "absent" else r["pass1"] == "absent", \
                consistent(r["pass2"], d["final"]) if d["final"] != "absent" else r["pass2"] == "absent"
            d["outcome"] = "both-consistent" if r1 and r2 else "first-pass-right" if r1 else "second-pass-right" if r2 else "both-wrong"
        else:
            d["outcome"] = "undecidable"
        d["note"] = NOTE
        d["auto"] = True
        out.append(d)
    return out


def main():
    for block in sys.argv[1:]:
        dest = RAW / "adjudication" / f"{block}.adjudication.json"
        if dest.exists():
            print(block, "has adjudicator decisions; left as is")
            continue
        todo = json.loads((RAW / "compare" / f"{block}.todo.json").read_text(encoding="utf-8"))
        records = decide(block, todo)
        dest.write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(block, len(records), "records;", sum(r["outcome"] == "undecidable" for r in records), "bracketed")


if __name__ == "__main__":
    main()
