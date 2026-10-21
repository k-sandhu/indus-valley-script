# Independent segmentation of held seal legends

Working directory: `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. The project studies the undeciphered Indus script. A seal legend is the short text cut on a seal, written here as a sequence of sign numbers from the Wells sign list (for example `740` is the jar sign). We have written rules that cut a legend into units and name its closing formula, the stretch at its end drawn from a list of recurring closings. Before we use the rules to score new material, we need to know whether someone who did not write them gets the same answer by following them. You are that second reader.

## What you have

- The rules: `experiments/2026-10-20-seal-legend-units/RULES-v2.md`. Read them first; they are short.
- The two lists the rules use, in `data/raw/2026-10-20-seal-legend-units/frozen-v2/`: `inventory.json` (field `units`, each with a `unit` list of sign numbers; these are the units of two or more signs) and `closing-stock.json` (field `units`, each with a `unit` list; these are the closing formulas).
- The legends to segment: `data/raw/2026-10-20-seal-legend-units/frozen-v2/held-legends.jsonl`, one JSON object per line with an `id` and a `text` (sign numbers in reading order, first sign read first).

Use only these four files. Do not open any other file in `experiments/2026-10-20-seal-legend-units/` or in `data/raw/2026-10-20-seal-legend-units/`, including code, model files, other outputs and anything in the `agreement` folder: the measurement is whether the rules, as written, determine the result. You may write your own short program from RULES-v2.md to apply them, or apply them by hand; either way, follow the text of RULES-v2.md, and where you find it ambiguous, choose the reading you think it intends and note the ambiguity.

## What to produce

Write `data/raw/2026-10-20-seal-legend-units/frozen-v2/agreement/agent-v2.jsonl` (create the folder if needed), one line per held legend, in the same order, as JSON: `{"id": "H000", "cuts": [positions], "closing": [sign numbers] or null}`. Positions count a cut between the i-th and (i+1)-th sign as i, so they run from 1 to the legend's length minus one, in increasing order. `closing` is the closing formula found by Rule 1, or `null` when the legend has no stock closing. If you wrote a program, save it in the same `agreement` folder as `agent-v2-program.py`.

When you finish, reply with a short account in connected prose: how you applied the rules, how many legends had a stock closing, and every place where the rules were ambiguous or silent and what you decided. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.
