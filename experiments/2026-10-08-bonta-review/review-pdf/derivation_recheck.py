"""Reviewer classification of Bonta's stated derivation of each Table 18 value (PDF pages cited).

Classes: M = metrology, numeral or M-field context; P = pictorial rebus; D = explicit dictionary or lexicon
cross-check; T = 2014 typological or predicate argument; X = cross-checking and trial and error without a stated
non-lexical anchor (the paper's default method, PDF p. 77); C = composite or ligature built from other values.
Compound labels (M+X, P+M) mark entries whose paper account has two stages.
Writes derivation-recheck.json comparing each class with pdf-2026-10-09-v1/value-derivations-v2.json.
From the repository root: python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/derivation_recheck.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
pkg = {r['table18_entry']: r for r in json.loads(
    (ROOT / 'experiments/2026-10-08-bonta-review/pdf-2026-10-09-v1/value-derivations-v2.json').read_text(encoding='utf-8'))['rows']}

R = {
    1: ('X', '118', 'suffix -ka from distribution'),
    2: ('X', '165', 'value fits the data; author calls it very provisional'),
    3: ('X', '191', 'single-word leader value; patni context'),
    4: ('X', '102', 'after considerable trial and error'),
    5: ('D', '70-71, 75-76, 95-96', 'bhu-pala found by cross-checking known values against a searchable lexicon'),
    6: ('M', '52-55, 109', 'M-field pair with stroke numeral read through MW matra; initial maha is a fitted extension (p. 109)'),
    7: ('X', '108', 'suffix -ja from distribution'),
    8: ('X', '177-178', 'limited uses; no derivation stated'),
    9: ('X', '91', 'frequent prefix su-'),
    10: ('X', '93', 'author calls it provisional'),
    11: ('X', '195', 'CV syllable; no derivation stated'),
    12: ('X', '113', 'prefix vi-; drawing possibly motivated by dvi- and long-stroke numerals'),
    13: ('X', '106', 'lengthiest cross-check; value contingent on PA'),
    14: ('X', '188', 'infrequent; reasonable provisional value'),
    15: ('X', '183', 'long-stroke numeral with a syllabic use; derivation not stated'),
    16: ('X', '144', 'prefix ati-'),
    17: ('M+X', '50-51, 55 (pala); 67-68, 202 (pala/pala with long a); 76 (bala)',
         'pala from M-field and weight context; long-a pala found when he realized the sign is a common final element of names, citing MW; bala fitted to balapati'),
    18: ('P+M', '45-47, 55, 132', 'bow drawing and dhanus-dhana near-homonym, asset notation with stroke numerals'),
    19: ('P+M', '45-47, 55, 132', 'same derivation as entry 18'),
    20: ('X', '127', 'allograph series of para/pra'),
    21: ('X', '130', 'only value consistent with the data'),
    22: ('X', '151', 'mostly in varman'),
    23: ('X', '154', 'suffix -man'),
    24: ('X', '162', 'mostly in sarman'),
    25: ('X', '168-169', 'cross-checked with known signs; only values that matched'),
    26: ('X', '181', 'mostly satya, aditya'),
    27: ('X', '180', 'resemblance to entry 8; full-word use'),
    28: ('X', '173', 'provisional; natha chosen over kumara by sound shape'),
    29: ('M', '45-46, 55, 189', 'fish drawing in M fields read as a weight unit (mina); -min from karmin is an extension'),
    30: ('X', '212', 'one value, two meanings; wealth sense noted in asset contexts'),
    31: ('M+P+X', '185-187', 'pot-like drawing and stroke-numeral contexts give caru; the name element caru with long a is an extension'),
    32: ('X', '157-158', 'affix -mana'),
    33: ('X', '174', 'kar- in karmin; kara'),
    34: ('X', '166-167', 'artifact-type argument; value called tentative'),
    35: ('X', '194', 'one of two signs for pra'),
    36: ('M', '43-44, 54, 142', 'three strokes as the numeral three; Sanskrit tri-/tra-'),
    37: ('C', '171', 'quasi-ligature of ra and tra; frequent before PAla in rashtrapala'),
    38: ('X', '141', 'contexts consistent with one root syllable'),
    39: ('X', '125', 'cross-checked against co-occurring signs; the only possible syllabic value'),
    40: ('X', '160', 'only value found consistent with the data; tentative'),
    41: ('X', '163-164', 'primary readings of the form dhara'),
    42: ('X', '131', 'prefix sam-'),
    43: ('X', '126', 'cross-checked with adjacent signs'),
    44: ('X', '148', 'after very long trial and error; only plausible candidate'),
    45: ('C', '140', 'geminate dhani plus the anthropomorph a'),
    46: ('X', '86', 'no derivation stated; author says no other reading occurs'),
    47: ('D', '75-76, 121', 'cross-checked against known values in a searchable lexicon'),
    48: ('P+X', '215-216', 'drawing plus plausibility of 7 of 8 readings; author calls the value provisional'),
    49: ('P', '216', 'drawing; author calls the value much more tentative than ASHVA'),
    50: ('T', '56-61', '2014 argument that the jar is the predicate be; possession by be-to construction'),
    51: ('T', '61', '2014 argument; arrow as isu near-homonym and be-worth predicate'),
    52: ('T', '64-66', '2014 nominalization of the be root for property'),
    53: ('C', '197', 'ligature of S(u)ri and PATI'),
    54: ('C', '199', 'ligature of entry 53 and DEVA'),
    55: ('C', '200', 'ligature with attached stroke; provisional'),
    56: ('C', '170-171', 'ligature of S(u)ri and PAla'),
    57: ('C', '200-201', 'provisional; rests on the attached-stroke argument of entry 55'),
    58: ('C', '201', 'ligature of kara and PAla (second-edition addition)'),
}

AGREE = {'later extension': ('X', 'C'), 'dictionary search against contexts': ('D',),
         'metrology or M field': ('M', 'M+X'), 'pictorial': ('P', 'P+M', 'P+X')}
rows = []
for e in range(1, 59):
    cls, pages, basis = R[e]
    pc = pkg[e]['category']
    rows.append({'entry': e, 'package_class': pc, 'package_pages': pkg[e]['source_pages'],
                 'reviewer_class': cls, 'reviewer_pages': pages, 'basis': basis,
                 'class_agrees': cls in AGREE[pc]})
out = {'status': 'Exploratory (reviewer classification from the PDF text and figures)',
       'rows': rows,
       'summary': {'entries': len(rows), 'agree': sum(r['class_agrees'] for r in rows),
                   'disagree': [(r['entry'], r['package_class'], r['reviewer_class']) for r in rows if not r['class_agrees']]}}
(Path(__file__).resolve().parent / 'derivation-recheck.json').write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
print(out['summary'])
