"""Deterministically build the edition-linked external contact register (Issue #22).

Mines held local primary editions and catalogues:
- CDLI catalogue (cdli_cat.csv) and transliterations (cdliatf_unblocked.atf)
- ORACC Old Akkadian (oakk.zip) and Ur III (epsd2-admin-ur3.zip) JSON archives
- Round-seal catalogue joins (experiments/2026-10-12-round-seal-tradition/joins.csv)
- External readable records inventory (experiments/2026-10-27-readable-external-records/sources.json)
- External phonetic anchor audit (research/literature/external_phonetic_anchor_audit.md)

Writes tracked structured register outputs under experiments/2026-11-22-external-contact-register/
and local-only bulk excerpts and exclusion audits under data/raw/2026-11-22-external-contact-register/.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments" / "2026-11-22-external-contact-register"
RAW_OUT_DIR = ROOT / "data" / "raw" / "2026-11-22-external-contact-register"

SOURCE_PATHS = {
    "cdli_cat": "data/raw/2026-10-21-head-direction-corpora/src-cdli-data-cat-v1/cdli_cat.csv",
    "cdli_atf": "data/raw/2026-10-21-head-direction-corpora/src-cdli-data-atf-v1/cdliatf_unblocked.atf",
    "oracc_oakk": "data/raw/2026-10-21-head-direction-corpora/src-oracc-oakk-archive-v8/oakk.zip",
    "oracc_ur3": "data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin",
    "round_joins": "experiments/2026-10-12-round-seal-tradition/joins.csv",
    "ext_sources": "experiments/2026-10-27-readable-external-records/sources.json",
    "ext_captures": "data/raw/2026-10-27-readable-external-records/web-captures.json",
    "gadd_pdf": "research/root_primary/gadd1932.pdf",
    "anchor_audit": "research/literature/external_phonetic_anchor_audit.md",
}

MELUHHA_PAT = re.compile(r"me-?\[?lu(?:h|-uh)\]?-?\[?h?a|meluhha|me-luh", re.IGNORECASE)
MELUHHA_FALSE_POSITIVES = {
    "P135796": "Personal name e-lum-me-luh in Ur III messenger text TUT 202, not Meluhha.",
    "P257207": "Sumerian compound [me-luh-luh]-ha 'purification rites' in Lament for Nippur.",
    "P346234": "Sumerian verbal form u3-me-luh-luh 'wash/cleanse' in UET 6, 0149.",
}
CONTEMP_PERIOD_TOKENS = ("Old Akkadian", "Lagash II", "Ur III", "Old Babylonian")

DILMUN_PHYSICAL_PIDS = [
    "P507617",
    "P507618",
    "P507619",
    "P507620",
    "P507621",
    "P507622",
    "P507623",
]
DILMUN_COMPOSITE_MAP = {
    "P507617": ["P507625 (RIME 4.add39.02.01 composite)"],
    "P507618": ["P507626 (RIME 4.add39.02.02 composite)"],
    "P507619": ["P507626 (RIME 4.add39.02.02 composite)"],
    "P507620": ["P507627 (RIME 4.add39.02.03 composite ?)"],
    "P507621": [],
    "P507622": ["P507626 (RIME 4.add39.02.02 composite)"],
    "P507623": ["P507624 (RIME 4.add39.01.01 composite)"],
}

def tok(pattern: str) -> re.Pattern[str]:
    """Match a whole whitespace-delimited cuneiform token (hyphens stay inside tokens)."""
    return re.compile(rf"(?<![A-Za-z0-9\-]){pattern}(?![A-Za-z0-9\-])", re.IGNORECASE)


# Deterministic commodity, unit, title, and institutional patterns for normalized ATF (editorial _, #, ?, !, [, ] stripped).
COMMODITY_PATTERNS = [
    (re.compile(r"(?:\{gesz\}|gesz\s+)ab-ba(?:\s+|-)me-luh|gesz\s+ab-me-luh|(?<![a-z\-])ab-ba\s+me-luh", re.I), "Meluhha ab-ba wood ({gesz}ab-ba me-luh-ha)"),
    (re.compile(r"(?:\{gesz\}|gesz\s+)?mes(?:\s+|-)me-luh", re.I), "Meluhha mes-wood ({gesz}mes me-luh-ha)"),
    (re.compile(r"\{gesz\}esi|(?<![a-z\-])i-si\s+im-ku4|(?<![a-z\-])i-szi-a-am", re.I), "ebony / esu-wood ({gesz}esi)"),
    (re.compile(r"dar(?:\{muszen\})?\s+me-luh", re.I), "Meluhha bird / figurine (dar{muszen} me-luh-ha)"),
    (re.compile(r"\{na4\}gug|(?<![a-z\-])gug\s+gi-rin|(?<![a-z\-])gug(?:\s+me-luh)", re.I), "carnelian ({na4}gug)"),
    (re.compile(r"(?:\{na4\})?za-gin3", re.I), "lapis lazuli (za-gin3)"),
    (tok(r"uruda(?:-me-luh-ha)?"), "copper (uruda)"),
    (tok(r"nagga"), "tin (nagga)"),
    (re.compile(r"(?<![a-z\-])ku3-babbar(?![a-z\-])|(?<![a-z\-])ku3\s+NE(?![a-z\-])"), "silver (ku3-babbar)"),
    (tok(r"ku3-sig17"), "gold (ku3-sig17)"),
    (tok(r"zabar"), "bronze (zabar)"),
    (re.compile(r"(?<![a-z\-])ma2\s+(?:\d+\(asz@c\)\s+)?me-luh|\{gesz\}ma2-gi4-lum", re.I), "Meluhha boat (ma2 me-luh-ha)"),
    (re.compile(r"(?<![a-z\-])ma2\s+dilmun", re.I), "Dilmun boat (ma2 dilmun)"),
    (re.compile(r"\{gesz\}gu-za|gesz\s+gu-za|\{gesz\}guzza", re.I), "chair / throne ({gesz}gu-za)"),
    (re.compile(r"\{gesz\}banszur", re.I), "table ({gesz}banszur)"),
    (re.compile(r"\{gesz\}giri3-gub", re.I), "footstool ({gesz}giri3-gub)"),
    (re.compile(r"(?:\{gesz\})?mu10-us2", re.I), "wood / timber component (mu10-us2)"),
    (re.compile(r"\{gesz\}dur2", re.I), "stool / seat ({gesz}dur2)"),
    (re.compile(r"(?<![a-z\-])ur\s+gun3-a\s+me-luh", re.I), "spotted dog of Meluhha (ur gun3-a me-luh-ha)"),
    (tok(r"sze(?:-ba)?"), "barley / grain (sze)"),
    (tok(r"siki"), "wool (siki)"),
    (tok(r"(?:i3-gesz|i3-ba|i3-nun|i3)"), "oil / sesame oil (i3)"),
    (tok(r"kasz"), "beer (kasz)"),
    (tok(r"ninda"), "bread (ninda)"),
    (tok(r"(?:zi3|dabin)"), "flour (zi3)"),
    (tok(r"(?:udu(?:-nita2)?|sila4)"), "sheep / lamb (udu)"),
    (tok(r"masz2"), "goat / kid (masz2)"),
    (tok(r"gu4"), "ox / cattle (gu4)"),
    (tok(r"gu2-tur"), "lentils / small pulses (gu2-tur)"),
    (tok(r"kusz"), "leather / hide (kusz)"),
    (tok(r"(?:gada|tug2)"), "textile / linen (tug2 / gada)"),
    (re.compile(r"(?:\{gesz\})?pesz3(?![a-z0-9\-])", re.I), "figs ({gesz}pesz3)"),
    (re.compile(r"(?<![a-z\-])zu2\s+am-si(?![a-z\-])|(?<![a-z\-])zu2\s+si(?![a-z\-])", re.I), "ivory (zu2 am-si)"),
    (tok(r"(?:szim|li)"), "aromatics / juniper (szim / li)"),
    (tok(r"naga"), "alkali / potash (naga)"),
    (tok(r"ku6"), "fish (ku6)"),
    (tok(r"zu2-lum"), "dates (zu2-lum)"),
    (re.compile(r"gu2-asz-tum", re.I), "vessel (musarrirtum / gu2-asz-tum)"),
]

UNIT_PATTERNS = [
    (tok(r"gur"), "unit: gur (~300 L)"),
    (re.compile(r"\d+\(barig|(?<![a-z\-])barig(?![a-z\-])", re.I), "unit: barig (~60 L)"),
    (re.compile(r"\d+\(ban2|(?<![a-z\-])ban2(?![a-z\-])", re.I), "unit: ban2 (~10 L)"),
    (tok(r"sila3"), "unit: sila3 (~1 L)"),
    (tok(r"ma-na"), "unit: ma-na (mina, ~500 g)"),
    (tok(r"gin2"), "unit: gin2 (shekel, ~8.3 g)"),
    (tok(r"gun2"), "unit: gun2 (talent, ~30 kg)"),
    (tok(r"e2-ba-an"), "unit: e2-ba-an (pair)"),
    (tok(r"sar"), "unit: sar (area/volume)"),
]

TITLE_PATTERNS = [
    (re.compile(r"eme-bal\s+me-luh", re.I), "eme-bal me-luh-ha (interpreter of Meluhha)"),
    (re.compile(r"(?<![a-z\-])lu2\s+me-luh", re.I), "lu2 me-luh-ha (man of Meluhha)"),
    (re.compile(r"(?<![a-z\-])dumu\s+me-luh", re.I), "dumu me-luh-ha (son of Meluhha / Meluhhan)"),
    (re.compile(r"(?<![a-z\-])ugula\s+me-luh", re.I), "ugula me-luh-ha (overseer of Meluhha)"),
    (re.compile(r"(?<![a-z\-])ra-gaba\s+me-luh", re.I), "ra-gaba me-luh-ha (mounted messenger of Meluhha)"),
    (re.compile(r"(?<![a-z\-])nu-banda3\s+ma2\s+me-luh", re.I), "nu-banda3 ma2 me-luh-ha (captain/overseer of Meluhha boat)"),
    (re.compile(r"(?<![a-z\-])lu2-tukul\s+ma2\s+me-luh", re.I), "lu2-tukul ma2 me-luh-ha (armed attendant of Meluhha boat)"),
    (re.compile(r"(?<![a-z\-])gurusz\s+ma2\s+me-luh", re.I), "gurusz ma2 me-luh-ha (worker of Meluhha boat)"),
    (re.compile(r"(?<![a-z\-])maszkim\s+ma2\s+dilmun", re.I), "maszkim ma2 dilmun (commissioner of Dilmun boat)"),
    (re.compile(r"(?<![a-z\-])ensi2\s+szuszin", re.I), "ensi2 szuszin{ki} (governor of Susa)"),
    (tok(r"ensi2"), "ensi2 (governor)"),
    (tok(r"lugal"), "lugal (king)"),
    (tok(r"sukkal"), "sukkal (royal messenger / chancellor)"),
    (tok(r"dub-sar"), "dub-sar (scribe)"),
    (tok(r"sagi"), "sagi (cup-bearer)"),
    (tok(r"ugula"), "ugula (overseer)"),
    (tok(r"nu-banda3"), "nu-banda3 (captain / inspector)"),
    (tok(r"ra-gaba"), "ra-gaba (mounted messenger)"),
    (tok(r"maszkim"), "maszkim (commissioner / requisitioner)"),
    (tok(r"szitim"), "szitim (builder)"),
    (tok(r"kuruszda"), "kuruszda (animal fattener)"),
    (tok(r"aga3-us2"), "aga3-us2 (soldier / guard)"),
    (re.compile(r"(?<![A-Za-z0-9\-])ARAD2?(?![A-Za-z0-9\-])"), "ARAD2 (servant)"),
    (tok(r"erin2"), "erin2 (troops / work-crew)"),
    (tok(r"sanga"), "sanga (temple administrator)"),
    (tok(r"szabra"), "szabra (chief steward)"),
    (tok(r"dam-gar3"), "dam-gar3 (merchant)"),
    (tok(r"lu2-?kiszib3"), "lu2-kiszib3 (seal-bearer)"),
    (re.compile(r"(?<![a-z\-])lu2\s+\{gesz\}tukul(?![a-z\-])", re.I), "lu2 {gesz}tukul (armed messenger)"),
]

SETTLEMENT_PATTERNS = [
    (re.compile(r"e2-duru5[- ]me-luh", re.I), "e2-duru5 me-luh-ha (village of Meluhha)"),
    (re.compile(r"i3-dub\s+(?:e2-duru5[- ]|sza3\s+)?me-luh", re.I), "i3-dub me-luh-ha (granary of Meluhha)"),
    (re.compile(r"\{gesz\}kiri6\s+me-luh", re.I), "{gesz}kiri6 me-luh-ha (orchard of Meluhha)"),
    (re.compile(r"gu2-ab-ba\{ki\}", re.I), "gu2-ab-ba{ki} (Gu'abba seaport)"),
    (re.compile(r"kur\s+me-luh|sza-du\s+me-luh", re.I), "kur me-luh-ha (land/mountain of Meluhha)"),
    (re.compile(r"ma2(?:#)?\s+(?:\d+\(asz@c\)#?\s+)?me-luh|\{gesz\}ma2-gi4-lum", re.I), "ma2 me-luh-ha (Meluhha boat)"),
]

KNOWN_ROYAL_PATTERNS = [
    (re.compile(r"szar-ru-ki-in|sargon", re.I), "Sargon of Akkad"),
    (re.compile(r"ma-an-isz-di2-su|ma-<an>-isz-di2-su", re.I), "Manishtushu"),
    (re.compile(r"na-ra-am-\{d\}suen", re.I), "Naram-Suen"),
    (re.compile(r"gu3-de2-a", re.I), "Gudea"),
    (re.compile(r"\{d\}szul-gi|szul-gi", re.I), "Shulgi"),
    (re.compile(r"\{d\}amar-\{d\}suen|amar-\{d\}suen", re.I), "Amar-Suen"),
    (re.compile(r"\{d\}szu-\{d\}suen|szu-\{d\}suen", re.I), "Shu-Suen"),
    (re.compile(r"\{d\}i-bi2-\{d\}suen|i-bi2-\{d\}suen", re.I), "Ibbi-Suen"),
    (re.compile(r"ia-ag-?\[?li-il3", re.I), "Yagli-El"),
    (re.compile(r"ri-mu-um|ri-mi-um", re.I), "Rimum"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_region(prov: str, default: str = "Mesopotamia (unprovenanced)") -> str:
    p = (prov or "").strip()
    if not p or p.lower().startswith("uncertain"):
        return default
    if "Susa" in p:
        return "Iran (Susa)"
    if "Bahrain" in p or "Dilmun" in p or "A'ali" in p or "Qal'at" in p:
        return "Gulf (Bahrain)"
    if "Failaka" in p:
        return "Gulf (Failaka)"
    city = p.split("(")[0].strip().rstrip("?").strip()
    return f"Mesopotamia ({city})"


def extract_oracc_meluhha(zip_path: Path, prefix: str) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Return (meluhha_lemmas_by_pid, catalogue_members) from an ORACC zip archive."""
    mel_data: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(zip_path) as z:
        gq = json.loads(z.read(prefix + "gloss-qpn.json"))
        cat = json.loads(z.read(prefix + "catalogue.json")).get("members", {})
        xis_map = gq.get("instances", {})
        pids = set()
        for entry in gq.get("entries", []):
            if "meluh" in entry.get("cf", "").lower():
                refs = xis_map.get(entry.get("xis", ""), [])
                for ref in refs:
                    pid = ref.split(".")[0].split(":")[-1]
                    if pid.startswith("P"):
                        pids.add(pid)
        namelist = set(z.namelist())
        for pid in sorted(pids):
            fp = f"{prefix}corpusjson/{pid}.json"
            pns: list[str] = []
            rns: list[str] = []
            nouns: list[tuple[str, str, str]] = []
            forms: list[str] = []
            if fp in namelist:
                j = json.loads(z.read(fp))
                def walk(n: Any) -> None:
                    if isinstance(n, dict):
                        if n.get("node") == "l":
                            f = n.get("f", {})
                            pos = f.get("pos", "")
                            cf = f.get("cf", "")
                            gw = f.get("gw", "")
                            form = f.get("form", "")
                            if form:
                                forms.append(form)
                            if pos == "PN" and cf:
                                pns.append(cf)
                            elif pos == "RN" and cf:
                                rns.append(cf)
                            elif pos in ("N", "GN", "SN", "AN") and cf:
                                nouns.append((form, cf, gw))
                        for v in n.values():
                            walk(v)
                    elif isinstance(n, list):
                        for item in n:
                            walk(item)
                walk(j)
            mel_data[pid] = {
                "pns": sorted(set(pns)),
                "rns": sorted(set(rns)),
                "nouns": nouns,
                "text_joined": " ".join(forms),
                "cat": cat.get(pid, {}),
            }
    return mel_data, cat


ORACC_RN_CANON = {
    "šulgi": "Shulgi (RN)",
    "šulgi(r)": "Shulgi (RN)",
    "amarsuenak": "Amar-Suen (RN)",
    "amarsuen": "Amar-Suen (RN)",
    "šusuen": "Shu-Suen (RN)",
    "ibbisuen": "Ibbi-Suen (RN)",
    "urnammak": "Ur-Namma (RN)",
    "gudea": "Gudea (RN)",
    "šarrukin": "Sargon of Akkad (RN)",
    "naramsuen": "Naram-Suen (RN)",
}


def clean_atf_for_tokens(text: str) -> str:
    """Strip ATF editorial markers (_, #, ?, !, [, ]) while preserving determinatives and hyphens."""
    return re.sub(r"[_#?!\[\]<>]", "", text)


def extract_atf_fields(
    atf_lines: list[str],
    oracc_info: dict[str, Any] | None = None,
    extra_seal_lines: list[str] | None = None,
    is_administrative: bool = True,
) -> dict[str, Any]:
    """Deterministically extract goods/units, personal names, titles, settlements, and seal lines."""
    text_lines = [
        l for l in atf_lines
        if not l.startswith(("#", "$", ">", "&"))
    ]
    joined = clean_atf_for_tokens("\n".join(text_lines))
    if oracc_info and oracc_info.get("text_joined"):
        # Also normalize Unicode subscripts/diacritics in ORACC forms for fallback matching
        oracc_ascii = (
            oracc_info["text_joined"]
            .replace("š", "sz").replace("Š", "SZ")
            .replace("ŋ", "g")
            .replace("₂", "2").replace("₃", "3").replace("₄", "4").replace("₅", "5")
            .replace("{geš}", "{gesz}")
        )
        joined_for_match = joined + "\n" + clean_atf_for_tokens(oracc_ascii)
    else:
        joined_for_match = joined

    goods: list[str] = []
    for pat, label in COMMODITY_PATTERNS:
        if pat.search(joined_for_match):
            goods.append(label)
    for pat, label in UNIT_PATTERNS:
        if pat.search(joined_for_match):
            goods.append(label)

    titles: list[str] = []
    for pat, label in TITLE_PATTERNS:
        if pat.search(joined_for_match):
            titles.append(label)
    # Also check vertical multiline "ensi2\n4. szuszin{ki}" on Susa seals
    if re.search(r"(?<![a-z\-])ensi2\s+(?:\d+\.\s+)?szuszin", joined_for_match, re.I):
        if "ensi2 szuszin{ki} (governor of Susa)" not in titles:
            titles.insert(0, "ensi2 szuszin{ki} (governor of Susa)")

    settlements: list[str] = []
    for pat, label in SETTLEMENT_PATTERNS:
        if pat.search(joined_for_match):
            settlements.append(label)

    # Extract seal lines first
    seal_lines: list[str] = []
    in_seal = False
    seal_candidates: list[str] = []
    seal_col_line = 0
    for l in atf_lines:
        if l.startswith("@seal"):
            in_seal = True
            seal_col_line = 0
            continue
        elif l.startswith("@column") and in_seal:
            seal_col_line = 0
            continue
        elif l.startswith("@"):
            in_seal = False
        if in_seal and re.match(r"^\d+['.]*\s+", l):
            cleaned = re.sub(r"^\d+['.]*\s+", "", l).strip()
            seal_lines.append(cleaned)
            seal_col_line += 1
            if seal_col_line == 1:
                cand = clean_atf_for_tokens(cleaned).strip()
                if cand and len(cand) >= 3 and not any(k in cand.lower() for k in ("lugal", "ensi2", "dub-sar", "arad", "...", "x x", "szu-{d}suen", "amar-{d}suen", "i-bi2-{d}suen", "szul-gi")):
                    seal_candidates.append(cand)

    # Personal names: authoritative ORACC PN/RN lemmas when available; structured ATF fallback for administrative texts
    pns: set[str] = set()
    if oracc_info:
        for pn in oracc_info.get("pns", []):
            if pn.lower() == "meluhha":
                continue
            pns.add(pn)
        for rn in oracc_info.get("rns", []):
            canon = ORACC_RN_CANON.get(rn.lower(), f"{rn} (RN)")
            pns.add(canon)
    else:
        for pat, label in KNOWN_ROYAL_PATTERNS:
            if pat.search(joined_for_match):
                pns.add(f"{label} (RN)")
        for cand in seal_candidates:
            if not cand.startswith("{d}"):
                pns.add(cand)
        if is_administrative:
            stop_words = {
                "lugal", "ensi2", "dub-sar", "e2", "uruda", "sze", "ma2", "gu",
                "mu", "sza", "a-na", "bi", "x", "me-luh-ha", "gu-szum", "e2-gal",
                "dumu", "arad2", "szu-{d}suen", "amar-{d}suen", "i-bi2-{d}suen",
                "{d}szu-{d}suen", "{d}amar-{d}suen", "{d}i-bi2-{d}suen", "{d}szul-gi",
                "sikil-la", "gar-ra", "us2-sa", "nam-erim2", "ba-ti", "szu-ba-ti",
            }
            for l in text_lines:
                if re.match(r"^\d+['.]*\s+", l):
                    cleaned = clean_atf_for_tokens(re.sub(r"^\d+['.]*\s+", "", l)).strip()
                    # Administrative provenance/agency formulas: "ki <PN>-ta", "kiszib3 <PN>", "giri3 <PN>", "a-na <PN>"
                    m_ki = re.search(r"(?:\bki\s+([a-z0-9\{\}\-\']{3,35}?)-ta\b|\b(?:kiszib3|giri3|a-na)\s+([a-z0-9\{\}\-\']{3,35}?)(?:-ta|-sze3|\s|$))", cleaned)
                    if m_ki:
                        cand = (m_ki.group(1) or m_ki.group(2) or "").strip("-")
                        if cand and cand.lower() not in stop_words and not cand[0].isdigit() and "-" in cand and "{ki}" not in cand and not cand.startswith("{d}"):
                            pns.add(cand)
                    m_ur = re.findall(r"(?<![a-z\-])(ur-\{d\}[a-z0-9\-]+|lu2-\{d\}[a-z0-9\-]+|szu-\{d\}[a-z0-9\-]+|be-li2-[a-z0-9\-]+|i3-li2-[a-z0-9\-]+|a-hu-[a-z0-9\-]+|ur-ab-ba|ur-sa6-ga|gal-zu)(?![a-z\-])", cleaned)
                    for name in m_ur:
                        n = name.rstrip("-")
                        if n.lower() not in stop_words:
                            pns.add(n)

    if extra_seal_lines:
        seal_lines.extend(extra_seal_lines)

    return {
        "goods_and_units": list(dict.fromkeys(goods)),
        "personal_names": sorted(pns),
        "titles_and_offices": list(dict.fromkeys(titles)),
        "settlements_and_places": list(dict.fromkeys(settlements)),
        "seal_lines": seal_lines,
    }


def main() -> None:
    EXP_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Compute exact SHA-256 hashes of all held input files
    source_hashes: dict[str, dict[str, Any]] = {}
    for key, rel in SOURCE_PATHS.items():
        fp = ROOT / rel
        if not fp.exists():
            raise FileNotFoundError(f"Required held input missing: {rel}")
        source_hashes[key] = {
            "logical_path": rel,
            "physical_path": str(fp.resolve()),
            "bytes": fp.stat().st_size,
            "sha256": sha256_file(fp),
        }

    # 2. Extract ORACC Meluhha texts and lemmas (OAKK + Ur III)
    oakk_mel, oakk_cat = extract_oracc_meluhha(ROOT / SOURCE_PATHS["oracc_oakk"], "epsd2/admin/oakk/")
    ur3_mel, ur3_cat = extract_oracc_meluhha(ROOT / SOURCE_PATHS["oracc_ur3"], "epsd2/admin/ur3/")
    oracc_mel_all: dict[str, dict[str, Any]] = {}
    for pid, info in oakk_mel.items():
        info["oracc_corpus"] = "oracc_oakk"
        oracc_mel_all[pid] = info
    for pid, info in ur3_mel.items():
        info["oracc_corpus"] = "oracc_ur3"
        oracc_mel_all[pid] = info

    # 3. Pass 1 on cdli_cat.csv: identify Susa Ur III sealed/seal objects, Dilmun physical/composites, AO 22310, and cache metadata
    cat_path = ROOT / SOURCE_PATHS["cdli_cat"]
    atf_path = ROOT / SOURCE_PATHS["cdli_atf"]

    # First scan ATF for all Meluhha candidate P-numbers (broad regex) and record exact lines
    atf_mel_lines: dict[str, list[str]] = collections.defaultdict(list)
    cur_p: str | None = None
    with atf_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("&P"):
                cur_p = line[1:8]
            elif cur_p and MELUHHA_PAT.search(line):
                atf_mel_lines[cur_p].append(line.strip())

    mel_candidate_pids = set(atf_mel_lines.keys()) | set(oracc_mel_all.keys()) | {"P525331"}

    cat_rows: dict[str, dict[str, str]] = {}
    susa_ur3_physical_pids: set[str] = set()
    susa_ur3_composite_seals: dict[str, dict[str, str]] = {}  # seal_id -> row
    susa_ur3_all_count = 0
    failaka_later_seals: list[dict[str, str]] = []

    with cat_path.open("r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            id_text = row.get("id_text", "").strip()
            if not id_text.isdigit():
                continue
            pid = "P" + id_text.zfill(6)
            prov = row.get("provenience", "")
            period = row.get("period", "")
            otype = row.get("object_type", "")
            pub = row.get("primary_publication", "")
            seal_id = row.get("seal_id", "").strip()
            seal_info = row.get("seal_information", "").strip()

            if pid in mel_candidate_pids or pid in DILMUN_PHYSICAL_PIDS or pid in ("P507624", "P507625", "P507626", "P507627"):
                cat_rows[pid] = row

            if "Susa" in prov and "Ur III" in period:
                susa_ur3_all_count += 1
                if seal_id or seal_info or "seal" in otype.lower():
                    cat_rows[pid] = row
                    if "composite" in pub.lower() and "seal" in otype.lower():
                        susa_ur3_composite_seals[seal_id] = row
                    else:
                        susa_ur3_physical_pids.add(pid)

            if pid in ("P511661", "P511663"):
                failaka_later_seals.append({"pid": pid, "provenience": prov, "period": period, "museum_no": row.get("museum_no", ""), "primary_publication": pub})

    # Partition Meluhha candidates into Cohort 1 vs excluded (false positives, later periods, undated)
    cohort1_mel_pids: list[str] = []
    excluded_mel_audit: list[dict[str, Any]] = []
    for pid in sorted(mel_candidate_pids):
        if pid == "P525331":
            continue  # Added explicitly with Louvre + CDLI combined metadata
        if pid in MELUHHA_FALSE_POSITIVES:
            excluded_mel_audit.append({
                "pid": pid,
                "reason": "lexical_or_onomastic_false_positive",
                "detail": MELUHHA_FALSE_POSITIVES[pid],
                "period": cat_rows.get(pid, {}).get("period", ""),
                "sample_lines": atf_mel_lines.get(pid, [])[:3],
            })
            continue
        row = cat_rows.get(pid, {})
        per = row.get("period", "")
        if not per and pid in oracc_mel_all:
            per = oracc_mel_all[pid]["cat"].get("period", "")
        if any(tok in per for tok in CONTEMP_PERIOD_TOKENS):
            cohort1_mel_pids.append(pid)
        else:
            excluded_mel_audit.append({
                "pid": pid,
                "reason": "later_or_undated_period_excluded_from_cohort_1",
                "period": per or "(blank in CDLI catalogue)",
                "provenience": row.get("provenience", ""),
                "primary_publication": row.get("primary_publication", ""),
                "sample_lines": atf_mel_lines.get(pid, [])[:2],
            })

    # Pass 2 on cdliatf_unblocked.atf: collect full ATF blocks for all needed P-numbers
    needed_atf_pids = (
        set(cohort1_mel_pids)
        | susa_ur3_physical_pids
        | {("P" + r["id_text"].zfill(6)) for r in susa_ur3_composite_seals.values()}
        | set(DILMUN_PHYSICAL_PIDS)
    )
    atf_blocks: dict[str, list[str]] = collections.defaultdict(list)
    cur_p = None
    with atf_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("&P"):
                cur_p = line[1:8]
                if cur_p in needed_atf_pids:
                    atf_blocks[cur_p].append(line.rstrip("\r\n"))
            elif cur_p in needed_atf_pids:
                atf_blocks[cur_p].append(line.rstrip("\r\n"))

    # Build register records
    records: list[dict[str, Any]] = []
    local_atf_excerpts: list[dict[str, Any]] = []
    meluhha_csv_rows: list[dict[str, Any]] = []

    def src_hash_map(*keys: str) -> dict[str, str]:
        return {source_hashes[k]["logical_path"]: source_hashes[k]["sha256"] for k in keys}

    # --- COHORT 1, CLASS 1: Explicit Meluhha mentions (CDLI + ORACC) ---
    for pid in sorted(cohort1_mel_pids):
        row = cat_rows.get(pid, {})
        oracc_info = oracc_mel_all.get(pid)
        oracc_cat = oracc_info["cat"] if oracc_info else {}
        atf_lines = atf_blocks.get(pid, [])

        prov = row.get("provenience") or oracc_cat.get("provenience") or ""
        period = row.get("period") or oracc_cat.get("period") or ""
        pub = row.get("primary_publication") or oracc_cat.get("primary_publication") or ""
        otype = row.get("object_type") or oracc_cat.get("object_type") or "tablet"
        lang = row.get("language") or oracc_cat.get("language") or "Sumerian"
        mno = row.get("museum_no") or oracc_cat.get("museum_no") or ""
        exc_no = row.get("excavation_no") or oracc_cat.get("excavation_no") or ""
        seal_id = row.get("seal_id", "").strip()
        is_comp = "composite" in (pub + " " + otype).lower()

        genre = row.get("genre", "") or oracc_cat.get("genre", "")
        extracted = extract_atf_fields(
            atf_lines,
            oracc_info,
            is_administrative=("Administrative" in genre or genre == ""),
        )
        has_atf = bool(atf_lines)
        has_oracc = oracc_info is not None

        if has_atf and has_oracc:
            t_status = "cdli_and_oracc_held_local"
            h_keys = ["cdli_cat", "cdli_atf", oracc_info["oracc_corpus"]]
        elif has_atf:
            t_status = "cdli_atf_held_local"
            h_keys = ["cdli_cat", "cdli_atf"]
        elif has_oracc:
            t_status = "oracc_json_held_local"
            h_keys = ["cdli_cat", oracc_info["oracc_corpus"]] if row else [oracc_info["oracc_corpus"]]
        else:
            t_status = "catalogue_metadata_only"
            h_keys = ["cdli_cat"]

        assoc_seals: list[str] = []
        if seal_id:
            assoc_seals.append(f"CDLI {seal_id}")
        if extracted["seal_lines"]:
            assoc_seals.append("seal_legend: " + " / ".join(extracted["seal_lines"][:5]))

        exc_locus_parts = []
        if prov and not prov.lower().startswith("uncertain"):
            exc_locus_parts.append(prov)
        if exc_no:
            exc_locus_parts.append(f"excavation_no={exc_no}")
        if row.get("findspot_square"):
            exc_locus_parts.append(f"square={row['findspot_square']}")
        if row.get("stratigraphic_level"):
            exc_locus_parts.append(f"stratum={row['stratigraphic_level']}")
        exc_locus = "; ".join(exc_locus_parts) if exc_locus_parts else "unprovenanced or uncertain in CDLI"

        src_dep = (
            f"dependent_composite_edition (CDLI {pid}; do not count as an additional physical carrier)"
            if is_comp
            else f"independent_physical_carrier (CDLI {pid}" + (f"; ORACC {oracc_info['oracc_corpus']}" if has_oracc else "") + ")"
        )

        rec = {
            "record_id": f"ECR-MEL-{pid}",
            "cohort": "cohort_1_contemporary",
            "region": normalize_region(prov),
            "carrier": "composite text" if is_comp else otype,
            "is_composite": is_comp,
            "museum_accession": mno if mno and mno not in ("—", "---") else None,
            "cdli_or_bdtn_id": pid,
            "excavated_locus": exc_locus,
            "date_period": period,
            "script_and_language": f"Cuneiform / {lang}",
            "primary_edition": pub or "unpublished or unassigned in CDLI",
            "edited_transliteration_status": t_status,
            "goods_and_units": extracted["goods_and_units"],
            "personal_names": extracted["personal_names"],
            "titles_and_offices": extracted["titles_and_offices"],
            "associated_seals": assoc_seals,
            "indus_contact_evidence_class": "explicit_meluhha_mention",
            "source_dependence": src_dep,
            "source_sha256": src_hash_map(*h_keys),
        }
        records.append(rec)

        meluhha_csv_rows.append({
            "record_id": rec["record_id"],
            "cdli_or_bdtn_id": pid,
            "is_composite": str(is_comp),
            "date_period": period,
            "region": rec["region"],
            "genre": row.get("genre", "") or oracc_cat.get("genre", ""),
            "primary_edition": rec["primary_edition"],
            "museum_accession": rec["museum_accession"] or "",
            "goods_and_units": "; ".join(rec["goods_and_units"]),
            "titles_and_offices": "; ".join(rec["titles_and_offices"]),
            "personal_names": "; ".join(rec["personal_names"]),
            "settlements_and_places": "; ".join(extracted["settlements_and_places"]),
            "associated_seals": "; ".join(rec["associated_seals"]),
            "edited_transliteration_status": t_status,
        })

        local_atf_excerpts.append({
            "record_id": rec["record_id"],
            "cdli_id": pid,
            "meluhha_lines": atf_mel_lines.get(pid, []),
            "seal_lines": extracted["seal_lines"],
            "oracc_text_excerpt": (oracc_info["text_joined"][:300] if oracc_info else ""),
        })

    # Add Shu-ilishu cylinder seal (Louvre AO 22310 / CDLI P525331 / S014339)
    p525331 = cat_rows.get("P525331", {})
    shu_rec = {
        "record_id": "ECR-MEL-P525331",
        "cohort": "cohort_1_contemporary",
        "region": "Mesopotamia (unprovenanced; Louvre stylistic attribution: Babylonia)",
        "carrier": "seal (cylinder)",
        "is_composite": False,
        "museum_accession": "Louvre AO 22310",
        "cdli_or_bdtn_id": "P525331",
        "excavated_locus": "unprovenanced; collection history via de Clercq; Louvre lists 'Babylonie = Sumer' by style, not documented excavation",
        "date_period": "Louvre catalogue: 2340-2200 BCE (Akkadian); CDLI P525331: Ur III (ca. 2100-2000 BC); Possehl 2006 retains late Akkadian or possible Ur III stylistic alternatives",
        "script_and_language": "Cuneiform / Akkadian (with Sumerian title logogram eme-bal; CDLI lists Sumerian)",
        "primary_edition": "CDLI seals 014339 (physical); Louvre ark:/53355/cl010147038; Possehl 2006, Expedition 48(1): 42-43",
        "edited_transliteration_status": "published_reading_in_secondary_capture_local",
        "goods_and_units": [],
        "personal_names": ["Shu-ilishu (su-i-li-su)"],
        "titles_and_offices": ["eme-bal me-luh-ha (interpreter of Meluhha)"],
        "associated_seals": [
            "CDLI S014339 (physical cylinder seal Louvre AO 22310)",
            "seal_legend: su-i-li-su / eme-bal me-luh-ha (per Louvre and Possehl 2006)",
        ],
        "indus_contact_evidence_class": "explicit_meluhha_mention",
        "source_dependence": "independent_physical_carrier (CDLI P525331; Louvre AO 22310; Possehl 2006 EXT-01/EXT-02; no Indus script present per external_phonetic_anchor_audit.md)",
        "source_sha256": src_hash_map("cdli_cat", "ext_sources", "ext_captures", "anchor_audit"),
    }
    records.append(shu_rec)
    meluhha_csv_rows.append({
        "record_id": shu_rec["record_id"],
        "cdli_or_bdtn_id": "P525331",
        "is_composite": "False",
        "date_period": shu_rec["date_period"],
        "region": shu_rec["region"],
        "genre": p525331.get("genre", "Administrative"),
        "primary_edition": shu_rec["primary_edition"],
        "museum_accession": shu_rec["museum_accession"],
        "goods_and_units": "",
        "titles_and_offices": "; ".join(shu_rec["titles_and_offices"]),
        "personal_names": "; ".join(shu_rec["personal_names"]),
        "settlements_and_places": "me-luh-ha (Meluhha)",
        "associated_seals": "; ".join(shu_rec["associated_seals"]),
        "edited_transliteration_status": shu_rec["edited_transliteration_status"],
    })

    # --- COHORT 1, CLASS 2: Ur III Susa sealed administrative transactions ---
    susa_composite_count = len(susa_ur3_composite_seals)
    for pid in sorted(susa_ur3_physical_pids):
        row = cat_rows[pid]
        atf_lines = atf_blocks.get(pid, [])
        seal_ids = [s.strip() for s in row.get("seal_id", "").split(",") if s.strip()]
        comp_refs = []
        extra_seal_lines: list[str] = []
        for sid in seal_ids:
            if sid in susa_ur3_composite_seals:
                crow = susa_ur3_composite_seals[sid]
                cpid = "P" + crow["id_text"].zfill(6)
                comp_refs.append(f"{sid} -> composite {cpid} ({crow.get('primary_publication', '')})")
                # Pull composite seal lines if needed
                for cl in atf_blocks.get(cpid, []):
                    if re.match(r"^\d+['.]*\s+", cl):
                        extra_seal_lines.append(re.sub(r"^\d+['.]*\s+", "", cl).strip())

        extracted = extract_atf_fields(atf_lines, None, extra_seal_lines=None)
        assoc_seals = []
        for sid in seal_ids:
            if sid in susa_ur3_composite_seals:
                cpid = "P" + susa_ur3_composite_seals[sid]["id_text"].zfill(6)
                assoc_seals.append(f"CDLI {sid} (linked composite {cpid})")
            else:
                assoc_seals.append(f"CDLI {sid}")
        if extracted["seal_lines"]:
            assoc_seals.append("seal_legend: " + " / ".join(extracted["seal_lines"][:8]))

        is_bdtns_157897 = pid == "P332451"
        cdli_bdtn = "P332451; BDTNS 157897" if is_bdtns_157897 else pid
        h_keys = ["cdli_cat", "cdli_atf", "ext_sources", "ext_captures"] if is_bdtns_157897 else (["cdli_cat", "cdli_atf"] if atf_lines else ["cdli_cat"])
        t_status = (
            "bdtns_and_cdli_atf_held_local"
            if is_bdtns_157897
            else ("cdli_atf_held_local" if atf_lines else "catalogue_metadata_only")
        )
        exc_no = row.get("excavation_no", "").strip()
        if is_bdtns_157897 and "TS.B 140" not in exc_no:
            exc_no = (exc_no + "; TS.B 140").strip("; ")
        exc_locus = f"Susa (mod. Shush)" + (f"; excavation_no={exc_no}" if exc_no else "")
        mno = row.get("museum_no", "").strip()
        if is_bdtns_157897 and "NMI BK 696" not in mno:
            mno = f"{mno} (BDTNS: NMI BK 696)"

        dep_note = f"independent_physical_carrier (CDLI {pid}"
        if is_bdtns_157897:
            dep_note += "; BDTNS 157897; De Graef 2005 MDP 54 p.150 no.29"
        if comp_refs:
            dep_note += "; linked dependent CDLI composite seals: " + ", ".join(comp_refs)
        dep_note += ")"

        rec = {
            "record_id": f"ECR-SUS-{pid}",
            "cohort": "cohort_1_contemporary",
            "region": "Iran (Susa)",
            "carrier": row.get("object_type", "tablet") or "tablet",
            "is_composite": False,
            "museum_accession": mno if mno and mno not in ("—", "---") else None,
            "cdli_or_bdtn_id": cdli_bdtn,
            "excavated_locus": exc_locus,
            "date_period": row.get("period", "Ur III (ca. 2100-2000 BC)"),
            "script_and_language": f"Cuneiform / {row.get('language') or 'Sumerian/Akkadian'}",
            "primary_edition": row.get("primary_publication") or "unpublished unassigned in CDLI",
            "edited_transliteration_status": t_status,
            "goods_and_units": extracted["goods_and_units"],
            "personal_names": extracted["personal_names"],
            "titles_and_offices": extracted["titles_and_offices"],
            "associated_seals": assoc_seals,
            "indus_contact_evidence_class": "susa_sealed_transaction",
            "source_dependence": dep_note,
            "source_sha256": src_hash_map(*h_keys),
        }
        records.append(rec)
        if atf_lines:
            local_atf_excerpts.append({
                "record_id": rec["record_id"],
                "cdli_id": pid,
                "seal_lines": extracted["seal_lines"],
                "atf_line_count": len(atf_lines),
            })

    # --- COHORT 1, CLASS 3: West Asian, Gulf, and unprovenanced Indus-style and Gulf Type seals ---
    joins_path = ROOT / SOURCE_PATHS["round_joins"]
    gulf_excluded_audit: list[dict[str, str]] = []
    with joins_path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lipi_id = row.get("record_id", "").strip()
            site = row.get("site", "").strip()
            group = row.get("group", "").strip()
            lno = row.get("laursen_no", "").strip()
            lref = row.get("laursen_reference", "").strip()
            gno = row.get("gadd_no", "").strip()
            other_id = row.get("other_identifier", "").strip()
            jstatus = row.get("join_status", "").strip()
            ltype = row.get("lipi_type", "").strip()

            # Exclude South Asian circular/cylinder seals, Linear Elamite no. 28, duplicate witness 6000.1, and unprovenanced non-Laursen cylinders
            if group == "south_asia":
                gulf_excluded_audit.append({"source_id": lipi_id or f"Laursen-{lno}", "site": site, "reason": "south_asia_internal_seal_not_external_contact"})
                continue
            if "duplicate witness" in jstatus:
                gulf_excluded_audit.append({"source_id": lipi_id, "site": site, "reason": "duplicate_witness_of_3898.1_U17649_BM123208"})
                continue
            if lno == "28":
                gulf_excluded_audit.append({"source_id": "Laursen-28", "site": site, "reason": "linear_elamite_inscription_outside_indus_set"})
                continue
            if "not applicable" in jstatus:
                gulf_excluded_audit.append({"source_id": lipi_id, "site": site, "reason": "unprovenanced_cylinder_without_laursen_or_gadd_edition"})
                continue

            # Assign clean deterministic ID and region
            if lno.isdigit():
                rec_id = f"ECR-GLF-L{int(lno):02d}"
            elif "10i" in lno:
                rec_id = "ECR-GLF-KALBA-K4"
            elif "10j" in lno:
                rec_id = "ECR-GLF-RJ2"
            elif lipi_id == "3882.1":
                rec_id = "ECR-GLF-SUSA-SB2425"
            else:
                rec_id = f"ECR-GLF-{lipi_id.replace('.', '_')}"

            site_low = site.lower()
            if site_low in ("ur", "girsu"):
                reg = f"Mesopotamia ({site})"
            elif site_low in ("qala'at al-bahrain", "karzakan", "saar", "janabiyah"):
                reg = f"Gulf (Bahrain: {site})"
            elif site_low == "failaka":
                reg = "Gulf (Failaka, Kuwait)"
            elif site_low == "kalba":
                reg = "Gulf (Kalba, UAE)"
            elif "junayz" in site_low or "jinz" in site_low:
                reg = "Gulf (Ra's al-Junayz, Oman)"
            elif site_low == "susa":
                reg = "Iran (Susa)"
            elif site_low == "luristan":
                reg = "Iran (Luristan)"
            else:
                reg = "Mesopotamia or Gulf (unprovenanced)"

            if ltype == "SEAL:CY":
                carrier = "seal (cylinder)"
            elif ltype == "SEAL:S":
                carrier = "seal (copper square stamp)"
            else:
                carrier = "seal (circular Gulf Type)"

            # Parse museum accession vs excavation locus
            museum_acc = other_id if other_id else None
            if site == "Unknown":
                exc_locus = "unprovenanced (Gadd 1932 suggests Babylonia for no. 17)" if gno == "17" else "unprovenanced"
            else:
                exc_locus = f"{site}" + (f" ({other_id})" if other_id and any(k in other_id for k in ("U.", "BBM", "RJ ")) else "")

            cat_ids = []
            if lipi_id:
                cat_ids.append(f"Lipi {lipi_id}")
            if lno:
                cat_ids.append(f"Laursen 2010 no. {lno}" if lno.isdigit() else f"Laursen 2010 {lno}")
            if gno:
                cat_ids.append(f"Gadd 1932 no. {gno}")

            edition_parts = []
            if lref:
                edition_parts.append(lref)
            if lno:
                edition_parts.append(f"Laursen 2010 (AAE 21: 96-134) {'no. ' + lno if lno.isdigit() else lno}")
            if gno:
                edition_parts.append(f"Gadd 1932 (PBA 18: 191-210) no. {gno}")
            if lipi_id == "3882.1":
                edition_parts.append("Louvre ark:/53355/cl010176471 (SB 2425; AS 41; CCO S. 299)")

            h_keys = ["round_joins"]
            if gno:
                h_keys.append("gadd_pdf")
                h_keys.append("anchor_audit")

            dep_extra = ""
            if lipi_id == "3898.1":
                dep_extra = "; Lipi 6000.1 ('Dilmun' export label) deduplicated as duplicate witness of this physical seal"

            rec = {
                "record_id": rec_id,
                "cohort": "cohort_1_contemporary",
                "region": reg,
                "carrier": carrier,
                "is_composite": False,
                "museum_accession": museum_acc,
                "cdli_or_bdtn_id": "; ".join(cat_ids) if cat_ids else None,
                "excavated_locus": exc_locus,
                "date_period": "Late 3rd to early 2nd millennium BCE (Gulf Type / Ur III to Early Dilmun horizon, ca. 2100-1900 BCE)",
                "script_and_language": "Indus script (or Gulf pseudo-script) / undeciphered",
                "primary_edition": "; ".join(edition_parts),
                "edited_transliteration_status": "indus_lipi_checked_local" if lipi_id else "gadd_1932_plate_local",
                "goods_and_units": [],
                "personal_names": [],
                "titles_and_offices": [],
                "associated_seals": ["; ".join(cat_ids)] if cat_ids else [],
                "indus_contact_evidence_class": "gulf_indus_style_seal",
                "source_dependence": f"independent_physical_carrier (join_status={jstatus}{dep_extra})",
                "source_sha256": src_hash_map(*h_keys),
            }
            records.append(rec)

    # Add Gadd 1932 Ur seals nos. 1, 6, and 7 audited in external_phonetic_anchor_audit.md (not in round_joins because no. 1 is square and nos. 6-7 are cylinders)
    gadd_extra_seals = [
        {
            "record_id": "ECR-GLF-GADD01",
            "region": "Mesopotamia (Ur)",
            "carrier": "seal (square stamp, Indus-style bison with archaic cuneiform)",
            "museum_accession": "BM 120573",
            "cdli_or_bdtn_id": "Gadd 1932 no. 1; U.7683",
            "excavated_locus": "Ur (excavation_no=U.7683)",
            "date_period": "Late 3rd millennium BCE (Old Akkadian to Ur III horizon)",
            "script_and_language": "Cuneiform (archaic, uncertain reading; no Indus script sequence present)",
            "primary_edition": "Gadd 1932 (PBA 18: 191-210), reprint pp. 5-6, Plate I.1; Possehl 2008 pp. 141-142",
            "personal_names": ["Ka-lu-lim or Ka-lu-si (provisional Marchesi 2007 reading reported in Possehl 2008; unconfirmed)"],
            "associated_seals": ["BM 120573 / U.7683 / Gadd 1932 no. 1"],
            "source_dependence": "independent_physical_carrier (audited in external_phonetic_anchor_audit.md; bison iconography only, no Indus script sequence; distinguished from Gadd no. 6)",
        },
        {
            "record_id": "ECR-GLF-GADD06",
            "region": "Mesopotamia (Ur)",
            "carrier": "seal (cylinder, Indus-related iconography without cuneiform)",
            "museum_accession": "BM 122947",
            "cdli_or_bdtn_id": "Gadd 1932 no. 6; U.16220",
            "excavated_locus": "Ur (excavation_no=U.16220)",
            "date_period": "Late 3rd millennium BCE (Old Akkadian to Ur III horizon)",
            "script_and_language": "Iconographic only (palm, bull, scorpion, snakes, human figure; no cuneiform legend)",
            "primary_edition": "Gadd 1932 (PBA 18: 191-210), pp. 7-8, 16, Plate I.6",
            "personal_names": [],
            "associated_seals": ["BM 122947 / U.16220 / Gadd 1932 no. 6"],
            "source_dependence": "independent_physical_carrier (audited in external_phonetic_anchor_audit.md; explicitly distinguished from Gadd no. 1 following Frenez 2023 fn. 26 citation mismatch)",
        },
        {
            "record_id": "ECR-GLF-GADD07",
            "region": "Mesopotamia (Ur)",
            "carrier": "seal (cylinder, Indus-style unicorn/tree and fish-like sign)",
            "museum_accession": None,
            "cdli_or_bdtn_id": "Gadd 1932 no. 7; U.11958",
            "excavated_locus": "Ur (excavation_no=U.11958)",
            "date_period": "Late 3rd millennium BCE (Old Akkadian to Ur III horizon)",
            "script_and_language": "Indus-like fish sign and uncertain marks; no cuneiform sequence",
            "primary_edition": "Gadd 1932 (PBA 18: 191-210), p. 8, Plate I.7",
            "personal_names": [],
            "associated_seals": ["U.11958 / Gadd 1932 no. 7"],
            "source_dependence": "independent_physical_carrier (audited in external_phonetic_anchor_audit.md; cylinder form with Indus graphics, not bilingual)",
        },
    ]
    for g in gadd_extra_seals:
        records.append({
            "record_id": g["record_id"],
            "cohort": "cohort_1_contemporary",
            "region": g["region"],
            "carrier": g["carrier"],
            "is_composite": False,
            "museum_accession": g["museum_accession"],
            "cdli_or_bdtn_id": g["cdli_or_bdtn_id"],
            "excavated_locus": g["excavated_locus"],
            "date_period": g["date_period"],
            "script_and_language": g["script_and_language"],
            "primary_edition": g["primary_edition"],
            "edited_transliteration_status": "gadd_1932_plate_local",
            "goods_and_units": [],
            "personal_names": g["personal_names"],
            "titles_and_offices": [],
            "associated_seals": g["associated_seals"],
            "indus_contact_evidence_class": "gulf_indus_style_seal",
            "source_dependence": g["source_dependence"],
            "source_sha256": src_hash_map("gadd_pdf", "anchor_audit"),
        })

    # --- COHORT 1, CLASS 4: Early Dilmun cuneiform-inscribed royal vessels and named seal tokens ---
    for pid in DILMUN_PHYSICAL_PIDS:
        row = cat_rows[pid]
        atf_lines = atf_blocks.get(pid, [])
        extracted = extract_atf_fields(atf_lines, None, is_administrative=False)
        comp_links = DILMUN_COMPOSITE_MAP.get(pid, [])
        dep_note = f"independent_physical_carrier (CDLI {pid}"
        if comp_links:
            dep_note += "; linked dependent CDLI composite: " + ", ".join(comp_links)
        dep_note += ")"

        # Clean titles/names specific to Dilmun royal inscriptions
        titles = list(extracted["titles_and_offices"])
        joined_atf = "\n".join(atf_lines)
        if "in-za-ak" in joined_atf or "in#-[za-ak]" in joined_atf:
            if "ARAD2 {d}in-za-ak (servant of Inzak)" not in titles:
                titles.append("ARAD2 {d}in-za-ak (servant of Inzak)")
        if "e2-gal" in joined_atf or "e2#-[gal]" in joined_atf or "[e2]-gal" in joined_atf:
            titles.append("e2-gal (palace)")

        rec = {
            "record_id": f"ECR-DLM-{pid}",
            "cohort": "cohort_1_contemporary",
            "region": normalize_region(row.get("provenience", "")),
            "carrier": "inscribed stone vessel",
            "is_composite": False,
            "museum_accession": row.get("museum_no") if row.get("museum_no") and row.get("museum_no") not in ("AB —", "QB —") else None,
            "cdli_or_bdtn_id": pid,
            "excavated_locus": row.get("provenience", "Bahrain") + (f"; excavation_no={row['excavation_no']}" if row.get("excavation_no") else ""),
            "date_period": row.get("period", "Old Babylonian (ca. 1900-1600 BC)"),
            "script_and_language": f"Cuneiform / {row.get('language') or 'Akkadian'}",
            "primary_edition": row.get("primary_publication", ""),
            "edited_transliteration_status": "cdli_atf_held_local",
            "goods_and_units": extracted["goods_and_units"],
            "personal_names": extracted["personal_names"],
            "titles_and_offices": list(dict.fromkeys(titles)),
            "associated_seals": [],
            "indus_contact_evidence_class": "dilmun_named_seal",
            "source_dependence": dep_note,
            "source_sha256": src_hash_map("cdli_cat", "cdli_atf"),
        }
        records.append(rec)
        local_atf_excerpts.append({
            "record_id": rec["record_id"],
            "cdli_id": pid,
            "atf_lines": atf_lines,
        })

    # Add EXT-05: Laursen et al. 2026 Bahrain stamped tokens (abstract-tier only, embargoed PDF)
    records.append({
        "record_id": "ECR-DLM-EXT05",
        "cohort": "cohort_1_contemporary",
        "region": "Gulf (Bahrain, with comparative Failaka evidence)",
        "carrier": "stamped clay tokens (group of 3 carrying impressions of 2 seals)",
        "is_composite": False,
        "museum_accession": None,
        "cdli_or_bdtn_id": "DOI 10.1086/739820 (EXT-05)",
        "excavated_locus": "Bahrain (exact trench/accession withheld in embargoed full article)",
        "date_period": "Early second millennium BCE (Early Dilmun)",
        "script_and_language": "Cuneiform seal legends (linguistic classification not inferred beyond abstract)",
        "primary_edition": "Laursen, Al Shaikh, Reeler, Lombard & Marchesi 2026, JNES 85(1): 115-145 (institutional abstract only; PDF embargoed until 2027-04-01)",
        "edited_transliteration_status": "abstract_only_embargoed",
        "goods_and_units": [],
        "personal_names": ["Yagli-El (abstract reports owner naming Yagli-el; identity with namesake king remains a research question)"],
        "titles_and_offices": ["divine servant epithet (reported in abstract; full wording uninspected)"],
        "associated_seals": ["2 cuneiform-inscribed Dilmun seals impressed on 3 stamped tokens (plates uninspected)"],
        "indus_contact_evidence_class": "dilmun_named_seal",
        "source_dependence": "secondary_synthesis_or_abstract (EXT-05 institutional abstract only; full article embargoed until 2027-04-01; no plates or object accessions inferred)",
        "source_sha256": src_hash_map("ext_sources", "ext_captures", "anchor_audit"),
    })

    # --- COHORT 2: Later dated comparative controls (strictly separated) ---
    records.extend([
        {
            "record_id": "ECR-CTL-EXT06",
            "cohort": "cohort_2_later_control",
            "region": "Iran (Persepolis)",
            "carrier": "administrative archive (clay tablets with seal impressions)",
            "is_composite": False,
            "museum_accession": None,
            "cdli_or_bdtn_id": "OIP 92 (EXT-06)",
            "excavated_locus": "Persepolis Fortification archive, Fars, Iran",
            "date_period": "Achaemenid period, ca. 509-493 BCE (strictly post-Indus control)",
            "script_and_language": "Cuneiform / Elamite (archive also includes Aramaic and other languages)",
            "primary_edition": "Hallock 1969, Persepolis Fortification Tablets, Oriental Institute Publications 92 (EXT-06 institutional landing page)",
            "edited_transliteration_status": "indexed_excerpt_only",
            "goods_and_units": ["food commodities and administrative rations (functional control; individual tablets not transcribed in this pass)"],
            "personal_names": [],
            "titles_and_offices": ["Achaemenid administrative officials and seal-holders (functional control)"],
            "associated_seals": ["Persepolis Fortification Seal corpus (PFS; functional comparison only)"],
            "indus_contact_evidence_class": "later_control",
            "source_dependence": "secondary_synthesis_or_abstract (EXT-06 institutional page; no new PDF acquired; CC BY-NC-ND 4.0 page notice kept local)",
            "source_sha256": src_hash_map("ext_sources", "ext_captures"),
        },
        {
            "record_id": "ECR-CTL-EXT07",
            "cohort": "cohort_2_later_control",
            "region": "South India (Tamil Nadu, including Karur)",
            "carrier": "silver ring and inscribed personal seals/rings (control group)",
            "is_composite": False,
            "museum_accession": None,
            "cdli_or_bdtn_id": "EXT-07 (Karur ring; linked to 16 frozen Tamil-Brahmi seals/rings in 2026-10-24-readable-seal-controls)",
            "excavated_locus": "Karur and Early Historic Tamil Nadu sites (exact Karur ring accession not supplied in excerpt)",
            "date_period": "Early Historic, 3rd century BCE to 3rd century CE (Karur ring: 1st century BCE; strictly post-Indus control)",
            "script_and_language": "Tamil-Brahmi / Early Tamil (individual texts require language adjudication)",
            "primary_edition": "Department of Archaeology, Government of Tamil Nadu, 'Tamil - Brahmi Script' (EXT-07 indexed official excerpt); Mahadevan 2003/2020",
            "edited_transliteration_status": "indexed_excerpt_only",
            "goods_and_units": [],
            "personal_names": ["Peravatan (Karur silver ring)"],
            "titles_and_offices": [],
            "associated_seals": ["Karur silver ring (Peravatan); 16 frozen Tamil-Brahmi seals and rings in experiments/2026-10-24-readable-seal-controls/"],
            "indus_contact_evidence_class": "later_control",
            "source_dependence": "secondary_synthesis_or_abstract (EXT-07 indexed official excerpt; direct request timed out; no new corpus legend admitted)",
            "source_sha256": src_hash_map("ext_sources", "ext_captures"),
        },
        {
            "record_id": "ECR-CTL-EXT08",
            "cohort": "cohort_2_later_control",
            "region": "Red Sea and Arabia (Berenike, Myos Hormos, comparative Sumhuram)",
            "carrier": "pottery sherds and reused amphora jars (control group)",
            "is_composite": False,
            "museum_accession": None,
            "cdli_or_bdtn_id": "JdI 140 (2025) (EXT-08)",
            "excavated_locus": "Berenike and Myos Hormos, Egypt; comparative Sumhuram / Khor Rori, Oman",
            "date_period": "Roman period, 1st century CE (strictly post-Indus control)",
            "script_and_language": "Tamil-Brahmi pottery inscriptions (and other Indian Ocean scripts discussed in source)",
            "primary_edition": "Sidebotham et al. 2025, 'Indians in Roman Berenike', Jahrbuch des Deutschen Archäologischen Instituts 140 (EXT-08 indexed excerpt)",
            "edited_transliteration_status": "indexed_excerpt_only",
            "goods_and_units": ["amphora and Coarse Red Slipped Ware trade containers (indexed excerpt)"],
            "personal_names": ["nantai kiran (reported on 1st c. CE Sumhuram reused amphora sherd in indexed excerpt; full plates uninspected)"],
            "titles_and_offices": [],
            "associated_seals": [],
            "indus_contact_evidence_class": "later_control",
            "source_dependence": "secondary_synthesis_or_abstract (EXT-08 indexed publication excerpts only; direct article and viewer timed out; one claimed Omani sherd qualified in source)",
            "source_sha256": src_hash_map("ext_sources", "ext_captures"),
        },
    ])

    # Sort records deterministically by cohort, evidence class, record_id
    class_order = {
        "explicit_meluhha_mention": 1,
        "susa_sealed_transaction": 2,
        "gulf_indus_style_seal": 3,
        "dilmun_named_seal": 4,
        "later_control": 5,
    }
    records.sort(key=lambda r: (r["cohort"], class_order[r["indus_contact_evidence_class"]], r["record_id"]))

    # Compute summary statistics
    c1 = [r for r in records if r["cohort"] == "cohort_1_contemporary"]
    c2 = [r for r in records if r["cohort"] == "cohort_2_later_control"]
    by_class = collections.Counter(r["indus_contact_evidence_class"] for r in records)
    by_class_phys = collections.Counter(r["indus_contact_evidence_class"] for r in records if not r["is_composite"])
    by_class_comp = collections.Counter(r["indus_contact_evidence_class"] for r in records if r["is_composite"])

    mel_recs = [r for r in c1 if r["indus_contact_evidence_class"] == "explicit_meluhha_mention"]
    mel_by_period = collections.Counter(r["date_period"] for r in mel_recs)
    mel_by_region = collections.Counter(r["region"] for r in mel_recs)

    c1_goods = collections.Counter(g for r in c1 for g in r["goods_and_units"])
    c1_titles = collections.Counter(t for r in c1 for t in r["titles_and_offices"])
    c1_pns = collections.Counter(p for r in c1 for p in r["personal_names"])
    mel_goods = collections.Counter(g for r in mel_recs for g in r["goods_and_units"])
    mel_titles = collections.Counter(t for r in mel_recs for t in r["titles_and_offices"])
    mel_pns = collections.Counter(p for r in mel_recs for p in r["personal_names"])
    mel_places = collections.Counter(
        s for row in meluhha_csv_rows for s in row["settlements_and_places"].split("; ") if s
    )

    summary = {
        "schema_version": "1.0",
        "date": "2026-11-22",
        "counts": {
            "total_records": len(records),
            "cohort_1_contemporary_total": len(c1),
            "cohort_1_contemporary_physical": sum(1 for r in c1 if not r["is_composite"]),
            "cohort_1_contemporary_composite_editions": sum(1 for r in c1 if r["is_composite"]),
            "cohort_2_later_control_total": len(c2),
            "by_evidence_class_total": dict(by_class),
            "by_evidence_class_physical": dict(by_class_phys),
            "by_evidence_class_composite": dict(by_class_comp),
            "susa_ur3_total_in_cdli_cat": susa_ur3_all_count,
            "susa_ur3_linked_composite_seals_not_double_counted": susa_composite_count,
            "dilmun_linked_composite_editions_not_double_counted": 4,
            "cohort_1_records_with_associated_seals": sum(1 for r in c1 if r["associated_seals"]),
            "meluhha_records_with_associated_seals": sum(1 for r in mel_recs if r["associated_seals"]),
            "cohort_1_unique_goods_and_units": len(c1_goods),
            "cohort_1_unique_titles_and_offices": len(c1_titles),
            "cohort_1_unique_personal_names": len(c1_pns),
            "meluhha_unique_goods_and_units": len(mel_goods),
            "meluhha_unique_titles_and_offices": len(mel_titles),
            "meluhha_unique_personal_names": len(mel_pns),
        },
        "exclusions_audit_counts": {
            "meluhha_false_positives_excluded": sum(1 for x in excluded_mel_audit if x["reason"] == "lexical_or_onomastic_false_positive"),
            "meluhha_later_or_undated_excluded": sum(1 for x in excluded_mel_audit if x["reason"] == "later_or_undated_period_excluded_from_cohort_1"),
            "meluhha_later_by_period": dict(collections.Counter(x["period"] for x in excluded_mel_audit if x["reason"] == "later_or_undated_period_excluded_from_cohort_1")),
            "round_seal_rows_excluded_or_deduplicated": len(gulf_excluded_audit),
            "middle_babylonian_failaka_seals_excluded": len(failaka_later_seals),
        },
        "meluhha_by_period": dict(mel_by_period.most_common()),
        "meluhha_by_region": dict(mel_by_region.most_common()),
        "top_meluhha_goods_and_units": mel_goods.most_common(30),
        "top_meluhha_titles_and_offices": mel_titles.most_common(30),
        "meluhha_settlements_and_places": mel_places.most_common(20),
        "top_cohort_1_personal_names": c1_pns.most_common(30),
        "source_inputs": source_hashes,
        "local_only_outputs": {
            "logical_dir": "data/raw/2026-11-22-external-contact-register/",
            "physical_dir": str(RAW_OUT_DIR.resolve()),
        },
    }

    # Write tracked outputs
    (EXP_DIR / "register-v1.json").write_text(
        json.dumps({"schema_version": "1.0", "date": "2026-11-22", "records": records}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (EXP_DIR / "summary-v1.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    csv_fields = [
        "record_id", "cdli_or_bdtn_id", "is_composite", "date_period", "region",
        "genre", "primary_edition", "museum_accession", "goods_and_units",
        "titles_and_offices", "personal_names", "settlements_and_places",
        "associated_seals", "edited_transliteration_status",
    ]
    meluhha_csv_rows.sort(key=lambda r: r["record_id"])
    with (EXP_DIR / "meluhha-commodities-titles-v1.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        w.writerows(meluhha_csv_rows)

    # Write local-only outputs under data/raw/2026-11-22-external-contact-register/ (on D:)
    with (RAW_OUT_DIR / "atf-excerpts-local-v1.jsonl").open("w", encoding="utf-8") as f:
        for item in local_atf_excerpts:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    (RAW_OUT_DIR / "excluded-records-audit-v1.json").write_text(
        json.dumps({
            "meluhha_excluded": excluded_mel_audit,
            "round_seal_excluded_or_deduplicated": gulf_excluded_audit,
            "middle_babylonian_failaka_seals": failaka_later_seals,
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (RAW_OUT_DIR / "source-hashes-v1.json").write_text(
        json.dumps(source_hashes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Register built successfully.")
    print(json.dumps(summary["counts"], indent=2))
    print("Exclusions:", json.dumps(summary["exclusions_audit_counts"], indent=2))


if __name__ == "__main__":
    main()
