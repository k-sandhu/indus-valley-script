"""Write reports and maintain the owned-path/source manifest after manual checks."""
from __future__ import annotations
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
import numpy as np
import scipy
from bench.common import RUN, provenance, read_json, sha256

EXCLUDED = {"experiments/2026-10-13-bench/CODEX-PROMPT.md", "experiments/2026-10-13-bench/launch.sh"}


def number(value):
    return str(value) if isinstance(value, int) else format(value, ".17g")


def make_reports():
    test = read_json(RUN / "selftest-final.json")
    comparisons = read_json(RUN / "reproduction-final/comparisons.json")
    interface = read_json(RUN / "interfaces-v1.json")
    key = test["tasks"]["key-calibration"]
    meaning = test["tasks"]["meaning-map"]
    lines = [
        "# Shared evaluation harness: results",
        "",
        "13 October 2026. Author: GPT-6.1-Sol, Codex API. This is a tooling and source-reproduction package. It adds five task commands under `bench/`, a versioned JSON envelope, source-pinned imports and a shared-round confirmation loader.",
        "",
        f"The final selftest passed all five tasks. All {len(comparisons['comparisons'])} local numerical comparisons matched their original endpoints, and all {len(interface['cases'])} interface checks passed. [Selftest](selftest-final.json), [comparisons](reproduction-final/comparisons.json), [interface cases](interfaces-v1.json).",
        "",
        "## Generated controls",
        "",
        f"The known synthetic key stood {key['correct']['rearrangements']['distance_sd']:.2f} SD above its within-band rearrangements and passed the overall, order-only and grouped-half checks. The scrambled and random keys failed, as did the reversed-transition rival model. This generated grammar differs from the original study's running-text law. The original power separations, recalculated from its preserved aggregate scores, were Sanskrit 27.38, Latin 33.17, Tamil 37.15 and Sumerian 72.47 SD.",
        "",
        f"The planted large meaning-map effect passed. Under no effect, {meaning['power'][0]['success']} of {meaning['power'][0]['total']} trials passed, a rate of {meaning['power'][0]['rate']:.2f} against the nominal 0.05. The selftest retains a Wilson interval and the predeclared binomial tolerance. Its normal-law power rates are recorded for effects 0, 0.25, 0.5 and 1.5 response-noise SD. Additional design-shaped and categorical planting checks preserve shared object responses in [the interface output](interfaces-v1.json).",
        "",
        "The loader checks passed for alias/text closure, the short-tablet exception, disjoint components, a whole-round freeze, changed predictions, site-proxy stripping, spending and a second seed's attempted reuse. Restoration and segmentation hand cases matched their stated arithmetic. Input checks reject invalid rankings/probabilities, mismatched queries and incomplete boundary coverage, and preserve existing output bytes.",
        "",
        "## Local source comparisons",
        "",
        "The table gives every reproduced number and its original witness. Score comparisons use absolute tolerance 1e-12; count comparisons require equality. The largest score difference is floating-point summation order. Imported source paths and hashes accompany the task outputs.",
        "",
        "| Measurement | Original | Bench | Original witness |",
        "|---|---:|---:|---|",
    ]
    for c in comparisons["comparisons"]:
        lines.append(f"| {c['name']} | {number(c['original'])} | {number(c['recomputed'])} | [source](../../{c['source']}) |")
    lines += [
        "",
        "The key comparison rescores the published assignment under its preserved dense model. Shot B recomputes its frozen measures and feeds them to the common rearrangement engine, including the original 10,000-draw seed. Restoration rescores saved masked predictions and the original JSON parents of all three visual-row/page releases. Segmentation rebuilds the four readable cohorts and reruns branching entropy, greedy n-grams and both trivial baselines. These are source reproductions, with no retraining of the historical restoration models.",
        "",
        "## Population and preserved scope",
        "",
        "The new October 13 seed gives 2,341 discovery and 2,354 confirmation families in 4,104 components. [Manifest](round-1.json) and [aggregate summary](round-1-summary.json). It inherits seal-size, site and motif exposures from the October 12 input. No confirmation statistic was read through this new round. Its real-population freshness requires source and object-identity review.",
        "",
        "The currently held line-break list contains the corrected 69 faces and 73 required divisions. The re-score finds branching-entropy hits 26/73 and 41/73 under the two line orders, and greedy hits 70/73 and 64/73. [Current re-score](reproduction-final/segmentation-lines.json). The earlier reviewed endpoint used 72 faces and 76 divisions. Its 29/76 and 44/76 branching figures remain in the original report. This source-population change is preserved explicitly; the current results are not presented as a reproduction of those older division counts. Precision/F1 remain null for these positive-only labels.",
        "",
        "The full 2,000-sweep DP rehearsal and the original multilingual blind-annealing power study were not rerun. The task can invoke the original DP scorer; the required segmentation source number is reproduced by the fast methods. The four original key-power distances are aggregate arithmetic reproductions, while the new key controls use independently generated plaintext and the same current scorer as real inputs. Joint planting of multiple predictions on one variable requires a separately declared generative law; the generic power command rejects that case rather than silently overwriting responses.",
        "",
        "All scientific outputs here are aggregates or generated controls. Acquired texts, full real sign sequences and source images were read in place and not copied into either owned directory. Earlier implementation endpoints remain in `selftest-v1.json`, `selftest-v2.json`, `reproduction-v1/` and `reproduction-v2/`. [Changed paths and sources](CHANGES.json), [complete created-path inventory](PATHS.json).",
        "",
        "## Commands and coordinator checks",
        "",
        "```text",
        "python -m bench selftest --directory experiments/2026-10-13-bench/selftest-shot-fixtures-final --out experiments/2026-10-13-bench/selftest-final.json",
        "python -B experiments/2026-10-13-bench/reproduce.py reproduction-final",
        "python -B experiments/2026-10-13-bench/check_interfaces.py interfaces-v1.json",
        "python tools/review_prose.py --path bench --no-write",
        "python tools/review_prose.py --path experiments/2026-10-13-bench --no-write",
        "```",
        "",
        "These endpoints now exist; choose new names when rerunning. The coordinator should repeat the synthetic controls and source comparisons, inspect closure and read logs, review population freshness and the partial line labels, and integrate the proposed shared text in [INTEGRATION.md](INTEGRATION.md). This author-performed reproduction does not supply an independent verification tier. The coordinator's prompt, launcher and other contributors' packages are unchanged. No network call, CI workflow or Git mutation was made.",
        "",
        "The strongest supported claim is that the shared scorers distinguish a known generated encoding from its scrambled controls while preserving the project's recorded scores. The deciding next check is an independent contributor's rerun, followed by a frozen prediction on newly reviewed object evidence.",
    ]
    report = RUN / "REPORT.md"
    if not report.exists():
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    retro = RUN / "RETROSPECTIVE.md"
    if not retro.exists():
        retro.write_text("""# Shared harness retrospective

13 October 2026. Author: GPT-6.1-Sol, Codex API. This record describes the observable approach, repairs and outcome.

The package began by reading repository rules, source rights, the calibration memo, shot design and review, Paper 001 methods, release scorers and segmentation procedures. Knowledge searches identified the earlier failed readability and reference-calibration paths. `PLAN.md` preceded implementation, and edits stayed in the two owned directories. The coordinating session's prompt and launcher were left unchanged.

Source methods were imported through isolated module names, with temporary aliases for legacy imports named `common` or `shots_common`. The imports suppress bytecode writes to source packages and reject a source change within a running process. Release scoring originally depended on Parquet wrappers; reading the preserved JSON parents and importing the core row/page functions removed that dependency while preserving scores.

The first synthetic run passed all five tasks. A first local replay matched 47 numbers. The wrapper was then extended to source-page recall, giving 50 comparisons. Later checks added transitive closure for generic key inputs, emitted-value counts, a paired restoration comparison, five discovery re-splits, shared-response power planting, categorical planting, site availability for frozen confirmation scoring, and refusal to reuse spent statistics under a second seed. Each changed code version received a new output endpoint; earlier successful runs were preserved.

The line-break source needed a population check. Its local face list now has the corrected 69 faces, while the earlier review described 72. The current 73-division re-score is recorded separately. Catalogue divisions establish required boundaries, so the scorer reports recall and leaves precision/F1 null for these partial labels. Complete readable-script references retain the original boundary and exact-word scoring.

The final selftest passes all five tasks, the 17 interface checks pass, and all 50 numerical source comparisons match. The new October 13 split preserves 4,104 components and records 2,341/2,354 families. Its seal-size, site and motif families inherit prior exposure. No new confirmation test was conducted on that split. The reports disclose omitted expensive replays and the need for an explicit joint planting law when several predictions share one response variable.

Only generated controls, source hashes, workflow records and aggregates were created. No acquired corpus payload, publication, recurring automation or Git mutation was introduced. Prose scans and a path/source inventory accompany the package; exact shared-document additions and registry/manifest proposals await coordinator integration.

The harness carries the existing numerical record into a common interface and catches procedural reuse and malformed inputs. Its next deciding test is independent reproduction of these endpoints and a frozen run on a population whose object identity and prior use have been reviewed.
""", encoding="utf-8")


def inventory():
    files = sorted(p for base in (ROOT / "bench", RUN) for p in base.rglob("*") if p.is_file()
                   and p.relative_to(ROOT).as_posix() not in EXCLUDED and "__pycache__" not in p.parts)
    paths = [p.relative_to(ROOT).as_posix() for p in files]
    for required in ("experiments/2026-10-13-bench/PATHS.json", "experiments/2026-10-13-bench/CHANGES.json"):
        if required not in paths:
            paths.append(required)
    paths.sort()
    (RUN / "PATHS.json").write_text(json.dumps({"schema_version": "1.0", "created_paths": paths,
                                                "excluded_coordinator_inputs": sorted(EXCLUDED)}, indent=2) + "\n", encoding="utf-8")
    reused = [
        ("experiments/2026-10-12-published-claim-tests/sanskrit-key/common.py", "imported Kneser-Ney, frequency strata and local key/corpus loading"),
        ("experiments/2026-10-12-published-claim-tests/sanskrit-key/stage3_fit.py", "adapted greedy option scoring and order-gain definition"),
        ("experiments/2026-10-12-published-claim-tests/sanskrit-key/stage5_power.py", "synthetic design reference; no acquired plaintext copied"),
        ("experiments/2026-10-12-conjecture-shots/shots_common.py", "imported closure and deterministic assignment rules"),
        ("experiments/2026-10-12-conjecture-shots/shot-b-reading/confirm.py", "generalized label rearrangements; imported frozen measures for replay"),
        ("experiments/2026-10-08-hf-public-release/release/code/score_core.py", "imported candidate alignment, visual-row aggregation, Wilson and calibration"),
        ("experiments/2026-10-08-hf-public-release/release/code/score_benchmark.py", "adapted input validation and frozen invalid-target/pipeline criteria"),
        ("experiments/2026-10-08-hf-public-release/release/code/score_recall.py", "imported page recall and aggregation"),
        ("experiments/2026-10-08-hf-public-release/release/code/score_recall_v3.py", "imported physical/numbered line recall"),
        ("experiments/2026-10-12-structure-first/segmenters.py", "imported all three segmenters and complete-boundary scoring"),
        ("experiments/2026-10-12-structure-first/common.py", "imported source loaders and distinct-text population"),
        ("experiments/2026-10-12-structure-first/step5-rehearsal/rehearse_segmentation.py", "imported gold boundaries and original matched sampling"),
        ("experiments/2026-10-12-structure-first/step3-segmentation/linebreaks.py", "imported line parser"),
        ("experiments/2026-10-12-structure-first/review/review_step3_segmenter_breaks.py", "adapted two-order segmenter agreement procedure"),
    ]
    changes = read_json(RUN / "CHANGES.json")
    changes.update(phase="verification complete; coordinator review pending", created=paths,
                   environment={"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                   reused_sources=[dict(path=p, sha256=sha256(ROOT / p), reuse=how) for p, how in reused],
                   file_hashes={p.relative_to(ROOT).as_posix(): sha256(p) for p in files
                                if p.name not in ("CHANGES.json", "PATHS.json")},
                   commands=["python tools/kb.py search calibration", "python tools/kb.py search segmentation",
                             "python -m bench selftest --directory experiments/2026-10-13-bench/selftest-shot-fixtures-final --out experiments/2026-10-13-bench/selftest-final.json",
                             "python -B experiments/2026-10-13-bench/reproduce.py reproduction-final",
                             "python -B experiments/2026-10-13-bench/check_interfaces.py interfaces-v1.json",
                             "python -m bench shots --action create --split experiments/2026-10-13-bench/round-1.json --out experiments/2026-10-13-bench/round-1-summary.json",
                             "python tools/review_prose.py --path bench --no-write",
                             "python tools/review_prose.py --path experiments/2026-10-13-bench --no-write"],
                   unchanged_coordinator_inputs={p: sha256(ROOT / p) for p in EXCLUDED if (ROOT / p).exists()},
                   coverage_change={"acquired_sources": 0, "new_objects": 0, "new_object_metadata": 0},
                   outcomes={"selftest": True, "interface_cases": 17, "local_comparisons": 50, "all_local_comparisons_match": True,
                             "package_verification": "experiments/2026-10-13-bench/verification-final-v3.json",
                             "prose_flags": 0, "knowledge_check": {"pass": False, "errors": ["knowledge/MAP.md differs from a fresh build"],
                                                                 "remedy": "Coordinator rebuild after integration"}})
    (RUN / "CHANGES.json").write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")
    manifest = read_json(RUN / "manifest-entry.json")
    manifest["hashes"] = {"bench/README.md": sha256(ROOT / "bench/README.md"),
                          "bench/schema.json": sha256(ROOT / "bench/schema.json")}
    (RUN / "manifest-entry.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Recompute this evolving file's digest after its coordinator proposal is refreshed.
    changes["file_hashes"]["experiments/2026-10-13-bench/manifest-entry.json"] = sha256(RUN / "manifest-entry.json")
    (RUN / "CHANGES.json").write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"created_paths": len(paths), "sources_hashed": len(reused), "environment": changes["environment"]}))


if __name__ == "__main__":
    make_reports()
    inventory()
