"""Bind dictionary rows to exact original headwords, not substring occurrences."""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/2026-10-22-rebus-winslow/code"))
import parse_winslow as winslow  # noqa: E402


def plain(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def exact_winslow_blocks(text, entry):
    result = []
    for match in re.finditer(r"<div>\s*(.*?)</div>", text, re.S):
        block = match.group(1)
        if "<hw>" not in block:
            continue
        principals, subs = winslow.parse_page("<div>" + block + "</div>", entry["page"])
        if entry["kind"] == "principal":
            if not any((entry["head"], entry["translit_plain"]) in principal["forms"]
                       and principal["gloss"] == entry["gloss"] for principal in principals):
                continue
            body = block.split("<p2>", 1)[0]
        else:
            if not any(entry["head"] in sub["heads"] and sub["gloss"] == entry["gloss"]
                       and entry.get("root") in [pair[1] for pair in sub["root_forms"]] for sub in subs):
                continue
            chosen = []
            for submatch in re.finditer(r"<p2>(.*?)</p2>", block, re.S):
                start = re.match(r"\s*\*?\s*((?:<tam>[^<]*</tam>\s*[–-]?\s*)+)", submatch.group(1))
                heads = re.findall(r"<tam>([^<]*)</tam>", start.group(1)) if start else []
                if entry["head"] in heads:
                    chosen.append(submatch.group(0))
            body = block.split("<p2>", 1)[0] + "\n" + "\n".join(chosen)
        result.append({"character_span": list(match.span()), "raw_html": body, "text": plain(body)})
    return result
