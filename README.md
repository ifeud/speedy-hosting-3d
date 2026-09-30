# Speedy Hosting

## Version 4: independent voxel-inspired web design

The UI has been completely recoded with a full-width original environment hero, square green web buttons, bold non-pixel typography, light/dark block sections, and Speedy's own brand. This is a broad Minecraft.net-inspired website direction, not a pixel-for-pixel clone or an imitation of Minecraft's in-game menus.

**`index.html` is the complete standalone website.** Artwork, fonts, icons, styles, JavaScript and the contained 3D hardware demo are embedded. Open it directly in a modern browser. No external runtime assets are requested.

## Original visuals and IP precautions

* Seven original AI-generated voxel environments replace every publisher image.
* No Minecraft, other game publisher or third-party product logo is used as Speedy branding.
* No proprietary Minecraft fonts, textures, UI graphics or intentional recognizable game characters are used.
* Archivo Black, Noto Sans and IBM Plex Mono are openly licensed fonts; full licenses are included.
* The wordmark, cursor vectors and 3D hardware geometry are authored for Speedy.
* Game names identify supported software descriptively. They do not name or brand the hosting company.
* A prominent non-affiliation notice is included at the top of the page and in the footer.

**These precautions are not a guarantee against a lawsuit or a legal clearance opinion.** AI generation does not guarantee non-infringement. Before commercial publication, review visual resemblance, trademark usage, actual operator identity/contact details, applicable publisher rules and local laws with qualified counsel. See `LEGAL_LAUNCH_CHECKLIST.md`.

## Website features

* Responsive navigation and mobile game menu
* Search and filters for six supported games
* Example monthly and annual plans, with clear billing disclosures
* Game-aware RAM requirements and local quote downloads
* Interactive Console, Files and Backups demonstration
* Keyboard, pointer and touch controls for the original 3D hardware view
* Region selection without invented live latency numbers
* FAQ, local support draft, client preview and legal dialogs
* Transparent 24 px arrow, hand, text and drag cursors with native fallbacks
* Reduced-motion and keyboard support
* SEO title, description, canonical, Open Graph, Twitter and JSON-LD metadata

Accounts, payments, support sending and server provisioning are not connected. The site is a frontend concept, not an operational hosting company.

## Project structure

```text
index.html                     Complete standalone website
public/
  index.html                   Prebuilt Vercel deliverable
  speedy-logo.svg              Transparent light wordmark
  speedy-logo-dark.svg         Transparent dark wordmark
  social-preview.jpg          Optional social-sharing asset
assets/
  v4/                          Seven original source illustrations, optimized art,
                               original vector fallback and artwork manifest
  cursors/                     Editable SVG and transparent PNG cursors
  icons/                       Phosphor SVG icons and MIT license
  *.woff2                     Embedded open-license fonts
  *-OFL.txt                   Full font licenses
  *-card.webp                  Optimized original catalog illustrations
  world.geojson                Public-domain geography
  v2/scene.min.js               Renderer bundle, retained filename for compatibility
  v2/three-LICENSE.txt          Three.js license
tools/
  site.html                    HTML template
  site.css                     New version 4 visual system
  site.js                      Website interactions
  scene.js                     Original 3D sculpture, controls and fallback logic
  build.py                     Single-file asset assembly
  cursors.py                   Cursor generation
  prepare-vercel.mjs           Production SEO origin injection
  qa.py                        Automated markup, art, font, cursor and interaction tests
```

Historical versions and reference materials are not included in the current source ZIP or deployed public folder.

## Rebuild

Requires Node.js 20.19+ and Python 3.11+.

```sh
npm ci
python -m pip install -r requirements.txt
python tools/cursors.py
npm run build
```

All required artwork and font files are already in the source package. Rebuilding does not download game artwork.

Preview:

```sh
npm run preview
```

Use `http://localhost:3000` on your own computer, or the supplied preview URL in a remote workspace.

## Verification

```sh
python -m pip install playwright beautifulsoup4
python -m playwright install chromium
python tools/qa.py
```

The current suite passed 199 checks across nine viewport widths from 320 to 1440 px, including original-art records, resource embedding, fonts, cursor transparency/hotspots, navigation, quotes, downloads, panel controls, 3D interaction, dialogs and full-page rendering. No JavaScript page errors, external runtime asset requests or horizontal page overflow were detected.

## Publishing

The private source repository and a publicly accessible Vercel website are separate things. Vercel deployment was previously declined by the user; it is not performed by opening or rebuilding the HTML.

To publish manually, push the source and prebuilt `public` folder to your private repository and import it into Vercel with framework **Other**. Keep `vercel.json`; it runs the built-in Node publishing step without dependency installation. `SITE_URL`, `VERCEL_PROJECT_PRODUCTION_URL` or `VERCEL_URL` supplies the production SEO origin.

The HTML uses `https://speedyhosting.example` until a real origin is supplied. The optional social-preview image must be available at its public metadata URL. Verify business details and connect secure production backends before launch.

Do not put credentials in source, HTML, screenshots, chat or the repository. Environment and local authentication files are ignored by Git.

## Licenses

* Archivo Black, Noto Sans and IBM Plex Mono: SIL Open Font Licenses included.
* Three.js and Phosphor Icons: MIT licenses included.
* Natural Earth geography: public domain.
* Original illustrations: AI-generated for this project, not official game assets. Legal clearance is not guaranteed.
