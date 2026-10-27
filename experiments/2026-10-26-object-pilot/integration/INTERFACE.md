# Integrated pilot interface

The frozen local endpoint is `D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot/integration-v1/`. It contains `pilot-integrated-v1.json`, `catalogue-integrated-v1.html` and `missing-evidence-integrated-v1.json`. The standalone HTML uses file URIs and keeps the underlying source assertions and coordinates visible. Detailed records remain local-only.

The integration retains all 539 assertions from register v4 and appends two explicit source-conflict review assertions. Twenty targets and 274 Dholavira candidate relationships remain unchanged. The two affected cards display the safe source-qualified statements and the blocked identity or context claims. The L-164 Rao plate remains an unresolved candidate page. No comparison entity becomes a pilot card.

Six verified pilot catalogue-view links from image recovery v2 are attached to the relevant cards. Each target groups identical image paths, so L-163 A and C share one displayed composite crop. The full image pass recovers fourteen index links against the October 13 image-file table. It establishes zero newly available pilot photographs. Earlier source-page photographs remain part of the baseline.

The combined evidence queue preserves every original register queue row and its priority and reason. Its top-priority list adds the exact ASI photograph and specimen registers and HARP object-card records needed to settle the two conflicts, alongside the accession-to-CISI bridges needed by the Dholavira targets.

Run the temporary preview from repository root:

```text
python -B -X utf8 experiments/2026-10-26-object-pilot/integration/preview_catalogue.py --html D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot/integration-v1/catalogue-integrated-v1.html --port 8765
```

Open `http://127.0.0.1:8765/`. Stop the terminal command with Ctrl-C when review ends. The server binds only to 127.0.0.1 and rewrites explicit file links to 57 allowlisted file routes within the checkout or D: project root. It serves no directory listing and rejects arbitrary paths. The standalone file-URI HTML remains the deliverable; this temporary local service publishes nothing externally.

`integrate.py` exclusively creates the frozen integration-v1 endpoint. Reproduction requires an unused endpoint path before running it. `manifest-v1.json` binds the four detailed inputs and the unchanged upstream renderer to output hashes. `validation-v1.json` records ten passing author checks, including actual source hashes, retained base assertion values and unchanged target membership. Preview preparation and HTTP checks pass. Browser QA and independent integrated review remain separate records. The author is gpt-6.1-sol using the Codex collaboration harness.
