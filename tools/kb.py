"""Search and maintain the repository's navigation layer. Standard library only."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote
from storage_paths import repository_relative

ROOT = Path(__file__).resolve().parents[1]
if os.name == 'nt' and not str(ROOT).startswith('\\\\?\\'):
    base = str(ROOT)
    ROOT = Path('\\\\?\\UNC\\' + base[2:] if base.startswith('\\\\') else '\\\\?\\' + base)
AREAS = ('corpus', 'data', 'structure', 'seals', 'tablets', 'numerals', 'images',
         'meaning', 'language', 'archaeology', 'comparative', 'methods')
STATUSES = ('proposed', 'synthetic', 'exploratory', 'frozen-evaluation', 'failed',
            'superseded', 'verified-computation', 'source-review', 'record')
KINDS = ('finding', 'question', 'conjecture', 'attempt', 'direction', 'retrospective', 'paper')
Q_KINDS = ('analysis', 'data-acquisition', 'metadata', 'verification', 'literature', 'fieldwork', 'tooling')
ACCESS = ('none-needed', 'public', 'local-only', 'acquire', 'fieldwork')
DIFFICULTY = ('starter', 'standard', 'expert')
ATTEMPT_FIELDS = ('id', 'theme', 'status', 'question', 'outcome', 'challenge', 'remedy',
                  'evidence', 'retry_when', 'status_class', 'area')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def relative(path):
    return repository_relative(path, ROOT).as_posix()


def uncomment(value):
    """Strip YAML comments outside quotes and flow collections."""
    quote = None
    escaped = False
    depth = 0
    for i, c in enumerate(value):
        if escaped:
            escaped = False
        elif c == '\\' and quote == '"':
            escaped = True
        elif quote:
            if c == quote:
                quote = None
        elif c in '\"\'':
            quote = c
        elif c in '[{':
            depth += 1
        elif c in ']}':
            depth -= 1
        elif c == '#' and depth == 0 and (i == 0 or value[i-1].isspace()):
            return value[:i].rstrip()
    return value.strip()


def split_flow(value):
    parts, start, depth, quote, escaped = [], 0, 0, None, False
    for i, c in enumerate(value):
        if escaped:
            escaped = False
        elif c == '\\' and quote == '"':
            escaped = True
        elif quote:
            if c == quote:
                quote = None
        elif c in '\"\'':
            quote = c
        elif c in '[{':
            depth += 1
        elif c in ']}':
            depth -= 1
        elif c == ',' and depth == 0:
            parts.append(value[start:i].strip())
            start = i + 1
    if quote or depth:
        raise ValueError('Unbalanced flow value')
    parts.append(value[start:].strip())
    return parts


def scalar(value):
    raw = value
    value = uncomment(value)
    try:
        if value.startswith('[') and value.endswith(']'):
            return [scalar(p) for p in split_flow(value[1:-1])] if value[1:-1].strip() else []
        if value.startswith('{') and value.endswith('}'):
            result = {}
            for p in split_flow(value[1:-1]) if value[1:-1].strip() else []:
                m = re.match(r'^([^:]+):\s*(.*)$', p)
                if not m:
                    return raw
                result[str(scalar(m[1]))] = scalar(m[2])
            return result
        if value.startswith('"') and value.endswith('"'):
            return json.loads(value)
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1].replace("''", "'")
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        if value.lower() in ('null', '~'):
            return None
        if re.fullmatch(r'[-+]?\d+', value):
            return int(value)
        if re.fullmatch(r'[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?', value):
            return float(value)
    except (ValueError, TypeError):
        return raw
    return value


def frontmatter(content):
    """Read the documented subset; retain unsupported structures as raw strings."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}, content
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if end is None:
        return {}, content
    fields = {}
    i = 1
    while i < end:
        m = re.match(r'^([\w-]+):\s*(.*)$', lines[i])
        if not m:
            i += 1
            continue
        key, val = m.groups()
        j = i + 1
        while j < end and not re.match(r'^[\w-]+:', lines[j]):
            j += 1
        tail = lines[i+1:j]
        significant = [s for s in tail if s.strip() and not s.lstrip().startswith('#')]
        if not uncomment(val) and significant:
            matches = [re.match(r'^\s+-\s+(.*)$', s) for s in significant]
            if all(matches) and all(not re.match(r'^[\w-]+:\s', m[1]) for m in matches):
                fields[key] = [scalar(m[1]) for m in matches]
            else:
                fields[key] = '\n'.join([val, *tail]).strip('\n')
        elif significant:
            fields[key] = '\n'.join([val, *tail])
        else:
            fields[key] = scalar(val)
        i = j
    return fields, '\n'.join(lines[end+1:]).lstrip('\n')


def heading(content, fallback):
    match = re.search(r'^#\s+(.+)$', content, re.M)
    return match[1].strip() if match else fallback


def index_items():
    result = []
    patterns = {
        'finding': 'knowledge/findings/F-*.md', 'question': 'knowledge/questions/Q-*.md',
        'conjecture': 'knowledge/conjectures/C-*.md', 'direction': 'knowledge/directions/*.md',
        'retrospective': 'knowledge/retrospectives/*.md', 'paper': 'papers/*/manuscript.md',
    }
    for kind, pattern in patterns.items():
        paths = set(ROOT.glob(pattern))
        if kind == 'retrospective':
            for folder in ('experiments', 'maintenance', 'presentations'):
                paths.update(ROOT.glob(f'{folder}/**/RETROSPECTIVE.md'))
                paths.update(ROOT.glob(f'{folder}/**/RETROSPECTIVE.json'))
        for path in sorted(paths):
            if path.name == 'README.md':
                continue
            content = read(path)
            fields, body = frontmatter(content)
            if path.suffix == '.json':
                fields = json.loads(content)
            result.append(dict(id=fields.get('id', relative(path)), kind=kind,
                               status=fields.get('status_class', fields.get('status', 'document')),
                               title=fields.get('title', heading(body, path.stem)), path=relative(path),
                               area=fields.get('area', ''), fields=fields, body=body))
    for path in sorted((ROOT/'knowledge/registry/attempts').glob('*.json')):
        fields = json.loads(read(path))
        result.append(dict(id=fields.get('id', path.stem), kind='attempt',
                           status=fields.get('status_class', fields.get('status', '')),
                           title=fields.get('question', path.stem), path=relative(path),
                           area=fields.get('area', ''), fields=fields, body=json_text(fields)))
    return sorted(result, key=lambda x: (x['kind'], str(x['id']), x['path']))


def registry_document():
    metadata = json.loads(read(ROOT/'knowledge/registry/metadata.json'))
    entries = [json.loads(read(p)) for p in sorted((ROOT/'knowledge/registry/attempts').glob('*.json'))]
    entries.sort(key=lambda e: (0, e['registry_order'], e['id']) if 'registry_order' in e else (1, 0, e['id']))
    return {**metadata, 'experiments': entries}


def short(value, limit=95):
    value = re.sub(r'\s+', ' ', str(value)).replace('|', '/').replace('[', '(').replace(']', ')')
    return value if len(value) <= limit else value[:limit-1].rstrip() + '…'


def map_document(items):
    lines = ['# Repository map', '', 'Generated by `python tools/kb.py build`; do not edit by hand.', '',
             'Read the section for your task, then open its card or source package. '
             'Use `python tools/kb.py search <terms>` to narrow the list and `show <ID>` to read a card. '
             'Before analysis, read [DATA.md](DATA.md) for the coverage your test needs.', '',
             '## Top level', '']
    # A fixed list of tracked directories, so local folders never enter the committed map.
    descriptions = {'papers': 'manuscripts and evidence maps', 'knowledge': 'cards, navigation and research memory',
                    'experiments': 'dated research protocols, outputs and reviews; new research goes in a new dated package',
                    'maintenance': 'dated records of earlier repository work: releases, publication screens, the website generator, storage and restructuring',
                    'presentations': 'slide decks, maps and visual summaries of recorded results',
                    'research': 'original investigation and source audits, frozen',
                    'src': 'original analysis code, frozen', 'results': 'original outputs, frozen',
                    'output': 'original reports and chart atlas, frozen', 'bench': 'shared evaluation harness',
                    'archive': 'preserved historical documentation', 'tools': 'manual repository utilities',
                    'data': 'data README and manifest; acquired inputs stay local', 'templates': 'contributor templates',
                    'site': 'website templates and static files', 'LICENSES': 'licence texts',
                    '.claude': 'repository skills', '.github': 'issue forms'}
    for name in sorted(descriptions):
        lines.append(f'- [{name}/](../{name}/): {descriptions[name]}.')
    # PLAN.md stays byte-identical: two evidence manifests record its hash.
    lines.append('- [PLAN.md](../PLAN.md): the superseded plan of the first investigation, 1 October, kept unchanged.')
    lines += ['', '## Entry documents', '']
    for p in ('README.md', 'AGENTS.md', 'knowledge/DATA.md', 'knowledge/WORKING-MODEL.md',
              'knowledge/INDEX.md', 'knowledge/TIMELINE.md', 'CONTRIBUTING.md', 'REPRODUCING.md'):
        target = os.path.relpath(ROOT/p, ROOT/'knowledge').replace('\\', '/')
        lines.append(f'- [{p}]({target})')

    def item_line(item, extra=''):
        target = os.path.relpath(ROOT/item['path'], ROOT/'knowledge').replace('\\', '/')
        return f"- [{item['id']}]({target}) · {item['status']}{extra} · {short(item['title'])}"

    lines += ['', '## Findings by area', '']
    for area in AREAS:
        group = [x for x in items if x['kind'] == 'finding' and x['area'] == area]
        if group:
            lines += [f'### {area}', ''] + [item_line(x) for x in group] + ['']
    lines += ['## Open questions by priority', '']
    for priority in range(1, 6):
        group = [x for x in items if x['kind'] == 'question' and x['fields'].get('status') in ('open', 'claimed')
                 and x['fields'].get('priority') == priority]
        if group:
            lines += [f'### Priority {priority}', ''] + [item_line(x, ' · '+x['area']) for x in group] + ['']
    lines += ['## Conjectures', '']
    lines += [item_line(x, ' · credence '+str(x['fields'].get('credence', '?'))) for x in items if x['kind'] == 'conjecture']
    lines += ['', '## Papers', ''] + [item_line(x) for x in items if x['kind'] == 'paper']
    # Attempts, retrospectives, memos and closed questions are reached by the CLI, which keeps the map short.
    count = Counter(x['kind'] for x in items)
    closed = Counter(x['fields'].get('status') for x in items if x['kind'] == 'question')
    lines += ['', '## Other records', '',
              f"- {count['attempt']} registry attempts: `python tools/kb.py list --kind attempt`, "
              'or the generated [registry](experiments/registry.json).',
              f"- {count['retrospective']} retrospectives: `python tools/kb.py list --kind retrospective`; "
              'the curated essays are indexed in [retrospectives/README.md](retrospectives/README.md).',
              f"- {count['direction']} direction memos: `python tools/kb.py list --kind direction`.",
              f"- {closed['done']} completed and {closed['dropped']} dropped questions: "
              '`python tools/kb.py list --kind question --status done` or `--status dropped`.']
    return '\n'.join(lines).rstrip() + '\n'


def generated():
    return {'knowledge/experiments/registry.json': json_text(registry_document()),
            'knowledge/MAP.md': map_document(index_items())}


def build():
    changed = []
    for name, content in generated().items():
        path = ROOT/name
        payload = content.encode('utf-8')
        if not path.exists() or path.read_bytes() != payload:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            changed.append(name)
    return changed


def links(content):
    """Balanced Markdown destinations, excluding fenced code and inline code."""
    fenced = False
    for number, original in enumerate(content.splitlines(), 1):
        if original.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
            continue
        if fenced:
            continue
        line = re.sub(r'`+[^`]*`+', '', original)
        definition = re.match(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)', line)
        if definition:
            yield number, definition[1].strip('<>')
        for m in re.finditer(r'!?\[[^\]]*\]\(', line):
            start, level, angle, escaped = m.end(), 1, False, False
            for i in range(start, len(line)):
                c = line[i]
                if escaped:
                    escaped = False
                elif c == '\\':
                    escaped = True
                elif c == '<':
                    angle = True
                elif c == '>':
                    angle = False
                elif not angle and c == '(':
                    level += 1
                elif not angle and c == ')':
                    level -= 1
                    if level == 0:
                        value = line[start:i].strip()
                        yield number, value[1:value.index('>')] if value.startswith('<') else re.split(r'\s+[\"\']', value)[0]
                        break


def new_markdown():
    names = ['AGENTS.md', 'CLAUDE.md', 'README.md', 'CONTRIBUTING.md', 'llms.txt',
             'knowledge/INDEX.md', 'knowledge/MAP.md', 'knowledge/TIMELINE.md', 'knowledge/experiments/README.md',
             'templates/FINDING.md', 'templates/QUESTION.md', 'templates/EXPERIMENT.md',
             'research/README.md', 'results/README.md', 'src/README.md', 'output/README.md']
    result = [ROOT/n for n in names if (ROOT/n).exists()]
    for pattern in ('knowledge/registry/*.md', 'knowledge/findings/*.md', 'knowledge/questions/*.md', '.claude/skills/*/*.md'):
        result += sorted(ROOT.glob(pattern))
    result += [p for p in (ROOT/'maintenance/2026-10-12-repo-restructure').glob('*.md') if p.name != 'CODEX-PROMPT.md']
    return sorted(set(result))


def check(strict=False):
    errors, warnings, notes, reviewed, ids, orders = [], [], [], set(), {}, {}
    omissions_path = ROOT/'maintenance/2026-10-11-public-release/public-omissions.json'
    omissions = set(json.loads(read(omissions_path)).get('targets', [])) if omissions_path.exists() else set()
    items = index_items()
    metadata = json.loads(read(ROOT/'knowledge/registry/metadata.json'))
    for field in ('schema_version', 'scope'):
        if field not in metadata:
            errors.append('knowledge/registry/metadata.json: missing field ' + field)
    if 'experiments' in metadata:
        errors.append('knowledge/registry/metadata.json: experiments belongs in per-entry files')

    def fail(item, message):
        errors.append(item['path'] + ': ' + message)

    def target_check(value, context, base=ROOT):
        if not isinstance(value, str):
            errors.append(context + ': expected a path string')
            return
        path_part = unquote(value.split('#', 1)[0].split('?', 1)[0])
        if not path_part or re.match(r'^[A-Za-z][\w+.-]*:', path_part):
            return
        target = (base/path_part).resolve()
        try:
            rel = relative(target)
        except ValueError:
            errors.append(context + ': path leaves repository: ' + value)
            return
        if rel in omissions:
            reviewed.add(rel)
        if not target.exists() and rel not in omissions:
            errors.append(context + ': missing path: ' + rel)
        # A #/ fragment on JSON evidence is a JSON Pointer, not a Markdown heading.
        if target.is_file() and target.suffix == '.json' and '#/' in value:
            try:
                node = json.loads(read(target))
                for token in value.split('#/', 1)[1].split('/'):
                    token = token.replace('~1', '/').replace('~0', '~')
                    node = node[int(token)] if isinstance(node, list) else node[token]
            except (ValueError, KeyError, IndexError, TypeError):
                errors.append(context + ': missing JSON field: ' + value)

    for item in items:
        kind, f, identifier = item['kind'], item['fields'], item['id']
        if identifier in ids:
            fail(item, 'duplicate ID also in ' + ids[identifier])
        ids[identifier] = item['path']
        required = {'finding': ('id', 'title', 'status_class', 'area', 'date', 'registry_ids', 'evidence', 'population'),
                    'question': ('id', 'title', 'status', 'area', 'kind', 'priority', 'data_access', 'compute',
                                 'difficulty', 'claimed_by', 'claim_expires', 'prior_attempts', 'related', 'sources'),
                    'conjecture': ('id', 'title', 'status', 'credence', 'credence_history', 'risk', 'area',
                                   'authors', 'prior_proposals', 'builds_on', 'tests'),
                    'attempt': ATTEMPT_FIELDS}.get(kind, ())
        for field in required:
            if field not in f:
                fail(item, 'missing field ' + field)
        if kind in ('finding', 'question', 'conjecture'):
            prefix = {'finding': 'F', 'question': 'Q', 'conjecture': 'C'}[kind]
            if not isinstance(identifier, str) or not re.fullmatch(prefix+r'-\d{4}', identifier):
                fail(item, 'invalid card ID')
            elif not Path(item['path']).name.startswith(identifier+'-'):
                fail(item, 'filename must start with ID and a slug')
            if not f.get('title'):
                fail(item, 'empty title')
        if kind == 'attempt':
            if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', identifier):
                fail(item, 'invalid attempt ID')
            elif Path(item['path']).stem != identifier:
                fail(item, 'filename and ID differ')
            if 'registry_order' in f:
                order = f['registry_order']
                if type(order) is not int or order < 0:
                    fail(item, 'registry_order must be a nonnegative integer')
                elif order in orders:
                    fail(item, 'duplicate registry_order')
                orders[order] = identifier
        if kind in ('finding', 'question', 'conjecture', 'attempt') and f.get('area') not in AREAS:
            fail(item, 'invalid area')
        if kind in ('finding', 'attempt') and f.get('status_class') not in STATUSES:
            fail(item, 'invalid status_class')
        allowed = {'question': {'status': ('open', 'claimed', 'done', 'dropped'), 'kind': Q_KINDS,
                               'data_access': ACCESS, 'compute': ('minutes', 'hours', 'days'), 'difficulty': DIFFICULTY},
                   'conjecture': {'status': ('open', 'strengthened', 'weakened', 'dead'), 'risk': ('safe', 'stretch', 'long-shot')}}
        for field, values in allowed.get(kind, {}).items():
            if f.get(field) not in values:
                fail(item, 'invalid ' + field)
        if kind == 'question':
            if type(f.get('priority')) is not int or f['priority'] not in range(1, 6):
                fail(item, 'priority must be 1 to 5')
            for field in ('claimed_by', 'claim_expires'):
                if not isinstance(f.get(field), str):
                    fail(item, field + ' must be a string')
            if f.get('claim_expires'):
                try:
                    expires = date.fromisoformat(f['claim_expires'])
                except (ValueError, TypeError):
                    fail(item, 'claim_expires must be an ISO date')
                else:
                    if expires < date.today() and f.get('status') not in ('done', 'dropped'):
                        warnings.append(f"{item['path']}: claim by {f.get('claimed_by') or 'an unnamed claimant'} "
                                        f"lapsed on {expires}; check the issue before taking the question")
            if f.get('status') == 'claimed' and not (f.get('claimed_by') and f.get('claim_expires')):
                fail(item, 'claimed questions need claimant and expiry')
        if kind == 'finding':
            try:
                date.fromisoformat(str(f.get('date', '')))
            except ValueError:
                fail(item, 'date must be an ISO date')
            if not f.get('population') or not f.get('evidence'):
                fail(item, 'population and evidence must be nonempty')
        if kind == 'conjecture':
            if type(f.get('credence')) not in (int, float) or not 0 <= f['credence'] <= 1:
                fail(item, 'credence must be between zero and one')
        list_fields = {'finding': ('registry_ids', 'evidence'), 'question': ('prior_attempts', 'related', 'sources'),
                       'conjecture': ('credence_history', 'authors', 'prior_proposals', 'builds_on', 'tests'),
                       'attempt': ('evidence',)}.get(kind, ())
        for field in list_fields:
            if not isinstance(f.get(field), list):
                fail(item, field + ' must be a list')
        for field in ('evidence', 'sources'):
            if isinstance(f.get(field), list):
                for value in f[field]:
                    target_check(value, item['path']+' '+field)
    for item in items:
        for field in ('registry_ids', 'prior_attempts', 'related'):
            if isinstance(item['fields'].get(field), list):
                for identifier in item['fields'][field]:
                    if identifier not in ids:
                        fail(item, field + ' refers to unknown ID ' + str(identifier))
    for path in new_markdown():
        for line, target in links(read(path)):
            target_check(target, relative(path)+':'+str(line), path.parent)
    # Contributors leave generated files to maintainers, so drift is a maintainer note unless --strict.
    for name, expected in generated().items():
        if not (ROOT/name).is_file() or (ROOT/name).read_bytes() != expected.encode('utf-8'):
            (errors if strict else notes).append(name + ': differs from a fresh build; run python tools/kb.py build')
    result = dict(status='pass' if not errors else 'fail', items=len(items),
                  counts=dict(sorted(Counter(x['kind'] for x in items).items())), errors=errors,
                  warnings=warnings, maintainer_notes=notes,
                  reviewed_local_only=sorted(reviewed), markdown_files_checked=len(new_markdown()))
    for error in errors:
        print('ERROR ' + error)
    for warning in warnings:
        print('WARNING ' + warning)
    for note in notes:
        print('MAINTAINER ' + note)
    print(f"kb.py check: {result['status'].upper()}; {len(items)} items; {len(errors)} errors; "
          f"{len(warnings)} warnings; {len(notes)} maintainer notes; "
          f"{len(reviewed)} reviewed local-only targets; {result['markdown_files_checked']} Markdown files.")
    return result


def create(kind, title, area, data=False):
    if data and kind != 'question':
        raise ValueError('--data applies only to questions')
    items = index_items()
    prefix = {'finding': 'F', 'question': 'Q', 'conjecture': 'C', 'attempt': 'ATTEMPT'}[kind]
    used = {x['id'] for x in items}
    # General questions use Q-0001 to Q-0999; data acquisition questions use Q-1001 onward.
    lower, upper = (1001, 9999) if data else (1, 999 if kind == 'question' else 9999)
    number = next((i for i in range(lower, upper+1) if f'{prefix}-{i:04d}' not in used), None)
    if number is None:
        raise ValueError('Contributor ID range is full')
    identifier = f'{prefix}-{number:04d}'
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:70] or 'untitled'
    if kind == 'attempt':
        path = ROOT/f'knowledge/registry/attempts/{identifier}.json'
        fields = dict(id=identifier, theme=title, status='proposed', question=title, outcome='',
                      challenge='', remedy='', evidence=[], retry_when='', status_class='proposed',
                      area=area, authors=[])
        content = json_text(fields)
    elif kind == 'conjecture':
        path = ROOT/f'knowledge/conjectures/{identifier}-{slug}.md'
        content = read(ROOT/'knowledge/conjectures/TEMPLATE.md').replace('C-NNNN', identifier)
        content = re.sub(r'^title: .*$', lambda m: 'title: '+json.dumps(title, ensure_ascii=False),
                         content, count=1, flags=re.M)
        content = re.sub(r'^area: \S+', lambda m: 'area: '+area, content, count=1, flags=re.M)
        content = content.replace('YYYY-MM-DD', date.today().isoformat())
    else:
        path = ROOT/f'knowledge/{"questions" if kind == "question" else "findings"}/{identifier}-{slug}.md'
        content = read(ROOT/f'templates/{kind.upper()}.md')
        content = content.replace(prefix+'-NNNN', identifier).replace('TITLE', json.dumps(title, ensure_ascii=False))
        content = content.replace('AREA', area).replace('YYYY-MM-DD', date.today().isoformat())
        if kind == 'question':
            content = content.replace('(../knowledge/DATA.md)', '(../DATA.md)')
        if data:
            content = content.replace('kind: analysis', 'kind: data-acquisition', 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(content)
    print(relative(path))


def display(items, as_json=False):
    if as_json:
        print(json_text([{k: v for k, v in x.items() if k != 'body'} for x in items]), end='')
    else:
        for x in items:
            print(f"{x['id']}\t{x['kind']}\t{x['status']}\t{x['title']}\t{x['path']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    search = sub.add_parser('search'); search.add_argument('terms', nargs='+')
    show = sub.add_parser('show'); show.add_argument('id')
    listing = sub.add_parser('list')
    nxt = sub.add_parser('next', help='Open questions with no recorded claimant; check the issue before claiming')
    for p in (search, listing):
        p.add_argument('--kind', choices=KINDS); p.add_argument('--json', action='store_true')
    listing.add_argument('--status'); listing.add_argument('--area', choices=AREAS)
    nxt.add_argument('--area', choices=AREAS); nxt.add_argument('--kind', choices=Q_KINDS)
    nxt.add_argument('--data-access', choices=ACCESS); nxt.add_argument('--difficulty', choices=DIFFICULTY)
    new = sub.add_parser('new'); new.add_argument('kind', choices=('question', 'finding', 'conjecture', 'attempt'))
    new.add_argument('--title', required=True)
    new.add_argument('--area', choices=AREAS, help='default: data with --data, otherwise methods')
    new.add_argument('--data', action='store_true', help='data acquisition question, numbered from Q-1001')
    sub.add_parser('build')
    sub.add_parser('check').add_argument('--strict', action='store_true',
                                         help='count generated-file drift as an error (for maintainers)')
    args = parser.parse_args()
    try:
        if args.command == 'build':
            changed = build()
            print('kb.py build: '+str(len(changed))+' files changed'+(' · '+', '.join(changed) if changed else ''))
            return 0
        if args.command == 'check':
            return 0 if check(args.strict)['status'] == 'pass' else 1
        if args.command == 'new':
            create(args.kind, args.title, args.area or ('data' if args.data else 'methods'), args.data)
            return 0
        items = index_items()
        if args.command == 'show':
            matches = [x for x in items if str(x['id']).casefold() == args.id.casefold()]
            if len(matches) != 1:
                raise ValueError('ID not found or ambiguous: '+args.id)
            print(read(ROOT/matches[0]['path']), end='')
            return 0
        if args.command == 'next':
            items = [x for x in items if x['kind'] == 'question' and x['fields'].get('status') == 'open'
                     and not x['fields'].get('claimed_by')]
            for attr, field in (('area', 'area'), ('kind', 'kind'), ('data_access', 'data_access'), ('difficulty', 'difficulty')):
                value = getattr(args, attr)
                if value:
                    items = [x for x in items if x['fields'].get(field) == value]
            items.sort(key=lambda x: (x['fields'].get('priority', 5), x['id']))
            display(items)
        else:
            if args.kind:
                items = [x for x in items if x['kind'] == args.kind]
            if args.command == 'list':
                if args.status:
                    items = [x for x in items if x['status'] == args.status or x['fields'].get('status') == args.status]
                if args.area:
                    items = [x for x in items if x['area'] == args.area]
            else:
                terms = [t.casefold() for t in args.terms]
                def score(x):
                    return sum(20*str(x['id']).casefold().count(t)+8*str(x['title']).casefold().count(t)
                               +min(10, x['body'].casefold().count(t)) for t in terms)
                items = [dict(x, score=score(x)) for x in items if score(x)]
                items.sort(key=lambda x: (-x['score'], x['kind'], x['id']))
            display(items, args.json)
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print('kb.py: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    # Windows redirected output uses the system code page unless explicitly set.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
