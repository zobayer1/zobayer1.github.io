# Agent tools

Scripts written by coding agents (Claude Code) while authoring posts, kept so the
outputs can be rebuilt and the techniques reused. Nothing here is part of the
site: `agents` is in the `exclude:` list in `_config.yml`.

Requirements: system `python3` (with `pygments` for the PDF), `gcc`, the Noto Sans,
Noto Sans Mono and Noto Sans Bengali fonts,
`google-chrome` for rendering and printing, `pdftoppm`/`pdftotext` for
checking PDFs, and `gsutil` for uploading. Run scripts with `python3 -I -B` so
they neither import from the working directory nor leave `__pycache__` behind.

## `recursion/`: "Don't Fear Recursion" figures and practice PDF

Built for `_posts/2026-11-14-dont-fear-recursion.md`. Its outputs live in the
bucket under `gs://glitchfest-pub/posts/20261114/`.

| File | What it does |
| --- | --- |
| `post_figures.py` | Generates the post's figures as light/dark SVG pairs (`trust`, `trust-fib`, `focus`, `ladder`, `down-up`, `stack`, `fib-tree`, `hanoi`). Also holds the shared SVG primitives: Chirpy-matched palettes, `doc()`, `text()`, `pill()`, `frame()`, `sealed()`. |
| `practice_figures.py` | Generates the 21 call-sequence figures in the practice PDF by running each recursion in Python and recording every call. Reusable: `ladder()` for linear recursion, `Trace`, `layout()`/`walk()` for call trees, `badge()`. |
| `build_practice_pdf.py` | Builds the A4 practice PDF from `PROBLEMS` (statements, Input/Output boxes, explanations) and the C code in `practice_source.md`, then prints it with headless Chrome. `--lang bn` builds the Bangla edition. |
| `practice_text_bn.py` | Bangla prose for `--lang bn`: titles, statements, group headings, explanations and page-1 notes. Code, Input/Output, title, URLs and figures are shared with the English edition. Its docstring sets the register: everyday spoken Bangla, with English CS terms written in Bangla script. |
| `practice_source.md` | The 20 C solutions, as the `c` code blocks of the retired practice post. The builder and both checkers read the blocks in order. |
| `check_solutions.py` | Compiles every solution exactly as the PDF prints it, with `-Wall -Wextra -pedantic -Werror`. Feeds it the PDF's Input box and compares the output with the Output box. |
| `fuzz_solutions.py` | Runs each solution on random inputs against a plain Python reference, and replays Tower of Hanoi moves for legality. Fixed seed. |

Rebuild everything and re-check:

```bash
T=agents/tools/recursion OUT=/tmp/recursion-build
python3 -I -B $T/check_solutions.py && python3 -I -B $T/fuzz_solutions.py
python3 -I -B $T/post_figures.py $OUT/figs
python3 -I -B $T/practice_figures.py $OUT/pfigs
python3 -I -B $T/build_practice_pdf.py $T/practice_source.md $OUT/pfigs $OUT/practice.html $OUT/recursion-practice-problems.pdf
python3 -I -B $T/build_practice_pdf.py $T/practice_source.md $OUT/pfigs $OUT/bn.html $OUT/recursion-practice-problems-bn.pdf --lang bn
gsutil cp $OUT/figs/*.svg $OUT/recursion-practice-problems*.pdf gs://glitchfest-pub/posts/20261114/
```

## `preview/`: checking a post before it is published

`local.yml` is a config override that empties `cdn` and turns off analytics,
pageviews and the service worker; its header has the build command. A typical
loop:

1. Build with the override into a scratch directory, and copy that post's
   generated figures into `<site>/posts/YYYYMMDD/`.
2. Serve the build with `python3 -m http.server`.
3. Screenshot it with `google-chrome --headless=new --screenshot=out.png --window-size=1280,7600 URL`.
   Add `--force-dark-mode` to check the dark theme.
4. For SVGs alone, put them in a bare HTML page on a `#fff` and a `#1b1b1e`
   background, and screenshot that.
5. For PDFs, rasterise pages with `pdftoppm -r 60 -png` and look at the pages,
   not just `pdfinfo`.

Lessons learned:

- Headless Chrome does not scroll in `--dump-dom` or `--screenshot` mode, so
  in-page anchor behaviour cannot be tested that way.
- The theme's `compress` layout strips optional tags such as `</body>` and
  `</li>`. Anything that searches or patches the built HTML must not rely on
  them.
- `pkill -f "http.server 8741"` matches its own shell command line and kills
  it. Use a bracket pattern such as `pkill -f "http[.]server 8741"`.
- In print, `break-inside: avoid` cannot keep a block that is taller than a
  page together. Cap figure height instead, for example `max-height: 100mm`.

## Figure conventions

- Figures are SVG, 720 px wide, in a light and a dark variant. Posts include
  both, `{: .light w=... h=... }` and `{: .dark ... }`, so the image follows
  Chirpy's theme toggle.
- Each SVG draws a background in the page colour (`#ffffff` or `#1b1b1e`), so
  dark text stays readable in the click-to-zoom lightbox.
- Colours: blue means a call or work before the call, green means a return or
  work after the call, grey is context. Base cases are green-filled.
- Skip the caption when the figure already carries its own text, and put the
  description in the alt text instead.
- Upload to `gs://glitchfest-pub/posts/YYYYMMDD/`, the bucket behind `cdn` in
  `_config.yml`. Posts reference images as `/posts/YYYYMMDD/name.svg`. Other
  files such as PDFs are linked by their full
  `https://storage.googleapis.com/glitchfest-pub/...` URL.
- Generate figures from real runs where possible, with asserted results, and
  make any layout overflow an error rather than drawing it.
