"""Record the attributed review corrections and checked seven-join supplement.

Writes only new small files in the B3 roots. Source rows remain local-only.
Existing B3 annotations are preserved in pre-v6-2026-10-07 before correction.
"""
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/synthesis/review-fixes-2026-10-07-v1'
COLLECTION = ROOT / 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(p, data):
    if p.exists():
        raise ValueError('Refusing overwrite: ' + str(p))
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    records = load(COLLECTION / 'focused-records.json')
    # Own source-reading notes. Full third-party records are not copied here.
    plans = [
        ('National Museum, New Delhi', '1878/1165', 'L-143', '01878', 'published_CISI_concordance', 'CISI1 p.373 / PDF409: L143; excavation1878; LTH SRG1165'),
        ('National Museum, New Delhi', '6742/1174', 'L-144', '06742(T037)', 'published_CISI_concordance', 'CISI1 p.373 / PDF409: L144; excavation6742; LTH SRG1174'),
        ('National Museum, New Delhi', '13051/1157', 'L-220', '13051(T031) CLXIV-B', 'published_CISI_concordance', 'CISI1 p.373 / PDF409: L220; excavation13051; LTH SRG1157'),
        ('National Museum, New Delhi', 'BNL-1-5026', 'B-3', 'BNL1 5026', 'normalized_full_excavation', 'CISI1 p.375 / PDF411: B3; BNL1 5026; full accession equal after punctuation normalization'),
        ('National Museum, New Delhi', 'BNL-1-170-84-1145', 'B-25', 'BNL1 170/84', 'normalized_full_excavation_with_concordance', 'CISI1 p.375 / PDF411: B25; BNL1 170/84; trailing1145 museum component excluded explicitly'),
        ('British Museum', '1947,0416.2', 'M-1662', 'VS 823003', 'published_Marshall_composite', 'Marshall1931 volumeII p.402 / PDF53: plate3; serial VS823; museum miscellaneous VS823'),
        ('British Museum', '1947,0416.3', 'M-1720', 'HR 629053', 'published_Marshall_composite', 'Marshall1931 volumeII p.402 / PDF53: plate53; serial HR629; museum miscellaneous Hr629')]
    supplement = []
    for institution, accession, cisi, idno, method, evidence in plans:
        museum = [r for r in records if r['institution'] == institution and r['accession'] == accession]
        if len(museum) != 1:
            raise ValueError('Museum record not unique: ' + accession)
        r = museum[0]
        original = ROOT / r['raw']
        if accession not in original.read_text(encoding='utf-8', errors='replace'):
            raise ValueError('Displayed accession missing in original witness')
        supplement.append({'institution': institution, 'accession': accession, 'record_id': r['record_id'],
                           'source_cisi': cisi, 'excavation_idno': idno, 'method': method, 'source_evidence': evidence,
                           'raw_record': r['raw'], 'raw_sha256': sha256(original.read_bytes()).hexdigest(),
                           'review_status': 'B3 checked saved museum record, printed concordance and unique local family; images and field adjudication incomplete'})
    save(RAW / 'museum-join-supplement.json', supplement)
    im77 = {'Mohenjo-daro': 1540, 'Harappa': 985, 'Chanhu-daro': 66, 'Lothal': 165, 'Kalibangan': 99,
            'Alamgirpur': 3, 'Amri': 2, 'Banawali': 7, 'Chandigarh': 4, 'Desalpar': 2, 'Dholavira': 1,
            'Jhukar': 1, 'Kot Diji': 1, 'Lohumjo-daro': 1, 'Rakhigarhi': 1, 'Rojdi': 2,
            'Ropar (Rupar)': 2, 'Surkotada': 5, 'Tarkhanewala Dera': 1,
            'Umma': 1, 'Kish': 2, 'Susa': 1, 'Girsu/Tello': 2, 'Ur': 6}
    gaps = [('Maski', 'CISI1', 'Msk', 1, 'p.358'), ('Mehi', 'CISI1', 'Mehi', 1, 'p.358'),
            ('Shahi-Tump', 'CISI1', 'Sht', 1, 'p.362'), ('Kalako-deray', 'CISI2', 'Kl', 1, 'p.396'),
            ('Lewan-dheri (Dar Dariz)', 'CISI2', 'Lwn', 1, 'p.400'), ('Loebanr', 'CISI2', 'LII', 1, 'p.401'),
            ('Periano-ghundai', 'CISI2', 'Pg', 2, 'p.410'), ('Tarakai Qila', 'CISI2', 'Trq', 8, 'p.414')]
    save(OWN / 'v6-correction-inputs.json', {'status': 'Exploratory', 'date': '2026-10-07',
        'review': 'REVIEW.md', 'im77_site_table': im77,
        'im77_source': 'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/mahadevan1977-full.pdf',
        'im77_locator': 'printed p.6 / PDF17; B3 re-opened page after review',
        'im77_unknown_south_asian': 1, 'im77_unknown_west_asian': 5,
        'catalogue_exclusions': [{'site': 'Harappa', 'edition': 'CISI1', 'prefix': 'H', 'number': 356,
            'reason': 'CISI1 p.375 corrigenda corrects H356 captions to H354; duplicate of H354, not a distinct catalogue object'}],
        'museum_supplement': (RAW / 'museum-join-supplement.json').relative_to(ROOT).as_posix(),
        'section_split_source': 'experiments/2026-10-06-evidence-census/synthesis/review/cisi1-range-verification.csv',
        'detailed_section_source': 'experiments/2026-10-06-evidence-census/synthesis/review/cisi1-class-split.csv',
        'frame_omissions': [{'site': s, 'edition': e, 'prefix': p, 'entries': n, 'locator': loc,
             'evidence': 'CISI1 contents p.iv / PDF8 or CISI2 contents p.iv / PDF7; B3 re-opened',
             'status': 'no contributing site row and no local site label; script eligibility not adjudicated'} for s, e, p, n, loc in gaps],
        'post_trim_note': 'Coordinator trim_source_titles.py and trim_source_titles_v2.py changed five batch source ledgers. Batch B created-paths.json and C/D file-manifest.json predate the title edits; batch D build.py --verify and inventory.py --verify retain stale ledger hashes.'})


if __name__ == '__main__':
    main()
