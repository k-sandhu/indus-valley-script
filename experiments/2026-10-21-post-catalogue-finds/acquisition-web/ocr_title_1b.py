"""OCR a small title-area crop in memory; never save page text or page images."""
import argparse
import json
import subprocess
ap=argparse.ArgumentParser()
ap.add_argument("pdf")
args=ap.parse_args()
image=subprocess.run(["pdftoppm","-f","1","-l","1","-singlefile","-scale-to","1800","-y","0","-H","260","-png",args.pdf],capture_output=True,timeout=60)
text=subprocess.run(["tesseract","stdin","stdout","--psm","6"],input=image.stdout,capture_output=True,timeout=45)
lines=[line.strip() for line in text.stdout.decode("utf-8",errors="replace").splitlines() if line.strip()]
print(json.dumps({"title_area_ocr":lines[:3]},ensure_ascii=True))
