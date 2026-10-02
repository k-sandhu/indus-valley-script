"""Conservative author-ordered XML controls; never invent order inside simultaneous units."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).parent
SOURCE=ROOT/"sources/sproat_2014_corpora/corpora"
OUT=ROOT/"nonlinguistic_controls"
OUT.mkdir(exist_ok=True)

def clean(text):
    return " ".join((text or "").split())

def text(element,tag):
    return clean(element.findtext(tag))

def describe_unit(element,path):
    if element.tag=="symbol":
        name=text(element,"title")
        uncertain=bool(element.get("reliability") or element.find("alternative") is not None or not name)
        return name,{"kind":"symbol","xml_path":path,"title":name,"attributes":dict(element.attrib),"alternative":text(element,"alternative"),"description":text(element,"description")},uncertain
    if element.tag=="symbolUnit":
        # Simultaneous composite is one token, not invented adjacency among its members.
        members=[]; uncertain=False
        for i, child in enumerate(element):
            if child.tag not in {"symbol","symbolUnit"}: continue
            token,meta,u=describe_unit(child,f"{path}/{child.tag}[{i+1}]")
            members.append({"token":token,"metadata":meta}); uncertain |= u
        token="UNIT("+"|".join(member["token"] for member in members)+")"
        uncertain |= bool(element.get("reliability") or not members)
        return token,{"kind":"simultaneous_composite","xml_path":path,"members":members,"description":text(element,"description"),"attributes":dict(element.attrib)},uncertain
    raise ValueError(element.tag)

def corpus(name):
    src=SOURCE/f"{name}.xml"
    doc=ET.parse(src).getroot()
    rows=[]; excluded=Counter(); tags=Counter(); n_docs=0
    for ei,entry in enumerate(doc.findall("entry"),1):
        bib=entry.find("bib")
        bibliography={c.tag:clean(c.text) for c in bib} if bib is not None else {}
        for di,document in enumerate(entry.findall("document"),1):
            n_docs += 1
            dt=document.find("docText")
            path=f"/collection/entry[{ei}]/document[{di}]"
            if dt is None:
                excluded["missing_docText"]+=1; continue
            children=list(dt)
            for child in children: tags[child.tag]+=1
            if any(child.tag not in {"symbol","symbolUnit","description"} for child in children):
                excluded["nested_side_line_or_other_layout"]+=1; continue
            tokens=[]; units=[]; uncertain=False
            for ci,child in enumerate(children,1):
                if child.tag=="description": continue
                token,meta,u=describe_unit(child,f"{path}/docText/{child.tag}[{ci}]")
                tokens.append(token);units.append(meta);uncertain |= u
            if uncertain:
                excluded["uncertain_or_alternative_transcription"]+=1;continue
            if len(tokens)<3:
                excluded["fewer_than_three_ordered_units"]+=1;continue
            desc=text(document,"description")
            row={"record_id":f"{name}:e{ei:04d}:d{di:04d}","sequence":tokens,
                 "complete_observed":True,"single_line":True,"max_damage":0,"max_uncertainty":0,
                 "object_type":document.get("type","UNKNOWN"),"description":desc,
                 "origin":document.get("origin","UNKNOWN"),"source_page":text(document,"page"),
                 "source_xml_path":path,"source_bibliography":bibliography,"units":units,
                 "author_xml_order_preserved":True,"side_id":"single_author_docText"}
            if name=="WeatherIcons":
                # Repeated forecasts from one station have overlapping target dates.
                m=re.match(r"([^:]+):\s*(.+)",desc)
                if not m:
                    excluded["unparsed_weather_station_time"]+=1;continue
                station,timestamp=m.groups()
                row.update(site=station,station_id=station,forecast_timestamp=timestamp,
                           artifact_id="weather-station:"+station,
                           order_basis="five-day forecast, one icon per successive day; Sproat2014 supplement s7")
            else:
                row.update(site=row["origin"],artifact_id=row["record_id"],
                           order_basis="published authors' XML order of the vertical pole stack; simultaneous symbolUnit preserved as one composite token")
                row["physical_alias_limitation"]="Stable XML document IDs are not independent physical-object identity. Similar named poles across sources can recur."
                if desc:
                    label=re.sub(r"[^\w]+"," ",desc.lower()).strip()
                    row["object_family_id"]="possible-pole:"+row["origin"]+":"+label
                    row["grouping_rule"]="Conservative equal-description/equal-origin grouping; may overmerge different poles. Unnamed poles retain XML-document ID; cross-source physical aliases can remain unknown."
                else:
                    row["object_family_id"]=row["record_id"]
                    row["grouping_rule"]="XML document only; unnamed pole physical identity unavailable."
            rows.append(row)
    out=OUT/f"{name}_author_ordered.jsonl"
    out.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in rows),encoding="utf-8")
    return {"corpus":name,"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
            "source_documents":n_docs,"direct_docText_tags":dict(tags),"included_length3plus":len(rows),
            "included_tokens":sum(len(r["sequence"]) for r in rows),
            "included_types":len({t for r in rows for t in r["sequence"]}),
            "unique_strings":len({tuple(r["sequence"]) for r in rows}),
            "station_or_origin_count":len({r["site"] for r in rows}),
            "excluded":dict(excluded),"file":str(out.relative_to(ROOT)),
            "output_sha256":hashlib.sha256(out.read_bytes()).hexdigest()}

if __name__=="__main__":
    summaries=[corpus("WeatherIcons"),corpus("TotemPoles")]
    (OUT/"flatten_manifest.json").write_text(json.dumps(summaries,indent=2),encoding="utf-8")
    print(json.dumps(summaries,indent=2))
