"""Figures for the "Don't Fear Recursion" post, as light/dark SVG pairs.

Usage: python3 post_figures.py OUT_DIR
Writes <name>-light.svg and <name>-dark.svg for every entry in FIGS:
trust, trust-fib, focus, ladder, down-up, stack, fib-tree and hanoi.
The post references them as /posts/20261114/<name>-<theme>.svg on the CDN.

Reusable for other posts' figures:
  THEMES      light/dark palettes matched to Chirpy's page colours
  doc()       SVG wrapper: title/desc for accessibility, shared arrow markers,
              blur/shadow filters, hatch pattern, and a page-coloured
              background so the lightbox popup stays readable
  text(), pill(), frame(), sealed()
              text, labelled pill, call frame, and the locked "trust it" box
Colour language: blue = calls / work before the call,
green = returns / work after the call, grey = context.
"""

import os
import sys

THEMES = {
    "light": dict(
        bg="#ffffff", ink="#24292f", muted="#6e7781", line="#afb8c1",
        box="#f6f8fa", boxline="#d0d7de", focus="#ffffff",
        accent="#0969da", accentsoft="#ddf4ff",
        green="#1a7f37", greensoft="#dafbe1",
        seal="#57606a", sealtext="#ffffff", hatch="#ffffff", shadow=0.22,
    ),
    "dark": dict(
        bg="#1b1b1e", ink="#e6edf3", muted="#8d96a0", line="#545d68",
        box="#24272d", boxline="#3d444d", focus="#1c2330",
        accent="#58a6ff", accentsoft="#14294a",
        green="#3fb950", greensoft="#133a20",
        seal="#3d444d", sealtext="#e6edf3", hatch="#ffffff", shadow=0.45,
    ),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"


def doc(w, h, t, body, title, desc):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">
<title id="t">{title}</title>
<desc id="d">{desc}</desc>
<style>
  .m {{ font-family: {MONO}; }}
  .s {{ font-family: {SANS}; }}
  .b {{ font-weight: 700; }}
</style>
<defs>
  <marker id="ah-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{t['green']}"/>
  </marker>
  <marker id="ah-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{t['accent']}"/>
  </marker>
  <marker id="ah-m" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{t['line']}"/>
  </marker>
  <filter id="blur" x="-10%" y="-40%" width="120%" height="180%">
    <feGaussianBlur stdDeviation="1.5"/>
  </filter>
  <filter id="lift" x="-20%" y="-30%" width="140%" height="160%">
    <feDropShadow dx="0" dy="4" stdDeviation="7" flood-color="{t['accent']}" flood-opacity="{t['shadow']}"/>
  </filter>
  <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="{t['hatch']}" stroke-opacity="0.10" stroke-width="3"/>
  </pattern>
</defs>
<rect width="{w}" height="{h}" rx="12" fill="{t['bg']}"/>
{body}
</svg>
"""


def text(x, y, s, t, cls="m", size=14, fill="ink", anchor="start", extra=""):
    color = t.get(fill, fill)
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def pill(x, y, label, t, fg="accent", bg="accentsoft"):
    w = 8 + len(label) * 7
    return (f'<rect x="{x - w}" y="{y - 14}" width="{w}" height="20" rx="10" fill="{t[bg]}"/>'
            + text(x - w / 2, y + 0.5, label, t, cls="s b", size=11.5, fill=fg, anchor="middle"))


def frame(x, y, w, h, name, state, t, state_fill="muted"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{t["box"]}" stroke="{t["boxline"]}" stroke-width="1.5"/>'
            + text(x + 14, y + h / 2 + 5, name, t, cls="m b", size=14)
            + text(x + w - 14, y + h / 2 + 5, state, t, size=13, fill=state_fill, anchor="end"))


# --------------------------------------------------------------------------
# 1. trust: the recursive call as a sealed box
# --------------------------------------------------------------------------
def fig_trust(t):
    W, H = 720, 222
    out = []
    out.append(f'<rect x="24" y="18" width="672" height="186" rx="10" fill="{t["focus"]}" stroke="{t["accent"]}" stroke-width="2"/>')
    out.append(text(46, 50, "factorial(n)", t, cls="m b", size=16, fill="accent"))
    out.append(text(674, 50, "promise: returns n!", t, cls="s", size=13, fill="muted", anchor="end"))
    out.append(f'<line x1="24" y1="66" x2="696" y2="66" stroke="{t["boxline"]}" stroke-width="1"/>')

    # row 1: the base case
    out.append(text(46, 104, "if (n == 0) return 1;", t, size=15))
    out.append(text(404, 104, "← the rule you already know", t, cls="s", size=13, fill="green"))

    # row 2: the sealed call
    out.append(text(46, 162, "return n ×", t, size=15))
    bx, bw = 152, 184
    out.extend(sealed(bx, 134, bw, 44, "factorial(n−1)", t))
    out.append(text(bx + bw + 6, 162, ";", t, size=15))
    out.append(text(404, 152, "← sealed: don't open it.", t, cls="s", size=13, fill="accent"))
    out.append(text(420, 172, "Trust the promise, it gives (n − 1)!", t, cls="s", size=13, fill="accent"))
    return doc(W, H, t, "\n".join(out),
               "Writing factorial(n)",
               "Inside factorial(n), the base case returns 1, and the call to factorial(n-1) is drawn as a "
               "sealed, locked box: you trust its promise to return (n-1)! instead of looking inside.")


def sealed(bx, by, bw, bh, label, t):
    """A locked, hatched box standing for a recursive call you trust without opening."""
    lx, ly = bx + 14, by + 17
    return [
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{t["seal"]}"/>',
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="url(#hatch)"/>',
        f'<path d="M{lx + 2.5},{ly + 1} v-3.5 a3.5,3.5 0 0 1 7,0 v3.5" fill="none" stroke="{t["sealtext"]}" stroke-width="1.8"/>',
        f'<rect x="{lx}" y="{ly}" width="12" height="10" rx="2" fill="{t["sealtext"]}"/>',
        text(bx + 34, by + 27, label, t, cls="m b", size=14, fill="sealtext"),
    ]


# --------------------------------------------------------------------------
# 1b. trust-fib: two sealed calls
# --------------------------------------------------------------------------
def fig_trust_fib(t):
    W, H = 720, 222
    out = []
    out.append(f'<rect x="24" y="18" width="672" height="186" rx="10" fill="{t["focus"]}" stroke="{t["accent"]}" stroke-width="2"/>')
    out.append(text(46, 50, "fib(n)", t, cls="m b", size=16, fill="accent"))
    out.append(text(674, 50, "promise: returns the n'th Fibonacci number", t, cls="s", size=13, fill="muted", anchor="end"))
    out.append(f'<line x1="24" y1="66" x2="696" y2="66" stroke="{t["boxline"]}" stroke-width="1"/>')

    out.append(text(46, 104, "if (n &lt;= 2) return 1;", t, size=15))
    out.append(text(404, 104, "← the rule you already know", t, cls="s", size=13, fill="green"))

    out.append(text(46, 162, "return", t, size=15))
    b1, b2, bw = 112, 254, 120
    out.extend(sealed(b1, 134, bw, 44, "fib(n−1)", t))
    out.append(text((b1 + bw + b2) / 2, 162, "+", t, size=15, anchor="middle"))
    out.extend(sealed(b2, 134, bw, 44, "fib(n−2)", t))
    out.append(text(b2 + bw + 6, 162, ";", t, size=15))
    out.append(text(404, 152, "← two sealed boxes, same promise.", t, cls="s", size=13, fill="accent"))
    out.append(text(420, 172, "Trust both, add their answers.", t, cls="s", size=13, fill="accent"))
    return doc(W, H, t, "\n".join(out),
               "Writing fib(n)",
               "Inside fib(n), the base case returns 1 for n up to 2, and the calls to fib(n-1) and fib(n-2) "
               "are drawn as two sealed, locked boxes: you trust both to keep the promise and add their answers.")


# --------------------------------------------------------------------------
# 2. focus: one rung of the call ladder in focus, the rest blurred
# --------------------------------------------------------------------------
def fig_focus(t):
    W, H = 720, 462
    out = []
    small = [
        # x, y, name, state, state colour
        (30, 22, "factorial(4)", "4 × ?", "muted"),
        (100, 94, "factorial(3)", "3 × ?", "muted"),
        (240, 316, "factorial(1)", "returns 1", "green"),
        (310, 390, "factorial(0)", "returns 1", "green"),
    ]
    fw, fh = 230, 50
    fx, fy, FW, FH = 170, 168, 320, 126  # the focused frame

    # ladder: who called whom (kept sharp)
    def elbow(px, pby, cx, cy):
        return (f'<path d="M{px},{pby} V{cy} H{cx - 2}" fill="none" stroke="{t["line"]}" '
                f'stroke-width="1.6" marker-end="url(#ah-m)"/>'
                f'<circle cx="{px}" cy="{pby}" r="2.6" fill="{t["line"]}"/>')
    out.append(elbow(52, 72, 100, 119))
    out.append(elbow(122, 144, fx, fy + 62))
    out.append(elbow(fx + 22, fy + FH, 240, 341))
    out.append(elbow(262, 366, 310, 415))

    # out-of-focus frames
    for x, y, name, state, col in small:
        out.append(f'<g filter="url(#blur)" opacity="0.55">{frame(x, y, fw, fh, name, state, t, col)}</g>')

    # the focused frame
    out.append(f'<rect x="{fx}" y="{fy}" width="{FW}" height="{FH}" rx="10" fill="{t["focus"]}" '
               f'stroke="{t["accent"]}" stroke-width="2.2" filter="url(#lift)"/>')
    out.append(text(fx + 18, fy + 32, "factorial(2)", t, cls="m b", size=16, fill="accent"))
    out.append(pill(fx + FW - 14, fy + 26, "IN FOCUS", t))
    out.append(text(fx + 18, fy + 62, "n = 2", t, size=14))
    out.append(text(fx + 18, fy + 86, f'factorial(1) gave <tspan fill="{t["green"]}" font-weight="700">1</tspan>', t, size=14))
    out.append(text(fx + 18, fy + 110, f'return 2 × 1 = <tspan fill="{t["green"]}" font-weight="700">2</tspan>', t, size=14))

    # answers travelling up
    out.append(f'<path d="M{240 + fw},341 C548,341 550,{fy + 80} {fx + FW + 4},{fy + 80}" fill="none" '
               f'stroke="{t["green"]}" stroke-width="2.2" marker-end="url(#ah-g)"/>')
    out.append(text(556, 318, "answer comes up", t, cls="s", size=13, fill="green"))
    out.append(f'<path d="M{fx + 250},{fy} C{fx + 250},132 {fx + 230},119 {100 + fw + 4},119" fill="none" '
               f'stroke="{t["green"]}" stroke-width="2.2" marker-end="url(#ah-g)"/>')
    out.append(text(432, 132, "send 2 to the caller", t, cls="s", size=13, fill="green"))

    # notes
    out.append(text(352, 52, "waiting, paused mid-line", t, cls="s", size=13, fill="muted"))
    out.append(text(556, 420, "done, only the answer", t, cls="s", size=13, fill="muted"))
    out.append(text(556, 438, "they gave matters", t, cls="s", size=13, fill="muted"))
    out.append(text(30, 446, "the ladder on paper: who called whom", t, cls="s", size=13, fill="muted"))
    return doc(W, H, t, "\n".join(out),
               "Tracing factorial(4), one step at a time",
               "The calls factorial(4) down to factorial(0) form a staircase. Only factorial(2) is in focus: "
               "n is 2, factorial(1) gave 1, so it returns 2. The other steps are blurred. Lines on the left "
               "record who called whom; an arrow brings the answer 1 up from factorial(1), and another sends "
               "2 up to the waiting factorial(3).")


# --------------------------------------------------------------------------
# 3. stack: the same ladder, as the machine keeps it
# --------------------------------------------------------------------------
def fig_stack(t):
    W, H = 720, 292
    out = []
    x, w, h, step, top = 232, 256, 42, 50, 26
    rows = [
        ("factorial(0)", "return 1", "green"),
        ("factorial(1)", "1 × ?", "muted"),
        ("factorial(2)", "2 × ?", "muted"),
        ("factorial(3)", "3 × ?", "muted"),
        ("main()", "waiting", "muted"),
    ]
    for i, (name, state, col) in enumerate(rows):
        y = top + i * step
        if i == 0:
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{t["focus"]}" '
                       f'stroke="{t["accent"]}" stroke-width="2.2" filter="url(#lift)"/>')
            out.append(text(x + 14, y + h / 2 + 5, name, t, cls="m b", size=14, fill="accent"))
            out.append(text(x + w - 14, y + h / 2 + 5, state, t, cls="m b", size=13, fill="green", anchor="end"))
        else:
            out.append(f'<g opacity="0.6">{frame(x, y, w, h, name, state, t, col)}</g>')

    bottom = top + 4 * step + h
    # calls push (left)
    out.append(f'<path d="M{x - 26},{bottom - 6} V{top + 8}" stroke="{t["accent"]}" stroke-width="2.2" marker-end="url(#ah-a)"/>')
    out.append(text(x - 40, 128, "each call", t, cls="s", size=13, fill="accent", anchor="end"))
    out.append(text(x - 40, 146, "pushes a frame", t, cls="s", size=13, fill="accent", anchor="end"))
    out.append(text(x - 40, top + 26, "only the top runs", t, cls="s", size=13, fill="muted", anchor="end"))

    # returns pop (right), handing each value down
    values = ["1", "1", "2", "6"]
    for i, v in enumerate(values):
        y1 = top + i * step + h / 2
        y2 = y1 + step
        out.append(f'<path d="M{x + w},{y1} C{x + w + 30},{y1} {x + w + 30},{y2} {x + w + 4},{y2}" fill="none" '
                   f'stroke="{t["green"]}" stroke-width="2" marker-end="url(#ah-g)"/>')
        out.append(text(x + w + 34, (y1 + y2) / 2 + 5, v, t, cls="m b", size=14, fill="green"))
    out.append(text(x + w + 62, 128, "each return pops a frame", t, cls="s", size=13, fill="green"))
    out.append(text(x + w + 62, 146, "and hands its value down", t, cls="s", size=13, fill="green"))
    return doc(W, H, t, "\n".join(out),
               "The call stack during factorial(3)",
               "Frames stacked from main at the bottom up to factorial(0) at the top, which is the only one "
               "running. Each call pushes a frame; each return pops one and hands its value, 1, 1, 2 and 6, "
               "to the frame below.")


# --------------------------------------------------------------------------
# 4. fib-tree: calls made by fib(5), left child n-2, right child n-1
# --------------------------------------------------------------------------
def fig_fib_tree(t):
    W, H = 600, 300
    nodes = {
        "a": (300, 40, 5), "b": (160, 112, 4), "c": (440, 112, 3),
        "d": (90, 184, 3), "e": (230, 184, 2), "f": (375, 184, 2), "g": (505, 184, 1),
        "h": (45, 256, 2), "i": (155, 256, 1),
    }
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("b", "e"), ("c", "f"), ("c", "g"), ("d", "h"), ("d", "i")]
    out = []
    for p, c in edges:
        x1, y1, _ = nodes[p]
        x2, y2, _ = nodes[c]
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["line"]}" stroke-width="1.8"/>')
    out.append(text(214, 72, "n − 1", t, cls="s", size=12, fill="muted", anchor="middle"))
    out.append(text(386, 72, "n − 2", t, cls="s", size=12, fill="muted", anchor="middle"))
    for x, y, v in nodes.values():
        leaf = v <= 2
        stroke = t["green"] if leaf else t["accent"]
        fill = t["greensoft"] if leaf else t["focus"]
        out.append(f'<circle cx="{x}" cy="{y}" r="19" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(text(x, y + 5.5, str(v), t, cls="m b", size=15, fill=stroke, anchor="middle"))
    out.append(f'<circle cx="402" cy="264" r="8" fill="{t["greensoft"]}" stroke="{t["green"]}" stroke-width="2"/>')
    out.append(text(418, 269, "base case, n ≤ 2", t, cls="s", size=13, fill="muted"))
    return doc(W, H, t, "\n".join(out),
               "Calls made by fib(5)",
               "A binary tree of calls. 5 calls 4 on the left and 3 on the right. 4 calls 3 and 2. "
               "That 3 calls 2 and 1. The right-hand 3 also calls 2 and 1. Nodes 1 and 2 are base cases, "
               "so fib(3) is computed twice and fib(2) three times.")


# --------------------------------------------------------------------------
# 6. hanoi: trust hanoi(n-1) to move a whole stack
# --------------------------------------------------------------------------
def fig_hanoi(t):
    W, H = 720, 186
    pw, gap, x0 = 162, 18, 9
    pegs = {"a": 31, "b": 81, "c": 131}
    states = [
        # (block peg, disk peg, highlighted piece, label)
        ("a", "a", None, "start"),
        ("b", "a", "block", "1. hanoi(n−1): a → b"),
        ("b", "c", "disk", "2. move disk n: a → c"),
        ("c", "c", "block", "3. hanoi(n−1): b → c"),
    ]
    out = []
    base = 124
    for k, (bpeg, dpeg, hl, label) in enumerate(states):
        px = x0 + k * (pw + gap)
        out.append(f'<rect x="{px}" y="10" width="{pw}" height="168" rx="10" fill="none" stroke="{t["boxline"]}" stroke-width="1.2"/>')
        out.append(f'<line x1="{px + 8}" y1="{base}" x2="{px + pw - 8}" y2="{base}" stroke="{t["line"]}" stroke-width="2.4"/>')
        for name, off in pegs.items():
            out.append(f'<line x1="{px + off}" y1="40" x2="{px + off}" y2="{base}" stroke="{t["line"]}" stroke-width="3" stroke-linecap="round"/>')
            out.append(text(px + off, base + 18, name, t, cls="m", size=12, fill="muted", anchor="middle"))
        # disk n
        dx = px + pegs[dpeg]
        dstroke = t["accent"] if hl == "disk" else t["boxline"]
        out.append(f'<rect x="{dx - 23}" y="{base - 19}" width="46" height="18" rx="4" fill="{t["box"]}" stroke="{dstroke}" stroke-width="{2 if hl == "disk" else 1.4}"/>')
        out.append(text(dx, base - 6, "n", t, cls="m b", size=11, anchor="middle"))
        # sealed block of n-1 disks
        bx = px + pegs[bpeg]
        btop = base - 19 - 30 if bpeg == dpeg else base - 30 - 1
        out.append(f'<rect x="{bx - 20}" y="{btop}" width="40" height="29" rx="5" fill="{t["seal"]}"/>')
        out.append(f'<rect x="{bx - 20}" y="{btop}" width="40" height="29" rx="5" fill="url(#hatch)"'
                   + (f' stroke="{t["accent"]}" stroke-width="2"' if hl == "block" else "") + '/>')
        out.append(text(bx, btop + 19, "n−1", t, cls="m b", size=11, fill="sealtext", anchor="middle"))
        out.append(text(px + pw / 2, 166, label, t, cls="s", size=12, fill="accent" if hl else "muted", anchor="middle"))
    return doc(W, H, t, "\n".join(out),
               "Tower of Hanoi in three trusted steps",
               "Four snapshots of pegs a, b and c. The top n-1 disks are drawn as one sealed block. "
               "Start: everything on a. Step 1: hanoi(n-1) moves the block to b. Step 2: disk n moves "
               "from a to c. Step 3: hanoi(n-1) moves the block from b onto c.")


# --------------------------------------------------------------------------
# 5. down-up: work before the call vs work after the call
# --------------------------------------------------------------------------
def fig_down_up(t):
    W, H = 720, 350
    out = []
    panels = [
        # x0, title, code, printing side, colour, output, when
        (0, "Work before the call", "print(i); f(i + 1);", "down", "accent", "0 1 2", "on the way down"),
        (362, "Work after the call", "f(i + 1); print(i);", "up", "green", "2 1 0", "on the way up"),
    ]
    soft = {"accent": "accentsoft", "green": "greensoft"}
    top, rh, bh, step, last = 84, 60, 30, 18, 3
    for x0, title, code, side, col, result, when in panels:
        L = lambda k: x0 + 46 + step * k
        R = lambda k: x0 + 314 - step * k
        Y = lambda k: top + rh * k
        out.append(f'<rect x="{x0 + 12}" y="12" width="334" height="326" rx="10" fill="none" stroke="{t["boxline"]}" stroke-width="1.2"/>')
        out.append(text(x0 + 30, 42, title, t, cls="s b", size=15))
        out.append(text(x0 + 330, 42, "n = 3", t, size=13, fill="muted", anchor="end"))
        out.append(text(x0 + 30, 66, code, t, size=13, fill="muted"))

        # direction bar on the printing side
        b1, b2 = Y(0) + 2, Y(last) + bh - 2
        if side == "down":
            out.append(f'<path d="M{x0 + 28},{b1} V{b2 - 10}" stroke="{t[col]}" stroke-width="3" stroke-linecap="round"/>')
            out.append(f'<path d="M{x0 + 22},{b2 - 12} L{x0 + 28},{b2} L{x0 + 34},{b2 - 12} z" fill="{t[col]}"/>')
        else:
            out.append(f'<path d="M{x0 + 330},{b2} V{b1 + 10}" stroke="{t[col]}" stroke-width="3" stroke-linecap="round"/>')
            out.append(f'<path d="M{x0 + 324},{b1 + 12} L{x0 + 330},{b1} L{x0 + 336},{b1 + 12} z" fill="{t[col]}"/>')

        for k in range(last + 1):
            x, y, w = L(k), Y(k), R(k) - L(k)
            base = k == last
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{bh}" rx="7" fill="{t["box"]}" stroke="{t["boxline"]}" stroke-width="1.4"/>')
            out.append(text(x + w / 2, y + 20, "f(3) stops" if base else f"f({k})", t, cls="m b", size=14,
                            fill="muted" if base else "ink", anchor="middle"))
            if base:
                continue
            g1, g2 = y + bh, Y(k + 1)
            mid = (g1 + g2) / 2
            dx, ux = L(k + 1) + 20, R(k + 1) - 20
            down_on, up_on = side == "down", side == "up"
            # the call, down the left
            dc = t[col] if down_on else t["line"]
            out.append(f'<path d="M{dx},{g1 + 2} V{g2 - 9}" stroke="{dc}" stroke-width="{2.2 if down_on else 1.4}"/>')
            out.append(f'<path d="M{dx - 5},{g2 - 10} L{dx},{g2 - 2} L{dx + 5},{g2 - 10} z" fill="{dc}"/>')
            # the return, up the right
            uc = t[col] if up_on else t["line"]
            out.append(f'<path d="M{ux},{g2 - 2} V{g1 + 9}" stroke="{uc}" stroke-width="{2.2 if up_on else 1.4}"/>')
            out.append(f'<path d="M{ux - 5},{g1 + 10} L{ux},{g1 + 2} L{ux + 5},{g1 + 10} z" fill="{uc}"/>')
            # the print, on whichever side does the work
            order = k + 1 if down_on else last - k
            if down_on:
                cx, tx, anchor = dx + 20, dx + 34, "start"
            else:
                cx, tx, anchor = ux - 20, ux - 34, "end"
            out.append(f'<circle cx="{cx}" cy="{mid}" r="9.5" fill="{t[soft[col]]}" stroke="{t[col]}" stroke-width="1.6"/>')
            out.append(text(cx, mid + 4.3, str(order), t, cls="s b", size=11.5, fill=col, anchor="middle"))
            out.append(text(tx, mid + 4.5, f"print {k}", t, size=13, fill=col, anchor=anchor))

        out.append(text(x0 + 30, 322, "output:", t, cls="s", size=13, fill="muted"))
        out.append(text(x0 + 84, 322, result, t, cls="m b", size=15, fill=col))
        out.append(text(x0 + 330, 322, when, t, cls="s", size=13, fill=col, anchor="end"))
    return doc(W, H, t, "\n".join(out),
               "Work before the call vs work after the call",
               "Two copies of the same staircase of calls, f(0) down to f(3) with n = 3, calls going down the "
               "left and returns coming up the right. When the print comes before the recursive call, the "
               "prints ride the calls down the left side and the output is 0 1 2. When it comes after the "
               "call, they ride the returns up the right side and the output is 2 1 0.")


# --------------------------------------------------------------------------
# 7. ladder: the full trace of factorial(4), down on the left, up on the right
# --------------------------------------------------------------------------
def fig_ladder(t):
    W, H = 720, 470
    top, rh, bh, step = 64, 80, 46, 28
    rungs = [
        ("factorial(4)", "n = 4", "4 × 6 = 24"),
        ("factorial(3)", "n = 3", "3 × 2 = 6"),
        ("factorial(2)", "n = 2", "2 × 1 = 2"),
        ("factorial(1)", "n = 1", "1 × 1 = 1"),
        ("factorial(0)", "", "base case: 1"),
    ]
    values = ["6", "2", "1", "1"]  # value carried up from rung k+1 to rung k
    last = len(rungs) - 1
    L = lambda k: 70 + step * k
    R = lambda k: W - 70 - step * k
    Y = lambda k: top + rh * k
    out = []

    # direction bars
    bar_top, bar_bot = Y(0) + 4, Y(last) + bh - 4
    out.append(f'<path d="M34,{bar_top} V{bar_bot - 12}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="M27,{bar_bot - 14} L34,{bar_bot} L41,{bar_bot - 14} z" fill="{t["accent"]}"/>')
    out.append(text(20, (bar_top + bar_bot) / 2, "calls go down", t, cls="s b", size=13, fill="accent", anchor="middle",
                    extra=f'transform="rotate(-90 20 {(bar_top + bar_bot) / 2})"'))
    out.append(f'<path d="M{W - 34},{bar_bot} V{bar_top + 12}" stroke="{t["green"]}" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="M{W - 41},{bar_top + 14} L{W - 34},{bar_top} L{W - 27},{bar_top + 14} z" fill="{t["green"]}"/>')
    out.append(text(W - 20, (bar_top + bar_bot) / 2, "answers come up", t, cls="s b", size=13, fill="green", anchor="middle",
                    extra=f'transform="rotate(90 {W - 20} {(bar_top + bar_bot) / 2})"'))

    for k, (name, down, up) in enumerate(rungs):
        x, y, w = L(k), Y(k), R(k) - L(k)
        base = k == last
        fill = t["greensoft"] if base else t["box"]
        stroke = t["green"] if base else t["boxline"]
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{bh}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        # coloured edge strips: blue on the way down, green on the way up
        if not base:
            out.append(f'<rect x="{x}" y="{y}" width="6" height="{bh}" rx="3" fill="{t["accent"]}"/>')
            out.append(f'<rect x="{x + w - 6}" y="{y}" width="6" height="{bh}" rx="3" fill="{t["green"]}"/>')
        out.append(text(x + 20, y + 29, name, t, cls="m b", size=15))
        if down:
            out.append(text(x + 148, y + 29, down, t, size=14, fill="accent"))
        out.append(text(x + w - 20, y + 29, up, t, cls="m b", size=15, fill="green", anchor="end"))

        if k < last:
            gy1, gy2 = y + bh, Y(k + 1)
            # the call: down the left side
            cx = L(k + 1) + 30
            out.append(f'<path d="M{cx},{gy1 + 3} V{gy2 - 4}" stroke="{t["accent"]}" stroke-width="2.2" marker-end="url(#ah-a)"/>')
            out.append(text(cx + 12, (gy1 + gy2) / 2 + 5, f"calls {rungs[k + 1][0]}", t, cls="s", size=12.5, fill="accent"))
            # the answer: up the right side
            rx = R(k + 1) - 30
            out.append(f'<path d="M{rx},{gy2 - 3} V{gy1 + 4}" stroke="{t["green"]}" stroke-width="2.2" marker-end="url(#ah-g)"/>')
            out.append(text(rx - 12, (gy1 + gy2) / 2 + 5, f"returns {values[k]}", t, cls="s b", size=12.5, fill="green", anchor="end"))

    # the final answer leaves the ladder
    fx = R(0) - 30
    out.append(f'<path d="M{fx},{Y(0) - 3} V{14}" stroke="{t["green"]}" stroke-width="2.2" marker-end="url(#ah-g)"/>')
    out.append(text(fx - 12, 40, "returns 24 to whoever called it", t, cls="s b", size=12.5, fill="green", anchor="end"))
    return doc(W, H, t, "\n".join(out),
               "The full trace of factorial(4)",
               "A U-shaped staircase of rungs. Going down the left: factorial(4) with n = 4 calls factorial(3), "
               "which calls factorial(2), then factorial(1), then factorial(0), the base case, which gives 1. "
               "Coming up the right: factorial(1) returns 1 × 1 = 1, factorial(2) returns 2 × 1 = 2, "
               "factorial(3) returns 3 × 2 = 6, and factorial(4) returns 4 × 6 = 24 to its caller.")


FIGS = {"trust": fig_trust, "trust-fib": fig_trust_fib, "focus": fig_focus, "ladder": fig_ladder, "down-up": fig_down_up, "stack": fig_stack, "fib-tree": fig_fib_tree, "hanoi": fig_hanoi}

if __name__ == "__main__":
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for name, fn in FIGS.items():
        for theme, palette in THEMES.items():
            path = os.path.join(out_dir, f"{name}-{theme}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fn(palette))
            print(path)
