"""Write the registry of Radiocarbon-journal date lists we downloaded.

Reads data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/acquisitions.jsonl and
writes dating-v1/code/radiocarbon_lists.json, which build_sources.py folds into
sources.json. Source ids are rc-<list>, for example rc-tf-ii.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
ACQ = ROOT / "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/acquisitions.jsonl"
OUT = pathlib.Path(__file__).resolve().parent / "radiocarbon_lists.json"

META = {
    "TF-I": ("Kusumgar, S., Lal, D. and Sarna, R. P.", 1963, "Tata Institute Radiocarbon Date List I", "5", "273-282"),
    "TF-II": ("Agrawal, D. P., Kusumgar, S., Lal, D. and Sarna, R. P.", 1964, "Tata Institute Radiocarbon Date List II", "6", "226-232"),
    "TF-III": ("Agrawal, D. P., Kusumgar, S. and Lal, D.", 1965, "Tata Institute Radiocarbon Date List III", "7", "291-295"),
    "TF-IV": ("Agrawal, D. P. and Kusumgar, S.", 1966, "Tata Institute Radiocarbon Date List IV", "8", "442-452"),
    "TF-V": ("Agrawal, D. P. and Kusumgar, S.", 1968, "Tata Institute Radiocarbon Date List V", "10", "131-143"),
    "TF-VI": ("Agrawal, D. P. and Kusumgar, S.", 1969, "Tata Institute Radiocarbon Date List VI", "11(1)", "188-193"),
    "TF-VII": ("Agrawal, D. P., Gupta, S. K. and Kusumgar, S.", 1969, "Tata Institute Radiocarbon Date List VII", "11(2)", "502-508"),
    "TF-VIII": ("Agrawal, D. P., Gupta, S. K. and Kusumgar, S.", 1971, "Tata Institute Radiocarbon Date List VIII", "13(1)", "84-93"),
    "TF-IX": ("Agrawal, D. P., Gupta, S. K. and Kusumgar, S.", 1971, "Tata Institute Radiocarbon Date List IX", "13(2)", "442-449"),
    "TF-X": ("Agrawal, D. P. and Kusumgar, S.", 1973, "Tata Institute Radiocarbon Date List X", "15(3)", "574-585"),
    "TF-XI": ("Agrawal, D. P. and Kusumgar, S.", 1975, "Tata Institute Radiocarbon Date List XI", "17(2)", "219-225"),
    "TF-1967": ("Radiocarbon editors", 1967, "Comprehensive Index, 1950-1965: Tata Institute of Fundamental Research", "9", "169-171"),
    "PRL-I": ("Agrawal, D. P., Krishnamurthy, R. V., Kusumgar, S. and Pant, R. K.", 1976, "Physical Research Laboratory Radiocarbon Date List I", "18(1)", "89-95"),
    "PRL-II": ("Agrawal, D. P., Krishnamurthy, R. V., Kusumgar, S. and Pant, R. K.", 1977, "Physical Research Laboratory Radiocarbon Date List II", "19(2)", "229-236"),
    "PRL-III": ("Agrawal, D. P., Krishnamurthy, R. V., Kusumgar, S. and Pant, R. K.", 1978, "Physical Research Laboratory Radiocarbon Date List III", "20(2)", "234-244"),
    "PRL-IV": ("Agrawal, D. P., Krishnamurthy, R. V., Kusumgar, S. and Pant, R. K.", 1981, "Physical Research Laboratory Radiocarbon Date List IV", "23(1)", "38-42"),
    "PRL-V": ("Agrawal, D. P., Krishnamurthy, R. V. and Kusumgar, S.", 1985, "Physical Research Laboratory Radiocarbon Date List V", "27(1)", "95-110"),
    "PRL-VI": ("Agrawal, D. P., Kusumgar, S. and Yadava, M. G.", 1991, "Physical Research Laboratory Radiocarbon Date List VI", "33(3)", "329-344"),
    "PRLC-I": ("Bhushan, R., Chakraborty, S. and Krishnaswami, S.", 1994, "Physical Research Laboratory (Chemistry) Radiocarbon Date List I", "36(2)", "251-256"),
    "BS-I": ("Rajagopalan, G., Vishnu-Mittre and Sekar, B.", 1978, "Birbal Sahni Institute Radiocarbon Measurements I", "20(3)", "398-404"),
    "BS-II": ("Rajagopalan, G., Vishnu-Mittre and Sekar, B.", 1980, "Birbal Sahni Institute Radiocarbon Measurements II", "22(1)", "54-60"),
    "BS-III": ("Rajagopalan, G., Vishnu-Mittre, Sekar, B. and Mandal, T. K.", 1982, "Birbal Sahni Institute Radiocarbon Measurements III", "24(1)", "45-53"),
    "PENN-III": ("Ralph, E. K.", 1959, "University of Pennsylvania Radiocarbon Dates III", "1 (American Journal of Science Radiocarbon Supplement)", "45-58"),
    "PENN-IV": ("Ralph, E. K. and Ackerman, R. E.", 1961, "University of Pennsylvania Radiocarbon Dates IV", "3", "4-14"),
    "PENN-V": ("Ralph, E. K. and Stuckenrath, R., Jr.", 1962, "University of Pennsylvania Radiocarbon Dates V", "4", "144-159"),
    "PENN-VI": ("Stuckenrath, R., Jr.", 1963, "University of Pennsylvania Radiocarbon Dates VI", "5", "82-103"),
    "PENN-VII": ("Ralph, E. K., Michael, H. N. and Gruninger, J., Jr.", 1965, "University of Pennsylvania Dates VII", "7", "179-186"),
    "PENN-VIII": ("Stuckenrath, R., Jr. and Ralph, E. K.", 1965, "University of Pennsylvania Radiocarbon Dates VIII", "7", "187-199"),
    "PENN-IX": ("Stuckenrath, R., Jr., Coe, W. R. and Ralph, E. K.", 1966, "University of Pennsylvania Radiocarbon Dates IX", "8", "348-385"),
    "PENN-X": ("Stuckenrath, R., Jr.", 1967, "University of Pennsylvania Radiocarbon Dates X", "9", "333-345"),
    "PENN-XI": ("Stuckenrath, R., Jr. and Lawn, B.", 1969, "University of Pennsylvania Radiocarbon Dates XI", "11(1)", "150-162"),
    "PENN-XII": ("Ralph, E. K. and Michael, H. N.", 1969, "University of Pennsylvania Radiocarbon Dates XII", "11(2)", "469-481"),
    "PENN-XIII": ("Lawn, B.", 1970, "University of Pennsylvania Radiocarbon Dates XIII", "12(2)", "577-589"),
    "PENN-XIV": ("Lawn, B.", 1971, "University of Pennsylvania Radiocarbon Dates XIV", "13(2)", "363-377"),
    "PENN-XV": ("Lawn, B.", 1973, "University of Pennsylvania Radiocarbon Dates XV", "15(2)", "367-381"),
    "PENN-XVI": ("Michael, H. N. and Ralph, E. K.", 1974, "University of Pennsylvania Radiocarbon Dates XVI", "16(2)", "198-218"),
    "PENN-XVII": ("Lawn, B.", 1974, "University of Pennsylvania Radiocarbon Dates XVII", "16(2)", "219-237"),
    "PENN-XVIII": ("Lawn, B.", 1975, "University of Pennsylvania Radiocarbon Dates XVIII", "17(2)", "196-215"),
    "PENN-XIX": ("Fishman, B., Forbes, H. and Lawn, B.", 1977, "University of Pennsylvania Radiocarbon Dates XIX", "19(2)", "188-228"),
    "PENN-XX": ("Fishman, B. and Lawn, B.", 1978, "University of Pennsylvania Radiocarbon Dates XX", "20(2)", "210-233"),
    "PENN-XXI": ("Meulengracht, A., McGovern, P. and Lawn, B.", 1981, "University of Pennsylvania Radiocarbon Dates XXI", "23(2)", "227-240"),
    "PENN-XXII": ("Hurst, B. J. and Lawn, B.", 1984, "University of Pennsylvania Radiocarbon Dates XXII", "26(2)", "212-240"),
    "PENN-1967": ("Radiocarbon editors", 1967, "Comprehensive Index, 1950-1965: University of Pennsylvania", "9", "119-128"),
}


def main():
    recs = {}
    for line in ACQ.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        recs[r["name"]] = r  # last retrieval wins
    out = []
    for name, (auth, yr, title, vol, pages) in META.items():
        r = recs[name]
        out.append({
            "id": "rc-" + name.lower(),
            "citation": f"{auth} {yr}. {title}. Radiocarbon {vol}: {pages}. doi:{r['doi']}",
            "url_or_path": r["file"],
            "url": r["final_url"],
            "doi": r["doi"],
            "retrieved_utc": r["retrieved_utc"],
            "sha256": r["sha256"],
            "text_extraction": r["file"][:-4] + ".txt",
            "note": "Text layer extracted with PyMuPDF; page markers in the .txt are PDF pages, journal page numbers are printed in the text.",
        })
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(out), "lists written to", OUT)


if __name__ == "__main__":
    main()
