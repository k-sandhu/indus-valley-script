"""Manual regression checks for the site's organization and publication gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_site as site


def main():
    checks = []

    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})

    source = site.GitSource(worktree=True)
    with site.kb_index(source) as kb:
        builder = site.Builder(source, ROOT / '_site/site-preview-fixture', kb)
        rows = builder.index_rows('finding')
        fixture = (PACKAGE / 'fixture-findings-README.md').read_text(encoding='utf-8')
        guide = site.parse_findings_guide(fixture, rows)
        check('Guide order is retained', [r['id'] for r in guide['themes'][0]['cards']] == ['F-0002', 'F-0001'])
        check('Introduction retains both paragraphs', '\n\n' in guide['intro'].strip())
        check('CRLF and LF parse identically', site.parse_findings_guide(fixture.replace('\n', '\r\n'), rows) == guide)
        for name, text in [
            ('Wrong title', fixture.replace('# Findings', '# Results', 1)),
            ('Wrong path', fixture.replace('F-0001-sequential', 'F-0001-missing', 1)),
            ('Wrong status', fixture.replace('*verified-computation*', '*failed*', 1)),
            ('Unknown card', fixture.replace('F-0002', 'F-9999')),
            ('Duplicate card', fixture.replace('- [F-0001](F-0001-sequential-prediction-on-unique-texts.md) The previous sign helps predict the next one in distinct texts. *verified-computation*',
                                               '- [F-0002](F-0002-second-order-known-slot-restoration.md) Repeated. *verified-computation*')),
            ('Unexpected prose after an entry', fixture.replace('## Results recorded', 'Unparsed material.\n\n## Results recorded')),
        ]:
            try:
                site.parse_findings_guide(text, rows)
            except ValueError:
                check(name + ' rejects a partial parse', True)
            else:
                check(name + ' rejects a partial parse', False)

        class GuideSource:
            """An in-memory fixture, never a file under knowledge/findings/."""
            def __init__(self, text):
                self.guide_text = text

            def __getattr__(self, name):
                return getattr(source, name)

            def allowed(self, path):
                return path == site.FINDINGS_GUIDE or source.allowed(path)

            def text(self, path, metadata=False):
                return self.guide_text if path == site.FINDINGS_GUIDE else source.text(path, metadata)

        builder.source = GuideSource(fixture)
        findings = builder.findings_sections(rows)
        listed = [r['id'] for t in findings['themes'] for r in t['rows']]
        check('Every card appears exactly once, including unlisted cards', len(listed) == len(set(listed)) == len(rows))
        check('Unlisted cards go into Other findings', findings['themes'][-1]['title'] == 'Other findings')
        check('Theme and result enter the JSON rows', rows[0]['theme'] == 'Sign order and prediction' and 'previous sign' in rows[0]['result'])
        check('Package reports receive a pinned repository link', source.commit in findings['uncarded']['body'])
        check('Excluded package targets receive unavailable text', 'not in the public repository' in findings['uncarded']['body'] and 'href="../../data/' not in findings['uncarded']['body'])
        builder.page('findings/index.html', 'Findings', site.FINDINGS_GUIDE, 'listing.jinja',
                     kind='finding', rows=rows, filters={}, index_url='index.json', findings=findings, attempt_groups=[])
        fixture_html = (builder.out / 'findings/index.html').read_text(encoding='utf-8')
        parser = site.InspectHTML()
        parser.feed(fixture_html)
        check('Fixture heading levels do not skip', all(b <= a+1 for a, b in zip(parser.headings, parser.headings[1:])))
        check('Guide section fragments are retained', 'sign-order-and-prediction' in parser.ids)
        check('Guide path routes to Findings', builder.link('knowledge/findings/README.md', 'README.md', 'index.html') == 'findings/index.html')
        builder.source = GuideSource('broken guide')
        check('Malformed guide falls back and records a reason', builder.findings_sections(rows) is None and builder.findings_guide['mode'] == 'area' and bool(builder.findings_guide['reason']))
        builder.source = source
        class MissingGuideSource(GuideSource):
            def allowed(self, path):
                return False if path == site.FINDINGS_GUIDE else source.allowed(path)

        builder.source = MissingGuideSource('')
        check('Absent guide falls back', builder.findings_sections(rows) is None)
        builder.source = source
        if source.allowed(site.FINDINGS_GUIDE):
            actual = builder.findings_sections(rows)
            check('Current shared findings guide parses', actual is not None)
            check('Current guide renders all cards', actual is not None and sum(len(t['rows']) for t in actual['themes']) == len(rows))

        attempts = builder.index_rows('attempt')
        check('Attempt dates sort newest first', [r['date'] for r in attempts] == sorted((r['date'] for r in attempts), reverse=True))
        check('Date grouping loses no rows', sum(len(g['rows']) for g in site.grouped_attempts(attempts)) == len(attempts))
        check('Undated attempts go last', not any(r['date'] for r in attempts[next((i for i,r in enumerate(attempts) if not r['date']), len(attempts)):]))
    check('Explicit date overrides package date', site.attempt_date({'date':'2026-10-27', 'package':'experiments/2026-10-26-a'}) == '2026-10-27')
    check('Package date overrides nested run date', site.attempt_date({'evidence':['experiments/2026-10-20-study/run-2026-10-27/REPORT.md']}) == '2026-10-20')
    check('Invalid dates stay undated', site.attempt_date({'date':'2026-02-30'}) == '')
    check('External tile loader is rejected', site.external_script_resource('L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png")'))
    check('External fetch remains rejected', site.external_script_resource('fetch("https://example.org/data.json")'))
    check('External hyperlinks remain allowed', not site.external_script_resource('<a href="https://example.org/">Source</a>'))
    check('Bulk data is excluded before reads', not source.allowed('data/raw/not-public.json'))
    check('Manifest is not a public asset', not source.allowed(site.MANIFEST))
    check('Recorded public omissions stay excluded', all(not source.allowed(p) for p in source.omissions))
    try:
        builder.copy((PACKAGE / 'fixture-findings-README.md').relative_to(ROOT).as_posix(), tracked_only=True)
    except ValueError as exc:
        check('Explore still requires tracked resources in a preview', 'not tracked' in str(exc))
    else:
        check('Explore still requires tracked resources in a preview', False)
    result = {'ok': all(c['passed'] for c in checks), 'fixture': (PACKAGE / 'fixture-findings-README.md').relative_to(ROOT).as_posix(),
              'fixture_sha256': hashlib.sha256(fixture.encode()).hexdigest(), 'source_commit': source.commit, 'checks': checks}
    (PACKAGE / 'parser-test.json').write_text(site.dumps(result), encoding='utf-8')
    print(site.dumps(result))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
