"""Recompute the focused pass from local witnesses, without new downloads."""
import os,sys
from pathlib import Path
sys.dont_write_bytecode=True
raw=Path(__file__).resolve().parents[3]/'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/tmp'
raw.mkdir(parents=True,exist_ok=True)
for key in ['TMP','TEMP','MPLCONFIGDIR']:os.environ[key]=str(raw)
from focused_classify import run as classify
from focused_records import run as records
from focused_analysis import run as analyze
from focused_registers import run as register
from focused_sources import run as sources
classify();records();analyze();register();sources()
