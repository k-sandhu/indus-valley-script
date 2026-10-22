"""Retrieve independent source witnesses; never execute downloaded material."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *
import urllib.parse
import concurrent.futures

def tap(name, query):
    url='https://simbad.cds.unistra.fr/simbad/sim-tap/sync?'+urllib.parse.urlencode(dict(REQUEST='doQuery',LANG='ADQL',FORMAT='json',QUERY=query))
    return download(url,RAW/name,'SIMBAD/CDS scientific database; cite SIMBAD and each measurement bibcode; raw response local-only.')

def main():
    q="""SELECT b.main_id,b.ra,b.dec,b.pmra,b.pmdec,b.plx_value,b.rvz_radvel,b.coo_bibcode,b.pm_bibcode,b.plx_bibcode,b.rvz_bibcode FROM basic AS b JOIN ident AS i ON b.oid=i.oidref WHERE i.id IN ('HIP 17702','HIP 21421','HIP 37279','HIP 68756')"""
    p=tap('simbad-basic-v1.json',q)
    tap('simbad-schema-v1.json',"SELECT table_name,column_name FROM TAP_SCHEMA.columns WHERE table_name IN ('mesPM','mesPlx','mespos')")
    refs=['ltpequ.c','ltpecl.c','ltpb.c','ltp.c','starpv.c','starpm.c','pvstar.c','t_erfa_c.c']
    def get(n):
        return download('https://raw.githubusercontent.com/liberfa/erfa/master/src/'+n, RAW/'erfa'/n, 'ERFA BSD 3-clause; NumFOCUS; SOFA-derived. Full notice retained in source. Local reference only.')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for v in pool.map(get,refs): print(v.name,flush=True)
    download('https://intcal.org/curves/intcal20.14c',RAW/'intcal20.14c','IntCal20 calibration curve, Reimer et al. 2020; intcal.org. Raw scientific curve local-only; cite publication.')
    download('https://opg.optica.org/ao/abstract.cfm?uri=ao-28-22-4735',RAW/'kasten-young-1989.html','Copyright 1989 Optical Society of America. Local reference only.')
    download('https://copernicus-dem-30m.s3.amazonaws.com/readme.html',RAW/'copernicus-readme.html','Copernicus DEM licence and AWS distribution documentation.')
    print(p.read_text(),flush=True)

if __name__=='__main__': main()
