"""Preserve distinct alternate public routes after the first access failures."""
from concurrent.futures import ThreadPoolExecutor
import json
import sys
from acquire_controls import capture, RAW

ROUTES = [
    ('oldavestan-lessons-lexicons', 'https://www.lexicons.ru/old/a/avestan/_pdf/old-avestan-exercises.pdf'),
    ('oldavestan-primer-swissbay', 'https://theswissbay.ch/pdf/Books/Linguistics/Mega%20linguistics%20pack/Indo-European/Iranian/Avestan%2C%20Introduction%20to%20Old%20%28Skj%C3%A6rv%C3%B8%29.pdf'),
    ('witzel1997-author-www', 'https://www.michaelwitzel.org/wp-content/uploads/2014/06/canon.pdf'),
    ('witzel1997-institutional', 'https://fid4sa-repository.ub.uni-heidelberg.de/110/1/VedicCanon_1997.pdf'),
    ('pollock1985-doi', 'https://doi.org/10.2307/601525'),
]

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(max_workers=5) as pool:
        result = list(pool.map(capture, ROUTES))
    with (RAW / 'acquisition-v2.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
