"""Audit previously examined inputs. No Indus rows or confirmation loader are read."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from lexical_inputs import FormCounts, Lexicon

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-22-reading-eval-readiness"
RAW = ROOT / "data/raw/2026-10-22-reading-eval-readiness"
BASE = ROOT / "experiments/2026-10-21-rebus-base-rate/code"
sys.path.insert(0, str(BASE))
import run_interlocks as historical  # noqa: E402
import rebus  # noqa: E402


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
            "bytes": path.stat().st_size}


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="run-v1")
    args = parser.parse_args()
    if not args.run.replace("-", "").isalnum():
        parser.error("run must contain only letters, numbers and hyphens")
    out = PKG / args.run
    detail_path = RAW / args.run / "lexical-audit-detail.json"
    summary_path = out / "input-audit.json"
    sources_path = out / "source-manifest.json"
    if any(path.exists() for path in (detail_path, summary_path, sources_path)):
        parser.error("Run output already exists; choose a new --run")
    lex_path = rebus.DER / "tamil-lex-entries.jsonl"
    ident_path = ROOT / "experiments/2026-10-22-rebus-blind-templates/identifications-v1.json"
    entries = [json.loads(line) for line in lex_path.open(encoding="utf-8")]
    identifications = read(ident_path)["identifications"]
    words = sorted({word for item in identifications.values() for word in item["words"]})
    tokens, sangam_hashes = historical.sangam_tokens()
    counts = FormCounts(tokens)
    lexicon = Lexicon(entries)
    one = [entry for entry in entries if len(entry["members"]) == 1]
    by_translit, by_t0 = {}, {}
    for entry in one:
        by_translit.setdefault(entry["translit"], entry)
        by_t0.setdefault(rebus.tl_norm(entry["translit"], "T0s"), entry)
    audit = []
    for word in words:
        old = by_translit.get(word) or by_t0.get(rebus.tl_norm(word, "T0s"))
        new = lexicon.resolve(word, counts)
        prefix = historical.tamil_prefix(old["head"]) if old else None
        audit.append({"word": word,
                      "historical": {"entry": old,
                                     "fallback": word not in by_translit and old is not None,
                                     "prefix": prefix,
                                     "count": historical.prefix_count(tokens, prefix) if old else 0},
                      "same_historical_form_exact_count": counts.exact(old["head"]) if old else None,
                      "repaired": new})

    winslow_path = ROOT / "data/raw/2026-10-22-rebus-winslow/derived-v1/winslow-entries.jsonl"
    winslow = [json.loads(line) for line in winslow_path.open(encoding="utf-8")]
    targets = {"murukkampū", "murukkañcettal", "jamīṉ"}
    examples = []
    witnesses = []
    for entry in winslow:
        if entry.get("translit_plain") not in targets:
            continue
        page = ROOT / f'data/raw/2026-10-22-rebus-winslow/sources-v1/winslow/page-{entry["page"]:05d}.html'
        page_text = page.read_text(encoding="utf-8")
        index = page_text.find(entry["head"])
        examples.append({"parsed": entry, "source": ref(page),
                         "head_found_in_source": index >= 0,
                         "source_context": page_text[max(0, index-120):index+700] if index >= 0 else None})
        witnesses.append(page)
    spent_path = ROOT / "bench/spent.json"
    spent = read(spent_path)
    exposure = [{"split_id": key, "input_sha256": value.get("input_sha256"),
                 "spent_families": value.get("spent_families", []),
                 "reads": len(value.get("reads", []))}
                for key, value in spent["splits"].items() if not value.get("synthetic", False)]
    detail = {"classification": "post-outcome input audit", "words": audit,
              "winslow_examples": examples}
    write_new(detail_path, detail)
    candidate_states = Counter(item["repaired"]["status"] for item in audit)
    illustrative = []
    for item in audit:
        if item["word"] in {"kā", "ā", "aṟu"}:
            illustrative.append({"query": item["word"],
                                 "legacy_selected_form": item["historical"]["entry"]["translit"] if item["historical"]["entry"] else None,
                                 "legacy_prefix_count": item["historical"]["count"],
                                 "exact_count_of_legacy_form": item["same_historical_form_exact_count"],
                                 "repaired_status": item["repaired"]["status"],
                                 "exact_candidates": len(item["repaired"]["candidates"]),
                                 "repaired_selected_frequency": item["repaired"]["frequency"]})
    summary = {
        "schema_version": "1.0", "task": "reading-eval-readiness/input-audit",
        "classification": "post-outcome input audit", "created_utc": datetime.now(timezone.utc).isoformat(),
        "new_indus_confirmation_reads": 0, "repaired_scientific_statistic": None,
        "dictionary_rows": len(entries), "identifications": len(identifications),
        "distinct_proposed_forms": len(words), "sangam_files": len(sangam_hashes),
        "historical_token_count": len(tokens), "lookup_status_counts": dict(candidate_states),
        "legacy_fallback_queries": sum(item["historical"]["fallback"] for item in audit),
        "queries_with_prefix_exact_count_difference": sum(item["historical"]["count"] != item["same_historical_form_exact_count"] for item in audit if item["historical"]["entry"]),
        "illustrative_input_checks": illustrative,
        "winslow_checks": [{"form": item["parsed"]["translit_plain"],
                            "page": item["parsed"]["page"],
                            "parsed_members_count": len(item["parsed"].get("members", [])),
                            "source_head_found": item["head_found_in_source"]} for item in examples],
        "exposure_ledger": {"source": ref(spent_path), "non_synthetic_splits": exposure},
        "limits": ["Counts cover the historical whole-file Tamil token stream, including any front matter or editorial text.",
                   "An exact written-form count is not inflection-aware lemma frequency or evidence for a sense.",
                   "No ambiguous lexical entry was selected. No new lexical aliases were accepted.",
                   "Winslow examples are diagnostics; its parser was not repaired and no corrected chance rate was calculated.",
                   "The exposure ledger is incomplete for reads outside the loader; missing entries do not prove freshness."],
        "local_detail": ref(detail_path)}
    code_paths = sorted((PKG / "code").glob("*.py"))
    manifest_paths = [lex_path, ident_path, winslow_path, spent_path, PKG / "PROTOCOL.md",
                      BASE / "run_interlocks.py", BASE / "rebus.py", BASE / "parse_tamil_lex.py",
                      ROOT / "experiments/2026-10-22-rebus-blind-templates/code/run_templates.py",
                      ROOT / "experiments/2026-10-22-rebus-winslow/code/parse_winslow.py"]
    source_manifest = {"schema_version": "1.0", "new_acquisitions": 0,
                       "handling": "Original and derived dictionary/token payloads remain local; code and aggregates are own work.",
                       "source_records": ["experiments/2026-10-21-rebus-base-rate/SOURCES.json",
                                          "experiments/2026-10-22-rebus-winslow/SOURCES.json"],
                       "inputs_and_code": [ref(path) for path in manifest_paths + code_paths + witnesses],
                       "sangam_files": [{"path": (rebus.SRC / "sangam" / name).relative_to(ROOT).as_posix(),
                                          "sha256": digest} for name, digest in sangam_hashes.items()]}
    write_new(sources_path, source_manifest)
    write_new(summary_path, summary)
    print(json.dumps({"output": summary_path.relative_to(ROOT).as_posix(),
                      "lookup_status_counts": dict(candidate_states),
                      "illustrative_input_checks": illustrative}, ensure_ascii=True))


if __name__ == "__main__":
    main()
