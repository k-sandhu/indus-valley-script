# True-north bearings of Harappan towns from registered plans: report of 21 October 2026

We registered excavators' published plans to satellite imagery and measured the true bearing of each plan's north arrow, so that wall directions measured relative to those arrows by the [town-axes package](../2026-10-21-town-axes/REPORT.md) could be converted to true north. Five towns whose architecture is backfilled or covered now have true-north deviations: the street grid of Kalibangan's lower city (KLB-2) at −6.7 ± 1.8°, Surkotada's citadel fortification at −11.4 ± 2.1°, the central street of Chanhu-daro's Mound II at −10.9 ± 3.8°, Farmana's structure complexes at −23.7 ± 4.3° and the Shikarpur fortification at +1.3 ± 4.4° (positive clockwise). Banawali, Kanmer and Rakhigarhi could not be registered. Together with the four imagery towns, eight towns with a layout date now have true-north values; Shikarpur has a true-north value but no layout date.

The frozen validation passed at Lothal and failed at Dholavira. At Dholavira the registration put the graticuled ASI contour drawing's north within 0.3 ± 0.3° of true north, as its latitude-longitude frame requires. The protocol compared plan-B's main system on that drawing, which plan-B measured on mound edges along the walls rather than on the walls themselves, with the imagery castle walls, and the two differ by 5.1° (z = 3.2). The three Dholavira plans that draw the walls convert to values within 1.4 standard errors of the imagery. Under the frozen rule this package does not offer its values for scoring the town-axes kill condition P0; a separate package with its own protocol has to test the cause first.

## Method

The [protocol](PROTOCOL.md) was frozen at 18:53 UTC on 21 October with the plan list, the briefs and the code (`FREEZE.json`), before any control point was chosen. Two registrars, R1 and R2, each split by region among three agents, registered the 21 plans of [plans-v1.json](plans-v1.json) independently under [REGISTRATION-BRIEF.md](REGISTRATION-BRIEF.md). A search agent looked for plans of Rakhigarhi and Shikarpur under [SEARCH-BRIEF.md](SEARCH-BRIEF.md), measured the one plan it found by plan-B's method and registered it. None of the agents was given an orientation value, the protocol or the purpose of the work, and their checking tool printed the residuals, the scale and the rotation error but never the rotation; the compass statements some of them met in the publications' text are recorded in their control files. We had read the town-axes report, which states the deviations, before designing the work, and therefore chose no control point ourselves. The 46 control and town files were hashed in `CONTROL-FREEZE.json` at 20:40:43 UTC, and `code/register.py` ran once, four seconds later ([results](registration-v1/results.json), [town table](registration-v1/towns.csv)).

A registrar recorded features that appear both on the plan and on Esri World Imagery (or an older Esri Wayback release): standing masonry and survey pillars (class A, 3 m), crossings of tracks, canals and field banks and the edges of excavation cuts (class B, 6 m), and mound outlines, village edges and channel banks (class C, 12 m). Where a plan showed nothing that survives, the registrar chained it through a second plan of the same site with shared drawn features (class P, 2 m). We fitted a similarity transform from plan pixels to Web Mercator, which is conformal and whose grid north is true north, by weighted least squares. The rotation error is the prior error from the class errors, scaled up when χ² per degree of freedom exceeds 1, or the jackknife error over leave-one-out fits if larger. A registration was accepted when the points were not collinear, χ² per degree of freedom was at most 9, the plan fitted better than its mirror image, and the fitted scale lay within 15% of the scale bar; it is used only if its rotation error is at most 5°. The two registrars' rotations were combined by inverse variance, with an error no smaller than half their difference. The [synthetic self-test](selftest-v1/selftest.json) confirmed the sign conventions and gave 72–85% coverage of the one-sigma interval and 97–99% of the two-sigma interval.

The true bearing α of a plan's arrow is its page azimuth, as measured by plan-B, minus the fitted rotation. A plan-B system with deviation θ relative to the arrow then has true-north deviation θ + α, and its error replaces plan-B's arrow term with the registration error.

## Registrations and arrow bearings

| Plan | Arrow label | R1 points, σφ | R2 points, σφ | Arrow true bearing α |
|---|---|---|---|---|
| Kalibangan, IAR 1967–68 Fig. 7 | none | 6 C, 2.06° | 6 C, 2.29° | +8.8 ± 1.6° |
| Kalibangan, IAR 1968–69 figure | none | 7 C, 2.23° | 7 C, 2.06° | +8.4 ± 1.5° |
| Surkotada, Joshi 1990 Fig. 8 | none | 12 A/B, 2.23° | 6 A, 3.75° | +3.6 ± 1.9° |
| Surkotada, Joshi 1990 Fig. 4 | none | 6 A, 5.69° (not used) | 5 A, 4.41° | +0.7 ± 4.4° |
| Chanhu-daro, Mackay 1943 Pl. IV | magnetic, 1935 | 12 P to Pl. I, then 5 C; 3.75° | not registrable | +9.9 ± 3.8° |
| Farmana, Shinde et al. 2008 Fig. 19 | none | not registrable | 10 P to Fig. 7, then 4 C; 4.31° | −1.4 ± 4.3° |
| Shikarpur, Gadekar, Rajesh and Ajithprasad 2014 Fig. 2 | none | search agent: 5 C, 4.39° | | +0.9 ± 4.4° |
| Harappa, Wheeler 1947 Pl. XV | none | 12 A/B, 0.59° | 9 A, 0.72° | +1.1 ± 0.5° |
| Dholavira, ASI 2020 drawing 9 | graticule | 11 B/C, 0.38° | 7 B/C, 0.48° | +0.3 ± 0.3° |
| Dholavira, ASI 2020 Fig. 2.10 | none | 4, 4.44° | 5, 0.76° | +1.6 ± 0.8° |
| Dholavira, Bisht 2015 Fig. 6.3 | none | 8 A/B, 1.52° | 5 A/B, 1.22° | −7.8 ± 2.0° |
| Dholavira, ASI 2020 Fig. 2.11 | none | 8 A/B, 1.50° | 5 A/B, 1.49° | −10.9 ± 1.9° |
| Lothal, Bisht 2015 Fig. 10.10 A | none | 8 A, 0.72° | 7 A/B, 0.81° | +1.5 ± 0.5° |
| Lothal, Rao 1979 Fig. 18 | none | rejected (scale 0.84) | 7 A/B, 13.5° (not used) | |

Positive α means that the drawn arrow points east of true north. Both Kalibangan plans of *Indian Archaeology – A Review*, registered on the citadel and lower-city mounds by two registrars each, have arrows about 8.5° east of true north; this is why their street grid, at −15.5° relative to the arrow, lies at −6.7° on true north. The registrars agree within their errors: over the nine plans that both registered informatively, the differences give χ² = 9.4 ([diagnostics](diagnostics-v1/diagnostics.json)). The largest differences are on the Dholavira castle drawing published twice (Bisht's Fig. 6.3 and the dossier's Fig. 2.11), where R1's rotations are about 4° larger than R2's on both copies; R1 noted that the drawing's reservoir and castle interior imply scales that differ by about 10%.

## True-north deviations

| Town, part | Plan | Relative to arrow | True north | Main system |
|---|---|---|---|---|
| Kalibangan, KLB-2 street grid | IAR 1967–68 Fig. 7 | −15.5 | −6.7 ± 1.8 | yes |
| Kalibangan, KLB-2 street grid and north wall | IAR 1968–69 | −14.7 | −6.3 ± 1.7 | |
| Kalibangan, KLB-2 west city wall | IAR 1967–68 Fig. 7 | −3.6 | +5.2 ± 1.8 | |
| Kalibangan, KLB-1 southern half, east and west walls | IAR 1967–68 Fig. 7 | −5.1 | +3.7 ± 1.8 | |
| Kalibangan, KLB-1 cross wall | IAR 1967–68 Fig. 7 | −13.7 | −4.9 ± 1.8 | |
| Kalibangan, KLB-1 northern half | IAR 1967–68 Fig. 7 | −8.4 | +0.4 ± 2.1 | |
| Kalibangan, KLB-1 southern half | IAR 1968–69 | −13.8 | −5.4 ± 1.8 | |
| Surkotada, citadel fortification | Joshi Fig. 8 | −15.1 | −11.4 ± 2.1 | yes |
| Surkotada, residential annexe | Joshi Fig. 8 | −17.2 | −13.6 ± 2.0 | |
| Surkotada, houses of citadel blocks 2 and 3 | Joshi Fig. 8 | −7.7 | −4.1 ± 2.0 | |
| Surkotada, citadel and annexe fortification | Joshi Fig. 4 | −10.5 | −9.8 ± 4.6 | |
| Chanhu-daro, Mound II central street | Mackay Pl. IV | −20.7 | −10.9 ± 3.8 | yes |
| Farmana, Structure Complexes 2–4 | Shinde Fig. 19 | −22.3 | −23.7 ± 4.3 | yes |
| Shikarpur, fortification | Gadekar Fig. 2 | +0.5 | +1.3 ± 4.4 | yes |
| Lothal, dock | Bisht Fig. 10.10 A | −3.8 | −2.3 ± 0.9 | yes |
| Lothal, acropolis platform | Bisht Fig. 10.10 A | −1.9 | −0.5 ± 0.9 | |
| Harappa, Mound AB citadel, east and west walls | Wheeler Pl. XV | −12.7 | −11.6 ± 0.9 | |
| Harappa, Mound AB citadel, south wall | Wheeler Pl. XV | +0.1 | +1.2 ± 0.9 | |

Deviations are in degrees. The KLB-1 walls on the 1967–68 plan are not square to each other, as plan-B noted, so the citadel's east and west walls and its cross wall differ by 8.6°. Harappa's town value comes from imagery of Mound F; Wheeler's plate is not the plan of plan-B's main system, so the registration adds only the citadel walls. The two Surkotada values come from points on its exposed masonry, which the registrars found 8.1 km east-south-east of the published coordinates (below).

## Validation

| Town | Registered | Imagery | z | Points used | Verdict |
|---|---|---|---|---|---|
| Lothal, dock | −2.31 ± 0.85 | −1.88 ± 0.30 | −0.47 | all, every one on exposed masonry | passes |
| Dholavira, drawing 9 main system | −0.38 ± 0.60 | −5.50 ± 1.50 | +3.17 | without exposed masonry (5 points for R1, 4 for R2) | fails |

The rule requires |z| ≤ 2 at both towns, so the validation fails. At Lothal no registration without exposed masonry could be made, because the site plan draws nothing but Harappan structures, and the comparison uses all points.

The secondary checks locate the failure. The graticule of drawing 9 registers to α = +0.29 ± 0.30° with all points and +0.55 ± 0.55° without masonry, so the registration recovers that drawing's true north. Plan-B's main system on drawing 9 is described in its town file as "mound edges along the castle and Middle Town walls" on the contour survey, a line set different from the castle walls that the imagery measurers traced. The other Dholavira plans draw the walls. Converted to true north, the dossier's whole-city plan (Fig. 2.10) gives −5.86 ± 0.82° (z = −0.21 against the imagery), Bisht's castle plan −2.03 ± 2.11° (z = +1.34) and its 2020 redrawing −2.81 ± 1.93° (z = +1.10). Relative to their own arrows the Dholavira castle systems spanned 15.5°; on true north they span 5.2°, and 3.8° without the mound-edge system.

The magnetic arrow at Chanhu-daro gives a less clean result. Mackay's Chanhu-daro Plate IV is labelled "MAG. NORTH NOV 2ND 1935", and IGRF gives a declination of +0.9° for that place and year, yet the registration gives α = +9.9 ± 3.8°, a difference of 2.4 combined standard errors. `register.py` skipped this check, because it looked up the declination in a field that holds a citation; `code/diagnostics.py`, written after the run, computes it. Only R1 registered this plan, through Mackay's site contour map (Plate I), and one of R1's five imagery points is a 20 m ring enclosure that R1 took to be Pir's tomb and R2 did not accept. Without that point the rotation moves by −2.9° and its error rises to 7.9°. We treat Chanhu-daro's value as the least secure of the five.

## Towns that could not be registered

Banawali's two plans (IAR 1983–84 Fig. 4 and 1987–88 Fig. 1) draw the fortification, moat and contours, none of which shows in seven imagery releases; the protected mound is bounded by straight field lines that match neither plan, and the reports' other figures are sections. Kanmer's plan draws only the fort walls, trenches and the site grid, all under scrub and trees in releases from 2010 to 2026, and only one rounded mound corner could be matched. For Rakhigarhi the search found no published plan with structures: Nath's report has sections and one unscaled contour plan, the *Puratattva* plans show mounds only and are marked not to scale, the *Indian Archaeology* entries of 1997–2001 have photographs, Shinde et al. (2018, *PLoS ONE*) map graves, and the 2023 Archaeopress volume is not open. Among the optional plans, Lothal Fig. 17 needs a site plate missing from the scan, the Rangpur and Rojdi plans show single trenches tied to grids that no surviving-feature plan draws, and Gola Dhoro could not be located.

## Site locations

Two registrars independently found Surkotada's exposed citadel at 23.6113 N, 70.9174 E, 8.1 km east-south-east of the coordinate (23.6304 N, 70.8407 E) that `plans-v1.json` took from plan-B and at which the town-axes imagery measurer img-A searched without finding the mound. R1 matched it to the GAZETTEER2018 entry of the project's site census. Farmana lies at about 29.040 N, 76.306 E, as the excavation report states, 25 km west of the coordinate in `plans-v1.json`. One registrar found Chanhu-daro's mounds about 60 m west-south-west of the published point. The Gola Dhoro coordinate is that of the town of Bagasra. These corrections belong in the settlement table and change the inputs of the town-axes horizon profiles for Surkotada and Farmana.

## Counting towns for P0

Eight towns with a layout date in the town-axes exploratory table now have true-north values: Mohenjo-daro, Harappa, Lothal and Dholavira from imagery, and Kalibangan, Surkotada, Chanhu-daro and Farmana from registration. That is the number the frozen P0 needs. Because the validation failed, the protocol's rule withholds these values from scoring until a new protocol tests the cause. The registered errors are also larger than the planning simulation assumed: with these eight towns, their dates and their errors (0.3–4.3°), the frozen P0 would pass under the Pleiades model with probability 0.40, against 0.97 for eleven towns at 1° (diagnostics, `planning_power_P0_pleiades`; dates and errors only).

## Decision and next evidence

We do not register these plans again with the same features. Two measurements would settle the open points. Surkotada's citadel masonry is exposed at the corrected coordinates, so the imagery method of the town-axes package can measure it directly and test the registered −11.4 ± 2.1° on a town where the registration puts the plan's arrow 3.6° east of true north. A scoring package for P0 should state in its protocol, before reading any value, that the Dholavira validation compares wall systems with wall systems, and how it treats Chanhu-daro's failed magnetic check and the towns registered by one registrar (Chanhu-daro, Farmana).

The boldest reading these measurements support is that the regional towns were laid out anticlockwise of true north, by less than their plan arrows made it. On true north, Kalibangan's lower-city grid lies at −6.7° (−15.5° relative to its arrow), Chanhu-daro's main street at −10.9° (−19.9° from the arrow corrected for 1935 declination), Surkotada's citadel at −11.4° (−15.1°), Farmana at −23.7° (−22.3°) and Dholavira's castle at −5.5°, while Harappa's Mound F, the house blocks of Mohenjo-daro and the Lothal dock lie within 2.3° of north and Shikarpur's fortification at +1.3 ± 4.4°. Harappa's own citadel walls on Mound AB, at −11.6 ± 0.9°, show that a turned axis also occurs inside a plains city, which suggests that the turn belongs to the ground a wall stands on rather than to the region. The test that decides it is the landform comparison of [C-0016](../../knowledge/conjectures/C-0016-plains-cities-on-true-north.md), now possible at ten towns with true-north values: measure on the elevation model the azimuth of the mound edge, river channel or ridge beside each measured system, and predict that every system turned by more than 5° from true north matches its landform within 5°, and that systems on open ground lie within 2° of north.
