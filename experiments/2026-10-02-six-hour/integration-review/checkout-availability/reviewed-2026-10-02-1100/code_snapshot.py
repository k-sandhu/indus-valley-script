"""Independently check the captured classification and attach source routes."""
from collections import Counter
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main(args):
    CAPTURE = BASE / args.capture
    destination = BASE / args.endpoint
    if destination.exists():
        raise RuntimeError('Preserve the reviewed endpoint.')
    destination.mkdir()
    selected = set(read(CAPTURE / 'selected-payload.json')['selected_paths'])
    links = read(CAPTURE / 'links.json')
    summary = read(CAPTURE / 'summary.json')
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(check=name, passed=bool(passed), detail=detail))

    # This pass reconstructs membership directly, without importing the scanner.
    for row in links:
        if row['category'] in ('network-or-scheme', 'local-fragment'):
            continue
        target = row['target']
        exact = target in selected
        descendants = sum(name.startswith(target.rstrip('/') + '/') for name in selected)
        expected = 'selected' if exact or descendants else 'local-only' if (ROOT / target).exists() else 'missing'
        check('captured target classification', row['category'] == expected and row['selected_descendants'] == descendants and row['exact_file_selected'] == exact)
    check('scope totals', len(summary['document_hashes']) == summary['documents'] and sum(summary['occurrences_by_category'].values()) == len(links) and summary['local_link_occurrences'] == sum(r['category'] in ('selected', 'local-only', 'missing', 'outside-repository') for r in links))
    counts = Counter(row['category'] for row in links)
    check('occurrence totals', counts == Counter(summary['occurrences_by_category']))
    targets = sorted({r['target'] for r in links if r['category'] == 'local-only'})
    check('eighteen unique local-only targets', len(targets) == 18)
    # A second simple syntax extraction checks every actual core link. There are
    # no reference definitions in this scope, as independently counted here.
    simple_count = 0
    definitions = 0
    live_changes = []
    for relative, sha in summary['document_hashes'].items():
        path = ROOT / summary.get('document_snapshots', {}).get(relative, relative)
        text = path.read_text(encoding='utf-8')
        check('captured document bytes preserved ' + relative, digest(path) == sha)
        if digest(ROOT / relative) != sha:
            live_changes.append(dict(path=relative, captured_sha256=sha, live_sha256=digest(ROOT / relative)))
        without_fences = re.sub(r'(?ms)^\s*```[^\n]*\n.*?^\s*```[^\n]*(?:\n|$)', '', text)
        definitions += len(re.findall(r'(?m)^\s*\[[^\]]+\]:', without_fences))
        simple_count += len(re.findall(r'!?\[[^\]]*\]\([^)]*\)', without_fences))
    check('independent actual-link syntax count', simple_count == len(links) and definitions == 0, dict(simple_inline_links=simple_count, explicit_definitions=definitions))
    routes = {}

    def route(target, records, action, basis):
        routes[target] = dict(target=target, records=records, next_action=action, observation_basis=basis)

    for name in ('mayig_summary.json', 'mayig_file_hashes.json'):
        route('data/normalized/' + name, ['knowledge/provenance/SOURCES.md', 'research/corpus/normalize_mayig.py', 'REPRODUCING.md'], 'Reacquire Mayig at ad2f1e218a34b8c33c57de0d6cb8d99272765bbb, preserve its MIT notice, check the pinned inputs, and inspect normalizer output paths before a fresh run.', 'Mayig row in the source inventory and the pinned normalizer.')
    for name in ('lipi_summary.json', 'lipi_clean_rtl_singleline.jsonl'):
        route('data/normalized/' + name, ['knowledge/provenance/SOURCES.md', 'research/corpus/normalize_lipi.py', 'research/corpus/CORPUS_REPORT.md', 'REPRODUCING.md'], 'Reacquire Lipi at fc8813a52e183d19c441631dc26c33a4dccbea39 and check the pinned input hash. Use a separate upstream clone so the normalizer resolves the source commit, then write a fresh derivative endpoint.', 'Lipi source row, corpus report and normalizer; source inventory records the clean JSONL hash.')
    route('data/normalized/indus_website_summary.json', ['knowledge/provenance/SOURCES.md', 'research/corpus/normalize_indus_website.py'], 'Reacquire indus-website at 2434249618b1e74de3f26d28b90dfde093c3dd94; check the SQL hash and run the text parser into a new output location.', 'Earlier-export source row and text-only normalizer.')
    route('data/normalized/mayig_wells_class_crosswalk.json', ['knowledge/provenance/SOURCES.md', 'research/corpus/build_sign_crosswalk.py', 'research/corpus/normalize_mayig.py'], 'Reacquire and normalize the pinned Mayig schema, then rebuild the many-to-many crosswalk in a fresh location and compare its recorded hash.', 'Source inventory crosswalk hash and explicit transformation helper.')
    route('data/normalized/source_definitions.json', ['knowledge/provenance/catalogue-caveats.md', 'research/corpus/orientation_clarification.json', 'research/corpus/FINAL_SOURCE_NOTES.md', 'archive/2026-10-01-investigation/import-manifest.json'], 'Use the preserved local structured definitions when available. A clone has the catalogue/orientation account and original-file hash record; recreating this exact historical structured file requires its local copy or a separately documented manual transcription.', 'Selected source summaries and import identity record; no complete generator for this structured file was found in the reviewed source helpers.')
    for year in (1979, 1980):
        records = ['research/corpus/primary/1979_extraction_assessment.md', f'research/corpus/primary/koskenniemi_parpola{year}_provenance.json', 'archive/2026-10-01-investigation/import-manifest.json']
        if year == 1980:
            records.insert(1, 'research/corpus/record_primary_provenance.py')
        route(f'data/normalized/koskenniemi{year}_definitions.json', records, 'Reacquire the edition using its provenance route and inspect the recorded definition pages. The 1980 helper records the revised rules; exact historical 1979 JSON restoration needs the local/imported file, since that helper reads an existing 1979 file.', 'Visual source-definition assessment and edition-specific provenance; manual-annotation dependency retained.')
    for year in (1979, 1980, 1982):
        route(f'research/corpus/primary/koskenniemi_parpola{year}.pdf', [f'research/corpus/primary/koskenniemi_parpola{year}_provenance.json', 'knowledge/provenance/SOURCES.md'], 'Follow the edition-specific URL and access route; compare byte count and SHA-256 before inspecting source pages.', 'Selected edition-specific acquisition manifest.')
    route('research/literature/sources/joshi_parpola_1987_cisi1.pdf', ['research/literature/source_retrieval_log.json', 'research/literature/source_identity_index.json', 'research/literature/cisi1_page_image_audit.json', 'knowledge/provenance/SOURCES.md'], 'Use the IGNCA scan URL listed in the source inventory and compare its recorded SHA-256 and page count.', 'Source inventory, original retrieval/identity records and page-image audit.')
    route('research/corpus/primary/fuls2010_help.pdf', ['knowledge/provenance/SOURCES.md', 'research/corpus/primary/fuls_menu_image_provenance.json', 'research/corpus/orientation_clarification.json', 'archive/2026-10-01-investigation/import-manifest.json'], 'Use the public epigraphica.de help PDF in the source inventory and compare its recorded hash. The adjacent image manifest describes the separately acquired orientation examples.', 'Source inventory has the PDF URL, bytes, page count and hash; image manifest covers the related photographs rather than this PDF.')
    for name in ('parpola2011_unicorn', 'kenoyer_meadow2010_inscribed_objects', 'parpola2020_bone_rods'):
        route(f'research/corpus/primary/{name}.pdf', [f'research/corpus/primary/{name}_provenance.json', 'knowledge/provenance/SOURCES.md'], 'Follow the recorded public URL and access method, retain the source-specific rights handling, and compare its byte count and SHA-256.', 'Selected source-specific acquisition manifest, including browser routes where direct requests failed.')
    route('research/literature/sources/sproat_2014_corpora/manifest.json', ['knowledge/provenance/SOURCES.md', 'research/literature/source_retrieval_log.json', 'research/literature/nonlinguistic_controls/README.md', 'research/literature/nonlinguistic_controls/flatten_manifest.json', 'archive/2026-10-01-investigation/import-manifest.json'], 'Reacquire the author archive from the source inventory, compare its ZIP hash and preserve its XML notices. The selected flattening manifest covers transformed corpora; the excluded archive-level manifest itself needs the local copy for exact restoration.', 'Author-archive inventory, selected retrieval/transform records and original import identity.')
    check('every excluded target has a source route', set(routes) == set(targets))
    for row in routes.values():
        row['occurrences'] = [dict(document=r['document'], line=r['line']) for r in links if r['target'] == row['target'] and r['category'] == 'local-only']
        row['local_bytes'] = (ROOT / row['target']).stat().st_size
        row['local_sha256'] = digest(ROOT / row['target'])
        row['record_hashes'] = {name: digest(ROOT / name) for name in row['records']}
        check('selected source route for ' + row['target'], all(name in selected and (ROOT / name).is_file() for name in row['records']))
    latent = ROOT / 'experiments/2026-10-02-six-hour/latent-forms/git-package/main-results-v1'
    manifest = read(latent / 'manifest.json')
    stream_hash = hashlib.sha256()
    for item in manifest['chunks']:
        compressed = (latent / item['file']).read_bytes()
        payload = gzip.decompress(compressed)
        check('compressed package chunk hash', hashlib.sha256(compressed).hexdigest() == item['compressed_sha256'])
        check('decompressed package chunk hash', hashlib.sha256(payload).hexdigest() == item['uncompressed_sha256'])
        stream_hash.update(payload)
    package_route = dict(original=manifest['original_path'], original_sha256=manifest['original_sha256'], selected_reconstruction_record='experiments/2026-10-02-six-hour/latent-forms/git-package/main-results-v1/RECONSTRUCT.md', selected_manifest='experiments/2026-10-02-six-hour/latent-forms/git-package/main-results-v1/manifest.json', chunks=len(manifest['chunks']), reconstructed_sha256=stream_hash.hexdigest(), local_link_occurrences_in_core_scope=sum(r['target'] == manifest['original_path'] for r in links), handling='Authored original stays local; exact bytes are available through selected lossless chunks.')
    check('lossless result package selected and exact', package_route['selected_reconstruction_record'] in selected and package_route['selected_manifest'] in selected and all((latent / c['file']).relative_to(ROOT).as_posix() in selected for c in manifest['chunks']) and stream_hash.hexdigest() == manifest['original_sha256'])
    check('known credential patterns absent in authored chunks', read(CAPTURE / 'credential-chunk-check.json')['total_known_matches'] == 0)
    write(destination / 'local-only-source-routes.json', list(routes.values()))
    write(destination / 'reconstructable-authored-result.json', package_route)
    write(destination / 'concurrent-document-changes.json', live_changes)
    report = dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(r['passed'] for r in checks), checks=checks, capture_hashes={p.relative_to(ROOT).as_posix(): digest(p) for p in CAPTURE.iterdir() if p.is_file()})
    write(destination / 'verification.json', report)
    (destination / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(checks=report['checks_total'], passed=report['checks_passed'], failures=[r for r in checks if not r['passed']], local_only_routes=len(routes))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', required=True)
    parser.add_argument('--endpoint', required=True)
    main(parser.parse_args())
