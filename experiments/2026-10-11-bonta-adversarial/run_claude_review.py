"""Requested external CLI review through subscription authentication only."""
from pathlib import Path
import os,subprocess,json,datetime
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-11-bonta-adversarial'
def main():
    cli=Path(os.environ['USERPROFILE'])/'.local/bin/claude.exe'
    blocked={'ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_BASE_URL','CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY','CLAUDE_CODE_API_KEY_HELPER_TTL_MS'}
    env={k:v for k,v in os.environ.items() if k not in blocked}
    settings=json.dumps({'apiKeyHelper':''})
    status=subprocess.run([str(cli),'--safe-mode','--settings',settings,'auth','status','--json'],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',check=True)
    auth=json.loads(status.stdout)
    if not auth.get('loggedIn') or auth.get('authMethod')!='claude.ai':raise SystemExit('No subscription login; do not fall back to a key')
    dest=HERE/'claude-review.md';record=HERE/'claude-review-execution.json';raw=RAW/'claude-opus-5-5-review.json'
    if any(p.exists() for p in [dest,record,raw]):raise SystemExit('Preserve earlier reviews')
    args=[str(cli),'--safe-mode','--settings',settings,'--model','claude-opus-5-5','--print','--output-format','json','--tools','Read,Glob,Grep','--allowedTools','Read','Glob','Grep','--permission-mode','dontAsk','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--no-session-persistence','--effort','high']
    prompt=(HERE/'claude-review-prompt.md').read_text(encoding='utf-8')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    print('Opus 5.5 subscription review started; read-only tools',flush=True)
    run=subprocess.run(args,cwd=ROOT,env=env,input=prompt,capture_output=True,text=True,encoding='utf-8')
    raw.write_text(run.stdout,encoding='utf-8')
    result=json.loads(run.stdout)
    actual=list(result.get('modelUsage',{}))
    success=run.returncode==0 and not result.get('is_error') and 'claude-opus-5-5' in actual
    public={'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested_model':'claude-opus-5-5','actual_models':actual,'authentication':'claude.ai subscription; API-key/helper/cloud overrides disabled','exit_code':run.returncode,'success':success,'num_turns':result.get('num_turns'),'permission_denials':result.get('permission_denials',[]),'usage':result.get('usage'),'modelUsage':result.get('modelUsage'),'scope':'External read-only review; raw CLI JSON remains local'}
    record.write_text(json.dumps(public,indent=2)+'\n',encoding='utf-8')
    dest.write_text(result.get('result','No review response')+'\n',encoding='utf-8')
    print(json.dumps({k:public[k] for k in ['success','actual_models','exit_code','num_turns']}),flush=True)
    if not success:raise SystemExit(1)
if __name__=='__main__':main()
