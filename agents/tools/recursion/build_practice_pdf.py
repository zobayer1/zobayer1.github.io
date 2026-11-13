"""Build the recursion practice-problem PDF (A4, one problem per page).

Usage: python3 build_practice_pdf.py SOURCE_MD FIG_DIR OUT_HTML [OUT_PDF]
  SOURCE_MD  practice_source.md; its 20 ```c blocks are the solutions, in order
  FIG_DIR    output of practice_figures.py
  OUT_PDF    if given, prints OUT_HTML to this PDF with headless Chrome
  --lang bn  Bangla edition: prose comes from practice_text_bn.py, everything
             else (title, URLs, code, Input/Output, figures) is unchanged
  --bn-font  font family for Bangla glyphs; Latin text stays in Noto Sans

Problem text, Input/Output boxes and explanations live in PROBLEMS below;
check_solutions.py imports PROBLEMS and tests the code against those boxes.
The HTML uses local Noto Sans / Noto Sans Mono and Pygments, so printing
needs no network. Page 1 holds the title, rules, linked contents and the
origin note; each problem then gets its own page.

The result is published at
https://storage.googleapis.com/glitchfest-pub/posts/20261114/recursion-practice-problems.pdf
"""

import argparse
import html
import os
import re
import sys

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CLexer

DEFAULT_BN_FONT = "Noto Sans Bengali"
POST_URL = "https://zobayer.net/posts/dont-fear-recursion/"
OLD_URL = "https://zobayer.blogspot.com/2009/12/cse-102-practice-recursions.html"

GROUPS = [
    ("On the way down, on the way up",
     "Work before the recursive call runs in calling order; work after it runs in reverse."),
    ("Trust the smaller answer",
     "Promise what the function returns, answer the case you already know, and build everything else from a smaller answer."),
    ("Carry it in the parameters",
     "Sometimes there's no smaller answer to trust, only progress to make. Then the parameters carry the state of the work, like a loop counter."),
    ("Shrink from both sides", None),
    ("More than one call", None),
]

# (group index, title, statement, input, output, explanation, figures)
PROBLEMS = [
    (0, "Print an array in reverse",
     "Print the elements of an array, last one first.",
     "69 87 45 21 47", "47 21 45 87 69",
     "The `printf` comes after the call, so nothing is printed on the way down. The calls run past the end of the "
     "array, and each paused call prints its element on the way back up, the last one first. Move the `printf` "
     "above the call and the array prints in order.",
     ["p01"]),
    (0, "Print from both ends",
     "Print the first and last elements, then the second and second-to-last, and so on, until they meet in the middle.",
     "1 5 7 8 9", "1 9\n5 8\n7 7",
     "Each pair is printed before the call, on the way down. Every call moves both ends one step inward, and the "
     "calls stop once `i` passes `j`. Swap the last two lines to print from the middle outwards.",
     ["p02"]),
    (0, "Print a series",
     "Given <i>n</i>, print 1 + x + x<sup>2</sup> + … + x<sup>n−1</sup>.",
     "5", "1 + x + x^2 + x^3 + x^4",
     "Every term is printed before the call, so the series comes out in calling order, and the returns carry "
     "nothing back. Try printing it highest power first.",
     ["p03"]),
    (0, "Reverse a line without an array",
     "Read a line and print it backwards. No arrays and no strings, only <code>getchar()</code> and <code>putchar()</code>.",
     "helloo", "oolleh",
     "Each call reads one character into its own `c`, then calls itself before printing. Nothing is printed until "
     "the newline stops the calls. Then every paused call prints its character on the way back up, last one first: "
     "the call stack is the array.",
     ["p04"]),
    (1, "Factorial",
     "Compute <i>n</i>!.",
     "5", "120",
     "`factorial(5)` trusts `factorial(4)` to return 24, then multiplies it by 5. On the way up, every call does "
     "exactly one multiplication. `long long` holds up to 20!.",
     ["p05"]),
    (1, "Fibonacci",
     "Compute the <i>n</i>'th Fibonacci number, where the first two are both 1.",
     "6", "8",
     "Each call adds the answers of its two calls. The call tree for `fib(5)` shows the cost: `fib(3)` is computed "
     "twice and `fib(2)` three times, and the waste grows exponentially with <i>n</i>. Correct, but slow for "
     "large <i>n</i>.",
     ["p06"]),
    (1, "Sum of a series",
     "Given <i>x</i> and <i>n</i>, compute 1 + x + x<sup>2</sup> + … + x<sup>n−1</sup>.",
     "2 5", "31",
     "Factor out an <i>x</i>: 1 + x(1 + x + … + x<sup>n−2</sup>). The bracket is the same problem for <i>n</i> − 1, "
     "so each call trusts the call below for it, multiplies by <i>x</i> and adds 1. The empty sum, <i>n</i> = 0, is "
     "the base case. No <code>pow()</code> needed.",
     ["p07"]),
    (1, "Maximum of an array",
     "Find the largest element of an array.",
     "7 4 9 6 2", "9",
     "Each call compares its own element with the largest of the rest, which the call below returns. Try the "
     "minimum next.",
     ["p08"]),
    (1, "Greatest common divisor",
     "Find the greatest common divisor of two non-negative integers.",
     "25 8895", "5",
     "Euclid's algorithm: gcd(a, b) = gcd(b, a mod b). Every call just hands new arguments to the next one, and the "
     "answer travels back up unchanged. The depth is only O(log min(a, b)), the safe kind.",
     ["p09"]),
    (1, "String functions",
     "Write your own <code>strlen</code>, <code>strcpy</code>, <code>strcat</code> and <code>strcmp</code>. Test "
     "them on two strings: the length of the first, a copy of it, the second appended to the copy, and a comparison "
     "of the two.",
     "abc\nabd", "length:  3\ncopy:    abc\nappend:  abcabd\ncompare: negative",
     "`my_strlen` counts the first character and trusts the call on the rest of the string, `s + 1`. The other three "
     "work the same way: handle the first character, then recurse on the rest. The library `strcpy` and `strcat` "
     "also return `dst`, which is left out here.",
     ["p10"]),
    (1, "Second maximum",
     "Find the second largest element of an array. Hint: the second maximum of the rest isn't enough on its own. "
     "Promise more.",
     "5 8 7 9 3", "8",
     "Each call gets the top two of the rest from the call below and fits its own element in: as the new largest, "
     "the new second largest, or not at all. A C function can return a struct, which is how one call hands back "
     "two answers without globals. Call it as `top2(a, 0, n).second`.",
     ["p11"]),
    (2, "Prime test",
     "Decide whether each number is prime.",
     "49\n999983\n1", "not prime\nprime\nnot prime",
     "`d` is the loop counter, passed along instead of incremented: each call tests one divisor and passes `d + 1` "
     "on. For 49, the calls stop at 7, which divides it, and 0 is passed back up.",
     ["p12"]),
    (2, "LCM, the long way",
     "Find the least common multiple of two numbers, without using lcm(a, b) = a × b / gcd(a, b).",
     "23 488", "11224",
     "`m` walks through the multiples of `a`. The first one divisible by `b` is the answer, and it is passed back up "
     "unchanged. Shown for 4 and 6; 23 and 488 would take 488 calls. That's a loop in disguise: compare it with "
     "problem 9.",
     ["p13"]),
    (2, "Reverse an integer",
     "Reverse the digits of a number, returning an <code>int</code>.",
     "123405", "504321",
     "The answer is built on the way down: each call moves the last digit of `n` onto the accumulator `acc`. When "
     "`n` runs out, `acc` holds the answer, which is passed back up unchanged.",
     ["p14"]),
    (2, "Remove odd numbers in place",
     "Remove the odd numbers from an array, with no second array and no printing inside the function. Print the "
     "result afterwards.",
     "1 54 88 6 55 7", "54 88 6",
     "`i` reads every element, while `j` only moves when an even number is copied. `j` never passes `i`, so nothing "
     "is overwritten before it is read. When `i` reaches the end, `j` is the new length.",
     ["p15"]),
    (2, "Linear search",
     "The first line is an array, the second the values to look for. For each value, print its index, or -1 if it "
     "isn't there.",
     "2 9 4 7 6\n5 9", "-1\n1",
     "Each call checks one element and moves on. Looking for 5, nothing matches, the calls run off the end of the "
     "array, and -1 comes back up. Try searching from the end next.",
     ["p16"]),
    (3, "Binary search",
     "Same as problem 16, but the array is sorted.",
     "1 2 3 4 5\n3 -5", "2\n-1",
     "Each call checks the middle of its range and drops the half that can't contain `v`, so the depth is "
     "O(log n). Looking for -5, the range is empty after two calls. `lo + (hi - lo) / 2` avoids the overflow that "
     "`(lo + hi) / 2` can hit on huge arrays.",
     ["p17"]),
    (3, "Palindrome sentence",
     "Decide whether each line is a palindrome, counting only letters and digits.",
     "madam, i'm adam\nhulala", "palindrome\nnot palindrome",
     "Each call compares the outer pair and moves inward, skipping anything that isn't a letter or a digit. Shown "
     "for the shorter \"pop, pop\". Try ignoring case next, so \"Madam, I'm Adam\" passes too.",
     ["p18"]),
    (4, "Fibonacci call orders",
     "<code>fib(n)</code> calls <code>fib(n - 1)</code>, then <code>fib(n - 2)</code>, and stops at <i>n</i> ≤ 2. "
     "Print the <i>n</i> of every call in <i>preorder</i> (before its calls), <i>inorder</i> (between them) and "
     "<i>postorder</i> (after them).",
     "5", "Preorder:  5 4 3 2 1 2 3 2 1\nInorder:   2 3 1 4 2 5 2 3 1\nPostorder: 2 1 3 2 4 2 1 3 5",
     "Every call prints its <i>n</i> exactly once; only the moment changes, before, between or after the calls. "
     "That's the same rule as problems 1 to 4. Follow one colour's numbers in the tree and you read off that order.",
     ["p19"]),
    (4, "Tower of Hanoi",
     "Three pegs <code>a</code>, <code>b</code> and <code>c</code>, and <i>n</i> disks on <code>a</code>, largest at "
     "the bottom. Move them all to <code>c</code>, one disk at a time, never placing a larger disk on a smaller one. "
     "Print each move, such as <code>a -&gt; c</code>.",
     "3", "a -> c\na -> b\nc -> b\na -> c\nb -> a\nb -> c\na -> c",
     "Trust `hanoi(n - 1)` to move a stack of <i>n</i> − 1 disks between any two pegs. Then <i>n</i> disks take three "
     "steps: move the top <i>n</i> − 1 out of the way, move the largest disk, and move the <i>n</i> − 1 back on top "
     "of it. Each call prints its move between its two calls, so the moves come out in inorder, just like problem "
     "19. That's 2<sup>n</sup> − 1 moves; tracing them by hand is a mess, trusting the function takes three lines.",
     ["p20-block", "p20"]),
]


UI_EN = {
    "lang": "en",
    "sub": ('A companion to <a href="{post}">Don\'t Fear Recursion</a>. Build its two habits: '
            '<b>trust the function</b> when you write it, <b>focus on one step</b> when you trace it.'),
    "rules": ("<b>Rules:</b> no loops and no global variables inside the recursive function. Whatever a step "
              "needs travels in its parameters or comes back in its return value. That's the whole point of the exercise."),
    "tip": ("<b>Try before you read on.</b> Every problem is followed by its solution, so cover it up and "
            "write your own first. Solutions show only the recursive function; reading input and printing output is up to you. "
            "The code is C, but the ideas carry over to any language."),
    "contents": "Contents",
    "how": "How it runs.",
    "footer": ('Originally posted on my old blog, <a href="{old}">I, ME AND MYSELF !!!</a>, on December 8, 2009, with the '
               'answers in separate documents. Rebuilt with the solutions inline, explained, and traced. Read the full article at '
               '<a href="{post}">zobayer.net/posts/dont-fear-recursion</a>.'),
}


def inline(s):
    """`code` -> <code>; everything else is already HTML."""
    return re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", s)


def main(post_md, fig_dir, out_html, lang="en", bn_font=DEFAULT_BN_FONT):
    ui, groups, texts = UI_EN, GROUPS, [(p[1], p[2], p[5]) for p in PROBLEMS]
    if lang == "bn":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import practice_text_bn as bn
        ui, groups, texts = bn.UI, bn.GROUPS, bn.PROBLEMS
    ui = {k: v.format(post=POST_URL, old=OLD_URL) for k, v in ui.items()}
    blocks = re.findall(r"^```c\n(.*?)^```", open(post_md, encoding="utf-8").read(), flags=re.S | re.M)
    assert len(blocks) == len(PROBLEMS) == 20, (len(blocks), len(PROBLEMS))
    fmt = HtmlFormatter(style="default", cssclass="code")
    parts = []
    toc = {}
    group = None
    for i, ((g, _, _, inp, outp, _, figs), (title, stmt, explain), code) in enumerate(zip(PROBLEMS, texts, blocks), 1):
        if g != group:
            group = g
            name, intro = groups[g]
            parts.append(f'<h2 class="group">{name}</h2>')
            if intro:
                parts.append(f'<p class="intro">{intro}</p>')
        toc.setdefault(g, []).append(f'<li><a href="#p{i}"><span class="tnum">{i}</span>{title}</a></li>')
        fig_html = "".join(f'<img class="fig" src="{fig_dir}/{f}.svg" alt="">' for f in figs)
        parts.append(f"""
<section class="problem" id="p{i}">
  <h3><span class="num">{i}</span>{title}</h3>
  <p>{stmt}</p>
  <div class="io">
    <div><div class="label">Input</div><pre>{html.escape(inp)}</pre></div>
    <div><div class="label">Output</div><pre>{html.escape(outp)}</pre></div>
  </div>
  <div class="label">Solution</div>
  {highlight(code, CLexer(), fmt)}
  <p class="explain"><b>{ui["how"]}</b> {inline(explain)}</p>
  {fig_html}
</section>""")

    css = fmt.get_style_defs(".code")
    toc_html = "".join(f'<div class="tgroup"><h4>{groups[g][0]}</h4><ol>{"".join(items)}</ol></div>'
                       for g, items in toc.items())
    doc = f"""<!doctype html>
<html lang="{ui["lang"]}">
<head>
<meta charset="utf-8">
<title>Don't Fear Recursion: 20 Practice Problems</title>
<style>
@page {{
  size: A4;
  margin: 16mm 16mm 18mm;
  @bottom-center {{ content: counter(page) " / " counter(pages); font: 8.5pt "Noto Sans", sans-serif; color: #6e7781; }}
}}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font: 10pt/{1.7 if lang == "bn" else 1.55} "Noto Sans", "{bn_font}", sans-serif; color: #24292f; margin: 0; }}
a {{ color: #0969da; text-decoration: none; }}
code, pre {{ font-family: "Noto Sans Mono", monospace; }}
code {{ font-size: 0.92em; background: #f6f8fa; border-radius: 4px; padding: 0.05em 0.3em; }}
header {{ border-bottom: 2px solid #0969da; padding-bottom: 10px; margin-bottom: 14px; }}
.kicker {{ font-size: 9pt; color: #6e7781; letter-spacing: 0.04em; text-transform: uppercase; }}
h1 {{ font-size: 22pt; line-height: 1.2; margin: 4px 0 6px; }}
.sub {{ margin: 0; color: #57606a; }}
.note {{ border-radius: 8px; padding: 8px 12px; margin: 8px 0; }}
.note.info {{ background: #ddf4ff; }}
.note.tip {{ background: #dafbe1; }}
h2.group {{ font-size: 14pt; margin: 18px 0 2px; padding-left: 10px; border-left: 4px solid #0969da; break-after: avoid; }}
p.intro {{ margin: 2px 0 6px; color: #57606a; break-after: avoid; }}
section.problem {{ break-inside: avoid; padding: 10px 0 14px; border-top: 1px solid #d0d7de; }}
h2.group + p.intro + section.problem, h2.group + section.problem {{ border-top: none; }}
h3 {{ font-size: 12.5pt; margin: 0 0 4px; display: flex; align-items: center; gap: 8px; }}
.num {{ display: inline-flex; align-items: center; justify-content: center; min-width: 22px; height: 22px;
        border-radius: 11px; background: #0969da; color: #fff; font-size: 10pt; padding: 0 4px; }}
section.problem > p {{ margin: 4px 0 8px; }}
.io {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 6px 0 10px; }}
.io pre {{ margin: 0; background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 6px 10px;
          font-size: 9pt; line-height: 1.45; white-space: pre-wrap; }}
.label {{ font-size: 8pt; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #57606a; margin-bottom: 3px; }}
.code {{ background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; margin: 0 0 8px; }}
.code pre {{ margin: 0; padding: 8px 12px; font-size: 8.8pt; line-height: 1.45; }}
p.explain {{ margin: 6px 0 6px; }}
img.fig {{ display: block; width: auto; max-width: 86%; max-height: 100mm; margin: 6px auto 0; }}
nav.toc {{ break-after: page; margin-top: 16px; }}
nav.toc h2 {{ font-size: 13pt; margin: 0 0 8px; }}
.tcols {{ columns: 2; column-gap: 28px; }}
.tgroup {{ break-inside: avoid; margin-bottom: 12px; }}
.tgroup h4 {{ margin: 0 0 4px; font-size: 10pt; color: #0969da; }}
.tgroup ol {{ list-style: none; margin: 0; padding: 0; }}
.tgroup li {{ margin: 2px 0; }}
.tgroup a {{ color: #24292f; }}
.tnum {{ display: inline-block; min-width: 22px; color: #6e7781; font-variant-numeric: tabular-nums; }}
footer {{ break-inside: avoid; }}
footer {{ margin-top: 18px; border-top: 1px solid #d0d7de; padding-top: 8px; font-size: 9pt; color: #57606a; }}
{css}
</style>
</head>
<body>
<header>
  <div class="kicker">zobayer.net</div>
  <h1>Don't Fear Recursion: 20 Practice Problems</h1>
  <p class="sub">{ui["sub"]}</p>
</header>
<div class="note info">{ui["rules"]}</div>
<div class="note tip">{ui["tip"]}</div>
<nav class="toc"><h2>{ui["contents"]}</h2><div class="tcols">{toc_html}</div>
<footer>{ui["footer"]}</footer></nav>
{''.join(parts)}

</body>
</html>
"""
    open(out_html, "w", encoding="utf-8").write(doc)
    print(f"wrote {out_html}")


def print_pdf(out_html, out_pdf):
    import os
    import subprocess
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=5000", f"--print-to-pdf={out_pdf}",
                    "file://" + os.path.abspath(out_html)], check=True, capture_output=True)
    print(f"wrote {out_pdf}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the recursion practice PDF.")
    ap.add_argument("source_md")
    ap.add_argument("fig_dir")
    ap.add_argument("out_html")
    ap.add_argument("out_pdf", nargs="?", help="print the HTML to this PDF with headless Chrome")
    ap.add_argument("--lang", choices=["en", "bn"], default="en", help="prose language (default en)")
    ap.add_argument("--bn-font", default=DEFAULT_BN_FONT, help=f"font family for Bangla text (default {DEFAULT_BN_FONT})")
    a = ap.parse_args()
    main(a.source_md, a.fig_dir, a.out_html, a.lang, a.bn_font)
    if a.out_pdf:
        print_pdf(a.out_html, a.out_pdf)
