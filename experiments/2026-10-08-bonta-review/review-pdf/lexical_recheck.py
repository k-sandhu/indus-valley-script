"""Reviewer reimplementation of the bundle-permutation lexical test, with alternative origin classes.

Reads the frozen selection (local raw) and the pinned Monier-Williams file (local raw), imports no
package code, and writes aggregate JSON beside this script. From the repository root:

    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/lexical_recheck.py
"""
import collections, itertools, json, math, random, re, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
SEL = RAW / 'pdf-2026-10-09-v1/lexical-selection-v2.json'
MW = RAW / 'acquisition-2026-10-08-v1/mw.txt'
OUTDIR = Path(__file__).resolve().parent

GROUPS = ['aA', 'iI', 'uU', 'fF', 'xX', 'kKgG', 'cCjJ', 'wWqQ', 'tTdD', 'pPbB', 'sSz', 'nR']
CM = {c: g[0] for g in GROUPS for c in g}


def norm(s):
    return ''.join(CM.get(c, c) for c in s)


def heads_of(path):
    heads = set()
    with path.open(encoding='utf-8') as f:
        for line in f:
            i = line.find('<k1>')
            if i >= 0:
                h = line[i + 4:line.find('<', i + 4)]
                if re.fullmatch('[A-Za-z]+', h):
                    heads.add(h)
    return heads


HEADS = heads_of(MW)
NHEADS = {norm(h) for h in HEADS}


def run(seqs, bundles, initial_only, endpoint, seed=1, draws=1999):
    """Observed whole-headword matches and the bundle-permutation null for the given sequences."""
    lex = HEADS if endpoint == 'exact' else NHEADS
    cache = {}

    def hit(donors):
        if donors in cache:
            return cache[donors]
        opts = []
        for pos, d in enumerate(donors):
            v = bundles[d]
            if pos:
                v = [x for x in v if x not in initial_only.get(str(d), [])]
            opts.append(v)
        res = False
        for combo in itertools.product(*opts):
            w = ''.join(combo)
            if (w if endpoint == 'exact' else norm(w)) in lex:
                res = True
                break
        cache[donors] = res
        return res

    involved = sorted({r for s in seqs for r in s})
    obs_flags = [hit(tuple(s)) for s in seqs]
    obs = sum(obs_flags)
    n = math.factorial(len(involved))
    if n <= 40320:
        assignments = list(itertools.permutations(involved))
        exh = True
    else:
        rng = random.Random(seed)
        assignments = [tuple(rng.sample(involved, len(involved))) for _ in range(draws)]
        exh = False
    scores = []
    for a in assignments:
        mp = dict(zip(involved, a))
        scores.append(sum(hit(tuple(mp[r] for r in s)) for s in seqs))
    ge = sum(x >= obs for x in scores)
    tail = ge / len(scores) if exh else (ge + 1) / (len(scores) + 1)
    return {'sequences': len(seqs), 'roles': len(involved), 'observed': obs,
            'null_mean': round(sum(scores) / len(scores), 4), 'null_n': len(scores), 'at_least_observed': ge,
            'tail': tail, 'exhaustive': exh, 'null_histogram': dict(sorted(collections.Counter(scores).items())), 'matched_sequences': [list(s) for s, h in zip(seqs, obs_flags) if h]}


CLASSES = [range(1, 14), range(14, 17), range(17, 35), range(35, 37), range(37, 53), range(53, 59)]


def run_classed(seqs, bundles, initial_only, endpoint, seed=1, draws=1999):
    """Same observed count; null permutes bundles only among roles of the same Table 18 class."""
    lex = HEADS if endpoint == 'exact' else NHEADS
    cache = {}

    def hit(donors):
        if donors in cache:
            return cache[donors]
        opts = []
        for pos, d in enumerate(donors):
            v = bundles[d]
            if pos:
                v = [x for x in v if x not in initial_only.get(str(d), [])]
            opts.append(v)
        res = any(((''.join(c)) if endpoint == 'exact' else norm(''.join(c))) in lex for c in itertools.product(*opts))
        cache[donors] = res
        return res

    involved = sorted({r for s in seqs for r in s})
    groups = [[r for r in involved if r in c] for c in CLASSES]
    obs = sum(hit(tuple(s)) for s in seqs)
    rng = random.Random(seed)
    scores = []
    for _ in range(draws):
        mp = {}
        for g in groups:
            sh = g[:]
            rng.shuffle(sh)
            mp.update(dict(zip(g, sh)))
        scores.append(sum(hit(tuple(mp[r] for r in s)) for s in seqs))
    ge = sum(x >= obs for x in scores)
    return {'sequences': len(seqs), 'observed': obs, 'null_mean': round(sum(scores) / len(scores), 4),
            'null_n': draws, 'at_least_observed': ge, 'tail': (ge + 1) / (draws + 1),
            'null_min': min(scores), 'null_max': max(scores), 'class_sizes': [len(g) for g in groups]}


def main():
    sel = json.loads(SEL.read_text(encoding='utf-8'))
    init = sel['initial_only_slp1']
    b0 = {int(k): v for k, v in sel['table18_role_variants_slp1'].items()}
    out = {'status': 'Exploratory (reviewer reimplementation, own seed 777 for Monte Carlo panels)',
           'headwords': len(HEADS), 'mw_sha256': hashlib.sha256(MW.read_bytes()).hexdigest()}

    def seqs_of(caption_only, allowed=None):
        pop = [r for r in sel['readings'] if not caption_only or r['basis'].startswith('explicit caption')]
        s = sorted({tuple(r['roles']) for r in pop if len(r['roles']) >= 2})
        if allowed is not None:
            s = [x for x in s if set(x) <= allowed]
        occ = sum(1 for r in pop if len(r['roles']) >= 2 and (allowed is None or set(r['roles']) <= allowed))
        return s, occ

    out['broad'] = {}
    for cap in (False, True):
        s, occ = seqs_of(cap)
        for ep in ('exact', 'normalized'):
            r = run(s, b0, init, ep, seed=777)
            r['multi_role_occurrences'] = occ
            out['broad'][f'{"caption" if cap else "full"}_{ep}'] = r

    out['class_restricted_null'] = {}
    for cap in (False, True):
        sq, _ = seqs_of(cap)
        for ep in ('exact', 'normalized'):
            out['class_restricted_null'][f'{"caption" if cap else "full"}_{ep}'] = run_classed(sq, b0, init, ep, seed=778)

    author = {6, 17, 18, 19, 36, 48, 49}
    ba = dict(b0)
    ba[6] = [v for v in b0[6] if v not in ('maha', 'mahA')]
    ba[17] = [v for v in b0[17] if v != 'bala']

    variants = {
        'A0_author_clear_origin': (author, {6: ba[6], 17: ba[17]}),
        # Anchors as the paper's pp. 43-55 describe them, with fish and the 2014 predicate values added,
        # and with the lexical pAla reading removed (pala only).
        'V1_anchors_pala_only': ({6, 17, 18, 19, 36, 29, 50, 51, 52}, {6: ['ma', 'mA'], 17: ['pala'], 29: ['mIna']}),
        # V1 with pAla restored (author treatment of PAla) and no ASHVA/GO.
        'V2_anchors_with_pAla': ({6, 17, 18, 19, 36, 29, 50, 51, 52}, {6: ['ma', 'mA'], 17: ['pala', 'pAla'], 29: ['mIna']}),
        # Author set plus fish and the three 2014 predicate/asset values.
        'V3_author_plus_fish_and_predicates': (author | {29, 50, 51, 52}, {6: ba[6], 17: ba[17], 29: ['mIna']}),
        # Author set without ASHVA/GO, whose support in the paper is their own readings.
        'V4_author_without_ASHVA_GO': ({6, 17, 18, 19, 36}, {6: ba[6], 17: ba[17]}),
        # V3 plus cAru (value 'caru' from the pot-like drawing in numeral contexts, PDF p. 185) and the numeral-sign
        # syllabic values vI and (e)ka, which the paper links to the stroke numerals (PDF pp. 113, 183).
        'V6_V3_plus_caru_and_numeral_signs': (author | {29, 50, 51, 52, 31, 12, 15}, {6: ba[6], 17: ba[17], 29: ['mIna'], 31: ['caru']}),
        # Author set without the sequences that need the fitted maha (all of mA): only types the clear-origin values can match.
        'V7_author_without_mA_types': ({17, 18, 19, 48}, {17: ba[17]}),
        # Author set with PAla restricted to the metrological value pala.
        'V5_author_pala_only': (author, {6: ba[6], 17: ['pala']}),
    }
    out['variants'] = {}
    for name, (roles, edits) in variants.items():
        b = dict(b0)
        b.update(edits)
        for cap in (True, False):
            s, occ = seqs_of(cap, roles)
            entry = {'roles_allowed': sorted(roles), 'bundle_edits': edits, 'multi_role_occurrences': occ,
                     'sequence_list': [list(x) for x in s]}
            for ep in ('exact', 'normalized'):
                entry[ep] = run(s, b, init, ep) if s else None
            out['variants'][f'{name}__{"caption" if cap else "full"}'] = entry
    (OUTDIR / 'lexical-recheck.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    for k, r in out['broad'].items():
        print('broad', k, r['observed'], r['sequences'], r['null_mean'], r['tail'])
    for k, r in out['class_restricted_null'].items():
        print('classed', k, r)
    for k, v in out['variants'].items():
        for ep in ('exact', 'normalized'):
            r = v[ep]
            print(k, ep, None if r is None else (r['observed'], r['sequences'], r['null_mean'], r['tail'], r['matched_sequences']))


if __name__ == '__main__':
    main()
