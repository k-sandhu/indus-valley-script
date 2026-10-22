"""Inspect bibliographic front matter and public indexes without saving page text."""
import argparse
import json
import re
import subprocess
import urllib.parse
import urllib.request
from html.parser import HTMLParser

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["pdf-front", "links", "ia-search", "ia-files"])
ap.add_argument("target")
ap.add_argument("--pages", default="1")
ap.add_argument("--lines", type=int, default=6)
args = ap.parse_args()
if args.mode == "pdf-front":
    for page in args.pages.split(","):
        result = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", page, "-l", page, args.target, "-"], capture_output=True, timeout=45)
        lines = [s.strip() for s in result.stdout.decode("utf-8", errors="replace").splitlines() if s.strip()]
        print(json.dumps({"page":page,"front_lines":lines[:args.lines]},ensure_ascii=True))
elif args.mode == "links":
    req = urllib.request.Request(args.target, headers={"User-Agent":"IndusResearchBibliography/1.0"})
    with urllib.request.urlopen(req, timeout=35) as response:
        data = response.read().decode("utf-8", errors="replace")
        final = response.url
    parser = Links()
    parser.feed(data)
    print(json.dumps({"final_url":final,"links":[urllib.parse.urljoin(final,link) for link in parser.links if re.search(r"pdf|download|review|archaeology|article|publication|report",link,re.I)]},ensure_ascii=True))
elif args.mode == "ia-search":
    url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q":args.target,"output":"json","rows":50,"fl[]":["identifier","title"]},doseq=True)
    with urllib.request.urlopen(url, timeout=40) as response:
        data = json.load(response)
    print(json.dumps(data.get("response",{}),ensure_ascii=True))
else:
    url = "https://archive.org/metadata/" + urllib.parse.quote(args.target)
    with urllib.request.urlopen(url,timeout=40) as response:
        data = json.load(response)
    print(json.dumps({"identifier":args.target,"title":data.get("metadata",{}).get("title"),"files":[{k:f.get(k) for k in ["name","size","md5","sha1","format"]} for f in data.get("files",[]) if f.get("name","").endswith(".pdf")],"rights":data.get("metadata",{}).get("rights"),"licenseurl":data.get("metadata",{}).get("licenseurl")},ensure_ascii=True))
