"""Write linked prose from completed aggregates; refuse existing documents."""
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
def read(name):
    return json.loads((OWN / name).read_text(encoding='utf-8'))
def write(name, text):
    p = OWN / name
    if p.exists():
        raise FileExistsError(p)
    p.parent.mkdir(exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8')
def percent(x):
    return f'{100*x:.4f}'
def contrast(entry, metric, multiplier=1):
    x = entry[metric]
    a, b = x['component_bootstrap_95_ci']
    return f'{x["difference"]*multiplier:+.4f} [{a*multiplier:+.4f}, {b*multiplier:+.4f}]'
def name(family, extra):
    return {'classical': 'MKN', 'gru': 'GRU', 'transformer': 'Transformer', 'metadata': 'Conditioned neural', 'ensemble': 'Log ensemble'}[family] + (' + extra' if extra else '')
def main():
    results = read('aggregate-results.json'); curves = read('learning-curves.json')
    audit = read('benchmark-audit.json'); graph = read('extra-graph-audit.json')
    training = read('training-diagnostics.json'); frozen = read('frozen-model/manifest.json'); verification = read('verification.json')
    frozen_check = read('frozen-inference-v2-verification.json')
    models = results['models']; primary = {k: v for k, v in models.items() if k.endswith('/loss')}
    best_accuracy = max(primary, key=lambda k: primary[k]['summary']['top1'])
    best_loss = min(primary, key=lambda k: primary[k]['summary']['bucket_cross_entropy_bits'])
    mkn = models['classical/extra0/loss']; m = mkn['summary']
    a = models[best_accuracy]['summary']; l = models[best_loss]['summary']
    lines = ['# Modern restoration on the preserved Paper 001 masks', '',
        f'Modified Kneser–Ney reaches {percent(m["top1"])}% exact top-one and {m["bucket_cross_entropy_bits"]:.6f} bucket bits on all 8,009 masks. The highest top-one among the primary procedures is {percent(a["top1"])}% for `{best_accuracy}`; the lowest native bucket loss is {l["bucket_cross_entropy_bits"]:.6f} bits for `{best_loss}`. These are Exploratory comparisons on a reused benchmark. [Aggregate results](aggregate-results.json), `models.*.summary`.', '',
        'The saved population, artifacts, targets, components and folds reproduce exactly. The broader export links 144–159 existing benchmark training strings per fold to test strings through other observed faces. The matched comparison retains the required saved folds; extra text excludes all such connections. This limits an independence claim for the broader register. [Benchmark audit](benchmark-audit.json), `correspondence`; [graph audit](extra-graph-audit.json), `outer`.', '',
        '## Accuracy, probability loss and calibration', '',
        'Primary choices minimize three-inner-fold loss. Neural probabilities average three seeds. Native bucket loss uses each fitted training vocabulary; common-alphabet loss pools added codes back into the original full outer-training UNKNOWN event. Exact top-k uses fine-code identity. Five-bin ECE compares top-label mass with exact correctness.', '',
        '| Procedure | Top-one % | Top-five % | Top-ten % | Native bits | Common bits | ECE % |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for key in ['Markov1', 'Markov2']:
        s = results['comparators'][key]
        lines.append(f'| {key}, saved | {percent(s["top1"])} | {percent(s["top5"])} | {percent(s["top10"])} | {s["bucket_cross_entropy_bits"]:.6f} | {s["common_alphabet_bucket_cross_entropy_bits"]:.6f} | {percent(s["expected_calibration_error"])} |')
    for extra in [0, 1]:
        for family in ['classical', 'gru', 'transformer', 'metadata', 'ensemble']:
            s = models[f'{family}/extra{extra}/loss']['summary']
            lines.append(f'| {name(family, extra)} | {percent(s["top1"])} | {percent(s["top5"])} | {percent(s["top10"])} | {s["bucket_cross_entropy_bits"]:.6f} | {s["common_alphabet_bucket_cross_entropy_bits"]:.6f} | {percent(s["expected_calibration_error"])} |')
    lines += ['', 'Every table entry comes from `aggregate-results.json`, `comparators` or `models.<family>/extra<0|1>/loss.summary`. Configuration and inner candidate losses are in `fold_selection`; detailed probabilities remain local.', '',
        'Paired differences below are new minus saved comparator. Accuracy differences are percentage points, and loss differences are bits. Intervals use 2,000 paired component resamples with seed 23101. They condition on the fitted models and transcription population.', '',
        '| Procedure | Comparator | Top-one difference [95% interval] | Native loss difference [95% interval] |',
        '|---|---|---:|---:|']
    gru = models['gru/extra0/loss']['summary']; transformer = models['transformer/extra0/loss']['summary']
    lines.insert(lines.index('Paired differences below are new minus saved comparator. Accuracy differences are percentage points, and loss differences are bits. Intervals use 2,000 paired component resamples with seed 23101. They condition on the fitted models and transcription population.'),
        f'The benchmark-only GRU gives {percent(gru["top1"])}% top-one and {gru["bucket_cross_entropy_bits"]:.6f} bits; the transformer gives {percent(transformer["top1"])}% and {transformer["bucket_cross_entropy_bits"]:.6f} bits. Loss selection chooses MKN order 3 and discount scale 1 in all ten outer fold/regime combinations. The tables compare each family with the same saved first- and second-order queries.')
    for extra in [0, 1]:
        for family in ['classical', 'gru', 'transformer', 'metadata', 'ensemble']:
            e = models[f'{family}/extra{extra}/loss']
            for reference in ['Markov1', 'Markov2']:
                metrics = e['paired'][reference]['strata']['all']['metrics']
                lines.append(f'| {name(family, extra)} | {reference} | {contrast(metrics, "top1", 100)} | {contrast(metrics, "bucket_loss_bits")} |')
    lines += ['', '`models.*.paired.<comparator>.strata` also gives paired top-five, top-ten, common-alphabet loss and ECE intervals for every position and frequency stratum.', '',
        f'MKN improves accuracy and loss over both saved Markov comparators. Its ECE is {percent(m["expected_calibration_error"])}%, compared with {percent(results["comparators"]["Markov1"]["expected_calibration_error"])}% for first order. The rare-target and boundary rows below locate that calibration cost. [Full MKN contrasts](aggregate-results.json), `models.classical/extra0/loss.paired`.', '',
        '## Additional text and metadata', '',
        'The observed export contains 5,680 faces. Complete, nonempty strings absent from the benchmark produce 1,533 extra candidate faces and 3,304 tokens. The graph uses every face, including unusable ones, to retain conservative transitive links. After excluding the held-out closure, one representative per extra string enters fitting. [Input audit](benchmark-audit.json), `extra_candidate_faces`, `extra_candidate_tokens` and `outer_extra`.', '',
        '| Outer fold | Connected faces excluded | Faces retained | Face tokens retained | Distinct texts added | Tokens added | Short texts added | Multiline texts added |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for e in audit['outer_extra']:
        lines.append('| ' + ' | '.join(str(e[k]) for k in ['fold', 'excluded_connected_faces', 'retained_faces', 'retained_face_tokens', 'added_texts', 'added_tokens', 'added_short_texts', 'added_multiline_texts']) + ' |')
    lines += ['', 'Inner fitting excludes the outer test closure and the inner validation closure. The independent breadth-first audit finds zero violations in all 5 outer and 15 inner allocations. Direction and multiline composition are recorded in `outer_extra[*].added_directions` and `added_multiline_texts`. Multiline faces use the export’s flattened reading order; uncertain line continuity can affect transfer.', '',
        '| Family | Extra minus no-extra top-one, points [95% interval] | Native loss, bits [95% interval] | Common loss, bits [95% interval] |',
        '|---|---:|---:|---:|']
    for family in ['classical', 'gru', 'transformer', 'metadata', 'ensemble']:
        metrics = results['direct_contrasts'][family + '/extra_minus_noextra']['strata']['all']['metrics']
        lines.append(f'| {name(family, 0)} | {contrast(metrics, "top1", 100)} | {contrast(metrics, "bucket_loss_bits")} | {contrast(metrics, "common_bucket_loss_bits")} |')
    lines += ['', 'These are separately selected procedures within each training regime. Additional text can change vocabulary, contexts, domain and selected settings. Common-alphabet loss compares the same target events; the native loss also includes finer prediction events when the extra pool supports a previously unseen fine code. [Direct contrasts](aggregate-results.json), `direct_contrasts.*extra_minus_noextra`.', '',
        'The conditioned model adds object type, site, region and motif together to the best unconditioned family selected inside each outer training set. It retunes duration on inner folds. The measurement concerns the joint predictive contribution of those fields and representative metadata; it does not isolate any single field.', '',
        '| Text regime | Conditioned minus selected unconditioned top-one, points [95% interval] | Native loss, bits [95% interval] |',
        '|---|---:|---:|']
    for extra in [0, 1]:
        metrics = results['direct_contrasts'][f'metadata/extra{extra}/conditioned_minus_selected_family']['strata']['all']['metrics']
        lines.append(f'| {"With extra" if extra else "Benchmark only"} | {contrast(metrics, "top1", 100)} | {contrast(metrics, "bucket_loss_bits")} |')
    lines += ['', '## Data size and model capacity', '',
        'The curve keeps the full-training inner-selected family, configuration and duration. Component subsets are nested at 25%, 50%, 75% and 100%; the extra pool stays fixed in the added-text regime. Each cell is exact top-one percent / native bucket bits.', '',
        '| Training fraction | MKN | MKN + extra | Selected neural | Selected neural + extra |',
        '|---|---:|---:|---:|---:|']
    for fraction in [25, 50, 75, 100]:
        values = []
        for family, extra in [('classical', 0), ('classical', 1), ('neural', 0), ('neural', 1)]:
            s = curves['models'][f'{family}/extra{extra}/p{fraction}']['summary']
            values.append(f'{percent(s["top1"])} / {s["bucket_cross_entropy_bits"]:.4f}')
        lines.append(f'| {fraction}% | ' + ' | '.join(values) + ' |')
    lines += ['', '![Accuracy learning curves](figures/learning-curves.png)', '', '[Learning-curve outputs](learning-curves.json), `models.*.summary`, contain OOV rates, strata, seed outcomes and exact training counts. Loss pooling changes as subset vocabularies grow, so these loss values do not by themselves identify a ceiling.', '',
        '| Procedure | 100% minus 75% top-one, points [95% interval] |', '|---|---:|']
    for family in ['classical', 'neural']:
        for extra in [0, 1]:
            e = curves['direct_contrasts'][f'{family}/extra{extra}/100_minus_75']['strata']['all']['metrics']
            lines.append(f'| {name("classical" if family == "classical" else "gru", extra).replace("GRU", "Selected neural")} | {contrast(e, "top1", 100)} |')
    gains = [curves['direct_contrasts'][f'{family}/extra{extra}/100_minus_75']['strata']['all']['metrics']['top1'] for family in ['classical', 'neural'] for extra in [0, 1]]
    lines += ['', f'The 75%-to-100% accuracy increment is positive in {sum(e["difference"] > 0 for e in gains)} of four curves; its interval is entirely above zero in {sum(e["component_bootstrap_95_ci"][0] > 0 for e in gains)}. These final increments directly answer whether performance is still rising under the declared procedure.']
    lines += ['', 'A positive final increment supports acquiring more suitable training data for the tested procedure. Neural training also takes more optimizer steps at larger subsets because the number of epochs stays fixed. The curve therefore combines data size with that training budget. The full benchmark has 205 singleton target types, all unseen in their benchmark-only training folds. They receive zero exact credit under a training-only candidate alphabet. [Frequency strata](aggregate-results.json), `models.classical/extra0/loss.summary.frequency_strata.1`.', '',
        'Configuration comparisons below pool inner losses across the five outer training sets, weighting by their query counts. They compare the declared small and larger configurations before outer evaluation.', '',
        '| Family | Regime | Small parameters | Larger parameters | Small inner bits | Larger inner bits |', '|---|---|---:|---:|---:|---:|']
    loads = audit['correspondence']['fold_token_loads']; weights = [8009 - n for n in loads]
    for family in ['gru', 'transformer']:
        for extra in [0, 1]:
            e = models[f'{family}/extra{extra}/loss']['fold_selection']
            pooled = [sum(weights[f] * e[f]['inner'][j]['bucket_loss_bits'] for f in range(5)) / sum(weights) for j in [0, 1]]
            parameters = []
            for width in [64, 128]:
                group = training['groups'][f'{family}/{width}/extra{extra}/inner']
                parameters.append(f'{group["parameters_min"]:,}–{group["parameters_max"]:,}')
            lines.append(f'| {name(family, 0)} | {"Extra" if extra else "Benchmark"} | {parameters[0]} | {parameters[1]} | {pooled[0]:.6f} | {pooled[1]:.6f} |')
    lines += ['', 'Parameter ranges reflect the inner training vocabularies. The GRU comparison changes width and depth together; both transformer configurations use two layers.']
    capped = sum(e['selected_at_maximum_45'] for k, e in training['groups'].items() if k.startswith('transformer/') and k.endswith('/inner'))
    total = sum(e['fits'] for k, e in training['groups'].items() if k.startswith('transformer/') and k.endswith('/inner'))
    lines += ['', f'Transformer early stopping selects the maximum 45 epochs in {capped} of {total} inner seed fits. That cap leaves longer-training behavior untested. The tested widths and curves support a bounded comparison of these models and data; they do not establish an information-theoretic limit or the best possible neural architecture. [Training diagnostics](training-diagnostics.json), `groups`.', '',
        '## Position, frequency and seed spread', '',
        'The table shows benchmark-only MKN. The aggregate file gives the same fields and paired differences against both comparators for every procedure. Frequency bins use target counts across the whole 8,009-query benchmark.', '',
        '| Stratum | Queries | Top-one % | Top-five % | Top-ten % | Bits | ECE % |', '|---|---:|---:|---:|---:|---:|---:|']
    for key, s in m['strata'].items():
        if key == 'all':
            continue
        lines.append(f'| {key} | {s["slots"]} | {percent(s["top1"])} | {percent(s["top5"])} | {percent(s["top10"])} | {s["bucket_loss_bits"]:.6f} | {percent(s["expected_calibration_error"])} |')
    lines += ['', '| Neural procedure | Seed top-one range, % | Seed loss range, bits |', '|---|---:|---:|']
    for extra in [0, 1]:
        for family in ['gru', 'transformer', 'metadata']:
            e = models[f'{family}/extra{extra}/loss']['seed_range']
            lines.append(f'| {name(family, extra)} | {percent(e["top1"][0])}–{percent(e["top1"][1])} | {e["bucket_cross_entropy_bits"][0]:.6f}–{e["bucket_cross_entropy_bits"][1]:.6f} |')
    lines += ['', 'The main neural scores average probabilities; the seed range reports individual fitted seeds. Neither range refits vocabulary, fold construction or configuration selection.', '',
        '## Secondary accuracy selection', '',
        '| Procedure | Loss-selected top-one % / bits | Top-one-selected top-one % / bits |', '|---|---:|---:|']
    for extra in [0, 1]:
        for family in ['classical', 'gru', 'transformer', 'metadata', 'ensemble']:
            s = models[f'{family}/extra{extra}/loss']['summary']; t = models[f'{family}/extra{extra}/top1']['summary']
            lines.append(f'| {name(family, extra)} | {percent(s["top1"])} / {s["bucket_cross_entropy_bits"]:.6f} | {percent(t["top1"])} / {t["bucket_cross_entropy_bits"]:.6f} |')
    lines += ['', 'Secondary selection changes the configuration or ensemble weight using inner accuracy; neural epoch selection remains loss-based. [Secondary outputs](aggregate-results.json), `models.<family>/extra<0|1>/top1` and `fold_selection`.', '',
        '## Verification, precedents and the carry-forward model', '',
        f'The scalar review reconstructs all stored classical probabilities in {len(verification["classical"])} distinct outer configurations, with brute-force complete-sequence checks on sampled corpus queries. It reproduces {len(verification["neural"])} neural seed checkpoints and checks hidden-query inputs throughout the test population. Independent multiplication and normalization reconstruct {len(verification["ensemble"])} ensemble arrays, including the repaired disk-interruption output. Toy cases cover every n-gram order, all boundary positions, continuation counts, normalization and neural padding. [Verification](verification.json), `classical`, `neural`, `ensemble` and `self_tests`. External review remains pending.', '',
        'The literature comparisons are in [RELATED-WORK.md](RELATED-WORK.md). Yadav’s 74% is 90%-mass candidate coverage; Venkatesh and Farghaly’s 63% is top-ten; Tiwari’s 2.60 is next-token perplexity. Ithaca and Aeneas restore spans in known languages, while the Linear B study tests a small recurrent model and finds negative transfer in its synthetic-gap assay. Their outcome definitions prevent a direct cross-paper ranking.', '',
        f'The single frozen carry-forward recipe is `{frozen["chosen"]["family"]}`, extra text `{frozen["chosen"]["extra"]}`, selected from pooled inner loss {frozen["chosen"]["pooled_inner_bits"]:.6f} bits. Modal configurations and median selected epochs determine its full-data fit. The manifest records {frozen["training_texts"]} training texts and {frozen["training_tokens"]} tokens, hashes, counts/weights and seeds. The adaptive outer procedure’s score is separate from this final full-data recipe. [Frozen record](frozen-model/manifest.json), `chosen`, `recipe`, `files`; [training identities](frozen-model/training-register.json). Future targets must be acquired and screened before testing it without retuning.', '',
        f'The frozen loader verifies all payload and fitting-code hashes. Its sample of {frozen_check["sample_strings"]} strings covers {frozen_check["sample_slots"]} masks. Fixed-batch hidden replacement leaves every sampled probability exactly unchanged. Changing batch size produces a maximum rounding difference of {frozen_check["maximum_batch_probability_change"]:.3g}. The first mixed-batch record remains preserved. [Refined verification](frozen-inference-v2-verification.json), [dated verification amendment](VERIFICATION-AMENDMENT-2026-10-07.md).', '',
        'Counts, weights, query predictions, source downloads and extracted source text stay in the assigned local raw directory. Rights for the derivative corpus remain unresolved. Source identity, access failures and the successful Aeneas author-PDF route are in [sources.json](sources.json).']
    write('REPORT.md', '\n'.join(lines))
    write('README.md', f'''# Modern restoration benchmark comparison

Status: Exploratory. Completed 7 October 2026 from a protocol written on 6 October before fitting.

Modified Kneser–Ney restores {percent(m["top1"])}% of 8,009 known slots with {m["bucket_cross_entropy_bits"]:.6f} bucket bits, compared with 34.5861% / 5.119435 bits for first order and 37.2706% / 5.247171 bits for second order. The highest primary top-one is {percent(a["top1"])}% (`{best_accuracy}`); the lowest native loss is {l["bucket_cross_entropy_bits"]:.6f} bits (`{best_loss}`). [Results and paired intervals](aggregate-results.json), `models`; [report](REPORT.md).

All saved masks, targets, artifacts, groups and folds match. Extra text adds 501–506 distinct strings and 1,419–1,427 tokens per fold after complete transitive exclusion. The wider export also links 144–159 existing benchmark training strings per fold to test strings; the original matched folds remain fixed. [Benchmark audit](benchmark-audit.json), [extra graph audit](extra-graph-audit.json).

The completed stages cover orders 2–5, two GRU configurations, two transformer configurations, three neural seeds, joint metadata conditioning, both text regimes, log-probability ensembles, secondary accuracy selection and 25/50/75/100% learning curves. [Curve results](learning-curves.json), [accuracy figure](figures/learning-curves.svg), [training diagnostics](training-diagnostics.json), [internal verification](verification.json). [Frozen carry-forward recipe](frozen-model/manifest.json), selected using inner outcomes, retains local counts/weights for a future fresh population. Its [refined loader checks](frozen-inference-v2-verification.json) verify fixed-batch hidden replacement; the [dated amendment](VERIFICATION-AMENDMENT-2026-10-07.md) records the first mixed-batch comparison.

## Reproduce from the repository root

The original normalized corpora and saved query audits must be present locally. Model fitting used Python 3.13.5, NumPy 2.5.3 and CUDA PyTorch 2.14.1+cu126 in the provided RTX 4070 environment. Plotting dependencies were added to the same environment. Pypdf from the system Python is needed only to repeat literature extraction. [Fitting environment](environment.json).

```powershell
$modernPython = 'C:/Users/sandh/.venvs/indus-ml/Scripts/python.exe'
& $modernPython -B experiments/2026-10-06-modern-restoration/run_all.py --run reviewer-2026-10-07
```

Choose a new run label. Fits can resume completed stage records; completed aggregate endpoints refuse replacement. `run_all.py` repeats all fitting, selection, curves, summaries and mathematical checks. It preserves the existing carry-forward model unless explicitly invoked with `--freeze`, which refuses an existing frozen record. The one-off `finish_when_ready.py` only continued this active run; no recurring automation exists.

To review existing predictions without retraining:

```powershell
& $modernPython -B experiments/2026-10-06-modern-restoration/data.py --output experiments/2026-10-06-modern-restoration/reviewer-benchmark-audit.json
& $modernPython -B experiments/2026-10-06-modern-restoration/audit_extra.py --output reviewer-extra-graph-audit.json --witness-name reviewer-extra-graph-witnesses.json
& $modernPython -B experiments/2026-10-06-modern-restoration/verify.py --run main --output reviewer-verification.json
& $modernPython -B experiments/2026-10-06-modern-restoration/summarize.py --run main --output reviewer-aggregate-results.json
& $modernPython -B experiments/2026-10-06-modern-restoration/summarize.py --run main --curves --output reviewer-learning-curves.json
& $modernPython -B experiments/2026-10-06-modern-restoration/verify_frozen.py --prefix reviewer-frozen-inference
& $modernPython -B experiments/2026-10-06-modern-restoration/inventory.py --verify
python -X utf8 -B tools/review_prose.py --path experiments/2026-10-06-modern-restoration --no-write
```

Inner count-of-count grids and training histories are under `main/`; raw probability matrices, per-query audits and weights are under `data/raw/2026-10-06-modern-restoration/main/`. Individual inner-seed arrays were removed after their complete means and seed records were audited, freeing 2,039,403,915 bytes. All outer predictions and checkpoints remain. There are three inner folds per outer fold. [Protocol](PROTOCOL.md), [dated auxiliary-loss amendment](AMENDMENT-2026-10-07.md), [disk recovery](RECOVERY-2026-10-07.md), [precedents](RELATED-WORK.md), [source access record](sources.json), [retrospective](RETROSPECTIVE.md), [proposed registry entry](registry-entry.json), and [complete path/hash inventory](file-manifest.json) provide the research record.

The accuracy figure uses Matplotlib 3.11.2, installed with `pip --no-cache-dir` in the authorized CUDA environment. Its added dependencies are pinned in [plot-requirements.txt](plot-requirements.txt), recorded in the local installation log and included in the path inventory. Re-render it with `& $modernPython -B experiments/2026-10-06-modern-restoration/plot_curves.py --prefix reviewer-learning-curves`.

The 45-epoch transformer cap, source transcription quality, full-register dependency links and future-population performance remain limitations. Published restoration percentages use different candidate-set and span definitions; see the source comparisons before ranking them against this benchmark.
''')
    write('RETROSPECTIVE.md', f'''# Work record for modern restoration

The package reconstructed the exact saved restoration population before fitting. It reused `load_records`, `group_records`, `make_folds`, `verify_saved` and reporting helpers from `src/six_hour/markov_baseline.py`, the alias-preserving loader in `src/methods/conditional_structure.py`, and the saved first-order and second-order audits. All 8,009 masks, 1,596 strings and 1,526 components matched. The registry’s loss-selected and adaptive Markov failures were retained as prior evidence; modified Kneser–Ney continuation smoothing and the neural models supplied different estimators.

The pre-fit protocol fixed orders, discount scales, neural widths/depths, dropout, optimizer, epoch cap, seeds, inner folds and primary loss selection. Candidate-dependent n-gram factors were evaluated with wildcard context indexes to avoid enumerating full strings during fitting. A separately counted scalar recursion checked full-string likelihoods. GRUs used packed sequences so right padding could not change backward context. Transformer padding masks and hidden-target replacement passed toy tests before the corpus fits. Original fitting-source snapshots remain under `main/code-snapshots/`.

The complete observed export required a wider object/string graph than the saved benchmark. Breadth-first traversal reproduced the fit exclusions and found zero extra-face violations. It also exposed links between existing benchmark components through outside faces. The original benchmark folds stayed fixed, as required by the package. The report carries the 144–159 connected benchmark training strings per fold beside the matched comparison. Added distinct strings numbered 501–506 per fold and added 1,419–1,427 tokens. Multi-line and other-direction faces retained the export’s reading order, with its line-continuity limitation.

Ordinary bucket loss changed its target events when extra text introduced fine codes. A dated amendment added a common-alphabet calculation, preserving primary native loss selection. Curve subsets can still pool missing vocabulary more coarsely; their accuracy and OOV rates carry the data-size interpretation. No hyperparameter grid or training limit changed after the outcomes.

MKN’s benchmark-only accuracy was {percent(m["top1"])}% and loss was {m["bucket_cross_entropy_bits"]:.6f} bits. The best primary accuracy was {percent(a["top1"])}% and lowest native loss {l["bucket_cross_entropy_bits"]:.6f} bits. Metadata, added text, seeds, secondary selection and learning curves all retain their complete aggregates in the report and JSON outputs. Transformer fits often selected the epoch cap, leaving longer training untested. The final carry-forward recipe was selected from inner losses and trained on the available full population; its payloads remain local and hashed.

Source retrieval found a distinction hidden by short abstracts. Yadav’s 74% is 90%-mass candidate coverage and Venkatesh and Farghaly’s 63% is top-ten coverage. Opened methods and exact source locations were recorded. Aeneas’ direct publisher PDF route returned HTML; the Warwick author PDF supplied the text. The direct Ithaca download returned a reCAPTCHA page despite HTTP 200, while the web reader exposed the full article. The source manifest distinguishes transport success from article access. A repeated PDF extraction refused existing outputs, and a cp1252 console could not print one Unicode excerpt; using `-X utf8` corrected the read without changing witnesses.

The computer's shared disk filled during the extra-text ensemble write and interrupted the first continuation. The recovery audited all saved JSON, JSONL and probability/checkpoint archives, preserved the one incomplete 13,353-byte array and rebuilt it from completed constituents. It removed 450 unneeded individual inner-seed arrays after confirming their complete means and seed records, freeing 2,039,403,915 bytes. Outer predictions, checkpoints and all fit histories remained intact. No fitting rule changed and no completed selection was repeated. The cleanup record's UTF-8 byte-order mark was removed after preserving its original bytes. [Recovery record](RECOVERY-2026-10-07.md), [interruption audit](interruption-audit.json) and [deleted-path record](storage-cleanup.json) document the interruption and repairs.

All declared model cells completed inside the assigned directories. The long neural shell session reported exit status 1 after its final selection line, with all 20 unconditioned selection records present and no Python traceback. A cached completion pass with explicit native exit propagation returned zero and repeated no fits. The original shell discrepancy remains unexplained. [Completion audit](run-completion-audit.json) preserves the observation. Internal scalar, probability, checkpoint and correspondence checks passed; external reviewer checks and a fresh source-reviewed population remain open. The full path/hash inventory records local predictions and source witnesses alongside tracked code, protocols and aggregates. Plotting dependencies were installed in the explicitly authorized CUDA environment.
''')
    registry = {'id': 'MODERN-RESTORATION-20261006', 'theme': 'modern-restoration-and-data-size', 'status': 'Exploratory',
        'question': 'Do modified Kneser–Ney, masked recurrent/transformer models, metadata and outside-population text improve the saved Paper 001 known-slot benchmark, and do learning curves show remaining data gains?',
        'outcome': f'MKN without extra: {percent(m["top1"])}% top-one, {m["bucket_cross_entropy_bits"]:.6f} bits on 8,009 identical queries. Highest primary accuracy: {percent(a["top1"])}% ({best_accuracy}); lowest native loss: {l["bucket_cross_entropy_bits"]:.6f} bits ({best_loss}). Complete paired strata, seeds and curves retained.',
        'challenge': 'Reused masks; additional vocabulary changes bucket events; wider export connects existing benchmark components; transformer epoch cap leaves longer training untested.',
        'remedy': 'Pre-fit nested component selection, exact correspondence, complete extra-face closure, common-alphabet loss amendment, scalar complete-chain and neural checkpoint checks, and one hashed carry-forward recipe.',
        'evidence': ['experiments/2026-10-06-modern-restoration/' + p for p in ['PROTOCOL.md', 'REPORT.md', 'aggregate-results.json', 'learning-curves.json', 'extra-graph-audit.json', 'verification.json', 'frozen-model/manifest.json', 'RETROSPECTIVE.md']],
        'retry_when': 'A newly acquired source-reviewed population can test the frozen recipe without retuning; any longer-training or different neural family needs a new exploratory protocol and fresh endpoints.'}
    write('registry-entry.json', json.dumps(registry, indent=2))
    write('frozen-model/README.md', f'''# Frozen carry-forward recipe

The record chooses `{frozen["chosen"]["family"]}` with extra text `{frozen["chosen"]["extra"]}` using pooled inner loss. Its full-data fit is recorded separately from the adaptive outer procedure’s evaluation score. Configuration, epochs, seeds and code/input/payload hashes are in [manifest.json](manifest.json). Imported repository helpers and the loader interface are pinned in [code-dependencies.json](code-dependencies.json). Corpus-derived counts, weights and training identities remain local-only. [Training register](training-register.json) supplies the future contamination screen.

`inference.py` loads the hashes and predicts every known slot without tuning. Its JSONL input has `seq` arrays of string graphic codes, preserving their leading zeros, and optional `object_type`, `site`, `region` and `symbol` fields. Output must be a fresh path inside the assigned local raw directory. A hidden target is overwritten by the model’s MASK or enumerated candidate; its placeholder does not affect that slot’s prediction.

```powershell
& C:/Users/sandh/.venvs/indus-ml/Scripts/python.exe -B experiments/2026-10-06-modern-restoration/inference.py --input data/raw/2026-10-06-modern-restoration/fresh-input.jsonl --output data/raw/2026-10-06-modern-restoration/fresh-predictions.jsonl
```

Future evaluation must obtain a fresh source-reviewed population, screen its object and string connections against the training register and broader source graph, freeze its query law before scoring, and keep this recipe unchanged. Naturally damaged gaps also need an independently supported missing-slot count.
''')

if __name__ == '__main__':
    main()
