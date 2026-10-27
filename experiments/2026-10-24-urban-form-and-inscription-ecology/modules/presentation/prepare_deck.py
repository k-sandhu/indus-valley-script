"""Freeze the local deck's authored-data inputs and their provenance."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
ROOT = PACKAGE.parents[1]
LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/presentation")
RUN = sys.argv[1] if len(sys.argv) > 1 else "v1"
INPUTS = []


def read(relative, raw=False):
    path = ROOT / relative
    data = path.read_bytes()
    INPUTS.append(dict(logical_path=relative, physical_path=str(path.resolve()), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
    return data.decode("utf-8-sig") if raw else json.loads(data)


def module(name, file):
    return f"experiments/2026-10-24-urban-form-and-inscription-ecology/modules/{name}/{file}"


def main():
    prefix = "experiments/2026-10-24-urban-form-and-inscription-ecology/"
    summary = read(prefix + "run-v3/summary.json")
    validation = read(prefix + "run-v3/validation.json")
    assert validation["status"] == "pass"
    assert summary["observation_assertions"] == 287 and summary["towns"] == 12
    observations = []
    sources = []
    for name in ["western", "eastern", "inscriptions"]:
        o = read(module(name, "observations.json"))
        observations += o if isinstance(o, list) else o["observations"]
        s = read(module(name, "sources.json"))
        sources += s if isinstance(s, list) else s.get("sources", s.get("source_records", []))
    md = list(csv.DictReader(read(module("western", "mohenjo-daro-residential-series.csv"), raw=True).splitlines()))
    for row in md:
        for key in ["approximate_bce", "n", "median_area_m2", "gini", "mean_log_area", "log_standard_deviation"]:
            row[key] = float(row[key])
    context = read(module("inscriptions", "context-table-summary.json"))
    prior = read(module("inscriptions", "prior-results.json"))
    synthetic = read(prefix + "synthetic-v1/results.json")
    shape = read(prefix + "shape-comparison-v1/results.json")
    assert shape["passed"] and shape["derived_dimension_pairs"] == 6
    method_sources = read(prefix + "methods-sources-v1.json") + read(prefix + "methods-sources-supplement-v1.json")
    read(prefix + "METHODS.md", raw=True)
    read(prefix + "TEST-DESIGN.md", raw=True)
    read(prefix + "REPORT.md", raw=True)
    cards = []
    for cid in ["C-0017", "C-0018", "C-0019"]:
        paths = list((ROOT / "knowledge/conjectures").glob(cid + "*.md"))
        assert len(paths) == 1
        t = read(paths[0].relative_to(ROOT).as_posix(), raw=True)
        cards.append(dict(id=cid, title=re.search(r"^title: (.+)$", t, re.M)[1], credence=float(re.search(r"^credence: (.+)$", t, re.M)[1]), text=t))
    assert "Rao" in cards[2]["text"]
    # Complete source details remain in notes, while the slide carries a short locator.
    d = dict(summary=summary, observations=observations, sources=sources, md_series=md,
             context=context, prior=prior, synthetic=synthetic, shape=shape, cards=cards, method_sources=method_sources)
    target = LOCAL / "build" / f"evidence-{RUN}.json"
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = dict(run=RUN, inputs=INPUTS, evidence_path=str(target), evidence_sha256=hashlib.sha256(target.read_bytes()).hexdigest(), acquired_source_images_embedded=0)
    (HERE / f"input-manifest-{RUN}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(inputs=len(INPUTS), assertions=len(observations), local_evidence=str(target))))


if __name__ == "__main__":
    main()
