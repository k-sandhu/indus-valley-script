"""Render the two original source reviews into a local, readable research page."""

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

import markdown

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]


def render_report(path):
    rendered = markdown.markdown(path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
    # Shift report headings under the page title without altering their text.
    rendered = re.sub(r"<(\/?)(h[1-5])([ >])", lambda m: f"<{m[1]}h{int(m[2][1])+1}{m[3]}", rendered)

    def rewrite(match):
        href = html.unescape(match[1])
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or href.startswith("#"):
            return match[0]
        target = (path.parent / parts.path).resolve()
        url = os.path.relpath(target, PACKAGE).replace("\\", "/")
        if parts.fragment:
            url += "#" + parts.fragment
        return 'href="' + html.escape(url, quote=True) + '"'

    return re.sub(r'href="([^"]+)"', rewrite, rendered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    out = (PACKAGE / args.run).resolve()
    if not out.is_relative_to(PACKAGE) or out.exists():
        raise ValueError("Choose a new reader endpoint in this package.")
    reports = [("continuity", "Changing markers", PACKAGE / "continuity/REPORT.md"), ("living-towns", "Living towns", PACKAGE / "living-towns/REPORT.md")]
    for _, _, path in reports:
        if not path.exists():
            raise FileNotFoundError(f"The review is incomplete: {path.name}")
    style = """
    :root{color-scheme:light;--ink:#163e40;--paper:#f6f5ed;--line:#dce1d5}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.85 'Segoe UI',Arial,sans-serif}a{color:#27695d;text-underline-offset:3px}header{position:sticky;top:0;z-index:9;background:#143d40;color:#f0f2e6;display:flex;align-items:center;justify-content:space-between;padding:17px 5vw;gap:20px}header a{color:inherit;text-decoration:none;font-size:13px}header .brand{font-size:17px;letter-spacing:3px}header nav{display:flex;gap:25px}.intro{max-width:900px;margin:60px auto 40px;padding:0 30px}.eyebrow{letter-spacing:2px;font-size:10px;color:#788979}h1{font:48px/1.13 Georgia,serif;font-weight:400;max-width:740px;letter-spacing:-1px;margin:17px 0 22px}.intro p{color:#617666;max-width:740px}.quicklinks{display:flex;gap:12px;flex-wrap:wrap;margin-top:25px}.quicklinks a{font-size:12px;padding:9px 14px;border:1px solid #cbd6c7;border-radius:3px;text-decoration:none}article{max-width:1000px;margin:35px auto;padding:38px 48px 50px;background:#fcfcf7;border:1px solid var(--line);border-radius:5px;scroll-margin-top:90px}article>.eyebrow{display:block;margin-bottom:20px}h2{font:34px/1.25 Georgia,serif;font-weight:400;margin:15px 0 30px}h3{font:27px/1.3 Georgia,serif;font-weight:400;margin:40px 0 14px}h4{font-size:17px;margin:30px 0 10px}p,li{max-width:830px}table{border-collapse:collapse;font-size:12px;width:100%;display:block;overflow:auto;margin:22px 0}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line);min-width:110px;line-height:1.7}th{font-size:11px;color:#5e7361}code{font-size:.87em;background:#edf0e7;border-radius:3px;padding:2px 4px;overflow-wrap:anywhere}pre{background:#edf0e7;padding:15px;overflow:auto;border-radius:4px}pre code{padding:0}blockquote{border-left:3px solid #b9915d;margin:20px 0;padding:0 20px;color:#627867}.report-link{font-size:12px;color:#6b806c}footer{max-width:900px;margin:35px auto 50px;padding:0 30px;font-size:12px;color:#6b7d6b}a:focus-visible{outline:3px solid #c28b4f;outline-offset:4px}@media(max-width:650px){body{font-size:13px}header{padding:15px 18px;gap:12px;align-items:flex-start}header .brand{font-size:13px;white-space:nowrap}header nav{gap:10px;flex-wrap:wrap;justify-content:flex-end}header nav a{font-size:10px}.intro{margin:35px auto 27px;padding:0 22px}h1{font-size:35px}article{padding:26px 22px;margin:20px 12px}h2{font-size:29px}h3{font-size:24px}table{font-size:11px}td,th{padding:10px 8px;min-width:100px}.quicklinks a{font-size:11px}}@media print{header,.quicklinks{display:none}article{border:0;max-width:100%;padding:0;break-before:page}body{font-size:11px}table{display:table;font-size:9px}h1{font-size:32px}h2{font-size:27px}a{color:inherit}}
    """
    sections = "\n".join(f'<article id="{ident}"><span class="eyebrow">{label.upper()} · SOURCE REVIEW</span>{render_report(path)}<p class="report-link"><a href="{path.relative_to(PACKAGE).as_posix()}">Original Markdown and evidence links ↗</a></p></article>' for ident,label,path in reports)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Indus Atlas · Continuity and living towns</title><link rel="icon" href="data:,"><style>{style}</style></head><body><header><a class="brand" href="index.html">INDUS ATLAS</a><nav><a href="index.html">The map</a><a href="reconstruction/index.html">Cities in 3D ↗</a><a href="#continuity">Changing markers</a><a href="#living-towns">Living towns</a></nav></header><main><div class="intro"><span class="eyebrow">CITIES AND THEIR AFTERLIVES</span><h1>What persisted when the urban world changed?</h1><p>We examine the evidence for changes in recognizable Harappan material, and the excavated sequences beneath places inhabited today. Each review preserves its observations, sources and the tests that could decide the remaining questions.</p><div class="quicklinks"><a href="#continuity">Read the marker-continuity study ↓</a><a href="#living-towns">Compare the town evidence ↓</a><a href="index.html#layer=towns">See the town anchors on the map ↗</a></div></div>{sections}</main><footer>Original project prose is dedicated to CC0. Linked third-party sources retain their own terms. This local page is a rendering of the two source reviews; their JSON records preserve the observation-level evidence.</footer></body></html>'''
    out.mkdir(parents=True)
    (out / "build_reader.snapshot.py").write_bytes(Path(__file__).read_bytes())
    target = out / "research.html"
    target.write_text(page, encoding="utf-8")
    paths = [path for _,_,path in reports] + [Path(__file__)]
    manifest = {"schema_version":"1.0", "inputs":[{"path": p.relative_to(ROOT).as_posix(), "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths], "output":{"path": target.relative_to(PACKAGE).as_posix(), "sha256":hashlib.sha256(target.read_bytes()).hexdigest()}, "markdown_version":markdown.__version__, "transformation":"Render original Markdown, shift headings, resolve relative evidence links; original report wording retained."}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output":target.relative_to(PACKAGE).as_posix(),"bytes":target.stat().st_size}))


if __name__ == "__main__":
    main()
