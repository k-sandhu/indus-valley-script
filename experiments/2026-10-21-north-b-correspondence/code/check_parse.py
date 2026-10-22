"""Boundary check of PROTOCOL.md step 3: language labels in the flattened source against parsed lines.

For every entry (longest print) and for the labels Ta., Kur., Malt. and Br., the check
counts label occurrences three ways: in the text left after stripping every HTML tag
from the entry body, in each kind of run of the parser's flattening (italic, bold
without italics, plain; before and after the comparison cut), and as parsed lines. It
writes a summary with counts and entry numbers to --out and a local file of context
snippets for the mismatches to data/raw/2026-10-21-north-b-correspondence/.

    python -I experiments/2026-10-21-north-b-correspondence/code/check_parse.py --out <path>
"""

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dedr_parts as dp  # noqa: E402

CHECKED = {"Ta": "Tamil", "Kur": "Kurukh", "Malt": "Malto", "Br": "Brahui"}
# deliberately looser than the parser's label pattern: any of the four abbreviations as a word
LOOSE = re.compile(r"(?<![\w])(Ta|Kur|Malt|Br)(?![\w])")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    pages = dp.load_pages()
    order, prints = dp.entries_from_pages(pages)
    totals = Counter()
    issues = {"flatten_mismatch": [], "italic_not_parsed": [], "plain_label": [], "bold_label": [],
              "after_cut": [], "northern_line_without_forms": [], "tamil_line_without_forms": []}
    snippets = []
    for key in order:
        page, body = max(prints[key], key=lambda v: len(v[1]))
        raw_text = html.unescape(re.sub(r"<[^>]+>", " ", body.replace(dp.SPAN_SPLIT, " ")))
        raw = Counter(m.group(1) for m in LOOSE.finditer(raw_text))
        runs = dp.flatten(body)
        by_kind = Counter()
        italic_kept = Counter()
        parsed = Counter()
        decisions = Counter()
        for letter, pruns in dp.split_parts(runs):
            kept, _ = dp.cut_comparison(pruns)
            n_kept = len(kept)
            for idx, (bold, italic, text) in enumerate(pruns):
                # the run that holds the cut is split: its kept text counts as kept
                if idx < n_kept:
                    ktext = kept[idx][2]
                    rest = text[len(ktext):] if idx == n_kept - 1 else ""
                else:
                    ktext, rest = "", text
                kind = "italic" if italic else ("bold" if bold else "plain")
                for m in LOOSE.finditer(ktext):
                    by_kind[(kind, m.group(1))] += 1
                    if kind == "italic":
                        italic_kept[m.group(1)] += 1
                for m in LOOSE.finditer(rest):
                    by_kind[("cut", m.group(1))] += 1
            log = []
            for ln in dp.parse_part(kept, log):
                if ln["label"] in CHECKED and not ln["plain"]:
                    parsed[ln["label"]] += 1
                if ln["label"] in CHECKED and ln["plain"]:
                    snippets.append({"entry": key, "part": letter, "issue": "plain_line", "label": ln["label"],
                                     "forms": [f["form"] for f in ln["forms"]][:3]})
                if ln["label"] in CHECKED:
                    if not ln["forms"]:
                        kind = "tamil_line_without_forms" if ln["label"] == "Ta" else "northern_line_without_forms"
                        issues[kind].append(key)
            for kind, lab in log:
                if lab in CHECKED:
                    decisions[(kind, lab)] += 1
        # part markers "(b)" removed from runs do not hold labels, so the run total equals the raw count
        for lab in CHECKED:
            run_total = sum(v for (k, l), v in by_kind.items() if l == lab)
            totals[("raw", lab)] += raw[lab]
            totals[("parsed", lab)] += parsed[lab]
            for kind in ("italic", "bold", "plain", "cut"):
                totals[(kind, lab)] += by_kind[(kind, lab)]
            if run_total != raw[lab]:
                issues["flatten_mismatch"].append(f"{key}:{lab}")
            for kind in ("italic citation", "plain line", "plain citation"):
                totals[(kind, lab)] += decisions[(kind, lab)]
                if decisions[(kind, lab)]:
                    issues.setdefault(kind.replace(" ", "_"), []).append(f"{key}:{lab}")
            if italic_kept[lab] != parsed[lab] + decisions[("italic citation", lab)]:
                issues["italic_not_parsed"].append(f"{key}:{lab}")
                snippets.append({"entry": key, "issue": "italic_not_parsed", "label": lab, "text": raw_text[:3000]})
            if by_kind[("plain", lab)]:
                issues["plain_label"].append(f"{key}:{lab}")
                for m in LOOSE.finditer(raw_text):
                    if m.group(1) == lab:
                        snippets.append({"entry": key, "issue": "plain_or_bold", "label": lab,
                                         "text": raw_text[max(0, m.start() - 120): m.end() + 80]})
            if by_kind[("bold", lab)]:
                issues["bold_label"].append(f"{key}:{lab}")
            if by_kind[("cut", lab)]:
                issues["after_cut"].append(f"{key}:{lab}")
                snippets.append({"entry": key, "issue": "after_cut", "label": lab, "text": raw_text[-1500:]})
    summary = {
        "entries": len(order),
        "label_counts": {lab: {k: totals[(k, lab)] for k in ("raw", "italic", "bold", "plain", "cut", "parsed",
                                                            "italic citation", "plain line", "plain citation")} for lab in CHECKED},
        "issue_counts": {k: len(v) for k, v in issues.items()},
        "issues": {k: sorted(set(v)) for k, v in issues.items()},
    }
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    local = dp.OUT_DIR / (out.stem + "-snippets.jsonl")
    local.parent.mkdir(parents=True, exist_ok=True)
    with local.open("w", encoding="utf-8", newline="\n") as fh:
        for s in snippets:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(json.dumps({"label_counts": summary["label_counts"], "issue_counts": summary["issue_counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
