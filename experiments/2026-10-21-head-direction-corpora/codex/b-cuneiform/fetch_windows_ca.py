"""Run the shared fetcher with Windows intermediate certificates, preserving TLS checks.

Usage: python -I fetch_windows_ca.py SHARED_FETCHER [shared fetcher arguments]
"""
import runpy
import ssl
import sys
import urllib.request
from pathlib import Path
import site

context = ssl.create_default_context()
bundle = Path('C:/Program Files/Git/usr/ssl/certs/ca-bundle.crt')
if bundle.exists():
    context.load_verify_locations(cafile=str(bundle))
bundle = Path(site.getusersitepackages()) / 'certifi/cacert.pem'
if bundle.exists():
    context.load_verify_locations(cafile=str(bundle))
for store in ('ROOT', 'CA'):
    for certificate, encoding, trust in ssl.enum_certificates(store):
        if encoding == 'x509_asn' and (trust is True or ssl.Purpose.SERVER_AUTH.oid in trust):
            context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(certificate))
urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=context)))
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
