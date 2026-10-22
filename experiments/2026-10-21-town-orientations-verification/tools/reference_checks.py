"""Compare IGRF calculations to saved BGS outputs and inspect official runway tables."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,re,html,json
from common import read_json,write_json
from igrf import field
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw');p.add_argument('--output');p.add_argument('--runway-tables',action='store_true');a=p.parse_args();root=Path(a.raw)
    if a.runway_tables:
        for path in sorted((root/'validation'/'official-aip').glob('*.html')):
            text=path.read_text(encoding='utf-8',errors='replace');marker=text.find('RUNWAY PHYSICAL CHARACTERISTICS');text=text[marker:marker+30000];plain=html.unescape(re.sub('<[^>]+>',' ',text));plain=' '.join(plain.split());print(path.name,plain[:3500])
        return
    cases=[]
    for path in sorted((root/'igrf'/'official-tests').glob('*.json')):
        text=path.read_text(encoding='utf-8-sig');data=json.loads(text[text.index('{'):])['geomagnetic-field-model-result'];c=data['coordinates'];lat=c['latitude']['value'];lon=c['longitude']['value'];year=int(data['date']['value'][:4]);expected=data['field-value']['declination']['value'];got=field(lat,lon,year,coefficients=root/'igrf'/'igrf14coeffs.txt');residual=got['declination_deg']-expected
        cases.append(dict(latitude=lat,longitude=lon,year=year,reference_declination_deg=expected,computed_declination_deg=got['declination_deg'],residual_deg=residual,tolerance_deg=.002,pass_=abs(residual)<=.002,reference_path=path.as_posix()))
    for c in cases:c['pass']=c.pop('pass_')
    result=dict(schema_version=1,model='IGRF-14',cases=cases,overall_pass=len(cases)>=3 and all(c['pass'] for c in cases))
    if a.output:write_json(a.output,result)
    print(result)
if __name__=='__main__':main()
