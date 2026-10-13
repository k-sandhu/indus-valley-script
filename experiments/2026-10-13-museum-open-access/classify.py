"""Automatic first-pass classification of harvested museum records.

The result is a proposal; harvest/manual-review.csv holds the decisions made after
reading each record and, where open, its photograph. Rules follow PROTOCOL.md.
"""
import re

INDUS_RE = re.compile(
    r"harapp|mohenjo|moenjo|mohenjodaro|chanhu|lothal|kalibangan|dholavira|banawali|nausharo|allahdino|"
    r"rakhigarhi|indus valley|indus civili[sz]ation|indus script|\bindus\b|kot ?diji|amri\b|sutkagen",
    re.I)
LATER_RE = re.compile(r"kushan|gandhar|mughal|islamic|buddhis|sasanian|bactria|hellenistic|achaemenid|sikh|"
                      r"medieval|gupta|maurya|parthian|seleucid|indo-greek|graeco|mathura|pala\b", re.I)
SEAL_RE = re.compile(r"\bseal|sealing|tablet|impression|amulet|stamp|\btag\b|token", re.I)
POT_RE = re.compile(r"\bpot\b|potsherd|sherd|jar|vessel|bowl|ceramic|pottery", re.I)
INSCR_RE = re.compile(r"inscri|\bscript\b|\bsigns?\b|characters|pictogra|graffiti|glyph|writing", re.I)
UNINSCR_RE = re.compile(r"uninscribed|no inscription|without (an )?inscription|not inscribed", re.I)
CAST_RE = re.compile(r"\bcast of\b|\bcasts?\b(?! (copper|bronze))|plaster|replica|reproduction|facsimile|\bcopy\b|electrotype",
                     re.I)
SITE_WORDS = [("mohenjo", "Mohenjo-daro"), ("moenjo", "Mohenjo-daro"), ("harapp", "Harappa"), ("chanhu", "Chanhu-daro"),
              ("lothal", "Lothal"), ("kalibangan", "Kalibangan"), ("dholavira", "Dholavira"), ("banawali", "Banawali"),
              ("nausharo", "Nausharo"), ("allahdino", "Allahdino"), ("rakhigarhi", "Rakhigarhi"), ("susa", "Susa"),
              ("suse", "Susa"), ("tello", "Girsu"), ("girsu", "Girsu"), ("ur\b", "Ur"), ("kish", "Kish")]


def _text(rec, keys):
    parts = []
    for k in keys:
        v = rec.get(k)
        if isinstance(v, list):
            parts.extend(str(x) for x in v if x)
        elif v:
            parts.append(str(v))
    return " | ".join(parts)


def classify_record(rec):
    attr_text = _text(rec, ["culture", "period", "findspot_raw", "provenance_raw", "title", "description", "date", "tags",
                            "place", "inscription_note"])
    name_text = _text(rec, ["object_name", "title", "classification"])
    all_text = _text(rec, ["title", "object_name", "description", "inscription_note", "bibliography", "material"])
    m = INDUS_RE.search(attr_text)
    later = LATER_RE.search(_text(rec, ["culture", "period", "date"]))
    indus = bool(m) and not later
    seal_like = bool(SEAL_RE.search(name_text))
    inscribed_text = bool(INSCR_RE.search(all_text))
    if UNINSCR_RE.search(all_text):
        inscription = "uninscribed"
    elif inscribed_text:
        inscription = "inscribed"
    else:
        inscription = "not-stated"
    lname = name_text.lower()
    if "impression" in lname and "modern impression" not in lname or "sealing" in lname:
        oclass = "sealing-or-impression"
    elif "tablet" in lname:
        oclass = "tablet"
    elif re.search(r"\bseal|stamp|amulet", lname):
        oclass = "seal"
    elif POT_RE.search(lname):
        oclass = "pottery"
    else:
        oclass = "other"
    originality = "cast-or-replica" if CAST_RE.search(name_text) else "original"
    site = ""
    low = attr_text.lower()
    for w, s in SITE_WORDS:
        if re.search(w, low):
            site = s
            break
    in_scope = indus and (seal_like or (inscription == "inscribed" and oclass in ("pottery", "other")))
    reason = ""
    if not indus:
        reason = "later period" if later else "not Indus-attributed"
    elif not in_scope:
        reason = "object class cannot carry an inscription per record" if not seal_like else ""
    return {
        "indus_attributed": indus,
        "attribution_basis": m.group(0) if m else "",
        "seal_like": seal_like,
        "object_class": oclass,
        "inscription_status": inscription,
        "originality": originality,
        "site_guess": site,
        "in_scope": in_scope,
        "exclusion_reason": reason,
    }
