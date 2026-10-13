#!/usr/bin/env python3
"""List, fetch and verify the data sources recorded in data/MANIFEST.json.

Standard library only. Run from any directory; paths resolve from the
repository root.

    python tools/fetch_data.py --list [--status held|partly-held|not-held|project-output]
    python tools/fetch_data.py --show <id>
    python tools/fetch_data.py --fetch <id> [--dest DIR] [--dry-run]
    python tools/fetch_data.py --verify <id>

--fetch acquires a source that has a public pinned location (a git commit or
an HTTP file with a recorded SHA256) into a new directory, by default
data/raw/<today>-fetch/<id>/. It never writes into an existing directory or
over an existing file, and it never touches the canonical local copy named in
the manifest. For sources without a public pinned location it prints the
acquisition steps. --verify hashes the canonical local copy, read-only.

Fetched third-party material is local-only: data/ is ignored by Git. Check
knowledge/provenance/REDISTRIBUTION.md before tracking anything derived from it.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import textwrap
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "MANIFEST.json"
USER_AGENT = "indus-research-fetch/1 (+https://github.com/k-sandhu/indus-valley-script)"


def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as fh:
        return json.load(fh)


def find(manifest: dict, source_id: str) -> dict:
    for src in manifest["sources"]:
        if src["id"] == source_id:
            return src
    sys.exit(f"unknown source id {source_id!r}; run --list")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_list(manifest: dict, status: str | None) -> None:
    rows = [s for s in manifest["sources"] if not status or s["status"] == status]
    width = max(len(s["id"]) for s in rows) if rows else 10
    print(f"{'id':<{width}}  {'status':<14} {'location':<22} {'fetch':<8} title")
    for s in rows:
        method = s.get("fetch", {}).get("method", "-")
        title = s["title"] if len(s["title"]) <= 70 else s["title"][:67] + "..."
        print(f"{s['id']:<{width}}  {s['status']:<14} {s.get('location', '-'):<22} {method:<8} {title}")
    counts = {}
    for s in manifest["sources"]:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    print(f"\n{len(rows)} shown; manifest totals: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


def cmd_show(src: dict) -> None:
    print(json.dumps(src, indent=2, ensure_ascii=False))


def print_steps(src: dict) -> None:
    fetch = src.get("fetch", {})
    print(f"{src['id']}: {src['title']}")
    print(f"status: {src['status']}; fetch method: {fetch.get('method', '-')}")
    steps = fetch.get("steps") or []
    if not steps:
        print("No acquisition steps are recorded; see knowledge/DATA.md.")
    for i, step in enumerate(steps, 1):
        print(textwrap.fill(f"{i}. {step}", width=100, subsequent_indent="   "))
    rights = src.get("rights", {})
    if rights:
        print(f"rights: {rights.get('status', '-')}; {rights.get('licence') or ''} {rights.get('detail') or ''}".rstrip())


def default_dest(src_id: str) -> pathlib.Path:
    today = _dt.date.today().isoformat()
    return ROOT / "data" / "raw" / f"{today}-fetch" / src_id


def verify_files(base: pathlib.Path, expected: dict) -> bool:
    ok = True
    for rel, digest in expected.items():
        path = base / rel
        if not path.exists():
            print(f"  MISSING {rel}")
            ok = False
            continue
        actual = sha256(path)
        status = "ok" if actual == digest else "MISMATCH"
        ok = ok and actual == digest
        print(f"  {status:8} {rel} {actual}")
    return ok


def fetch_git(src: dict, dest: pathlib.Path, dry_run: bool) -> int:
    fetch = src["fetch"]
    url, commit = fetch["url"], fetch["commit"]
    if dry_run:
        print(f"[dry run] git clone --no-checkout {url} {dest}")
        print(f"[dry run] git -C {dest} checkout --detach {commit}")
        for rel in fetch.get("verify", {}):
            print(f"[dry run] verify sha256 of {rel}")
        return 0
    if shutil.which("git") is None:
        sys.exit("git is required for this source")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--no-checkout", url, str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "--detach", commit], check=True)
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()
    print(f"checked out {head}")
    ok = head == commit and verify_files(dest, fetch.get("verify", {}))
    print("verification passed" if ok else "VERIFICATION FAILED: keep the copy for inspection; do not use it as the pinned input")
    return 0 if ok else 1


def fetch_http(src: dict, dest: pathlib.Path, dry_run: bool) -> int:
    fetch = src["fetch"]
    target = dest / fetch["filename"]
    if dry_run:
        print(f"[dry run] GET {fetch['url']}")
        print(f"[dry run] write {target}")
        if fetch.get("sha256"):
            print(f"[dry run] expect sha256 {fetch['sha256']} ({fetch.get('bytes', '?')} bytes)")
        return 0
    dest.mkdir(parents=True)
    request = urllib.request.Request(fetch["url"], headers={"User-Agent": USER_AGENT})
    h = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=120) as resp, target.open("xb") as out:
        for chunk in iter(lambda: resp.read(1 << 20), b""):
            out.write(chunk)
            h.update(chunk)
            size += len(chunk)
    record = {
        "source_id": src["id"],
        "url": fetch["url"],
        "retrieved_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "bytes": size,
        "sha256": h.hexdigest(),
        "expected_sha256": fetch.get("sha256"),
    }
    (dest / "acquisition.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    if fetch.get("sha256") and record["sha256"] != fetch["sha256"]:
        print("HASH MISMATCH: the server returned a different file; it is kept for inspection only")
        print(json.dumps(record, indent=2))
        return 1
    print(json.dumps(record, indent=2))
    return 0


def cmd_fetch(src: dict, dest_arg: str | None, dry_run: bool) -> int:
    method = src.get("fetch", {}).get("method")
    if method not in ("git", "http"):
        print_steps(src)
        return 0
    dest = pathlib.Path(dest_arg).resolve() if dest_arg else default_dest(src["id"])
    if dest.exists():
        sys.exit(f"refusing to write into existing path {dest}; choose a new --dest")
    for local in src.get("local_paths", []):
        if (ROOT / local).exists():
            print(f"note: a local copy already exists at {local}; it is left unchanged")
    rights = src.get("rights", {})
    print(f"rights: {rights.get('status', '-')}; copies stay local-only under data/")
    if method == "git":
        return fetch_git(src, dest, dry_run)
    return fetch_http(src, dest, dry_run)


def cmd_verify(src: dict) -> int:
    hashes = src.get("hashes") or {}
    if not hashes:
        print("No hashes are recorded for this source.")
        return 0
    print(f"verifying canonical local copy of {src['id']} (read-only)")
    return 0 if verify_files(ROOT, hashes) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="List, fetch and verify sources in data/MANIFEST.json.")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="print the manifest as a table")
    group.add_argument("--show", metavar="ID", help="print one manifest record")
    group.add_argument("--fetch", metavar="ID", help="acquire a source into a new directory, or print its steps")
    group.add_argument("--verify", metavar="ID", help="hash the canonical local copy against the manifest")
    ap.add_argument("--status", help="filter --list by status")
    ap.add_argument("--dest", help="new destination directory for --fetch")
    ap.add_argument("--dry-run", action="store_true", help="with --fetch, print the actions without network access")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    manifest = load_manifest()
    if args.list:
        cmd_list(manifest, args.status)
        return 0
    if args.show:
        cmd_show(find(manifest, args.show))
        return 0
    if args.fetch:
        return cmd_fetch(find(manifest, args.fetch), args.dest, args.dry_run)
    return cmd_verify(find(manifest, args.verify))


if __name__ == "__main__":
    raise SystemExit(main())
