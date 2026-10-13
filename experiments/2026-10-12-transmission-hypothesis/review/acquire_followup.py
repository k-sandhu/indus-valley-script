"""Separate disclosed transport exception and added scholarly comparator."""
from datetime import datetime, timezone
import hashlib
import json
import requests
from acquire_controls import capture, RAW, REPO


def author_pdf():
    key = 'witzel1997-author-tls-exception'
    meta_path = RAW / f'{key}.acquisition.json'
    if meta_path.exists():
        raise FileExistsError(meta_path)
    url = 'https://michaelwitzel.org/wp-content/uploads/2014/06/canon.pdf'
    meta = {'route_id': key, 'requested_url': url,
            'retrieved_utc': datetime.now(timezone.utc).isoformat(),
            'tls_verification': False,
            'transport_note': 'Per-request exception after separately retained hostname-validation failure; no credentials sent or global TLS settings changed.',
            'rights_status': 'rights-unverified', 'redistribution': 'local-only'}
    try:
        r = requests.get(url, timeout=25, verify=False,
                         headers={'User-Agent': 'Mozilla/5.0 research-source-check'})
        ext = '.pdf' if r.content.startswith(b'%PDF') else '.html'
        path = RAW / f'{key}{ext}'
        with path.open('xb') as stream:
            stream.write(r.content)
        meta.update({'resolved_url': r.url, 'status_code': r.status_code,
                     'content_type': r.headers.get('Content-Type'), 'bytes': len(r.content),
                     'sha256': hashlib.sha256(r.content).hexdigest(),
                     'path': path.relative_to(REPO).as_posix(),
                     'successful_pdf': r.status_code == 200 and ext == '.pdf'})
    except requests.RequestException as exc:
        meta.update({'error': str(exc), 'successful_pdf': False})
    with meta_path.open('x', encoding='utf-8') as stream:
        json.dump(meta, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    return meta


if __name__ == '__main__':
    result = [author_pdf(), capture(('skjaervo-kayanian', 'https://www.iranicaonline.org/articles/kayanian-i/'))]
    with (RAW / 'acquisition-v3.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
