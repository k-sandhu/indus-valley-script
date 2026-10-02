"""Render the completed synthetic calibration endpoints for manuscript reuse."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
PARENT = HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(output):
    inputs = {"original_results": PARENT / "main/results.json", "original_audit": PARENT / "verification_main.json",
              "face_results": PARENT / "noisy-faces/main/results.json", "face_audit": PARENT / "noisy-faces/verification_main.json"}
    loaded = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in inputs.items()}
    assert loaded["original_results"]["status"] == loaded["face_results"]["status"] == "complete"
    assert loaded["original_audit"]["passed"] and loaded["face_audit"]["status"] == "pass"
    assert not loaded["original_audit"]["quick"] and not loaded["original_audit"]["prefix"]
    aggregates = {**loaded["original_results"]["aggregate"], **loaded["face_results"]["aggregate"]}
    panels = [
        ("Independent records", [("independent_records/record_columns", "Record columns", "#AD5C27", "o"),
                                  ("unique_records/unique_record_columns", "Unique conditioned", "#695090", "s")]),
        ("Two identical faces", [("physical_copies/record_columns", "Record columns", "#AD5C27", "o"),
                                  ("physical_copies/block_columns", "Object columns", "#16757A", "s")]),
        ("Correlated, differing faces", [("noisy_faces/record_columns", "Record columns", "#AD5C27", "o"),
                                           ("noisy_faces/face_vectors", "Face vectors", "#16757A", "s")])]
    points = []
    for panel, series in panels:
        for key, label, _, _ in series:
            for alpha, endpoint in aggregates[key]["rejections"].items():
                lower, upper = endpoint["wilson_95_ci"]
                points.append({"panel": panel, "series": label, "case": key, "threshold": float(alpha),
                               "datasets": aggregates[key]["datasets"], "count": endpoint["count"],
                               "rate": endpoint["rate"], "lower": lower, "upper": upper})
    assert all(point["datasets"] == 1000 for point in points)
    if output.exists():
        raise FileExistsError("Refusing an existing figure endpoint")
    output.mkdir(parents=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.fonttype": "none", "pdf.fonttype": 42})
    figure, axes = plt.subplots(1, 3, figsize=(11.8, 4.25), sharey=True)
    ymax = max(15, 5 * math.ceil(100 * max(point["upper"] for point in points) / 5))
    for axis, (panel, series) in zip(axes, panels):
        axis.plot([0, 11], [0, 11], color="#6A6A6A", linestyle="--", linewidth=1, label="Nominal threshold")
        for index, (key, label, color, marker) in enumerate(series):
            selected = sorted([point for point in points if point["case"] == key], key=lambda point: point["threshold"])
            x = [100 * point["threshold"] + (-.15 if index == 0 else .15) for point in selected]
            y = [100 * point["rate"] for point in selected]
            error = [[100 * (point["rate"] - point["lower"]) for point in selected],
                     [100 * (point["upper"] - point["rate"]) for point in selected]]
            axis.errorbar(x, y, yerr=error, color=color, marker=marker, linestyle="none", markersize=5,
                          elinewidth=1.2, capsize=3, label=label)
        axis.set(title=panel, xlabel="Nominal threshold (%)", xlim=(0, 11), ylim=(0, ymax), xticks=[1, 5, 10])
        axis.grid(axis="y", color="#E2E2E2", linewidth=.7)
        axis.set_axisbelow(True)
        axis.legend(loc="upper left", fontsize=8.5, frameon=False, handlelength=1.6)
    axes[0].set_ylabel("Rejections under the generating law (%)")
    figure.suptitle("Conditional-reference calibration on synthetic populations", fontsize=13)
    figure.text(.5, .025, "1,000 generated populations per case; 99 reference draws per population; bars show 95% Wilson intervals.",
                ha="center", fontsize=9)
    figure.tight_layout(rect=(0, .06, 1, .92))
    for extension in ["png", "svg", "pdf"]:
        figure.savefig(output / f"calibration.{extension}", dpi=220, facecolor="white")
    plt.close(figure)
    with (output / "points.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(points[0]))
        writer.writeheader()
        writer.writerows(points)
    metadata = {"input_sha256": {name: digest(path) for name, path in inputs.items()}, "source_sha256": digest(Path(__file__)),
                "matplotlib_version": matplotlib.__version__, "points": len(points),
                "format": ["png", "svg", "pdf"], "y_axis_limits_percent": [0, ymax]}
    (output / "figure.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "main")
    args = parser.parse_args()
    main(args.output)
