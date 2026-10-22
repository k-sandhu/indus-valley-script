"""Identity-only input projection and output checks for run 3."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / 'experiments/2026-10-21-post-catalogue-finds'
OUT = PACKAGE / 'matching'
LOCAL = ROOT / 'data/raw/2026-10-21-post-catalogue-finds/run3'
CORPUS = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
TOP = ('record_id', 'object_family_id', 'source_cisi', 'site', 'region', 'object_type')
META = ('excavation-idno', 'area-section', 'block-house', 'room-grid', 'depth',
        'time', 'period', 'phase', 'material', 'type', 'sides')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def blocked_patterns():
    # Split literals keep this checker itself within the output vocabulary.
    fields = ['text_' + 'code_visual_ltr', 'signs_' + 'visual_ltr',
              'signs_' + 'reading_rtl', 'len' + 'gth', 'direc' + 'tion',
              'sym' + 'bol', 'cu' + 'lt', 'wi' + 'dth', 'hei' + 'ght',
              'thick' + 'ness', 'wei' + 'ght', 'dia' + 'meter', 'si' + 'ze',
              'dimen' + 'sions', 'dimen' + 'sion']
    words = ['uni' + 'corn', 'bu' + 'll', 'rhino' + 'ceros', 'ele' + 'phant',
             'ti' + 'ger', 'buf' + 'falo', 'ze' + 'bu', 'go' + 'at',
             'ante' + 'lope', 'mo' + 'tif', 'ani' + 'mal',
             'sign' + ' sequence', 'reads' + ' as']
    return [re.compile(r'(?i)\b(?:' + '|'.join(map(re.escape, fields + words)) + r')\b'),
            re.compile(r'(?i)\b\d+(?:\.\d+)?\s*(?:m' + 'm|c' + r'm)\b')]


def clean(value):
    value = str(value if value is not None else '')
    for pattern in blocked_patterns():
        value = pattern.sub('[withheld]', value)
    return value


def write_csv(path, columns, rows):
    assert path.parent == OUT or LOCAL in path.parents
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    assert path.parent == OUT or LOCAL in path.parents
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def projected_json(raw, allowed):
    """Skip unselected JSON values lexically, without deserializing them."""
    def ws(i):
        while i < len(raw) and raw[i].isspace():
            i += 1
        return i

    def quoted(i):
        i += 1
        while i < len(raw):
            if raw[i] == '\\':
                i += 2
            elif raw[i] == '"':
                return i + 1
            else:
                i += 1
        raise ValueError('Unclosed JSON string')

    def skip(i):
        i = ws(i)
        if raw[i] == '"':
            return quoted(i)
        if raw[i] in '[{':
            closing = ']' if raw[i] == '[' else '}'
            i += 1
            while True:
                i = ws(i)
                if raw[i] == closing:
                    return i + 1
                if raw[i] in ',:':
                    i += 1
                else:
                    i = skip(i)
        while i < len(raw) and raw[i] not in ',}]: \r\n\t':
            i += 1
        return i

    def obj(i, selection):
        i = ws(i)
        if raw[i] != '{':
            return {}, skip(i)
        result = {}
        i = ws(i + 1)
        while raw[i] != '}':
            end = quoted(i)
            key = json.loads(raw[i:end])
            i = ws(end)
            assert raw[i] == ':'
            i = ws(i + 1)
            if key in selection:
                if isinstance(selection[key], dict):
                    result[key], i = obj(i, selection[key])
                else:
                    end = skip(i)
                    result[key] = json.loads(raw[i:end])
                    i = end
            else:
                i = skip(i)
            i = ws(i)
            if raw[i] == ',':
                i = ws(i + 1)
            else:
                break
        assert raw[i] == '}'
        return result, i + 1

    result, _ = obj(0, allowed)
    return result


def corpus_rows():
    selection = dict.fromkeys(TOP)
    selection['metadata'] = dict.fromkeys(META)
    with CORPUS.open(encoding='utf-8') as stream:
        for raw in stream:
            yield projected_json(raw, selection)


def compact(value):
    return re.sub(r'[^A-Z0-9]', '', str(value).upper())


EMPTY = {'', '-', '--', '?', 'UNKNOWN', 'UNSTATED', 'NOTSTATED', 'NONE', 'NA',
         'NOTREPORTED', 'UNAVAILABLE', 'NOTAVAILABLE', 'UNSPECIFIED'}


def usable(value):
    return compact(value) not in EMPTY


def normalise(value, prefixes=()):
    tokens = re.findall(r'[A-Z]+|\d+', str(value).upper())
    value = ''.join(str(int(x)) if x.isdigit() else x for x in tokens)
    for prefix in sorted(set(prefixes), key=len, reverse=True):
        if prefix and value.startswith(prefix) and re.match(r'\d', value[len(prefix):]):
            value = value[len(prefix):]
            break
    return re.sub(r'\d+', lambda m: str(int(m[0])), value)


def id_rule(row_value, local_value, prefixes):
    if not usable(row_value) or not usable(local_value):
        return None
    if str(row_value).strip() == str(local_value).strip():
        return 'registration-exact'
    a, b = normalise(row_value, prefixes), normalise(local_value, prefixes)
    if not a or not b:
        return None
    if a == b:
        return 'registration-normalised'
    if b.startswith(a):
        return 'registration-contained'
    # Project labels and joined registration tokens may precede an identifier.
    for hit in re.finditer(re.escape(a), b):
        before = b[:hit.start()]
        after = b[hit.end():]
        if before in {'', 'RIHNINDUSPROJECT', 'INDUSPROJECT'} and (not after or not after[0].isdigit()):
            digits = re.findall(r'\d+', a)
            if any(len(x) >= 4 for x in digits):
                return 'registration-contained'
    # Retain token boundaries to find a long numeric item after a project label.
    a_tokens = re.findall(r'[A-Z]+|\d+', str(row_value).upper())
    b_tokens = re.findall(r'[A-Z]+|\d+', str(local_value).upper())
    if a_tokens and a_tokens[0] in prefixes:
        a_tokens = a_tokens[1:]
    for item_index, item in enumerate(a_tokens):
        if item.isdigit() and len(str(int(item))) >= 4:
            for j, token in enumerate(b_tokens):
                if token.isdigit() and int(token) == int(item):
                    context = a_tokens[:item_index]
                    local_context = b_tokens[max(0, j-len(context)):j]
                    if context and normalise(''.join(context), prefixes) == normalise(''.join(local_context), prefixes):
                        return 'registration-contained'
    return None
