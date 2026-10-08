"""Compatibility entry point for the reviewed documentation generator."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from build_release import HERE,read,dump
from release_policy import Portable
from write_release_docs import generate

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,required=True);p.add_argument('--records',type=Path);a=p.parse_args()
    release=a.release.resolve()
    if not release.is_relative_to(HERE):raise ValueError('Use an owned build folder')
    records=a.records or HERE/'build-records'/release.name
    portable=Portable();portable.mapping=read(records/'portable-source-map.json')
    generate(release,SimpleNamespace(records=records,portable=portable))
    dump(records/'portable-source-map.json',portable.mapping)
