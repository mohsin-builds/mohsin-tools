# Mohsin Tools — Concept C release candidate v0.6

This is the approved **Concept C — Modern Creative** visual direction, implemented as an independent static site for the existing Cloudflare Pages project `mohsin-tools-app` at `tools.mohsinlabs.com`.

## Visual specification
- Brand: Mohsin Tools by Mohsin Labs
- Typeface: Manrope (with system fallbacks), matching the Satoshi / Manrope / Inter family referenced by Concept C
- Canvas: mostly white with violet, magenta and sky-blue gradient accents
- Hero: left-aligned “Turn images into progress.” headline, two CTAs, decorative angled mountain-preview device with floating action chips
- Four-item utility benefit strip, three pastel tool cards, large lavender benefits panel and minimal footer
- Consistent matching headers, tool-page controls and privacy page

The illustration inside the tilted device is a locally stored SVG alpine illustration. This maintains the concept's composition without depending on an externally hosted image or embedding a low-resolution piece of the concept screenshot.

## Existing features preserved
1. Image compressor with user-specified KB ceiling and honest failure message when the target cannot be met.
2. Photo and signature resizer with exact-size export, high-resolution signature master, lossless PNG option and zoom inspector.
3. Local JPG, PNG and WebP converter.

## Run checks
```bash
node scripts/build.mjs
node tests/unit.mjs
python tests/static_check.py
python tests/browser_offline.py
```
Browser-offline tests exercise actual Canvas output and downloads, not the production HTTP module-loading path.

## Deploy (requires Cloudflare dashboard access)
Open the **existing** `mohsin-tools-app` Cloudflare Pages project, select **Create deployment**, select Production and upload the Cloudflare ZIP containing the prebuilt root assets. Do **not** create a new project or change DNS. Check `/`, the three `/tools/*.html` pages and `/privacy.html` after deployment, preferably in Incognito.

## Privacy & dependencies
Browser files are processed in-device. Manrope is optionally loaded from Google Fonts (with local system fallbacks) and may make a font request. No account, server-side image processing, database, paid API, or tracker is required.