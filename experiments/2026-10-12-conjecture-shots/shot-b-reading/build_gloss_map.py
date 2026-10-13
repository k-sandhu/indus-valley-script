"""Build GLOSS-MAP.json for Shot B from the hand assignments below and discovery evidence.

Every sign with at least ten tokens in the discovery half receives a class, a working
English gloss, a picture note, a rival gloss and prior proposals. Evidence counts,
the frequency and position bands of the rearrangement null and the attributes used by
the predictions are computed here from the discovery half only.

Classes
  NUM    numeral (stroke count)
  LINK   grammatical link between an institution and a holder ("of", "household of")
  AFF    affiliation: name of a great household or institution that opens a legend
  NAME   element of a personal name
  COMM   commodity, unit, department or counted item; qualifies an office or is counted
  TITLE  office or role noun
  DET    closing determinative after an office ("the man", "the body", "the office")

Attributes
  official   AFF, TITLE, and the institutional determinatives 400 and 621
  locality   "local" for NAME and COMM, "pan" for every other class
  stock      for NAME and COMM only: "H" if at least 45% of discovery tokens are on
             Harappa-genre tablets (TAB:B, TAB:I); "MD" if at least 30% are on copper
             tablets (TAB:C); otherwise ""
"""
import collections
import csv
import json

from common_b import DISC, SHOT, UNKNOWN, ends, load_discovery, otype_group

# code: (class, gloss, picture, rival gloss, prior proposals)
G = {
    # ---- numerals -------------------------------------------------------------------
    "001": ("NUM", "one", "one short stroke", "after 820 a link variant like 002", "Mahadevan 1986 separates short-stroke markers from numerals; project catalogue: medial quantity or relation marker"),
    "003": ("NUM", "three", "three short strokes", "a fixed name part in N+390 legends", "numeral since Hunter 1934; Mahadevan 1977"),
    "004": ("NUM", "four", "four short strokes", "fixed name part", "numeral; Mahadevan 1977"),
    "005": ("NUM", "five", "five short strokes", "fixed name part", "numeral; Mahadevan 1977"),
    "013": ("NUM", "three (two over one)", "two short strokes over one", "a grammatical marker after openers, like 002", "numeral three in two tiers; project catalogue: quantity"),
    "016": ("NUM", "six", "two tiers of three", "asterism count (Parpola's six-star group)", "Parpola 1988 six strokes + fish = Pleiades"),
    "017": ("NUM", "seven", "four over three", "asterism count (seven sages)", "Parpola 1988 seven strokes + fish = Ursa Major"),
    "055": ("NUM", "twelve", "three tiers of four", "a single grid sign, not a number", "structure-first step 4 notes the twelve-stroke excess"),
    "031": ("NUM", "one (standard unit)", "one tall stroke", "a word divider or name part", "Wells 2008 tall strokes differ in value from short strokes"),
    "032": ("NUM", "two (standard units)", "two tall strokes", "fixed part of 032-220 (Parpola's Venus reading)", "Wells 2008; Mahadevan 1997 on Parpola's two-long-stroke fish"),
    "033": ("NUM", "three (standard units)", "three tall strokes", "fixed part of the 705-033-520 title", "Wells 2008 W700 + stroke modules"),
    "034": ("NUM", "four (standard units)", "four tall strokes", "a tier mark on tablets", "Wells 2008"),
    "035": ("NUM", "five (standard units)", "five tall strokes", "a tier mark", "Wells 2008"),
    # ---- links ----------------------------------------------------------------------
    "002": ("LINK", "of (links an institution to its holder)", "two short strokes, raised", "the number two", "Mahadevan 1986 superscript short strokes as grammatical markers; Fairservis 1992 paired dash as genitive; Yadav 2019 opener modules"),
    "060": ("LINK", "of (links the bow and cross households to the holder)", "a stroke beside a hooked stroke", "a numeral-like marker or a separate word", "project catalogue: medial quantity or relation marker"),
    "741": ("LINK", "household of", "jar with one inner stroke", "a jar-type commodity (a filled store jar)", "project catalogue: property or possessed account class"),
    "742": ("LINK", "household of (variant)", "jar with two inner strokes", "a graded store jar", "project catalogue: property or possessed account class"),
    "745": ("LINK", "household of (variant)", "jar with three inner strokes", "a graded store jar", "project catalogue: property or possessed account class"),
    # ---- affiliations (openers) ------------------------------------------------------
    "861": ("AFF", "the temple estate (household of the god)", "lozenge with an inner chevron at the top", "a city or polity name", "project catalogue: lord, master or responsible holder; Yadav 2019 opener module; Bose 2026 opener community"),
    "817": ("AFF", "the temple estate (allograph of 861)", "lens with an inner chevron at the top", "a city or polity name", "project catalogue: lord, master; Khanna and Merriam 2025 list 002-817"),
    "820": ("AFF", "the royal household (the wheel)", "lens crossed by six spokes", "a deity name; a city name", "project catalogue: deity or divine affiliation"),
    "920": ("AFF", "the household of the bow (a military household)", "bow-shaped bracket with a knot at mid-height", "a ruler's title", "project catalogue: king, chief or ruling office"),
    "692": ("AFF", "the household of the crossed staves (paired with 920)", "outlined X", "a rank title", "project catalogue: prosperity or sri name element"),
    # ---- offices and roles -----------------------------------------------------------
    "740": ("TITLE", "steward, keeper of a store", "storage jar with out-turned ears and pointed base", "genitive 'of, belonging to' (Mahadevan 1970-73; Bonta 'as'); priest (Mahadevan 1982)", "Mahadevan 1982 jar = priest ideogram suffixed to names; project catalogue: be, belong to the account holder"),
    "520": ("TITLE", "guard, armed retainer", "arrowhead or lance on a shaft", "the counted unit 'arrow' in 033-520", "Mahadevan 1982 lance = warrior; project catalogue: acceptance or possession predicate"),
    "151": ("TITLE", "porter, office-bearer", "man with a yoke and two hanging loads", "a carrier-service category", "Mahadevan 1982 bearer = officer or functionary; Rao 2018 carrier labour; project catalogue: load-carrier"),
    "154": ("TITLE", "store-porter (carrier of jars)", "yoke-bearer whose head is jar ears", "a counted container load", "Mahadevan 1982 jar-bearer ligature; project catalogue: qualified carrier"),
    "156": ("TITLE", "store-porter (counted)", "yoke-bearer with jar-ear head", "a counted container load", "Mahadevan 1982; project catalogue: qualified carrier or counted container-load"),
    "158": ("TITLE", "store-porter of the tablet series", "yoke-bearer with jar ears and crossed body", "a counted container load", "Mahadevan 1982; project catalogue: qualified carrier"),
    "527": ("TITLE", "warden of a barred enclosure", "barred panel with side uprights", "a container or suffix category", "project catalogue: bounded institutional or account-class suffix"),
    "617": ("TITLE", "keeper of the twin granaries", "two adjacent grids", "a measure of land in two plots", "project catalogue: adjacent grids, paired compartments"),
    "142": ("TITLE", "overseer (staff-bearer)", "man holding a staff", "a personal name", "project catalogue: staff-bearing person or responsible agent"),
    "140": ("TITLE", "lady, matron", "figure with breasts and one raised arm", "a goddess name", "project catalogue: mother, woman or female household representative"),
    "097": ("TITLE", "retainer of the house", "man standing between two tall strokes", "a work-party unit", "project catalogue: person, household member or work-party unit"),
    "091": ("TITLE", "partners, joint holders", "two men side by side", "a two-person work party", "project catalogue: two-person work party or joint household"),
    "137": ("TITLE", "servant", "man with a small object at the waist", "a work-party unit", "project catalogue: person, household member or work-party unit"),
    "095": ("TITLE", "drover, herdsman", "man holding a short stick", "a personal name", "project catalogue: staff-holder, overseer"),
    "125": ("TITLE", "archer", "man holding a bow and arrow", "a wealth or donation name element", "project catalogue: wealth, donation or dhana name element"),
    "368": ("TITLE", "banner-bearer", "upright with a hatched triangular flag", "a storage compartment", "project catalogue: measured allotment, container or storage compartment"),
    "061": ("TITLE", "chief of (prefixed to an office)", "reversed lambda", "a name element", "project catalogue: protector, lord or natha name element"),
    # ---- determinatives --------------------------------------------------------------
    "090": ("DET", "the man (an individual holder)", "standing man", "a personal title 'person'", "Parpola, Parpola and Brunswig 1977 link the man sign with personal names; project catalogue: person-related"),
    "400": ("DET", "the body (the office as an institution)", "upright with four teeth to one side (comb)", "a closing account category or tally", "project catalogue: closing account category or counted group; comb kankata"),
    "621": ("DET", "the office (the house of the office)", "tall box divided by an inner bar", "a maker or kara name element", "project catalogue: maker, doing or kara name element"),
    # ---- commodities, units, departments --------------------------------------------
    "700": ("COMM", "standard measure (bowl)", "plain U-shaped bowl", "a tier or rank token", "Wells 2008 W700 number modules; Fuls 2020 volumes; project catalogue: name element"),
    "390": ("COMM", "share of grain (sheaf)", "forked stalk with a central stem", "a keeper title", "project catalogue: keeper/protector or measured unit"),
    "405": ("COMM", "large share (sheaf with side shoot)", "forked stalk with a side shoot", "a variant of 390 with the same value", "project catalogue: keeper/protector or measured unit"),
    "407": ("COMM", "share of fodder (twigged stalk)", "stalk with a side twig", "a variant of 390", "project catalogue: keeper/protector or measured unit"),
    "590": ("COMM", "granary bin", "square box with a central post on top", "a name syllable", "project catalogue: sound component bhu"),
    "176": ("COMM", "cloth (seated weaver with a comb)", "seated figure holding a toothed tool", "water or irrigation allocation", "project catalogue: water, channel or irrigation allocation"),
    "100": ("COMM", "labour gang (many-headed man)", "man with three heads", "a personal name element", "project catalogue: person-related"),
    "415": ("COMM", "field work (rake)", "rake or harrow with five tines on a shaft", "a name syllable", "Mahadevan's arrow/harrow discussion; project catalogue: name syllable sa"),
    "760": ("COMM", "seed grain (sprouting vessel)", "vessel with branching sprouts at the rim", "a registered possession", "project catalogue: receipt or registered possession"),
    "923": ("COMM", "sealed portion (outlined bracket)", "bracket drawn in outline", "a connector", "project catalogue: affiliation or recipient connector"),
    "904": ("COMM", "double portion (two brackets)", "two nested brackets", "a connector", "project catalogue: affiliation or recipient connector"),
    "900": ("COMM", "portion (bracket)", "single bracket", "a connector or genitive", "project catalogue: recipient, affiliation or genitive-like connector"),
    "384": ("COMM", "fruit (inverted leaf with stem)", "inverted heart-shaped leaf on a stem", "a fibre crop", "project catalogue: plant produce, cultivated fruit or fibre crop"),
    "388": ("COMM", "fruit harvest (hatched inverted leaf)", "hatched inverted leaf on a stem", "a fibre crop", "project catalogue: plant produce"),
    "382": ("COMM", "single fruit", "inverted leaf on a short stem", "a fibre crop", "project catalogue: plant produce"),
    "482": ("COMM", "upland store (hill with marker)", "outlined tall caret with a diamond at the apex", "water allocation", "project catalogue: water, channel or wet-land allocation"),
    "480": ("COMM", "hill pasture (counted)", "tall caret", "a hill-district name", "project catalogue: upland origin or hill-name"),
    "717": ("COMM", "basket of goods", "U with hatched side and strokes", "a ration container", "project catalogue: container, capacity or stored ration"),
    "840": ("COMM", "double bale", "two overlapping lenses", "a name syllable ra", "project catalogue: sound component ra"),
    "585": ("COMM", "hall, roofed store (the Seven Halls with 017)", "peaked frame with an inner arrow and splayed feet", "a doorway (dvara) or raised store", "project catalogue: protected premises or raised store; anchor-expansion review rejects doorway"),
    "575": ("COMM", "platform, threshing floor", "open trapezoid with a small box on top", "a name syllable so", "project catalogue: sound component so"),
    "615": ("COMM", "field plot (grid)", "rectangle divided into a grid", "a measure or mana name element", "project catalogue: measure, esteem or mana name element"),
    "460": ("COMM", "grain heaps", "three tall triangles in a row", "grouped allotments", "project catalogue: grouped allotments or summary of counted lots"),
    "463": ("COMM", "small heaps", "three small triangles on a base", "hills or places", "project catalogue: multiple hills or grouped allotments"),
    "335": ("COMM", "pen, enclosure", "box with two peaks on the rim", "a settlement", "project catalogue: enclosure, store, settlement"),
    "711": ("COMM", "sealed vessel", "U crossed by an X", "mixed contents", "project catalogue: mixed or joined contents"),
    "705": ("COMM", "filled bowl (grain)", "U with a long stroke inside", "a name syllable ma", "project catalogue: sound component ma"),
    "706": ("COMM", "filled bowl (oil)", "U with a stroke ending in a drop", "a name syllable ma", "project catalogue: sound component ma"),
    "550": ("COMM", "bound bale (tied bundle)", "pincer or bowtie with open ends", "a craft output", "project catalogue: work, manufacture, craft output"),
    "555": ("COMM", "bound bale (variant)", "pincer with side tick", "a craft output", "project catalogue: work, manufacture"),
    "554": ("COMM", "bound bale (variant)", "bowtie without the joining stroke", "a craft output", "project catalogue: work, manufacture"),
    "440": ("COMM", "storeroom (doorway frame)", "rectangle open at the bottom with one leg short", "a household account", "project catalogue: household account, store or recorded holding"),
    "501": ("COMM", "graded measure", "triangle with inner marks", "a subdivided container", "project catalogue: subdivided container, measured share"),
    "595": ("COMM", "lidded box", "striped box with a post on top", "a name syllable kha", "project catalogue: sound component kha"),
    "845": ("COMM", "fodder bundle", "two overlapping hatched leaves", "a territory or polity", "project catalogue: territory, polity or institutional domain"),
    "321": ("COMM", "rack, frame", "H with two bars and a hanging stroke", "an honoured person", "project catalogue: honoured person or Aryaka name"),
    "790": ("COMM", "kernel, seed", "plain lens", "an estate or land parcel", "project catalogue: estate, land parcel or produce account"),
    "540": ("COMM", "tied pair", "closed bowtie", "a paired portion", "project catalogue: paired portion or joining candidate"),
    "905": ("COMM", "double portion, toothed (copper-tablet form of 904)", "two nested brackets with an outward tooth", "a connector", "project catalogue: affiliation, recipient or connecting element"),
    "435": ("COMM", "sickle (harvest)", "zigzag with a hook", "a name syllable hu", "project catalogue: sound component hu"),
    "436": ("COMM", "sickle (tablet variant)", "zigzag with a hook, reversed", "a name syllable hu", "project catalogue: sound component hu"),
    "690": ("COMM", "bound sheaves (double cross)", "two nested chevron pairs", "a name syllable ja", "project catalogue: sound component ja"),
    "171": ("COMM", "sapling (counted)", "T with two leaves", "paired holdings", "project catalogue: paired holdings or association"),
    "070": ("COMM", "standard pole (with 520: guard of the standard)", "upright with two arms", "a victory or jaya name element", "project catalogue: victory, bowstring or jaya name element"),
    "413": ("COMM", "tally (notched stick)", "upright with many crossbars", "a counted series", "project catalogue: counted series, inventory total or scale"),
    "605": ("COMM", "hatched store", "hatched tall box with a small side box", "a storage compartment", "project catalogue: measured allotment, container or storage compartment"),
    # ---- name elements ---------------------------------------------------------------
    "220": ("NAME", "Star (theophoric name element)", "fish with crossed tail and fins", "a counted commodity 'fish'", "Parpola et al. 1969 and Parpola 1994 fish = star rebus; Mahadevan 1986 modified fish interchangeable; project catalogue: fish/asset denomination"),
    "240": ("NAME", "Elder Star (fish with whiskers)", "fish with cheek strokes", "a weight class", "Parpola 1994; project catalogue: asset denomination or weight class"),
    "235": ("NAME", "Lord Star (capped fish)", "fish under a caret", "a weight class", "Parpola 1994; Mahadevan 1986; project catalogue: asset denomination"),
    "233": ("NAME", "Barred Star", "fish crossed by a bar", "a graded asset", "Mahadevan 1986; project catalogue: marked fish or graded asset"),
    "231": ("NAME", "Marked Star", "fish with an inner stroke", "provisions", "Mahadevan 1986; project catalogue: marked fish or asset class"),
    "226": ("NAME", "Star of the four (dotted fish; asterism)", "fish with four dots at the corners", "a weight class", "Parpola 1988 asterism names"),
    "236": ("NAME", "Lord Star of the four (capped dotted fish)", "capped fish with four dots", "a weight class", "Parpola 1988"),
    "255": ("NAME", "Spotted one (hatched creature)", "hatched oval with fins, possibly a creature", "a messenger or bird", "project catalogue: bird, messenger or mobile service"),
    "798": ("NAME", "Leaf-pincer", "leaf with pincers at one end", "a fibre or textile unit", "project catalogue: fibre processor or weaver"),
    "803": ("NAME", "Leaf-trident", "leaf enclosing a three-pronged stem", "a produce account", "project catalogue: large asset denomination or produce-account unit"),
    "806": ("NAME", "Leaf-tree", "leaf enclosing a branched stem", "a produce account", "project catalogue: large asset denomination or produce-account unit"),
    "832": ("NAME", "Leaf with a mark", "leaf with one inner stroke", "a supporting authority", "project catalogue: holder, bearer or supporting authority"),
    "503": ("NAME", "Ladder-peak", "tall hatched triangle", "a measured allotment", "project catalogue: measured allotment"),
    "495": ("NAME", "Hatched horn", "hatched curved triangle", "a subdivided container", "project catalogue: subdivided container"),
    "350": ("NAME", "Prongs over a pot", "prongs above a small oval", "a vara name element", "project catalogue: choice, favour or vara name element"),
    "416": ("NAME", "Double rake", "rake with two stacked heads", "a saha name element", "project catalogue: together or saha name element"),
    "892": ("NAME", "Bow with arrow", "D-shaped bow crossed by an arrow", "wealth or donation", "project catalogue: wealth, donation or dhana name element"),
    "890": ("NAME", "Bow", "D-shaped bow", "wealth or gift", "project catalogue: wealth, gift or bow-related name"),
    "850": ("NAME", "Lozenge", "plain diamond", "an estate or land parcel", "project catalogue: estate, land parcel"),
    "877": ("NAME", "Cluster of jewels", "diamond with four small diamonds", "Sripati name", "project catalogue: lord of prosperity or Sripati/Suripati name"),
    "630": ("NAME", "Toothed frame", "tall box with teeth top and bottom", "a para name prefix", "project catalogue: superior, further or para name element"),
    "632": ("NAME", "Toothed frame (variant)", "toothed box with marks on top", "a para name prefix", "project catalogue: superior or para name element"),
    "165": ("NAME", "Hook", "bracket closed at the top with a hook", "a pra prefix", "project catalogue: forth, forward or pra name prefix"),
    "175": ("NAME", "Seated one", "seated figure", "water allocation", "project catalogue: water, channel or irrigation allocation"),
    "455": ("NAME", "Triple point", "three joined triangles", "a levy or kara element", "project catalogue: hand, doing, levy or kara name element"),
    "500": ("NAME", "Divided peak", "triangle with a central divider", "a graded measure", "project catalogue: graded measure or capacity allotment"),
    "530": ("NAME", "Half-closed cross", "X closed on one side", "wealth or vasu", "project catalogue: wealth, good or vasu name element"),
    "297": ("NAME", "Rays", "three slanted parallel strokes", "a mana element", "project catalogue: measure, esteem or mana name element"),
    "318": ("NAME", "Comb-frame", "H with strokes hanging below the bar", "an enclosure", "project catalogue: enclosure, store, settlement"),
}


def main():
    rows = load_discovery()
    tok = collections.Counter(s for r in rows for s in r["signs_reading_rtl"] if s != UNKNOWN)
    ttype = collections.defaultdict(collections.Counter)
    for r in rows:
        g = otype_group(r["object_type"])
        for s in r["signs_reading_rtl"]:
            if s != UNKNOWN:
                ttype[s][g] += 1
    distinct = set()
    for r in rows:
        si, ei = ends(r)
        seq = tuple(r["signs_reading_rtl"])
        if r["single_line"] and si and ei and seq and UNKNOWN not in seq:
            distinct.add((otype_group(r["object_type"]), seq))
    pos = collections.defaultdict(collections.Counter)
    prev_ = collections.defaultdict(collections.Counter)
    next_ = collections.defaultdict(collections.Counter)
    for g, seq in distinct:
        ext = ("^",) + seq + ("$",)
        for i in range(1, len(ext) - 1):
            s = ext[i]
            prev_[s][ext[i - 1]] += 1
            next_[s][ext[i + 1]] += 1
            if len(seq) >= 2:
                pos[s]["initial" if i == 1 else "final" if i == len(seq) else "medial"] += 1

    frequent = [s for s, n in tok.most_common() if n >= 10]
    missing = [s for s in frequent if s not in G]
    extra = [s for s in G if s not in frequent]
    if missing or extra:
        raise SystemExit(f"gloss table mismatch: missing {missing}, extra {extra}")

    def fband(n):
        return "100+" if n >= 100 else "40-99" if n >= 40 else "20-39" if n >= 20 else "10-19"

    signs = []
    for s in frequent:
        cls, gloss, pic, rival, prior = G[s]
        p = pos[s]
        t = sum(p.values()) or 1
        ini, fin = p["initial"] / t, p["final"] / t
        pband = "final" if fin >= 0.40 else "initial" if ini >= 0.30 else "medial"
        n = tok[s]
        tab_h = (ttype[s]["TAB:B"] + ttype[s]["TAB:I"]) / n
        tab_c = ttype[s]["TAB:C"] / n
        stock = ""
        if cls in ("NAME", "COMM"):
            if tab_h >= 0.45:
                stock = "H"
            elif tab_c >= 0.30:
                stock = "MD"
        official = cls in ("AFF", "TITLE") or s in ("400", "621")
        signs.append({
            "code": s,
            "class": cls,
            "gloss": gloss,
            "picture": pic,
            "rival_gloss": rival,
            "prior_proposals": prior,
            "official": official,
            "locality": "local" if cls in ("NAME", "COMM") else "pan",
            "stock": stock,
            "evidence": {
                "discovery_tokens": n,
                "tokens_by_object_group": dict(ttype[s]),
                "positions_distinct_texts_len2plus": dict(p),
                "initial_share": round(ini, 3),
                "final_share": round(fin, 3),
                "top_preceding": prev_[s].most_common(4),
                "top_following": next_[s].most_common(4),
            },
            "band": {"frequency": fband(n), "position": pband},
        })
    by_class = collections.Counter(x["class"] for x in signs)
    out = {
        "shot": "2026-10-12-conjecture-shots/shot-b-reading",
        "version": "v1, draft before freezing predictions",
        "population": "signs with at least ten tokens in the discovery half (all object types, unknown signs excluded)",
        "classes": {
            "NUM": "numeral (stroke count); short strokes count items, tall strokes count standard units",
            "LINK": "grammatical link between an institution and its holder",
            "AFF": "great household or institution named at the opening of a legend",
            "NAME": "element of a personal name",
            "COMM": "commodity, unit, department or counted item",
            "TITLE": "office or role noun",
            "DET": "closing determinative after an office",
        },
        "attribute_rules": {
            "official": "class AFF or TITLE, or code 400 or 621",
            "locality": "local for NAME and COMM; pan for NUM, LINK, AFF, TITLE, DET",
            "stock": "NAME/COMM only: H if >=45% of discovery tokens on TAB:B or TAB:I; MD if >=30% on TAB:C",
        },
        "band_rules": {
            "frequency": "discovery tokens 10-19, 20-39, 40-99, 100+",
            "position": "over distinct intact single-line texts of length >=2: final if final share >=0.40; else initial if initial share >=0.30; else medial",
        },
        "counts_by_class": dict(by_class),
        "signs": signs,
    }
    (SHOT / "GLOSS-MAP.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    cells = collections.defaultdict(list)
    for x in signs:
        cells[(x["band"]["frequency"], x["band"]["position"])].append(f'{x["code"]}:{x["class"]}')
    print(dict(by_class))
    for k in sorted(cells):
        print(k, cells[k])
    print("official", sum(x["official"] for x in signs), "stock", collections.Counter(x["stock"] for x in signs))
    print("H", [x["code"] for x in signs if x["stock"] == "H"], "MD", [x["code"] for x in signs if x["stock"] == "MD"])


if __name__ == "__main__":
    main()
