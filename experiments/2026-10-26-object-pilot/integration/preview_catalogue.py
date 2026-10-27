"""Read-only localhost preview for an explicit HTML file and its local file links."""
import argparse,html,mimetypes,re,sys
from pathlib import Path
from urllib.parse import urlparse,unquote,quote
from http.server import BaseHTTPRequestHandler,HTTPServer
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
ALLOWED=[ROOT.resolve(),Path('D:/projects/indus_valley_script').resolve()]
def within(p):return any(p.is_relative_to(root) for root in ALLOWED)
def prepare(path):
    path=path.resolve();assert within(path) and path.is_file()
    assets={};paths={}
    def replace(m):
        raw=html.unescape(m[2]);u=urlparse(raw)
        if u.scheme!='file':return m[0]
        assert u.netloc in ('','localhost'),'Remote file URI forbidden'
        name=unquote(u.path)
        if re.match(r'^/[A-Za-z]:/',name):name=name[1:]
        p=Path(name).resolve();assert within(p),f'Outside allowed roots: {p}'
        if not p.is_file():return m[0]
        if p not in paths:
            key=f'/asset/{len(assets)+1}/{quote(p.name)}';assets[key]=p;paths[p]=key
        return m[1]+html.escape(paths[p]+('#'+u.fragment if u.fragment else ''),quote=True)+m[3]
    page=re.sub(r'((?:href|src)=[\"\x27])(file:[^\"\x27]+)([\"\x27])',replace,path.read_text(encoding='utf8'))
    return page.encode('utf8'),assets
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--html',type=Path,required=True);ap.add_argument('--port',type=int,required=True);a=ap.parse_args()
    assert 1024<=a.port<=65535
    page,assets=prepare(a.html)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            route=urlparse(self.path).path
            if route in ('/','/index.html'):body=page;typ='text/html; charset=utf-8'
            elif route in assets:
                p=assets[route];body=p.read_bytes();typ=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
        def do_HEAD(self):self.send_error(405)
        def log_message(self,fmt,*args):pass
    server=HTTPServer(('127.0.0.1',a.port),Handler)
    print(f'http://127.0.0.1:{a.port}/ — {len(assets)} exact local assets; read-only; Ctrl-C stops',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
