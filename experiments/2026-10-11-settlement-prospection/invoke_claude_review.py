"""Request an explicit Opus-5.5 CLI review of a preserved authored packet."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    a.packet=a.packet.resolve()
    a.output=a.output.resolve()
    if a.output.exists():raise FileExistsError('Review endpoint exists; choose a new version.')
    a.output.mkdir(parents=True)
    env=dict(os.environ)
    # The configured external key failed401. Omit only in this child, using the
    # existing authenticated Claude subscription; never print or persist credentials.
    env.pop('ANTHROPIC_API_KEY',None)
    args=['claude','-p','--model','claude-opus-5-5','--effort','high','--tools','',
          '--strict-mcp-config','--disable-slash-commands','--no-session-persistence',
          '--safe-mode','--output-format','json']
    version=subprocess.run(['claude','--version'],capture_output=True,text=True,encoding='utf-8').stdout.strip()
    started=datetime.now(timezone.utc).isoformat()
    result=subprocess.run(args,input=a.packet.read_text(encoding='utf-8'),env=env,
                          cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=1800)
    # Auth/session details from auth-status were never inserted in this packet.
    (a.output/'cli-result.json').write_text(result.stdout,encoding='utf-8')
    (a.output/'cli-stderr.txt').write_text(result.stderr,encoding='utf-8')
    try:r=json.loads(result.stdout)
    except json.JSONDecodeError:r={}
    if r.get('result'):(a.output/'review.md').write_text(str(r['result'])+'\n',encoding='utf-8')
    metadata=dict(started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),cli_version=version,
                  requested_model='claude-opus-5-5',model_usage=r.get('modelUsage'),exit_code=result.returncode,
                  is_error=r.get('is_error'),terminal_reason=r.get('terminal_reason'),
                  packet_path=a.packet.relative_to(ROOT).as_posix(),packet_sha256=hashlib.sha256(a.packet.read_bytes()).hexdigest(),
                  tools='disabled; review based on supplied authored packet, not independent external source retrieval',
                  authentication='existing Claude subscription; invalid external API key omitted for child process only',
                  permissions='no file mutation, shell, MCP or messaging tools available to reviewer')
    (a.output/'invocation.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:metadata[k] for k in ['cli_version','requested_model','exit_code','is_error','terminal_reason']}))
    if result.returncode or r.get('is_error'):raise SystemExit(1)

if __name__=='__main__':main()
