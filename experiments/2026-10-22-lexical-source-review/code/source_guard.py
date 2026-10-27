"""General source metadata repair, selected after the source-review outcomes.

Keep a parent origin mark separate from a claim that the complete subentry is a
loan. Reject splits produced by grammatical roots. Do not infer missing splits.
"""
import re

from prepare import OUT, PKG, read, save
from source_blocks import winslow

IS_LETTER = re.compile(r"^(?:is\s+)?(?:a|an|the)\s+(?:(?:syllabic|compound)\s+)?letter\s+of\s+(?:the\s+)?\w+\s+alphabet\b", re.I)


def grammatical(gloss, label):
    first = (gloss or "").strip()
    if label and first.startswith(label):
        first = first[len(label):].strip(" ,.")
    return winslow.grammatical(gloss, label) or bool(IS_LETTER.search(first))


def parse_page_reviewed(text, page):
    principals, subentries = [], []
    for block in winslow.DIV_RE.findall(text):
        if "<hw>" not in block:
            continue
        p, s = winslow.parse_page("<div>"+block+"</div>",page)
        if len(p) != 1:
            raise ValueError("Expected exactly one principal per source block")
        parent = dict(p[0])
        parent["grammatical"] = grammatical(parent["gloss"],parent["pos_source"])
        principals.append(parent)
        for original in s:
            child = dict(original)
            child["root_grammatical"] = parent["grammatical"]
            child["parent_asterisk"] = parent["asterisk"]
            child["parent_foreign_mark"] = parent["foreign_mark"]
            child["parent_origin_mark_present"] = parent["star"]
            child["whole_entry_loan_status"] = "not_determined_by_parent_mark"
            subentries.append(child)
    return principals, subentries


def guard_entry(entry, block):
    principals, subentries = parse_page_reviewed("<div>"+block+"</div>",entry["page"])
    if entry["kind"] == "principal":
        matches = [p for p in principals if (entry["head"],entry["translit_plain"]) in p["forms"] and p["gloss"]==entry["gloss"]]
    else:
        matches = [s for s in subentries if entry["head"] in s["heads"] and s["gloss"]==entry["gloss"] and entry["root"] in [pair[1] for pair in s["root_forms"]]]
    if len(matches)!=1:
        raise ValueError("Source identity must resolve exactly once")
    match=matches[0]
    blocked=match.get("root_grammatical",match.get("grammatical",False))
    return {"source_identity_resolved":True,"grammatical_root_or_entry":blocked,
            "original_members":entry["members"],"guarded_members":[] if blocked else entry["members"],
            "split_suppressed":blocked and len(entry["members"])==2,
            "parent_origin_mark_present":match.get("parent_origin_mark_present"),
            "whole_entry_loan_status":"not_determined_by_parent_mark",
            "scope":"Existing candidate guard; absence of a split remains unresolved."}


def main():
    records=[]
    for packet in read(OUT / "compound-packets-v2.json"):
        if len(packet["witnesses"])!=1:
            raise ValueError("Expected one exact original-source block")
        result=guard_entry(packet["entry"],packet["witnesses"][0]["raw_html"])
        records.append(dict(result,entry_id=packet["entry_id"],sample_id=packet["sample_id"]))
    save(OUT / "source-guard-review.json",records)
    summary={"rows":len(records),"suppressed_split_ids":[x["sample_id"] for x in records if x["split_suppressed"]],
             "parent_origin_mark_ids":[x["sample_id"] for x in records if x["parent_origin_mark_present"]],
             "post_outcome_repair":True,"whole_dictionary_reextracted":False,"increment_rule_added":False}
    save(PKG / "guard-results-v1.json",summary)
    print(summary)


if __name__=="__main__":
    main()
