"""Convert reviewed printed-list transcriptions to local SCHEMA.md records.

python -I normalize_brahmi.py --transcriptions <jsonl> [<jsonl> ...] \
  --rights <source-status.json> --lexicon <tsv> --out <new jsonl> --review <new tsv> \
  [--source-rules <reviewed source defaults.json>]

Paths are explicit. No statistics are computed. Unresolved language, script or
identity fields raise errors for review; original fields are preserved locally.
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hd_common import read_jsonl, write_jsonl
from validate_records import check_record, LANGUAGES, SCRIPTS
import edition_rules

SURVEY = {"asi-ar-1903-04", "asi-ar-1913-14", "asi-ar-1911-12"}
ENDINGS = {
    "Sanskrit": ("sya", "asya", "āyāḥ", "yāḥ", "aḥ", "ā", "am", "aṃ", "e", "ena"),
    "Prakrit": ("sa", "asa", "iye", "ye"),
    "Tamil": ("aṉ", "ṉ"),
}
ASPIRATES = {"kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh"}
CONSONANTS = set("kgṅcjñṭḍṇtdnpbmyrlvśṣshḻṟṉḵf")
MARKS = {"ṃ", "ṁ", "ḥ", "ँ", "\u0310", "\u0303", "m\u0310", "m\u0303"}
LACUNA = re.compile(r"\.{2,}|…+|\[(?:\s|[-–—.?xX])+\]|(?<!\w)[xX?]+(?!\w)")


OLD_CONVENTION = {"asi-ar-1911-12", "asi-ar-1913-14"}  # AMENDMENT-2.md; Bloch writes the Indological convention


def transliterate(text, survey=False, source=None):
    """Lower-case and convert to IAST by source (AMENDMENT-2.md, AMENDMENT-3.md).

    The older Survey convention maps chh to the IAST aspirate ch and ch to c through a placeholder,
    so the aspirate is not turned into c by the second replacement (the defect of the literal
    sequential mapping, AMENDMENT-3.md). In the Indo-Aryan sources e and o have one sign each in
    Brahmi, so ē and ō become e and o. Tamil keeps its long and short e and o.
    """
    text = unicodedata.normalize("NFC", text).lower()
    if source is None and survey:
        source = "asi-ar-1913-14"
    if source in OLD_CONVENTION:
        text = text.replace("chh", "\u0001").replace("ch", "c").replace("\u0001", "ch")
        for old, new in (("sh", "ṣ"), ("ṛi", "ṛ")):
            text = text.replace(old, new)
    if source in SURVEY:
        for old, new in (("ṁ", "ṃ"), ("ç", "ś"), ("ē", "e"), ("ō", "o")):
            text = text.replace(old, new)
    return unicodedata.normalize("NFC", text)


def clean_form(text, survey=False):
    text = LACUNA.sub(" ", transliterate(text, survey))
    text = re.sub(r"[\[\]()?]", "", text)
    return " ".join(text.split())


def segment_word(word, corpus):
    word = unicodedata.normalize("NFC", word.replace("-", ""))
    vowels = set("aāiīuūṛṝeēoō") | ({"ḷ", "ḹ"} if corpus == "ia-ganges" else set())
    consonants = CONSONANTS | ({"ḷ"} if corpus == "ta-brahmi" else set())
    tokens, i = [], 0
    while i < len(word):
        pair = word[i:i + 2]
        if pair in ASPIRATES or pair in {"ai", "au", "m\u0310", "m\u0303"}:
            tokens.append(pair)
            i += 2
        elif word[i] in vowels | consonants | MARKS:
            tokens.append(word[i])
            i += 1
        else:
            raise ValueError("unsupported transliteration character U+%04X" % ord(word[i]))
    # In Indo-Aryan legends ḷ before a vowel is the retroflex lateral of a name, not the vowel (AMENDMENT-3.md).
    if corpus == "ia-ganges":
        tokens = ["\u0001" if t == "ḷ" and k + 1 < len(tokens) and (tokens[k + 1] in vowels or tokens[k + 1] in {"ai", "au"})
                  else t for k, t in enumerate(tokens)]
        consonants = consonants | {"\u0001"}
    units, cluster = [], []
    for token in tokens:
        if token in MARKS:
            if cluster or not units:
                raise ValueError("unattached vowel modifier")
            units[-1] += token
        elif token in vowels or token in {"ai", "au"}:
            units.append("".join(cluster) + token)
            cluster = []
        else:
            if corpus == "ta-brahmi" and cluster:
                units.append(cluster.pop() + "·")
            cluster.append(token)
    # At a word end each consonant without a vowel is a separate sign.
    units.extend(token + "·" for token in cluster)
    return [u.replace("\u0001", "ḷ") for u in units]


def load_lexicon(path):
    result = {}
    with open(path, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != ["form", "tag", "language", "note"]:
            raise ValueError("lexicon header must be form, tag, language, note")
        for row in reader:
            key = (unicodedata.normalize("NFC", row["form"]), row["language"])
            if key in result:
                raise ValueError("duplicate lexicon entry")
            result[key] = row["tag"]
    return result


def tag_member(member, language, lexicon):
    languages = ([language] if language in ENDINGS else ["Prakrit"] if language == "Pali" else
                 ["Sanskrit", "Prakrit"] if language == "mixed Sanskrit-Prakrit" else ["Sanskrit", "Prakrit", "Tamil"])
    for lang in languages:
        if (member, lang) in lexicon:
            return lexicon[member, lang], "lexicon"
    endings = sorted({ending for lang in languages for ending in ENDINGS[lang]}, key=lambda x: (-len(x), x))
    for ending in endings:
        if member.endswith(ending) and len(member) > len(ending):
            stem = member[:-len(ending)]
            for lang in languages:
                if ending in ENDINGS[lang] and (stem, lang) in lexicon:
                    return lexicon[stem, lang], "lexicon"
    return "NAME", "default-name"


def completeness(entry):
    text = entry.get("legend_as_printed") or ""
    doubtful = bool(entry.get("doubtful")) or "?" in text
    explicit = entry.get("completeness")
    if explicit:
        return explicit, doubtful
    if not text.strip():
        return ("illegible" if entry.get("illegible_part") else "no-legend"), doubtful
    gaps = list(LACUNA.finditer(text))
    if gaps:
        if not LACUNA.sub("", text).strip(" []()?-"):
            return "illegible", doubtful
        if any(not text[:m.start()].strip(" []()?") or not text[m.end():].strip(" []()?") for m in gaps):
            return "damaged-edge", doubtful
        return "damaged-internal", doubtful
    illegible = entry.get("illegible_part")
    if illegible:
        description = str(illegible).lower()
        if re.search(r"\b(first|last|beginning|end|edge|initial|final)\b", description):
            return "damaged-edge", doubtful
        return "damaged-internal", doubtful
    if entry.get("restored") or re.search(r"[\[(].*?[\])]", text):
        return "restored", doubtful
    return "complete", doubtful


def language_fields(entry, source):
    note = entry.get("language") or entry.get("language_note")
    # A remark that only compares a form with Prakrit or calls it irregular does not identify the
    # language; it is kept in the record and the collection rule decides (AMENDMENT-3.md, R10).
    if note and not entry.get("language") and not re.match(r"\s*(the language is|language:)", str(note), re.I) \
            and str(note).strip() not in LANGUAGES:
        note = None
    if note:
        if note in LANGUAGES:
            language = note
        else:
            lowered = str(note).lower()
            if "mixed" in lowered or ("sanskrit" in lowered and "prakrit" in lowered):
                language = "mixed Sanskrit-Prakrit"
            else:
                language = next((x for x in LANGUAGES if x.lower() == lowered or x.lower() in lowered), None)
        if language is None:
            raise ValueError("unresolved language remark; supply reviewed language")
        return language, entry.get("language_basis", "editor"), "entry language remark"
    period_text = str(entry.get("period") or "").lower()
    if source in {"asi-ar-1903-04", "asi-ar-1913-14"} and "pre-gupta" in period_text:
        return "mixed Sanskrit-Prakrit", "editor", "pre-Gupta Basarh legend: Marshall's statement for pre-Gupta legends (AMENDMENT-3.md, R10)"
    general = entry.get("collection_language")
    if general in LANGUAGES:
        return general, "editor", entry.get("collection_language_rule", "editor collection statement supplied in transcription")
    if source == "asi-ar-1911-12":
        period = str(entry.get("period") or entry.get("date_as_printed") or "").lower()
        if "pre-gupta" in period or any(x in period for x in ("maury", "sunga", "śuṅga", "kushan", "kuṣāṇa")):
            return "mixed Sanskrit-Prakrit", "editor", "Marshall pre-Gupta: Prakrit or mixed (Amendment 1)"
        if "gupta" in period or "later" in period:
            return "Sanskrit", "editor", "Marshall Gupta and later: Sanskrit (Amendment 1)"
        if not period:
            return "Sanskrit", "editor", "Marshall undated entry: the majority class, Gupta and Sanskrit (p. 46; AMENDMENT-3.md, R10)"
    raise ValueError("no language basis; supply entry language or editor collection statement")


def period_from_date(text):
    """Period label from an editor's palaeographic date (AMENDMENT-3.md, R10).

    A century range takes its earliest century. B.C. centuries and the 1st century A.D. are
    `early`; the 2nd and 3rd centuries A.D. `Kushana`; the 4th to 6th `Gupta`; the 7th and later
    `later`. Named periods in the text (Mauryan, Śuṅga, Kuṣāṇa, Gupta) decide when no century is given.
    """
    t = unicodedata.normalize("NFC", str(text or "")).lower()
    ordinals = {"first": "1st", "second": "2nd", "third": "3rd", "fourth": "4th", "fifth": "5th",
                "sixth": "6th", "seventh": "7th", "eighth": "8th", "ninth": "9th", "tenth": "10th"}
    for word, number in ordinals.items():
        t = re.sub(r"\b%s\b" % word, number, t)
    t = t.replace("of our era", "a.d.")
    if re.search(r"\b(older|earlier) than\b[^;]*\bgupta\b|pre-gupta|before the gupta", t):
        return "pre-Gupta (Kushana)"
    if re.search(r"early type|early period|antiquity|older than sanskrit", t):
        return "pre-Gupta (early)"
    m = re.search(r"(\d+)(?:st|nd|rd|th)?(?:\s*(?:or|to|-|–|and)\s*\d+(?:st|nd|rd|th)?)?\s*(?:century|cent\.?)?\s*(b\.?\s*c|a\.?\s*d)", t)
    if not m:
        # A century without an era is A.D. in these reports.
        m = re.search(r"(\d+)(?:st|nd|rd|th)(?:\s*(?:or|to|-|–|and)\s*\d+(?:st|nd|rd|th)?)?\s*(century)", t)
    if m:
        century = int(m.group(1))
        era = "ad" if m.group(2) == "century" else m.group(2).replace(" ", "").replace(".", "")
        if era == "bc" or century <= 1:
            return "pre-Gupta (early)"
        if century <= 3:
            return "pre-Gupta (Kushana)"
        if century <= 6:
            return "Gupta"
        return "post-Gupta (later)"
    if "kush" in t or "kuṣāṇa" in t:
        return "pre-Gupta (Kushana)"
    if any(x in t for x in ("maury", "śuṅga", "sunga", "aśoka", "asoka")):
        return "pre-Gupta (early)"
    if "gupta" in t:
        return "Gupta"
    return None


def script_field(entry, corpus):
    if corpus == "ta-brahmi":
        return "Tamil-Brahmi"
    if entry.get("script") in SCRIPTS:
        return entry["script"]
    period = str(entry.get("period") or entry.get("date_as_printed") or "").lower()
    if "post-gupta" in period or "later" in period:
        return "Brahmi (later)"
    if "gupta" in period and "pre-gupta" not in period:
        return "Brahmi (Gupta)"
    if "kushan" in period or "kuṣāṇa" in period:
        return "Brahmi (Kushana)"
    if "pre-gupta" in period or any(x in period for x in ("maury", "sunga", "śuṅga", "early")):
        return "Brahmi (early)"
    if not period and entry.get("source") == "asi-ar-1911-12":
        entry["script_rule"] = "Marshall undated entry: the majority class, Gupta (p. 46; AMENDMENT-3.md, R10)"
        return "Brahmi (Gupta)"
    raise ValueError("no script stage; supply reviewed script or period")


def bloch_aliases(references):
    aliases = []
    if references is None:
        return aliases
    if not isinstance(references, list):
        references = [references]
    for ref in references:
        if isinstance(ref, dict):
            if ref.get("source") in {"asi-ar-1903-04", "bloch1903", "Bloch"} and ref.get("entry") is not None:
                if ref.get("equated", True) and not ref.get("uncertain", False):
                    entries = ref["entry"] if isinstance(ref["entry"], list) else [ref["entry"]]
                    aliases.extend("bloch1903:" + str(n) for n in entries)
            continue
        value = str(ref)
        aliases.extend("bloch1903:" + n for n in re.findall(r"bloch1903:(\d+[A-Za-z]?)", value))
        # Accept only explicit equivalences, not every discussion reference.
        if re.search(r"(?:same as|identical with|equated with|=)", value, re.I) and re.search(r"Bloch|1903.{0,2}1904", value, re.I):
            number_part = re.split(r"\bNos?\.?\s*", value, flags=re.I)
            if len(number_part) > 1:
                aliases.extend("bloch1903:" + n for n in re.findall(r"\d+[A-Za-z]?", number_part[-1]))
    return aliases


def normalize_entry(entry, rights, lexicon):
    def nfc(value):
        if isinstance(value, str):
            return unicodedata.normalize("NFC", value)
        if isinstance(value, list):
            return [nfc(x) for x in value]
        if isinstance(value, dict):
            return {nfc(k): nfc(v) for k, v in value.items()}
        return value
    entry = nfc(entry)
    source = entry["source"]
    if source in SURVEY and not entry.get("period"):
        derived = period_from_date(entry.get("date_as_printed"))
        if derived:
            entry["period"], entry["period_rule"] = derived, "from date_as_printed (AMENDMENT-3.md, R10)"
        elif entry.get("default_period"):
            entry["period"], entry["period_rule"] = entry["default_period"], "editor's collection date (AMENDMENT-3.md, R10)"
    if source not in SURVEY | {"mahadevan-2003"}:
        raise ValueError("unsupported source")
    if source not in rights:
        raise ValueError("source absent from rights mapping")
    corpus = "ta-brahmi" if source == "mahadevan-2003" else "ia-ganges"
    number = str(entry.get("entry", ""))
    sub = str(entry.get("sub_entry") or "").strip()
    aliases = list(entry.get("aliases") or [])
    if source == "asi-ar-1903-04":
        object_id = "bloch1903:" + number
        die_id = object_id + sub
        kind, genre, site = "clay-sealing", "sealing", "Basarh"
        identifier = number + sub
    elif source == "asi-ar-1913-14":
        register = entry.get("register") or entry.get("register_number") or entry.get("register_no")
        if register is None:
            # The list itself is numbered by the Unclassified Register.
            register = entry.get("entry")
        if register is None:
            raise ValueError("Spooner register missing")
        object_id, die_id = "spooner1913:" + str(register), "spooner1913-die:" + number + sub
        kind, genre, site = "clay-sealing", "sealing", "Basarh"
        identifier = number + sub
        aliases.extend(bloch_aliases(entry.get("cross_references")))
        aliases.extend("bloch1903:" + str(n) for n in entry.get("bloch_equivalents", []))
    elif source == "asi-ar-1911-12":
        match = re.match(r"\d+", number)
        if not match:
            raise ValueError("Bhita entry number missing")
        object_id = "marshall1911:" + number
        die_id = object_id + sub
        genre = "seal" if int(match[0]) <= 13 or int(match[0]) == 115 else "sealing"
        kind = ("ring" if entry.get("object_kind") in {"ring", "signet-ring"} else "seal-die") if genre == "seal" else "clay-sealing"
        site, identifier = "Bhita", number + sub
    else:
        if entry.get("table") is None or entry.get("row") is None:
            raise ValueError("Mahadevan table and row required")
        identifier = f"T{entry['table']}.{entry['row']}"
        object_id = die_id = "mahadevan2003:" + identifier
        raw_kind = entry.get("object_kind")
        if raw_kind not in {"seal", "ring", "coin"}:
            raise ValueError("Mahadevan object kind unresolved")
        genre = "coin" if raw_kind == "coin" else "seal"
        kind = "seal-die" if raw_kind == "seal" else raw_kind
        site = entry.get("site") or entry.get("site_as_printed")
        if not site and re.search(r"\bKarur\b", str(entry.get("findspot_as_printed") or ""), re.I):
            site = "Karur"
        if site and re.search(r"\bKarur\b", site, re.I):
            site = "Karur"
        elif site and re.search(r"river|bed|findspot|unknown|provenance", site, re.I):
            site = None
        if isinstance(site, str):
            site = site.strip() or None
    if not number and source in SURVEY:
        raise ValueError("entry identifier missing")
    text = entry.get("legend_as_printed") or ""
    printed_lines = entry.get("legend_lines_as_printed")
    if printed_lines is not None:
        if not isinstance(printed_lines, list) or any(not isinstance(x, str) for x in printed_lines):
            raise ValueError("legend_lines_as_printed must be strings")
    # AMENDMENT-3.md: editorial marks, lacunae and line-end joins, then IAST by source.
    reading = edition_rules.read_legend(text, printed_lines, source)
    lines = [[transliterate(w, source=source) for w in line] for line in reading["lines"]]
    if printed_lines is None and len(lines) > 1:
        # Without an edition line division the legend is one line (SCHEMA.md, line_division_basis none).
        lines = [[w for line in lines for w in line]]
        reading["breaks"] = []
    if not lines:
        lines = [[]]  # no legend: one empty line, as in run C's original
    words = [word for line in lines for word in line]
    members = [word.split("-") for word in words]
    if any(not part for word in members for part in word):
        raise ValueError("empty compound member")
    language, basis, rule = language_fields(entry, source)
    tagged = [[tag_member(part, language, lexicon) for part in word] for word in members]
    word_units = [segment_word(word, corpus) for word in words]
    # Sign-unit positions at which a printed line begins (AMENDMENT-3.md, R4).
    offsets = [0]
    for units_of_word in word_units:
        offsets.append(offsets[-1] + len(units_of_word))
    line_breaks_units = []
    for index, prefix in reading["breaks"]:
        if prefix is None:
            line_breaks_units.append(offsets[index])
        else:
            inside = len(segment_word(transliterate(prefix, source=source), corpus))
            line_breaks_units.append(offsets[index] + max(1, min(inside, len(word_units[index]) - 1)))
    line_breaks_units = sorted(set(line_breaks_units))
    state = edition_rules.completeness_from(reading, entry)
    doubtful = bool(entry.get("doubtful")) or reading["doubtful"]
    transcription = entry.get("transcription")
    if transcription is None:
        transcriber = entry.get("transcriber")
        if isinstance(transcriber, dict):
            by = transcriber.get("by") or transcriber.get("name") or transcriber.get("model")
            method = entry.get("method") or transcriber.get("method")
        else:
            by, method = transcriber, entry.get("method") or entry.get("transcription_method")
        if not method:
            # The transcription brief explicitly requires checking page images.
            method = "page-image"
        transcription = {"method": method, "by": by}
    record = dict(entry)
    record.update(record_id=f"{corpus}:{source}:{identifier}", corpus=corpus, object_id=object_id,
                  die_id=die_id, object_kind=kind, genre=genre, aliases=sorted(set(aliases)), site=site,
                  source_locator={key: entry[key] for key in ("page_printed", "page_pdf", "entry", "plate", "figure", "table", "row", "scan") if entry.get(key) is not None},
                  language=language, language_basis=basis, language_rule=rule,
                  script=script_field(entry, corpus), rights=nfc(rights[source]), legend_as_printed=text,
                  lines=lines, line_division_basis="edition" if printed_lines is not None else "none",
                  line_breaks_units=line_breaks_units if printed_lines is not None else [],
                  edition_rule_flags={k: v for k, v in reading.items() if k not in ("lines", "breaks")},
                  words=words, members=members, word_units=word_units,
                  units=[u for word in word_units for u in word],
                  line_of_word=[i for i, line in enumerate(lines) for _ in line],
                  tags=[[t for t, _ in word] for word in tagged],
                  tag_source=[[s for _, s in word] for word in tagged],
                  completeness=state, reading_doubtful=doubtful, transcription=transcription)
    if entry.get("plates") is not None:
        record["source_locator"]["plate"] = entry["plates"]
    if source == "asi-ar-1913-14":
        record["duplicate_objects"] = entry.get("duplicates") or []
    if site is None:
        record["site_reason"] = entry.get("site_reason") or "No unambiguous place name supplied; review in feasibility ledger"
    if entry.get("findspot_as_printed"):
        record["findspot"] = entry["findspot_as_printed"]
    elif corpus == "ta-brahmi":
        original_site = entry.get("site_as_printed") or entry.get("site")
        if original_site and original_site != site:
            record["findspot"] = original_site
    if entry.get("dimensions") is not None:
        record["dimensions_as_printed"] = entry["dimensions"]
    errors = check_record(record)
    if errors:
        raise ValueError(f"{record['record_id']}: validation checks {sorted(errors)}")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcriptions", nargs="+", required=True, type=Path)
    for name in ("rights", "lexicon", "out", "review"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--source-rules", type=Path,
                        help="reviewed source defaults for collection_language, collection_language_rule, script, period")
    parser.add_argument("--corrections", type=Path,
                        help="coordinator corrections from the page-image review, keyed source:entry or source:entry:sub")
    args = parser.parse_args()
    try:
        if args.out.exists() or args.review.exists():
            raise ValueError("output or review already exists")
        rights = json.loads(args.rights.read_text(encoding="utf-8-sig"))
        lexicon = load_lexicon(args.lexicon)
        rules = json.loads(args.source_rules.read_text(encoding="utf-8-sig")) if args.source_rules else {}
        allowed_defaults = {"collection_language", "collection_language_rule", "script", "period", "default_period"}
        if any(not isinstance(v, dict) or set(v) - allowed_defaults for v in rules.values()):
            raise ValueError("source-rules has unsupported defaults")
        corrections = json.loads(args.corrections.read_text(encoding="utf-8-sig")) if args.corrections else {}
        used = set()
        records = []
        for p in args.transcriptions:
            for original in read_jsonl(p):
                # Coordinator corrections from the page-image review (key source:entry), then R1.
                key = (f"{original['source']}:T{original.get('table')}.{original.get('row')}"
                       if original["source"] == "mahadevan-2003" else f"{original['source']}:{original.get('entry')}")
                row = dict(original)
                if key in corrections:
                    row.update(corrections[key])
                    row["coordinator_correction"] = sorted(corrections[key])
                    used.add(key)
                for part in edition_rules.explode_impressions(row):
                    sub_key = f"{key}:{part.get('sub_entry')}"
                    if sub_key in corrections:
                        part.update(corrections[sub_key])
                        part["coordinator_correction"] = sorted(corrections[sub_key])
                        used.add(sub_key)
                    merged = dict(part)
                    for name, value in rules.get(part["source"], {}).items():
                        if not merged.get(name):
                            merged[name] = value
                    if merged.get("exclude_reason"):
                        continue
                    records.append(normalize_entry(merged, rights, lexicon))
        unused = sorted(set(corrections) - used - {"_comment"})
        if unused:
            raise ValueError("corrections not applied: " + ", ".join(unused))
        if len({r["record_id"] for r in records}) != len(records):
            raise ValueError("duplicate record identifiers")
        counts = Counter((member, tag, source, r["language"])
                         for r in records for ms, ts, ss in zip(r["members"], r["tags"], r["tag_source"])
                         for member, tag, source in zip(ms, ts, ss))
        write_jsonl(args.out, records)
        args.review.parent.mkdir(parents=True, exist_ok=True)
        with args.review.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t")
            writer.writerow(("member", "tag", "tag_source", "language", "count"))
            for key, count in sorted(counts.items()):
                writer.writerow((*key, count))
        print(json.dumps({"records": len(records), "review_members": len(counts)}))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    main()
