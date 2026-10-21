"""Record source attempts for which the shared fetcher wrote no response record.

Usage: python -I record_failures.py --raw-root DIR --acquisition-dir DIR --out JSON
"""
import argparse
import datetime
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser()
    for arg in ('raw-root','acquisition-dir','out'): ap.add_argument('--'+arg,required=True,type=Path)
    a=ap.parse_args(); records=[]
    methods={1:'shared urllib default TLS',2:'shared urllib with Windows ROOT and CA certificates',
        3:'stdlib WinHTTP validated TLS',4:'Git curl Schannel validated TLS',
        5:'shared urllib with Windows certificates and Git CA bundle',
        6:'shared urllib with Windows certificates and Git and certifi CA bundles',
        7:'Windows system curl Schannel validated TLS'}
    for version,method in methods.items():
        path=a.acquisition_dir/f'oracc-oakk-archive-v{version}.json'
        directory=a.raw_root/f'src-oracc-oakk-archive-v{version}'
        if not path.exists():
            created=datetime.datetime.fromtimestamp(directory.stat().st_birthtime,datetime.timezone.utc).isoformat()
            rec=dict(source_id='oracc-oakk',url='https://oracc.museum.upenn.edu/json/epsd2-admin-oakk.zip',
                status='failed',transport=method,attempt_directory_created_utc=created,
                recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                time_basis='directory creation timestamp; the shared fetcher exited before writing its own record',
                bytes=0,sha256=None,local_path=None,error='SSL certificate verification failed: unable to get local issuer certificate',
                rights_status='rights-unverified',rights_note='No source payload acquired in this attempt')
            path.write_text(json.dumps(rec,indent=1)+'\n',encoding='utf-8')
        rec=json.loads(path.read_text(encoding='utf-8'))
        records.append(dict(record=path.as_posix(),transport=method,status=rec.get('status','failed'),bytes=rec.get('bytes',0),sha256=rec.get('sha256'),error=rec.get('error')))
    a.out.write_text(json.dumps(records,indent=1)+'\n',encoding='utf-8')
    print(json.dumps(dict(failed_attempts=len(records),response_bytes=sum(r['bytes'] for r in records))))


if __name__=='__main__': main()
