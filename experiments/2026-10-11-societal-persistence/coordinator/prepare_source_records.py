"""Write authored reading scopes and pins for coordinator source witnesses."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-11-societal-persistence/coordinator/sources-v1"

def pin(name):
    p = RAW / name
    return {"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    records = [
        {"id": "C01", "authors": ["Sophie Martin"], "year": 2004,
         "title": "The Cost of Restoration as a Way of Defining Resilience: a Viability Approach Applied to a Model of Lake Eutrophication",
         "publication": "Ecology and Society 9(2):8", "url": "https://ecologyandsociety.org/vol9/iss2/art8/inline.html",
         "depth": "selected abstract, introduction, viability definitions and discussion; equation images not reconstructed",
         "loci": ["web lines60–120", "web lines177–180", "web lines287–310"],
         "witnesses": [pin("martin2004.html"), pin("primary-web-v1.json"), pin("selected-web-v2.json")],
         "rights_status": "rights-unverified", "rights_notice": "Copyright2004 authors, published under license by Resilience Alliance; no blanket redistribution permission established",
         "rights_locus": "primary-web-v1.json web line3", "handling": "local-only",
         "supported_use": "Viability already asks which currently admissible states have an admissible future trajectory, conditional on controls, disturbances, objectives and horizon."},
        {"id": "C02", "authors": ["Monica L. Smith"], "year": 2016,
         "title": "Urban infrastructure as materialized consensus", "publication": "World Archaeology 48:164–178; author PDF uses internal pages1–15",
         "doi": "10.1080/00438243.2015.1124804", "url": "https://escholarship.org/content/qt2m83d6mq/qt2m83d6mq_noSplash_1a1fa895e685c057e889b47a60cb2597.pdf",
         "depth": "cover and internal article pages1–4; remaining article and case studies not inspected for this source record",
         "loci": ["PDF0-based0 cover metadata", "PDF0-based1–4/internal pp1–4"],
         "witnesses": [pin("smith2016.pdf"), pin("smith2016-selected-pages-0-4.txt")],
         "transformations": [{"tool": "pypdf PdfReader.extract_text", "pages_0_based": [0,1,2,3,4], "parent_sha256": pin("smith2016.pdf")["sha256"]}],
         "rights_status": "rights-unverified", "rights_notice": "Copyright2016 Taylor & Francis; public institutional author copy, open redistribution rights unverified",
         "rights_locus": "PDF0-based1 footer", "handling": "local-only",
         "supported_use": "Infrastructure maintenance involves changing providers, users and negotiations across generations; existing functionality does not imply a settled allocation of future maintenance obligations."},
        {"id": "C03", "authors": ["Ben Jervis"], "year": 2024,
         "title": "Repetition, persistence and generality: problematising the endurance of medieval urbanity", "publication": "World Archaeology pp125–138; online10September2024",
         "doi": "10.1080/00438243.2024.2387660", "url": "https://www.tandfonline.com/doi/abs/10.1080/00438243.2024.2387660",
         "depth": "publisher search-rendered abstract, introduction and Eat, fish, sleep, repeat section; direct full-page acquisition denied; no complete PDF reading",
         "loci": ["jervis2024-search-v5.json abstract/introduction", "same witness: Eat, fish, sleep, repeat, Townwall Street floor renewal discussion"],
         "witnesses": [pin("jervis2024-search-v5.json"), pin("selected-web-v2.json"), pin("manifest.json")],
         "access_limit": "normal direct request returned HTTP403; search-rendered primary text retained, search content is an access witness rather than independent excavation evidence",
         "rights_status": "rights-unverified", "rights_notice": "publisher licensing access advertised; no reusable full-source license verified in inspected scope", "handling": "local-only",
         "supported_use": "Repeated maintenance can preserve urban practices through changing buildings and demographic trajectories; this is an existing archaeological interpretation."},
        {"id": "C04", "authors": ["Ben Jervis"], "year": 2026,
         "title": "Thinking Through Change: Combining the Adaptive Cycle and Assemblage Theory to Assess Urban Change in Later Medieval Northern England",
         "publication": "Journal of Archaeological Method and Theory 33, article67;17June2026", "doi": "10.1007/s10816-026-09803-2",
         "url": "https://link.springer.com/article/10.1007/s10816-026-09803-2",
         "depth": "selected primary web text: yard maintenance, boundaries, temporality, constraints on archaeological resolution and conclusion; not every cited excavation",
         "loci": ["web lines146–176", "web lines177–187", "web lines240–285", "web lines302–334", "web lines383–394", "web lines616–619 rights"],
         "witnesses": [pin("jervis2026-web-v3.json"), pin("jervis2026-web-v4.json"), pin("jervis2026-metadata-v6.json"), pin("jervis2026.html")],
         "access_limit": "normal request returned HTTP200 with3038-byte challenge HTML, not article; primary web-rendered excerpts support reading",
         "rights_status": "explicit-license", "license": "CC BY4.0 for article with specified third-party credit-line exceptions", "license_url": "https://creativecommons.org/licenses/by/4.0/",
         "rights_locus": "jervis2026-metadata-v6.json web lines616–619", "handling": "local-only source witnesses in this task",
         "supported_use": "Repeated maintenance, persistent boundaries and component-specific temporalities already figure in archaeological endurance theory; the new procedure must add explicit measurement and inference rules."},
    ]
    output = {"created_utc": datetime.now(timezone.utc).isoformat(), "scope": "Coordinator-selected primary passages; acquired bytes do not imply complete reading", "sources": records}
    with (HERE / "SOURCES.json").open("x", encoding="utf-8") as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2); stream.write("\n")
    observations = [
        {"id": "CO01", "source_ids": ["C01"], "locus": "abstract/methods, web60–120 and177–180", "observation": "The viability construction distinguishes the set satisfying current constraints from the subset admitting a constraint-preserving trajectory under specified controls.", "type": "original theoretical precedent"},
        {"id": "CO02", "source_ids": ["C02"], "locus": "internal pp2–4/PDF0-based2–4", "observation": "The author identifies multiple infrastructure constituencies and maintenance obligations renegotiated across generations.", "type": "original interpretive precedent"},
        {"id": "CO03", "source_ids": ["C03"], "locus": "Eat, fish, sleep, repeat section, Townwall Street floor discussion", "observation": "The author uses successive floor and building surfaces to interpret repetitive maintenance and material demands in urban endurance.", "type": "original interpretive precedent; primary excavation reports not independently inspected here"},
        {"id": "CO04", "source_ids": ["C04"], "locus": "web146–176,177–187,240–285,302–334,383–394", "observation": "The article treats persistent urban relations as heterogeneous and sustained through repeated practices, while archaeological gaps limit a single coherent cycle reconstruction.", "type": "original interpretive precedent; selected passages"},
    ]
    with (HERE / "OBSERVATIONS.json").open("x", encoding="utf-8") as stream:
        json.dump({"observations": observations}, stream, ensure_ascii=False, indent=2); stream.write("\n")
    print(json.dumps({"sources":len(records),"observations":len(observations)}))

if __name__ == "__main__":
    main()
