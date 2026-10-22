"""Acquire pinned assets. Run with python -I and explicit repository paths."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request

LOCK = threading.RLock()
sys.dont_write_bytecode = True
ORIGINAL_OPEN = urllib.request.urlopen


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def hashes(path):
    hs = {k: hashlib.new(k) for k in ("sha256", "md5", "sha1")}
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            for h in hs.values():
                h.update(chunk)
    return {k: h.hexdigest() for k, h in hs.items()}


def initialize(root, raw, records):
    global ROOT, RAW, RECORDS, FETCH
    ROOT, RAW, RECORDS = root.resolve(), raw.resolve(), records.resolve()
    RAW.mkdir(parents=True, exist_ok=True)
    RECORDS.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("repository_fetch", ROOT / "tools/fetch_data.py")
    FETCH = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(FETCH)
    urllib.request.urlopen = logged_open


def log(url, status, size, **fields):
    with LOCK:
        with (RECORDS / "acquisition-log-1a.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(dict(url=url, time_utc=stamp(), status=status, bytes=size, **fields)) + "\n")


class Response:
    def __init__(self, response, url):
        self.response, self.url, self.size = response, url, 0

    def __getattr__(self, name):
        return getattr(self.response, name)

    def read(self, *args):
        try:
            data = self.response.read(*args)
            self.size += len(data)
            return data
        except Exception:
            raise

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        log(self.url, self.response.status if typ is None else "read-failed", self.size)
        self.response.close()


def logged_open(request, *args, **kwargs):
    url = request.full_url if hasattr(request, "full_url") else str(request)
    try:
        return Response(ORIGINAL_OPEN(request, *args, **kwargs), url)
    except Exception as exc:
        log(url, getattr(exc, "code", type(exc).__name__), 0)
        raise


def request(url, method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": FETCH.USER_AGENT}, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read(), dict(resp.headers)


def metadata(identifier):
    path = RAW / "metadata" / (identifier + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    for attempt in range(3):
        try:
            body, _ = request("https://archive.org/metadata/" + urllib.parse.quote(identifier))
            data = json.loads(body)
            if not data.get("files"):
                return None
            dump(path, data)
            return data
        except Exception:
            if attempt == 2:
                return None


def files_for(meta, suffix):
    return [f for f in meta.get("files", []) if f["name"].lower().endswith(suffix)]


def choose(meta, role, exact=None):
    if exact:
        candidates = [f for f in meta["files"] if f["name"] == exact]
    elif role == "pdf":
        candidates = files_for(meta, ".pdf")
        candidates.sort(key=lambda f: (f.get("source") != "original", "_text" in f["name"]))
    elif role == "text":
        candidates = files_for(meta, "_djvu.txt")
    else:
        candidates = files_for(meta, "_djvu.xml") or files_for(meta, "_hocr.html")
    return candidates[0] if candidates else None


def proposal(source_id, identifier, meta, role, kind, exact=None):
    f = choose(meta, role, exact)
    if not f:
        return None
    m = meta["metadata"]
    suffix = {"pdf": "", "text": "-djvu-txt", "ocr": "-page-ocr"}[role]
    return dict(id=source_id + suffix, logical_source_id=source_id, title=m.get("title", identifier),
                authors_or_editors=m.get("creator", ""), year_or_volume=m.get("date", ""),
                kind=kind, asset_role=role, fetch=dict(method="http", url="https://archive.org/download/" +
                urllib.parse.quote(identifier) + "/" + urllib.parse.quote(f["name"], safe=""),
                filename=f["name"], bytes=int(f.get("size", 0)), archive_md5=f.get("md5", ""),
                archive_sha1=f.get("sha1", "")), identifiers={"archive_identifier": identifier},
                rights={"status": "rights-unverified", "licenseurl": m.get("licenseurl", "")},
                status="not-held", questions=["Q-1026"])


def search(query):
    url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": query,
        "fl[]": "identifier,title,date", "rows": 1000, "output": "json"})
    try:
        body, _ = request(url)
        data = json.loads(body)
        dump(RAW / "metadata" / ("search-" + hashlib.sha256(query.encode()).hexdigest()[:12] + ".json"), data)
        return data.get("response", {}).get("docs", [])
    except Exception:
        return []


def discover():
    entries, inventory, failures = [], [], []
    reports = [
        ("farmana-2006-08", "excavationsatfarmana200608vshindeetal_212_v", "Excavations at Farmana, 2006-08 - V Shinde et al.pdf"),
        ("farmana-2007-08-report", "farmanaexcavationreport200708vasantshindeetal_254_F", "Farmana Excavation Report 2007-08 - Vasant Shinde et al.pdf"),
        ("farmana-necropolis", "harappannecropolisatfarmanainghaggarbasinvshindeetal_464_U", None),
        ("rakhigarhi-nath", "excavationsatrakhigarhi19972000amarendranath_457_Z", "Excavations at Rakhigarhi, 1997-2000 - Amarendra Nath.pdf"),
        ("surkotada-1990", "masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t", None),
        ("kanmer-ch6", "excavationsatkanmer200509ch6auesugismeena_648_B", "Excavations at Kanmer, 2005-09, ch 6 - A Uesugi & S Meena.pdf"),
        ("tarkhanewala-2009", "excavationsattar00triv", "excavationsattar00triv.pdf")]
    known_p = {n: ["dli.ministry." + str(29975 + n - 18)] for n in range(18, 28)}
    known_p.update({28: ["in.gov.ignca.84853", "puratattvano28indianarchaeologicalsocietybhu_511_M"],
        **{n: ["dli.ministry." + str(29986 + n - 29)] for n in range(29, 34)},
        34: ["in.gov.ignca.87942", "puratattvano34indianarchaeologicalsocietybhu_20_W"],
        35: ["dli.ministry.29994"], 36: ["dli.ministry.29992"], 37: ["dli.ministry.29993"]})
    found_p = search('title:puratattva AND mediatype:texts')
    found_m = search('title:("man and environment") AND mediatype:texts')
    allids = {x[1] for x in reports} | {i for v in known_p.values() for i in v}
    allids |= {"dli.calcutta." + str(n).zfill(5) for n in range(6847, 6867)}
    allids |= {x["identifier"] for x in found_p + found_m}
    allids |= {"tdl.49427-indian-archaeology-2003-2004-a-review", "indianarchaeology199798areview_830_j"}
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        metas = dict(zip(sorted(allids), pool.map(metadata, sorted(allids))))
    for sid, ident, exact in reports:
        meta = metas.get(ident)
        if not meta:
            failures.append(dict(source_id=sid, identifier=ident, reason="archive-metadata-unavailable"))
            continue
        inventory.append(dict(source_id=sid, identifier=ident, kind="excavation-report", route="archive.org"))
        for role in (["text"] if sid == "farmana-necropolis" else ["pdf", "text"]):
            p = proposal(sid, ident, meta, role, "excavation-report", exact if role == "pdf" else None)
            if p:
                entries.append(p)
            else:
                failures.append(dict(source_id=sid, role=role, reason="archive-file-unavailable"))
    for doc in found_p:
        title = str(doc.get("title", ""))
        match = re.search(r'(?:no\.?|vol(?:ume)?\.?|issue)\s*[:.-]?\s*(\d{1,2})\b', title, re.I)
        if not match:
            match = re.search(r'puratattva\D{0,8}(\d{1,2})\b', title, re.I)
        if match and 18 <= int(match[1]) <= 80:
            known_p.setdefault(int(match[1]), []).append(doc["identifier"])
    selected = []
    for n, ids in sorted(known_p.items()):
        ids = list(dict.fromkeys(ids))
        choices = [i for i in ids if metas.get(i) and choose(metas[i], "text")]
        if choices:
            selected.append(("puratattva-" + str(n), choices[0], str(n), ids))
        else:
            failures.append(dict(source_id="puratattva-" + str(n), reason="archive-text-unavailable"))
    m_groups = {}
    for ident, meta in metas.items():
        if not meta:
            continue
        m = meta.get("metadata", {})
        title = str(m.get("title", ""))
        if not re.search(r'man\s*(?:and|&)\s*environment', title, re.I):
            continue
        match = re.search(r'(?:vol(?:ume)?s?\.?|v\.)\s*[:.-]?\s*(\d{1,2})(?:\s*[-&/]\s*(\d{1,2}))?', title, re.I)
        if not match:
            match = re.search(r'environment\D{0,5}(\d{1,2})(?:\s*[-&/]\s*(\d{1,2}))?', title, re.I)
        if match and int(match[1]) >= 10:
            vol = match[1] + ("-" + match[2] if match[2] else "")
            m_groups.setdefault(vol, []).append(ident)
    for vol, ids in sorted(m_groups.items()):
        choices = [i for i in ids if choose(metas[i], "text")]
        if choices:
            selected.append(("man-environment-" + vol, choices[0], vol, ids))
    for sid, ident, vol, alternatives in selected:
        p = proposal(sid, ident, metas[ident], "text", "journal-issue-ocr")
        p["id"] = sid
        p["year_or_volume"] = vol
        entries.append(p)
        inventory.append(dict(source_id=sid, identifier=ident, kind="journal-issue", route="archive.org",
                              year_or_volume=vol, alternates=alternatives))
    ident = "tdl.49427-indian-archaeology-2003-2004-a-review"
    if metas.get(ident):
        for role in ("text", "ocr"):
            p = proposal("iar-2003-04", ident, metas[ident], role, "annual-review")
            if p:
                if role == "text":
                    p["id"] = "iar-2003-04"
                entries.append(p)
        inventory.append(dict(source_id="iar-2003-04", identifier=ident, kind="annual-review", route="archive.org"))
    for year in [1992, 1993, 1994, 1995, 1996, 1997, 1998, 2000, 2006, 2010, 2012]:
        sid = f"iar-{year}-{str(year+1)[2:]}"
        filename = f"{year}-{year+1}.pdf"
        url = "https://www.asiaurangabadcircle.com/assets/files/publications/" + filename
        size = 0
        try:
            _, hdrs = request(url, "HEAD")
            size = int(hdrs.get("Content-Length", 0))
        except Exception:
            pass
        entries.append(dict(id=sid, logical_source_id=sid, title=f"Indian Archaeology {year}-{year+1} - A Review",
            authors_or_editors="", year_or_volume=f"{year}-{year+1}", kind="annual-review", asset_role="pdf",
            fetch=dict(method="http", url=url, filename=filename, bytes=size), identifiers={},
            rights=dict(status="rights-unverified", licenseurl=""), status="not-held", questions=["Q-1026"]))
        inventory.append(dict(source_id=sid, kind="annual-review", route="asi-mirror"))
    dump(RECORDS / "manifest-proposals-1a.json", {"sources": entries})
    dump(RECORDS / "discovery-1a.json", dict(sources=inventory, failures=failures,
         journal_searches=["Internet Archive title search and neighbouring Calcutta identifiers"],
         metadata_items=len([m for m in metas.values() if m])))
    print(json.dumps(dict(proposed_assets=len(entries), logical_sources=len(inventory), failures=len(failures))))


def acquire(entry):
    if entry.get("status") == "held":
        if all((ROOT / p).is_file() for p in entry.get("local_paths", [])):
            return entry
        pins = list(entry.get("hashes", {}).values())
        if pins:
            entry["fetch"]["sha256"] = pins[0]
        entry["status"] = "not-held"
    dest = RAW / "sources" / entry["id"]
    if dest.exists():
        rec = dest / "acquisition.json"
        if not rec.exists():
            entry["acquisition_failure"] = "existing-incomplete-destination-kept"
            return entry
    else:
        try:
            FETCH.fetch_http(entry, dest, False)
        except Exception as exc:
            entry["acquisition_failure"] = type(exc).__name__
            return entry
    try:
        record = json.loads((dest / "acquisition.json").read_text(encoding="utf-8"))
        path = dest / entry["fetch"]["filename"]
        hs = hashes(path)
        rel = path.relative_to(ROOT).as_posix()
        entry.update(status="held", location="local-only", local_paths=[rel], hashes={rel: record["sha256"]},
                     verification=hs, retrieved_utc=record["retrieved_utc"], actual_bytes=path.stat().st_size)
        entry["fetch"]["sha256"] = record["sha256"]
        for alg in ("md5", "sha1"):
            pin = entry["fetch"].get("archive_" + alg)
            entry[alg + "_match"] = (hs[alg] == pin) if pin else ""
        if hs["sha256"] != record["sha256"] or entry["md5_match"] is False or entry["sha1_match"] is False:
            entry["acquisition_failure"] = "hash-mismatch-kept"
    except Exception as exc:
        entry["acquisition_failure"] = type(exc).__name__
    return entry


def fetch_all():
    path = RECORDS / "manifest-proposals-1a.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(acquire, e): e for e in data["sources"]}
        for future in cf.as_completed(futures):
            future.result()
            dump(path, data)
    print(json.dumps(dict(held=sum(e["status"] == "held" for e in data["sources"]),
                          failed=sum(bool(e.get("acquisition_failure")) for e in data["sources"]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["discover", "fetch"])
    ap.add_argument("--root", type=pathlib.Path, required=True)
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    ap.add_argument("--records", type=pathlib.Path, required=True)
    args = ap.parse_args()
    initialize(args.root, args.raw, args.records)
    {"discover": discover, "fetch": fetch_all}[args.command]()


if __name__ == "__main__":
    main()
