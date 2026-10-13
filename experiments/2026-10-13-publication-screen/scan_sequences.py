"""Count Lipi (ICIT-coded) sequence windows of length four or more in screened files.

Reads the frozen inventory and the local Lipi and earlier-website corpora. Writes per-file counts to
the package directory and the matched stretches themselves only to the ignored raw directory.

Passes
- strict: three-digit tokens joined only by separator characters (the protocol's decision pass);
- loose: one- to three-digit integers padded to three digits (protocol discovery pass);
- broad: optional W prefix, and underscore, dot, colon, semicolon or equals also join (added after the first run);
- stream: W-prefixed or bare three-digit tokens within 80 characters join regardless of intervening text
  (added after the first run, to find context windows split across JSON fields);
- short complete texts: strict runs of exactly two or three codes that equal a complete Lipi text.
"""
from pathlib import Path
from collections import Counter
import json, re, sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-13-publication-screen'
NORM = ROOT / 'data/normalized'
N = 4
STREAM_GAP = 80
TEXT_SUFFIXES = {'.json', '.jsonl', '.csv', '.tsv', '.md', '.html', '.htm', '.js', '.txt', '.svg', '.geojson',
                 '.py', '.yml', '.yaml', '.tpl', '.css', '.sh', '.map', '.sha256', ''}
SEP = re.compile(r'[\s,"\'\[\]()+\-/|>→←·]*')
BROAD_SEP = re.compile(r'[\s,"\'\[\]()+\-/|>_.:;=→←·]*')
STRICT = re.compile(r'(?<![0-9A-Za-z_.])\d{3}(?![0-9A-Za-z_])')
LOOSE = re.compile(r'(?<![0-9A-Za-z_.])\d{1,3}(?![0-9A-Za-z_.])')
BROAD = re.compile(r'(?<![0-9A-Za-z.])W?(\d{3})(?![0-9A-Za-z])')


def windows(seq):
    return [tuple(seq[i:i + N]) for i in range(len(seq) - N + 1)]


def load_index():
    grams, texts, web_grams, short = set(), {}, set(), {}
    sources = Counter()
    for fname in ('lipi_observed_faces.jsonl', 'lipi_observed_parts.jsonl'):
        for line in open(NORM / fname, encoding='utf-8'):
            r = json.loads(line)
            for key in ('signs_reading_rtl', 'signs_visual_ltr'):
                seq = tuple(r[key])
                for w in windows(seq):
                    if set(w) != {'000'}:
                        grams.add(w)
                if fname.startswith('lipi_observed_faces'):
                    if len(seq) >= N:
                        texts.setdefault(seq, r['record_id'])
                    elif len(seq) in (2, 3) and '000' not in seq:
                        short.setdefault(seq, r['record_id'])
            sources[fname] += 1
    for line in open(NORM / 'indus_website_observed.jsonl', encoding='utf-8'):
        r = json.loads(line)
        seqs = [r['signs_visual_ltr'], list(reversed(r['signs_visual_ltr']))]
        seqs += r.get('parts_visual_ltr', []) + r.get('parts_reading_rtl', [])
        for seq in seqs:
            for w in windows(seq):
                if set(w) != {'000'} and all(re.fullmatch(r'\d{3}', c) for c in w):
                    web_grams.add(tuple(w))
    return grams, texts, web_grams, short, sources


def runs(text, pattern, sep=SEP, stream=False, minimum=N):
    """Yield lists of padded code tokens joined by separators (or by proximity when stream=True)."""
    cur, last_end = [], None
    for m in pattern.finditer(text):
        tok = (m.group(1) if m.groups() else m.group()).zfill(3)
        if last_end is None:
            joined = False
        elif stream:
            joined = m.start() - last_end <= STREAM_GAP
        else:
            joined = sep.fullmatch(text, last_end, m.start()) is not None
        if joined:
            cur.append(tok)
        else:
            if len(cur) >= minimum:
                yield cur
            cur = [tok]
        last_end = m.end()
    if len(cur) >= minimum:
        yield cur


def scan(text, grams, texts, web_grams, pattern, sep=SEP, stream=False):
    matched = web_only = 0
    stretches = []
    for run in runs(text, pattern, sep, stream):
        ws = windows(run)
        flags = [w in grams for w in ws]
        matched += sum(flags)
        web_only += sum(1 for w, f in zip(ws, flags) if not f and w in web_grams)
        i = 0
        while i < len(flags):
            if flags[i]:
                j = i
                while j + 1 < len(flags) and flags[j + 1]:
                    j += 1
                stretches.append(tuple(run[i:j + N]))
                i = j + 1
            else:
                i += 1
    lengths = Counter(len(s) for s in stretches)
    full = [s for s in stretches if s in texts]
    return {'matched_windows': matched, 'website_only_windows': web_only, 'stretches': len(stretches),
            'stretches_ge5': sum(v for k, v in lengths.items() if k >= 5),
            'stretches_ge6': sum(v for k, v in lengths.items() if k >= 6),
            'longest': max(lengths) if lengths else 0,
            'full_text_stretches': len(full), 'distinct_full_texts': len(set(full)),
            'distinct_stretches': len(set(stretches))}, stretches, full


def short_texts(text, short):
    hits = Counter()
    for run in runs(text, STRICT, minimum=2):
        if len(run) in (2, 3) and tuple(run) in short:
            hits[tuple(run)] += 1
    return hits


def main():
    inv_name = sys.argv[1] if len(sys.argv) > 1 else 'inventory.json'
    out_name = sys.argv[2] if len(sys.argv) > 2 else 'sequence-scan.json'
    inv = json.loads((RAW / inv_name).read_text(encoding='utf-8'))
    grams, texts, web_grams, short, sources = load_index()
    keys = ('matched_windows', 'stretches', 'longest', 'distinct_full_texts')
    results, detail = [], {}
    for f in inv['files']:
        if f['bytes'] is None or Path(f['path']).suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = (ROOT / f['path']).read_bytes().decode('utf-8', errors='replace')
        strict, s_str, s_full = scan(text, grams, texts, web_grams, STRICT)
        loose, l_str, _ = scan(text, grams, texts, web_grams, LOOSE)
        broad, b_str, _ = scan(text, grams, texts, web_grams, BROAD, BROAD_SEP)
        stream, st_str, _ = scan(text, grams, texts, web_grams, BROAD, stream=True)
        sh = short_texts(text, short)
        rec = {'path': f['path'], 'bytes': f['bytes'], 'strict': strict,
               'loose': {k: loose[k] for k in keys}, 'broad': {k: broad[k] for k in keys},
               'stream': {k: stream[k] for k in keys},
               'short_complete_texts': {'runs': sum(sh.values()), 'distinct': len(sh),
                                        'length3_distinct': sum(1 for t in sh if len(t) == 3)}}
        results.append(rec)
        if strict['stretches'] or loose['stretches'] or broad['stretches'] or stream['stretches'] or len(sh) >= 5:
            def top(x, k=8):
                return [['-'.join(s), n] for s, n in Counter(x).most_common(k)]
            detail[f['path']] = {'strict': top(s_str, 15),
                                 'strict_full_texts': ['-'.join(s) for s in sorted(set(s_full), key=len, reverse=True)[:10]],
                                 'loose': top(l_str), 'broad': top(b_str), 'stream': top(st_str),
                                 'short_texts': [['-'.join(s), n] for s, n in sh.most_common(8)]}
    hits = [r for r in results if r['strict']['stretches'] or r['loose']['stretches'] or r['broad']['stretches']
            or r['stream']['stretches'] or r['short_complete_texts']['distinct'] >= 5]
    out = {'index': {'lipi_records_read': dict(sources), 'lipi_4gram_windows': len(grams),
                     'lipi_full_texts_len_ge4': len(texts), 'lipi_short_texts_len_2_3': len(short),
                     'website_4gram_windows': len(web_grams), 'window_length': N},
           'scope': __doc__.split('Passes', 1)[1].strip(),
           'files_scanned': len(results),
           'files_with_strict_matches': sum(1 for r in results if r['strict']['stretches']),
           'files_with_loose_only_matches': sum(1 for r in results if r['loose']['stretches'] and not r['strict']['stretches']),
           'files_with_broad_matches': sum(1 for r in results if r['broad']['stretches']),
           'files_with_stream_matches': sum(1 for r in results if r['stream']['stretches']),
           'files_with_5plus_short_texts': sum(1 for r in results if r['short_complete_texts']['distinct'] >= 5),
           'files': sorted(hits, key=lambda r: (-r['strict']['matched_windows'], -r['stream']['matched_windows'], r['path']))}
    (HERE / out_name).write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    (RAW / out_name.replace('.json', '-stretches.json')).write_text(json.dumps(detail, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k not in ('files', 'scope')}, indent=1))


if __name__ == '__main__':
    main()
