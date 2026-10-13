"""Record a working-draft refinement and recover its earlier body from the patch.

The recovered text is explicitly reconstructed, not a pre-edit snapshot or a
frozen empirical endpoint. The original selection and protocols stay unchanged.
"""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PACKAGE=HERE.parent
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/theory-refinement-v1'
INSERTIONS=[
 'The new fixed passage frame supplies a concrete incorporation example. RV 10.71.2 compares fashioning speech with sifting meal and connects speech with companion recognition. A practical process becomes a model for an intellectual activity. This is a directly represented association at the textual endpoint. Its earlier history remains to be compared. The [refinement record](coordinator/REFINEMENT-analogy.md) labels the development after reading that stanza.\n\n',
 'The sifting image suggests one specific form of this process: material actions can provide models for selecting, refining or coordinating knowledge. Its historical study should code the practical action, the conceptual use and the verbal form separately. A familiar operation and a distinctive inherited poetic construction can contribute to the same image. Neither component\'s history determines the whole combination by itself.\n\n'
]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=HERE/'theory-refinement-v1.json'
    if RAW.exists() or out.exists():raise SystemExit('Refinement record exists; no overwrite.')
    current=(PACKAGE/'THEORY.md').read_text('utf-8')
    earlier=current
    for text in INSERTIONS:
        assert earlier.count(text)==1
        earlier=earlier.replace(text,'')
    RAW.mkdir(parents=True)
    restored=RAW/'THEORY-before-analogy-reconstructed.md'
    with restored.open('x',encoding='utf-8',newline='\n') as stream:stream.write(earlier)
    with out.open('x',encoding='utf-8') as stream:
        json.dump({'created_utc':datetime.now(timezone.utc).isoformat(),
                   'scope':'Unfrozen working-theory revision after a new fixed-frame reading, with reconstructed earlier body. No old experiment endpoint changed.',
                   'reconstruction_method':'Remove only the two documented inserted paragraphs from the current draft. This is not represented as a pre-edit byte snapshot.',
                   'reconstructed_path':restored.relative_to(ROOT).as_posix(),'reconstructed_sha256':sha(restored),
                   'current_theory_sha256':sha(PACKAGE/'THEORY.md'),
                   'refinement_sha256':sha(HERE/'REFINEMENT-analogy.md'),'insertions':INSERTIONS},stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({'inserted_paragraphs':len(INSERTIONS),'older_body_reconstructed':True}))


if __name__=='__main__':main()
