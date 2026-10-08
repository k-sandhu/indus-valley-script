"""Preserve the reviewed 0.3.0 witnesses and record the 0.3.1 plan."""
from datetime import datetime, timezone
import shutil
from build_release import HERE, RAW, dump, sha

def main():
    dest=HERE/'history/2026-10-08-v0.3.0-code'
    if dest.exists(): raise FileExistsError(dest)
    dest.mkdir(parents=True)
    for p in HERE.iterdir():
        if p.is_file() and (p.suffix=='.py' or p.name in ['PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','registry-entry.json','sources.json','rights-audit.json','RELEASE-CHECKLIST.md']):
            shutil.copyfile(p,dest/p.name)
    baseline=HERE/'history/2026-10-08-release-v0.3.0'
    shutil.copytree(HERE/'release',baseline)
    protected={p.relative_to(HERE).as_posix():sha(p) for folder in ['review','review-0.3.0'] for p in (HERE/folder).rglob('*') if p.is_file()}
    protected.update({p.name:sha(p) for p in [HERE/'REVIEW.md',HERE/'REVIEW-0.3.0.md']})
    now=datetime.now(timezone.utc).isoformat()
    dump(HERE/'preservation-plan-2026-10-08-v031.json',dict(recorded_utc=now,reviewer_hashes=protected,release_0_3_0={p.relative_to(baseline).as_posix():sha(p) for p in baseline.rglob('*') if p.is_file()},existing_owned_files=[p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()],existing_raw_files=[p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file()]))
    protocol=HERE/'PROTOCOL.md'
    with protocol.open('a',encoding='utf8') as f:
        f.write(f'''\n\n### Version 0.3.1 amendment: 8 October 2026\n\nPlan recorded at {now}, before modifying the 0.3.1 builder or computing its checks. Read REVIEW-0.3.0.md in full and preserve the reviewed release, current code and owner records in history/. The review verifies private Hub revision 541766d5ea8a4c3b3ec5fcc416ee764af8763afb against the 0.3.0 folder. This revision performs no Hub action. The earlier 0.3.0 amendment combines planned work and post-build repairs; its heading alone does not establish that the plan preceded the first build. Its two paragraphs beginning “The first build attempts” and “Final prose inspection” record repairs retrospectively on 8 October. Their original wording is preserved in the code-history snapshot; no earlier timestamp is inferred.\n\nUse printed_inscription_id and classification_literal as the public prediction keys, accept inscription_number and classification_code as frozen-format aliases, require both values to be present (null allowed), and reject conflicting aliases. Build minimal files using only the card's documented fields and frozen values. Compare their full summaries, row records and bootstrap intervals with the frozen baseline; required number/classification counts are 23/19 of 60, 62/55 of 80 and 71/72 of 80. Test missing fields and valid aliases.\n\nPopulate independent reading candidate_fields_would_change by joining each candidate to its old chart-cell membership and its field-specific location, following the chart audit's mapping rule. Keep corrected_cell as the union of chart_locations, chart_references and shape_only_chart_locations. Document and measure why that union produces 20 v2 reader B corrected-cell units and seven class-metadata units, against the audit's strict-location counts 12 and six. Compare the 26 definite independent-reading changes with the audit and derive v3 changes by the same rule. Flags are Exploratory annotations; all frozen payloads and scores remain unchanged.\n\nRemove the CFF alternative-licence list, retaining per-component terms in LICENSE and the citation message. Describe earlier readers as Claude Sonnet and v3 readers as Claude Sonnet 5.5. Apply the review's comprehension improvements: frame table, distinct component descriptions, defined census/process terms, public chart expert-review priorities and public provenance pointers. Update stale preview statements and preserve all earlier validation files.\n\nBuild into fresh owned folders. Load every configuration, compare parent values/images and all three frozen metrics, test the public prediction format, validate CFF, rerun applicable reviewer scripts with redirected outputs and local substitutes for Hub calls, inspect rights/prose/privacy matches, and compare a second fresh build byte for byte. Hash reviewer files before and after. A negative result is an unexplained score, source, flag, image or rebuild mismatch, a malformed prediction accepted silently, invalid CFF, unexplained third-party text/sequence or private disclosure. The public viewer and new hosted revision remain coordinator checks after upload.\n''')
    dump(HERE/'protocol-plan-2026-10-08-v031.json',dict(recorded_utc=now,protocol_sha256=sha(protocol),build_not_started=True))
    print(now)

if __name__=='__main__':main()
