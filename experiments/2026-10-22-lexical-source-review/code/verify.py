"""Verify source bindings and audit arithmetic without rerunning a reading."""
import argparse
from collections import Counter
import io
import json
from pathlib import Path
import unittest

from prepare import ROOT, PKG, OUT, read, sha


def jsonl(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists(): parser.error("output exists; choose a new path")
    stream=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(PKG / "code"),pattern="test_source_review.py")
    tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    records=jsonl(OUT / "compound-review.jsonl")
    accepted=[r for r in records if r["in_frozen_sample"] and len(r["parser_members"])==2]
    counts=Counter(r["review_decision"] for r in accepted)
    expected=read(PKG / "results-v1.json")
    agreement=expected["source_boundary_agreement"]
    arithmetic=(dict(counts)==expected["accepted_split_decisions"] and
                agreement["adjudicable_denominator"]==counts["supported_split"]+counts["incorrect_split"] and
                agreement["adjudicable_numerator"]==counts["supported_split"] and
                agreement["lower_bound"]==counts["supported_split"]/len(accepted) and
                agreement["upper_bound"]==(counts["supported_split"]+counts["undecidable"])/len(accepted))
    bench=read(PKG / "shots-synthetic-v1.json")
    checks={"focused_source_tests":tests.wasSuccessful(),"independent_review_arithmetic":arithmetic,
            "synthetic_access_guards":bench["pass"] and bench["synthetic"],
            "no_effect_rerun":expected["rebus_effect_recomputed"] is False}
    value={"schema_version":"1.0","task":"lexical-source-review/verification","pass":all(checks.values()),
           "checks":checks,"tests_run":tests.testsRun,"test_output":stream.getvalue(),
           "verification_tier":"submitted","scope":"Author verification of source integrity, bindings and arithmetic; no independent linguistic adjudication",
           "new_real_confirmation_access":False,
           "code_sha256":{p.relative_to(ROOT).as_posix():sha(p) for p in sorted((PKG / "code").glob("*.py"))},
           "local_guard_output_sha256":sha(OUT / "source-guard-review.json")}
    with args.out.open("x",encoding="utf-8") as output:
        json.dump(value,output,indent=2);output.write("\n")
    print(json.dumps({"pass":value["pass"],"tests_run":tests.testsRun,"checks":checks}))
    return 0 if value["pass"] else 1


if __name__=="__main__":
    raise SystemExit(main())
