# Execution notes

The first schema inspection searched the normalized table's nonexistent `cisi` top-level field and returned zero tablets. The corrected query uses `source_cisi`; all 66 tablet rows are present. The original probe was diagnostic and wrote no endpoint.

A quoted one-line PowerShell/Python inspection failed with an unterminated string. The subsequent file-backed helper avoids nested quote substitution. Two searches also used a shell wildcard which `rg` did not expand; the corrected searches pass a directory with a glob argument or filter its file listing.

An optional renderer for seven imported glyph codes could not import `fontTools` in either the system Python or the supplied workspace Python. Those attempts wrote no font or image witness. Pillow's FreeType backend then successfully read WOFF2 directly, removing the conversion dependency. The rendered glyphs corrected a preliminary family label: 154/156 belong to complex C, while 861 is diamond D. Its crop and font hashes are preserved locally.

The first aggregate endpoint retained every count and registration but queried a nonexistent face-position field. This silently left its displayed positions null. A schema inspection found the actual key `form_display_position`. The second endpoint restores those fields and adds a source-display summary; the first endpoint and its source snapshot remain unchanged. Count, exact-module and finite-count results are identical between endpoints.
