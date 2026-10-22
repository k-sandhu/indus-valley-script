"""Extract page text and mechanical keyword locations without displaying source prose."""
from __future__ import annotations

import argparse
import collections
import concurrent.futures as cf
import csv
import hashlib
import html
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import unicodedata
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

sys.dont_write_bytecode = True


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def word_count(text):
    return len(re.findall(r"\b\w+\b", text))


def normalized(text):
    text = unicodedata.normalize("NFKD", text).lower()
    text = re.sub(r"(?<=\w)[\-\u00ad\u2010-\u2014]\s*(?=\w)", "", text)
    return re.sub(r"[^a-z0-9]", "", text)


class Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "div", "br", "tr", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)


HELD = {
    "iar-1987-88": "b-gujarat-kutch-maharashtra/IAR1987-1988-ALT.pdf",
    "iar-1988-89": "b-gujarat-kutch-maharashtra/IAR1988-1989-ALT.pdf",
    "iar-1989-90": "b-gujarat-kutch-maharashtra/IAR1989-1990-ALT.pdf",
    "iar-1990-91": "b-gujarat-kutch-maharashtra/IAR1990-1991-ALT.pdf",
    "iar-1991-92": "b-gujarat-kutch-maharashtra/IAR1991-92.pdf",
    "iar-1999-00": "c-north-india/iar1999.pdf",
    "iar-2007-08": "c-north-india/iar2007_alt.pdf",
    "iar-2009-10": "b-gujarat-kutch-maharashtra/IAR2009-10.pdf",
    "iar-2013-14": "c-north-india/iar2013_alt.pdf",
    "nuhato-2018-held": "b-gujarat-kutch-maharashtra/NUHATO2018.pdf",
    "shikarpur-2009-held": "b-gujarat-kutch-maharashtra/SHIKARPUR2009.pdf",
    "kanmer-ch8-held": "b-gujarat-kutch-maharashtra/KANMER2012CH8.html",
    "khirsara-2017-held": "b-gujarat-kutch-maharashtra/KHIRSARA2017.html",
    "nagwada-2018-held": "b-gujarat-kutch-maharashtra/NAGWADA2018.pdf",
    "binjor2017-held": "c-north-india/binjor2017.pdf",
    "puratattva-35-held": "c-north-india/puratattva35_retry.pdf",
    "puratattva-36-held": "c-north-india/puratattva36_retry.pdf",
    "rakhigarhi-inventory-held": "c-north-india/rakhigarhi_inventory.pdf",
    "chanhu-surface2017-held": "a-pakistan-afghanistan/major-revision/chanhu-surface2017.pdf",
    "juna-khatiya-2021-held": "b-gujarat-kutch-maharashtra/JUNAKHATIYA2021.pdf",
}


def held_inventory():
    base = "data/raw/2026-10-06-evidence-census/sites-deep/"
    records = [dict(source_id=sid, local_path=base + rel, route="held",
                    kind="annual-review" if sid.startswith("iar-") else "excavation-report") for sid, rel in HELD.items()]
    records.append(dict(source_id="bisht-2015-held", local_path="data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf",
                        route="held", kind="excavation-report"))
    frame_dir = ROOT / "experiments/2026-10-02-six-hour/kanmer-physical-use"
    refs = []
    for name in ("SOURCES.md", "source-register.json", "artifact-manifest.json"):
        path = frame_dir / name
        if not path.exists():
            continue
        if name.endswith(".json"):
            def walk(value):
                if isinstance(value, dict):
                    for k, v in value.items():
                        if any(w in k.lower() for w in ("path", "file", "local", "witness")) and isinstance(v, str):
                            refs.append(v)
                        elif isinstance(v, (list, dict)):
                            walk(v)
                elif isinstance(value, list):
                    for v in value:
                        walk(v)
                elif isinstance(value, str) and re.search(r'\.(?:pdf|html?|png|jpe?g|txt|bin)$', value, re.I):
                    refs.append(value)
            walk(json.loads(path.read_text(encoding="utf-8")))
        else:
            text = path.read_text(encoding="utf-8")
            refs.extend(re.findall(r'`([^`]+\.(?:pdf|html?|png|jpe?g|txt))`', text, re.I))
            refs.extend(re.findall(r'\]\(([^)]+\.(?:pdf|html?|png|jpe?g|txt))\)', text, re.I))
    seen = set()
    for value in refs:
        if value.startswith(("https:", "http:")) or "2026-10-20-fresh-test-collection" in value:
            continue
        for path in (ROOT / value, frame_dir / value):
            path = path.resolve()
            if path.is_file() and path not in seen:
                seen.add(path)
                records.append(dict(source_id=f"kanmer-frame-{len(seen)}", local_path=path.relative_to(ROOT).as_posix(),
                                    route="held", kind="excavation-report", no_sweep=True))
                break
    canonical = json.loads((ROOT / "data/MANIFEST.json").read_text(encoding="utf-8"))
    expected, bib = {}, {}
    for item in canonical["sources"]:
        for path, digest in item.get("hashes", {}).items():
            expected[path.replace("\\", "/")] = digest
            bib[path.replace("\\", "/")] = item
        for path in item.get("local_paths", []):
            bib[path.replace("\\", "/")] = item
    for rec in records:
        path = ROOT / rec["local_path"]
        item = bib.get(rec["local_path"], {})
        rec.update(title=item.get("title", path.stem), authors_or_editors="", year_or_volume="",
                   rights_notice_observed="rights-unverified", notes="Held bibliography requires title-page confirmation.")
        archive_url = str(item.get("fetch", {}).get("url", ""))
        identifier = re.search(r'archive.org/(?:download|details)/([^/]+)', archive_url)
        if identifier:
            rec["identifier"] = identifier[1]
        if rec["source_id"].startswith("iar-"):
            year = int(rec["source_id"].split("-")[1])
            rec.update(title=f"Indian Archaeology {year}-{year+1} - A Review", year_or_volume=f"{year}-{year+1}")
        if path.exists():
            hs = FETCH.hashes(path)
            rec.update(bytes=path.stat().st_size, sha256=hs["sha256"], status="held-verified",
                       manifest_sha256=expected.get(rec["local_path"], ""))
            if rec["manifest_sha256"] and rec["manifest_sha256"] != rec["sha256"]:
                rec.update(status="failed", notes="Manifest SHA256 mismatch; retained in place.")
        else:
            rec.update(status="failed", notes="Held path missing.")
    FETCH.dump(RECORDS / "held-verification-1a.json", records)
    print(json.dumps(dict(held_sources=len(records), kanmer_frame=sum(bool(r.get("no_sweep")) for r in records),
         manifest_pins=sum(bool(r.get("manifest_sha256")) for r in records), failed=sum(r["status"] == "failed" for r in records))))


def proposal_data():
    return json.loads((RECORDS / "manifest-proposals-1a.json").read_text(encoding="utf-8"))


def append_assets(requests):
    data = proposal_data()
    existing = {e["id"] for e in data["sources"]}
    for sid, ident, role, kind in requests:
        meta = FETCH.metadata(ident)
        entry = FETCH.proposal(sid, ident, meta, role, kind) if meta else None
        if entry and entry["id"] not in existing:
            data["sources"].append(entry)
            existing.add(entry["id"])
    FETCH.dump(RECORDS / "manifest-proposals-1a.json", data)


def duplicates():
    data = proposal_data()
    entries = {e["id"]: e for e in data["sources"]}
    a, b = entries.get("iar-1996-97"), entries.get("iar-1997-98")
    if a and b and a.get("verification", {}).get("sha256") == b.get("verification", {}).get("sha256") and a.get("status") == b.get("status") == "held":
        b["duplicate_of"] = "iar-1996-97"
        ident = "indianarchaeology199798areview_830_j"
        meta = FETCH.metadata(ident)
        if meta and "iar-1997-98-archive" not in entries:
            entry = FETCH.proposal("iar-1997-98-archive", ident, meta, "pdf", "annual-review")
            if entry:
                entry["logical_source_id"] = "iar-1997-98-archive"
                data["sources"].append(entry)
    FETCH.dump(RECORDS / "manifest-proposals-1a.json", data)


def sources():
    data = proposal_data()
    groups = collections.defaultdict(list)
    for e in data["sources"]:
        groups[e["logical_source_id"]].append(e)
    inventory = {r["source_id"]: r for r in json.loads((RECORDS / "discovery-1a.json").read_text(encoding="utf-8"))["sources"]}
    held = json.loads((RECORDS / "held-verification-1a.json").read_text(encoding="utf-8"))
    held_ids = {r["source_id"] for r in held}
    rows = []
    for sid, entries in groups.items():
        if sid in held_ids:
            continue
        good = [e for e in entries if e.get("status") == "held" and not e.get("acquisition_failure")]
        primary = next((e for e in good if e["asset_role"] == "pdf"), None) or next((e for e in good if e["asset_role"] == "text"), None) or (good[0] if good else entries[0])
        inv = inventory.get(sid, {})
        authors = primary.get("authors_or_editors", "")
        if isinstance(authors, list):
            authors = "; ".join(authors)
        rec = dict(source_id=sid, title=primary["title"], authors_or_editors=authors,
            year_or_volume=inv.get("year_or_volume", primary.get("year_or_volume", "")), kind=inv.get("kind", primary["kind"]),
            route="archive.org" if primary.get("identifiers") else "asi-mirror",
            identifier=primary.get("identifiers", {}).get("archive_identifier", ""), url=primary["fetch"]["url"],
            local_path=(primary.get("local_paths") or [""])[0], file_name=primary["fetch"]["filename"],
            bytes=primary.get("actual_bytes", ""), sha256=primary.get("verification", {}).get("sha256", ""),
            archive_md5=primary["fetch"].get("archive_md5", ""), archive_sha1=primary["fetch"].get("archive_sha1", ""),
            md5_match=primary.get("md5_match", ""), sha1_match=primary.get("sha1_match", ""),
            rights_notice_observed=primary["rights"].get("licenseurl") or "rights-unverified",
            status="acquired" if good else "failed", notes="Bibliographic fields from archive metadata." if primary.get("identifiers") else "Bibliographic year from requested mirror filename.",
            assets=entries)
        if primary.get("duplicate_of"):
            rec.update(status="duplicate", notes="Byte-identical to " + primary["duplicate_of"] + "; archive replacement listed separately.")
        rows.append(rec)
    all_assets = [e for values in groups.values() for e in values]
    for rec in held:
        rec["assets"] = groups.get(rec["source_id"], [])
        alias = {"puratattva-35-held": "puratattva-35", "puratattva-36-held": "puratattva-36"}.get(rec["source_id"])
        if alias:
            rec["assets"] = [e for e in all_assets if e.get("logical_source_id") == alias and e.get("asset_role") == "ocr"]
        rows.append(rec)
    return rows


def split_ocr(path):
    if path.name.endswith("_djvu.xml"):
        pages = []
        for event, elem in ET.iterparse(path, events=("end",)):
            if elem.tag.split("}")[-1].upper() == "OBJECT":
                lines = []
                for line in elem.iter():
                    if line.tag.split("}")[-1].upper() == "LINE":
                        lines.append(" ".join("".join(w.itertext()) for w in line if w.tag.split("}")[-1].upper() == "WORD"))
                pages.append("\n".join(lines))
                elem.clear()
        return pages
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = re.split(r'(?=<div\b[^>]*class=[\'"][^\'"]*ocr_page)', text)
    pages = []
    for chunk in chunks:
        if not re.match(r'<div\b[^>]*class=[\'"][^\'"]*ocr_page', chunk):
            continue
        parser = Stripper()
        parser.feed(chunk)
        pages.append("".join(parser.parts))
    return pages


def printed_map(pages):
    result = {}
    for i, text in enumerate(pages, 1):
        lines = [s.strip() for s in text.splitlines() if s.strip()]
        options = []
        for s in lines[:3] + lines[-3:]:
            if re.fullmatch(r"[\[\](\-\s]*([0-9]{1,4}|[ivxlcdmIVXLCDM]{1,12})[\[\])\-\s]*", s):
                options.append(re.sub(r"[^0-9ivxlcdmIVXLCDM]", "", s))
        if options:
            result[str(i)] = options[-1]
    return result


def ocr_pages(path, sid, low, pages, state, target):
    renderer = str(pathlib.Path(shutil.which("pdfinfo")).with_name("pdftoppm.exe"))
    progress_path = RAW / "ocr-cache" / (sid + ".json")
    progress = json.loads(progress_path.read_text(encoding="utf-8")) if progress_path.exists() else {}
    if progress.get("parent_sha256") != state["sha256"]:
        progress = dict(parent_sha256=state["sha256"], completed_pages=[])
    completed = set(progress["completed_pages"])
    lock = threading.Lock()

    def one(i):
        page_path = target / f"p{i+1:04}.txt"
        if i+1 in completed and page_path.exists():
            return i, page_path.read_text(encoding="utf-8"), False
        try:
            # With no output prefix, Poppler sends the rendered PGM to stdout.
            rendered = subprocess.run([renderer, "-f", str(i+1), "-l", str(i+1), "-r", "300",
                "-singlefile", "-gray", str(path)], capture_output=True, timeout=240)
            if rendered.returncode:
                return i, "", True
            result = subprocess.run([TESSERACT, "stdin", "stdout", "-l", "eng", "--dpi", "300"],
                input=rendered.stdout, capture_output=True, timeout=240,
                env={**os.environ, "OMP_THREAD_LIMIT": "1"})
            if result.returncode:
                return i, "", True
            text = result.stdout.decode("utf-8", errors="replace")
            page_path.write_text(text, encoding="utf-8")
            with lock:
                completed.add(i+1)
                progress["completed_pages"] = sorted(completed)
                FETCH.dump(progress_path, progress)
            return i, text, False
        except Exception:
            return i, "", True

    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        for i, text, failed in pool.map(one, low):
            if failed:
                state.setdefault("ocr_failed_pages", []).append(i+1)
            else:
                pages[i] = text
    state["ocr_cache_parent_sha256"] = state["sha256"]


def extract_one(rec):
    sid = rec["source_id"]
    target = RAW / "text" / sid
    target.mkdir(parents=True, exist_ok=True)
    state_path = RAW / "processing" / (sid + ".json")
    if state_path.exists():
        old = json.loads(state_path.read_text(encoding="utf-8"))
        expected_ocr = next((e.get("verification", {}).get("sha256") for e in rec.get("assets", []) if e.get("asset_role") == "ocr" and e.get("status") == "held"), None)
        needs_policy = str(rec.get("local_path", "")).lower().endswith(".pdf") and old.get("text_basis") == "archive-page-ocr" and old.get("page_text_policy") != "preserve-pdf-text-v2"
        if not needs_policy and old.get("sha256") == rec.get("sha256") and old.get("text_complete") and old.get("ocr_parent_sha256") == expected_ocr:
            return old
    state = {k: v for k, v in rec.items() if k != "assets"}
    if rec.get("no_sweep"):
        state.update(text_basis="", pdf_pages="", text_complete=True, text_reason="Witness listed without sweeping, as requested.")
        FETCH.dump(state_path, state)
        return state
    if rec["status"] == "failed" or not rec.get("local_path"):
        state.update(text_reason="Acquisition or held verification failed.", text_complete=True)
        FETCH.dump(state_path, state)
        return state
    path = ROOT / rec["local_path"]
    assets = rec.get("assets", [])
    ocr = next((e for e in assets if e.get("asset_role") == "ocr" and e.get("status") == "held" and not e.get("acquisition_failure")), None)
    state["ocr_parent_sha256"] = ocr.get("verification", {}).get("sha256") if ocr else None
    pages = []
    try:
        if path.suffix.lower() == ".pdf":
            info = subprocess.run(["pdfinfo", str(path)], capture_output=True, timeout=120)
            match = re.search(rb"^Pages:\s*(\d+)", info.stdout, re.M)
            if not match:
                raise ValueError("PDF page count unavailable")
            page_count = int(match[1])
            result = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"], capture_output=True, timeout=240)
            if result.returncode:
                raise ValueError("PDF text extraction failed")
            pages = result.stdout.decode("utf-8", errors="replace").split("\f")
            if pages and not pages[-1].strip():
                pages.pop()
            if len(pages) != page_count:
                pages = []
                for i in range(1, page_count + 1):
                    result = subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), "-enc", "UTF-8", str(path), "-"], capture_output=True, timeout=120)
                    pages.append(result.stdout.decode("utf-8", errors="replace").replace("\f", ""))
            if True:
                low = [i for i, text in enumerate(pages) if word_count(text) < 15]
                state.update(pdf_pages=page_count, image_only_pages=len(low), text_basis="pdf-text-layer")
                if len(low) > page_count / 5:
                    if ocr:
                        alternative = split_ocr(ROOT / ocr["local_paths"][0])
                        if len(alternative) == page_count:
                            for i in low:
                                pages[i] = alternative[i]
                            state["text_basis"] = "archive-page-ocr"
                            state["page_text_policy"] = "preserve-pdf-text-v2"
                            state["notes"] = state.get("notes", "") + " Text policy preserve-pdf-text-v2; archive OCR replaces pages below the text threshold."
                        else:
                            state["ocr_page_mismatch"] = len(alternative)
                    if state["text_basis"] == "pdf-text-layer":
                        state["needs_ocr"] = low
                        if OCR:
                            state["text_basis"] = "tesseract"
                            ocr_pages(path, sid, low, pages, state, target)
                            state.pop("needs_ocr", None)
        elif ocr:
            pages = split_ocr(ROOT / ocr["local_paths"][0])
            state.update(pdf_pages=len(pages), image_only_pages="", text_basis="archive-page-ocr")
        elif path.suffix.lower() in (".html", ".htm"):
            parser = Stripper()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            pages = [html.unescape("".join(parser.parts))]
            state.update(pdf_pages=1, image_only_pages="", text_basis="html", text_reason="HTML is stored as one page.")
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            pages = [text]
            state.update(pdf_pages=1, image_only_pages="", text_basis="djvu-txt-unpaged", text_reason="Whole archive text is provisional leaf 1; PDF leaf numbers unavailable until page OCR acquisition.")
        for i, text in enumerate(pages, 1):
            (target / f"p{i:04}.txt").write_text(text, encoding="utf-8")
        pmap = printed_map(pages)
        FETCH.dump(target / "printed_page_map.json", pmap)
        state.update(printed_page_detected_share=len(pmap) / len(pages) if pages else 0,
                     text_complete=not state.get("needs_ocr"), extracted_pages=len(pages),
                     transformation_parent_sha256=rec.get("sha256"), text_directory=target.relative_to(ROOT).as_posix())
        front = "\n".join(pages[:12])
        if sid.startswith("puratattva-"):
            title = str(rec.get("title", ""))
            match = re.search(r'(?:number|no\.?)\s*(\d+)(?:,|\s)\s*((?:19|20)\d{2}(?:\s*[-\u2013]\s*(?:\d{4}|\d{2}))?)?', title, re.I)
            if match:
                state["year_or_volume"] = "issue " + match[1] + ("; " + match[2] if match[2] else "")
            year_counts = collections.Counter(re.findall(r'\b(?:19|20)\d{2}\b', front))
            state["front_matter_year_candidates"] = dict(year_counts)
        if sid.startswith("iar-"):
            years = re.findall(r'(?:19|20)\d{2}\s*[-\u2013\u2014]\s*(?:(?:19|20))?\d{2}', front)
            counts = collections.Counter(re.sub(r"\s", "", y).replace("\u2013", "-").replace("\u2014", "-") for y in years)
            if counts:
                observed = counts.most_common(1)[0][0]
                state["observed_volume_year"] = observed
                state["year_or_volume"] = observed
                state["title"] = "Indian Archaeology " + observed + " - A Review"
                state["notes"] = rec.get("notes", "") + " Volume year detected in front matter."
                expected = re.search(r'iar-(\d{4})-(\d{2})', sid)
                if expected and not observed.startswith(expected[1] + "-") and state["status"] != "duplicate":
                    state["status"] = "wrong-volume"
            else:
                state["notes"] = rec.get("notes", "") + " Volume year unresolved in front matter."
        elif rec.get("title") and normalized(str(rec["title"])) in normalized(front):
            state["notes"] = rec.get("notes", "") + " Title confirmed in front matter."
        FETCH.dump(state_path, state)
        print(json.dumps(dict(source_id=sid, pages=len(pages), basis=state.get("text_basis"), pending_ocr=len(state.get("needs_ocr", [])))), flush=True)
    except Exception as exc:
        state.update(text_complete=False, text_reason="Extraction failed: " + type(exc).__name__)
        FETCH.dump(state_path, state)
        print(json.dumps(dict(source_id=sid, extraction_error=type(exc).__name__)), flush=True)
    return state


def extract_all():
    rows = sources()
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        states = list(pool.map(extract_one, rows))
    FETCH.dump(RECORDS / "processing-summary-1a.json", states)


def supplemental():
    requests = []
    for rec in sources():
        if not rec.get("identifier") or rec.get("no_sweep"):
            continue
        sid = rec["source_id"]
        state_path = RAW / "processing" / (sid + ".json")
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        candidate = source_hits(sid)
        if state.get("needs_ocr") or candidate:
            requests.append((sid, rec["identifier"], "ocr", rec["kind"]))
        if sid == "farmana-necropolis" and candidate:
            requests.append((sid, rec["identifier"], "pdf", "excavation-report"))
    before = len(proposal_data()["sources"])
    append_assets(requests)
    print(json.dumps(dict(added_assets=len(proposal_data()["sources"]) - before)))


KEYWORDS = ["seal", "sealing", "tablet", "inscri", "script", "sign", "character", "letter", "legend", "graffit", "tag", "impression"]
PATTERNS = {k: re.compile(r"(?<![a-z])" + r"[\s\-\u00ad]*".join(k) + r"[a-z]*", re.I) for k in KEYWORDS}


def hits(text):
    compact = normalized(text)
    sites = {}
    for code, terms in SITES.items():
        # Boundaries retain specificity while optional spacing tolerates OCR splits.
        count = 0
        for term in terms:
            letters = re.sub(r"[^a-z0-9]", "", normalized(term))
            if letters not in compact:
                continue
            pattern = r"(?<![a-z0-9])" + r"[\s\-\u00ad\u2010-\u2014]*".join(re.escape(c) for c in letters) + r"(?![a-z0-9])"
            count += len(re.findall(pattern, text, re.I))
        if count:
            sites[code] = count
    kws = {k: len(p.findall(text)) for k, p in PATTERNS.items() if k in compact}
    kws = {k: v for k, v in kws.items() if v}
    generic = "harappan" in compact and bool(kws)
    return sites, kws, generic


def source_hits(sid):
    for path in (RAW / "text" / sid).glob("p[0-9][0-9][0-9][0-9].txt"):
        sites, kws, generic = hits(path.read_text(encoding="utf-8"))
        if kws and (sites or generic):
            return True
    return False


def iar_headings(text):
    # Only uppercase site/district heading spans are eligible for tracked output.
    found = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not re.search(r'\b(?:EXCAVATION|EXPLORATION)\s+(?:AT|IN)\b', line, re.I):
            continue
        span = line.strip()
        for following in lines[i+1:i+3]:
            if "DISTRICT" in span.upper():
                break
            if following.strip() and following.upper() == following:
                span += " " + following.strip()
        match = re.search(r'\b(?:EXCAVATION|EXPLORATION)\s+(?:AT|IN)\s+(.+?\bDISTRICT\b(?:\s+[^.;:\u2014\u2013]+)?)(?:[.;:\u2014\u2013]|$)', span, re.I)
        if match:
            value = re.split(r'\s+[-\u2014\u2013]\s*', match[1])[0].strip(" ,:-")
            if len(value.split()) <= 18 and not re.search(r'\b(?:SEAL|SCRIPT|INSCRI|FIG|PLATE|CM|MM|KG)\b', value, re.I):
                found.append((i, value))
    return found


FIELDS = "source_id,title,authors_or_editors,year_or_volume,kind,route,identifier,url,local_path,file_name,bytes,sha256,archive_md5,archive_sha1,md5_match,sha1_match,pdf_pages,text_basis,image_only_pages,printed_page_detected_share,rights_notice_observed,status,notes".split(",")
CANDIDATE_FIELDS = "source_id,pdf_page,printed_page,site_code,generic_harappan_hit,n_site_terms,n_keywords,keyword_classes,context_only".split(",")


def sweep():
    states = json.loads((RECORDS / "processing-summary-1a.json").read_text(encoding="utf-8"))
    states = [json.loads((RAW / "processing" / (r["source_id"] + ".json")).read_text(encoding="utf-8"))
              if (RAW / "processing" / (r["source_id"] + ".json")).exists() else r for r in states]
    candidates, leads, exposure = [], [], []
    by_source, by_site = {}, collections.Counter({code: 0 for code in SITES})
    unresolved = []
    selected = None
    if INCREMENTAL and (RECORDS / "source-register-1a.csv").exists():
        with (RECORDS / "source-register-1a.csv").open(encoding="utf-8", newline="") as f:
            previous = {r["source_id"]: r for r in csv.DictReader(f)}
        selected = {r["source_id"] for r in states if r["source_id"] not in previous or any(
            str(r.get(k, "")) != str(previous[r["source_id"]].get(k, "")) for k in ("sha256", "text_basis", "pdf_pages")) or
            (r.get("page_text_policy") == "preserve-pdf-text-v2" and "preserve-pdf-text-v2" not in previous[r["source_id"]].get("notes", ""))}
        with (RECORDS / "candidate-pages-1a.csv").open(encoding="utf-8", newline="") as f:
            candidates = [r for r in csv.DictReader(f) if r["source_id"] not in selected]
        for r in candidates:
            for k in ("pdf_page", "n_site_terms", "n_keywords", "generic_harappan_hit", "context_only"):
                r[k] = int(r[k])
        with (RECORDS / "new-site-leads-1a.csv").open(encoding="utf-8", newline="") as f:
            leads = [r for r in csv.DictReader(f) if r["source_id"] not in selected]
        old = json.loads((RECORDS / "sweep-summary-1a.json").read_text(encoding="utf-8"))
        by_source = {k: v for k, v in old["per_source"].items() if k not in selected}
        unresolved = [r for r in old.get("unresolved_iar_heading_pages", []) if r["source_id"] not in selected]
    for rec in states:
        sid = rec["source_id"]
        target = RAW / "text" / sid
        files = sorted(target.glob("p[0-9][0-9][0-9][0-9].txt"))
        if rec.get("text_basis") == "djvu-txt-unpaged":
            rec["notes"] = rec.get("notes", "") + " " + rec.get("text_reason", "")
        if rec.get("no_sweep") or rec.get("exclude_from_sweep") or not files:
            rec["notes"] = rec.get("notes", "") + " " + rec.get("text_reason", "")
            if rec.get("no_sweep"):
                exposure.append(dict(source_id=sid, agent="codex gpt-6.1-sol run 1A", access="bytes hashed by script",
                    pages="", purpose="Witness path and SHA256 only; no extraction or sweep."))
            elif rec.get("exclude_from_sweep"):
                exposure.append(dict(source_id=sid, agent="codex gpt-6.1-sol run 1A", access="text layer read by script",
                    pages=f"1-{len(files)}", purpose="Bibliographic volume check; excluded from sweep."))
            continue
        pmap_path = target / "printed_page_map.json"
        exposure.append(dict(source_id=sid, agent="codex gpt-6.1-sol run 1A", access="text layer read by script",
                             pages=f"1-{len(files)}", purpose="Page extraction, bibliography checks and keyword sweep."))
        if selected is not None and sid not in selected:
            continue
        pmap = json.loads(pmap_path.read_text(encoding="utf-8")) if pmap_path.exists() else {}
        direct, per_site, last_heading = {}, collections.Counter(), ""
        snippets = RAW / "snippets" / (sid + ".jsonl")
        snippets.parent.mkdir(parents=True, exist_ok=True)
        with snippets.open("w", encoding="utf-8") as out:
            for p, path in enumerate(files, 1):
                text = path.read_text(encoding="utf-8")
                sites, kws, generic = hits(text)
                if sid.startswith("iar-"):
                    headings = iar_headings(text)
                    lines = text.splitlines()
                    sections = [(last_heading, "\n".join(lines[:headings[0][0]]))] if headings else [(last_heading, text)]
                    for h, (offset, heading) in enumerate(headings):
                        end = headings[h+1][0] if h+1 < len(headings) else len(lines)
                        sections.append((heading, "\n".join(lines[offset:end])))
                    page_leads = set()
                    if generic and any(k in kws for k in ("seal", "inscri", "script")):
                        for heading, section in sections:
                            if not any(PATTERNS[k].search(section) for k in ("seal", "inscri", "script")):
                                continue
                            if not heading:
                                unresolved.append(dict(source_id=sid, pdf_page=p))
                            elif not hits(heading)[0] and heading not in page_leads:
                                page_leads.add(heading)
                                leads.append(dict(source_id=sid, pdf_page=p, printed_page=pmap.get(str(p), ""), heading_as_printed=heading))
                    if headings:
                        last_heading = headings[-1][1]
                if not kws or not (sites or generic):
                    continue
                codes = list(sites) or ["GENERIC"]
                direct[p] = codes
                for code in codes:
                    candidates.append(dict(source_id=sid, pdf_page=p, printed_page=pmap.get(str(p), ""), site_code=code,
                        generic_harappan_hit=int(generic), n_site_terms=sites.get(code, 0), n_keywords=sum(kws.values()),
                        keyword_classes="|".join(kws), context_only=0))
                    by_site[code] += 1
                    per_site[code] += 1
                out.write(json.dumps(dict(pdf_page=p, page_text=text), ensure_ascii=False) + "\n")
        context = set()
        for p, codes in direct.items():
            for neighbor in (p-1, p+1):
                if 1 <= neighbor <= len(files):
                    for code in codes:
                        if code in direct.get(neighbor, []) or (neighbor, code) in context:
                            continue
                        context.add((neighbor, code))
                        candidates.append(dict(source_id=sid, pdf_page=neighbor, printed_page=pmap.get(str(neighbor), ""),
                            site_code=code, generic_harappan_hit=0, n_site_terms=0, n_keywords=0, keyword_classes="", context_only=1))
        by_source[sid] = dict(candidate_pages=len(direct), context_page_references=len(context), per_site=dict(per_site))
        print(json.dumps(dict(swept_source=sid, candidate_pages=len(direct))), flush=True)
    by_site = collections.Counter({code: 0 for code in SITES})
    for row in candidates:
        if not int(row["context_only"]):
            by_site[row["site_code"]] += 1
    write_csv(RECORDS / "candidate-pages-1a.csv", sorted(candidates, key=lambda r: (r["source_id"], r["pdf_page"], r["site_code"])), CANDIDATE_FIELDS)
    write_csv(RECORDS / "new-site-leads-1a.csv", leads, ["source_id", "pdf_page", "printed_page", "heading_as_printed"])
    write_csv(RECORDS / "source-register-1a.csv", states, FIELDS)
    write_csv(RECORDS / "exposure-log-1a.csv", exposure, ["source_id", "agent", "access", "pages", "purpose"])
    FETCH.dump(RECORDS / "sweep-summary-1a.json", dict(per_source=by_source, per_site=dict(by_site),
         candidate_page_references=sum(by_site.values()), unique_candidate_pages=sum(r["candidate_pages"] for r in by_source.values()),
         new_site_leads=len(leads), context_rows=sum(int(r["context_only"]) for r in candidates),
         unresolved_iar_heading_pages=unresolved,
         incremental_sources_reswept=sorted(selected) if selected is not None else "all",
         unpaged_note="Provisional unpaged text uses page 1; rerun after supplemental OCR acquisition."))
    print(json.dumps(dict(sources=len(states), candidate_pages=sum(r["candidate_pages"] for r in by_source.values()), leads=len(leads))))


def inventory():
    metas = []
    for path in (RAW / "metadata").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("metadata"):
            m = data["metadata"]
            title = str(m.get("title", ""))
            if re.search(r'man\s*(and|&)\s*environment|puratattva', title, re.I):
                metas.append(dict(identifier=path.stem, title=title, date=m.get("date", ""), text=bool(FETCH.choose(data, "text"))))
    print(json.dumps(metas, ensure_ascii=True))


def main():
    global ROOT, RAW, RECORDS, FETCH, SITES, OCR, TESSERACT, INCREMENTAL
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["held", "duplicates", "extract", "supplemental", "sweep", "inventory"])
    ap.add_argument("--root", type=pathlib.Path, required=True)
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    ap.add_argument("--records", type=pathlib.Path, required=True)
    ap.add_argument("--seed", type=pathlib.Path, required=True)
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--incremental", action="store_true")
    args = ap.parse_args()
    ROOT, RAW, RECORDS, OCR = args.root.resolve(), args.raw.resolve(), args.records.resolve(), args.ocr
    INCREMENTAL = args.incremental
    TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    FETCH = load_module(RECORDS / "fetch_proposed.py", "fetch_proposed")
    FETCH.initialize(ROOT, RAW, RECORDS)
    SITES = {}
    with args.seed.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            SITES[row["site_code"]] = list(dict.fromkeys([row["site"]] + [s for s in row["aliases"].split("|") if s]))
    {"held": held_inventory, "duplicates": duplicates, "extract": extract_all,
     "supplemental": supplemental, "sweep": sweep, "inventory": inventory}[args.command]()


if __name__ == "__main__":
    main()
