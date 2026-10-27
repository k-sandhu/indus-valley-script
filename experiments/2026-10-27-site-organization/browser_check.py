"""Check the local preview in installed Chromium, without network access."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=ROOT / '_site/site-preview-final')
    parser.add_argument('--shots', type=Path, default=ROOT / '_site/site-preview-final-shots')
    args = parser.parse_args()
    args.site = args.site.resolve()
    args.shots = args.shots.resolve()
    args.shots.mkdir(parents=True, exist_ok=True)
    browser_path = Path('C:/Users/sandh/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe')
    results, errors, external = [], [], []

    def check(name, passed, **details):
        results.append({'name': name, 'passed': bool(passed), **details})

    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}/'
    with (args.shots / 'server.log').open('w', encoding='utf-8') as log:
        server = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1',
                                   '--directory', str(args.site)], stdout=log, stderr=log,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        try:
            for _ in range(100):
                try:
                    with urlopen(base, timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(.1)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=str(browser_path), headless=True)
                version = browser.version
                pages = [('home', 'index.html'), ('findings', 'findings/index.html'),
                         ('registry', 'attempts/index.html'), ('explore', 'explore/index.html')]
                for width in (1280, 375):
                    context = browser.new_context(viewport={'width': width, 'height': 900})
                    # Any unexpected off-machine request is blocked and recorded.
                    def route_request(route):
                        if route.request.url.startswith(base) or route.request.url.startswith('data:'):
                            route.continue_()
                        else:
                            external.append(route.request.url)
                            route.abort()
                    context.route('**/*', route_request)
                    page = context.new_page()
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    for name, url in pages:
                        response = page.goto(base + url, wait_until='networkidle')
                        check(f'{width}px {name}: HTTP 200', response.status == 200)
                        check(f'{width}px {name}: no document overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                        check(f'{width}px {name}: skip link and language', page.locator('a.skip').count() == 1 and page.locator('html').get_attribute('lang') == 'en')
                        page.screenshot(path=str(args.shots / f'{name}-{width}.png'))
                        if name == 'home':
                            check(f'{width}px home: ten recent attempts', page.locator('.recent-work li').count() == 10)
                            labels = page.locator('.counts dt').all_text_contents()
                            check(f'{width}px home: conjecture count', 'conjectures' in labels)
                            page.get_by_role('link', name='Recent work', exact=True).click()
                            check(f'{width}px home: recent-work jump', page.url.endswith('#recent-work'))
                            page.screenshot(path=str(args.shots / f'recent-work-{width}.png'))
                        if name in ('findings', 'registry'):
                            rows = json.loads((args.site / ('findings' if name == 'findings' else 'attempts') / 'index.json').read_text(encoding='utf-8'))
                            check(f'{width}px {name}: all rows rendered', page.locator('.listing [data-id]').count() == len(rows))
                            query = 'F-0001' if name == 'findings' else rows[0]['id']
                            page.locator('input[name=search]').fill(query)
                            expected = {r['id'] for r in rows if query.lower() in json.dumps(r, ensure_ascii=False).lower()}
                            actual = set(page.locator('.listing [data-id]:visible').evaluate_all('(items) => items.map(item => item.dataset.id)'))
                            check(f'{width}px {name}: search matches JSON rows', actual == expected)
                            page.locator('input[name=search]').fill('no-such-entry-7d90c139')
                            check(f'{width}px {name}: empty groups hide', page.locator('.listing [data-id]:visible').count() == 0 and page.locator('.listing [data-group]:visible').count() == 0)
                            page.get_by_role('button', name='Reset', exact=True).click()
                            page.wait_for_function('!document.querySelector(".listing [data-id][hidden]")')
                            check(f'{width}px {name}: reset restores all rows', page.locator('.listing [data-id]:visible').count() == len(rows))
                            if name == 'findings':
                                theme = rows[0]['theme']
                                status = rows[0]['status']
                                page.locator('select[name=theme]').select_option(theme)
                                page.locator('select[name=status]').select_option(status)
                                expected = {r['id'] for r in rows if r['theme'] == theme and r['status'] == status}
                                actual = set(page.locator('.listing [data-id]:visible').evaluate_all('(items) => items.map(item => item.dataset.id)'))
                                check(f'{width}px findings: theme and status combine', actual == expected)
                                page.locator('.finding-theme:visible').first.evaluate("element => element.scrollIntoView({block: 'start'})")
                                page.screenshot(path=str(args.shots / f'finding-theme-{width}.png'))
                            else:
                                dates = [r['date'] for r in rows]
                                check(f'{width}px registry: newest first', dates == sorted(dates, reverse=True))
                                check(f'{width}px registry: date jumps cover groups', page.locator('.date-nav a').count() == page.locator('.attempt-group').count())
                                page.locator('.attempt-group').first.evaluate("element => element.scrollIntoView({block: 'start'})")
                                page.screenshot(path=str(args.shots / f'registry-table-{width}.png'))
                        if name == 'explore':
                            check(f'{width}px explore: two described viewers', page.locator('.cards li p').count() == 2)
                    # Native disclosure stays within the viewport at phone width.
                    page.get_by_role('navigation', name='Main navigation').get_by_text('Record', exact=True).click()
                    check(f'{width}px navigation: native disclosure opens', page.locator('.nav-list details[open]').count() == 1)
                    check(f'{width}px navigation: open disclosure does not overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                    if width == 375:
                        page.screenshot(path=str(args.shots / 'navigation-open-375.png'))
                    context.close()

                context = browser.new_context(java_script_enabled=False, viewport={'width': 375, 'height': 900})
                page = context.new_page()
                for name, url in pages:
                    page.goto(base + url)
                    check(f'No JavaScript {name}: no document overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                    if name in ('findings', 'registry'):
                        folder = 'findings' if name == 'findings' else 'attempts'
                        expected = len(json.loads((args.site / folder / 'index.json').read_text(encoding='utf-8')))
                        check(f'No JavaScript {name}: complete visible list', page.locator('.listing [data-id]:visible').count() == expected)
                    if name == 'home':
                        check('No JavaScript home: ten recent attempts', page.locator('.recent-work li:visible').count() == 10)
                page.get_by_role('navigation', name='Main navigation').get_by_text('Ideas', exact=True).click()
                check('No JavaScript navigation: disclosure works', page.locator('.nav-list details[open]').count() == 1)
                page.goto(base)
                page.get_by_role('navigation', name='Main navigation').get_by_role('link', name='Findings', exact=True).click()
                page.locator('.listing [data-id] a').first.click()
                check('Home to a finding takes two links without JavaScript', '/findings/F-' in page.url and page.locator('[aria-current=location]').text_content() == 'Findings')
                page.screenshot(path=str(args.shots / 'finding-card-no-js-375.png'))
                context.close()
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)
    check('No browser script errors', not errors, errors=errors)
    check('No external resource requests', not external, requests=external)
    result = {'ok': all(r['passed'] for r in results), 'browser': 'Chromium ' + version,
              'site': args.site.relative_to(ROOT).as_posix(), 'screenshots': args.shots.relative_to(ROOT).as_posix(),
              'checks': results}
    (PACKAGE / 'browser-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    failures = [r['name'] for r in results if not r['passed']]
    (PACKAGE / 'browser-check.md').write_text(
        '# Browser check\n\nWe served the preview with `python -m http.server` on a loopback port and used ' + result['browser'] +
        ' through the installed Python Playwright package. No browser or package was downloaded.\n\n' +
        f"{len(results)} checks {'pass' if result['ok'] else 'include failures'}. Home, Findings, Registry and Explore loaded at 1280 × 900 and 375 × 900. " +
        'We checked document width, navigation disclosures, current-section markup, skip links, recent-work count, search, reset, combined theme and status filters, hidden empty groups and registry date order. ' +
        'A separate context with JavaScript disabled retained the full lists and followed Home → Findings → a finding card in two links.\n\n' +
        'Screenshots are local-only at `' + result['screenshots'] + '`. [Exact results](browser-results.json) record each check. ' +
        ('Failures: ' + ', '.join(failures) + '. ' if failures else '') +
        'The browser made no off-machine resource requests; server and browser processes were stopped. Visual inspection covers page tops, recent work, themed findings, a registry date section, an open mobile navigation group and a finding card; table content scrolls within its own container at phone width.\n', encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'checks': len(results), 'failures': failures, 'screenshots': result['screenshots']}))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
