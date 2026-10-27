import requests,re,pathlib
root=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-phase-pass2')
u='https://www.cambridge.org/core/journals/radiocarbon/article/tata-institute-radiocarbon-date-list-i/D702BB5DE8A77C1D8EE58DF4D8B1E8DA'
r=requests.get(u);(root/'cambridge.html').write_bytes(r.content)
for x in re.findall(r'[^\s"<>]+\.pdf[^\s"<>]*',r.text): print(x[:500])
