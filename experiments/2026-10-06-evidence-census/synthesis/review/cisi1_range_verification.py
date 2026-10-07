"""Reviewer table: verification of the 19 CISI 1 ranges against page headers, with class split of absent keys.

The page-header readings (printed page, entry numbers per page, object class) were made by the reviewer from
rendered header strips of data/raw/.../c-north-india/cisi1.pdf (PDF page = printed page + 36). They are typed here.
Local matches are recomputed from data/normalized/lipi_observed_faces.jsonl. Writes review/cisi1-range-verification.csv
and review/cisi1-class-split.csv.
"""
import csv
import json
import re
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
faces = [json.loads(x) for x in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.strip()]


def keys(site, prefix):
    s = set()
    for f in faces:
        if f['site'] == site:
            m = re.fullmatch(r'([A-Za-z]+)-?(\d+)', str(f['source_cisi']).strip())
            if m and m[1].casefold() == prefix.casefold():
                s.add(int(m[2]))
    return s


# site, local label, prefix, last number, printed pages (reviewer reading), header evidence
RANGES = [
    ('Lothal', 'Lothal', 'L', 290, '238-297', 'headers contiguous 1-3, 4-6 ... 283-290 over 60 pages; seals L1-123, impressions L124-216 (p.268 shows the change), tablets L217-220, graffiti L221-290'),
    ('Dholavira', 'Dholavira', 'Dlv', 2, '355', 'DHOLAVIRA 1-2 SEALS'),
    ('Surkotada', 'Surkotada', 'Sktd', 6, '362-363', '1-2 on p.362, 3-6 on p.363'),
    ('Khirsara', 'Khirsara', 'Krs', 2, '357', 'KHIRSARA 1-2 SEALS'),
    ('Rojdi', 'Rodji', 'Rjd', 1, '361', 'ROJDI 1 SEALS'),
    ('Desalpar', 'Desalpur', 'Dlp', 3, '355', 'DESALPUR 1-3 SEALS, SEAL IMPR.'),
    ('Rangpur', None, 'Rgp', 2, '360', 'RANGPUR 1-2 GRAFFITI; MISC.'),
    ('Prabhas Patan', None, 'Pbs', 1, '359', 'PRABHAS PATAN 1 SEALS'),
    ('Daimabad', 'Daimabad', 'Dmd', 9, '352-354', '1-3 seals p.352; 4-5 seals and incised tablets p.353; 6-9 graffiti p.354'),
    ('Pabumath', 'Pabumath', 'Pbm', 1, '358', 'PABUMATH 1 SEALS'),
    ('Kalibangan', 'Kalibangan', 'K', 122, '298-326', 'headers contiguous 1-2, 3-4 ... 121, 122 over 29 pages'),
    ('Banawali', 'Banawali', 'B', 37, '344-349', 'headers contiguous 1-6, 7-14, 15-22, 23, 24-29, 30-37'),
    ('Rakhigarhi', 'Rakhigarhi', 'Rgr', 3, '359-360', '1-2 seals p.359; 3 seal impressions p.360'),
    ('Alamgirpur', 'Alamgirpur', 'Agr', 3, '350', 'ALAMGIRPUR 1-3 GRAFFITI'),
    ('Hulas', 'Hulas', 'Hls', 1, '356', 'HULAS 1'),
    ('Ropar (Rupar)', 'Rupar', 'Rpr', 1, '361', 'RUPAR 1 SEALS'),
    ('Chandigarh', 'Chandigarh', 'Ch', 4, '351', 'GRAFFITI CHANDIGARH 1-4'),
    ('Tarkhanewala Dera', 'Tarkhanewala-dera', 'Tkwd', 3, '363', 'TARKHANEWALA-DERA 1-3'),
    ('Rohira', None, 'Rhr', 2, '361', 'SEAL IMPR. ROHIRA 1-2; GRAFFITI'),
]
# Absent keys split by the section of the CISI 1 catalogue in which each entry stands (reviewer reading of page headers
# and plate captions): (graffiti or pottery marks, seals / impressions / tablets / other). Banawali B24-29 mixes tablets
# and graffiti and is counted with graffiti.
ABSENT_BY_CLASS = {'Lothal': (52, 59), 'Kalibangan': (10, 16), 'Banawali': (6, 8), 'Rangpur': (2, 0), 'Prabhas Patan': (0, 1),
                   'Daimabad': (3, 4), 'Chandigarh': (1, 0), 'Tarkhanewala Dera': (1, 1), 'Rohira': (0, 2)}
rows = []
for site, label, prefix, n, pages, ev in RANGES:
    have = keys(label, prefix) if label else set()
    m = sum(1 for i in range(1, n + 1) if i in have)
    g, s = ABSENT_BY_CLASS.get(site, (0, 0))
    assert g + s == n - m, (site, g, s, n - m)
    rows.append(dict(site=site, range=f'{prefix}1-{n}', entries=n, local_match=m, local_absent=n - m, absent_in_graffiti_or_pottery_sections=g,
                     absent_in_seal_impression_tablet_sections=s, printed_pages_read=pages, page_header_evidence=ev, verdict='confirmed'))
with (OUT / 'cisi1-range-verification.csv').open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print('ranges', len(rows), 'entries', sum(r['entries'] for r in rows), 'match', sum(r['local_match'] for r in rows), 'absent', sum(r['local_absent'] for r in rows))

CLASSES = {
    'Lothal': ('L', [('seals', 1, 123), ('seal impressions', 124, 216), ('tablets in bas-relief', 217, 220), ('graffiti', 221, 290)]),
    'Kalibangan': ('K', [('seals', 1, 65), ('tablets in bas-relief', 66, 81), ('seal impressions', 82, 89), ('graffiti', 90, 120), ('miscellaneous copper objects', 121, 122)]),
    'Banawali': ('B', [('seals', 1, 22), ('seal impression', 23, 23), ('tablets and graffiti', 24, 29), ('graffiti', 30, 37)]),
}
out = []
for site, (prefix, classes) in CLASSES.items():
    have = keys(site, prefix)
    for name, lo, hi in classes:
        n = hi - lo + 1
        m = sum(1 for i in range(lo, hi + 1) if i in have)
        out.append(dict(site=site, section=name, entries=f'{prefix}{lo}-{hi}', n=n, local_match=m, local_absent=n - m, percent_absent=round(100 * (n - m) / n)))
with (OUT / 'cisi1-class-split.csv').open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
tot = collections.Counter()
for o in out:
    tot['graffiti' if 'graffiti' in o['section'] else 'other'] += o['local_absent']
print(dict(tot))
