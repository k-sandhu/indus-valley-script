"""Freeze the sample before building local source packets for adjudication."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-22-lexical-source-review"
OUT = ROOT / "data/raw/2026-10-22-lexical-source-review/run-v1"
SEED = "lexical-source-review-2026-10-22-v1"
sys.path.insert(0, str(ROOT / "experiments/2026-10-22-reading-eval-readiness/code"))
from lexical_inputs import entry_id, roman_key  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments/2026-10-21-rebus-base-rate/code"))
import parse_tamil_lex as tl  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path):
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def stratum(entry):
    accepted = len(entry["members"]) == 2
    loan = entry.get("star") or entry.get("foreign_mark")
    if accepted and loan:
        return "accepted_origin_flag"
    if accepted and entry.get("seg") == "ety":
        return "accepted_etymology"
    if accepted:
        return "accepted_other"
    if loan:
        return None
    if entry["kind"] == "sub" and re.search("am|añ|aṅ", entry["translit_plain"]):
        return "rejected_increment_screen"
    if entry["kind"] == "principal" and not entry.get("ety"):
        return "rejected_principal_no_etymology"
    if entry["kind"] == "sub":
        return "rejected_other_subentry"
    return None


def freeze():
    source = ROOT / "data/raw/2026-10-22-rebus-winslow/derived-v1/winslow-entries.jsonl"
    entries = rows(source)
    excluded = {"murukkampū", "murukkañcettal", "jamīṉ"}
    sizes = {"accepted_origin_flag": 6, "accepted_etymology": 6,
             "accepted_other": 8, "rejected_increment_screen": 6,
             "rejected_principal_no_etymology": 8, "rejected_other_subentry": 6}
    pools = {key: [] for key in sizes}
    regressions = []
    for entry in entries:
        if entry["translit_plain"] in excluded:
            regressions.append(entry)
            continue
        group = stratum(entry)
        if group:
            identifier = entry_id(entry, "winslow")
            rank = hashlib.sha256((SEED + "|" + identifier).encode()).hexdigest()
            pools[group].append((rank, identifier, entry))
    selection = []
    for group, size in sizes.items():
        for _, identifier, entry in sorted(pools[group])[:size]:
            selection.append({"sample_id": f"W{len(selection)+1:02d}", "stratum": group,
                              "entry_id": identifier, "entry": entry})
    local = OUT / "selection.json"
    save(local, {"seed": SEED, "selected": selection, "known_regressions": regressions})
    save(PKG / "FREEZE.json", {"created_utc": datetime.now(timezone.utc).isoformat(),
                               "seed": SEED, "source": {"path": source.relative_to(ROOT).as_posix(), "sha256": sha(source)},
                               "protocol_sha256": sha(PKG / "PROTOCOL.md"), "selector_sha256": sha(Path(__file__)),
                               "local_selection": {"path": local.relative_to(ROOT).as_posix(), "sha256": sha(local)},
                               "stratum_population": {key: len(value) for key, value in pools.items()},
                               "stratum_selected": dict(Counter(item["stratum"] for item in selection)),
                               "selected_row_ids": [{key: item[key] for key in ("sample_id", "stratum", "entry_id")} for item in selection],
                               "known_regression_count": len(regressions),
                               "scope": "Deterministic stratified source audit; not an unexamined linguistic confirmation cohort"})
    print(json.dumps({"selected": len(selection), "strata": dict(Counter(item["stratum"] for item in selection))}))


def plain(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def winslow_packet(item):
    entry = item["entry"]
    path = ROOT / f'data/raw/2026-10-22-rebus-winslow/sources-v1/winslow/page-{entry["page"]:05d}.html'
    text = path.read_text(encoding="utf-8")
    witnesses = []
    for match in re.finditer(r"<div>\s*(.*?)</div>", text, re.S):
        block = match.group(1)
        if "<hw>" not in block or entry["head"] not in block:
            continue
        if entry["kind"] == "sub":
            subs = [sub.group(0) for sub in re.finditer(r"<p2>.*?</p2>", block, re.S) if entry["head"] in sub.group(0)]
            if not subs:
                continue
            body = block[:block.find("<p2>")] + "\n" + "\n".join(subs)
        else:
            body = block.split("<p2>", 1)[0]
            if entry["head"] not in body:
                continue
        witnesses.append({"source_path": path.relative_to(ROOT).as_posix(), "source_sha256": sha(path),
                          "query_page": entry["page"], "character_span": list(match.span()),
                          "raw_html": body, "text": plain(body)})
    return dict(item, witnesses=witnesses)


def packets():
    frozen = read(PKG / "FREEZE.json")
    selected_path = ROOT / frozen["local_selection"]["path"]
    if sha(selected_path) != frozen["local_selection"]["sha256"]:
        raise ValueError("selection changed")
    selected = read(selected_path)
    compound = [winslow_packet(item) for item in selected["selected"]]
    compound += [winslow_packet({"sample_id": f"R{index+1:02d}", "stratum": "known_regression",
                               "entry_id": entry_id(entry, "winslow"), "entry": entry})
                 for index, entry in enumerate(selected["known_regressions"])]
    save(OUT / "compound-packets.json", compound)
    identifiers = read(ROOT / "experiments/2026-10-22-rebus-blind-templates/identifications-v1.json")["identifications"]
    entries = rows(ROOT / "data/raw/2026-10-21-rebus-base-rate/derived-v1/tamil-lex-entries.jsonl")
    senses = []
    words = sorted({word for ident in identifiers.values() for word in ident["words"]})
    for word in words:
        candidates = [entry for entry in entries if len(entry["members"]) == 1 and roman_key(entry["translit"]) == roman_key(word)]
        sourced = []
        for entry in candidates:
            path = ROOT / f'data/raw/2026-10-21-rebus-base-rate/sources-v1/tamil-lex/page-{entry["page"]:05d}.html'
            raw = path.read_text(encoding="utf-8")
            witnesses = []
            for match in re.finditer(r"<div>\s*(.*?)</div>", raw, re.S):
                block = match.group(1)
                records = tl.parse_page("<div>" + block + "</div>", entry["page"])
                if any(entry_id(record) == entry_id(entry) for record in records):
                    witnesses.append({"source_path": path.relative_to(ROOT).as_posix(), "source_sha256": sha(path),
                                      "query_page": entry["page"], "character_span": list(match.span()),
                                      "raw_html": block, "text": plain(block)})
            sourced.append({"entry_id": entry_id(entry), "entry": entry, "witnesses": witnesses})
        senses.append({"word": word, "proposals": [{"id": key, **item} for key, item in identifiers.items() if word in item["words"]],
                       "candidates": sourced})
    save(OUT / "sense-packets.json", senses)
    print(json.dumps({"compound_packets": len(compound), "compound_without_witness": sum(not item["witnesses"] for item in compound),
                      "sense_forms": len(senses), "sense_candidates": sum(len(item["candidates"]) for item in senses),
                      "sense_candidates_without_witness": sum(not item["witnesses"] for row in senses for item in row["candidates"])}))


if __name__ == "__main__":
    {"freeze": freeze, "packets": packets}[sys.argv[1]]()
