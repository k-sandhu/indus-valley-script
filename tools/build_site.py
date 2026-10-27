"""Build the public research website from a Git-selected source snapshot."""
from __future__ import annotations

import argparse
from collections import defaultdict
from contextlib import contextmanager
from datetime import date
import hashlib
import html
from html.parser import HTMLParser
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote, unquote, urlencode, urlsplit, urlunsplit

import jinja2
import markdown

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/k-sandhu/indus-valley-script'
SITE = 'https://k-sandhu.github.io/indus-valley-script/'
OMISSIONS = 'experiments/2026-10-11-public-release/public-omissions.json'
MANIFEST = 'data/MANIFEST.json'
EXPLORE = ('experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html',
           'output/chart_atlas/index.html')
FINDINGS_GUIDE = 'knowledge/findings/README.md'
LIVING_ATLAS = 'experiments/2026-10-26-indus-living-atlas'
# A group has children; a direct entry has a destination. No scripted menu.
NAV = [('Home', 'index.html'), ('Findings', 'findings/index.html'),
       ('Ideas', [('Working model', 'working-model/index.html'), ('Conjectures', 'conjectures/index.html')]),
       ('Questions', 'questions/index.html'),
       ('Record', [('Registry', 'attempts/index.html'), ('Timeline', 'timeline/index.html'),
                   ('Papers', 'papers/index.html'), ('Data', 'data.html')]),
       ('Explore', 'explore/index.html'),
       ('About', [('Contribute', 'contribute/index.html'), ('Reuse', 'reuse/index.html')])]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
RESOURCE_ATTRS = {'src', 'poster', 'data', 'srcset'}


def git(*args, root=ROOT, payload=None, env=None):
    result = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', '-C', str(root), *args], input=payload,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def safe_path(path):
    path = unquote(path).replace('\\', '/')
    normalized = posixpath.normpath(path).lstrip('/')
    if normalized in ('', '.', '..') or normalized.startswith('../') or ':' in normalized:
        raise ValueError(f'Unsafe repository path: {path}')
    return normalized


def relative_url(target, page):
    return quote(posixpath.relpath(target, posixpath.dirname(page) or '.'), safe='/')


def tree_inventory(commit, root=ROOT):
    result = {}
    for record in git('ls-tree', '-rz', commit, root=root).split(b'\0'):
        if record:
            fields, name = record.split(b'\t', 1)
            mode, kind, oid = fields.decode().split()
            if kind == 'blob' and mode in ('100644', '100755'):
                result[name.decode('utf-8')] = oid
    return result


class GitSource:
    """Inventory first; contents cannot bypass the public-path gate."""
    def __init__(self, worktree=False, root=ROOT):
        self.root = root
        self.worktree = worktree
        self.commit = git('rev-parse', 'HEAD', root=root).decode().strip()
        self.date = git('show', '-s', '--format=%cI', self.commit, root=root).decode().strip()
        self.committed = tree_inventory(self.commit, root)
        self.tracked = {p.decode('utf-8') for p in git('ls-files', '--cached', '-z', root=root).split(b'\0') if p}
        self.files = (set(p.decode('utf-8') for p in git('ls-files', '--cached', '--others',
                      '--exclude-standard', '-z', root=root).split(b'\0') if p)
                      if worktree else set(self.committed))
        self.cache = {}
        self.inputs = {}
        self.omissions = []
        self.omissions = json.loads(self.text(OMISSIONS))['targets']
        self.files = {p for p in self.files if not self.excluded(p)}
        if worktree:
            self.files = {p for p in self.files if self.root.joinpath(*PurePosixPath(p).parts).is_file()
                          and not self.root.joinpath(*PurePosixPath(p).parts).is_symlink()}
        self.dirs = {str(parent) for p in self.files for parent in PurePosixPath(p).parents if str(parent) != '.'}

    def excluded(self, path):
        return (path == 'data' or path.startswith('data/') or
                any(path == p.rstrip('/') or path.startswith(p.rstrip('/') + '/') for p in self.omissions))

    def allowed(self, path):
        return path in self.files and not self.excluded(path)

    def bytes(self, path, metadata=False):
        exception = metadata and path == MANIFEST and path in (self.tracked if self.worktree else self.committed)
        if not exception and not self.allowed(path):
            raise ValueError(f'Not in the public repository: {path}')
        if path not in self.cache:
            if self.worktree:
                candidate = self.root.joinpath(*PurePosixPath(path).parts)
                # Do not follow a worktree symlink or junction out of the source root.
                if candidate.is_symlink() or not candidate.resolve().is_relative_to(self.root.resolve()):
                    raise ValueError(f'Unsafe worktree source: {path}')
                self.cache[path] = candidate.read_bytes()
            else:
                self.cache[path] = git('show', f'{self.commit}:{path}', root=self.root)
            self.inputs[path] = hashlib.sha256(self.cache[path]).hexdigest()
        return self.cache[path]

    def text(self, path, metadata=False):
        return self.bytes(path, metadata).decode('utf-8-sig')


class GitDirectory:
    """The pathlib operations used by kb.index_items, over the Git inventory."""
    def __init__(self, source, prefix=''):
        self.source, self.prefix = source, prefix

    def __truediv__(self, suffix):
        return GitDirectory(self.source, posixpath.join(self.prefix, suffix))

    def glob(self, pattern):
        full = posixpath.join(self.prefix, pattern)
        return [PurePosixPath(p) for p in sorted(self.source.files)
                if PurePosixPath(p).match(full) and
                ('**' in full or len(PurePosixPath(p).parts) == len(PurePosixPath(full).parts))]


class GitModuleLoader(importlib.abc.Loader):
    def __init__(self, source):
        self.source = source

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.__file__ = str(self.source.root / 'tools/kb.py')
        exec(compile(self.source.text('tools/kb.py'), module.__file__, 'exec'), module.__dict__)


@contextmanager
def kb_index(source):
    # Import both parsing and indexing code from the selected Git source.
    spec = importlib.util.spec_from_loader('site_kb', GitModuleLoader(source))
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)
    kb.ROOT = GitDirectory(source)
    kb.read = lambda path: source.text(str(path))
    kb.relative = lambda path: str(path)
    yield kb


class SourceTemplates(jinja2.BaseLoader):
    def __init__(self, source):
        self.source = source

    def get_source(self, environment, template):
        path = 'site/templates/' + safe_path(template)
        if not self.source.allowed(path):
            raise jinja2.TemplateNotFound(template)
        return self.source.text(path), path, lambda: True


def section(text, name):
    match = re.search(r'^#{1,6}\s+' + re.escape(name) + r'\s*$', text, re.M)
    if not match:
        return ''
    level = len(match[0].split()[0])
    tail = text[match.end():]
    end = re.search(r'^#{1,' + str(level) + r'}\s', tail, re.M)
    return tail[:end.start() if end else len(tail)].strip()


def text_only(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '',
                  markdown.markdown(str(value), extensions=['extra'])))).strip()


def parse_findings_guide(content, rows):
    """Parse the shared guide contract. Reject partial parses instead of losing prose."""
    lines = content.replace('\r\n', '\n').strip().splitlines()
    if not lines or lines[0].strip() != '# Findings':
        raise ValueError('expected # Findings as the first heading')
    by_id = {row['id']: row for row in rows}
    intro, themes, seen, uncarded = [], [], set(), None
    current = None
    for number, line in enumerate(lines[1:], 2):
        if line.startswith('## '):
            title = line[3:].strip()
            if not title or uncarded is not None:
                raise ValueError(f'line {number}: empty theme or section after the final section')
            if title == 'Results recorded in packages but not yet carded':
                uncarded = {'title': title, 'intro': [], 'entries': []}
                current = uncarded
            else:
                current = {'title': title, 'intro': [], 'cards': []}
                themes.append(current)
        elif line.startswith('#'):
            raise ValueError(f'line {number}: only level-2 theme headings are supported')
        elif line.startswith('- ['):
            if current is None:
                raise ValueError(f'line {number}: entry before the first theme')
            if current is uncarded:
                if not re.fullmatch(r'- \[[^\]]+\]\([^)]+\) .+', line):
                    raise ValueError(f'line {number}: malformed package entry')
                current['entries'].append(line)
                continue
            match = re.fullmatch(r'- \[(F-\d{4})\]\(([^)]+)\) (.+?)\s+\*([\w-]+)\*\.?', line)
            if not match:
                raise ValueError(f'line {number}: malformed finding entry')
            identifier, target, result, status = match.groups()
            row = by_id.get(identifier)
            if row is None or identifier in seen:
                raise ValueError(f'line {number}: unknown or repeated finding {identifier}')
            if safe_path(posixpath.join(posixpath.dirname(FINDINGS_GUIDE), target)) != row['path']:
                raise ValueError(f'line {number}: card path does not match {identifier}')
            if status != row['status']:
                raise ValueError(f'line {number}: status does not match {identifier}')
            current['cards'].append({'id': identifier, 'result': result})
            seen.add(identifier)
        else:
            if line.strip() and (line.lstrip().startswith(('-', '*', '+')) or
                                 (current and current.get('cards', current.get('entries')))):
                raise ValueError(f'line {number}: prose must precede the section entries')
            (intro if current is None else current['intro']).append(line)
    if not any(s.strip() for s in intro) or not themes or any(not any(s.strip() for s in t['intro']) or not t['cards'] for t in themes):
        raise ValueError('the guide needs an introduction and themes with prose and findings')
    return {'intro': '\n'.join(intro), 'themes': themes, 'uncarded': uncarded, 'listed': seen}


def attempt_date(fields):
    """Use an explicit ISO date, then the dated package containing the evidence."""
    candidates = [fields.get('date', '')]
    paths = [fields.get('package', ''), *fields.get('evidence', [])]
    # A nested run date does not replace the package's starting date.
    candidates.extend(m[1] for path in paths if isinstance(path, str)
                      for m in [re.match(r'^experiments/(\d{4}-\d{2}-\d{2})(?:-|/|$)', path)] if m)
    for value in candidates:
        try:
            return date.fromisoformat(str(value)[:10]).isoformat()
        except ValueError:
            pass
    return ''


def grouped_attempts(rows):
    groups = []
    months = ('January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December')
    for row in rows:
        day = row['date']
        if not groups or groups[-1]['date'] != day:
            groups.append({'date': day, 'title': str(int(day[8:])) + ' ' + months[int(day[5:7])-1] + ' ' + day[:4]
                           if day else 'Undated attempts', 'rows': []})
        groups[-1]['rows'].append(row)
    return groups


class RewriteHTML(HTMLParser):
    def __init__(self, builder, source, page, headings=False):
        super().__init__(convert_charrefs=False)
        self.builder, self.source, self.page, self.headings = builder, source, page, headings
        self.output, self.links, self.heading_tags = [], [], []
        self.previous_heading = 1

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            url = attrs.get('href', '')
            resolved = self.builder.link(url, self.source, self.page)
            self.links.append(resolved is None)
            if resolved is None:
                tag, attrs = 'span', {'class': 'unavailable'}
            else:
                attrs['href'] = resolved
        if tag == 'img':
            src = attrs.get('src', '')
            resolved = self.builder.resource(src, self.source, self.page)
            if resolved is None:
                self.output.append('<span class="unavailable">' + html.escape(attrs.get('alt', 'Image')) +
                                   ' (not in the public repository)</span>')
                return
            attrs['src'] = resolved
            attrs.setdefault('alt', '')
            attrs.setdefault('loading', 'lazy')
        if self.headings and re.fullmatch('h[1-6]', tag):
            new = min(int(tag[1]) + 1, self.previous_heading + 1, 6)
            self.heading_tags.append((tag, f'h{new}'))
            tag = f'h{new}'
            self.previous_heading = new
        self.output.append('<' + tag + ''.join(' ' + k + ('="' + html.escape(str(v), quote=True) + '"'
                           if v is not None else '') for k, v in attrs.items()) + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'a' and self.links:
            if self.links.pop():
                self.output.append(' (not in the public repository)</span>')
                return
        if self.headings and re.fullmatch('h[1-6]', tag) and self.heading_tags:
            _, tag = self.heading_tags.pop()
        self.output.append('</' + tag + '>')

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append('&' + name + ';')

    def handle_charref(self, name):
        self.output.append('&#' + name + ';')

    def handle_comment(self, data):
        self.output.append('<!--' + data + '-->')

    def handle_decl(self, decl):
        self.output.append('<!' + decl + '>')


class Builder:
    def __init__(self, source, out, kb):
        self.source, self.out, self.kb = source, out, kb
        self.items = kb.index_items()
        self.groups = {k: [x for x in self.items if x['kind'] == k]
                       for k in ('finding', 'question', 'conjecture', 'attempt', 'paper')}
        self.routes = {'README.md': 'index.html', 'knowledge/WORKING-MODEL.md': 'working-model/index.html',
                       'knowledge/DATA.md': 'data.html', 'knowledge/TIMELINE.md': 'timeline/index.html',
                       'CONTRIBUTING.md': 'contribute/index.html', 'REUSE.md': 'reuse/index.html',
                       'THIRD_PARTY_NOTICES.md': 'reuse/notices.html',
                       'knowledge/findings': 'findings/index.html', 'knowledge/questions': 'questions/index.html',
                       FINDINGS_GUIDE: 'findings/index.html',
                       'knowledge/conjectures': 'conjectures/index.html',
                       'knowledge/conjectures/README.md': 'conjectures/rules.html',
                       'knowledge/experiments/registry.json': 'attempts/index.html'}
        for kind, folder in [('finding', 'findings'), ('question', 'questions'), ('conjecture', 'conjectures')]:
            for item in self.groups[kind]:
                self.routes[item['path']] = f"{folder}/{item['id']}.html"
        for item in self.groups['paper']:
            self.routes[item['path']] = 'papers/' + PurePosixPath(item['path']).parent.name + '/index.html'
            for name in ('methods.md', 'claim-evidence-map.md'):
                path = str(PurePosixPath(item['path']).parent / name)
                if source.allowed(path):
                    self.routes[path] = 'papers/' + PurePosixPath(path).parent.name + '/' + name[:-3] + '.html'
        for path in EXPLORE:
            if source.allowed(path):
                self.routes[path] = path
        self.env = jinja2.Environment(loader=SourceTemplates(source), autoescape=True,
                                      keep_trailing_newline=True, newline_sequence='\n')
        self.copied, self.pages, self.unavailable, self.skipped, self.dynamic = {}, {}, set(), [], set()
        self.findings_guide = {'path': FINDINGS_GUIDE, 'mode': 'area', 'reason': 'not in the public repository'}
        self.env.filters['label'] = lambda value: str(value).replace('-', ' ').replace('_', ' ')

    def write(self, path, content):
        target = self.out.joinpath(*PurePosixPath(safe_path(path)).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode('utf-8') if isinstance(content, str) else content)

    def github(self, path):
        kind = 'tree' if path in self.source.dirs else 'blob'
        return f'{REPO}/{kind}/{self.source.commit}/' + quote(path, safe='/')

    def target(self, url, source):
        parsed = urlsplit(html.unescape(url))
        if url.startswith(REPO + '/blob/') or url.startswith(REPO + '/tree/'):
            # Existing repository URLs receive the same publication gate and commit pin.
            tail = parsed.path.split('/', 5)
            if len(tail) == 6:
                return safe_path(tail[5]), parsed
        if parsed.scheme or parsed.netloc:
            return None, parsed
        if not parsed.path:
            return source, parsed
        return safe_path(posixpath.join(posixpath.dirname(source), unquote(parsed.path))), parsed

    def link(self, url, source, page):
        if not url or url.startswith('#'):
            return url
        try:
            target, parsed = self.target(url, source)
        except ValueError:
            self.unavailable.add((source, url))
            return None
        if target is None:
            return url if parsed.scheme in ('http', 'https', 'mailto', 'tel', 'data') or parsed.netloc else None
        if not (self.source.allowed(target) or target in self.source.dirs):
            self.unavailable.add((source, target))
            return None
        if target in self.routes:
            dest = relative_url(self.routes[target], page)
            # JSON Pointers name fields rather than HTML sections.
            fragment = '' if target.endswith('.json') else parsed.fragment
            return urlunsplit(('', '', dest, parsed.query, fragment))
        return self.github(target) + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')

    def resource(self, url, source, page):
        if url.startswith('data:') or url.startswith('#'):
            return url
        try:
            target, parsed = self.target(url, source)
        except ValueError:
            target = None
        if target is None or not self.source.allowed(target):
            self.unavailable.add((source, url))
            return None
        self.copy(target, tracked_only=source in EXPLORE)
        return relative_url(target, page) + ('#' + parsed.fragment if parsed.fragment else '')

    def copy(self, path, tracked_only=False):
        if path in self.copied:
            return
        if not self.source.allowed(path):
            raise ValueError(f'Excluded asset: {path}')
        # Assets referenced by Explore must already be tracked, even in a preview.
        if tracked_only and path not in (self.source.tracked if self.source.worktree else self.source.committed):
            raise ValueError(f'Asset is not tracked: {path}')
        payload = self.source.bytes(path)
        self.copied[path] = hashlib.sha256(payload).hexdigest()
        self.write(path, payload)

    def rendered(self, body, source, page):
        converted = markdown.markdown(body, extensions=['extra', 'sane_lists', 'toc'],
                                      extension_configs={'toc': {'permalink': False}})
        parser = RewriteHTML(self, source, page, headings=True)
        parser.feed(converted)
        return ''.join(parser.output)

    def page(self, path, title, source, template='document.jinja', **values):
        def nav_link(label, dest):
            # Cards and secondary pages belong to the section containing their index.
            current = path == dest
            active = current or (dest.endswith('/index.html') and path.startswith(dest[:-10]))
            return {'label': label, 'url': relative_url(dest, path), 'current': current, 'active': active}
        nav = []
        for label, dest in NAV:
            if isinstance(dest, list):
                children = [nav_link(name, target) for name, target in dest]
                nav.append({'label': label, 'children': children, 'active': any(c['active'] for c in children)})
            else:
                nav.append(nav_link(label, dest))
        context = dict(title=title, page=path, source_url=self.github(source), source_path=source,
                       commit=self.source.commit, commit_date=self.source.date, worktree=self.source.worktree,
                       nav_groups=nav,
                       nav=[(name, relative_url(target, path)) for label, dest in NAV
                            for name, target in (dest if isinstance(dest, list) else [(label, dest)])],
                       css=relative_url('assets/site.css', path), js=relative_url('assets/site.js', path),
                       home=relative_url('index.html', path), repo=REPO, **values)
        self.write(path, self.env.get_template(template).render(**context))
        self.pages[path] = source

    def document(self, source, title=None, **extra):
        if not self.source.allowed(source):
            self.skipped.append({'path': source, 'reason': 'not in the public repository'})
            return
        body = self.kb.frontmatter(self.source.text(source))[1]
        page = self.routes[source]
        self.page(page, title or self.kb.heading(body, source), source,
                  template=extra.pop('template', 'document.jinja'), body=self.rendered(body, source, page), **extra)

    def index_rows(self, kind):
        rows = []
        for item in self.groups[kind]:
            row = {**item['fields'], 'id': item['id'], 'title': item['title'], 'area': item['area'],
                   'status': item['status'], 'path': item['path'], 'source_url': self.github(item['path'])}
            if kind == 'attempt':
                evidence = row.get('evidence', [])
                package = next((p.split('#')[0] for p in evidence if p.startswith('experiments/') and self.source.allowed(p.split('#')[0])), item['path'])
                # A package directory is discoverable even when its first witness is omitted.
                row['url'] = self.github(str(PurePosixPath(package).parent)) if package != item['path'] else self.github(package)
                row['date'] = attempt_date(row)
                # Report candidates go through link(), including omitted and absent reports.
                reports = [p for p in evidence if re.search(r'/(?:REPORT|README)\.md(?:#.*)?$', p)]
                preferred = row.get('package', '').rstrip('/')
                row['report_path'] = next((p for p in reports if PurePosixPath(p.split('#')[0]).name == 'REPORT.md'),
                                          preferred + '/REPORT.md' if preferred else reports[0] if reports else item['path'])
                row['report_url'] = self.link(row['report_path'], 'README.md', 'index.html')
            else:
                row['url'] = PurePosixPath(self.routes[item['path']]).name
                row['claim'] = text_only(section(item['body'], 'Claim' if kind == 'conjecture' else 'Question' if kind == 'question' else 'Finding'))
            rows.append(row)
        if kind == 'attempt':
            # Stable ID order resolves ties without consulting time or file timestamps.
            rows.sort(key=lambda r: r['id'])
            rows.sort(key=lambda r: r['date'], reverse=True)
        return rows

    def findings_sections(self, rows):
        self.findings_guide = {'path': FINDINGS_GUIDE, 'mode': 'area', 'reason': 'not in the public repository'}
        for row in rows:
            row['theme'] = row['area']
        if not self.source.allowed(FINDINGS_GUIDE):
            return None
        try:
            guide = parse_findings_guide(self.source.text(FINDINGS_GUIDE), rows)
        except ValueError as exc:
            self.findings_guide['reason'] = str(exc)
            return None
        page = 'findings/index.html'
        by_id = {r['id']: r for r in rows}
        themes, anchors = [], set()
        for theme in guide['themes']:
            cards = []
            for entry in theme['cards']:
                row = by_id[entry['id']]
                row['theme'] = theme['title']
                row['result'] = text_only(entry['result'])
                cards.append({**row, 'result_html': self.rendered(entry['result'], FINDINGS_GUIDE, page)})
            anchor = markdown.extensions.toc.slugify(theme['title'], '-')
            while anchor in anchors:
                anchor += '-2'
            anchors.add(anchor)
            themes.append({'title': theme['title'], 'anchor': anchor, 'rows': cards,
                           'intro': self.rendered('\n'.join(theme['intro']), FINDINGS_GUIDE, page)})
        other = [row for row in rows if row['id'] not in guide['listed']]
        for row in other:
            row['theme'] = 'Other findings'
        if other:
            themes.append({'title': 'Other findings', 'anchor': 'other-findings', 'rows': other,
                           'intro': '<p>These cards have not yet been placed in the findings guide.</p>'})
        uncarded = guide['uncarded']
        self.findings_guide = {'path': FINDINGS_GUIDE, 'mode': 'guide', 'reason': '',
                               'listed': len(guide['listed']), 'other': len(other)}
        return {'intro': self.rendered(guide['intro'], FINDINGS_GUIDE, page), 'themes': themes,
                'uncarded': {'title': uncarded['title'],
                             'body': self.rendered('\n'.join(uncarded['intro']) + '\n\n' +
                                                   '\n'.join(uncarded['entries']), FINDINGS_GUIDE, page)} if uncarded else None}

    def card(self, item):
        path = self.routes[item['path']]
        history = item['fields'].get('credence_history', [])
        if not isinstance(history, list) or any(not isinstance(row, dict) for row in history):
            raise ValueError(f"Unsupported credence history: {item['path']}")
        claim_url = None
        if item['kind'] == 'question':
            forms = sorted(p for p in self.source.files if p.startswith('.github/ISSUE_TEMPLATE/') and p.endswith(('.yml', '.yaml'))
                           and re.search(r'^name:\s*[\"\x27]?Claim a question', self.source.text(p), re.M))
            if forms:
                claim_url = REPO + '/issues/new?' + urlencode({'template': PurePosixPath(forms[0]).name,
                                                              'title': f"[{item['id']}] Claim: {item['title']}"})
            else:
                self.skipped.append({'path': '.github/ISSUE_TEMPLATE/claim-question.yml', 'reason': 'claim form unavailable'})
        self.page(path, f"{item['id']}: {item['title']}", item['path'], 'card.jinja',
                  item=item, fields=item['fields'], history=history, claim_url=claim_url,
                  body=self.rendered(item['body'], item['path'], path))

    def explore(self, path):
        if not self.source.allowed(path):
            self.skipped.append({'path': path, 'reason': 'not in the public repository'})
            return
        content = self.source.text(path)
        # The two reviewed viewers embed their row data. All dynamic image paths
        # are enumerated, including both the focused drawing and its chart source.
        for match in re.finditer(r'"(focused_path|path|image)"\s*:\s*"([^"\n]+\.(?:png|jpg|jpeg|svg|webp))"', content):
            key, asset = match.groups()
            target = safe_path(posixpath.join(posixpath.dirname(path), asset)) if key == 'image' else safe_path(asset)
            self.copy(target, tracked_only=True)
            self.dynamic.add((path, target))
        # Keep the embedded viewers' existing relative links to downloadable JSON.
        for match in re.finditer(r'(?:href|src)=[\"\x27]([^\"\x27]+\.json)[\"\x27]', content):
            target = safe_path(posixpath.join(posixpath.dirname(path), match[1]))
            if self.source.allowed(target):
                self.copy(target, tracked_only=True)
                self.routes[target] = target
        # Catalogue script templates contain source links as well as static HTML.
        parser = RewriteHTML(self, path, path)
        parser.feed(content)
        content = ''.join(parser.output)
        def dynamic_link(match):
            url = match[1]
            if '${' in url or url.startswith('#'):
                return match[0]
            result = self.link(url, path, path)
            if result is None:
                return 'data-unavailable="not in the public repository"'
            return 'href="' + html.escape(result, quote=True) + '"'
        content = re.sub(r'href="([^"\n]+)"', dynamic_link, content)
        footer = '<footer><p><a href="' + self.github(path) + '">Source on GitHub</a> · ' + self.source.commit[:12] + '</p></footer>'
        # The source viewers populate their cards in JavaScript. Also present
        # their exact embedded rows as a no-script table.
        if path == EXPLORE[0]:
            embedded = re.search(r'<script[^>]*id="catalogue-data"[^>]*>(.*?)</script>', content, re.S)
            rows = json.loads(embedded[1])['rows'] if embedded else []
            columns = [('sign_id', 'Sign'), ('meaning', 'Claim'), ('tier', 'Status')]
        else:
            embedded = re.search(r'const rows=(\[.*?\]);\s*const q=', content, re.S)
            rows = json.loads(embedded[1]) if embedded else []
            columns = [('rank', 'Rank'), ('code', 'Code'), ('alternatives', 'Code alternatives'),
                       ('rank_alternatives', 'Rank alternatives'), ('pdf_page', 'PDF page'),
                       ('column', 'Column'), ('row', 'Row'), ('numeric_confidence', 'Confidence')]
        if not rows:
            raise ValueError(f'Viewer embedded rows unavailable: {path}')
        fallback = '<noscript><h2>Viewer data</h2><table><thead><tr>' + ''.join('<th scope="col">' + label + '</th>' for _, label in columns) + '</tr></thead><tbody>'
        fallback += ''.join('<tr>' + ''.join('<td>' + html.escape(str(row.get(key, ''))) + '</td>' for key, _ in columns) + '</tr>' for row in rows)
        fallback += '</tbody></table><p><a href="' + self.github(posixpath.join(posixpath.dirname(path), 'catalogue-data.json' if path == EXPLORE[0] else 'reference.json')) + '">Viewer data on GitHub</a></p></noscript>'
        suffix = fallback + footer
        end = '</body>' if '</body>' in content else '</html>' if '</html>' in content else None
        content = content.replace(end, suffix + end) if end else content + '\n' + suffix
        self.write(path, content)
        self.pages[path] = path

    def build(self):
        for name in ('site.css', 'site.js'):
            self.write('assets/' + name, self.source.bytes('site/static/' + name))
        indexes = {kind: self.index_rows(kind) for kind in ('finding', 'question', 'conjecture', 'attempt')}
        findings = self.findings_sections(indexes['finding'])
        for kind, folder in [('finding', 'findings'), ('question', 'questions'), ('conjecture', 'conjectures'), ('attempt', 'attempts')]:
            self.write(folder + '/index.json', dumps(indexes[kind]))
            for item in self.groups[kind] if kind != 'attempt' else []:
                self.card(item)
            filters = (['area', 'kind', 'difficulty', 'data_access', 'priority'] if kind == 'question' else
                       ['theme', 'status'] if kind == 'finding' else [])
            visible_rows = [row for row in indexes[kind] if row['status'] in ('open', 'claimed')] if kind == 'question' else indexes[kind]
            values = {field: sorted({str(row.get(field, '')) for row in visible_rows if row.get(field, '') != ''}) for field in filters}
            listing_source = dict(finding='knowledge/findings', question='knowledge/questions', conjecture='knowledge/conjectures', attempt='knowledge/experiments/registry.json')[kind]
            if kind == 'finding' and findings:
                listing_source = FINDINGS_GUIDE
            self.page(folder + '/index.html', dict(finding='Findings', question='Open questions', conjecture='Conjectures', attempt='Registry')[kind],
                      listing_source,
                      'listing.jinja', kind=kind, rows=visible_rows, filters=values, index_url='index.json',
                      findings=findings, attempt_groups=grouped_attempts(visible_rows) if kind == 'attempt' else [])
        readme = self.source.text('README.md')
        purpose = readme.split('\n', 1)[1].split('\n## ', 1)[0].strip()
        model = self.source.text('knowledge/WORKING-MODEL.md') if self.source.allowed('knowledge/WORKING-MODEL.md') else ''
        model = model.replace('\r\n', '\n')
        headlines = []
        for m in re.finditer(r'^## ([^\n]+)\n+(.+?)(?=\n\n|\Z)', model, re.M | re.S):
            if re.search(r'\bCredence\s+[0-9]', m[2]):
                headlines.append({'heading': m[1], 'body': self.rendered(m[2], 'knowledge/WORKING-MODEL.md', 'index.html')})
        bootstrap = next((line for line in readme.splitlines() if line.startswith('For agents:')), '')
        self.page('index.html', self.kb.heading(readme, 'Indus Valley script'), 'README.md', 'home.jinja',
                  purpose=self.rendered(purpose, 'README.md', 'index.html'),
                  standing=self.rendered(section(readme, 'Where things stand'), 'README.md', 'index.html'),
                  headlines=headlines, conjectures=indexes['conjecture'], bootstrap=bootstrap,
                  # Coordination, release and preservation records stay in the registry only.
                  recent=[row for row in indexes['attempt'] if row['status'] != 'record'][:10],
                  counts={'findings': len(indexes['finding']), 'conjectures': len(indexes['conjecture']),
                          'open questions': sum(r.get('status') in ('open', 'claimed') for r in indexes['question']),
                          'attempts': len(indexes['attempt'])})
        for source in ('knowledge/WORKING-MODEL.md', 'knowledge/DATA.md', 'knowledge/TIMELINE.md',
                       'REUSE.md', 'THIRD_PARTY_NOTICES.md', 'knowledge/conjectures/README.md'):
            if source == 'REUSE.md':
                licence = re.search(r'No project-wide licence has been chosen\.', readme)
                self.document(source, template='reuse.jinja', licence=licence[0] if licence else '', notices='notices.html')
            elif source != 'knowledge/DATA.md':
                self.document(source)
        data_path = 'knowledge/DATA.md'
        manifest_rows = []
        if MANIFEST in (self.source.tracked if self.source.worktree else self.source.committed):
            manifest_rows = json.loads(self.source.text(MANIFEST, metadata=True)).get('sources', [])
        else:
            self.skipped.append({'path': MANIFEST, 'reason': 'not tracked; metadata table omitted'})
        if self.source.allowed(data_path):
            self.page('data.html', 'Data', data_path, 'data.jinja', rows=manifest_rows,
                      body=self.rendered(self.source.text(data_path), data_path, 'data.html'))
        else:
            self.skipped.append({'path': data_path, 'reason': 'not in the public repository'})
        contribute = self.source.text('CONTRIBUTING.md')
        agents = self.source.text('AGENTS.md')
        self.page('contribute/index.html', 'Contribute', 'CONTRIBUTING.md', 'contribute.jinja',
                  body=self.rendered(contribute, 'CONTRIBUTING.md', 'contribute/index.html'), bootstrap=bootstrap,
                  skills=self.rendered(section(agents, 'Repository skills'), 'AGENTS.md', 'contribute/index.html'))
        for path in EXPLORE:
            self.explore(path)
        catalogue_readme = 'experiments/2026-10-11-bonta-adversarial/README.md'
        catalogue_text = self.source.text(catalogue_readme).replace('\r\n', '\n') if self.source.allowed(catalogue_readme) else ''
        catalogue_intro = catalogue_text.split('\n\n', 2)[1] if '\n\n' in catalogue_text else ''
        # The frozen chart viewer has no adjacent README. Its description is in the root README.
        chart_sentence = re.search(r'The \[chart atlas\]\([^)]+\)[^.]+\.', readme)
        descriptions = (next((s.strip() for s in re.split(r'(?<=\.)\s+', catalogue_intro)
                              if s.startswith('Fifty-six ')), text_only(catalogue_intro)),
                        text_only(chart_sentence[0]) if chart_sentence else 'The chart atlas is part of the first investigation’s recorded outputs.')
        atlas_script = LIVING_ATLAS + '/mapping/atlas.js'
        if self.source.allowed(atlas_script):
            if external_script_resource(self.source.text(atlas_script)):
                self.skipped.append({'path': LIVING_ATLAS + '/index.html',
                                     'reason': 'Living atlas not packaged: the optional street basemap loads external OpenStreetMap tiles; site resources must be local.'})
            else:
                self.skipped.append({'path': LIVING_ATLAS + '/index.html',
                                     'reason': 'Living atlas source changed; its full resource closure needs a new publication review before packaging.'})
        self.page('explore/index.html', 'Explore', 'README.md', 'explore.jinja',
                  viewers=[{'name': label, 'url': relative_url(path, 'explore/index.html'), 'description': description}
                           for path, label, description in zip(EXPLORE, ('Reviewed sign catalogue', 'Chart atlas'), descriptions)
                           if path in self.pages])
        papers = []
        pdfs = [{'name': PurePosixPath(path).name, 'url': self.github(path)} for path in sorted(self.source.files)
                if path.startswith('output/pdf/') and path.endswith('.pdf')]
        for item in self.groups['paper']:
            paper_links = [{'label': name[:-3].replace('-', ' '), 'url': PurePosixPath(self.routes[str(PurePosixPath(item['path']).parent/name)]).name}
                           for name in ('methods.md', 'claim-evidence-map.md') if str(PurePosixPath(item['path']).parent/name) in self.routes]
            self.document(item['path'], item['title'], template='paper.jinja', links=paper_links, pdfs=pdfs)
            for name in ('methods.md', 'claim-evidence-map.md'):
                path = str(PurePosixPath(item['path']).parent / name)
                if path in self.routes:
                    self.document(path)
            papers.append({'title': item['title'], 'url': relative_url(self.routes[item['path']], 'papers/index.html'),
                           'links': [{'label': name[:-3].replace('-', ' '), 'url': relative_url(self.routes[str(PurePosixPath(item['path']).parent/name)], 'papers/index.html')}
                                     for name in ('methods.md', 'claim-evidence-map.md') if str(PurePosixPath(item['path']).parent/name) in self.routes]})
        self.page('papers/index.html', 'Papers', 'README.md', 'papers.jinja', papers=papers, pdfs=pdfs)
        self.page('404.html', 'Page not found', 'README.md', body='<p><a href="index.html">Home</a></p>')
        self.write('.nojekyll', b'')
        if self.source.allowed('llms.txt'):
            llms = self.source.text('llms.txt')
        else:
            llms = '# ' + self.kb.heading(readme, 'Indus research') + '\n\n' + bootstrap + '\n'
            self.skipped.append({'path': 'llms.txt', 'reason': 'not in the public repository; only bootstrap and index links emitted'})
        def llm_link(m):
            resolved = self.link(m[2], 'llms.txt', 'llms.txt')
            if resolved is None:
                return m[1] + ' (not in the public repository)'
            if not urlsplit(resolved).scheme:
                resolved = SITE + resolved
            return '[' + m[1] + '](' + resolved + ')'
        llms = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', llm_link, llms)
        llms += '\n## JSON indexes\n\n' + ''.join(f'- [{folder}]({SITE}{folder}/index.json)\n' for folder in ('findings', 'questions', 'conjectures', 'attempts'))
        self.write('llms.txt', llms)
        self.write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                   ''.join('<url><loc>' + html.escape(SITE + quote(path, safe='/')) + '</loc><lastmod>' + self.source.date[:10] + '</lastmod></url>\n'
                           for path in sorted(self.pages) if path != '404.html') + '</urlset>\n')
        self.write('site-build.json', dumps({'schema_version': 1, 'source_commit': self.source.commit, 'source_date': self.source.date,
                   'mode': 'worktree' if self.source.worktree else 'commit', 'public_files': sorted(self.source.files),
                   'omissions': self.source.omissions, 'inputs': self.source.inputs, 'copied': self.copied,
                   'pages': self.pages, 'dynamic_assets': sorted(self.dynamic), 'skipped': self.skipped,
                   'findings_guide': self.findings_guide,
                   'unavailable_links': [{'source': s, 'target': t} for s, t in sorted(self.unavailable)]}))


class InspectHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.resources, self.ids, self.images, self.headings = [], [], set(), [], []
        self.lang = None
        self.source = False
        self.scripts, self.styles = [], []
        self.active = None

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        for key in RESOURCE_ATTRS:
            if attrs.get(key):
                if key == 'data' and tag != 'object':
                    continue
                self.resources.extend([part.strip().split()[0] for part in attrs[key].split(',')] if key == 'srcset' else [attrs[key]])
        if tag == 'link' and attrs.get('href'):
            self.resources.append(attrs['href'])
        if tag in ('use', 'image'):
            self.resources.extend(attrs[key] for key in ('href', 'xlink:href') if attrs.get(key))
        if attrs.get('data-index'):
            self.resources.append(attrs['data-index'])
        if attrs.get('style'):
            self.resources.extend(css_urls(attrs['style']))
        if tag == 'img':
            self.images.append(attrs)
        if re.fullmatch('h[1-6]', tag):
            self.headings.append(int(tag[1]))
        if tag in ('script', 'style'):
            self.active = tag
        if tag == 'base':
            self.resources.append(attrs.get('href', '/'))

    def handle_endtag(self, tag):
        if tag == self.active:
            self.active = None

    def handle_data(self, data):
        if 'Source on GitHub' in data:
            self.source = True
        if self.active == 'script':
            self.scripts.append(data)
        if self.active == 'style':
            self.styles.append(data)


def css_urls(content):
    return re.findall(r'url\(\s*[\"\x27]?([^\)\"\x27]+)', content) + re.findall(r'@import\s+[\"\x27]([^\"\x27]+)', content)


def external_script_resource(content):
    # Tile layers request images dynamically, including when enabled by a control.
    return bool(re.search(r'\b(?:fetch|WebSocket|EventSource|importScripts|tileLayer)\s*\(\s*[\"\x27](?:https?:)?//', content))


def check(out, root=ROOT):
    metadata = json.loads((out / 'site-build.json').read_text(encoding='utf-8'))
    commit = metadata['source_commit']
    committed = set(tree_inventory(commit, root))
    public = set(metadata['public_files'])
    if metadata['mode'] == 'commit' and not public <= committed:
        raise ValueError('Build inventory contains paths outside its commit')
    if metadata['mode'] == 'worktree':
        eligible = {p.decode('utf-8') for p in git('ls-files', '--cached', '--others', '--exclude-standard', '-z', root=root).split(b'\0') if p}
        if not public <= eligible:
            raise ValueError('Preview inventory contains ignored or absent source paths')
    omissions = metadata['omissions']
    errors = []
    expected_omissions = json.loads(git('show', f'{commit}:{OMISSIONS}', root=root).decode('utf-8-sig'))['targets']
    if metadata['mode'] == 'commit' and omissions != expected_omissions:
        errors.append('Omissions differ from the build commit')
    def excluded(p):
        return p == 'data' or p.startswith('data/') or any(p == x.rstrip('/') or p.startswith(x.rstrip('/') + '/') for x in omissions)
    for p in public:
        if excluded(p):
            errors.append(f'Excluded public path: {p}')
    files = {p.relative_to(out).as_posix(): p for p in out.rglob('*') if p.is_file()}
    inspectors = {}
    for name, p in sorted(files.items()):
        if excluded(name):
            errors.append(f'Excluded output: {name}')
        if p.suffix == '.html':
            parser = InspectHTML()
            parser.feed(p.read_text(encoding='utf-8'))
            inspectors[name] = parser
            if parser.lang != 'en':
                errors.append(f'{name}: missing lang=en')
            if not parser.source:
                errors.append(f'{name}: missing source link')
            if any('alt' not in attrs for attrs in parser.images):
                errors.append(f'{name}: image without alt')
            if parser.headings and (parser.headings[0] != 1 or any(b > a+1 for a, b in zip(parser.headings, parser.headings[1:]))):
                errors.append(f'{name}: heading order skips a level')
    preview_targets = set()
    def verify(url, origin, resource=False):
        parsed = urlsplit(html.unescape(url))
        if parsed.scheme == 'data' or url.startswith('#') and resource:
            return
        if parsed.netloc or parsed.scheme:
            if resource:
                errors.append(f'{origin}: external resource {url}')
            if url.startswith(REPO + '/blob/') or url.startswith(REPO + '/tree/'):
                match = re.match(re.escape(REPO) + r'/(blob|tree)/([^/]+)/(.*)', urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', '')))
                if not match or match[2] != commit:
                    errors.append(f'{origin}: unpinned GitHub link {url}')
                elif match:
                    target = unquote(match[3]).rstrip('/')
                    exists = target in public if match[1] == 'blob' else any(p.startswith(target + '/') for p in public)
                    if not exists or excluded(target):
                        errors.append(f'{origin}: GitHub target not public {target}')
                    elif metadata['mode'] == 'worktree' and target not in committed and not any(p.startswith(target + '/') for p in committed):
                        preview_targets.add(target)
            return
        try:
            target = safe_path(posixpath.join(posixpath.dirname(origin), unquote(parsed.path))) if parsed.path else origin
        except ValueError:
            errors.append(f'{origin}: unsafe URL {url}')
            return
        if target not in files:
            errors.append(f'{origin}: missing target {target}')
        elif parsed.fragment and target in inspectors and unquote(parsed.fragment) not in inspectors[target].ids:
            # The catalogue creates Wxxx anchors while rendering its embedded rows.
            if not (target == EXPLORE[0] and re.fullmatch('W[0-9]{3}', parsed.fragment)):
                errors.append(f'{origin}: missing fragment {target}#{parsed.fragment}')
    for name, parser in inspectors.items():
        for url in parser.links:
            verify(url, name)
        for url in parser.resources:
            verify(url, name, True)
        for block in parser.styles:
            for url in css_urls(block):
                verify(url, name, True)
        for block in parser.scripts:
            # Static script-template hyperlinks and literal dynamic image paths.
            for url in re.findall(r'href=[\"\x27]([^\"\x27]+)', block):
                if '${' not in url:
                    verify(url, name)
            if external_script_resource(block):
                errors.append(f'{name}: script loads an external resource')
    for name, path in files.items():
        if path.suffix == '.css':
            for url in css_urls(path.read_text(encoding='utf-8')):
                verify(url, name, True)
        if path.suffix == '.js':
            block = path.read_text(encoding='utf-8')
            if external_script_resource(block):
                errors.append(f'{name}: script loads an external resource')
        if path.suffix == '.json' and name.endswith('/index.json'):
            for row in json.loads(path.read_text(encoding='utf-8')):
                verify(row['url'], name)
                verify(row['source_url'], name)
                if row.get('report_url'):
                    verify(row['report_url'], 'index.html')
    for origin, target in metadata['dynamic_assets']:
        if target not in files or target not in metadata['copied']:
            errors.append(f'{origin}: missing dynamic asset {target}')
    for target, digest in metadata['copied'].items():
        if target not in public or excluded(target):
            errors.append(f'Copied source not public: {target}')
        elif target not in files or hashlib.sha256(files[target].read_bytes()).hexdigest() != digest:
            errors.append(f'Copied asset changed: {target}')
    sizes = sorted(({'path': n, 'bytes': p.stat().st_size} for n, p in files.items()), key=lambda x: (-x['bytes'], x['path']))
    total = sum(row['bytes'] for row in sizes)
    if total >= 1_000_000_000:
        errors.append('Site exceeds 1 GB')
    result = {'ok': not errors, 'source_commit': commit, 'mode': metadata['mode'], 'pages': len(inspectors),
              'files': len(files), 'bytes': total, 'largest_files': sizes[:10], 'errors': sorted(set(errors)),
              'unavailable_links': len(metadata['unavailable_links']), 'skipped': metadata['skipped']}
    if metadata['mode'] == 'worktree':
        result['preview_targets_absent_at_commit'] = len(preview_targets)
    return result


def build_to(source, out):
    if out.exists() and any(out.iterdir()):
        if not (out / 'site-build.json').is_file():
            raise ValueError('Output must be empty or contain a previous site build')
        # The explicitly named build directory is the only recursive-delete target.
        resolved = out.resolve()
        if resolved == source.root.resolve() or source.root.resolve().is_relative_to(resolved) or out.is_symlink():
            raise ValueError('Output overlaps the repository root')
        if any((source.root / p).resolve().is_relative_to(resolved) for p in source.files):
            raise ValueError('Output overlaps public source files')
        shutil.rmtree(resolved)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'site-build.json').write_text('{}\n', encoding='utf-8')
    with kb_index(source) as kb:
        Builder(source, out, kb).build()
    return check(out, source.root)


def publish(root=ROOT):
    source = GitSource(root=root)
    with tempfile.TemporaryDirectory(prefix='indus-site-publish-') as tmp:
        out = Path(tmp) / 'site'
        result = build_to(source, out)
        if not result['ok']:
            raise ValueError(dumps(result))
        # Build trees directly. Neither the current index nor a worktree is involved.
        nodes = {}
        for path in sorted(p for p in out.rglob('*') if p.is_file()):
            parts = path.relative_to(out).parts
            node = nodes
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = git('hash-object', '-w', '--stdin', root=root, payload=path.read_bytes()).decode().strip()
        def make_tree(node):
            records = []
            for name, value in sorted(node.items(), key=lambda pair: pair[0] + ('/' if isinstance(pair[1], dict) else '')):
                mode, kind, oid = ('040000', 'tree', make_tree(value)) if isinstance(value, dict) else ('100644', 'blob', value)
                records.append(f'{mode} {kind} {oid}\t{name}'.encode('utf-8') + b'\0')
            return git('mktree', '-z', root=root, payload=b''.join(records)).decode().strip()
        tree = make_tree(nodes)
        old_result = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', '-C', str(root), 'rev-parse', '--verify', 'refs/heads/gh-pages'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        old = old_result.stdout.decode().strip() if old_result.returncode == 0 else None
        env = os.environ.copy()
        # The site commit carries the identity of the source commit's author, so it is attributed to the maintainer who published it.
        name, email = git('log', '-1', '--format=%an%x00%ae', source.commit, root=root).decode('utf-8').strip().split('\0')
        env.update(GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email,
                   GIT_AUTHOR_DATE=source.date, GIT_COMMITTER_DATE=source.date)
        args = ['commit-tree', tree] + (['-p', old] if old else [])
        new = git(*args, root=root, payload=f'Build website from {source.commit}\n'.encode(), env=env).decode().strip()
        git('update-ref', 'refs/heads/gh-pages', new, old or '0' * 40, root=root)
        return {**result, 'published_local_commit': new, 'previous_local_commit': old, 'tree': tree, 'pushed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('_site'))
    parser.add_argument('--worktree', action='store_true')
    parser.add_argument('--check', type=Path, metavar='DIRECTORY')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if sum((args.worktree, args.check is not None, args.publish)) > 1:
        parser.error('--worktree, --check and --publish are separate commands')
    try:
        result = check(args.check.resolve()) if args.check else publish() if args.publish else build_to(GitSource(args.worktree), args.out.resolve())
        print(dumps(result), end='')
        return 0 if result['ok'] else 1
    except (ValueError, OSError, KeyError, jinja2.TemplateNotFound) as exc:
        print(dumps({'ok': False, 'error': str(exc)}), end='')
        return 1


if __name__ == '__main__':
    sys.exit(main())
