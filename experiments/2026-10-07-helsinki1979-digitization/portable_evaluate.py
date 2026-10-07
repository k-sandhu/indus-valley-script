"""Run the unchanged frozen evaluator using its owned, byte-identical inputs."""
import contextlib
import io
import json
from pathlib import Path
import sys
import evaluate

HERE=Path(__file__).resolve().parent

class PortableInputRoot:
    """Interpret the historical Windows locator on any checkout platform."""
    def __truediv__(self,relative):
        return HERE/'portable-inputs'/Path(str(relative).replace('\\','/'))

evaluate.ROOT=PortableInputRoot()
if '--out' not in sys.argv:raise SystemExit('Specify --out with a new owned directory')
target=Path(sys.argv[sys.argv.index('--out')+1]).resolve()
if not target.is_relative_to(HERE):raise SystemExit('Output must be inside the owned directory')
with contextlib.redirect_stdout(io.StringIO()):evaluate.main()
path=target/'metrics.json'
original=HERE/'evaluation/2026-10-07-frozen-v1/metrics.json'
print(json.dumps(dict(output=str(path),sha256=evaluate.sha(path),
                     byte_identical_to_frozen=path.read_bytes()==original.read_bytes()),indent=2))
