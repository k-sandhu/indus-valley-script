# Brief for the registrars: registering published site plans to satellite imagery

You are a registrar for the plan-registration package of the Indus research repository at `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (run every command from that root, with Python 3.13). Your job is to find features that appear both on an excavator's published plan and on current satellite imagery, and to record each feature's pixel position on the plan and on the imagery. The coordinator later fits a similarity transform (rotation, scale and translation) from your points. You choose and record points; you do not compute or report any orientation.

Your registrar label (R1 or R2), your agent label (for example R1-G2) and the plans assigned to you are given in your assignment message. Another registrar works on the same plans independently.

## What you must not open

Do not open, list or search inside any of these: `experiments/2026-10-21-town-axes/`; anything under `data/raw/2026-10-21-town-axes/` except the plan renders in `plan-B/renders/` and the publications in `plan-B/downloads/`; `experiments/2026-10-21-town-orientations-verification/` and its raw data; the other registrar's directories (`control-R1/` or `control-R2/`, whichever is not yours, and the matching folders under `data/raw/2026-10-21-plan-registration/`), `experiments/2026-10-21-plan-registration/PROTOCOL.md`, `knowledge/conjectures/`, `knowledge/questions/Q-1032*`, `knowledge/directions/` and `knowledge/registry/attempts/TOWN-*`. These hold orientation values and the reasons for this work, and you should choose points without knowing either. If you come across a statement of a wall's or a town's orientation anyway, stop reading it, and record in your control file's notes what you saw and where.

## The plans

`experiments/2026-10-21-plan-registration/plans-v1.json` lists each plan's id (`town:source_id`), the render file you must work on, the publication and page it came from, the scale bar in metres per pixel where the plan has one, and published site coordinates. The coordinates are unchecked and may be off by several hundred metres; find the site from the plan's own features. Your pixel coordinates must refer to the exact render file named in `render`. Where `render_alternative_same_pixels` is given (an inverted or masked copy), it has the same pixel frame and you may view whichever is clearer. You may read the rest of the publication for context, such as site descriptions, other figures and the location of datum points.

## Tools

`experiments/2026-10-21-plan-registration/code/cptools.py` has the commands you need; run it with `--help`. In brief:

- `mosaic --reg <agent> --name <name> LAT LON HALF_M --z 18` fetches Esri World Imagery around a point and writes a PNG and a JSON file with its georeferencing. Zoom 17 to 19 is allowed; 19 is sharper where it exists. `--release <id>` fetches an older Esri Wayback release instead; `releases LAT LON` lists the releases that hold distinct imagery at a point, and `meta LAT LON` reports the current imagery's source and date.
- `grid IMAGE X0 Y0 W H --scale S --step G --reg <agent>` crops any image (a plan render or a mosaic) and draws a grid labelled in that image's own pixel coordinates. The Read tool shows large images downscaled, so read positions from gridded crops at a scale where the feature is several pixels wide. `--points <control file> --side plan` or `--side image` marks the points you have recorded.
- `px2ll` and `ll2px` convert between mosaic pixels and longitude and latitude.
- `check <control file>` fits each link with the frozen error model and prints the number of points, the fitted metres per pixel and its ratio to the scale bar, χ² per degree of freedom, the mirror-image test, the rotation error, each point's residual in metres, and whether the link is accepted. It does not print the rotation, and you should not compute it.
- `overlay <control file> --reg <agent> --link 0 --mosaic <mosaic json>` draws the plan's dark ink, transformed by the fitted transform, in red over the imagery, with your points. Use it to see whether mound outlines, roads and other features line up.
- `render PDF PAGE_INDEX --reg <agent> --name <name> --dpi D` renders a page of a publication, for an auxiliary plan.

Everything these tools write goes under `data/raw/2026-10-21-plan-registration/<agent>/`, which Git ignores. Plans and imagery are third-party material and must stay there.

## Choosing control points

A control point is a point you can identify on the plan and in the imagery whose position is unlikely to have changed between the survey and the image. Give each point a class.

| Class | Features | Error used in the fit |
|---|---|---|
| A | Sharp corners of permanent built features: standing masonry, a building or compound wall corner, a survey pillar or benchmark, a well head, a bridge abutment, the crossing of two metalled roads or of a road and a railway | 3 m |
| B | Well-defined points on linear landscape features drawn on the plan: crossings and sharp bends of tracks, canals, drains or field embankments; corners of excavation cuts or spoil heaps that are still visible | 6 m |
| C | Points on landforms and soft edges: corners, re-entrants or extremities of a mound outline or contour, breaks of slope, the edge of a village or a tank, a bend in the bank of a dry channel | 12 m |
| P | A link between two plans: the same drawn feature (wall corner, trench corner, grid peg) on both | 2 m |

Set `exposed_masonry: true` for a point that lies on ancient masonry that is exposed and visible as masonry in the imagery. A mound edge over buried walls is a landform (class C) and is not flagged.

Follow these rules in order.

1. For each plan, first list every feature on the plan that might still be visible: mound outlines and contours, roads, tracks, canals, railways, villages, buildings, wells, survey pillars, river banks, excavation dumps, fences. Then look for each in the imagery, starting from the site coordinates and widening the search if needed. Record each candidate and whether you used it.
2. Use every class A or B point you can identify with confidence. Add class C points until there are at least five points if the plan allows, chosen to spread over the whole extent of the plan rather than to cluster. Points far apart constrain the fit far better than points close together.
3. At least three points are required, and they must not all lie near one line.
4. Choose points from what the plan and the imagery show, nothing else.
5. After running `check`, you may move or remove a point only when you can name an identification error: it is a different feature, the feature was rebuilt or moved since the survey, or you misread a pixel. Write every change in the control file's `log` with its reason. Do not remove a point only because its residual is large. Before you finish, rerun `check` and make sure the file is final.
6. If the plan itself shows fewer than three features that survive in the imagery, you may chain it through an auxiliary plan of the same site: another plan, from the same or another publication, that shows both the plan's structures and surviving features. Render it with `render`, measure its scale bar (two end points in pixels and the length in metres), link the assigned plan to it with class P points on features drawn on both, and link the auxiliary plan to the imagery as above. Put the auxiliary plan's control points in the same control file as a second link.
7. A plan with no three usable features is recorded as not registrable, with every feature you looked for and why each failed. That is a valid result; do not force a registration.

Work on the plans in the order given in your assignment: targets, then validation plans, then optional plans. Spend the effort a careful surveyor would on each plan, and move on when the features run out.

## The control file

Write one JSON file per plan to `experiments/2026-10-21-plan-registration/control-<R1 or R2>/<town>__<source_id>.json`, in this form:

```json
{
 "schema_version": "1.0",
 "registrar": "R1",
 "agent": "R1-G2",
 "plan": "kanmer:kharakwal-fig5",
 "status": "registered",
 "reason": null,
 "aux_plans": [],
 "links": [
  {"plan": "kanmer:kharakwal-fig5", "to": "map", "points": [
   {"id": "cp1", "class": "C", "exposed_masonry": false,
    "plan_px": [412.5, 88.0],
    "mosaic": "data/raw/2026-10-21-plan-registration/R1-G2/mosaics/<name>.json",
    "mosaic_px": [1033.0, 761.5],
    "plan_feature": "north-east corner of the mound outline (hachured edge)",
    "image_feature": "north-east corner of the raised mound, edge of the lighter soil",
    "confidence": "corner rounded by erosion; position good to about 10 m"}
  ]}
 ],
 "candidates_considered": [
  {"feature": "village road drawn along the south edge", "used": false, "why": "the road has been realigned; no match in the imagery"}
 ],
 "imagery": [
  {"mosaic": "data/raw/2026-10-21-plan-registration/R1-G2/mosaics/<name>.json", "service": "Esri World Imagery", "release": null, "imagery_date": "20260326"}
 ],
 "log": [
  {"utc": "2026-10-21T19:40:00Z", "change": "moved cp3 from the inner to the outer edge of the embankment", "reason": "the plan draws the outer toe of the bank"}
 ],
 "notes": "free text: how the site was located, anything unusual"
}
```

A point in a link to an auxiliary plan has `target_px` (pixels on the auxiliary plan) in place of `mosaic` and `mosaic_px`, and that link's `to` is the auxiliary plan's id. An auxiliary plan entry in `aux_plans` has `id` (`town:aux-<short name>`), `town`, `citation`, `publication_file`, `pdf_page_index`, `render`, `render_sha256` and `scale_bar` (`{"p1_px": [x, y], "p2_px": [x, y], "length_m": L}`). For a plan that is not registrable, set `status` to `"not registrable"`, give `reason`, leave `links` empty and still fill `candidates_considered`.

## Your final message

End with a short report in connected prose: for each plan, whether it was registered, how many points of which classes, the rotation error and scale ratio that `check` reported, and, for any plan not registered, why. List the files you wrote. Write it to maximise the reader's comprehension: explain directly in connected prose, keep shared assumptions together, and do not interrupt the account with repeated warnings or corrective comparisons.
