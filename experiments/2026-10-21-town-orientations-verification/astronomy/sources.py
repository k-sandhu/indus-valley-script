"""Retrieve the complete independent source set, with pinned cached witnesses."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from acquire import main,tap
from records import *
if __name__=='__main__':
    main()
    tap('simbad-thuban-pm-v1.json',"SELECT b.main_id,m.pmra,m.pmde,m.bibcode FROM basic AS b JOIN ident AS i ON b.oid=i.oidref JOIN mesPM AS m ON b.oid=m.oidref WHERE i.id='HIP 68756'")
    tap('simbad-thuban-plx-v1.json',"SELECT m.* FROM basic AS b JOIN ident AS i ON b.oid=i.oidref JOIN mesPLX AS m ON b.oid=m.oidref WHERE i.id='HIP 68756'")
    for res in (30,90):
        download(f'https://copernicus-dem-{res}m.s3.amazonaws.com/tileList.txt',RAW/f'tileList-{res}.txt','Copernicus DEM licence; AWS tile inventory; local-only raw reference.')
    download('https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf',
       RAW/'License-COPDEM-30.pdf','Licence for Copernicus DEM instance COP-DEM-GLO-30-F Global 30m Full, Free & Open. Local licence witness.')
