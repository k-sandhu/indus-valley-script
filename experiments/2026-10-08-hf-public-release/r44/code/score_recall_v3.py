def recall_page(predicted,reference,physical=False):
    matched=detected=true=0;columns=[]
    for column in reference['columns']:
        left,right=column['x_extent_pdf']
        actual=column['physical_line_centers_pdf'] if physical else column['row_centers_pdf']
        assert len(actual)==column['physical_line_count' if physical else 'row_count']
        guesses=[]
        for r in predicted:
            if not physical and r['line_kind']!='numbered':continue
            field=r.get('margin_pdf_box');box=r['glyph_pdf_box']
            x=(field[0]+field[2])/2 if field else (box[0]+box[2])/2
            if left<=x<=right:guesses.append((box[1]+box[3])/2 if physical else r['row_anchor_y_2x']/2)
        pairs=sorted((abs(a-b),i,j) for i,a in enumerate(guesses) for j,b in enumerate(actual) if abs(a-b)<=9)
        used_guess=set();used_true=set()
        for distance,i,j in pairs:
            if i not in used_guess and j not in used_true:used_guess.add(i);used_true.add(j)
        matched+=len(used_true);true+=len(actual);detected+=len(guesses)
        columns.append(dict(reference_rows=len(actual),detected_rows=len(guesses),matched_rows=len(used_true)))
    detected=sum(physical or r['line_kind']=='numbered' for r in predicted)
    return dict(pdf_page=reference['pdf_page'],matched=matched,true=true,detected=detected,columns=columns)

