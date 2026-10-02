# Registered physical views and collection records

Read the [report](REPORT.md) for the acquired views and the next observation. The [protocol](PROTOCOL.md) fixes the targets. [Observations](observations-v2.json) preserve source coordinates, native-image dimensions, crop hashes and the coded result for 19 publication panels. The [second reading](second-reading.json) checks L190's contact shape.

The [source manifest](source-manifest.json), [access log](access-log.json), [search log](search-log.json) and [record locators](record-locators.json) retain successful acquisitions and failed routes. The [alternative-scan comparison](alternative-scan-check.json) shows why the second CISI1 PDF adds no image detail. The [request record](request-packet.json) identifies the locally saved, unsent observation packet.

[Preparation](prepare.py) extracts the declared crops and keeps the detailed catalogue table local. [Assembly](assemble.py) records source and request metadata. Run [verify.py](verify.py) manually to check the [passing verification output](verification-v2.json). The [first check](verification.json) preserves two output-link failures. Existing source assets are required; their paths and hashes are in the manifest. The [retrospective](RETROSPECTIVE.md) records the approach, acquisition failures and the corrected crop pilot.
