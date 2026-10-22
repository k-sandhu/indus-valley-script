"""Print page count, page sizes and text-layer status of PDFs."""
import sys, fitz
for p in sys.argv[1:]:
    try:
        d = fitz.open(p)
    except Exception as e:
        print(p, "ERROR", e); continue
    n = d.page_count
    txt = sum(1 for i in range(min(n, 40)) if len(d[i].get_text().strip()) > 50)
    sizes = {}
    for i in range(n):
        r = d[i].rect
        k = (round(r.width), round(r.height))
        sizes[k] = sizes.get(k, 0) + 1
    big = sorted(sizes.items(), key=lambda x: -x[1])[:4]
    print(f"{p}\n  pages={n} text_pages_in_first40={txt} sizes={big} toc={len(d.get_toc())}")
