"""Reviewer's independent descriptor coding (written before opening the package's coder rows).

Each row follows the package's descriptor definitions in PROTOCOL.md and its 7 October clarification.
Drawings were viewed at 4x to 30x in the local raw directory (renders of the preserved brochure page 4,
the pinned Unicode 18.0 charts and the atlas cell images). The reviewer saw only the identifiers of the
package's matched pairs (run-v1-query-matches.json) and coder B's prose notes before coding; no package
descriptor row was opened until this file was complete.

Rule used for the two subjective fields, applied to every drawing:
  orientation: direction of the longest straight segment; 'mixed' when the two longest directions are
               within about 10% of each other and for closed curved figures; single curved strokes use
               the direction of their overall extent (U shapes vertical, arches and waves horizontal).
  symmetry:    reflection symmetry within ordinary drawing irregularity.

Writes review/reviewer-coding.json.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'reviewer-coding.json'
KEYS = ['segments', 'curved', 'loops', 'L', 'T', 'X', 'Y', 'other', 'terminals', 'components', 'dots', 'symmetry', 'orientation']


def row(inv, id_, seg, cur, loops, L, T, X, Y, oth, term, comp, dots, sym, ori, unc=False, note=''):
    r = dict(inventory=inv, id=id_, segments=seg, curved=cur, loops=loops, L=L, T=T, X=X, Y=Y, other=oth,
             terminals=term, components=comp, dots=dots, symmetry=sym, orientation=ori, uncertain=unc, note=note)
    return r


rows = []
t = lambda n, *a, **k: rows.append(row('tamil', 'T%02d' % n, *a, **k))
#      id  seg cur loops L  T  X  Y  oth term comp dots sym        ori
t(1,   3, 0, 1, 2, 0, 1, 0, 0, 2, 1, 0, 'vertical', 'diagonal')
t(2,   2, 0, 0, 1, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'diagonal')
t(3,   3, 0, 0, 0, 0, 0, 1, 0, 3, 1, 0, 'vertical', 'diagonal')
t(4,   3, 0, 0, 0, 0, 0, 1, 0, 3, 1, 0, 'vertical', 'diagonal')
t(5,   4, 0, 0, 0, 0, 0, 0, 1, 4, 1, 0, 'vertical', 'diagonal')
t(6,   3, 0, 1, 3, 0, 0, 0, 0, 0, 1, 0, 'vertical', 'diagonal')
t(7,  10, 0, 8, 3, 14, 0, 0, 0, 0, 1, 0, 'vertical', 'diagonal', note='7 interior rungs plus base; apex corner added after comparison (first pass had L=2)')
t(8,   4, 0, 2, 2, 1, 0, 1, 0, 0, 1, 0, 'vertical', 'diagonal')
t(9,   3, 0, 0, 0, 0, 0, 0, 1, 4, 1, 0, 'vertical', 'vertical')
t(10,  3, 0, 0, 0, 0, 0, 0, 1, 4, 1, 0, 'horizontal', 'horizontal')
t(11,  3, 0, 0, 0, 0, 0, 0, 1, 4, 1, 0, 'vertical', 'vertical')
t(12,  5, 0, 0, 0, 0, 0, 0, 2, 6, 1, 0, 'vertical', 'vertical')
t(13,  3, 0, 0, 0, 0, 0, 1, 0, 3, 1, 0, 'vertical', 'vertical')
t(14,  4, 0, 1, 1, 2, 1, 0, 0, 4, 1, 0, 'vertical', 'diagonal', note='barbs continue the upper lines')
t(15,  1, 1, 0, 0, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'vertical', note='U with straight sides, one smooth segment')
t(16,  2, 2, 0, 0, 0, 0, 0, 0, 4, 2, 0, 'vertical', 'vertical')
t(17,  1, 1, 0, 0, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'horizontal')
t(18,  5, 1, 2, 2, 1, 1, 1, 0, 2, 1, 0, 'vertical', 'horizontal')
t(19,  1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 'both', 'mixed')
t(20,  3, 1, 4, 0, 4, 1, 0, 0, 0, 1, 0, 'both', 'mixed')
t(21,  3, 0, 0, 2, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'vertical')
t(22,  4, 0, 1, 4, 0, 0, 0, 0, 0, 1, 0, 'both', 'vertical')
t(23,  9, 0, 6, 0, 14, 0, 0, 0, 4, 1, 0, 'both', 'vertical', note='7 rungs')
t(24,  4, 0, 0, 2, 1, 0, 0, 0, 3, 1, 0, 'vertical', 'vertical')
t(25,  5, 0, 0, 2, 2, 0, 0, 0, 4, 1, 0, 'vertical', 'horizontal')
t(26,  5, 0, 0, 2, 2, 0, 0, 0, 4, 1, 0, 'vertical', 'horizontal', True, 'bar 130 vs legs 117: orientation borderline')
t(27,  5, 0, 0, 2, 2, 0, 0, 0, 4, 1, 0, 'horizontal', 'vertical', note='E with four arms')
t(28,  4, 0, 0, 2, 1, 0, 0, 0, 3, 1, 0, 'vertical', 'mixed')
t(29,  2, 0, 0, 0, 0, 1, 0, 0, 4, 1, 0, 'both', 'mixed')
t(30,  2, 0, 0, 0, 0, 1, 0, 0, 4, 1, 0, 'both', 'diagonal')
t(31,  3, 0, 0, 0, 0, 0, 0, 1, 6, 1, 0, 'both', 'diagonal', note='degree-six centre')
t(32,  4, 0, 2, 4, 0, 1, 0, 0, 0, 1, 0, 'both', 'diagonal')
t(33,  6, 0, 0, 4, 0, 1, 0, 0, 4, 1, 0, 'none', 'mixed')
t(34,  1, 1, 0, 0, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'horizontal', note='smooth wave, one segment')
t(35, 13, 0, 0, 0, 0, 0, 1, 5, 13, 1, 0, 'vertical', 'vertical', note='six branch pairs, bottom pair is a Y')
t(36,  2, 0, 0, 0, 1, 0, 0, 0, 3, 1, 0, 'none', 'diagonal')
t(37,  2, 0, 0, 1, 0, 0, 0, 0, 2, 1, 0, 'none', 'vertical')
t(38,  5, 0, 1, 3, 0, 0, 1, 0, 1, 1, 0, 'vertical', 'vertical')
t(39,  1, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 'both', 'vertical')
t(40,  4, 3, 1, 0, 0, 0, 2, 0, 2, 1, 0, 'vertical', 'mixed', True, 'open top loop; neck contacts coded Y')
t(41,  3, 0, 1, 1, 1, 1, 0, 0, 3, 1, 0, 'none', 'diagonal', True, 'crossbar overshoots right diagonal')
t(42,  5, 4, 0, 0, 0, 0, 2, 0, 4, 1, 0, 'both', 'vertical', True, 'four curls, each one open spiral arc')

u = lambda c, *a, **k: rows.append(row('tifinagh', 'U%04X' % c, *a, **k))
#        seg cur loops L T X Y oth term comp dots sym        ori
u(0x2D30, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 'both', 'mixed')
u(0x2D31, 2, 1, 2, 0, 2, 0, 0, 0, 0, 1, 0, 'both', 'mixed')
u(0x2D32, 3, 1, 4, 0, 4, 1, 0, 0, 0, 1, 0, 'both', 'mixed')
u(0x2D33, 3, 0, 1, 2, 0, 1, 0, 0, 2, 1, 0, 'vertical', 'diagonal')
u(0x2D34, 3, 0, 1, 2, 0, 1, 0, 0, 2, 1, 0, 'vertical', 'diagonal')
u(0x2D35, 4, 0, 2, 4, 0, 1, 0, 0, 0, 1, 0, 'both', 'diagonal')
u(0x2D36, 3, 0, 0, 0, 0, 0, 0, 0, 2, 3, 2, 'vertical', 'vertical')
u(0x2D37, 2, 0, 0, 1, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'diagonal')
u(0x2D38, 2, 0, 0, 1, 0, 0, 0, 0, 2, 1, 0, 'vertical', 'diagonal')
u(0x2D39, 4, 0, 0, 2, 1, 0, 0, 0, 3, 1, 0, 'horizontal', 'vertical')
u(0x2D3A, 4, 0, 0, 2, 1, 0, 0, 0, 3, 1, 0, 'horizontal', 'vertical')
u(0x2D3B, 3, 2, 2, 0, 0, 0, 0, 0, 2, 3, 0, 'both', 'horizontal')
u(0x2D3C, 7, 0, 0, 4, 2, 0, 0, 0, 4, 1, 0, 'both', 'vertical')
u(0x2D3D, 4, 0, 1, 3, 1, 0, 0, 0, 1, 1, 0, 'none', 'mixed')
u(0x2D3E, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 'horizontal', 'mixed')
u(0x2D3F, 4, 0, 1, 3, 1, 0, 0, 0, 1, 1, 0, 'none', 'mixed')
u(0x2D40, 2, 1, 2, 0, 2, 0, 0, 0, 0, 1, 0, 'both', 'mixed')
u(0x2D41, 2, 1, 2, 0, 0, 2, 0, 0, 2, 1, 0, 'diagonal', 'mixed')
u(0x2D42, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 'both', 'vertical')
u(0x2D43, 2, 0, 0, 0, 1, 0, 0, 0, 3, 1, 0, 'none', 'diagonal')
u(0x2D44, 4, 0, 0, 2, 1, 0, 0, 0, 3, 1, 0, 'vertical', 'vertical')
u(0x2D45, 3, 0, 0, 0, 0, 0, 0, 1, 5, 1, 0, 'vertical', 'diagonal')
u(0x2D46, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 'both', 'mixed')
u(0x2D47, 4, 0, 1, 2, 0, 0, 1, 0, 1, 1, 0, 'none', 'mixed')
u(0x2D48, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 'both', 'horizontal')
u(0x2D49, 4, 0, 0, 3, 0, 0, 0, 0, 2, 1, 0, 'horizontal', 'diagonal')
u(0x2D4A, 3, 0, 0, 0, 2, 0, 0, 0, 4, 1, 0, 'both', 'vertical')
u(0x2D4B, 2, 2, 0, 0, 0, 1, 0, 0, 4, 1, 0, 'both', 'vertical', True, 'two arcs touching at one point')
u(0x2D4C, 4, 0, 1, 0, 0, 4, 0, 0, 8, 1, 0, 'both', 'mixed')
u(0x2D4D, 3, 0, 0, 0, 2, 0, 0, 0, 4, 1, 0, 'none', 'vertical')
u(0x2D4E, 3, 0, 0, 2, 0, 0, 0, 0, 2, 1, 0, 'horizontal', 'vertical')
u(0x2D4F, 1, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 'both', 'vertical')

o = lambda c, *a, **k: rows.append(row('ogham', 'U%04X' % c, *a, **k))
# Stem letters only. The five lozenge letters U1690-U1694 are not recoded: filled lozenges need an interpretation
# the reviewer cannot make independently of the package's convention.
for k, c in enumerate(range(0x1681, 0x1686), start=1):      # strokes below the stem
    o(c, k + 1, 0, 0, 0, k, 0, 0, 0, k + 2, 1, 0, 'vertical', 'horizontal')
for k, c in enumerate(range(0x1686, 0x168B), start=1):      # strokes above the stem
    o(c, k + 1, 0, 0, 0, k, 0, 0, 0, k + 2, 1, 0, 'vertical', 'horizontal')
o(0x168B, 2, 0, 0, 0, 0, 1, 0, 0, 4, 1, 0, 'diagonal', 'diagonal', True, 'slash across stemline; oblique mirror only')
for k, c in enumerate(range(0x168C, 0x1690), start=2):      # k diagonal strokes across the stem
    o(c, k + 1, 0, 0, 0, 0, k, 0, 0, 2 * k + 2, 1, 0, 'none', 'mixed', True, 'stroke/stem lengths about equal')

i = lambda n, *a, **k: rows.append(row('indus', 'I%02d' % n, *a, **k))
#      seg cur loops L  T  X  Y  oth term comp dots sym        ori
i(2,   7, 0, 0, 0, 0, 0, 1, 1, 9, 3, 0, 'vertical', 'vertical', True, 'figure between two bars')
i(3,  10, 0, 0, 1, 0, 0, 2, 2, 8, 1, 0, 'vertical', 'vertical', True, 'two figures joined by V-shaped arms')
i(5,   8, 2, 2, 1, 1, 0, 1, 1, 4, 2, 0, 'none', 'mixed', True, 'figure with V arm to ringed circle')
i(6,   4, 2, 1, 1, 2, 1, 0, 0, 4, 1, 0, 'vertical', 'vertical')
i(7,   4, 2, 1, 1, 2, 1, 0, 0, 4, 1, 0, 'vertical', 'vertical', True, 'four short corner ticks ignored')
i(9,   6, 2, 1, 2, 2, 1, 0, 0, 6, 2, 0, 'vertical', 'vertical', True, 'separate caret above apex')
i(12,  4, 2, 2, 0, 2, 1, 0, 0, 2, 1, 0, 'none', 'vertical', True, 'tangent ellipses coded as X')
i(13,  3, 0, 0, 0, 0, 0, 1, 0, 3, 1, 0, 'vertical', 'vertical')
i(14,  9, 2, 3, 6, 1, 0, 0, 2, 1, 1, 0, 'none', 'vertical', True, 'curved stem, three leaf loops, two four-way contacts')
i(17,  1, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 'both', 'vertical')
i(18,  5, 0, 0, 0, 0, 0, 0, 0, 10, 5, 0, 'both', 'vertical')
i(19,  6, 0, 0, 0, 0, 0, 0, 0, 12, 6, 0, 'both', 'vertical')
i(20,  4, 4, 0, 0, 0, 0, 0, 0, 8, 4, 0, 'vertical', 'horizontal', True, 'four stacked arches')
i(21,  8, 2, 0, 0, 0, 0, 0, 0, 16, 8, 0, 'both', 'vertical', True, 'strokes inside parentheses')
i(24,  4, 2, 1, 1, 1, 1, 0, 0, 5, 2, 0, 'none', 'vertical', True, 'separate caret above leaf')
i(26,  4, 0, 1, 3, 1, 0, 0, 0, 1, 1, 0, 'vertical', 'vertical')
i(28,  6, 0, 3, 4, 4, 0, 0, 0, 0, 1, 0, 'none', 'vertical')
i(29,  8, 0, 3, 6, 4, 0, 0, 0, 0, 1, 0, 'vertical', 'vertical')
i(30,  6, 0, 1, 4, 2, 0, 0, 0, 2, 1, 0, 'both', 'vertical')
i(31,  5, 0, 2, 0, 6, 0, 0, 0, 4, 1, 0, 'both', 'vertical')
i(32,  7, 0, 4, 0, 8, 2, 0, 0, 6, 1, 0, 'both', 'horizontal', True, 'rungs 290 vs verticals 240')
i(34,  5, 1, 0, 0, 3, 0, 0, 0, 5, 1, 0, 'vertical', 'vertical', True, 'U with three prongs')
i(35,  6, 1, 0, 1, 3, 0, 0, 0, 7, 2, 0, 'vertical', 'vertical', True, 'separate caret above U with three prongs')
i(41,  6, 0, 0, 0, 0, 0, 0, 0, 12, 6, 0, 'none', 'diagonal', True, 'six parallel strokes')

if __name__ == '__main__':
    OUT.write_text(json.dumps(rows, indent=1), encoding='utf-8')
    from collections import Counter
    print(len(rows), dict(Counter(r['inventory'] for r in rows)))
