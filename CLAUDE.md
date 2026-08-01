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

### Theme overrides

A file in this repo's `_layouts/` or `_includes/` shadows the gem's file of the same path, so
overrides are copies that drift from upstream and **must be re-checked after a theme bump**.
Current overrides:

- `_layouts/home.html` — copy of Chirpy 7.5.0's, plus three blocks marked `LOCAL:` that add a
  GoatCounter view count to each post card's meta row. Diff against
  `$(bundle info --path jekyll-theme-chirpy)/_layouts/home.html` after upgrading and re-apply.
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
  Add `-p`/`--production` for production mode, `-H <host>` to change bind host. Inside Docker it
  auto-adds `--force_polling`.
- **Build + link-check:** `bash tools/test.sh` — does a `JEKYLL_ENV=production` build into
  `_site` then runs `htmlproofer` (external URLs disabled, localhost ignored). Pass
  `-c "<config_a,config_b>"` for alternate configs.
- **Plain build:** `bundle exec jekyll b -d _site`.

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

### Last-modified dates

`_plugins/posts-lastmod-hook.rb` derives each post's `last_modified_at` from **git history** (a
post is "modified" only if it has more than one commit touching its file). This is why CI needs
full git history (`fetch-depth: 0`) and why editing a post's content shows up as a modified date
after the change is committed.

## Static assets & CDN

- `assets/lib` is a **git submodule** ([chirpy-static-assets](https://github.com/cotes2020/chirpy-static-assets))
  providing self-hosted JS/CSS libraries (`assets.self_host.enabled: true`). Run
  `git submodule update --init` after cloning, or builds/CI will be missing vendored assets.
- Media resources (avatar, post images, etc.) whose paths start with `/` are rewritten to the CDN
  `https://storage.googleapis.com/glitchfest-pub` (`cdn:` in `_config.yml`) — a public
  Google Cloud Storage bucket served over Google's own TLS.

## The npm / Node tooling caveat

`package.json`, `rollup.config.js`, `purgecss.config.js`, the stylelint config, husky, and
semantic-release config are all **inherited from the upstream Chirpy theme repo** and are geared
toward *building the theme itself*. They operate on `_javascript/` and `_sass/` source dirs that
**do not exist in this content repo**. Do not expect `npm run build`, `npm test`, or the
`stylelint`/`rollup`/`purgecss` scripts to be part of the normal content workflow — the real build
is the Jekyll build above. Treat this Node tooling as vendored/vestigial unless you are
intentionally importing theme-source files to customize the theme locally.
