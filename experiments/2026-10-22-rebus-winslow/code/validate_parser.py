"""Check the Winslow parser against the Tamil Lexicon before the freeze.

Three checks, none of which looks at the words of the interlock searches:

  transliteration  our romanisation of each principal's Tamil form against the
                   DSAL romanisation printed with it
  agreement        for Winslow compounds whose Tamil form is also a two-member
                   compound of the Tamil Lexicon, the share whose members match the
                   Lexicon's hyphenation (first members compared through their
                   sandhi bases, second members directly, both under T0s)
  coverage         of Winslow sub-entries whose Tamil form is a two-member compound
                   of the Lexicon, the share we split; and of those whose Tamil form
                   is a one-member Lexicon headword, the share we split anyway

    python -I experiments/2026-10-22-rebus-winslow/code/validate_parser.py OUT.json [LOCAL_DETAIL.json]
"""

import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_winslow as pw  # noqa: E402
from parse_winslow import rebus  # noqa: E402

LEX = rebus.DER / "tamil-lex-entries.jsonl"


def t0(x):
    return rebus.tl_norm(x, "T0s")


def members_agree(w, l):
    first = {t0(b) for b in rebus.sandhi_bases(w[0])} & {t0(b) for b in rebus.sandhi_bases(l[0])}
    return bool(first) and t0(w[1]) == t0(l[1])


def main(out_path, detail_path=None):
    out_path = Path(out_path)
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    pages, digest = pw.load_pages()
    recs = pw.build(pages)
    lex = defaultdict(list)
    for line in LEX.open(encoding="utf-8"):
        e = json.loads(line)
        lex[e["head"].replace(" ", "")].append(e["members"])

    pr = [r for r in recs if r["kind"] == "principal"]
    tr_ok = sum(pw.translit(r["head"]) == r["translit_plain"] for r in pr)
    tr_bad = [(r["head"], r["translit_plain"], pw.translit(r["head"])) for r in pr
              if pw.translit(r["head"]) != r["translit_plain"]]

    agree = Counter()
    disagree = []
    cover = Counter()
    false_split = Counter()
    for r in recs:
        lm = lex.get(r["head"].replace(" ", ""))
        two = [m for m in (lm or []) if len(m) == 2]
        if len(r["members"]) == 2 and (r["kind"] == "sub" or r["seg"] == "ety"):
            if two:
                ok = any(members_agree(r["members"], m) for m in two)
                agree[(r["seg"], ok)] += 1
                if not ok and len(disagree) < 3000:
                    disagree.append({"head": r["head"], "winslow": r["members"], "lexicon": two[0], "rule": r["seg"]})
        if r["kind"] == "sub" and r["pos"] is not None and lm:
            if two:
                cover[("lexicon_two_member", bool(r["members"]))] += 1
            elif all(len(m) == 1 for m in lm):
                false_split[bool(r["members"])] += 1
                if r["members"]:
                    false_split["second:" + r["members"][1]] += 1

    by_rule = {}
    for rule in ("first", "second", "phrase", "ety"):
        n_ok, n_bad = agree[(rule, True)], agree[(rule, False)]
        if n_ok + n_bad:
            by_rule[rule] = {"compared": n_ok + n_bad, "agree": n_ok, "share": n_ok / (n_ok + n_bad)}
    n_ok = sum(v for (rule, ok), v in agree.items() if ok)
    n_all = sum(agree.values())
    split_cov = cover[("lexicon_two_member", True)]
    all_cov = split_cov + cover[("lexicon_two_member", False)]
    fs_n = false_split[True] + false_split[False]
    top_false = Counter({k[7:]: v for k, v in false_split.items() if isinstance(k, str)}).most_common(30)
    result = {
        "schema_version": "1.0", "task": "rebus-winslow/parser-validation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {"winslow_pages": len(pages), "winslow_pages_digest": digest,
                   "tamil_lexicon_table": {"path": str(LEX.relative_to(rebus.ROOT)).replace("\\", "/"), "sha256": rebus.sha256(LEX)},
                   "code": {p.name: rebus.sha256(p) for p in sorted(Path(__file__).resolve().parent.glob("*.py"))}},
        "records": len(recs), "principals": len(pr), "sub_entries": sum(1 for r in recs if r["kind"] == "sub"),
        "two_member_compounds": sum(1 for r in recs if len(r["members"]) == 2),
        "transliteration": {"principal_forms": len(pr), "exact": tr_ok, "share": tr_ok / len(pr), "mismatches": len(tr_bad)},
        "agreement_with_lexicon": {"compared": n_all, "agree": n_ok, "share": n_ok / n_all if n_all else None, "by_rule": by_rule},
        "coverage": {"sub_entries_that_are_lexicon_two_member_compounds": all_cov, "split_by_us": split_cov,
                     "share": split_cov / all_cov if all_cov else None,
                     "sub_entries_that_are_lexicon_one_member_words": fs_n, "split_by_us_anyway": false_split[True],
                     "share_split_anyway": false_split[True] / fs_n if fs_n else None,
                     "commonest_second_members_of_those": top_false},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    if detail_path:
        Path(detail_path).parent.mkdir(parents=True, exist_ok=True)
        Path(detail_path).write_text(json.dumps({"transliteration_mismatches": tr_bad, "disagreements": disagree},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("two_member_compounds", "transliteration", "agreement_with_lexicon", "coverage")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(*sys.argv[1:]))
