# Validation

Checked on 22 October 2026 with Chromium through Playwright CLI.

- All 24 slides were captured at a 1440 × 958 viewport and visually inspected. The final version has no detected horizontal overflow or body content colliding with a footer.
- All 24 slides fit a 390-pixel mobile viewport without horizontal overflow. Representative mobile captures were inspected. Longer slides scroll vertically, with navigation fixed at the bottom.
- Previous, Home, right-arrow navigation and Overview selection reached their expected slide numbers.
- Print media exposes all 24 slides at 1440 × 900 CSS pixels. The generated print-check PDF contains 24 pages, confirmed with pypdf.
- All five images are embedded data URLs. There are no external scripts, styles or fonts. The 21 distinct local source links resolve to existing files; nine external literature links reproduce the sources used in the prior audit.
- Python compilation of the builder passed. The browser initially requested a missing favicon; the final HTML supplies an empty inline favicon.

The machine-readable results are in `browser-check.json`, `link-check.json` and `MANIFEST.json`. Screenshots and the print-check PDF remain local in `output/playwright/indus-deck/` because they reproduce catalogue photographs.

This check verifies the presentation and its links. It does not independently reproduce the research or adjudicate the archaeological readings. Those qualifications are recorded beside the relevant results and in the linked source reports.
