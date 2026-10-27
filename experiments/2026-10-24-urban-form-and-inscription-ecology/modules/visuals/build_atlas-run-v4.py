"""Twenty-three source-backed figures, with local-only PNG and SVG exports."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[1]
RAW = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/visuals")
RUN = BASE / "run-v3"
NAVY = "#17344D"
TEAL = "#137E83"
GOLD = "#C89127"
BRICK = "#AF5B43"
BLUE = "#4F7DA8"
LIGHT = "#E8EEF1"
PALE = "#F7F8F5"
GRAY = "#65727A"
WHITE = "#FFFFFF"
COLORS = [TEAL, BLUE, GOLD, BRICK, "#876C98"]
TOWNS = ["mohenjo-daro", "harappa", "dholavira", "lothal", "chanhu-daro", "kalibangan", "banawali", "rakhigarhi", "surkotada", "kanmer", "shikarpur", "farmana"]
DISPLAY = {t: t.replace("-", " ").title() for t in TOWNS}
DISPLAY.update({"mohenjo-daro": "Mohenjo-daro", "chanhu-daro": "Chanhudaro"})


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrap(text, width=50):
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def clean(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#B4C2C9")
    ax.tick_params(colors=NAVY)
    ax.grid(axis="x", alpha=0.16, color=GRAY)
    ax.set_axisbelow(True)


def canvas(title, subtitle="", size=(11.4, 7.2)):
    fig = plt.figure(figsize=size, facecolor=WHITE)
    title_artist = fig.text(0.055, 0.955, title, fontsize=22, color=NAVY, weight="bold", va="top")
    fig.canvas.draw()
    while title_artist.get_window_extent(fig.canvas.get_renderer()).width > fig.bbox.width * 0.89:
        title_artist.set_fontsize(title_artist.get_fontsize() - 0.5)
        fig.canvas.draw()
    if subtitle:
        fig.text(0.055, 0.902, subtitle, fontsize=11.2, color=GRAY, va="top")
    return fig


def card(ax, x, y, w, h, title, body, color=TEAL, title_size=13, body_size=11):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02", facecolor=PALE, edgecolor="#CBD5D9", linewidth=1.0, transform=ax.transAxes)
    ax.add_patch(patch)
    ax.add_patch(Rectangle((x, y + h - 0.025), w, 0.025, facecolor=color, edgecolor="none", transform=ax.transAxes))
    ax.text(x + 0.02, y + h - 0.065, title, fontsize=title_size, weight="bold", color=color, va="top", transform=ax.transAxes)
    ax.text(x + 0.02, y + h - 0.145, body, fontsize=body_size, color=NAVY, va="top", transform=ax.transAxes, linespacing=1.45)


def arrow(ax, start, end, color=TEAL, style="-|>", lw=1.8, **kwargs):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=15, color=color, linewidth=lw, zorder=5, shrinkA=0, shrinkB=0, transform=ax.transAxes, **kwargs))


class Atlas:
    def __init__(self, out):
        if not (RUN / "validation.json").exists() or load(RUN / "validation.json")["status"] != "pass":
            raise RuntimeError("Validated run-v3 is required; no fallback to failed endpoints.")
        assert (ROOT / "data/raw").resolve() == Path("D:/projects/indus_valley_script/data/raw")
        self.out = out
        self.out.mkdir(parents=True, exist_ok=False)
        self.rows = load(RUN / "observations.json")
        self.obs = {r["id"]: r for r in self.rows}
        self.towns = {t["town"]: t for t in load(RUN / "towns.json")}
        self.sources = {s.get("source_id", s.get("id")): s for s in load(RUN / "sources.json")}
        self.synthetic = load(BASE / "synthetic-v1/results.json")
        self.context = load(BASE / "modules/inscriptions/context-table-summary.json")
        self.prior = load(BASE / "modules/inscriptions/prior-results.json")
        self.figures = []
        self.text_bounds = []
        self.input_paths = [RUN / f for f in ["observations.json", "sources.json", "towns.json", "summary.json", "validation.json"]]
        self.input_paths += [BASE / "synthetic-v1/results.json", BASE / "modules/inscriptions/context-table-summary.json", BASE / "modules/inscriptions/prior-results.json", BASE / "modules/western/mohenjo-daro-residential-series.csv", BASE / "METHODS.md", BASE / "modules/inscriptions/test-design.md"]
        self.input_paths.append(BASE / "shape-comparison-v1/results.json")

    def save(self, fig, number, slug, title, caption, ids=(), kind="source-backed chart", extra_sources=(), values=None):
        missing = [oid for oid in ids if oid not in self.obs]
        if missing:
            raise KeyError(missing)
        stem = f"fig-{number:02d}-{slug}"
        fig.text(0.055, 0.035, f"{number:02d}  |  Urban form and inscription ecology  |  24 October 2026", fontsize=9.0, color=GRAY)
        fig.text(0.945, 0.035, "Source locators in figure manifest", fontsize=9.0, color=GRAY, ha="right")
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        fw, fh = fig.canvas.get_width_height()
        bounds = []
        for artist in fig.findobj(match=matplotlib.text.Text):
            if not artist.get_visible() or not artist.get_text().strip():
                continue
            bbox = artist.get_window_extent(renderer)
            if bbox.x0 < -1 or bbox.y0 < -1 or bbox.x1 > fw + 1 or bbox.y1 > fh + 1:
                bounds.append({"text": artist.get_text(), "bounds": [bbox.x0, bbox.y0, bbox.x1, bbox.y1]})
        self.text_bounds.append({"figure": number, "outside_canvas_text": bounds})
        assets = []
        for extension in ("png", "svg"):
            p = self.out / f"{stem}.{extension}"
            fig.savefig(p, dpi=300, facecolor=WHITE, metadata={"Creator": "Indus research project; matplotlib", "Title": title})
            asset = {"format": extension, "physical_path": str(p), "logical_path": "data/raw/2026-10-24-urban-form-and-inscription-ecology/visuals/" + self.out.name + "/" + p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
            if extension == "png":
                with Image.open(p) as im:
                    asset["pixels"] = list(im.size)
            assets.append(asset)
        sources = []
        for sid in dict.fromkeys(self.obs[oid]["source_id"] for oid in ids):
            source = self.sources[sid]
            sources.append({"source_id": sid, "title": source["title"], "url": source.get("url"), "sha256": source.get("sha256"), "locators": list(dict.fromkeys(self.obs[oid]["locator"] for oid in ids if self.obs[oid]["source_id"] == sid))})
        sources.extend(extra_sources)
        self.figures.append({"figure": number, "id": stem, "title": title, "kind": kind, "caption": caption, "observation_ids": list(ids), "sources": sources, "data_values": values, "assets": assets, "rights": "Project-authored chart or conceptual diagram; no source imagery reproduced", "archaeological_values_changed": False})
        plt.close(fig)

    def locations(self):
        fig = canvas("Twelve towns, several regional settings", "Inherited WGS84 index points. No modern river is used as an ancient waterway.")
        ax = fig.add_axes([0.08, 0.22, 0.55, 0.60])
        for i, town in enumerate(TOWNS, 1):
            point = self.towns[town]["axis_horizon_register"]
            x, y = point["longitude"], point["latitude"]
            offsets={8:(-16,16),12:(16,-9),9:(20,17),10:(22,-13),11:(-17,-9)}
            if i in offsets:
                ax.scatter(x,y,s=35,color=TEAL,edgecolor=WHITE,linewidth=.8,zorder=3)
                ax.annotate(str(i),(x,y),xytext=offsets[i],textcoords="offset points",ha="center",va="center",fontsize=9.5,weight="bold",color=WHITE,bbox={"boxstyle":"circle,pad=.24","fc":TEAL,"ec":WHITE},arrowprops={"arrowstyle":"-","color":GRAY,"lw":.8},zorder=4)
            else:
                ax.scatter(x, y, s=175, color=TEAL, edgecolor=WHITE, linewidth=1.4, zorder=3)
                ax.text(x, y, str(i), va="center", ha="center", color=WHITE, fontsize=10, weight="bold")
        ax.set(xlim=(66.7, 78), ylim=(21.1, 31.7), xlabel="Longitude (degrees E)", ylabel="Latitude (degrees N)")
        ax.set_aspect(1 / math.cos(math.radians(26)))
        clean(ax)
        ax = fig.add_axes([0.66, 0.16, 0.30, 0.66]); ax.axis("off")
        for i, town in enumerate(TOWNS, 1):
            ax.text(0.02, 1 - (i - 1) * 0.068, f"{i:02d}   {DISPLAY[town]}", fontsize=12, color=NAVY, va="top")
        fig.text(0.08, 0.098, "Points identify sites or image centres, with positional accuracy unreported. They are not wall survey coordinates.", fontsize=10, color=GRAY)
        values = {town: {k: self.towns[town]["axis_horizon_register"][k] for k in ["latitude", "longitude", "source_path", "json_pointer", "source_sha256"]} for town in TOWNS}
        self.save(fig, 1, "twelve-town-locations", "Twelve-town locations", "Inherited coordinates locate the twelve case towns. The map contains no inferred ancient river, boundary or wall coordinate; local positional accuracy is unreported. The point numbers retain the common town order used in the atlas.", values=values, extra_sources=[{"source_id":"AXIS-REGISTER-V5", "title":"Q-1032 town-axis register, run-v5", "url":None,"locator":"town-axis-table.json; per-town JSON pointers in data_values"}])

    def coverage(self):
        labels = ["Setting", "Chronology", "Extent", "Excavation", "Layout / access", "Buildings", "Count denominator", "Materials", "Water / drainage", "Local change", "Replanning", "Documents", "Phase joins"]
        domains = list(self.towns[TOWNS[0]]["domains"])
        codes = {"indexed-assertions": 0, "mixed-assertions-and-limits": 1, "not-indexed": 2}
        a = [[codes[self.towns[t]["domains"][d]["status"]] for d in domains] for t in TOWNS]
        fig = canvas("The source index is uneven across fields", "Reference index for 12 towns × 13 domains. Completeness is not assessed.")
        ax = fig.add_axes([0.20, 0.30, 0.73, 0.53])
        ax.imshow(a, cmap=ListedColormap([TEAL, GOLD, LIGHT]), vmin=0, vmax=2, aspect="auto")
        ax.set_xticks(range(13), labels=labels, rotation=42, ha="right", fontsize=10)
        ax.set_yticks(range(12), labels=[DISPLAY[t] for t in TOWNS], fontsize=11)
        for x in np.arange(-0.5, 13, 1): ax.axvline(x, color=WHITE, lw=1)
        for y in np.arange(-0.5, 12, 1): ax.axhline(y, color=WHITE, lw=1)
        fig.legend(handles=[Line2D([0],[0],marker="s",ls="",color=c,label=l,markersize=11) for c,l in [(TEAL,"Indexed assertion"),(GOLD,"Assertions with limits"),(LIGHT,"Not indexed in this pass")]], loc="lower center", bbox_to_anchor=(0.54,0.09), ncol=3, frameon=False, fontsize=10)
        self.save(fig,2,"source-domain-index","Source-domain reference index", "The register indexes 98 cells with assertions, 40 with assertions and limits, and 18 without indexed assertions. A blank index cell does not establish an ancient absence. Domain completeness and comparable recovery denominators remain unassessed.", values={"towns":TOWNS,"domains":domains,"codes":codes,"matrix":a,"status_counts":load(RUN/"summary.json")["town_domain_status_counts"]})

    def assertion_coverage(self):
        fig=canvas("These are source assertions, not ancient frequencies", "The three modules contribute different kinds of evidence. One Harappa–Lahoma comparison links two places.")
        ax=fig.add_axes([0.19,0.23,0.70,0.60])
        modules=["western","eastern","inscriptions"]
        counts={t:collections.Counter(r["module"] for r in self.rows if t in r.get("towns",[r["town"]])) for t in TOWNS}
        y=np.arange(len(TOWNS)); left=np.zeros(len(TOWNS))
        for m,c,label in zip(modules,[TEAL,GOLD,BLUE],["Western / southern architecture","Eastern / Gujarat architecture","Inscription activity / context"]):
            data=[counts[t][m] for t in TOWNS];ax.barh(y,data,left=left,color=c,label=label,height=.66);left+=data
        for i,n in enumerate(left):ax.text(n+0.6,i,str(int(n)),va="center",fontsize=11,color=NAVY)
        ax.set_yticks(y,[DISPLAY[t] for t in TOWNS]);ax.invert_yaxis();ax.set_xlabel("Assertion links to a town");ax.set_xlim(0,max(left)+5);clean(ax)
        ax.legend(loc="lower right",frameon=False,fontsize=9.4)
        fig.text(.19,.105,"287 unique assertions and core-town links; one also names Lahoma Lal Tibba outside the core frame. Source effort shapes totals.",fontsize=9.8,color=GRAY)
        self.save(fig,3,"assertion-coverage","Assertion coverage by module", "Town totals count source-assertion links, with no interpretation as settlement size, structure abundance or inscription density. The 287 unique assertions have 287 core-town links; one also links Lahoma Lal Tibba as a hinterland comparison outside the twelve-town frame.", values={t:dict(c) for t,c in counts.items()})

    def materials(self):
        rows=[("Kalibangan II","Domestic walls","Mud brick", "EAST-KALIBANGAN-016"),("Kalibangan II","Wet installations","Fired brick", "EAST-KALIBANGAN-016"),("Banawali II","Defences","Moulded brick; mud mortar", "EAST-BANAWALI-017"),("Banawali II","Baths and drains","Fired brick", "EAST-BANAWALI-015"),("Rakhigarhi II","Houses / wet features","Mud brick / fired brick", "EAST-RAKHIGARHI-007"),("Farmana IIA–IIB","Walls / wet features","Mud brick / fired brick", "EAST-FARMANA-006"),("Kanmer IIa","Enclosure","Clay core; local stone veneer", "EAST-KANMER-005"),("Kanmer IIa","House walls","Stone; fine sand and clay", "EAST-KANMER-011"),("Shikarpur I → II","Buildings","Mud brick → more local stone", "EAST-SHIKARPUR-004"),("Dholavira IV–V","Lower-town walls","Rubble / ashlar; mud mortar", "W-DHO-021"),("Mohenjo-daro","Bath waterproofing","Gypsum mortar; bitumen", "W-MD-007")]
        fig=canvas("Materials were allocated to particular functions", "Source descriptions compare components and phases. No wall-volume shares have been measured.")
        ax=fig.add_axes([.06,.15,.89,.69]);ax.axis("off")
        colxs=[0,.25,.50]; widths=[.245,.245,.50]
        for x,w,lab in zip(colxs,widths,["Town / phase","Component","Reported material"]):
            ax.add_patch(Rectangle((x,.94),w,.06,facecolor=NAVY,transform=ax.transAxes));ax.text(x+.012,.972,lab,va="center",color=WHITE,weight="bold",fontsize=12,transform=ax.transAxes)
        for i,(town,feature,material,oid) in enumerate(rows):
            y=.94-(i+1)*.077
            ax.add_patch(Rectangle((0,y),1,.075,facecolor=PALE if i%2==0 else WHITE,transform=ax.transAxes))
            for x,txt in zip(colxs,[town,feature,material]):ax.text(x+.012,y+.038,txt,va="center",fontsize=10.7,color=NAVY,transform=ax.transAxes)
        ids=[r[3] for r in rows]+["EAST-SHIKARPUR-005"]
        self.save(fig,4,"materials-by-function","Materials by function", "Material allocation differs by component and period. Mud brick, fired brick and stone coexist within towns; the entries are reported examples, not town-wide proportions or a complete materials inventory.",ids,values=[{"town_phase":r[0],"component":r[1],"material":r[2],"observation_id":r[3]} for r in rows])

    def change_matrix(self):
        mapping={
          "mohenjo-daro":[["W-MD-011"],[],[],[],[]],
          "harappa":[["W-HAR-014","W-HAR-015"],[],[],["W-HAR-014"],[]],
          "dholavira":[["W-DHO-011","W-DHO-013"],["W-DHO-015"],["W-DHO-024"],["W-DHO-008","W-DHO-026"],["W-DHO-024"]],
          "lothal":[["W-LOT-003"],["W-LOT-007"],["W-LOT-009"],["W-LOT-003"],["W-LOT-014"]],
          "chanhu-daro":[[],["W-CHD-005"],[],[],[]],
          "kalibangan":[["EAST-KALIBANGAN-007"],["EAST-KALIBANGAN-006","EAST-KALIBANGAN-014"],["EAST-KALIBANGAN-014"],["EAST-KALIBANGAN-003"],[]],
          "banawali":[["EAST-BANAWALI-005"],["EAST-BANAWALI-007"],[],["EAST-BANAWALI-004"],["EAST-BANAWALI-005"]],
          "rakhigarhi":[["EAST-RAKHIGARHI-005"],["EAST-RAKHIGARHI-008"],[],["EAST-RAKHIGARHI-009"],[]],
          "surkotada":[["EAST-SURKOTADA-005"],["EAST-SURKOTADA-003"],["EAST-SURKOTADA-014"],["EAST-SURKOTADA-013"],["EAST-SURKOTADA-004","EAST-SURKOTADA-014"]],
          "kanmer":[["EAST-KANMER-004"],["EAST-KANMER-012"],["EAST-KANMER-012"],["EAST-KANMER-014"],["EAST-KANMER-012"]],
          "shikarpur":[[],["EAST-SHIKARPUR-006"],[],["EAST-SHIKARPUR-007"],[]],
          "farmana":[["EAST-FARMANA-007"],["EAST-FARMANA-007"],["EAST-FARMANA-009","EAST-FARMANA-010","EAST-FARMANA-011"],[],["EAST-FARMANA-009","EAST-FARMANA-010","EAST-FARMANA-011"]]}
        cols=["Rearrangement /\nregularization","Retained /\nreused framework","Space occupied /\npassage blocked","Enclosure\nchange","Access /\nroute changed"]
        fig=canvas("Town histories combine different kinds of change", "Selected source examples, not comparable rates. Each filled cell refers to named assertions.")
        ax=fig.add_axes([.20,.20,.73,.58]);a=np.array([[bool(x) for x in mapping[t]] for t in TOWNS]);ax.imshow(a,cmap=ListedColormap([PALE,LIGHT]),vmin=0,vmax=1,aspect="auto")
        ax.set_xticks(range(5),cols,fontsize=10);ax.xaxis.tick_top();ax.set_yticks(range(12),[DISPLAY[t] for t in TOWNS],fontsize=11)
        for i,t in enumerate(TOWNS):
            for j,ids in enumerate(mapping[t]):
                txt=" / ".join(x.split("-")[-1] for x in ids) if ids else "—"
                ax.text(j,i,txt,ha="center",va="center",fontsize=10,color=TEAL if ids else "#A8B2B8",weight="bold" if ids else "normal")
        for x in np.arange(-.5,5,1):ax.axvline(x,color=WHITE,lw=2)
        for y in np.arange(-.5,12,1):ax.axhline(y,color=WHITE,lw=2)
        fig.text(.20,.115,"Cells show assertion-number suffixes. Full IDs, phases and locators are preserved in the manifest. — = no example selected.",fontsize=9.8,color=GRAY)
        ids=list(dict.fromkeys(oid for cells in mapping.values() for cell in cells for oid in cell))
        self.save(fig,5,"planning-change-matrix","Selected change and retention relations", "This manually selected reference matrix links change categories to specific assertions. A town may combine several processes at different dates and scales. Cell suffixes refer to the full assertion IDs in the manifest; an empty selection is not an ancient absence or a completeness claim.",ids,values={"columns":cols,"selected_assertions":mapping,"classification":"project-authored reference selection; no rate or similarity statistic"})

    def dholavira_timeline(self):
        ids=[f"W-DHO-{i:03d}" for i in range(33,40)]
        bounds=[]
        for oid in ids:
            r=self.obs[oid];bounds.append((r["phase"],r.get("start_bce"),r.get("end_bce")))
        if any(a is None or b is None for _,a,b in bounds):
            duration={r["observation_id"]:r for r in load(RUN/"duration-spans.json")}
            bounds=[(self.obs[oid]["phase"],duration[oid]["start_bce"],duration[oid]["end_bce"]) for oid in ids]
        fig=canvas("Dholavira's stages are separated by interruptions", "Approximate source chronology. These are model bounds, not new construction dates.")
        ax=fig.add_axes([.235,.23,.67,.59]);labels=[]
        notes=["First enclosed nucleus","Inward addition; northern housing","Clearance; castle, bailey and enlarged town","Urban framework maintained","Street occupation; later changes","Contraction and reuse","Circular houses after a long gap"]
        for i,((phase,start,end),note) in enumerate(zip(bounds,notes)):
            ax.barh(i,start-end,left=end,height=.56,color=COLORS[i%len(COLORS)],alpha=.9)
            labels.append(f"{phase}\n{start}–{end} BCE")
        ax.set_yticks(range(7),labels,fontsize=10.5);ax.invert_yaxis();ax.set_xlim(3100,1370);ax.set_xticks([3000,2800,2600,2400,2200,2000,1800,1600,1400]);ax.set_xlabel("BCE, source's approximate scheme (older → younger)");clean(ax)
        for lo,hi,txt in [(1950,2000,"short gap"),(1500,1800,"longer gap")]:
            ax.axvspan(lo,hi,color=GOLD,alpha=.10);ax.text((lo+hi)/2,2.5,txt,ha="center",color=BRICK,fontsize=9,rotation=90,va="center")
        fig.text(.08,.105,"The empty intervals follow the published stage bounds. Their durations are not independently dated hiatus estimates.",fontsize=10,color=GRAY)
        self.save(fig,6,"dholavira-stage-timeline","Dholavira stage chronology", "Seven approximate stage intervals from the preliminary report retain the short and longer interruptions between its stages. The plot does not add their endpoints into one continuous occupation duration and supplies no new wall or sample date.",ids,values={"bounds":bounds,"chronology_status":"approximate source model","continuity_assumed":False})

    def banawali(self):
        fig=canvas("Banawali: enclosure and replanning followed settlement", "A source sequence can explain a radial plan without treating radial form as unplanned.")
        ax=fig.add_axes([.055,.18,.89,.65]);ax.axis("off")
        stages=[("IA","Open village","Sun-dried brick\nNo enclosure reported"),("IB","Boundary added","Wall reinforced inside\nand widened outside"),("IC","Housing cleared","New bipartite town\nRadial lower-town streets"),("II","Outline retained","Houses rebuilt through\nsix or more phases")]
        for i,(phase,title,body) in enumerate(stages):
            x=.015+i*.252
            card(ax,x,.31,.225,.53,phase+"  |  "+title,body,COLORS[i],title_size=11.2,body_size=11)
            if i<3:arrow(ax,(x+.232,.57),(x+.255,.57),color=GRAY)
        ax.text(.03,.14,"Changed:",color=BRICK,fontsize=12,weight="bold");ax.text(.17,.14,"houses, enclosure width and street arrangement",fontsize=12,color=NAVY)
        ax.text(.03,.05,"Retained:",color=TEAL,fontsize=12,weight="bold");ax.text(.17,.05,"the curving inherited boundary and later town outline",fontsize=12,color=NAVY)
        ids=[f"EAST-BANAWALI-{i:03d}" for i in [2,3,4,5,6,7,8,11]]
        self.save(fig,7,"banawali-phase-sequence","Banawali building sequence", "Conceptual flow of the excavator's IA, IB, IC and II sequence. Housing clearance and a new bipartite/radial arrangement are assigned to IC, followed by rebuilding within the inherited outline. This is a sequence diagram, with no measured plan geometry.",ids,kind="source-backed conceptual sequence",values={"stages":stages})

    def kanmer(self):
        fig=canvas("Kanmer: open space filled while direction persisted", "Illustrative geometry, not an excavation plan. IIa → IIb is a reported stratigraphic relation.")
        ax=fig.add_axes([.055,.18,.89,.65]);ax.axis("off");ax.set(xlim=(0,1),ylim=(0,1))
        for i,(phase,fill) in enumerate([("IIa: partly exposed open space",False),("IIb: buildings occupy the space",True)]):
            x=.03+i*.49
            ax.add_patch(Rectangle((x,.31),.42,.46,fill=False,edgecolor=NAVY,lw=2,transform=ax.transAxes))
            for xx,yy,ww,hh in [(.02,.02,.11,.15),(.02,.27,.11,.17),(.28,.02,.12,.18),(.28,.27,.12,.17)]:
                ax.add_patch(Rectangle((x+xx,.31+yy),ww,hh,facecolor=LIGHT,edgecolor=NAVY,lw=1,transform=ax.transAxes))
            if fill:
                ax.add_patch(Rectangle((x+.15,.40),.11,.23,facecolor=GOLD,edgecolor=NAVY,lw=1,transform=ax.transAxes));ax.plot([x+.15,x+.26],[.51,.51],color=NAVY,transform=ax.transAxes)
            else:ax.text(x+.21,.53,"Open\narea",ha="center",va="center",fontsize=12,color=TEAL,transform=ax.transAxes)
            ax.text(x+.21,.83,phase,ha="center",fontsize=11.8,color=NAVY,weight="bold",transform=ax.transAxes)
        arrow(ax,(.455,.54),(.515,.54),color=TEAL)
        ax.text(.03,.16,"IIa exposure: 7 × 5 m in the open space, partly exposed",fontsize=12,color=NAVY)
        ax.text(.03,.055,"The IIb report preserves orientation while structures widen. The source does not decide how quickly infill occurred.",fontsize=11,color=GRAY)
        ids=["EAST-KANMER-008","EAST-KANMER-009","EAST-KANMER-010","EAST-KANMER-012","EAST-KANMER-013"]
        self.save(fig,8,"kanmer-retention-and-infill","Kanmer retained orientation and occupied open space", "The diagram illustrates the distinction between a retained directional framework and the occupation of previously open space. Rectangles are schematic and unscaled; they are not traced rooms. The published 7×5 m refers to the partly exposed IIa open area, not the whole courtyard or the drawn box.",ids,kind="source-backed conceptual diagram",values={"partly_exposed_open_space_m":[7,5],"IIb_orientation":"retained","geometry":"illustrative and unscaled"})

    def farmana(self):
        fig=canvas("Farmana records three named losses of circulation space", "Illustrative before-and-after strips. These are three distinct locations, not one reconstructed street.")
        ax=fig.add_axes([.055,.16,.89,.68]);ax.axis("off")
        examples=[("East Area Lane 1","Bathing platform","1.50 × 1.43 m","EAST-FARMANA-009"),("East Area Lane 2","Structure 11A added","Earlier width 1.90 m","EAST-FARMANA-010"),("Street at Structure 3I","External strengthening wall","0.55 m thick; 2.10 m exposed","EAST-FARMANA-011")]
        for i,(name,addition,size,oid) in enumerate(examples):
            y=.68-i*.27
            ax.text(.01,y+.14,name,fontsize=12,weight="bold",color=NAVY)
            ax.add_patch(Rectangle((.01,y),.20,.09,facecolor=LIGHT,transform=ax.transAxes))
            ax.text(.11,y+.045,"Earlier route",ha="center",va="center",fontsize=10,color=NAVY)
            arrow(ax,(.22,y+.045),(.28,y+.045),color=GRAY)
            ax.add_patch(Rectangle((.29,y),.20,.09,facecolor=LIGHT,transform=ax.transAxes))
            ax.add_patch(Rectangle((.29,y),.08,.09,facecolor=GOLD,transform=ax.transAxes))
            ax.text(.54,y+.075,addition,fontsize=12,color=BRICK,weight="bold")
            ax.text(.54,y+.005,size,fontsize=11.2,color=NAVY)
        fig.text(.07,.105,"The figures give reported dimensions. Drawing widths and positions are illustrative, with no shared north reference or scale.",fontsize=10,color=GRAY)
        self.save(fig,9,"farmana-named-encroachments","Farmana named circulation changes", "Source-local examples preserve a bathing platform in East Area Lane 1, Structure 11A in East Area Lane 2 and an external strengthening wall at Structure 3I. Their broad IIA–IIB framework was retained. Schematics show the process, not actual plan geometry or a measured before/after width for one street.",[e[3] for e in examples]+["EAST-FARMANA-007"],kind="source-backed conceptual diagram",values={"examples":examples,"drawn_geometry":"unscaled"})

    def md_residences(self):
        with (BASE/"modules/western/mohenjo-daro-residential-series.csv").open(encoding="utf8",newline="") as f: rows=list(csv.DictReader(f))
        fig=canvas("One Mohenjo-daro neighbourhood changed through rebuilding", "DK-G South residence samples. Published century labels are model-assigned, not measured dates.")
        xs=np.arange(5); phases=[r["phase"].replace("Intermediate ","Int.\n").replace("Late II and I","Late\nII / I").replace("Late III","Late\nIII") for r in rows]
        for j,(field,title,unit,col) in enumerate([("gini","Gini coefficient","",TEAL),("median_area_m2","Median area (m²)","",BLUE),("n","Residence samples (n)","",GOLD)]):
            ax=fig.add_axes([.08+j*.30,.25,.255,.53]); y=[float(r[field]) for r in rows]
            if field=="n":ax.bar(xs,y,color=col,width=.6)
            else:ax.plot(xs,y,"o-",color=col,lw=2.5,markersize=7)
            for x,value in zip(xs,y):ax.annotate(f"{value:g}",(x,value),xytext=(0,8),textcoords="offset points",ha="center",color=col,fontsize=10.8,weight="bold")
            ax.set_title(title,fontsize=12,color=NAVY,pad=16);ax.set_xticks(xs,phases,fontsize=8.9);ax.set_ylabel(unit,fontsize=10);clean(ax)
            ax.set_ylim((0,.46) if field=="gini" else (0,max(y)*1.3))
        fig.text(.08,.12,"Int. = Intermediate. Century labels 2500→2100 BCE are model-assigned; recurrent buildings make phase counts non-additive.",fontsize=10,color=GRAY)
        ids=[f"W-MD-{i:03d}" for i in range(12,27)]
        self.save(fig,10,"mohenjo-daro-residential-series","Mohenjo-daro residential series", "Published DK-G South residence-area Gini, medians and sample sizes across five reconstructed relative phases. Century labels are assigned by the source's model, without independent phase dates. Buildings may recur across phases, so the five sample sizes are not an additive household census.",ids,values=rows)

    def denominators(self):
        fig=canvas("A block, a room and a well estimate are different units", "Selected published quantities retain their exposure and reconstruction denominators.")
        ax=fig.add_axes([.055,.12,.89,.73]);ax.axis("off")
        specs=[("≈17","Housing blocks","Dholavira Lower Town","Excavated blocks; each can contain several buildings",["W-DHO-018"]),("14","Small streets","Dholavira Lower Town","Reported exposed network, Stages IV–V",["W-DHO-017"]),("7","Blocks","Lothal","Traced blocks; cumulative publication coverage",["W-LOT-004"]),("12","Cells in one building","Chanhudaro Building A","Rooms in one complex, not twelve houses",["W-CHD-011"]),("≥700","Estimated wells","Mohenjo-daro","Extrapolation to unexcavated built-up area",["W-MD-003"]),("10","Blocks in one structure","Rakhigarhi RGR2","Excavator's granary interpretation kept separate",["EAST-RAKHIGARHI-010"]),("9","Labelled rooms","Farmana Complex 4","Building continues into unexcavated ground",["EAST-FARMANA-014"]),("9","Trenches, 5 × 5 m each","Shikarpur 2007–08","Nominal trench layout; exposure changes with depth",["EAST-SHIKARPUR-003"])]
        for i,(n,unit,town,limit,ids) in enumerate(specs):
            col=i%2;row=i//2;x=.01+col*.50;y=.78-row*.245
            ax.add_patch(Rectangle((x,y),.475,.215,facecolor=PALE,edgecolor="#D5DFE3",transform=ax.transAxes))
            ax.text(x+.018,y+.155,n,fontsize=26,weight="bold",color=COLORS[col],va="center")
            ax.text(x+.14,y+.165,unit,fontsize=11.4,weight="bold",color=NAVY,va="center")
            ax.text(x+.14,y+.105,town,fontsize=10.5,color=GRAY,va="center")
            ax.text(x+.018,y+.045,wrap(limit,60),fontsize=9.4,color=NAVY,va="center")
        self.save(fig,11,"count-denominator-comparison","Structure-count denominators", "Selected source counts describe different units and opportunities for observation. These quantities are not ranked as town sizes and are not divided by unrelated whole-site areas. The labels retain partial exposures and extrapolations.",list(dict.fromkeys(oid for s in specs for oid in s[4])),values={"quantities":[list(s[:4]) for s in specs]})

    def dholavira_stages(self):
        raw=self.context["stage_raw_counts"]
        groups=[("III A",raw["III A"]),("IV",raw["IV"]),("V",raw["V"]),("VI",raw["VI"]),("Other labels",225-sum(raw[k] for k in ["III A","IV","V","VI"]))]
        detail=[("Blank cell",raw["[blank]"]),("Dash",raw["-"]),("Question mark",raw["?"]),("Indeterminate / Unst",raw["Indeter minate"]+raw["Unst"]),("Mixed IV/V",sum(v for k,v in raw.items() if k.replace(" ","").startswith("IV/V"))),("Qualified V",raw["V !"]+raw["V ?"]),("Mixed V/VI",raw["V/ VI"]),("Qualified VI",raw["VI !"]+raw["VI- ? Mispla ced"])]
        assert sum(x[1] for x in groups)==225 and sum(x[1] for x in detail)==63
        fig=canvas("Dholavira's 225 context rows retain their stage labels", "Printed seal-context rows include noninscribed and damaged objects. They are not a new physical-object census.")
        ax=fig.add_axes([.10,.22,.39,.58]);labels=[x[0] for x in groups];vals=[x[1] for x in groups]
        ax.barh(range(5),vals,color=[BLUE,TEAL,TEAL,TEAL,GOLD],height=.65)
        ax.set_yticks(range(5),labels);ax.invert_yaxis();ax.set_xlim(0,76);ax.set_xlabel("Printed rows");clean(ax)
        for i,v in enumerate(vals):ax.text(v+1,i,str(v),va="center",fontsize=13,weight="bold",color=NAVY)
        ax=fig.add_axes([.57,.22,.34,.58]);ax.axis("off")
        ax.text(0,1,"The 63 other labels",fontsize=14,weight="bold",color=GOLD,va="top")
        for i,(name,n) in enumerate(detail):
            y=.87-i*.106;ax.text(0,y,name,fontsize=11.3,color=NAVY,va="center");ax.text(1,y,str(n),fontsize=12,weight="bold",color=GOLD,ha="right",va="center")
        fig.text(.10,.12,"The sole III A row is accession 13204, inscription = Nil. Recovery stage does not identify manufacture or use date.",fontsize=10,color=GRAY)
        self.save(fig,12,"dholavira-context-stage-labels","Dholavira context-stage labels", "The complete printed 225-row population has 162 unqualified labels across III A, IV, V and VI, with 63 missing, mixed or qualified labels. Raw stage strings remain in the source extraction. Counts describe the publication's table and have no phase-exposure denominator.",["INS-008","INS-009","INS-010"],values={"five_groups":groups,"other_label_groups":detail,"all_raw_labels":raw,"denominator":225})

    def dholavira_inscription_flags(self):
        raw=self.context["inscription_raw_counts"]
        groups=[("Yes / Yes,",raw["Yes"]+raw["Yes,"]),("Nil",raw["Nil"]),("Missing",raw["Missing"]),("Blank",raw["[blank]"]),("Other / qualified",sum(v for k,v in raw.items() if k not in ["Yes","Yes,","Nil","Missing","[blank]"]))]
        fig=canvas("An inscription flag is not a count of readable texts", "Dholavira context table: the 225 rows preserve explicit absence, damage and uncertainty separately.")
        ax=fig.add_axes([.18,.24,.55,.55]);y=np.arange(5);vals=[v for _,v in groups]
        ax.barh(y,vals,color=[TEAL,BLUE,BRICK,LIGHT,GOLD],height=.65);ax.set_yticks(y,[n for n,_ in groups]);ax.invert_yaxis();ax.set_xlabel("Printed rows");ax.set_xlim(0,160);clean(ax)
        for i,v in enumerate(vals):ax.text(v+2,i,str(v),va="center",fontsize=13,color=NAVY,weight="bold")
        ax=fig.add_axes([.78,.24,.18,.55]);ax.axis("off");ax.text(0,1,"Raw qualified flags",fontsize=12,color=GOLD,weight="bold",va="top")
        others=[(k,v) for k,v in raw.items() if k not in ["Yes","Yes,","Nil","Missing","[blank]"]]
        for i,(label,n) in enumerate(others):ax.text(0,.85-i*.13,f"{label}: {n}",fontsize=10.7,color=NAVY,va="top")
        fig.text(.18,.12,"139 explicit Yes rows. Catalogue flags preserve what was reported; no new sign reading or object identity adjudication.",fontsize=10,color=GRAY)
        self.save(fig,13,"dholavira-inscription-flags","Dholavira inscription-status flags", "The inscription column explicitly flags 139 rows Yes or Yes,. Nil, Missing, blank cells and qualified flags retain separate meanings. This is neither a legibility census nor a frequency estimate of writing in the ancient town.",["INS-008","INS-011"],values={"groups":groups,"raw_flags":raw,"denominator":225})

    def harappa_clump(self):
        values=np.array([[5,0,1],[7,2,0],[4,0,3]])
        fig=canvas("The Harappa clump joins several reported cutting hands", "H-2218–H-2239: 22 incised steatite tablets in secondary debris outside wall 296.")
        ax=fig.add_axes([.13,.28,.49,.48]);ax.imshow(values,cmap="Blues",vmin=0,vmax=7,aspect="auto")
        ax.set_xticks(range(3),["Clump\n16 objects","Nearby\n2 objects","Scattered\n4 objects"],fontsize=12)
        ax.set_yticks(range(3),["Hand 1","Hand 2","Hand 3"],fontsize=12)
        for i in range(3):
            for j in range(3):ax.text(j,i,str(values[i,j]),ha="center",va="center",fontsize=22,weight="bold",color=WHITE if values[i,j]>=4 else NAVY)
        for v in [.5,1.5]:ax.axvline(v,color=WHITE,lw=3);ax.axhline(v,color=WHITE,lw=3)
        ax=fig.add_axes([.68,.25,.27,.53]);ax.axis("off")
        ax.text(0,1,"Manufacture",fontsize=15,color=TEAL,weight="bold",va="top")
        ax.text(0,.88,"At least three cutting hands\nunder the excavators'\nmicroscopic attribution.",fontsize=11.5,color=NAVY,va="top",linespacing=1.5)
        ax.text(0,.58,"Disposal",fontsize=15,color=TEAL,weight="bold",va="top")
        ax.text(0,.46,"Clump members share\na recovery context.\nThree hands do not establish\nthree workshops.",fontsize=11.5,color=NAVY,va="top",linespacing=1.5)
        fig.text(.13,.12,"Late 3B dates deposition relative to wall and fill. Attachment, contents, quantity and actual use remain unreported.",fontsize=10,color=GRAY)
        self.save(fig,14,"harappa-tablet-clump","Harappa tablet manufacturing and discard groups", "The source attributes at least three cutting hands to 22 named incised-steatite tablets. Sixteen were found together, two nearby and four scattered. Manufacturing groups, object counts and depositional independence remain separate; no physical-use function is established by the matrix.",["INS-021","INS-022","INS-023"],values={"matrix":values.tolist(),"rows":["reported hand 1","reported hand 2","reported hand 3"],"columns":["clump","nearby","scattered"],"total_objects":22})

    def lothal_populations(self):
        fig=canvas("Lothal's sealing numbers describe unreconciled populations", "The accounts must retain their publication, deposit and inventory scope.")
        ax=fig.add_axes([.055,.15,.89,.68]);ax.axis("off")
        specs=[(.01,"1979 · Volume I","65","Successive layers by\nblocks 41i–41j", "One named passage\ndeposit account",TEAL),(.345,"1985 · Volume II","69 of 90","Small area at south end\nof easternmost passage","Subset and total in\nthis publication",BLUE),(.68,"2005 · reanalysis","93","Studied sealing\nassemblage","Source reanalysis\npopulation",GOLD)]
        for x,title,n,where,scope,color in specs:
            card(ax,x,.34,.30,.59,title,"",color,title_size=11.2)
            ax.text(x+.15,.70,n,fontsize=31,color=color,weight="bold",ha="center",va="center")
            ax.text(x+.15,.55,where,fontsize=11.5,color=NAVY,ha="center",va="center",linespacing=1.4)
            ax.text(x+.15,.40,scope,fontsize=10.3,color=GRAY,ha="center",va="center",linespacing=1.4)
        ax.text(.5,.20,"No object-by-object reconciliation establishes an identical inventory.",ha="center",fontsize=12,color=BRICK,weight="bold")
        ax.text(.5,.09,"A separate 12-member elephant cohort is assigned to one die; it is not a count of twelve offices.",ha="center",fontsize=10.8,color=NAVY)
        self.save(fig,15,"lothal-sealing-denominators","Lothal sealing population scopes", "Volume I's 65 sealings, Volume II's 69 of 90 and the later 93-object reanalysis retain their different scopes. The inventories remain unreconciled. Twelve elephant sealings form a separate published die cohort; no count of officers, transactions or simultaneous layers follows.",["INS-035","INS-036","INS-039"],extra_sources=[{"source_id":"KM2010-MS","title":"Inscribed Objects from Harappa Excavations 1986–2007","url":"https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf","locator":"author manuscript p.7: Lothal 93 specimens"}],values={"rao1979_named_deposit":65,"rao1985_subset":69,"rao1985_total":90,"later_studied_assemblage":93,"elephant_die_group_members":12,"inventories_reconciled":False})

    def object_life(self):
        fig=canvas("Manufacture, operation and recovery have different maps", "A physical object joins these events only when its identity and context are preserved.")
        ax=fig.add_axes([.055,.16,.89,.67]);ax.axis("off")
        xs=[.01,.255,.50,.745];w=.225
        heads=["Carrier","Entry of the mark","Operation / use","Recovered context"]
        for x,head in zip(xs,heads):ax.text(x+.01,.94,head,fontsize=12,color=TEAL,weight="bold")
        rows=[("Goblet fragment","Stamped before firing","Persistent designation;\ncontents unjoined","Later sump or\nother fill"),("Clay sealing","Pressed with a seal","Cords and a\nclosure contact","Passage layers;\nheating affects survival"),("Incised tablet","Carved stone, then\nfired in some series","Operational relation\nremains unresolved","Wall-side discard;\nclump and scatter"),("Large writing","Inlaid panel or\ninscribed stone","Display / lintel\npositions reconstructed","Gate chamber /\nsecondary slab context")]
        for i,row in enumerate(rows):
            y=.68-i*.205
            for j,(x,txt) in enumerate(zip(xs,row)):
                ax.add_patch(Rectangle((x,y),w,.15,facecolor=PALE if j!=2 else LIGHT,edgecolor="#D4DFE4",transform=ax.transAxes))
                ax.text(x+w/2,y+.075,txt,ha="center",va="center",fontsize=10.7,color=NAVY,linespacing=1.4)
                if j<3:arrow(ax,(x+w+.002,y+.075),(xs[j+1]-.003,y+.075),color=GRAY,lw=1.3)
        ids=["INS-001","INS-002","INS-005","INS-021","INS-023","INS-024","INS-025","INS-026","INS-027","INS-035","INS-038"]
        self.save(fig,16,"object-life-history","Object life and archaeological recovery", "Source-backed conceptual chains distinguish when a mark was created, how a carrier functioned and where it was recovered. Persistent pre-firing marks, actual clay fastening traces, unassigned tablet use and reconstructed monumental positions require different context relations.",ids,kind="source-backed conceptual chain",values={"columns":heads,"rows":rows})

    def prior_results(self):
        fig=canvas("Earlier positives and failures constrain the urban model", "Existing populations and statistic families are examined; these figures add no fresh confirmation.")
        ax=fig.add_axes([.055,.13,.89,.72]);ax.axis("off")
        cards=[("Cross-city legend relations","13 of 16 matching sealings\nmatch only seals at other sites","Six distinct texts in the recount;\ntext, tool and package movement differ.",TEAL,"PR-02"),("Regional graphic prediction","−0.01584 bits per target\n95% interval −0.04107 to +0.00610","306 components. Adding city\nfailed the positive regional prediction.",BRICK,"PR-03"),("Ordered fish combinations","43 positive · 8 opposing · 2 ties","A structural result; the narrow\nasterism-coverage model failed.",TEAL,"PR-15"),("Household / office sign map","−0.43557 null standard deviations","The frozen 118-sign map failed;\nits meanings cannot label buildings.",BRICK,"PR-14"),("Harappa physical use","No contents joins in the\nbounded 47-entry source frame","The absence is in searched source\ncoverage, not an ancient zero.",GOLD,"PR-12"),("H-912 exact Fish comparison","3 objects · 1 text component","Physical quantity and transaction\nrelations remain unjoined.",GOLD,"PR-16")]
        for i,(title,value,scope,color,pid) in enumerate(cards):
            x=.01+(i%2)*.50;y=.67-(i//2)*.31
            ax.add_patch(FancyBboxPatch((x,y),.475,.29,boxstyle="round,pad=0.012,rounding_size=0.02",facecolor=PALE,edgecolor="#CBD5D9",transform=ax.transAxes))
            ax.add_patch(Rectangle((x,y+.265),.475,.025,facecolor=color,transform=ax.transAxes))
            ax.text(x+.02,y+.242,title,fontsize=11.3,color=color,weight="bold",va="top")
            ax.text(x+.02,y+.182,value,fontsize=11.8,color=color,weight="bold",va="top",linespacing=1.3)
            ax.text(x+.02,y+.074,scope,fontsize=9.7,color=NAVY,va="top",linespacing=1.3)
        self.save(fig,17,"prior-support-and-failures","Prior results and limitations", "The matrix preserves positive structural or locality observations beside failed predictions and missing physical joins. It draws from pinned prior outputs, with their original exposure status; no shared corpus is re-split or called fresh.",kind="prior-result comparison",extra_sources=[{"source_id":pid,"title":title,"url":None,"locator":next(r["exact_output"] for r in self.prior["results"] if r["id"]==pid)} for title,_,_,_,pid in cards],values={"cards":[list(x) for x in cards]})

    def synthetic_orientation(self):
        fig=canvas("Two ordered districts can blur a town-wide direction score", "SYNTHETIC METHOD DEMONSTRATION · generated angles, known districts, no ancient plan.")
        data=self.synthetic["orientation"]
        if isinstance(data,dict):
            # Keep schema failures explicit instead of guessing the data population.
            raise TypeError("Expected a list of orientation demonstrations")
        ax=fig.add_axes([.08,.20,.43,.59]);offsets=[r["district_offset_degrees"] for r in data]
        ax.plot(offsets,[r["global_q4"] for r in data],"o-",color=BRICK,lw=2.8,markersize=8,label="Town-wide Q4")
        ax.plot(offsets,[1]*len(data),"s--",color=TEAL,lw=2,markersize=6,label="Within each district Q4")
        ax.set(xlim=(-2,47),ylim=(-.05,1.15),xlabel="Angle between the two generated grids (degrees)",ylabel="Fourfold orientation order Q4");ax.set_xticks([0,15,30,45]);clean(ax);ax.legend(frameon=False,fontsize=10,loc="lower left")
        ax=fig.add_axes([.58,.22,.35,.56]);ax.set(xlim=(-1.3,1.3),ylim=(-1.3,1.3));ax.set_aspect("equal");ax.axis("off")
        for angle,color,label in [(0,TEAL,"District A"),(30,GOLD,"District B")]:
            for deg in [angle,angle+90]:
                rad=math.radians(deg);v=.85*np.array([math.cos(rad),math.sin(rad)])
                ax.plot([-v[0],v[0]],[-v[1],v[1]],color=color,lw=7,alpha=.9,solid_capstyle="round")
            ax.text(-1.1,1.15-(angle/30)*.22,label,color=color,fontsize=11,weight="bold")
        ax.text(0,-1.12,"30° between districts\nLocal Q4 = 1; pooled Q4 = 0.5",ha="center",fontsize=11,color=NAVY,linespacing=1.5)
        fig.text(.08,.105,"Q4 = |mean exp(4iθ)|. Generated right-angle pairs share a fourfold axis. The 2026 paper's clustering is not reproduced.",fontsize=10,color=GRAY)
        self.save(fig,18,"synthetic-local-global-orientation","Synthetic local and pooled orientation order", "Generated internally perfect grids retain local fourfold order Q4=1. Equal districts separated by 30° have pooled Q4=0.5, and 45° yields approximately zero. This demonstrates aggregation effects without assigning ancient town districts or implementing the 2026 paper's clustering.",kind="synthetic method demonstration",extra_sources=[{"source_id":"BARTHELEMY-BOEING-2026-V1","title":"2026 orientation-district method, version 1","url":"https://arxiv.org/abs/2609.13029v1","locator":"section III.3; project synthetic-v1/results.json"}],values=[{"offset_degrees":r["district_offset_degrees"],"global_q4":r["global_q4"],"local_q4":r["local_q4"]} for r in data])

    def sign_power(self):
        fig=canvas("Useful power needs independent comparisons", "SYNTHETIC PLANNING REFERENCE · exact one-sided sign test at nominal α = 0.025.")
        ax=fig.add_axes([.10,.22,.70,.60]);data=self.synthetic["power"]
        for color,n in zip(COLORS,[20,40,80,120]):
            rows=[r for r in data if r["independent_non_tied_pairs"]==n]
            ax.plot([r["true_positive_pair_probability"] for r in rows],[r["power"] for r in rows],"o-",color=color,lw=2.5,markersize=7,label=f"{n} independent pairs")
        ax.axhline(.8,color=GRAY,lw=1.3,ls="--");ax.text(.753,.80,"80%",va="center",color=GRAY,fontsize=11,bbox={"facecolor":WHITE,"edgecolor":"none","pad":1})
        ax.set(xlim=(.585,.765),ylim=(0,1.03),xlabel="True probability that a pair favours the prediction",ylabel="Probability of passing the exact test");ax.set_xticks([.60,.65,.70,.75]);clean(ax);ax.legend(frameon=False,loc="lower right",fontsize=11)
        fig.text(.10,.115,"Optimistic reference: town clustering, ties, shared caches, recovery bias and uncertain contexts reduce usable information.",fontsize=10,color=GRAY)
        self.save(fig,19,"exact-sign-test-power","Exact sign-test planning power", "Exact binomial power is shown for independent, non-tied pairs at one-sided nominal alpha 0.025. The discrete attained alpha is retained in the data. These are planning calculations, not estimated archaeological effect sizes or a guarantee of power for clustered towns.",kind="synthetic planning calculation",extra_sources=[{"source_id":"PROJECT-SYNTHETIC-V1","title":"Urban-study synthetic diagnostics","url":None,"locator":"synthetic-v1/results.json /power; synthetic_diagnostics.py"}],values=data)

    def rivals(self):
        fig=canvas("The same regular plan permits different institutions", "Competing models make their strongest predictions about timing, access, production and distribution.")
        ax=fig.add_axes([.055,.14,.89,.70]);ax.axis("off")
        models=[("One directing authority",TEAL,["Linked rebuilding across\nseveral neighbourhoods","Restricted production and\na city-wide issuing network","Control hierarchy survives\nmaterial and recovery checks"]),("Several negotiating groups",BLUE,["Persistent shared streets\nwith locally different rebuilding","Documentary groups cross\nsome boundaries, not all","Neighbourhood / corporate\nmodels add predictive value"]),("Convergent local solutions",GOLD,["Layout follows slope, water,\nmaterials and inherited edges","Object distributions follow\nproduction and discard","Access adds little once\nphysical constraints are modelled"])]
        for i,(title,color,lines) in enumerate(models):
            x=.01+i*.335;card(ax,x,.10,.31,.82,title,"",color,title_size=12.1)
            for j,(lab,text) in enumerate(zip(["Architecture","Documents","Deciding comparison"],lines)):
                y=.69-j*.215;ax.text(x+.02,y,lab,fontsize=10,color=color,weight="bold");ax.text(x+.02,y-.05,text,fontsize=11.1,color=NAVY,va="top",linespacing=1.45)
        self.save(fig,20,"rival-institutional-models","Institutional rivals and predictions", "Conceptual predictions compare a single directing authority, several coordinating groups and convergence under common physical constraints. Orthogonality, shared brick ratios or a common script alone cannot select among the models. Their tests require matched dated contexts and independent production evidence.",kind="prospective model comparison",extra_sources=[{"source_id":"M-SMITH-2007","title":"Form and Meaning in the Earliest Cities: A New Approach to Ancient Urban Planning","url":"https://doi.org/10.1177/1538513206293713","locator":"pp.6–8,24–30,33–40"},{"source_id":"GREEN2022","title":"Indus public goods and institutions","url":"https://doi.org/10.3389/fpos.2022.823071","locator":"sections on institutions and public goods"},{"source_id":"PROJECT-METHODS","title":"Comparing the towns through their building histories","url":None,"locator":"METHODS.md: rival accounts"}],values={"models":[[m[0],m[2]] for m in models]})

    def test_pipeline(self):
        fig=canvas("A deciding study joins walls, objects and genuinely new contexts", "A prospective workflow. The current register supplies source relations and acquisition targets.")
        ax=fig.add_axes([.055,.15,.89,.69]);ax.axis("off")
        steps=[("1","Name the episode","Join wall, floor, drain\nand dated construction"),("2","Reconstruct access","Code entrances and\nuncertain connections"),("3","Code manufacture blind","Define material groups\nwithout script outcomes"),("4","Close identities","Group aliases, fragments,\ndies and related caches"),("5","Freeze the competitors","Pin predictions, power,\nnull and joint update"),("6","Read new contexts once","Score held-out deposits;\ncheck town and cache influence")]
        for i,(n,title,body) in enumerate(steps):
            col=i%3;row=i//3;x=.01+col*.335;y=.55-row*.42
            card(ax,x,y,.31,.34,title,body,COLORS[col],title_size=11.8,body_size=11)
            ax.text(x+.278,y+.283,n,fontsize=12,weight="bold",ha="right",color=COLORS[col])
            if col<2:arrow(ax,(x+.315,y+.17),(x+.333,y+.17),color=GRAY)
        arrow(ax,(.84,.54),(.16,.48),color=GRAY,connectionstyle="arc3,rad=.05")
        ax.text(.5,.025,"A new seed on examined objects does not create a fresh population.",ha="center",fontsize=11,color=BRICK,weight="bold")
        self.save(fig,21,"deciding-test-workflow","Deciding test workflow", "The prospective sequence joins source-qualified construction episodes and reconstructed access to independently coded production groups, closes object and context dependencies, freezes all models and evaluates new contexts once. No confirmation cohort is opened by this atlas.",kind="prospective workflow",extra_sources=[{"source_id":"PROJECT-DESIGN","title":"A prospective test of urban coordination through access and documents","url":None,"locator":"modules/inscriptions/test-design.md"},{"source_id":"SHOTS-DESIGN","title":"Two conjecture shots: design","url":None,"locator":"experiments/2026-10-12-conjecture-shots/DESIGN.md"}],values={"steps":steps,"confirmation_access":False})

    def chain_readiness(self):
        fig=canvas("The remaining joins are specific enough to acquire", "Four bounded cases show where the physical chain is supported and where interpretation still enters.")
        ax=fig.add_axes([.055,.15,.89,.68]);ax.axis("off")
        headers=["Case","Identity / place","Time relation","Operation / missing link"]
        xs=[0,.24,.50,.74];widths=[.235,.255,.235,.26]
        for x,w,h in zip(xs,widths,headers):
            ax.add_patch(Rectangle((x,.91),w,.085,facecolor=NAVY,transform=ax.transAxes));ax.text(x+.012,.952,h,va="center",color=WHITE,fontsize=10.8,weight="bold",transform=ax.transAxes)
        rows=[("Dholavira\nNorth Gate panel","Ten signs recovered\nin western chamber","Stage IV use attributed;\nconstruction join unmade","Above-passage mounting\nneeds original field relation"),("Harappa\nTrench 54","Captioned tablets /\nblanks; courtyard fill","3B by source pottery;\nworking floor unresolved","Manufacture supported;\ncontroller and use unjoined"),("Harappa\n22-tablet series","Named cohort; 16 in\nsecondary clump","Late 3B deposition,\nnot manufacture date","Repeated production;\ntransaction / quantity unjoined"),("Lothal\nL-164","1864 = L-164 =\nLTH SRG 1232","Layer-by-object\njoin unresolved","Cords on flat contact;\nstopper versus box disputed")]
        for i,row in enumerate(rows):
            y=.91-(i+1)*.205
            ax.add_patch(Rectangle((0,y),1,.2,facecolor=PALE if i%2==0 else LIGHT,transform=ax.transAxes))
            for x,text in zip(xs,row):ax.text(x+.012,y+.105,text,fontsize=10.5,color=NAVY,va="center",linespacing=1.5,transform=ax.transAxes)
        ids=["W-DHO-016","INS-001","INS-002","INS-013","INS-014","INS-021","INS-023","INS-037","INS-038","INS-039"]
        self.save(fig,22,"evidence-chain-acquisition-targets","Evidence-chain acquisition targets", "Four source-qualified cases retain different unfinished relations: panel mounting and episode, production deposit and working floor, tablet manufacture and use, and sealing contact geometry and layer. A published phase attribution is distinct from a direct construction date; searched-source unknowns remain explicit.",ids,kind="source-chain comparison",values={"headers":headers,"rows":rows})

    def dimension_ratios(self):
        result=load(BASE/"shape-comparison-v1/results.json")
        assert result["passed"] and len(result["rows"])==6 and result["source_measurements_new"]==0
        rows=result["rows"]
        fig=canvas("Proportions vary among named enclosures and interiors", "Exploratory arithmetic from published metre lengths. No dimension-error model is supplied.")
        ax=fig.add_axes([.31,.23,.42,.58]);labels=["Dholavira · inner arms","Kalibangan I · enclosure","Kalibangan II · citadel","Kalibangan II · lower city","Surkotada IC · citadel interior","Surkotada IC · annexe interior"]
        for i,r in enumerate(rows):
            value=r["longer_to_shorter_ratio"];color=BLUE if i==0 else GOLD if i<4 else TEAL
            ax.plot([1,value],[i,i],color=color,lw=2.3,alpha=.5)
            ax.scatter([value],[i],s=85,color=color,zorder=3)
            ax.annotate(f"{value:.2f}",(value,i),xytext=(8,0),textcoords="offset points",va="center",color=color,weight="bold",fontsize=12)
        ax.axvline(1,color=GRAY,ls="--",lw=1);ax.set_yticks(range(6),labels,fontsize=10.6);ax.set_ylim(5.5,-.5);ax.set_xlim(.96,2.16);ax.set_xlabel("Longer length / shorter length");clean(ax)
        ax=fig.add_axes([.79,.23,.17,.58]);ax.axis("off");ax.text(0,1.08,"Source lengths (m)",fontsize=11,color=NAVY,weight="bold")
        for i,r in enumerate(rows):
            dims=r["dimensions_m"];ax.text(0,1-(i+.5)/6,f"{dims[0]:g} × {dims[1]:g}",fontsize=11.4,color=NAVY,va="center")
        fig.text(.08,.125,"Six architectural parts in three towns. Dholavira's southeast corner is unconfirmed; Kalibangan I retains a scan/HTML discrepancy.",fontsize=9.7,color=GRAY)
        fig.text(.08,.085,"Dots show calculated ratios, with no error bars because measurement uncertainty is unreported. Canonical intent is untested.",fontsize=9.7,color=GRAY)
        self.save(fig,23,"named-part-dimension-ratios","Named-part dimension ratios", "Six exploratory longer-to-shorter ratios use paired published enclosure-arm or interior lengths. These are architectural parts in three towns, not six whole-town measurements. No uncertainty model or inference of intentional canonical proportions is supplied. Dholavira's southeast corner and the Kalibangan I scan-versus-HTML dimension discrepancy remain explicit.",[r["observation_id"] for r in rows],values=rows)

    def assemble(self):
        methods=[self.locations,self.coverage,self.assertion_coverage,self.materials,self.change_matrix,self.dholavira_timeline,self.banawali,self.kanmer,self.farmana,self.md_residences,self.denominators,self.dholavira_stages,self.dholavira_inscription_flags,self.harappa_clump,self.lothal_populations,self.object_life,self.prior_results,self.synthetic_orientation,self.sign_power,self.rivals,self.test_pipeline,self.chain_readiness,self.dimension_ratios]
        for method in methods:
            method()
            print("rendered",len(self.figures),self.figures[-1]["id"],flush=True)
        self.contact_sheets()
        result={"schema_version":"1.0","data_endpoint":"run-v3","figures":self.figures,"figure_count":len(self.figures),"input_manifest":[{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in self.input_paths],"output_root":str(self.out),"code_sha256":sha(Path(__file__)),"third_party_images_reproduced":0,"new_archaeological_measurements":0,"confirmation_access":False,"text_bounds":self.text_bounds,"selected_cover_figures":[1,5,6,9,10,18]}
        (HERE/f"manifest-{self.out.name}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        bounds=[row for row in self.text_bounds if row["outside_canvas_text"]]
        print(json.dumps({"figures":len(self.figures),"outside_text_figures":[x["figure"] for x in bounds],"out":str(self.out)}),flush=True)

    def contact_sheets(self):
        font_path=Path("C:/Windows/Fonts/arial.ttf")
        font=ImageFont.truetype(str(font_path),18) if font_path.exists() else ImageFont.load_default()
        selections=[("contact-sheet-all.jpg",self.figures,3,650),("selected-cover-contact.jpg",[r for r in self.figures if r["figure"] in [1,5,6,9,10,18]],3,850)]
        for name,figures,cols,w in selections:
            h=round(w*7.2/11.4);rh=h+45;rows=math.ceil(len(figures)/cols)
            sheet=Image.new("RGB",(cols*w,rows*rh),WHITE);draw=ImageDraw.Draw(sheet)
            for i,row in enumerate(figures):
                path=next(a["physical_path"] for a in row["assets"] if a["format"]=="png")
                with Image.open(path) as im:
                    im=im.convert("RGB");im.thumbnail((w,h));sheet.paste(im,((i%cols)*w,(i//cols)*rh))
                draw.text(((i%cols)*w+10,(i//cols)*rh+h+5),f"{row['figure']:02d}  {row['title'][:65]}",fill=NAVY,font=font)
            sheet.save(self.out/name,quality=92)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--run",default="run-v1");args=parser.parse_args()
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"text.color":NAVY,"axes.labelcolor":NAVY,"axes.edgecolor":"#BAC8CE","svg.fonttype":"none","savefig.facecolor":WHITE,"axes.titleweight":"bold"})
    atlas=Atlas(RAW/args.run);atlas.assemble()


if __name__=="__main__":main()
