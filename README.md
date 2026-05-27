# zobayer.net

My personal blog — notes on software engineering, and whatever else I feel like writing.

🔗 **Live site: <https://zobayer.net>**

Built with [Jekyll](https://jekyllrb.com/) and the
[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme (used as a gem), and
deployed to GitHub Pages by GitHub Actions on every push to `main`.

## Local development

Ruby is managed with [mise](https://mise.jdx.dev/); the site builds with Jekyll.

```bash
git submodule update --init   # fetch theme assets (assets/lib)
mise install                  # install the pinned Ruby (see .tool-versions)
bundle install
bash tools/run.sh             # serve at http://127.0.0.1:4000
```

Full setup, build, link-checking, post-writing, and deployment instructions are in
**[docs/local-development.md](docs/local-development.md)**.

## License

This repository is dual-licensed:

- **Content** — the writing under `_posts/` and `_tabs/`, and original images — is
  © Zobayer Hasan and licensed under
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
  See [`LICENSE`](LICENSE).
- **Theme & code** — the Chirpy theme and the inherited configuration/tooling are under
  the MIT License (© 2021 Cotes Chung). See [`LICENSE-THEME`](LICENSE-THEME).
