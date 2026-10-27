"""Map verified storage aliases back to repository-relative logical paths."""
import json
from pathlib import Path


def repository_relative(path, root):
    path, root = Path(path), Path(root)
    try:
        return path.relative_to(root)
    except ValueError:
        pass
    config = root / 'LOCAL_STORAGE.json'
    if not config.is_file():
        raise ValueError(f'{path} is outside {root}')
    physical_root = Path(json.loads(config.read_text(encoding='utf-8'))['storage_root']).resolve()
    resolved = path.resolve()
    # Windows callers can use either extended-length or ordinary paths.
    canonical = lambda p: Path(str(p).removeprefix('\\\\?\\'))
    relative = canonical(resolved).relative_to(canonical(physical_root))
    logical = root / relative
    if canonical(logical.resolve()) != canonical(resolved):
        raise ValueError(f'{path} has no matching repository storage alias')
    return relative
