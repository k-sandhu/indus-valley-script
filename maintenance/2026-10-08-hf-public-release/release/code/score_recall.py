import score_core as E

def recall_page(predicted,reference):
    matched=detected=true=0;columns=[]
    for column in reference['columns']:
        left,right=column['x_extent_pdf'];actual=column['row_centers_pdf']
        assert len(actual)==column['row_count']
        guesses=[r['row_anchor_y_2x']/2 for r in predicted if left<=(r['margin_xyxy_2x'][0]+r['margin_xyxy_2x'][2])/4<=right]
        pairs=sorted((abs(a-b),i,j) for i,a in enumerate(guesses) for j,b in enumerate(actual) if abs(a-b)<=9)
        used_guess=set();used_true=set()
        for distance,i,j in pairs:
            if i in used_guess or j in used_true:continue
            used_guess.add(i);used_true.add(j)
        count=len(used_true);matched+=count;true+=len(actual);detected+=len(guesses)
        columns.append(dict(reference_rows=len(actual),detected_rows=len(guesses),matched_rows=count))
    # Predictions outside every source-column extent are false positives.
    detected=len(predicted)
    return dict(pdf_page=reference['pdf_page'],matched=matched,true=true,detected=detected,columns=columns)


def page_summary(pages):
    m=sum(p['matched'] for p in pages);t=sum(p['true'] for p in pages);d=sum(p['detected'] for p in pages)
    return dict(pages=len(pages),matched=m,true_rows=t,detected_rows=d,recall=E.wilson(m,t),precision=E.wilson(m,d))

