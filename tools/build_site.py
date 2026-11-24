"""Build the public research website from a Git-selected source snapshot."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date
import hashlib
import html
from html.parser import HTMLParser
import importlib.abc
import importlib.util
import json
import math
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
SITE_PATH_PREFIX = urlsplit(SITE).path  # '/indus-valley-script/'
OMISSIONS = 'maintenance/2026-10-11-public-release/public-omissions.json'
MANIFEST = 'data/MANIFEST.json'
EXPLORE = ('experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html',
           'output/chart_atlas/index.html')
RELAY_VIEWER = 'presentations/2026-10-13-relay-visualization/run-v1/index.html'
FINDINGS_GUIDE = 'knowledge/findings/README.md'
VOCABULARY_PATH = 'knowledge/registry/VOCABULARY.md'
LIVING_ATLAS = 'experiments/2026-10-26-indus-living-atlas'
# Atlas pages and the tracked files they load, published at their repository paths.
ATLAS_PAGES = ('index.html', 'research.html', 'reconstruction/index.html', 'reconstruction/run-v5/index.html')
ATLAS_ASSETS = ('mapping/atlas.css', 'mapping/atlas.js', 'mapping/current-data.js',
                'mapping/vendor/leaflet/leaflet.css', 'mapping/vendor/leaflet/leaflet.js',
                'mapping/vendor/leaflet/leaflet.js.map', 'mapping/vendor/leaflet/LICENSE',
                *(f'mapping/vendor/leaflet/images/{name}.png'
                  for name in ('layers', 'layers-2x', 'marker-icon', 'marker-icon-2x', 'marker-shadow')))
# The site copy drops the optional online street basemap so that every map resource is local.
ATLAS_STREET_CONTROL = '<label class="check"><input id="modern" type="checkbox"> Modern street basemap <small>online</small></label>'
ATLAS_STREET_HANDLER = re.compile(r'\r?\n  \$\("modern"\)\.addEventListener\("change",e=>\{.*?'
                                  r'Ancient rivers are not reconstructed";\}\r?\n  \}\);', re.S)
RELAY_FONT_LINKS = re.compile(r'<link[^>]+href="https://fonts\.(?:googleapis|gstatic)\.com[^"]*"[^>]*>\s*', re.I)

# A group has children; a direct entry has a destination. Native details keep menus usable without JS.
NAV = [
    ('Home', 'index.html'),
    ('Explore', 'explore/index.html'),
    ('Findings', 'findings/index.html'),
    ('Ideas', [('Working model', 'working-model/index.html'), ('Conjectures', 'conjectures/index.html')]),
    ('Questions', 'questions/index.html'),
    ('Record', [('Papers', 'papers/index.html'), ('Registry', 'attempts/index.html'),
                ('Data', 'data.html'), ('Timeline', 'timeline/index.html')]),
    ('Participate', [('Agent hub', 'agents/index.html'), ('Agent rules', 'agents/rules.html'),
                     ('Contribute', 'contribute/index.html'), ('Reuse & licence', 'reuse/index.html')]),
]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
RESOURCE_ATTRS = {'src', 'poster', 'data', 'srcset'}
DEFAULT_DESC = ('Open, source-linked research on the Indus civilisation and its undeciphered script: '
                'findings, testable conjectures, interactive atlases, and open tasks for humans and AI agents.')
DATA_ACCESS_LEGEND = {
    'none-needed': 'Executable from repository files alone without external downloads.',
    'public': 'Uses public or openly retrievable sources alongside tracked repository files.',
    'local-only': 'Requires local acquired corpora or scans kept outside Git (see REPRODUCING.md).',
    'acquire': 'Requires acquiring a printed volume, archive scan, or licensed dataset not yet held.',
    'fieldwork': 'Requires new physical inspection, excavation, or museum access.',
}
# Paper-specific PDF pairings (only show PDFs that belong to a given manuscript).
PAPER_PDFS = {
    '005': ('indus_settlement_survey_gaps_2026-10-11.pdf',),
}


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


def site_absolute_path(target):
    return SITE_PATH_PREFIX + quote(safe_path(target), safe='/')


def site_full_url(target):
    if target == 'index.html':
        return SITE + 'index.html'
    return SITE + quote(safe_path(target), safe='/')


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
        self._cat_proc = None
        self.omissions = []
        self.omissions = json.loads(self.text(OMISSIONS))['targets']
        self.files = {p for p in self.files if not self.excluded(p)}
        if worktree:
            self.files = {p for p in self.files if self.root.joinpath(*PurePosixPath(p).parts).is_file()
                          and not self.root.joinpath(*PurePosixPath(p).parts).is_symlink()}
        self.dirs = {str(parent) for p in self.files for parent in PurePosixPath(p).parents if str(parent) != '.'}

    def close(self):
        proc = self._cat_proc
        self._cat_proc = None
        if proc is not None:
            try:
                if proc.stdin:
                    proc.stdin.close()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
                proc.wait()

    def _read_blob(self, oid):
        if self._cat_proc is None or self._cat_proc.poll() is not None:
            self._cat_proc = subprocess.Popen(
                ['git', '-c', f'safe.directory={self.root.as_posix()}', '-C', str(self.root), 'cat-file', '--batch'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
        self._cat_proc.stdin.write(f'{oid}\n'.encode('ascii'))
        self._cat_proc.stdin.flush()
        header = self._cat_proc.stdout.readline().decode('utf-8', 'replace').strip()
        parts = header.split()
        if len(parts) < 3 or parts[1] != 'blob':
            raise ValueError(f'Unable to read git blob {oid}: {header}')
        size = int(parts[2])
        data = self._cat_proc.stdout.read(size)
        # Consume trailing newline emitted by git cat-file --batch.
        self._cat_proc.stdout.read(1)
        if len(data) != size:
            raise ValueError(f'Truncated git blob {oid}')
        return data

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
                oid = self.committed.get(path)
                if oid:
                    self.cache[path] = self._read_blob(oid)
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
    saved = sys.modules.get('storage_paths')
    if source.allowed('tools/storage_paths.py'):
        sp_spec = importlib.util.spec_from_loader('storage_paths', None)
        sp_mod = importlib.util.module_from_spec(sp_spec)
        sp_mod.__file__ = str(source.root / 'tools/storage_paths.py')
        exec(compile(source.text('tools/storage_paths.py'), sp_mod.__file__, 'exec'), sp_mod.__dict__)
        sys.modules['storage_paths'] = sp_mod
    try:
        spec = importlib.util.spec_from_loader('site_kb', GitModuleLoader(source))
        kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kb)
        kb.ROOT = GitDirectory(source)
        kb.read = lambda path: source.text(str(path))
        kb.relative = lambda path: str(path)
        yield kb
    finally:
        if saved is None:
            sys.modules.pop('storage_paths', None)
        else:
            sys.modules['storage_paths'] = saved


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


def strip_leading_h1(body):
    """Remove a leading level-1 Markdown heading when the page template renders it as <h1>."""
    stripped = body.lstrip('\ufeff \t\r\n')
    match = re.match(r'^#\s+[^\n]+(?:\r?\n)+', stripped)
    return (stripped[match.end():], True) if match else (body, False)


def text_only(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '',
                  markdown.markdown(str(value), extensions=['extra'])))).strip()


def trim_desc(value, limit=185):
    clean = re.sub(r'\s+', ' ', str(value or '')).strip()
    if len(clean) <= limit:
        return clean
    cut = clean[:limit - 1].rsplit(' ', 1)[0]
    return cut.rstrip('.,;:') + '…'


def reading_minutes(text):
    words = len(re.findall(r'\b\w+\b', text_only(text)))
    return max(1, math.ceil(words / 220))


def extract_toc(html_fragment):
    items = []
    for m in re.finditer(r'<h2\s+[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', html_fragment, re.S):
        label = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', m[2]))).strip()
        if label:
            items.append({'id': m[1], 'label': label})
    return items


def credence_pct(value):
    try:
        return max(0, min(100, int(round(float(value) * 100))))
    except (TypeError, ValueError):
        return None


def credence_chart_svg(history):
    """Build a static, inline SVG credence trajectory chart when 2+ points exist."""
    points = []
    for row in history or []:
        try:
            val = max(0.0, min(1.0, float(row.get('value'))))
        except (TypeError, ValueError):
            continue
        points.append({'date': str(row.get('date', '')), 'value': val})
    if len(points) < 2:
        return ''
    w, h = 580, 156
    left, right, top, bottom = 46, 36, 18, 32
    inner_w, inner_h = w - left - right, h - top - bottom
    coords = []
    for idx, pt in enumerate(points):
        x = left + (inner_w * idx / (len(points) - 1))
        y = top + inner_h * (1.0 - pt['value'])
        coords.append((x, y, pt))
    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in coords)
    area = f'{coords[0][0]:.1f},{top + inner_h:.1f} ' + poly + f' {coords[-1][0]:.1f},{top + inner_h:.1f}'
    lines = [
        f'<svg class="credence-chart" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="Credence history from {points[0]["value"]:.2f} to {points[-1]["value"]:.2f}">',
    ]
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        ty = top + inner_h * (1.0 - tick)
        lines.append(f'<line x1="{left}" y1="{ty:.1f}" x2="{w - right}" y2="{ty:.1f}" class="cc-grid"/>')
        lines.append(f'<text x="{left - 8}" y="{ty + 4:.1f}" text-anchor="end" class="cc-axis">{tick:.2f}</text>')
    lines.append(f'<polygon points="{area}" class="cc-area"/>')
    lines.append(f'<polyline points="{poly}" class="cc-line"/>')
    for idx, (x, y, pt) in enumerate(coords):
        cls = 'cc-dot cc-dot-last' if idx == len(coords) - 1 else 'cc-dot'
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="{cls}"><title>{html.escape(pt["date"])}: {pt["value"]:.2f}</title></circle>')
        label_y = y - 9 if pt['value'] < 0.85 else y + 16
        lines.append(f'<text x="{x:.1f}" y="{label_y:.1f}" text-anchor="middle" class="cc-val">{pt["value"]:.2f}</text>')
        if idx in (0, len(coords) - 1) or len(coords) <= 4:
            lines.append(f'<text x="{x:.1f}" y="{h - 8}" text-anchor="middle" class="cc-date">{html.escape(pt["date"])}</text>')
    lines.append('</svg>')
    return ''.join(lines)


def parse_status_classes(vocab_text):
    """Parse verbatim status-class definitions from VOCABULARY.md."""
    sec = section(vocab_text, 'Status classes')
    slug_map = {
        'Proposed': 'proposed', 'Synthetic': 'synthetic', 'Exploratory': 'exploratory',
        'Frozen evaluation': 'frozen-evaluation', 'Failed': 'failed', 'Superseded': 'superseded',
        'Verified computation': 'verified-computation',
    }
    rows = []
    for line in sec.splitlines():
        m = re.match(r'^-\s+([^:]+):\s+(.+)$', line.strip())
        if m and m[1] in slug_map:
            rows.append({'slug': slug_map[m[1]], 'label': m[1], 'definition': m[2].strip()})
    # Parse the two extra classes documented in the prose paragraph.
    extra = re.search(r'Source review \(`source-review`\) is ([^.]+\.)\s+Record \(`record`\) is ([^.]+\.)', sec)
    if extra:
        rows.append({'slug': 'source-review', 'label': 'Source review', 'definition': extra[1][0].upper() + extra[1][1:]})
        rows.append({'slug': 'record', 'label': 'Record', 'definition': extra[2][0].upper() + extra[2][1:]})
    return rows


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


def parse_paper_questions(readme_text):
    """Extract manuscript question summaries from the README table."""
    questions = {}
    for m in re.finditer(r'^\|\s*\[(\d{3})\]\((papers/[^)]+)\)\s*\|\s*(.+?)\s*\|$', readme_text, re.M):
        questions[safe_path(m[2])] = {'number': m[1], 'question': text_only(m[3])}
    return questions


def make_agent_prompt(question=None):
    if question is None:
        return (
            f'Clone {REPO} and read AGENTS.md, CONTRIBUTING.md, knowledge/DATA.md, '
            'knowledge/editorial/WRITING.md, and knowledge/experiments/registry.json. '
            'Run `python tools/kb.py next --data-access public` (or `--data-access none-needed`) to find a task '
            'executable without restricted local corpora. Check GitHub Issues for the chosen Q-ID and claim it by '
            'opening or commenting on the issue with the Q-ID in the title (claims lapse after 7 days without an update). '
            'Put your protocol and outputs in a new dated folder `experiments/YYYY-MM-DD-short-slug/` plus your new card files '
            '(never edit generated `registry.json` or `MAP.md`), disclose your model and harness in `authors`, and run '
            '`python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, and '
            '`python tools/verify_knowledge_repo.py --output <your new verification path>` before opening a pull request.'
        )
    qid = question['id']
    title = question['title']
    return (
        f'Clone {REPO} and read AGENTS.md, CONTRIBUTING.md, and knowledge/editorial/WRITING.md. '
        f'Inspect {qid} ("{title}") with `python tools/kb.py show {qid}`, check GitHub Issues ({REPO}/issues?q=is%3Aissue+{qid}) '
        f'to confirm no active claim exists, and claim {qid} by opening or commenting on an issue with {qid} in the title '
        '(claims lapse after 7 days without an update). Read knowledge/experiments/registry.json and linked prior attempts before running. '
        'Put all outputs in a new dated folder `experiments/YYYY-MM-DD-short-slug/` plus your new card files, disclose your model and '
        'harness in `authors`, and run `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, '
        'and `python tools/verify_knowledge_repo.py --output <your new verification path>` before opening a pull request.'
    )


class RewriteHTML(HTMLParser):
    def __init__(self, builder, source, page, headings=False, shift_headings=True, strip_scripts=False):
        super().__init__(convert_charrefs=False)
        self.builder, self.source, self.page = builder, source, page
        self.headings, self.shift_headings, self.strip_scripts = headings, shift_headings, strip_scripts
        self.output, self.links, self.heading_tags = [], [], []
        self.previous_heading = 1
        self._in_stripped_script = False

    def handle_starttag(self, tag, attrs):
        if self.strip_scripts and tag.lower() == 'script':
            self._in_stripped_script = True
            return
        if self._in_stripped_script:
            return
        attrs = dict(attrs)
        if self.strip_scripts:
            attrs = {k: v for k, v in attrs.items() if not k.lower().startswith('on')}
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
            base = int(tag[1]) + (1 if self.shift_headings else 0)
            new = max(2, min(base, self.previous_heading + 1, 6))
            self.heading_tags.append((tag, f'h{new}'))
            tag = f'h{new}'
            self.previous_heading = new
        self.output.append('<' + tag + ''.join(' ' + k + ('="' + html.escape(str(v), quote=True) + '"'
                           if v is not None else '') for k, v in attrs.items()) + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and not self._in_stripped_script:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.strip_scripts and tag.lower() == 'script':
            self._in_stripped_script = False
            return
        if self._in_stripped_script:
            return
        if tag == 'a' and self.links:
            if self.links.pop():
                self.output.append(' (not in the public repository)</span>')
                return
        if self.headings and re.fullmatch('h[1-6]', tag) and self.heading_tags:
            _, tag = self.heading_tags.pop()
        self.output.append('</' + tag + '>')

    def handle_data(self, data):
        if not self._in_stripped_script:
            self.output.append(data)

    def handle_entityref(self, name):
        if not self._in_stripped_script:
            self.output.append('&' + name + ';')

    def handle_charref(self, name):
        if not self._in_stripped_script:
            self.output.append('&#' + name + ';')

    def handle_comment(self, data):
        if not self._in_stripped_script:
            self.output.append('<!--' + data + '-->')

    def handle_decl(self, decl):
        if not self._in_stripped_script:
            self.output.append('<!' + decl + '>')


class Builder:
    def __init__(self, source, out, kb):
        self.source, self.out, self.kb = source, out, kb
        self.items = kb.index_items()
        self.groups = {k: [x for x in self.items if x['kind'] == k]
                       for k in ('finding', 'question', 'conjecture', 'attempt', 'paper')}
        self.routes = {
            'README.md': 'index.html',
            'knowledge/WORKING-MODEL.md': 'working-model/index.html',
            'knowledge/DATA.md': 'data.html',
            'knowledge/TIMELINE.md': 'timeline/index.html',
            'CONTRIBUTING.md': 'contribute/index.html',
            'AGENTS.md': 'agents/rules.html',
            'REUSE.md': 'reuse/index.html',
            'THIRD_PARTY_NOTICES.md': 'reuse/notices.html',
            'knowledge/findings': 'findings/index.html',
            'knowledge/questions': 'questions/index.html',
            FINDINGS_GUIDE: 'findings/index.html',
            'knowledge/conjectures': 'conjectures/index.html',
            'knowledge/conjectures/README.md': 'conjectures/rules.html',
            'knowledge/experiments/registry.json': 'attempts/index.html',
        }
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
        self.atlas = all(source.allowed(f'{LIVING_ATLAS}/{name}') for name in ATLAS_PAGES + ATLAS_ASSETS)
        if self.atlas:
            for name in ATLAS_PAGES + ATLAS_ASSETS:
                self.routes[f'{LIVING_ATLAS}/{name}'] = f'{LIVING_ATLAS}/{name}'
        self.relay = source.allowed(RELAY_VIEWER)
        if self.relay:
            self.routes[RELAY_VIEWER] = RELAY_VIEWER
        self.claim_template = self._find_claim_template()
        self.env = jinja2.Environment(loader=SourceTemplates(source), autoescape=True,
                                      keep_trailing_newline=True, newline_sequence='\n')
        self.copied, self.pages, self.unavailable, self.skipped, self.dynamic = {}, {}, set(), [], set()
        self.findings_guide = {'path': FINDINGS_GUIDE, 'mode': 'area', 'reason': 'not in the public repository'}
        self.env.filters['label'] = lambda value: str(value).replace('-', ' ').replace('_', ' ')
        self.env.filters['pct'] = credence_pct
        self.has_favicon = source.allowed('site/static/favicon.svg')
        self.has_social_card = source.allowed('site/static/social-card.png')
        self.stats = {
            'register_objects': '4,695',
            'atlas_sites': 115,
            'atlas_located': 112,
            'atlas_towns': 16,
            'atlas_scenes': 7,
            'catalogue_signs': 56,
            'chart_signs': 687,
        }

    def _find_claim_template(self):
        forms = sorted(p for p in self.source.files if p.startswith('.github/ISSUE_TEMPLATE/') and p.endswith(('.yml', '.yaml'))
                       and re.search(r'^name:\s*[\"\x27]?Claim a question', self.source.text(p), re.M))
        return PurePosixPath(forms[0]).name if forms else None

    def question_claim_url(self, qid, title):
        if not self.claim_template:
            return None
        return REPO + '/issues/new?' + urlencode({'template': self.claim_template, 'title': f'[{qid}] Claim: {title}'})

    def question_issues_url(self, qid):
        return f'{REPO}/issues?q=' + quote(f'is:issue {qid}')

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

    def rendered(self, body, source, page, strip_h1=False):
        shift = True
        if strip_h1:
            body, stripped = strip_leading_h1(body)
            if stripped:
                shift = False
        converted = markdown.markdown(body, extensions=['extra', 'sane_lists', 'toc'],
                                      extension_configs={'toc': {'permalink': False}})
        parser = RewriteHTML(self, source, page, headings=True, shift_headings=shift, strip_scripts=True)
        parser.feed(converted)
        return ''.join(parser.output)

    def _inject_viewer_meta(self, content, title, desc, path):
        if not re.search(r'</head>', content, re.I):
            return content
        meta = []
        if not re.search(r'<meta[^>]+name=["\']description["\']', content, re.I):
            meta.append(f'<meta name="description" content="{html.escape(trim_desc(desc), quote=True)}">')
        url = site_full_url(path)
        meta.append(f'<link rel="canonical" href="{html.escape(url, quote=True)}">')
        meta.append('<meta property="og:type" content="website">')
        meta.append(f'<meta property="og:title" content="{html.escape(title, quote=True)}">')
        meta.append(f'<meta property="og:description" content="{html.escape(trim_desc(desc), quote=True)}">')
        meta.append(f'<meta property="og:url" content="{html.escape(url, quote=True)}">')
        if self.has_social_card:
            og_img = SITE + 'assets/social-card.png'
            meta.append(f'<meta property="og:image" content="{og_img}">')
            meta.append('<meta name="twitter:card" content="summary_large_image">')
            meta.append(f'<meta name="twitter:image" content="{og_img}">')
        else:
            meta.append('<meta name="twitter:card" content="summary">')
        meta.append(f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">')
        meta.append(f'<meta name="twitter:description" content="{html.escape(trim_desc(desc), quote=True)}">')
        return re.sub(r'</head>', '\n  ' + '\n  '.join(meta) + '\n</head>', content, count=1, flags=re.I)

    def page(self, path, title, source, template='document.jinja', **values):
        root_relative = values.pop('root_relative', False)
        def url_for(dest):
            return site_absolute_path(dest) if root_relative else relative_url(dest, path)
        def nav_link(label, dest):
            # Cards and secondary pages belong to the section containing their index.
            current = path == dest
            active = current or (dest.endswith('/index.html') and path.startswith(dest[:-10]) and dest != 'index.html')
            return {'label': label, 'url': url_for(dest), 'current': current, 'active': active}
        nav = []
        for label, dest in NAV:
            if isinstance(dest, list):
                children = [nav_link(name, target) for name, target in dest]
                nav.append({'label': label, 'children': children, 'active': any(c['active'] for c in children)})
            else:
                nav.append(nav_link(label, dest))
        canonical = '' if values.pop('no_canonical', False) else (SITE if path == 'index.html' else site_full_url(path))
        desc = trim_desc(values.pop('description', '') or DEFAULT_DESC)
        breadcrumbs = values.pop('breadcrumbs', None)
        if breadcrumbs is not None:
            breadcrumbs = [{'label': b['label'], 'url': url_for(b['dest']) if b.get('dest') else None}
                           for b in breadcrumbs]
        context = dict(
            title=title, page=path, source_url=self.github(source), source_path=source,
            commit=self.source.commit, commit_date=self.source.date, commit_day=self.source.date[:10],
            worktree=self.source.worktree,
            nav_groups=nav,
            nav=[(name, url_for(target)) for label, dest in NAV
                 for name, target in (dest if isinstance(dest, list) else [(label, dest)])],
            css=url_for('assets/site.css'), js=url_for('assets/site.js'),
            favicon=url_for('assets/favicon.svg') if self.has_favicon else '',
            social_image=(SITE + 'assets/social-card.png') if self.has_social_card else '',
            canonical_url=canonical, meta_description=desc,
            home=url_for('index.html'),
            explore_url=url_for('explore/index.html'),
            search_url=url_for('search/index.html'),
            agents_url=url_for('agents/index.html'),
            llms_url=url_for('llms.txt'),
            llms_full_url=url_for('llms-full.txt'),
            repo=REPO, site_url=SITE, breadcrumbs=breadcrumbs,
            **values,
        )
        self.write(path, self.env.get_template(template).render(**context))
        self.pages[path] = source

    def document(self, source, title=None, **extra):
        if not self.source.allowed(source):
            self.skipped.append({'path': source, 'reason': 'not in the public repository'})
            return
        body = self.kb.frontmatter(self.source.text(source))[1]
        page = self.routes[source]
        rendered_html = self.rendered(body, source, page, strip_h1=True)
        toc = extract_toc(rendered_html)
        first_para = text_only(re.sub(r'^#[^\n]*\n+', '', body.strip()).split('\n\n', 1)[0])
        self.page(page, title or self.kb.heading(body, source), source,
                  template=extra.pop('template', 'document.jinja'),
                  body=rendered_html, toc=toc if len(toc) >= 3 else [],
                  reading_time=reading_minutes(body),
                  description=extra.pop('description', first_para),
                  **extra)

    def index_rows(self, kind):
        rows = []
        for item in self.groups[kind]:
            row = {**item['fields'], 'id': item['id'], 'title': item['title'], 'area': item['area'],
                   'status': item['status'], 'path': item['path'], 'source_url': self.github(item['path'])}
            if kind == 'attempt':
                evidence = row.get('evidence', [])
                package = next((p.split('#')[0] for p in evidence if p.startswith('experiments/') and self.source.allowed(p.split('#')[0])), item['path'])
                # A package directory is discoverable even when its first witness is omitted.
                row['href'] = self.github(str(PurePosixPath(package).parent)) if package != item['path'] else self.github(package)
                row['url'] = row['href']
                row['date'] = attempt_date(row)
                # Report candidates go through link(), including omitted and absent reports.
                reports = [p for p in evidence if re.search(r'/(?:REPORT|README)\.md(?:#.*)?$', p)]
                preferred = row.get('package', '').rstrip('/')
                row['report_path'] = next((p for p in reports if PurePosixPath(p.split('#')[0]).name == 'REPORT.md'),
                                          preferred + '/REPORT.md' if preferred else reports[0] if reports else item['path'])
                resolved_report = self.link(row['report_path'], 'README.md', 'index.html')
                row['report_href'] = resolved_report
                row['report_url'] = (site_full_url(resolved_report) if resolved_report and not urlsplit(resolved_report).scheme
                                     else resolved_report)
            else:
                route = self.routes[item['path']]
                row['href'] = PurePosixPath(route).name
                row['url'] = site_full_url(route)
                row['claim'] = text_only(section(item['body'], 'Claim' if kind == 'conjecture' else 'Question' if kind == 'question' else 'Finding'))
                if kind == 'question':
                    if row['status'] in ('open', 'claimed'):
                        row['claim_url'] = self.question_claim_url(item['id'], item['title'])
                        row['issues_url'] = self.question_issues_url(item['id'])
                    else:
                        row['claim_url'] = None
                        row['issues_url'] = None
                elif kind == 'conjecture':
                    row['credence_pct'] = credence_pct(row.get('credence'))
            rows.append(row)
        if kind == 'attempt':
            # Stable ID order resolves ties without consulting time or file timestamps.
            rows.sort(key=lambda r: r['id'])
            rows.sort(key=lambda r: r['date'], reverse=True)
        elif kind == 'question':
            rows.sort(key=lambda r: (int(r.get('priority') or 9), r['id']))
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
                           'intro_plain': text_only('\n'.join(theme['intro'])),
                           'intro': self.rendered('\n'.join(theme['intro']), FINDINGS_GUIDE, page)})
        other = [row for row in rows if row['id'] not in guide['listed']]
        for row in other:
            row['theme'] = 'Other findings'
        if other:
            themes.append({'title': 'Other findings', 'anchor': 'other-findings', 'rows': other,
                           'intro_plain': 'Cards not yet placed in the findings guide.',
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
        issues_url = None
        agent_prompt = ''
        if item['kind'] == 'question' and item['status'] in ('open', 'claimed'):
            claim_url = self.question_claim_url(item['id'], item['title'])
            issues_url = self.question_issues_url(item['id'])
            if claim_url is None:
                self.skipped.append({'path': '.github/ISSUE_TEMPLATE/claim-question.yml', 'reason': 'claim form unavailable'})
            agent_prompt = make_agent_prompt(item)
        section_map = {'finding': ('Findings', 'findings/index.html'),
                       'question': ('Questions', 'questions/index.html'),
                       'conjecture': ('Conjectures', 'conjectures/index.html')}
        sec_label, sec_dest = section_map[item['kind']]
        rendered_html = self.rendered(item['body'], item['path'], path)
        lead = text_only(section(item['body'], 'Claim' if item['kind'] == 'conjecture' else 'Question' if item['kind'] == 'question' else 'Finding'))
        self.page(
            path, f"{item['id']}: {item['title']}", item['path'], 'card.jinja',
            item=item, fields=item['fields'], history=history, claim_url=claim_url,
            issues_url=issues_url, agent_prompt=agent_prompt,
            credence_chart=credence_chart_svg(history) if item['kind'] == 'conjecture' else '',
            credence_pct=credence_pct(item['fields'].get('credence')) if item['kind'] == 'conjecture' else None,
            breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': sec_label, 'dest': sec_dest}, {'label': item['id']}],
            toc=extract_toc(rendered_html) if len(extract_toc(rendered_html)) >= 3 else [],
            reading_time=reading_minutes(item['body']),
            description=lead or item['title'],
            body=rendered_html,
        )

    def explore(self, path):
        if not self.source.allowed(path):
            self.skipped.append({'path': path, 'reason': 'not in the public repository'})
            return
        content = self.source.text(path)
        for match in re.finditer(r'"(focused_path|path|image)"\s*:\s*"([^"\n]+\.(?:png|jpg|jpeg|svg|webp))"', content):
            key, asset = match.groups()
            target = safe_path(posixpath.join(posixpath.dirname(path), asset)) if key == 'image' else safe_path(asset)
            self.copy(target, tracked_only=True)
            self.dynamic.add((path, target))
        for match in re.finditer(r'(?:href|src)=[\"\x27]([^\"\x27]+\.json)[\"\x27]', content):
            target = safe_path(posixpath.join(posixpath.dirname(path), match[1]))
            if self.source.allowed(target):
                self.copy(target, tracked_only=True)
                self.routes[target] = target
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
        home_rel = relative_url('explore/index.html', path)
        footer = (f'<footer style="margin:24px auto;max-width:1100px;padding:14px 20px;border-top:1px solid #c9d4d1;'
                  f'font:13px/1.5 system-ui,sans-serif;display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between">'
                  f'<a href="{home_rel}">Back to Explore</a>'
                  f'<span><a href="{self.github(path)}">Source on GitHub</a> · {self.source.commit[:12]}</span></footer>')
        if path == EXPLORE[0]:
            embedded = re.search(r'<script[^>]*id="catalogue-data"[^>]*>(.*?)</script>', content, re.S)
            rows = json.loads(embedded[1])['rows'] if embedded else []
            self.stats['catalogue_signs'] = sum(1 for r in rows if r.get('meaning')) or len(rows)
            columns = [('sign_id', 'Sign'), ('meaning', 'Claim'), ('tier', 'Status')]
            viewer_title = 'Reviewed Indus sign catalogue · Indus Research'
            viewer_desc = 'Indus signs with example inscriptions, proposed senses and adversarial review evidence.'
        else:
            embedded = re.search(r'const rows=(\[.*?\]);\s*const q=', content, re.S)
            rows = json.loads(embedded[1]) if embedded else []
            self.stats['chart_signs'] = len(rows)
            columns = [('rank', 'Rank'), ('code', 'Code'), ('alternatives', 'Code alternatives'),
                       ('rank_alternatives', 'Rank alternatives'), ('pdf_page', 'PDF page'),
                       ('column', 'Column'), ('row', 'Row'), ('numeric_confidence', 'Confidence')]
            viewer_title = '1979 Helsinki sign chart atlas · Indus Research'
            viewer_desc = f'{len(rows)} sign drawings and numbers from Koskenniemi and Parpola (1979), linked to chart pages.'
        if not rows:
            raise ValueError(f'Viewer embedded rows unavailable: {path}')
        content = self._inject_viewer_meta(content, viewer_title, viewer_desc, path)
        fallback = '<noscript><h2>Viewer data</h2><table><thead><tr>' + ''.join('<th scope="col">' + label + '</th>' for _, label in columns) + '</tr></thead><tbody>'
        fallback += ''.join('<tr>' + ''.join('<td>' + html.escape(str(row.get(key, ''))) + '</td>' for key, _ in columns) + '</tr>' for row in rows)
        fallback += '</tbody></table><p><a href="' + self.github(posixpath.join(posixpath.dirname(path), 'catalogue-data.json' if path == EXPLORE[0] else 'reference.json')) + '">Viewer data on GitHub</a></p></noscript>'
        suffix = fallback + footer
        end = '</body>' if '</body>' in content else '</html>' if '</html>' in content else None
        content = content.replace(end, suffix + end) if end else content + '\n' + suffix
        self.write(path, content)
        self.pages[path] = path

    def write_tracked(self, path, content):
        if path not in (self.source.tracked if self.source.worktree else self.source.committed):
            raise ValueError(f'Asset is not tracked: {path}')
        payload = content.encode('utf-8')
        self.copied[path] = hashlib.sha256(payload).hexdigest()
        self.write(path, payload)

    def living_atlas(self):
        """Publish the living atlas with local resources only; return its Explore entry."""
        index = f'{LIVING_ATLAS}/index.html'
        if not self.atlas:
            self.skipped.append({'path': index, 'reason': 'not in the public repository'})
            return None

        def report_links(content):
            def gated(match):
                resolved = self.link(match[1], index, index)
                return '"' + (resolved or '#') + '"'
            return re.sub(r'"((?:\.\./)+[^"\s]+?\.md(?:#[^"]*)?)"', gated, content)

        for name in ATLAS_ASSETS:
            path = f'{LIVING_ATLAS}/{name}'
            if name not in ('mapping/atlas.js', 'mapping/current-data.js'):
                self.copy(path, tracked_only=True)
                continue
            content = self.source.text(path)
            if name == 'mapping/atlas.js':
                content, count = ATLAS_STREET_HANDLER.subn('', content)
                if count != 1:
                    raise ValueError(f'Living atlas street basemap handler not found: {path}')
            content = report_links(content)
            if external_script_resource(content):
                raise ValueError(f'Living atlas script loads an external resource: {path}')
            self.write_tracked(path, content)
        data_text = self.source.text(f'{LIVING_ATLAS}/mapping/current-data.js')
        data = json.loads(data_text.split('=', 1)[1].strip().rstrip(';'))
        summary = data.get('summary', {})
        located = sum(1 for s in data.get('sites', []) if s.get('lat') is not None and s.get('lon') is not None)
        self.stats['atlas_sites'] = summary.get('find_sites') or len(data.get('sites', []))
        self.stats['atlas_located'] = located
        self.stats['atlas_towns'] = summary.get('living_towns') or len(data.get('towns', []))
        atlas_desc = (f"Map of {self.stats['atlas_sites']} Indus find places ({located} located), "
                      f"{self.stats['atlas_towns']} living towns, and {self.stats['atlas_scenes']} source-linked 3D city reconstructions.")
        for name in ATLAS_PAGES:
            path = f'{LIVING_ATLAS}/{name}'
            content = self.source.text(path)
            if name == 'index.html':
                if ATLAS_STREET_CONTROL not in content:
                    raise ValueError(f'Living atlas street basemap control not found: {path}')
                content = content.replace(ATLAS_STREET_CONTROL, '')
            parser = RewriteHTML(self, path, path)
            parser.feed(content)
            content = ''.join(parser.output)
            page_title = ('Indus living atlas · Indus Research' if name == 'index.html'
                          else 'Indus cities in 3D · Indus Research' if 'reconstruction' in name
                          else 'Indus atlas continuity reader · Indus Research')
            content = self._inject_viewer_meta(content, page_title, atlas_desc, path)
            source_link = '<a href="' + self.github(path) + '">Source on GitHub</a> · ' + self.source.commit[:12]
            if name == 'index.html':
                def table(columns, rows):
                    return ('<table><thead><tr>' + ''.join('<th scope="col">' + label + '</th>' for label, _ in columns) +
                            '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + html.escape(str(value(row) or '')) + '</td>'
                                                                                for _, value in columns) + '</tr>' for row in rows) +
                            '</tbody></table>')
                places = table([('Place', lambda r: r.get('name')), ('Country', lambda r: r.get('country')),
                                ('Region', lambda r: r.get('region')), ('Location basis', lambda r: r.get('coord_kind')),
                                ('Inscribed objects', lambda r: (r.get('counts') or {}).get('families')),
                                ('First inscribed find', lambda r: (r.get('first_inscribed_find') or {}).get('year'))],
                               data['sites'])
                towns = table([('Town', lambda r: r.get('name')), ('Country', lambda r: r.get('country')),
                               ('Category', lambda r: str(r.get('category') or '').replace('-', ' '))], data['towns'])
                suffix = ('<noscript><h2>Places in the atlas</h2>' + places + '<h2>Towns inhabited today</h2>' + towns +
                          '<p><a href="' + self.github(f'{LIVING_ATLAS}/mapping/current-data.js') + '">Atlas data on GitHub</a> · ' +
                          source_link + '</p></noscript>')
            else:
                suffix = '<footer><p>' + source_link + '</p></footer>'
            end = '</body>' if '</body>' in content else '</html>' if '</html>' in content else None
            content = content.replace(end, suffix + end) if end else content + '\n' + suffix
            self.write(path, content)
            self.pages[path] = path
        return {
            'id': 'living-atlas',
            'kind': 'Map and 3D architecture',
            'stat': f"{self.stats['atlas_sites']} places ({located} located) · {self.stats['atlas_scenes']} 3D scenes · {self.stats['atlas_towns']} living towns",
            'name': 'Indus living atlas',
            'path': index,
            'url': relative_url(index, 'explore/index.html'),
            'home_url': index,
            'secondary_label': 'Open 3D city models',
            'secondary_url': relative_url(f'{LIVING_ATLAS}/reconstruction/index.html', 'explore/index.html'),
            'secondary_home_url': f'{LIVING_ATLAS}/reconstruction/index.html',
            'description': (f"Explore {self.stats['atlas_sites']} places where Indus inscribed objects were found ({located} located), "
                            f"{self.stats['atlas_towns']} towns inhabited today, and {self.stats['atlas_scenes']} source-linked 3D city "
                            'and building reconstructions. The website copy uses offline map geometry only.'),
        }

    def relay_viewer(self):
        """Publish the societal persistence teaching-relay animation without external fonts."""
        path = RELAY_VIEWER
        if not self.relay:
            return None
        content = self.source.text(path)
        content = RELAY_FONT_LINKS.sub('', content)
        if not content.lstrip().lower().startswith('<!doctype'):
            if '</style>' not in content:
                raise ValueError(f'Relay viewer style boundary missing: {path}')
            head, body = content.split('</style>', 1)
            content = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                       + head + '</style>\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
        content = self._inject_viewer_meta(
            content, 'The teaching relay · Indus Research',
            'Animated replay of 48 finite renewal worlds from our societal-persistence study.', path,
        )
        home_rel = relative_url('explore/index.html', path)
        suffix = ('<noscript><p>JavaScript is needed to animate the 48 finite renewal worlds. '
                  f'Read the full model results on <a href="{self.github("experiments/2026-10-11-societal-persistence/MODEL-RESULTS.md")}">GitHub</a>.</p></noscript>'
                  f'<footer style="margin:24px auto;max-width:1100px;padding:14px 20px;border-top:1px solid #c9d4d1;'
                  f'font:13px/1.5 system-ui,sans-serif;display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between">'
                  f'<a href="{home_rel}">Back to Explore</a>'
                  f'<span><a href="{self.github(path)}">Source on GitHub</a> · {self.source.commit[:12]}</span></footer>')
        content = content.replace('</body>', suffix + '\n</body>')
        self.write(path, content)
        self.pages[path] = path
        return {
            'id': 'teaching-relay',
            'kind': 'Interactive simulation',
            'stat': '48 finite renewal worlds',
            'name': 'The teaching relay',
            'path': path,
            'url': relative_url(path, 'explore/index.html'),
            'home_url': path,
            'description': ('An animated replay of our societal-persistence model: watch two brick-built services '
                            'and a teacher\'s skill age under shocks, and see when shared operations carry knowledge across generations.'),
        }

    def build_llms_full(self, purpose, findings, headlines, conjectures, starter_questions, open_questions):
        """Emit a single clean Markdown digest for LLM/agent ingestion."""
        parts = [
            '# Indus civilisation and script research — full agent digest',
            '',
            f'Commit: `{self.source.commit}` ({self.source.date[:10]})',
            f'Repository: {REPO}',
            f'Website: {SITE}',
            f'Full agent rules (verbatim): {self.github("AGENTS.md")}',
            '',
            '## Summary',
            '',
            text_only(purpose),
            '',
            '## Standing constraints',
            '',
            '- The Indus script remains undeciphered; do not claim established phonetic readings or meanings.',
            '- No CI/CD or recurring workflows exist or should be added.',
            '- Check `knowledge/experiments/registry.json` before starting so failed or superseded paths are not repeated without new evidence.',
            '- Claim a question on GitHub Issues with the Q-ID in the title; claims lapse after 7 days without an update.',
            '- Own a new dated folder `experiments/YYYY-MM-DD-short-slug/` and new card files; never overwrite frozen endpoints or edit generated `registry.json` / `MAP.md`.',
            '- Attach `python -m bench <task>` outputs for inscription-corpus claims, or prespecified source-audit/spatial/formal controls for archaeology and continuity studies.',
            '- Run `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, and `python tools/verify_knowledge_repo.py --output <your new verification path>`.',
            '- Disclose model and harness in `authors`.',
            '',
            '## Data access values',
            '',
            *(f'- `{k}`: {v}' for k, v in DATA_ACCESS_LEGEND.items()),
            '',
            '## Machine-readable endpoints',
            '',
            f'- Summary and starter queue: {SITE}api/summary.json',
            f'- Findings index: {SITE}findings/index.json',
            f'- Open questions index: {SITE}questions/index.json',
            f'- Conjectures index: {SITE}conjectures/index.json',
            f'- Attempts registry: {SITE}attempts/index.json',
            f'- Site search index: {SITE}search-index.json',
            '',
            '## Working model headlines',
            '',
        ]
        for h in headlines:
            cred = f" (credence {h['credence']})" if h.get('credence') is not None else ''
            parts.append(f"- **{h['heading']}**{cred}: {h['summary']}")
        parts.extend(['', '## Conjectures', ''])
        for c in conjectures:
            parts.append(f"- `{c['id']}` [{c['status']}, credence {c.get('credence')}, {c.get('risk', '')}]: {c['title']} ({c['url']})")
        if findings and findings.get('themes'):
            parts.extend(['', '## Findings by theme', ''])
            for theme in findings['themes']:
                parts.append(f"### {theme['title']}")
                for row in theme['rows']:
                    parts.append(f"- `{row['id']}` ({row['status']}): {row.get('result') or row['title']} ({row['url']})")
                parts.append('')
        parts.extend(['## Open tasks runnable without restricted local corpora', ''])
        for q in starter_questions:
            parts.append(
                f"- `{q['id']}` [P{q.get('priority', '')}, {q.get('difficulty', '')}, data: {q.get('data_access', '')}, {q['status']}]: "
                f"{q['title']} ({q['url']})"
            )
        parts.extend(['', '## Other priority open questions (check data_access before claiming)', ''])
        shown_ids = {q['id'] for q in starter_questions}
        for q in [x for x in open_questions if x['id'] not in shown_ids][:20]:
            parts.append(
                f"- `{q['id']}` [P{q.get('priority', '')}, {q.get('difficulty', '')}, data: {q.get('data_access', '')}, {q['status']}]: "
                f"{q['title']} ({q['url']})"
            )
        return '\n'.join(parts).strip() + '\n'

    def build(self):
        for name in ('site.css', 'site.js'):
            self.write('assets/' + name, self.source.bytes('site/static/' + name))
        for opt in ('favicon.svg', 'social-card.png'):
            if self.source.allowed('site/static/' + opt):
                self.write('assets/' + opt, self.source.bytes('site/static/' + opt))

        indexes = {kind: self.index_rows(kind) for kind in ('finding', 'question', 'conjecture', 'attempt')}
        findings = self.findings_sections(indexes['finding'])
        open_questions = [row for row in indexes['question'] if row['status'] in ('open', 'claimed')]

        for kind, folder in [('finding', 'findings'), ('question', 'questions'), ('conjecture', 'conjectures'), ('attempt', 'attempts')]:
            # Emit clean JSON indexes with unambiguous absolute SITE URLs.
            json_rows = [{k: v for k, v in row.items() if k not in ('href', 'report_href')} for row in indexes[kind]]
            self.write(folder + '/index.json', dumps(json_rows))
            for item in self.groups[kind] if kind != 'attempt' else []:
                self.card(item)
            filters = (
                ['status', 'area', 'kind', 'difficulty', 'data_access', 'priority'] if kind == 'question' else
                ['theme', 'status'] if kind == 'finding' else
                ['status', 'risk', 'area'] if kind == 'conjecture' else
                ['area', 'status']
            )
            visible_rows = open_questions if kind == 'question' else indexes[kind]
            values = {field: sorted({str(row.get(field, '')) for row in visible_rows if row.get(field, '') != ''}) for field in filters}
            listing_source = dict(finding='knowledge/findings', question='knowledge/questions',
                                  conjecture='knowledge/conjectures', attempt='knowledge/experiments/registry.json')[kind]
            if kind == 'finding' and findings:
                listing_source = FINDINGS_GUIDE
            titles = dict(finding='Findings', question='Open questions', conjecture='Conjectures', attempt='Experiment registry')
            descs = dict(
                finding='Measured results, source audits, and failed tests across the Indus script and civilisation.',
                question='Open research, metadata, verification, and data-acquisition tasks ready for humans and AI agents.',
                conjecture='Explicit working hypotheses with numeric credences, predictions, and kill conditions.',
                attempt='Chronological record of every recorded research run, including failed and superseded attempts.',
            )
            self.page(
                folder + '/index.html', titles[kind], listing_source, 'listing.jinja',
                kind=kind, rows=visible_rows, filters=values, index_url='index.json',
                findings=findings,
                attempt_groups=grouped_attempts(visible_rows) if kind == 'attempt' else [],
                breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': titles[kind]}],
                description=descs[kind],
            )

        readme = self.source.text('README.md')
        reg_match = re.search(r'all\s+([0-9,]+)\s+provisional\s+Lipi\s+objects', readme)
        if reg_match:
            self.stats['register_objects'] = reg_match[1]
        purpose = readme.split('\n', 1)[1].split('\n## ', 1)[0].strip()
        purpose_paragraphs = [p.strip() for p in purpose.replace('\r\n', '\n').split('\n\n') if p.strip()]
        hero_lead = text_only(purpose_paragraphs[0]) if purpose_paragraphs else DEFAULT_DESC
        model = self.source.text('knowledge/WORKING-MODEL.md') if self.source.allowed('knowledge/WORKING-MODEL.md') else ''
        model = model.replace('\r\n', '\n')
        headlines = []
        for m in re.finditer(r'^## ([^\n]+)\n+(.+?)(?=\n\n|\Z)', model, re.M | re.S):
            cred_m = re.search(r'\bCredence\s+([0-9](?:\.[0-9]+)?)', m[2])
            if cred_m:
                val = float(cred_m[1])
                plain = text_only(m[2])
                first_sentence = re.split(r'(?<=\.)\s+', plain, maxsplit=1)[0]
                headlines.append({
                    'heading': re.sub(r'^\d+\.\s*', '', m[1]),
                    'number': m[1].split('.', 1)[0] if '.' in m[1] else '',
                    'credence': f'{val:.2f}',
                    'credence_pct': credence_pct(val),
                    'summary': first_sentence,
                    'body': self.rendered(m[2], 'knowledge/WORKING-MODEL.md', 'index.html'),
                })
        bootstrap = next((line for line in readme.splitlines() if line.startswith('For agents:')), '')

        for path in EXPLORE:
            self.explore(path)
        catalogue_readme = 'experiments/2026-10-11-bonta-adversarial/README.md'
        catalogue_text = self.source.text(catalogue_readme).replace('\r\n', '\n') if self.source.allowed(catalogue_readme) else ''
        catalogue_intro = catalogue_text.split('\n\n', 2)[1] if '\n\n' in catalogue_text else ''
        chart_sentence = re.search(r'The \[chart atlas\]\([^)]+\)[^.]+\.', readme)
        descriptions = (
            next((s.strip() for s in re.split(r'(?<=\.)\s+', catalogue_intro)
                  if s.startswith('Fifty-six ')), text_only(catalogue_intro)),
            text_only(chart_sentence[0]) if chart_sentence else 'The chart atlas shows sign drawings and numbers from Koskenniemi and Parpola (1979).',
        )
        viewers = []
        atlas = self.living_atlas()
        if atlas:
            viewers.append(atlas)
        explore_meta = [
            ('sign-catalogue', 'Reviewed sign catalogue', 'Sign gallery', f"{self.stats['catalogue_signs']} reviewed signs"),
            ('chart-atlas', '1979 chart atlas', 'Reference index', f"{self.stats['chart_signs']} sign drawings"),
        ]
        for path, (vid, label, vkind, stat), description in zip(EXPLORE, explore_meta, descriptions):
            if path in self.pages:
                viewers.append({
                    'id': vid, 'kind': vkind, 'stat': stat, 'name': label, 'path': path,
                    'url': relative_url(path, 'explore/index.html'), 'home_url': path,
                    'description': description,
                })
        relay = self.relay_viewer()
        if relay:
            viewers.append(relay)

        external_viewers = []
        civ_readme = 'experiments/2026-10-20-contemporary-civilisations/README.md'
        if self.source.allowed(civ_readme):
            external_viewers.append({
                'id': 'contemporary-civilisations',
                'kind': 'Comparative study',
                'stat': '22 Bronze Age societies',
                'name': 'Indus beside its Bronze Age contemporaries',
                'url': self.github(civ_readme),
                'description': ('Compares Mature Harappan territory, city area, population, writing and urban institutions '
                                'against 21 contemporary societies of 2600–1900 BCE. The interactive map requires online tiles, '
                                'so its report and data live on GitHub.'),
            })
        relay_readme = 'presentations/2026-10-13-relay-visualization/README.md'
        if not relay and self.source.allowed(relay_readme):
            external_viewers.append({
                'id': 'teaching-relay',
                'kind': 'Simulation package',
                'stat': '48 finite renewal worlds',
                'name': 'The teaching relay (renewal animation)',
                'url': self.github(relay_readme),
                'description': ('Replays 48 trajectories of our societal-persistence model showing how brick-built services '
                                'and specialist skills survive shocks across generations. Includes derivation code and frozen trajectories on GitHub.'),
            })

        self.page(
            'explore/index.html', 'Explore', 'README.md', 'explore.jinja',
            viewers=viewers, external_viewers=external_viewers, stats=self.stats,
            breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': 'Explore'}],
            description='Interactive maps, 3D Indus city reconstructions, sign catalogues, and visual packages.',
        )

        # Papers
        paper_questions = parse_paper_questions(readme)
        papers = []
        pdfs = [{'name': PurePosixPath(path).name, 'url': self.github(path)} for path in sorted(self.source.files)
                if path.startswith('output/pdf/') and path.endswith('.pdf')]
        pdf_by_name = {p['name']: p for p in pdfs}
        for item in self.groups['paper']:
            paper_links = [{'label': name[:-3].replace('-', ' '),
                            'url': PurePosixPath(self.routes[str(PurePosixPath(item['path']).parent / name)]).name}
                           for name in ('methods.md', 'claim-evidence-map.md')
                           if str(PurePosixPath(item['path']).parent / name) in self.routes]
            pmeta = paper_questions.get(item['path'], {})
            folder_num = PurePosixPath(item['path']).parent.name.split('-', 1)[0]
            pnum = pmeta.get('number') or folder_num
            own_pdfs = [pdf_by_name[n] for n in PAPER_PDFS.get(pnum, ()) if n in pdf_by_name]
            self.document(
                item['path'], item['title'], template='paper.jinja',
                links=paper_links, pdfs=own_pdfs, paper_number=pnum,
                paper_question=pmeta.get('question', ''),
                breadcrumbs=[{'label': 'Home', 'dest': 'index.html'},
                             {'label': 'Papers', 'dest': 'papers/index.html'},
                             {'label': f'Paper {pnum}'}],
                description=pmeta.get('question') or item['title'],
            )
            for name in ('methods.md', 'claim-evidence-map.md'):
                path = str(PurePosixPath(item['path']).parent / name)
                if path in self.routes:
                    self.document(
                        path,
                        breadcrumbs=[{'label': 'Home', 'dest': 'index.html'},
                                     {'label': 'Papers', 'dest': 'papers/index.html'},
                                     {'label': f'Paper {pnum}', 'dest': self.routes[item['path']]},
                                     {'label': name[:-3].replace('-', ' ').capitalize()}],
                    )
            papers.append({
                'number': pnum,
                'title': item['title'],
                'question': pmeta.get('question', ''),
                'url': relative_url(self.routes[item['path']], 'papers/index.html'),
                'home_url': self.routes[item['path']],
                'links': [{'label': name[:-3].replace('-', ' '),
                           'url': relative_url(self.routes[str(PurePosixPath(item['path']).parent / name)], 'papers/index.html')}
                          for name in ('methods.md', 'claim-evidence-map.md')
                          if str(PurePosixPath(item['path']).parent / name) in self.routes],
            })
        self.page(
            'papers/index.html', 'Manuscript drafts', 'README.md', 'papers.jinja',
            papers=papers, pdfs=pdfs,
            breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': 'Papers'}],
            description='Draft research manuscripts with linked methods, claim-evidence maps, and PDF reports.',
        )

        # Standalone documents (including full rendered AGENTS.md at agents/rules.html)
        doc_crumbs = {
            'knowledge/WORKING-MODEL.md': [{'label': 'Home', 'dest': 'index.html'}, {'label': 'Working model'}],
            'knowledge/TIMELINE.md': [{'label': 'Home', 'dest': 'index.html'}, {'label': 'Timeline'}],
            'REUSE.md': [{'label': 'Home', 'dest': 'index.html'}, {'label': 'Reuse & licence'}],
            'THIRD_PARTY_NOTICES.md': [{'label': 'Home', 'dest': 'index.html'}, {'label': 'Reuse & licence', 'dest': 'reuse/index.html'}, {'label': 'Third-party notices'}],
            'knowledge/conjectures/README.md': [{'label': 'Home', 'dest': 'index.html'}, {'label': 'Conjectures', 'dest': 'conjectures/index.html'}, {'label': 'Rules'}],
            'AGENTS.md': [{'label': 'Home', 'dest': 'index.html'}, {'label': 'Agent hub', 'dest': 'agents/index.html'}, {'label': 'Agent rules (AGENTS.md)'}],
        }
        for source in ('knowledge/WORKING-MODEL.md', 'knowledge/TIMELINE.md',
                       'REUSE.md', 'THIRD_PARTY_NOTICES.md', 'knowledge/conjectures/README.md', 'AGENTS.md'):
            crumbs = doc_crumbs[source]
            if source == 'REUSE.md':
                self.document(source, template='reuse.jinja', notices='notices.html', breadcrumbs=crumbs)
            elif source == 'AGENTS.md':
                self.document(source, title='Agent rules (AGENTS.md)', breadcrumbs=crumbs)
            else:
                self.document(source, breadcrumbs=crumbs)

        data_path = 'knowledge/DATA.md'
        manifest_rows = []
        if MANIFEST in (self.source.tracked if self.source.worktree else self.source.committed):
            manifest_rows = json.loads(self.source.text(MANIFEST, metadata=True)).get('sources', [])
        else:
            self.skipped.append({'path': MANIFEST, 'reason': 'not tracked; metadata table omitted'})
        if self.source.allowed(data_path):
            data_body = self.rendered(self.source.text(data_path), data_path, 'data.html', strip_h1=True)
            self.page(
                'data.html', 'Data coverage and sources', data_path, 'data.jinja',
                rows=manifest_rows, body=data_body,
                toc=extract_toc(data_body) if len(extract_toc(data_body)) >= 3 else [],
                breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': 'Data'}],
                description='What inscribed-object, archaeological, urban and comparative datasets we hold, and what is still missing.',
            )
        else:
            self.skipped.append({'path': data_path, 'reason': 'not in the public repository'})

        contribute = self.source.text('CONTRIBUTING.md')
        agents_md = self.source.text('AGENTS.md')
        contribute_html = self.rendered(contribute, 'CONTRIBUTING.md', 'contribute/index.html', strip_h1=True)
        self.page(
            'contribute/index.html', 'Contribute', 'CONTRIBUTING.md', 'contribute.jinja',
            body=contribute_html, bootstrap=bootstrap,
            toc=extract_toc(contribute_html) if len(extract_toc(contribute_html)) >= 3 else [],
            skills=self.rendered(section(agents_md, 'Repository skills'), 'AGENTS.md', 'contribute/index.html'),
            breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': 'Contribute'}],
            description='How humans and AI agents claim open questions, run frozen tests, and submit verifiable work.',
        )

        # Starter queue: require public or none-needed data access so fresh clones can run them.
        public_open = [
            q for q in open_questions
            if q.get('status') == 'open' and q.get('data_access') in ('public', 'none-needed')
        ]
        public_open.sort(key=lambda q: (0 if q.get('difficulty') == 'starter' else 1, int(q.get('priority') or 9), q['id']))
        starter_questions = public_open[:8]

        status_classes = (parse_status_classes(self.source.text(VOCABULARY_PATH))
                          if self.source.allowed(VOCABULARY_PATH) else [])

        # Dedicated Agent Coordination Hub
        self.page(
            'agents/index.html', 'Agent coordination hub', 'AGENTS.md', 'agents.jinja',
            bootstrap=bootstrap,
            agent_prompt=make_agent_prompt(),
            agents_rules_github=self.github('AGENTS.md'),
            starter_questions=starter_questions[:6],
            status_classes=status_classes,
            data_access_legend=DATA_ACCESS_LEGEND,
            skills=self.rendered(section(agents_md, 'Repository skills'), 'AGENTS.md', 'agents/index.html'),
            counts={
                'open': len(open_questions),
                'public_data': len(public_open),
                'starter_public': sum(1 for q in public_open if q.get('difficulty') == 'starter'),
                'attempts': len(indexes['attempt']),
            },
            breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': 'Agent hub'}],
            description='Entry point for autonomous AI research agents: full rules, bootstrap prompt, llms.txt, JSON task queues, and public-data starter tasks.',
        )

        # Home page
        recent_attempts = [row for row in indexes['attempt'] if row['status'] != 'record'][:8]
        dead_or_weakened = [c for c in indexes['conjecture'] if c['status'] in ('dead', 'weakened')]
        active_conjectures = [c for c in indexes['conjecture'] if c['status'] not in ('dead', 'weakened')]
        theme_cards = []
        if findings and findings.get('themes'):
            for t in findings['themes']:
                theme_cards.append({
                    'title': t['title'],
                    'anchor': t['anchor'],
                    'count': len(t['rows']),
                    'intro': trim_desc(t.get('intro_plain', ''), 145),
                    'highlight': t['rows'][0].get('result') or t['rows'][0]['title'] if t['rows'] else '',
                    'highlight_id': t['rows'][0]['id'] if t['rows'] else '',
                    'highlight_url': f"findings/{t['rows'][0]['href']}" if t['rows'] else 'findings/index.html',
                })

        self.page(
            'index.html', self.kb.heading(readme, 'Indus civilisation and script research'), 'README.md', 'home.jinja',
            purpose=self.rendered(purpose, 'README.md', 'index.html'),
            hero_lead=hero_lead,
            standing=self.rendered(section(readme, 'Where things stand'), 'README.md', 'index.html'),
            headlines=headlines,
            conjectures=indexes['conjecture'],
            active_conjectures=active_conjectures,
            dead_or_weakened=dead_or_weakened,
            bootstrap=bootstrap,
            recent=recent_attempts,
            viewers=viewers,
            theme_cards=theme_cards,
            starter_questions=starter_questions[:4],
            papers_count=len(papers),
            stats=self.stats,
            counts={
                'objects in register': self.stats['register_objects'],
                'findings': len(indexes['finding']),
                'conjectures': len(indexes['conjecture']),
                'open questions': len(open_questions),
                'recorded runs': len(indexes['attempt']),
            },
            description=DEFAULT_DESC,
        )

        # Site-wide search index & page
        search_entries = []
        for row in indexes['finding']:
            search_entries.append({
                'kind': 'Finding', 'id': row['id'], 'title': row['title'],
                'summary': row.get('result') or row.get('claim') or '',
                'meta': f"{row.get('theme') or row['area']} · {row['status']}",
                'path': f"findings/{row['href']}",
                'url': row['url'],
            })
        for row in indexes['conjecture']:
            search_entries.append({
                'kind': 'Conjecture', 'id': row['id'], 'title': row['title'],
                'summary': row.get('claim') or '',
                'meta': f"{row['area']} · {row['status']} · credence {row.get('credence')}",
                'path': f"conjectures/{row['href']}",
                'url': row['url'],
            })
        for row in open_questions:
            search_entries.append({
                'kind': 'Question', 'id': row['id'], 'title': row['title'],
                'summary': row.get('claim') or '',
                'meta': f"{row['area']} · {row.get('difficulty', '')} · {row.get('data_access', '')}",
                'path': f"questions/{row['href']}",
                'url': row['url'],
            })
        for p in papers:
            search_entries.append({
                'kind': 'Paper', 'id': f"Paper {p['number']}", 'title': p['title'],
                'summary': p.get('question') or '',
                'meta': 'Manuscript draft',
                'path': p['home_url'],
                'url': site_full_url(p['home_url']),
            })
        for v in viewers:
            search_entries.append({
                'kind': 'Explorer', 'id': v['kind'], 'title': v['name'],
                'summary': v['description'],
                'meta': v['stat'],
                'path': v['home_url'],
                'url': site_full_url(v['home_url']),
            })
        self.write('search-index.json', dumps(search_entries))
        self.page(
            'search/index.html', 'Search the knowledge base', 'README.md', 'search.jinja',
            total_entries=len(search_entries),
            breadcrumbs=[{'label': 'Home', 'dest': 'index.html'}, {'label': 'Search'}],
            description='Search across findings, conjectures, open questions, papers, and interactive explorers.',
        )

        # Machine-readable summary API for agents and dashboards
        summary_api = {
            'schema_version': 1,
            'project': self.kb.heading(readme, 'Indus civilisation and script research'),
            'status': 'undeciphered',
            'repository': REPO,
            'website': SITE,
            'commit': self.source.commit,
            'commit_date': self.source.date,
            'counts': {
                'register_objects': self.stats['register_objects'],
                'findings': len(indexes['finding']),
                'conjectures': len(indexes['conjecture']),
                'open_questions': len(open_questions),
                'public_open_questions': len(public_open),
                'attempts': len(indexes['attempt']),
                'papers': len(papers),
            },
            'data_access_legend': DATA_ACCESS_LEGEND,
            'endpoints': {
                'agents_md_raw': self.github('AGENTS.md'),
                'agent_hub': SITE + 'agents/index.html',
                'agent_rules': SITE + 'agents/rules.html',
                'llms_txt': SITE + 'llms.txt',
                'llms_full_txt': SITE + 'llms-full.txt',
                'findings': SITE + 'findings/index.json',
                'questions': SITE + 'questions/index.json',
                'conjectures': SITE + 'conjectures/index.json',
                'attempts': SITE + 'attempts/index.json',
                'search': SITE + 'search-index.json',
            },
            'bootstrap_prompt': make_agent_prompt(),
            'starter_questions': [
                {
                    'id': q['id'], 'title': q['title'], 'area': q['area'], 'kind': q.get('kind'),
                    'priority': q.get('priority'), 'difficulty': q.get('difficulty'),
                    'data_access': q.get('data_access'), 'status': q['status'],
                    'url': q['url'],
                    'claim_url': q.get('claim_url'),
                    'issues_url': q.get('issues_url'),
                    'command': f"python tools/kb.py show {q['id']}",
                }
                for q in starter_questions
            ],
            'conjectures': [
                {'id': c['id'], 'title': c['title'], 'status': c['status'], 'credence': c.get('credence'),
                 'risk': c.get('risk'), 'url': c['url']}
                for c in indexes['conjecture']
            ],
        }
        self.write('api/summary.json', dumps(summary_api))

        self.page(
            '404.html', 'Page not found', 'README.md',
            root_relative=True, no_canonical=True,
            body=(f'<p>This page does not exist in the published build. Return to '
                  f'<a href="{site_absolute_path("index.html")}">Home</a> or '
                  f'<a href="{site_absolute_path("search/index.html")}">search the knowledge base</a>.</p>'),
        )
        self.write('.nojekyll', b'')

        if self.source.allowed('llms.txt'):
            llms = self.source.text('llms.txt')
        else:
            llms = '# ' + self.kb.heading(readme, 'Indus research') + '\n\n' + bootstrap + '\n'
            self.skipped.append({'path': 'llms.txt', 'reason': 'not in the public repository; only bootstrap and index links emitted'})
        def llm_link(m):
            # Link AGENTS.md to its commit-pinned GitHub markdown blob so agents read every hard rule verbatim.
            if m[2] == 'AGENTS.md' and self.source.allowed('AGENTS.md'):
                return '[' + m[1] + '](' + self.github('AGENTS.md') + ')'
            resolved = self.link(m[2], 'llms.txt', 'llms.txt')
            if resolved is None:
                return m[1] + ' (not in the public repository)'
            if not urlsplit(resolved).scheme:
                resolved = SITE + resolved
            return '[' + m[1] + '](' + resolved + ')'
        llms = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', llm_link, llms)
        llms += (
            '\n## Agent coordination and machine-readable indexes\n\n'
            f'- [Agent coordination hub]({SITE}agents/index.html)\n'
            f'- [Full agent rules (rendered)]({SITE}agents/rules.html)\n'
            f'- [Full single-file digest (llms-full.txt)]({SITE}llms-full.txt)\n'
            f'- [Project summary and public starter queue JSON]({SITE}api/summary.json)\n'
            f'- [Site search index JSON]({SITE}search-index.json)\n'
            + ''.join(f'- [{folder}]({SITE}{folder}/index.json)\n' for folder in ('findings', 'questions', 'conjectures', 'attempts'))
        )
        self.write('llms.txt', llms)
        self.write('llms-full.txt', self.build_llms_full(purpose, findings, headlines, indexes['conjecture'], starter_questions, open_questions))

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
        self.meta_urls = []
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
            rel_tokens = set(str(attrs.get('rel', '')).lower().split())
            if rel_tokens == {'canonical'}:
                self.meta_urls.append(attrs['href'])
            else:
                self.resources.append(attrs['href'])
        if tag == 'meta' and attrs.get('content'):
            if attrs.get('property') in ('og:url', 'og:image') or attrs.get('name') == 'twitter:image':
                self.meta_urls.append(attrs['content'])
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
    def verify_site_url(url, origin):
        parsed = urlsplit(html.unescape(url))
        rel = unquote(parsed.path)
        if not rel.startswith(SITE_PATH_PREFIX):
            errors.append(f'{origin}: unexpected site URL {url}')
            return
        tail = rel[len(SITE_PATH_PREFIX):].lstrip('/') or 'index.html'
        if tail.endswith('/'):
            tail += 'index.html'
        try:
            target = safe_path(tail)
        except ValueError:
            errors.append(f'{origin}: unsafe site URL {url}')
            return
        if target not in files:
            errors.append(f'{origin}: missing SITE target {target}')
    def verify(url, origin, resource=False):
        parsed = urlsplit(html.unescape(url))
        if parsed.scheme == 'data' or url.startswith('#') and resource:
            return
        if parsed.netloc or parsed.scheme:
            if resource:
                errors.append(f'{origin}: external resource {url}')
            if url.startswith(SITE):
                verify_site_url(url, origin)
                return
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
        # Allow site-root absolute paths on 404.html so nested missing URLs still load assets and nav.
        if origin == '404.html' and parsed.path.startswith(SITE_PATH_PREFIX):
            verify_site_url(SITE + parsed.path[len(SITE_PATH_PREFIX):], origin)
            return
        try:
            target = safe_path(posixpath.join(posixpath.dirname(origin), unquote(parsed.path))) if parsed.path else origin
        except ValueError:
            errors.append(f'{origin}: unsafe URL {url}')
            return
        if target not in files:
            errors.append(f'{origin}: missing target {target}')
        elif parsed.fragment and target in inspectors and unquote(parsed.fragment) not in inspectors[target].ids:
            # The catalogue creates Wxxx anchors while rendering its embedded rows; the atlas
            # pages read key=value fragments as view state rather than element ids.
            if not (target == EXPLORE[0] and re.fullmatch('W[0-9]{3}', parsed.fragment) or
                    target.startswith(LIVING_ATLAS + '/') and '=' in parsed.fragment):
                errors.append(f'{origin}: missing fragment {target}#{parsed.fragment}')
    for name, parser in inspectors.items():
        for url in parser.links:
            verify(url, name)
        for url in parser.resources:
            verify(url, name, True)
        for url in parser.meta_urls:
            if url.startswith(SITE):
                verify_site_url(url, name)
        for block in parser.styles:
            for url in css_urls(block):
                verify(url, name, True)
        for block in parser.scripts:
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
        if name == 'search-index.json':
            for row in json.loads(path.read_text(encoding='utf-8')):
                verify(row['path'], 'index.html')
                verify(row['url'], name)
        if name == 'api/summary.json':
            summary = json.loads(path.read_text(encoding='utf-8'))
            for url in summary.get('endpoints', {}).values():
                verify(url, name)
            for row in summary.get('starter_questions', []) + summary.get('conjectures', []):
                if row.get('url'):
                    verify(row['url'], name)
        if name in ('llms.txt', 'llms-full.txt'):
            text = path.read_text(encoding='utf-8')
            for url in re.findall(r'https://[^\s)>\]]+', text):
                url = url.rstrip('.,;:')
                if url.startswith(SITE) or url.startswith(REPO + '/blob/') or url.startswith(REPO + '/tree/'):
                    verify(url, name)
        if name == 'sitemap.xml':
            for url in re.findall(r'<loc>([^<]+)</loc>', path.read_text(encoding='utf-8')):
                verify(url, name)
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
    try:
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
    finally:
        source.close()


def publish(root=ROOT):
    source = GitSource(root=root)
    try:
        with tempfile.TemporaryDirectory(prefix='indus-site-publish-') as tmp:
            out = Path(tmp) / 'site'
            result = build_to(source, out)
            if not result['ok']:
                raise ValueError(dumps(result))
            # Build trees directly. Neither the current index nor a worktree is involved.
            all_files = sorted(p for p in out.rglob('*') if p.is_file())
            stdin_paths = '\n'.join(p.as_posix() for p in all_files) + '\n'
            oids = git('hash-object', '-w', '--no-filters', '--stdin-paths', root=root,
                       payload=stdin_paths.encode('utf-8')).decode().splitlines()
            if len(oids) != len(all_files):
                raise ValueError('hash-object count mismatch during publish')
            nodes = {}
            for path, oid in zip(all_files, oids):
                parts = path.relative_to(out).parts
                node = nodes
                for part in parts[:-1]:
                    node = node.setdefault(part, {})
                node[parts[-1]] = oid
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
    finally:
        source.close()


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
