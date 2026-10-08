"""Apply the v3 review to living documents; reuse its preserved calculations."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT = HERE / 'repair/2026-10-08-review-response-v1'
RUN = HERE / 'repair/2026-10-08-v3'
DOCS = ['README.md', 'REPORT.md', 'RETROSPECTIVE.md', 'sources.json', 'registry-entry.json']
METRICS = 'repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json'
REVIEW = 'review-v3/recomputed-v3-claims.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')


def once(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f'Expected one document locator: {before[:70]}')
    return text.replace(before, after, 1)


def fix_spaces(text):
    text = text.replace('\r\n', '\n').replace('\r', '')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'(?m)^(\|[^\n]*\|)\n(?:[ \t]*\n)+(?=\|)', r'\1\n', text)
    for a, b in [('pages(PDF', 'pages (PDF'), ('47,127,172', '47, 127, 172'),
                 ('195.0,390.1', '195.0, 390.1'), ('one, two orfive', 'one, two or five'),
                 ('rows,327/352', 'rows, 327/352'), ('(320 fields),357/369', '(320 fields), 357/369'),
                 ('counts:1,850', 'counts: 1,850'), ('pt(maximum', 'pt (maximum')]:
        text = text.replace(a, b)
    return text


def fix_encoding(value, fixes):
    if isinstance(value, str):
        for a, b in [('\u00e2\u20ac\u201c', '–'), ('\u00e2\u0080\u0093', '–')]:
            count = value.count(a)
            if count:
                fixes['en_dash_replacements'] += count
                value = value.replace(a, b)
        return value
    if isinstance(value, list):
        return [fix_encoding(x, fixes) for x in value]
    if isinstance(value, dict):
        return {k: fix_encoding(v, fixes) for k, v in value.items()}
    return value


def write_documents(record=DEFAULT):
    record = Path(record)
    snapshot = read(record / 'document-snapshot.json')['files']
    response = read(record / 'review-response.json')
    link = record.relative_to(HERE).as_posix()
    provenance = (
        'The v3 reference comes from two Claude Sonnet 5.5 readers and a Claude adjudicator using shared conventions and chart cards, with **no human check**. '
        'The count-page reference was built with pixel scripts that use the same field-block cue as the pipeline, with printed-line spacing as a cross-check. '
        'The rates measure agreement with that reference. [Reader process](repair/2026-10-08-v3/blind/adjudication-notes.json), `agreement_summary`, `counts_comparison`; '
        '[review](REVIEW-V3.md), M3.\n\n')
    sensitivity = (
        'On the same 80 fresh three-section rows, accepting {23} for the isolated ticks at 35:2 and 70:4 would give strict top five **64/80 (80.0%)**, meeting the 64-row threshold. '
        'The frozen shape-only top five is **65/80 (81.3%; Wilson 95% 71.3–88.3%)**. '
        'The declared strict score remains 62/80 and the frozen verdict remains Failed: count is still 72/80 against 76 and number 71/80 against 72 under either reading choice. '
        f'[Review recomputation]({REVIEW}), `sensitivity.strict_top5_if_35_2_and_70_4_were_23`; '
        f'[frozen metrics]({METRICS}), `summary.shape_only_top5.whole_rows_all_sample`, `negative_result_criteria`.\n\n')
    clustering = (
        'The Wilson intervals and row bootstraps do not cluster by source page. V3\'s numbered stratum has 28 rows on only eight pages, with up to six rows per page; '
        'each sorted stratum samples 18 of its 28 eligible pages. These intervals do not capture shared page-geometry variation. '
        f'[Review recomputation]({REVIEW}), `sample_pages`, `eligible_pages_number_order`.\n\n')
    overlap = (
        'The 18 random count pages are new relative to the previous count-page set. Eight (32, 35, 46, 47, 58, 98, 163, 171) carried first-endpoint or v2 recognition targets. '
        f'[Review recomputation]({REVIEW}), `count_page_overlap`.\n\n')
    for name in ['README.md', 'REPORT.md']:
        s = fix_spaces(snapshot[name]['text'])
        marker = '## Three frozen endpoints and their frames' if name == 'REPORT.md' else '| Outcome, Wilson 95% interval'
        if name == 'README.md':
            # Insert immediately before the first table, retaining the whole header.
            at = s.index(marker); s = s[:at] + provenance + s[at:]
        else:
            s = once(s, marker, provenance + marker)
        at = s.index('| V3 frozen criterion')
        s = s[:at] + clustering + s[at:]
        marker = '## Unit recall and confidence calibration' if name == 'REPORT.md' else 'V3 random-page numbered recall and precision'
        at = s.index(marker)
        s = s[:at] + ('## Reading-choice sensitivity\n\n' if name == 'REPORT.md' else '') + sensitivity + s[at:]
        if name == 'README.md':
            s = once(s, 'The count frame is 18 fresh random pages plus stress 62, 129, 130;', 'The count frame is 18 random pages new relative to the previous count-page set plus stress 62, 129, 130;')
            at = s.index('The 18 top-five failures')
            s = s[:at] + overlap + s[at:]
            s = s.replace('Use the immutable [option-B contract]', 'Use the amended [option-B contract]')
            s = s.replace('and [schema](option-b-schema.json), preserving', 'and [schema](option-b-schema.json) with the hash-pinned proposal payload, preserving')
            s = s.replace("row 31's seven shifted unit windows", "row 31's shifted windows 3–6")
            s += f'\nThe fifth follow-up applies [REVIEW-V3.md](REVIEW-V3.md); its [response]({link}/review-response.json) records the reused sensitivity/probe and [preservation check]({link}/preservation-check.json). The same source attribution applies to the 21 rendered [count-page images](repair/2026-10-08-v3/blind/page-count-source/).\n'
            s = s.replace('Every path changed for this follow-up is listed in [changed-paths.json](repair/2026-10-08-endpoint-record-v1/changed-paths.json).', 'The previous endpoint record lists its [changed paths](repair/2026-10-08-endpoint-record-v1/changed-paths.json); this review response lists its [changed paths]('+link+'/changed-paths.json).')
            s = s.replace('`write_v3_endpoint_docs.py` regenerates these living documents from aggregates and their pre-record snapshots.', '`write_v3_endpoint_docs.py` regenerates these living documents and delegates to `apply_v3_review.write_documents()` when the review-response record exists. To reproduce the small review response from the repository root, run `python experiments/2026-10-07-helsinki1979-digitization/apply_v3_review.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-review-response-repeat`, using a new output path.')
            s += '\nCheck the amendments and protected hashes from the repository root with `python experiments/2026-10-07-helsinki1979-digitization/verify_v3_review.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-review-check-repeat.json`, using a new output file.\n'
        else:
            s = s.replace('| Independent count frame |', '| Count-reference frame |')
            s = once(s, "V3's 18 random pages are fresh relative to the previous count-page set. ", overlap)
            s = s.replace('this count test measures discovery, not sign recognition on those pages.', 'this count test measures matching source rows under the field-block convention, rather than sign recognition on those pages.')
            s = s.replace('Inspecting row 31 shows that the seven windows cut the U and adjacent fish drawings and assign overlapping underline slots.', 'Inspecting row 31 shows that windows 3–6 cut the U and adjacent fish drawings and assign overlapping underline slots; windows 0–2 are well placed.')
            s = s.replace('The criterion gaps count passing rows required at the frozen point thresholds; they are not promises that repairing that many rows would validate a future method.', 'The criterion gaps use the frozen point thresholds. The diagnostic partitions and reading/crop sensitivities are post-outcome analyses and do not replace the frozen endpoint.')
            s = s.replace('These are earliest observed failure stages, not counterfactual accuracy gains.', 'These partitions use the earliest observed failed check.')
            marker = 'Number reading fails in 9/80 rows'
            probe = ('The reviewer\'s **Exploratory crop-trim probe** made six of the eight crop-stage rows top-five compatible: 21, 44, 48, 55, 58 and 66. '
                     'The smallest successful lower-edge trims were 0.5, 1.5, 1.5, 1.0, 0.5 and 1.5 PDF points respectively. '
                     'Neighbour strips of 0.4–1.3 pt change the column projection used to split units, coupling crop bounds to counts and candidate identity. '
                     'Row 58 changes from five to six units; row 66 reaches six instead of seven units at a 0.5 pt trim and becomes top-five compatible at 1.5 pt. '
                     'The passing control row 5 becomes incompatible at a 1.0 pt trim. Rows 76 and 77 were not probed. '
                     'Trim sizes were selected after outcomes, so this is a diagnostic of the lower-edge mechanism rather than a validated fixed-trim repair. '
                     '[Probe](review-v3/counterfactual-bottom-edge.json), per-row trim fields; [controls](review-v3/counterfactual-bottom-edge-control.json), `5`; [review](REVIEW-V3.md), M1.\n\n')
            at = s.index(marker); s = s[:at] + probe + s[at:]
            marker = '| V3 section, frame size |'
            at = s.index(marker)
            s = s[:at] + f'Seven of the nine number errors are single-digit substitutions in equal-length strings; the rows and literals are retained in the [response]({link}/review-response.json), `number_error_details`. Speck windows in rows 14, 60 and 65 and the detached last dash window in row 32 are concrete candidates for a later segmentation repair.\n\n' + s[at:]
            timing = ('The method and prediction files record 14:11:23Z and 14:13:49Z, before the earliest reader start of 15:28:00Z. '
                      'The review confirms the file mtimes and hash chain, but the first Git commit recording the freeze, `0445bad`, is timestamped 15:33:31Z, after readers began. '
                      'Thus the recorded order rests on embedded/file timestamps and the hash chain; Git alone does not establish a pre-reader anchor. '
                      'Later authorized runs should have the coordinator record the freeze commit before launching readers. [Review](REVIEW-V3.md), M5 and Checked claims.\n\n')
            at = s.index('The new record reuses'); s = s[:at] + timing + s[at:]
        (HERE / name).write_text(s, encoding='utf-8')

    retro = fix_spaces(snapshot['RETROSPECTIVE.md']['text'])
    at = retro.index('The new work produces')
    retro = retro[:at] + '**Superseded preparation status.** The following opening records the stage before the coordinator completed the v3 readings. The completed endpoint and reader costs appear below under “Completed v3 endpoint”.\n\n' + retro[at:]
    retro += f'''\n\n## V3 review applied, 8 October 2026

The Claude Sonnet reviewer reproduced every headline figure, the evaluator and endpoint-record replays, the freeze/selection chain and the full inventory. This step reused [REVIEW-V3.md](REVIEW-V3.md) and the scripts/results in [review-v3](review-v3/), leaving them unchanged. It adds AI-reference provenance beside the headlines, with no human check and shared field-block cues in the count scripts. Reading-choice sensitivity now appears beside the frozen strict result: accepting the two isolated ticks as23 gives64/80, and the stored shape-only score is65/80. Count and number still fail; the verdict and quarantine remain unchanged.

The review's post hoc lower-edge probe restores six crop-stage rows and breaks passing control row5; rows76 and77 were not probed. The report records this coupling between crop geometry and unit projection as Exploratory. It also records page clustering, eight count pages with earlier recognition targets and the first freeze commit's time after reader starts. The row31 description now identifies windows3–6. Listed spacing defects and the superseded opening are corrected. The source-location strings were checked and retain proper Unicode en dashes; no mojibake remained in the pre-edit snapshot. The interface document is described as amended, while the proposal payload remains hash-pinned.

No new reference, model inference, crop rule, chart correction or endpoint score was produced. [Response]({link}/review-response.json) preserves the reused calculations and [document snapshot]({link}/document-snapshot.json) preserves the pre-edit wording. [Preservation]({link}/preservation-check.json) covers frozen witnesses and every review file. The shared registry is unchanged; the coordinator can integrate the updated owned registry proposal.

The first post-edit integrity check passed 25 of 26 checks; its only failure was the link to the not-yet-written changed-path inventory. The failed result is retained as `endpoint-check.json`. Creating the inventory resolves that link. Document regeneration now normalizes line endings and retains adjacent table rows; the earlier documentation generator delegates to this amendment so a rerun preserves the corrections. The final integrity and prose checks are stored in the review-response directory.

An ad hoc text check passed Unicode literals through a PowerShell pipe, which converted its en dashes to question marks and produced four false failures. The retained `response-check.json` records that attempt. The file-based `verify_v3_review.py` uses Unicode escapes for those checks and also verifies protected hashes and identical document regeneration.
'''
    retro = retro.replace('as23 gives64/80', 'as {23} gives 64/80').replace('is65/80', 'is 65/80').replace('row5;', 'row 5;').replace('rows76 and77', 'rows 76 and 77').replace('row31', 'row 31').replace('windows3–6', 'windows 3–6')
    (HERE / 'RETROSPECTIVE.md').write_text(retro, encoding='utf-8')
    sources = json.loads(snapshot['sources.json']['text'])
    fixes = dict(en_dash_replacements=0); sources = fix_encoding(sources, fixes)
    assert fixes['en_dash_replacements'] == response['encoding_fixes']['en_dash_replacements']
    sources['sources'].append(dict(id='package-m-v3-review', title='Review of package M, v3 work (8 October 2026)', authors=['Claude Sonnet reviewer'], year=2026,
        venue='Private research repository review', url=None, path='experiments/2026-10-07-helsinki1979-digitization/REVIEW-V3.md', opened=True,
        seen_only_search_snippet=False, quoted_words=0, source_locations=['Verdict', 'Method findings M1–M5', 'Writing', 'Required fixes, ranked'],
        scope='Post-outcome review and exploratory probe; frozen endpoint preserved'))
    dump(HERE / 'sources.json', sources)
    entry = json.loads(snapshot['registry-entry.json']['text'])
    entry['outcome'] += (' V3 rates use two Claude Sonnet 5.5 readers and a Claude adjudicator with shared conventions/cards and no human check; count scripts share the field-block cue with the pipeline. '
                         'Reading sensitivity: strict top five 64/80 if 35:2 and 70:4 accept {23}; frozen shape-only 65/80. Count 72/80 against 76 and number 71/80 against 72 still fail. The original strict verdict remains Failed.')
    entry['challenge'] += ' Row intervals omit page clustering; 8 random count pages carried earlier recognition targets. The first freeze commit follows reader starts despite earlier embedded/file timestamps.'
    entry['remedy'] += ' Applied Sonnet v3 review without editing frozen/review witnesses; reported reading-choice sensitivities and the six-row trim recovery with its broken control.'
    entry['evidence'] = list(dict.fromkeys(entry['evidence'] + ['experiments/2026-10-07-helsinki1979-digitization/'+p for p in ['REVIEW-V3.md', REVIEW, 'review-v3/counterfactual-bottom-edge.json', 'review-v3/counterfactual-bottom-edge-control.json', link+'/review-response.json', link+'/preservation-check.json']]))
    dump(HERE / 'registry-entry.json', entry)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, default=DEFAULT)
    args = ap.parse_args(); out = args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Use a new owned review-response directory')
    old_pin = read(HERE / 'repair/2026-10-08-endpoint-record-v1/preservation-check.json')['hashes']
    assert all(sha(HERE/p) == h for p,h in old_pin.items())
    protected = {p: h for p,h in old_pin.items()}
    protected.update({p.relative_to(HERE).as_posix():sha(p) for p in (HERE / 'review-v3').rglob('*') if p.is_file()})
    protected['REVIEW-V3.md'] = sha(HERE / 'REVIEW-V3.md')
    claims = read(HERE / REVIEW); m = read(HERE / METRICS)
    probe = read(HERE / 'review-v3/counterfactual-bottom-edge.json')
    controls = read(HERE / 'review-v3/counterfactual-bottom-edge-control.json')
    recoveries = {i:min(float(k) for k,v in x.items() if isinstance(v,dict) and v['top5_whole_row']) for i,x in probe.items()}
    assert recoveries == {'21':.5, '55':1., '44':1.5, '48':1.5, '58':.5, '66':1.5}
    assert controls['5']['0.0']['top5_whole_row'] and not controls['5']['1.0']['top5_whole_row']
    assert all(x['reproduces_frozen_top1_at_delta0'] for x in list(probe.values())+list(controls.values()))
    assert claims['sensitivity']['strict_top5_if_35_2_and_70_4_were_23'] == 64
    assert m['summary']['strict_top5']['whole_rows_all_sample']['success'] == 62
    assert m['summary']['shape_only_top5']['whole_rows_all_sample']['success'] == 65
    numbers = []
    for row in m['rows']:
        if not row['number_correct']:
            a,b = row['reference_inscription_number'],row['predicted_inscription_number']
            same = isinstance(a,str) and isinstance(b,str) and len(a)==len(b)
            numbers.append(dict(sample_index=row['sample_index'], reference=a, prediction=b,
                                single_digit_substitution=same and sum(x!=y for x,y in zip(a,b))==1 and a.isdigit() and b.isdigit()))
    assert sum(x['single_digit_substitution'] for x in numbers) == 7
    out.mkdir(parents=True)
    if (DEFAULT / 'document-snapshot.json').exists():
        snapshots = read(DEFAULT / 'document-snapshot.json')['files']
    else:
        snapshots = {name:dict(text=(HERE/name).read_bytes().decode('utf-8'),sha256=sha(HERE/name)) for name in DOCS}
    dump(out / 'document-snapshot.json', dict(status='Verified computation', files=snapshots))
    fixes = dict(en_dash_replacements=0);fix_encoding(json.loads(snapshots['sources.json']['text']),fixes)
    response = dict(status='Exploratory', frozen_verdict='Failed', all_occurrences_quarantined=True,
        provenance='Two Claude Sonnet5.5 readers and a Claude adjudicator; shared conventions/cards; no human check. Count scripts use the pipeline field-block cue.',
        sensitivity=dict(frozen_strict=m['summary']['strict_top5']['whole_rows_all_sample'],accept_23_in_35_2_and_70_4=64,
                         frozen_shape_only=m['summary']['shape_only_top5']['whole_rows_all_sample'],count_required=[72,76],number_required=[71,72]),
        crop_trim_probe=dict(reused=True,rows_recovered=6,crop_stage_rows=8,minimum_successful_trims_pdf_points=recoveries,
                             control_row5_breaks_at_pdf_points=1.,unprobed=[76,77],new_validated_crop_rule=False),
        sample_pages=claims['sample_pages'],count_page_overlap=claims['count_page_overlap'],number_error_details=numbers,
        timing=dict(method_created_utc='2026-10-08T14:11:23Z',prediction_created_utc='2026-10-08T14:13:49Z',
                    earliest_reader_started_utc='2026-10-08T15:28:00Z',first_freeze_commit='0445bad',first_freeze_commit_utc='2026-10-08T15:33:31Z',
                    source='REVIEW-V3.md: Checked claims and M5; no history changed'),
        encoding_fixes=fixes,protected_hashes=protected,reused_outputs=[REVIEW,'review-v3/replay-hashes.json','review-v3/counterfactual-bottom-edge.json','review-v3/counterfactual-bottom-edge-control.json'])
    dump(out/'review-response.json',response)
    write_documents(out)
    assert all(sha(HERE/p)==h for p,h in protected.items())
    dump(out/'preservation-check.json',dict(status='Verified computation',all_unchanged=True,frozen_witnesses=len(old_pin),
        protected_file_count=len(protected),hashes=protected))
    print(json.dumps(dict(output=out.relative_to(HERE).as_posix(),frozen_witnesses=len(old_pin),protected_files=len(protected),encoding_fixes=fixes,reused_probe=True)))


if __name__=='__main__':main()
