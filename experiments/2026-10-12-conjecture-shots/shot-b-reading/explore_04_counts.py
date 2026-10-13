"""Exploration 4: the specific discovery counts cited in READING.md and the C-0002 card.

These were first computed with inline commands while the reading was written; this
script reproduces them and writes discovery/reading_counts.json (counts only).
Requires gloss_texts.py to have been run (reads the local glossed readings).
"""
import collections
import json

from common_b import DISC, RAW, otype_group

NUMS = {"001", "003", "004", "005", "013", "016", "017", "031", "032", "033", "034", "035", "055"}
SHEAF = {"390", "405", "407"}

L = [json.loads(x) for x in open(RAW / "glossed_discovery.jsonl", encoding="utf-8")]
D = {}
for o in L:
    if o["single_line"] and o["intact_start"] and o["intact_end"] and "000" not in o["signs"] and o["signs"]:
        D.setdefault((otype_group(o["object_type"]), tuple(o["signs"])), o)

out = {}
# legends ending 740, 740-090 and 740-400 by object group
end = collections.Counter()
for (g, s) in D:
    end[f"{g}|texts"] += 1
    end[f"{g}|ends_740"] += s[-1] == "740"
    end[f"{g}|ends_740-090"] += s[-2:] == ("740", "090")
    end[f"{g}|ends_740-400"] += s[-2:] == ("740", "400")
out["endings_by_group"] = dict(end)
# 002 after the openers
c = collections.Counter()
for (g, s) in D:
    for i, x in enumerate(s):
        if x == "002":
            c["tokens"] += 1
            p = s[i - 1] if i else "^"
            c["after_817_861_820"] += p in ("817", "861", "820")
            c["after_numeral"] += p in NUMS
out["sign_002"] = dict(c)
# sheaf signs
c = collections.Counter()
for (g, s) in D:
    for i, x in enumerate(s):
        if x in SHEAF:
            c["tokens"] += 1
            c["after_numeral"] += i > 0 and s[i - 1] in NUMS
            c["after_590"] += i > 0 and s[i - 1] == "590"
out["sheaf_signs"] = dict(c)
c = collections.Counter()
for (g, s) in D:
    if any(x in NUMS for x in s) and any(x in SHEAF for x in s):
        c["texts_with_numeral_and_sheaf"] += 1
        c["numeral_directly_before_sheaf"] += any(s[i] in SHEAF and s[i - 1] in NUMS for i in range(1, len(s)))
out["numeral_sheaf_texts"] = dict(c)
# 700 on Harappa tablets (intact faces, not distinct)
c = collections.Counter()
for o in L:
    if otype_group(o["object_type"]) in ("TAB:B", "TAB:I") and "700" in o["signs"] and o["intact_start"] \
            and o["intact_end"] and "000" not in o["signs"]:
        s = o["signs"]
        c["intact_faces_with_700"] += 1
        c["numeral_plus_700_only"] += len(s) == 2 and (s[0] in NUMS or s[1] in NUMS)
out["tablet_700"] = dict(c)
# closing three-sign phrases on seals
c = collections.Counter("-".join(s[-3:]) for (g, s) in D if g == "SEAL" and len(s) >= 3)
out["seal_closing_trigrams_top"] = c.most_common(8)
(DISC / "reading_counts.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
