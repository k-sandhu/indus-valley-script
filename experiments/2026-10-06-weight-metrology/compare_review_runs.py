"""Compare completed v3/v4 runs, isolating the documented book-list repair."""
import argparse
import json
from parse_catalogue import ROOT, RAW, RUN, sha, write_json

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/review-response-reproduction.json');args=ap.parse_args()
    output=ROOT/args.output
    if output.exists():raise FileExistsError(output)
    old=RUN/'runs/2026-10-07-review-response-v3';new=RUN/'runs/2026-10-07-review-response-v4'
    excluded={'manifest.json','completion.json','parser-audit.json','dholavira-model-tests.json'}
    identical=[]
    for p in new.rglob('*'):
        if not p.is_file() or p.name in excluded:continue
        name=p.relative_to(new).as_posix();assert p.read_bytes()==(old/name).read_bytes(),name;identical.append(name)
    before=json.loads((old/'dholavira-model-tests.json').read_text());after=json.loads((new/'dholavira-model-tests.json').read_text())
    beforebook=before.pop('book_heavier_list');afterbook=after.pop('book_heavier_list');assert before==after
    rawold=RAW/'2026-10-07-review-response-v3';rawnew=RAW/'2026-10-07-review-response-v4';rawidentical=[]
    for p in rawnew.iterdir():
        if p.name=='ascalone-dholavira-heavier-list.json':continue
        assert p.read_bytes()==(rawold/p.name).read_bytes(),p.name;rawidentical.append(p.name)
    write_json(output,{'status':'Verified computation','run_status':'Exploratory','old_run_status':'Superseded',
              'byte_identical_owned_files_n':len(identical),'byte_identical_owned_files':identical,
              'byte_identical_local_derivatives_n':len(rawidentical),'byte_identical_local_derivatives':rawidentical,
              'model_tests_equal_except_book_list_aggregate':True,'book_list_before':beforebook,'book_list_after':afterbook,
              'metadata_differences':'Protocol/code hashes, raw output paths and elapsed time differ as declared; metadata are excluded from byte comparison.'})
    print(output.read_text())

if __name__=='__main__':main()
