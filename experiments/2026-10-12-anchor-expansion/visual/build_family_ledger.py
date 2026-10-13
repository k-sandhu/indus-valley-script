"""Record image-reviewed candidate families before the new context results."""
from pathlib import Path
from collections import Counter
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-12-anchor-expansion/visual'

# Membership is based on the contact sheets recorded in sheet-manifest-initial.
# These are working visual/semantic comparisons, not learned corpus clusters.
DEFINITIONS = [
 ('quantity_strokes', '001 002 003 004 005 006 007 012 013 014 015 016 017 018 019 020 025 026 027 028 029 031 032 033 034 035 036 037 039 055 056 059',
  'Separate short or long strokes occur in rows and stacked groups, without an enclosing object.',
  'Quantity or ordered-count mark; individual numerical values are left open.', 'saṃkhyā gaṇanā śreṇi', 'unconstrained',
  'Parallel rods, punctuation or rank marks could produce the same repeated strokes.'),
 ('bounded_tallies', '042 043 044 047 048 049 050 051 057',
  'A stroke group has curved side brackets, an upper cap, or short marks around its edge.',
  'Bounded count or qualified group.', 'varga gaṇa śreṇi', 'unconstrained',
  'A fence, vessel contents or added phonographic marks could explain the boundary.'),
 ('forked_stem', '061 062 063 064 065 066 069 070 071 080 081',
  'A single stem divides into angled branches or crossed prongs; W069 repeats the stem.',
  'Forked implement, branch or qualified shaft.', 'śākhā śūla daṇḍa', 'unconstrained',
  'A schematic body or arbitrary fork-shaped grapheme remains possible.'),
 ('headed_shaft', '072 073 074 075 082 083 084 085',
  'A long stem carries a loop, leaf-like head, roof or arched boundary around its upper part.',
  'Headed staff or emblem-bearing shaft.', 'daṇḍa dhvaja', 'unconstrained',
  'A plant stem or schematic person could supply the same outline.'),
 ('human_agent', '090 093 094 095 096 097 098 099 100 104 105 106 107',
  'A central upright has lateral arms and two lower legs. Several forms add head or hand features.',
  'Person, named agent or worker category.', 'puruṣa nara karmakara', 'nonfinal_entity',
  'An authority emblem or a conventional marker could use the human outline.'),
 ('paired_agents', '091',
  'Two complete legged figures stand side by side and join at shoulder level.',
  'Paired workers or a two-person service group.', 'yuga gaṇa puruṣa', 'counted_entity',
  'A duplicated person sign or paired authority emblem remains possible.'),
 ('enclosed_human', '101 102 103 141',
  'A legged human-like figure stands between curved side boundaries.',
  'Person or worker attached to a bounded group or place.', 'puruṣa koṣṭha', 'nonfinal_entity',
  'The side curves may mark a graphic variant or carried objects rather than a place.'),
 ('object_handling_person', '110 111 112 113 117 118 119 137 138 139 147',
  'A human-like stem is attached to U-shaped supports, rounded objects, a diamond or foot-level pendants.',
  'Equipment or goods handler; the held object is not assigned one material.', 'bhārin karmakara', 'nonfinal_entity',
  'Shield, weapon, weight apparatus and posture variants remain distinct object possibilities.'),
 ('animal_or_hide_bearer', '115 116 121',
  'A legged figure touches an irregular curved side form, which has animal-like or hanging-strip features.',
  'Animal-product handler, herder or hide worker.', 'gopāla carman', 'nonfinal_entity',
  'The curved form may be a vessel, tool or draped equipment rather than an animal or hide.'),
 ('fish_bearer', '122',
  'A legged central figure is connected to a side oval with a forked end.',
  'Fish or aquatic-product handler.', 'matsya', 'nonfinal_entity',
  'A bow, looped implement or graphic appendage could resemble the side fish-like form.'),
 ('bow_bearer', '125 126 127 146',
  'A person-like stem stands beside one or two curved bows attached near the arms.',
  'Bow bearer, archer or bow-making service.', 'dhanvin dhanus', 'nonfinal_entity',
  'Large vessels, paired shields or loops are visual alternatives to bows.'),
 ('paired_work_party', '123',
  'Two legged figures support a shared horizontal bar with a central hanging divided object.',
  'Paired carrier service or jointly handled load.', 'yuga vivadha bhārin', 'closing',
  'Balance apparatus, a shared ceremonial object or two independent figures remain alternatives.'),
 ('creature_bearer', '128 129',
  'A legged central figure has one or two angular, head-like objects at raised arms.',
  'Creature handler or qualified worker.', 'paśu pāla', 'nonfinal_entity',
  'The angular objects may be tools, birds, masks or conventional hand marks.'),
 ('toothed_tool_bearer', '130 131 132 133 134 135 136',
  'A legged figure has a transverse toothed or forked extension at one or both arms; W136 has shorter side hooks.',
  'Toothed-implement worker, with harrow or cultivation service as a leading comparison.', 'matya kaṅkata kṛṣaka', 'counted_entity',
  'Comb, rake, branching crop, insignia and body variants remain possible.'),
 ('crossed_body_equipment', '140 148 150',
  'A legged form has crossed loops or a rectangular transverse feature across its upper body.',
  'Person equipped with crossed straps or a load frame.', 'bandha yuga bhārin', 'unconstrained',
  'Folded arms, posture variants or a geometric symbol could explain the crossing.'),
 ('staff_bearer', '142 143 144 145',
  'A central legged figure holds one or two long vertical staffs. Short outer marks or an added stroke group qualify two variants.',
  'Staff-bearing person, responsible agent or named office.', 'daṇḍin adhikārin', 'nonfinal_entity',
  'Guard, equipment handler, rank emblem and qualified person remain possibilities.'),
 ('carrier_yoke', '151 152 153 154 155 156 157 158 159 160 161 172',
  'A crossbar or shoulder-level support carries two suspended loops or angled loads. Most forms retain a central legged figure; W172 retains a frame and two loops.',
  'Load-carrier, sling-load or transport-service category.', 'vivadha śikya śikyapāśa yuga bhārin', 'closing',
  'A balance, frame-supported objects or a qualified person is possible. Hook, head and internal-stroke variants do not receive separate lexical values.'),
 ('looped_cover', '165 166 167 168',
  'A curved upper arch surrounds one or two short inner strokes or returned lower loops.',
  'Sling, looped support or suspended covering.', 'śikya pāśa', 'unconstrained',
  'Arch, hoof, vessel rim or two curved strokes remain equally plausible.'),
 ('paired_suspended_ovals', '169 170 171 173',
  'Two upright ovals share a central join or stem, or attach to two upright supports; outer sloping strokes occur in W170.',
  'Paired hanging units or linked loads.', 'śikya yuga dvaya', 'unconstrained',
  'Paired leaves, fruit, eyes or an abstract two-unit marker are visual rivals.'),
 ('multi_appendage_creature', '190 191 192 193 194 195 204 205 206 207 208 209 272',
  'An oval or segmented center has several lateral and lower appendages. W272 has two rounded lateral extensions, a segmented body and forked lower features.',
  'Multi-limbed creature or animal-product category; precise species is open.', 'krimi vṛścika paśu', 'counted_entity',
  'Bird, insect, scorpion, crustacean, plant bundle and composite emblem remain rivals. W204 also retains the earlier SENA source-coder disagreement.'),
 ('loop_chain', '200 201 202 203 215 216 217',
  'Two or three upright loops are stacked and joined; some add a side staff, division or flanking bars.',
  'Linked units, looped binding or a grouped series.', 'pāśa bandha śreṇi', 'internal_connector',
  'Paired eyes, body segments, bead counts or a commodity outline could produce the loops.'),
 ('fish_shapes', '219 220 221 222 223 224 225 226 227 228 229 230 231 232 233 234 235 236 237 240 241 242 243 244 250 251 252 253 255 256 257',
  'An upright oval or narrow body ends in a forked lower tail. Side bars, fins, interior strokes, roof marks and repeated bodies vary across the family.',
  'Fish or aquatic-product category, with body qualifications left open.', 'matsya', 'counted_entity',
  'Leaf, seed pod, schematic body and abstract oval-with-fork signs are alternatives. W244 and W255–257 have especially elaborate appendages.'),
 ('bird_shapes', '260 261 262 263 264 265 266 267 268 269 270 271 276 277 278 279 280 281',
  'A bent or upright creature has a projecting neck/head, hatched body and lower legs or tail. Some repeat it or add side boundaries.',
  'Bird or bird-product category.', 'pakṣin śakuni', 'counted_entity',
  'Other animals, hooked implements, cloth strips and conventional angular bodies remain possible for the more schematic forms.'),
 ('rooted_oval', '285 286 287',
  'An oval or narrow center carries an upper fork and lower root-like strokes.',
  'Rooted crop, sprout or plant-product category.', 'aṅkura bīja', 'counted_entity',
  'Fish, schematic person and tied-object outlines share these components.'),
 ('bent_parallel_rows', '289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308',
  'Two to four parallel strips bend at the same angle and divide into lower strokes; W307/W308 add a rounded upper end.',
  'Ordered bundle or row of bent units.', 'śreṇi varga stamba', 'unconstrained',
  'Animal legs, folded rods, teeth, chevrons and phonographic stroke variants remain possible.'),
 ('many_legged_outline', '309 310 311',
  'A looped or hatched upper body ends in several spreading lower strokes.',
  'Grouped workers, many-legged creature or bundled material.', 'gaṇa paśu stamba', 'unconstrained',
  'The upper loop and lower strokes do not identify whether the figure is animate.'),
 ('compartmented_frame', '315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 335',
  'Two outer uprights support horizontal bars and, in many forms, short repeated vertical dividers.',
  'Rack, partitioned storage frame or bounded holding category.', 'koṣṭha kośa śreṇi', 'closing',
  'Ladder, fence, loom, seat and abstract tally panel remain graphic rivals.'),
 ('forked_leaf_vessel', '336 337 338',
  'A lower bounded row of upright strokes supports two pointed or curved upper lobes.',
  'Contained stalks or sprouting plant bundle.', 'stamba śūka', 'counted_entity',
  'Horns on an enclosure, toothed equipment or a geometric compound remain alternatives.'),
 ('horned_animal', '340 341 342 343 344 345 346 347 348 953 957',
  'A horizontal divided or hatched body has multiple lower legs, a neck/head at one end and an upturned tail-like end. W953/W957 are more abbreviated side forms.',
  'Animal or herd-product category; domestic stock is a leading comparison.', 'paśu go', 'counted_entity',
  'Rack plus attached emblem, mixed creature and tool compounds remain possible. No species is assigned to every variant.'),
 ('dangling_loop', '350 351 352',
  'A lower closed loop joins upper stems or crossed forked arms.',
  'Looped sling, tied load or suspended unit.', 'śikya pāśa bandha', 'unconstrained',
  'Seed bulb, head-down creature and arbitrary looped grapheme are alternatives.'),
 ('rail_tally', '353 354',
  'Several upright rods cross a horizontal rail, with one or two rods continuing below it.',
  'Joined row or bundled units.', 'śreṇi stamba', 'unconstrained',
  'Comb, rake, forked staff and crossed strokes remain alternatives.'),
 ('gate_frame', '360 361 362 363 440 441 442 443 444',
  'An upper bar joins two descending posts. Some add another bar, enclosing roof, slanted sides or inner marks.',
  'Gateway, doorway or bounded access category.', 'dvāra koṣṭha', 'closing',
  'Seat, stand, vessel outline and simple geometric frame remain possible.'),
 ('flag_panel', '058 525 526 527 950',
  'A vertical staff supports a side rectangular panel, with inner divisions or exposed teeth in several forms.',
  'Raised panel, divided holding or qualified category marker.', 'koṣṭha kośa kaṅkata', 'closing',
  'Flag, comb, rack and small field diagram remain competitors. W527 supplies the already reviewed divided-panel comparison.'),
 ('circled_stem', '370 371 372 373 374 375 376 946',
  'A small closed oval, diamond or loop sits on an upright stem; some add prongs, side rails or a second crossed loop.',
  'Seed-bearing stem, staff emblem or marked unit.', 'bīja aṅkura daṇḍa', 'unconstrained',
  'Ring-headed equipment and body outlines are equally plausible. W373 preserves the earlier SENA mapping disagreement.'),
 ('leaf_cluster', '380 381 382 384 385 386 387 388',
  'Pointed or lobed closed outlines carry a stem, repeated inner branches or adjacent duplicates.',
  'Leaf, foliage or plant-product category.', 'parṇa pallava', 'counted_entity',
  'Heart-shaped vessel, fan, feather and lattice object remain possible.'),
 ('plant_branch', '389 390 391 392 393 394 411 412 413 956',
  'A central trunk carries a top fork or repeated side branches; W389 repeats the trunk and W412 adds side rails.',
  'Plant, crop or branching product category.', 'śākhā stamba śūka', 'counted_entity',
  'Rake, tree emblem, branched staff and stroke-count designs remain alternatives.'),
 ('toothed_closer', '400 401 402',
  'A vertical spine carries repeated transverse teeth; W401 doubles the spine and W402 faces the opposite way.',
  'Closing group or category marker with comb/rake as the pictorial comparison.', 'kaṅkata gaṇa varga', 'closing',
  'Tool, tallied row, rack or multiple rods may explain the teeth. Group/class remains a functional hypothesis.'),
 ('toothed_implements', '045 046 404 405 406 407 408 409 410 415 416 417 418',
  'A stem or rail supports several short teeth or prongs. Some have two tiers, a second stem or an angled head.',
  'Toothed or forked implement, possibly rake, harrow or comb.', 'matya kaṅkata', 'counted_entity',
  'Plant branches, bundled rods and count marks remain alternatives to equipment.'),
 ('bound_stalks', '420 421 422 423 424 425 426 427 428 429 430',
  'Three or four upright stems share a basal rectangle or horizontal band. Upper forks, side branches and lower hatching vary.',
  'Bound stalks, contained grain or a reed bundle.', 'stamba śūka kāṇḍa', 'counted_entity',
  'Fence, rack, row of people or qualified vessel is possible. Later sheaf terminology is not imported into every variant.'),
 ('wave_zigzag', '450 451 452 453 927 928',
  'One or two continuous lines repeatedly bend or undulate.',
  'Flowing water, channel or wavy material category.', 'udaka nadī', 'nonfinal_entity',
  'Cord, folded cloth, teeth and arbitrary zigzag writing signs remain alternatives.'),
 ('repeated_triangles', '455 456 457 458 460 461 462 463',
  'Several triangles or triangular lobes share a side or horizontal rail; some carry a cap, branch or leaf-like feature.',
  'Repeated pointed units, grouped portions or a serrated row.', 'śreṇi varga śūka', 'unconstrained',
  'Mountains, teeth, leaves, paired emblems and geometric duplication remain possible.'),
 ('angular_support', '465 466 467 468 469 470 471 472 473 474 475',
  'Two sloping uprights form an A-like support, with an inner crossbar, lower stroke marks or attached forked foot.',
  'Angled support or qualified load/cultivation frame.', 'yuga lāṅgala matya', 'counted_entity',
  'Shelter, plough-frame, balance stand and a geometric qualifier remain competitors.'),
 ('peaked_band', '479 480 481 482 483 484',
  'One or two diagonal strips meet at a peak; some add internal cells or short lower marks.',
  'Peaked cover, folded band or roof category.', 'śālā bandha', 'unconstrained',
  'Arrowhead, leaf lobe and two joined strokes remain possible.'),
 ('triangular_leaf', '490 491 492 493 494 495',
  'A pointed curved wedge has zero, one or several interior transverse bars.',
  'Leaf, wedge-shaped portion or qualified blade.', 'parṇa śūka', 'counted_entity',
  'Tool blade, container side and geometric triangle remain alternatives.'),
 ('divided_triangle', '500 501 502 503 504 505 506',
  'A closed triangle carries a central upright, inner cells or repeated horizontal divisions; several add a top cap.',
  'Divided heap, bounded portion or triangular storage category.', 'koṣṭha māna', 'counted_entity',
  'Roof, leaf, tool head and abstract divided triangle remain alternatives.'),
 ('handled_rectangle', '510 511 512 513 514 590 591 592 593 595 596 597',
  'A rectangle carries an upper or lower stem; inner bars, cells, a small symbol and repeated objects qualify it.',
  'Handled container, framed measure or storage unit.', 'kośa koṣṭha māna', 'counted_entity',
  'Standard, loom weight, instrument and staff-mounted panel are alternatives.'),
 ('binding_bowtie', '530 531 532 533 534 535 540 541 542 543 544 545 546 547 550 551 552 554 555 556 560 561 562 563 564 565',
  'Two diagonals meet at a crossing, usually closing one or both sides as triangles; loops, inner bars and prongs qualify the ends.',
  'Binding, paired joining or relationship marker.', 'bandha pāśa yuga', 'internal_connector',
  'Paired portions, fish-like outlines, bows and an autonomous geometric grapheme remain possible.'),
 ('gateway_compound', '570 571 572 573 575 576 577 578 579 585 586',
  'Two posts and a roof enclose open space or an arrow-like mark. Some add upper branches, a block, a divided beam or paired frames.',
  'Qualified doorway, covered holding or store-access category.', 'dvāra śālā koṣṭha', 'closing',
  'Vessel, equipment stand, capped count and graphic enclosure remain competitors.'),
 ('arrow_shaft', '515 516 517 518 519 520 521',
  'A pointed head or upper angle sits over a long shaft; a loop, leaf, lower angle or side arms may be added.',
  'Arrow, pointed implement or directional/authority shaft.', 'iṣu śara daṇḍa', 'nonfinal_entity',
  'Plant stem, roof mark and spear-like equipment remain possible.'),
 ('plain_divided_enclosure', '599 600 601 602 603 604 605 620 621 622 623 625 626 627 628',
  'A closed rectangle is plain, repeated or divided into sections, sometimes with a hook, staff or inner marks.',
  'Bounded holding, compartment or allotment unit.', 'koṣṭha kośa māna', 'counted_entity',
  'Field, container, building plan and arbitrary geometric token remain competitors.'),
 ('toothed_border_box', '606 629 630 631 632 633 634 635 636 637 638 639 640 641 642 643',
  'A rectangular border carries short inward or outward teeth, with some internal strokes, waves or a small crossed symbol.',
  'Bounded and qualified store, rack or allocation category.', 'koṣṭha kośa kaṅkata', 'closing',
  'Loom, frame, perforated object and conventional border modification remain possible.'),
 ('grid_compartments', '615 616 617',
  'A rectangle is divided by several horizontal and vertical bars; W617 has two adjacent gridded rectangles.',
  'Compartmented storage, lattice or grouped measured units.', 'koṣṭha kośa māna', 'closing',
  'Textile, game board, rack or geometric grid remains possible. W617 may be two tokens rather than one code; cell count is not assigned.'),
 ('crossbar_units', '528 610 611',
  'A central upright and transverse bar form a stepped cross or support one or two bounded end cells.',
  'Joined support, divided beam or unit relationship.', 'yuga śreṇi', 'unconstrained',
  'Balance, staff, structural frame and geometric crossing remain possible.'),
 ('cross_junction', '645 646 647 678 679 680 681 682 683 684 685 686 687 688 689 690 692 693 694',
  'Crossing diagonal strokes form an X or radiating joint. Caps, roofs, side loops, outer bands and short edge marks qualify it.',
  'Joining, binding or associated-unit marker.', 'bandha pāśa yuga', 'internal_connector',
  'Body outline, tied bundle, star, independent commodity and graphic qualifier remain possibilities.'),
 ('cup_vessels', '697 698 699 700 701 702 703 704 705 706 711 712 713 714 715 716 717 718 719 720 721 722 725 727 728 729 731',
  'An open U-shaped or cup-like boundary has a rounded or angled base. Interior strokes, bars, loops, a roof, handles or duplicate cups qualify it.',
  'Vessel, contained material or bounded portion category.', 'kumbha droṇa kośa', 'counted_entity',
  'Open enclosure, suspension loop, grain bundle and geometric U remain rivals. No capacity value is inferred.'),
 ('sprouting_vessel', '707 708 709 710 723',
  'A U-shaped boundary contains a central stem, fork, leaf or diamond-like lower plant form.',
  'Plant-bearing vessel, sprout or contained crop.', 'aṅkura stamba kumbha', 'counted_entity',
  'Contained tool, liquid drop and qualified enclosure remain possible.'),
 ('rooted_cup', '732 733 734 735 736',
  'An open cup-like upper outline ends in several spreading lower strokes, with optional inner stem or loop.',
  'Rooted plant bundle or legged/grounded container.', 'stamba aṅkura', 'counted_entity',
  'Vessel feet, suspended cords and graphic qualifiers remain alternatives to roots.'),
 ('rim_marked_vessel', '740 741 742 743 744 745 746 747 748 749 750 751 752 753',
  'A U-shaped boundary has teeth or short projecting marks at its upper ends, plus optional inner quantity strokes or circular division.',
  'Qualified container or closing account category.', 'kumbha kośa varga', 'closing',
  'Handled vessel, bent toothed equipment, enclosure and phonographic rim modification remain possible.'),
 ('terminal_qualified_vessel', '759 760 761 762 763 764 765 766 767 768 770 772 773 775 776 777 778 780 781 782 783 784 785 786',
  'A U-shaped or lobed boundary carries forked, leaf-like, looped or toothed upper terminals; inner crosses, loops and repeated stems vary.',
  'Compound container or account category with plant, tool or grouped-unit qualifications.', 'kumbha stamba śūka kaṅkata', 'closing',
  'Plant bundle, hanging framework, handled vessel and independent joined glyphs remain possible. Distinct terminal shapes are not assigned one shared plant species.'),
 ('plain_oval_units', '790 791 792 795 796',
  'One or two closed ovals are plain or have a dot, short rim marks or an outer cap.',
  'Round unit, contained item or allotment token.', 'māna varga', 'counted_entity',
  'Seed, eye, bead, vessel mouth and abstract oval remain equally possible.'),
 ('enclosed_emblem', '803 804 805 806 807 808 809 810 811 812 813 814 815 816 817 826 827 828 829 830 831 832 833 834 835 836 837 838 839',
  'A closed oval contains a stem, geometric shape, grid, rod, repeated strokes or a lower division; some add small outer marks.',
  'Bounded entity or unit with an internal qualifier.', 'kośa koṣṭha māna', 'counted_entity',
  'Seed, seal emblem, body part and a unified grapheme remain alternatives. The internal sign is not automatically read as a separate word.'),
 ('wheel_spokes', '818 820 821 822 823 824 945',
  'A closed oval has crossbars, radial divisions or several wedge-like sectors; W821 repeats it and other forms add flanking marks.',
  'Wheel, rotating equipment or divided transport unit.', 'cakra yāna', 'counted_entity',
  'Divided round measure, lattice, sun emblem and graphic class mark remain possible.'),
 ('woven_mesh', '383 825',
  'Repeated diagonal lines form visible closed cells in a pointed double strip or closed oval.',
  'Woven, netted or lattice material category.', 'jāla tantu', 'counted_entity',
  'Leaf venation, perforated tool and geometric hatching remain possible.'),
 ('paired_oval_join', '794 797 798 799 801 840 841 842 843 844 845',
  'Two ovals intersect, flank an open crossing or attach to angled strokes; several forms add edge bars or interior divisions.',
  'Paired-unit joining, linkage or combined holdings.', 'yuga bandha dvaya', 'internal_connector',
  'Paired eyes, joined vessels, body parts and independent looped graphemes remain alternatives.'),
 ('diamond_enclosure', '849 850 851 852 853 854 855 856 857 858 859 860 861 862 863 864 865 866 868 869 870 871 872 874 875 876 877 878 879 880',
  'A diamond-shaped boundary is plain or contains a smaller shape, staff, grid, wheel, stroke group or end qualification.',
  'Bounded allotment, parcel or qualified compartment.', 'koṣṭha kośa māna', 'counted_entity',
  'Field, eye, body, seed, shield and abstract geometric token remain rivals. A shared diamond border does not determine the inner qualifier.'),
 ('bow_or_curved_blade', '890 891 892 893 894 895 896 897 898',
  'A curved side joins a straight or divided chord; some add a diagonal, short rim marks or a pointed end.',
  'Bow, curved blade or half-round unit.', 'dhanus parṇa', 'counted_entity',
  'Half vessel, leaf, shield and schematic curved strip remain alternatives.'),
 ('curved_rows', '908 909 911 914 918 919',
  'Several matching arcs repeat side by side or one above another; some arcs carry small enclosed loops.',
  'Ordered row, repeated curved units or layered material.', 'śreṇi varga', 'unconstrained',
  'Waves, teeth, strings, vessel rims and ornamental duplication remain possible.'),
 ('arch_canopy', '930 931 932 933',
  'An arched or peaked upper boundary covers a divided interior, stroke group, arrow-like feature or upright prongs.',
  'Covered store, shelter or bounded institutional category.', 'śālā koṣṭha dvāra', 'closing',
  'Fan, vessel, plant bundle and composite emblem remain possible.'),
 ('enclosed_fish_group', '940 942 943',
  'Two fish-like oval-and-tail forms stand between curved side boundaries, with an interior cross or loop in some versions.',
  'Paired fish or bounded aquatic-product group.', 'matsya varga', 'counted_entity',
  'Paired people, curved enclosures and joined whole glyphs remain alternatives.'),
 ('mixed_compound', '944 947 951 952',
  'One graphic joins a fish-like figure and post frame; others combine curved forms, a legged rectangle or an enclosed bird outline.',
  'Compound record category with a contained or joined entity; the entity varies by code.', 'koṣṭha paśu pakṣin', 'unconstrained',
  'Each may be a single emblem or a differently segmented sequence. This family records composition, not one material meaning.'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    prior = json.loads((HERE.parent / 'candidate-starting-pool.json').read_text(encoding='utf-8'))['rows']
    by_code = {row['code']: row for row in prior}
    sheets = json.loads((HERE / 'sheet-manifest-initial.json').read_text(encoding='utf-8'))['rows']
    code_sheet = {code: sheet['path'] for sheet in sheets for code in sheet['codes']}
    rows = []
    assignments = {}
    for family_id, code_string, observation, meaning, words, role, rivals in DEFINITIONS:
        codes = code_string.split()
        missing = [code for code in codes if code not in by_code]
        if missing:
            raise ValueError((family_id, 'Missing inventory codes', missing))
        for code in codes:
            if code in assignments:
                raise ValueError((code, assignments[code], family_id))
            assignments[code] = family_id
        drawings = sorted({drawing['path'] for code in codes for drawing in by_code[code]['drawings']})
        rows.append({'family_id': family_id, 'codes': codes,
                     'picture_observation': observation, 'working_meaning': meaning,
                     'Sanskrit_comparison_words': words.split(), 'role_predictions': [role],
                     'graphic_rivals': [rivals], 'source_drawing_paths': drawings,
                     'visual_support': 'private-font-only',
                     'seen_images': sorted({code_sheet[code] for code in codes}),
                     'confidence_reason': 'All listed exact-code font witnesses were seen. The shared component supports a working family; the material meaning and role require the separately declared inscription tests.',
                     'prior_layer': {code: by_code[code]['tier_before'] for code in codes},
                     'code_source_support': {code: {'exact_witness': code_sheet[code],
                         'class_images': by_code[code]['drawings'],
                         'class_identity_limit': 'Chart class correspondence does not establish exact Wells variant strokes.'}
                         for code in codes}})
    uncovered = sorted(set(by_code) - set(assignments), key=int)
    data = {'date': '2026-10-12', 'construction': 'Visible-component review fixed before new complete-context outputs were read. Prior project outcomes were already known; this is not a blinded semantic study.',
            'scope': 'One primary family per assigned code. Sanskrit words are comparison hints pending exact sense selection by the separate Sanskrit reviewer. The private font is a drawing witness, not an artifact photograph.',
            'counts': {'families': len(rows), 'assigned_codes': len(assignments), 'uncovered_codes': len(uncovered),
                       'new_unreviewed_codes': sum(by_code[code]['tier_before'] == 'unreviewed' for code in assignments),
                       'assigned_prior_layers': dict(Counter(by_code[code]['tier_before'] for code in assignments))},
            'rows': rows, 'uncovered_codes': uncovered}
    write(RAW / 'families-draft-before-chart-check.json', data)

    representatives = []
    for row in rows:
        candidates = [code for code in row['codes'] if by_code[code]['drawings']]
        # Select the already discussed central example when possible; otherwise
        # the first declared code with a licensed chart pointer. No corpus support
        # or new context result enters this selection.
        preferred = {'carrier_yoke': '151', 'toothed_tool_bearer': '130',
                     'multi_appendage_creature': '272', 'fish_shapes': '220',
                     'horned_animal': '345', 'compartmented_frame': '319',
                     'flag_panel': '527', 'plant_branch': '411',
                     'toothed_closer': '400', 'plain_divided_enclosure': '600',
                     'wheel_spokes': '818', 'woven_mesh': '825', 'arch_canopy': '930'}
        code = preferred.get(row['family_id'])
        if code not in candidates:
            code = candidates[0] if candidates else None
        if code:
            drawing = by_code[code]['drawings'][0]
            source = ROOT / drawing['path']
            representatives.append({'family_id': row['family_id'], 'code': code,
                                    'source': drawing['path'], 'source_sha256': sha(source),
                                    'graphic_class': drawing['graphic_class']})
    labels = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 17)
    contacts = []
    for offset in range(0, len(representatives), 36):
        batch = representatives[offset:offset + 36]
        image = Image.new('RGB', (1500, 1080), 'white')
        draw = ImageDraw.Draw(image)
        for index, rep in enumerate(batch):
            x, y = (index % 6) * 250, (index // 6) * 180
            original = Image.open(ROOT / rep['source'])
            original.thumbnail((246, 139))
            image.paste(original, (x + 2, y + 39))
            draw.text((x + 5, y + 2), f"W{rep['code']} / {rep['graphic_class']}", font=labels, fill='black')
            draw.text((x + 5, y + 19), rep['family_id'][:25], font=labels, fill='black')
            draw.rectangle((x, y, x + 249, y + 179), outline='#aaaaaa')
        target = RAW / f'licensed-class-sheet-{offset // 36 + 1:02d}.png'
        if target.exists():
            raise FileExistsError(target)
        image.save(target)
        contacts.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target),
                         'representatives': batch, 'seen': False,
                         'license': 'CC BY 4.0',
                         'attribution': 'Koskenniemi and Parpola, Corpus of Texts in the Indus Script (1979), University of Helsinki edition; original project atlas cells.',
                         'transformation': 'Whole atlas cells resized into a labelled contact sheet; no stroke editing.'})
    write(HERE / 'licensed-sheet-manifest-initial.json', {'rows': contacts})
    print(json.dumps(data['counts']))


if __name__ == '__main__':
    main()
