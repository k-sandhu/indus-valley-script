# Building the architectural explorer

We began with the existing town-axis and infrastructure packages, then checked named building dimensions against the held Dholavira report and public excavator captions. This kept the work close to already documented evidence while adding an interaction the static atlas lacked: an orbitable, exportable metric model with each feature's sources beside it.

## Source choices and limits

The browser could not fetch the large UNESCO management PDF, and the first Dholavira nomination download returned an access error. We used the previously held 127 MB preliminary report rather than claiming those failed routes supplied a new witness. A text search within that scan found the reservoir description on printed pp. 149–150, correcting an early search-result locator from another report rendition. We checked the body text and retained the scan's provisional edition status.

The scan also exposes a city-length conflict between its prose and table. The model uses the repeated prose value and records the conflicting table entry. For the reservoir, source checking separated ordinary depth from a deeper localized probe; applying 10.60 m uniformly would have exaggerated the basin geometry. The exact probe outline and stair coordinates remain display assumptions. We chose district patches in the city contexts because a common survey frame and complete phase plans were missing.

## Renderer repairs

Run-v1 failed to execute because the inspection API had a misplaced closing parenthesis. Node's syntax checker located it. Run-v2 executed, but visual review showed a more consequential display error: sorting large Canvas polygons by their centres let the ground hide the western mound and monuments. We preserved both endpoints.

Run-v3 replaced the geometry pass with native WebGL and a depth buffer. Canvas now carries the labels and rulers. Surface picking uses interpolated triangle depth rather than the old polygon order. The implementation has no vendor dependency, and the browser reports nonempty mesh pixels for all seven scenes. A simplified Canvas fallback is labelled when WebGL is unavailable; its occlusion handling is limited.

Run-v4 reduced the desktop canvas minimum height so that the layer controls remain visible. It passed all 32 browser checks. Run-v5 adds per-feature page locators, a clear display-sensitivity field and explicit assumed placement for the reservoir stairs. Its repeated checks pass with the same geometry counts and pixel counts. The stable entry points to run-v5, preserving earlier endpoints.

## Verification and delivery

The final deterministic check passes 769 tests. It independently parses each OBJ, checks its indices and extents, and compares metric rulers and selected geometry with published quantities. Browser checks cover all models, surface selection, feature focus, Plan, orbit, keyboard and zoom controls, layers, height sensitivity, downloads and operation with network access disabled. A 390 px layout has no horizontal overflow. We visually inspected the seven models and the mobile page. Physical touch hardware and independent archaeological review remain untested.

We retained all downloaded sources, screenshots and browser download files on D:. The repository contribution contains original procedural geometry, source pointers, code, reports and check records. Shared data inventories, generated knowledge maps and previous packages remain unchanged. No script benchmark population was opened and no publication was performed.

The strongest supported reading is that the available architectural measurements already support useful metric inspection. The next model should replace a specific uncertain field with a registered observation: the reservoir floor and steps, a gateway section or a city street network tied to a building episode. That evidence can decide which present assumptions should be retained or removed.
