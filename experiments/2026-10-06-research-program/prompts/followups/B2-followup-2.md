# Second follow-up for package B2 from the coordinator: focused pass on GPT-6.1-Sol

The coordinator has switched this session to GPT-6.1-Sol. Keep every existing file and add a dated amendment to `PROTOCOL.md` for this pass. Two gaps matter most for the user's question, so concentrate on them rather than widening the register.

## 1. Counts and fields for the largest holdings

For each of these holdings, find the number of inscribed Indus objects (seals, sealings, tablets, inscribed pottery and other inscribed objects) that its public catalogue exposes, the fields each record provides, and the image licence: the National Museum New Delhi and the other museums on the Museums of India portal (`museumsofindia.gov.in`, which has object pages with accession numbers); ASI site museums where an online catalogue exists; the British Museum (count inscribed seals and sealings, not all Indus-related objects); the Penn Museum; the Louvre; the Metropolitan Museum (its collection API returned HTTP 410, so use the website search and object pages); the Museum of Fine Arts Boston; and the National Museum of Pakistan, Karachi. Record every query with its URL, date, status and the count you read, and save raw responses in the local raw directory. Where a catalogue exposes only a sample, say so.

## 2. A join by excavation number

The corpus export `data/normalized/lipi_observed_faces.jsonl` records an excavation identifier (`metadata.excavation-idno`) for 1,831 Mohenjo-daro faces and 2,652 Harappa faces, and CISI identifiers in `source_cisi`. Museum records for Mohenjo-daro and Harappa objects often give a field or excavation number (for example DK, HR, VS or SD numbers from the Marshall, Mackay and Vats excavations) or a CISI reference. Collect museum records that carry such numbers and match them against the corpus fields with exact and normalized matching (case, spacing, punctuation, leading zeros), keeping uncertain matches separate. Report how many museum records carry a usable identifier, how many match, and for matched pairs compare site, object type, material, dimensions and inscription description. The earlier candidate where `Hr 5635` and `HR 5635345` disagree should be resolved or explained.

Update the registers, field matrix, paired audit, `REPORT.md`, `README.md`, `RETROSPECTIVE.md` and `registry-entry.json`. In the report, answer with numbers and bases: how many inscribed Indus objects are openly searchable in the main holdings, which fields they carry, and what fraction can be joined to corpus records.
