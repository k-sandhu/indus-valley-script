"""Write experiments/2026-10-21-plan-registration/measure-S/sources.json from fetch_log.json and the
assessments below. Run from the repository root with python -P."""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "experiments" / "2026-10-21-plan-registration" / "measure-S"

USE = {
    "jls764_html_fig_3262.png": ("shikarpur", "used", "Gadekar, Rajesh and Ajithprasad 2014, JLS 1(1), doi:10.2218/jls.v1i1.764, Figure 2 (HTML galley image file 3262): plan of the mound and fortification with north symbol, 50 m scale bar and survey grid. Measured (towns/shikarpur.json, source jls2014-fig2) and registered (control-S/shikarpur__jls2014-fig2.json). CC BY 2.5 Scotland."),
    "jls764_html_fig_3261.jpg": ("shikarpur", "rejected", "Same article, Figure 1: regional map of Harappan sites and raw-material sources; no site plan."),
    "shikarpur_2008-09_harappacom_wb20250616.pdf": ("shikarpur", "rejected", "Bhan et al., Excavations at Shikarpur, Gujarat 2008-2009 (harappa.com, via Wayback): text and photographs only (Fig. 1 a photograph of the southern fortification face); no plan."),
    "shikarpur_2008-09_harappacom_wb20240418.pdf": ("shikarpur", "rejected", "Second Wayback digest of the same URL; exactly 1 MiB and unreadable (truncated capture)."),
    "bhan_harappacom_kuldeep_k_bhan_1.pdf": ("shikarpur", "rejected", "K. K. Bhan, 'Some important aspects of technology and craft production ...', Walking with the Unicorn (2018), harappa.com copy: Shikarpur appears only in photographs of beads and raw material; the site plans are of Gola Dhoro."),
    "iar_1997-98.pdf": ("rakhigarhi", "rejected", "Indian Archaeology 1997-98 - A Review, entry 20 Excavation at Rakhigarhi: photographic plates only."),
    "iar_1998-99.pdf": ("rakhigarhi", "rejected", "Indian Archaeology 1998-99 - A Review, entry 12 Excavation at Rakhigarhi: photographic plates only."),
    "iar_1999-2000.pdf": ("rakhigarhi", "rejected", "Indian Archaeology 1999-2000 - A Review, entry 23 Excavation at Rakhigarhi: photographic plates only."),
    "iar_2000-01.pdf": ("rakhigarhi", "rejected", "Indian Archaeology 2000-2001 - A Review: Rakhigarhi appears only under conservation (fencing of mounds I-III)."),
    "iar_1988-89.pdf": ("shikarpur", "rejected", "Indian Archaeology 1988-89 - A Review, entry 21 Excavation at Shikarpur (Gujarat State Department of Archaeology): text only."),
    "iar_1989-90.pdf": ("shikarpur", "rejected", "Indian Archaeology 1989-90 - A Review, entry 18 Excavation at Shikarpur (Valamiyo Timbo): text only."),
    "plos_0192299_g002.tif": ("rakhigarhi", "rejected", "Shinde et al. 2018, PLoS ONE 13(2): e0192299, Fig. 2: oblique aerial photograph of the mounds and the cemetery; not a plan."),
    "plos_0192299_g003.tif": ("rakhigarhi", "rejected", "Same article, Fig. 3: vertical drone photograph of the RGR-7 cemetery trenches with a north arrow and trench sizes; graves only, no Harappan walls, streets or drains."),
    "plos_0192299_g007.tif": ("rakhigarhi", "rejected", "Same article, Fig. 7: map of graves in the necropolis trenches; graves, not walls."),
    "archaeopress_9781803275918_sample.pdf": ("rakhigarhi", "rejected", "Shinde and Shin (eds) 2023, Archaeopress, free sample: front matter and Chapter 1 only; the full volume is sold, not open access; its list of figures names photographs for the settlement mounds."),
    "rawat2015_gujarat_port_towns.pdf": ("shikarpur", "rejected", "Y. S. Rawat 2015, 'Possible port towns of Harappan time in Gujarat' (copy on ancientportsantiques.com): Shikarpur appears as a general-view photograph (Fig. 8) only."),
    "heritage11-2_30_metal_objects_gujarat.pdf": ("shikarpur", "rejected", "Heritage: Journal of Multidisciplinary Studies in Archaeology 11.2, article 30, on metal objects from Harappan sites in Gujarat: no Shikarpur plan."),
}
BASE = "data/raw/2026-10-21-town-axes/plan-B/downloads/"
EARLIER = [
    ("nath_rakhigarhi_1997-2000.pdf", "rakhigarhi", "rejected", "A. Nath, Excavations at Rakhigarhi [1997-98 to 1999-2000] (Internet Archive excavationsatrakhigarhi19972000amarendranath_457_Z). Re-examined every figure page: sections (PDF page indices 98-100), regional and soil maps, photographs (Pls 4.1-4.6, page indices 101 and 122-125), burial and bead tables; appendix Fig. 1 (page index 335) is a contoured mound plan with an unlabelled arrow and no scale bar, usable only as an auxiliary plan. No structural plan."),
    ("puratattva28.pdf", "rakhigarhi", "rejected", "Puratattva 28: Nath, 'Rakhigarhi: A Harappan metropolis in the Sarasvati-Drishadvati divide', site plan of mounds (PDF page index 51) marked 'not to scale'; no structures."),
    ("puratattva29.pdf", "rakhigarhi", "rejected", "Puratattva 29: Nath, 'Further excavations at Rakhigarhi' (PDF page indices 59-62): text only."),
    ("puratattva31.pdf", "rakhigarhi", "rejected", "Puratattva 31: Nath, 'Rakhigarhi: 1999-2000', site plan of mounds (PDF page index 61) marked 'not to scale'; no structures."),
    ("shikarpur_2007-08_harappacom.pdf", "shikarpur", "auxiliary only", "Bhan and Ajithprasad, Excavations at Shikarpur 2007-2008 (harappa.com): Fig. 1, 0.5 m contour plan of 2008 with compass rose, 100 m scale bar, local grid, NH-8A, an unmetalled road, a stream and a mound polygon; no structures. Considered as an auxiliary plan for registration, but it shares no drawn feature with the measured plan."),
    ("shikarpur_lithic_studies_764.pdf", "shikarpur", "superseded", "PDF galley of Gadekar, Rajesh and Ajithprasad 2014: Figure 2 is an [image] placeholder; the figure itself was obtained from the HTML galley (jls764_html_fig_3262.png)."),
    ("iar_198788ar.pdf", "shikarpur", "rejected", "Indian Archaeology 1987-88 - A Review, entry 31 Excavation at Shikarpur (Valmiyo Timbo): text only; gives the setting beside NH-8A and the mound size."),
]
NOT_DOWNLOADED = [
    {"source": "Journal of Lithic Studies site (journals.ed.ac.uk/lithicstudies/article/view/764 and its galley URLs)", "town": "shikarpur", "outcome": "HTTP 503 'Page unavailable' from the University of Edinburgh on 2026-10-21; the HTML galley (view/764/1564, Wayback capture of 2017-06-17) listed the figure files, which were taken from Wayback captures"},
    {"source": "harappa.com pages and PDFs (direct)", "town": "both", "outcome": "HTTP 403 (Cloudflare challenge); files obtained through Wayback Machine captures"},
    {"source": "Shodhganga (shodhganga.inflibnet.ac.in) search for 'rakhigarhi' and 'shikarpur'", "town": "both", "outcome": "automated bot challenge (Anubis); not attempted"},
    {"source": "rarebooksocietyofindia.org copy of Nath's Rakhigarhi report", "town": "rakhigarhi", "outcome": "HEAD request: Content-Length 10532585, the size of the Internet Archive copy already in hand; not downloaded"},
    {"source": "Archaeopress 2023 Rakhigarhi volume, full text", "town": "rakhigarhi", "outcome": "sold, not open access; not downloaded"},
    {"source": "ResearchGate figure page for the JLS Shikarpur plan; ResearchGate 'A Study of Excavations Conducted at the Archaeological Site Rakhigarhi between 1960 To 2025'", "town": "both", "outcome": "requires sign-in or bot checks; not accessed"},
    {"source": "Ashoka University page 'The Harappan City of Rakhigarhi'; press reports (Deccan Herald, Outlook, ThePrint, Live History India)", "town": "rakhigarhi", "outcome": "read for context; photographs only, no plans"},
    {"source": "Internet Archive advanced search for Indian Archaeology - A Review after 2000-01, for 'rakhigarhi' and for 'shikarpur'", "town": "both", "outcome": "no later IAR volumes; the only Rakhigarhi item is Nath's report; no Shikarpur items"},
]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def main():
    log = json.loads((PKG / "fetch_log.json").read_text())
    downloads = []
    for r in log:
        town, st, why = USE[r["file"].split("/")[-1]]
        rr = dict(r)
        rr.update(town=town, status=st, assessment=why)
        downloads.append(rr)
    prior = [{"file": BASE + f, "sha256": sha(BASE + f), "bytes": (ROOT / (BASE + f)).stat().st_size, "town": t, "status": s,
              "assessment": a, "origin": "downloaded by the earlier search (town-axes plan-B); re-examined here"} for f, t, s, a in EARLIER]
    render = "data/raw/2026-10-21-plan-registration/S/renders/jls764_fig2_native.png"
    out = {"schema_version": "1.0", "agent": "S", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "downloads": downloads, "earlier_downloads_reexamined": prior, "examined_not_downloaded": NOT_DOWNLOADED,
           "renders": [{"file": render, "sha256": sha(render), "from": "data/raw/2026-10-21-plan-registration/S/downloads/jls764_html_fig_3262.png",
                        "how": "RGBA PNG flattened onto white with PIL, no resampling (the source is not a PDF page, so cptools.py render does not apply)"}],
           "rights": "All files are third-party material kept under data/raw/2026-10-21-plan-registration/S/ (git-ignored). The JLS article is CC BY 2.5 Scotland and the PLoS ONE article CC BY 4.0; the others keep their own terms."}
    (PKG / "sources.json").write_text(json.dumps(out, indent=1))
    print(len(downloads), len(prior))


if __name__ == "__main__":
    main()
