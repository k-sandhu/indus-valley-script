"""One-time reporting tag and inventory amendment after final prose fixes."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    p=HERE/'write_package_report_v3.py';s=p.read_text(encoding='utf8')
    for a,b in [('v32','v36'),('v33','v37'),('v34','v38'),('v31','v35'),('r33','r35'),('r34','r36')]:s=s.replace(a,b)
    start=s.index('    with (HERE/');end=s.index("    prefix='",start)
    block=s[start:end]
    s=s[:start]+"    if '## 8 October 2026: version 0.3.0' not in (HERE/'RETROSPECTIVE.md').read_text(encoding='utf8'):\n"+'\n'.join('    '+line if line else '' for line in block.splitlines())+'\n'+s[end:]
    s=s.replace('created-paths-v0.3.0-2026-10-08.json','created-paths-v0.3.0-2026-10-08-v2.json');p.write_text(s,encoding='utf8')
    p=HERE/'inventory_v3.py';s=p.read_text(encoding='utf8').replace('created-paths-v0.3.0-2026-10-08.json','created-paths-v0.3.0-2026-10-08-v2.json').replace('completion-checks-v0.3.0-2026-10-08.json','completion-checks-v0.3.0-2026-10-08-v2.json').replace('v34.json','v38.json').replace('v31.json','v35.json')
    start=s.index('    # Windows PowerShell');end=s.index('    completion=dict',start)
    s=s[:start]+"    prose=read(HERE/'prose-review-v0.3.0-2026-10-08-v3.json')\n    owned.add('prose-review-v0.3.0-2026-10-08-v3.json')\n"+s[end:]
    s=s.replace("prose_report='prose-review-v0.3.0-2026-10-08-v2.json'", "prose_report='prose-review-v0.3.0-2026-10-08-v3.json'")
    s=s.replace("    owned.add(output.relative_to(HERE).as_posix())", "    owned.update(p.relative_to(HERE).as_posix() for p in (HERE/'history/2026-10-08-release-v0.2.0').rglob('*') if p.is_file())\n    owned.add(output.relative_to(HERE).as_posix())")
    s=s.replace("dict(source='r33/',destination='release/',files=136)","dict(source='r35/',destination='release/',files=136)").replace("dict(source='r30/, r31/, r32/'", "dict(source='r30/, r31/, r32/, former release r33/'")
    p.write_text(s,encoding='utf8')

if __name__=='__main__':main()
