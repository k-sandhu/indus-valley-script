"""Face-level image index (question card Q-1004) for the 8,722 local Lipi image crops.

Usage (from the repository root):
    python -P experiments/2026-10-13-image-index-and-units/build_index.py --out experiments/2026-10-13-image-index-and-units/run-2026-10-13/images

Steps, following PROTOCOL.md: hash and parse every file name; add the captions read
visually for the volume/page files (volpage-readings.tsv); check every name against the
caption text that tesseract read inside the crop (crop_ocr.py output, local); place each
catalogue key on a CISI volume and page (page_index.py output); link every face of
data/normalized/lipi_observed_faces.jsonl to the files that show its object, with kind
(object photograph or impression), side relation and join rule; and count coverage
before (the data inventory's rule) and after, by object type and site.

Outputs hold file names, hashes, parsed fields, identifiers, joins and counts. No sign
sequence, image or caption text is written to the output directory.
"""
import argparse
import collections
import csv
import hashlib
import json
import pathlib
import re
import sys

from PIL import Image

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CROPS = ROOT / "data/lipi/public/seal_images"
INDEX = ROOT / "data/lipi/src/assets/data/seal_id_and_image_mapping.json"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
RAW = ROOT / "data/raw/2026-10-13-image-index-and-units"
OCR = RAW / "crop-ocr/crop-ocr.jsonl"
VOLPAGE = HERE / "volpage-readings.tsv"
OVERRIDES = HERE / "name-overrides.tsv"
ALIASES = HERE / "key-aliases.tsv"
VERIFIED = HERE / "verified-sides.tsv"
PAGE_INDEX = HERE / "run-2026-10-13/pages/key-pages.csv"
CATALOGUE = ROOT / "experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv"
INV = ROOT / "experiments/2026-10-12-data-inventory"

KEY = re.compile(r"^([A-Za-z?]{1,6})-0*(\d+)$")
SIDE_UP = "ABCDEFG"
SIDE_LO = "abcdefg"
EXTRA = {"bis": 2, "ter": 3, "quater": 4, "bi": 2}
WORDS = {"duplicate", "crop", "interior", "see", "p", "for"}
STANDARD_SCALES = {"19", "25", "33", "35", "40", "50", "66", "70", "100", "150", "200", "250", "290", "300", "400", "1000"}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def norm_key(prefix, num):
    return f"{prefix}-{int(num)}"


def new_view(prefix, num):
    return {"key": norm_key(prefix, num), "part": None, "sides": [], "impression": False, "inscription": None,
            "photo_part": None, "extra_photo": None, "scale": None, "residue": [], "notes": []}


def add_side_token(view, tok):
    """Interpret a token in side position; return True if consumed."""
    if re.fullmatch(r"[A-G]", tok):
        view["sides"].append(tok)
        return True
    if re.fullmatch(r"[a-g]", tok):
        view["sides"].append(tok)
        view["impression"] = True
        return True
    if tok == "aa":
        view["sides"].append("a")
        view["impression"] = True
        view["notes"].append("caption aa")
        return True
    m = re.fullmatch(r"([A-G])(bis|ter|quater)", tok)
    if m:
        view["sides"].append(m.group(1))
        view["extra_photo"] = EXTRA[m.group(2)]
        return True
    m = re.fullmatch(r"([A-G])(\d{2,4})", tok)
    if m:
        view["sides"].append(m.group(1))
        view["scale"] = m.group(2)
        return True
    m = re.fullmatch(r"([A-G])\s*\((\d)\)", tok)
    if m:
        view["sides"].append(m.group(1))
        view["photo_part"] = int(m.group(2))
        return True
    if not view["sides"]:
        letters = re.fullmatch(r"[A-G](?:[4+\-]?[A-G])+", tok)
        if letters:
            view["sides"].extend(ch for ch in tok if ch in SIDE_UP)
            view["notes"].append("view across sides")
            return True
        m = re.fullmatch(r"([A-G])-", tok)
        if m:
            view["sides"].append(m.group(1))
            return True
    return False


def parse_name(name):
    """Parse a Lipi crop file name into views (one per catalogue key) and residue."""
    stem = name.rsplit(".", 1)[0]
    rec = {"file": name, "name_form": "catalogue-key", "views": [], "residue": [], "volume": None, "page": None}
    m = re.match(r"^(?:z_fix_|fix_)?vol(\d)_page_(\d+)_seal_(\d+)_(no_valid_id|duplicate)$", stem)
    m2 = re.match(r"^z_fix_page_(\d+)_seal_(\d+)_no_valid_id$", stem)
    if m:
        rec.update(name_form="volume-page", volume=int(m.group(1)), page=int(m.group(2)))
        rec["notes"] = [m.group(4)] + (["z_fix"] if stem.startswith(("z_fix", "fix")) else [])
        return rec
    if m2:
        rec.update(name_form="page-only", page=int(m2.group(1)))
        rec["notes"] = ["z_fix"]
        return rec
    if stem.startswith("z-fix"):
        rec.update(name_form="unparsed-fix")
        return rec
    tokens = stem.split("_")
    view = None
    stop = False
    for i, tok in enumerate(tokens):
        if stop:
            rec["residue"].append(tok)
            continue
        if tok == "":
            continue
        k = KEY.fullmatch(tok)
        if k and (view is None or k.group(1) in PREFIXES):
            view = new_view(k.group(1), k.group(2))
            rec["views"].append(view)
            continue
        if view is None:
            rec["residue"].append(tok)
            continue
        low = tok.lower()
        if low == "for":
            stop = True
            rec["residue"].append(tok)
            continue
        if tok == "imp":
            view["impression"] = True
            continue
        if not view["sides"] and re.fullmatch(r"\d", tok):
            view["part"] = int(tok)
            continue
        if add_side_token(view, tok):
            continue
        if tok in EXTRA:
            view["extra_photo"] = EXTRA[tok]
            if tok == "bi":
                view["notes"].append("bis truncated")
            continue
        if view["sides"] and re.fullmatch(r"\d(?:-\d)?", tok):
            view["inscription"] = tok
            continue
        if re.fullmatch(r"\d{2,4}", tok):
            view["scale"] = tok
            if tok not in STANDARD_SCALES:
                view["notes"].append("unusual scale " + tok)
            continue
        parts = tok.split("-")
        if len(parts) == 2 and parts[1].lower() in WORDS | {"duplicate", "crop"}:
            if parts[0] and not add_side_token(view, parts[0]) and parts[0] in EXTRA:
                view["extra_photo"] = EXTRA[parts[0]]
            view["notes"].append(parts[1].lower())
            continue
        if view["sides"] and re.fullmatch(r"[A-G]", tok):
            view["sides"].append(tok)
            view["notes"].append("view across sides")
            continue
        if low in WORDS:
            view["notes"].append(low)
            continue
        view["residue"].append(tok)
    if not rec["views"]:
        rec["name_form"] = "unparsed"
    elif len({v["key"] for v in rec["views"]}) > 1:
        rec["name_form"] = "several-keys"
    return rec


CAPTION = re.compile(r"^\s*([A-Za-z?]{1,6})-0*(\d+)\s*(.*)$")


def parse_caption(text):
    """Parse a caption read visually, e.g. 'M-1146 (1) A', 'L-213 A 2 bis', 'Kd-8 A+E (70 %)'."""
    m = CAPTION.match(text)
    if not m:
        return None
    view = new_view(m.group(1), m.group(2))
    rest = m.group(3)
    sc = re.search(r"\((\d+)\s*%\)", rest)
    if sc:
        view["scale"] = sc.group(1)
        rest = rest[:sc.start()] + rest[sc.end():]
    pm = re.match(r"\s*\((\d)\)\s*", rest)
    if pm:
        view["part"] = int(pm.group(1))
        rest = rest[pm.end():]
    for tok in rest.split():
        if re.fullmatch(r"[A-G](?:\+[A-G])*", tok):
            view["sides"].extend(tok.split("+"))
        elif re.fullmatch(r"[a-g](?:\+[a-g])*", tok):
            view["sides"].extend(tok.split("+"))
            view["impression"] = True
        elif tok in EXTRA:
            view["extra_photo"] = EXTRA[tok]
        elif re.fullmatch(r"\(\d\)", tok):
            view["photo_part"] = int(tok[1])
        elif re.fullmatch(r"\d(?:-\d)?", tok):
            view["inscription"] = tok
        else:
            view["residue"].append(tok)
    if len(view["sides"]) > 1:
        view["notes"].append("view across sides")
    return view


def view_kind(v):
    if not v["sides"]:
        return "impression" if v["impression"] else "unknown"
    up = [s for s in v["sides"] if s in SIDE_UP]
    lo = [s for s in v["sides"] if s in SIDE_LO]
    if v["impression"] and not up:
        return "impression"
    if up and not lo and not v["impression"]:
        return "object"
    return "mixed"


def tolerant_pattern(key):
    """Regex for a key as OCR may print it: confusable digits and optional hyphen."""
    prefix, num = key.split("-")
    conf = {"0": "[0Oo]", "1": "[1lI!|i]", "2": "[2Z]", "5": "[5S]", "6": "[6b]", "8": "[8B]", "9": "[9g]"}
    p = "".join(f"[{c.upper()}{c.lower()}]" if c.isalpha() else re.escape(c) for c in prefix.replace("?", "?"))
    if prefix.startswith("?"):
        p = r"[?7]" + p[3:]
    n = "".join(conf.get(d, d) for d in num)
    return re.compile(rf"(?<![A-Za-z]){p}\s*[-–—~.]?\s*{n}(?!\d)")


OCR_KEY = re.compile(r"(?<![A-Za-z])([A-Z][a-z]{0,4}|[A-Z]{1,2}|\?)\s?-\s?(\d{1,4})(?!\d)\s*([A-Ga-g](?:\+[A-Ga-g])*)?\b")


PREFIXES = set()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    sys.path.insert(0, str(INV))
    import coverage as inv  # noqa: E402  (the inventory's grouping rules, read-only)

    names = sorted(p.name for p in CROPS.iterdir() if p.is_file())
    for n in names:
        k = re.match(r"^([A-Za-z]{1,6})-\d+", n)
        if k:
            PREFIXES.add(k.group(1))
    faces = [json.loads(l) for l in FACES.open(encoding="utf-8") if l.strip()]
    lipi_keys = collections.defaultdict(list)
    for f in faces:
        k = (f["metadata"].get("cisi") or "").strip()
        km = KEY.fullmatch(k)
        if km:
            lipi_keys[norm_key(km.group(1), km.group(2))].append(f)
    lipi_prefixes = {k.split("-")[0] for k in lipi_keys}

    # ---- file records ----
    ocr = {}
    if OCR.exists():
        for line in OCR.open(encoding="utf-8"):
            r = json.loads(line)
            ocr[r["file"]] = r.get("ocr", "")
    overrides = {}
    if OVERRIDES.exists():
        for row in csv.DictReader(OVERRIDES.open(encoding="utf-8"), delimiter="\t"):
            overrides[row["file"]] = row
    aliases = {}
    if ALIASES.exists():
        for row in csv.DictReader(ALIASES.open(encoding="utf-8"), delimiter="\t"):
            aliases[row["file_key"]] = row["lipi_key"]
    verified = {}
    if VERIFIED.exists():
        for row in csv.DictReader(VERIFIED.open(encoding="utf-8"), delimiter="\t"):
            verified[row["record_id"]] = row["side"]
    volpage = {}
    for row in csv.DictReader(VOLPAGE.open(encoding="utf-8"), delimiter="\t"):
        volpage[row["file"]] = row

    files = []
    hash_groups = collections.defaultdict(list)
    for n in names:
        b = (CROPS / n).read_bytes()
        h = sha256_bytes(b)
        hash_groups[h].append(n)
        try:
            with Image.open(CROPS / n) as im:
                size = im.size
        except OSError:
            size = None
        rec = parse_name(n)
        rec["sha256"] = h
        rec["bytes"] = len(b)
        rec["pixels"] = size
        rec["source_of_keys"] = "file name"
        if n in overrides:
            o = overrides[n]
            rec["views"] = [v for v in (parse_caption(c.strip()) for c in o["caption_read"].split(";")) if v]
            rec["source_of_keys"] = "file name corrected by visual reading"
            rec["override_note"] = o["note"]
        if rec["name_form"] in ("volume-page", "page-only", "unparsed-fix"):
            vp = volpage.get(n)
            rec["views"] = []
            if vp and vp["caption_read"].strip() and vp["caption_read"].strip() != "?":
                for cap in vp["caption_read"].split(";"):
                    v = parse_caption(cap.strip())
                    if v:
                        rec["views"].append(v)
                rec["source_of_keys"] = "caption read visually"
            rec["volpage_note"] = vp["note"] if vp else "not read"
        # key normalization: recorded aliases, then upper-case I written for lower-case l
        for v in rec["views"]:
            v["prefix_corrected"] = False
            v["alias_of"] = None
            if v["key"] in aliases:
                v["alias_of"] = v["key"]
                v["key"] = aliases[v["key"]]
                continue
            if v["key"] not in lipi_keys:
                p, num = v["key"].split("-")
                alt = p.replace("I", "l")
                if alt != p and f"{alt}-{num}" in lipi_keys:
                    v["key"] = f"{alt}-{num}"
                    v["prefix_corrected"] = True
        files.append(rec)

    # ---- OCR check of every catalogue-key name ----
    ocr_counts = collections.Counter()
    for rec in files:
        text = ocr.get(rec["file"], "")
        rec["ocr_check"] = None
        rec["ocr_other_keys"] = []
        if not rec["views"]:
            continue
        own = {v.get("alias_of") or v["key"] for v in rec["views"]}
        found = [k for k in own if tolerant_pattern(k).search(text)]
        others = []
        for pm, nm, side in OCR_KEY.findall(text):
            k = norm_key(pm, nm)
            if k not in own and (k in lipi_keys or pm in lipi_prefixes):
                others.append(k + (" " + side if side else ""))
        rec["ocr_other_keys"] = sorted(set(others))
        if len(found) == len(own):
            status = "all keys found"
        elif found:
            status = "some keys found"
        elif others:
            status = "other key found"
        elif text.strip():
            status = "no key read"
        else:
            status = "no text"
        rec["ocr_check"] = status
        ocr_counts[(rec["source_of_keys"], status)] += 1

    # ---- volume and page of each key ----
    vol_of = {}
    for row in csv.DictReader(CATALOGUE.open(encoding="utf-8")):
        ed = row["edition"]
        vol = 1 if ed.startswith("CISI1") else 2 if ed.startswith("CISI2") else None
        for pfx in {row["prefix"], row["matching_prefix"]}:
            vol_of.setdefault(pfx, []).append((int(row["first"]), int(row["last"]), vol))
    key_pages = {}
    if PAGE_INDEX.exists():
        for row in csv.DictReader(PAGE_INDEX.open(encoding="utf-8")):
            key_pages[row["key"]] = row

    def volume_page(key, rec):
        if rec["name_form"] == "volume-page":
            return rec["volume"], rec["page"], "file name"
        if key in key_pages:
            kp = key_pages[key]
            return int(kp["volume"]), int(kp["pdf_page"]), kp["basis"]
        p, num = key.split("-")
        for lo, hi, vol in vol_of.get(p, []):
            if lo <= int(num) <= hi and vol:
                return vol, None, "catalogue range (volume only)"
        return None, None, None

    # ---- links from files to keys ----
    key_files = collections.defaultdict(list)
    for rec in files:
        for v in rec["views"]:
            key_files[v["key"]].append((rec, v))

    # side letters per key from file names (for the ordinal rule)
    key_sides = {}
    for key, lst in key_files.items():
        letters = sorted({s.upper() for rec, v in lst for s in v["sides"]})
        key_sides[key] = letters

    fam_faces = collections.OrderedDict()
    for f in faces:
        fam_faces.setdefault(f["object_family_id"], []).append(f)

    links = []
    face_status = {}
    for fam, flist in fam_faces.items():
        nface = len(flist)
        for f in flist:
            raw = (f["metadata"].get("cisi") or "").strip()
            km = KEY.fullmatch(raw)
            key = norm_key(km.group(1), km.group(2)) if km else None
            ordinal = int(f["record_id"].split(".")[-1])
            letters = key_sides.get(key, [])
            hint = letters[ordinal - 1] if nface > 1 and ordinal - 1 < len(letters) else ""
            if nface == 1:
                presumed, rule = "A", "single-face"
            elif f["record_id"] in verified:
                presumed, rule = verified[f["record_id"]], "verified-by-viewing"
            else:
                # Amendment 2: the ordinal rule failed the targeted check; sides stay unassigned
                presumed, rule = None, "several-faces-unassigned"
            face_status[f["record_id"]] = {"key": key, "presumed_side": presumed, "rule": rule, "n_faces": nface}
            if not key:
                continue
            for rec, v in key_files.get(key, []):
                kind = view_kind(v)
                sides_up = {s.upper() for s in v["sides"]}
                if rule == "several-faces-unassigned":
                    rel = "side-unassigned"
                elif not sides_up or presumed is None:
                    rel = "side-unknown"
                elif sides_up == {presumed}:
                    rel = "face-side"
                elif presumed in sides_up:
                    rel = "multi-side"
                else:
                    rel = "other-side"
                vol, page, basis = volume_page(key, rec)
                flags = []
                if v.get("prefix_corrected"):
                    flags.append("prefix_corrected")
                if v.get("alias_of"):
                    flags.append("alias:" + v["alias_of"])
                if v["residue"] or rec["residue"]:
                    flags.append("residue")
                if rec["name_form"] == "several-keys":
                    flags.append("several-keys")
                if rec["source_of_keys"] != "file name":
                    flags.append(rec["source_of_keys"].replace(" ", "-"))
                links.append({
                    "record_id": f["record_id"], "object_family_id": fam, "cisi": raw, "key": key,
                    "file": rec["file"], "sha256": rec["sha256"], "kind": kind,
                    "sides": "".join(v["sides"]), "part": v["part"] or "", "inscription": v["inscription"] or "",
                    "photo_part": v["photo_part"] or "", "extra_photo": v["extra_photo"] or "", "scale": v["scale"] or "",
                    "presumed_side": presumed or "", "side_rule": rule, "relation": rel, "ordinal_hint": hint,
                    "cisi_volume": vol or "", "cisi_pdf_page": page or "", "page_basis": basis or "",
                    "ocr_check": rec["ocr_check"] or "", "flags": ";".join(flags),
                })

    # ---- coverage before (inventory rule) and after ----
    image_index = json.loads(INDEX.read_text(encoding="utf-8"))
    present = set(names)
    indexed = {k for k, fl in image_index.items() if any(x in present for x in fl)}
    indexed_files = {x for fl in image_index.values() for x in fl if x in present}
    by_face = collections.defaultdict(list)
    for l in links:
        by_face[l["record_id"]].append(l)

    def face_flags(f):
        raw = (f["metadata"].get("cisi") or "").strip()
        ls = by_face.get(f["record_id"], [])
        return {
            "before": raw in indexed,
            "any": bool(ls),
            "face_side_object": any(l["relation"] == "face-side" and l["kind"] == "object" for l in ls),
            "face_side_impression": any(l["relation"] in ("face-side",) and l["kind"] == "impression" for l in ls),
            "face_side_any": any(l["relation"] in ("face-side", "multi-side") for l in ls),
            "index_only_face_side_object": any(l["relation"] == "face-side" and l["kind"] == "object" and l["file"] in indexed_files for l in ls),
            "index_only_face_side_impression": any(l["relation"] == "face-side" and l["kind"] == "impression" and l["file"] in indexed_files for l in ls),
        }

    MEASURES = ["before", "index_only_face_side_object", "index_only_face_side_impression", "any", "face_side_any",
                "face_side_object", "face_side_impression"]
    ff = {f["record_id"]: face_flags(f) for f in faces}
    obj = {}
    for fam, flist in fam_faces.items():
        obj[fam] = {k: any(ff[f["record_id"]][k] for f in flist) for k in MEASURES}
        obj[fam]["all_faces_face_side"] = all(ff[f["record_id"]]["face_side_any"] for f in flist)
        key0 = face_status[flist[0]["record_id"]]["key"]
        views0 = {(s.upper(), v["inscription"] or "", v["part"] or "") for rec, v in key_files.get(key0, []) for s in (v["sides"] or [])} if key0 else set()
        obj[fam]["several_faces"] = len(flist) > 1
        obj[fam]["several_faces_enough_views"] = len(flist) > 1 and len(views0) >= len(flist)
    def group_of(f):
        return inv.type_group(f["metadata"].get("type"))
    def site_of(f):
        return inv.site_group(inv.norm(f["metadata"].get("site")))
    cov_rows = []
    measures = MEASURES
    for unit in ("object", "face"):
        for dim, fn in (("all", lambda f: "all"), ("type", group_of), ("site", site_of)):
            groups = collections.defaultdict(list)
            if unit == "object":
                for fam, flist in fam_faces.items():
                    groups[fn(flist[0])].append(obj[fam])
            else:
                for f in faces:
                    groups[fn(f)].append(ff[f["record_id"]])
            for g, vals in sorted(groups.items()):
                row = {"unit": unit, "dimension": dim, "group": g, "n": len(vals)}
                for m in measures + (["all_faces_face_side", "several_faces", "several_faces_enough_views"] if unit == "object" else []):
                    c = sum(1 for v in vals if v[m])
                    row[m] = c
                    row[m + "_pct"] = round(100 * c / len(vals), 1)
                cov_rows.append(row)

    # ---- faces without image ----
    no_image = []
    for f in faces:
        if not ff[f["record_id"]]["any"]:
            st = face_status[f["record_id"]]
            reason = "no CISI key" if not st["key"] else "no file for the key"
            no_image.append({"record_id": f["record_id"], "object_family_id": f["object_family_id"],
                             "cisi": (f["metadata"].get("cisi") or "").strip(), "site": f["metadata"].get("site"),
                             "type_group": group_of(f), "reason": reason})

    # ---- outputs ----
    out.mkdir(parents=True)
    with (out / "image-files.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["file", "sha256", "hash_group_size", "bytes", "width", "height", "name_form", "source_of_keys", "keys",
                "views", "residue", "volume_in_name", "page_in_name", "ocr_check", "ocr_other_keys", "linked_faces", "note"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        nlinks = collections.Counter(l["file"] for l in links)
        for rec in files:
            w.writerow({
                "file": rec["file"], "sha256": rec["sha256"], "hash_group_size": len(hash_groups[rec["sha256"]]),
                "bytes": rec["bytes"], "width": rec["pixels"][0] if rec["pixels"] else "", "height": rec["pixels"][1] if rec["pixels"] else "",
                "name_form": rec["name_form"], "source_of_keys": rec["source_of_keys"],
                "keys": ";".join(v["key"] for v in rec["views"]),
                "views": ";".join(f"{v['key']}|{''.join(v['sides'])}|{view_kind(v)}" + (f"|part{v['part']}" if v['part'] else "")
                                  + (f"|x{v['extra_photo']}" if v['extra_photo'] else "") + (f"|{v['scale']}%" if v['scale'] else "") for v in rec["views"]),
                "residue": ";".join(rec["residue"] + [r for v in rec["views"] for r in v["residue"]]),
                "volume_in_name": rec["volume"] or "", "page_in_name": rec["page"] or "",
                "ocr_check": rec["ocr_check"] or "", "ocr_other_keys": ";".join(rec["ocr_other_keys"]),
                "linked_faces": nlinks.get(rec["file"], 0),
                "note": rec.get("volpage_note", rec.get("override_note", "")),
            })
    lcols = list(links[0].keys())
    with (out / "face-image-links.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols)
        w.writeheader()
        w.writerows(links)
    with (out / "faces-without-image.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(no_image[0].keys()))
        w.writeheader()
        w.writerows(no_image)
    ccols = list(cov_rows[0].keys())
    for r in cov_rows:
        for c in ccols:
            r.setdefault(c, "")
    ccols = sorted({c for r in cov_rows for c in r}, key=lambda c: (c not in ("unit", "dimension", "group", "n"), c))
    with (out / "coverage.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols)
        w.writeheader()
        w.writerows(cov_rows)

    files_with_link = {l["file"] for l in links}
    keys_without_lipi = sorted({v["key"] for rec in files for v in rec["views"] if v["key"] not in lipi_keys})
    summary = {
        "files": len(files),
        "hash_groups": len(hash_groups),
        "files_in_groups_of_two_or_more": sum(len(v) for v in hash_groups.values() if len(v) > 1),
        "groups_of_two_or_more": sum(1 for v in hash_groups.values() if len(v) > 1),
        "name_forms": dict(collections.Counter(r["name_form"] for r in files)),
        "source_of_keys": dict(collections.Counter(r["source_of_keys"] for r in files)),
        "files_with_residue_tokens": sum(1 for r in files if r["residue"] or any(v["residue"] for v in r["views"])),
        "files_with_prefix_correction": sum(1 for r in files if any(v.get("prefix_corrected") for v in r["views"])),
        "files_with_alias_key": sum(1 for r in files if any(v.get("alias_of") for v in r["views"])),
        "files_with_name_corrected_by_reading": sum(1 for r in files if r["source_of_keys"] == "file name corrected by visual reading"),
        "files_linked_to_a_face": len(files_with_link),
        "files_not_linked": len(files) - len(files_with_link),
        "keys_in_file_names_absent_from_lipi": len(keys_without_lipi),
        "keys_in_file_names_absent_from_lipi_list": keys_without_lipi,
        "files_in_lipi_index": sum(1 for r in files if r["file"] in {x for v in image_index.values() for x in v}),
        "ocr_check": {f"{a}|{b}": n for (a, b), n in sorted(ocr_counts.items())},
        "links": len(links),
        "link_kinds": dict(collections.Counter(l["kind"] for l in links)),
        "link_relations": dict(collections.Counter(l["relation"] for l in links)),
        "link_rules": dict(collections.Counter(l["side_rule"] for l in links)),
        "links_with_page": sum(1 for l in links if l["cisi_pdf_page"] != ""),
        "links_with_volume": sum(1 for l in links if l["cisi_volume"] != ""),
        "faces": len(faces),
        "faces_with_any_image": sum(1 for v in ff.values() if v["any"]),
        "faces_without_image": len(no_image),
        "faces_without_image_reasons": dict(collections.Counter(r["reason"] for r in no_image)),
        "objects": len(fam_faces),
        "objects_before": sum(1 for v in obj.values() if v["before"]),
        "objects_after_any": sum(1 for v in obj.values() if v["any"]),
        "objects_after_face_side_object_photo": sum(1 for v in obj.values() if v["face_side_object"]),
        "objects_after_face_side_impression": sum(1 for v in obj.values() if v["face_side_impression"]),
        "objects_index_only_face_side_object_photo": sum(1 for v in obj.values() if v["index_only_face_side_object"]),
        "objects_index_only_face_side_impression": sum(1 for v in obj.values() if v["index_only_face_side_impression"]),
        "objects_all_faces_have_face_side_image": sum(1 for v in obj.values() if v["all_faces_face_side"]),
        "objects_with_several_faces": sum(1 for v in obj.values() if v["several_faces"]),
        "objects_with_several_faces_any_image": sum(1 for v in obj.values() if v["several_faces"] and v["any"]),
        "objects_with_several_faces_views_at_least_faces": sum(1 for v in obj.values() if v["several_faces_enough_views"]),
        "faces_verified_side": sum(1 for st in face_status.values() if st["rule"] == "verified-by-viewing"),
        "faces_side_unassigned_with_image": sum(1 for f in faces if face_status[f["record_id"]]["rule"] == "several-faces-unassigned" and ff[f["record_id"]]["any"]),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    (out / "input-hashes.json").write_text(json.dumps({
        "lipi_faces": hashlib.sha256(FACES.read_bytes()).hexdigest(),
        "lipi_image_index": hashlib.sha256(INDEX.read_bytes()).hexdigest(),
        "crop_ocr": hashlib.sha256(OCR.read_bytes()).hexdigest() if OCR.exists() else None,
        "volpage_readings": hashlib.sha256(VOLPAGE.read_bytes()).hexdigest(),
        "verified_sides": hashlib.sha256(VERIFIED.read_bytes()).hexdigest() if VERIFIED.exists() else None,
        "key_aliases": hashlib.sha256(ALIASES.read_bytes()).hexdigest() if ALIASES.exists() else None,
        "name_overrides": hashlib.sha256(OVERRIDES.read_bytes()).hexdigest() if OVERRIDES.exists() else None,
        "key_pages": hashlib.sha256(PAGE_INDEX.read_bytes()).hexdigest() if PAGE_INDEX.exists() else None,
        "image_directory_files": len(names)}, indent=1), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("files", "links", "faces_with_any_image", "objects_before", "objects_after_any")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
