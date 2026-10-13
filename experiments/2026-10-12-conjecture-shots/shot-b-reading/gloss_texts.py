"""Apply the gloss map and the slot grammar to every discovery text.

Full glossed readings (with sign sequences) go to data/raw/.../shot-b-reading/
glossed_discovery.jsonl. Aggregate grammar statistics go to
discovery/grammar_summary.json.

Slot grammar, applied to a text in reading order:
  OPENER  = an AFF sign followed by one or more LINK signs, or a TITLE prefix
            (140, 142, 097, 091, 061) at the start
  CLOSING = from the end: an optional DET, then the head (the last non-DET sign),
            then the COMM signs and one NUM sign immediately before the head
  CORE    = everything between
Signs outside the map are glossed as "?" with class UNMAPPED.
"""
import collections
import json

from common_b import DISC, RAW, SHOT, UNKNOWN, ends, load_discovery, otype_group

GM = json.loads((SHOT / "GLOSS-MAP.json").read_text(encoding="utf-8"))
MAP = {x["code"]: x for x in GM["signs"]}
PREFIX_TITLES = {"140", "142", "097", "091", "061"}


def cls(s):
    if s == UNKNOWN:
        return "LOST"
    return MAP[s]["class"] if s in MAP else "UNMAPPED"


def gloss(s):
    if s == UNKNOWN:
        return "[lost]"
    return MAP[s]["gloss"] if s in MAP else "?"


def parse(seq):
    seq = list(seq)
    n = len(seq)
    i = 0
    opener = []
    if n >= 2 and cls(seq[0]) == "AFF" and cls(seq[1]) == "LINK":
        opener = [seq[0]]
        i = 1
        while i < n and cls(seq[i]) == "LINK":
            opener.append(seq[i])
            i += 1
    elif n >= 2 and seq[0] in PREFIX_TITLES:
        opener = [seq[0]]
        i = 1
    j = n
    det = []
    if j - 1 >= i and cls(seq[j - 1]) == "DET":
        det = [seq[j - 1]]
        j -= 1
    head = []
    if j - 1 >= i:
        head = [seq[j - 1]]
        j -= 1
    quals = []
    if head and cls(head[0]) in ("TITLE", "COMM", "DET"):
        while j - 1 >= i and cls(seq[j - 1]) == "COMM":
            quals.insert(0, seq[j - 1])
            j -= 1
        if j - 1 >= i and cls(seq[j - 1]) == "NUM":
            quals.insert(0, seq[j - 1])
            j -= 1
    core = seq[i:j]
    return {"opener": opener, "core": core, "closing": quals + head + det}


def render(p):
    def g(xs):
        return " + ".join(gloss(x) for x in xs)
    parts = []
    if p["opener"]:
        parts.append(f"[{g(p['opener'])}]")
    if p["core"]:
        parts.append(g(p["core"]))
    if p["closing"]:
        parts.append(f"<{g(p['closing'])}>")
    return " | ".join(parts)


def main():
    rows = load_discovery()
    RAW.mkdir(parents=True, exist_ok=True)
    out = []
    for r in rows:
        seq = r["signs_reading_rtl"]
        p = parse(seq)
        si, ei = ends(r)
        out.append({"cisi": r.get("source_cisi"), "object_type": r["object_type"], "signs": seq,
                    "intact_start": si, "intact_end": ei, "single_line": r["single_line"],
                    "classes": [cls(s) for s in seq], "parse": p, "reading": render(p)})
    with open(RAW / "glossed_discovery.jsonl", "w", encoding="utf-8") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")

    # aggregate grammar statistics over distinct intact single-line texts
    distinct = {}
    for o in out:
        if o["single_line"] and o["intact_start"] and o["intact_end"] and UNKNOWN not in o["signs"] and o["signs"]:
            distinct.setdefault((otype_group(o["object_type"]), tuple(o["signs"])), o)
    stats = {}
    for grp in ("SEAL", "TAB:B", "TAB:I", "TAB:C", "POT", "TAG", "OTHER"):
        texts = [o for (g, _), o in distinct.items() if g == grp]
        if not texts:
            continue
        c = collections.Counter()
        cls_tokens = collections.Counter()
        for o in texts:
            seq, k = o["signs"], o["classes"]
            n = len(seq)
            cls_tokens.update(k)
            c["texts"] += 1
            c["len3plus"] += n >= 3
            c["mapped_all"] += all(x not in ("UNMAPPED",) for x in k)
            c["opener_aff_link"] += bool(o["parse"]["opener"]) and k[0] == "AFF"
            c["opener_title_prefix"] += bool(o["parse"]["opener"]) and k[0] == "TITLE"
            c["opener_aff_link_len3plus"] += bool(o["parse"]["opener"]) and k[0] == "AFF" and n >= 3
            last = k[-1]
            c[f"final_{last}"] += 1
            c["has_name"] += "NAME" in k
            c["has_num"] += "NUM" in k
            # rule checks
            c["viol_aff_not_initial"] += any(x == "AFF" for x in k[1:])
            c["viol_link_without_aff_or_link_before"] += any(
                k[i] == "LINK" and (i == 0 or k[i - 1] not in ("AFF", "LINK", "NUM")) for i in range(n))
            c["viol_det_not_after_office"] += any(
                k[i] == "DET" and (i == 0 or seq[i - 1] not in ("740",) and k[i - 1] not in ("TITLE", "DET", "COMM"))
                for i in range(n))
            c["det_nonfinal"] += any(k[i] == "DET" for i in range(n - 1))
            c["title_or_det_final"] += last in ("TITLE", "DET")
            c["comm_final"] += last == "COMM"
        stats[grp] = {"counts": dict(c), "class_tokens": dict(cls_tokens)}
    (DISC / "grammar_summary.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
    print(json.dumps({g: v["counts"] for g, v in stats.items()}, indent=1))


if __name__ == "__main__":
    main()
