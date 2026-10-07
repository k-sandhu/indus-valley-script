"""Reviewer scan of the package's tracked files for corpus content.

Looks for (a) any run of three or more consecutive corpus sign codes (both reading orders, common
separators) and (b) the key 'record_id' or any corpus record_id longer than five characters, in the
package directory (excluding review/). Also counts single-face and two-face strata in the tracked
stratified tables, where a table row can expose the sign multiset of one object.
Writes review/tracked_output_scan.json with counts only.
"""
import json, re, csv, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-chronology-region'
rows = [json.loads(l) for l in open(ROOT / 'data/normalized/lipi_observed_faces.jsonl', encoding='utf-8')]
grams = set()
for r in rows:
    for seq in (r['signs_reading_rtl'], r['signs_visual_ltr']):
        for n in (3, 4, 5):
            for j in range(len(seq) - n + 1):
                g = seq[j:j + n]
                if '000' in g: continue
                for sep in (' ', ',', '-', '.', ', ', '/'): grams.add(sep.join(g))
text_ext = {'.json', '.csv', '.md', '.py', '.txt', '.html'}
files = [p for p in sorted(PKG.rglob('*')) if p.is_file() and 'review' not in p.relative_to(PKG).parts and p.name != 'REVIEW.md' and p.suffix.lower() in text_ext]
blob = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in files)
ngram_hits = [g for g in grams if len(g) >= 11 and g in blob]
rid_key_data = sum(len(re.findall(r'record_id', p.read_text(encoding='utf-8', errors='replace'))) for p in files if p.suffix.lower() in {'.json', '.csv'})
rid_key_code_docs = sum(len(re.findall(r'record_id', p.read_text(encoding='utf-8', errors='replace'))) for p in files if p.suffix.lower() not in {'.json', '.csv'})
rids = [r['record_id'] for r in rows if len(r['record_id']) > 5]
rid_values = [x for x in rids if x in blob]

# broader pattern: runs of three-digit codes with optional quotes or brackets between them, compared with corpus trigrams
g3 = set()
for r in rows:
    for seq in (r['signs_reading_rtl'], r['signs_visual_ltr']):
        for j in range(len(seq) - 2):
            t3 = tuple(seq[j:j + 3])
            if '000' not in t3: g3.add(t3)
run = re.compile(r'(?<![\d.])(?:["\[\(]?\d{3}["\]\)]?\s*[,;:/.\- ]\s*){2,}["\[\(]?\d{3}["\]\)]?(?![\d.])')
trigram_hits = 0
for p_ in files:
    for m in run.finditer(p_.read_text(encoding='utf-8', errors='replace')):
        codes = re.findall(r'\d{3}', m.group(0))
        trigram_hits += sum(tuple(codes[j:j + 3]) in g3 or tuple(reversed(codes[j:j + 3])) in g3 for j in range(len(codes) - 2))

def table(name): return list(csv.DictReader(open(PKG / 'main-2026-10-07-v1' / name, encoding='utf-8', newline='')))
single = {}
for name in ['region_type_strata.csv', 'site_type_strata.csv', 'harappa_label_type_strata.csv', 'harappa_major_type_strata.csv', 'all_site_time_strata.csv']:
    t = table(name)
    one = [x for x in t if int(x['faces']) == 1]
    single[name] = {'cells': len(t), 'cells_with_one_face': len(one), 'cells_with_two_faces': sum(int(x['faces']) == 2 for x in t),
                    'one_face_cells_with_clear_ordered_text': sum(int(x['clear_faces']) == 1 for x in one),
                    'one_face_clear_cells_with_three_or_fewer_slots': sum(int(x['clear_faces']) == 1 and int(x['observed_slots']) <= 3 for x in one)}
out = {'status': 'Reviewer check, not a package result', 'text_files_scanned': len(files), 'corpus_sign_ngram_strings_searched': len(grams),
       'sign_ngrams_of_three_or_more_signs_found_in_tracked_text': len(ngram_hits), 'code_runs_equal_to_a_corpus_trigram_with_quotes_or_brackets_allowed': trigram_hits, 'occurrences_of_record_id_in_json_and_csv_files': rid_key_data, 'occurrences_of_record_id_in_code_and_documents': rid_key_code_docs,
       'corpus_record_id_strings_found': rid_values, 'single_face_strata': single}
Path(__file__).with_name('tracked_output_scan.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps(out, indent=2))
