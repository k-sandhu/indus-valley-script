"""Check every dating-v1/towns/*.json file against the conventions in METHOD.md.

Prints one line per problem and a summary per town; exits 1 if any hard error.
Checks: required keys, BCE ranges older-first, half-life conversion
(age_bp_5568 = round(printed / 1.03) when the printed half-life is 5730),
every cited source id present in the town's sources array, local paths exist
and their SHA-256 matches when given.
"""
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOWNS = HERE.parent / "towns"

TOP = {"town", "compiled_utc", "parts", "first_occupation", "sources", "notes"}
PART = {"part", "layout_phase", "what_was_built", "locator", "excavator_range_bce", "excavator_basis",
        "radiocarbon", "bayesian_start", "syntheses", "conflicts"}
PART_OPT = {"note"}
RC = {"lab_no", "material", "context", "phase", "age_bp_printed", "sigma_printed", "half_life_printed",
      "age_bp_5568", "sigma_5568", "calibrated_published", "curve", "source", "page"}
RC_OPT = {"note", "cited_via"}


def rng_ok(v):
    if v is None:
        return True
    if not (isinstance(v, list) and len(v) == 2):
        return False
    a, b = v
    if a is None or b is None:
        return True
    return isinstance(a, (int, float)) and isinstance(b, (int, float)) and a >= b


def logged_hashes():
    """SHA-256 values recorded in every acquisitions.jsonl under the dating raw directory."""
    out = set()
    for f in (ROOT / "data/raw/2026-10-21-town-axes/dating").rglob("acquisitions.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                out.add(json.loads(line).get("sha256"))
            except json.JSONDecodeError:
                pass
    return out


LOGGED = logged_hashes()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(path):
    errs, warns = [], []
    d = json.loads(path.read_text(encoding="utf-8"))
    if set(d) != TOP:
        errs.append(f"top keys {sorted(set(d) ^ TOP)}")
    if d.get("town") != path.stem:
        errs.append("town slug differs from filename")
    ids = {s.get("id") for s in d.get("sources", [])}
    cited = set()
    nrc = 0
    for i, p in enumerate(d.get("parts", [])):
        extra = set(p) - PART - PART_OPT
        missing = PART - set(p)
        if extra or missing:
            errs.append(f"part {i} keys extra={sorted(extra)} missing={sorted(missing)}")
        if not rng_ok(p.get("excavator_range_bce")):
            errs.append(f"part {i} excavator_range_bce {p.get('excavator_range_bce')}")
        for r in p.get("radiocarbon") or []:
            nrc += 1
            extra = set(r) - RC - RC_OPT
            missing = RC - set(r)
            if extra or missing:
                errs.append(f"rc {r.get('lab_no')} keys extra={sorted(extra)} missing={sorted(missing)}")
            cited.add(r.get("source"))
            if r.get("cited_via"):
                cited.add(r["cited_via"])
            hl, a, s = r.get("half_life_printed"), r.get("age_bp_printed"), r.get("sigma_printed")
            a2, s2 = r.get("age_bp_5568"), r.get("sigma_5568")
            if hl == 5730 and a is not None:
                if a2 != round(a / 1.03):
                    errs.append(f"rc {r.get('lab_no')} age_bp_5568 {a2} != round({a}/1.03)={round(a / 1.03)}")
                if s is not None and s2 != round(s / 1.03):
                    errs.append(f"rc {r.get('lab_no')} sigma_5568 {s2} != round({s}/1.03)={round(s / 1.03)}")
            if hl == 5568 and a is not None and (a2 != a or s2 != s):
                errs.append(f"rc {r.get('lab_no')} 5568 values not copied")
            if hl not in (5568, 5730, None):
                errs.append(f"rc {r.get('lab_no')} half_life_printed {hl}")
        bs = p.get("bayesian_start")
        for b in (bs if isinstance(bs, list) else [bs] if bs else []):
            cited.add(b.get("source"))
            if not rng_ok(b.get("hpd95_bce")):
                errs.append(f"part {i} bayesian hpd95_bce {b.get('hpd95_bce')}")
        for s in p.get("syntheses") or []:
            cited.add(s.get("source"))
            if not rng_ok(s.get("range_bce")):
                errs.append(f"part {i} synthesis range_bce {s.get('range_bce')}")
    fo = d.get("first_occupation") or {}
    if not rng_ok(fo.get("range_bce")):
        errs.append(f"first_occupation range_bce {fo.get('range_bce')}")
    cited.discard(None)
    for c in sorted(cited - ids):
        errs.append(f"cited source {c!r} not in sources")
    for c in sorted(ids - cited):
        warns.append(f"source {c!r} listed but not cited in a structured field")
    for s in d.get("sources", []):
        loc = s.get("url_or_path") or ""
        hashes = []
        for tok in [m.rstrip(".") for m in re.findall(r"(?<![\w/.:-])(?:data|research|experiments)/[^\s;()|,]+", loc)]:
            p = ROOT / tok
            if not p.exists():
                warns.append(f"source {s.get('id')} path not found: {tok}")
            elif p.is_file():
                hashes.append(sha(p))
        # A source may list several local files (scan, OCR text, page images); its
        # sha256 must belong to one of them.
        if s.get("sha256") and hashes and s["sha256"] not in hashes and s["sha256"] not in LOGGED:
            errs.append(f"source {s.get('id')} sha256 matches none of its local files")
    return d, errs, warns, nrc


def main():
    bad = False
    for path in sorted(TOWNS.glob("*.json")):
        try:
            d, errs, warns, nrc = check(path)
        except Exception as e:  # noqa: BLE001
            print(f"{path.name}: UNREADABLE {e!r}")
            bad = True
            continue
        print(f"{path.stem}: parts={len(d.get('parts', []))} radiocarbon={nrc} sources={len(d.get('sources', []))} errors={len(errs)} warnings={len(warns)}")
        for e in errs:
            print("  ERROR", e)
        for w in warns:
            print("  warn ", w)
        bad |= bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
