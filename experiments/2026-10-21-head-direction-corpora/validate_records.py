"""Validate local records without computing statistics.

python -I validate_records.py --records <jsonl> [<jsonl> ...] --out <new json>
Writes aggregate failures by check; exits 1 on any invalid record, 2 on I/O.
Nested members, tags and tag_source have one list per word.
"""
import argparse
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hd_common import read_jsonl, write_json

CORPORA = {"ia-ganges", "ta-brahmi", "sux-ur3", "akk-sargonic", "sux-sargonic"}
TAGS = {"NAME", "DIVINE", "PLACE", "TITLE", "KIN", "NUMBER", "GRAM", "OTHER"}
KINDS = {"seal-die", "cylinder-seal", "stamp-seal", "ring", "coin", "clay-sealing",
         "sealed-tablet", "sealed-envelope", "bulla", "other"}
COMPLETENESS = {"complete", "restored", "damaged-edge", "damaged-internal", "illegible", "no-legend"}
LANGUAGES = {"Sanskrit", "Prakrit", "mixed Sanskrit-Prakrit", "Pali", "Tamil", "Sumerian", "Akkadian", "mixed"}
SCRIPTS = {"Brahmi (early)", "Brahmi (Kushana)", "Brahmi (Gupta)", "Brahmi (later)", "Tamil-Brahmi", "cuneiform"}
REQUIRED = {
    **dict.fromkeys(("record_id", "corpus", "source", "object_id", "object_kind", "genre",
                     "language", "language_basis", "script", "legend_as_printed",
                     "line_division_basis", "completeness"), str),
    **dict.fromkeys(("aliases", "lines", "words", "members", "units", "word_units",
                     "line_of_word", "tags", "tag_source"), list),
    "source_locator": dict, "site": (str, type(None)), "rights": (str, dict),
    "transcription": dict, "reading_doubtful": bool,
}


def string_list(value):
    return isinstance(value, list) and all(isinstance(x, str) and x for x in value)


def nested_strings(value):
    return isinstance(value, list) and all(string_list(x) for x in value)


def check_record(record):
    failures = set()
    if not isinstance(record, dict):
        return {"record_type"}
    for field, expected in REQUIRED.items():
        if field not in record:
            failures.add("required:" + field)
        elif not isinstance(record[field], expected):
            failures.add("type:" + field)
    for field in ("record_id", "source", "object_id", "language", "script"):
        if field in record and not record[field]:
            failures.add("empty:" + field)
    enums = {"corpus": CORPORA, "genre": {"seal", "sealing", "coin"},
             "object_kind": KINDS, "completeness": COMPLETENESS,
             "line_division_basis": {"edition", "atf", "none"}, "language": LANGUAGES,
             "language_basis": {"editor", "token-language", "catalogue"}, "script": SCRIPTS}
    for field, allowed in enums.items():
        if field in record and (not isinstance(record[field], str) or record[field] not in allowed):
            failures.add("enum:" + field)
    for field in ("words", "units", "aliases"):
        if field in record and not string_list(record[field]):
            failures.add("type:" + field)
    for field in ("lines", "members", "word_units", "tags", "tag_source"):
        if field in record and not nested_strings(record[field]):
            failures.add("type:" + field)
    if record.get("site") is None and not any(isinstance(record.get(k), str) and record[k].strip()
                                            for k in ("site_reason", "site_missing_reason", "site_ledger_entry")):
        failures.add("site_null_reason")
    if record.get("site") == "":
        failures.add("site_empty")
    transcription = record.get("transcription")
    if isinstance(transcription, dict):
        if transcription.get("method") not in {"page-image", "ocr-checked-against-image", "digital-edition"}:
            failures.add("transcription_method")
        if not isinstance(transcription.get("by"), str) or not transcription["by"].strip():
            failures.add("transcription_by")
    words = record.get("words")
    if string_list(words):
        for field in ("members", "word_units", "tags", "tag_source"):
            value = record.get(field)
            if isinstance(value, list) and len(value) != len(words):
                failures.add("word_count:" + field)
        lines = record.get("lines")
        if nested_strings(lines):
            if [word for line in lines for word in line] != words:
                failures.add("lines_flatten")
            indices = record.get("line_of_word")
            if not isinstance(indices, list) or len(indices) != len(words):
                failures.add("line_of_word_count")
            elif any(type(i) is not int or not 0 <= i < len(lines) for i in indices):
                failures.add("line_of_word_index")
            elif indices != [i for i, line in enumerate(lines) for _ in line]:
                failures.add("line_of_word_alignment")
        members = record.get("members")
        if nested_strings(members) and len(members) == len(words):
            if any(not parts or "-".join(parts) != word for parts, word in zip(members, words)):
                failures.add("members_per_word")
            for field in ("tags", "tag_source"):
                value = record.get(field)
                if nested_strings(value) and (len(value) != len(members) or
                                             any(len(a) != len(b) for a, b in zip(value, members))):
                    failures.add("member_count:" + field)
        if nested_strings(record.get("word_units")):
            if any(not units for units in record["word_units"]):
                failures.add("empty_word_units")
            if [unit for word in record["word_units"] for unit in word] != record.get("units"):
                failures.add("units_flatten")
    if nested_strings(record.get("tags")) and any(t not in TAGS for ts in record["tags"] for t in ts):
        failures.add("enum:tags")
    if nested_strings(record.get("tag_source")) and any(t not in {"editor-pos", "editor-translation", "lexicon", "default-name"}
                                                       for ts in record["tag_source"] for t in ts):
        failures.add("enum:tag_source")
    if record.get("line_division_basis") == "none" and isinstance(record.get("lines"), list) and len(record["lines"]) != 1:
        failures.add("none_line_count")
    if "die_id" in record and record["die_id"] is not None and not isinstance(record["die_id"], str):
        failures.add("type:die_id")
    if "impressions" in record and record["impressions"] is not None and (type(record["impressions"]) is not int or record["impressions"] < 0):
        failures.add("type:impressions")

    def nfc(value):
        if isinstance(value, str):
            return unicodedata.is_normalized("NFC", value)
        if isinstance(value, dict):
            return all(nfc(k) and nfc(v) for k, v in value.items())
        if isinstance(value, list):
            return all(nfc(v) for v in value)
        return True
    if not nfc(record):
        failures.add("unicode_nfc")
    return failures


def validate(records):
    counts, seen, total, invalid = Counter(), set(), 0, 0
    for record in records:
        total += 1
        failures = check_record(record)
        record_id = record.get("record_id") if isinstance(record, dict) else None
        if isinstance(record_id, str):
            if record_id in seen:
                failures.add("duplicate_record_id")
            seen.add(record_id)
        counts.update(failures)
        invalid += bool(failures)
    return {"records": total, "invalid_records": invalid, "valid": not invalid,
            "failures_by_check": dict(sorted(counts.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", nargs="+", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate(r for path in args.records for r in read_jsonl(path))
        write_json(args.out, result)
        print(__import__("json").dumps(result, sort_keys=True))
        return 0 if result["valid"] else 1
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    sys.exit(main())
