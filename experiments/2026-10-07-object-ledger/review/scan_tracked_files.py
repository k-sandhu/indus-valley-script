"""Reviewer scan of the package's tracked files for sign sequences and copied third-party prose.

Part 1. Builds every sign sequence of two or more signs from the Lipi and Mayig exports (both directions,
all contiguous runs of three or more signs, plus whole two-sign sequences) and looks for them in every
text file under the package directory, in the hyphen, space, comma, plus-delimited and JSON-array forms.
Part 2. Lists the longest string values in the tracked JSON files and checks word 8-grams of the package
prose and string values against the local source texts and the saved museum record text.

The script prints counts and file names; it never writes sequence content anywhere.

Run from the repository root:  python experiments/2026-10-07-object-ledger/review/scan_tracked_files.py
Writes review/tracked-file-scan.json.
"""
import collections
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-07-object-ledger'
OUT = PKG / 'review' / 'tracked-file-scan.json'


def strip(tok):
    return re.sub(r'^[PW]', '', str(tok))


# ---------- part 1: sequences
seqs = []
for line in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8-sig').splitlines():
    if line.strip():
        r = json.loads(line)
        seqs.append(('lipi', [strip(x) for x in r['signs_visual_ltr']]))
for line in (ROOT / 'data/normalized/mayig_faces.jsonl').read_text(encoding='utf-8-sig').splitlines():
    if line.strip():
        r = json.loads(line)
        seqs.append(('mayig', [strip(x) for x in r['signs_visual_ltr']]))
        gids = [strip(g['id']) for g in r.get('graphemes', []) if isinstance(g, dict) and 'id' in g]
        if gids:
            seqs.append(('mayig_p', gids))

ngrams = {}          # n>=3 contiguous runs -> source label
whole2 = {}          # two-sign sequences (whole inscriptions of length 2)
for label, s in seqs:
    s = [t for t in s if re.fullmatch(r'\d{3}', t)]
    if len(s) == 2:
        whole2[tuple(s)] = label
        whole2[tuple(reversed(s))] = label
    for direction in (s, list(reversed(s))):
        for n in range(3, len(direction) + 1):
            for i in range(0, len(direction) - n + 1):
                ngrams.setdefault(tuple(direction[i:i + n]), label)

TOK = r'(?<![\w.])[PW]?\d{3}(?![\w.])'
RUN = re.compile(r'(?:' + TOK + r')(?:(?:\s*[-,+]\s*|\s+|"\s*,\s*"|\'\s*,\s*\')(?:' + TOK + r'))+')
PLUS2 = re.compile(r'\+(' + TOK + r')-(' + TOK + r')\+?')

TEXT_SUFFIX = {'.json', '.md', '.py', '.csv', '.txt', '.jsonl', '.html'}
hits = collections.defaultdict(list)
files_scanned = 0
bytes_scanned = 0
for p in sorted(PKG.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX:
        continue
    if 'review' in p.relative_to(PKG).parts[:1] and p.name in ('negative_tests.py', 'scan_tracked_files.py'):
        continue
    try:
        text = p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        continue
    files_scanned += 1
    bytes_scanned += len(text)
    for m in RUN.finditer(text):
        toks = [strip(t) for t in re.findall(TOK, m.group(0))]
        if len(toks) >= 3:
            # any 3+ window inside the run that is a corpus run
            found = None
            for n in range(len(toks), 2, -1):
                for i in range(0, len(toks) - n + 1):
                    if tuple(toks[i:i + n]) in ngrams:
                        found = (n, ngrams[tuple(toks[i:i + n])])
                        break
                if found:
                    break
            if found:
                hits[str(p.relative_to(ROOT))].append({'kind': 'run>=3', 'tokens': found[0], 'source': found[1]})
        elif len(toks) == 2 and m.group(0).strip().startswith('+'):
            if tuple(toks) in whole2:
                hits[str(p.relative_to(ROOT))].append({'kind': 'plus-delimited two-sign text', 'source': whole2[tuple(toks)]})
    for m in PLUS2.finditer(text):
        toks = (strip(m.group(1)), strip(m.group(2)))
        if toks in whole2:
            hits[str(p.relative_to(ROOT))].append({'kind': 'plus-delimited two-sign text', 'source': whole2[toks]})

res = {'distinct_runs_of_3_or_more_indexed': len(ngrams), 'two_sign_sequences_indexed': len(whole2) // 2,
       'files_scanned': files_scanned, 'chars_scanned': bytes_scanned,
       'files_with_corpus_sequence_hits': len(hits), 'hits_by_file': {k: len(v) for k, v in hits.items()},
       'hit_kinds': dict(collections.Counter(h['kind'] for v in hits.values() for h in v))}

# ---------- part 2: long strings and prose overlap
def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


long_strings = []
all_json_strings = {}
for p in sorted(PKG.rglob('*.json')):
    rel = p.relative_to(PKG)
    if rel.parts[0].startswith(('replay', 'run-', 'review')) and not rel.parts[0].startswith('run-2026-10-07-v4'):
        continue
    try:
        o = json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        continue
    for s in strings(o):
        if len(s) >= 90:
            all_json_strings.setdefault(s, set()).add(str(rel))
for s, files in all_json_strings.items():
    long_strings.append((len(s), sorted(files)[0], s[:110]))
long_strings.sort(reverse=True)
res['json_strings_90_chars_or_longer'] = len(long_strings)
res['longest_json_string_files'] = [{'chars': n, 'file': f} for n, f, _ in long_strings[:8]]

source_texts = {}
for rel in ['research/literature/sources/meadow_kenoyer_2000_tiny_seals.txt', 'research/corpus/primary/kenoyer_meadow2010_inscribed_objects.txt',
            'experiments/2026-10-02-six-hour/context-audit/local-witness/kenoyer-meadow2010-harp-full.txt', 'data/six-hour/lothal/extracted.txt',
            'research/literature/sources/gadd1932_ocr.txt']:
    p = ROOT / rel
    if p.exists():
        source_texts[rel] = p.read_text(encoding='utf-8', errors='replace')
try:
    import fitz
    d = fitz.open(str(ROOT / 'data/six-hour/lothal/frenez-tosi2005.pdf'))
    source_texts['frenez-tosi2005.pdf (text layer)'] = '\n'.join(pg.get_text() for pg in d)
except Exception:
    pass
museum = json.loads((ROOT / 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/focused-records.json').read_text(encoding='utf-8'))
mus_text = '\n'.join(' '.join(str(v) for k, v in m.items() if k in ('description', 'bibliography', 'date')) + ' ' + ' '.join(str(v) for v in m.get('metadata', {}).values()) for m in museum)
source_texts['saved museum records'] = mus_text


def words(t):
    return re.findall(r"[A-Za-z0-9']+", t.lower())


N = 8
index = {}
for name, t in source_texts.items():
    w = words(t)
    for i in range(len(w) - N + 1):
        index.setdefault(' '.join(w[i:i + N]), name)

overlaps = collections.defaultdict(list)
for p in sorted(PKG.rglob('*.md')):
    if p.parts[-2] == 'review':
        continue
    w = words(p.read_text(encoding='utf-8'))
    for i in range(len(w) - N + 1):
        g = ' '.join(w[i:i + N])
        if g in index:
            overlaps[str(p.relative_to(ROOT))].append((g, index[g]))
for s, files in all_json_strings.items():
    w = words(s)
    for i in range(len(w) - N + 1):
        g = ' '.join(w[i:i + N])
        if g in index:
            overlaps[sorted(files)[0]].append((g, index[g]))
res['source_word_8gram_overlaps_by_file'] = {k: len(v) for k, v in overlaps.items()}
res['source_word_8gram_overlap_examples'] = [{'file': k, 'source': v[0][1], 'ngram': v[0][0]} for k, v in list(overlaps.items())[:6]]
# every overlapping string value, shortened, to show that all are bibliographic titles
overlap_strings = set()
for s in all_json_strings:
    w = words(s)
    if any(' '.join(w[i:i + N]) in index for i in range(len(w) - N + 1)):
        overlap_strings.add(s[:70])
res['strings_with_8gram_overlap_all_json'] = sorted(overlap_strings)

# pairs of three-digit numbers outside this directory's review files (the two-sign texts cannot be told apart by format)
PAIR = re.compile(r'(?<![\w.-])' + TOK + r'(?:\s*[-,]\s*' + TOK + r')+(?![\w-])')
pair_files = collections.Counter()
pair_examples = collections.Counter()
for p in sorted(PKG.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX or p.relative_to(PKG).parts[0] == 'review':
        continue
    t = p.read_text(encoding='utf-8', errors='replace')
    for m in PAIR.finditer(t):
        pair_files[p.suffix.lower()] += 1
        pair_examples[m.group(0)[:20]] += 1
res['runs_of_three_digit_numbers_by_file_type_outside_review'] = dict(pair_files)
res['most_common_such_runs'] = [[k, c] for k, c in pair_examples.most_common(8)]
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(res, indent=1, ensure_ascii=False)[:5000])
