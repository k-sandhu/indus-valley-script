"""Screen frozen-inventory files for credentials, email addresses, embedded images, record fields,
long quotations, earlier local-only rules and size. Email addresses are written masked; quotation
candidates are written only to the ignored raw directory."""
from pathlib import Path
from collections import Counter
import json, os, re, sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-13-publication-screen'
TEXT_SUFFIXES = {'.json', '.jsonl', '.csv', '.tsv', '.md', '.html', '.htm', '.js', '.txt', '.svg', '.geojson',
                 '.py', '.yml', '.yaml', '.tpl', '.css', '.sh', '.map', '.sha256', ''}
TOKENS = {
    'github': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})',
    'openai_anthropic': rb'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{35,}',
    'huggingface': rb'hf_[A-Za-z0-9]{30,}',
    'aws_key_id': rb'(?:AKIA|ASIA)[0-9A-Z]{16}',
    'google_api': rb'AIza[0-9A-Za-z_-]{35}',
    'slack': rb'xox[abprs]-[A-Za-z0-9-]{10,}',
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----',
    'bearer_header': rb'(?i)authorization["\']?\s*[:=]\s*["\']?bearer\s+[A-Za-z0-9._~+/-]{20,}',
    'signed_url': rb'(?i)(?:X-Amz-Signature|X-Goog-Signature|[?&]Signature=|[?&]sig=[A-Za-z0-9%]{20,}|[?&]token=[A-Za-z0-9._%-]{20,}|[?&]Expires=\d{9,})',
    'cookie_header': rb'(?i)(?:set-cookie|"cookie"\s*:)',
    'password_assignment': rb'(?i)(?:password|passwd|secret_key|api_key|apikey|access_token)["\']?\s*[:=]\s*["\'][^"\'\s]{8,}',
}
TOKENS = {k: re.compile(v) for k, v in TOKENS.items()}
EMAIL = re.compile(rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
FIELDS = [b'"signs_reading_rtl"', b'"signs_visual_ltr"', b'"text_code_visual_ltr"', b'"sequence"', b'"target_code"',
          b'"source_text"', b'"caption"', b'"excerpt"', b'<LEND>', b'"translation"', b'"transliteration"',
          b'"quote"', b'"quotation"', b'"text"', b'"codes"', b'"context"']
IMAGE_EMBED = re.compile(rb'data:image/[a-z+]+;base64,')
QUOTE_FIELDS = re.compile(r'"(quote|quotation|excerpt|source_text|translation|transliteration|text|snippet|passage|definition|entry_text|gloss_text)"\s*:\s*"((?:[^"\\]|\\.){80,})"')
MD_QUOTE = re.compile(r'(?:^>\s?(.+)$)|(?:“([^”]{80,})”)|(?:(?<![=\w])"([^"\n]{80,})")', re.M)


def mask(addr):
    local, _, domain = addr.partition('@')
    return f'{local[:1]}***@{domain}'


def gitignore_local_rules():
    rules = []
    for line in (ROOT / '.gitignore').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('!'):
            rules.append(line)
    return rules


def main():
    inv_name = sys.argv[1] if len(sys.argv) > 1 else 'inventory.json'
    out_name = sys.argv[2] if len(sys.argv) > 2 else 'payload-scan.json'
    inv = json.loads((RAW / inv_name).read_text(encoding='utf-8'))
    omissions = set(json.loads((ROOT / 'experiments/2026-10-11-public-release/public-omissions.json').read_text(encoding='utf-8'))['targets'])
    owners = [a for a in (subprocess_email(), os.environ.get('SCREEN_OWNER_EMAIL')) if a]
    results, quotes = [], {}
    emails_all = Counter()
    for f in inv['files']:
        if f['bytes'] is None:
            continue
        path = f['path']
        b = (ROOT / path).read_bytes()
        rec = {'path': path, 'bytes': f['bytes'], 'kind': f['kind']}
        cred = {k: len(p.findall(b)) for k, p in TOKENS.items()}
        cred = {k: v for k, v in cred.items() if v}
        if cred:
            rec['credential_patterns'] = cred
        is_text = Path(path).suffix.lower() in TEXT_SUFFIXES
        em = sorted(set(m.decode('ascii', 'replace') for m in EMAIL.findall(b))) if is_text else []
        em = [e for e in em if not re.search(r'\.(png|jpg|svg|gif|js|css)$', e)]
        if em:
            rec['emails_masked'] = sorted(set(mask(e) for e in em))
            for e in em:
                emails_all[mask(e)] += 1
        low = b.lower()
        for a in owners:
            if a.lower().encode() in low or a.split('@')[0].lower().encode() in low:
                rec['owner_address_or_local_part_present'] = True
        n_img = len(IMAGE_EMBED.findall(b))
        if n_img:
            rec['embedded_images'] = n_img
        suffix = Path(path).suffix.lower()
        if suffix in TEXT_SUFFIXES:
            fc = {k.decode(): b.count(k) for k in FIELDS}
            fc = {k: v for k, v in fc.items() if v >= 15}
            if fc:
                rec['field_signatures'] = fc
            t = b.decode('utf-8', 'replace')
            cand = []
            for m in QUOTE_FIELDS.finditer(t):
                words = len(m.group(2).split())
                if words > 15:
                    cand.append({'field': m.group(1), 'words': words, 'text': m.group(2)[:400]})
            if suffix in {'.md', '.txt', '.html', '.tpl'}:
                for m in MD_QUOTE.finditer(t):
                    s = next(g for g in m.groups() if g)
                    if len(s.split()) > 15:
                        cand.append({'field': 'prose-quote', 'words': len(s.split()), 'text': s[:400]})
            if cand:
                rec['long_quote_candidates'] = len(cand)
                quotes[path] = cand
        flags = []
        if path in omissions:
            flags.append('october-11-public-omission')
        if path.startswith('data/') and path not in ('data/README.md',):
            flags.append('audit_git_payload-forbidden-data-path')
        if path.startswith('.github/workflows/'):
            flags.append('ci-workflow')
        if f['bytes'] > 100 * 1024 * 1024:
            flags.append('over-100MB')
        elif f['bytes'] > 50 * 1024 * 1024:
            flags.append('over-50MB')
        elif f['bytes'] > 5 * 1024 * 1024:
            flags.append('over-5MB')
        if flags:
            rec['flags'] = flags
        if len(rec) > 3:
            results.append(rec)
    out = {'scope': 'Credential signatures, email addresses (masked), embedded base64 images, record-field counts >=15, '
                    'long quotation candidates (>15 words in quote-like JSON fields or quoted prose), earlier omissions and size.',
           'files_screened': sum(1 for f in inv['files'] if f['bytes'] is not None),
           'owner_addresses_checked': len(owners),
           'files_with_credential_patterns': sum(1 for r in results if 'credential_patterns' in r),
           'files_with_emails': sum(1 for r in results if 'emails_masked' in r),
           'files_with_owner_address_or_local_part': sum(1 for r in results if r.get('owner_address_or_local_part_present')),
           'distinct_emails_masked': dict(emails_all),
           'files_with_embedded_images': sum(1 for r in results if 'embedded_images' in r),
           'files_with_field_signatures': sum(1 for r in results if 'field_signatures' in r),
           'files_with_long_quote_candidates': sum(1 for r in results if 'long_quote_candidates' in r),
           'files': results}
    (HERE / out_name).write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    (RAW / out_name.replace('.json', '-quotes.json')).write_text(json.dumps(quotes, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'files'}, indent=1))


def subprocess_email():
    """Return the configured Git address; the owner's personal address is supplied in SCREEN_OWNER_EMAIL."""
    import subprocess
    try:
        return subprocess.check_output(['git', 'config', 'user.email'], cwd=ROOT).decode().strip() or None
    except Exception:
        return None


if __name__ == '__main__':
    main()
