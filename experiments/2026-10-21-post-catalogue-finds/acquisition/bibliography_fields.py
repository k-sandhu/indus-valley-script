"""Validate bibliographic fields against title text and running heads."""
import collections
import html
import json
import pathlib
import re
import subprocess


def norm(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())


def annual_years(text):
    values = []
    for first, last in re.findall(r'\b((?:19|20)\d{2})\s*[-\u2013\u2014]\s*((?:(?:19|20))?\d{2})\b', text):
        start = int(first)
        end = int(last) if len(last) == 4 else start // 100 * 100 + int(last)
        if end < start:
            end += 100
        if end == start+1:
            values.append(f"{start}-{str(end)[2:]}")
    return values


def person(value):
    words = re.findall(r'[A-Za-z]+', value)
    return (2 <= len(words) <= 18 and sum(w[0].isupper() for w in words) / len(words) >= .75
            and not re.search(r'\b(?:ial|correspondence|process|center|board|survey|society|university|department|copyright|co-editors)\b', value, re.I))


KNOWN = {
    "farmana-2006-08": (["Excavations at Farmana"], ["Vasant Shinde", "Toshiki Osada", "Manmohan Kumar"]),
    "farmana-2007-08-report": (["Farmana Excavation Report", "Excavations at Farmana"], ["Vasant Shinde", "Toshiki Osada", "Akinori Uesugi", "Manmohan Kumar"]),
    "farmana-necropolis": (["Harappan Necropolis at Farmana in the Ghaggar Basin", "Harappan Necropolis at Farmana"], ["Vasant Shinde", "Toshiki Osada", "Manmohan Kumar"]),
    "rakhigarhi-nath": (["Excavations at Rakhigarhi"], ["Amarendra Nath"]),
    "surkotada-1990": (["Excavations at Surkotada"], ["Jagat Pati Joshi"]),
    "kanmer-ch6": (["Excavations at Kanmer"], ["Akinori Uesugi", "S. Meena", "J. S. Kharakwal", "Y. S. Rawat", "Toshiki Osada"]),
    "tarkhanewala-2009": (["Excavations at Tarkhanewala-Dera and Chak 86 (2003-2004)"], ["P. K. Trivedi"]),
    "shikarpur-2009-held": (["Excavations at Shikarpur"], []),
    "nuhato-2018-held": (["Excavation of Nuhato Site of Indus Valley Civilization"], []),
    "bisht-2015-held": (["Dholavira Report"], ["R. S. Bisht"]),
}


def repair(args):
    root, raw, records = args.root.resolve(), args.raw.resolve(), args.records.resolve()
    state_path = records / "processing-summary-1a.json"
    states = json.loads(state_path.read_text(encoding="utf-8"))
    proposals_path = records / "manifest-proposals-1a.json"
    proposals = json.loads(proposals_path.read_text(encoding="utf-8"))
    grouped = collections.defaultdict(list)
    for e in proposals["sources"]:
        grouped[e["logical_source_id"]].append(e)
    held = {r["source_id"]: r for r in json.loads((records / "held-verification-1a.json").read_text(encoding="utf-8"))}
    results = []
    for r in states:
        sid = r["source_id"]
        r["file_name"] = pathlib.Path(r.get("local_path", "")).name
        if r.get("no_sweep"):
            (raw / "processing" / (sid + ".json")).write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
            continue
        files = sorted((raw / "text" / sid).glob("p[0-9][0-9][0-9][0-9].txt"))[:12]
        page_text = [p.read_text(encoding="utf-8") for p in files]
        front = "\n".join(page_text)
        first = "\n".join(page_text[:3])
        entries = grouped.get(sid, [])
        origin = next((e for e in entries if e["asset_role"] == "pdf"), None) or next((e for e in entries if e["asset_role"] == "text"), None)
        title = origin["title"] if origin else held.get(sid, {}).get("title", pathlib.Path(r.get("local_path", "")).stem)
        identifier = r.get("identifier", "")
        meta_path = raw / "metadata" / (identifier + ".json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")).get("metadata", {}) if meta_path.exists() else {}
        basis, confirmed = ("archive metadata" if origin else "held record"), False
        names = re.findall(r'(?im)^[ \t]*(?:edited[ \t]+by|(?:chief[ \t]+)?editors?)\b[ \t]*:?[ \t]*(?:\r?\n[ \t]*)?([A-Z][A-Za-z .,&()\x27-]{2,90})[ \t]*$', first)
        names = [re.sub(r'\s+', ' ', v.strip()) for v in names if person(v)]
        if sid in KNOWN:
            titles, authors = KNOWN[sid]
            for value in titles:
                if norm(value) in norm(front):
                    title, basis, confirmed = value, "front-matter short-title match", True
                    break
            known_authors = [v for v in authors if norm(v) in norm(front)]
            if known_authors:
                names = known_authors
            if sid == "bisht-2015-held":
                title = "Dholavira Report"
        if r.get("local_path", "").lower().endswith(".html"):
            names = []
            content = (root / r["local_path"]).read_text(encoding="utf-8", errors="replace")
            tag = re.search(r'<title\b[^>]*>(.*?)</title>', content, re.I | re.S)
            if tag:
                value = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', tag[1]))).strip()
                if 3 <= len(value.split()) <= 45 and not re.search(r'Just a moment|Access denied', value, re.I):
                    title, basis, confirmed = value, "HTML title element", True
        source_path = root / r.get("local_path", "")
        if sid.startswith("iar-"):
            volume_text = front
            if source_path.suffix.lower() == ".pdf":
                proc = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "12", "-enc", "UTF-8", str(source_path), "-"], capture_output=True, timeout=120)
                if proc.returncode == 0 and annual_years(proc.stdout.decode("utf-8", errors="replace")):
                    volume_text = proc.stdout.decode("utf-8", errors="replace")
            years = annual_years(volume_text)
            if years:
                observed = collections.Counter(years).most_common(1)[0][0]
                r["observed_volume_year"] = observed
                r["year_or_volume"] = observed
                title, basis, confirmed = "Indian Archaeology " + observed + " - A Review", "title/contents volume year", True
                expected = re.search(r'iar-(\d{4})', sid)[1]
                duplicate = any(e.get("duplicate_of") for e in entries)
                r["status"] = "duplicate" if duplicate else "wrong-volume" if observed[:4] != expected else "held-verified" if r["route"] == "held" else "acquired"
            else:
                r.pop("observed_volume_year", None)
        if sid.startswith("puratattva-"):
            title = "Puratattva"
            expected = re.search(r'puratattva-(\d+)', sid)[1]
            number = re.search(r'(?im)^[ \t]*(?:number|no\.?)[ \t]*[:.-]?[ \t]*(\d{1,2})\b', first)
            number = number or re.search(r'(?is)puratattva.{0,150}?(?:number|no\.?)[ \t]*(\d{1,2})\b', first)
            actual = number[1] if number else expected
            if number:
                basis, confirmed = "front-matter issue number", True
                r["observed_issue_number"] = actual
                if actual != expected:
                    r["status"] = "wrong-volume"
            years = annual_years(first)
            if not years:
                mt = str(meta.get("title", ""))
                years = annual_years(mt)
            date = re.search(r'(?:19|20)\d{2}', str(meta.get("date", "")))
            year = collections.Counter(years).most_common(1)[0][0] if years else date[0] if date else ""
            r["year_or_volume"] = "issue " + actual + ("; " + year if year else "")
        elif sid.startswith("man-environment-"):
            title = "Man and Environment"
            header_years = []
            for text in page_text:
                head = "\n".join(text.splitlines()[:20])
                if "manandenvironment" in norm(head):
                    header_years.extend(re.findall(r'\b(?:19[7-9]\d|20[0-2]\d)\b', head))
            vol = sid.removeprefix("man-environment-")
            r["year_or_volume"] = "volume " + vol
            if header_years:
                dates = [k for k, n in collections.Counter(header_years).most_common(2)]
                r["year_or_volume"] += "; header year(s) " + ",".join(sorted(dates))
            if "manandenvironment" in norm(front):
                basis, confirmed = "front-matter journal title", True
        elif not sid.startswith("iar-"):
            publication = re.search(r'(?:\u00a9|copyright)\s*(?:[^\n\d]{0,40})((?:19|20)\d{2})', first, re.I)
            standalone = re.findall(r'(?m)^[ \t]*((?:19|20)\d{2})[ \t]*$', first)
            if publication:
                r["year_or_volume"] = publication[1]
            elif standalone:
                r["year_or_volume"] = collections.Counter(standalone).most_common(1)[0][0]
            elif sid.startswith("farmana-"):
                r["year_or_volume"] = ""
        author = "; ".join(dict.fromkeys(names))
        if not author:
            creator = meta.get("creator", "")
            candidates = creator if isinstance(creator, list) else [creator]
            names = [v for v in candidates if isinstance(v, str) and person(v) and norm(v) in norm(front)]
            author = "; ".join(names)
        r.update(title=title, authors_or_editors=author)
        # Remove notes from the superseded bibliography heuristic.
        r["notes"] = r.get("notes", "").split(" Bibliography basis:")[0]
        r["notes"] += " Bibliography basis: " + basis + "."
        if not author:
            r["notes"] += " Author/editor unresolved; archive creator not treated as authorship."
        if r.get("status") == "wrong-volume":
            r["notes"] += " Observed volume differs from requested source id."
        if r.get("ocr_page_mismatch"):
            r["notes"] += " Archive OCR leaf count differs; Tesseract used on the held PDF."
        if r.get("text_basis") == "djvu-txt-unpaged":
            r["notes"] += " Unpaged text retained after a zero-hit sweep."
        result = dict(source_id=sid, title=title, authors_or_editors=author, year_or_volume=r.get("year_or_volume", ""),
            title_basis=basis, title_confirmed=confirmed, author_confirmed=bool(author))
        results.append(result)
        for entry in entries:
            entry["authors_or_editors"] = author
            if confirmed:
                entry["title"] = title
        (raw / "processing" / (sid + ".json")).write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    state_path.write_text(json.dumps(states, indent=2, ensure_ascii=False), encoding="utf-8")
    proposals_path.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")
    (records / "bibliography-validation-1a.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(dict(sources=len(results), titles_confirmed=sum(r["title_confirmed"] for r in results), authors_confirmed=sum(r["author_confirmed"] for r in results))))
