import fitz,pathlib,json
p=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-pass3');d=fitz.open('research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf');a=[x.get_text() for x in d];(p/'held-chapter-text.json').write_text(json.dumps(a),encoding='utf8');print(len(d));print(a[0][:400]);print(a[-1][-4500:])
