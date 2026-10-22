"""Compact JSON writer for the town configurations (role img-B).

Lists of numbers and lists of coordinate pairs stay on one line, so polygons
and endpoints remain readable.
"""
import json


def _fmt(o, ind=0):
    sp = " " * ind
    if isinstance(o, dict):
        if not o:
            return "{}"
        items = [f'{sp} {json.dumps(k, ensure_ascii=False)}: {_fmt(v, ind + 1).lstrip()}' for k, v in o.items()]
        return "{\n" + ",\n".join(items) + "\n" + sp + "}"
    if isinstance(o, list):
        flat = json.dumps(o, ensure_ascii=False)
        if all(not isinstance(x, (dict, str)) for x in o) and len(flat) < 2000:
            return flat
        if not o:
            return "[]"
        return "[\n" + ",\n".join(sp + " " + _fmt(x, ind + 1).lstrip() for x in o) + "\n" + sp + "]"
    return json.dumps(o, ensure_ascii=False)


def save(cfg, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(_fmt(cfg) + "\n")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
