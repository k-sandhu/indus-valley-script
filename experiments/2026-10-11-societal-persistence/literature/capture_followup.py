"""Capture a direct 2026 counterprecedent identified in Jervis's conclusion."""
import json
from pathlib import Path
from capture_sources import OUT, capture, sha

if __name__ == '__main__':
    target = OUT / 'capture-v4.json'
    if target.exists():
        raise FileExistsError(target)
    item = ('L28-priss2026', 'https://www.cambridge.org/core/services/aop-cambridge-core/content/view/9F0354FCAB61E534295AB049C430F6F0/S0003598X2510272Xa.pdf/urban-resilience-in-ancient-mesopotamia-insights-into-the-socioeconomic-system-of-the-bronze-and-iron-age-khabur-valley.pdf')
    row = capture(item, 'capture-v4')
    target.write_text(json.dumps({
        'reason': 'Jervis 2026 explicitly recommends a three-way integration with this archaeological network study. Follow-up selected after the initial census; not a prespecified ranking.',
        'script_sha256': sha(Path(__file__).read_bytes()),
        'capture_helper_sha256': sha(Path(__file__).with_name('capture_sources.py').read_bytes()),
        'attempts': [row],
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(row)
