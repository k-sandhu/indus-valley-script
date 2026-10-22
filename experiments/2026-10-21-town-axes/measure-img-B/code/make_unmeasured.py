"""Write the configurations of towns we examined but could not measure (role img-B).

Each configuration lists the imagery we inspected, so that measure.py records
the mosaics, their SHA-256 and the imagery dates in the town file, and states
why no line could be measured.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cfgio  # noqa: E402

HERE = Path(__file__).resolve().parent

TOWNS = {
 "kalibangan": {
  "location": {"lat": 29.47386, "lon": 74.13039, "basis": "Located on Esri World Imagery at zoom 17 and 18: the fenced, eroded mound north-west of Kalibangan village (OpenStreetMap places the village at 29.4696 N, 74.1348 E), with the larger high mound in the east of the fenced area and a lower, tree-covered area to its west. The coordinates are those of the centre of the high mound."},
  "sources": [
   {"id": "src1", "name": "kalibangan_core", "x": [185048, 185054], "y": [108593, 108598], "role": "inspected (current World Imagery)"},
   {"id": "src2", "name": "kalibangan_core", "x": [185048, 185054], "y": [108593, 108598], "wayback_release": "16749", "role": "inspected (archived release with lower vegetation)"},
   {"id": "src3", "name": "kalibangan_core", "x": [185048, 185054], "y": [108593, 108598], "wayback_release": "8432", "role": "inspected (archived release)"}],
  "notes": "We examined the current release and two archived releases (13 October 2021 and 21 July 2021), with contrast enhancement. The mound surface is deeply gullied and partly backfilled; the excavated fortification walls, streets and houses of the citadel and lower town are not visible. The only long straight features are visitor tracks and a straight pale strip with a dark edge on the eastern part of the mound, which runs into the network of tracks and may be a track or a backfilled trench line, together with one small rectangular outline beside it. None of these can be identified as Harappan architecture, so we measured no line. The perimeter fence and the farmland around the site follow the cardinal canal-colony grid and were not used."},
 "surkotada": {
  "location": {"lat": 23.62614, "lon": 70.83986, "basis": "OpenStreetMap archaeological-site node 'Surkotada' (23.62614 N, 70.83986 E), checked against the Wikipedia coordinates (23.6304 N, 70.8407 E, about 470 m north); neither position shows an identifiable mound or fortification in the imagery, so the location is not confirmed."},
  "sources": [
   {"id": "src1", "name": "surkotada_site", "x": [182654, 182657], "y": [113357, 113360], "role": "inspected (current World Imagery, around the OpenStreetMap position)"},
   {"id": "src2", "name": "surkotada_overview2", "x": [182654, 182658], "y": [113353, 113357], "role": "inspected (current World Imagery, around the Wikipedia position)"}],
  "notes": "We searched the current World Imagery around the OpenStreetMap and Wikipedia positions of Surkotada and the archived releases of the OpenStreetMap tile from 2021 to 2026. The ground is scrub and gullied sandstone with tracks, a reservoir to the east and fields to the north; no mound outline, stone fortification or straight wall could be identified with confidence, so we did not measure the site and do not confirm its location."},
 "banawali": {
  "location": {"lat": 29.59839, "lon": 75.39217, "basis": "Wikipedia coordinates (29.59833 N, 75.39194 E) fall on an oval, grass-covered protected mound of about 6 ha surrounded by fields; the coordinates are those of the mound centre in Esri World Imagery."},
  "sources": [
   {"id": "src1", "name": "banawali_survey", "x": [185967, 185973], "y": [108488, 108494], "role": "inspected (current World Imagery)"}],
  "notes": "The mound is backfilled and grassed. Its surface shows only visitor tracks (a perimeter track and several crossing tracks) and one small modern square near the centre; no Harappan wall, street or fortification is visible in the current image or in the archived releases of 2021 to 2025 that we inspected. The fields around the mound follow the cardinal canal-colony grid and were not used."},
 "rakhigarhi": {
  "location": {"lat": 29.29159, "lon": 76.11121, "basis": "OpenStreetMap archaeological-site nodes for the Rakhigarhi mounds (RGR-1 at 29.29366 N, 76.11439 E; RGR-2 at 29.29132 N, 76.11074 E) on the north side of Rakhigarhi village; the coordinates are those of the central mound west of the pond."},
  "sources": [
   {"id": "src1", "name": "rakhigarhi_survey", "x": [186490, 186500], "y": [108742, 108752], "role": "inspected (current World Imagery)"},
   {"id": "src2", "name": "rakhigarhi_rgr1", "x": [186496, 186497], "y": [108745, 108746], "wayback_release": "64776", "role": "inspected (archived release of 31 August 2023, during excavation)"}],
  "notes": "The mounds north of the village are eroded, scrub-covered and crossed by tracks; much of the site lies under the modern village. Recent excavation trenches appear in the 2023 and 2024 releases only as black protective covers and, in the current image, as a few small square trench outlines and a large roofed shelter; the walls inside them are not visible. Trench edges, covers, roofs, ponds and the cardinal field grid were excluded, which leaves no measurable Harappan line."},
 "chanhu-daro": {
  "location": {"lat": 26.17353, "lon": 68.32304, "basis": "Wikidata coordinates for Chanhu-daro (Q1062208: 26.17361 N, 68.32306 E) fall on the eroded mounds east of a modern walled compound with a circular building, between canals and fields; the coordinates are those of the mounds' centre in Esri World Imagery."},
  "sources": [
   {"id": "src1", "name": "chanhu-daro_survey", "x": [180820, 180826], "y": [111310, 111316], "role": "inspected (current World Imagery)"}],
  "notes": "The mounds are eroded and scrub-covered, with tracks and a few pits; no wall, street or platform edge is visible. The straight lines in the area are canals, roads, field boundaries and the walls of the modern compound to the west, all excluded."},
 "kanmer": {
  "location": {"lat": 23.41775, "lon": 70.86286, "basis": "Wikipedia coordinates (23.4179 N, 70.8634 E) fall on a scrub-covered mound of roughly 1 ha bounded by a stream on the west and north, north of Kanmer village; the coordinates are those of the mound centre in Esri World Imagery."},
  "sources": [
   {"id": "src1", "name": "kanmer_survey", "x": [182671, 182674], "y": [113522, 113525], "role": "inspected (current World Imagery)"}],
  "notes": "The mound is covered with scrub and crossed by tracks; a small modern shelter stands on its southern part. The excavated fortification walls are not visible in the current image (with contrast enhancement) or in the archived releases of 2021 to 2026, so no line could be measured."},
 "shikarpur": {
  "location": {"lat": 23.23794, "lon": 70.67743, "basis": "Coordinates published for the site (23 deg 14 min 15 s N, 70 deg 40 min 39 s E, given by Wikipedia and a lithics study of the site) fall on an oval, densely wooded mound of about 4 ha south of the Kandla-Bhachau highway; the coordinates are those of its centre in Esri World Imagery."},
  "sources": [
   {"id": "src1", "name": "shikarpur_site", "x": [182535, 182539], "y": [113664, 113669], "role": "inspected (current World Imagery)"}],
  "notes": "The mound is covered by a dense stand of trees and shrubs; no part of the excavated fortification or houses is visible. The straight features nearby are the highway, tracks and wind-turbine pads, all excluded."},
}

OPTIONAL = {
 "juni-kuran": {
  "location": {"lat": 23.946255, "lon": 69.767039, "basis": "Wikidata coordinates for the archaeological site (Q63358276: 23.94626 N, 69.76704 E), about 1.3 km east of the hamlet of Juni Kuran in OpenStreetMap (23.94421 N, 69.75402 E). Neither position, nor a 2 km overview around them at zoom 17, shows an identifiable fortified mound, so the location is not confirmed."},
  "sources": [{"id": "src1", "name": "juni-kuran_survey", "x": [181872, 181876], "y": [113101, 113106], "role": "inspected (current World Imagery, around the Wikidata position)"}],
  "notes": "Optional town. The ground around the published positions is scrub, gullies and small fields with tracks; we could not identify the fortified citadel or any straight wall, so we did not measure the site and do not confirm its location."},
 "sutkagen-dor": {
  "location": {"lat": 25.498333, "lon": 61.950278, "basis": "Wikidata coordinates for Sutkagen Dor (Q2369920: 25.49833 N, 61.95028 E) fall on a reddish, eroded rise west of a seasonal stream and east of a N-S road; the location is plausible but not confirmed by any identifiable wall."},
  "sources": [{"id": "src1", "name": "sutkagen-dor_survey", "x": [176179, 176185], "y": [111856, 111862], "role": "inspected (current World Imagery)"}],
  "notes": "Optional town. The rise at the published position has a roughly rectangular reddish outline with some straight N-S edges, but at this resolution they cannot be told apart from erosion of the natural outcrop, and no wall face can be identified with confidence. We did not measure it."},
 "nausharo": {
  "location": {"lat": 29.365, "lon": 67.588, "basis": "Wikidata coordinates for Nausharo (Q2039702: 29.365 N, 67.588 E, given to three decimals) fall beside a tree-covered mound surrounded by fields on the Kachhi plain; the coordinates are the published ones."},
  "sources": [{"id": "src1", "name": "nausharo_survey", "x": [180285, 180291], "y": [108683, 108689], "role": "inspected (current World Imagery)"}],
  "notes": "Optional town. The mound is covered by trees and scrub and shows no wall; the straight lines around it are field bunds of the surrounding farmland (themselves laid out on a slightly rotated grid), which we excluded. Not measured."},
 "kotada-bhadli": {
  "location": {"lat": 23.34635, "lon": 69.42608, "basis": "OpenStreetMap archaeological-site node 'Old Kotada' at Kotda (Tharavada)-Bhadli (23.34635 N, 69.42608 E); the imagery shows fields, scrub and a stream there but no identifiable fortified enclosure, so the location is not confirmed."},
  "sources": [{"id": "src1", "name": "kotada-bhadli_survey", "x": [181624, 181628], "y": [113578, 113582], "role": "inspected (current World Imagery)"}],
  "notes": "Optional town. No stone fortification or wall is visible at or around the published position, including in a contrast-enhanced view; the straight features are field edges and tracks. Not measured."},
 "bhirrana": {
  "location": {"lat": 29.55491, "lon": 75.54777, "basis": "OpenStreetMap archaeological-site node 'Ancient Site of Bhirrana' (29.55491 N, 75.54777 E), on a scrub-covered mound north of Bhirdana village, crossed by a road on its east side."},
  "sources": [{"id": "src1", "name": "bhirrana_survey", "x": [186082, 186086], "y": [108525, 108529], "role": "inspected (current World Imagery)"}],
  "notes": "Optional town. The mound is backfilled and covered with scrub and tracks; no wall is visible. The surrounding fields follow the cardinal canal-colony grid and were excluded. Not measured."},
}

TOWNS.update(OPTIONAL)

if __name__ == "__main__":
    for slug, d in TOWNS.items():
        cfg = {"town": slug, "zoom": 18, "location": d["location"], "sources": d["sources"], "parts": [],
               "check_lines": [], "systems": [], "main_system": None,
               "main_system_reason": "No Harappan line could be identified in the imagery.",
               "published_values": [], "measurable": False, "notes": d["notes"]}
        cfgio.save(cfg, HERE / "configs" / f"{slug}.json")
        print("wrote", slug)
