"""Propose candidate line segments in a region of a plan image with OpenCV's LSD.

usage: python lsd_candidates.py IMAGE x0 y0 x1 y1 MINLEN [blur] [angle_window]
angle_window is "v" (within 20 degrees of image vertical), "h" (of horizontal)
or "all". Prints JSON line stubs with full-image coordinates; we inspect each
candidate on the plan before adopting it as a measured line, and the adopted
lines are then refitted by measure_lines.py like any hand-placed line.
"""
import sys, json
import cv2
import numpy as np

img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
x0, y0, x1, y1 = map(int, sys.argv[2:6])
minlen = float(sys.argv[6])
blur = int(sys.argv[7]) if len(sys.argv) > 7 else 5
win = sys.argv[8] if len(sys.argv) > 8 else "all"
sub = img[y0:y1, x0:x1]
if blur > 1:
    sub = cv2.GaussianBlur(sub, (blur, blur), 0)
lsd = cv2.createLineSegmentDetector(0)
res = lsd.detect(sub)[0]
out = []
if res is not None:
    for l in res[:, 0, :]:
        a, b, c, d = map(float, l)
        ln = float(np.hypot(c - a, d - b))
        if ln < minlen:
            continue
        ang = np.degrees(np.arctan2(c - a, -(d - b))) % 180
        if win == "v" and not (ang < 20 or ang > 160):
            continue
        if win == "h" and not (70 < ang < 110):
            continue
        out.append({"p1": [round(a + x0, 1), round(b + y0, 1)], "p2": [round(c + x0, 1), round(d + y0, 1)],
                    "len": round(ln), "img_az": round(float(ang), 2)})
out.sort(key=lambda t: (t["p1"][0], t["p1"][1]))
for o in out:
    print(json.dumps(o))
print(len(out), "segments")
