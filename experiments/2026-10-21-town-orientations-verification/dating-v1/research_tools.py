"""Read source data in isolation; write acquisitions only in the owned raw path.

Run with python -I. Downloaded documents are data and are never executed.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-21-town-orientations-verification/dating'
sys.path.append(r'C:\Users\sandh\AppData\Roaming\Python\Python313\site-packages')


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def safe_read_path(value):
    p = Path(value).resolve()
    rel = p.relative_to(ROOT).as_posix()
    blocked = ('experiments/2026-10-21-town-axes', 'data/raw/2026-10-21-town-axes')
    if any(rel == b or rel.startswith(b + '/') for b in blocked):
        raise ValueError('Excluded source')
    parent = 'experiments/2026-10-21-town-orientations-verification'
    if rel.startswith(parent + '/') and not rel.startswith(parent + '/dating-v1/'):
        raise ValueError('Excluded sibling source')
    return p


def fetch(args):
    target = (RAW / args.filename).resolve()
    target.relative_to(RAW.resolve())
    if target.exists():
        raise FileExistsError(target)
    req = urllib.request.Request(args.url, headers={'User-Agent': 'Mozilla/5.0 (archaeological bibliography research)'})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
        record = {'url': args.url, 'final_url': r.url, 'retrieved_utc': utc(),
                  'byte_count': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'content_type': r.headers.get('Content-Type'),
                  'rights_notice_observed': args.rights,
                  'handling': 'local-only; no redistribution decision',
                  'path': target.relative_to(ROOT).as_posix()}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    dump(target.with_name(target.name + '.acquisition.json'), record)
    print(json.dumps(record))


def links(args):
    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for k, v in attrs:
                if v and k in ('href', 'src', 'content') and re.search(args.pattern, v, re.I):
                    print(tag, k, v)
    req=urllib.request.Request(args.url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        content=r.read().decode('utf-8',errors='replace')
    Links().feed(content)


def pdf(args):
    import fitz
    path = safe_read_path(args.path)
    doc = fitz.open(path)
    print('PDF:', path.relative_to(ROOT).as_posix(), 'pages:', len(doc))
    selected = set()
    if args.pages:
        for item in args.pages.split(','):
            ends = item.split('-')
            selected.update(range(int(ends[0])-1, int(ends[-1])))
    else:
        selected = {i for i, p in enumerate(doc) if re.search(args.pattern, p.get_text(), re.I)}
    for i in sorted(selected):
        text = doc[i].get_text(sort=args.sort)
        if args.ocr:
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
            result = subprocess.run(['tesseract', 'stdin', 'stdout', '--psm', '3'],
                                    input=pix.tobytes('png'), capture_output=True, check=True)
            text = result.stdout.decode('utf-8', errors='replace')
        print('\n--- PDF page', i+1, '---')
        # Do not transcribe measurements of town, wall, or street direction.
        lines = text.splitlines()
        bad = re.compile(r'orient|bearing|azimuth|north|south|east|west|\bN[EW]\b|\bS[EW]\b|north.?south|east.?west|degrees|°', re.I)
        for line in lines:
            if not bad.search(line):
                print(line)


def status(args):
    proc = subprocess.run(['git', '--no-optional-locks', '-c', 'safe.directory=' + ROOT.as_posix(),
                           'status', '--porcelain', '--untracked-files=all'], cwd=ROOT,
                          capture_output=True, text=True, check=True)
    owned = ('experiments/2026-10-21-town-orientations-verification/dating-v1/',
             'data/raw/2026-10-21-town-orientations-verification/dating/')
    lines = proc.stdout.splitlines()
    ours = [s for s in lines if any(s[3:].replace('\\', '/').strip('"').startswith(x) for x in owned)]
    record = {'checked_utc': utc(), 'command': 'git status --porcelain --untracked-files=all',
              'owned_status_lines': ours, 'other_status_line_count': len(lines)-len(ours),
              'note': 'Other contributors\' paths and contents were not opened by this check.'}
    dump(OUT / (args.name + '.json'), record)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(required=True)
    p = subs.add_parser('fetch')
    p.add_argument('filename'); p.add_argument('url'); p.add_argument('--rights', required=True)
    p.set_defaults(func=fetch)
    p = subs.add_parser('pdf')
    p.add_argument('path'); p.add_argument('--pages'); p.add_argument('--pattern', default='chronolog|radiocarbon')
    p.add_argument('--sort', action='store_true'); p.add_argument('--ocr', action='store_true'); p.set_defaults(func=pdf)
    p = subs.add_parser('status'); p.add_argument('name'); p.set_defaults(func=status)
    p = subs.add_parser('links'); p.add_argument('url'); p.add_argument('--pattern',default=r'\.pdf|download|supinfo'); p.set_defaults(func=links)
    args = parser.parse_args()
    args.func(args)
