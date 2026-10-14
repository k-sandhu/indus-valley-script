"""Assemble each pass's block files for comparison: apply tail readings and join split entries.

Usage (from the repository root):
  python experiments/2026-10-13-cisi-basic-data-full/assemble_passes.py [--volume cisi1|cisi2]

The readers' files in data/raw/2026-10-13-cisi-basic-data-full/pass1/ and pass2/ are never
changed. This script writes assembled copies to data/raw/2026-10-13-cisi-basic-data-full/
assembled/pass1/ and assembled/pass2/, which the pipeline then reads with --raw. Two rules, the
same for both passes:

1. Tails (AMENDMENT-1.md). When <block>.tail.<pass>.txt exists, the block's entries from the first
   CISI number that the tail also contains onward are replaced by the tail's entries. If the main
   file lacks that number, the tail's entries are appended and any main entries with the same
   numbers are dropped. The CISI 2 corrigenda tail replaces the main corrigenda from the line that
   best matches its first line.
2. Entries split across a block boundary. A reader marks the fragment at the head of the next block
   with an empty CISI cell and a "# continued" comment. The fragment's non-empty cells are appended,
   with a space, to the same columns of the last entry of the preceding block in the same volume,
   and removed from the later block.
3. A CISI number that a reader bracketed (for example a final digit read as [2/3]) is set, in the
   assembled copy only, to the candidate that continues the numbering of the neighbouring entries
   of the same site, when exactly one candidate does; the reading as written is kept in a comment
   line. The number is an identifier that the printed order fixes, so this is not a reading of the
   page. A site prefix with a bracketed letter is set to the reader's first candidate in the same
   way. Unresolved cases are logged and left for the coordinator.

Every change is listed in assembled/assembly-log.json (CISI numbers and actions, no values).
"""
import argparse
import difflib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data/raw/2026-10-13-cisi-basic-data-full"
OUT = RAW / "assembled"
KEY = re.compile(r"^\s*([A-Za-z?]+(?:[-.]|\[[-./]+\])\s*\d+[A-Za-z]?)")


def key_of(line):
    first = line.split(" | ")[0].replace("{", "").replace("}", "")
    m = KEY.match(first)
    return re.sub(r"\[[-./]+\]", "-", re.sub(r"\s+", "", m[1])).replace(".", "-") if m else None


def is_entry(line):
    return line.strip() and not line.lstrip().startswith("#") and " | " in line


def read(path):
    return path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else None


def apply_tail(main, tail, log, block, p):
    tail_entries = [l for l in tail if is_entry(l)]
    tail_keys = [key_of(l) for l in tail_entries if key_of(l)]
    keep_comments = [l for l in tail if l.lstrip().startswith("#") and not re.match(r"#\s*(pass|started|finished)", l.lstrip(), re.I)]
    if not tail_keys:
        log.append({"block": block, "pass": p, "action": "tail-empty"})
        return main
    first = tail_keys[0]
    main_idx = [i for i, l in enumerate(main) if is_entry(l)]
    # t01 repeats the main reader's last strip, so the tail's first entry must be one of the main
    # file's last few entries. A tail reading of that entry's CISI number that matches an entry
    # further up (a misread digit) would otherwise discard the rest of the block: in that case
    # the tail's first entry is taken to be the main file's last entry, whose number stands.
    recent = [i for i in main_idx[-4:]]
    cut = next((i for i in recent if key_of(main[i]) == first), None)
    if cut is None and main_idx:
        # the main file's last line may be the cut-off line itself, with an unreadable site prefix
        last_col1 = main[main_idx[-1]].split(" | ")[0]
        mnum = re.search(r"-\s*(\d+)\s*$", last_col1.strip())
        last_key = key_of(main[main_idx[-1]])
        if (last_key is None or "?" in last_key) and mnum and first.split("-")[-1] == mnum[1]:
            cut = main_idx[-1]
            log.append({"block": block, "pass": p, "action": "tail-replaces-unreadable-last-entry", "first_tail_cisi": first})
    if cut is None and any(key_of(main[i]) == first for i in main_idx[:-4]) and main_idx:
        last = main_idx[-1]
        first_tail = next(i for i, l in enumerate(tail) if is_entry(l) and key_of(l))
        old = tail[first_tail].split(" | ")
        tail = list(tail)
        tail[first_tail] = " | ".join([key_of(main[last])] + old[1:])
        tail.insert(first_tail, f"# col1 as read in the tail: {old[0].strip()}; number set to the main file's last entry")
        tail_entries = [l for l in tail if is_entry(l)]
        tail_keys = [key_of(l) for l in tail_entries if key_of(l)]
        keep_comments = [l for l in tail if l.lstrip().startswith("#") and not re.match(r"#\s*(pass|started|finished)", l.lstrip(), re.I)]
        log.append({"block": block, "pass": p, "action": "tail-number-out-of-place", "tail_read": old[0].strip(),
                    "set_to": key_of(main[last])})
        first, cut = key_of(main[last]), last
    finished = [l for l in main if re.match(r"#\s*finished", l.lstrip(), re.I)]
    if cut is None:
        drop = set(tail_keys)
        body = [l for l in main if not (is_entry(l) and key_of(l) in drop) and l not in finished]
        log.append({"block": block, "pass": p, "action": "tail-appended", "first_tail_cisi": first,
                    "tail_entries": len(tail_entries)})
    else:
        body = main[:cut]
        log.append({"block": block, "pass": p, "action": "tail-replaced-from", "first_tail_cisi": first,
                    "main_entries_replaced": sum(1 for l in main[cut:] if is_entry(l)), "tail_entries": len(tail_entries)})
    return body + [f"# tail: entries below from {block}.tail.{p}.txt (AMENDMENT-1.md)"] + keep_comments + tail_entries + finished


def apply_corrigenda_tail(main, tail, log, p):
    lines = [l for l in tail if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        return main
    body_idx = [i for i, l in enumerate(main) if l.strip() and not l.lstrip().startswith("#")]
    best, score = None, 0.0
    for i in body_idx:
        r = difflib.SequenceMatcher(None, main[i].strip(), lines[0].strip()).ratio()
        if r > score:
            best, score = i, r
    finished = [l for l in main if re.match(r"#\s*finished", l.lstrip(), re.I)]
    if best is not None and score >= 0.6:
        head = main[:best]
        log.append({"block": "cisi2-corrigenda", "pass": p, "action": "tail-replaced-from-line",
                    "main_line": best + 1, "match_ratio": round(score, 3), "tail_lines": len(lines)})
    else:
        head = [l for l in main if l not in finished]
        log.append({"block": "cisi2-corrigenda", "pass": p, "action": "tail-appended", "match_ratio": round(score, 3),
                    "tail_lines": len(lines)})
    return head + [f"# tail: lines below from cisi2-corrigenda-tail.{p}.txt (AMENDMENT-1.md)"] + lines + finished


def join_continuations(files, order, log, p):
    """files: block -> list of lines (modified in place)."""
    for prev, cur in zip(order, order[1:]):
        lines = files.get(cur)
        if not lines or prev not in files:
            continue
        plines = files[prev]
        j = max((k for k, x in enumerate(plines) if is_entry(x)), default=None)
        if j is None:
            continue
        prev_key = key_of(plines[j])
        for i, l in enumerate(lines):
            if is_entry(l):
                nxt = next((x for x in lines[i + 1:] if x.strip()), "")
                marked = re.match(r"#\s*continued\b", nxt.lstrip(), re.I) is not None
                # a fragment at the head of the block: no CISI number, or the preceding block's
                # last number followed by a "# continued" comment
                if key_of(l) and not (marked and key_of(l) == prev_key):
                    break
                frag = [c.strip() for c in l.split(" | ")]
                frag += [""] * (5 - len(frag))
                cells = [c.strip() for c in plines[j].split(" | ")]
                cells += [""] * (5 - len(cells))
                for c in range(1, 5):
                    if frag[c]:
                        cells[c] = (cells[c] + " " + frag[c]).strip()
                plines[j] = " | ".join(cells)
                lines[i] = f"# continuation moved to the last entry of {prev}"
                log.append({"block": cur, "pass": p, "action": "continuation-joined", "into_block": prev,
                            "into_cisi": key_of(plines[j]), "columns": [c + 1 for c in range(1, 5) if frag[c]]})
                continue


NUMBER = re.compile(r"^(\s*\{?)([A-Za-z?]+)([-.]\s*)((?:\d|\[[^\]]*\])+)(.*)$")


def expand(text):
    parts = re.split(r"(\[[^\]]*\])", text)
    out = [""]
    for part in parts:
        if part.startswith("["):
            if "?" in part:
                return []
            out = [o + c for o in out for c in part[1:-1].split("/")]
        else:
            out = [o + part for o in out]
    return [o for o in out if o.isdigit()]


def resolve_bracketed_numbers(lines, log, block, p):
    """Give an entry whose CISI number a reader bracketed the candidate that fits the sequence."""
    entries = [i for i, l in enumerate(lines) if is_entry(l)]
    for i in entries:
        col1 = lines[i].split(" | ")[0]
        pm = re.match(r"^(\s*\{?)((?:[A-Za-z?]|\[[A-Za-z]+(?:/[A-Za-z]+)+\]|\[\?+\])+)([-.].*)$", col1)
        if pm and "[" in pm[2]:
            prefix = re.sub(r"\[([A-Za-z]+)(?:/[A-Za-z]+)+\]", lambda x: x[1], pm[2])
            prefix = re.sub(r"\[(\?+)\]", lambda x: x[1], prefix)
            lines[i] = " | ".join([pm[1] + prefix + pm[3]] + lines[i].split(" | ")[1:])
            lines[i] = lines[i] + "\n" + f"# col1 as read: {col1.strip()}; site prefix set to the reader's first candidate"
            log.append({"block": block, "pass": p, "action": "site-prefix-first-candidate", "prefix": prefix})
    lines[:] = [x for l in lines for x in l.split("\n")]
    entries = [i for i, l in enumerate(lines) if is_entry(l)]
    for n, i in enumerate(entries):
        col1 = lines[i].split(" | ")[0]
        m = NUMBER.match(col1)
        if not m or "[" not in m[4]:
            continue
        cands = expand(m[4])
        neigh = []
        for k in (n - 1, n + 1):
            if 0 <= k < len(entries):
                nk = key_of(lines[entries[k]])
                if nk and nk.split("-")[0] == m[2]:
                    neigh.append((k - n, int(re.sub(r"\D", "", nk.split("-", 1)[1]) or 0)))
        fit = [c for c in cands if any(int(c) == v - d for d, v in neigh)]
        if len(set(fit)) == 1:
            new = m[1] + m[2] + m[3] + fit[0] + m[5]
            lines[i] = " | ".join([new] + lines[i].split(" | ")[1:])
            lines.insert(i, f"# col1 as read: {col1.strip()}; number set by sequence")
            entries = [e + 1 if e >= i else e for e in entries]
            log.append({"block": block, "pass": p, "action": "cisi-number-by-sequence", "cisi": f"{m[2]}-{fit[0]}"})
        elif cands:
            # The neighbours do not decide it: align on the reader's first candidate, so that a
            # different reading in the other pass surfaces as a row decision for the adjudicator.
            new = m[1] + m[2] + m[3] + cands[0] + m[5]
            lines[i] = " | ".join([new] + lines[i].split(" | ")[1:])
            lines.insert(i, f"# col1 as read: {col1.strip()}; number set to the reader's first candidate")
            entries = [e + 1 if e >= i else e for e in entries]
            log.append({"block": block, "pass": p, "action": "cisi-number-first-candidate", "cisi": f"{m[2]}-{cands[0]}"})
        else:
            log.append({"block": block, "pass": p, "action": "cisi-number-unresolved", "candidates": len(cands)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume", choices=["cisi1", "cisi2"], action="append")
    args = ap.parse_args()
    volumes = args.volume or ["cisi1", "cisi2"]
    specs = json.loads((HERE / "blocks.json").read_text(encoding="utf-8"))
    log, missing = [], []
    for p in ("pass1", "pass2"):
        (OUT / p).mkdir(parents=True, exist_ok=True)
        for v in volumes:
            order = [s["block"] for s in specs if s["volume"] == v and s["block"] != "cisi2-p435-M595"]
            files = {}
            for b in order + (["cisi2-p435-M595"] if v == "cisi2" else []):
                main_lines = read(RAW / p / f"{b}.{p}.txt")
                if main_lines is None:
                    missing.append(f"{p}/{b}")
                    continue
                main_lines = list(main_lines)
                resolve_bracketed_numbers(main_lines, log, b, p)
                tail = read(RAW / p / f"{b}.tail.{p}.txt")
                if tail:
                    tail = list(tail)
                    resolve_bracketed_numbers(tail, log, b + " tail", p)
                files[b] = apply_tail(main_lines, tail, log, b, p) if tail else main_lines
            join_continuations(files, order, log, p)
            for b, lines in files.items():
                (OUT / p / f"{b}.{p}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            corr = read(RAW / p / f"{v}-corrigenda.{p}.txt")
            if corr is not None:
                # The section heading is not a corrigendum; one reader wrote it as a line, the other as a comment.
                corr = [f"# heading: {l.strip()}" if re.fullmatch(r"\s*corrigenda\.?\s*", l, re.I) else l for l in corr]
            if corr is None:
                missing.append(f"{p}/{v}-corrigenda")
            else:
                ctail = read(RAW / p / f"{v}-corrigenda-tail.{p}.txt")
                corr = apply_corrigenda_tail(corr, ctail, log, p) if ctail else corr
                (OUT / p / f"{v}-corrigenda.{p}.txt").write_text("\n".join(corr) + "\n", encoding="utf-8")
    (OUT / "assembly-log.json").write_text(json.dumps({"volumes": volumes, "missing": missing, "log": log}, indent=1),
                                           encoding="utf-8")
    print(json.dumps({"missing": missing, "actions": len(log)}, indent=1))
    for r in log:
        print(r)


if __name__ == "__main__":
    main()
