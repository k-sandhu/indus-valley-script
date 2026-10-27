"""Additional source witnesses, chosen after the first source review; no scoring."""
import json
from pathlib import Path
import re
import sys

from prepare import ROOT, OUT, PKG, rows, read, save, sha, entry_id, tl, plain
from source_blocks import exact_winslow_blocks


def tl_witness(entry):
    path = ROOT / f'data/raw/2026-10-21-rebus-base-rate/sources-v1/tamil-lex/page-{entry["page"]:05d}.html'
    witnesses = []
    for match in re.finditer(r"<div>\s*(.*?)</div>", path.read_text(encoding="utf-8"), re.S):
        if any(entry_id(record) == entry_id(entry) for record in tl.parse_page("<div>"+match.group(1)+"</div>", entry["page"])):
            witnesses.append({"source_path": path.relative_to(ROOT).as_posix(), "source_sha256": sha(path),
                              "query_page": entry["page"], "character_span": list(match.span()),
                              "raw_html": match.group(1), "text": plain(match.group(1))})
    return {"entry_id": entry_id(entry), "entry": entry, "witnesses": witnesses}


def main():
    packets = read(OUT / "compound-packets.json")
    lexicon = rows(ROOT / "data/raw/2026-10-21-rebus-base-rate/derived-v1/tamil-lex-entries.jsonl")
    for packet in packets:
        entry = packet["entry"]
        path = ROOT / f'data/raw/2026-10-22-rebus-winslow/sources-v1/winslow/page-{entry["page"]:05d}.html'
        packet["witnesses"] = [dict(witness, source_path=path.relative_to(ROOT).as_posix(), source_sha256=sha(path),
                                    query_page=entry["page"])
                               for witness in exact_winslow_blocks(path.read_text(encoding="utf-8"), entry)]
        packet["tamil_lexicon_comparison"] = [tl_witness(candidate) for candidate in lexicon if candidate["head"] == entry["head"]]
    save(OUT / "compound-packets-v2.json", packets)
    terms = {"āṟu", "ēḻu", "iru-var", "aṟu-mīṉ", "eḻu-mīṉ", "kāvu-", "aṟṟu", "veḷi", "vēḷ", "vaṭakku", "aṇiṟ-piḷḷai"}
    extra = [tl_witness(entry) for entry in lexicon if entry["translit"] in terms]
    save(OUT / "sense-supplements.json", {"selection": "Explicit follow-up forms and compounds from the reviewed proposal and dictionary passages; post-outcome source audit", "entries": extra})
    print(json.dumps({"compound_exact_witnesses": [len(packet["witnesses"]) for packet in packets],
                      "compound_tl_matches": sum(bool(packet["tamil_lexicon_comparison"]) for packet in packets),
                      "supplement_rows": len(extra)}))


if __name__ == "__main__":
    main()
