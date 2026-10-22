"""Locate inputs for the round-seal package.

The package may run from a git worktree whose ignored data directories are empty.
Inputs are then read from the main checkout that owns the shared `.git` directory.
Set INDUS_DATA_ROOT to override.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STUDY_B_REL = Path("experiments/2026-10-12-published-claim-tests/foreign-finds")
FACES_REL = Path("data/normalized/lipi_observed_faces.jsonl")


def _main_checkout() -> Path:
    try:
        common = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        return Path(common).resolve().parent
    except Exception:
        return REPO


def data_root() -> Path:
    env = os.environ.get("INDUS_DATA_ROOT")
    if env:
        return Path(env)
    if (REPO / FACES_REL).exists():
        return REPO
    return _main_checkout()


DATA = data_root()
STUDY_B = (REPO / STUDY_B_REL) if (REPO / STUDY_B_REL / "ffcore.py").exists() else DATA / STUDY_B_REL
RAW = DATA / "data" / "raw" / "2026-10-12-round-seal-tradition"
LIPI_IMAGES = DATA / "data" / "lipi" / "public" / "seal_images"
LIPI_FONT = DATA / "data" / "lipi" / "src" / "assets" / "fonts" / "indus-font.woff2"
LAURSEN_PDF = DATA / "data/raw/2026-10-06-chronology-region/review-response-sources-2026-10-07-v1/laursen2010.pdf"
GADD_PDF = DATA / "data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/gadd1932.pdf"

FROZEN = {
    "ffcore.py": "0d955b5f6e351843b7309c677e5b6c6f93844a5e6bdaf2c8dd71ed9ddfab6102",
    "faces": "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db",
}


def import_ffcore():
    sys.path.insert(0, str(STUDY_B))
    import ffcore  # noqa: E402
    if ffcore.sha256_file(STUDY_B / "ffcore.py") != FROZEN["ffcore.py"]:
        raise RuntimeError("Study B ffcore.py differs from its frozen hash")
    if ffcore.sha256_file(ffcore.FACES) != FROZEN["faces"]:
        raise RuntimeError("normalized Lipi faces differ from the frozen hash")
    return ffcore


def rel(path: Path) -> str:
    """Repository-relative path for records, whichever checkout holds the file."""
    path = Path(path).resolve()
    for base in (REPO, DATA):
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            continue
    return path.as_posix()
