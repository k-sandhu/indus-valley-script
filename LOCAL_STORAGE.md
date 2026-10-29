# Local storage

Bulk local inputs live under `D:\projects\indus_valley_script` on this workstation. The working Git checkout remains at `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. Directory junctions and file links connect the historical paths to their D: copies. Existing relative paths, source locators and frozen manifests retain their meaning.

The storage root contains `data/raw/`, `data/lipi/`, `data/mayig/`, `data/indus_website/`, `data/normalized/`, `data/six-hour/`, downloaded literature, scratch files and large ignored outputs. The migration manifest at `D:\projects\indus_valley_script\migration-2026-10-24.json` lists each moved file with its byte count and SHA-256. Its verification file records the check before the C: copies were removed. The release package moved from `experiments/` to `maintenance/` on 28 October, and its D: copies followed on 29 October; `relocation-2026-10-29.json` in the storage root lists the old and new physical path and hash of each linked file. Tracked research records and code remain in the checkout.

Put new acquisitions, imagery, rendered plans, DEM tiles, OCR, source-derived payloads and large scratch files in `D:\projects\indus_valley_script\data\raw\YYYY-MM-DD-slug\`. The equivalent `data/raw/YYYY-MM-DD-slug/` path in the checkout reaches the same directory through a junction. Record both the repository-relative logical path and the physical D: path in new acquisition records. Keep local inputs out of Git under the existing redistribution rules.

Run project commands from the checkout root. Before a download or restoration, check that D: is mounted and `data/raw` resolves to D:. A junction target missing from D: is a missing input; restore it from its acquisition record or backup. Do not replace the junction with a new C: directory. Do not recursively follow links when inventorying or cleaning the checkout. D: is local storage and needs its own backup.

Other machines can acquire inputs at the documented relative paths or map those paths to a different storage volume. The D: location is this workstation's storage choice, not a condition for reproducing the research.
