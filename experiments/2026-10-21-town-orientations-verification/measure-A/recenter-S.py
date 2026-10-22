"""Fresh, explicitly recentered renders of an already held composite."""
import subprocess,sys,shutil
from pathlib import Path
source,directory,lat,lon=sys.argv[1:]
tool=Path(__file__).resolve().parent.parent/'tools'/'render_image.py'
for size in [2000,800]:
    for layer,edge in [('RGB',False),('NIR',False),('brightness',False),('brightness',True)]:
        if shutil.disk_usage('C:/').free<1073741824:raise RuntimeError('Below 1 GiB free')
        out=Path(directory)/f'recenter-{size}-{layer}{"-edge" if edge else ""}-v1.png'
        cmd=[sys.executable,'-I',str(tool),source,str(out),'--point',lat,lon,'--size',str(size),'--layer',layer,'--upsample','6' if size==800 else '3','--grid','100']
        if edge:cmd.append('--edge')
        subprocess.run(cmd,check=True)
