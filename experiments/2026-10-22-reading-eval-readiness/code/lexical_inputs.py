"""Exact lexical inputs for a future scorer; no phonological fallback or inference.

An exact written-form count is not lemma frequency or a meaning attestation.
Dictionary rows and token lists are supplied by the caller and remain local.
"""
from collections import Counter, defaultdict
import hashlib
import json
import unicodedata


def form_key(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A nonempty written form is required")
    return unicodedata.normalize("NFC", value.strip())


def roman_key(value):
    return form_key(value).casefold()


def tamil_tokens(text):
    """Tokenize supplied plain text at non-Tamil letters/marks, keeping vowel marks."""
    current = []
    out = []
    for ch in unicodedata.normalize("NFC", text):
        if "\u0b80" <= ch <= "\u0bff" and unicodedata.category(ch)[0] in "LM":
            current.append(ch)
        elif current:
            out.append("".join(current))
            current = []
    if current:
        out.append("".join(current))
    return out


class FormCounts:
    def __init__(self, tokens):
        self.counts = Counter(form_key(token) for token in tokens)

    def exact(self, form):
        return self.counts.get(form_key(form), 0)

    def reviewed_variants(self, forms):
        """Caller supplies reviewed complete forms; canonical duplicates count once."""
        keys = {form_key(form) for form in forms}
        if not keys:
            raise ValueError("At least one complete form is required")
        return sum(self.counts.get(key, 0) for key in keys)


def entry_id(entry, namespace="tamil-lexicon"):
    encoded = json.dumps(entry, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return namespace + ":" + hashlib.sha256(encoded).hexdigest()


class Lexicon:
    def __init__(self, entries, namespace="tamil-lexicon"):
        self.by_key = defaultdict(list)
        self.by_id = {}
        for entry in entries:
            if len(entry.get("members", [])) != 1:
                continue
            identifier = entry_id(entry, namespace)
            if identifier in self.by_id:
                continue
            record = dict(entry, entry_id=identifier)
            self.by_id[identifier] = record
            self.by_key[roman_key(entry["translit"])].append(record)
        for records in self.by_key.values():
            records.sort(key=lambda record: record["entry_id"])

    def resolve(self, query, counts=None, adjudication=None):
        """Return every exact candidate, or one explicitly reviewed record.

        `adjudication` must identify this query, the selected entry, reviewer,
        evidence and relation. It cannot silently reuse another query's decision.
        """
        query_key = roman_key(query)
        candidates = list(self.by_key.get(query_key, []))
        result = {"query": query, "normalization": "NFC; roman casefold; boundary trim",
                  "status": "missing", "entry_id": None, "frequency": None,
                  "frequency_measure": "exact_written_form",
                  "candidates": candidates, "adjudication": None}
        selected = None
        if adjudication is not None:
            required = ("query", "entry_id", "reviewer", "evidence", "relation")
            if any(not isinstance(adjudication.get(key), str) or
                   not adjudication[key].strip() for key in required):
                raise ValueError("Adjudication requires query, entry_id, reviewer, evidence and relation")
            if roman_key(adjudication["query"]) != query_key:
                raise ValueError("Adjudication belongs to another query")
            selected = self.by_id.get(adjudication["entry_id"])
            if selected is None:
                raise ValueError("Adjudication names an unknown entry")
            relation = adjudication["relation"]
            exact = selected in candidates
            if relation not in ("exact-sense", "attested-form-variant"):
                raise ValueError("Adjudication relation must be exact-sense or attested-form-variant")
            if relation == "exact-sense" and not exact:
                raise ValueError("An exact-sense decision cannot select a different written form")
            if not exact:
                candidates.append(selected)
            result.update(status="adjudicated", adjudication=dict(adjudication))
        elif len(candidates) == 1:
            selected = candidates[0]
            result["status"] = "exact"
        elif candidates:
            result["status"] = "ambiguous"
        result["candidates"] = candidates
        if counts is not None:
            result["form_counts"] = {
                form: counts.exact(form)
                for form in sorted({form_key(record["head"]) for record in candidates})}
        if selected is not None:
            result["entry_id"] = selected["entry_id"]
            if counts is not None:
                result["frequency"] = counts.exact(selected["head"])
        return result
