# Project website generator: instructions for GPT-6.1-Sol

You are building the generator for the project's public website, to be served by GitHub Pages from a `gh-pages` branch at `https://k-sandhu.github.io/indus-valley-script/`. The repository root is `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows; Python 3.13 as `python` with the `markdown` 3.x and `jinja2` packages installed; Git Bash and PowerShell available). Today is 13 October 2026. A coordinating Claude session wrote these instructions, will review your work, and will publish the site itself. You build and test; you do not publish.

The owner chose this design: the repository is the single source of truth, the site is a read-only presentation generated from it, no CI/CD workflow is added, and generated HTML lives only on the `gh-pages` branch, never on `main`.

## 1. Read first

`AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `REUSE.md`, `llms.txt`, `knowledge/MAP.md`, `knowledge/WORKING-MODEL.md`, `knowledge/DATA.md`, `knowledge/TIMELINE.md`, `knowledge/registry/VOCABULARY.md`, the templates in `templates/` and `knowledge/conjectures/TEMPLATE.md`, a sample of cards in `knowledge/findings/`, `knowledge/questions/` and `knowledge/conjectures/`, `tools/kb.py` (reuse its frontmatter parser and item index by importing it rather than reimplementing), `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, `experiments/2026-10-11-public-release/public-omissions.json`, the self-contained pages `experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html` and `output/chart_atlas/index.html` with their asset folders, and `.github/ISSUE_TEMPLATE/`.

## 2. Hard rules

1. **Publish only what Git already publishes.** The generator reads repository files only through Git: by default the files at `HEAD` (`git ls-tree -r HEAD` and `git show HEAD:<path>`), and with `--worktree` the files listed by `git ls-files --cached --others --exclude-standard`, for local previews before a commit. It never reads `data/`, any path in `public-omissions.json`, or any ignored file. A missing or excluded link target becomes plain text marked "not in the public repository".
2. **Edit only your paths** (section 6). Other contributors are editing cards, the working model, the registry and experiment packages while you work; read them, never write them. Do not run `git commit` on `main`, `git push`, `git checkout`, `git reset`, `git stash` or `git clean`, and do not change repository settings or enable Pages.
3. **No workflows, no external requests from the site.** Do not add `.github/workflows`. The pages load no external fonts, scripts, analytics or CDNs; everything is local to the site.
4. **Deterministic output.** The same commit gives byte-identical output. The only build-specific values are the source commit hash and its commit date.

## 3. What the site contains

Base path `/indus-valley-script/`; all internal links relative so a local preview works.

- **Home**: the README's statement of purpose, "Where things stand" (rendered from the README section), the working model's headline claims with credences, the conjecture table with status badges, the counts of findings, open questions and registry attempts, the bootstrap line for agents, and links to Contribute and Data.
- **Findings**: an index grouped by area with status-class badges, and one page per card.
- **Working model**: `knowledge/WORKING-MODEL.md` rendered.
- **Conjectures**: an index (ID, claim, status, credence, risk, area) and one page per card, with the credence history shown as a small table.
- **Open questions**: a board filterable in the browser by area, kind, difficulty, data access and priority, showing status and claim fields; each question page has a "Claim or discuss on GitHub" link that opens the repository's claim issue form with the Q-ID prefilled in the title (build the URL from the form's file name and the `title` query parameter).
- **Registry**: a searchable table of all attempts (ID, area, status class, question, outcome), each linking to its package on GitHub.
- **Data**: `knowledge/DATA.md` rendered, plus a table generated from `data/MANIFEST.json` if it is tracked.
- **Timeline**: `knowledge/TIMELINE.md` rendered.
- **Papers**: one page per `papers/*/manuscript.md`, with links to methods and evidence maps and to tracked PDFs in `output/pdf/`.
- **Explore**: copies of the self-contained sign catalogue and the chart atlas with every asset they reference, after checking that each asset is tracked; their internal relative paths must keep working.
- **Contribute**: `CONTRIBUTING.md` rendered, the agent bootstrap line, the skills list, and links to issues and Discussions (`https://github.com/k-sandhu/indus-valley-script/discussions`).
- **Reuse**: `REUSE.md` and `THIRD_PARTY_NOTICES.md` rendered; state that no project-wide licence has been chosen, exactly as `REUSE.md` says.
- **Site root files**: `llms.txt` (the repository's `llms.txt` with links rewritten to absolute site URLs, plus links to the JSON indexes), `index.json` files for findings, questions, conjectures and attempts (machine-readable, for agents), `sitemap.xml`, `404.html`, `.nojekyll`.

Every rendered page carries a "Source on GitHub" link to the blob at the build commit. Markdown links between rendered files point to their site pages; links to any other repository file point to `https://github.com/k-sandhu/indus-valley-script/blob/<commit>/<path>` (or `tree/` for directories); links that already point outside the repository are kept.

## 4. Design

- **Readability:** one stylesheet with a readable line length, clear headings, accessible contrast, mobile layout, `lang="en"`, alt text for every image, keyboard-usable filters. Status badges use text labels as well as colour.
- **Scripting:** search and filtering in a single small vanilla JavaScript file over the JSON indexes; pages remain readable without JavaScript.
- **Templates:** Jinja2 templates in `site/templates/`, static files in `site/static/`.
- **Site prose:** headings and short labels only. Do not write new descriptions of findings; the content comes from the repository files.
- **Size:** the built site well under GitHub Pages' 1 GB limit; report its size and its largest files.

## 5. Commands

- `python tools/build_site.py --out _site` builds from `HEAD`.
- `python tools/build_site.py --worktree --out _site` builds a local preview from tracked plus untracked, non-ignored files.
- `python tools/build_site.py --check _site` verifies the built site: every internal link and asset resolves, every GitHub link uses the build commit and points to a tracked path, no file under `data/` or in the omissions list was copied, no page loads an external resource.
- `python tools/build_site.py --publish` builds from `HEAD` and writes the result as a new commit on the local `gh-pages` branch using Git plumbing (`hash-object`, `mktree`, `commit-tree`, `update-ref`) or a temporary worktree outside the repository directory, without touching `main`'s index or working tree. The commit message names the source commit. It does not push. Test it against a throwaway clone of the repository in a temporary directory, not in the real repository.

## 6. Paths you own

- `tools/build_site.py`
- `site/**` (templates, static files, `site/README.md` explaining how to build, check and publish, and `site/requirements.txt` with the exact `markdown` and `jinja2` versions)
- `experiments/2026-10-13-site-generator/**` (your record; this prompt file stays unchanged): `PLAN.md` written first, `CHANGES.json`, test outputs, `RETROSPECTIVE.md`
- `.gitignore`: add exactly one line, `/_site/`, and nothing else

## 7. Verification

Save in `experiments/2026-10-13-site-generator/`: the outputs of a `--worktree` build and its `--check`, a second build showing byte-identical output, the publish test against the throwaway clone, a page list with sizes, and a screenshot-free accessibility checklist (lang, alt text, heading order, contrast values of the badge colours). Run `python tools/review_prose.py --path site --no-write` and `python tools/review_prose.py --path experiments/2026-10-13-site-generator --no-write`.

## 8. Writing

Follow `knowledge/editorial/WRITING.md`. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Labels and headings are short and literal.

## 9. Final message

End with: every path created or modified; the build, check and publish-test results; the site size and page count; anything that could not be rendered or copied and why; and what the coordinator should check before publishing.
