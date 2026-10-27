"""Materialize the documented, provisional source judgments; never score a reading."""
from collections import Counter
import json
import re

from prepare import ROOT, OUT, PKG, read, rows, save, sha, entry_id
from supplement import tl_witness

REVIEWER = {"model": "GPT-6; exact backend identifier not exposed", "harness": "Codex desktop",
            "role": "AI source reviewer", "qualifications": "No specialist Tamil or Dravidianist credentials",
            "status": "provisional_source_review", "date": "2026-10-22"}

# Each selection is (transliteration, dictionary page, homograph, role, sense).
SENSES = {
 "aṇil": ("supported", [("aṇil",63,"","picture","squirrel")], "The dictionary supports the animal name. The Indus picture identification remains a proposed identification."),
 "aṟu": ("supported_scoped_combining_form", [("aṟu-mīṉ",181,"","compound_evidence","Pleiades; etymology explicitly cites āṟu³"),("āṟu",259,"³","numeral_lemma","six")], "The compound entry supplies the numeral relationship. No exact one-member aṟu row is available; aṟṟu has comparison and increment senses and is excluded."),
 "eḻu": ("supported_scoped_combining_form", [("eḻu-mīṉ",544,"","compound_evidence","seven stars of Ursa Major; etymology explicitly cites ēḻu"),("ēḻu",568,"","numeral_lemma","seven")], "The exact eḻu² entry means a pillar or crossbar. The compound directly supplies the numeral relationship."),
 "iraṇṭu": ("supported", [("iraṇṭu",309,"","numeral","sense 1: two")], "Select the numeral sense; retain the other senses in the source record."),
 "iru": ("supported_scoped_combining_form", [("iru-kaṇ",326,"","compound_evidence","two eyes; etymology explicitly cites iraṇṭu"),("iraṇṭu",309,"","numeral_lemma","two")], "The exact iru² entry means great or black. The dictionary's iru-kaṇ entry supplies direct evidence for numeral iru in compounds; the proposal reconstructs a Proto-Dravidian numeral stem."),
 "katir": ("supported", [("katir",712,"¹","picture","sense 6: spindle"),("katir",712,"¹","proposed_rebus","senses 1–2: ray and light")], "The source proposes the spindle-to-radiance connection. The unrelated supplementary homograph is excluded."),
 "kaṇ": ("supported", [("kaṇ",683,"","picture","sense 1: eye")], "The proposal derives an overseer through a doubled-eye construction and a related seeing verb; overseer is not the selected simple eye sense."),
 "kā": ("supported_multiple_senses", [("kā",840,"⁴","picture","sense 1: carrying pole"),("kā",840,"³","proposed_rebus","sense 1: protection")], "The pole and protection senses have different homograph records. The first exact record is a letter and is excluded."),
 "kāvaṭi": ("supported_with_attestation_limit", [("kāvaṭi",900,"","picture","sense 1: carrying pole; sense 2: decorated offering pole")], "Parpola 1997 p.175 discusses this form, states its absence from Old Tamil literature and reports a 1628 chronicle for the cult. Those are claims in the proposal; their cited primary sources have not been checked."),
 "kāvu": ("supported_verb_citation_form", [("kāvu-",903,"¹","picture_action","sense 1: carry on the shoulder with a pole")], "The exact nominal kāvu³ means sacrifice or ointment. The source's carrying root is supported by kāvu-¹. Parpola also reports a carrying-yoke noun on p.175; that noun has no exact selected Tamil Lexicon record here."),
 "kōḷ": ("supported_action_not_animal_name", [("koḷ-",1162,"¹","picture_action","sense 1: seize, grasp"),("kōḷ",1202,"¹","proposed_rebus","sense 1: taking or seizing; sense 15: planet")], "The proposal names the crab by its grasping action. It does not present kōḷ as a dictionary noun meaning crab."),
 "muruku": ("supported_multiple_senses", [("muruku",3279,"³","picture","ear helix ornament"),("muruku",3279,"¹","proposed_rebus","sense 1: youth; sense 2: Skanda")], "Ring ornament and youth or deity require separate homograph records. The coral-tree form murukku in Winslow has a doubled consonant."),
 "mīṉ": ("supported_multiple_senses", [("mīṉ",3214,"²","picture","sense 1: fish"),("mīṉ",3214,"¹","proposed_rebus","sense 1: star")], "Fish and star are separate homographs with different printed etymologies. Their historical relationship requires linguistic review."),
 "nīr": ("supported", [("nīr",2299,"¹","picture","sense 1: water")], "The irrigation-worker interpretation uses a larger compound in the proposal. The second-person pronoun homograph is excluded."),
 "oru": ("supported", [("oru",597,"²","numeral","one, used before consonants")], "The sheep and plant homographs are excluded."),
 "oṉṟu": ("supported", [("oṉṟu",615,"²","numeral","sense 1: one")], "The numeric sense is explicit."),
 "piḷḷai": ("partly_supported", [("piḷḷai",2712,"","proposed_rebus","senses 1–3: child, son, young; animal-young and suffix uses also listed"),("aṇiṟ-piḷḷai",63,"","picture_compound","squirrel; compound of aṇil")], "The dictionary supports child and animal-young senses and the squirrel compound. A standalone Tamil squirrel sense claimed in the proposal has not been independently verified in these entries."),
 "tāḷ": ("supported_with_celestial_uncertainty", [("tāḷ",1855,"¹","picture","sense 1: leg, foot"),("tāḷ",1855,"¹","proposed_rebus","sense 11: comet, with a Purananuru citation")], "Parpola 2009 discusses whether the old celestial reference is a comet or constellation. The dictionary's English label does not resolve that textual question."),
 "tōḷ": ("wrong_language_for_cited_sense", [("tōḷ",2115,"³","different_tamil_sense","sense 1: shoulder; sense 2: arm")], "Parpola 2009 p.63 attributes the animal hind-thigh form tōḷ to Toda and the leg or foot form tāḷ to Tamil. Remove tōḷ from the Tamil alternatives for this cited picture sense; retain its Toda provenance."),
 "vaṭam": ("supported_with_distinct_target_form", [("vaṭam",3474,"¹","picture","sense 8: banyan"),("vaṭakku",3472,"","target_context","north")], "The proposal relates a fig or banyan-star construction to the north star. The separate word vaṭakku does not authorize a universal spelling alias with vaṭam."),
 "veḷ": ("supported_with_distinct_forms", [("veḷ",3790,"¹","attribute","sense 1: white; sense 4: bright"),("vēḷ",3842,"²","proposed_rebus_context","sense 2: desire; sense 4: Skanda"),("veḷi",3806,"¹","picture_context","sense 2: open space; sense 4: intervening space")], "Parpola 2010 uses three distinct forms for the open-space picture, whiteness and deity or desire. Preserve vowel length and the final vowel; no universal alias is accepted."),
 "ā": ("supported", [("ā",201,"⁸","picture","sense 2: female cattle; sense 3: bull")], "The selected cattle homograph is distinct from the initial letter entry. The proposal's reconstructed grammatical rebus remains a linguistic hypothesis."),
 "āvu": ("wrong_language_for_cited_sense", [("āvu",252,"¹","different_tamil_sense","crab's-eye plant")], "Parpola 1997 p.171 lists āvu under Kannada and Telugu. His Tamil and Malayalam forms are ā and āṉ. Remove āvu from the Tamil alternatives for the cited cattle identification."),
 "āṉ": ("supported_multiple_senses", [("āṉ",260,"¹","picture","sense 1: female cattle; sense 2: ox"),("āṉ",260,"³","grammatical_comparison","sense 2: third-person singular masculine ending")], "Cattle and grammatical ending require separate records. Their reconstructed historical connection is not established by this source audit.")
}

# PDF page numbers are one-based; printed pages are supplied separately.
PROPOSAL_PAGES = {
 "aṇil": [(2010,25,26)], "aṟu": [(2005,27,54),(1997,11,177)],
 "eḻu": [(2005,27,54)], "iraṇṭu": [(1997,5,171)], "iru": [(1997,5,171)],
 "katir": [(2010,20,21),(2010,21,22)], "kaṇ": [(2005,33,60)],
 "kā": [(1997,7,173)], "kāvaṭi": [(1997,9,175),(1997,10,176)],
 "kāvu": [(1997,7,173),(1997,9,175)], "kōḷ": [(2005,30,57)],
 "muruku": [(2010,22,23)], "mīṉ": [(2005,25,52)], "nīr": [(2005,34,61)],
 "oru": [(1997,5,171)], "oṉṟu": [(1997,5,171)], "piḷḷai": [(2010,25,26)],
 "tāḷ": [(2009,27,63)], "tōḷ": [(2009,27,63)], "vaṭam": [(2005,28,55),(2005,29,56)],
 "veḷ": [(2010,26,27)], "ā": [(1997,5,171)], "āvu": [(1997,5,171)], "āṉ": [(1997,5,171)]
}

# Decisions concern source-supported segmentation, with lexical eligibility separate.
# Abbreviations are expanded in the output; no scores are inferred from dictionary absence.
COMPOUNDS = {
 "W01": ("supported_split",["cā","vintu"],"explicit_etymology","The entry explicitly names both members; the original carries a Sanskrit-origin mark."),
 "W02": ("undecidable",["ava","ciyai"],"member_form_conflict","The etymology prints ciyai, while the parser returns ciyam. The Tamil Lexicon gives a Sanskrit source; the second-member identity requires linguistic adjudication."),
 "W03": ("supported_split",["cu","piṭcam"],"explicit_etymology","Both members are printed in the etymology."),
 "W04": ("supported_split",["ku","mati"],"explicit_etymology","The printed etymology and Tamil Lexicon agree on the members."),
 "W05": ("supported_split",["payam","karam"],"explicit_etymology_with_junction","The printed payam plus karam supports the surface payaṅ junction; both dictionaries identify a Sanskrit derivation."),
 "W06": ("supported_split",["cit","ākācam"],"explicit_etymology","Both members are explicit in the source and Tamil Lexicon."),
 "W07": ("supported_split",["a","pāl"],"explicit_etymology_with_junction","The source prints a plus pāl; the parser retains the junction consonant in ppāl. This is a grammatical construction, not an eligible pair of picture nouns."),
 "W08": ("undecidable",["a","vai"],"sense_etymology_conflict","Winslow places pronoun and assembly senses under one a plus vai etymology. The Tamil Lexicon separates the pronoun and Sanskrit-derived assembly. The split cannot be assigned to a common lexical sense."),
 "W09": ("supported_split",["ni","vāraṇam"],"explicit_etymology","The source prints both members; the Tamil Lexicon supplies a Sanskrit derivation despite the missing row-origin flag."),
 "W10": ("supported_split",["akam","pakai"],"explicit_etymology_with_junction","The etymology explicitly names inside and enmity; the surface loses final m."),
 "W11": ("supported_split",["taṇ","aṭai"],"explicit_etymology_with_junction","Winslow's two named members agree with the Tamil Lexicon taṇ-ṇ-aṭai analysis after the junction consonant is separated."),
 "W12": ("supported_split",["uravu","nīr"],"explicit_etymology","The source explicitly names both members and the uravu variant."),
 "W13": ("supported_split",["kampam","nāṭṭiyam"],"nested_gloss_and_member_entry","The post or pillar parent and pole-dancing subentry agree with the independently checked nāṭṭiyam dancing entry."),
 "W14": ("supported_split",["cīr","varicai"],"tamil_lexicon_hyphenation","The Tamil Lexicon prints cīr-varicai; Winslow nests the entry under cīr."),
 "W15": ("supported_split",["kuṭai","niḻal"],"nested_gloss_and_member_entry","The shade parent and umbrella-shade subentry agree with the separately checked kuṭai umbrella entry."),
 "W16": ("supported_split",["muḻu","tēṅkāy"],"tamil_lexicon_hyphenation","The source means an unbroken coconut and the Tamil Lexicon prints muḻu-t-tēṅkāy."),
 "W17": ("supported_split",["puḻuti","nāṟṟu"],"tamil_lexicon_hyphenation","The dry-earth parent and dry-ground plants gloss agree with the Tamil Lexicon decomposition."),
 "W18": ("supported_split",["cē","maṟi"],"tamil_lexicon_hyphenation","The Tamil Lexicon explicitly prints cē-maṟi. Winslow labels the subentry a verbal noun, so noun-pool eligibility needs a declared policy."),
 "W19": ("supported_split",["nāṇayam","puṭavai"],"nested_gloss_and_member_entry","The rare or choice sense of the parent and fine-cloth subentry agree with the separately checked puṭavai cloth entry."),
 "W20": ("incorrect_split",["ai","taru"],"tamil_lexicon_hyphenation","The source means five celestial trees; the Tamil Lexicon prints ai-n-taru. The parser's aint plus aru cuts into the tree member taru."),
 "W21": ("supported_missed_compound",["tāycci","tampalam"],"tamil_lexicon_hyphenation","The Tamil Lexicon prints tāycci-t-tampalam for the same game entry; Winslow supplies the parent and subentry."),
 "W22": ("outside_noun_pair_scope",["nīlam","pārikka"],"infinitive_phrase","The source labels an infinitive meaning become blue, under a Sanskrit-marked parent. A phrase-analysis policy is required before inclusion."),
 "W23": ("undecidable",["narampu","puṭaittal"],"nominalized_verb","The vein parent and swelling-of-veins verbal noun suggest a compositional analysis. The source does not explicitly mark the second boundary and no exact Tamil Lexicon entry was found."),
 "W24": ("supported_missed_compound",["maṉam","malarcci"],"tamil_lexicon_hyphenation","The Tamil Lexicon prints maṉa-malarcci and cites Winslow. This supports the boundary, not an independent attestation. The parent carries a Sanskrit mark absent from the subentry row."),
 "W25": ("undecidable",["pacc","uṭampu"],"unresolved_first_member_morphology","The Tamil Lexicon identifies uṭampu in the etymology but leaves the full headword unhyphenated. The relationship to the pacumai parent needs a morphological decision."),
 "W26": ("outside_noun_pair_scope",["nir","āyutam"],"grammatical_prefix","The parent explicitly identifies nir as a Sanskrit prefix. This is not two picture nouns."),
 "W27": ("undecidable",[],"no_member_analysis","The source gives rivalry and a cross-reference; it supplies no two-member decomposition."),
 "W28": ("outside_noun_pair_scope",[],"letter","The source identifies a compound letter, not a lexical compound."),
 "W29": ("undecidable",[],"no_member_analysis","Both dictionaries give the nail or claw senses without a member analysis. This does not prove etymological simplicity."),
 "W30": ("undecidable",[],"no_member_analysis","The drum definition and cross-reference provide no member analysis."),
 "W31": ("undecidable",[],"no_member_analysis","The nail, ladder and well-sweep senses provide no member analysis."),
 "W32": ("undecidable",[],"no_member_analysis","The colour definition provides no member analysis."),
 "W33": ("undecidable",[],"no_member_analysis","The listed plants and wood sense provide no member analysis."),
 "W34": ("outside_two_member_scope",["taṉi","vali","perumāḷ"],"tamil_lexicon_hyphenation","The Tamil Lexicon supplies three members for the plant name."),
 "W35": ("outside_noun_pair_scope",[],"grammatical_derivative","The source presents an appellative noun for an invisible thing under the seeing verb; no two-lexical-noun decomposition is established."),
 "W36": ("outside_noun_pair_scope",["aḷḷu","kaṭṭa"],"infinitive_phrase","The source labels an infinitive meaning fasten with cramps under the cramp parent."),
 "W37": ("outside_noun_pair_scope",["kōṭṭai","kaṭṭa"],"infinitive_phrase","The source labels an infinitive meaning construct a fort under a Sanskrit-marked parent."),
 "W38": ("outside_noun_pair_scope",[],"grammatical_phrase","The source gives say no under the negative grammatical root al."),
 "W39": ("outside_noun_pair_scope",["ācaraṇai","paṇṇa"],"infinitive_phrase","The source labels perform a religious rite as an infinitive under a Sanskrit-marked parent."),
 "W40": ("undecidable",["muṉ","pōla"],"adverbial_phrase","The source gives as formerly under muṉ. Compound versus phrase status is unresolved."),
 "R01": ("supported_missed_compound",["murukku","cettal"],"nested_gloss","The subentry describes dry murukku wood under dried material. The nasal junction requires a general morphological rule; the source identifies the botanical sense."),
 "R02": ("incorrect_split",[],"letter_root_and_loan","The root ja is explicitly a letter. The subentry means land and refers to camīṉ; the Tamil Lexicon supplies zamīn. The ja plus mīṉ split is invalid."),
 "R03": ("supported_missed_compound",["murukku","pū"],"nested_gloss","The entry names the coral-tree flower under the murukku tree. Its murukkam surface increment does not identify the deity muruku.")
}


def refs(packet):
    return [{key: witness[key] for key in ("source_path","source_sha256","query_page","character_span")}
            for witness in packet["witnesses"]]


def select(candidates, spec):
    term, page, hom, role, sense = spec
    found = [item for item in candidates if (item["entry"]["translit"], item["entry"]["page"], item["entry"]["hom"]) == (term,page,hom)]
    if len(found) != 1 or len(found[0]["witnesses"]) != 1:
        raise ValueError(f"ambiguous or missing source selection: {spec}")
    item = found[0]
    return {"entry_id": item["entry_id"], "form": term, "homograph": hom, "role": role,
            "supported_sense": sense, "source_refs": refs(item),
            "source_citations_as_printed": re.findall(r"\([^()]*\)", item["witnesses"][0]["text"]),
            "earliest_attestation": None, "attestation_status": "dictionary_citations_recorded; primary_text_and_date_not_verified"}


def proposal_ref(year, page, printed):
    folder = "2026-10-20-fish-context" if year == 2010 else "2026-10-22-rebus-blind-templates"
    path = ROOT / f"data/raw/{folder}/sources-v1/parpola{year}-attempt1.pdf"
    return {"source_path": path.relative_to(ROOT).as_posix(), "source_sha256": sha(path),
            "pdf_page_one_based": page, "printed_page": printed}


def jsonl(path, records):
    with path.open("x",encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+"\n")


def main():
    packets = read(OUT / "sense-packets.json")
    supplements = read(OUT / "sense-supplements.json")["entries"]
    lexicon = rows(ROOT / "data/raw/2026-10-21-rebus-base-rate/derived-v1/tamil-lex-entries.jsonl")
    more = [tl_witness(entry) for entry in lexicon if entry["translit"] in {"iru-kaṇ","koḷ-","nāṭṭiyam","kuṭai","puṭavai","taru"}]
    save(OUT / "additional-member-witnesses.json",more)
    all_candidates = {item["entry_id"]:item for packet in packets for item in packet["candidates"]}
    all_candidates.update({item["entry_id"]:item for item in supplements+more})
    senses = []
    for packet in packets:
        form = packet["word"]
        status, specs, rationale = SENSES[form]
        selected = [select(list(all_candidates.values()),spec) for spec in specs]
        senses.append({"form":form,"review_decision":status,"reviewer":REVIEWER,
                       "proposed_identifications":packet["proposals"],"selected_senses":selected,
                       "exact_candidate_entry_ids":[item["entry_id"] for item in packet["candidates"]],
                       "exact_candidates":[{"entry_id":item["entry_id"],"entry":item["entry"],"source_refs":refs(item)} for item in packet["candidates"]],
                       "proposal_source_refs":[proposal_ref(*args) for args in PROPOSAL_PAGES[form]],
                       "rationale":rationale,"uncertainty":"Source review is provisional; historical phonology, source chronology and Indus identification require separate evidence.",
                       "accepted_for_tamil_picture_alternative":status != "wrong_language_for_cited_sense"})
    jsonl(OUT / "sense-review.jsonl",senses)
    aliases=[]
    for form,target,context in [("aṟu","āṟu","aṟu-mīṉ"),("eḻu","ēḻu","eḻu-mīṉ"),("iru","iraṇṭu","iru-kaṇ"),("kāvu","kāvu-","verb citation form")]:
        row=next(row for row in senses if row["form"]==form)
        aliases.append({"surface_form":form,"lemma_form":target,"scope":context,
                        "relation":"source_attested_combining_form" if form!="kāvu" else "verb_citation_form",
                        "source_selections":row["selected_senses"],"reviewer":REVIEWER,
                        "universal_alias":False,"frequency_alias":False})
    save(OUT / "accepted-relations.json",aliases)
    compound=[]
    for packet in read(OUT / "compound-packets-v2.json"):
        sample=packet["sample_id"]
        decision,members,basis,rationale=COMPOUNDS[sample]
        extras=[item for item in more if item["entry"]["translit"] in {"W13":{"nāṭṭiyam"},"W15":{"kuṭai"},"W19":{"puṭavai"},"W20":{"taru"}}.get(sample,set())]
        compound.append({"sample_id":sample,"sample_stratum":packet["stratum"],"entry_id":packet["entry_id"],
                         "form":packet["entry"]["translit_plain"],"parser_members":packet["entry"]["members"],
                         "review_decision":decision,"source_supported_members":members,"decision_basis":basis,
                         "rationale":rationale,"source_refs":refs(packet),"original_entry":packet["entry"],
                         "dictionary_crosschecks":[{"entry_id":item["entry_id"],"entry":item["entry"],"source_refs":refs(item)} for item in packet["tamil_lexicon_comparison"]+extras],
                         "reviewer":REVIEWER,"uncertainty":"Provisional source boundary review; historical derivation and native-noun eligibility are separate judgments.",
                         "in_frozen_sample":sample.startswith("W")})
    jsonl(OUT / "compound-review.jsonl",compound)
    accepted=[row for row in compound if row["in_frozen_sample"] and len(row["parser_members"])==2]
    rejected=[row for row in compound if row["in_frozen_sample"] and len(row["parser_members"])!=2]
    counts=Counter(row["review_decision"] for row in accepted)
    supported=counts["supported_split"]; bad=counts["incorrect_split"]; unknown=counts["undecidable"]
    summary={"sense_forms":len(senses),"exact_candidate_records":sum(len(row["exact_candidate_entry_ids"]) for row in senses),
             "sense_decisions":dict(Counter(row["review_decision"] for row in senses)),
             "selected_sense_records":sum(len(row["selected_senses"]) for row in senses),
             "source_attested_scoped_relations":len(aliases),"frozen_sample":len(accepted)+len(rejected),"known_regressions":3,
             "accepted_split_decisions":dict(counts),"rejected_decisions":dict(Counter(row["review_decision"] for row in rejected)),
             "source_boundary_agreement":{"adjudicable_numerator":supported,"adjudicable_denominator":supported+bad,
                                          "conditional_fraction":supported/(supported+bad),"all_accepted_denominator":len(accepted),
                                          "lower_bound":supported/len(accepted),"upper_bound":(supported+unknown)/len(accepted),
                                          "scope":"Source boundary agreement in the selected stratified audit. Junction variants count when the source explicitly names the members. This is neither native-noun eligibility precision nor dictionary-wide accuracy."},
             "global_recall":None,"new_reading_evaluation":False,"rebus_effect_recomputed":False,
             "reviewer":REVIEWER}
    save(PKG / "results-v1.json",summary)
    artifacts=[OUT / name for name in ["sense-review.jsonl","compound-review.jsonl","accepted-relations.json","additional-member-witnesses.json"]]
    paths={ROOT / ref["source_path"] for row in senses for ref in row["proposal_source_refs"]}
    for item in list(all_candidates.values())+read(OUT / "compound-packets-v2.json"):
        paths.update(ROOT/ref["source_path"] for ref in refs(item))
        for match in item.get("tamil_lexicon_comparison",[]): paths.update(ROOT/ref["source_path"] for ref in refs(match))
    save(PKG / "source-manifest-v1.json",{"sources":[{"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path)} for path in sorted(paths)],
                                         "local_outputs":[{"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path)} for path in artifacts],
                                         "redistribution":"Source pages, detailed derivatives and review rows remain local. Only hashes, code and aggregate project observations are tracked."})
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
