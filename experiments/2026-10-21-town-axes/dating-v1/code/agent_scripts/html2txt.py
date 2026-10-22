"""Print visible paragraph text of a saved HTML page."""
import html
import re
import sys

raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
parts = re.findall(r"(?is)<(p|h1|h2|h3|li|td|figcaption|blockquote)[^>]*>(.*?)</\1>", raw)
for tag, body in parts:
    t = html.unescape(re.sub(r"(?s)<[^>]+>", "", body))
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 30:
        print("[%s] %s" % (tag, t))
