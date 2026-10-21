"""Acquire one HTTPS file through validated Windows TLS using the standard library.

Usage: python -I fetch_winhttp.py --url URL --dest NEW_DIRECTORY --name NAME
    --record RECORD --source-id ID --title TITLE --rights-status STATUS --rights-note NOTE

WinHTTP supplies the operating system's certificate-chain handling when OpenSSL
cannot build the server chain. Certificate verification remains enabled.
"""
import argparse
import ctypes
from ctypes import wintypes as w
import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


def main():
    ap = argparse.ArgumentParser()
    for arg in ('url', 'dest', 'name', 'record', 'source-id', 'title', 'rights-status', 'rights-note'):
        ap.add_argument('--' + arg, required=True)
    args = ap.parse_args()
    dest, record = Path(args.dest), Path(args.record)
    if record.exists() or (dest.exists() and any(dest.iterdir())):
        raise ValueError('destination or record already populated')
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / args.name
    url = urlsplit(args.url)
    assert url.scheme == 'https'
    dll = ctypes.WinDLL('winhttp', use_last_error=True)
    signatures = {
        'WinHttpOpen': ([w.LPCWSTR, w.DWORD, w.LPCWSTR, w.LPCWSTR, w.DWORD], w.HANDLE),
        'WinHttpConnect': ([w.HANDLE, w.LPCWSTR, w.WORD, w.DWORD], w.HANDLE),
        'WinHttpOpenRequest': ([w.HANDLE, w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, ctypes.POINTER(w.LPCWSTR), w.DWORD], w.HANDLE),
        'WinHttpSendRequest': ([w.HANDLE, w.LPCWSTR, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, ctypes.c_size_t], w.BOOL),
        'WinHttpReceiveResponse': ([w.HANDLE, w.LPVOID], w.BOOL),
        'WinHttpReadData': ([w.HANDLE, w.LPVOID, w.DWORD, ctypes.POINTER(w.DWORD)], w.BOOL),
        'WinHttpQueryHeaders': ([w.HANDLE, w.DWORD, w.LPCWSTR, w.LPVOID, ctypes.POINTER(w.DWORD), ctypes.POINTER(w.DWORD)], w.BOOL),
        'WinHttpCloseHandle': ([w.HANDLE], w.BOOL),
    }
    for name, (params, result) in signatures.items():
        function = getattr(dll, name)
        function.argtypes, function.restype = params, result
    def check(result):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return result
    handles = []
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec = dict(source_id=args.source_id, title=args.title, url=args.url, local_path=target.as_posix(),
               retrieved_utc_start=started, rights_status=args.rights_status, rights_note=args.rights_note,
               transport='stdlib-ctypes-WinHTTP-validated-TLS', prior_failure='urllib OpenSSL incomplete certificate chain')
    try:
        session = check(dll.WinHttpOpen('indus-research-kb/1.0', 0, None, None, 0)); handles.append(session)
        conn = check(dll.WinHttpConnect(session, url.hostname, url.port or 443, 0)); handles.append(conn)
        request = check(dll.WinHttpOpenRequest(conn, 'GET', url.path + ('?' + url.query if url.query else ''), None, None, None, 0x00800000)); handles.append(request)
        check(dll.WinHttpSendRequest(request, None, 0, None, 0, 0, 0))
        check(dll.WinHttpReceiveResponse(request, None))
        status, size = w.DWORD(), w.DWORD(4)
        check(dll.WinHttpQueryHeaders(request, 19 | 0x20000000, None, ctypes.byref(status), ctypes.byref(size), None))
        rec['http_status'] = status.value
        if status.value != 200:
            raise ValueError('HTTP ' + str(status.value))
        buffer, got = ctypes.create_string_buffer(1 << 20), w.DWORD()
        h256, h1, count = hashlib.sha256(), hashlib.sha1(), 0
        with target.open('wb') as out:
            while True:
                check(dll.WinHttpReadData(request, buffer, len(buffer), ctypes.byref(got)))
                if not got.value:
                    break
                chunk = buffer.raw[:got.value]
                out.write(chunk); h256.update(chunk); h1.update(chunk); count += len(chunk)
        rec.update(bytes=count, sha256=h256.hexdigest(), sha1=h1.hexdigest(), status='acquired')
    except Exception as exc:
        rec.update(status='failed', error=repr(exc), bytes=target.stat().st_size if target.exists() else 0)
        raise
    finally:
        for handle in reversed(handles):
            dll.WinHttpCloseHandle(handle)
        rec['retrieved_utc_end'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(rec))


if __name__ == '__main__':
    main()
