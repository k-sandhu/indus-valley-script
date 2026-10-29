"""Owner-approved public identifiers and portable provenance transformations."""
from __future__ import annotations
import hashlib
import json
import re

DATASET_ID = 'ksaw008/indus-reference-benchmarks'
ISSUES_URL = 'https://github.com/k-sandhu/indus-reference-benchmarks/issues'
AUTHOR = 'k-sandhu'
MIXED_LICENSE = 'CC BY 4.0 edition content; CC0 1.0 project additions'
LIPI_COMMIT = 'fc8813a52e183d19c441631dc26c33a4dccbea39'

class Portable:
    def __init__(self):
        self.mapping = {}
    def label(self, original):
        for alias, value in self.mapping.items():
            if value == original:
                return alias
        alias = 'source-%04d' % (len(self.mapping) + 1)
        self.mapping[alias] = original
        return alias
    def value(self, obj):
        if isinstance(obj, dict):
            return {k:self.value(v) for k,v in obj.items()}
        if isinstance(obj, list):
            return [self.value(v) for v in obj]
        if not isinstance(obj, str):
            return obj
        if obj[:1] in '[{':
            try:
                return json.dumps(self.value(json.loads(obj)), ensure_ascii=False, sort_keys=True, separators=(',',':'))
            except (ValueError, TypeError):
                pass
        # Keep public release paths and URLs; replace repository-only evidence pointers.
        pat = r'(?<![\w/])(?:experiments|data/(?:raw|normalized)|research|output|raw)/[^\s\"\'<>;,)}\]]+'
        obj = re.sub(pat, lambda m:self.label(m.group()), obj.replace('\\','/'))
        obj = re.sub(r'[A-Za-z]:/Users/[^\s\"\'<>;,)}\]]+', lambda m:self.label(m.group()), obj)
        obj = re.sub(r'https://github\.com/k-sandhu/indus-valley-script[^\s\"\'<>]*', 'Source method summarized in docs/METHODS.md', obj)
        return obj

def bytes_safe(obj):
    """Stable logical hash representation; do not serialize PNG bytes as text."""
    if isinstance(obj, bytes):
        return {'bytes':len(obj),'sha256':hashlib.sha256(obj).hexdigest()}
    if isinstance(obj, dict):
        return {k:bytes_safe(v) for k,v in obj.items()}
    if isinstance(obj, list):
        return [bytes_safe(v) for v in obj]
    return obj
