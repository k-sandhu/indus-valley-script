"""Save the independent visual readings after inspecting original-page PDF crops."""
from pathlib import Path
import csv
import json

ROOT=Path(__file__).parent
manifest=json.loads((ROOT/"sampling_manifest.json").read_text(encoding="utf-8"))
# Manual original-image readings; no OCR, templates, matches, or crosswalk tables were read.
values={
 (20,1,6):(23,135), (20,2,12):(50,517), (20,3,2):(65,183),
 (20,3,12):(71,489), (20,4,31):(107,342), (20,4,34):(109,561),
 (20,5,22):(121,1), (20,6,5):(124,767), (20,6,14):(126,723),
 (20,6,32):(136,717), (20,7,34):(158,319), (20,8,10):(166,277),
 (20,8,32):(179,789), (20,9,31):(201,52), (20,9,33):(202,53),
 (21,0,8):(207,349), (21,1,7):(227,229), (21,1,21):(235,117),
 (21,1,23):(237,34), (21,1,30):(241,488), (21,3,1):(270,66),
 (21,3,4):(270,58), (21,4,6):(290,435), (21,4,32):(306,80),
 (21,5,18):(317,407), (21,6,20):(336,361), (21,7,17):(355,387),
 (21,7,19):(355,684), (21,9,9):(393,406), (21,9,13):(396,599),
}
ambiguities={(21,4,6):[435,436],(21,9,9):[406,405]}
rows=[]
for cell in manifest["sample"]:
    key=(cell["pdf_page"],cell["column_0based"],cell["row_0based"])
    upper,lower=values[key]
    ambiguous=key in ambiguities
    rows.append({**cell,"upper_rank":upper,"lower_stable_finnish_code":lower,
                 "confidence":"medium" if ambiguous else "high",
                 "alternative_lower_codes":ambiguities.get(key,[]),
                 "confidence_note":"Faint final digit; 5/6 distinction is not fully secure in original scan." if ambiguous else "Both printed labels visually clear in original-PDF crop."})
result={"audit_type":"independent manual transcription of printed numeric labels only",
        "source_sha256":manifest["source_sha256"],"seed":manifest["seed"],
        "grid_verified":"35 row levels each on PDF20/21;10 columns;PDF21 finalcolumn occupied rows0–21",
        "blindness":"Read original PDF images and own rendered crops only; did not inspect root numeric OCR, templates, matches, or expected label outputs.",
        "glyph_limitation":"Glyph drawings are locator context; this audit does not establish glyph identity, phonetics, or meanings.",
        "high_confidence_cells":28,"medium_confidence_cells":2,"labels":rows}
(ROOT/"manual_numeric_labels.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
with (ROOT/"manual_numeric_labels.csv").open("w",newline="",encoding="utf-8") as f:
    columns=["pdf_page","printed_page","column_0based","row_0based","upper_rank","lower_stable_finnish_code","confidence","alternative_lower_codes","image"]
    writer=csv.DictWriter(f,fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({c:json.dumps(row[c]) if c=="alternative_lower_codes" else row[c] for c in columns})
print(f"Saved {len(rows)} cells,28 high confidence,2 medium with explicit alternatives.")
