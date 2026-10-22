"""Preserve the initial search endpoint before a candidate-register repair."""
import shutil
from pathlib import Path
p=Path(__file__).parent
dest=p/'prior-search-2026-10-21'
dest.mkdir(exist_ok=True)
for name in ['unnamed-search.csv','unnamed-summary.json','unnamed-line-review.csv','unnamed-line-review.json']:
    if (p/name).exists() and not (dest/name).exists():shutil.copyfile(p/name,dest/name)
print('Initial search endpoint preserved.')
