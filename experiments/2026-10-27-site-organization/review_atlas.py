"""Record the tracked atlas resources and the publication blocker without copying them."""
import hashlib
from pathlib import Path
import posixpath
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import build_site as site

source = site.GitSource(True)
base = site.LIVING_ATLAS
roots = [base + '/' + p for p in ('index.html', 'research.html', 'reconstruction/index.html',
                                  'reconstruction/viewer.html', 'reconstruction/run-v5/index.html')]
pending = list(roots)
reviewed, resources, blockers = {}, [], []
while pending:
    path = pending.pop(0)
    if path in reviewed:
        continue
    tracked = path in source.tracked
    public = source.allowed(path)
    reviewed[path] = {'tracked': tracked, 'public': public}
    if not (tracked and public):
        blockers.append({'path': path, 'reason': 'resource is not tracked and public'})
        continue
    reviewed[path]['sha256'] = hashlib.sha256(source.bytes(path)).hexdigest()
    if not path.endswith(('.html', '.css', '.js')):
        continue
    content = source.text(path)
    if path.endswith('.html'):
        parser = site.InspectHTML()
        parser.feed(content)
        refs = parser.resources
        scripts = parser.scripts
    elif path.endswith('.css'):
        refs, scripts = site.css_urls(content), []
    else:
        refs, scripts = [], [content] if path.endswith('.js') else []
    for script in scripts:
        if site.external_script_resource(script):
            blockers.append({'path': path, 'reason': 'external script resource loader',
                             'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png' if 'tile.openstreetmap.org' in script else 'see source'})
    for ref in refs:
        parsed = urlsplit(ref)
        if parsed.scheme == 'data' or ref.startswith('#'):
            continue
        if parsed.scheme or parsed.netloc:
            blockers.append({'path': path, 'reason': 'external page resource', 'url': ref})
            continue
        target = site.safe_path(posixpath.join(posixpath.dirname(path), parsed.path))
        resources.append({'source': path, 'target': target})
        if target not in reviewed:
            pending.append(target)

notices = [base + '/' + name for name in ('README.md', '.gitignore', 'reconstruction/.gitignore',
                                          'reconstruction/README.md', 'mapping/REPORT.md',
                                          'mapping/vendor/leaflet/LICENSE', 'mapping/vendor/leaflet/acquisition.json',
                                          'mapping/river-acquisition-v2.json')]
for path in notices:
    reviewed[path] = {'tracked': path in source.tracked, 'public': source.allowed(path),
                      'sha256': hashlib.sha256(source.bytes(path)).hexdigest()}
result = {'source_commit': source.commit, 'mode': 'worktree', 'eligible': not blockers,
          'roots': roots, 'reviewed': reviewed, 'static_resource_edges': resources, 'blockers': blockers,
          'rights': {'project_code': 'Unlicense', 'project_prose_and_geometry': 'CC0 1.0',
                     'Leaflet': 'BSD-2-Clause; complete notice is tracked', 'Natural_Earth': 'public domain',
                     'source_photographs_and_scanned_plans': 'not redistributed by the atlas',
                     'optional_street_tiles': 'remote service; not a tracked local resource'},
          'decision': 'Leave the atlas bundle off Explore. Retain the local-resource gate. The research reader has no external runtime resources; reconstruction/index.html selects the embedded run-v5 page, while viewer.html is a build template with a MODEL_PAYLOAD placeholder. A successor offline bundle needs its own source-link rewriting and complete no-script lists.'}
(Path(__file__).parent / 'atlas-review.json').write_text(site.dumps(result), encoding='utf-8')
print(site.dumps({'eligible': result['eligible'], 'reviewed_files': len(reviewed), 'blockers': blockers}))
