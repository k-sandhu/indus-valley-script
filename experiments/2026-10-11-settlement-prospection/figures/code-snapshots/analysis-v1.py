"""Recompute the declared settlement-review aggregates and original figures.

The two local registers select places associated with inscription evidence.
Published survey counts have their own populations. Synthetic yield examples
illustrate sensitivity to assumptions and are not archaeological forecasts.

Usage (from the repository root):
    python experiments/2026-10-11-settlement-prospection/analysis.py \
        --output experiments/2026-10-11-settlement-prospection/run-v1 \
        --figures experiments/2026-10-11-settlement-prospection/figures

Both output directories must be new. The script never replaces a run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
CENSUS_INPUT = REPOSITORY / "experiments/2026-10-08-site-map-and-overview/data/sites-census.json"
DATING_INPUT = REPOSITORY / "experiments/2026-10-08-site-map-and-overview/data/dating-south-asia.json"
RAW = REPOSITORY / "data/raw/2026-10-11-settlement-prospection"
SOUTH_ASIAN_COUNTRIES = frozenset(("India", "Pakistan", "Afghanistan"))

# Our transcription of Green et al. 2019, Table 1, PDF page 15.
# Each percentage refers to the number of tested map features in that cell.
GREEN_CELLS = (
    ("combined", 3, 2, "50"),
    ("combined", 2, 3, "33.33"),
    ("combined", 1, 0, None),
    ("form line", 3, 37, "54.05"),
    ("form line", 2, 116, "58.62"),
    ("form line", 1, 240, "25.83"),
    ("shaded", 3, 18, "5.56"),
    ("shaded", 2, 76, "15.79"),
    ("shaded", 1, 60, "13.33"),
    ("hachure", 3, 1, "0"),
    ("hachure", 2, 25, "40"),
    ("hachure", 1, 201, "7.96"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPOSITORY).as_posix()
    except ValueError:
        return str(path.resolve())


def evidence_file(path: Path, role: str) -> dict:
    return {"path": relative(path), "bytes": path.stat().st_size,
            "sha256": sha256(path), "role": role}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("CSV rows must not be empty")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def recover_positives(tested: int, percent: str | None) -> int:
    """Find an integer compatible with the table's two-decimal precision."""
    if not isinstance(tested, int) or isinstance(tested, bool) or tested < 0:
        raise ValueError("A tested-feature count must be a nonnegative integer")
    if tested == 0:
        if percent is not None:
            raise ValueError("A zero denominator has no defined percentage")
        return 0
    if percent is None:
        raise ValueError("A positive denominator requires a reported percentage")
    target = Decimal(percent).quantize(Decimal("0.01"))
    if not Decimal(0) <= target <= Decimal(100):
        raise ValueError("Percentage outside zero to 100")
    compatible = [
        count for count in range(tested + 1)
        if (Decimal(100) * Decimal(count) / Decimal(tested)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP) == target
    ]
    if len(compatible) != 1:
        raise ValueError(f"Expected one compatible integer; found {len(compatible)}")
    return compatible[0]


def finite_nonnegative(value: float, name: str) -> float:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def square_equivalent(area_ha: float, *, area_unit: str = "ha") -> float:
    if area_unit != "ha":
        raise ValueError("Area must be expressed in hectares")
    finite_nonnegative(area_ha, "Area")
    return math.sqrt(10_000 * area_ha)


def excavation_volume(area_ha: float, fraction: float, thickness_m: float,
                      *, area_unit: str = "ha", thickness_unit: str = "m") -> float:
    if area_unit != "ha" or thickness_unit != "m":
        raise ValueError("Use hectares for area and metres for thickness")
    for name, value in (("Area", area_ha), ("Fraction", fraction), ("Thickness", thickness_m)):
        finite_nonnegative(value, name)
    if fraction > 1:
        raise ValueError("Excavated area fraction exceeds one")
    return 10_000 * area_ha * fraction * thickness_m


def synthetic_fragments(volume_m3: float, density_per_m3: float, recovery: float) -> float:
    for name, value in (("Volume", volume_m3), ("Density", density_per_m3), ("Recovery", recovery)):
        finite_nonnegative(value, name)
    if recovery > 1:
        raise ValueError("Recovery fraction exceeds one")
    return volume_m3 * density_per_m3 * recovery


def repeat_detection(probability: float, visits: int) -> float:
    if not 0 <= probability <= 1 or not math.isfinite(probability):
        raise ValueError("Detection probability must lie between zero and one")
    if not isinstance(visits, int) or isinstance(visits, bool) or visits < 0:
        raise ValueError("Visit count must be a nonnegative integer")
    return 1 - (1 - probability) ** visits


def metadata(census: dict, dating: dict) -> tuple[dict, list[dict], list[dict]]:
    sites = census["sites"]
    dated = dating["sites"]
    coordinate_status = Counter(row["coord_status"] for row in sites)
    country_rows = []
    for country in sorted({row["country"] for row in sites}):
        subset = [row for row in sites if row["country"] == country]
        located = sum(row.get("lat") is not None and row.get("lon") is not None for row in subset)
        country_rows.append({"country": country, "entries": len(subset),
                             "accepted_coordinate_present": located,
                             "accepted_coordinate_absent": len(subset) - located})
    phase_basis = Counter(phase["basis"] for row in dated for phase in row["phases"])
    dated_country_rows = []
    for country in sorted({row["country"] for row in dated}):
        subset = [row for row in dated if row["country"] == country]
        dated_country_rows.append({
            "country": country, "site_entries": len(subset),
            "phase_entries": sum(len(row["phases"]) for row in subset),
            "radiocarbon_basis_phase_labels": sum(
                phase["basis"] == "radiocarbon" for row in subset for phase in row["phases"]),
            "site_entries_with_radiocarbon_basis_phase": sum(
                any(phase["basis"] == "radiocarbon" for phase in row["phases"]) for row in subset),
        })
    selected_south = [row for row in sites if row["country"] in SOUTH_ASIAN_COUNTRIES]
    result = {
        "population": "Selected local inscription-associated site entities and provenance labels",
        "coordinate_file": {
            "entries": len(sites),
            "accepted_coordinate_present": sum(row.get("lat") is not None and row.get("lon") is not None for row in sites),
            "coordinate_status_counts": dict(sorted(coordinate_status.items())),
            "first_fieldwork_year_present": sum(row.get("first_fieldwork_year") is not None for row in sites),
            "south_asian_entries": len(selected_south),
            "south_asian_accepted_coordinate_present": sum(
                row.get("lat") is not None and row.get("lon") is not None for row in selected_south),
            "country_counts": country_rows,
        },
        "dating_file": {
            "population": "A separate selected chronology register; no record-level join to the coordinate cohort",
            "site_entries": len(dated), "phase_entries": sum(phase_basis.values()),
            "phase_basis_counts": dict(sorted(phase_basis.items())),
            "site_entries_with_radiocarbon_basis_phase": sum(
                any(phase["basis"] == "radiocarbon" for phase in row["phases"]) for row in dated),
            "country_counts": dated_country_rows,
        },
        "interpretation": "These metadata counts describe the selected files. Phase labels are not independent laboratory dates. Neither file supplies a civilization-wide settlement denominator or evidence of archaeological absence.",
    }
    return result, country_rows, dated_country_rows


def green_table() -> tuple[dict, list[dict], list[dict], list[dict]]:
    cells = [{"map_symbol": symbol, "size_class": size, "tested_features": tested,
              "reported_percent": percent, "recovered_archaeological_positives": recover_positives(tested, percent)}
             for symbol, size, tested, percent in GREEN_CELLS]
    by_symbol = []
    for symbol in ("combined", "form line", "shaded", "hachure"):
        subset = [row for row in cells if row["map_symbol"] == symbol]
        tested = sum(row["tested_features"] for row in subset)
        positives = sum(row["recovered_archaeological_positives"] for row in subset)
        by_symbol.append({"map_symbol": symbol, "tested_features": tested,
                          "archaeological_positives": positives, "positive_percent": 100 * positives / tested})
    by_size = []
    for size in (1, 2, 3):
        subset = [row for row in cells if row["size_class"] == size]
        tested = sum(row["tested_features"] for row in subset)
        positives = sum(row["recovered_archaeological_positives"] for row in subset)
        by_size.append({"size_class": size, "tested_features": tested,
                        "archaeological_positives": positives, "positive_percent": 100 * positives / tested})
    tested = sum(row["tested_features"] for row in cells)
    positives = sum(row["recovered_archaeological_positives"] for row in cells)
    result = {
        "source_id": "GREEN2019", "doi": "10.3390/rs11182089", "locator": "Table 1, PDF page 15",
        "population": "779 selected historical-map features field-checked in northwest India during 2017-2018",
        "method": "Recover the unique integer that reproduces each reported percentage after rounding to two decimal places. A cell with zero tested features has zero positives and an undefined percentage.",
        "tested_features": tested, "archaeological_positives": positives,
        "positive_percent": 100 * positives / tested,
        "cells": cells, "by_map_symbol": by_symbol, "by_map_size_class": by_size,
        "interpretation": "Positives span archaeological periods. The selected sample cannot estimate a national or Indus-period detection probability. Map size classes are cartographic classes, not measured settlement areas.",
    }
    return result, cells, by_symbol, by_size


def published_arithmetic() -> dict:
    return {
        "historical_excavation_ratio": {
            "excavated": 96, "mature_harappan_sites": 1022, "percent": 100 * 96 / 1022,
            "source_id": "LUCKNOW_CHAPTER", "locator": "printed page 41 / PDF page 3, citing 2002 sources",
            "interpretation": "Historical site-count arithmetic; not a present excavation census and not an excavated-area fraction.",
        },
        "cholistan_remote_mounds": {
            "detected_clusters": 337, "linked_legacy_locations": 71, "unmatched_clusters": 337 - 71,
            "clusters_below_5_ha": 246, "below_5_ha_percent": 100 * 246 / 337,
            "source_id": "ORENGO2020", "doi": "10.1073/pnas.2005583117",
            "interpretation": "Unmatched remote clusters require field checking and dating. These are not 266 confirmed new Indus sites. Visible-mound areas do not measure every occupation deposit.",
        },
        "southern_punjab_cartographic_revision": {
            "automatically_selected_features": 638, "after_manual_review_features": 646,
            "net_feature_revision": 646 - 638,
            "source_id": "GARCIA2023", "doi": "10.1186/s40494-023-00985-6", "locator": "Table 1",
            "interpretation": "The net revision is eight mapped features. Reconciliation and field dates are needed before counting new archaeological sites.",
        },
        "ganweriwala_areas": [
            {"measure": "legacy site area", "area_ha": 81.5, "source_id": "GULZAR2018",
             "method": "Earlier site-area estimate discussed in Gulzar 2018"},
            {"measure": "December 2015 ground survey", "area_ha": 66.7, "source_id": "GULZAR2018",
             "method": "Total-station and surface-artifact site boundary; published 2018"},
            {"measure": "2020 visible-mound detection", "area_ha": 33.0, "source_id": "ORENGO2020",
             "method": "Remote delineation of visible mounded area"},
        ],
    }


def synthetic_scenarios() -> tuple[dict, list[dict], list[dict], list[dict]]:
    geometry = [{"area_ha": area, "square_equivalent_side_m": square_equivalent(area)}
                for area in (1.0, 5.0, 30.0, 66.7, 200.0)]
    area, fraction, thickness, recovery = 30.0, 0.01, 1.0, 0.8
    volume = excavation_volume(area, fraction, thickness)
    yields = [{"area_ha": area, "excavated_area_fraction": fraction,
               "deposit_thickness_m": thickness, "excavated_volume_m3": volume,
               "assumed_fragment_density_per_m3": density, "assumed_recovery_fraction": recovery,
               "synthetic_recovered_fragments": synthetic_fragments(volume, density, recovery)}
              for density in (5.0, 50.0, 500.0)]
    observation = [{"constructed_true_sites": sites, "constructed_overall_recording_probability": probability,
                    "expected_recorded_sites": sites * probability}
                   for sites, probability in ((200, 0.5), (1000, 0.1))]
    repeats = [{"constructed_per_visit_detection_probability": probability, "visits": visits,
                "constructed_at_least_once_detection_probability": repeat_detection(probability, visits)}
               for probability in (0.0, 0.1, 0.5) for visits in (1, 2, 3, 5, 10)]
    result = {
        "status": "SYNTHETIC: constructed sensitivity examples, not estimates of archaeological quantities",
        "square_equivalent_geometry": geometry,
        "geometry_definition": "The side length of a square with the stated area; it does not describe a site's actual shape, phase, or surviving extent.",
        "yield_formula": "recovered_fragments = 10000 * area_ha * excavated_area_fraction * deposit_thickness_m * density_per_m3 * recovery_fraction",
        "yield_scenarios": yields,
        "yield_assumptions": "All values are selected for illustration. No source-derived fragment-density calibration, rare-object rate, whole-site forecast or civilization-wide total is supplied.",
        "observation_nonidentifiability_examples": observation,
        "observation_statement": "Different true totals and overall recording probabilities give the same expected record count. Without restrictions on the recording process, an observed count does not identify the missing total.",
        "conditional_observation_chain": ["occupied places", "surviving deposits", "surveyed deposits",
                                            "method-detected deposits", "dated or attributed evidence", "published records"],
        "conditional_chain_formula": "P(record|occupied) = P(survives|occupied) * P(surveyed|survives,occupied) * P(detected|surveyed,survives,occupied) * P(dated|detected,surveyed,survives,occupied) * P(published|dated,detected,surveyed,survives,occupied)",
        "conditional_chain_assumption": "This is the chain rule for conditional probabilities; it does not require independent stages.",
        "repeat_detection": repeats,
        "repeat_formula": "P(detected at least once) = 1 - (1-p)^k",
        "repeat_assumptions": "The formula assumes a constant per-visit probability and independent visits. Shared seasonal visibility, prior survey choices and inaccessible or deeply buried deposits can violate it. A method with p=0 remains uninformative on repetition.",
    }
    return result, geometry, yields, repeats


def verification(meta: dict, green: dict, arithmetic: dict, scenarios: dict,
                 input_files: list[dict]) -> dict:
    checks: list[dict] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(name)

    def rejects(name: str, function, *args, **kwargs) -> None:
        try:
            function(*args, **kwargs)
        except (ValueError, TypeError):
            check(name, True, "The deliberately invalid input was rejected")
        else:
            check(name, False, "The invalid input was accepted")

    check("coordinate_status_partition", sum(meta["coordinate_file"]["coordinate_status_counts"].values()) == meta["coordinate_file"]["entries"],
          "Coordinate-status counts conserve the selected population")
    check("country_partition", sum(row["entries"] for row in meta["coordinate_file"]["country_counts"]) == meta["coordinate_file"]["entries"],
          "Country counts conserve the selected population")
    check("coordinate_presence_matches_accepted_statuses", meta["coordinate_file"]["accepted_coordinate_present"] ==
          sum(meta["coordinate_file"]["coordinate_status_counts"][key] for key in ("census-verified", "census-partial")),
          "Null-coordinate and accepted-status totals agree")
    check("dating_phase_partition", sum(meta["dating_file"]["phase_basis_counts"].values()) == meta["dating_file"]["phase_entries"],
          "Chronological basis counts conserve phase entries")
    check("two_cohorts_remain_distinct", meta["coordinate_file"]["south_asian_entries"] != meta["dating_file"]["site_entries"],
          "No positional or name-based join has merged the selected 85-entry and 86-entry cohorts")
    check("green_published_totals", (green["tested_features"], green["archaeological_positives"]) == (779, 199),
          "The recovered cells reproduce the table's total")
    for dimension in ("by_map_symbol", "by_map_size_class"):
        check(f"green_{dimension}_partition", sum(row["tested_features"] for row in green[dimension]) == 779
              and sum(row["archaeological_positives"] for row in green[dimension]) == 199,
              "Independent row and column aggregations reproduce the total")
    for cell in green["cells"]:
        count, tested = cell["recovered_archaeological_positives"], cell["tested_features"]
        check(f"green_rounding_{cell['map_symbol'].replace(' ', '_')}_{cell['size_class']}",
              0 <= count <= tested and (tested == 0 or abs(100 * count / tested - float(cell["reported_percent"])) < 0.0051),
              "Integer counts obey their denominator and the displayed rounding precision")
    rejects("mutation_wrong_percent", recover_positives, 37, "54.06")
    rejects("mutation_zero_denominator_percentage", recover_positives, 0, "0")
    rejects("mutation_negative_feature_count", recover_positives, -1, "50")
    rejects("mutation_percentage_outside_range", recover_positives, 10, "101")
    rejects("mutation_ambiguous_rounded_count", recover_positives, 100_000, "50")
    rejects("mutation_area_unit", square_equivalent, 30.0, area_unit="acres")
    rejects("mutation_negative_area", square_equivalent, -1.0)
    rejects("mutation_thickness_unit", excavation_volume, 30.0, 0.01, 1.0, thickness_unit="cm")
    rejects("mutation_area_fraction", excavation_volume, 30.0, 1.1, 1.0)
    rejects("mutation_recovery_fraction", synthetic_fragments, 3000.0, 5.0, 1.1)
    rejects("mutation_nonfinite_density", synthetic_fragments, 3000.0, float("nan"), 0.8)
    check("yield_linear_scaling", synthetic_fragments(3000, 50, 0.8) == 10 * synthetic_fragments(3000, 5, 0.8),
          "Changing only density by a factor of ten changes the fragment result by the same factor")
    check("zero_recovery", synthetic_fragments(3000, 50, 0.0) == 0,
          "Recovery zero produces zero fragments")
    check("geometry_unit_conversion", square_equivalent(1) == 100 and math.isclose(square_equivalent(200), math.sqrt(2_000_000)),
          "Hectares convert to square metres before square-equivalent dimensions are calculated")
    check("synthetic_equal_expected_records", len({row["expected_recorded_sites"] for row in scenarios["observation_nonidentifiability_examples"]}) == 1,
          "The distinct constructed true totals share an expected record count")
    check("repeat_zero_detection", repeat_detection(0, 10) == 0,
          "Repeating a method with zero detection probability does not recover hidden deposits")
    check("repeat_monotonicity", all(repeat_detection(0.1, k) <= repeat_detection(0.1, k + 1) for k in range(10)),
          "Detection accumulates under the stated independent-visit assumptions")
    check("remote_unmatched_arithmetic", arithmetic["cholistan_remote_mounds"]["unmatched_clusters"] == 266,
          "The unmatched unit is a remotely detected cluster")
    check("no_empirical_artifact_forecast", scenarios["status"].startswith("SYNTHETIC") and "No source-derived" in scenarios["yield_assumptions"],
          "Output type and assumption records prohibit empirical or civilization-wide forecast interpretation")
    for item in input_files:
        path = REPOSITORY / item["path"]
        check(f"input_hash_{path.name}", sha256(path) == item["sha256"], "Input hash unchanged during computation")
        changed = hashlib.sha256(path.read_bytes() + b"\x00").hexdigest()
        check(f"mutation_hash_{path.name}", changed != item["sha256"], "A one-byte mutation changes the recorded hash")
    return {"status": "passed", "check_count": len(checks), "checks": checks,
            "scope": "Computational checks of declared counts, units, rounding and output type. Archaeological source interpretation and field validation require separate review."}


def make_figures(directory: Path, green: dict, arithmetic: dict, scenarios: dict) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    from matplotlib.ticker import FuncFormatter

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 14, "axes.labelsize": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "savefig.facecolor": "white"})
    navy, teal, ochre, grey = "#233e53", "#28776d", "#b76a29", "#687784"
    figure_records = []

    def save(fig, name: str, caption: str) -> None:
        fig.savefig(directory / f"{name}.svg", bbox_inches="tight", metadata={"Date": None})
        fig.savefig(directory / f"{name}.png", bbox_inches="tight", dpi=200, metadata={"Software": "Original settlement-prospection analysis"})
        plt.close(fig)
        figure_records.append({"name": name, "svg": relative(directory / f"{name}.svg"),
                               "png": relative(directory / f"{name}.png"), "caption": caption})

    rows = green["by_map_symbol"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    y = list(range(len(rows)))
    ax.barh(y, [row["positive_percent"] for row in rows], color=[grey, teal, navy, ochre], height=0.62)
    ax.set_yticks(y, [row["map_symbol"].capitalize() for row in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 58)
    ax.set_xlabel("Field-checked features with archaeological evidence (%)")
    ax.set_title("Archaeological positives by historical-map symbol", loc="left", pad=25)
    ax.text(0, 1.025, "Green et al. 2019, Table 1: selected 2017–2018 checks; all archaeological periods",
            transform=ax.transAxes, fontsize=9.3, color=grey)
    for index, row in enumerate(rows):
        ax.text(row["positive_percent"] + 0.8, index,
                f"{row['archaeological_positives']}/{row['tested_features']} ({row['positive_percent']:.1f}%)", va="center", fontsize=10)
    ax.grid(axis="x", alpha=0.18)
    ax.set_axisbelow(True)
    fig.text(0.02, 0.02, "Recovered cell counts sum to 199 positives among 779 features. The sample was selected for map-feature checking.", fontsize=8.9)
    fig.subplots_adjust(bottom=0.19, left=0.14, right=0.99, top=0.79)
    save(fig, "historical-map-checks", "Figure: Among Green et al.'s selected historical-map checks, form-line features had 150 positives among 393 tested features. Counts span archaeological periods and describe this selected sample.")

    rows = arithmetic["ganweriwala_areas"]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    y = list(range(len(rows)))
    ax.barh(y, [row["area_ha"] for row in rows], color=[grey, teal, navy], height=0.58)
    ax.set_yticks(y, ["Legacy site boundary", "2015 ground-survey boundary", "2020 visible-mound boundary"])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Area (hectares)")
    ax.set_title("Ganweriwala: three definitions of area", loc="left", pad=25)
    ax.text(0, 1.025, "Gulzar 2018 and Orengo et al. 2020; each bar uses a different boundary and method",
            transform=ax.transAxes, fontsize=9.2, color=grey)
    for index, row in enumerate(rows):
        ax.text(row["area_ha"] + 1.4, index, f"{row['area_ha']:g} ha", va="center", fontsize=11)
    ax.grid(axis="x", alpha=0.18)
    ax.set_axisbelow(True)
    fig.text(0.02, 0.02, "These values do not constitute a confidence interval or a time series of occupation growth.", fontsize=9)
    fig.subplots_adjust(bottom=0.19, left=0.31, right=0.99, top=0.79)
    save(fig, "ganweriwala-area-definitions", "Figure: The legacy 81.5 ha estimate, Gulzar's 66.7 ha December 2015 ground survey, and Orengo et al.'s approximately 33 ha visible mound use different spatial definitions. They cannot be combined into one statistical interval.")

    fig, (chain_ax, example_ax) = plt.subplots(2, 1, figsize=(9, 6.5), gridspec_kw={"height_ratios": [1.15, 1]})
    chain_ax.set_xlim(0, 1)
    chain_ax.set_ylim(0, 1)
    chain_ax.axis("off")
    chain_ax.set_title("How occupied places become published records", loc="left", pad=20)
    labels = ["Occupied\nplaces", "Surviving\ndeposits", "Surveyed\ndeposits", "Method-detected\ndeposits", "Dated or attributed\nevidence", "Published\nrecords"]
    width = 0.147
    x_values = [0.005 + index * 0.169 for index in range(6)]
    for index, (x, label) in enumerate(zip(x_values, labels)):
        chain_ax.add_patch(FancyBboxPatch((x, 0.44), width, 0.3, boxstyle="round,pad=0.005,rounding_size=0.013",
                                         linewidth=1, facecolor="#edf2f3", edgecolor=navy))
        chain_ax.text(x + width / 2, 0.59, label, ha="center", va="center", fontsize=8.8)
        if index < 5:
            chain_ax.add_patch(FancyArrowPatch((x + width + 0.002, 0.59), (x_values[index + 1] - 0.008, 0.59),
                                               arrowstyle="-|>", mutation_scale=11, color=grey))
    chain_ax.text(0.005, 0.18, "Each stage conditions the next. The chain rule does not assume independent losses.", fontsize=10, color=grey)
    examples = scenarios["observation_nonidentifiability_examples"]
    example_ax.barh([1, 0], [row["constructed_true_sites"] for row in examples], color="#dce5e8", height=0.58, label="Constructed true total")
    example_ax.barh([1, 0], [row["expected_recorded_sites"] for row in examples], color=teal, height=0.58, label="Expected records")
    example_ax.set_yticks([1, 0], ["200 places × 0.5 recording", "1,000 places × 0.1 recording"])
    example_ax.set_xlim(0, 1100)
    example_ax.set_xlabel("Constructed number of places")
    example_ax.set_title("The same expected record count can arise from different totals", loc="left", fontsize=12, pad=12)
    for row, y_value in zip(examples, [1, 0]):
        example_ax.text(row["constructed_true_sites"] + 12, y_value, f"{row['constructed_true_sites']:,}", va="center", fontsize=10)
        example_ax.text(50, y_value, "100", ha="center", va="center", color="white", fontsize=9)
    example_ax.legend(loc="upper right", frameon=False, fontsize=9)
    example_ax.grid(axis="x", alpha=0.18)
    example_ax.set_axisbelow(True)
    fig.text(0.015, 0.01, "SYNTHETIC examples: probabilities and totals are constructed. They illustrate missing-total nonidentifiability.", fontsize=9)
    fig.subplots_adjust(left=0.25, bottom=0.13, right=0.99, top=0.89, hspace=0.47)
    # The top diagram needs the full width, while the lower plot retains space for labels.
    chain_ax.set_position([0.02, 0.56, 0.96, 0.32])
    save(fig, "observation-chain", "Figure: A conditional observation chain separates occupation, survival, survey coverage, detection, attribution and publication. In constructed examples, 200 places recorded with overall probability 0.5 and 1,000 recorded with probability 0.1 each give 100 expected records. No actual missing-site total is estimated.")

    rows = scenarios["yield_scenarios"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    y = list(range(len(rows)))
    ax.barh(y, [row["synthetic_recovered_fragments"] for row in rows], color=[navy, teal, ochre], height=0.58)
    ax.set_yticks(y, [f"{row['assumed_fragment_density_per_m3']:g} fragments/m³" for row in rows])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(1000, 4_000_000)
    ax.set_xticks([10_000, 100_000, 1_000_000], ["10,000", "100,000", "1,000,000"])
    ax.set_xlabel("Constructed recovered-fragment count (logarithmic axis)")
    ax.set_title("Synthetic find-yield sensitivity", loc="left", pad=38)
    ax.text(0, 1.085, "30 ha × 1% excavated × 1 m thickness = 3,000 m³; assumed recovery = 80%",
            transform=ax.transAxes, fontsize=9.2, color=grey)
    ax.text(0, 1.025, "Only the assumed density changes between the three examples", transform=ax.transAxes, fontsize=9.2, color=grey)
    for index, row in enumerate(rows):
        value = row["synthetic_recovered_fragments"]
        ax.text(value * 1.13, index, f"{value:,.0f}", va="center", fontsize=10)
    ax.grid(axis="x", which="major", alpha=0.18)
    ax.set_axisbelow(True)
    fig.text(0.02, 0.02, "All inputs are illustrative assumptions. The calculation supplies no empirical fragment density or rare-object rate.", fontsize=8.9)
    fig.subplots_adjust(bottom=0.18, left=0.22, right=0.98, top=0.74)
    save(fig, "synthetic-find-yield", "Figure: Illustrative densities of 5, 50 and 500 fragments per cubic metre, applied to a constructed excavation volume of 3,000 m³ at assumed 80% recovery, yield 12,000, 120,000 and 1,200,000 fragments. These are sensitivity examples, not find forecasts.")

    write_json(directory / "manifest.json", {"rights_status": "own-work", "method": "Original matplotlib plots from this run's aggregate results and synthetic calculations",
                                              "figures": figure_records,
                                              "files": [evidence_file(path, "original figure") for path in sorted(directory.iterdir()) if path.is_file()]})
    return figure_records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New aggregate-results directory")
    parser.add_argument("--figures", type=Path, required=True, help="New original-figures directory")
    args = parser.parse_args()
    output, figures = args.output.resolve(), args.figures.resolve()
    if output == figures:
        parser.error("Results and figures require distinct directories")
    for path in (output, figures):
        if path.exists():
            parser.error(f"Refusing to replace an existing endpoint: {path}")
    # Check dependencies and all inputs before creating the endpoint.
    import matplotlib
    census = json.loads(CENSUS_INPUT.read_text(encoding="utf-8"))
    dating = json.loads(DATING_INPUT.read_text(encoding="utf-8"))
    input_files = [evidence_file(CENSUS_INPUT, "selected coordinate metadata"), evidence_file(DATING_INPUT, "separate selected chronological metadata")]
    witnesses = [evidence_file(RAW / name, "local-only source witness") for name in
                 ("GREEN2019.pdf", "ORENGO2020.xml", "GARCIA2023.pdf", "GULZAR2018.pdf") if (RAW / name).is_file()]
    meta, countries, chronology_countries = metadata(census, dating)
    green, cells, symbols, sizes = green_table()
    arithmetic = published_arithmetic()
    scenarios, geometry, yields, repeats = synthetic_scenarios()
    checked = verification(meta, green, arithmetic, scenarios, input_files)
    output.mkdir(parents=True, exist_ok=False)
    figures.mkdir(parents=True, exist_ok=False)
    write_json(output / "metadata-coverage.json", meta)
    write_csv(output / "coordinate-metadata-by-country.csv", countries)
    write_csv(output / "chronology-metadata-by-country.csv", chronology_countries)
    write_json(output / "historical-map-checks.json", green)
    write_csv(output / "historical-map-checks-cells.csv", cells)
    write_csv(output / "historical-map-checks-by-symbol.csv", symbols)
    write_csv(output / "historical-map-checks-by-size-class.csv", sizes)
    write_json(output / "published-count-arithmetic.json", arithmetic)
    write_json(output / "synthetic-scenarios.json", scenarios)
    write_csv(output / "square-equivalent-geometry.csv", geometry)
    write_csv(output / "synthetic-fragment-yields.csv", yields)
    write_csv(output / "synthetic-repeat-detection.csv", repeats)
    write_json(output / "verification.json", checked)
    figure_records = make_figures(figures, green, arithmetic, scenarios)
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(), "status": "verified-computation",
        "script": evidence_file(Path(__file__), "own analysis code"), "inputs": input_files,
        "source_witnesses": witnesses, "source_witness_handling": "Local-only downloaded third-party material; hashes and canonical source pointers describe the witnesses.",
        "environment": {"python": platform.python_version(), "matplotlib": matplotlib.__version__, "platform": platform.platform()},
        "outputs": [evidence_file(path, "own aggregate result") for path in sorted(output.iterdir()) if path.is_file()],
        "figures_manifest": evidence_file(figures / "manifest.json", "own original-figure manifest"),
        "figure_count": len(figure_records), "verification_check_count": checked["check_count"],
        "reproduction": "Use new --output and --figures directories for every rerun. Preserve this endpoint and compare hashes and numerical values separately from rendering-environment changes.",
    }
    write_json(output / "manifest.json", manifest)
    print(json.dumps({"output": relative(output), "figures": relative(figures),
                      "checks_passed": checked["check_count"], "green_tested": green["tested_features"],
                      "green_positives": green["archaeological_positives"], "figure_count": len(figure_records)}, indent=2))


if __name__ == "__main__":
    main()
