"""Pass JSON through stdin to avoid Windows PowerShell native quote removal."""
import sys, runpy
from pathlib import Path
sys.dont_write_bytecode = True
if sys.argv[1] in ('pick', 'finish'):
    sys.argv.append(sys.stdin.read())
sys.argv[0] = str(Path(__file__).with_name('helper-G.py'))
runpy.run_path(sys.argv[0], run_name='__main__')
