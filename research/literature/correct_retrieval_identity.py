"""Preserve failed/misidentified acquisition evidence; correct bibliographic identities."""
import json
from pathlib import Path
root = Path(__file__).parent
path = root / "source_retrieval_log.json"
records = json.loads(path.read_text(encoding="utf-8"))
for record in records:
    if record["id"] == "sproat_2010":
        record["requested_identity"] = "Sproat2010 Indus statistical critique"
        record["identity_verified"] = False
        record["actual_title"] = "Book Review: Natural Language Processing with Python by Steven Bird, Ewan Klein, and Edward Loper"
        record["status"] = "misidentified download; unrelated to Indus critique"
        record["correction"] = "Use sproat_2010_last_words, ACL J10-3012, for the Indus statistical critique. Original acquisition and bytes retained."
    if record["id"] == "kenoyer_1998_ancient_cities":
        record["requested_identity"] = "Kenoyer1998 Ancient Cities of the Indus Valley Civilization"
        record["identity_verified"] = False
        record["actual_title"] = "Decipherment of the Indus script"
        record["publication"] = "unverified"
        record["status"] = "library landing/download mismatch; unverified claimant essay"
        record["correction"] = "Library landing page names Kenoyer1998, but the downloaded 33-page PDF is a different essay. No evidence for Kenoyer1998 was obtained. Original bytes retained."
    if record["id"] == "sproat_2014":
        record["identity_verified"] = False
        record["status"] = "dead PDF route returned generic LSA HTML; paper not acquired through this route"
        record["correction"] = "HTTP200 is a generic LSA page, not the requested article. The primary 2014 supplement and author's XML corpus were acquired separately."
    if record["id"] == "sproat_2014_corpora":
        record["identity_verified"] = True
        record["actual_content_type"] = "application/zip"
        record["correction"] = "Generic retrieval helper named non-PDF bytes .html; raw bytes are a valid ZIP. Unmodified archive preserved, safely extracted under sources/sproat_2014_corpora with per-file manifest."
path.write_text(json.dumps(records, indent=2), encoding="utf-8")
path = root / "evidence_and_novelty_matrix.md"
text = path.read_text(encoding="utf-8")
text = text.replace("[Sproat 2010](https://aclanthology.org/J10-4009.pdf), pp.795–800", "[Sproat 2010](https://aclanthology.org/J10-3012.pdf), pp.588–592")
text = text.replace("Version 2, updated", "Version 3, updated")
text = text.replace("H2238 remains without a retrieved primary illustration.", "H2238's excavation number H95-2613 matches Meadow and Kenoyer2000 Fig.4 specimen18 (internal14–15/PDF15–16), whose drawing supports three short strokes beside the diamond-like sign; photographs and fine-glyph identity remain unverified. See `h2238_primary_audit.md`.")
path.write_text(text, encoding="utf-8")
print("Corrected both retrieval identities and Sproat matrix citation; original acquisitions retained.")
