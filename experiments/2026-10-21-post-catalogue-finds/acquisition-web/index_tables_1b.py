"""Read publication-index rows as bibliographic data."""
import json
import sys
import urllib.request
from html.parser import HTMLParser

class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.row = None
        self.rows = []
    def handle_starttag(self,tag,attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.row = {"text":[], "links":[]}
        if tag == "a" and self.row is not None and attrs.get("href"):
            self.row["links"].append(attrs["href"])
    def handle_data(self,data):
        if self.row is not None and data.strip():
            self.row["text"].append(data.strip())
    def handle_endtag(self,tag):
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

for url in sys.argv[1:]:
    try:
        with urllib.request.urlopen(url,timeout=35) as response:
            data = response.read().decode("utf-8",errors="replace")
        parser = Tables()
        parser.feed(data)
        print(json.dumps({"url":url,"rows":parser.rows},ensure_ascii=True))
    except Exception as exc:
        print(json.dumps({"url":url,"error":str(exc)}))
