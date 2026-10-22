"""List PDF pages whose text mentions a keyword together with a plan or figure word.

Lines mentioning orientation figures (orient, degree, the degree sign) are
suppressed so that stated orientations are not displayed.
Usage: findpages.py <pdf> <keyword> [--any] [--max 80]
"""
import sys
sys.dont_write_bytecode = True
import argparse
import re
import warnings
warnings.filterwarnings("ignore")
import fitz

SUPPRESS = re.compile(r"orient|degree|°|\bdeg\b|azimuth|bearing", re.I)
PLANWORD = re.compile(r"\bplan\b|\bfig|\bpl\.|plate|layout|contour|map", re.I)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pdf")
    p.add_argument("keyword")
    p.add_argument("--any", action="store_true", help="list every page mentioning the keyword")
    p.add_argument("--max", type=int, default=80)
    a = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    kw = re.compile(a.keyword, re.I)
    shown = 0
    with fitz.open(a.pdf) as d:
        print("pages", d.page_count)
        for i in range(d.page_count):
            t = d[i].get_text()
            if not kw.search(t):
                continue
            lines = [l.strip() for l in t.splitlines() if l.strip() and not SUPPRESS.search(l)]
            hits = [l for l in lines if PLANWORD.search(l) and (kw.search(l) or a.any)]
            if hits or a.any:
                print(f"p{i+1}:", " | ".join(h[:110] for h in hits[:4]))
                shown += 1
                if shown >= a.max:
                    break


if __name__ == "__main__":
    main()
