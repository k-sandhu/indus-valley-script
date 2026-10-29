"""Extract embedded PNGs; loose chart cards and count pages already exist in a snapshot."""
from pathlib import Path
import argparse
import hashlib
import pyarrow.parquet as pq

def embedded_images(release):
    for name, pairs in [('chart_reference',[('image_path','image')]),
                        ('benchmark_rows_v1',[('context_image_path','context_image')]),
                        ('benchmark_rows_v2',[('context_image_path','context_image'),('exact_image_path','exact_image')])]:
        for row in pq.read_table(Path(release)/'data'/f'{name}.parquet').to_pylist():
            for path_key, image_key in pairs:
                if row.get(path_key) and row.get(image_key):
                    yield row[path_key], row[image_key]['bytes']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--release',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); root=a.out.resolve()
    count=0
    for path,data in embedded_images(a.release):
        target=(root/path).resolve()
        if not target.is_relative_to(root):raise ValueError('Image path escapes output folder')
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=data:raise FileExistsError(target)
        target.write_bytes(data);count+=1
    print(f'Extracted {count} embedded PNGs to {root}')

if __name__=='__main__':main()
