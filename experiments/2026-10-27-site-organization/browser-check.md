# Browser check

We served the preview with `python -m http.server` on a loopback port and used Chromium 151.0.7922.34 through the installed Python Playwright package. No browser or package was downloaded.

69 checks pass. Home, Findings, Registry and Explore loaded at 1280 × 900 and 375 × 900. We checked document width, navigation disclosures, current-section markup, skip links, recent-work count, search, reset, combined theme and status filters, hidden empty groups and registry date order. A separate context with JavaScript disabled retained the full lists and followed Home → Findings → a finding card in two links.

Screenshots are local-only at `_site/site-preview-final-shots`. [Exact results](browser-results.json) record each check. The browser made no off-machine resource requests; server and browser processes were stopped. Visual inspection covers page tops, recent work, themed findings, a registry date section, an open mobile navigation group and a finding card; table content scrolls within its own container at phone width.
