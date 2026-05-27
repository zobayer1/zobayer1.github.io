# Local Development

How to set up, run, and contribute to this blog locally. The site is a
[Jekyll](https://jekyllrb.com/) site built on the
[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme (consumed as a gem)
and is deployed automatically to GitHub Pages.

## Prerequisites

- **git**
- **[mise](https://mise.jdx.dev/)** — manages the Ruby version for this project.

> **Do not use your distro's system Ruby.** On recent Fedora it is 4.x, which the
> Chirpy theme's `ruby ~> 3.1` constraint rejects. mise installs and pins the supported
> version for you, isolated from the system.

## 1. Clone with submodules

The self-hosted theme assets live in a git submodule (`assets/lib`):

```bash
git clone --recurse-submodules git@github.com:zobayer1/zobayer1.github.io.git
cd zobayer1.github.io
```

Already cloned without `--recurse-submodules`? Fetch them with:

```bash
git submodule update --init
```

## 2. Install Ruby (via mise)

The Ruby version is pinned in [`.tool-versions`](../.tool-versions):

```bash
mise install
```

> If `mise install` fails while **compiling** Ruby (e.g. the `psych`/libyaml extension
> "could not be configured"), switch to precompiled binaries — no system build tools
> required:
>
> ```bash
> mise settings ruby.compile=false
> mise install
> ```

## 3. Install gems

```bash
bundle install
```

## Run the site locally

```bash
bash tools/run.sh
```

Runs `jekyll serve` with live reload at <http://127.0.0.1:4000>. Useful flags:

- `bash tools/run.sh -H 0.0.0.0` — bind all interfaces (view from another device)
- `bash tools/run.sh -p` — run in production mode

Equivalent direct command: `bundle exec jekyll serve --livereload`.

## Build

```bash
bundle exec jekyll build                          # outputs to _site/
JEKYLL_ENV=production bundle exec jekyll build    # production build, as CI does
```

## Check links

```bash
bash tools/test.sh
```

Builds the site and runs `html-proofer` over `_site` (internal links only; external
links are skipped). Worth running before you push — the CI workflow does **not** run it.

## Writing a post

Create a file in `_posts/` named `YYYY-MM-DD-title-with-dashes.md` with front matter:

```yaml
---
title: My Post Title
date: 2026-05-27 10:00:00 +0600   # include the timezone offset
categories: [Top Category, Sub Category]   # up to two, most general first
tags: [tag-one, tag-two]                    # lowercase
---
```

The published URL will be `/posts/title-with-dashes/`. The "last modified" date is
derived automatically from git history (`_plugins/posts-lastmod-hook.rb`), so a post is
only flagged as updated once its file has more than one commit.

Work-in-progress drafts can live in `_drafts/` (not published; comments disabled).

## Deployment

Pushing to `main` triggers the **Build and Deploy** GitHub Actions workflow
(`.github/workflows/pages-deploy.yml`), which builds with Ruby 3.4 and publishes to
GitHub Pages. There is no manual deploy step — merging to `main` deploys the site.
