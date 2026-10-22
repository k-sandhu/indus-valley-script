"""Shared strict CSV reader for one independent observation per settlement."""
from pathlib import Path
import sys,csv,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'astronomy'))
from records import *
from core import TARGETS
FIELDS=('slug','part','role','lat','lon','theta_deg','sigma_theta_deg','D_year','sigma_D_years')
NUM=FIELDS[3:]
def read_table(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not set(FIELDS)<=set(reader.fieldnames or []): raise ValueError('missing CSV fields')
        rows=list(reader)
    seen=set()
    for row in rows:
        if row['slug'] in seen: raise ValueError('duplicate settlement slug: '+row['slug'])
        seen.add(row['slug'])
        if row['role'] not in ('discovery','confirmation'): raise ValueError('invalid role')
        for k in NUM:
            row[k]=float(row[k])
            if not math.isfinite(row[k]): raise ValueError('nonfinite '+k)
        if row['sigma_theta_deg']<0 or row['sigma_D_years']<0: raise ValueError('negative uncertainty')
        if abs(row['lat'])>90 or abs(row['lon'])>180: raise ValueError('coordinate range')
        for c in TARGETS:
            for k in ('thetac_'+c,'rate_'+c):
                if row.get(k,'')!='':
                    row[k]=float(row[k])
                    if not math.isfinite(row[k]): raise ValueError('nonfinite '+k)
    return rows
