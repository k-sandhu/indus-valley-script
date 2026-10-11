"""Build one record per inscribed-find site entity from the 2026-10-06 evidence census.

Reads the four deep site batches, the local Lipi site register and the synthesis alias
joins, and writes data/sites-census.json. Standard library only. The script copies
values from the census rows; it does not add coordinates, dates or counts of its own.
Campaign year strings are parsed by a small rule set, and every entry the rules would
misread is curated by hand in CAMPAIGN_OVERRIDES with the source text quoted beside it.

Run: python experiments/2026-10-08-site-map-and-overview/build_site_table.py [--review]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CENSUS = ROOT / "experiments/2026-10-06-evidence-census"
DEEP = CENSUS / "sites-deep"
BATCH_FILES = OrderedDict([
    ("A", "a-pakistan-afghanistan"),
    ("B", "b-gujarat-kutch-maharashtra"),
    ("C", "c-north-india"),
    ("D", "d-finds-abroad"),
])
BATCH_SCOPE = {
    "A": "Pakistan and Afghanistan",
    "B": "Gujarat, Kutch and Maharashtra",
    "C": "North India",
    "D": "Finds abroad",
}
REGISTER = CENSUS / "sites-and-publications/site-register.csv"
JOINS = CENSUS / "synthesis/register-joins.json"
COVERAGE = ROOT / "experiments/2026-10-06-research-program/local-site-coverage.json"
OUT = HERE / "data/sites-census.json"

# ---------------------------------------------------------------------------
# Hand-curated campaign events. Key: "batch:row_index:campaign_index". The census
# row text is quoted in the comment above each entry. Fields not given here
# (directors, institution, source, locator, years text) are copied from the row.
# `first_year: False` keeps an event out of the first-fieldwork computation.
# ---------------------------------------------------------------------------
CAMPAIGN_OVERRIDES = {
    # A Amri: years "1929 discovery;1959–62 excavations", directors "N.G.Majumdar
    # (discovery);Jean-Marie Casal (excavations)", institution "French Archaeological Mission
    # to the Indus". The institution belongs to the excavations only.
    "A:1:0": [
        dict(start=1929, end=1929, kind="discovery", label="Discovered by N. G. Majumdar", directors="N.G.Majumdar"),
        dict(start=1959, end=1962, kind="excavation", label="Excavated by Jean-Marie Casal, French Archaeological Mission to the Indus",
             directors="Jean-Marie Casal"),
    ],
    # A Chanhu-daro: "2015–17;2018 mentioned in2017 paper publication programme"
    "A:4:2": [dict(start=2015, end=2017, kind="excavation",
                   label="Excavated by Aurore Didier with Pakistan/Sindh collaborators, French Mission to the Indus",
                   note="Row adds that 2018 is mentioned in the 2017 paper's publication programme.")],
    # A Harappa: years "1921;1923–25;1926–34", directors "Daya Ram Sahni;M.S.Vats".
    # Three year groups, two directors, no mapping in the row.
    "A:10:0": [
        dict(start=1921, end=1921, kind="excavation", label="Excavated by Daya Ram Sahni and M. S. Vats, ASI",
             note="Row gives three year groups and two directors without pairing them."),
        dict(start=1923, end=1925, kind="excavation", label="Excavated by Daya Ram Sahni and M. S. Vats, ASI",
             note="Row gives three year groups and two directors without pairing them."),
        dict(start=1926, end=1934, kind="excavation", label="Excavated by Daya Ram Sahni and M. S. Vats, ASI",
             note="Row gives three year groups and two directors without pairing them."),
    ],
    # A Hissam-dheri: "before 2019; exact date unreported"; method "Ground Penetrating
    # Radarandmagnetometersurveymentionedindependently; director/year not stated"
    "A:11:1": [dict(start=None, end=None, kind="survey",
                    label="Ground-penetrating radar and magnetometer survey",
                    note="Row: before 2019; exact date unreported.")],
    # A Judeirjo-daro: "before 1964; exact date unreported"; method "siteidentification
    # andsurface collection; excavation notreported"
    "A:13:0": [dict(start=None, end=None, kind="survey",
                    label="Identified by R. L. Raikes; surface collection by the Department of Archaeology",
                    note="Row: before 1964; exact date unreported. Excavation not reported.")],
    # A Lohumjo-daro: "1929–1931 surveyprogramme; site season exact date not recovered"
    "A:16:0": [dict(start=1929, end=1931, kind="survey",
                    label="Survey programme of Nani Gopal Majumdar, ASI",
                    note="Row: site season exact date not recovered; report title and snippets establish two trial trenches.")],
    # A Mundigak: "1951–1959, ten campaigns in DAFA account;1951–1958 listed by Uesugi and CISI 3.3"
    "A:20:0": [dict(start=1951, end=1959, kind="excavation",
                    label="Excavated by Jean-Marie Casal, DAFA",
                    note="Ten campaigns 1951–1959 in DAFA account; Uesugi and CISI 3.3 list 1951–1958.")],
    # A Murda Sang: years "1997 discovery;1998 trial trenching", director "Investigator account
    # by Ute Franke-Vogt; field director not explicitly identified in inspected page"
    "A:21:0": [
        dict(start=1997, end=1997, kind="discovery", label="Discovered; account by Ute Franke-Vogt", directors=""),
        dict(start=1998, end=1998, kind="excavation", label="Trial trenching, Joint German-Pakistani Archaeological Mission to Kalat",
             directors="", note="Field director not explicitly identified in the inspected page."),
    ],
    # A Naru-Waro-dharo: years "1955", directors "F.A.Khan attribution in Biagi 2024
    # reference50; institutional excavation confirmed by gazetteer"
    "A:22:0": [dict(start=1955, end=1955, kind="excavation",
                    label="Excavated by the Department of Archaeology, Pakistan; F. A. Khan per Biagi 2024",
                    note="Original 1955 report not inspected.")],
    # A Nausharo: "1986 onward (CISI2);1985–96 programme reported by archive snippet"
    "A:23:0": [
        dict(start=1986, end=None, kind="excavation", label="Excavated by Jean-François Jarrige, French Archaeological Mission to the Indus",
             note="CISI 2: 1986 onward."),
        dict(start=1985, end=1996, kind="excavation", label="Excavation programme of Jean-François Jarrige",
             note="1985–96 programme reported by an archive snippet; differs from CISI 2."),
    ],
    # A Rehman Dheri: "1976–1982; resumed 1991"; directors ["Farzand Ali Durrani",
    # "George Erdosy (1991 collaboration)"]
    "A:30:0": [
        dict(start=1976, end=1982, kind="excavation", label="Excavated by Farzand Ali Durrani, University of Peshawar",
             directors="Farzand Ali Durrani"),
        dict(start=1991, end=1991, kind="excavation", label="Excavation resumed by Farzand Ali Durrani with George Erdosy",
             directors="Farzand Ali Durrani; George Erdosy (1991 collaboration)"),
    ],
    # A Shortughai: "1975 survey; 1976 test trenches; 1977–1979 three campaigns";
    # directors "Jean-Claude Gardin (survey); Henri-Paul Francfort (excavation); ..."
    "A:32:0": [
        dict(start=1975, end=1975, kind="survey", label="Surveyed by Jean-Claude Gardin, DAFA", directors="Jean-Claude Gardin"),
        dict(start=1976, end=1976, kind="excavation", label="Test trenches by Henri-Paul Francfort, DAFA and CNRS",
             directors="Henri-Paul Francfort"),
        dict(start=1977, end=1979, kind="excavation", label="Three campaigns by Henri-Paul Francfort, DAFA and CNRS",
             directors="Henri-Paul Francfort; Z. Païman, M.-H. Pottier and N. Rasouli listed as collaborators"),
    ],
    # A Sotka Koh: "1960 sixweeks; Sutkagenvisit7October"; method "Discoveryandsurfacesurvey
    # near Pasni; trial excavationnotshown"
    "A:34:0": [dict(start=1960, end=1960, kind="survey",
                    label="Discovered and surveyed by George F. Dales, T. Cuyler Young, Jr. and M. Rafique Mughal",
                    note="Row method: discovery and surface survey near Pasni; trial excavation not shown.")],
    # A Sutkagen-dor: years "1876–1877;1927;1955", directors ["Major E.Mockler",
    # "Sir Aurel Stein", "Henry Field"], reason "Earliersurveys; exactdirectorinstitution
    # assignmentnotfullyaudited."
    "A:35:0": [
        dict(start=1876, end=1877, kind="survey", label="Early work by Major E. Mockler", directors="Major E. Mockler",
             note="Director-year pairing follows list order; row says assignment not fully audited."),
        dict(start=1927, end=1927, kind="survey", label="Visit by Sir Aurel Stein", directors="Sir Aurel Stein",
             note="Director-year pairing follows list order; row says assignment not fully audited."),
        dict(start=1955, end=1955, kind="survey", label="Survey by Henry Field, Peabody Museum Harvard", directors="Henry Field",
             note="Director-year pairing follows list order; row says assignment not fully audited."),
    ],
    # A Sutkagen-dor: "1960 sixweeks; Sutkagenvisit7October"; method "Survey and4smalltest
    # excavations A/A1, B, C, D"
    "A:35:1": [dict(start=1960, end=1960, kind="excavation",
                    label="Survey and four small test excavations by George F. Dales, T. Cuyler Young, Jr. and M. Rafique Mughal",
                    note="Sutkagen-dor visit on 7 October 1960.")],
    # B Dholavira: "13 seasons, 1989–90 to 2004–05; no work in 1993–94,1995–96,2000–01"
    "B:1:0": [dict(start=1989, end=2005, kind="excavation", label="Excavated by R. S. Bisht, ASI",
                   note="13 seasons, 1989–90 to 2004–05; no work in 1993–94, 1995–96, 2000–01.")],
    # B Kanmer: "2005–06 to 2008–09 covered by final volume; regional review describes field project to 2010"
    "B:3:0": [dict(start=2005, end=2010, kind="excavation",
                   label="Excavated by J. S. Kharakwal and Y. S. Rawat with Toshiki Osada",
                   note="Final volume covers 2005–06 to 2008–09; regional review describes the project to 2010.")],
    # B Khirsara: "2009–10 first new season; continuing project described as 2010–2013"
    "B:7:0": [dict(start=2009, end=2013, kind="excavation", label="Excavated by Jitendra Nath, ASI Excavation Branch V",
                   note="2009–10 first new season; continuing project described as 2010–2013.")],
    # B Rojdi: "1957–58 and 1958–59, earlier state excavation; seven later seasons beginning
    # 1982 and ending 1995"; director "P. P. Pandya and S. R. Rao in early campaigns;
    # Gregory L. Possehl and M. H. Raval in later project"
    "B:9:0": [
        dict(start=1957, end=1959, kind="excavation", label="Excavated by P. P. Pandya and S. R. Rao, Gujarat State Archaeology",
             directors="P. P. Pandya and S. R. Rao"),
        dict(start=1982, end=1995, kind="excavation",
             label="Seven seasons by Gregory L. Possehl and M. H. Raval, University of Pennsylvania and Gujarat State Archaeology",
             directors="Gregory L. Possehl and M. H. Raval"),
    ],
    # B Juni Kuran: "2003–04 to 2005–06 in regional review; official records specifically verify 2003–04 and 2004–05"
    "B:11:0": [dict(start=2003, end=2006, kind="excavation", label="Excavated by Shubhra Pramanik, ASI",
                    note="Regional review gives 2003–04 to 2005–06; official records verify 2003–04 and 2004–05.")],
    # B Navinal: "Initial exploration by P. P. Pandya in 1950s; systematic 2013–2017 surveys and two 2015 test pits"
    "B:13:0": [
        dict(start=None, end=None, kind="survey", label="Initial exploration by P. P. Pandya", directors="P. P. Pandya",
             note="Row gives the 1950s without a year."),
        dict(start=2013, end=2017, kind="survey", label="Systematic surveys by S. V. Rajesh, P. Ajithprasad, G. S. Abhayan and collaborators",
             directors="S. V. Rajesh, P. Ajithprasad, G. S. Abhayan and collaborating researchers"),
        dict(start=2015, end=2015, kind="excavation", label="Two test pits",
             directors="S. V. Rajesh, P. Ajithprasad, G. S. Abhayan and collaborating researchers"),
    ],
    # B Nagwada: "1985–1989; named annual campaigns 1986–87,1987–88,1988–89"
    "B:14:0": [dict(start=1985, end=1989, kind="excavation", label="Excavated by K. T. M. Hegde, M.S. University of Baroda",
                    note="Named annual campaigns 1986–87, 1987–88, 1988–89.")],
    # B Bet Dwarka: "NIO explorations 1981–1994/95; onshore and offshore operations"
    "B:16:0": [dict(start=1981, end=1995, kind="survey",
                    label="Onshore and offshore explorations by S. R. Rao, later Sundaresh and A. S. Gaur, National Institute of Oceanography",
                    note="Row: 1981–1994/95.")],
    # B Rangpur: "1935; November1936 on p.8 (1937 on p.10); March1947; December1953–March1954,
    # November1954–February1955,April1956"; director "M. S. Vats; G. S. Ghurye; M. G. Dikshit;
    # S. R. Rao respectively"
    "B:17:0": [
        dict(start=1935, end=1935, kind="excavation", label="Excavated by M. S. Vats, ASI", directors="M. S. Vats"),
        dict(start=1936, end=1936, kind="excavation", label="Excavated by G. S. Ghurye, University of Bombay", directors="G. S. Ghurye",
             note="November 1936 on p.8; 1937 on p.10 (internal discrepancy retained by the census)."),
        dict(start=1947, end=1947, kind="excavation", label="Excavated by M. G. Dikshit, Deccan College", directors="M. G. Dikshit"),
        dict(start=1953, end=1956, kind="excavation", label="Excavated by S. R. Rao, ASI", directors="S. R. Rao",
             note="December 1953–March 1954, November 1954–February 1955, April 1956."),
    ],
    # B Prabhas Patan: "1955–56,1956–57; re-excavation1971–72,1975–76,1976–77"; director
    # "Early B. Subbarao and P. P. Pandya; later Deccan College team; complete director-by-season
    # reconciliation unresolved"
    "B:18:0": [
        dict(start=1955, end=1957, kind="excavation", label="Excavated by B. Subbarao and P. P. Pandya",
             directors="B. Subbarao and P. P. Pandya"),
        dict(start=1971, end=1977, kind="excavation", label="Re-excavation by a Deccan College team",
             directors="Deccan College team", note="Seasons 1971–72, 1975–76, 1976–77; director-by-season reconciliation unresolved."),
    ],
    # B Nuhato: "2009 test trenches; March2018 eight-trench project"; director
    # "Kallemullah Lashari in2009; Qasid Hussain Mallah in2018"
    "B:20:0": [
        dict(start=2009, end=2009, kind="excavation", label="Test trenches under Kallemullah Lashari, Sindh Antiquities Department",
             directors="Kallemullah Lashari"),
        dict(start=2018, end=2018, kind="excavation", label="Eight-trench project under Qasid Hussain Mallah, Sindh Antiquities Department",
             directors="Qasid Hussain Mallah"),
    ],
    # B Juna Khatiya: "Exploration and excavation before2021 publication; exact years not
    # specified in the inspected primary passage;2024 institutional project lead retained in search log"
    "B:23:0": [dict(start=None, end=None, kind="excavation",
                    label="Exploration and excavation by University of Kerala and K.S.K.V. Kachchh University teams",
                    note="Before the 2021 publication; exact years not specified.")],
    # B Kanewal: "6–30 January1977 in monograph title; work reported under1977–78 annual review"
    "B:24:0": [dict(start=1977, end=1977, kind="excavation", label="Excavated by K. N. Momin under R. N. Mehta, M.S. University of Baroda",
                    note="6–30 January 1977 in monograph title; reported under the 1977–78 annual review.")],

    # C rows hold one free-text campaign paragraph each; all are curated here.
    # C Kalibangan: "Nine field seasons, 1961–1969; B. B. Lal and B. K. Thapar,
    # Archaeological Survey of India. Report title uses 1960–69."
    "C:0:0": [dict(start=1961, end=1969, kind="excavation", label="Excavated by B. B. Lal and B. K. Thapar, ASI",
                   directors="B. B. Lal and B. K. Thapar", note="Nine field seasons; report title uses 1960–69.")],
    # C Banawali: "R. S. Bisht: 1974–77 Haryana Department of Archaeology; later ASI seasons,
    # including 1987–88 final season, Excavation Branch V, Vadodara. Complete season-by-season
    # intervening list unresolved."
    "C:1:0": [
        dict(start=1974, end=1977, kind="excavation", label="Excavated by R. S. Bisht, Haryana Department of Archaeology", directors="R. S. Bisht"),
        dict(start=1987, end=1988, kind="excavation", label="Final ASI season under R. S. Bisht, Excavation Branch V", directors="R. S. Bisht",
             note="Intervening ASI seasons unresolved."),
    ],
    # C Rakhigarhi: "1997–98, 1998–99 and 1999–2000, Amarendra Nath, ASI. Later Deccan
    # College/Vasant Shinde campaigns are leads requiring season and inscription inventories."
    "C:2:0": [dict(start=1997, end=2000, kind="excavation", label="Excavated by Amarendra Nath, ASI", directors="Amarendra Nath",
                   note="Later Deccan College/Vasant Shinde campaigns are recorded as leads without seasons.")],
    # C Farmana: "Four consecutive seasons 2006–07 to 2009–10. Vasant Shinde and Manmohan Kumar,
    # Deccan College and M. D. University with RIHN; Toshiki Osada included in 2007–08 team."
    "C:3:0": [dict(start=2006, end=2010, kind="excavation",
                   label="Excavated by Vasant Shinde and Manmohan Kumar, Deccan College and M. D. University with RIHN",
                   directors="Vasant Shinde and Manmohan Kumar", note="Four seasons, 2006–07 to 2009–10.")],
    # C Bhirrana: "2003–04 through 2005–06, L. S. Rao, ASI Excavation Branch I, Nagpur. ..."
    "C:4:0": [dict(start=2003, end=2006, kind="excavation", label="Excavated by L. S. Rao, ASI Excavation Branch I", directors="L. S. Rao",
                   note="Opened primary reports cover 2003–04 and 2004–05; 2005–06 article is a bibliographic lead.")],
    # C Kunal: "Haryana Department of Archaeology work under J. S. Khatri and M. Acharya,
    # including 1985–86 and 1991–92. Complete campaign list and later seasons unresolved."
    "C:5:0": [
        dict(start=1985, end=1986, kind="excavation", label="Excavated by J. S. Khatri and M. Acharya, Haryana Department of Archaeology",
             directors="J. S. Khatri and M. Acharya", note="Complete campaign list unresolved."),
        dict(start=1991, end=1992, kind="excavation", label="Excavated by J. S. Khatri and M. Acharya, Haryana Department of Archaeology",
             directors="J. S. Khatri and M. Acharya"),
    ],
    # C Mitathal: "January–April 1968, Suraj Bhan, Kurukshetra University. ASI/CNRS sampling in
    # 1987–88 under R. S. Bisht and H. P. Francfort. 2006–07 and 2010–11 excavations appear in
    # later preliminary accounts; full campaign inventory unresolved."
    "C:6:0": [
        dict(start=1968, end=1968, kind="excavation", label="Excavated by Suraj Bhan, Kurukshetra University", directors="Suraj Bhan"),
        dict(start=1987, end=1988, kind="other", label="ASI/CNRS sampling under R. S. Bisht and H. P. Francfort",
             directors="R. S. Bisht and H. P. Francfort"),
        dict(start=2006, end=2007, kind="excavation", label="Excavation in later preliminary accounts", directors=""),
        dict(start=2010, end=2011, kind="excavation", label="Excavation in later preliminary accounts", directors=""),
    ],
    # C Sanauli: "August 2005–August 2006, D. V. Sharma, ASI. Later 2018–19 Sanjay Kumar
    # Manjul/Arvin Manjul excavations are publication leads; inscription count not verified."
    "C:7:0": [
        dict(start=2005, end=2006, kind="excavation", label="Excavated by D. V. Sharma, ASI", directors="D. V. Sharma"),
        dict(start=2018, end=2019, kind="excavation", label="Excavated by Sanjay Kumar Manjul and Arvin Manjul",
             directors="Sanjay Kumar Manjul; Arvin Manjul", note="Recorded as publication leads."),
    ],
    # C Alamgirpur: "1958–59 Y. D. Sharma, ASI, following a Bharat Sewak Samaj camp; 2008
    # R. N. Singh and C. A. Petrie, BHU and Cambridge."
    "C:8:0": [
        dict(start=1958, end=1959, kind="excavation", label="Excavated by Y. D. Sharma, ASI", directors="Y. D. Sharma",
             note="Following a Bharat Sewak Samaj camp."),
        dict(start=2008, end=2008, kind="excavation", label="Excavated by R. N. Singh and C. A. Petrie, BHU and Cambridge",
             directors="R. N. Singh and C. A. Petrie"),
    ],
    # C Hulas: "Five consecutive seasons 1978–79 to 1982–83; K. N. Dikshit, ASI Excavation Branch II, ..."
    "C:9:0": [dict(start=1978, end=1983, kind="excavation", label="Excavated by K. N. Dikshit, ASI Excavation Branch II",
                   directors="K. N. Dikshit", note="Five seasons, 1978–79 to 1982–83.")],
    # C Ropar: "1953–54 and 1954–55, Y. D. Sharma, ASI; 2011–12 V. N. Prabhakar, ASI Excavation Branch II, Delhi. ..."
    "C:10:0": [
        dict(start=1953, end=1955, kind="excavation", label="Excavated by Y. D. Sharma, ASI", directors="Y. D. Sharma"),
        dict(start=2011, end=2012, kind="excavation", label="Excavated by V. N. Prabhakar, ASI Excavation Branch II", directors="V. N. Prabhakar"),
    ],
    # C Chandigarh: "Chance discovery December 1969, Sector 17; excavation January 1970, ASI and
    # Punjab Directorate of Archaeology and Museums. J. S. Nigam, N. C. Ghosh, R. K. Pant and
    # B. M. Pande named as excavators."
    "C:11:0": [
        dict(start=1969, end=1969, kind="discovery", label="Chance discovery in Sector 17", directors=""),
        dict(start=1970, end=1970, kind="excavation",
             label="Excavated by J. S. Nigam, N. C. Ghosh, R. K. Pant and B. M. Pande, ASI and Punjab Directorate",
             directors="J. S. Nigam, N. C. Ghosh, R. K. Pant and B. M. Pande"),
    ],
    # C Kotla Nihang Khan: "Late July 1929, four trial trenches, Madho Sarup Vats, ASI, ..."
    "C:12:0": [dict(start=1929, end=1929, kind="excavation", label="Four trial trenches by Madho Sarup Vats, ASI",
                    directors="Madho Sarup Vats")],
    # C Sanghol: "Punjab Department excavation began 1968–69 under G. B. Sharma; 1985–86 to
    # 1989–90 ASI work under C. Margabandhu, alongside Punjab Department work. ..."
    "C:13:0": [
        dict(start=1968, end=1969, kind="excavation", label="Excavation begun by G. B. Sharma, Punjab Department", directors="G. B. Sharma",
             note="Row: excavation began 1968–69; later succession unresolved."),
        dict(start=1985, end=1990, kind="excavation", label="ASI excavation under C. Margabandhu", directors="C. Margabandhu"),
    ],
    # C Karanpura: "2012–13 and 2013–14, V. N. Prabhakar, ASI Excavation Branch II, ..."
    "C:14:0": [dict(start=2012, end=2014, kind="excavation", label="Excavated by V. N. Prabhakar, ASI Excavation Branch II",
                    directors="V. N. Prabhakar")],
    # C Binjor: "2014–15, 2015–16 and 2016–17 in the paper; Sanjay Kumar Manjul/Arvin Manjul, ASI
    # Institute of Archaeology with Excavation Branch II. Hosting summary instead names third
    # season 2017–18; unresolved discrepancy."
    "C:15:0": [dict(start=2014, end=2017, kind="excavation", label="Excavated by Sanjay Kumar Manjul and Arvin Manjul, ASI",
                    directors="Sanjay Kumar Manjul; Arvin Manjul",
                    note="Paper gives 2014–15 to 2016–17; a hosting summary names a third season in 2017–18.")],
    # C Baror: "2003–04 Urmila Sant; 2004–05 T. J. Baidya; ASI Excavation Branch III, Patna, ..."
    "C:16:0": [
        dict(start=2003, end=2004, kind="excavation", label="Excavated by Urmila Sant, ASI Excavation Branch III", directors="Urmila Sant"),
        dict(start=2004, end=2005, kind="excavation", label="Excavated by T. J. Baidya, ASI Excavation Branch III", directors="T. J. Baidya"),
    ],
    # C Tarkhanewala Dera: "2003–04 P. K. Trivedi and J. K. Patnaik, ASI Excavation Branch IV,
    # Bhubaneswar; earlier Ghosh survey/trials reported in 1953."
    "C:17:0": [
        dict(start=1953, end=1953, kind="report", label="Earlier survey and trials by Ghosh, reported in 1953", directors="Ghosh"),
        dict(start=2003, end=2004, kind="excavation", label="Excavated by P. K. Trivedi and J. K. Patnaik, ASI Excavation Branch IV",
             directors="P. K. Trivedi and J. K. Patnaik"),
    ],
    # C Manda: "1973 ASI North Western/Frontier Circle trials; December 1976 survey and excavation
    # beginning 15 April 1977, J. P. Joshi and Madhu Bala, ASI Exploration Branch."
    "C:18:0": [
        dict(start=1973, end=1973, kind="excavation", label="Trials by ASI North Western/Frontier Circle", directors=""),
        dict(start=1976, end=1976, kind="survey", label="Survey by J. P. Joshi and Madhu Bala, ASI", directors="J. P. Joshi and Madhu Bala"),
        dict(start=1977, end=1977, kind="excavation", label="Excavated by J. P. Joshi and Madhu Bala, ASI Exploration Branch",
             directors="J. P. Joshi and Madhu Bala", note="Excavation began 15 April 1977."),
    ],
    # C Lohari Ragho: "Surveys 2009 and 2014; excavations 2015 and 2017, R. N. Singh and C. A.
    # Petrie, ... Earlier Haryana surveys 1980–81 and Garge surveys use different component labels."
    "C:19:0": [
        dict(start=2009, end=2009, kind="survey", label="Survey by R. N. Singh and C. A. Petrie", directors="R. N. Singh and C. A. Petrie"),
        dict(start=2014, end=2014, kind="survey", label="Survey by R. N. Singh and C. A. Petrie", directors="R. N. Singh and C. A. Petrie"),
        dict(start=2015, end=2015, kind="excavation", label="Excavated by R. N. Singh and C. A. Petrie, BHU and Cambridge",
             directors="R. N. Singh and C. A. Petrie"),
        dict(start=2017, end=2017, kind="excavation", label="Excavated by R. N. Singh and C. A. Petrie, BHU and Cambridge",
             directors="R. N. Singh and C. A. Petrie",
             note="Row: earlier Haryana surveys (1980–81) and Garge surveys use different component labels; not entered as events here."),
    ],
    # C Masudpur: "2008 survey, April–May 2009 excavation of Masudpur I and VII; further Masudpur I
    # excavation 19 January–24 February 2018, R. N. Singh and C. A. Petrie, BHU/Cambridge. ..."
    "C:20:0": [
        dict(start=2008, end=2008, kind="survey", label="Survey by R. N. Singh and C. A. Petrie", directors="R. N. Singh and C. A. Petrie"),
        dict(start=2009, end=2009, kind="excavation", label="Excavation of Masudpur I and VII by R. N. Singh and C. A. Petrie",
             directors="R. N. Singh and C. A. Petrie"),
        dict(start=2018, end=2018, kind="excavation", label="Further excavation of Masudpur I by R. N. Singh and C. A. Petrie",
             directors="R. N. Singh and C. A. Petrie"),
    ],
    # C Bhagwanpura: "1975–76, J. P. Joshi and Madhu Bala, ASI; published final report in 1993."
    "C:21:0": [
        dict(start=1975, end=1976, kind="excavation", label="Excavated by J. P. Joshi and Madhu Bala, ASI", directors="J. P. Joshi and Madhu Bala"),
        dict(start=1993, end=1993, kind="report", label="Final report published", directors="J. P. Joshi and Madhu Bala"),
    ],
    # C Siswal: "Autumn 1970, 2 × 2 m trial trench, Suraj Bhan, Kurukshetra University; 1987–88
    # ASI/CNRS sampling under Bisht/Francfort."
    "C:22:0": [
        dict(start=1970, end=1970, kind="excavation", label="Trial trench by Suraj Bhan, Kurukshetra University", directors="Suraj Bhan"),
        dict(start=1987, end=1988, kind="other", label="ASI/CNRS sampling under R. S. Bisht and H. P. Francfort", directors="Bisht/Francfort"),
    ],
    # C Tigrana: "1987–88 Indo-French trial trenching, R. S. Bisht, ASI, and H. P. Francfort, CNRS.
    # 2016 excavation preliminary report by Narender Parmar and colleagues published in 2019; ..."
    "C:23:0": [
        dict(start=1987, end=1988, kind="excavation", label="Indo-French trial trenching by R. S. Bisht (ASI) and H. P. Francfort (CNRS)",
             directors="R. S. Bisht and H. P. Francfort"),
        dict(start=2016, end=2016, kind="excavation", label="Excavation reported by Narender Parmar and colleagues",
             directors="Narender Parmar and colleagues", note="Preliminary report published in 2019; article body not accessed."),
    ],
    # C Rohira: "1982–83 resumed excavation, G. B. Sharma, Punjab Department of Cultural Affairs,
    # Archaeology and Museums, assisted by ... Earlier seasons require a complete list."
    "C:24:0": [dict(start=1982, end=1983, kind="excavation", label="Resumed excavation by G. B. Sharma, Punjab Department",
                    directors="G. B. Sharma", note="Earlier seasons not listed in the row.")],

    # D rows hold one free-text campaign value each; all are curated here.
    # D Ur: "Gadd's objects derive from Woolley's campaigns 1923–1932; joint British Museum/University Museum expedition. ..."
    "D:0:0": [dict(start=1923, end=1932, kind="excavation", label="Excavated by Woolley, British Museum/University Museum expedition",
                   directors="Woolley")],
    # D Kish: "Oxford–Field Museum expedition, 1923–1933; reviewed book records campaigns under Langdon, Mackay and Watelin. ..."
    "D:1:0": [dict(start=1923, end=1933, kind="excavation", label="Oxford–Field Museum expedition under Langdon, Mackay and Watelin",
                   directors="Langdon, Mackay and Watelin", note="Season-by-season director attribution incomplete.")],
    # D Nippur: "Area WC-1 investigations in the 13th and 14th seasons, 1975–1976, Oriental Institute
    # expedition directed by McGuire Gibson; exact discovery day unresolved."
    "D:2:0": [dict(start=1975, end=1976, kind="excavation", label="Excavated by McGuire Gibson, Oriental Institute",
                   directors="McGuire Gibson", note="Area WC-1, 13th and 14th seasons.")],
    # D Tell Asmar: "1930–1932 Iraq Expedition, Henri Frankfort, Oriental Institute of Chicago; this report covers the second campaign."
    "D:3:0": [dict(start=1930, end=1932, kind="excavation", label="Excavated by Henri Frankfort, Oriental Institute Iraq Expedition",
                   directors="Henri Frankfort")],
    # D Girsu/Tello: "Twenty campaigns 1877–1933 are the stated scope of Parrot's final synthesis;
    # de Sarzec's early excavation publication underlies the Gulf seal."
    "D:4:0": [dict(start=1877, end=1933, kind="excavation", label="Twenty campaigns, the scope of Parrot's final synthesis",
                   directors="de Sarzec (early excavation)")],
    # D Umma: "SAHI project began 2016 under Drahoslav Hulínek with Iraqi partners; seasons 2016,
    # 2017, 2019 and 2020; Geneva/Bern Sumerologists joined the 2017 survey."
    "D:5:0": [dict(start=2016, end=2020, kind="other", label="SAHI project under Drahoslav Hulínek with Iraqi partners",
                   directors="Drahoslav Hulínek", note="Seasons 2016, 2017, 2019 and 2020.")],
    # D Susa: "de Morgan 1897–1912; de Mecquenem 1913–1939 with wartime interruption; Ghirshman
    # 1946–1967; Steve 1967–1968; Perrot 1968–1979, French delegation/mission."
    "D:7:0": [
        dict(start=1897, end=1912, kind="excavation", label="Excavated by de Morgan, French delegation", directors="de Morgan"),
        dict(start=1913, end=1939, kind="excavation", label="Excavated by de Mecquenem, French delegation", directors="de Mecquenem",
             note="With wartime interruption."),
        dict(start=1946, end=1967, kind="excavation", label="Excavated by Ghirshman, French mission", directors="Ghirshman"),
        dict(start=1967, end=1968, kind="excavation", label="Excavated by Steve, French mission", directors="Steve"),
        dict(start=1968, end=1979, kind="excavation", label="Excavated by Perrot, French mission", directors="Perrot"),
    ],
    # D Tepe Yahya: "Harvard excavations 1967–1975 directed by C. C. Lamberg-Karlovsky."
    "D:8:0": [dict(start=1967, end=1975, kind="excavation", label="Excavated by C. C. Lamberg-Karlovsky, Harvard",
                   directors="C. C. Lamberg-Karlovsky")],
    # D Shahr-i Sokhta: "Italian mission from 1967 under Maurizio Tosi; early reports cover 1967 and 1968. ..."
    "D:9:0": [dict(start=1967, end=None, kind="excavation", label="Italian mission under Maurizio Tosi", directors="Maurizio Tosi",
                   note="From 1967; early reports cover 1967 and 1968.")],
    # D Konar Sandal/Jiroft: "2002–2008 excavations directed by Yousef Majidzadeh; ..."
    "D:10:0": [dict(start=2002, end=2008, kind="excavation", label="Excavated by Yousef Majidzadeh", directors="Yousef Majidzadeh")],
    # D Tepe Hissar: "Schmidt, University of Pennsylvania, 1931–1932; 1972 surface survey; 1976
    # Pennsylvania/Turin/ICAR restudy; 1995 Iranian salvage excavation."
    "D:11:0": [
        dict(start=1931, end=1932, kind="excavation", label="Excavated by Schmidt, University of Pennsylvania", directors="Schmidt"),
        dict(start=1972, end=1972, kind="survey", label="Surface survey", directors=""),
        dict(start=1976, end=1976, kind="other", label="Pennsylvania/Turin/ICAR restudy", directors=""),
        dict(start=1995, end=1995, kind="excavation", label="Iranian salvage excavation", directors=""),
    ],
    # D Failaka: "Danish mission 1958–1963; Johns Hopkins 1973–1974; French 1984–1985; renewed
    # Kuwaiti-Danish 2008–2017 under Flemming Højlund."
    "D:12:0": [
        dict(start=1958, end=1963, kind="excavation", label="Danish mission", directors=""),
        dict(start=1973, end=1974, kind="excavation", label="Johns Hopkins work", directors=""),
        dict(start=1984, end=1985, kind="excavation", label="French work", directors=""),
        dict(start=2008, end=2017, kind="excavation", label="Kuwaiti-Danish work under Flemming Højlund", directors="Flemming Højlund"),
    ],
    # D Hili: "Hili 8 investigations in the late 1970s recognised Indus pottery; Serge Cleuziou and
    # Philippe Gouin are named in the paper's acknowledgements."
    "D:16:0": [dict(start=None, end=None, kind="other", label="Hili 8 investigations", directors="",
                    note="Late 1970s; Serge Cleuziou and Philippe Gouin are named in the paper's acknowledgements.")],
    # D Ras al-Jinz: "Joint Hadd Project of Serge Cleuziou and Maurizio Tosi; RJ-2 reports cited in
    # 1988, 1990 and 2000. Full season register unresolved."
    "D:17:0": [dict(start=1988, end=2000, kind="report", label="RJ-2 reports of the Joint Hadd Project of Serge Cleuziou and Maurizio Tosi",
                    directors="Serge Cleuziou and Maurizio Tosi", note="Reports cited in 1988, 1990 and 2000; season register unresolved.")],
    # D Salut: "Italian Mission, University of Pisa, with Sultan's cultural-affairs office, began
    # tower ST1 excavation in 2010; publication includes the ongoing 2015–2016 season."
    "D:18:0": [dict(start=2010, end=2016, kind="excavation", label="Tower ST1 excavation by the Italian Mission, University of Pisa",
                    directors="", note="Began 2010; publication includes the ongoing 2015–2016 season.")],
    # D Bat: "ArchaeOman describes Danish work from 1972 and later German projects; complete
    # director/campaign register remains unresolved."
    "D:19:0": [dict(start=1972, end=None, kind="other", label="Danish work from 1972, later German projects", directors="")],
    # D Umm an-Nar: "Danish Aarhus Museum settlement excavations 1959–1965; burial documentation 1959–1961."
    "D:20:0": [
        dict(start=1959, end=1965, kind="excavation", label="Settlement excavations by the Danish Aarhus Museum", directors=""),
        dict(start=1959, end=1961, kind="other", label="Burial documentation", directors=""),
    ],
    # D Altyn Depe: "Systematic Russian excavation from 1965; Masson and Kircho's publications underpin the corpus."
    "D:21:0": [dict(start=1965, end=None, kind="excavation", label="Systematic Russian excavation", directors="",
                    note="Masson and Kircho's publications underpin the corpus.")],
    # D Gonur Depe: "Sarianidi test trenches 1972 and 1974; broad excavation from 1988; north palace
    # 1991–1995 and 2002–2004; excavation led by Sarianidi until 2013 and later Nadezhda Dubova, ..."
    "D:22:0": [
        dict(start=1972, end=1972, kind="excavation", label="Test trenches by Sarianidi", directors="Sarianidi"),
        dict(start=1974, end=1974, kind="excavation", label="Test trenches by Sarianidi", directors="Sarianidi"),
        dict(start=1988, end=2013, kind="excavation", label="Broad excavation led by Sarianidi", directors="Sarianidi",
             note="North palace 1991–1995 and 2002–2004."),
        dict(start=None, end=None, kind="excavation", label="Excavation led by Nadezhda Dubova with Turkmen partners and Bern project",
             directors="Nadezhda Dubova", note="After Sarianidi's leadership ended in 2013."),
    ],
    # D Sarazm: "Isakov's Tajik archaeological project and French collaboration are documented in the
    # 1987 report; full season history requires the nomination dossier."
    "D:23:0": [dict(start=1987, end=1987, kind="report", label="Isakov's Tajik project with French collaboration, documented in a 1987 report",
                    directors="Isakov")],
    # D Shortughai: "French archaeological mission, Henri-Paul Francfort, 1976–1979; final report 1989."
    "D:30:0": [
        dict(start=1976, end=1979, kind="excavation", label="French archaeological mission under Henri-Paul Francfort", directors="Henri-Paul Francfort"),
        dict(start=1989, end=1989, kind="report", label="Final report", directors="Henri-Paul Francfort"),
    ],
    # D Nindowari-damb: "Jean-Marie Casal, 1962–1965, French archaeological mission."
    "D:31:0": [dict(start=1962, end=1965, kind="excavation", label="Excavated by Jean-Marie Casal, French archaeological mission",
                    directors="Jean-Marie Casal")],
    # D Miri Qalat: "French Archaeological Mission in Makran, Roland Besenval with Pakistan Department
    # of Archaeology and Museums, 1990–1996."
    "D:32:0": [dict(start=1990, end=1996, kind="excavation", label="Excavated by Roland Besenval, French Archaeological Mission in Makran",
                    directors="Roland Besenval")],
    # D Sibri: "Jarrige's French mission sequence at Mehrgarh, Nausharo and Sibri, 1975–2002;
    # Sibri-only season breakdown unresolved." Not site-specific, so kept out of first year.
    "D:33:0": [dict(start=1975, end=2002, kind="other", label="Jarrige's French mission sequence at Mehrgarh, Nausharo and Sibri",
                    directors="Jean-François Jarrige", first_year=False,
                    note="Sibri-only season breakdown unresolved; excluded from the first-fieldwork year.")],
    # D Murda Sang: "Discovered 1997 and trial trenched 1998; Ute Franke-Vogt's project account
    # documents the work. Precise director/institution allocation unresolved."
    "D:35:0": [
        dict(start=1997, end=1997, kind="discovery", label="Discovered; Ute Franke-Vogt's project account", directors=""),
        dict(start=1998, end=1998, kind="excavation", label="Trial trenching; Ute Franke-Vogt's project account", directors=""),
    ],
}

# Coordinate status adjustments where the row text, not its structure, marks the point as
# partial. Each reason quotes the row.
COORD_STATUS_OVERRIDES = {
    "A:2": ("census-partial", "Row: 'Secondary epigraphic corpus coordinate; its underlying gazetteer reference not established. "
                              "A report/gazetteer coordinate remains unresolved.'"),
}

KIND_VERB = {"discovery": "Discovered", "survey": "Surveyed", "excavation": "Excavated",
             "report": "Reported", "other": "Fieldwork"}
STATUS_RANK = {"census-verified": 0, "census-partial": 1, "census-candidate-unresolved": 2, "missing": 3}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def slug(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def text_of(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return "; ".join(text_of(x) for x in v if text_of(x))
    if isinstance(v, dict):
        return v.get("detail") or v.get("value") or ""
    return str(v)


def sources_of(entry):
    """Return (source_ids list, locator string) from any census evidence shape."""
    ids, locs = [], []
    if not isinstance(entry, dict):
        return ids, ""
    for key in ("source_id", "source"):
        if isinstance(entry.get(key), str):
            ids.append(entry[key])
    for key in ("source_ids", "sources"):
        ids.extend(x for x in as_list(entry.get(key)) if isinstance(x, str))
    for key in ("location", "locator", "source_page"):
        if isinstance(entry.get(key), str) and entry[key]:
            locs.append(entry[key])
    for ev in as_list(entry.get("evidence")):
        if isinstance(ev, dict):
            if ev.get("source_id"):
                ids.append(ev["source_id"])
            if ev.get("location"):
                locs.append(ev["location"])
    seen = []
    for x in ids:
        if x not in seen:
            seen.append(x)
    return seen, "; ".join(dict.fromkeys(locs))


# ---------------------------------------------------------------------------
# Coordinates
# ---------------------------------------------------------------------------
DMS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*°\s*(?:(\d+(?:\.\d+)?)\s*[′']\s*)?(?:(\d+(?:\.\d+)?)\s*[″\"]\s*)?([NSEW])")


def parse_dms(text):
    """Parse one '29°17.365′N' style value. Returns (value, note) or (None, reason)."""
    m = DMS_RE.search(text or "")
    if not m:
        return None, "unparsed"
    deg, mins, secs, hemi = m.groups()
    mins_f = float(mins) if mins else 0.0
    secs_f = float(secs) if secs else 0.0
    if mins_f >= 60 or secs_f >= 60:
        return None, f"malformed printed value {text!r} (minutes or seconds exceed 60)"
    val = float(deg) + mins_f / 60 + secs_f / 3600
    if hemi in "SW":
        val = -val
    note = ""
    if secs and len(secs.split(".")[0]) == 3 and secs.startswith("0"):
        note = f"printed seconds '{secs}' read as {int(float(secs))}"
    return round(val, 6), note


def parse_spaced(text):
    """Parse D-batch strings such as 'N32 11 22.05 E48 15 22.94' or 'N36.1500 E54.3500'."""
    parts = re.findall(r"([NSEW])\s*([\d.]+(?:\s+[\d.]+){0,2})", text or "")
    out = {}
    for hemi, nums in parts:
        vals = [float(x) for x in nums.split()]
        v = vals[0] + (vals[1] / 60 if len(vals) > 1 else 0) + (vals[2] / 3600 if len(vals) > 2 else 0)
        if hemi in "SW":
            v = -v
        out["lat" if hemi in "NS" else "lon"] = round(v, 6)
    return out.get("lat"), out.get("lon")


def coord_record(batch, idx, row):
    """Return a coordinate witness dict for one census row."""
    rec = dict(lat=None, lon=None, coord_status="missing", coord_source_ids=[], coord_locator="", coord_note="",
               candidate_lat=None, candidate_lon=None, candidate_points=[], printed_value=None)
    c = row["identity"]["coordinates"] if batch == "D" else row.get("coordinates")
    if not isinstance(c, dict):
        rec["coord_note"] = "no coordinate field in row"
        return rec
    ids, loc = sources_of(c)
    rec["coord_source_ids"], rec["coord_locator"] = ids, loc

    if batch == "A":
        status = c.get("status")
        lat = c.get("latitude")
        lon = c.get("longitude")
        if isinstance(c.get("value"), list) and len(c["value"]) == 2:
            lat, lon = c["value"]
        if isinstance(c.get("value"), str):
            rec["printed_value"] = c["value"]
        if lat is not None and lon is not None:
            rec["lat"], rec["lon"] = round(float(lat), 6), round(float(lon), 6)
            if status == "partial":
                rec["coord_status"] = "census-partial"
                rec["coord_note"] = c.get("coordinate_basis", "")
            else:
                rec["coord_status"] = "census-verified"
                rec["coord_note"] = c.get("note") or c.get("precision") or c.get("confidence") or ""
            if c.get("candidate_object_locality"):
                k = c["candidate_object_locality"]
                rec["candidate_points"].append(dict(name=k.get("name"), lat=k.get("latitude"), lon=k.get("longitude"),
                                                    source_id=k.get("source_id"), locator=k.get("locator"),
                                                    note=k.get("join_status")))
        else:
            cand = c.get("candidate")
            reason = c.get("detail") or c.get("reason") or "unresolved"
            if isinstance(cand, dict) and cand.get("latitude") is not None:
                rec["coord_status"] = "census-candidate-unresolved"
                rec["candidate_lat"], rec["candidate_lon"] = round(cand["latitude"], 6), round(cand["longitude"], 6)
                cids, cloc = sources_of(cand)
                rec["candidate_points"].append(dict(lat=cand["latitude"], lon=cand["longitude"], source_id="; ".join(cids),
                                                    locator=cloc, note="accepted: false" if cand.get("accepted") is False else ""))
                rec["coord_source_ids"], rec["coord_locator"] = cids, cloc
            rec["coord_note"] = reason

    elif batch == "B":
        if c.get("latitude") is not None:
            rec["lat"], rec["lon"] = round(c["latitude"], 6), round(c["longitude"], 6)
            rec["coord_status"] = "census-verified"
            rec["coord_note"] = c.get("conflicts") or c.get("precision_note") or ""
            rec["printed_value"] = c.get("original")
        elif c.get("bounding_box"):
            bb = c["bounding_box"]
            rec["lat"] = round((bb["south"] + bb["north"]) / 2, 6)
            rec["lon"] = round((bb["west"] + bb["east"]) / 2, 6)
            rec["coord_status"] = "census-partial"
            rec["coord_note"] = ("bounding-box centroid of the published extent " + (c.get("original") or "") +
                                 "; " + (c.get("note") or "")).strip("; ")
            rec["printed_value"] = c.get("original")
        else:
            rec["coord_note"] = c.get("reason") or "no coordinate"

    elif batch == "C":
        v = c.get("value")
        if isinstance(v, dict):
            basis = v.get("basis", "")
            partial = any(w in basis for w in ("proxy", "cluster", "shared", "unresolved"))
            note_bits = [basis]
            if v.get("latitude") is not None:
                lat, lon = v["latitude"], v["longitude"]
                ok = True
            else:
                rec["printed_value"] = f"{v.get('latitude_text')} {v.get('longitude_text')}"
                lat, n1 = parse_dms(v.get("latitude_text"))
                lon, n2 = parse_dms(v.get("longitude_text"))
                ok = lat is not None and lon is not None
                note_bits += [n for n in (n1, n2) if n and lat is not None and lon is not None]
                if not ok:
                    note_bits = [f"printed {rec['printed_value']}: " + "; ".join(n for n in (n1, n2) if n)]
            if ok:
                rec["lat"], rec["lon"] = round(lat, 6), round(lon, 6)
                rec["coord_status"] = "census-partial" if partial else "census-verified"
            pm = v.get("protected_monument_candidates")
            if pm:
                for la, lo in zip(pm["latitude_values"], pm["longitude_values"]):
                    rec["candidate_points"].append(dict(lat=la, lon=lo, source_id=pm.get("source_id"), locator=pm.get("location"),
                                                        note="official register mound point; match to the site unresolved"))
                if not ok:
                    rec["coord_status"] = "census-candidate-unresolved"
            if c.get("limitation"):
                note_bits.append(c["limitation"])
            rec["coord_note"] = "; ".join(b for b in note_bits if b)
        else:
            rec["coord_note"] = c.get("explanation") or c.get("status") or "no coordinate"

    elif batch == "D":
        v = c.get("value")
        if isinstance(v, str):
            rec["printed_value"] = v
            lat, lon = parse_spaced(v)
            if lat is not None and lon is not None:
                rec["lat"], rec["lon"] = lat, lon
                loc_text = c.get("location", "")
                rec["coord_status"] = "census-partial" if ("island-scale" in loc_text or "not every" in loc_text) else "census-verified"
                rec["coord_note"] = loc_text
        else:
            rec["coord_note"] = c.get("reason") or "unresolved"

    key = f"{batch}:{idx}"
    if key in COORD_STATUS_OVERRIDES and rec["lat"] is not None:
        rec["coord_status"], why = COORD_STATUS_OVERRIDES[key]
        rec["coord_note"] = (rec["coord_note"] + "; " if rec["coord_note"] else "") + "status override: " + why
    return rec


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------
YEAR_RE = re.compile(r"(?<!\d)(1[89]\d\d|20\d\d)(?:\s*[–-]\s*(\d{4}|\d{2})(?!\d))?")
KIND_PATTERNS = [
    ("discovery", re.compile(r"discover", re.I)),
    ("survey", re.compile(r"survey|reconnaissance|exploration|surface collection|identification", re.I)),
    ("excavation", re.compile(r"excavat|trench|season|campaign", re.I)),
]


def years_in(text):
    text = re.sub(r"as listed by.*", "", text)
    ys = []
    for m in YEAR_RE.finditer(text):
        a = int(m.group(1))
        ys.append(a)
        if m.group(2):
            b = m.group(2)
            b = int(b) if len(b) == 4 else (a // 100) * 100 + int(b)
            if b >= a:
                ys.append(b)
    return ys


def kind_of(*texts):
    for t in texts:
        for kind, pat in KIND_PATTERNS:
            if t and pat.search(t):
                return kind
    return None


def clean_label(s):
    s = re.sub(r"\.(?=[A-Z][a-z])", ". ", s)
    s = re.sub(r"(?<=[a-z]),(?=[A-Z])", ", ", s)
    return re.sub(r"\s+", " ", s).strip()


def campaign_entries(batch, row):
    if batch == "C":
        return [row["excavation_campaigns"]]
    return as_list(row.get("excavation_campaigns"))


def parse_campaigns(batch, idx, row, log):
    events, skipped = [], []
    for ci, e in enumerate(campaign_entries(batch, row)):
        key = f"{batch}:{idx}:{ci}"
        if e.get("status") in ("unresolved", "unresolved_after_search") or (e.get("value") is None and not e.get("years")):
            skipped.append(dict(campaign_index=ci, status=e.get("status"),
                                reason=e.get("detail") or e.get("reason") or "", search_ids=e.get("search_ids", [])))
            continue
        years_text = e.get("years") or e.get("value") or ""
        directors = e.get("directors", e.get("director", ""))
        directors = "; ".join(directors) if isinstance(directors, list) else (directors or "")
        inst = e.get("institutions", e.get("institution", ""))
        inst = "; ".join(inst) if isinstance(inst, list) else (inst or "")
        ids, loc = sources_of(e)
        base = dict(years=years_text, directors=directors, institution=inst, source_id="; ".join(ids), locator=loc,
                    row_note="; ".join(text_of(e.get(k)) for k in ("method", "detail", "reason", "disagreement",
                                                                     "disagreements", "limitation", "note") if text_of(e.get(k))))
        if key in CAMPAIGN_OVERRIDES:
            for o in CAMPAIGN_OVERRIDES[key]:
                ev = dict(base)
                ev.update(start_year=o["start"], end_year=o["end"], kind=o["kind"], label=o["label"],
                          note=o.get("note", ""), parse="override", counts_for_first_year=o.get("first_year", True))
                if "directors" in o:
                    ev["directors"] = o["directors"]
                events.append(ev)
            log["override"].append(key)
            continue
        if batch in ("C", "D"):
            log["unhandled"].append(key)
        segments = [s.strip() for s in years_text.split(";") if s.strip()]
        dparts = [d.strip() for d in directors.split(";") if d.strip()] if directors else []
        if isinstance(e.get("directors"), list):
            dparts = [d for d in e["directors"]]
        align = len(dparts) == len(segments) > 1 and ("respectively" in directors or all("(" in d for d in dparts))
        seg_events = []
        for si, seg in enumerate(segments):
            ys = years_in(seg)
            if not ys:
                if seg_events:
                    seg_events[-1]["note"] = (seg_events[-1]["note"] + "; " if seg_events[-1]["note"] else "") + seg
                continue
            d = dparts[si] if align else directors
            d = re.sub(r"\s*respectively\s*$", "", d)
            kind = kind_of(seg) or kind_of(base["row_note"], directors) or "excavation"
            # Label only: drop caveat clauses and pairing parentheticals; `directors` keeps the row text.
            who_parts = [p for p in re.split(r"\s*;\s*", d)
                         if p and not re.search(r"unresolved|not stated|not verified|not explicit|field director", p, re.I)]
            who = clean_label("; ".join(re.sub(r"\s*\((?:\d{4}[^)]*|discovery|excavations?)\)", "", p) for p in who_parts))
            label = f"{KIND_VERB[kind]} by {who}" if who else f"{KIND_VERB[kind]}"
            if inst and len(inst) < 60 and not re.search(r"\bnot\b", inst, re.I):
                label += f", {clean_label(inst)}"
            ev = dict(base)
            ev.update(start_year=min(ys), end_year=max(ys), kind=kind, label=label, directors=d,
                      note="", parse="auto", counts_for_first_year=True)
            seg_events.append(ev)
        if not seg_events:
            ev = dict(base)
            ev.update(start_year=None, end_year=None, kind=kind_of(years_text, base["row_note"]) or "excavation",
                      label=clean_label(directors) or "Fieldwork", note="no year in row text", parse="auto",
                      counts_for_first_year=True)
            seg_events.append(ev)
        events.extend(seg_events)
        log["auto"].append(key)
    return events, skipped


# ---------------------------------------------------------------------------
# Counts and dating notes
# ---------------------------------------------------------------------------
def count_entry(e, batch):
    if not isinstance(e, dict):
        return None
    val = e.get("count", e.get("value"))
    if val is None or isinstance(val, (dict, list, str)):
        return None
    ids, loc = sources_of(e)
    return dict(object_class=e.get("object_class") or e.get("class"), value=val, unit=e.get("unit"),
                count_date=e.get("count_date", e.get("date_of_count", e.get("date"))),
                basis=e.get("count_basis") or e.get("basis") or e.get("scope") or "",
                source_id="; ".join(ids), locator=loc, batch=batch)


def reported_counts(batch, row):
    key = {"A": "reported_object_counts", "B": "reported_counts", "C": "reported_object_counts", "D": "published_counts"}[batch]
    out = [count_entry(e, batch) for e in as_list(row.get(key))]
    return [x for x in out if x]


def m77_counts(batch, row):
    out = []
    if batch == "A":
        m = row.get("mahadevan_1977_count") or {}
        if m.get("count") is not None:
            out.append(dict(value=m["count"], unit=m.get("unit"), count_date=m.get("date_of_count"),
                            source_id=m.get("source_id"), locator=m.get("location"), batch=batch))
    elif batch == "B":
        m = row.get("mahadevan1977") or {}
        if m.get("value") is not None:
            ids, loc = sources_of(m)
            out.append(dict(value=m["value"], unit=m.get("unit"), count_date=m.get("count_date"),
                            source_id="; ".join(ids), locator=loc, batch=batch))
    elif batch == "C":
        m = row.get("mahadevan_1977_or_icit_count") or {}
        if m.get("main_corpus_objects") is not None:
            ids, loc = sources_of(m)
            aids, aloc = sources_of({"evidence": m.get("addendum_evidence")})
            out.append(dict(value=m["main_corpus_objects"], unit=m.get("unit"), count_date=m.get("count_date"),
                            addendum_objects=m.get("addendum_objects"), addendum_locator=aloc,
                            source_id="; ".join(ids), locator=loc, batch=batch))
    elif batch == "D":
        m = row.get("icit_mahadevan_counts") or {}
        if m.get("value") is not None:
            ids, loc = sources_of(m)
            out.append(dict(value=m["value"], source_id="; ".join(ids), locator=loc, batch=batch))
    return out


def icit_counts(batch, row):
    out = []
    if batch == "A":
        m = row.get("icit_count") or {}
        if m.get("count") is not None:
            ids, loc = sources_of(m)
            out.append(dict(value=m["count"], unit=m.get("unit_or_basis"), count_date=m.get("date"),
                            icit_id=m.get("id"), source_id="; ".join(ids), locator=loc, batch=batch))
    elif batch == "B":
        m = row.get("icit_site_count") or {}
        if m.get("value") is not None:
            ids, loc = sources_of(m)
            out.append(dict(value=m["value"], unit=m.get("unit"), count_date=m.get("count_date"),
                            basis=m.get("count_basis"), source_id="; ".join(ids), locator=loc, batch=batch))
    return out


def cisi_entries(batch, row):
    out = []
    if batch == "A":
        c = row.get("cisi") or {}
        ids = c.get("source_ids", [])
        if c.get("verified_ranges"):
            for vol, text in c["verified_ranges"].items():
                out.append(dict(volume=f"CISI {vol}", range=text, source_id="; ".join(ids), batch=batch))
        if c.get("volume_or_range"):
            out.append(dict(volume=c["volume_or_range"], range=c["volume_or_range"], catalogue_objects=c.get("count"),
                            note=c.get("basis"), source_id="; ".join(ids), locator=c.get("locator"), batch=batch))
        if c.get("volume"):
            rng = c.get("catalogue_range")
            pages = c.get("page_range") or c.get("supplement_page_range")
            out.append(dict(volume=f"{c['volume']}" + (f" ({c['year']})" if c.get("year") else ""), range=rng, pages=pages,
                            note=c.get("count_basis") or c.get("alias") or "", source_id="; ".join(ids),
                            locator=c.get("locator"), batch=batch))
        for v in as_list(c.get("volumes")):
            ids2, loc2 = sources_of(v)
            out.append(dict(volume=f"{v.get('volume')} ({v.get('year')})", range=v.get("cisi_identifiers"),
                            pages=v.get("page_range"), source_id="; ".join(ids2), locator=loc2, batch=batch))
    elif batch == "B":
        for v in as_list(row.get("cisi_coverage")):
            if v.get("identifier_range"):
                ids, loc = sources_of(v)
                out.append(dict(volume=f"{v['volume']} ({v.get('year')})", range=v["identifier_range"], pages=v.get("page_range"),
                                catalogue_objects=v.get("catalogue_object_slots"), source_id="; ".join(ids), locator=loc,
                                batch=batch))
    elif batch == "C":
        c = row.get("cisi_coverage") or {}
        if c.get("entry_range"):
            ids, loc = sources_of(c)
            out.append(dict(volume=f"{c['volume']} ({c.get('year')})", range=c["entry_range"], pages=c.get("page_range"),
                            catalogue_objects=c.get("catalogue_objects"), note=c.get("limitation"),
                            source_id="; ".join(ids), locator=loc, batch=batch))
            lv = c.get("later_volume")
            if lv:
                ids, loc = sources_of(lv)
                out.append(dict(volume=f"{lv['volume']} ({lv.get('year')})", range=None, pages=lv.get("page_range"),
                                note=lv.get("limitation"), source_id="; ".join(ids), locator=loc, batch=batch))
    elif batch == "D":
        c = row.get("cisi_coverage") or {}
        if isinstance(c.get("value"), str):
            ids, loc = sources_of(c)
            out.append(dict(volume=None, range=c["value"], source_id="; ".join(ids), locator=loc, batch=batch))
    return out


def dating_notes(batch, row):
    meta_key = {"A": "publication_metadata", "B": "metadata_available", "C": "main_publication_metadata",
                "D": "publication_metadata"}[batch]
    meta = row.get(meta_key) or {}
    out = []
    for field in ("stratum_or_phase", "absolute_dates"):
        m = meta.get(field)
        if not isinstance(m, dict):
            continue
        status = m.get("status") or m.get("availability")
        if status not in ("yes", "partial"):
            continue
        if batch == "A":
            text = m.get("detail") or m.get("note") or ""
        elif batch == "B":
            text = m.get("scope") or ""
        elif batch == "C":
            text = m.get("explanation") or ""
        else:
            text = m.get("location") or ""
        ids, loc = sources_of(m)
        if not text:
            continue
        # D rows put the descriptive text in `location`; it is both the statement and its locator.
        shown = "; ".join(ids) if batch == "D" else ", ".join(x for x in ("; ".join(ids), loc) if x)
        out.append(dict(field=field, status=status, text=text, source_id="; ".join(ids), locator=loc,
                        source=shown, batch=batch))
    return out


# ---------------------------------------------------------------------------
# Row loading
# ---------------------------------------------------------------------------
def load_rows():
    rows = []
    for batch, folder in BATCH_FILES.items():
        path = DEEP / folder / "site-rows.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data["sites"] if batch == "A" else data["rows"] if batch == "C" else data
        for i, r in enumerate(items):
            if batch == "D":
                ident = r["identity"]
                name = ident["canonical_name"]
                alts = ident.get("alternative_spellings", [])
                labels = list(r.get("local_labels", []))
                country = ident["country"]["value"]
                prov = ident["province"].get("value")
                region = r.get("region")
                status = r.get("status")
                scope = r.get("scope")
            else:
                name = r["canonical_name"]
                alts = r.get("alternative_spellings", [])
                lc = r.get("local_corpus") or {}
                labels = [lc["site"]] if lc.get("site") and not lc.get("site_label_absent") and lc.get("label_present", True) else []
                country = r.get("country")
                prov = r.get("province") if batch != "C" else r.get("province_or_union_territory")
                if isinstance(prov, dict):
                    prov = prov.get("detail")
                region = lc.get("region")
                status = r.get("status") or r.get("evidence_status")
                scope = r.get("batch_scope")
            rows.append(dict(batch=batch, index=i, file=rel(path), name=name, alts=alts, labels=labels, country=country,
                             province=prov, region=region, status=status, scope=scope, raw=r,
                             entity_id=r.get("site_entity_id")))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--review", action="store_true", help="print every parsed campaign event for checking")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    rows = load_rows()
    coverage = {s["site"]: s for s in json.loads(COVERAGE.read_text(encoding="utf-8"))["sites"]}
    register = list(csv.DictReader(REGISTER.open(encoding="utf-8-sig")))
    joins = json.loads(JOINS.read_text(encoding="utf-8"))["site_aliases"]

    # Group rows: synthesis alias joins first, every other row alone.
    by_pointer = {f"{r['file']}#row={r['index']}": r for r in rows}
    groups, grouped = [], set()
    merges = []
    for j in joins:
        members = []
        for p in j["row_pointers"]:
            key = p.split(";name=")[0]
            r = by_pointer[key]
            members.append(r)
            grouped.add(id(r))
        groups.append(dict(canonical=j["canonical"], rows=members, join_status=j["status"]))
        merges.append(dict(canonical=j["canonical"], join_status=j["status"],
                           rows=[f"{r['batch']}:{r['index']} {r['name']}" for r in members],
                           source=rel(JOINS) + "#site_aliases"))
    for r in rows:
        if id(r) not in grouped:
            groups.append(dict(canonical=r["name"], rows=[r], join_status=None))
    groups.sort(key=lambda g: (min("ABCD".index(r["batch"]) for r in g["rows"]), min(r["index"] for r in g["rows"])))

    log = {"auto": [], "override": [], "unhandled": []}
    entities = []
    for g in groups:
        g["rows"].sort(key=lambda r: ("ABCD".index(r["batch"]), r["index"]))
        prim = next((r for r in g["rows"] if r["name"] == g["canonical"]), g["rows"][0])
        names = []
        for r in g["rows"]:
            names += [r["name"]] + list(r["alts"]) + list(r["labels"])
        labels = list(dict.fromkeys(l for r in g["rows"] for l in r["labels"]))
        coords = [dict(coord_record(r["batch"], r["index"], r["raw"]), batch=r["batch"], index=r["index"]) for r in g["rows"]]
        best = sorted(coords, key=lambda c: (STATUS_RANK[c["coord_status"]], "ABCD".index(c["batch"])))[0]
        events, skipped = [], []
        for r in g["rows"]:
            ev, sk = parse_campaigns(r["batch"], r["index"], r["raw"], log)
            for e in ev:
                e["batch"] = r["batch"]
            for s in sk:
                s["batch"], s["row_index"] = r["batch"], r["index"]
            events += ev
            skipped += sk
        uniq, seen = [], set()
        for e in events:
            k = (e["start_year"], e["end_year"], e["kind"], e["label"], e["source_id"], e["locator"])
            if k not in seen:
                seen.add(k)
                uniq.append(e)
        events = uniq
        notes = []
        for r in g["rows"]:
            notes += dating_notes(r["batch"], r["raw"])
        merged_notes = OrderedDict()
        for n in notes:
            k = (n["text"], n["source"])
            if k in merged_notes:
                if n["field"] not in merged_notes[k]["field"]:
                    merged_notes[k]["field"] += "; " + n["field"]
            else:
                merged_notes[k] = dict(n)
        notes = list(merged_notes.values())
        ent = OrderedDict()
        ent["id"] = slug(g["canonical"])
        ent["name"] = g["canonical"]
        ent["alternative_spellings"] = [n for n in dict.fromkeys(names) if n != g["canonical"]]
        ent["batch"] = prim["batch"]
        ent["batches"] = list(dict.fromkeys(r["batch"] for r in g["rows"]))
        ent["batch_scope"] = BATCH_SCOPE[prim["batch"]]
        region = prim["region"] or next((r["region"] for r in g["rows"] if r["region"]), None)
        ent["region"] = region or BATCH_SCOPE[prim["batch"]]
        ent["region_basis"] = ("local corpus or census region label" if region else "census batch scope (no local region label)")
        ent["country"] = prim["country"]
        ent["province"] = prim["province"]
        ent["row_scope"] = prim["scope"]
        ent["census_entity_id"] = prim["entity_id"]
        ent["lat"], ent["lon"] = best["lat"], best["lon"]
        ent["coord_status"] = best["coord_status"]
        ent["coord_source_id"] = "; ".join(best["coord_source_ids"])
        ent["coord_locator"] = best["coord_locator"]
        ent["coord_source"] = ", ".join(x for x in (ent["coord_source_id"], best["coord_locator"]) if x)
        ent["coord_note"] = best["coord_note"]
        ent["coord_printed_value"] = best["printed_value"]
        ent["coord_from_row"] = f"{best['batch']}:{best['index']}"
        ent["candidate_lat"], ent["candidate_lon"] = best["candidate_lat"], best["candidate_lon"]
        ent["candidate_points"] = best["candidate_points"]
        ent["coord_alternatives"] = [dict(row=f"{c['batch']}:{c['index']}", lat=c["lat"], lon=c["lon"], coord_status=c["coord_status"],
                                          source_id="; ".join(c["coord_source_ids"]), locator=c["coord_locator"], note=c["coord_note"])
                                     for c in coords if c is not best]
        ent["fieldwork"] = events
        ent["campaigns_unresolved"] = skipped
        firsts = [e for e in events if e["start_year"] is not None and e["counts_for_first_year"] and e["kind"] != "report"]
        reports = [e for e in events if e["start_year"] is not None and e["kind"] == "report"]
        f = min(firsts, key=lambda e: e["start_year"]) if firsts else None
        rp = min(reports, key=lambda e: e["start_year"]) if reports else None
        ent["first_fieldwork_upper_bound"] = False
        if f and (not rp or f["start_year"] <= rp["start_year"]):
            ent["first_fieldwork_year"] = f["start_year"]
            ent["first_fieldwork_basis"] = f"{f['kind']}: {f['label']} ({f['years']}; {f['source_id']}, {f['locator']})"
        elif rp:
            ent["first_fieldwork_year"] = rp["start_year"]
            ent["first_fieldwork_upper_bound"] = True
            ent["first_fieldwork_basis"] = (f"report year, so fieldwork is no later than this: {rp['label']} "
                                            f"({rp['years']}; {rp['source_id']}, {rp['locator']})")
        else:
            ent["first_fieldwork_year"] = None
            ent["first_fieldwork_basis"] = "no dated fieldwork event in the census rows"
        # Counts
        lab_recs = []
        for l in labels:
            s = coverage.get(l)
            lab_recs.append(dict(label=l, faces=s["faces"] if s else 0, object_families=s["object_families"] if s else 0,
                                 distinct_cisi_ids=s["distinct_cisi_ids"] if s else 0,
                                 object_classes=s["object_classes"] if s else {}))
        ent["_labels"] = labels
        ent["_lab_recs"] = lab_recs
        counts = OrderedDict()
        counts["m77"] = [m for r in g["rows"] for m in m77_counts(r["batch"], r["raw"])]
        counts["cisi"] = [c for r in g["rows"] for c in cisi_entries(r["batch"], r["raw"])]
        counts["icit"] = [c for r in g["rows"] for c in icit_counts(r["batch"], r["raw"])]
        dmin = [r["raw"].get("published_indus_related_minimum_objects") for r in g["rows"] if r["batch"] == "D"]
        counts["published_indus_related_minimum_objects"] = dmin[0] if dmin else None
        counts["other_reported"] = [c for r in g["rows"] for c in reported_counts(r["batch"], r["raw"])]
        for k in ("m77", "cisi", "icit", "other_reported"):
            # Alias rows in one batch (Gharo Bhiro and Nuhato in A) repeat identical entries.
            counts[k] = list({json.dumps(x, sort_keys=True, ensure_ascii=False): x for x in counts[k]}.values())
        ent["counts"] = counts
        ent["dating_notes"] = notes
        ent["status"] = prim["status"]
        ent["census_row_ref"] = [dict(batch=r["batch"], file=r["file"], index=r["index"], name=r["name"]) for r in g["rows"]]
        ent["merge"] = (dict(join_status=g["join_status"], source=rel(JOINS) + "#site_aliases",
                             rows=[f"{r['batch']}:{r['index']}" for r in g["rows"]]) if len(g["rows"]) > 1 else None)
        entities.append(ent)

    # Register labels: attach to entities by alias, else create register-only entities.
    index = {}
    for ent in entities:
        keys = [ent["name"]] + ent["alternative_spellings"]
        keys += [re.sub(r"\s*\(.*?\)\s*", "", k) for k in keys] + re.findall(r"\(([^)]*)\)", ent["name"])
        for k in keys:
            nk = norm(k)
            if nk:
                if nk in index and index[nk] is not ent:
                    print(f"WARNING alias collision {k!r}: {index[nk]['name']} / {ent['name']}")
                index.setdefault(nk, ent)
    reg_unmatched, not_entities = [], []
    for i, r in enumerate(register):
        label = r["site"]
        if label == "Unknown":
            not_entities.append(dict(label=label, faces=int(r["local_lipi_face_rows"]), entity_type=r["entity_type"],
                                     register_row=i))
            continue
        ent = index.get(norm(label))
        reg = dict(label=label, entity_type=r["entity_type"], country_or_region=r["country_or_region"],
                   local_lipi_face_rows=int(r["local_lipi_face_rows"]), local_mayig_face_rows=int(r["local_mayig_face_rows"]),
                   register_row=i)
        if ent is None:
            ent = OrderedDict(id=slug(label), name=label, alternative_spellings=[], batch="register-only", batches=[],
                              batch_scope=None, region=coverage.get(label, {}).get("region"),
                              region_basis="local corpus region label", country=r["country_or_region"],
                              province=None, row_scope=None, census_entity_id=None, lat=None, lon=None, coord_status="missing",
                              coord_source_id="", coord_locator="", coord_source="", coord_note="no deep-census row",
                              coord_printed_value=None, coord_from_row=None, candidate_lat=None, candidate_lon=None,
                              candidate_points=[], coord_alternatives=[], fieldwork=[], campaigns_unresolved=[],
                              first_fieldwork_upper_bound=False, first_fieldwork_year=None,
                              first_fieldwork_basis="no deep-census row", _labels=[], _lab_recs=[],
                              counts=OrderedDict(m77=[], cisi=[], icit=[], published_indus_related_minimum_objects=None,
                                                 other_reported=[]),
                              dating_notes=[], status=r["status"], census_row_ref=[], merge=None)
            entities.append(ent)
            index[norm(label)] = ent
            reg_unmatched.append(label)
        ent.setdefault("register_labels", []).append(reg)
        if label not in ent["_labels"]:
            ent["_labels"].append(label)
            s = coverage.get(label)
            ent["_lab_recs"].append(dict(label=label, faces=s["faces"] if s else 0,
                                         object_families=s["object_families"] if s else 0,
                                         distinct_cisi_ids=s["distinct_cisi_ids"] if s else 0,
                                         object_classes=s["object_classes"] if s else {}))
        if label not in ent["alternative_spellings"] and label != ent["name"]:
            ent["alternative_spellings"].append(label)

    # Finalise local counts and field order.
    final = []
    for ent in entities:
        recs = ent.pop("_lab_recs")
        ent.pop("_labels")
        classes = Counter()
        for x in recs:
            classes.update(x["object_classes"])
        local = OrderedDict(
            faces=sum(x["faces"] for x in recs), object_families=sum(x["object_families"] for x in recs),
            distinct_cisi_ids=sum(x["distinct_cisi_ids"] for x in recs), object_classes=dict(classes),
            mayig_face_rows=sum(x["local_mayig_face_rows"] for x in ent.get("register_labels", [])),
            labels=recs, source=rel(COVERAGE),
            note="Sum of literal site-label rows in the local Lipi export; faces and families are not verified unique objects.")
        counts = OrderedDict(local_lipi=local)
        counts.update(ent["counts"])
        ent["counts"] = counts
        ent.setdefault("register_labels", [])
        final.append(ent)

    # Summary
    with_c = [e for e in final if e["lat"] is not None]
    summary = OrderedDict()
    summary["total_entities"] = len(final)
    summary["with_coordinates"] = len(with_c)
    summary["without_coordinates"] = len(final) - len(with_c)
    summary["by_coord_status"] = dict(Counter(e["coord_status"] for e in final))
    summary["by_batch"] = {b: dict(total=n, with_coordinates=sum(1 for e in final if e["batch"] == b and e["lat"] is not None))
                           for b, n in Counter(e["batch"] for e in final).items()}
    summary["by_country"] = {c: dict(total=n, with_coordinates=sum(1 for e in final if e["country"] == c and e["lat"] is not None))
                             for c, n in sorted(Counter(e["country"] for e in final).items())}
    summary["with_first_fieldwork_year"] = sum(1 for e in final if e["first_fieldwork_year"] is not None)
    summary["census_rows_read"] = len(rows)
    summary["merges"] = merges
    summary["register_labels_matched"] = sum(len(e["register_labels"]) for e in final)
    summary["register_only_entities"] = reg_unmatched
    summary["register_labels_not_entities"] = not_entities
    summary["local_faces_in_entities"] = sum(e["counts"]["local_lipi"]["faces"] for e in final)
    summary["campaign_parsing"] = dict(auto_entries=len(log["auto"]), override_entries=len(log["override"]),
                                       unresolved_entries_skipped=sum(len(e["campaigns_unresolved"]) for e in final),
                                       unhandled_free_text=log["unhandled"])
    summary["missing_coordinates"] = [dict(id=e["id"], name=e["name"], country=e["country"], region=e["region"],
                                           province=e["province"], coord_status=e["coord_status"])
                                      for e in final if e["lat"] is None]

    out = OrderedDict()
    out["title"] = "Indus-script find sites from the 2026-10-06 evidence census"
    out["generated_by"] = rel(Path(__file__))
    out["status"] = "Exploratory. Values are copied from census rows; coordinates are never added here."
    out["inputs"] = [f"{rel(DEEP / f)}/site-rows.json" for f in BATCH_FILES.values()] + [rel(REGISTER), rel(JOINS), rel(COVERAGE)]
    out["field_notes"] = {
        "coord_status": "census-verified: numeric point accepted in the row; census-partial: the row marks the point as a proxy, "
                        "area centroid or locality, or (Bet Dwarka) the point is the centroid of a published bounding box; "
                        "census-candidate-unresolved: only an unaccepted candidate exists, kept in candidate_lat/candidate_lon "
                        "or candidate_points; missing: no point in any row.",
        "fieldwork": "Events parsed from excavation_campaigns. parse=override marks hand-curated entries (see CAMPAIGN_OVERRIDES "
                     "in the script). 'years' is the row's text verbatim.",
        "first_fieldwork_year": "Earliest start_year among discovery, survey, excavation and other events that count for the "
                                "first year. If only a report year is earlier or available, it is used with "
                                "first_fieldwork_upper_bound=true.",
        "counts": "Copied per row, not reconciled. B-batch ICIT values count legible sign occurrences, not objects.",
        "dating_notes": "stratum_or_phase and absolute_dates entries whose availability is yes or partial, text verbatim. "
                        "Most describe what dating metadata a source offers; a few state a period or BCE range. "
                        "D-batch rows keep the text in the locator field, so text and locator are the same string.",
        "batch": "Batch of the primary row; merged entities list every contributing batch in `batches`.",
    }
    out["summary"] = summary
    out["sites"] = final
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"wrote {rel(OUT)}: {len(final)} entities, {len(with_c)} with coordinates")
    print("by status:", summary["by_coord_status"])
    print("campaign parsing:", summary["campaign_parsing"])
    if args.review:
        for e in final:
            print(f"\n## {e['name']} [{e['batch']}] first={e['first_fieldwork_year']} coords={e['lat']},{e['lon']} {e['coord_status']}")
            for ev in e["fieldwork"]:
                print(f"   {ev['parse']:8} {ev['kind']:10} {ev['start_year']}-{ev['end_year']} | {ev['label']} | <{ev['years']}>"
                      + (f" | note: {ev['note']}" if ev['note'] else ""))


if __name__ == "__main__":
    main()
