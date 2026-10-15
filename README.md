# Mohsin Tools — v1.0 (26 free browser tools)

A standalone, privacy-conscious collection of free, browser-based image, PDF, text, developer and everyday utilities. Built by Mohsin Labs and hosted independently on Cloudflare Pages.

**Public product:** https://tools.mohsinlabs.com/

## Product architecture

- **Independent repository:** `mohsin-builds/mohsin-tools`, separate from Mohsin Labs OS.
- **Static frontend:** HTML, CSS, JavaScript, Canvas, File and Crypto APIs.
- **Hosting:** Existing Cloudflare Pages project `mohsin-tools-app` (manual ZIP upload).
- **Data:** Selected image and text files are processed locally; Cloudflare Web Analytics observes page usage, not user-selected image contents.
- **Design:** User-approved Concept C — light neutral canvas and restrained purple/blue gradient accents.

## Tools

The directory has 26 dedicated pages grouped into Image & PDF (10), Text & Writing (6), Developer (6), and Everyday (4). The three original image processing tools remain intact.

## SEO and accessibility

- Dedicated pages with unique, descriptive `<title>`, meta descriptions and H1 headings.
- Tool-specific usage instructions, practical examples and realistic limitations rather than generic repeated copy.
- Canonical URLs on `tools.mohsinlabs.com`; robots.txt and sitemap.xml for discovery.
- JSON-LD for WebSite/ItemList on the homepage and WebApplication/BreadcrumbList on utility pages, with truthful `price: 0` and no fabricated review data.
- Crawlable links and related-tool navigation, with semantic content in the initial HTML.
- Static optimized social preview asset; no backend SEO or indexing API required.

These changes improve crawlability and explain the product, but **do not guarantee rankings or indexing**. Google Search Console domain verification and sitemap submission must be completed from the authorized Google account.

## Local checks

```bash
node tests/unit.mjs
node tests/directory.mjs
node tests/seo.mjs
node scripts/build.mjs
python3 tests/static_check.py
```

Optional offline Chromium suite: `python3 tests/browser_v1_offline.py` (requires Chromium, Playwright, PIL and PyMuPDF). Full deployed HTTP and SSL checks must be performed on production after release.

## Deploy

Upload the prepared **Cloudflare production ZIP** as a new deployment to the existing `mohsin-tools-app` Pages project. Do not change DNS or create a second project. Browser-check several real tools, the sitemap, and Web Analytics after deployment.

## Limitations

Some tools depend on modern browser support. A 200-pixel signature cannot retain limitless zoom detail; PDF output from selected images does not include OCR. UUID v4 requires a secure browsing context (HTTPS). Follow receiving websites' actual size and format requirements before submitting generated files.