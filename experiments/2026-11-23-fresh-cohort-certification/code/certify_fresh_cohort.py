"""Deterministic fresh-cohort certification pipeline for post-catalogue Indus finds.

Implements experiments/2026-11-23-fresh-cohort-certification/PROTOCOL.md.
Strictly blind to inscription sign sequences: never loads sign strings from Lipi
and never displays PDF page images or inscription readings.
"""
from __future__ import annotations

import csv
import datetime
import functools
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
RAW_OUT = ROOT / "data" / "raw" / "2026-11-23-fresh-cohort-certification"

INPUTS = {
    "protocol": PKG / "PROTOCOL.md",
    "objects_503": ROOT / "experiments/2026-10-21-post-catalogue-finds/objects.csv",
    "join_decisions": ROOT / "experiments/2026-10-21-post-catalogue-finds/join-decisions.csv",
    "local_unnamed": ROOT / "experiments/2026-10-21-post-catalogue-finds/local-unnamed.csv",
    "source_register": ROOT / "experiments/2026-10-21-post-catalogue-finds/matching/source-register.csv",
    "exposure_log": ROOT / "experiments/2026-10-21-post-catalogue-finds/exposure-log.csv",
    "reconciled_358": ROOT / "data/raw/2026-10-22-candidate-identity-exposure/run-v3/reconciled-dispositions.csv",
    "candidate_reviews_358": ROOT / "data/raw/2026-10-22-candidate-identity-exposure/run-v3/candidate-reviews.jsonl",
    "duplicate_relations": ROOT / "data/raw/2026-10-22-candidate-identity-exposure/run-v3/duplicate-relations.jsonl",
    "lipi_faces": ROOT / "data/normalized/lipi_observed_faces.jsonl",
    "base_register_4695": ROOT / "data/raw/2026-10-22-object-register/run-v2/objects.jsonl",
    "mackay_marshall_1146": ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv",
    "cisi_flags_3680": ROOT / "experiments/2026-10-13-cisi-basic-data-full/object-flags.csv",
    "cisi1_basic": ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl",
    "cisi2_basic": ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi2-basic-data.jsonl",
    "bench_spent": ROOT / "bench/spent.json",
    "predictions_json": ROOT / "experiments/2026-10-20-seal-legend-units/predictions.json",
    "calibration_json": ROOT / "experiments/2026-10-20-seal-legend-units/run-2026-10-20/calibration-v2.json",
    "farmana_coverage": ROOT / "experiments/2026-10-20-fresh-test-collection/coverage-summary.json",
}

# Farmana rows independently verified as known matches to Lipi families 149-153
# in 2026-10-20-fresh-test-collection and 2026-10-20-farmana-reserve-review.
FARMANA_VERIFIED_KNOWN = {
    "PCF-FRM-001": "151",
    "PCF-FRM-002": "149",
    "PCF-FRM-003": "153",
    "PCF-FRM-004": "152",
    "PCF-FRM-005": "150",
}

PLACEHOLDERS = {"", "-", "--", "- -", "?", "??", "Unknown", "unknown", None}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_digits(s: str) -> set[str]:
    """Extract whole numeric tokens of length >= 3 for conservative identifier checks."""
    return {m for m in re.findall(r"\d+", s or "") if len(m) >= 3}


def norm_token(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def is_blank(val: object) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s in PLACEHOLDERS or s == "0"


def canonical_object_class(obj_type: str) -> str:
    t = (obj_type or "").strip().lower()
    if t == "seal":
        return "seal"
    if t == "sealing":
        return "sealing"
    if t == "tablet":
        return "tablet"
    if "pottery" in t or t.startswith("pot"):
        return "pottery"
    if t == "inscribed-tool":
        return "inscribed-tool"
    return "other"


def lipi_type_compatible(obj_class: str, lipi_type: str) -> bool:
    lt = (lipi_type or "").upper()
    if not lt or lt == "UNKNOWN":
        return True
    if obj_class == "seal":
        return lt.startswith("SEAL")
    if obj_class == "sealing":
        return lt.startswith("TAG") or lt.startswith("IMPL")
    if obj_class == "tablet":
        return lt.startswith("TAB")
    if obj_class == "pottery":
        return lt.startswith("POT")
    if obj_class == "inscribed-tool":
        return lt.startswith("MISC") or lt.startswith("COP") or lt.startswith("IMP") or lt.startswith("TOOL")
    return True


def parse_pdf_pages(spec: str) -> list[int]:
    pages: list[int] = []
    for part in re.split(r"[;,]", spec or ""):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b and (b - a) <= 20:
                pages.extend(range(a, b + 1))
        elif re.match(r"^\d+$", part):
            pages.append(int(part))
    return sorted(set(pages))


def extract_plate_tokens(plate_str: str) -> list[str]:
    """Return normalized search patterns for a figure or plate reference."""
    if not plate_str:
        return []
    tokens = []
    for seg in re.split(r"[;,]", plate_str):
        seg = seg.strip()
        if not seg:
            continue
        # Remove bracketed OCR notes like 2[1] -> check both 21 and 2
        cleaned = re.sub(r"\[(\d+)\]", r"\1", seg)
        # Extract label + number
        m = re.search(r"(pl\.?|plate|fig\.?|figure)\s*([0-9ivxlcdm]+(?:[.:a-z0-9-]+)?)", cleaned, re.I)
        if m:
            kind = "pl" if m.group(1).lower().startswith("pl") else "fig"
            num = m.group(2).strip().rstrip(".")
            tokens.append(f"{kind}:{num.lower()}")
        else:
            tokens.append(cleaned.lower())
    return tokens


def match_caption_in_text(text: str, plate_tokens: list[str]) -> list[str]:
    """Check whether plate/figure caption tokens (including ranges and parent figures) appear on a page."""
    hits = []
    low = re.sub(r"\s+", " ", (text or "").lower())
    for tok in plate_tokens:
        if ":" in tok:
            kind, num = tok.split(":", 1)
            base_num = re.split(r"[:\s]", num)[0]
            prefix = r"\b(?:pl\.?|plate|pls\.?|plates)\s*" if kind == "pl" else r"\b(?:fig\.?|figure|figs\.?|figures)\s*"
            # 1. Exact label match (e.g. 'pl. 6.1', 'figure 6')
            if re.search(prefix + re.escape(base_num) + r"\b", low):
                hits.append(tok)
                continue
            # 2. Sub-panel letter split (e.g. '4d' -> 'fig. 4 d' or parent figure 'fig. 4')
            m_split = re.match(r"^([0-9ivxlcdm]+)([a-z])$", base_num)
            if m_split:
                parent_num, sub = m_split.group(1), m_split.group(2)
                if re.search(prefix + re.escape(parent_num) + r"\s*[\(\[]?" + re.escape(sub) + r"\b", low):
                    hits.append(tok)
                    continue
                if re.search(prefix + re.escape(parent_num) + r"\b", low):
                    hits.append(f"{kind}:{parent_num}(parent)")
                    continue
            # 3. Numeric plate/figure range (e.g. 'Plates 13-14' contains 13)
            if base_num.isdigit():
                target_n = int(base_num)
                for m_rng in re.finditer(prefix + r"(\d+)\s*[-–]\s*(\d+)\b", low):
                    lo_n, hi_n = int(m_rng.group(1)), int(m_rng.group(2))
                    if lo_n <= target_n <= hi_n and (hi_n - lo_n) <= 10:
                        hits.append(f"{kind}:{lo_n}-{hi_n}(range)")
                        break
        elif tok and tok in low:
            hits.append(tok)
    return hits


def blind_pdf_plate_audit(
    row: dict,
    src: dict,
    pdf_log: list[dict],
) -> dict:
    """Verify held PDF existence, hash, page bounds, and image/drawing presence blindly.

    Never renders images for visual inspection and never extracts sign sequences.
    Requires embedded raster image(s) (or >200 vector drawing primitives) on a confirmed
    plate/figure page; prose text pages with zero images are never accepted as plates.
    """
    sid = row["primary_publication"]
    lp_rel = (src.get("local_path") or "").strip()
    plate_str = (row.get("plate_or_figure") or "").strip()
    pdf_pages = parse_pdf_pages(row.get("pdf_page") or "")
    expected_sha = (src.get("sha256") or "").strip()

    res = {
        "source_id": sid,
        "local_path": lp_rel,
        "file_exists": False,
        "is_pdf": False,
        "sha256_matches_register": False,
        "pdf_page_count": None,
        "cited_pdf_pages": pdf_pages,
        "cited_plate_or_figure": plate_str,
        "verified_plate_pdf_pages": [],
        "interleaved_unindexed_plate_leaves": [],
        "embedded_images_on_verified_pages": 0,
        "vector_drawings_on_verified_pages": 0,
        "max_image_pixels": None,
        "caption_token_hits": [],
        "plate_verified": False,
        "plate_status": "no_held_file",
    }

    if not lp_rel:
        return res
    full_path = ROOT / lp_rel
    if not full_path.exists():
        return res
    res["file_exists"] = True

    actual_sha = sha256_file(full_path)
    res["sha256_matches_register"] = bool(expected_sha) and (actual_sha.lower() == expected_sha.lower())

    if full_path.suffix.lower() != ".pdf":
        res["plate_status"] = f"non_pdf_source_{full_path.suffix.lower().lstrip('.')}"
        pdf_log.append({
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "row_id": row["row_id"],
            "source_id": sid,
            "path": lp_rel,
            "action": "stat_and_hash_non_pdf",
            "sha256": actual_sha,
            "sha256_matches_register": res["sha256_matches_register"],
        })
        return res

    res["is_pdf"] = True
    plate_tokens = extract_plate_tokens(plate_str)

    doc = fitz.open(str(full_path))
    try:
        n_pages = len(doc)
        res["pdf_page_count"] = n_pages

        in_bounds_cited = [p for p in pdf_pages if 1 <= p <= n_pages]
        search_pages = list(in_bounds_cited)
        for p in in_bounds_cited:
            for delta in (1, 2, 3, 4, 5, -1, -2, -3, -4):
                q = p + delta
                if 1 <= q <= n_pages and q not in search_pages:
                    search_pages.append(q)

        checked_stats: dict[int, dict] = {}

        def inspect_page(pno: int) -> dict:
            if pno in checked_stats:
                return checked_stats[pno]
            page = doc[pno - 1]
            imgs = page.get_images(full=True)
            max_px = max((im[2] * im[3] for im in imgs), default=0)
            drawings = len(page.get_drawings())
            txt = page.get_text("text") or ""
            hits = match_caption_in_text(txt, plate_tokens) if plate_tokens else []
            st = {
                "page": pno,
                "text_len": len(txt),
                "n_images": len(imgs),
                "max_image_pixels": max_px,
                "n_drawings": drawings,
                "caption_hits": hits,
            }
            checked_stats[pno] = st
            return st

        for pno in search_pages:
            inspect_page(pno)

        # Detect whether this is a full-page scanned PDF (nearly all nearby pages have exactly 1 scan raster)
        nearby_one_img = sum(1 for st in checked_stats.values() if st["n_images"] == 1)
        is_fullpage_scan_pdf = len(checked_stats) >= 4 and (nearby_one_img / len(checked_stats)) >= 0.85

        def is_true_plate_page(st: dict) -> bool:
            has_visual = st["n_images"] >= 1 or st["n_drawings"] > 200
            if not has_visual or not st["caption_hits"]:
                return False
            # On a full-page scanned PDF, a prose page (text_len > 800) with 1 scan raster is just a text page
            # that mentions the plate in prose; a genuine plate/figure page has short caption text (< 600 chars).
            if is_fullpage_scan_pdf and st["n_images"] == 1 and st["text_len"] > 600:
                return False
            return True

        matched_plate_pages = [p for p, st in checked_stats.items() if is_true_plate_page(st)]
        interleaved_image_only = sorted(
            p for p, st in checked_stats.items()
            if st["n_images"] >= 1 and st["text_len"] <= 20
        )

        # If a plate is cited and not found in the local window, scan the rest of the PDF for a caption-matched visual page
        if plate_tokens and not matched_plate_pages and not interleaved_image_only:
            for pno in range(1, n_pages + 1):
                if pno in checked_stats:
                    continue
                txt = doc[pno - 1].get_text("text") or ""
                if match_caption_in_text(txt, plate_tokens):
                    st = inspect_page(pno)
                    if is_true_plate_page(st):
                        matched_plate_pages.append(pno)
                        if len(matched_plate_pages) >= 3:
                            break

        if plate_str:
            if matched_plate_pages:
                ref_p = in_bounds_cited[0] if in_bounds_cited else matched_plate_pages[0]
                # Prefer dedicated plate/figure pages (shorter text_len) first, then proximity to cited page
                matched_plate_pages = sorted(
                    set(matched_plate_pages),
                    key=lambda x: (0 if checked_stats[x]["text_len"] < 600 else 1, abs(x - ref_p)),
                )
                # Keep dedicated plate pages exclusively if any exist
                dedicated = [p for p in matched_plate_pages if checked_stats[p]["text_len"] < 600]
                chosen = dedicated[:2] if dedicated else matched_plate_pages[:2]
                res["verified_plate_pdf_pages"] = chosen
                res["caption_token_hits"] = sorted({h for p in chosen for h in checked_stats[p]["caption_hits"]})
                res["embedded_images_on_verified_pages"] = sum(checked_stats[p]["n_images"] for p in chosen)
                res["vector_drawings_on_verified_pages"] = sum(checked_stats[p]["n_drawings"] for p in chosen)
                res["max_image_pixels"] = max(checked_stats[p]["max_image_pixels"] for p in chosen)
                res["plate_verified"] = True
                res["plate_status"] = "verified_plate_caption_and_visual"
            elif interleaved_image_only:
                res["interleaved_unindexed_plate_leaves"] = interleaved_image_only[:5]
                res["plate_verified"] = False
                res["plate_status"] = "interleaved_image_only_plate_leaf_no_ocr_caption"
            else:
                res["plate_verified"] = False
                res["plate_status"] = "cited_plate_not_located_by_ocr"
        else:
            res["plate_status"] = "no_plate_or_figure_cited"

        pdf_log.append({
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "row_id": row["row_id"],
            "source_id": sid,
            "path": lp_rel,
            "action": "blind_pdf_page_and_caption_probe",
            "sha256": actual_sha,
            "sha256_matches_register": res["sha256_matches_register"],
            "pdf_page_count": n_pages,
            "pages_inspected_count": len(checked_stats),
            "verified_plate_pdf_pages": res["verified_plate_pdf_pages"],
            "interleaved_unindexed_plate_leaves": res["interleaved_unindexed_plate_leaves"],
            "plate_status": res["plate_status"],
            "sign_sequences_read": False,
            "images_rendered_to_agent": False,
        })
    finally:
        doc.close()

    return res


def mcnemar_one_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(b, n + 1)) * (0.5 ** n)


@functools.lru_cache(maxsize=None)
def mcnemar_cached(b: int, c: int) -> float:
    return mcnemar_one_sided(b, c)


def binom_tail(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, j) * (p ** j) * ((1.0 - p) ** (n - j)) for j in range(k, n + 1))


def compute_power_for_n(n_seals: int, pred_spec: dict, cal: dict) -> dict:
    """Compute exact P1-P4 pass bounds and statistical power for a seal pool of size n_seals.

    Uses the exact frozen bounds in predictions.json and exact simulation model/seed (20261021)
    from experiments/2026-10-20-seal-legend-units/make_predictions.py.
    """
    if n_seals <= 0:
        return {
            "n_single_line": 0,
            "P1": {"scorable": False},
            "P2": {"scorable": False},
            "P3": {"scorable": False},
            "P4": {"note": "Requires >=3 divided (two-line) seal legends across both pools; expected <1 in this pool."},
        }

    rng = np.random.default_rng(20261021 + n_seals)
    sims = 40000
    s1 = cal["S1_closing_coverage"]
    s2 = cal["S2_end_start_asymmetry"]
    s3 = cal["S3_opening_known_elsewhere"]
    n_h = cal["held_legends"]
    p1 = s1["count"] / n_h
    p0 = s1["shuffle_null_mean"]
    p3 = s3["held_known"] / s3["held_scored"]
    share3 = s3["share_of_legends_scored"]
    pb = s2["discordant_end"] / n_h
    pc = s2["discordant_start"] / n_h

    key = str(min(max(n_seals, 1), 400))
    lo = pred_spec["bounds"]["P1"]["lower"][key]
    kill = pred_spec["bounds"]["P1"]["kill"][key]

    p1_out = {
        "n_single_line": n_seals,
        "lower_bound": round(lo, 6),
        "kill_bound": round(kill, 6),
        "kill_active": n_seals >= 20,
        "p_pass_if_held_rate": round(float(np.mean(rng.binomial(n_seals, p1, size=sims) / n_seals >= lo - 1e-12)), 4),
        "p_pass_if_held_minus_0.15": round(float(np.mean(rng.binomial(n_seals, p1 - 0.15, size=sims) / n_seals >= lo - 1e-12)), 4),
        "p_pass_if_held_minus_0.25": round(float(np.mean(rng.binomial(n_seals, p1 - 0.25, size=sims) / n_seals >= lo - 1e-12)), 4),
        "p_pass_if_shuffle_null": round(float(np.mean(rng.binomial(n_seals, p0, size=sims) / n_seals >= lo - 1e-12)), 4),
    }

    def p2_rate(qb: float, qc: float, n_sim: int = 20000) -> float:
        draws = rng.multinomial(n_seals, [qb, qc, max(0.0, 1.0 - qb - qc)], size=n_sim)
        return float(np.mean([(b > c) and mcnemar_cached(int(b), int(c)) < 0.05 for b, c, _ in draws]))

    half = (pb + pc) / 2.0
    p2_out = {
        "n_single_line": n_seals,
        "p_pass_if_held_rates": round(p2_rate(pb, pc), 4),
        "p_pass_if_half_asymmetry": round(p2_rate(half + (pb - pc) / 4.0, half - (pb - pc) / 4.0), 4),
        "p_pass_if_no_asymmetry": round(p2_rate(half, half), 4),
    }

    k_open = max(1, int(round(n_seals * share3)))
    hi = pred_spec["bounds"]["P3"]["upper"][str(min(k_open, 400))]
    p3_out = {
        "expected_openings_scored": k_open,
        "upper_bound": round(hi, 6),
        "p_pass_if_held_rate": round(float(np.mean(rng.binomial(k_open, p3, size=sims) / k_open <= hi + 1e-12)), 4),
        "p_pass_if_held_plus_0.20": round(float(np.mean(rng.binomial(k_open, min(p3 + 0.20, 1.0), size=sims) / k_open <= hi + 1e-12)), 4),
        "p_pass_if_formulaic_0.90": round(float(np.mean(rng.binomial(k_open, 0.90, size=sims) / k_open <= hi + 1e-12)), 4),
    }

    # Divided legends: in Lipi, 93 of 2,239 seals (4.15%) have a catalogue line division
    exp_divided = round(n_seals * (93.0 / 2239.0), 3)
    p4_out = {
        "expected_divided_seals_at_lipi_rate_4.15pct": exp_divided,
        "min_divided_faces_required": 3,
        "power_if_3_divided": round(binom_tail(3, 3, 37 / 59), 4),
        "scorable_alone_expected": exp_divided >= 3.0,
    }

    return {
        "n_single_line": n_seals,
        "credence_weight_multiplier": 1.0 if n_seals >= 20 else 0.5,
        "P1": p1_out,
        "P2": p2_out,
        "P3": p3_out,
        "P4": p4_out,
    }


def main() -> None:
    RAW_OUT.mkdir(parents=True, exist_ok=True)

    # 1. Hash all inputs
    input_hashes = {}
    for k, p in INPUTS.items():
        if not p.exists():
            raise SystemExit(f"Missing required input {k}: {p}")
        input_hashes[k] = {
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        }
    (RAW_OUT / "input-hashes.json").write_text(json.dumps(input_hashes, indent=2) + "\n", encoding="utf-8")

    # 2. Load base register (4,695) and Lipi metadata ONLY (explicitly excluding sign fields)
    base_reg = {}
    with INPUTS["base_register_4695"].open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                base_reg[str(obj["source_family_id"])] = {
                    "object_id": obj["object_id"],
                    "exposure_status": obj["exposure_status"],
                    "physical_identity_status": obj["physical_identity_status"],
                }

    lipi_families: dict[str, dict] = {}
    lipi_by_site: dict[str, list[str]] = defaultdict(list)
    lipi_by_cisi: dict[str, set[str]] = defaultdict(set)
    lipi_by_site_reg_token: dict[tuple[str, str], set[str]] = defaultdict(set)
    lipi_face_count = 0

    with INPUTS["lipi_faces"].open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            lipi_face_count += 1
            d = json.loads(line)
            fid = str(d["object_family_id"])
            if fid in lipi_families:
                continue
            m = d.get("metadata", {})
            site = (d.get("site") or "").strip()
            otype = (d.get("object_type") or m.get("type") or "").strip()
            cisi = (d.get("source_cisi") or m.get("cisi") or "").strip()
            excav = (m.get("excavation-idno") or "").strip()
            rec = {
                "family_id": fid,
                "site": site,
                "object_type": otype,
                "material": (m.get("material") or "").strip(),
                "cisi": cisi,
                "excavation_idno": excav,
                "area": (m.get("area-section") or "").strip(),
                "block": (m.get("block-house") or "").strip(),
                "room": (m.get("room-grid") or "").strip(),
                "h_mm": (m.get("horizontal(mm)") or "").strip(),
                "v_mm": (m.get("vertical(mm)") or "").strip(),
                "th_mm": (m.get("thickness(mm)") or "").strip(),
                "period": (m.get("period") or "").strip(),
            }
            lipi_families[fid] = rec
            if site:
                lipi_by_site[site.lower()].append(fid)
            if not is_blank(cisi):
                lipi_by_cisi[norm_token(cisi)].add(fid)
            if site and not is_blank(excav):
                lipi_by_site_reg_token[(site.lower(), norm_token(excav))].add(fid)
                for dg in norm_digits(excav):
                    lipi_by_site_reg_token[(site.lower(), f"num:{dg}")].add(fid)

    # 3. Load 1,146 Mackay/Marshall joins
    mm_rows = []
    mm_by_field = defaultdict(set)
    mm_by_family = defaultdict(list)
    with INPUTS["mackay_marshall_1146"].open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            mm_rows.append(r)
            fid = r["lipi_family_id"].strip()
            mm_by_family[fid].append(r["source_row_id"])
            if not is_blank(r.get("field_no")):
                mm_by_field[norm_token(r["field_no"])].add(fid)

    # 4. Load CISI 1 & 2 basic-data joins (3,680 flags, 2,602 joined; plus 1,543 + 2,139 rows)
    cisi_flags = []
    cisi_joined_count = 0
    cisi_key_to_family: dict[str, str] = {}
    with INPUTS["cisi_flags_3680"].open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cisi_flags.append(r)
            if r["join"] == "one-family" and r["lipi_family"].strip():
                cisi_joined_count += 1
                cisi_key_to_family[norm_token(r["cisi"])] = r["lipi_family"].strip()

    cisi_basic_by_cisi: dict[str, dict] = {}
    cisi_basic_by_site_excav: dict[tuple[str, str], set[str]] = defaultdict(set)
    cisi_basic_sites: Counter = Counter()
    for path_key in ("cisi1_basic", "cisi2_basic"):
        with INPUTS[path_key].open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                ck = norm_token(d.get("cisi", ""))
                sh = (d.get("site_heading") or "").strip().lower()
                cisi_basic_sites[sh] += 1
                cisi_basic_by_cisi[ck] = {
                    "cisi": d.get("cisi", ""),
                    "volume": d.get("volume", ""),
                    "site_heading": sh,
                    "col3_excavation": d.get("col3_excavation", ""),
                    "lipi_family": cisi_key_to_family.get(ck, ""),
                }
                exc = d.get("col3_excavation") or ""
                if sh and not is_blank(exc):
                    cisi_basic_by_site_excav[(sh, norm_token(exc))].add(d.get("cisi", ""))

    # 5. Load bench/spent.json
    spent_data = json.loads(INPUTS["bench_spent"].open(encoding="utf-8").read())
    spent_input_hashes = {v.get("input_sha256", "") for v in spent_data.get("splits", {}).values()}
    spent_lipi_is_spent = input_hashes["lipi_faces"]["sha256"] in spent_input_hashes

    # 6. Load 503 post-catalogue rows, source register, 358 candidate audit, duplicates
    with INPUTS["objects_503"].open(encoding="utf-8") as f:
        objects_503 = list(csv.DictReader(f))
    with INPUTS["source_register"].open(encoding="utf-8") as f:
        source_reg = {r["source_id"]: r for r in csv.DictReader(f)}
    with INPUTS["reconciled_358"].open(encoding="utf-8") as f:
        reconciled_358 = {r["source_row_id"]: r for r in csv.DictReader(f)}
    reviews_358 = {}
    with INPUTS["candidate_reviews_358"].open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                reviews_358[d["source_row_id"]] = d
    dup_relations = []
    dup_by_row: dict[str, list[dict]] = defaultdict(list)
    with INPUTS["duplicate_relations"].open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                dup_relations.append(d)
                for rid in d["row_ids"]:
                    dup_by_row[rid].append(d)

    # 7. Adjudicate every one of the 503 rows
    pdf_log: list[dict] = []
    certified_rows: list[dict] = []

    for row in objects_503:
        rid = row["row_id"]
        site_code = row["site_code"]
        site = row["site"]
        local_site = (row["local_site_label"] or site).strip()
        obj_class = canonical_object_class(row["object_type"])
        cat_status = row["catalogue_status"]
        insc_status = row["inscription_status"]
        reg = (row["registration"] or "").strip()
        cisi_base = (row["cisi_in_baseline"] or "").strip()
        src = source_reg.get(row["primary_publication"], {})
        rec358 = reconciled_358.get(rid)
        rev358 = reviews_358.get(rid)

        # Cross-corpus deterministic checks
        lipi_site_fids = lipi_by_site.get(local_site.lower(), [])
        lipi_compat_fids = [
            fid for fid in lipi_site_fids
            if lipi_type_compatible(obj_class, lipi_families[fid]["object_type"])
        ]

        # Direct CISI / registration / Mackay-Marshall / CISI 1-2 checks
        direct_lipi_hits: set[str] = set()
        direct_cisi_basic_hits: set[str] = set()
        direct_mm_hits: set[str] = set()

        if not is_blank(cisi_base):
            for part in re.split(r"[;,\s]+", cisi_base):
                nt = norm_token(part)
                if nt in lipi_by_cisi:
                    direct_lipi_hits.update(lipi_by_cisi[nt])
                if nt in cisi_basic_by_cisi:
                    direct_cisi_basic_hits.add(cisi_basic_by_cisi[nt]["cisi"])
                    if cisi_basic_by_cisi[nt]["lipi_family"]:
                        direct_lipi_hits.add(cisi_basic_by_cisi[nt]["lipi_family"])

        if not is_blank(reg):
            nt_reg = norm_token(reg)
            if (local_site.lower(), nt_reg) in lipi_by_site_reg_token:
                direct_lipi_hits.update(lipi_by_site_reg_token[(local_site.lower(), nt_reg)])
            if local_site.lower() == "mohenjo-daro" and nt_reg in mm_by_field:
                direct_mm_hits.update(mm_by_field[nt_reg])
            if (local_site.lower(), nt_reg) in cisi_basic_by_site_excav:
                direct_cisi_basic_hits.update(cisi_basic_by_site_excav[(local_site.lower(), nt_reg)])

        supported_fids = list(rev358.get("supported_candidate_family_ids", [])) if rev358 else []
        unresolved_fids = list(rev358.get("unresolved_candidate_family_ids", [])) if rev358 else []
        exp_status_2026_10_22 = rec358["reviewed_exposure_status"] if rec358 else "not_in_358_baseline_catalogued"
        id_status_2026_10_22 = rec358["identity_status"] if rec358 else "in_baseline_catalogue"

        # Check duplicate relations
        row_dups = dup_by_row.get(rid, [])
        is_secondary_possible_dup = bool((row.get("possible_duplicate_of") or "").strip())

        # Determine if this row is a verified-absent post-catalogue object eligible for blind PDF plate check
        # Note: PCF-DHV-141 is excluded from verified-absent because Dholavira has 106 unregistered Lipi SEAL*
        # families including family 4277 in grid square 35 x 63 x 4 (period 6) and 8 SEAL* families with no spatial unit.
        is_dholavira_unregistered_pool = (
            site_code == "DHV"
            and cat_status == "post-catalogue"
            and id_status_2026_10_22 != "identifier_supported_provisional_family"
        )
        is_surkotada_pottery_alias_pool = (
            site_code == "SKT"
            and cat_status == "post-catalogue"
            and obj_class == "pottery"
        )

        # Evaluate absence proof for non-matched, non-baseline, non-DHV-pool rows
        absence_proof_basis = None
        if (
            cat_status == "post-catalogue"
            and id_status_2026_10_22 == "not_linked_in_held_register"
            and not is_dholavira_unregistered_pool
            and not direct_lipi_hits
            and not direct_mm_hits
            and not direct_cisi_basic_hits
            and not supported_fids
            and not unresolved_fids
        ):
            if len(lipi_site_fids) == 0:
                absence_proof_basis = "site_absent_in_lipi_and_cisi"
            elif len(lipi_compat_fids) == 0:
                absence_proof_basis = "site_type_absent_in_lipi_and_cisi"
            else:
                # Check if all compatible local families are exhaustively ruled out by registration or material
                all_disjoint_reg = (
                    not is_blank(reg)
                    and all(
                        not is_blank(lipi_families[fid]["excavation_idno"])
                        and norm_token(lipi_families[fid]["excavation_idno"]) != norm_token(reg)
                        for fid in lipi_compat_fids
                    )
                )
                row_mat = (row.get("material") or "").strip().lower()
                all_disjoint_mat = (
                    bool(row_mat)
                    and all(
                        not is_blank(lipi_families[fid]["material"])
                        and lipi_families[fid]["material"].strip().lower() != row_mat
                        for fid in lipi_compat_fids
                    )
                )
                if all_disjoint_reg:
                    absence_proof_basis = "site_registration_exhaustive_disjoint"
                elif all_disjoint_mat:
                    absence_proof_basis = "site_type_material_exhaustive_disjoint"
                else:
                    absence_proof_basis = "unverified_against_site_lipi_pool"

        # Run blind PDF plate audit on all verified-absent post-catalogue rows (and also on GDH-013/014 for completeness)
        plate_audit = None
        if cat_status == "post-catalogue" and id_status_2026_10_22 == "not_linked_in_held_register" and not is_dholavira_unregistered_pool:
            plate_audit = blind_pdf_plate_audit(row, src, pdf_log)

        # Tier assignment (mutually exclusive, strictly following PROTOCOL.md)
        tier = ""
        sub_reason = ""

        # Tier 1: already_present_or_exposed
        if cat_status in ("in-baseline-catalogue", "possibly-in-cisi3"):
            tier = "already_present_or_exposed"
            sub_reason = "cisi_baseline_catalogue" if cat_status == "in-baseline-catalogue" else "possibly_in_cisi3_catalogue"
        elif (
            row["local_match"] == "matched"
            or id_status_2026_10_22 == "identifier_supported_provisional_family"
            or bool(direct_lipi_hits)
            or bool(direct_mm_hits)
        ):
            tier = "already_present_or_exposed"
            sub_reason = "matched_to_lipi_identifier"
        elif rid in FARMANA_VERIFIED_KNOWN:
            tier = "already_present_or_exposed"
            sub_reason = "confirmed_known_in_2026_10_20_farmana_reserve_audit"
        elif exp_status_2026_10_22 == "source_page_image_display_recorded_object_scope_unresolved":
            tier = "already_present_or_exposed"
            sub_reason = "historical_inscription_image_display_recorded"
        # Tier 2: blocked_by_alias_ambiguity
        elif is_dholavira_unregistered_pool:
            tier = "blocked_by_alias_ambiguity"
            if rid == "PCF-DHV-141":
                sub_reason = "dholavira_unregistered_lipi_pool_grid_boundary_conflict_fam4277"
            elif row.get("context_join_family"):
                sub_reason = "dholavira_context_join_without_accession_crosswalk"
            else:
                sub_reason = "dholavira_unregistered_lipi_pool_no_accession_crosswalk"
        elif is_surkotada_pottery_alias_pool:
            tier = "blocked_by_alias_ambiguity"
            sub_reason = "surkotada_cisi1_four_unnumbered_potsherds_alias_pool"
        # Tier 3: certified_absent_sealed
        elif (
            cat_status == "post-catalogue"
            and insc_status == "stated"
            and absence_proof_basis in (
                "site_absent_in_lipi_and_cisi",
                "site_type_absent_in_lipi_and_cisi",
                "site_registration_exhaustive_disjoint",
                "site_type_material_exhaustive_disjoint",
            )
            and not is_secondary_possible_dup
            and plate_audit is not None
            and plate_audit["plate_verified"]
        ):
            tier = "certified_absent_sealed"
            sub_reason = f"{absence_proof_basis}__and__{plate_audit['plate_status']}"
        # Tier 4: conditionally_absent_needs_plate_check
        else:
            tier = "conditionally_absent_needs_plate_check"
            if id_status_2026_10_22 == "not_linked_in_held_register":
                if insc_status != "stated":
                    sub_reason = "verified_absent_uncertain_inscription_status"
                elif is_secondary_possible_dup:
                    sub_reason = "verified_absent_secondary_possible_duplicate_row"
                elif plate_audit and not plate_audit["is_pdf"]:
                    sub_reason = f"verified_absent_no_held_plate_pdf_{plate_audit['plate_status']}"
                elif plate_audit and not plate_audit["plate_verified"]:
                    sub_reason = f"verified_absent_plate_unverified_{plate_audit['plate_status']}"
                else:
                    sub_reason = "verified_absent_missing_resolving_check"
            elif row.get("context_join_family"):
                sub_reason = "small_site_context_join_without_identifier"
            elif insc_status != "stated":
                sub_reason = "small_site_uncertain_inscription_candidate"
            else:
                sub_reason = "small_site_candidate_needs_plate_or_registration_check"

        # Build participant-scoped exposure summary
        if tier == "certified_absent_sealed":
            fresh_for_prospective_2026_10_20 = True
            excluded_transcribers = [
                "2026-10-21 codex gpt-6.1-sol extraction runs (text/OCR screening logged in exposure-log.csv)"
            ]
        else:
            fresh_for_prospective_2026_10_20 = False
            excluded_transcribers = []

        # Metadata completeness grade (transparently distinguishing full reg vs site/type exhaustion)
        meta_fields_present = {
            "site": bool(site),
            "object_type": bool(row["object_type"]),
            "registration": not is_blank(reg),
            "findspot": not is_blank(row.get("findspot")),
            "dimensions_in_objects_csv": False,  # objects.csv intentionally withheld dimensions per 2026-10-21 blinding
        }

        certified_rows.append({
            "row_id": rid,
            "site_code": site_code,
            "site": site,
            "local_site_label": local_site,
            "object_type": row["object_type"],
            "object_class": obj_class,
            "material": row.get("material", ""),
            "catalogue_status": cat_status,
            "inscription_status": insc_status,
            "registration": reg,
            "findspot": row.get("findspot", ""),
            "primary_publication": row["primary_publication"],
            "publication_year": row.get("publication_year", ""),
            "page": row.get("page", ""),
            "pdf_page": row.get("pdf_page", ""),
            "plate_or_figure": row.get("plate_or_figure", ""),
            "possible_duplicate_of": row.get("possible_duplicate_of", ""),
            "duplicate_relation_ids": [d["relation_id"] for d in row_dups],
            "in_358_audit": rec358 is not None,
            "audit_2026_10_22_identity_status": id_status_2026_10_22,
            "audit_2026_10_22_exposure_status": exp_status_2026_10_22,
            "supported_lipi_family_ids": sorted(set(supported_fids) | direct_lipi_hits | ({FARMANA_VERIFIED_KNOWN[rid]} if rid in FARMANA_VERIFIED_KNOWN else set())),
            "unresolved_lipi_family_ids": unresolved_fids,
            "context_join_family": row.get("context_join_family", ""),
            "site_lipi_family_count": len(lipi_site_fids),
            "site_compatible_type_lipi_count": len(lipi_compat_fids),
            "mackay_marshall_hits": sorted(direct_mm_hits),
            "cisi_basic_data_hits": sorted(direct_cisi_basic_hits),
            "spent_in_bench_json": bool(supported_fids or direct_lipi_hits or rid in FARMANA_VERIFIED_KNOWN) and spent_lipi_is_spent,
            "certification_tier": tier,
            "sub_reason": sub_reason,
            "absence_proof_basis": absence_proof_basis,
            "metadata_fields_present": meta_fields_present,
            "plate_audit": plate_audit,
            "seal_eligible_for_P1_P4": (tier == "certified_absent_sealed" and obj_class == "seal"),
            "fresh_for_frozen_2026_10_20_predictions": fresh_for_prospective_2026_10_20,
            "excluded_transcribers_for_blind_shot": excluded_transcribers,
        })

    # Save PDF access log locally on D:
    with (RAW_OUT / "pdf-access-log.jsonl").open("w", encoding="utf-8") as f:
        for ev in pdf_log:
            f.write(json.dumps(ev) + "\n")

    # Save tracked fresh-cohort-v1.json and fresh-cohort-v1.csv
    (PKG / "fresh-cohort-v1.json").write_text(json.dumps(certified_rows, indent=2) + "\n", encoding="utf-8")

    csv_fields = [
        "row_id", "site_code", "site", "object_class", "object_type", "material",
        "catalogue_status", "inscription_status", "registration",
        "primary_publication", "page", "pdf_page", "plate_or_figure",
        "in_358_audit", "audit_2026_10_22_identity_status", "audit_2026_10_22_exposure_status",
        "certification_tier", "sub_reason", "absence_proof_basis",
        "site_lipi_family_count", "site_compatible_type_lipi_count",
        "supported_lipi_family_ids", "spent_in_bench_json",
        "plate_verified", "plate_status", "verified_plate_pdf_pages",
        "seal_eligible_for_P1_P4", "fresh_for_frozen_2026_10_20_predictions",
    ]
    with (PKG / "fresh-cohort-v1.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in certified_rows:
            pa = r["plate_audit"] or {}
            w.writerow({
                "row_id": r["row_id"],
                "site_code": r["site_code"],
                "site": r["site"],
                "object_class": r["object_class"],
                "object_type": r["object_type"],
                "material": r["material"],
                "catalogue_status": r["catalogue_status"],
                "inscription_status": r["inscription_status"],
                "registration": r["registration"],
                "primary_publication": r["primary_publication"],
                "page": r["page"],
                "pdf_page": r["pdf_page"],
                "plate_or_figure": r["plate_or_figure"],
                "in_358_audit": r["in_358_audit"],
                "audit_2026_10_22_identity_status": r["audit_2026_10_22_identity_status"],
                "audit_2026_10_22_exposure_status": r["audit_2026_10_22_exposure_status"],
                "certification_tier": r["certification_tier"],
                "sub_reason": r["sub_reason"],
                "absence_proof_basis": r["absence_proof_basis"] or "",
                "site_lipi_family_count": r["site_lipi_family_count"],
                "site_compatible_type_lipi_count": r["site_compatible_type_lipi_count"],
                "supported_lipi_family_ids": ";".join(r["supported_lipi_family_ids"]),
                "spent_in_bench_json": r["spent_in_bench_json"],
                "plate_verified": pa.get("plate_verified", ""),
                "plate_status": pa.get("plate_status", ""),
                "verified_plate_pdf_pages": ";".join(str(p) for p in pa.get("verified_plate_pdf_pages", [])),
                "seal_eligible_for_P1_P4": r["seal_eligible_for_P1_P4"],
                "fresh_for_frozen_2026_10_20_predictions": r["fresh_for_frozen_2026_10_20_predictions"],
            })

    # 8. Summaries and exact P1-P4 statistical power
    tier_counts = Counter(r["certification_tier"] for r in certified_rows)
    tier_counts_358 = Counter(r["certification_tier"] for r in certified_rows if r["in_358_audit"])
    tier_by_class = defaultdict(Counter)
    tier_by_site = defaultdict(Counter)
    sub_reason_counts = Counter((r["certification_tier"], r["sub_reason"]) for r in certified_rows)

    for r in certified_rows:
        tier_by_class[r["certification_tier"]][r["object_class"]] += 1
        tier_by_site[r["site"]][r["certification_tier"]] += 1

    sealed_rows = [r for r in certified_rows if r["certification_tier"] == "certified_absent_sealed"]
    sealed_seals = [r for r in sealed_rows if r["object_class"] == "seal"]
    sealed_non_seals = [r for r in sealed_rows if r["object_class"] != "seal"]

    # Power analysis for P1-P4
    pred_spec = json.loads(INPUTS["predictions_json"].open(encoding="utf-8").read())
    cal = json.loads(INPUTS["calibration_json"].open(encoding="utf-8").read())
    farmana_cov = json.loads(INPUTS["farmana_coverage"].open(encoding="utf-8").read())

    n_sealed_seals = len(sealed_seals)
    # Also compute sensitivity power for:
    # (a) certified_absent_sealed seals at 100% single-line yield (n_sealed_seals)
    # (b) certified_absent_sealed seals at 60% single-line yield (CISI 3.1 rate in PREDICTIONS.md)
    # (c) + Mitathal seal (PCF-MTL-001) once Man & Environment 35 PDF is acquired
    # (d) + lower-bound absent seals at Bhirrana (2) + Khirsara (5) once plate-checked
    # (e) minimum threshold pool n=20 (full credence weight & P1 kill active)
    # (f) n=50 (target post-catalogue / CISI 3.1 expected pool)
    n_at_60pct = max(1, int(round(n_sealed_seals * 0.60))) if n_sealed_seals else 0
    power_scenarios = {
        "certified_absent_sealed_100pct_yield": {
            "description": f"All {n_sealed_seals} certified_absent_sealed seals qualify as complete >=3-sign single-line legends",
            "n_seals": n_sealed_seals,
            "power": compute_power_for_n(n_sealed_seals, pred_spec, cal),
        },
        "certified_absent_sealed_60pct_yield": {
            "description": f"60% single-line eligibility yield (CISI 3.1 rate from PREDICTIONS.md) on {n_sealed_seals} certified_absent_sealed seals",
            "n_seals": n_at_60pct,
            "power": compute_power_for_n(n_at_60pct, pred_spec, cal),
        },
        "plus_mitathal_pdf_acquisition": {
            "description": f"Certified seals ({n_sealed_seals}) plus PCF-MTL-001 (verified absent at Mitathal; needs Man & Environment 35 PDF)",
            "n_seals": n_sealed_seals + 1,
            "power": compute_power_for_n(n_sealed_seals + 1, pred_spec, cal),
        },
        "plus_small_site_plate_checks_lower_bound": {
            "description": f"Certified seals ({n_sealed_seals}) + Mitathal (1) + lower-bound absent seals at Bhirrana (2) and Khirsara (5) after plate checks",
            "n_seals": n_sealed_seals + 8,
            "power": compute_power_for_n(n_sealed_seals + 8, pred_spec, cal),
        },
        "threshold_n20_full_weight": {
            "description": "Minimum pool size (n=20) for full credence update and active P1 kill condition in PREDICTIONS.md",
            "n_seals": 20,
            "power": compute_power_for_n(20, pred_spec, cal),
        },
        "target_n50_reference": {
            "description": "Reference expected pool size (n=50) from PREDICTIONS.md (reachable via CISI 3.1 purchase or ICIT/Dholavira crosswalk)",
            "n_seals": 50,
            "power": compute_power_for_n(50, pred_spec, cal),
        },
    }

    summary = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "protocol_sha256": input_hashes["protocol"]["sha256"],
        "reference_corpora_checked": {
            "lipi_faces": lipi_face_count,
            "lipi_families": len(lipi_families),
            "base_register_objects": len(base_reg),
            "base_register_exposure_counts": dict(Counter(v["exposure_status"] for v in base_reg.values())),
            "mackay_marshall_joins": len(mm_rows),
            "cisi_1_2_basic_data_rows": len(cisi_flags),
            "cisi_1_2_joined_to_lipi": cisi_joined_count,
            "bench_spent_splits": len(spent_data.get("splits", {})),
            "lipi_input_spent_in_bench": spent_lipi_is_spent,
        },
        "input_accounting": {
            "objects_503_total": len(objects_503),
            "reconciled_358_total": len(reconciled_358),
            "in_baseline_catalogue_not_in_358": sum(1 for r in certified_rows if not r["in_358_audit"]),
            "duplicate_relations_total": len(dup_relations),
        },
        "tier_counts_all_503": dict(tier_counts),
        "tier_counts_within_358": dict(tier_counts_358),
        "tier_by_object_class": {k: dict(v) for k, v in tier_by_class.items()},
        "tier_by_site": {k: dict(v) for k, v in sorted(tier_by_site.items())},
        "sub_reason_counts": {f"{t}::{sr}": c for (t, sr), c in sorted(sub_reason_counts.items())},
        "certified_absent_sealed_summary": {
            "total": len(sealed_rows),
            "seals": len(sealed_seals),
            "non_seals": len(sealed_non_seals),
            "by_object_class": dict(Counter(r["object_class"] for r in sealed_rows)),
            "by_site": dict(Counter(r["site"] for r in sealed_rows)),
            "seal_row_ids": [r["row_id"] for r in sealed_seals],
            "non_seal_row_ids": [r["row_id"] for r in sealed_non_seals],
            "objects": [
                {
                    "row_id": r["row_id"],
                    "site": r["site"],
                    "object_class": r["object_class"],
                    "registration": r["registration"],
                    "primary_publication": r["primary_publication"],
                    "page": r["page"],
                    "pdf_page": r["pdf_page"],
                    "plate_or_figure": r["plate_or_figure"],
                    "verified_plate_pdf_pages": r["plate_audit"]["verified_plate_pdf_pages"],
                    "plate_status": r["plate_audit"]["plate_status"],
                    "absence_proof_basis": r["absence_proof_basis"],
                    "audit_2026_10_22_exposure_status": r["audit_2026_10_22_exposure_status"],
                }
                for r in sealed_rows
            ],
        },
        "farmana_2026_10_20_reserve_cross_check": {
            "note": "Farmana 2011 marked-pottery reserve from 2026-10-20-fresh-test-collection sits outside the 503-row objects.csv (which listed only Farmana's 4 seals and 2 sealings). Kept separate so no object is double counted.",
            "farmana_2026_10_20_summary": farmana_cov,
        },
        "P1_to_P4_power_analysis": power_scenarios,
        "pdf_access_events_logged": len(pdf_log),
        "input_hashes": input_hashes,
    }

    (PKG / "summary-v1.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Console summary (strictly aggregate counts and plate-audit status)
    print("=== CERTIFICATION COMPLETE ===")
    print("All 503 rows:", dict(tier_counts))
    print("Within 358 rows:", dict(tier_counts_358))
    print("Certified absent sealed by class:", dict(Counter(r["object_class"] for r in sealed_rows)))
    print("\n=== ALL 28 ABSENT-IN-2026-10-22 ROWS PLATE AUDIT & FINAL TIER ===")
    for r in certified_rows:
        if r["audit_2026_10_22_identity_status"] == "not_linked_in_held_register":
            pa = r["plate_audit"] or {}
            print(
                f"{r['row_id']:11s} | {r['site_code']} | {r['object_class']:14s} | {r['inscription_status']:9s} | "
                f"{r['certification_tier']:38s} | plate={pa.get('plate_status', 'n/a')} "
                f"vpages={pa.get('verified_plate_pdf_pages', [])} hits={pa.get('caption_token_hits', [])}"
            )


if __name__ == "__main__":
    main()
