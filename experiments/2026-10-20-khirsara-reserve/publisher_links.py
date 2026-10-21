import pathlib,re
s=pathlib.Path('data/raw/2026-10-20-khirsara-reserve/publisher-root.response').read_text(encoding='utf-8');print([(a,re.sub('<[^>]*>','',b).strip()) for a,b in re.findall(r'<a[^>]+href=[\x22\x27]([^\x22\x27]+)[\x22\x27][^>]*>(.*?)</a>',s,re.S) if any(w in (a+b).lower() for w in ['darp','publication','journal','pdf','2012','archive'])])
