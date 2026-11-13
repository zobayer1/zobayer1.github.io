# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal Jekyll blog (`zobayer.net`) built on the **Chirpy** theme, derived from
[chirpy-starter](https://github.com/cotes2020/chirpy-starter). The theme is consumed as a
**RubyGem** (`jekyll-theme-chirpy ~> 7.5`, see `Gemfile`), so this repo holds mostly *content and
config* — it does not vendor the theme's `_sass` or `_javascript` source. To inspect theme
internals, run `bundle info --path jekyll-theme-chirpy`.

This is a content repo, not theme development. Most of what you'll do is author Markdown
posts/pages and adjust `_config.yml`.

`README.md` and `docs/local-development.md` are the human-facing versions of the setup/deploy
material below — keep them in sync when any of it changes.

### Theme overrides

A file in this repo's `_layouts/`, `_includes/`, `_data/`, or `assets/` shadows the gem's file of
the same path, so overrides are copies that drift from upstream and **must be re-checked after a
theme bump**. The resolved theme version is in `Gemfile.lock` (currently 7.5.0). Current
overrides:

- `_layouts/home.html` — copy of Chirpy 7.5.0's, plus three blocks marked `LOCAL:` that add a
  GoatCounter view count to each post card's meta row. Diff against
  `$(bundle info --path jekyll-theme-chirpy)/_layouts/home.html` after upgrading and re-apply.
- `_layouts/page.html` — copy of Chirpy 7.5.0's, plus one `LOCAL:` line letting front matter
  override just the `<h1>` via a `heading` key (used by `_tabs/about.md`). Setting `title` instead
  would not work: the theme's `_includes/head.html` builds the browser `<title>` for tabs from
  `site.data.locales[lang].tabs[tab_key]` **with no `| default:` fallback** (unlike `page.html`,
  which has one), so a tab whose title is not a key in `_data/locales/en.yml` renders an empty
  `<title>`. Keeping `title` canonical and layering `heading` on top avoids that.
- `_includes/pageviews/goatcounter-list.html` — new file, no upstream counterpart. Fills in the
  counts on post cards. The theme's own `pageviews/goatcounter.html` handles post pages only.
- `_includes/pageviews/goatcounter.html` — copy of Chirpy 7.5.0's, changed to read from the
  Worker, and to hide the line rather than print `1` on failure. Upstream's fallback is
  indistinguishable from a genuine count of 1, which once disguised a GoatCounter outage here
  as real data. Upstream's spinner is never shown either — see the CSS note below.
- `_includes/pageviews/counts-store.html` — new file, no upstream counterpart. Shared by both
  pageview includes: starts the request at parse time and keeps the last response in
  localStorage for 60s.
- `assets/js/data/swconf.js` — copy of Chirpy 7.5.0's, plus one `LOCAL:` block adding
  `pageviews.proxy` to the service worker's `interceptor.urlPrefixes`. The service worker is
  cache-first and ignores `Cache-Control`, so without this it stores the Worker's response on
  first visit and replays it until the next deploy rotates `cacheName` — freezing every count.
  The same worker has scope `/`, so it also controls the other GitHub Pages sites served from
  this domain: `/cse-221` (zobayer1/cse-221) and `/elastic-migrate` (zobayer1/elastic-migrate).
  They are listed under `pwa.cache.deny_paths` in `_config.yml`; without that, it served stale
  copies of their pages until a hard reload. Add any new project site on this domain there.
- `_data/` (`authors.yml`, `contact.yml`, `media.yml`, `share.yml`, `locales/`, `origin/`) —
  vendored wholesale from the theme's *source* repo (not the gem), so it is invisible drift: the
  gem ships its own copies and these silently win. Only `contact.yml` carries local edits (a
  LinkedIn entry, and the X icon for the Twitter row). Re-check after a theme bump.
- `assets/css/jekyll-theme-chirpy.scss` — Chirpy's designated customization entry point, not a
  shadow copy, so a theme bump does not invalidate it. Holds the sidebar brand font, the enlarged
  avatar, the widened sidebar (breakpoints must stay in sync with the theme's `lg`/`xxxl`), and
  the `.pv-ready` visibility rule described under Page view counts.

## Page view counts

Counts do **not** come from GoatCounter's public `/counter/*.json` endpoint. That endpoint is
served with `Cache-Control: public` and `Expires: +4h` from GoatCounter's own edge, so it lags
reality by up to ~4h. Its cache cannot be defeated from the client (`?cb=` is ignored; `?start=`
is honoured but merely keys a separate 4h entry), and deliberately busting it would just hammer
a free service.

Instead, `worker/` holds a Cloudflare Worker that reads GoatCounter's authenticated API
(`/api/v0/stats/hits`) and re-exposes every path's count as a single public JSON map. The site
fetches it once per page load — one request for the whole home page, not one per card.
`pageviews.proxy` in `_config.yml` is that URL; empty means no counts appear anywhere, as there
is deliberately no fallback.

- **Deploy:** pushing a change under `worker/` to `main` triggers
  `.github/workflows/worker-deploy.yml`. `pages-deploy.yml` ignores `worker/**` so a
  Worker-only change does not rebuild the site. Manually it is `cd worker && npx wrangler deploy`
  (or `-c worker/wrangler.toml` from the root). CI needs two GitHub secrets,
  `CLOUDFLARE_API_TOKEN` (the "Edit Cloudflare Workers" template) and `CLOUDFLARE_ACCOUNT_ID`.
- **The GoatCounter API token is a Worker secret** — `npx wrangler secret put GOATCOUNTER_TOKEN` —
  never in the repo and deliberately *not* in GitHub. Worker secrets live in Cloudflare and
  survive redeploys, so CI never needs it. Local dev secrets belong in `worker/.dev.vars`, which
  is gitignored.
- **Freshness** is capped by `CACHE_TTL` (5 min) via the `PV_CACHE` KV namespace, which also
  bounds GoatCounter to ~12 API calls/hour no matter how much traffic the site gets. KV is used
  rather than the Cache API because the latter appears to be a no-op on `workers.dev` subdomains.
  The Worker separately sends `max-age=BROWSER_TTL` (60s) so a visitor clicking around the site
  paints counts from their own browser cache instead of refetching — a refetch per page load
  means a spinner in the post meta and a spinning tab throbber every time. Worst case a visitor
  sees `BROWSER_TTL + CACHE_TTL` of staleness. The includes therefore use a plain `fetch()`; do
  not reintroduce `cache: 'no-cache'`, which defeats this entirely.
- **No spinner on post pages.** Chirpy's markup seeds `#pageviews` with a spinner, but the
  pageviews script is emitted into `<head>` — thousands of characters before the element is
  parsed — so it cannot paint until `DOMContentLoaded`, and on a long post that spinner turns
  for the whole parse. Two mitigations: `counts-store.html` starts the request at parse time
  instead of on `DOMContentLoaded`, and caches the map in localStorage for 60s so a repeat visit
  needs no network at all. The line itself is then hidden by
  `.post-meta span:has(> #pageviews)` in `assets/css/jekyll-theme-chirpy.scss` and revealed with
  `.pv-ready` once a real number exists, which also means a failed lookup degrades to nothing
  rather than a spinner that turns forever.
- **`START` (2023-01-01) bounds the query window and must stay bounded.** GoatCounter always
  returns a per-day *and* per-hour series for every path in the range — `group` does not suppress
  it — so an all-time window exceeds the Worker's 128MB memory limit while reading the body. Data
  for this site begins in 2024 (measured: the site total is flat for every floor from 2018 through
  2024-01-03, then falls). Hits before `START` are not counted, so bump it if older data is ever
  imported.
- `worker/` is in the Jekyll `exclude:` list so it is never published to the site.
- The Worker reports **all-time** counts, while the GoatCounter dashboard defaults to a limited
  period — the two only agree with the dashboard set to All time.

## Common commands

Ruby is managed with [mise](https://mise.jdx.dev/), pinned to the version in `.tool-versions`.
**Do not use Fedora's system Ruby** — it is 4.x, which Chirpy's `ruby ~> 3.1` constraint rejects.
First-time setup: `mise install` (installs the pinned Ruby) then `bundle install`. After that:

> If `mise install` fails compiling Ruby (e.g. the `psych`/libyaml extension can't be configured),
> run `mise settings ruby.compile=false` to use precompiled binaries — no system build deps needed.


- **Serve locally with livereload:** `bash tools/run.sh` (wraps `bundle exec jekyll s -l`).
  Add `-p`/`--production` for production mode, `-d`/`--drafts` to render `_drafts/` (implies
  `--future`), `-H <host>` to change bind host. Inside Docker it auto-adds `--force_polling`.
- **Build + link-check:** `bash tools/test.sh` — does a `JEKYLL_ENV=production` build into
  `_site` then runs `htmlproofer` (external URLs disabled, localhost ignored). Pass
  `-c "<config_a,config_b>"` for alternate configs. CI does not run this, so it is the only
  link-checking that happens.
- **Plain build:** `bundle exec jekyll b -d _site`.
- **`tools/init.sh` is destructive and unused here** — it is the inherited chirpy-starter
  bootstrap, which hard-resets to the theme release commit and wipes `_posts/`. Never run it.

## Deployment

Pushing to `main` (or `master`) triggers `.github/workflows/pages-deploy.yml`, which builds with
`JEKYLL_ENV=production` and publishes to GitHub Pages. There is **no manual deploy step** — commit
to `main` and CI handles it. Notes:

- The workflow checks out with `submodules: true` (required, see below) and `fetch-depth: 0`
  (required by the lastmod hook, see below).
- The CI `htmlproofer` test step is intentionally commented out; link-checking only happens if you
  run `tools/test.sh` locally.
- Custom domain is `zobayer.net` (`CNAME`).

## Content authoring

- **Posts** live in `_posts/` named `YYYY-MM-DD-title.md`. Front matter uses `layout: post`,
  `title`, `date` (with timezone offset, e.g. `+0600`), and a space-separated `categories` list.
  The published URL is `/posts/:title/` (set via `defaults` in `_config.yml` — do not change the
  permalink pattern without updating all inter-post links).
- **Tabs / standalone pages** live in `_tabs/` (e.g. `about.md`, `archives.md`). They use
  `layout: page`, an `icon` (Font Awesome class), and an `order` for sidebar sorting. URL is
  `/:title/`.
- **Drafts** in `_drafts/` have comments disabled by default.
- Tag/category index pages are generated automatically by `jekyll-archives`
  (`/tags/:name/`, `/categories/:name/`).

### Resume page (`/resume/`)

Three files: `_tabs/resume.html` (markup), `assets/css/resume.scss` (compiled to
`/assets/css/resume.css`) and `assets/js/resume.js`. Both assets are linked from the page itself,
so no other page loads them. The tab is `.html`, not `.md`, so kramdown never touches the markup.
Easy things to break:

- **Titles:** the browser `<title>` comes from `resume: Resume` in `_data/locales/en.yml`, and the
  visible `<h1>` from the `heading` override. Below 850px Chirpy hides that `<h1>`, so the hero
  repeats the name in `.rz-name`.
- **Page-only layout rules:** `resume.css` hides `#panel-wrapper` and widens `<main>`. That is safe
  only because the stylesheet loads on this page alone; never move those rules into
  `jekyll-theme-chirpy.scss`.
- **Card structure:** work cards use CSS subgrid, so every `.rz-card` must have exactly six
  children, in order: `h3`, `.rz-meta`, `.rz-proof`, `.rz-what`, `details`, `.rz-chips`. A card
  with a missing or extra child breaks the alignment of its whole row.
- **Lenses:** the "Read as" buttons set `data-lens` on `.rz`. CSS does the dimming and reordering
  from each element's `data-tags` (lens ids: `architect ic lead ai security`). JS only animates and
  mirrors the lens into `?lens=`, so `/resume/?lens=ai` is a shareable tailored view.
- **Timeline:** built by JS from the JSON in `#rz-tl-data`; each bar's `card` is the id it opens.
  Behavior lives in a separate file because the `compress` layout collapses inline scripts onto
  one line, which breaks `//` comments.
- **No JS:** everything still renders except the lens bar and the timeline.
- **Content source:** the text is maintained in a private databank and copied here deliberately.
  Make content changes there first; this page is a rendering of it.

### Last-modified dates

`_plugins/posts-lastmod-hook.rb` derives each post's `last_modified_at` from **git history** (a
post is "modified" only if it has more than one commit touching its file). This is why CI needs
full git history (`fetch-depth: 0`) and why editing a post's content shows up as a modified date
after the change is committed.

## Static assets & CDN

- `assets/lib` is a **git submodule** ([chirpy-static-assets](https://github.com/cotes2020/chirpy-static-assets))
  providing self-hosted JS/CSS libraries. `assets.self_host` is `enabled: true` but scoped to
  `env: development`, so the submodule is what **local dev** loads (via `_data/origin/basic.yml`)
  while production builds go to jsDelivr (`_data/origin/cors.yml`). Practical consequence: a
  clone without `git submodule update --init` serves a local site with broken fonts, icons, TOC,
  and search, while production is unaffected. CI checks out submodules anyway.
- Media resources (avatar, post images, etc.) whose paths start with `/` are rewritten to the CDN
  `https://storage.googleapis.com/glitchfest-pub` (`cdn:` in `_config.yml`) — a public
  Google Cloud Storage bucket served over Google's own TLS.

## Agent tools (`agents/tools/`)

Reusable scripts that agents wrote while authoring posts. `agents/tools/README.md` indexes them
with what each one does and how to run it. Read it before making figures, diagrams or a PDF
handout for a post. Extend an existing tool before writing a new one, and give every new tool a
README entry. `agents` is in Jekyll's `exclude:` list, so nothing in it is published.

- **`agents/tools/recursion/`** holds the figures and the practice-problem PDF for "Don't Fear
  Recursion". Two of its files are the starting point for any new algorithm figure:
  `post_figures.py` has the Chirpy-matched light/dark SVG primitives, and `practice_figures.py`
  has `ladder()` and the call-tree renderers, which draw from real traced runs.
  `check_solutions.py` and `fuzz_solutions.py` must both pass before the PDF is rebuilt or
  republished.
- **`agents/tools/preview/local.yml`** is a config override for previewing a production build
  locally: empty `cdn`, with analytics, pageviews and the PWA off. The README has the screenshot
  loop.
- **Post media convention:** figures are 720px SVGs in light and dark variants, included with
  `{: .light }` and `{: .dark }`. They are uploaded to `gs://glitchfest-pub/posts/YYYYMMDD/` and
  referenced as `/posts/YYYYMMDD/name.svg`; the `cdn` prefix is added at build time. Other files,
  such as PDFs, are linked by their full bucket URL. Uploading publishes, so confirm with the
  owner first.

## The npm / Node tooling caveat

`package.json`, `rollup.config.js`, `purgecss.config.js`, the stylelint config, husky, and
semantic-release config are all **inherited from the upstream Chirpy theme repo** and are geared
toward *building the theme itself*. They operate on `_javascript/` and `_sass/` source dirs that
**do not exist in this content repo**. Do not expect `npm run build`, `npm test`, or the
`stylelint`/`rollup`/`purgecss` scripts to be part of the normal content workflow — the real build
is the Jekyll build above. Treat this Node tooling as vendored/vestigial unless you are
intentionally importing theme-source files to customize the theme locally.

The one live dependency in that file is **`wrangler`**, added locally for the Worker. Its version
is deliberately mirrored by `wranglerVersion` in `.github/workflows/worker-deploy.yml` so CI and
local `npx wrangler deploy` agree — bump both together or not at all.
