# Follow-up for package B2 from the coordinator: a depth pass

Your registers are a useful frame, but only one collection has a captured catalogue count, eleven rows were not queried, six downloads failed, and the 30-object paired audit validated none. The user's question is whether all findable evidence is indexed and with how much metadata, so each row needs a documented query result. Keep your existing files' history: write a dated amendment to `PROTOCOL.md`, then update the registers, field matrix, paired audit, `REPORT.md`, `README.md`, `RETROSPECTIVE.md` and `registry-entry.json`.

## Query every collection with a documented method

For each collection row, run at least one concrete search and record the exact query URL or API call, the date, the HTTP status, the result count and the record fields seen, saving raw responses in the local raw directory. If a route fails, try the alternatives below before recording a failure, and record each attempt. Use several query terms per collection (for example "Indus", "Harappa", "Harappan", "Mohenjo-daro", "Mohenjodaro", "Chanhu-daro", "Lothal", "Indus seal", "steatite seal", "unicorn seal") and report counts per term with duplicates removed by object number.

Known public routes, to check and use where they work:
- Metropolitan Museum of Art: `https://collectionapi.metmuseum.org/public/collection/v1/search?q=...` and `/objects/{id}`; open access images are CC0.
- Art Institute of Chicago: `https://api.artic.edu/api/v1/artworks/search?q=...`.
- Cleveland Museum of Art: `https://openaccess-api.clevelandart.org/api/artworks/?q=...`.
- Smithsonian (National Museum of Asian Art and others): `https://api.si.edu/openaccess/api/v1.0/search?q=...&api_key=DEMO_KEY`.
- Harvard Art Museums and the Peabody: public search pages; the Harvard API needs a key, so use the web search pages.
- British Museum: collection search pages with place and culture filters (for example the Indus Valley Civilisation term page you found), counted by object type.
- Louvre: `https://collections.louvre.fr/` search, with per-object JSON at `https://collections.louvre.fr/ark:/53355/{id}.json`.
- Penn Museum: `https://www.penn.museum/collections/search.php?term=...`.
- Museum of Fine Arts Boston: `https://collections.mfa.org/search/objects/*/...`.
- Berlin State Museums: `https://recherche.smb.museum/` and its API.
- Royal Ontario Museum, Ashmolean, Brooklyn and Musée Guimet: their public collection search pages.
- Indian national museums: the Museums of India portal (`museumsofindia.gov.in`, covering the National Museum New Delhi, the Indian Museum Kolkata, the Allahabad Museum and others) and each museum's own site; the ASI site museums; CSMVS Mumbai.
- Pakistan, the Gulf, Iraq, Iran, Oman, Turkmenistan and Afghanistan: record whether any online catalogue exists, using official museum and ministry sites.

For each collection report: inscribed or sealed Indus objects found (seals, sealings, tablets, inscribed pottery, other), the count basis, fields provided (accession number, findspot, excavation number, date, dimensions, material, number of photographs and views, bibliography or CISI reference), image and data licence, and API or bulk access.

## Complete the paired audit

Select 30 objects that a museum record and a corpus record both describe, joined by an explicit shared identifier: an excavation number, a CISI number, a Mackay, Marshall or Vats catalogue number, or a published concordance. The British Museum, Met, Penn, Louvre and Indian museum records are the likeliest sources; corpus side identifiers are in `data/normalized/lipi_observed_faces.jsonl` (`source_cisi`, `metadata.excavation-idno`) and the CISI volumes. Compare fields and record disagreements. If fewer than 30 explicit joins exist, report how many you found, which identifiers made each join possible, and which candidate joins remain unconfirmed.

## Report

State, with numbers and bases, how many Indus inscribed objects are openly searchable online, in which institutions, with which fields, and under which licences; which major holdings have no online catalogue; and what fraction of sampled museum records can be joined to corpus records. Keep "not found" separate from "not queried".
