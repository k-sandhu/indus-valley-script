"""Local-only plan atlas. Source rasters and detailed crop records stay on D:."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[1]
RAW = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/figures")
CREAM, INK, TEAL, RUST = "#f8f6ef", "#17344d", "#137e83", "#af5b43"
GRAY, PALE, LIGHT, GOLD = "#637277", "#e9eeea", "#d3ddda", "#bd8d3d"
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":13, "text.color":INK,
                     "axes.labelcolor":INK, "xtick.color":INK, "ytick.color":INK,
                     "axes.facecolor":CREAM, "figure.facecolor":CREAM,
                     "axes.spines.top":False, "axes.spines.right":False,
                     "svg.fonttype":"none", "svg.hashsalt":"indus-plan-atlas-v1"})


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lines(s, width=54):
    return "\n".join(textwrap.wrap(str(s), width, break_long_words=False))


def canvas(title, subtitle="", size=(15, 9.5)):
    fig = plt.figure(figsize=size, facecolor=CREAM)
    artist = fig.text(.05,.955,title,fontsize=25,weight="bold",va="top",color=INK)
    fig.canvas.draw()
    while artist.get_window_extent(fig.canvas.get_renderer()).width > fig.bbox.width*.9:
        artist.set_fontsize(artist.get_fontsize()-.5)
        fig.canvas.draw()
    fig.text(.05,.891,subtitle,fontsize=13,color=GRAY,va="top",linespacing=1.4)
    return fig


def box(ax, x, y, w, h, heading, body, color=TEAL, fs=14):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.012,rounding_size=.012",
        transform=ax.transAxes,facecolor=PALE,edgecolor=LIGHT,linewidth=1))
    ax.add_patch(Rectangle((x,y+h-.012),w,.012,transform=ax.transAxes,color=color,lw=0))
    ax.text(x+.018,y+h-.04,heading,transform=ax.transAxes,va="top",weight="bold",fontsize=fs+1,color=color)
    ax.text(x+.018,y+h-.11,body,transform=ax.transAxes,va="top",fontsize=fs,linespacing=1.5,color=INK)


def arrow(ax, a, b, color=TEAL, dashed=False):
    ax.add_patch(FancyArrowPatch(a,b,transform=ax.transAxes,arrowstyle="-|>",mutation_scale=18,
        lw=2,color=color,linestyle="--" if dashed else "-",shrinkA=4,shrinkB=4))


class Atlas:
    def __init__(self, label, draft=False):
        self.label, self.draft = label, draft
        if not draft:
            frozen = load(HERE / "inputs-freeze-v1.json")
            for item in frozen["files"]:
                assert sha(item["physical_path"]) == item["sha256"], item["physical_path"]
            assert frozen["root_run_ready_authorized"] is True
        self.out = RAW / label
        self.out.mkdir(parents=True,exist_ok=False)
        self.figures, self.text_bounds, self.input_assets = [], [], []
        self.custom_panels = []
        self.context = load(BASE / "modules/contexts/context-joins.json")
        self.joins = {r["id"]:r for r in self.context["joins"]}
        self.dates = {r["id"]:r for r in load(BASE / "modules/contexts/date-evidence.json")["records"]}
        self.east = load(BASE / "modules/plans-east/measurements.json")
        self.em = {r["id"]:r for r in self.east["measured"]}
        self.sources = {}
        for name in ["plans-east","contexts","mohenjo-control","plans-west"]:
            registry = load(BASE/f"modules/{name}/sources.json")
            for s in registry.get("sources",[]) if isinstance(registry,dict) else registry:
                self.sources[s.get("source_id",s.get("id"))] = s
        self.context_assets = {r["id"]:r for r in load(BASE/"modules/contexts/visual-assets.json")["assets"]}
        self.east_assets = {r["id"]:r for r in load(BASE/"modules/plans-east/visual-assets.json")}
        self.md = load(BASE/"modules/mohenjo-control/measurements.json")
        self.md_assets = {r["id"]:r for r in load(BASE/"modules/mohenjo-control/plan-panels.json")["panels"]}
        self.west_assets = {r["id"]:r for r in load(BASE/"modules/plans-west/visual-assets.json")["assets"]}
        self.west_panels = {r["id"]:r for r in load(BASE/"modules/plans-west/plan-panels.json")["panels"]}
        self.west_measurements = {r["id"]:r for r in load(BASE/"modules/plans-west/measurements.json")["measurements"]}
        self.run = load(BASE/"run-v1.json")

    def source_ref(self, sid, locator):
        s = self.sources[sid]
        return {"source_id":sid,"title":s["title"],"url":s.get("url"),"locator":locator,
                "source_sha256":s.get("sha256")}

    def check_asset(self, asset):
        p = Path(asset["physical_path"])
        assert sha(p)==asset["sha256"],p
        self.input_assets.append({"physical_path":str(p),"sha256":asset["sha256"],"id":asset.get("id")})
        return p

    def crop_pdf(self, sid, index, clip, key, printed, detail):
        import fitz
        s = self.sources[sid]
        assert sha(s["physical_path"])==s["sha256"]
        d=fitz.open(s["physical_path"]);page=d[index]
        p=RAW/"source-panels-v1"/f"{key}.png";p.parent.mkdir(exist_ok=True)
        payload=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(clip)).tobytes("png")
        if p.exists():
            assert p.read_bytes()==payload,"Use a new source-panel version for changed pixels: "+str(p)
        else:p.write_bytes(payload)
        spec={"id":key,"source_id":sid,"source_parent":s["physical_path"],"source_parent_sha256":s["sha256"],
              "pdf_index0":index,"printed_page":printed,"locator":detail,"clip_pdf_points":clip,
              "render_scale":3,"rotation":page.rotation,"media_box":list(page.mediabox),"physical_path":str(p),"sha256":sha(p)}
        self.custom_panels.append(spec)
        return p

    def save(self, fig, n, slug, title, caption, towns, sources, values=None, kind="authored source-based chart"):
        stem=f"fig-{n:02d}-{slug}"
        footer=f"{n:02d}  |  Shared infrastructure and excavation contexts  |  24 October 2026"
        if self.draft:footer += "  |  DRAFT"
        fig.text(.05,.035,footer,fontsize=9,color=GRAY)
        fig.text(.95,.035,"Local-only atlas · exact sources in manifest",fontsize=9,color=GRAY,ha="right")
        fig.canvas.draw();renderer=fig.canvas.get_renderer();fw,fh=fig.canvas.get_width_height()
        bad=[]
        for artist in fig.findobj(match=matplotlib.text.Text):
            if not artist.get_visible() or not artist.get_text().strip():continue
            b=artist.get_window_extent(renderer)
            if b.x0<-.5 or b.y0<-.5 or b.x1>fw+.5 or b.y1>fh+.5:
                bad.append({"text":artist.get_text(),"bounds":[b.x0,b.y0,b.x1,b.y1]})
        self.text_bounds.append({"figure":n,"outside_canvas_text":bad})
        assets=[]
        for ext in ["png","svg"]:
            p=self.out/f"{stem}.{ext}"
            fig.savefig(p,dpi=220,facecolor=CREAM,metadata={"Creator":"Indus research project; Matplotlib"} if ext=="svg" else {"Software":"Indus research project; Matplotlib"})
            assets.append(self.asset_record(p))
        plt.close(fig)
        self.record(n,stem,title,kind,caption,towns,sources,values,assets)

    def asset_record(self,p):
        a={"format":p.suffix[1:],"physical_path":str(p),"sha256":sha(p),"bytes":p.stat().st_size}
        if p.suffix==".png":
            with Image.open(p) as im:a["pixels"]=list(im.size)
        return a

    def record(self,n,stem,title,kind,caption,towns,sources,values,assets):
        png=next(a for a in assets if a["format"]=="png")
        self.figures.append({"figure":n,"id":stem,"title":title,"kind":kind,"towns":towns,
            "caption":caption,"source_note":"; ".join(f'{s["source_id"]}: {s["locator"]}' for s in sources),
            "sources":sources,"data_values":values,"physical_path":png["physical_path"],"sha256":png["sha256"],
            "assets":assets,"local_only":True,"rights":"Local-only; source assets retain their terms; no web redistribution authorized"})

    def reuse_board(self,n,asset_id,slug,caption):
        a=self.east_assets[asset_id];p=self.check_asset(a)
        dest=self.out/f"fig-{n:02d}-{slug}.png";dest.write_bytes(p.read_bytes())
        ref=self.source_ref(a["source_id"],f'p. {a["printed_page"]}, Fig. {a["figure"]}, PDF zero index {a["pdf_zero_based_index"]}')
        self.record(n,dest.stem,a["title"],"actual source-plan measurement board",caption,[{"PE-P01":"farmana","PE-P02":"farmana","PE-P03":"kanmer","PE-P04":"banawali"}[asset_id]], [ref],
            {"source_asset_id":asset_id,"source_asset_sha256":a["sha256"],"unannotated_crop_path":a["unannotated_crop_path"],"unannotated_crop_sha256":a["unannotated_crop_sha256"]},[self.asset_record(dest)])

    def reuse_west(self,n,asset_id,slug):
        a=self.west_assets[asset_id];p=self.check_asset(a);dest=self.out/f"fig-{n:02d}-{slug}.png";dest.write_bytes(p.read_bytes())
        refs=[];panels=[]
        for src in a["source_panels"]:
            panel=self.west_panels[src["panel_id"]];panels.append(panel)
            refs.append({"source_id":src["source_id"],"title":src["title"],"url":src["url"],
                "locator":f'{src["locator"]}; PDF zero index {src["pdf_page_index"]}' if src["pdf_page_index"] is not None else src["locator"],"source_sha256":src["source_sha256"]})
        measurements=[self.west_measurements[i] for i in a["measurement_ids"]]
        phases="; ".join(dict.fromkeys(p["phase"] for p in panels))
        north=" ".join(dict.fromkeys(p["north_reference"] for p in panels))
        uncertainty=" Local metre bounds are endpoint-reading sensitivity; original survey, compilation and scan errors remain unknown." if measurements else " No new metre dimension is inferred from this board."
        caption=a["caption"]+" Phase scope: "+phases+". North: "+north+uncertainty
        values={"source_asset_id":asset_id,"source_asset_sha256":a["sha256"],"source_panels":[{k:p[k] for k in ["id","phase","panel_class","north_reference","crop_physical_path","crop_sha256","rotation_counterclockwise_degrees"]} for p in panels],
                "measurements":measurements,"registration_id":a.get("registration_id")}
        if a.get("registration_id"):values["registration"]=self.run["grid_registration"]
        self.record(n,dest.stem,a["title"],"actual source-plan measurement board",caption,list(dict.fromkeys(p["town"] for p in panels)),refs,values,[self.asset_record(dest)])

    def reuse_mohenjo(self,n,mid,slug):
        a=self.md_assets[mid];p=self.check_asset(a);dest=self.out/f"fig-{n:02d}-{slug}.png";dest.write_bytes(p.read_bytes())
        r=next(r for r in self.md["rows"] if r["id"]==mid)
        caption=f'MACKAY-VOL2, plate {r["plate"]}, PDF zero index {r["pdf_index0"]}, {r["phase_raw"]}. The original plan and magnified source banks show a local horizontal First Street chord opposite Block 5. Calibration uses the printed 0–50 feet bar, excluding its negative subdivided extension, and the declared 0.3048 m/ft conversion. The reading is {r["estimate_m"]:.2f} m, with {r["reading_lower_m"]:.2f}–{r["reading_upper_m"]:.2f} m conservative digitization bounds. Source N type is unspecified; original survey and scan error remain unknown. This is not a cross-panel identical ground transect or an independently dated repair.'
        if "alternative_edge" in r:caption+=' Plate XIX retains the second plausible western edge: '+f'{r["alternative_edge"]["estimate_m"]:.2f} m, bounds {r["alternative_edge"]["reading_lower_m"]:.2f}–{r["alternative_edge"]["reading_upper_m"]:.2f} m. Both readings are preserved.'
        self.record(n,dest.stem,a["title"],"actual source-plan measurement board",caption,["mohenjo-daro"],[self.source_ref("MACKAY-VOL2",a["locator"])],r,[self.asset_record(dest)])

    def board(self,n,slug,title,subtitle,panels,notes,caption,towns,sources,values=None):
        # Uniform source-image boards. The copied source pixels are scaled only;
        # original colours, north arrows and printed annotations remain intact.
        width=2700;header=180;footer=125;left=1770;right=width-left
        gap=35;heights=[];prepared=[]
        for panel in panels:
            path=Path(panel["physical_path"]);expected=panel.get("sha256")
            if expected:assert sha(path)==expected,path
            self.input_assets.append({"id":panel.get("id"),"physical_path":str(path),"sha256":sha(path)})
            image=Image.open(path).convert("RGB")
            if panel.get("crop_box"):
                crop=panel["crop_box"];image=image.crop(crop)
                self.custom_panels.append({"id":panel.get("id"),"parent_raster":str(path),"parent_sha256":sha(path),"crop_box_px":crop,"rotation":0,"contrast_changed":False})
            target_width=left-2*gap
            target_height=min(round(image.height*target_width/image.width),1100 if len(panels)>1 else 1860)
            scale=min(target_width/image.width,target_height/image.height)
            image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
            prepared.append((image,panel.get("label","")));heights.append(image.height+70)
        content_height=max(sum(heights)+gap*(len(panels)+1),1500)
        bg=Image.new("RGB",(width,header+content_height+footer),CREAM);d=ImageDraw.Draw(bg)
        font="C:/Windows/Fonts/arial.ttf";bold="C:/Windows/Fonts/arialbd.ttf"
        tfont=ImageFont.truetype(bold,49);sfont=ImageFont.truetype(font,31);bfont=ImageFont.truetype(font,33);hfont=ImageFont.truetype(bold,37);ffont=ImageFont.truetype(font,27)
        d.text((55,27),f"{n:02d}  {title}",font=tfont,fill=INK)
        for i,line in enumerate(textwrap.wrap(subtitle,125)):
            d.text((55,95+i*38),line,font=sfont,fill=GRAY)
        y=header+gap
        for im,label in prepared:
            if label:d.text((gap,y),label,font=hfont,fill=TEAL)
            y+=60;x=gap+(left-2*gap-im.width)//2;bg.paste(im,(x,y));y+=im.height+gap
        cursor=header+gap
        for heading,body,color in notes:
            d.rectangle((left+20,cursor,left+45,cursor+40),fill=color)
            d.text((left+65,cursor-2),heading,font=hfont,fill=color);cursor+=62
            for line in textwrap.wrap(body,47,break_long_words=False):
                d.text((left+30,cursor),line,font=bfont,fill=INK);cursor+=43
            cursor+=45
        if cursor>header+content_height-15:raise ValueError((n,"board notes exceed canvas",cursor,content_height))
        d.text((55,bg.height-100),"Source pixels and detailed crop records stay on D. Exact source locators and limits are in the figure manifest.",font=ffont,fill=GRAY)
        d.text((55,bg.height-60),"Local-only atlas · no inferred object points or ancient geometry added"+(" · DRAFT" if self.draft else ""),font=ffont,fill=GRAY)
        dest=self.out/f"fig-{n:02d}-{slug}.png";bg.save(dest)
        self.record(n,dest.stem,title,"actual source/context evidence board",caption,towns,sources,values,[self.asset_record(dest)])

    def context_board(self,n,aid,slug,title,subtitle,notes,caption,town):
        a=self.context_assets[aid];self.check_asset(a)
        loc=a["locator"];ref=self.source_ref(a["source_id"],f'p. {loc["printed_page"]}, PDF zero index {loc["pdf_index"]}; {aid}')
        with Image.open(a["physical_path"]) as im:
            mask=np.asarray(im.convert("L"))<235
            xs=np.where(mask.mean(axis=0)>.002)[0];ys=np.where(mask.mean(axis=1)>.002)[0]
            crop=[max(0,int(xs.min())-25),max(0,int(ys.min())-25),min(im.width,int(xs.max())+26),min(im.height,int(ys.max())+26)]
        self.board(n,slug,title,subtitle,[{"physical_path":a["physical_path"],"sha256":a["sha256"],"id":aid,"label":"Original publication figure","crop_box":crop}],notes,caption,[town],[ref],{"asset_id":aid,"context_assessment_ids":a.get("context_assessment_ids"),"display_change":"Conservative white-margin trim; full original asset remains linked"})

    def locations(self):
        prior=load(ROOT/"experiments/2026-10-24-urban-form-and-inscription-ecology/modules/visuals/manifest-run-v7.json")
        coords=prior["figures"][0]["data_values"]
        keys=["harappa","banawali","farmana","dholavira","kanmer","lothal","mohenjo-daro"]
        geo=load(BASE/"geography-sources-v1.json")[0];assert sha(geo["physical_path"])==geo["sha256"]
        land=load(geo["physical_path"])
        fig=canvas("Six-town source frame and a supplementary control","Modern land outline; inherited town coordinates locate sites, not excavated walls.")
        ax=fig.add_axes([.07,.15,.73,.67]);ax.set_facecolor("#e5f0ef")
        for feat in land["features"]:
            polys=feat["geometry"]["coordinates"]
            if feat["geometry"]["type"]=="Polygon":polys=[polys]
            for poly in polys:
                pts=np.asarray(poly[0]);ax.add_patch(Polygon(pts,closed=True,facecolor="#e7e0cf",edgecolor="#879d99",lw=.6))
        offsets={"harappa":(-.2,.65),"banawali":(-1.25,.65),"farmana":(.45,-.5),"dholavira":(-1.4,.55),"kanmer":(.65,.1),"lothal":(.6,-.5),"mohenjo-daro":(-1.5,.3)}
        for key in keys:
            c=coords[key];lon,lat=c["longitude"],c["latitude"];control=key=="mohenjo-daro"
            ax.scatter(lon,lat,s=110,facecolor=CREAM if control else TEAL,edgecolor=RUST if control else INK,lw=2,zorder=5)
            dx,dy=offsets[key];name="Mohenjo-daro\n(control)" if control else key.title()
            ax.annotate(name,(lon,lat),(lon+dx,lat+dy),arrowprops={"arrowstyle":"-","color":GRAY},fontsize=13,weight="bold",color=RUST if control else INK)
        ax.set_xlim(65,79);ax.set_ylim(20.5,32.8);ax.set_aspect(1/math.cos(math.radians(27)));ax.set_xlabel("Longitude east");ax.set_ylabel("Latitude north");ax.grid(color="white",alpha=.65)
        dlon=200/(111.32*math.cos(math.radians(22)))
        ax.plot([65.7,65.7+dlon],[21.3,21.3],color=INK,lw=3);ax.text(65.7,21.55,"200 km, approximate at 22° N",fontsize=10)
        fig.text(.82,.72,"6 primary towns",weight="bold",fontsize=15,color=TEAL)
        fig.text(.82,.64,"+1 supplementary\nMohenjo-daro control",fontsize=13,color=RUST,linespacing=1.5)
        fig.text(.82,.47,"Natural Earth 1:110m\nmodern coastline.\n\nNo ancient rivers or\npolitical boundaries\nare inferred.",fontsize=12,color=GRAY,linespacing=1.5)
        self.save(fig,1,"source-frame-map","Six-town source frame and supplementary control",
            "Six primary source-frame towns and supplementary Mohenjo-daro use the prior Q-1032 run-v5 coordinates pinned by the previous atlas Figure 1. Local positional accuracy is unreported. Natural Earth 1:110m land supplies a modern low-resolution coastline; it is not an ancient coast or a wall survey.",keys,
            [{"source_id":"NE110-LAND","title":"Natural Earth 1:110m land","url":geo["url"],"locator":"geography-v1/land.geojson","source_sha256":geo["sha256"]},
             {"source_id":"AXIS-REGISTER-V5","title":"Q-1032 town-axis register, run-v5","url":None,"locator":"prior atlas Figure 1; per-town pointers retained","source_sha256":coords[keys[0]]["source_sha256"]}],{k:coords[k] for k in keys})

    def farmana_bounds(self):
        ids=["PE-M001","PE-M002","PE-M003","PE-M004","PE-M005","PE-M006"]
        names=["East Lane 1 · IIA","East Lane 2 · IIA","Main Street · IIB","3I buttress projection","3I internal cross-span","4C passage · IIB"]
        fig=canvas("Farmana: local clearances and a wall projection","Six scoped readings from two excavation windows. These quantities do not form a time series.")
        ax=fig.add_axes([.25,.23,.67,.55]);values=[]
        for i,(mid,name) in enumerate(zip(ids,names)):
            x=self.em[mid];value=x["value"];lo,hi=x["reading_bound"];color=RUST if mid=="PE-M004" else GRAY if mid=="PE-M005" else TEAL
            ax.errorbar(value,5-i,xerr=[[value-lo],[hi-value]],fmt="o",color=color,ms=9,capsize=6,lw=2.5)
            ax.text(hi+.12,5-i,f'{value:.2f} m',va="center",fontsize=13,color=color)
            values.append({"id":mid,"value":value,"bounds":[lo,hi],"unit":"m","source_id":x["source_id"],"locator":x["locator"]})
        ax.set_yticks(range(6),list(reversed(names)));ax.set_xlabel("Metres on the source plan");ax.set_xlim(0,5.8);ax.grid(axis="x",alpha=.3)
        fig.text(.25,.145,"Bounds cover endpoint and scale reading. Unknown survey and scan errors can be larger.",fontsize=12,color=GRAY)
        fig.text(.25,.102,"Lane 1's 1.91 m local transect differs from its reported 1.60 m average; the difference remains unresolved.",fontsize=11,color=RUST)
        self.save(fig,6,"farmana-reading-bounds","Farmana local clearances and wall projection",
            "Six local readings preserve different feature scopes. E1 and E2 are Period IIA eastern lanes; C1-C4 use the Period IIB central composite, whose individual repair and closure dates are unresolved. Bars are conservative digitization bounds, not confidence intervals or original survey accuracy. The IIA Lane 1 local transect lies above the textual average; these are different scopes and no correction was forced. No north correction is required for local lengths; the detailed panels lack an explicit north symbol.",["farmana"],[self.source_ref("PE-S01","pp. 57, 99; Figures 5.18, 5.70; PDF zero indices 70,112; textual dimensions pp. 70,78,103,116-117,145")],values)

    def kanmer_sequence(self):
        fig=canvas("Kanmer: open-space infill can preserve alignment","Source-ordered observations. The boxes show propositions, not reconstructed plan geometry.")
        ax=fig.add_axes([.05,.16,.90,.66]);ax.axis("off")
        box(ax,.015,.31,.28,.52,"Earlier open space","Partly exposed extent:\n7 m north–south × 5 m east–west.\n\nStreet or open space in the\nexcavators' description.\nFull extent unknown.",TEAL,13)
        box(ax,.36,.31,.28,.52,"Added structures","OP10 describes structures\nwithin the former open space.\n\nThree partly exposed rooms\nin one subphase; later phases\nuse additional trenches.",RUST,13)
        box(ax,.705,.31,.28,.52,"Orientation retained","The Multicultural report\nretains the fort orientation\nwhile describing IIb infill.\n\nRoute continuity and wall\nsurvival are unmeasured.",TEAL,13)
        arrow(ax,(.30,.57),(.35,.57));arrow(ax,(.645,.57),(.70,.57))
        ax.text(.03,.12,"Room counts keep their source scope: more than six in OP10's later account; eight per structural phase in the Multicultural account.",fontsize=12,color=GRAY)
        self.save(fig,8,"kanmer-ordered-infill","Kanmer source-ordered infill and retained alignment",
            "OP10 pp. 85-86 and the 2011 Multicultural report pp. 363-364 describe additions in earlier open space and continued fort alignment. Their structural-phase numbering and exposed room counts remain separate. The 7 by 5 m extent is only partially exposed. Boxes are an authored observation diagram, with no reconstructed plan geometry. POSTJOIN-LEAD-01 preserves OP10 p. 86's sealing on layer 9 floor levels in southwest Z28 and a separate X30/layer 8 button seal. Those positive associations lack registrations, named rooms and independent event dates; neither is equated with the previously assessed three-impression cohort.",["kanmer"],[self.source_ref("PE-S06","pp. 85-86, Figure 8; preview pages 93-94; full PDF unheld"),self.source_ref("PE-S02","pp. 363-364, Figure 8; PDF indices 8-9")],{"open_space_dimensions_m":[7,5],"extent":"partial","OP10_subphase_rooms":3,"OP10_later_rooms":">6","Multicultural_rooms_per_structural_phase":8,"independent_persistence_episodes":0,"postjoin_lead":load(BASE/"POSTJOIN-LEAD-01.json")},kind="authored source-ordered observation diagram")

    def harappa_partial_chain(self):
        specifications=[(4,[65,248,555,331],"har-wall15-dates-v2",143,"Table 1: BP and 1-sigma calibrated BC, as printed"),
                        (8,[66,214,602,278],"har-tr22-prose",147,"Trench 22 prose: tablets from street deposits"),
                        (21,[75,462,561,660],"har-fig11-caption-v2",160,"Figure 11 caption: 11.04 and 11.06 assigned to Trench 7/8, wash")]
        panels=[]
        for index,clip,key,printed,detail in specifications:
            p=self.crop_pdf("MK1997",index,clip,key,printed,detail)
            panels.append({"id":key,"physical_path":str(p),"sha256":sha(p),"label":detail})
        self.board(10,"harappa-wall15-partial-chain","Harappa: a dated wall and a disputed tablet deposit",
            "Actual source excerpts show the surviving links and the unresolved documentary end.",panels,
            [("1  Hearth → wall","A-8047, A-8048 and A-8049 are reported below Wall 15. They constrain its later construction; they do not directly date tablet use.",TEAL),
             ("2  Prose → tablets","The Trench 22 narrative places two cited faience tablets in street deposits inside the perimeter wall.",TEAL),
             ("3  Caption conflict","Figure 11.04 and 11.06 instead give Trench 7/8, wash. Registrations H94-2274 and H94-2283 remain explicit.",RUST),
             ("What would decide it","Reconcile the field registers and deposits, then link the object-use surface and a named repair. Three determinations do not supply three independent repair episodes.",RUST)],
            "MK1997 printed p. 143, Table 1 (PDF index 4), supplies A-8047/AA-16461, A-8048 and source-flagged A-8049 from hearths below Wall 15. The source prints 1σ calibrated BC intervals, with the calibration method unspecified in this bounded table. Printed p. 147 (index 8) places the cited tablets in Trench 22 street deposits, whereas Figure 11 caption p. 160 (index 21) assigns 11.04 and 11.06 to Trench 7/8 wash. This is a partial date-to-wall chain; the object-use and repair joins remain unresolved. The excerpts contain no plan north or new measurement.",
            ["harappa"],[self.source_ref("MK1997","p. 143 Table 1, p. 147 Trench 22, p. 160 Fig. 11 caption; PDF zero indices 4,8,21")],
            {"context_id":"HAR-TR22-CAPTION-CONFLICT","date_ids":["HAR-A8047","HAR-A8048","HAR-A8049"],"date_to_original_tablet_use_established":False})

    def harappa_workshop(self):
        self.context_board(11,"HAR-WORKSHOP-PLAN","harappa-manufacture-plan","Harappa: a bounded tablet-manufacturing setting",
            "Original workshop plan; the mapped area and the illustration cohort have different spatial precision.",
            [("Positive material evidence","Unfired and broken tablets, steatite blanks, sawn material, faience waste and firing-canister fragments support manufacture.",TEAL),
             ("Bounded cohort","Figure 3 illustrates five incised tablets, two blanks and eight moulded faience tablets. These are 15 illustration units, not a site census.",TEAL),
             ("Formation matters","The courtyard material is fill exposed by wall robbery and erosion. Manufacture evidence does not establish original document use on that floor.",RUST),
             ("Map limits","The source has a 5 m bar and N arrow of unspecified reference. Individual registered tablets have no plotted operating-surface points.",GRAY)],
            "KENOYER2005 Figure 2, PDF index 7, maps Trench 54 workshop [601], bounded source features and the local survey grid. The 5 m bar and N arrow are retained; true/grid/magnetic reference is unspecified. The Figure 3 cohort has 15 illustration units in a manufacturing setting, while the report describes courtyard fill, wall robbery and erosion. No new geometry, exact tablet-use point or event-specific construction date is inferred.","harappa")

    def harappa_dump(self):
        self.context_board(12,"HAR-SECONDARY-CLUMP","harappa-secondary-clump","Harappa: a close group in a secondary deposit",
            "Original plan preserves approximate find positions and Wall 296; deposition follows wall construction.",
            [("Physical grouping","The source reconstructs 22 incised tablets: 16 in a clump, two nearby and four scattered.",TEAL),
             ("Ordered deposit","The dump was deposited after Wall 296 construction, between Walls 250 and 296 and before Period 3C material.",RUST),
             ("Source map precision","The find dots are approximate. A 5 m bar and source north convention remain visible; no modern object coordinates are assigned.",GRAY),
             ("Testable next join","Identify the original manufacture or use location independently. A tight discarded group does not locate an operating office.",RUST)],
            "MK2000 Figure 2, author-PDF p. 7/index 7, maps Wall 296 and approximate tablet find locations; the 5 m bar and source north convention are retained. Source interpretation pp. 12-13 places the group in secondary fill deposited after the wall. The 22-tablet cohort is a dependent source reconstruction, not 22 independent institutional episodes. No original-use point or wall-construction date is supplied by the grouping.","harappa")

    def harappa_floor(self):
        self.context_board(13,"HAR-FLOOR-SEALS","harappa-floor-seals","Harappa: seal identities preserve depositional differences",
            "Original registration figure, read with its floor, floor-fill and upper-fill descriptions.",
            [("Courtyard association","H95-2491/4690-01 has a reported courtyard association. The prose says floor; the figure retains a floor/fill qualifier.",TEAL),
             ("Room association","H95-2598/4666-19 occurs in a reported room assemblage with hearth, bin and grindstone. A same-context determination is not supplied.",TEAL),
             ("Separate upper fill","H95-2419/4609-01 is from upper fill. Its wear records object history, while the original operating room remains unresolved.",RUST),
             ("Date boundary","Nearby hearth determinations cannot be transferred to these individual seal-use or construction events.",GRAY)],
            "MK1997 Figure 7, printed p. 154/PDF index 15, preserves registrations and loci. The contextual discussion p. 150/index 11 differentiates Trench 10E courtyard floor or floor-fill, a hearth-and-bin room and upper fill. The source gives no exact object point or independently dated original-use and repair pair. The original object photographs are retained; no north-bearing inference applies.","harappa")

    def dholavira_fields(self):
        s=load(BASE/"modules/contexts/dholavira225-summary.json");g=s["gate_counts"]
        keys=["accession_string","grid_label","stratum_label","depth_label","area_label","unqualified_stage","explicit_room_label"]
        labels=["Accession string","Grid label","Stratum label","Depth label","Area label","Unqualified stage","Explicit room label"]
        values=[g[k] for k in keys]
        fig=canvas("Dholavira: recorded fields stop short of an original-use join","225 publication rows and accession strings. Physical-object identity remains unadjudicated.")
        ax=fig.add_axes([.25,.26,.66,.52]);y=np.arange(len(keys))
        ax.barh(y,values,color=[TEAL]*6+[RUST],height=.58);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,245);ax.set_xlabel("Rows with the named usable field, out of 225")
        for i,v in enumerate(values):ax.text(v+3,i,str(v),va="center",weight="bold",fontsize=14)
        ax.grid(axis="x",alpha=.2);ax.set_axisbelow(True)
        fig.text(.25,.16,"Separate endpoint: 0 rows establish a primary-use surface and independent construction-date join in this held table.",color=RUST,fontsize=11.8)
        fig.text(.25,.105,"Field bars are parallel descriptions, not successive filters. The usable-label predicate excludes placeholders and Unst. labels.",color=GRAY,fontsize=10.7)
        self.save(fig,17,"dholavira-field-gates","Dholavira stage-to-use limits",
            "BISHT2015-PRELIM seal-context table printed pp. 250-258 supplies 225 rows with 225 unique accession strings. The context module's usable-label predicate gives 223 grid, 211 stratum, 201 depth, 204 area and 162 unqualified stage labels; three rows explicitly name a room. These are parallel field counts. They are not an object census or cumulative eligibility funnel. Zero rows establish the original-use and independently dated construction join within the held table, which does not assert absence of such contexts at Dholavira.",["dholavira"],[self.source_ref("BISHT2015-PRELIM","seal-context table pp. 250-258; contexts/dholavira225-summary.json and CLARIFICATION-01.json")],{"denominator":225,"field_counts":dict(zip(keys,values)),"primary_use_surface_established":0,"independent_construction_date_established":0,"field_count_scope":"parallel presence gates; source rows"})

    def dholavira_panel(self):
        p=self.crop_pdf("BISHT2015-PRELIM",244,[68,204,536,673],"dholavira-gate-ten-sign-panel",228,"Figures 8.2-8.4: gate find context, close-up and source drawing")
        self.board(18,"dholavira-panel-context","Dholavira: public architecture, unresolved emplacement date",
            "The source records fallen inlays in the western chamber of the Castle north gate.",
            [{"id":"dhol-gate-context","physical_path":str(p),"sha256":sha(p),"label":"Original Figures 8.2-8.4, printed p. 228"}],
            [("Strong spatial anchor","The western chamber is a named architectural context. The source photograph and drawing preserve the ten-sign panel association.",TEAL),
             ("Recovery → mounting","Recovery on the floor is observed. An original wooden panel above the gate lintel is reconstructed from layout and support evidence.",RUST),
             ("Stage → event","A site stage or distant TL determination does not independently date the panel's installation or a gate repair.",RUST),
             ("Deciding observation","Join the mounting evidence to an independently dated construction or repair surface. The public location alone does not identify the installing authority.",TEAL)],
            "BISHT2015-PRELIM printed p. 228, Figures 8.2-8.4/PDF index 244, shows the find position, close-up and source drawing. Context discussion continues pp. 229-230/indices 245-246. DHO-GATE10 retains the fallen position in the western chamber and the reconstructed lintel mounting; no event-specific emplacement date is established. The source photograph has no plan north arrow or metric measurement added here.",["dholavira"],[self.source_ref("BISHT2015-PRELIM","pp. 228-230, Figures 8.2-8.4; PDF indices 244-246")],{"context_id":"DHO-GATE10","source_sign_count":10,"mounting_reconstructed":True,"emplacement_date_join":False})

    def lothal_map(self):
        self.context_board(20,"LOT-DEPOSIT-PLAN","lothal-deposit-map","Lothal: a discovery area is not an application point",
            "The original site and warehouse detail locate a sealing cohort with competing formation histories.",
            [("Discovery area","The source bounds the sealing-discovery area around warehouse passage 41I-41J. It does not plot each original sealing application.",TEAL),
             ("Formation alternatives","Stored goods, discarded sealing material and later fill require separate tests. The reanalysis shares Rao's excavation evidence.",RUST),
             ("Scale and north","The source has 100 m and 5 m bars and its own north arrows. They are retained without imposing a new orientation.",GRAY),
             ("Independent locality","W1 is inferred from stamp identity and W2 names a broad trench. Neither supplies the same direct warehouse-room deposit as W.",RUST)],
            "FT2005 Figure 2, printed p. 97/PDF index 34, retains the site map, warehouse detail, 100 m and 5 m bars and source north arrows of unspecified reference. The marked discovery area is a cohort anchor, not an individual original-application point. The reanalysis and Rao publication share one excavation source lineage; rival formation histories remain open.","lothal")

    def lothal_counts(self):
        s=load(BASE/"modules/contexts/lothal-denominators.json");review=load(BASE/"lothal-recount-v1.json")
        assert review["passed"] and review["counts"]==s["table_literal_counts"]
        cats=["W","W1","W2","O","?"];a=[review["counts"][k] for k in cats];b=[s["prose_counts"][k] for k in cats]
        fig=canvas("Lothal: the table and prose have different denominators","A separate reader reproduced all 93 table rows; the discrepancy with the prose remains visible.")
        ax=fig.add_axes([.10,.27,.80,.52]);x=np.arange(5);width=.32
        ax.bar(x-width/2,a,width,color=TEAL,label="Table 1: 93 rows");ax.bar(x+width/2,b,width,color=RUST,label="Prose categories: sum 92")
        for i,(u,v) in enumerate(zip(a,b)):
            ax.text(i-width/2,u+.7,str(u),ha="center",weight="bold");ax.text(i+width/2,v+.7,str(v),ha="center",weight="bold")
        ax.set_xticks(x,["W\ndirect warehouse","W1\nstamp-inferred","W2\nbroad trench","O\nother","?\nunknown"]);ax.set_ylim(0,42);ax.set_ylabel("Publication rows");ax.legend(frameon=False,loc="upper right");ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True)
        fig.text(.10,.15,"W1 locality is inferred from stamp identity. W2 is broad SRG3 provenance without a demonstrated warehouse-room deposit.",fontsize=11.6,color=GRAY)
        fig.text(.10,.10,"Unknown rows retain their category; they are not treated as finds outside the warehouse.",fontsize=11.5,color=RUST)
        self.save(fig,21,"lothal-provenance-counts","Lothal provenance counts and source conflict",
            "FT2005 Table 1, printed pp. 93-94/PDF indices 30-31, gives W35, W1=18, W2=11, O10 and ?19 across 93 rows. The root's separate reader reproduced 93/93 rows in lothal-recount-v1.json. Prose p. 71/index 8 gives O11 and ?17, summing to 92 with the unchanged other categories. W1 is stamp-based location inference, W2 is broad-trench provenance, and ? remains unknown. These dependent publication categories are not matched original-use or repair episodes.",["lothal"],[self.source_ref("FT2005","Table 1 pp. 93-94, prose p. 71; PDF indices 30-31,8")],{"categories":cats,"table":a,"prose":b,"table_total":sum(a),"prose_sum":sum(b),"independent_recount":"lothal-recount-v1.json","recount_agreement_rows":93})

    def mohenjo_widths(self):
        fig=canvas("First Street: four local chords and one missing bank","Categorical source phases. Different frontages, no common geodetic transect and no temporal-trend estimate.")
        ax=fig.add_axes([.26,.24,.64,.55]);rows=self.md["rows"]
        for i,r in enumerate(rows):
            y=4-i
            if r["estimate_m"] is None:
                ax.text(3.8,y,"No value: western phase bank unresolved",color=RUST,va="center",fontsize=13)
                continue
            val,lo,hi=r["estimate_m"],r["reading_lower_m"],r["reading_upper_m"]
            ax.errorbar(val,y,xerr=[[val-lo],[hi-val]],fmt="o",color=TEAL,ms=9,lw=2.5,capsize=5)
            if "alternative_edge" in r:
                a=r["alternative_edge"];val=a["estimate_m"];lo=a["reading_lower_m"];hi=a["reading_upper_m"]
                ax.errorbar(val,y-.12,xerr=[[val-lo],[hi-val]],fmt="s",color=RUST,ms=7,lw=2,capsize=5)
        ax.set_yticks(range(5),list(reversed([r["phase_raw"]+" · "+r["plate"] for r in rows])));ax.set_xlim(3.5,13);ax.set_ylim(-.65,4.65);ax.set_xlabel("Metres from each panel's own graphic bar");ax.grid(axis="x",alpha=.25)
        ax.legend(handles=[Line2D([0],[0],color=TEAL,marker="o",lw=2,label="Retained source-edge reading"),Line2D([0],[0],color=RUST,marker="s",lw=2,label="Plate XIX alternative western edge")],frameon=False,fontsize=11,loc="upper right")
        fig.text(.26,.14,"Endpoint and scale-bar reading bounds overlap. Unknown source error can be larger.",fontsize=12,color=GRAY)
        fig.text(.26,.095,"The fifth reading stays missing; phase labels do not provide independently dated construction events.",fontsize=11.5,color=RUST)
        self.save(fig,24,"first-street-width-bounds","First Street local chords and missing fifth reading",
            "MACKAY-VOL2 plates XVI-XX, PDF zero indices 45,47,49,51,53, supply four readable local horizontal chords and one unmeasurable fixed-row bank. Bars use 0–50 feet, with 5 px feature-endpoint and 3 px bar-endpoint radii. Plate XIX retains both western edges. The source N reference is unspecified; no north correction is needed for length. The relative phases are categorical and not independent repair dates. No trend line, common-ground transect, continuous-access inference or missing-value imputation is used.",["mohenjo-daro"],[self.source_ref("MACKAY-VOL2","plates XVI-XX; PDF indices 45,47,49,51,53")],{"rows":rows,"same_ground_transect":False,"trend_fitted":False,"missing_imputed":False})

    def published_gini(self):
        source=load(BASE/"modules/mohenjo-control/published-residential-intervals.json");rows=source["rows"]
        assert source["bound_level"]==.8 and source["recomputed"] is False
        fig=canvas("A separate source control: published residential Gini bounds","DK-G South summary rows. Published 80% intervals are reproduced without recomputing individual house data.")
        ax=fig.add_axes([.21,.24,.61,.53]);labels=[]
        for i,r in enumerate(rows):
            val,lo,hi=r["gini"],r["published_lower"],r["published_upper"];y=4-i
            ax.errorbar(val,y,xerr=[[val-lo],[hi-val]],fmt="o",color=TEAL,ms=9,lw=2.5,capsize=5)
            ax.text(.465,y,f'n = {r["n_residences"]}',va="center",fontsize=13,color=GRAY)
            labels.append(r["phase_raw"])
        ax.set_yticks(range(5),list(reversed(labels)));ax.set_xlabel("Published residence-area Gini");ax.set_xlim(.15,.52);ax.grid(axis="x",alpha=.2)
        fig.text(.21,.14,"The 80% level comes from the paper's Figure 5 caption and its supplied R script.",fontsize=12,color=GRAY)
        fig.text(.21,.095,"These phase summaries do not supply street vectors, independent repair dates or a new width–inequality test.",fontsize=11.5,color=RUST)
        self.save(fig,25,"published-gini-control","Published residential Gini source control",
            "GREEN2026-OSM sup001.csv, Subarea=DKGS, supplies five published phase Gini estimates, lower/upper bounds and residence sample sizes. The paper Figure 5 caption and supplied R script set conf.level=0.8. We reproduce these 80% bounds without recomputation. Buildings may recur across phases, so sample sizes are not additive. Model-assigned centuries are omitted from the plot because they do not independently date construction. This control remains separate from First Street chord measurements.",["mohenjo-daro"],[self.source_ref("GREEN2026-OSM","sup001.csv, Subarea=DKGS; Figure 5 caption and supplied R script, conf.level=0.8")],source)

    def intrusive_rice(self):
        self.context_board(26,"KAN-RICE-COUNTEREXAMPLE","kanmer-intrusive-rice","Kanmer: direct rice ages challenge field-phase assignment",
            "Original sample discussion; later grains entered archaeological deposits attributed to much earlier phases.",
            [("PLD-16351","Rice grains: reported AD 335-425 interval, 95.4% coverage. The bounded paragraph does not give the raw BP determination.",TEAL),
             ("PLD-16353","Rice grains: reported AD 321-410 component, 80.1% coverage. This is not the full distribution or a matching 95.4% interval.",TEAL),
             ("Formation interpretation","The authors interpret the later grains as percolated or reworked into older remains. A field-phase label did not establish their age.",RUST),
             ("Construction limit","Neither grain date is joined to a named repair or documentary-use event. They are retained as a depositional counterexample.",RUST)],
            "POKHARIA2011 printed p. 1836/PDF index 3 reports rice samples PLD-16351 at AD335-425 (95.4%) and PLD-16353 at AD321-410 (80.1% reported component). Raw BP determinations and calibration method are omitted from this paragraph. The authors interpret the later grains as percolated or reworked into older deposits. These are two paragraph dating-evidence entries, not two independent Harappan construction dates. No plan north or metric geometry is inferred.","kanmer")

    def eligibility(self):
        decisions=self.run["decisions"];counts=self.run["counts"]
        fig=canvas("Every prediction gate remains unqualified","One grid-registered descriptive pair does not supply the matched route–partition comparison.")
        ax=fig.add_axes([.05,.16,.90,.66]);ax.axis("off")
        headings=[("Prediction",.00),("Required evidence",.15),("Qualified",.69),("Effect",.83)]
        for t,x in headings:ax.text(x,.97,t,weight="bold",fontsize=14,color=TEAL,va="top")
        reqs=["12 independent episodes in 4 towns; complete comparable route and partition windows",
              "6 directly joined repairs in 3 towns; at least 4 usable local component connections",
              "Independent repair dates; frozen network model compared with distance and engineering",
              "20 matched primary-use / custody-change pairs in 4 towns, with adequate sensitivity",
              "Matched episodes and physical evidence distinguishing shared work from goods allocation"]
        for i,(r,req) in enumerate(zip(decisions,reqs)):
            y=.85-i*.155
            ax.axhline(y+.025,color=LIGHT,lw=1)
            ax.text(.0,y,r["claim"],fontsize=14,va="top",weight="bold")
            ax.text(.15,y,lines(req,57),fontsize=12.4,va="top",linespacing=1.4)
            ax.text(.725,y,str(r["eligible"]),fontsize=19,va="top",color=RUST,ha="center")
            ax.text(.83,y,"Not estimable" if r["effect"] is None else str(r["effect"]),fontsize=12.5,va="top",color=GRAY)
        fig.text(.05,.105,"Zero is the count of qualified assembled episodes or pairs in this source frame. It is not an estimate of ancient institutional absence.",fontsize=11.5,color=RUST)
        self.save(fig,29,"prediction-eligibility","Prediction eligibility matrix",
            "The frozen run-v1 decisions retain zero qualified observations for C-0017 P1/P2/P3, C-0018 and C-0019. Harappa Area C Figures 4.12/4.16 supply one grid-registered descriptive pair, with an incomplete internal-partition comparator and mixed upper street levels. No effect is estimated. The integrated 29 architectural source cases, 32 context assessments and 78 dating-evidence entries have different units and are not interchangeable independent episodes.",self.run["primary_towns"],[{"source_id":"PROTOCOL-2026-10-24","title":"Shared infrastructure against excavation plans","url":None,"locator":"PROTOCOL.md, Predictions, controls and decision; frozen run-v1.json decisions","source_sha256":sha(BASE/"PROTOCOL.md")}],{"decisions":decisions,"source_units":counts})

    def rival_tests(self):
        fig=canvas("Selective continuity has several testable explanations","Prospective rival predictions. The present source frame supplies no institutional verdict.")
        ax=fig.add_axes([.05,.18,.90,.64]);ax.axis("off")
        rows=[
            ("Shared coordination","Through-routes survive rebuilding more often than internal divisions; connected repairs share independent dates.","A complete, powered matched study shows no predicted route advantage, or repair timing follows only engineering and distance."),
            ("Engineering constraints","Durable foundations, grade and drainage explain retention; effects weaken after material and preservation controls.","The route advantage persists within the same foundations, materials and exposure, while network relationships predict repair better."),
            ("Inherited parcel rights","Frontage and parcel boundaries persist while internal rooms and household access change.","Boundaries reset freely while shared connections persist across the resets, with no parcel continuity needed."),
            ("Local infill and maintenance","Small additions narrow or close access at different times; service replacement follows clogging and local need.","Independently dated coordinated repairs and repeated open-network preservation exceed the local engineering model.")]
        ax.text(.0,.99,"Explanation",weight="bold",color=TEAL,fontsize=14)
        ax.text(.21,.99,"Discriminating prediction",weight="bold",color=TEAL,fontsize=14)
        ax.text(.60,.99,"Evidence that would challenge it",weight="bold",color=RUST,fontsize=14)
        for i,(name,pred,challenge) in enumerate(rows):
            y=.88-i*.215
            ax.axhline(y+.035,color=LIGHT,lw=1)
            ax.text(.0,y,lines(name,18),weight="bold",fontsize=13.5,va="top",color=TEAL)
            ax.text(.21,y,lines(pred,48),fontsize=12.0,va="top",linespacing=1.45)
            ax.text(.60,y,lines(challenge,48),fontsize=12.0,va="top",linespacing=1.45)
        fig.text(.05,.10,"Deciding test: register the same phase windows, count open connections and internal partitions, then date named repairs independently.",fontsize=12,color=INK,weight="bold")
        self.save(fig,30,"rival-predictions","Rival predictions and deciding observations",
            "These are project-authored prospective tests. The strongest supported reading is selective continuity: inherited outlines and alignment coexist with local rebuilding and changed access. Distinguishing coordination, engineering, parcel rights and local infill requires registered common windows, complete inventories, preservation controls and independently dated named repairs. Count continued through-access separately from aligned walls; reconcile original-use object contexts before testing any documentary or labour mechanism.",self.run["primary_towns"],[{"source_id":"PROTOCOL-2026-10-24","title":"Shared infrastructure against excavation plans","url":None,"locator":"PROTOCOL.md; TEST-DESIGN.md; C-0017 P1-P3 and documentary gates","source_sha256":sha(BASE/"PROTOCOL.md")}],{"rivals":[{"name":n,"prediction":p,"challenge":c} for n,p,c in rows],"status":"prospective, untested"},kind="authored prospective test diagram")

    def build(self):
        self.locations()
        self.reuse_west(2,"PW-V01","harappa-grid-registered-pair")
        self.reuse_board(3,"PE-P04","banawali-composite-limit",
            "PE-S03, printed p. 33, Figure 1/PDF index 46, combines Pre-Harappan and Harappan defences and structures from several periods. The N symbol is unspecified north. The curved northeast defence band does not provide a retained straight-corner angle; its attempted measurement was withdrawn after visual review. Text pp. 16-17 orders enclosure retention and domestic replacement, without paired plan exposure or a numerical survival denominator.")
        self.reuse_board(4,"PE-P01","farmana-eastern-lanes",
            "PE-S01, p. 57, Figure 5.18/PDF index 70, is explicitly assigned to Period IIA on pp. 52-54. E1 and E2 are local clear-width transects, 1.91 m (1.78-2.05) and 1.95 m (1.82-2.09), using the same 5 m graphic bar. Bounds describe digitization only. The detailed panel has no north arrow. The bathing platform and western Lane 2 disturbance are locally later; the source does not provide separate registered pre-encroachment panels.")
        self.reuse_board(5,"PE-P02","farmana-main-street-4c",
            "PE-S01, p. 99, Figure 5.70/PDF index 112, is the eastern half of the central IIB composite, explicitly joined on p. 97. It separates a 3.96 m Main Street transect, the roughly 0.59 m 3I buttress projection with broad reading sensitivity, a 4.66 m inner span and a 1.79 m 4C passage. The cap described p. 152 removes 4C's northern connection to Lane 1; Lane 1 itself is not reported closed. Source north is not printed on the detailed panel; graphic-bar bounds are digitization sensitivity, with repair dates unresolved.")
        self.farmana_bounds()
        self.reuse_board(7,"PE-P03","kanmer-fort-corner",
            "PE-S02, p. 360, Figure 5/PDF index 5, is an unsplit KMR II overview of exposed fort parts, gaps and trenches. K1 is 88.53 degrees with a 77.81-99.25 degree digitization bound, widened by the short arm; source survey error is unknown. The N arrow has unspecified reference. The printed 2 cm = 5 m statement has no metric graphic bar, so no metre length is inferred from nominal page centimetres. Separate IIa/IIb residential plan panels remain missing.")
        self.kanmer_sequence()
        self.reuse_west(9,"PW-V02","harappa-gateway-drain")
        self.harappa_partial_chain()
        self.harappa_workshop()
        self.harappa_dump()
        self.harappa_floor()
        self.reuse_west(14,"PW-V04","dholavira-east-gate-blockings")
        self.reuse_west(15,"PW-V05","dholavira-north-down")
        self.reuse_west(16,"PW-V06","dholavira-defence-sequence")
        self.dholavira_fields()
        self.dholavira_panel()
        self.reuse_west(19,"PW-V09","lothal-recovered-figure17")
        self.lothal_map()
        self.lothal_counts()
        self.reuse_mohenjo(22,"MD-WIDTH-45","mackay-xvi-source-reading")
        self.reuse_mohenjo(23,"MD-WIDTH-51","mackay-xix-alternative-banks")
        self.mohenjo_widths()
        self.published_gini()
        self.intrusive_rice()
        self.reuse_west(27,"PW-V08","dholavira-water-connections")
        self.reuse_west(28,"PW-V11","lothal-inlet-changes")
        self.eligibility()
        self.rival_tests()
        self.finish()

    def finish(self):
        self.figures.sort(key=lambda r:r["figure"])
        assert [f["figure"] for f in self.figures]==list(range(1,31))
        selected=[1,2,4,5,7,9,10,11,12,14,15,18,19,20,21,22,24,29,30]
        manifest={"schema_version":"1.0","atlas_label":self.label,"status":"draft" if self.draft else "rendered; individual visual review recorded separately",
            "authors":[{"model":"GPT-6 family; exact serving variant unknown","harness":"Codex desktop","agent":"/root/eastern_towns"}],
            "root_run_sha256":sha(BASE/"run-v1.json"),"input_freeze_sha256":None if self.draft else sha(HERE/"inputs-freeze-v1.json"),
            "code_sha256":sha(Path(__file__)),"figure_count":len(self.figures),"output_root":str(self.out),"local_only":True,
            "figures":self.figures,"selected_cover_figures":selected,"input_assets":self.input_assets,"text_bounds":self.text_bounds,
            "source_imagery_policy":"Source plans and detailed transforms remain local-only on D; tracked files contain authored metadata and code.",
            "counts":{"authored_png_and_svg_figures":sum(len(f["assets"])==2 for f in self.figures),"source_raster_boards":sum(len(f["assets"])==1 for f in self.figures)}}
        name=f"manifest-{self.label}.json"
        (HERE/name).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        (self.out/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        (self.out/"custom-source-panel-transforms.json").write_text(json.dumps(self.custom_panels,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        captions=[]
        for f in self.figures:
            captions += [f'## Figure {f["figure"]}. {f["title"]}',"",f["caption"],"",f["source_note"],""]
            for s in f["sources"]:
                if s.get("url"):captions += [f'[{s["title"]}]({s["url"]})',""]
        (HERE/f"captions-{self.label}.md").write_text("\n".join(captions),encoding="utf-8")
        (self.out/"CAPTIONS.md").write_text("\n".join(captions),encoding="utf-8")
        print(json.dumps({"manifest":str(HERE/name),"sha256":sha(HERE/name),"figure_count":30,"text_overflow_figures":[r["figure"] for r in self.text_bounds if r["outside_canvas_text"]]},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--label",default="run-v1");parser.add_argument("--draft",action="store_true")
    args=parser.parse_args();Atlas(args.label,args.draft).build()
