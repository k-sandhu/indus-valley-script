"""Apply the 2026-10-07 evidence overlay to the exploratory B2 registers.

Run from repository root after depth_queries.py. The overlay preserves the original
first-pass notes and adds observations, query statuses, expanded matrix and audit.
"""
from __future__ import annotations

import csv
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-06-evidence-census/collections-and-datasets/depth-pass"
DATE = "2026-10-07"

FIELDS = ["accession_number", "findspot", "excavation_number", "date", "dimensions", "material", "photographs", "multiple_views", "bibliography"]

# Page/API evidence was reviewed directly where the URL is listed; web-search result pages
# do not expose upstream HTTP response codes or complete per-query catalogue totals.
OBS = {
    "National Museum New Delhi": {
        "method": "web__run search_query: site:nationalmuseumindia.gov.in Harappan seal; opened official Harappan gallery and collection pages",
        "url": "https://www.nationalmuseumindia.gov.in/en/harappan-civilization",
        "http": None, "count": None, "basis": "No inscription-specific search total; official pages expose examples and gallery scope",
        "inscribed": 1, "types": "One script-bearing Pashupati seal record witness; other Harappan objects", "fields": ["accession number", "findspot", "date", "dimensions", "material", "image"],
        "evidence": ["https://nationalmuseumindia.gov.in/en/collections/index/6", "https://museumsofindia.gov.in/repository/record/nat_del-201-33-11909"],
    },
    "ASI site museums: Lothal, Kalibangan, Dholavira, Rakhigarhi": {
        "method": "NMMA public catalogue pages by museum and object type; Lothal Seals & Sealing category; six API terms also queried for museum APIs where available",
        "url": "https://nmma.nic.in/nmma/exploreMuseum.do?museum=ASM-KML",
        "http": None, "count": 133, "basis": "NMMA category count 'Seals & Sealing' for Archaeological Museum, Lothal; category includes seal/sealing objects, inscription status not individually adjudicated; direct response timed out in this pass",
        "inscribed": 1, "types": "One Lothal steatite seal with five Harappan signs is a minimum record witness; category's other 132 entries not individually adjudicated", "fields": ["reference number", "provenance", "museum", "object type", "photograph"],
        "evidence": ["https://nmma.nic.in/nmma/exploreMuseum.do?museum=ASM-KML", "https://nmma.nic.in/nmma/antiqDetail.do?object=32&refId=1425186", "https://nmma.nic.in/nmma/exploreMusObject.do?musname=GM-KAM&object=32"],
    },
    "CSMVS Mumbai": {"method":"web__run search_query: site:networksofthepast.csmvs.in Harappan seal; direct record opened", "url":"https://networksofthepast.csmvs.in/object/sealing/", "http":200,"count":1,"basis":"One direct indexed seal record observed; collection total not exposed","inscribed":1,"types":"Seal","fields":["accession number","findspot","date","dimensions","material","image"],"evidence":["https://networksofthepast.csmvs.in/object/sealing/"]},
    "Indian Museum Kolkata": {"method":"web__run search_query: site:museumsofindia.gov.in/repository/record Indus seal Kolkata; direct JATAN record reviewed in search excerpt", "url":"https://museumsofindia.gov.in/repository/record/im_kol-10382-A7251-Hr4869-26924", "http":None,"count":1,"basis":"One direct Harappa seal-amulet record witness; no institution-wide inscription count; exact-record HTTP status not captured","inscribed":1,"types":"Seal-amulet","fields":["accession number","findspot","date","dimensions","material","image"],"evidence":["https://museumsofindia.gov.in/repository/record/im_kol-10382-A7251-Hr4869-26924","https://museumsofindia.gov.in/repository/collection/ObjectType?museum=im_kol"]},
    "Allahabad Museum": {"method":"web__run search_query: Allahabad Museum Indus Harappan seal official collection; official central hall PDF opened", "url":"https://theallahabadmuseum.com/pdf/centralhallnew.pdf", "http":200,"count":None,"basis":"Collection overview names Mohenjo-daro objects and seal/sealings; no item-level query total","inscribed":None,"types":"Seals and sealings named in collection overview","fields":["object type","findspot/site-level provenance"],"evidence":["https://theallahabadmuseum.com/pdf/centralhallnew.pdf"]},
    "National Museum of Pakistan Karachi": {"method":"web__run search_query: National Museum Pakistan Karachi Harappa seal online collection; official Department of Archaeology museum page opened", "url":"https://doam.gov.pk/public/heritage-sites/792", "http":200,"count":None,"basis":"Official overview confirms Mohenjo-daro stamp seals; no object search/count surfaced","inscribed":None,"types":"Stamp seals and other Indus objects","fields":["collection overview only"],"evidence":["https://doam.gov.pk/public/heritage-sites/792"]},
    "Lahore Museum": {"method":"web__run search_query: Lahore Museum Harappa seal official collection search; official homepage opened", "url":"https://lahoremuseum.punjab.gov.pk/", "http":200,"count":None,"basis":"Official highlights include one Mohenjo-daro unicorn seal; no catalogue count","inscribed":1,"types":"Unicorn seal; other Indus holdings not counted","fields":["findspot","date","dimensions","description","image"],"evidence":["https://lahoremuseum.punjab.gov.pk/"]},
    "Harappa Museum": {"method":"web__run search_query: Harappa Museum Pakistan official online collection seal; Harappa.com seal archive reviewed as a separate research resource", "url":"https://www.harappa.com/category/slide-subject/seals", "http":None,"count":None,"basis":"No official museum item catalogue or museum-level total located; Harappa.com is not the museum catalogue","inscribed":None,"types":"Site research archive examples only","fields":["excavation code","findspot/trench","object type","image","description"],"evidence":["https://www.harappa.com/category/slide-subject/seals"]},
    "Mohenjo-daro site museum": {"method":"web__run search_query: Mohenjo-daro site museum collection seal official catalogue", "url":None,"http":None,"count":None,"basis":"No current official item-level catalogue surfaced in this search; holdings remain known from published CISI records","inscribed":None,"types":"Uncounted","fields":[],"evidence":["https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-volume-3-new-material-untr/"]},
    "Archaeological Museum Kalibangan": {"method":"NMMA public catalogue search by museum; category/object-type pages queried", "url":"https://nmma.nic.in/nmma/exploreMusObject.do?musname=GM-KAM&object=32", "http":None,"count":None,"basis":"Direct request timed out; catalogue snippets show object-wise pages but no seal-category total captured","inscribed":None,"types":"Seal category query attempted","fields":["title","reference number","provenance","state","photograph"],"evidence":["https://nmma.nic.in/nmma/exploreMusObject.do?musname=GM-KAM&object=32","https://nmma.nic.in/nmma/exploreMusObject.do?musname=GM-KAM&object=101"]},
    "Dholavira site museum": {"method":"web__run search_query: Dholavira site museum Harappan seal museum catalogue", "url":None,"http":None,"count":None,"basis":"Search did not surface a public item catalogue or count; no zero-holdings inference","inscribed":None,"types":"Uncounted","fields":[],"evidence":["https://www.harappa.com/blog/dholavira-and-its-mysterious-sign-board"]},
    "Rakhigarhi Site Museum and Interpretation Centre": {"method":"web__run search_query: Rakhigarhi museum Harappan seal collection official", "url":None,"http":None,"count":None,"basis":"Government/project pages surfaced, no item catalogue or query count","inscribed":None,"types":"Uncounted","fields":[],"evidence":["https://sansad.in/getFile/loksabhaquestions/annex/1711/AU3201.pdf?source=pqals"]},
    "British Museum": {"method":"British Museum Collection Online Indus Valley Civilisation term page and object pages queried/opened", "url":"https://www.britishmuseum.org/collection/term/x46239", "http":403,"count":724,"basis":"Local direct term-page request returned 403; web-search excerpt displayed 724 related objects, all object types; not an inscribed-object count; object-number dedup not independently repeated across all pages","inscribed":3,"types":"At least three script-bearing stamp-seal object-record witnesses from search excerpts; term page's broader 724 mixed objects are not partitioned by inscription","fields":["museum number","findspot","date","dimensions","material","images","bibliography","additional IDs"],"evidence":["https://www.britishmuseum.org/collection/term/x46239","https://www.britishmuseum.org/collection/object/A_1892-1210-1","https://www.britishmuseum.org/collection/object/A_1947-0416-4","https://www.britishmuseum.org/collection/object/A_1947-0416-1"]},
    "Louvre": {"method":"Louvre collections search q=Indus; public object JSON fallback", "url":"https://collections.louvre.fr/en/recherche?q=Indus", "http":429,"count":21,"basis":"Search page excerpt reports 21 broad Indus matches; local direct page request returned 429; not all are inscriptions","inscribed":1,"types":"At least one script-bearing SB 2425 seal object-record witness; result set also includes other seals, weights and sculpture","fields":["object/accession numbers","inscription system","findspot","date","dimensions","material","bibliography","two image URLs/rights statements"],"evidence":["https://collections.louvre.fr/en/recherche?q=Indus","https://collections.louvre.fr/ark:/53355/cl010176471.json"]},
    "Metropolitan Museum of Art": {"method":"Open Access API search for six terms; API route returned HTTP 410 for all terms; fallback web search surfaced object pages", "url":"https://collectionapi.metmuseum.org/public/collection/v1/search?q=Indus", "http":410,"count":None,"basis":"Six API queries returned 410 Gone; three seal record witnesses are named in the source list; no complete catalogue total","inscribed":3,"types":"At least three Indus seal object-record witnesses; inscription presence is explicit on some records, not field-verified on all three","fields":["object number","date","culture/period","dimensions","material","image","rights"],"evidence":["https://www.metmuseum.org/art/collection/search/38287","https://www.metmuseum.org/art/collection/search/324062","https://www.metmuseum.org/art/collection/search/324065"]},
    "Penn Museum": {"method":"web__run search_query: Penn Museum Indus seal Harappa; direct object record reviewed", "url":"https://collections.penn.museum/collections/object/329820", "http":200,"count":1,"basis":"One explicit object record witness; collection search result count unmeasured","inscribed":1,"types":"Seal","fields":["object ID","site","culture","inscription language","image"],"evidence":["https://collections.penn.museum/collections/object/329820"]},
    "MFA Boston": {"method":"web__run search_query: site:collections.mfa.org/search/objects Indus seal; public search surfaced a seal record of Gupta date, not confirmed Indus", "url":"https://collections.mfa.org/search/objects/*/Indus", "http":None,"count":None,"basis":"No confirmed Indus inscription record from query; search result was a later-period seal, so Indus count unmeasured","inscribed":None,"types":"Not confirmed","fields":["accession number","object place","medium","dimensions"],"evidence":["https://collections.mfa.org/objects/243823/seal"]},
    "Peabody Museum Harvard": {"method":"web__run search_query: Harvard Art Museums Peabody Indus seal; Harvard collection domain blocked to search tool", "url":"https://harvardartmuseums.org/collections", "http":None,"count":None,"basis":"Search tool blocked Harvard collection route; no Indus item count or record verified","inscribed":None,"types":"Unverified","fields":[],"evidence":["https://harvardartmuseums.org/collections"]},
    "Ashmolean": {"method":"web__run search_query: site:ashmolean.org/collections Indus seal Harappa; direct object record reviewed", "url":"https://jameelcentre.ashmolean.org/collection/4/6739/6740/all/per_page/50/offset/0/sort_by/seqn/object/11120", "http":200,"count":1,"basis":"One matched online object record (triangular prism sealing); collection-wide count unmeasured","inscribed":1,"types":"Terracotta sealing","fields":["accession number","findspot","date","dimensions","material","bibliography","image"],"evidence":["https://jameelcentre.ashmolean.org/collection/4/6739/6740/all/per_page/50/offset/0/sort_by/seqn/object/11120"]},
    "Bharat Kala Bhavan, Banaras Hindu University": {"method":"web__run search_query: Bharat Kala Bhavan Harappa seal online collection", "url":None,"http":None,"count":None,"basis":"No object-level Indus catalogue record or count surfaced","inscribed":None,"types":"Unverified","fields":[],"evidence":[]},
    "Museum of Archaeology and Anthropology, University of Cambridge": {"method":"web__run search_query: Cambridge MAA Indus seal object collection; catalogue existence page opened", "url":"https://collections.maa.cam.ac.uk/", "http":None,"count":None,"basis":"Searchable catalogue confirmed institutionally, but no Indus seal record/count surfaced in search","inscribed":None,"types":"Unverified","fields":["full catalogue records and digital images where available; field-level Indus record not inspected"],"evidence":["https://maa.cam.ac.uk/collections"]},
    "Musée Guimet": {"method":"web__run search_query: Musée Guimet Indus seal online catalogue; resources and official collection pages reviewed", "url":"https://www.guimet.fr/en/resources", "http":None,"count":None,"basis":"Official resources page points to collection catalogues/Joconde (3,203 Guimet descriptions); no Indus-specific count; direct status for this exact page not captured","inscribed":None,"types":"Indus holdings reported but no item query total","fields":["catalogue descriptions; object-level Indus fields not inspected"],"evidence":["https://www.guimet.fr/en/resources","https://collections.louvre.fr/en/ark:/53355/cl010169734"]},
    "Brooklyn Museum": {"method":"web__run search_query: Brooklyn Museum collection Indus Valley Harappan seal search; online search interface reviewed", "url":"https://opencollection.brooklynmuseum.org/search/advanced", "http":None,"count":None,"basis":"Search interface found, no Indus object count returned in search results","inscribed":None,"types":"Unmeasured","fields":["title","description","provenance","accession","medium","period","image and rights filter"],"evidence":["https://opencollection.brooklynmuseum.org/search/advanced"]},
    "Cleveland Museum of Art": {"method":"Open Access API searched six terms; Indus seal term returned three unique inscription-bearing seal records", "url":"https://openaccess-api.clevelandart.org/api/artworks/?q=Indus%20seal", "http":200,"count":3,"basis":"Deduplicated union of explicit API IDs among Indus seal results: 147416, 140095, 147417; generic q=Indus returned 10 total records, of which 3 were seals with inscriptions","inscribed":3,"types":"Three inscribed seals","fields":["accession number","title","date","culture","material","dimensions","image","CC0/open-access data"],"evidence":["https://openaccess-api.clevelandart.org/api/artworks/?q=Indus%20seal","https://www.clevelandart.org/open-access"]},
    "Royal Ontario Museum": {"method":"web__run search_query: Royal Ontario Museum collection Harappan seal Indus object", "url":"https://collections.rom.on.ca/", "http":None,"count":None,"basis":"No Indus object-level result/count surfaced; query result pointed to unrelated collection record","inscribed":None,"types":"Unmeasured","fields":[],"evidence":["https://collections.rom.on.ca/"]},
    "Museum für Asiatische Kunst Berlin": {"method":"web__run search_query: Berlin Museum Asiatische Kunst Indus seal object database; SMB online catalogue route surfaced", "url":"https://search.smb.museum/?sammlungen=Museum+f%C3%BCr+Asiatische+Kunst", "http":None,"count":None,"basis":"Catalogue route exists; no Indus object result/count verified","inscribed":None,"types":"Unmeasured","fields":[],"evidence":["https://search.smb.museum/?sammlungen=Museum+f%C3%BCr+Asiatische+Kunst"]},
    "Vorderasiatisches Museum Berlin": {"method":"web__run search_query: Vorderasiatisches Museum Berlin Indus seal collection search; SMB digitized catalogue route surfaced", "url":"https://search.smb.museum/?page=92&sammlungen=Vorderasiatisches+Museum", "http":None,"count":None,"basis":"Catalogue route exists, but no Indus-related record confirmed","inscribed":None,"types":"Unmeasured","fields":[],"evidence":["https://search.smb.museum/?page=92&sammlungen=Vorderasiatisches+Museum"]},
    "Iraq Museum Baghdad": {"method":"web__run search_query: Iraq Museum Baghdad Indus Valley seal public online catalogue", "url":None,"http":None,"count":None,"basis":"No official online collection catalogue result surfaced; published objects from Ur/Babylon held in other collections are not evidence of Iraq Museum holding","inscribed":None,"types":"Unverified","fields":[],"evidence":[]},
    "Bahrain National Museum": {"method":"web__run search_query: Bahrain National Museum Indus seals catalogue; official Hall of Dilmun page reviewed", "url":"https://culture.gov.bh/en/authority/cultural_sites/BahrainNationalMuseum/HallofDilmun/", "http":None,"count":None,"basis":"Official display page confirms Dilmun stamp-seal collection; no Indus inscriptions count; direct status for this exact page not captured","inscribed":None,"types":"Dilmun seals (not counted as Indus-script objects)","fields":["collection overview only"],"evidence":["https://culture.gov.bh/en/authority/cultural_sites/BahrainNationalMuseum/HallofDilmun/"]},
    "Kuwait National Museum / Failaka": {"method":"web__run search_query: Kuwait National Museum Failaka Indus seal collection; Penn record says impression made from original seal in Kuwait National Museum", "url":None,"http":None,"count":None,"basis":"One secondary catalogue witness describes a seal impression from an original at Kuwait National Museum; no official object catalogue/count","inscribed":None,"types":"Seal impression witness; Indus attribution not confirmed","fields":["site","culture affiliation note","collection reference in secondary record"],"evidence":["https://www.penn.museum/collections/object/267022"]},
    "Iran museums / Susa finds": {"method":"web__run search_query: Iran National Museum Susa Indus seal online collection catalogue", "url":"https://irannationalmuseum.ir/en/", "http":None,"count":None,"basis":"No Indus object catalogue count surfaced; Louvre’s Susa record is a separate holding, not evidence for an Iranian museum count","inscribed":None,"types":"Unverified","fields":[],"evidence":["https://irannationalmuseum.ir/en/"]},
    "Oman museums": {"method":"web__run search_query: Oman National Museum Indus seal online collection catalogue", "url":"https://www.nm.gov.om/en/home", "http":None,"count":None,"basis":"Official museum site located; no item-level Indus search result or count surfaced","inscribed":None,"types":"Unverified","fields":[],"evidence":["https://www.nm.gov.om/en/home"]},
    "UAE museums": {"method":"web__run search_query: UAE museum Indus Valley seal collection Abu Dhabi; official Louvre Abu Dhabi record reviewed", "url":"https://www.louvreabudhabi.ae/en/whats-online/art-from-home/dilmun", "http":None,"count":1,"basis":"One public seal record AM 4500, but described as Umm an Nar/Dilmun and not confirmed to bear Indus script; not counted as an Indus inscription; direct status for this exact page not captured","inscribed":0,"types":"One comparative Gulf seal record, excluded from confirmed Indus-script count","fields":["accession number","site","date","material","dimensions","description","image"],"evidence":["https://www.louvreabudhabi.ae/en/whats-online/art-from-home/dilmun"]},
    "Turkmenistan museums": {"method":"web__run search_query: Turkmenistan museum Indus seal Harappan online catalogue", "url":"https://museum.gov.tm/en/content/1676", "http":None,"count":None,"basis":"Official State Museum article notes Margush clay seal resemblance; not a verified Indus-script object or catalogue count; direct status for this exact page not captured","inscribed":0,"types":"Comparative seal only, excluded from Indus inscription count","fields":["site-level narrative only"],"evidence":["https://museum.gov.tm/en/content/1676"]},
    "Afghanistan museums": {"method":"web__run search_query: National Museum of Afghanistan Indus seal online collection; official ministry page and older museum catalogue references reviewed", "url":"https://moic.gov.af/en/department-archaeology-transfers-156-historical-artifacts-national-museum", "http":None,"count":None,"basis":"No current searchable item catalogue/count; older printed catalogue includes regional seals not confirmed Indus objects","inscribed":None,"types":"Unverified","fields":[],"evidence":["https://moic.gov.af/en/department-archaeology-transfers-156-historical-artifacts-national-museum"]},
    "Spurlock Museum, Illinois (comparator)": {"method":"web__run search_query: Spurlock Museum Indus seal online collection", "url":None,"http":None,"count":None,"basis":"Comparator search retained from first pass; no Indus object record verified in depth search","inscribed":None,"types":"Unverified","fields":[],"evidence":[]},
    "Smithsonian NMNH (replica comparator)": {"method":"Smithsonian Open Access API queried six terms with DEMO_KEY; all six current requests returned HTTP 429; no confirmed Indus collection objects counted", "url":"https://api.si.edu/openaccess/api/v1.0/search?q=Indus&api_key=DEMO_KEY", "http":429,"count":None,"basis":"See six per-term status/count records in local query-log; responses included rate limits and no confirmed held inscribed Indus originals","inscribed":None,"types":"No confirmed held original; replica comparator only","fields":["search-result title and record ID; object fields not validated"],"evidence":["https://api.si.edu/openaccess/api/v1.0/search?q=Indus&api_key=DEMO_KEY"]},
}

FIELD_UPDATES = {
    "National Museum New Delhi": {"accession_number": True, "findspot": True, "date": True, "dimensions": True, "material": True, "photographs": True},
    "ASI site museums: Lothal, Kalibangan, Dholavira, Rakhigarhi": {"accession_number": True, "findspot": True, "date": True, "dimensions": True, "material": True, "photographs": True},
    "CSMVS Mumbai": {"accession_number": True, "findspot": True, "date": True, "dimensions": True, "material": True, "photographs": True},
    "Indian Museum Kolkata": {"accession_number": True, "findspot": True, "date": True, "dimensions": True, "material": True, "photographs": True},
    "Lahore Museum": {"findspot": True, "date": True, "dimensions": True, "photographs": True},
    "British Museum": {"accession_number": True, "findspot": True, "excavation_number": True, "date": True, "dimensions": True, "material": True, "photographs": True, "bibliography": True},
    "Louvre": {"accession_number": True, "findspot": True, "date": True, "dimensions": True, "material": True, "photographs": True, "bibliography": True},
    "Metropolitan Museum of Art": {"accession_number": True, "date": True, "dimensions": True, "material": True, "photographs": True},
    "Penn Museum": {"accession_number": True, "findspot": True, "photographs": True},
    "Ashmolean": {"accession_number": True, "findspot": True, "date": True, "dimensions": True, "material": True, "photographs": True, "bibliography": True},
    "Cleveland Museum of Art": {"accession_number": True, "date": True, "dimensions": True, "material": True, "photographs": True},
}

def main() -> None:
    log_path = RAW / "query-log.json"
    if log_path.exists():
        api_log = json.loads(log_path.read_text(encoding="utf-8"))
        with (HERE / "museum-api-query-counts.csv").open("w", newline="", encoding="utf-8-sig") as f:
            cols = ["institution", "term", "exact_url", "date", "http_status", "endpoint_total", "returned_ids_count", "returned_object_ids", "count_basis", "raw_response_file", "error"]
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for q in api_log.get("attempts", []):
                w.writerow({"institution": q["institution"], "term": q["term"], "exact_url": q["url"], "date": q["date"], "http_status": q["http_status"], "endpoint_total": q["endpoint_total"], "returned_ids_count": q["returned_id_count"], "returned_object_ids": ";".join(q["returned_ids"]), "count_basis": q["count_basis"], "raw_response_file": q["response_file"], "error": q["error"]})

    register_path = HERE / "collection-register.json"
    data = json.loads(register_path.read_text(encoding="utf-8"))
    for row in data["collections"]:
        o = OBS.get(row["institution"])
        if not o:
            o = {"method": "No matching depth observation", "url": None, "http": None, "count": None, "basis": "Not queried in depth pass", "inscribed": None, "types": "Unmeasured", "fields": [], "evidence": []}
        for field, value in FIELD_UPDATES.get(row["institution"], {}).items():
            row.setdefault("record_fields", {})[field] = bool(row.get("record_fields", {}).get(field)) or value
        image_counts = {"Louvre": {"photograph_count": 2, "view_count": None, "image_count_basis": "two image URLs in SB 2425 JSON; the API does not label them as distinct views"},
                        "Cleveland Museum of Art": {"photograph_count": 1, "view_count": 1, "image_count_basis": "each of three object records provides web/print/full renditions of one source image; renditions are not counted as separate photographs"}}
        row["depth_pass"] = {
            "date": DATE, "method_or_exact_query": o["method"], "query_url_or_api": o["url"],
            "http_status": o["http"], "status_note": "null means browser search did not expose upstream HTTP status or no direct route was reachable; it is not a successful response",
            "result_count": o["count"], "count_basis": o["basis"],
            "confirmed_inscribed_or_sealed_indus_objects": o["inscribed"],
            "object_types": o["types"], "record_fields_seen": o["fields"], "evidence_urls": o["evidence"],
            **image_counts.get(row["institution"], {"photograph_count": None, "view_count": None, "image_count_basis": "No defensible distinct photograph/view count in reviewed search excerpt"}),
            "raw_search_log": "data/raw/2026-10-06-evidence-census/collections-and-datasets/depth-pass/web-search-log.json",
            "not_found_vs_not_queried": "query executed; null count is unmeasured, not zero" if o["url"] or "search_query" in o["method"] or "web__run" in o["method"] else "not queried",
        }
    data["depth_pass_on"] = DATE
    data["depth_pass_note"] = "Depth entries retain original first-pass fields. Search excerpts do not expose per-query HTTP codes or complete result totals; nulls are explicitly unmeasured. API/page status and raw bodies are in local raw depth-pass/query-log.json where captured."
    register_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    columns = ["institution", "region", "online_catalogue", "query", "query_date", "search_status", "result_count", "count_basis", *FIELDS, "image_data_licence", "api_or_bulk_download", "cisi_or_excavation_join", "depth_query_date", "depth_query_or_method", "query_url_or_api", "http_status", "depth_result_count", "depth_count_basis", "minimum_object_witness_count", "photograph_count", "view_count", "record_fields_seen", "evidence_urls", "notes", "source_ids"]
    with (HERE / "collection-register.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for row in data["collections"]:
            d = row["depth_pass"]
            item = {**row, **{k: bool(row.get("record_fields", {}).get(k, False)) for k in FIELDS},
                    "depth_query_date": d["date"], "depth_query_or_method": d["method_or_exact_query"], "query_url_or_api": d["query_url_or_api"], "http_status": d["http_status"],
                    "depth_result_count": d["result_count"], "depth_count_basis": d["count_basis"], "minimum_object_witness_count": d["confirmed_inscribed_or_sealed_indus_objects"], "photograph_count": d["photograph_count"], "view_count": d["view_count"],
                    "record_fields_seen": "; ".join(d["record_fields_seen"]), "evidence_urls": "; ".join(d["evidence_urls"]), "source_ids": ";".join(row.get("source_ids", []))}
            w.writerow(item)

    # Field matrix includes collection samples and datasets. True means a field was seen on the sampled record/schema, not that the institution consistently provides it.
    dataset = json.loads((HERE / "dataset-register.json").read_text(encoding="utf-8"))
    matrix_rows = []
    for row in data["collections"]:
        matrix_rows.append({"source": row["institution"], "source_kind": "collection", **{k: bool(row.get("record_fields", {}).get(k, False)) for k in FIELDS}, "field_basis": "first-pass sampled record; see depth_pass.record_fields_seen and evidence_urls"})
    for row in dataset["datasets"]:
        mf = set(row.get("metadata_fields", []))
        alias = {"accession_number": {"accession", "accession number", "object number", "museum number", "identifier", "cisi number"}, "findspot": {"findspot", "site", "provenance", "place"}, "excavation_number": {"excavation number", "excavation references", "excavation-idno", "excavation identifier"}, "date": {"date", "period", "chronology"}, "dimensions": {"dimensions", "measurements"}, "material": {"material"}, "photographs": {"photographs", "images", "photo", "photographs/views"}, "multiple_views": {"views", "sides", "multiple views", "photographs/views"}, "bibliography": {"bibliography", "references", "published reference"}}
        matrix_rows.append({"source": row["name"], "source_kind": "dataset", **{k: bool(mf & alias[k]) for k in FIELDS}, "field_basis": "metadata_fields in dataset-register.json; presence in dataset description, not independent field-level verification"})
    with (HERE / "metadata-field-matrix.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["source", "source_kind", *FIELDS, "field_basis"])
        w.writeheader(); w.writerows(matrix_rows)

    # No confirmed object-level joins. Preserve one near-candidate whose IDs differ and therefore cannot be counted.
    with (HERE / "paired-sample-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        cols = ["sample_slot", "museum_record", "corpus_record", "explicit_join_key", "fields_compared", "disagreements", "status", "reason"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        w.writerow({"sample_slot": 1, "museum_record": "British Museum 1947,0416.4 (https://www.britishmuseum.org/collection/object/A_1947-0416-4)", "corpus_record": "Lipi observed-face record_id 2478.1; source_cisi M-1906; metadata.excavation-idno HR 5635345", "explicit_join_key": "BM additional ID: Hr 5635; corpus metadata: HR 5635345 (not an exact identifier match)", "fields_compared": "object type and material agree broadly; accession/CISI crosswalk absent", "disagreements": "museum findspot Mohenjo-daro; corpus site Mohenjo-daro; excavation identifiers are not equal", "status": "unconfirmed candidate", "reason": "String-prefix resemblance is not an explicit shared identifier or published concordance; excluded from confirmed numerator."})
        for n in range(2, 31):
            w.writerow({"sample_slot": n, "status": "not filled", "reason": "No explicit shared identifier verified for this slot; not evidence of no corpus match."})

    # Update machine-readable dataset register with depth-pass scope, preserving original dataset counts.
    for row in dataset["datasets"]:
        row["depth_pass_review"] = {"date": DATE, "status": "carried forward; individual versions/exports not newly downloaded unless noted in protocol", "count_warning": "Prior counts and version bases remain as stated; not current verified totals."}
    (HERE / "dataset-register.json").write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Source register entries preserve the observed access mode for newly surfaced pages.
    src_path = HERE / "sources.json"
    sources = json.loads(src_path.read_text(encoding="utf-8"))
    known = {x.get("url") for x in sources}
    http_by_url = {}
    if log_path.exists():
        for record in api_log.get("attempts", []) + api_log.get("page_attempts", []):
            url = record.get("url")
            if url:
                http_by_url[url] = record.get("http_status")
    new_sources = []
    for i, row in enumerate(data["collections"], 1):
        d = row["depth_pass"]
        for j, url in enumerate(d["evidence_urls"], 1):
            if url in known:
                continue
            known.add(url)
            new_sources.append({
                "id": f"B2D-{i:02d}-{j:02d}", "title": f"{row['institution']} public collection/query witness",
                "authors": [row["institution"]], "year": None, "venue": "Official collection page/API or live-search result witness",
                "url": url, "source_type": "museum catalogue/query page or institutional overview",
                "access": (f"Direct HTTP response status {http_by_url[url]} on 2026-10-07; body or error saved in the local raw depth-pass log." if url in http_by_url and http_by_url[url] is not None else ("Direct request attempted 2026-10-07 but no HTTP response status was returned; timeout is in the local raw depth-pass log." if url in http_by_url else "Search-result excerpt reviewed 2026-10-07; upstream HTTP status not exposed and a direct response for this exact URL was not captured.")),
                "use": "Object-level metadata or collection/search discoverability only; count basis and limitations are stated in the depth_pass fields."
            })
    sources.extend(new_sources)
    for source in sources:
        if str(source.get("id", "")).startswith("B2D-"):
            url = source.get("url")
            if url in http_by_url:
                source["access"] = f"Direct HTTP response status {http_by_url[url]} on 2026-10-07; body or error saved in the local raw depth-pass log." if http_by_url[url] is not None else "Direct request attempted 2026-10-07 but no HTTP response status was returned; timeout is in the local raw depth-pass log."
            else:
                source["access"] = "Search-result excerpt reviewed 2026-10-07; upstream HTTP status not exposed and a direct response for this exact URL was not captured."
    src_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"collections": len(data["collections"]), "rows_with_depth_observation": sum(bool(x.get("depth_pass")) for x in data["collections"]), "confirmed_inscribed_counts": {x["institution"]:x["depth_pass"]["confirmed_inscribed_or_sealed_indus_objects"] for x in data["collections"] if isinstance(x["depth_pass"].get("confirmed_inscribed_or_sealed_indus_objects"), int)}, "paired_confirmed": 0, "paired_candidate_unconfirmed": 1, "matrix_rows": len(matrix_rows)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
