"""Check final artifacts, hashes, syntax, links and JSON without writing elsewhere."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from bench.common import RUN, read_json, sha256, write_json


def captured_json(path):
    # PowerShell captures stdout as UTF-16; json.loads(bytes) detects its BOM.
    return json.loads(Path(path).read_bytes())


def main():
    errors, code, json_files, links = [], 0, 0, 0
    for base in (ROOT / "bench", RUN):
        for path in base.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix == ".py":
                compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
                code += 1
            if path.suffix == ".json":
                captured_json(path)
                json_files += 1
            if path.suffix == ".md" and path.name != "CODEX-PROMPT.md":
                body = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8-sig"), flags=re.S)
                for target in re.findall(r"\]\(([^)]+)\)", body):
                    if "://" in target or target.startswith("#"):
                        continue
                    target = target.split("#")[0]
                    if target and not (path.parent / target).exists():
                        errors.append({"path": str(path.relative_to(ROOT)), "missing_link": target})
                    links += 1
    final = read_json(RUN / "selftest-final.json")
    comparisons = read_json(RUN / "reproduction-final/comparisons.json")
    interfaces = read_json(RUN / "interfaces-v1.json")
    for obj in (final, interfaces, *[read_json(p) for p in (RUN / "reproduction-final").glob("*.json")]):
        if obj["schema_version"] != "1.0" or not isinstance(obj["synthetic"], bool):
            errors.append({"schema": "bad envelope"})
        for item in obj["provenance"]:
            if item["path"].startswith("bench/") and sha256(ROOT / item["path"]) != item["sha256"]:
                errors.append({"changed_benchmark_code": item["path"]})
    if not final["pass"] or not interfaces["pass"] or not comparisons["all_match"]:
        errors.append({"failed_result": True})
    for file in (RUN / "prose-bench-final.json", RUN / "prose-experiment-final.json"):
        if captured_json(file)["flags"]:
            errors.append({"prose_flags": str(file)})
    result = {"schema_version": "1.0", "python_files_compiled": code, "json_files_parsed": json_files,
              "local_links_checked": links, "final_code_hashes_match": not any("changed_benchmark_code" in e for e in errors),
              "selftest_pass": final["pass"], "interface_cases": len(interfaces["cases"]),
              "source_comparisons": len(comparisons["comparisons"]), "errors": errors, "pass": not errors,
              "knowledge_map_status": "One generated-map drift error; coordinator rebuild required"}
    name = sys.argv[1] if len(sys.argv) > 1 else "verification-final.json"
    write_json(RUN / name, result)
    print(result)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
