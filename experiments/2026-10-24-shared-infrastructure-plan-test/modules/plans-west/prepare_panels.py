"""Make attributed source crops and retain their exact parent transformations."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west")
WEB = {
    "HARP-TR54-TOP": ("harappa-tr54-top.png", "harappa-tr54-top.html", "Trench 54 top plan"),
    "HARP-TR54-DETAIL": ("harappa-tr54-detail.jpg", "harappa-tr54-detail.html", "Trench 54 detail plan"),
    "HARP-TR54-WEST-SECTION": ("harappa-tr54-west-section.jpg", "harappa-tr54-west-section.html", "Section view of walls and platforms"),
    "HARP-TR39-P2": ("harappa-tr39-period2.jpg", "harappa-tr39-period2.html", "Plan of Kot Diji phase levels"),
    "HARP-TR39-P3": ("harappa-tr39-period3.jpg", "harappa-tr39-period3.html", "Plan of Harappa phase remains"),
    "HARP-INSIDE-WALL250": ("harappa-inside-wall250.jpg", "harappa-inside-wall250.html", "Structures inside perimeter wall"),
    "HARP-MOUND-E-ET": ("harappa-mound-e-et.jpg", "harappa-mound-e-et.html", "Harappa 1993-2001 Mound E/ET plan"),
    "HARP-TR54-SECTION-AUX": ("harappa-tr54-section.jpg", "harappa-tr54-section.html", "Trench 54 section plan"),
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    freeze = HERE / "inventory-freeze.json"
    assert sha(freeze) == json.loads((HERE / "inventory-freeze.sha256.json").read_text())["sha256"]
    inv = json.loads(freeze.read_text(encoding="utf-8"))
    output = LOCAL / "crops-v1"
    output.mkdir()
    indexes = {}
    for f in sorted(LOCAL.glob("renders-index-v*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            indexes[(r["source_id"], r["pdf_page_index"])] = r
    acquired = {}
    for f in sorted(LOCAL.glob("acquisition-routes-v*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            if r["status"] == "acquired":
                acquired[Path(r["physical_path"]).name] = r
    sources = json.loads((HERE / "sources-initial.json").read_text(encoding="utf-8"))["sources"]
    for sid, (image_name, html_name, title) in WEB.items():
        a, html = acquired[image_name], acquired[html_name]
        sources.append(dict(id=sid, title=title, authors="Harappa Archaeological Research Project; slideshow by Jonathan Mark Kenoyer and Richard H. Meadow",
                            year="excavations 1995-2001; web edition accessed 24 October 2026", url=html["url"],
                            acquisition_url=a["url"], physical_path=a["physical_path"], logical_path=a["logical_path"],
                            sha256=a["sha256"], bytes=a["bytes"], caption_html_physical_path=html["physical_path"],
                            caption_html_sha256=html["sha256"], rights_status="rights-unverified", rights="Harappa.com copyright footer; local-only", new_acquisition=True,
                            role="primary excavation-project plan or section" if not sid.endswith("AUX") else "acquired auxiliary section, outside selected numerical panels"))
    source_map = {r["id"]: r for r in sources}
    panels = []
    for r in inv["selected_panels"]:
        row = dict(r)
        if r["pdf_page_index"] is not None:
            parent = indexes[(r["source_id"], r["pdf_page_index"])]
            path = Path(parent["physical_path"])
            row.update(parent_render=parent, pdf_page_index_missing_reason=None)
        else:
            a = acquired[WEB[r["source_id"]][0]]
            path = Path(a["physical_path"])
            row.update(parent_render=dict(physical_path=str(path), sha256=a["sha256"], transform_note="Untouched project-hosted source image; no PDF parent"),
                       pdf_page_index_missing_reason="The original source is a project-hosted image, not a PDF page.")
        assert sha(path) == row["parent_render"]["sha256"]
        image = Image.open(path).convert("RGB")
        crop = r["crop_pixels"] or [0, 0, image.width, image.height]
        if r["id"] == "PW-P05":
            crop = [70, 140, 1450, 1050]
            row["crop_clarification"] = "Lower crop edge extends from 1005 to 1050 solely to retain the source scale bar; recorded before numerical tracing."
        left, top, right, bottom = crop
        assert 0 <= left < right <= image.width and 0 <= top < bottom <= image.height
        w, hh = right-left, bottom-top
        crop_image = image.crop(crop)
        rotation = {"PW-P15": -90, "PW-P16": 90, "PW-P23": -90}.get(r["id"], 0)
        if rotation == 90:
            crop_image = crop_image.transpose(Image.Transpose.ROTATE_90)
            matrix = [[0, 1, -top], [-1, 0, left+w-1], [0, 0, 1]]
        elif rotation == -90:
            crop_image = crop_image.transpose(Image.Transpose.ROTATE_270)
            matrix = [[0, -1, top+hh-1], [1, 0, -left], [0, 0, 1]]
        else:
            matrix = [[1, 0, -left], [0, 1, -top], [0, 0, 1]]
        dest = output / f"{r['id']}.png"
        crop_image.save(dest)
        row.update(source_title=source_map[r["source_id"]]["title"], source_url=source_map[r["source_id"]]["url"],
                   parent_source_sha256=source_map[r["source_id"]]["sha256"], parent_image_size=[image.width, image.height],
                   crop_pixels_actual=crop, rotation_counterclockwise_degrees=rotation,
                   parent_pixel_to_crop_pixel_matrix=matrix, crop_size=[crop_image.width, crop_image.height],
                   crop_physical_path=str(dest), crop_logical_path=f"data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west/crops-v1/{dest.name}",
                   crop_sha256=sha(dest), resampling="none; integer crop and 90-degree transpose only",
                   rights_status="rights-unverified", handling="local-only source crop and all annotated derivatives",
                   modern_restoration_status="No modern restoration mask supplied for the selected drawing or photograph; no unqualified original-masonry survival score is computed.")
        panels.append(row)
    (LOCAL / "panel-crops-v1.json").write_text(json.dumps(panels,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (HERE / "sources.json").write_text(json.dumps(dict(sources=sources, new_source_images=8,new_caption_html=8,source_routes="acquisition-routes-v1.json and acquisition-routes-v2.json on D",handling="All source payloads and derivatives remain local-only."),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    clarification = dict(created_utc=datetime.now(timezone.utc).isoformat(), frozen_inventory_sha256=sha(freeze),
                         change="PW-P05 display crop lower edge extended to retain scale bar", before=[70,140,1450,1005],after=[70,140,1450,1050],
                         scope="Display crop only, before endpoint digitization. No feature target, source window, scoring rule or endpoint changed.")
    (HERE / "CROP-CLARIFICATION-01.json").write_text(json.dumps(clarification,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(crops=len(panels),sources=len(sources),new_images=8)))


if __name__ == "__main__":
    main()
