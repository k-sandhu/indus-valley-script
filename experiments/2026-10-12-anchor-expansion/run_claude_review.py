"""Bounded Opus 5.5 CLI review through subscription authentication only."""
from pathlib import Path
import datetime,json,os,subprocess
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-anchor-expansion'

def main():
    cli=Path(os.environ['USERPROFILE'])/'.local/bin/claude.exe'
    dest=HERE/'claude-review.md';record=HERE/'claude-review-execution.json';raw=RAW/'claude-opus-5-5-review.json'
    if any(p.exists() for p in [dest,record,raw]):raise SystemExit('Preserve previous review outputs')
    blocked={'ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_BASE_URL','CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY','CLAUDE_CODE_API_KEY_HELPER_TTL_MS'}
    env={k:v for k,v in os.environ.items() if k not in blocked};settings=json.dumps({'apiKeyHelper':''})
    if not cli.exists():raise SystemExit('CLI unavailable; no API fallback')
    check=subprocess.run([str(cli),'--safe-mode','--settings',settings,'auth','status','--json'],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
    auth=json.loads(check.stdout)
    if check.returncode or not auth.get('loggedIn') or auth.get('authMethod')!='claude.ai':raise SystemExit('Subscription unavailable; no API fallback')
    args=[str(cli),'--safe-mode','--settings',settings,'--model','claude-opus-5-5','--print','--output-format','json','--tools','Read,Glob,Grep','--allowedTools','Read','Glob','Grep','--permission-mode','dontAsk','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--no-session-persistence','--effort','high','--max-turns','40']
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();print('Opus 5.5 subscription review started; read-only tools',flush=True)
    r=subprocess.run(args,cwd=ROOT,env=env,input=(HERE/'claude-review-prompt.md').read_text(encoding='utf-8'),capture_output=True,text=True,encoding='utf-8')
    raw.write_text(r.stdout,encoding='utf-8')
    try:result=json.loads(r.stdout)
    except ValueError:result={'is_error':True,'result':'CLI did not return JSON; local stderr retained.'}
    (RAW/'claude-review-stderr.txt').write_text(r.stderr,encoding='utf-8')
    actual=list(result.get('modelUsage',{}));success=r.returncode==0 and not result.get('is_error') and 'claude-opus-5-5' in actual and bool(result.get('result'))
    public=dict(started_utc=start,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),requested_model='claude-opus-5-5',actual_models=actual,authentication='claude.ai subscription; API-key/helper/cloud overrides disabled',exit_code=r.returncode,success=success,num_turns=result.get('num_turns'),permission_denials=result.get('permission_denials',[]),usage=result.get('usage'),scope='External read-only review of saved evidence and local images; no calculation execution by reviewer.')
    record.write_text(json.dumps(public,indent=2)+'\n',encoding='utf-8');dest.write_text(result.get('result','No complete review response')+'\n',encoding='utf-8')
    print(json.dumps({k:public[k] for k in ['success','actual_models','exit_code','num_turns']}),flush=True)
    if not success:raise SystemExit(1)

if __name__=='__main__':main()
