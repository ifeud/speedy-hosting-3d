# Speedy Hosting

An original game-hosting website concept with a real interactive 3D server sculpture, seven original environment and hardware illustrations, and transparent custom cursors.

## Open the website

**`index.html` is the entire website.** Open it directly in a modern browser. Styling, variable fonts, Phosphor SVG icons, optimized artwork, custom cursors, JavaScript, and the Three.js renderer are embedded. No CDN or external runtime requests are needed.

The optional `social-preview.jpg` must be hosted publicly for social-sharing crawlers. It is not needed to display the page.

## What changed in version 2

* A true WebGL hero sculpture with pointer, touch, and keyboard rotation, rather than floating status cards.
* No floating green badges or pills. No double-hyphen punctuation in visible copy.
* Six original game-world illustrations and one original industrial hardware illustration.
* Four original transparent cursor designs: arrow, hand, text selection, and multidirectional drag. Native fallbacks are included.
* Restrained depth interactions, editorial typography, and a charcoal, cream, and orange palette.
* Reduced-motion support, keyboard controls, responsive navigation, and an artwork fallback when WebGL is unavailable.
* Existing game filters, plan configurator, billing toggle, example quotes, control-panel demo, FAQs, and local support drafts remain functional.

## Project structure

```text
index.html                    Standalone deliverable
public/
  index.html                  Identical prebuilt Vercel page
  speedy-logo.svg             Transparent vector wordmark
  social-preview.jpg          Social-sharing preview
assets/
  v2/                         Original full-size generated artwork and 3D bundle
  cursors/                    Original SVG and transparent PNG cursor designs
  icons/                      Phosphor SVG source icons and license
  *.woff2                     Embedded variable fonts
  *-OFL.txt                   Font licenses
  world.geojson               Natural Earth map source
  *-card.webp                 Optimized game artwork
speedy-logo.svg                Standalone transparent logo
social-preview.jpg             Social-sharing asset
tools/
  site.html                   HTML template
  site.css                    Base component styles
  v2.css                      Version 2 art direction and cursor styles
  site.js                     Website interactions
  scene.js                    Authored Three.js sculpture and controls
  build.py                    Asset optimization and single-file assembly
  cursors.py                  Transparent cursor generation
  prepare-vercel.mjs          Automatic production SEO URL injection
  qa.py                       Automated interaction and responsive checks
package.json                  Exact JavaScript dependency versions
package-lock.json             Reproducible dependency lockfile
requirements.txt              Python build dependencies
vercel.json                   Publishes only the public folder
```

## Build from source

Requires Node.js 20.19 or newer and Python 3.11 or newer.

```sh
npm ci
python -m pip install -r requirements.txt
python tools/cursors.py
npm run build
```

The build writes the standalone `index.html` and the identical `public/index.html`, plus the logo and social preview in `public`.

Preview only the public website:

```sh
python -m http.server 3000 --bind 0.0.0.0 --directory public
```

Open `http://localhost:3000` on your own computer. Remote preview environments should use their provided preview URL.

## Vercel publishing

Vercel deploys the website; GitHub stores the private source repository. These are separate services.

### Import a private GitHub repository

1. Create or use a **private** GitHub repository and commit this source.
2. In Vercel, choose **Add New → Project**, authorize the GitHub integration, and import the private repository.
3. Select **Other** as the framework. The included `vercel.json` serves the already-built `public` directory. No package installation is required. A tiny built-in Node.js publishing step injects the real production origin into the SEO tags.
4. Deploy. The source repository can remain private while the website is publicly accessible.
5. To keep future deployments up to date, commit both source changes and the rebuilt `public` files. The Git integration then deploys new commits.

### Deploy from the CLI

```sh
npm ci
npx vercel login
npx vercel --prod
```

Use the official browser sign-in flow. Do not put access tokens in the repository, HTML, screenshots, source files, or chat. `.env`, local credentials, and Vercel project metadata are ignored by Git.

The private repository does **not** automatically make the deployed website private. If the website should also be access restricted, configure Vercel Deployment Protection in your account.

## SEO and production checks

SEO metadata includes the title, description, robots directive, canonical URL, Open Graph, Twitter card, and JSON-LD.

Before public launch:

* On Vercel, `tools/prepare-vercel.mjs` automatically resolves the SEO origin from `SITE_URL`, `VERCEL_PROJECT_PRODUCTION_URL`, or `VERCEL_URL`. Set `SITE_URL` to your custom production origin if needed. For other hosts, replace the example origin in the template and rebuild.
* Host `public/social-preview.jpg` at the social-preview URL referenced by the metadata.
* Verify actual prices, game requirements, locations, features, support arrangements, and business policies.
* Connect secure authentication, billing, payment, provisioning, and support backends if turning the concept into a real hosting service.

This is a frontend concept. It does not collect payments, create accounts, send support messages, or provision servers. Form inputs stay in memory in the browser. Downloaded quotes and support drafts are local files.

## Third-party and artwork credits

* Three.js: MIT license. Authored sculpture geometry, lighting, batching, and interactions are in `tools/scene.js`.
* Phosphor Icons: MIT license. Source and license in `assets/icons`.
* Space Grotesk and Manrope: SIL Open Font License. Full licenses are in `assets` and embedded in the HTML.
* Natural Earth geography: public domain.
* Seven original generated illustrations are in `assets/v2`. They are creative interpretations, not official game screenshots.
* The original wordmark and transparent cursor vectors are included as editable SVGs.
* Game names belong to their respective publishers. This concept is not affiliated with the publishers.

All runtime visuals and fonts are embedded in the standalone page. Production social-sharing previews are the only optional publishing asset that needs a public URL.
