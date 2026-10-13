# Website generator

The website presents the repository's research record. Git selects the source files. Python 3.13, Markdown 3.8.2 and Jinja2 3.1.6 build the pages. Templates use `.jinja` so the repository's downloaded-HTML exclusion does not hide them.

Run these commands from the repository root:

```text
python tools/build_site.py --out _site
python tools/build_site.py --worktree --out _site
python tools/build_site.py --check _site
```

Use an empty output directory or a previous build directory. A build reads HEAD by default. `--worktree` reads files selected by `git ls-files --cached --others --exclude-standard` for a preview. The preview label identifies that mode; its source links still name HEAD. The check reports how many preview targets are absent at that commit. Commit the source before publishing so those links resolve on GitHub. All generated HTML belongs in the ignored output directory or on gh-pages. The generator adds no workflow.

The data directory and public omissions are excluded. The requested manifest table is the sole read exception: `data/MANIFEST.json` must be tracked, and its source file is never copied. Explore image assets must be tracked even in a preview. Missing document links become text labelled "not in the public repository". External hyperlinks remain usable; pages load local resources.

Start a local HTTP server to use search and filters:

```text
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. Pages also contain their full lists without JavaScript. Explore supplies tables of the viewers' embedded rows when JavaScript is disabled. `site-build.json` records the source commit, inputs, copied assets, omitted links and unavailable pages. `--check` checks these records, page links, assets, pinned repository links and external resource references. It reports size and the largest files.

After reviewing and committing the source files, publish to the local branch:

```text
python tools/build_site.py --publish
```

This command builds and checks HEAD, writes a new gh-pages commit with Git plumbing, and updates that local branch. It preserves the current branch, index and working tree. A later invocation uses the existing gh-pages commit as its parent. Commit metadata uses the source commit's date. It does not push. The coordinator handles the push and GitHub Pages settings after reviewing the result.

The base URL is `https://k-sandhu.github.io/indus-valley-script/`. Page links are relative; the sitemap and llms.txt use absolute public URLs. The build output is deterministic for a fixed source commit and pinned dependencies.
