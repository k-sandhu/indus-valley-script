"""Record locally acquired primary editions and verified editorial rules.

This records acquisition facts; it does not download or recode any inscription.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/corpus/primary'

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

common = {
    'authors': ['Kimmo Koskenniemi', 'Asko Parpola'],
    'publisher': 'Department of Asian and African Studies, University of Helsinki',
    'retrieved_date_utc': '2026-10-02',
    'retrieval_method': 'Public University of Helsinki file link, standard urllib request with Mozilla/5.0 User-Agent; response 200 and PDF signature verified. No login or access restriction was bypassed.',
    'modifications': 'PDF unchanged. Local text extraction and PNG crops are derivative inspection aids.',
}
for year, title, url, size, sha, pages, license_value, portal in [
    (1980, 'Documentation and Duplicates of the Texts in the Indus Script',
     'https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf',
     8143483, '0ced4102dc6197246df6c84e4b730ed380f41085a4a1ea8dd8a6459332da37d1', 98,
     'No explicit reuse license verified for this edition. Retain locally for research; do not infer the licenses of other editions apply.', None),
    (1982, 'A Concordance to the Texts in the Indus Script',
     'https://tuhat.helsinki.fi/ws/portalfiles/portal/209717802/indus_concordance_1982.pdf',
     16767043, '07d24564cd3abf23620a3cd9d417c9931c9d3e1aafb204d7c4fd49b4022d043c', 201,
     'CC BY 4.0 explicitly linked for the final published PDF on the official portal.',
     'https://researchportal.helsinki.fi/en/publications/a-concordande-to-the-texts-in-the-indus-script/'),
]:
    path = OUT / f'koskenniemi_parpola{year}.pdf'
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert path.stat().st_size == size and actual == sha
    row = dict(common, year=year, title=title, source_url=url, local_file=str(path.relative_to(ROOT)).replace('\\','/'), bytes=size, sha256=sha, pdf_pages=pages, license=license_value, portal=portal)
    if year == 1982:
        row['license_url'] = 'https://creativecommons.org/licenses/by/4.0/'
        row['portal_title_typo'] = 'The portal title spells Concordande; the publication itself spells Concordance.'
        row['text_extraction'] = 'Image-only pages: no usable native text layer. The .txt file contains page separators, not extracted prose or numerical sequences.'
    else:
        row['text_extraction'] = 'Prose OCR exists, but diagrams and many numbers are corrupt. Definitions below were read on rendered primary pages.'
    write(OUT / f'koskenniemi_parpola{year}_provenance.json', row)

definition = {
    'source': 'Koskenniemi and Parpola 1980, Documentation and Duplicates of the Texts in the Indus Script',
    'source_url': 'https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf',
    'local_pdf': 'research/corpus/primary/koskenniemi_parpola1980.pdf',
    'sha256': '0ced4102dc6197246df6c84e4b730ed380f41085a4a1ea8dd8a6459332da37d1',
    'verification': 'Boundary table read visually on printed/PDF p14; duplicate criteria and processing read visually on printed/PDF pp54–57. All descriptions are paraphrases.',
    'boundary_revision': {
        '1979_caution': 'Printed p13 explains that original physical boundaries were not always indicated by spaces in the 1979 text plots; some were indicated only by the boundary code, and some were omitted based on parallel texts. Blank segmentation alone cannot recover every original line/side.',
        '1980_codes': {' ': 'One continuous line on one side', '1': 'One line with apparently intentional gaps on one side', '2': 'Two lines on one side', '3': 'Three lines on one side', '4': 'Four lines on one side', '6': 'One-line inscription on two sides', '7': 'One-line inscription on three sides', '8': 'One-line inscription on four sides', '9': 'Other cases'},
        'gap_uncertainty': 'The authors explicitly acknowledge that a putative intentional gap can instead be one or more obliterated signs.',
        'uninscribed_caution': 'The continuous one-line category includes uninscribed objects represented by auxiliary graphics; such graphics are not text tokens.'
    },
    'duplicates': {
        'scope': 'Editorial duplicate here means textual repetition or conservative fragment compatibility, not necessarily the same physical artifact.',
        'exact': 'Same number of sides, corresponding sides have equal symbol lengths, and symbols match pairwise. Certain and uncertain readings of the same sign are equated for this matching operation.',
        'fragment_compatibility': ['Preserve linear order and the number of sides.', 'Every readable symbol of the fragment must match the same readable symbol in the proposed original.', 'A marker for one missing sign can match one missing or one readable sign.', 'An unknown-length broken end can match zero or more consecutive symbols.', 'The proposed original must preserve at least as much information at every matched position.'],
        'epistemic_limit': 'A compatible fragment does not prove its lost content. The original choice can depend on sorting when more than one intact text is compatible.',
        'exact_representative': ['Prefer the fewest uncertain signs.', 'Then choose the lowest inscription identification number.'],
        'compatible_representative': ['Prefer the shortest number of readable signs.', 'Then the shortest total symbol length.', 'Then the most frequent exact-duplicate text.'],
        'empty_texts': 'Texts with no readable signs are marked and excluded from later matching.',
        'strict': 'Process separately within the same object-type and iconography codes.',
        'loose': 'Process the entire corpus without object-type/iconography partitioning.',
        'published_options': ['All texts, including duplicates.', 'Unique texts and strict duplicate-set representatives.', 'Unique texts and loose duplicate-set representatives.'],
        'analysis_implication': 'Unique-text controls have clear prior precedent. Physical artifact counts, text counts and template counts should remain separate; different objects with one text are distinct archaeological observations.'
    }
}
write(ROOT / 'data/normalized/koskenniemi1980_definitions.json', definition)

# Append rather than overwrite the independently verified 1979 definitions.
p = ROOT / 'data/normalized/koskenniemi1979_definitions.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['later_boundary_revision_caution'] = definition['boundary_revision']['1979_caution']
d['later_definition_reference'] = 'data/normalized/koskenniemi1980_definitions.json'
write(p, d)
print('Recorded two primary acquisition manifests and 1980 definitions.')
