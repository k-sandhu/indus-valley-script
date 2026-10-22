---
id: Q-1032
title: "Measure the axis bearing, horizon and founding date of every planned Harappan town"
status: open
area: data
kind: data-acquisition
priority: 2
data_access: public
compute: days
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [TOWN-AXES-2026-10-21]
related: [Q-1021, Q-1014, Q-1016, Q-1017]
sources: [knowledge/directions/parpola-forward-2026-10-20.md, research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf, experiments/2026-10-21-town-axes/MEASUREMENT-BRIEF.md, experiments/2026-10-21-town-axes/DATING-BRIEF.md]
authors: ["Claude Opus 5.5 (claude-opus-5-5), Claude Code desktop harness"]
---

# Question

For every Harappan town with straight walls or streets, in what direction relative to true north were its main axes laid out, how precisely can that direction be measured, what are its latitude and its horizon to the east and west, and when was the layout built and on what radiocarbon evidence? The population starts with Mohenjo-daro, Harappa, Kalibangan, Lothal, Dholavira, Surkotada, Banawali, Rakhigarhi, Chanhu-daro, Kanmer and Shikarpur and includes every other town whose Harappan architecture can be measured in satellite imagery or on a published plan.

# Why it matters

Our object record stops at the site name. The places the objects came from have no table of their own, although several open questions turn on how the towns were planned and when. The direction note of 20 October proposes that the builders aligned new towns on the setting point of a star, so that a town's deviation from the cardinal directions records the date of its layout ([study 4](../directions/parpola-forward-2026-10-20.md#4-the-towns-were-laid-out-on-the-stars)). Wanzke (*Interim Reports* vol. 2, 1987, pp. 33–44) measured Mohenjo-daro alone and wrote that the theory needed exact orientations at other Harappan sites; we found no study that supplied them. The same table gives each site coordinates, a horizon and a dated layout phase, fields that [DATA.md](../DATA.md) does not yet hold for any site, and its layout dates feed the calendar mapping of [Q-1021](Q-1021-chronology-calendar-ranges.md).

# What is needed

Read [DATA.md](../DATA.md) and the [redistribution rules](../provenance/REDISTRIBUTION.md). For each town, two independent measurements of the axis bearing from georeferenced imagery and, separately, from published plans, keeping plans drawn to magnetic or unspecified north apart from those drawn to true north; for each measurement the structures measured, their part of the town, their length and a one-sigma error. Latitude and longitude of the measured architecture. The apparent horizon altitude east and west from a digital elevation model (Copernicus GLO-30 and GLO-90), excluding the mound itself. The excavator's layout phase for each part of the town, every radiocarbon determination from that phase and the one before it with laboratory number and half-life, any Bayesian phase model, and the excavator's and later syntheses' calendar ranges, each with a page locator. Imagery tiles, plans and DEM tiles stay local-only; bearings, coordinates, horizon altitudes and dates are our observations and can be tracked.

# How to decide

The table is complete for a town when it has two independent imagery measurements that agree within three combined standard errors or a recorded discordance, a plan measurement with its north reference where any plan exists, a horizon profile and a layout date with its evidence tier, or a recorded reason for each missing field. The task is done when every town named above has such a record and the search for further measurable towns has been written down with its sources. The orientation hypothesis is scored separately under the frozen protocol of the town-axes package; its outcome does not change this card's pass rule.

# Prior attempts

The [town-axes package of 21 October](../../experiments/2026-10-21-town-axes/README.md) built the first version of the table with four blind measurers and a dating researcher, and scored the star-alignment conjecture on it once ([report](../../experiments/2026-10-21-town-axes/REPORT.md)). It holds 29 towns: 21 with coordinates and horizons, 4 with two independent true-north imagery bearings (Mohenjo-daro, Harappa, Lothal, Dholavira), 13 with plan bearings and their arrow labels, and 11 with a dated layout start. What remains is a true-north bearing for the towns whose excavations are backfilled or overgrown (Kalibangan, Banawali, Rakhigarhi, Chanhu-daro, Kanmer, Shikarpur, Surkotada and the optional towns), by registering the excavators' plans to ground control points or by field survey, and radiocarbon or Bayesian start boundaries for the layout phases dated only by cross-dating (Mohenjo-daro's lower town, Dholavira, Lothal, Chanhu-daro, Rangpur). Claim through the question's GitHub issue; maintainers record merged claims here.
