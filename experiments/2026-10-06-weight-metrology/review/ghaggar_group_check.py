"""Reviewer exploratory check: relate the fitted Dholavira sample to the heavier-unit list in Ascalone 2022 pp. 169-171.

Parses the enumerated 'Cat. no. N: x g ... = u g' lines of the Ghaggar group from the local PDF (only IDs that fall inside the
group's printed heading ranges), intersects them with the package's 298 primary certain objects and refits with the
package's own function. Aggregates only. Run from the repository root:
    python -X utf8 -B experiments/2026-10-06-weight-metrology/review/ghaggar_group_check.py
"""
import json
import re
import sys
from pathlib import Path

import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-weight-metrology'
RAW = ROOT / 'data/raw/2026-10-06-weight-metrology'
sys.path.insert(0, str(PKG))
import analyze  # noqa: E402

doc = fitz.open(ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf')
txt = '\n'.join(doc[pn].get_text() for pn in (183, 184, 185))
sec = txt[txt.find('The weights are:'):txt.find('The Western group (Cat. no. 1310')]
ents = re.findall(r'Cat\. no\. (\d+): ([\d.,]+) g (?:x|÷) ([\d⁄/ ]+?) = ([\d.,]+) g', sec)
heading = [(1296, 1296), (1303, 1303), (1316, 1321), (1340, 1340), (1657, 1657), (1665, 1665), (1676, 1682), (1696, 1699), (1721, 1736),
           (1758, 1761), (1763, 1764), (1796, 1825), (1875, 1878), (1881, 1884), (1916, 1921), (1952, 1954), (1965, 1966), (1971, 1971),
           (1991, 1991), (1999, 1999), (2007, 2007), (2055, 2055)]
head = set()
for a, b in heading:
    head.update(range(a, b + 1))
group = sorted({int(e[0]) for e in ents} & head)
book_units = [float(e[3].replace(',', '.')) for e in ents if int(e[0]) in head]

rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
prim = json.loads((RAW / 'main/selection-ids.json').read_text())['site_primary_ids']['Dholavira']
mass = {i: rows[i - 1]['mass_g'] for i in prim}
in_group = [i for i in prim if i in set(group)]
rest = [mass[i] for i in prim if i not in set(group)]
fit_rest = analyze.fit(rest, 'indus_binary_decimal')
fit_grp = analyze.fit([mass[i] for i in in_group], 'indus_binary_decimal')
band = [i for i in prim if 1.3 <= mass[i] < 5]
out = {'book_list_ids_enumerated': len(group), 'book_text_says': 95, 'book_mean_of_printed_units_g': float(np.mean(book_units)),
       'in_primary_certain_sample': len(in_group), 'primary_between_1_3_and_5_g': len(band),
       'of_which_in_book_list': sum(1 for i in band if i in set(group)),
       'fit_primary_without_book_list': {k: fit_rest[k] for k in ('n', 'unit_g', 'signal_cv_percent', 'signal_probability')},
       'fit_book_list_members_only': {k: fit_grp[k] for k in ('n', 'unit_g', 'signal_cv_percent', 'signal_probability')},
       'note': 'The book defines the list by deviation from the 13.65 g shekel, so the fit on the remaining objects is conditional on that selection.'}
(PKG / 'review/ghaggar-group-check.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1))
