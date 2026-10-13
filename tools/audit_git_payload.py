"""Inspect the selected private Git payload without printing credential values."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    selected = subprocess.run(["git","ls-files","--cached","--others","--exclude-standard"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    selected = sorted(set(selected))
    known_tokens = re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{35,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
    suspect = []
    sizes = []
    for name in selected:
        path = ROOT/name
        if not path.is_file():
            continue
        payload = path.read_bytes()
        if known_tokens.search(payload):
            suspect.append(name)
        sizes.append((len(payload),name))
    forbidden = [name for name in selected if name.startswith("data/") and name not in ("data/README.md", "data/MANIFEST.json") or name.startswith(".github/workflows/") or name.startswith("research/literature/sources/") or name.startswith("research/literature/primary/") or name.startswith("research/literature/nonlinguistic_controls/") and name.endswith(".jsonl") or name.startswith("experiments/2026-10-02-six-hour/markov-") and name.endswith(".jsonl")]
    staged = subprocess.run(["git","ls-files","--stage"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    byte_mismatches = []
    for entry in staged:
        metadata,name = entry.split("\t",1)
        expected = metadata.split()[1]
        payload = (ROOT/name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        if actual != expected:
            byte_mismatches.append(name)
    result = {"status":"pass" if not suspect and not forbidden else "review-required", "selected_files":len(selected),
              "selected_bytes":sum(s for s,_ in sizes), "known_credential_pattern_paths":suspect,"excluded_source_violations":forbidden,
              "staged_files_byte_checked":len(staged),"index_working_copy_byte_differences":byte_mismatches,
              "largest_files":[{"path":p,"bytes":s} for s,p in sorted(sizes,reverse=True)[:12]],
              "scope":"Known credential patterns, selected sizes and declared local-only source paths; not a complete rights or secret audit."}
    (ROOT/"knowledge/provenance/git-payload-review.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if suspect or forbidden:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
