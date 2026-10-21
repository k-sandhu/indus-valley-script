"""Shared paths and JSON helpers. Imported by the study commands; no standalone action."""
from pathlib import Path
import hashlib
import json
import unicodedata
import site
import sys

# -I excludes user-site packages. Add only the installed interpreter's package
# directory explicitly, without processing .pth files or loading downloaded code.
TRUSTED_PACKAGES = Path(site.getusersitepackages()).resolve()
if TRUSTED_PACKAGES.is_dir():
    sys.path.append(str(TRUSTED_PACKAGES))

CODE = Path(__file__).resolve().parent
PACKAGE = CODE.parent
ROOT = PACKAGE.parent.parent
RAW = ROOT / 'data/raw/2026-10-21-dravidian-root-meanings'
LOCAL = RAW / 'codex-run1'
DOWNLOADS = RAW / 'downloads'
RUN = PACKAGE / 'run1'
ENTRY = {'FISH':'4885', 'STAR':'4876', 'SIX':'2485', 'SEVEN':'910',
         'THREE':'5052', 'BANYAN':'5220', 'NORTH':'5218', 'EARRING':'4979',
         'YOUTH':'4978', 'SQUIRREL':'4198', 'CHILD':'4198', 'SPACE':'5498',
         'WHITE':'5496a', 'VELGOD':'5528', 'SPINDLE':'1195', 'LIGHT':'1193'}
GROUPS = {'North':['Brahui','Malto','Kurukh'],
          'Central':['Ollari Gadba','Parji','Kolami'],
          'South II':['Kuwi','Gondi','Koya','Telugu'],
          'South I':['Tamil','Malayalam','Kannada','Kodava','Tulu','Yeruva','Toda','Kota','Badaga','Betta Kurumba']}
TIPS = sum(GROUPS.values(), [])
VALUES = ['STAR','NORTH','YOUTH','CHILD','WHITE','VELGOD','LIGHT']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary=path.with_name(path.name+'.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        temporary.replace(path)
    except Exception:
        if temporary.exists(): temporary.unlink()
        raise

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def code_hashes():
    return {str(p.relative_to(CODE)).replace('\\','/'):sha(p)
            for p in sorted(CODE.rglob('*')) if p.is_file()}

def folded(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))
