# Regional research helpers

These four Python files preserve the regional contributors’ acquisition and record-compilation code. The acquisition helper writes downloads and extracted third-party text to the local raw directory. Run it from the repository root with `python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/research-code/afghan-minor-revision/acquire.py`; it requires requests and pypdf. No dependency installation was performed.

The three regional compilation helpers record how the contributors assembled their initial revision rows. Later page checks also produced manual corrections in the curated `revision-*.json` inputs. For the final census, run the main package’s `build_revision.py` and the remaining commands in its README. Regenerating regional inputs from a helper alone can lose those later corrections.
