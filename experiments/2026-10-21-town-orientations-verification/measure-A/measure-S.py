"""Run the unchanged refinement tool and draw a separate, fresh fitted-line check."""
import sys,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
owned=Path(__file__).resolve().parent
tools=owned.parent/'tools'
picks,side,output,overlay=map(Path,sys.argv[1:])
if output.exists() or overlay.exists():raise FileExistsError('fresh outputs required')
subprocess.run([sys.executable,'-I',str(tools/'measure_lines.py'),str(picks),str(side),str(output)],check=True)
result=json.loads(output.read_text(encoding='utf-8'))
# Original PNG is preserved. This separate annotated image is for inspection only.
im=Image.open(str(side)[:-5]).convert('RGB');draw=ImageDraw.Draw(im)
for line in result['lines']:
    points=[tuple(p) for p in line['refined_endpoints_px']]
    draw.line(points,fill='red',width=2)
    for x,y in points:draw.ellipse((x-3,y-3,x+3,y+3),outline='red',width=2)
    draw.text(points[0],line['id'],fill='red',stroke_width=1,stroke_fill='white')
if result.get('arrow'):
    draw.line([tuple(p) for p in result['arrow']['refined_endpoints_px']],fill='green',width=2)
im.save(overlay)
print(json.dumps([dict(id=r['id'],theta=r['theta_deg'],sigma=r['sigma_deg'],length=r['length_m'],inliers=r['inlier_count'],profiles=r['profile_count']) for r in result['lines']]))
