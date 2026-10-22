import sys
sys.path.insert(0, 'experiments/2026-10-21-town-axes/measure-img-B/code')
import cfgio
p = 'experiments/2026-10-21-town-axes/measure-img-B/code/configs/lothal.json'
c = cfgio.load(p)
c['location'] = {"lat": 22.5225, "lon": 72.2491, "basis": "Located on Esri World Imagery at zoom 17 and 18: the fenced, wooded mound east of the national highway near Saragwala, with the water-filled rectangular dock on its east side and the excavated acropolis and lower town west of it. The coordinates are those of the centre of the excavated area between the acropolis and the dock."}
D = {
 "P1": ("Brick-lined rectangular basin on the east side of the town, usually identified as the dock, measured on the current image. The basin is filled with water and its walls have been conserved by the Archaeological Survey of India; the polygon covers the basin and its walls but not the modern paths along its east side and south end.",
        "Overlay checked by eye: the peak runs along the long west and east walls of the basin, which dominate the histogram (88 percent of the edge weight lies near N-S); there is no secondary peak."),
 "P1w": ("The dock measured again on the archived October 2021 release (a WorldView-2 image of 2019 or 2021), as a second witness.",
         "Overlay checked by eye: same edges as P1; the two images agree within their errors."),
 "P2": ("Two areas of the acropolis on the archived 2021 image: the building at its north-west corner (walls visible as dark shadow lines) and the block of square warehouse units near its south-east. The square outline around the warehouse, which may be a modern revetment of the platform edge, and the paths across the acropolis are outside the polygons.",
        "Overlay checked by eye: the peak follows the walls of the north-west building and the grid of warehouse units; the north wall of the building (S9) is turned a few degrees further anticlockwise than the rest."),
 "P3": ("North-western excavated block of the lower town on the archived 2021 image: a walled compound with internal rooms, bounded on the east by a straight path (excluded).",
        "Overlay checked by eye: the walls of this block are visibly turned anticlockwise from the dock and the acropolis; the peak follows them, and the current image (P3c) gives the same value."),
 "P3c": ("The north-western lower-town block measured on the current image as a second witness.",
         "Overlay checked by eye: walls are fainter than on the 2021 image; the peak agrees with P3."),
 "P4": ("Two groups of excavated houses in the western lower town on the archived 2021 image, west of the main N-S path (excluded).",
        "Overlay checked by eye: the histogram is broad with two near-equal peaks on either side of the reported value; the houses share the anticlockwise turn of the north-western block, but the value is uncertain by several degrees."),
 "P5": ("Union of the lower-town polygons P3 and P4 on the archived 2021 image.",
        "The combined peak lies close to the north-western block, which has the sharpest walls."),
}
conf = {"P1": "high", "P1w": "high", "P2": "medium", "P3": "medium", "P3c": "medium", "P4": "low", "P5": "medium"}
for P in c['parts']:
    P['description'], P['eye_check'] = D[P['id']]
    P['confidence'] = conf[P['id']]
notes = {"sys1w": "Second witness for sys1 on the archived 2021 image.",
         "sys3c": "Second witness for sys3 on the current image.",
         "sys4": "Broad, double-peaked histogram; low reliability.",
         "sys5": "Combined lower-town measurement; check lines are listed under sys3."}
for s in c['systems']:
    if s['id'] in notes:
        s['note'] = notes[s['id']]
c['main_system'] = "sys1"
c['main_system_reason'] = "The dock is the longest straight Harappan construction at Lothal (its walls run for more than 200 m) and gives the sharpest and most stable peak on both images; the acropolis buildings agree with it. The lower-town blocks form a second, distinct system turned several degrees further anticlockwise, reported as sys3 and sys5."
c['notes'] = ("We measured Lothal on two releases of Esri World Imagery at zoom 18 (0.55 m per pixel): the current release (a Vantor Vivid image of 27 February 2026), on which the dock is clear but the acropolis and lower town are faded, and an archived Wayback release of 13 October 2021, on which the low walls of the acropolis and lower town stand out much more clearly. "
              "The dock and the acropolis share one direction, while the excavated lower-town blocks west of the acropolis are turned about 7 to 9 degrees further anticlockwise; the two systems are separated by more than their errors on both images. "
              "The dock walls have been conserved and the basin is kept filled with water, so its edges are partly modern facing on the excavated line. The square outline around the warehouse units may also be a modern revetment and is excluded from the acropolis polygon. Modern features excluded: the perimeter fence, the visitor paths that cross the site (one runs N-S along the east side of the north-western block and another diagonally across the lower town), the museum and site buildings to the south, and the highway and field boundaries outside the site.")
cfgio.save(c, p)
