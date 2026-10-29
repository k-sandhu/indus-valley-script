"""Compare edited Markdown files with their committed versions.

Reports, per file, numbers, link targets and inline code spans that disappeared or
appeared, and front-matter fields that changed. A rewrite for clarity should keep
every link and code span and change no front-matter field except `title`; numbers
may be consolidated, but each change needs a reason in the editor's report.

Usage: python experiments/2026-10-13-academic-writing-pass/check_invariants.py FILE [FILE ...]
       [--base REV] [--json]
Exit status 1 if a link, code span or protected front-matter field was lost or changed.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
NUMBER = re.compile(r'(?<![\w.])[-−+]?\d[\d,]*(?:\.\d+)?(?:%|‰)?')
LINK = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
BARE_URL = re.compile(r'(?<![(<\[])\bhttps?://[^\s)>\]]+')
CODE = re.compile(r'`([^`\n]+)`')


def committed(path, base):
    rel = Path(path).resolve().relative_to(ROOT).as_posix()
    out = subprocess.run(['git', 'show', f'{base}:{rel}'], cwd=ROOT, capture_output=True)
    return out.stdout.decode('utf-8').replace('\r\n', '\n') if out.returncode == 0 else None


def front_matter(text):
    if not text.startswith('---\n'):
        return {}
    end = text.find('\n---', 4)
    fields, key = {}, None
    for line in text[4:end].splitlines():
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if m:
            key = m[1]
            fields[key] = m[2]
        elif key:
            fields[key] += '\n' + line
    return fields


def numbers(text):
    body = re.sub(r'\]\([^)]*\)', ']', text)          # numbers inside link targets are links
    body = BARE_URL.sub('', body)
    return Counter(n.replace(',', '').replace('−', '-') for n in NUMBER.findall(body))


def compare(path, base):
    new = Path(path).read_text(encoding='utf-8').replace('\r\n', '\n')
    old = committed(path, base)
    if old is None:
        return {'file': path, 'status': 'new file; nothing to compare'}
    links_old = Counter(LINK.findall(old) + BARE_URL.findall(old))
    links_new = Counter(LINK.findall(new) + BARE_URL.findall(new))
    code_old, code_new = Counter(CODE.findall(old)), Counter(CODE.findall(new))
    nums_old, nums_new = numbers(old), numbers(new)
    fm_old, fm_new = front_matter(old), front_matter(new)
    fm_changed = sorted(k for k in set(fm_old) | set(fm_new) if fm_old.get(k) != fm_new.get(k))
    result = {
        'file': Path(path).resolve().relative_to(ROOT).as_posix(),
        'words_before': len(old.split()), 'words_after': len(new.split()),
        'links_lost': sorted(set(links_old) - set(links_new)),
        'links_added': sorted(set(links_new) - set(links_old)),
        'code_lost': sorted(set(code_old) - set(code_new)),
        'numbers_lost': sorted(set(nums_old) - set(nums_new)),
        'numbers_added': sorted(set(nums_new) - set(nums_old)),
        'front_matter_changed': fm_changed,
    }
    protected = [k for k in fm_changed if k != 'title']
    result['status'] = 'FAIL' if result['links_lost'] or result['code_lost'] or protected else 'ok'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='+')
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    results = [compare(f, args.base) for f in args.files]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            print(f"{r['status']:4}  {r['file']}")
            for key in ('words_before', 'words_after', 'links_lost', 'links_added', 'code_lost',
                        'numbers_lost', 'numbers_added', 'front_matter_changed'):
                if r.get(key):
                    print(f'      {key}: {r[key]}')
    raise SystemExit(1 if any(r['status'] == 'FAIL' for r in results) else 0)


if __name__ == '__main__':
    main()
