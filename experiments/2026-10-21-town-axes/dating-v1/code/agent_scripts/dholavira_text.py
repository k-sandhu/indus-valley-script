import sys
sys.path.insert(0, 'experiments/2026-10-21-town-axes/measure-img-B/code')
import cfgio
p = 'experiments/2026-10-21-town-axes/measure-img-B/code/configs/dholavira.json'
c = cfgio.load(p)
c['location'] = {"lat": 23.887, "lon": 70.2131, "basis": "Located on Esri World Imagery at zoom 17 and 18: the walled site on Khadir island north of the village of Dholavira, with the conserved stone fortifications of the castle in the south of the walled area and the site museum and village to the south-east. The coordinates are those of the castle."}
for P in c['parts']:
    if P['id'] == 'P1':
        P['holes'] = [[[855, 1170], [1120, 1140], [1120, 1162], [855, 1192]]]
        P['holes_note'] = "hole: diagonal visitor path across the southern part of the castle"
D = {
 "P1": ("The castle (citadel): its stone fortification walls on the north, west and south, and the excavated buildings inside it. A diagonal visitor path across its southern part is cut out as a hole, and the polygon stops short of the N-S path along its east side.",
        "Overlay checked by eye: the peak runs parallel to the northern fortification and the walls of the buildings inside the castle; the secondary peak about 14 degrees further anticlockwise is weak (29 percent) and comes from short wall stubs and shadows near the north-west gate area."),
 "P2": ("The rectangular stone-lined reservoir immediately east of the castle, with its west and east walls about 50 m long.",
        "Overlay checked by eye: the peak follows the long west and east walls of the reservoir; the reservoir is turned slightly less than the castle."),
 "P3": ("Excavated houses in the bailey, west of the castle.",
        "Overlay checked by eye: the house walls are short and the histogram is a broad plateau with several near-equal peaks (contrast below 1); the automatic value is not reliable."),
 "P4": ("The middle town north of the castle and the open ground: the main E-W street with house walls along both sides, the N-S street running south from it at the west, and a group of excavated houses east of centre. The main E-W street is also used as a visitor path, so its edges are partly path edges on the line of the ancient street.",
        "Overlay checked by eye: the peak follows the edges of the E-W street and the walls along it; the N-S house walls east of centre are closer to north, which produces the secondary peak near 0."),
}
conf = {"P1": "high", "P2": "high", "P3": "low", "P4": "medium"}
for P in c['parts']:
    P['description'], P['eye_check'] = D[P['id']]
    P['confidence'] = conf[P['id']]
for s in c['systems']:
    if s['id'] == 'sys3':
        s['note'] = "Automatic value not reliable (plateau histogram); no check lines."
c['main_system'] = "sys1"
c['main_system_reason'] = "The castle has the longest and clearest Harappan walls at the site (its northern fortification and the buildings inside it), and the reservoir beside it and the middle town north of it are turned in the same sense within a few degrees; we take the castle as the town's main layout and report the reservoir and the middle town as separate systems in the same family."
c['notes'] = ("Esri World Imagery at zoom 18 (0.55 m per pixel; the service reports a 0.5 m Vantor Vivid WorldView-2 image of 18 December 2023). "
              "An imagery seam runs E-W just south of the castle; all polygons lie north of it in one image. "
              "The castle fortifications and the reservoir east of it are clear and conserved; the middle town is partly overgrown, and only its main E-W street, one N-S street and a few houses are visible. The bailey houses are too short and broken to give a stable value. The outer fortification and the lower town east of the middle town are under scrub and could not be traced except as straight paths, which we did not measure. "
              "Modern features excluded: visitor paths (the diagonal path across the castle, the N-S path along the castle's east side and the paths on the line of the outer walls), the small shed in the castle's north gate area, the site museum and road to the south-east, and the field boundaries around the site. "
              "All measured parts are turned anticlockwise from north, the castle by the largest amount.")
cfgio.save(c, p)
