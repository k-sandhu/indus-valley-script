"""Run the shared anonymous public-file fetcher with an explicit TLS limitation.

Usage: python -I fetch_recorded_tls.py SHARED_FETCHER [shared arguments]

The caller must include an acquisition note stating that TLS peer authentication
was unavailable. This fallback authenticates no server and sends no credentials.
The acquired bytes remain untrusted, hashed, local source data.
"""
import runpy
import ssl
import sys
import urllib.request

if '--note' not in sys.argv or 'TLS peer authentication was not verified' not in sys.argv[sys.argv.index('--note')+1]:
    raise SystemExit('an explicit acquisition limitation is required')
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=context)))
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0],run_name='__main__')
