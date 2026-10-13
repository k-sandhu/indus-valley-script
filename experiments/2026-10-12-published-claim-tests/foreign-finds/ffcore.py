"""Shared data handling for Study B (inscriptions found outside South Asia).

This module reads the normalized Lipi faces, assigns analysis groups, parses
text codes into reading-order tokens with damage masks, and builds
length- and medium-matched comparator cells. It contains no sequence model;
`analysis.py` adds the models and statistics. The independent check in
`verify.py` deliberately does not import this module.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FACES = ROOT / "data" / "normalized" / "lipi_observed_faces.jsonl"
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "2026-10-12-decipherment-claim-tests" / "foreign-finds"

UNKNOWN = "000"
BLANK = "999"
BOS = "<s>"
EOS = "</s>"
K_FOLDS = 10
MIN_COMPARATORS = 20

# ---------------------------------------------------------------- groups
SOUTH_ASIAN_REGIONS = {
    "Lower Indus", "Inter-Riverine", "Gujarat/Kutch", "Eastern Headwaters",
    "Upper Indus", "South India",
}
# 'Iranian Plateau' mixes Baluchistan/Makran sites (Pakistan) with Iranian finds.
BALUCHISTAN_SITES = {"Nindowari-damb", "Sibri", "Ornach area", "Miri Qalat", "Murda Sang"}
IRAN_SITES = {"Susa", "Tepe Yahya", "Luristan"}
WEST_ASIAN_REGIONS = {"Persian Gulf", "Mesopotamia"}
CENTRAL_ASIAN_REGION = "Central Asia"
# Same physical seal: BM 123208 (export site label 'Dilmun') is the Ur seal
# U.17649, Gadd 1932 no. 16 (see the 2026-10-06 finds-abroad census).
DUPLICATE_WITNESS = {"6000.1": "3898.1"}


def natural_key(record_id: str):
    out = []
    for part in re.split(r"[.]", record_id):
        out.append((0, int(part), "") if part.isdigit() else (1, 0, part))
    return tuple(out)


def assign_group(face: dict) -> str:
    region, site = face["region"], face["site"]
    if region in SOUTH_ASIAN_REGIONS:
        return "south_asia"
    if region == "Iranian Plateau":
        if site in BALUCHISTAN_SITES:
            return "south_asia"
        if site in IRAN_SITES:
            return "west_asia"
        raise ValueError(f"unassigned Iranian Plateau site {site!r}")
    if region in WEST_ASIAN_REGIONS:
        return "west_asia"
    if region == CENTRAL_ASIAN_REGION:
        return "central_asia"
    if region == "Other":
        return "unprovenanced"
    raise ValueError(f"unassigned region {region!r}")


def west_subregion(face: dict) -> str:
    if face["region"] == "Persian Gulf":
        return "Gulf"
    if face["region"] == "Mesopotamia":
        return "Mesopotamia"
    return "Iran"


def peripheral_label(face: dict) -> str | None:
    """South Asian peripheral/control groups, fixed before outcomes."""
    if face["region"] == "Gujarat/Kutch":
        return "gujarat_kutch"
    if face["region"] == "Eastern Headwaters":
        return "eastern_headwaters"
    if face["site"] == "Kalibangan":
        return "kalibangan"
    if face["site"] in BALUCHISTAN_SITES:
        return "baluchistan_makran"
    if face["region"] == "Upper Indus":
        return "upper_indus"
    if face["site"] == "Chanhu-daro":
        return "chanhudaro_control"
    return None


# ---------------------------------------------------------------- media
def normalized_type(face: dict) -> str:
    t = face["object_type"]
    return {"POsT:T:g": "POT:T:g", "POT:T:S": "POT:T:s"}.get(t, t)


def medium(face: dict) -> str:
    t = normalized_type(face)
    if t == "SEAL:S":
        return "square"
    if t in ("SEAL:C", "SEAL:CY"):
        return "round"
    if t.startswith("SEAL"):
        return "seal_other"
    if t.startswith("POT"):
        return "pottery"
    if t.startswith("TAG"):
        return "tag"
    if t.startswith("TAB"):
        return "tablet"
    return "misc"


SEAL_MEDIA = {"square", "round", "seal_other"}

LADDERS = {
    "primary": {
        "square": [("square",), ("seal",), ("all",)],
        "round": [("seal",), ("all",)],
        "seal_other": [("seal",), ("all",)],
        "pottery": [("pottery",), ("nonseal",), ("all",)],
        "tag": [("tag",), ("nonseal",), ("all",)],
        "tablet": [("tablet",), ("nonseal",), ("all",)],
        "misc": [("nonseal",), ("all",)],
    },
    "square_only": {
        "square": [("square",), ("seal",), ("all",)],
        "round": [("square",), ("seal",), ("all",)],
        "seal_other": [("square",), ("seal",), ("all",)],
        "pottery": [("pottery",), ("nonseal",), ("all",)],
        "tag": [("tag",), ("nonseal",), ("all",)],
        "tablet": [("tablet",), ("nonseal",), ("all",)],
        "misc": [("nonseal",), ("all",)],
    },
    "any_object": {m: [("all",)] for m in
                   ("square", "round", "seal_other", "pottery", "tag", "tablet", "misc")},
}


def in_level(med: str, level: str) -> bool:
    if level == "all":
        return True
    if level == "seal":
        return med in SEAL_MEDIA
    if level == "nonseal":
        return med not in SEAL_MEDIA
    return med == level


# ---------------------------------------------------------------- parsing
def parse_code(face: dict) -> dict:
    """Return reading-order lines and edge flags.

    The ICIT code is visual left-to-right with '+' for an intact edge and
    ']' (left) or '[' (right) for a broken edge. Reading order reverses it,
    so the reading start is the visual right edge.
    """
    code = face["text_code_visual_ltr"]
    first, last = code[0], code[-1]
    body = code
    if first in "+]":
        body = body[1:]
    if body and body[-1] in "+[":
        body = body[:-1]
    if re.search(r"[+\[\]]", body):
        raise ValueError(f"internal edge marker in {face['record_id']}")
    lines_visual = [[t.zfill(3) for t in line.split("-") if t] for line in body.split("/")]
    tokens_visual = [t for line in lines_visual for t in line]
    if tokens_visual != face["signs_visual_ltr"]:
        raise ValueError(f"token mismatch in {face['record_id']}")
    lines_reading = [list(reversed(line)) for line in reversed(lines_visual)]
    has_damage_marker = (UNKNOWN in tokens_visual) or ("[" in code) or ("]" in code)
    trust_edges = face["metadata"].get("complete", "").strip().upper() == "Y" or has_damage_marker
    start_known = last == "+" and trust_edges
    end_known = first == "+" and trust_edges
    return {
        "lines": lines_reading,
        "single_line": len(lines_reading) == 1,
        "start_known": start_known,
        "end_known": end_known,
        "length": len(tokens_visual),
    }


def structure_string(parsed: dict) -> str:
    """Mask signs as X: a damage pattern without sign identities."""
    parts = []
    for line in parsed["lines"]:
        parts.append("-".join(t if t in (UNKNOWN, BLANK) else "X" for t in line))
    s = "/".join(parts)
    return ("+" if parsed["start_known"] else "?") + s + ("+" if parsed["end_known"] else "?")


def is_full_comparator(face: dict, parsed: dict) -> bool:
    toks = parsed["lines"][0] if parsed["single_line"] else []
    return (parsed["single_line"] and face["complete_observed"] and parsed["start_known"]
            and parsed["end_known"] and UNKNOWN not in toks and BLANK not in toks)


# ---------------------------------------------------------------- events
def spans(text: dict):
    """Yield (tokens, at_start, at_end) for maximal runs of readable signs.

    at_start/at_end are True only when the run touches a known text edge of a
    single-line text. Lines of multi-line texts never receive edges.
    """
    single = text["single_line"]
    for line in text["lines"]:
        run, run_start = [], 0
        for i, tok in enumerate(line + [None]):
            if tok is None or tok in (UNKNOWN, BLANK):
                if run:
                    at_start = single and text["start_known"] and run_start == 0
                    at_end = single and text["end_known"] and i == len(line)
                    yield run, at_start, at_end
                run, run_start = [], i + 1
            else:
                run.append(tok)


def events(text: dict, order: int = 2):
    """Yield (history_tuple, target). History has length 1..order-1.

    Events whose history would be empty (first sign of a span without a known
    start) are skipped, so no event conditions on unobserved context.
    """
    for run, at_start, at_end in spans(text):
        seq = ([BOS] if at_start else []) + run + ([EOS] if at_end else [])
        first_target = 1
        for i in range(first_target, len(seq)):
            h = tuple(seq[max(0, i - (order - 1)):i])
            yield h, seq[i]


def known_signs(text: dict):
    return [t for line in text["lines"] for t in line if t not in (UNKNOWN, BLANK)]


# ---------------------------------------------------------------- matching
def comparator_window(test: dict, comp_tokens: list[str]) -> dict | None:
    """Apply the test text's damage mask and edge flags to a complete comparator."""
    L, M = test["length"], len(comp_tokens)
    sk, ek = test["start_known"], test["end_known"]
    if sk and ek:
        if M != L:
            return None
        window = comp_tokens
    else:
        if M < L:
            return None
        if sk:
            window = comp_tokens[:L]
        elif ek:
            window = comp_tokens[M - L:]
        else:
            off = (M - L) // 2
            window = comp_tokens[off:off + L]
    mask = test["lines"][0]
    masked = [m if m in (UNKNOWN, BLANK) else w for m, w in zip(mask, window)]
    return {"lines": [masked], "single_line": True, "start_known": sk, "end_known": ek,
            "length": L}


def choose_cell(test_face: dict, test_text: dict, pool: list[dict], ladder_name: str):
    """Return (level, list of pool indices) for the first ladder level with
    at least MIN_COMPARATORS eligible complete comparators."""
    ladder = LADDERS[ladder_name][medium(test_face)]
    tried = []
    for (level,) in ladder:
        idx = [i for i, p in enumerate(pool)
               if p["full"] and in_level(p["medium"], level)
               and comparator_window(test_text, p["text"]["lines"][0]) is not None]
        tried.append((level, len(idx)))
        if len(idx) >= MIN_COMPARATORS:
            return level, idx, tried
    return None, [], tried


# ---------------------------------------------------------------- folds
class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def assign_folds(pool: list[dict], k: int = K_FOLDS) -> list[int]:
    """Group by object family and identical code string; hash the component's
    smallest record id into one of k folds."""
    uf = UnionFind()
    by_family, by_code = {}, {}
    for p in pool:
        rid = p["record_id"]
        uf.find(rid)
        fam, code = p["face"]["object_family_id"], p["face"]["text_code_visual_ltr"]
        if fam in by_family:
            uf.union(by_family[fam], rid)
        else:
            by_family[fam] = rid
        if code in by_code:
            uf.union(by_code[code], rid)
        else:
            by_code[code] = rid
    members = defaultdict(list)
    for p in pool:
        members[uf.find(p["record_id"])].append(p["record_id"])
    fold_of = {}
    for root, ids in members.items():
        cid = min(ids, key=natural_key)
        f = int(hashlib.sha256(("ff-" + cid).encode()).hexdigest(), 16) % k
        for rid in ids:
            fold_of[rid] = f
    return [fold_of[p["record_id"]] for p in pool]


# ---------------------------------------------------------------- loading
def load_faces():
    faces = [json.loads(line) for line in FACES.open(encoding="utf-8")]
    out = []
    for f in faces:
        text = parse_code(f)
        out.append({
            "record_id": f["record_id"], "face": f, "text": text,
            "group": assign_group(f), "medium": medium(f),
            "full": is_full_comparator(f, text),
            "clean": bool(f["clean_rtl_singleline"]),
            "peripheral": peripheral_label(f) if assign_group(f) == "south_asia" else None,
        })
    return out


def vocabulary(faces: list[dict]) -> list[str]:
    signs = sorted({t for f in faces for t in known_signs(f["text"])})
    return signs + [EOS]


def dedupe_test_faces(test: list[dict]) -> list[dict]:
    """Within a test group collapse faces of one object family with identical codes."""
    seen, out = set(), []
    for f in sorted(test, key=lambda x: natural_key(x["record_id"])):
        key = (f["face"]["object_family_id"], f["face"]["text_code_visual_ltr"])
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def counter_top(c: Counter, n=5):
    return [[k, v] for k, v in c.most_common(n)]
