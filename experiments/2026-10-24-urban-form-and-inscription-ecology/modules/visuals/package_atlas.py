"""Package the reviewed scientific figures locally, without source reproductions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf8")


def main():
    run = "run-v7"
    manifest_path = HERE / f"manifest-{run}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf8"))
    validation = json.loads((HERE / f"validation-{run}.json").read_text(encoding="utf8"))
    assert validation["status"] == "pass"
    out = Path(manifest["output_root"])
    notes = {
        1:"All twelve numbered points and displaced callout connectors are readable; accuracy qualification remains visible.",
        2:"Display labels follow named domain keys. Legend defines index statuses; completeness qualifier remains visible.",
        3:"All twelve totals and module colours are readable; 287 core links remain separate from the external comparison.",
        4:"Each material is tied to a component and phase; no percentage bar or material-volume inference is drawn.",
        5:"All suffixes, column labels and the unselected-cell key are readable; classification remains a selected reference index.",
        6:"All seven approximate intervals and both source-model gaps are readable; no continuous duration is asserted.",
        7:"IA, IB, IC and II appear in source order, with retained and changed elements explained below.",
        8:"Both illustrative panels, the infill arrow, reported exposure dimensions and timing qualification are readable.",
        9:"Three distinct named locations and reported dimensions are readable; unscaled drawing and absent common north are explicit.",
        10:"Gini values, median areas and residence-sample counts are readable; recurring samples and model dates are qualified.",
        11:"All eight quantities preserve original units and scope. The well count is explicitly an extrapolated estimate.",
        12:"Five displayed stage groups sum to 225; the eight qualified/unknown categories total 63 and remain listed.",
        13:"Five displayed inscription groups sum to 225; six qualified flags are listed. Explicit Yes is distinguished from readable text.",
        14:"The matrix preserves all nine source cells and the 16/2/4 recovery totals. Hand attribution and secondary deposition remain visible.",
        15:"The 65, 69-of-90 and 93 scopes remain separate; the 12-member die group is qualified below.",
        16:"All four object-life rows and the arrows are readable; manufacture, operation and recovery remain distinct columns.",
        17:"All six prior-result cards are readable; support, failures, uncertainty and lack of new confirmation remain visible.",
        18:"Synthetic label, generated offset axis, Q4 formula and local-versus-pooled curves are readable; no ancient plan is pictured.",
        19:"All four independent-pair curves and the 80 percent reference are readable; optimistic assumptions remain visible.",
        20:"Three selected institutional models and their predictions are readable; the integrated test supplies the fuller competing model set.",
        21:"Six numbered stages and the return arrow from step 3 to step 4 are readable; no confirmation cohort was accessed.",
        22:"All four bounded source chains retain their identity, time and missing-operation relation in separate columns.",
        23:"All six ratios align with their published dimension pairs; uncertainty and the architectural-part denominator remain visible."
    }
    review = {"run":run, "status":"pass", "review_type":"Contributing agent's visual review, not independent peer verification", "reviewer":"GPT-6 family through Codex collaboration; exact deployed model identifier unavailable in worker context", "method":"Rendered every figure to PNG and SVG. Viewed each of the 23 final PNGs individually through view_image, then both contact sheets. Reviewed data labels, figure text, source scope, layout and units. SVG syntax and hashes were checked by verify_atlas.py.", "manifest_sha256":sha(manifest_path), "figures":[{"figure":f["figure"], "id":f["id"], "status":"pass", "png_sha256":next(a["sha256"] for a in f["assets"] if a["format"]=="png"), "review":notes[f["figure"]]} for f in manifest["figures"]], "contact_sheets":[{"path":str(out / n),"sha256":sha(out / n),"viewed":True} for n in ["contact-sheet-all.jpg","selected-cover-contact.jpg"]], "remaining_scope":"Index and selected examples have unassessed archaeological completeness. Conceptual geometry is illustrative; synthetic calculations are planning demonstrations. Source interpretations and phase models require the qualifications preserved in the research register."}
    review_path = HERE / f"visual-review-{run}.json"
    write(review_path, review)
    captions = ["# Figure captions and source locators", "", "Accepted graphic run: run-v7. Archaeological register: run-v3. The manifest retains data values and hashes.", ""]
    for figure in manifest["figures"]:
        captions += [f"## Figure {figure['figure']:02d}. {figure['title']}", "", figure["caption"], "", f"Type: {figure['kind']}.", ""]
        if figure["observation_ids"]:
            captions += ["Assertions: " + ", ".join(figure["observation_ids"]) + ".", ""]
        for source in figure["sources"]:
            title = f"[{source['title']}]({source['url']})" if source.get("url") else source["title"]
            locations = "; ".join(source.get("locators", [source.get("locator", "")]))
            captions += [f"- {source['source_id']}: {title}. {locations}"]
        captions += [""]
    captions_path = HERE / f"captions-{run}.md"
    captions_path.write_text("\n".join(captions)+"\n", encoding="utf8")
    archive_path = out / "urban-form-visual-atlas-run-v7.zip"
    assert not archive_path.exists(), "Preserve an existing release archive."
    payload = [(Path(a["physical_path"]), Path(a["physical_path"]).name) for f in manifest["figures"] for a in f["assets"]]
    payload += [(out / n, n) for n in ["contact-sheet-all.jpg","selected-cover-contact.jpg"]]
    payload += [(HERE / n, n) for n in ["README.md","PROTOCOL.md","RETROSPECTIVE.md","DATA-UPDATE.md",manifest_path.name,f"validation-{run}.json",review_path.name,captions_path.name,"build_atlas.py","verify_atlas.py"]]
    with zipfile.ZipFile(archive_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path, name in payload:
            archive.write(path, name)
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None and len(archive.namelist()) == len(payload)
    release = {"run":run, "status":"pass", "archive_physical_path":str(archive_path), "archive_logical_path":"data/raw/2026-10-24-urban-form-and-inscription-ecology/visuals/run-v7/"+archive_path.name, "bytes":archive_path.stat().st_size,"sha256":sha(archive_path),"entries":len(payload),"contents":[{"archive_name":name,"sha256":sha(path),"bytes":path.stat().st_size} for path,name in payload],"local_only":True,"source_photographs_or_plans":0}
    write(HERE / f"release-{run}.json",release)
    write(HERE / "changed-paths.json",{"owned_module":str(HERE),"repository_files":[str(p) for p in sorted(HERE.iterdir()) if p.is_file()],"owned_local_raw_root":str(out.parent),"accepted_run":str(out),"shared_files_modified":[]})
    print(json.dumps({k:release[k] for k in ["status","archive_physical_path","bytes","entries","sha256"]}))


if __name__ == "__main__":
    main()
