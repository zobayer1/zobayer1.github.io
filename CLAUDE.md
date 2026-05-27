# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal Jekyll blog (`zobayer.net`) built on the **Chirpy** theme, derived from
[chirpy-starter](https://github.com/cotes2020/chirpy-starter). The theme is consumed as a
**RubyGem** (`jekyll-theme-chirpy ~> 7.1`, see `Gemfile`), so this repo holds *content and
config only* — it does not contain the theme's `_layouts`, `_includes`, `_sass`, or
`_javascript` source. To inspect theme internals, run `bundle info --path jekyll-theme-chirpy`.

This is a content repo, not theme development. Most of what you'll do is author Markdown
posts/pages and adjust `_config.yml`.

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
  `https://assets.zobayer.net` (`cdn:` in `_config.yml`).

## The npm / Node tooling caveat

`package.json`, `rollup.config.js`, `purgecss.config.js`, the stylelint config, husky, and
semantic-release config are all **inherited from the upstream Chirpy theme repo** and are geared
toward *building the theme itself*. They operate on `_javascript/` and `_sass/` source dirs that
**do not exist in this content repo**. Do not expect `npm run build`, `npm test`, or the
`stylelint`/`rollup`/`purgecss` scripts to be part of the normal content workflow — the real build
is the Jekyll build above. Treat this Node tooling as vendored/vestigial unless you are
intentionally importing theme-source files to customize the theme locally.
