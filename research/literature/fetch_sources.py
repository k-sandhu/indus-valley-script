"""Download primary literature and preserve retrieval/provenance for this audit.

Run: python research/literature/fetch_sources.py
Source files are research inputs, not claims of permission to redistribute them.
"""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ("rao_2009_science", "2009", "peer-reviewed paper", "https://homes.cs.washington.edu/~rao/ScienceIndus.pdf"),
    ("rao_2009_markov", "2009", "peer-reviewed paper", "https://homes.cs.washington.edu/~rao/PNASIndus.pdf"),
    ("yadav_2010_ngrams", "2010", "author manuscript of peer-reviewed paper", "https://arxiv.org/pdf/0901.3017"),
    ("sinha_2011_network", "2011", "author manuscript of peer-reviewed paper", "https://arxiv.org/pdf/1005.4997"),
    ("rao_2010_reply", "2010", "peer-reviewed discussion", "https://aclanthology.org/J10-4016.pdf"),
    ("sproat_2010", "2010", "peer-reviewed discussion", "https://aclanthology.org/J10-4009.pdf"),
    ("yadav_2011_design", "2011", "peer-reviewed paper", "https://www.harappa.com/sites/default/files/pdf/Indus-sign-design.pdf"),
    ("yadav_2013_site_type", "2013", "peer-reviewed paper", "https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf"),
    ("yadav_2017_clusters", "2017", "peer-reviewed paper", "https://www.ijcaonline.org/archives/volume162/number1/yadav-2017-ijca-913207.pdf"),
    ("yadav_2019_overview", "2019", "peer-reviewed paper", "https://insa.nic.in/writereaddata/UpLoadedFiles/IJHS/Vol54_2_2019__Art01.pdf"),
    ("rao_2018_economics", "2018", "published edited-volume chapter", "https://arxiv.org/pdf/1812.00049"),
    ("mukhopadhyay_2019", "2019", "peer-reviewed paper", "https://www.nature.com/articles/s41599-019-0274-1.pdf"),
    ("mukhopadhyay_2023", "2023", "peer-reviewed paper", "https://www.nature.com/articles/s41599-023-02320-7.pdf"),
    ("mukhopadhyay_2025_fish", "2025", "research bulletin article", "https://rmrl.in/bulletin/bulletin-No-6-June-2025.pdf"),
    ("nair_2026_baselines", "2026-04-20", "unreviewed preprint", "https://arxiv.org/html/2604.17828v1"),
    ("raghavendra_2026_specificity", "2026-08-04", "unreviewed preprint", "https://arxiv.org/html/2608.02999v1"),
    ("bourdeau_2026_tests", "2026-09-25", "unreviewed independent project page", "https://dbourdeau.github.io/cyphersolver/indus.html"),
    ("parpola_1980_duplicates", "1980", "published author paper", "https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf"),
    ("parpola_2008_copper", "2008", "published edited-volume chapter", "https://tuhat.helsinki.fi/ws/portalfiles/portal/127257447/Parpola_A_2008._Copper_tablets_from_Mohenjo_daro._ECL_During_Caspers_Vol.pdf"),
    ("parpola_2005_study", "2005", "published symposium paper", "https://www.harappa.com/sites/default/files/pdf/indusscript%282%29.pdf"),
    ("kenoyer_2006_context", "2006", "published edited-volume chapter", "https://www.harappa.com/sites/default/files/pdf/Kenoyer2006_The%20Origin%2C%20Context%20and%20Function%20of%20the%20Indus%20Sc.pdf"),
    ("parpola_1986_deciphering", "1986", "author research essay", "https://www.harappa.com/script/parpola15.html"),
    ("joshi_parpola_1987_cisi1", "1987", "primary object corpus; government-hosted scan", "https://ignca.gov.in/Asi_data/76884.pdf"),
    ("farmer_sproat_witzel_2004", "2004", "peer-reviewed journal essay", "https://hasp.ub.uni-heidelberg.de/journals/ejvs/article/download/620/612/1254"),
    ("daggumati_revesz_2021_allographs", "2021", "peer-reviewed paper", "https://www.nature.com/articles/s41599-021-00713-0.pdf"),
]

def retrieve(item):
    key, publication, status, url = item
    record = {"id": key, "publication": publication, "status": status, "url": url,
              "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        response = requests.get(url, timeout=90, headers={"User-Agent": "IndusLiteratureResearch/1.0"})
        record["http_status"] = response.status_code
        response.raise_for_status()
        raw = response.content
        is_pdf = raw[:4] == b"%PDF"
        suffix = ".pdf" if is_pdf else ".html"
        raw_path = ROOT / "sources" / (key + suffix)
        raw_path.parent.mkdir(exist_ok=True)
        raw_path.write_bytes(raw)
        record["raw_file"] = str(raw_path.relative_to(ROOT))
        record["sha256"] = hashlib.sha256(raw).hexdigest()
        if is_pdf:
            reader = PdfReader(raw_path)
            record["pages"] = len(reader.pages)
            text = "\n\n".join(f"[PAGE {i+1}]\n{page.extract_text() or ''}" for i, page in enumerate(reader.pages))
        else:
            soup = BeautifulSoup(raw, "html.parser")
            for node in soup(["script", "style"]):
                node.decompose()
            text = soup.get_text("\n", strip=True)
        text_path = ROOT / "sources" / (key + ".txt")
        text_path.write_text(text, encoding="utf-8")
        record["text_file"] = str(text_path.relative_to(ROOT))
        record["text_chars"] = len(text)
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        records = list(executor.map(retrieve, SOURCES))
    (ROOT / "source_retrieval_log.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    for record in records:
        print(record["id"], record.get("http_status"), record.get("pages", "html"), record.get("text_chars", record.get("error")))
