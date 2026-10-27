"""Append a new dispatch version for one or more direction updates."""
import json
import sys
from prepare import PACKAGE

latest = max(PACKAGE.glob('dispatch-v*.json'), key=lambda p: int(p.stem.split('-v')[-1]))
rows = json.loads(latest.read_text(encoding='utf-8'))
updates = json.loads(sys.argv[1])
for update in updates:
    row = rows[update['direction'] - 1]
    assert row['direction'] == update['direction']
    row.update(update)
version = int(latest.stem.split('-v')[-1]) + 1
target = PACKAGE / f'dispatch-v{version}.json'
with target.open('x', encoding='utf-8') as stream:
    json.dump(rows, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(target.name)
