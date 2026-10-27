"""Bundle an explicit list of authored products; acquired source files stay local."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

P = Path(__file__).resolve().parent
REPO = P.parents[1]
LOCAL = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def actual(path):
    return Path(path.replace('\\\\', '\\'))


def main(out):
    if out.exists() or (P / 'artifact-manifest.json').exists():
        raise FileExistsError('Preserve the delivery endpoint and its manifest.')
    assert out.resolve().is_relative_to(LOCAL.resolve())
    assert load(P / 'study-validation-v3.json')['status'] == 'pass'
    assert load(P / 'book-visual-review-v4.json')['status'] == 'pass'
    assert load(P / 'modules/visuals/validation-run-v7.json')['status'] == 'pass'
    book = load(P / 'book-manifest-v4.json')
    deck = next(r for r in load(P / 'modules/presentation/artifact-manifest.json')['artifacts'] if r['version'] == 'v2')
    atlas = load(P / 'modules/visuals/release-run-v7.json')
    products = [
        ('study/indus-towns-study.pdf', actual(book['output_physical_path']), book['sha256'], 'illustrated study, 74 pages'),
        ('presentation/indus-urban-form.pptx', actual(deck['physical_path']), deck['sha256'], '26 editable slides'),
        ('graphics/urban-form-visual-atlas.zip', actual(atlas['archive_physical_path']), atlas['sha256'], '23 PNG and 23 SVG figures with captions and manifests'),
    ]
    files = [(name, path) for name, path, _, _ in products]
    whitelist = [
        'README.md', 'REPORT.md', 'COMPARISON.md', 'METHODS.md', 'TEST-DESIGN.md', 'SOURCES.md',
        'DATA-UPDATE.md', 'PROPOSED-INTEGRATION.md', 'RETROSPECTIVE.md', 'REVIEW-RESPONSE.md',
        'AUTHORSHIP-CORRECTION.md', 'EXPOSURE.json', 'ENVIRONMENT.json', 'CHECKS.json', 'PROSE-REVIEW.json',
        'PROTOCOL.md', 'PROTOCOL.sha256.json', 'quantities.csv', 'comparison-selection.json',
        'tables-manifest.json', 'methods-sources-v1.json', 'methods-sources-supplement-v1.json',
        'study-validation-v3.json', 'book-manifest-v4.json',
        'book-layout-v4.json', 'book-visual-review-v4.json', 'bench-shots-synthetic-v1.json',
        'build_register.py', 'make_tables.py', 'compare_enclosures.py', 'synthetic_diagnostics.py',
        'build_book.py', 'review_book.py', 'verify_study.py', 'package_delivery.py',
        'shape-comparison-v1/results.json', 'synthetic-v1/results.json',
        'run-v3/observations.json', 'run-v3/observations.csv', 'run-v3/sources.json', 'run-v3/towns.json',
        'run-v3/duration-spans.json', 'run-v3/summary.json', 'run-v3/missing-fields.csv',
        'run-v3/input-manifest.json', 'run-v3/validation.json', 'run-v3/source-integrity.json',
        'modules/western/observations.json', 'modules/western/sources.json',
        'modules/western/mohenjo-daro-residential-series.csv', 'modules/western/table1-conflicts.json',
        'modules/eastern/observations.json', 'modules/eastern/sources.json',
        'modules/inscriptions/observations.json', 'modules/inscriptions/sources.json',
        'modules/inscriptions/context-table-summary.json', 'modules/inscriptions/prior-results.json',
        'modules/visuals/manifest-run-v7.json', 'modules/visuals/captions-run-v7.md',
        'modules/visuals/validation-run-v7.json', 'modules/visuals/visual-review-run-v7.json',
        'modules/visuals/release-run-v7.json', 'modules/presentation/artifact-manifest.json',
        'modules/presentation/verification-v2.json', 'modules/presentation/visual-review-v2.json',
        'reviews/eastern-review.md', 'reviews/western-review.md', 'reviews/integrated-report-review.md',
    ]
    files += [('evidence/' + name, P / name) for name in whitelist]
    cards = [
        'knowledge/conjectures/C-0017-shared-routes-across-rebuilding.md',
        'knowledge/conjectures/C-0018-sealings-at-urban-handovers.md',
        'knowledge/conjectures/C-0019-tablets-for-shared-work.md',
        'knowledge/questions/Q-0040-urban-rebuilding-and-documentary-practice.md',
        'knowledge/registry/attempts/URBAN-FORM-INSCRIPTION-ECOLOGY-2026-10-24.json',
    ]
    files += [(name, REPO / name) for name in cards]
    assert len({name for name, _ in files}) == len(files)
    for name, path, digest, _ in products:
        assert path.is_file() and sha(path) == digest, name
    assert all(path.is_file() for _, path in files)
    contents = [{'archive_name': name, 'sha256': sha(path), 'bytes': path.stat().st_size} for name, path in files]
    payload = {
        'date': '2026-10-24', 'contents': contents,
        'rights': 'Project-authored prose, code, source summaries, aggregates and graphics. Cited third-party sources retain their own terms.',
        'excluded': ['Acquired PDFs, photographs and excavation plans', 'OCR and source text', 'Detailed 225-row Dholavira extraction', 'Raw inscription corpora'],
        'reproduction': 'The evidence folder is a review copy. Reproduction uses the repository code, held sources and recorded historical paths.',
        'scientific_confirmation': False,
    }
    out.parent.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, path in files:
            z.write(path, name)
        z.writestr('DELIVERY-CONTENTS.json', json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(r['archive_name'])).hexdigest() == r['sha256'] for r in contents)
    root_manifest = {
        'date': '2026-10-24', 'local_only': True, 'scientific_confirmation': False,
        'products': [{'role': role, 'physical_path': str(path),
                      'logical_path': 'data/raw/2026-10-24-urban-form-and-inscription-ecology/' + path.relative_to(LOCAL).as_posix(),
                      'sha256': digest, 'bytes': path.stat().st_size} for _, path, digest, role in products],
        'delivery_archive': {'physical_path': str(out), 'sha256': sha(out), 'bytes': out.stat().st_size,
                             'entries': len(files) + 1, 'content_hashes_checked_after_archive': len(files)},
        'preview_physical_path': str(LOCAL / 'visuals/run-v7/selected-cover-contact.jpg'),
        'excluded_acquired_source_images_and_plans': True,
        'payload_manifest': payload,
    }
    (P / 'artifact-manifest.json').write_text(json.dumps(root_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(root_manifest['delivery_archive'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
